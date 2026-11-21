"""0.1.26 persistent operator event journal and canonical TAVIA diagnostics."""
import http.client
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.local_client.manager_events import EventJournal, MAX_EVENTS
from tools.local_client.manager_assets import inspect_tavia, AssetImportError
from tools.local_client.manager import Management

spec=importlib.util.spec_from_file_location('local_server_026', ROOT/'tools/local-client/server.py')
server=importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class StubSecrets:
    persistent=False
    def get(self,key): return None
    def put(self,key,value): pass


class EventJournalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.events=EventJournal(self.root)

    def test_restart_order_and_bounded_retention(self):
        for index in range(MAX_EVENTS+4):
            self.events.record('info','assets.import','IMPORT_CHECK','Validation event',{'sizeBytes':index})
        saved=EventJournal(self.root).list()
        self.assertEqual(len(saved['events']),MAX_EVENTS)
        self.assertEqual(saved['events'][0]['details']['sizeBytes'],MAX_EVENTS+3)
        self.assertEqual(saved['events'][-1]['details']['sizeBytes'],4)
        self.assertFalse(saved['diagnosticOnly'] is False)
        self.assertLess(self.events.path.stat().st_size,512*1024)
        if os.name!='nt': self.assertEqual(self.events.path.stat().st_mode & 0o777,0o600)
        self.assertEqual(len(EventJournal(self.root).list('error')['events']),0)

    def test_no_credentials_paths_or_unapproved_details(self):
        token='github_pat_SuperSecret987'
        event=self.events.record('error','assets.import','TAVIA_VALIDATION_REJECTED',
             'Bearer '+token+' failed at C:\\Users\\operator\\private\\tokens.txt',
             {'packId':'token='+token,'filename':'C:\\private\\sensitive',
              'sizeBytes':99,'payload':'secret'})
        data=self.events.path.read_text(encoding='utf-8')
        self.assertNotIn(token,data)
        self.assertNotIn('tokens.txt',data)
        self.assertNotIn('filename',data)
        self.assertNotIn('payload',data)
        self.assertEqual(event['details']['sizeBytes'],99)
        self.assertEqual(event['level'],'error')

    def test_filters_and_wrong_values(self):
        self.events.record('warning','assets.config','TAVIA_SOURCE_MISSING','No Assets checkout')
        self.events.record('error','assets.import','TAVIA_ARCHIVE_INVALID','Invalid archive')
        self.assertEqual(len(self.events.list('error')['events']),1)
        for value in ('trace','',None):
            with self.assertRaises(ValueError): self.events.list(value)
        with self.assertRaises(ValueError):self.events.record('info','bad invalid','OK','No')


class AssetImportDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.private=Path(self.temp.name)
        self.source=os.environ.get('TAVI_ASSETS_ROOT')
        self.manager=Management(ROOT, assets_root=self.source, private_root=self.private,secrets=StubSecrets())
        server.Handler.manager=self.manager
        server.Handler.csrf_token='test-events-csrf'
        self.httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        worker=threading.Thread(target=self.httpd.serve_forever,daemon=True)
        worker.start()
        self.addCleanup(self.httpd.server_close)
        self.addCleanup(self.httpd.shutdown)
        self.port=self.httpd.server_port

    def request(self,method,path,payload=b'',csrf=True,origin=True):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=10)
        headers={}
        if csrf:headers['X-TaviX-Local-CSRF']='test-events-csrf'
        if path == '/__manager/v1/events/client': headers['Content-Type']='application/json'
        if origin:headers['Origin']=f'http://127.0.0.1:{self.port}'
        conn.request(method,path,body=payload if method!='GET' else None,headers=headers)
        response=conn.getresponse()
        raw=response.read()
        status=response.status
        conn.close()
        return status,json.loads(raw)

    def test_failed_import_visible_and_copyable_after_restart(self):
        status,error=self.request('POST','/__manager/v1/assets/import',b'not a .tavia file')
        self.assertEqual(status,400)
        self.assertEqual(error['errorCode'],'TAVIA_ARCHIVE_INVALID')
        self.assertRegex(error['eventId'],r'^[a-f0-9]{12}$')
        status,results=self.request('GET','/__manager/v1/events?level=error')
        self.assertEqual(status,200)
        self.assertEqual(results['events'][0]['id'],error['eventId'])
        self.assertEqual(results['events'][0]['action'],'assets.import')
        self.assertEqual(results['events'][0]['details']['sizeBytes'],len(b'not a .tavia file'))
        self.assertNotIn('not a .tavia file',json.dumps(results))
        self.assertEqual(EventJournal(self.private).list('error')['events'][0]['id'],error['eventId'])

    def test_canonical_schema_validation_reason_is_exposed_without_traceback(self):
        if not self.source:self.skipTest('Canonical Assets source not provided')
        buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,'w') as z:z.writestr('manifest.json','{}')
        status,reply=self.request('POST','/__manager/v1/assets/import',buffer.getvalue())
        self.assertEqual(status,400)
        self.assertEqual(reply['errorCode'],'TAVIA_VALIDATION_REJECTED')
        self.assertIn('unsupported manifest schema',reply['error'])
        self.assertNotIn('Traceback',reply['error'])
        journal=EventJournal(self.private).list('error')['events']
        self.assertIn('unsupported manifest schema',journal[0]['message'])
        self.assertEqual(journal[0]['id'],reply['eventId'])

    def test_valid_canonical_tavia_records_success_and_draft(self):
        if not self.source:self.skipTest('Canonical Assets source not provided')
        pack=self.private/'example.tavia'
        p=subprocess.run([sys.executable,str(Path(self.source)/'tools/tavia.py'),'build',
                         str(Path(self.source)/'examples/cards-v1'),str(pack)],
                         capture_output=True,text=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr)
        status,result=self.request('POST','/__manager/v1/assets/import',pack.read_bytes())
        self.assertEqual(status,201,result)
        self.assertEqual(result['id'],'org.tavi.cards.standard')
        status,events=self.request('GET','/__manager/v1/events')
        self.assertEqual(status,200)
        self.assertEqual(events['events'][0]['code'],'TAVIA_DRAFT_VALIDATED')
        self.assertEqual(events['events'][0]['details']['packId'],result['id'])
        self.assertEqual(len(self.manager.asset_drafts()),1)

    def test_cross_origin_deny_logged_without_sensitive_payload(self):
        evil=b'github_pat_fake-secret-token'
        status,result=self.request('POST','/__manager/v1/assets/import',evil,origin=False)
        self.assertEqual(status,403)
        self.assertEqual(result['errorCode'],'REQUEST_INVALID')
        data=self.manager.events.path.read_text(encoding='utf-8')
        self.assertNotIn('github_pat_',data)
        self.assertIn('approval required',data)

    def test_browser_error_codes_only(self):
        for code,ok in [('UI_UNCAUGHT_ERROR',True),('UI_NETWORK_ERROR',True),('token=secret',False)]:
            status,result=self.request('POST','/__manager/v1/events/client',
                         json.dumps({'code':code}).encode())
            self.assertEqual(status,201 if ok else 400)
        self.assertEqual(len(self.manager.events.list()['events']),3)
        self.assertNotIn('token=secret',self.manager.events.path.read_text(encoding='utf-8'))

    def test_view_has_diagnostics_and_download_without_secrets(self):
        html=(ROOT/'tools/local-client/index.html').read_text(encoding='utf-8')
        js=(ROOT/'tools/local-client/manager.js').read_text(encoding='utf-8')
        for token in ('id="events"','id="eventList"','id="eventCopy"','id="eventExport"'):
            self.assertIn(token,html)
        self.assertIn('navigator.clipboard.writeText',js)
        self.assertIn('refreshEvents',js)
        self.assertNotIn('localStorage',js)
        self.assertIn('sandbox="allow-scripts allow-forms"',html)


if __name__=='__main__':unittest.main()
