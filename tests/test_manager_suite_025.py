"""Local management suite: negative and exact-approval gates, no live mutations."""
import http.client
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer

from tools.local_client.manager import Management, checked_https, safe_json
from tools.local_client.manager_assets import inspect_tavia

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'tools/local-client/server.py'
spec=importlib.util.spec_from_file_location('local_server_025',PATH)
server=importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class MemoryCredentials:
    persistent=False
    def __init__(self): self.stored={}
    def get(self,key):return self.stored.get(key)
    def put(self,key,value):self.stored[key]=value


class ManagementSuiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.secrets=MemoryCredentials()
        self.mgr=Management(ROOT,private_root=Path(self.tmp.name),secrets=self.secrets)

    def test_private_state_cannot_live_under_source_checkout(self):
        with self.assertRaises(ValueError):Management(ROOT,private_root=ROOT/'.secrets-test',secrets=self.secrets)

    def test_catalog_and_git_baseline_and_no_auto_publish(self):
        j=self.mgr.bootstrap()
        self.assertEqual(j['schema'],'tavix.manager/v1')
        self.assertTrue(any(x['id']=='inc.thebigtree.tavi.klondike' for x in j['catalog']))
        self.assertFalse(j['remoteMutationsEnabled'])
        self.assertFalse(j['walletMutationsEnabled'])
        self.assertFalse(j['git']['pushAuthorized'])
        self.assertNotIn('csrf',j)

    def test_price_draft_does_not_change_repository_and_rejects_bad_values(self):
        catalog_before=(ROOT/'tavi.repository.json').read_bytes()
        value={'kind':'asset-object','packId':'org.tavi.cards.standard','id':'cards.spades.ace','version':'1.0.0','priceGold':20}
        self.assertEqual(self.mgr.set_price_draft(value)['state'],'local_proposal_only')
        self.assertEqual(self.mgr.price_drafts()[0]['priceGold'],20)
        with self.assertRaises(ValueError):self.mgr.set_price_draft({k:v for k,v in value.items() if k!='packId'})
        self.assertEqual(catalog_before,(ROOT/'tavi.repository.json').read_bytes())
        for invalid in [-1,1_000_001,True,1.5,'20']:
            with self.assertRaises(ValueError):self.mgr.set_price_draft({**value,'priceGold':invalid})
        with self.assertRaises(ValueError):self.mgr.set_price_draft({**value,'token':'x'})
        self.assertFalse((ROOT/'prices.json').exists())

    def test_reject_cross_origin_and_hostile_endpoints(self):
        for url in ('http://example.com/admin','https://x/admin?token=secret','https://user:pw@x/admin',
                    'https://x/other','https://x/a/../admin'):
            with self.assertRaises(ValueError):checked_https(url,'/admin')
        self.assertEqual(checked_https('https://example.com/dapi/admin','/admin'), 'https://example.com/dapi/admin')
        self.assertNotIn('token',safe_json({'ok':True,'token':'test','nested':{'privateToken':'abc','status':'ready'}}))

    def test_remote_actions_require_separate_receipts_and_credentials(self):
        digest='a'*64
        self.mgr._settings.update({'looprdAdmin':'https://example.com/dapi/admin',
                                    'looprdCatalog':'https://example.com/dapi/catalog'})
        with self.assertRaises(ValueError):self.mgr.stage_tavia({'sha256':digest,'receipt':{'action':'publish'}})
        with self.assertRaises(ValueError):self.mgr.transition_tavia({'action':'publish','packId':'org.tavi.cards.standard',
            'version':'1.0.0','manifestSha256':digest,'receipt':{'action':'stage'}})
        valid={'action':'publish','packId':'org.tavi.cards.standard','version':'1.0.0',
               'manifestSha256':digest,'endpoint':self.mgr._settings['looprdAdmin']}
        with self.assertRaises(ValueError):self.mgr.transition_tavia({**valid,'receipt':valid})
        self.assertFalse(self.secrets.stored)

    def test_exact_receipt_routes_through_existing_assets_operator_tools(self):
        root=os.environ.get('TAVI_ASSETS_ROOT')
        if not root:self.skipTest('Optional canonical Assets source missing')
        digest='b'*64
        self.mgr.assets_root=Path(root)
        self.mgr._settings['looprdAdmin']='https://example.invalid/dapi/admin'
        archive=self.mgr.private/'asset-drafts'/(digest+'.tavia')
        archive.parent.mkdir(parents=True)
        payload=b'draft-payload'
        digest=__import__('hashlib').sha256(payload).hexdigest()
        archive.unlink(missing_ok=True)
        archive=self.mgr.private/'asset-drafts'/(digest+'.tavia')
        archive.write_bytes(payload)
        self.mgr._write_json('assets.json',{digest:{'id':'org.test.pack','sha256':digest}})
        stage_receipt={'action':'stage','approvedSha256':digest,'endpoint':self.mgr._settings['looprdAdmin']}
        with patch.object(self.mgr,'_run_assets_operator',return_value={'ok':True,'action':'staged_only'}) as call:
            result=self.mgr.stage_tavia({'sha256':digest,'receipt':stage_receipt})
            self.assertEqual(result['action'],'staged_only')
            self.assertIn('ziprunner-tavia-postrun.py',call.call_args.args[0][0])
            self.assertEqual(call.call_args.args[1],'looprd_ingest')
        manifest='a'*64
        pub_receipt={'action':'publish','packId':'org.test.pack','version':'1.0.0',
                     'manifestSha256':manifest,'endpoint':self.mgr._settings['looprdAdmin']}
        with patch.object(self.mgr,'_run_assets_operator',return_value={'ok':True}) as call:
            self.mgr.transition_tavia({k:v for k,v in pub_receipt.items() if k!='endpoint'} | {'receipt':pub_receipt})
            self.assertIn('looprd-registry.py',call.call_args.args[0][0])
            self.assertEqual(call.call_args.args[1],'looprd_publish')

    @patch('tools.local_client.manager.api_request')
    def test_github_connection_only_uses_readonly_identity_and_redacts(self, remote):
        remote.side_effect=[{'login':'operator'},{'full_name':'TheBigTreeInc/tavix','private':False,'permissions':{'push':True}}]
        token='github-token-not-real-credential'
        result=self.mgr.connect_github({'repository':'TheBigTreeInc/tavix','token':token})
        self.assertEqual(result['login'],'operator')
        self.assertNotIn(token,json.dumps(self.mgr.bootstrap()))
        self.assertEqual([x.args[0] for x in remote.call_args_list],
                         ['https://api.github.com/user','https://api.github.com/repos/TheBigTreeInc/tavix'])

    def test_looprd_connection_is_secretless_in_bootstrap(self):
        data={'catalog':'https://looprd.example/dapi/catalog','admin':'https://looprd.example/dapi/admin',
              'readToken':'read-not-a-real-token-long','ingestToken':'ingest-not-a-real-token-long','publishToken':''}
        self.mgr.connect_looprd(data)
        state=json.dumps(self.mgr.bootstrap())
        self.assertNotIn('read-not-a-real',state)
        self.assertNotIn('ingest-not-a-real',state)
        self.assertIn('looprd.example',state)
        self.assertEqual(self.mgr._settings['looprdAdmin'],data['admin'])

    def test_actual_http_rejects_untrusted_mutations(self):
        server.Handler.manager=self.mgr
        server.Handler.csrf_token='test-csrf-approval'
        httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        self.addCleanup(httpd.server_close)
        worker=threading.Thread(target=httpd.serve_forever,daemon=True);worker.start()
        self.addCleanup(httpd.shutdown)
        port=httpd.server_port
        conn=http.client.HTTPConnection('127.0.0.1',port,timeout=4)
        self.addCleanup(conn.close)
        conn.request('GET','/__manager/v1/bootstrap')
        response=conn.getresponse();bootstrap=json.loads(response.read())
        self.assertEqual(response.status,200)
        self.assertEqual(bootstrap['csrf'],'test-csrf-approval')
        for origin,csrf in [('http://attacker.invalid','test-csrf-approval'),
                            (f'http://127.0.0.1:{port}','wrong')]:
            conn.request('POST','/__manager/v1/prices',body=json.dumps({'id':'org.test','version':'1.0.0',
                 'kind':'game','priceGold':0}),headers={'Content-Type':'application/json',
                 'Origin':origin,'X-TaviX-Local-CSRF':csrf})
            result=conn.getresponse();result.read();self.assertEqual(result.status,403)
        self.assertEqual(self.mgr.price_drafts(),[])

    def test_browser_has_separate_credential_and_preview_boundary(self):
        html=(ROOT/'tools/local-client/index.html').read_text(encoding='utf-8')
        script=(ROOT/'tools/local-client/manager.js').read_text(encoding='utf-8')
        self.assertIn('sandbox="allow-scripts allow-forms"',html)
        self.assertNotIn('allow-same-origin',html)
        for name in ('overview','packages','assets','storefront','connections','operations'):
            self.assertIn('id="'+name+'"',html)
        self.assertNotIn('localStorage',script)
        self.assertNotIn('Bearer ',script)
        self.assertIn('X-TaviX-Local-CSRF',script)
        self.assertIn('openEditorFull',script)

    def test_tavia_uses_assets_own_validator_when_available(self):
        root=os.environ.get('TAVI_ASSETS_ROOT')
        if not root:self.skipTest('Optional native Assets checkout path not supplied')
        import subprocess, sys
        with tempfile.TemporaryDirectory() as temp:
            archive=Path(temp)/'cards.tavia'
            result=subprocess.run([sys.executable,str(Path(root)/'tools/tavia.py'),'build',
                                   str(Path(root)/'examples/cards-v1'),str(archive)],
                                  capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)
            meta=inspect_tavia(archive.read_bytes(),root)
            self.assertEqual(meta['id'],'org.tavi.cards.standard')
            self.assertIn('card.back',meta['resources'])
            mgr=Management(ROOT,assets_root=root,private_root=Path(self.tmp.name),secrets=self.secrets)
            self.assertEqual(mgr.import_tavia(archive.read_bytes())['status'],'validated_local_draft')
            self.assertEqual(len(mgr.asset_drafts()),1)
            with self.assertRaises(ValueError):inspect_tavia(b'not a zip',root)


if __name__=='__main__':unittest.main()
