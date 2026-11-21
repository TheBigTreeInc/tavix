"""TaviX 0.1.37 diagnostic and local Assets connection source regressions."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT/'tools/studio-desktop'
sys.path.insert(0,str(STUDIO))
import review_cli as api
import studio_diagnostics as diag


class StudioDiagnostics037(unittest.TestCase):
    def test_health_no_assets_is_actionable_and_does_not_claim_remote_connection(self):
        report = diag.health(ROOT,None,'sibling')
        status = {c['id']:c for c in report['checks']}
        self.assertEqual(status['tavia-validator']['code'],'TAVIA_SOURCE_MISSING')
        self.assertIn('Select',status['tavia-validator']['nextStep'])
        self.assertEqual(status['github']['status'],'ready' if (ROOT/'tools/studio-desktop/studio_release_gateway.py').is_file() else 'pending')
        self.assertIn('Publishing',status['github']['nextStep'] if status['github']['status']=='ready' else status['github']['message']+' '+status['github']['nextStep'])
        self.assertEqual(status['looprd']['status'],'ready' if (ROOT/'tools/studio-desktop/studio_looprd_adapter.py').is_file() else 'pending')
        self.assertEqual(status['tavix-validator']['status'], 'ready' if (ROOT/'tools/tavix_package.py').is_file() else 'blocked')
        self.assertNotIn(str(ROOT),json.dumps(report))
        self.assertNotIn('password',json.dumps(report))

    def test_connectivity_probe_detects_good_source_and_rejects_wrong_identity(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p/'src/tavi_assets').mkdir(parents=True)
            (p/'src/tavi_assets/__init__.py').write_text('')
            (p/'src/tavi_assets/tavia.py').write_text('def unpack_tavia(source, target):\n    pass\n')
            (p/'project.zr').write_text(json.dumps({'project_key':'tavi-assets'}))
            self.assertEqual([c for c in diag.health(ROOT,p,'operator')['checks'] if c['id']=='tavia-validator'][0]['status'],'ready')
            (p/'project.zr').write_text(json.dumps({'project_key':'tavix'}))
            self.assertEqual([c for c in diag.health(ROOT,p,'operator')['checks'] if c['id']=='tavia-validator'][0]['status'],'blocked')

    def test_readonly_json_report_never_echoes_a_poisoned_private_log(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(diag,'_private_journal',return_value=Path(d)/'diagnostics.json'):
                diag.record('inspect',['ARCHIVE_REJECTED','INSPECT_OK'],'tavia','a'*64)
                diag.record('inspect',['ARCHIVE_REJECTED'], 'tavia', 'b'*64)
                path=Path(d)/'diagnostics.json'
                items=json.loads(path.read_text(encoding='utf-8'))
                self.assertEqual(len(items),3)
                items.append({'at':'C:/Users/me/secret token','code':'ARCHIVE_REJECTED','operation':'inspect','path':'C:/private'})
                path.write_text(json.dumps(items))
                output=diag.recent()
                self.assertEqual(len(output),3)
                self.assertNotIn('C:/',json.dumps(output))
                self.assertNotIn('path',json.dumps(output))
                for i in range(100):diag.record('inspect',['INSPECT_OK'],'tavix', 'c'*64)
                self.assertLessEqual(len(diag.recent()),48)

    def test_invalid_display_type_and_archive_report_without_exception_path(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'invalid.tavia'
            manifest={'schema':'tavi.assets.pack/v1','id':'org.example.invalid','version':'1.0.0',
                'display':'not a mapping','type':'playing-cards','resources':{}}
            with zipfile.ZipFile(p,'w') as z:z.writestr('manifest.json',json.dumps(manifest))
            report=api.inspect(p,ROOT,None,'cards-back-only')
            self.assertFalse(report['canonicalValid'])
            self.assertTrue(any(i['code']=='TAVIA_VALIDATOR_MISSING' for i in report['issues']))
            self.assertNotIn(str(p),json.dumps(report))

    def test_isolated_python_cli_returns_structured_health_without_paths(self):
        with tempfile.TemporaryDirectory() as d:
            command=[sys.executable,'-I',str(STUDIO/'review_cli.py'),'health',str(ROOT),'-','sibling']
            result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'HOME':d},timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads(result.stdout)
            self.assertTrue(report['ok'])
            self.assertEqual(report['result']['schema'],diag.SCHEMA)
            self.assertNotIn(d,result.stdout)
            self.assertNotIn(str(ROOT),result.stdout)

    def test_native_connection_preferences_and_diagnostics_are_local_only(self):
        lib=(STUDIO/'src-tauri/src/lib.rs').read_text(encoding='utf-8')
        connection=(STUDIO/'src-tauri/src/studio_connection.rs').read_text(encoding='utf-8')
        review=(STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        ui=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        self.assertIn('studio_connection::studio_connect_assets',lib)
        self.assertIn('studio_connection::studio_health',lib)
        self.assertIn('studio_connect_assets',ui)
        self.assertIn('studio_reset_assets',ui)
        self.assertIn('Copy diagnostic report',ui)
        self.assertIn('recentAttempts',ui)
        self.assertIn('rfd::FileDialog',connection)
        self.assertIn('project_key',connection)
        self.assertIn('tavi-assets',connection)
        self.assertIn('assets-source.json',connection)
        self.assertIn('super::studio_connection::assets_checkout()',review)
        for phrase in ('Command::new("git")','reqwest','tauri_plugin_http','publish_to_store'):
            self.assertNotIn(phrase,connection)
        caps=json.loads((STUDIO/'src-tauri/capabilities/default.json').read_text(encoding='utf-8'))
        self.assertEqual(caps['permissions'],['core:default'])

if __name__ == '__main__':unittest.main()
