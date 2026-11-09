"""The optional kit gate checks source/packed bytes but never native acceptance."""
import pathlib
import tempfile
import unittest
from tools.tavix_package import pack
from tools.tavix_ui_conformance import check

ROOT=pathlib.Path(__file__).resolve().parents[1]

class ConformanceTests(unittest.TestCase):
 def test_source_and_exact_archive(self):
  p=ROOT/'examples/ui-kit'
  report=check(p)
  self.assertEqual(report['sourceIntegrity'],'passed')
  self.assertEqual(report['nativeRendering'],'not_tested')
  with tempfile.TemporaryDirectory() as td:
   dest=pathlib.Path(td)/'kit.tavix'
   pack(p,dest)
   self.assertEqual(check(dest),report)

 def test_byte_change_is_rejected(self):
  import shutil
  with tempfile.TemporaryDirectory() as td:
   target=pathlib.Path(td)/'app'
   shutil.copytree(ROOT/'examples/ui-kit',target)
   css=target/'ui/kit/ui.css'
   css.write_bytes(css.read_bytes()+b'\n/* unreviewed override */\n')
   with self.assertRaisesRegex(ValueError,'differs from reviewed SDK'):
    check(target)

 def test_disallowed_path_and_missing_license(self):
  self.assertRaisesRegex(ValueError,'invalid in-package kit directory',check,ROOT/'examples/ui-kit','../runtime')
  import shutil
  with tempfile.TemporaryDirectory() as td:
   target=pathlib.Path(td)/'app'
   shutil.copytree(ROOT/'examples/ui-kit',target)
   (target/'ui/kit/LUCIDE_LICENSE.json').unlink()
   with self.assertRaisesRegex(ValueError,'UI kit file missing'):
    check(target)
