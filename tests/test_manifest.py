from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class ManifestTests(unittest.TestCase):
    def test_camelot_manifest_loads_modern_modules_without_retail_vault(self):
        path = ROOT / 'XIV_Databar_Continued_Camelot.toc'
        self.assertTrue(path.is_file(), 'Forever needs a Camelot manifest')
        toc = path.read_text()
        self.assertIn('## Interface: 16001', toc)
        self.assertIn('Mainline\\modules\\talent.lua', toc)
        self.assertIn('Mainline\\modules\\micromenu.lua', toc)
        self.assertNotIn('Mainline\\modules\\load_modules.xml', toc)
        self.assertNotIn('vault.lua', toc)
        self.assertNotIn('Classic\\modules', toc)

    def test_lua_library_is_loaded_as_script(self):
        root = ET.parse(ROOT / 'embeds.xml').getroot()
        ldb = next(e for e in root if 'LibDataBroker-1.1.lua' in e.get('file', ''))
        self.assertEqual(ldb.tag.rsplit('}', 1)[-1], 'Script')

if __name__ == '__main__':
    unittest.main()
