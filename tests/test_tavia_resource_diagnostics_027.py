"""TaviX 0.1.27: explain canonical TAVIA suffix failures, without changing policy."""
import http.client
import importlib.util
import json
import threading
from http.server import ThreadingHTTPServer
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.local_client.manager_assets import (
    inspect_tavia, AssetImportError, _unsupported_resource_diagnostic,
    TAVIA_RESOURCE_SUFFIXES,
)
from tools.local_client.manager_events import EventJournal


def archive_with(*members):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json', '{"schema":"tavi.assets.pack/v1"}')
        for name in members:
            z.writestr(name, b'data')
    return out.getvalue()


class InvalidAssetResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = os.environ.get('TAVI_ASSETS_ROOT')

    def test_offending_member_is_identified_after_canonical_rejection(self):
        if not self.assets: self.skipTest('TAVI_ASSETS_ROOT required')
        with self.assertRaises(AssetImportError) as result:
            inspect_tavia(archive_with('docs/README.md'), self.assets)
        self.assertEqual(result.exception.code, 'TAVIA_VALIDATION_REJECTED')
        self.assertIn('docs/README.md', result.exception.public_message)
        self.assertIn('Remove or convert', result.exception.public_message)
        self.assertIn('.tavix', result.exception.public_message)

    def test_multiple_unsupported_extensions_are_bounded(self):
        data=archive_with('scripts/boot.js', 'css/theme.css','images/a.png')
        name,count,types = _unsupported_resource_diagnostic(data)
        self.assertEqual(name, 'scripts/boot.js')
        self.assertEqual(count, 2)
        self.assertEqual(types, '.css, .js')
        self.assertNotIn('.png',types)

    def test_malicious_names_not_exposed(self):
        for member in ('ghp_Secret1234.md','token=SECRET.md',
                       '../private.txt','secret/keys.env', 'C:\\Users\\hello.txt'):
            name,count,types = _unsupported_resource_diagnostic(archive_with(member))
            self.assertEqual(count, 1)
            self.assertEqual(name, '[unsafe archive member name hidden]', member)
            self.assertNotIn('Secret1234',str((name,types)))

    def test_no_false_hint_for_permitted_extension(self):
        name,count,types = _unsupported_resource_diagnostic(archive_with('media/image.webp'))
        self.assertEqual((name,count,types), ('',0,''))
        self.assertIn('.webp', TAVIA_RESOURCE_SUFFIXES)

    def test_no_injection_from_corrupt_zip(self):
        self.assertEqual(_unsupported_resource_diagnostic(b'not zip'), ('',0,''))


    def test_http_event_id_and_rejected_member(self):
        if not self.assets: self.skipTest('TAVI_ASSETS_ROOT required')
        from tools.local_client.manager import Management
        class StubSecrets:
            persistent=False
            def get(self,key): return None
            def put(self,key,value): pass
        spec=importlib.util.spec_from_file_location('tavix_027_server', ROOT/'tools/local-client/server.py')
        server=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        with tempfile.TemporaryDirectory() as d:
            manager=Management(ROOT,assets_root=self.assets,private_root=d,secrets=StubSecrets())
            server.Handler.manager=manager
            server.Handler.csrf_token='test-csrf-027'
            listener=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
            worker=threading.Thread(target=listener.serve_forever,daemon=True)
            worker.start()
            try:
                port=listener.server_port
                conn=http.client.HTTPConnection('127.0.0.1',port,timeout=10)
                conn.request('POST','/__manager/v1/assets/import',archive_with('docs/README.md'),
                  headers={'Origin':f'http://127.0.0.1:{port}','X-TaviX-Local-CSRF':'test-csrf-027'})
                response=conn.getresponse()
                self.assertEqual(response.status,400)
                body=json.loads(response.read());conn.close()
                self.assertEqual(body['errorCode'],'TAVIA_VALIDATION_REJECTED')
                self.assertIn('docs/README.md',body['error'])
                self.assertRegex(body['eventId'],r'^[a-f0-9]{12}$')
                saved=EventJournal(d).list('error')['events'][0]
                self.assertEqual(saved['id'],body['eventId'])
                self.assertIn('docs/README.md',saved['message'])
            finally:
                listener.shutdown()
                listener.server_close()

    def test_diagnostic_roundtrip_to_redacted_event(self):
        if not self.assets: self.skipTest('TAVI_ASSETS_ROOT required')
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(AssetImportError) as failure:
                inspect_tavia(archive_with('docs/README.md'), self.assets)
            journal=EventJournal(d)
            saved=journal.record('error','assets.import',failure.exception.code,
                                 failure.exception.public_message, {'format':'tavia'})
            report=EventJournal(d).list('error')['events'][0]
            self.assertEqual(saved['id'],report['id'])
            self.assertIn('README.md',report['message'])
            self.assertNotIn('/tmp/',report['message'])


if __name__ == '__main__': unittest.main()
