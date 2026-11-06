import importlib.util
from pathlib import Path
import tempfile
import unittest
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tavix_qa', ROOT / 'tools/local-client/qa.py')
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)

class ExactPackageQATests(unittest.TestCase):
    def test_real_staged_atrium(self):
        result = qa.verify(ROOT, 'inc.thebigtree.tavi.atrium', '1.0.5')
        self.assertEqual(result['status'], 'passed', result)
        self.assertIn('two-client multiplayer', result['capabilities_not_tested'])

    def test_reject_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp) / 'extensions' / 'example' / '1.0.0'
            d.mkdir(parents=True)
            (d / 'manifest.json').write_text(json.dumps({'id':'example','version':'1.0.0','entrypoints':{'panel':'../../../../outside'}}))
            self.assertEqual(qa.verify(temp, 'example', '1.0.0')['status'], 'failed')

    def test_reject_bad_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp) / 'extensions' / 'example' / '1.0.0'
            d.mkdir(parents=True)
            (d / 'manifest.json').write_text(json.dumps({'id':'example','version':'1.0.0','entrypoints':{'panel':'ui/index.html'}}))
            (d / 'ui').mkdir()
            (d / 'ui/index.html').write_text('test')
            with zipfile.ZipFile(d / 'example.tavix','w') as z:
                z.writestr('../evil', 'x')
            self.assertEqual(qa.verify(temp, 'example', '1.0.0')['status'], 'failed')

if __name__ == '__main__':
    unittest.main()
