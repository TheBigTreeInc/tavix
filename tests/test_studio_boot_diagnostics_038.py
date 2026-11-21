"""0.1.40 native Studio stale-window and validator isolation regressions."""
from pathlib import Path
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools/studio-desktop'

class StudioBoot038(unittest.TestCase):
    def test_embedded_designer_catalog_is_available_without_python(self):
        rust=(STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        self.assertIn('include_str!("../../blueprints/cards-standard-54.json")',rust)
        self.assertIn('include_str!("../../blueprints/cards-back-only.json")',rust)
        self.assertIn('include_str!("../../blueprints/dice-d6-2d.json")',rust)
        self.assertIn('include_str!("../../blueprints/tarot-standard-78.json")',rust)
        body=rust.split('pub(crate) fn review_blueprints()',1)[1].split('#[tauri::command]',1)[0]
        self.assertNotIn('script_call(',body)
        self.assertIn('Value::Array(result)',body)
        for name in ['cards-standard-54','cards-back-only','dice-d6-2d','tarot-standard-78']:
            entry=json.loads((STUDIO/'blueprints'/f'{name}.json').read_text(encoding='utf-8'))
            self.assertEqual(entry['id'],name)
            self.assertEqual(entry['schema'],'tavix.studio.asset-blueprint/v1')

    def test_python_failures_are_safe_and_actionable(self):
        rust=(STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        for code in ('STUDIO_PYTHON_UNAVAILABLE','STUDIO_VALIDATOR_NO_RESPONSE','STUDIO_VALIDATOR_PROTOCOL'):
            self.assertIn(code,rust)
        self.assertNotIn('Validator did not return structured data',rust)
        self.assertIn('if output.stdout.is_empty()',rust)
        self.assertNotIn('output.stderr',rust)

    def test_failure_is_scoped_and_live_version_visible(self):
        frontend=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        self.assertIn("const STUDIO_UI_VERSION = '0.1.60'",frontend)
        self.assertIn('Studio executable and checkout versions differ',frontend)
        self.assertIn('serviceErrors.blueprints',frontend)
        self.assertIn('serviceErrors.health',frontend)
        self.assertIn('STUDIO_[A-Z0-9_]',frontend)
        self.assertIn('serviceErrors.submissions',frontend)
        self.assertIn('sourceVersion:',frontend)
        self.assertNotIn('One or more Studio services failed to initialize',frontend)
        self.assertIn('Copy diagnostic report',frontend)
        self.assertIn('Connect Tavi Assets folder',frontend)

    def test_stale_executable_refuses_to_launch_without_touching_it(self):
        source=(STUDIO/'run_windows.py').read_text(encoding='utf-8')
        self.assertIn('ready_binary(STUDIO, package_version, sources)',source)
        self.assertIn('source versions disagree',source)
        self.assertIn('Close the old Studio window',source)
        self.assertIn('subprocess.call([str(exe)]',source)
        for needle in ('os.kill(', 'shutil.rmtree(', 'remove_file(', 'powershell -Command Stop-Process'):
            self.assertNotIn(needle,source)

    def test_versions_and_approval_gates(self):
        conf=json.loads((STUDIO/'src-tauri/tauri.conf.json').read_text(encoding='utf-8'))
        pkg=json.loads((STUDIO/'package.json').read_text(encoding='utf-8'))
        for filename in ('project.zr','tavix.zr','recipes/tavix-studio.zr'):
            self.assertEqual(json.loads((ROOT/filename).read_text(encoding='utf-8'))['version'],'0.1.60')
        self.assertEqual(conf['version'],pkg['version'])
        self.assertEqual(pkg['version'],'0.1.60')
        self.assertFalse(conf['bundle']['active'])
        ui=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        self.assertIn('Publish to official store — integration pending',ui)
        self.assertIn('isDisabled',ui)
        self.assertEqual(json.loads((STUDIO/'src-tauri/capabilities/default.json').read_text(encoding='utf-8'))['permissions'],['core:default'])

if __name__=='__main__': unittest.main()
