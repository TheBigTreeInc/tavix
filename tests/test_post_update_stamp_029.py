"""Regression: ZipRunner 1.2.304.299 hard-limits post-update test entries to 20.

The 0.1.28 source candidate failed *before* overlay with 21 declarations.
Combining related tests must not discard either command, disable attention flags,
or weaken the existing build/release approval gates.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PostUpdateStampRepairTests(unittest.TestCase):
    def test_compatible_stamped_version_and_entry_limit(self):
        stamp = json.loads((ROOT / '.ziprunner-post-update-tests.json').read_text(encoding='utf-8'))
        project = json.loads((ROOT / 'project.zr').read_text(encoding='utf-8'))
        board = json.loads((ROOT / '.ziprunner-workboard-update.json').read_text(encoding='utf-8'))
        manifest = json.loads((ROOT / 'ziprunner-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(stamp['schema'], 'ziprunner.post-update-tests.v1')
        self.assertEqual(stamp['version'], project['version'])
        self.assertEqual(stamp['version'], board['version'])
        self.assertEqual(stamp['version'], manifest['project']['version'])
        self.assertEqual(stamp['version'], '0.1.60')
        self.assertEqual(manifest['project']['base_version'], '0.1.58')
        self.assertLessEqual(len(stamp['tests']), 20)
        self.assertGreater(len(stamp['tests']), 0)

    def test_no_coverage_lost_when_combining_diagnostics(self):
        stamp = json.loads((ROOT / '.ziprunner-post-update-tests.json').read_text(encoding='utf-8'))
        tests = stamp['tests']
        self.assertEqual(len({t['semantic_id'] for t in tests}), len(tests))
        self.assertTrue(all(t['kind'] == 'command' and t['rerun_policy'] == 'every_update'
                            and t['attention_on_failure'] is True and t['gating'] is False
                            for t in tests))
        commands = '\n'.join(t['command'] for t in tests)
        for module in ('test_manager_events_026.py', 'test_tavia_resource_diagnostics_027.py',
                       'test_manager_suite_025.py', 'test_native_studio_028.py'):
            self.assertIn(module, commands)
        self.assertIn('python -m unittest discover -s tests -v', commands)
        combined = next(t for t in tests if t['semantic_id'] == 'tavix-manager-events-026')
        self.assertEqual(combined['definition_revision'], '2')
        self.assertEqual(combined['command'].count(' && '), 1)
        self.assertNotIn('tavix-tavia-resources-027', {t['semantic_id'] for t in tests})

    def test_repair_does_not_add_publication_authority(self):
        project = json.loads((ROOT / 'project.zr').read_text(encoding='utf-8'))
        self.assertFalse(project['delete_missing'])
        self.assertTrue(project['mechanisms_require_build_success'])
        self.assertEqual(project['post_build_mechanisms'], [])
        self.assertIn('ziprunner.config.json', project['protected_paths'])
        source = (ROOT / 'ZIPRUNNER_HANDOFF.md').read_text(encoding='utf-8')
        self.assertIn('No Git push or public release is authorized', source)


if __name__ == '__main__':
    unittest.main()
