"""Regression for native Windows cargo E0382: moved map key reused in JSON response.

This is a source guard only. The Windows native cargo build must independently pass.
"""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUST = ROOT / 'tools/studio-desktop/src-tauri/src/studio_catalog.rs'

class StudioCatalogRustOwnership056(unittest.TestCase):
    def test_row_identity_retained_for_result_after_map_insert(self):
        body = RUST.read_text(encoding='utf-8')
        self.assertIn('entries.insert(row_key.clone(),row.clone());',body)
        self.assertNotRegex(body, r'entries\.insert\(row_key\s*,')
        self.assertIn('"rowKey":row_key',body)
        self.assertIn('"remoteApplied":false',body)
        self.assertLess(body.index('entries.insert(row_key.clone(),row.clone());'),
                        body.index('"rowKey":row_key'))

    def test_no_new_publish_authority_or_profile_file_change(self):
        body=RUST.read_text(encoding='utf-8')
        self.assertIn('catalog-drafts.json',body)
        self.assertIn('valid_row(&row_key)?;',body)
        self.assertIn('"publicationAuthorized":false',body)
        self.assertNotIn('LOOPRD_ASSETS_PUBLISH_TOKEN',body)
        self.assertNotIn('gh release',body)
        project=json.loads((ROOT/'project.zr').read_text(encoding='utf-8'))
        self.assertEqual(project['version'],'0.1.60')
        self.assertFalse(project['delete_missing'])
        self.assertEqual(project['post_build_mechanisms'],[])

if __name__=='__main__':unittest.main()
