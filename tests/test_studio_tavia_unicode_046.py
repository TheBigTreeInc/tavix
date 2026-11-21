"""TaviX 0.1.47 native Windows IPC Unicode and safe canonical-rejection regression."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / 'tools/studio-desktop'
sys.path.insert(0, str(STUDIO))
from review_cli import protocol_response
sys.path.insert(0, str(ROOT / 'tools/local_client'))
import manager_assets

class UnicodeNativeProtocol046(unittest.TestCase):
    def test_native_cli_json_is_ascii_safe_with_unicode_package_title(self):
        # A Windows redirected Python stdout pipe can use the active legacy code
        # page (e.g. CP1252). Native Rust parses stdout as UTF-8 JSON bytes.
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            path = d/'unicode.tavia'
            with zipfile.ZipFile(path,'w') as archive:
                archive.writestr('manifest.json',json.dumps({
                    'schema':'tavi.assets.pack/v1','id':'example.tarot.unicode',
                    'version':'0.1.0','type':'cards',
                    'display':{'name':'Obsidian Tarot — Étoile ☀'},
                    'resources':{'card.back':{'default':'images/back.webp'}},
                    'files':{'images/back.webp':'0'*64}
                }))
                archive.writestr('images/back.webp',b'RIFF\x00\x00\x00\x00WEBPfixture')
            process = subprocess.run([sys.executable,'-I',str(STUDIO/'review_cli.py'),
                                    'inspect',str(ROOT),str(path),'-','-'],
                                     cwd=str(ROOT),capture_output=True,timeout=12,
                                     env={**os.environ,'HOME':str(d)})
            self.assertEqual(process.returncode,0,process.stderr.decode('utf-8','replace')[:500])
            self.assertTrue(process.stdout.isascii(), 'Response must be safe even if Windows encodes ANSI')
            response = json.loads(process.stdout)
            self.assertTrue(response['ok'])
            self.assertEqual(response['result']['title'],'Obsidian Tarot — Étoile ☀')
            self.assertFalse(response['result']['canonicalValid'])
            self.assertIn('TAVIA_VALIDATOR_MISSING',{i['code'] for i in response['result']['issues']})

    def test_expected_metadata_key_is_safe_canonical_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            assets = d/'tavi-assets';(assets/'src/tavi_assets').mkdir(parents=True)
            (assets/'project.zr').write_text(json.dumps({'project_key':'tavi-assets'}),encoding='utf-8')
            (assets/'src/tavi_assets/tavia.py').write_text('# canonical source marker\n',encoding='utf-8')
            buf=io.BytesIO()
            with zipfile.ZipFile(buf,'w') as archive:
                archive.writestr('manifest.json','{}')
            mocked=subprocess.CompletedProcess(args=['python'],returncode=0,stdout=(
                manager_assets.MARKER+'{"ok":false,"reason":"invalid attribute key"}\n'),stderr='private_path')
            with patch.object(manager_assets.subprocess,'run',return_value=mocked):
                with self.assertRaises(manager_assets.AssetImportError) as captured:
                    manager_assets.inspect_tavia(buf.getvalue(),assets)
            e=captured.exception
            self.assertEqual(e.code,'TAVIA_VALIDATION_REJECTED')
            self.assertIn('invalid attribute key',e.public_message)
            self.assertNotIn('private_path',e.public_message)

    def test_unknown_validator_rejection_stays_masked(self):
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory);assets=d/'tavi-assets';(assets/'src/tavi_assets').mkdir(parents=True)
            (assets/'project.zr').write_text('{"project_key":"tavi-assets"}',encoding='utf-8')
            (assets/'src/tavi_assets/tavia.py').write_text('# canonical marker\n',encoding='utf-8')
            buf=io.BytesIO()
            with zipfile.ZipFile(buf,'w') as z:z.writestr('manifest.json','{}')
            result=subprocess.CompletedProcess(args=['python'],returncode=0,
                stdout=manager_assets.MARKER+json.dumps({'ok':False,'reason':'C:/user/private/token!'}),stderr='')
            with patch.object(manager_assets.subprocess,'run',return_value=result):
                with self.assertRaises(manager_assets.AssetImportError) as cm:
                    manager_assets.inspect_tavia(buf.getvalue(),assets)
            self.assertEqual(cm.exception.code,'TAVIA_VALIDATOR_FAILED')
            self.assertNotIn('C:/user',cm.exception.public_message)

    def test_metadata_naming_correction_does_not_waive_blueprint(self):
        text=(ROOT/'tools/studio-desktop/review_cli.py').read_text(encoding='utf8')
        self.assertIn('ensure_ascii=True',text)
        self.assertIn("BLUEPRINT_NOT_SELECTED",text)
        self.assertIn("canonical_valid and bool(identity and version)",text)
        rust=(STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf8')
        self.assertIn('serde_json::from_slice',rust)
        self.assertIn('Canonical validation and blueprint completeness must pass',rust)

if __name__=='__main__':unittest.main()
