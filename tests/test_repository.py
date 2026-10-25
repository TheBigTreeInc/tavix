import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from repository import run_stage,check_index,build_index,write_index

class RepositoryTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.addCleanup(self.t.cleanup)
  self.base=Path(self.t.name); self.repo=self.base/'repo';self.repo.mkdir();(self.repo/'project.zr').write_text('{}');(self.repo/'tavi.repository.json').write_bytes(build_index(self.repo))
  self.ext=self.base/'bundle';(self.ext/'ui').mkdir(parents=True)
  (self.ext/'ui'/'index.html').write_text('<html><body>Test</body></html>')
  self.manifest={'schema':'tavi.extension/v1','id':'org.example.application','version':'1.0.0','name':'Test','summary':'x','publisher':'example','kind':'app','hostApi':{'min':'1.0.0','maxExclusive':'2.0.0'},'entrypoints':{'panel':'ui/index.html'},'contributions':[],'permissions':['ui.panel'],'platforms':['web']}
  self.save()
 def save(self): (self.ext/'manifest.json').write_text(json.dumps(self.manifest))
 def stage(self):return run_stage(self.repo,self.ext,'https://github.com/example/source','MIT')
 def test_canonical_index_bytes_are_platform_independent(self):
  # Windows Path.write_text() translates '\n' to '\r\n'; a byte-exact
  # repository index must be seeded with canonical bytes on every platform.
  expected=build_index(self.repo)
  actual=(self.repo/'tavi.repository.json').read_bytes()
  self.assertEqual(actual,expected)
  self.assertNotIn(b'\r\n',actual)
  self.assertTrue(check_index(self.repo))
 def test_windows_crlf_catalog_is_detected_and_regenerated(self):
  target=self.repo/'tavi.repository.json'
  target.write_bytes(target.read_bytes().replace(b'\n',b'\r\n'))
  with self.assertRaisesRegex(ValueError,'Stale or modified repository index'):
   check_index(self.repo)
  self.assertTrue(write_index(self.repo))
  self.assertTrue(check_index(self.repo))
 def test_staging_and_catalog(self):
  self.assertEqual(self.stage()['status'],'staged');self.assertTrue(check_index(self.repo));
  index=json.loads((self.repo/'tavi.repository.json').read_text());self.assertEqual(index['extensions'][0]['entrypoint'],'https://thebigtreeinc.github.io/tavix/extensions/org.example.application/1.0.0/ui/index.html')
  self.assertEqual(self.stage()['status'],'unchanged')
 def test_colliding_release_rejected_without_overwrite(self):
  self.stage();p=self.repo/'extensions/org.example.application/1.0.0/ui/index.html';prior=p.read_bytes()
  (self.ext/'ui/index.html').write_text('changed')
  with self.assertRaisesRegex(ValueError,'collision'):self.stage()
  self.assertEqual(p.read_bytes(),prior)
 def test_version_changes_add_releases_and_select_latest(self):
  self.stage();self.manifest['version']='1.1.0';self.save();self.stage();
  self.assertEqual(json.loads((self.repo/'tavi.repository.json').read_text())['extensions'][0]['manifest']['version'],'1.1.0')
 def test_reject_mismatched_metadata(self):
  self.stage()
  with self.assertRaisesRegex(ValueError,'metadata'):run_stage(self.repo,self.ext,'https://github.com/example/other','MIT')
 def test_reject_tamper(self):
  self.stage();(self.repo/'extensions/org.example.application/1.0.0/ui/index.html').write_text('tampered')
  with self.assertRaises(ValueError):check_index(self.repo)
 def test_reject_publisher_takeover_on_next_version(self):
  self.stage();self.manifest['version']='1.1.0';self.manifest['publisher']='other';self.save()
  with self.assertRaisesRegex(ValueError,'Publisher identity'):self.stage()
 def test_preserve_lock_across_versioned_release(self):
  self.stage();lock=self.repo/'extensions/org.example.application/1.0.0/tavix.lock.json'
  before=lock.read_bytes()
  self.manifest['version']='1.0.1';self.save();self.stage()
  self.assertEqual(lock.read_bytes(),before)
 def test_id_traversal(self):
  self.manifest['id']='../secret';self.save()
  with self.assertRaises(ValueError):self.stage()
if __name__=='__main__':unittest.main()
