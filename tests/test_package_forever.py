"""Offline fixture tests; integration builds use the checked-in dependency lock."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

BUILDER = Path(__file__).resolve().parents[1] / 'scripts/package_forever.py'


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'source'
        self.root.mkdir()
        self.lock = Path(self.tmp.name) / 'lock.json'
        self.lock.write_text('{"dependencies": []}')
        self.output = Path(self.tmp.name) / 'beta.zip'
        self.put('XIV_Databar_Continued_Camelot.toc', '## Interface: 16001\n## X-Curse-Project-ID: 123\ncore.lua\n')
        self.put('core.lua', '-- fixture\n')

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_builder(self):
        return subprocess.run([sys.executable, str(BUILDER), '--root', str(self.root), '--lock', str(self.lock), '--output', str(self.output)], capture_output=True, text=True)

    def test_reproducible_single_install_folder_without_development_files(self):
        for name in ['README.md', 'FOREVER.md', 'LICENSE', 'Mainline.toc', '.git/config', 'tests/foo.lua', 'scripts/foo.lua', 'node_modules/foo.lua', 'docs/foo.md', 'CHANGELOG.md', 'package.json']:
            self.put(name, 'not runtime')
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        first = self.output.read_bytes()
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(first, self.output.read_bytes())
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(set(archive.namelist()), {'XIV_Databar_Continued/' + name for name in ['XIV_Databar_Continued.toc', 'core.lua', 'README.md', 'FOREVER.md', 'LICENSE']})
            self.assertNotIn(b'Project-ID', archive.read('XIV_Databar_Continued/XIV_Databar_Continued.toc'))

    def test_downloads_pinned_archive_preserving_license(self):
        dependency = Path(self.tmp.name) / 'dependency.zip'
        with zipfile.ZipFile(dependency, 'w') as archive:
            archive.writestr('upstream-commit/lib.lua', '-- real fixture')
            archive.writestr('upstream-commit/LICENSE.txt', 'fixture license')
            archive.writestr('upstream-commit/test/test.lua', '-- excluded')
            archive.writestr('upstream-commit/upstream.toc', 'excluded')
        self.lock.write_text(json.dumps({'dependencies': [{'name': 'fixture', 'kind': 'zip', 'url': dependency.as_uri(), 'sha256': hashlib.sha256(dependency.read_bytes()).hexdigest(), 'destination': 'Libs/Fixture'}]}))
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(archive.read('XIV_Databar_Continued/Libs/Fixture/LICENSE.txt'), b'fixture license')
            self.assertIn('XIV_Databar_Continued/Libs/Fixture/lib.lua', archive.namelist())
            self.assertNotIn('XIV_Databar_Continued/Libs/Fixture/upstream.toc', archive.namelist())
            self.assertNotIn('XIV_Databar_Continued/Libs/Fixture/test/test.lua', archive.namelist())

    def test_rejects_invalid_recursive_xml_graph(self):
        self.put('XIV_Databar_Continued_Camelot.toc', '## Interface: 16001\nembeds.xml\n')
        self.put('embeds.xml', '<Ui><Include file="Core/nested.xml"/></Ui>')
        for child, reason in [('<Ui><Script file="missing.lua"/></Ui>', 'Missing reference'), ('<Ui><Include file="../core.lua"/></Ui>', 'Include must reference XML'), ('<Ui><Script file="../../outside.lua"/></Ui>', 'Unsafe reference')]:
            with self.subTest(reason=reason):
                self.put('Core/nested.xml', child)
                result = self.run_builder()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(reason, result.stderr)
        self.put('Core/nested.xml', '<Ui><Script file="../core.lua"/></Ui>')
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_raw_download_checksum_mismatch_does_not_publish_zip(self):
        dependency = Path(self.tmp.name) / 'lib.lua'
        dependency.write_bytes(b'-- pinned fixture')
        item = {'name': 'fixture', 'kind': 'file', 'url': dependency.as_uri(), 'sha256': '0' * 64, 'destination': 'Libs/Fixture/lib.lua'}
        self.lock.write_text(json.dumps({'dependencies': [item]}))
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('SHA256 mismatch', result.stderr)
        self.assertFalse(self.output.exists())
        item['sha256'] = hashlib.sha256(dependency.read_bytes()).hexdigest()
        self.lock.write_text(json.dumps({'dependencies': [item]}))
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(archive.read('XIV_Databar_Continued/Libs/Fixture/lib.lua'), dependency.read_bytes())

    def test_rejects_cross_platform_dependency_paths(self):
        dependency = Path(self.tmp.name) / 'dependency.zip'
        unsafe = [r'root/sub\..\..\..\..\evil.lua', 'C:/evil.lua',
                  'root/C:evil.lua', '/root/evil.lua', 'root/../evil.lua',
                  r'root\evil.lua', 'root/docs/C:ignored.txt']
        for member in unsafe:
            with self.subTest(member=member):
                self.output.unlink(missing_ok=True)
                with zipfile.ZipFile(dependency, 'w') as archive:
                    archive.writestr(member, '-- unreferenced fixture')
                self.lock.write_text(json.dumps({'dependencies': [{
                    'name': 'fixture', 'kind': 'zip', 'url': dependency.as_uri(),
                    'sha256': hashlib.sha256(dependency.read_bytes()).hexdigest(),
                    'destination': 'Libs/Fixture'}]}))
                result = self.run_builder()
                self.assertNotEqual(result.returncode, 0, member)
                self.assertIn('Unsafe archive member', result.stderr)
                self.assertFalse(self.output.exists())
        for kind in ('file', 'zip'):
            for destination in (r'Libs\..\evil.lua', 'C:/evil.lua',
                                'Libs/C:evil.lua', '/evil.lua', '../evil.lua'):
                with self.subTest(kind=kind, destination=destination):
                    self.output.unlink(missing_ok=True)
                    self.lock.write_text(json.dumps({'dependencies': [{
                        'name': 'fixture', 'kind': kind, 'url': dependency.as_uri(),
                        'sha256': hashlib.sha256(dependency.read_bytes()).hexdigest(),
                        'destination': destination}]}))
                    result = self.run_builder()
                    self.assertNotEqual(result.returncode, 0, destination)
                    self.assertIn('Unsafe dependency destination', result.stderr)
                    self.assertFalse(self.output.exists())

    def test_rejects_unreferenced_unsafe_source_filenames(self):
        for name in (r'Core/sub\..\..\..\evil.lua', 'Core/C:evil.lua'):
            with self.subTest(name=name):
                self.output.unlink(missing_ok=True)
                path = self.put(name, '-- not in TOC')
                try:
                    result = self.run_builder()
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Unsafe package entry', result.stderr)
                    self.assertFalse(self.output.exists())
                finally:
                    path.unlink()

    def test_validates_every_final_entry_not_only_reachable_graph(self):
        import runpy
        builder = runpy.run_path(str(BUILDER))
        for name in (r'Libs\evil.lua', 'C:/evil.lua', '/evil.lua',
                     'Libs/../evil.lua', 'Libs/file:stream.lua'):
            with self.subTest(name=name):
                files = {'XIV_Databar_Continued.toc': b'core.lua\n',
                         'core.lua': b'-- safe', name: b'-- unreachable'}
                with self.assertRaisesRegex(ValueError, 'Unsafe package entry'):
                    builder['validate_graph'](files)

    def test_explicit_manifest_selection(self):
        self.put('custom.toc', '## Interface: 16001\ncore.lua\n')
        (self.root / 'XIV_Databar_Continued_Camelot.toc').unlink()
        result = subprocess.run([sys.executable, str(BUILDER), '--root', str(self.root), '--lock', str(self.lock), '--toc', 'custom.toc', '--output', str(self.output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
