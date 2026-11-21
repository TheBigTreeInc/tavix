"""Bounded TAVIB + live GitHub publication gateway source and behavioral checks.

No real network, CLI authentication, release or untrusted app execution is used.
"""
from __future__ import annotations
import hashlib, io, json, os, sys, tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools/studio-desktop'
sys.path.insert(0,str(STUDIO))
from studio_tavib import CONTAINER_SCHEMA,parse_tavib,discover,import_selected
from studio_blueprint_library import load,app_origin
from studio_release_gateway import releases, draft, publish, receipt, connection

def blue():
    return {'schema':'tavix.studio.asset-blueprint/v1','id':'redlink-icons','version':'1.0.0',
      'title':'Redlink optional device icons','description':'A partial pack is fine.',
      'applicablePackTypes':['redlink-icons'],'requiredResources':[],
      'requiredPrefixes':{'redlink.icon.':1},'optionalResources':[],
      'designerChecklist':['Check mobile readability.']}

def tavib(manifest_override=None,extra=None):
    b=json.dumps(blue(),separators=(',',':')).encode()
    m={'schema':CONTAINER_SCHEMA,'id':'redlink-icons','version':'1.0.0',
       'blueprintSha256':hashlib.sha256(b).hexdigest()}
    if manifest_override:m.update(manifest_override)
    file=io.BytesIO()
    with zipfile.ZipFile(file,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json',json.dumps(m));z.writestr('blueprint.json',b)
        if extra:z.writestr(*extra)
    return file.getvalue()

class StudioTavibPublisher052(unittest.TestCase):
    def test_tavib_accepts_partial_minimum_not_full_icon_set(self):
        data=parse_tavib(tavib())
        self.assertEqual(data['requiredPrefixes'],{'redlink.icon.':1})
        self.assertEqual(data['requiredResources'],[])

    def test_portable_blueprint_builder_is_deterministic(self):
        from build_tavib import build
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            src=ROOT/'examples/studio-blueprints/redlink-network-icons.json'
            a=base/'a.tavib';b=base/'b.tavib'
            build(src,a);build(src,b)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            parsed=parse_tavib(a.read_bytes())
            self.assertEqual(parsed['requiredPrefixes'],{'redlink.network.icon.':1})
            with self.assertRaisesRegex(ValueError,'Output must be a new'):build(src,a)

    def test_tavib_fails_closed_for_wrong_digest_unknown_members_and_zip_size(self):
        for b in (tavib({'blueprintSha256':'0'*64}),tavib(extra=('script.js','alert(1)')),
                  tavib(extra=('../escape.webp','xyz')),b'PK'+'x'.encode()*140000):
            with self.subTest(size=len(b)),self.assertRaises(Exception):parse_tavib(b)

    def test_discovery_and_import_keep_provenance_immutable(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp);source=base/'redlink.tavix';source.write_bytes(b'a safe exact-hash stand-in')
            sha=hashlib.sha256(source.read_bytes()).hexdigest()
            candidates=[('schematics/redlink-icons.tavib',hashlib.sha256(tavib()).hexdigest(),blue())]
            with patch('studio_tavib._validated_outer',return_value=(sha,'org.tavi.redlink','0.1.30',candidates)), \
                 patch.dict(os.environ,{'HOME':temp,'LOCALAPPDATA':temp}):
                report=discover(source,ROOT)
                self.assertEqual(report['appId'],'org.tavi.redlink')
                self.assertEqual(len(report['candidates']),1)
                saved=import_selected(source,ROOT,sha,[report['candidates'][0]['member']])
                self.assertEqual(saved['publication'],False)
                local_id=saved['ids'][0]
                self.assertTrue(local_id.startswith('local-app-'))
                imported,_=load(ROOT,local_id)
                self.assertEqual(imported['requiredPrefixes'],{'redlink.icon.':1})
                self.assertEqual(app_origin(local_id)['upstreamId'],'redlink-icons')
                with self.assertRaisesRegex(ValueError,'TAVIB_ALREADY_IMPORTED'):
                    import_selected(source,ROOT,sha,[report['candidates'][0]['member']])
                with self.assertRaisesRegex(ValueError,'TAVIB_SOURCE_CHANGED'):
                    import_selected(source,ROOT,'0'*64,[report['candidates'][0]['member']])

    def test_release_gateway_rejects_absent_review_and_unapproved_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);pack=root/'package.tavia';pack.write_bytes(b'hello')
            record=root/'review.json';digest=hashlib.sha256(pack.read_bytes()).hexdigest()
            record.write_text(json.dumps({'sha256':digest,'status':'draft','canonicalValid':True,
                                          'storeReady':True,'kind':'tavia','packageId':'org.redlink','version':'1.0.0'}),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'RELEASE_APPROVAL_REQUIRED'):
                draft('TheBigTreeInc/tavi-assets',pack,record,digest)
            self.assertFalse((root/'publication-receipts').exists())

    def test_release_create_and_publish_are_two_explicit_separate_gh_actions(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);root=base/'studio';(root/'reviews').mkdir(parents=True);(root/'submissions').mkdir()
            package=root/'submissions/a.tavia';package.write_bytes(b'fixed approved pack')
            digest=hashlib.sha256(package.read_bytes()).hexdigest()
            record=root/'reviews'/(digest+'.json')
            record.write_text(json.dumps({'sha256':digest,'status':'review_approved','canonicalValid':True,
                    'storeReady':True,'kind':'tavia','packageId':'org.tavi.redlink','version':'1.2.0'}),encoding='utf-8')
            calls=[]
            with patch('studio_release_gateway.connection',return_value={'authenticated':True}),\
                 patch('studio_release_gateway._gh',side_effect=lambda args,**kw:calls.append(args) or b''):
                drafted=draft('TheBigTreeInc/tavi-assets',package,record,digest)
                self.assertEqual(drafted['status'],'draft')
                self.assertIn('--draft',calls[0])
                self.assertNotIn('--draft=false',calls[0])
                with self.assertRaisesRegex(ValueError,'RELEASE_ALREADY_PREPARED'):
                    draft('TheBigTreeInc/tavi-assets',package,record,digest)
                self.assertEqual(receipt(digest,record)['status'],'draft')
                live=publish('TheBigTreeInc/tavi-assets',record,digest)
                self.assertEqual(live['status'],'public')
                self.assertIn('--draft=false',calls[-1])
                self.assertEqual(receipt(digest,record)['status'],'public')
            self.assertEqual(len(calls),2)
            self.assertFalse(drafted['officialStorePublished'])

    def test_release_list_does_not_confuse_github_with_official_store(self):
        import studio_release_gateway as gateway
        response=[{'name':'Redlink','tag_name':'tavi-tavix-org.tavi.redlink-v1.0.0',
                   'html_url':'https://github.com/TheBigTreeInc/tavi-assets/releases/tag/tavi-tavix-org.tavi.redlink-v1.0.0',
                   'published_at':'2026-11-17T10:00:00Z','draft':False,'prerelease':False}]
        with patch.object(gateway,'connection',return_value={'authenticated':False,'code':'GITHUB_AUTH_REQUIRED'}),\
             patch.object(gateway,'_fetch_public',return_value=json.dumps(response).encode()),\
             patch.object(gateway,'public_catalog',return_value={'status':'not_published','code':'CATALOG_NOT_FOUND'}):
            info=releases('TheBigTreeInc/tavi-assets')
        self.assertEqual(info['scope'],'public_only')
        self.assertFalse(info['officialStorePublished'])
        self.assertEqual(len(info['releases']),1)
        with self.assertRaises(ValueError):releases('https://evil.test/')

    def test_native_transport_does_not_accept_renderer_paths_or_tokens(self):
        rust=(STUDIO/'src-tauri/src/studio_publish.rs').read_text(encoding='utf-8')
        self.assertIn('fn approved_record(digest: &str)',rust)
        self.assertIn('confirm_digest!=digest',rust)
        self.assertIn('public_distribution_approved',rust)
        self.assertNotIn('github_token',rust)
        self.assertIn('studio_github_create_draft',rust)
        self.assertIn('studio_github_publish_draft',rust)
        importer=(STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        self.assertIn('rfd::FileDialog::new().add_filter("TaviX app with blueprints"',importer)
        self.assertIn('script_call("tavib_discover"',importer)
        frontend=(STUDIO/'src/publishing-setup.tsx').read_text(encoding='utf-8')
        self.assertIn('Publish GitHub draft publicly',frontend)
        self.assertIn('LoopRD registry publication and entitlements remain separate',frontend)

if __name__=='__main__':unittest.main()
