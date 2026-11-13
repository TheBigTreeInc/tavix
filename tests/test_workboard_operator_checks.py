"""Prevent a pre-overlay ZipRunner Workboard rejection on Windows and Linux."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class WorkboardOperatorChecksTests(unittest.TestCase):
    def test_workboard_operator_checks_and_version(self):
        workboard = json.loads((ROOT / '.ziprunner-workboard-update.json').read_text(encoding='utf-8'))
        self.assertEqual(workboard['schema'], 'ziprunner.workboard-update.v1')
        self.assertEqual(workboard['project'], 'tavix')
        self.assertEqual(workboard['version'], '0.1.22')
        for section in ('implemented', 'remaining'):
            items = workboard[section]
            self.assertTrue(items, section)
            for item in items:
                with self.subTest(section=section, workboard_id=item['id']):
                    self.assertIsInstance(item['id'], str)
                    self.assertTrue(item['title'].strip())
                    self.assertTrue(item['summary'].strip())
                    checks = item.get('operator_checks')
                    self.assertIsInstance(checks, list)
                    self.assertGreaterEqual(len(checks), 1)
                    self.assertLessEqual(len(checks), 20)
                    self.assertTrue(all(isinstance(check, str) and check.strip() for check in checks))

    def test_tavix_release_approval_is_still_gated(self):
        p = json.loads((ROOT / 'project.zr').read_text(encoding='utf-8'))
        self.assertEqual(p['version'], '0.1.22')
        self.assertFalse(p['delete_missing'])
        self.assertEqual(p['post_build_mechanisms'], [])
        self.assertIn('ziprunner.config.json', p['protected_paths'])
        handoff = (ROOT / 'ZIPRUNNER_HANDOFF.md').read_text(encoding='utf-8')
        self.assertIn('No Git push or public release is authorized', handoff)
