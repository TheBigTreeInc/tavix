"""0.1.40 operator regression: distinguish canonical rejection from IPC failures."""
from contextlib import redirect_stdout
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
import review_cli as api
import studio_diagnostics as diag


class TaviaProtocol039(unittest.TestCase):
    def test_specific_canonical_adapter_failures_are_not_called_unavailable(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            adapter = home/'tools/local_client/manager_assets.py'
            adapter.parent.mkdir(parents=True)
            assets = home/'assets/src/tavi_assets/tavia.py'
            assets.parent.mkdir(parents=True)
            assets.write_text('')
            source = home/'candidate.tavia'
            source.write_bytes(b'fixture')
            template = '''class AssetImportError(ValueError):
 def __init__(self, code, message):
  super().__init__(message)
  self.code=code
  self.public_message=message

def inspect_tavia(data, assets_root):
 raise AssetImportError(%r,%r)
'''
            expectations = {
                'TAVIA_VALIDATOR_PROTOCOL': 'TAVIA_VALIDATOR_PROTOCOL',
                'TAVIA_VALIDATOR_TIMEOUT': 'TAVIA_VALIDATOR_TIMEOUT',
                'TAVIA_VALIDATOR_FAILED': 'TAVIA_VALIDATOR_FAILED',
                'TAVIA_VALIDATION_REJECTED': 'TAVIA_CANONICAL_REJECTED',
                'TAVIA_ARCHIVE_INVALID': 'TAVIA_ARCHIVE_REJECTED',
            }
            for injected, expected in expectations.items():
                with self.subTest(injected=injected):
                    adapter.write_text(template % (injected, 'Canonical validator returned no structured result'))
                    passed, code, hint = api._canonical_validation(source, 'tavia', home, home/'assets')
                    self.assertFalse(passed)
                    self.assertEqual(code, expected)
                    self.assertIn('structured result', hint)
                    self.assertNotEqual(code, 'TAVIA_VALIDATOR_UNAVAILABLE')

    def test_runtime_adapter_fault_is_sanitized_and_distinct(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            adapter = home/'tools/local_client/manager_assets.py'
            adapter.parent.mkdir(parents=True)
            assets = home/'assets/src/tavi_assets/tavia.py'
            assets.parent.mkdir(parents=True)
            assets.write_text('')
            source = home/'candidate.tavia'
            source.write_bytes(b'fixture')
            adapter.write_text('''class AssetImportError(ValueError): pass

def inspect_tavia(data, assets_root):
 raise TypeError('C:/private/folder/token=secret')
''')
            passed, code, hint = api._canonical_validation(source, 'tavia', home, home/'assets')
            self.assertFalse(passed)
            self.assertEqual(code, 'TAVIA_VALIDATOR_UNEXPECTED')
            self.assertNotIn('C:/private', hint)
            self.assertNotIn('secret', hint)

    def test_protocol_envelope_captures_noisy_print_and_unhandled_failure(self):
        with patch.object(api, 'main', side_effect=lambda _: (print('C:/user/secret'), {'value': True})[1]):
            with redirect_stdout(io.StringIO()) as stream:
                response = api.protocol_response(['test'])
            self.assertTrue(response['ok'])
            self.assertEqual(response['result'], {'value': True})
            self.assertEqual(stream.getvalue(), '')
        with patch.object(api, 'main', side_effect=TypeError('C:/private/credentials')):
            with patch.object(api, 'record_diagnostic') as sink:
                response = api.protocol_response(['test'])
            self.assertEqual(response['code'], 'REVIEW_INTERNAL_FAILURE')
            self.assertNotIn('C:/private', json.dumps(response))
            sink.assert_called_once_with('cli', ['REVIEW_INTERNAL_FAILURE'])

    def test_unrelated_pack_does_not_emit_53_missing_playing_cards(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d)/'noncards.tavia'
            manifest = {'schema': 'tavi.assets.pack/v1', 'id': 'org.example.theme',
                        'version': '1.0.0', 'type': 'theme', 'resources': {}}
            with zipfile.ZipFile(source, 'w') as z:
                z.writestr('manifest.json', json.dumps(manifest))
            wrong = api.inspect(source, ROOT, None, 'cards-standard-54')
            self.assertEqual(sum(i['code']=='BLUEPRINT_TYPE_MISMATCH' for i in wrong['issues']), 1)
            self.assertFalse(any(i['code'].startswith('BLUEPRINT_MISSING') for i in wrong['issues']))
            self.assertFalse(wrong['storeReady'])
            without = api.inspect(source, ROOT, None, '')
            self.assertIsNone(without['blueprint'])
            self.assertTrue(any(i['code']=='BLUEPRINT_NOT_SELECTED' for i in without['issues']))
            self.assertFalse(without['storeReady'])

    def test_frontend_starts_without_presuming_full_card_deck(self):
        source = (STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        self.assertIn("useState('')", source)
        dialog = (STUDIO/'src/import-setup.tsx').read_text(encoding='utf-8')
        self.assertIn('Custom / no blueprint yet', dialog)
        self.assertIn('not store-ready', dialog.lower())
        self.assertNotIn("useState('cards-standard-54')", source)
        for code in ['TAVIA_VALIDATOR_PROTOCOL','TAVIA_VALIDATOR_FAILED','TAVIA_VALIDATOR_TIMEOUT']:
            self.assertIn(code, diag.CODES)

    def test_cli_health_and_missing_archive_always_emit_json(self):
        command = [sys.executable, '-I', str(STUDIO/'review_cli.py')]
        cases = [(['health', str(ROOT),'-','sibling'], True),
                 (['inspect',str(ROOT),'/does/not/exist.tavia','-','-'], False)]
        for args, success in cases:
            with self.subTest(args=args[0]):
                completed = subprocess.run(command + args, capture_output=True, text=True, timeout=20)
                self.assertEqual(completed.returncode == 0, success)
                obj = json.loads(completed.stdout)
                self.assertEqual(obj['ok'], success)
                self.assertEqual(len(completed.stdout.splitlines()),1)
                self.assertNotIn('Traceback',completed.stdout)

    def test_real_canonical_sample_roundtrip_when_assets_source_provided(self):
        src = os.environ.get('TAVI_ASSETS_ROOT','')
        source_root = Path(src) if src else ROOT.parent/'tavi-assets'
        if not (source_root/'src/tavi_assets/tavia.py').is_file():
            self.skipTest('Canonical Assets checkout not available in this environment')
        with tempfile.TemporaryDirectory() as d:
            archive = Path(d)/'sample.tavia'
            command = [sys.executable,'-I',str(source_root/'tools/tavia.py'), 'build',
                       str(source_root/'examples/cards-v1'),str(archive)]
            result = subprocess.run(command,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            report = api.inspect(archive, ROOT, source_root, '')
            self.assertTrue(report['canonicalValid'],report['issues'])
            self.assertFalse(report['storeReady'])
            self.assertTrue(any(i['code']=='BLUEPRINT_NOT_SELECTED' for i in report['issues']))


if __name__=='__main__':
    unittest.main()
