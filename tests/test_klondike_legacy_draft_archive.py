"""Guarded local archival of obsolete example-org Klondike staging draft."""
import json
from pathlib import Path
import tempfile
import unittest

from tools.klondike_legacy_draft_archive import archive_legacy_draft, OLD_APP, NEW_APP

ROOT = Path(__file__).resolve().parents[1]

class KlondikeLegacyDraftArchiveTests(unittest.TestCase):
    def test_noop_when_no_legacy_draft(self):
        with tempfile.TemporaryDirectory() as temp:
            result = archive_legacy_draft(Path(temp))
            self.assertEqual(result['status'], 'no_legacy_draft')
            self.assertFalse(result['changed'])

    def test_fail_closed_for_unknown_legacy_content(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            legacy = root/'extensions'/OLD_APP/'0.1.1'
            legacy.mkdir(parents=True)
            payload = legacy/'unknown-file'
            payload.write_bytes(b'unknown or unreviewed content')
            with self.assertRaises(ValueError):
                archive_legacy_draft(root)
            self.assertEqual(payload.read_bytes(), b'unknown or unreviewed content')
            self.assertFalse((root/'.tavix-local').exists())

    def test_symbolic_link_is_rejected_without_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root/'original'
            target.mkdir()
            legacy = root/'extensions'/OLD_APP/'0.1.1'
            legacy.parent.mkdir(parents=True)
            try:
                legacy.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('OS disallows symbolic links without privileges')
            with self.assertRaisesRegex(ValueError, 'symlink'):
                archive_legacy_draft(root)
            self.assertTrue(legacy.is_symlink())

    def test_ziprunner_calls_guard_before_preflight_and_tests(self):
        for filename in ('project.zr','tavix.zr'):
            conf=json.loads((ROOT/filename).read_text(encoding='utf-8'))
            build=conf['build']
            self.assertIn('klondike_legacy_draft_archive.py', build[0])
            self.assertIn('ziprunner_catalog_preflight.py', build[1])
            self.assertIn('unittest discover', build[2])
            self.assertFalse(conf['delete_missing'])
            self.assertEqual(conf['post_build_mechanisms'], [])
        self.assertIn('.tavix-local/', (ROOT/'.gitignore').read_text(encoding='utf-8'))

if __name__=='__main__':
    unittest.main()
