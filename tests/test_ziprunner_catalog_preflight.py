import json
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from repository import build_index, check_index, run_stage
from ziprunner_catalog_preflight import preflight

class PreflightTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)/'repo';self.root.mkdir()
  (self.root/'project.zr').write_text('{}',encoding='utf8')
  (self.root/'tavi.repository.json').write_bytes(build_index(self.root))
  self.package=Path(self.tmp.name)/'package';(self.package/'ui').mkdir(parents=True)
  (self.package/'ui/index.html').write_text('<p>app</p>',encoding='utf8')
  self.manifest={'schema':'tavi.extension/v1','id':'org.example.test','version':'1.0.0','name':'Test',
   'summary':'test','publisher':'example','kind':'app','hostApi':{'min':'1.0.0','maxExclusive':'2.0.0'},
   'entrypoints':{'panel':'ui/index.html'},'contributions':[], 'permissions':['ui.panel'],'platforms':['web']}
 def stage(self):
  (self.package/'manifest.json').write_text(json.dumps(self.manifest),encoding='utf8')
  return run_stage(self.root,self.package,'https://github.com/example/repo','MIT')
 def run_cli_check(self,*extra):
  return subprocess.run([sys.executable,str(ROOT/'tools/repository.py'),'check',
                         '--repository',str(self.root),*extra],
                        capture_output=True,text=True,check=False)
 def test_legacy_ziprunner_check_command_repairs_crlf_without_config_change(self):
  self.stage(); catalog=self.root/'tavi.repository.json'
  catalog.write_bytes(catalog.read_bytes().replace(b'\n',b'\r\n'))
  result=self.run_cli_check()
  self.assertEqual(result.returncode,0,result.stderr)
  evidence=json.loads(result.stdout)
  self.assertEqual(evidence['index_preflight']['reason'],'canonical_line_endings_or_formatting')
  self.assertTrue(check_index(self.root))
 def test_legacy_ziprunner_check_command_reconciles_valid_overlay(self):
  self.stage(); catalog=self.root/'tavi.repository.json'; old=catalog.read_bytes()
  self.manifest['version']='1.0.1';self.stage();catalog.write_bytes(old)
  result=self.run_cli_check()
  self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(json.loads(result.stdout)['index_preflight']['reason'],
                   'validated_overlay_newer_releases')
  self.assertTrue(check_index(self.root))
 def test_cli_strict_check_remains_read_only_and_fails_on_stale_catalog(self):
  self.stage(); catalog=self.root/'tavi.repository.json'
  catalog.write_bytes(catalog.read_bytes().replace(b'\n',b'\r\n'))
  before=catalog.read_bytes();result=self.run_cli_check('--strict')
  self.assertEqual(result.returncode,1)
  self.assertEqual(before,catalog.read_bytes())
 def test_cli_does_not_reconcile_unlisted_new_extension(self):
  self.stage();catalog=self.root/'tavi.repository.json';old=catalog.read_bytes()
  self.manifest['id']='org.example.second';self.stage();catalog.write_bytes(old)
  result=self.run_cli_check()
  self.assertEqual(result.returncode,1)
  self.assertIn('explicit publisher staging required',result.stderr)
  self.assertEqual(catalog.read_bytes(),old)
 def test_cli_does_not_reconcile_tampered_publisher(self):
  self.stage();catalog=self.root/'tavi.repository.json';altered=json.loads(catalog.read_bytes())
  altered['extensions'][0]['source']='https://github.com/attacker/repo'
  catalog.write_bytes(json.dumps(altered).encode('utf8'))
  before=catalog.read_bytes();result=self.run_cli_check()
  self.assertEqual(result.returncode,1)
  self.assertIn('modified or mismatches',result.stderr)
  self.assertEqual(catalog.read_bytes(),before)
 def test_cli_strict_accepts_clean_repository(self):
  self.stage()
  result=self.run_cli_check('--strict')
  self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(json.loads(result.stdout)['index_preflight'],'not_needed')
 def test_clean_catalog_is_unmodified(self):
  self.stage(); before=(self.root/'tavi.repository.json').read_bytes()
  self.assertEqual(preflight(self.root)['status'],'unchanged')
  self.assertEqual((self.root/'tavi.repository.json').read_bytes(),before)
 def test_crlf_only_repaired_to_lf(self):
  self.stage(); catalog=self.root/'tavi.repository.json'
  catalog.write_bytes(catalog.read_bytes().replace(b'\n',b'\r\n'))
  self.assertEqual(preflight(self.root)['reason'],'canonical_line_endings_or_formatting')
  self.assertTrue(check_index(self.root)); self.assertNotIn(b'\r\n',catalog.read_bytes())
 def test_older_catalog_with_valid_newer_overlay_is_reconciled(self):
  self.stage();catalog=self.root/'tavi.repository.json';old=catalog.read_bytes()
  self.manifest['version']='1.0.1';self.stage();catalog.write_bytes(old)
  result=preflight(self.root)
  self.assertEqual(result['reason'],'validated_overlay_newer_releases')
  self.assertEqual(result['upgraded_extensions'][0]['to'],'1.0.1')
  self.assertTrue(check_index(self.root))
 def test_tampered_catalog_does_not_get_rewritten(self):
  self.stage();catalog=self.root/'tavi.repository.json';old=json.loads(catalog.read_bytes())
  old['extensions'][0]['source']='https://github.com/attacker/repo'
  catalog.write_text(json.dumps(old),encoding='utf8')
  before=catalog.read_bytes()
  with self.assertRaisesRegex(ValueError,'modified or mismatches'):
   preflight(self.root)
  self.assertEqual(before,catalog.read_bytes())
 def test_missing_release_does_not_get_rewritten(self):
  self.stage();catalog=self.root/'tavi.repository.json';old=catalog.read_bytes()
  (self.root/'extensions/org.example.test/1.0.0/ui/index.html').unlink()
  with self.assertRaises(ValueError):preflight(self.root)
  self.assertEqual(old,catalog.read_bytes())
 def test_unlisted_new_app_is_not_automatically_published(self):
  self.stage();catalog=self.root/'tavi.repository.json';old=catalog.read_bytes()
  self.manifest['id']='org.example.second';self.stage();catalog.write_bytes(old)
  with self.assertRaisesRegex(ValueError,'extension set'):
   preflight(self.root)
  self.assertEqual(old,catalog.read_bytes())

if __name__=='__main__': unittest.main()
