#!/usr/bin/env python3
"""Build a deterministic, standalone Forever ZIP using only Python's stdlib.

Usage: python3 scripts/package_forever.py --output /tmp/Forever-beta.zip
Dependency downloads are checked against scripts/forever-libs.json.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

ADDON = 'XIV_Databar_Continued'
RUNTIME_DIRS = {'Core', 'Classic', 'Mainline', 'locales', 'media'}
DOCS = {'README.md', 'FOREVER.md', 'LICENSE'}


def validate_package_path(name, context):
    path = PurePosixPath(name)
    if '\\' in name or ':' in name or path.is_absolute() or '..' in path.parts:
        raise ValueError(context + ': ' + name)
    return path


def default_output(root, toc):
    """dist/XIV_Databar_Forever-<version>.zip, derived from the manifest."""
    for line in (root / toc).read_text(encoding='utf-8-sig').splitlines():
        match = re.match(r'##\s*Version\s*:\s*(.+)$', line, re.I)
        if match:
            version = re.sub(r'[^A-Za-z0-9._-]', '_', match.group(1).strip()) or 'dev'
            return root / 'dist' / f'XIV_Databar_Forever-{version}.zip'
    return root / 'dist' / 'XIV_Databar_Forever-dev.zip'


def source_files(root, toc):
    files = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if not path.is_file() or path.is_symlink():
            continue
        if any(part.startswith('.') for part in relative.parts):
            continue
        if relative.parts[0] not in RUNTIME_DIRS and not (len(relative.parts) == 1 and (path.name in DOCS or path.suffix in {'.lua', '.xml', '.png'})):
            continue
        if path.suffix == '.toc':
            continue
        files[relative.as_posix()] = path.read_bytes()
    manifest = (root / toc).read_text(encoding='utf-8-sig')
    manifest = '\n'.join(line for line in manifest.splitlines() if not re.match(r'##\s*X-(?:Curse-Project-ID|Wago-ID|WoWI-ID)\s*:', line, re.I)) + '\n'
    files[ADDON + '.toc'] = manifest.encode()
    return files


def dependency_files(lock):
    from io import BytesIO
    from urllib.request import urlopen

    files = {}
    for item in json.loads(lock.read_text())['dependencies']:
        with urlopen(item['url'], timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('SHA256 mismatch: ' + item['name'])
        destination = validate_package_path(item['destination'], 'Unsafe dependency destination')
        if item['kind'] == 'file':
            files[str(destination)] = data
        elif item['kind'] == 'zip':
            with zipfile.ZipFile(BytesIO(data)) as archive:
                for entry in archive.infolist():
                    path = validate_package_path(entry.filename, 'Unsafe archive member')
                    relative = PurePosixPath(*path.parts[1:])
                    if entry.is_dir() or len(path.parts) < 2:
                        continue
                    if any(p.startswith('.') or p.lower() in {'test', 'tests', 'docs', 'scripts', 'node_modules'} for p in relative.parts):
                        continue
                    if relative.suffix not in {'.lua', '.xml'} and not relative.name.lower().startswith(('license', 'copying', 'copyright')):
                        continue
                    files[str(destination / relative)] = archive.read(entry)
        else:
            raise ValueError('Unknown dependency kind: ' + item['kind'])
    return files


def validate_graph(files):
    import posixpath
    import xml.etree.ElementTree as ET

    # Validate every output name, including files unreachable from the TOC.
    # References are normalized separately so valid ../ XML includes still work.
    for name in files:
        validate_package_path(name, 'Unsafe package entry')
    visited = set()

    def visit(name):
        if name.startswith(('../', '/')) or ':' in name:
            raise ValueError('Unsafe reference: ' + name)
        if name not in files:
            raise ValueError('Missing reference: ' + name)
        if name in visited:
            return
        visited.add(name)
        if name.endswith('.toc'):
            references = [(line.strip(), None) for line in files[name].decode('utf-8-sig').splitlines() if line.strip() and not line.lstrip().startswith('#')]
        elif name.endswith('.xml'):
            try:
                document = ET.fromstring(files[name])
            except ET.ParseError as error:
                raise ValueError(f'Invalid XML {name}: {error}') from error
            references = [(element.attrib['file'], element.tag.rsplit('}', 1)[-1]) for element in document.iter() if 'file' in element.attrib and element.tag.rsplit('}', 1)[-1] in {'Include', 'Script'}]
        else:
            return
        for reference, tag in references:
            if tag == 'Include' and not reference.lower().endswith('.xml'):
                raise ValueError(f'Include must reference XML: {name}: {reference}')
            normalized = reference.replace('\\', '/')
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), normalized))
            visit(target)

    visit(ADDON + '.toc')
    return len(visited)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--toc', default=ADDON + '_Camelot.toc')
    parser.add_argument('--lock', type=Path, default=Path(__file__).with_name('forever-libs.json'))
    parser.add_argument('--output', type=Path, default=None,
                        help='archive to write (default: dist/XIV_Databar_Forever-<version>.zip)')
    args = parser.parse_args()
    output = args.output or default_output(args.root, args.toc)
    files = source_files(args.root, args.toc)
    files.update(dependency_files(args.lock))
    checked = validate_graph(files)
    print(f'Validated {checked} TOC/XML graph files')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(ADDON + '/' + name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content, compresslevel=9)
    print(f'{output}: {len(files)} files; sha256={hashlib.sha256(output.read_bytes()).hexdigest()}')
    print('Extract this archive into Interface\\AddOns\\ so you get AddOns\\' + ADDON + '\\')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        sys.exit(f'Packaging failed: {error}')
