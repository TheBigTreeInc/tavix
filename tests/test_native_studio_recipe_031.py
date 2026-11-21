"""0.1.31: ZipRunner portable recipe requires explicit operator adoption."""
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

def read(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))

class RecipeContractTests(unittest.TestCase):
    def test_all_portable_recipes_match(self):
        a=read('project.zr')
        self.assertEqual(a,read('tavix.zr'))
        self.assertEqual(a,read('recipes/tavix-studio.zr'))
        self.assertEqual(a['project_key'],'tavix')
        self.assertEqual(a['version'],'0.1.60')
    def test_build_start_exact_paths(self):
        a=read('project.zr')
        self.assertIn('python tools/studio-desktop/build_windows.py',a['build'])
        self.assertEqual(a['start'],['python tools/studio-desktop/run_windows.py'])
        self.assertTrue(a['mechanisms_require_build_success'])
        self.assertFalse(a['delete_missing'])
        self.assertEqual(a['post_build_mechanisms'],[])
    def test_no_automated_config_write_or_secret(self):
        a=read('project.zr')
        self.assertNotIn('ziprunner.config.json', [p.name for p in ROOT.iterdir()])
        self.assertIn('ziprunner.config.json',a['protected_paths'])
        self.assertNotIn('target_dir',a)
        self.assertNotIn('command_dir',a)
        self.assertNotIn('git',a)
        txt=(ROOT/'docs/QA_0.1.31.adoc').read_text(encoding='utf-8')
        self.assertIn('explicit',txt.lower())
        self.assertIn('Configuration',txt)
        self.assertIn('existing `tavix` project',txt)
    def test_stamped_identity(self):
        a=read('project.zr'); stamp=read('.ziprunner-post-update-tests.json')
        board=read('.ziprunner-workboard-update.json');m=read('ziprunner-manifest.json')
        self.assertEqual({a['version'],stamp['version'],board['version'],m['project']['version']},{'0.1.60'})
        self.assertEqual(m['project']['base_version'],'0.1.58')
        self.assertEqual(len(stamp['tests']),20)
        self.assertEqual(len({x['semantic_id'] for x in stamp['tests']}),20)

if __name__=='__main__': unittest.main()
