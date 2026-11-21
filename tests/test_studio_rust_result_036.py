"""Native Studio Windows E0308 source regression; not a substitute for cargo check."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / 'tools/studio-desktop'

class NativeStudioRustResult036(unittest.TestCase):
    def test_review_persistence_returns_owned_error(self):
        rust = (STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        begin = rust.index('fn save_review(')
        end = rust.index('fn submitted_path(', begin)
        body = rust[begin:end]
        self.assertIn('fn save_review(id: &str, record: &Value) -> Result<(), String>', body)
        self.assertIn('fs::rename(&tmp, &path).map_err(|_| "Cannot finalize review update".to_string())', body)
        self.assertNotIn('fs::rename(&tmp, &path).map_err(|_| "Cannot finalize review update")',body)
        self.assertIn('file.sync_all()',body)
        self.assertIn('create_new(true)',body)

    def test_no_unused_path_import(self):
        rust = (STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        self.assertIn('use std::{fs, io::Write, path::PathBuf, process::Command};',rust)
        self.assertNotIn('path::{Path, PathBuf}',rust)
        self.assertEqual(rust.count('fn save_review('),1)

    def test_same_native_version_and_existing_authorization_gates(self):
        package = json.loads((STUDIO/'package.json').read_text(encoding='utf-8'))
        conf = json.loads((STUDIO/'src-tauri/tauri.conf.json').read_text(encoding='utf-8'))
        cfg = json.loads((ROOT/'project.zr').read_text(encoding='utf-8'))
        manifest = json.loads((ROOT/'ziprunner-manifest.json').read_text(encoding='utf-8'))
        stamp = json.loads((ROOT/'.ziprunner-post-update-tests.json').read_text(encoding='utf-8'))
        self.assertEqual({package['version'],conf['version'],cfg['version'],manifest['project']['version'],stamp['version']},{'0.1.60'})
        self.assertEqual(manifest['project']['base_version'],'0.1.58')
        self.assertLessEqual(len(stamp['tests']),20)
        self.assertFalse(cfg['delete_missing'])
        self.assertEqual(cfg['post_build_mechanisms'],[])
        frontend=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        self.assertIn('<Button isDisabled>Publish to official store — integration pending</Button>',frontend)

if __name__=='__main__':unittest.main()
