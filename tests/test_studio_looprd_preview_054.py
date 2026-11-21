"""Native LoopRD transport and TAVIB inspection boundaries; no real network/release."""
from __future__ import annotations
import base64,hashlib,io,json,os,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools/studio-desktop'
sys.path.insert(0,str(STUDIO))
import studio_looprd_adapter as adapter
import studio_tavib as tavib
from test_studio_tavib_publishing_052 import tavib as example_tavib,blue

class LoopRDPreview054(unittest.TestCase):
    def test_approved_host_and_dapi_path_are_fully_bounded(self):
        self.assertEqual(adapter.url('https://api.example.org','/component/v2/catalog','/catalog'),
                         'https://api.example.org/component/v2/catalog')
        for host,path in [('http://api.example.org','/component/catalog'),
                          ('https://evil.org@api.example.org','/component/catalog'),
                          ('https://api.example.org','/component/../catalog'),
                          ('https://api.example.org','//catalog'),
                          ('https://api.example.org','/component/admin'),
                          ('https://api.example.org','/component/%2f/catalog')]:
            with self.subTest(host=host,path=path),self.assertRaisesRegex(adapter.RegistryError,'ENDPOINT'):
                adapter.url(host,path,'/catalog')

    def test_separate_read_and_publish_scopes_never_become_grants_from_presence(self):
        with patch.dict(os.environ,{'LOOPRD_ASSETS_READ_TOKEN':'r'*40,
                                    'LOOPRD_ASSETS_PUBLISH_TOKEN':'p'*40,
                                    'LOOPRD_ASSETS_INGEST_TOKEN':'i'*40}):
            with patch.object(adapter,'request',side_effect=lambda target,credential,op,**kwargs:
                              {'ok':True,'packs':[]} if op=='catalog' else {'ok':True,'versions':[]}):
                state=adapter.connection('https://api.example.org','/component/admin','/component/catalog')
        self.assertTrue(state['read']);self.assertTrue(state['inspect'])
        self.assertFalse(state['serverPublisherApproved'])
        self.assertEqual(state['schema'],'tavix.studio.looprd-connection/v1')
        self.assertTrue(state['ingestCredentialPresent'])

    def test_missing_scopes_fail_closed_without_network(self):
        with patch.dict(os.environ,{},clear=True),patch.object(adapter,'request') as mocked:
            state=adapter.connection('https://api.example.org','/component/admin','/component/catalog')
        self.assertFalse(state['read']);self.assertFalse(state['inspect'])
        self.assertFalse(state['publishCredentialPresent'])
        mocked.assert_not_called()

    def test_catalog_and_inspect_only_accept_valid_bounded_rows(self):
        valid={'packId':'org.tavi.example','version':'1.2.3','manifestSha256':'a'*64}
        with patch.dict(os.environ,{'LOOPRD_ASSETS_READ_TOKEN':'r'*40,'LOOPRD_ASSETS_PUBLISH_TOKEN':'p'*40}),\
             patch.object(adapter,'request',side_effect=lambda *args,**kwargs:
                          {'ok':True,'packs':[valid,dict(valid,packId='../unsafe')]}
                          if args[2]=='catalog' else
                          {'ok':True,'versions':[dict(valid,status='ready'),dict(valid,status='invalid')]}):
            self.assertEqual(len(adapter.catalog('https://api.example.org','/component/catalog')['packs']),1)
            self.assertEqual(len(adapter.inspect('https://api.example.org','/component/admin')['versions']),1)

    def test_stage_and_publish_are_unavailable_without_exact_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            a=Path(folder)/'package.tavia';a.write_bytes(b'package')
            review=Path(folder)/'review.json'
            digest=hashlib.sha256(a.read_bytes()).hexdigest()
            review.write_text(json.dumps({'sha256':digest,'kind':'tavia','status':'draft','canonicalValid':True,
                                          'storeReady':True,'packageId':'org.example','version':'1.0.0'}),encoding='utf-8')
            with patch.object(adapter,'request') as request:
                with self.assertRaisesRegex(adapter.RegistryError,'REVIEW_REQUIRED'):
                    adapter.publish('https://api.example.org','/component/admin',str(a),str(review),digest,str(Path(folder)/'missing.json'))
                request.assert_not_called()

    def test_publish_checks_ready_state_and_manifest_bound_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);pack=base/'selected.tavia';pack.write_bytes(b'exact bytes')
            digest=hashlib.sha256(pack.read_bytes()).hexdigest();review=base/'review.json'
            review.write_text(json.dumps({'sha256':digest,'kind':'tavia','status':'review_approved',
                'canonicalValid':True,'storeReady':True,'packageId':'org.tavi.example',
                'version':'1.0.0'}),encoding='utf-8')
            target='https://api.example.org/deployed/admin'; receipt=base/'approval.json'
            receipt.write_text(json.dumps({'action':'publish','packId':'org.tavi.example','version':'1.0.0',
                'manifestSha256':'b'*64,'endpoint':target}),encoding='utf-8')
            with patch.dict(os.environ,{'LOOPRD_ASSETS_PUBLISH_TOKEN':'p'*40}),                 patch.object(adapter,'inspect',return_value={'versions':[{'packId':'org.tavi.example',
                    'version':'1.0.0','status':'ready','manifestSha256':'b'*64}]}),                 patch.object(adapter,'request',return_value={'ok':True,'status':'published'}) as sent:
                result=adapter.publish('https://api.example.org','/deployed/admin',str(pack),str(review),digest,str(receipt))
                self.assertEqual(result['status'],'published')
                self.assertFalse(result['entitlementsGranted'])
                self.assertEqual(sent.call_args.args[2],'publish')
                receipt.write_text(json.dumps({'action':'publish','packId':'org.tavi.example','version':'1.0.0',
                     'manifestSha256':'0'*64,'endpoint':target}),encoding='utf-8')
                with self.assertRaisesRegex(adapter.RegistryError,'RECEIPT_INVALID'):
                    adapter.publish('https://api.example.org','/deployed/admin',str(pack),str(review),digest,str(receipt))
                self.assertEqual(sent.call_count,1)

    def test_stage_requires_valid_assets_checkout_and_exact_stage_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);pack=base/'selected.tavia';pack.write_bytes(b'exact bytes')
            digest=hashlib.sha256(pack.read_bytes()).hexdigest();review=base/'review.json';receipt=base/'stage.json'
            review.write_text(json.dumps({'sha256':digest,'kind':'tavia','status':'review_approved',
                'canonicalValid':True,'storeReady':True,'packageId':'org.tavi.example',
                'version':'1.0.0'}),encoding='utf-8')
            target='https://api.example.org/deployed/admin'
            receipt.write_text(json.dumps({'action':'stage','approvedSha256':digest,'endpoint':target}),encoding='utf-8')
            assets=base/'tavi-assets'
            with patch.dict(os.environ,{'LOOPRD_ASSETS_INGEST_TOKEN':'i'*40}),patch.object(adapter,'request') as sent:
                with self.assertRaisesRegex(adapter.RegistryError,'CANONICAL_ASSETS_REQUIRED'):
                    adapter.stage('https://api.example.org','/deployed/admin',str(pack),str(review),digest,str(receipt),str(assets))
                sent.assert_not_called()

    def test_tavib_details_show_optional_and_minimum_resources_and_safe_art(self):
        source_detail=blue()
        source_detail['description']='This application permits a partial icon set.'
        # The validated package helper checks archive integrity; mock just that step
        # to isolate exact-member inspection and display fields.
        raw=example_tavib(extra=('README.md','Redlink author notes'))
        archive=io.BytesIO()
        with zipfile.ZipFile(archive,'w') as z:z.writestr('schematics/redlink-icons.tavib',raw)
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'app.tavix';src.write_bytes(archive.getvalue())
            digest=hashlib.sha256(src.read_bytes()).hexdigest()
            with patch('studio_tavib._validated_outer',return_value=(digest,'org.tavi.redlink','0.1.30',[
                ('schematics/redlink-icons.tavib',hashlib.sha256(raw).hexdigest(),source_detail)])):
                info=tavib.inspect_member(src,ROOT,digest,'schematics/redlink-icons.tavib')
                self.assertEqual(info['requiredPrefixes'],{'redlink.icon.':1})
                self.assertEqual(info['requiredResources'],[])
                self.assertIn('author notes',info['readme'])
                self.assertFalse(info['publicationAuthorized'])
                with self.assertRaisesRegex(ValueError,'SOURCE_CHANGED'):
                    tavib.inspect_member(src,ROOT,'0'*64,'schematics/redlink-icons.tavib')
                with self.assertRaisesRegex(ValueError,'SELECTION_INVALID'):
                    tavib.inspect_member(src,ROOT,digest,'../untrusted.tavib')

    def test_optional_embedded_webp_can_be_previewed_but_is_never_executed(self):
        # Small 2x2 valid WebP, embedded as data; no image decoder or network needed.
        artwork=base64.b64decode('UklGRjwAAABXRUJQVlA4IDAAAAAQAgCdASoCAAIAAUAmJaACdLoB+AH4AAPIAP7vdtf+rPpoRf2kf/sZiCua+/kAAAA=')
        raw=example_tavib(extra=('preview.webp',artwork))
        outer=io.BytesIO()
        with zipfile.ZipFile(outer,'w') as z:z.writestr('schematics/redlink-icons.tavib',raw)
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'example.tavix';file.write_bytes(outer.getvalue())
            digest=hashlib.sha256(file.read_bytes()).hexdigest()
            with patch('studio_tavib._validated_outer',return_value=(digest,'org.tavi.redlink','0.1.30',[
                ('schematics/redlink-icons.tavib',hashlib.sha256(raw).hexdigest(),blue())])):
                result=tavib.inspect_member(file,ROOT,digest,'schematics/redlink-icons.tavib')
                self.assertEqual(base64.b64decode(result['previewBase64']),artwork)
                self.assertFalse(result['publicationAuthorized'])

    def test_native_bridge_is_renderer_secretless_and_preview_is_read_only(self):
        rust=(STUDIO/'src-tauri/src/studio_publish.rs').read_text(encoding='utf-8')
        self.assertIn('studio_looprd_connect',rust)
        self.assertIn('studio_looprd_stage',rust)
        self.assertIn('studio_looprd_publish',rust)
        self.assertIn('operator_receipt()',rust)
        self.assertNotIn('token:String',rust)
        main=(STUDIO/'src-tauri/src/lib.rs').read_text(encoding='utf-8')
        self.assertIn('review::review_tavib_detail',main)
        ui=(STUDIO/'src/tavib-import.tsx').read_text(encoding='utf-8')
        self.assertIn('Inspect blueprints from TaviX',ui)
        self.assertIn("invoke<TavibDetail>('review_tavib_detail'",ui)
        self.assertIn('designerChecklist',ui)
        self.assertIn('optionalResources',ui)
        self.assertIn('previewBase64',ui)
        publishing=(STUDIO/'src/publishing-setup.tsx').read_text(encoding='utf-8')
        self.assertIn('Connect / test permissions',publishing)
        self.assertIn('View published catalog',publishing)
        self.assertIn('Stage in LoopRD',publishing)
        self.assertIn('Publish staged pack',publishing)
        self.assertNotIn('looprd_token',publishing)

if __name__=='__main__':unittest.main()
