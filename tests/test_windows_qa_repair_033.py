"""Source regression for the exact operator Windows 0.1.32 full-suite failure.

Read sources with explicit UTF-8 independent of the Windows system code page.
These assertions are authorization boundary coverage, not permission to publish.
"""
import json
import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]

class WindowsQaRepair033(unittest.TestCase):
    def test_review_source_reads_frontend_as_utf8(self):
        test=(ROOT/'tests/test_studio_review_032.py').read_text(encoding='utf-8')
        frontend=(ROOT/'tools/studio-desktop/src/main.tsx').read_text(encoding='utf-8')
        self.assertIn("(ROOT/'tools/studio-desktop/src/main.tsx').read_text(encoding='utf-8')",test)
        self.assertIn('Publish to official store — integration pending',frontend)
        self.assertIn('<Button isDisabled>Publish to official store — integration pending</Button>',frontend)

    def test_exact_publication_guard_remains_and_project_has_no_publish_mechanism(self):
        handoff=(ROOT/'ZIPRUNNER_HANDOFF.md').read_text(encoding='utf-8')
        self.assertIn('No Git push or public release is authorized',handoff)
        project=json.loads((ROOT/'project.zr').read_text(encoding='utf-8'))
        self.assertEqual(project['version'],'0.1.60')
        self.assertFalse(project['delete_missing'])
        self.assertTrue(project['mechanisms_require_build_success'])
        self.assertEqual(project['post_build_mechanisms'],[])
        self.assertIn('ziprunner.config.json',project['protected_paths'])

    def test_ziprunner_stamped_version_and_no_test_count_regression(self):
        stamp=json.loads((ROOT/'.ziprunner-post-update-tests.json').read_text(encoding='utf-8'))
        board=json.loads((ROOT/'.ziprunner-workboard-update.json').read_text(encoding='utf-8'))
        manifest=json.loads((ROOT/'ziprunner-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual({stamp['version'],board['version'],manifest['project']['version']},{'0.1.60'})
        self.assertEqual(manifest['project']['base_version'],'0.1.58')
        self.assertLessEqual(len(stamp['tests']),20)
        self.assertEqual(len(set(t['semantic_id'] for t in stamp['tests'])),len(stamp['tests']))

if __name__=='__main__': unittest.main()
