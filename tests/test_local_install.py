import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('local_packages', ROOT/'tools/local-client/local_packages.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
from tools.tavix_package import pack

class LocalInstallTests(unittest.TestCase):
    def test_install_remove_and_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/'src'; source.mkdir()
            (source/'manifest.json').write_text(json.dumps({'schema':'tavi.extension/v1','id':'test.app','version':'1.0.0','entrypoints':{'panel':'index.html'}}))
            (source/'index.html').write_text('<h1>ok</h1>')
            archive=root/'app.tavix';pack(source,archive)
            result=mod.install(archive.read_bytes(),root/'local')
            self.assertEqual(result['publisher_trust'],'unverified')
            self.assertEqual(len(mod.installed(root/'local')),1)
            with self.assertRaisesRegex(ValueError,'already installed'):mod.install(archive.read_bytes(),root/'local')
            mod.remove(root/'local','test.app','1.0.0')
            self.assertEqual(mod.installed(root/'local'),[])
    def test_invalid_archive_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(Exception):mod.install(b'not a zip',Path(tmp))
    def test_traversal_remove_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):mod.remove(Path(tmp),'..','foo')
if __name__=='__main__': unittest.main()
