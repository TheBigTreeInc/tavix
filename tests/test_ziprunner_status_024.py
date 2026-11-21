"""Unpublished read-only ZipRunner TaviX extension candidate contract."""
import json
from pathlib import Path
import unittest
from tools.tavix_package import validate, validate_archive
ROOT=Path(__file__).resolve().parents[1]
class ZipRunnerApp24(unittest.TestCase):
 def test_manifest_and_archive(self):
  app=ROOT/'examples/ziprunner-operations-0.1.0'
  m=json.loads((app/'manifest.json').read_text(encoding='utf-8'))
  self.assertEqual(m['permissions'],['ui.panel'])
  self.assertEqual(m['id'],'inc.thebigtree.tavi.ziprunner')
  self.assertEqual(validate(app),validate_archive(ROOT/'candidates/inc.thebigtree.tavi.ziprunner-0.1.0.tavix'))
 def test_untrusted_bridge_fails_closed(self):
  txt=(ROOT/'examples/ziprunner-operations-0.1.0/ui/main.mjs').read_text(encoding='utf-8')
  self.assertIn("'ziprunner.status.read/v1'",txt)
  self.assertIn('sdk.capabilities()',txt)
  self.assertNotIn('localStorage',txt)
  self.assertNotIn('fetch(',txt)
  self.assertNotIn('Bearer ',txt)
  cat=(ROOT/'tavi.repository.json').read_text(encoding='utf-8')
  self.assertNotIn('inc.thebigtree.tavi.ziprunner',cat)
if __name__=='__main__':unittest.main()
