"""0.1.47: read-only package contents, safe previews, hidden CLI, pub destinations."""
from pathlib import Path
import base64
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / 'tools/studio-desktop'
sys.path.insert(0, str(STUDIO))
from studio_pack_catalog import catalog,preview,_safe_svg

SVG=(b'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
     b'<rect x="0" y="0" width="100" height="100" fill="#123456"/></svg>')


def fixture(root,kind='tavia'):
    path=root / ('pack.' + kind)
    digest=hashlib.sha256(SVG).hexdigest()
    m={'schema':'tavi.assets.pack/v1','id':'org.sample.cards','version':'0.1.0',
       'type':'playing-cards','files':{'assets/ace.svg':digest},
       'resources':{'card.face.spades.ace':{'default':'assets/ace.svg'}},
       'objects':{'ace':{'kind':'playing-card','name':'Ace','resources':['card.face.spades.ace']}},
       'collections':{'deck':{'kind':'deck','name':'Deck','entries':[{'objectId':'ace','quantity':1}]}}}
    lock={'schema':'tavix.package/v1','standard':'tavix/1.0','files':[{'path':'assets/ace.svg','sha256':digest,'size':len(SVG)}]}
    if kind=='tavix':m={'schema':'tavi.extension/v1','id':'org.sample.app','version':'0.1.0','classification':{'type':'game'},'assetDependencies':[{'packId':'org.sample.cards','required':False}]}
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('manifest.json',json.dumps(m));z.writestr('assets/ace.svg',SVG)
        if kind=='tavix':z.writestr('tavix.lock.json',json.dumps(lock))
    return path

class PackageBrowser041(unittest.TestCase):
    def test_tavia_catalog_has_complete_resource_object_collection_and_files(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(Path(d))
            for section,total in [('resources',1),('objects',1),('collections',1),('files',2),('dependencies',0)]:
                row=catalog(p,'tavia',section,0,40)
                self.assertEqual(row['total'],total)
            self.assertEqual(catalog(p,'tavia','resources',0,40)['items'][0]['path'],'assets/ace.svg')
            self.assertEqual(catalog(p,'tavia','objects',0,40)['items'][0]['name'],'Ace')
            self.assertEqual(catalog(p,'tavia','collections',0,40)['items'][0]['entries'],1)
            self.assertEqual(catalog(p,'tavia','summary',0,40)['items'][0]['counts']['objects'],1)

    def test_exact_original_svg_preview_without_canonical_approval(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(Path(d))
            result=preview(p,'tavia','assets/ace.svg')
            self.assertEqual(result['mime'],'image/svg+xml')
            self.assertEqual(base64.b64decode(result['dataUrl'].split(',',1)[1]),SVG)

    def test_tavix_archive_and_dependencies_browse_without_execute(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(Path(d),'tavix')
            self.assertEqual(catalog(p,'tavix','summary',0,40)['items'][0]['counts']['dependencies'],1)
            self.assertEqual(catalog(p,'tavix','dependencies',0,40)['items'][0]['packId'],'org.sample.cards')
            self.assertEqual(base64.b64decode(preview(p,'tavix','assets/ace.svg')['dataUrl'].split(',',1)[1]),SVG)

    def test_traversal_unlisted_modified_and_scripts_are_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(Path(d))
            with self.assertRaisesRegex(ValueError,'Preview type unavailable'):preview(p,'tavia','../private.svg')
            with self.assertRaisesRegex(ValueError,'Preview member unavailable'):preview(p,'tavia','assets/missing.svg')
            script=b'<svg xmlns="http://www.w3.org/2000/svg"><script>evil()</script></svg>'
            self.assertFalse(_safe_svg(script))
            self.assertFalse(_safe_svg(b'<svg><image href="https://bad.example.org/x"/></svg>'))
            self.assertFalse(_safe_svg(b'<!DOCTYPE svg><svg/>'))
            with zipfile.ZipFile(p,'a') as z:z.writestr('assets/unlisted.svg',script)
            with self.assertRaisesRegex(ValueError,'Artwork not declared'):preview(p,'tavia','assets/unlisted.svg')

    def test_digest_bound_cli_archive_and_private_paths_not_echoed(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(Path(d)); digest=hashlib.sha256(p.read_bytes()).hexdigest()
            def command(sha):
                result=subprocess.run([sys.executable,'-I',str(STUDIO/'review_cli.py'),'catalog',str(ROOT),str(p),sha,'resources','0','40'],capture_output=True,text=True)
                return json.loads(result.stdout),result
            ok,call=command(digest)
            self.assertEqual(call.returncode,0)
            self.assertEqual(ok['result']['total'],1)
            bad,call=command('0'*64)
            self.assertNotEqual(call.returncode,0)
            self.assertNotIn(str(p),call.stdout)
            self.assertEqual(bad['code'],'REVIEW_OPERATION_REJECTED')

    def test_official_registry_still_config_only_while_github_release_requires_review(self):
        source=(STUDIO/'src-tauri/src/studio_publish.rs').read_text(encoding='utf-8')
        self.assertIn('remotePublishAvailable',source)
        self.assertIn('"remotePublishAvailable":false',source)
        self.assertIn('"githubWriteAuthorized":false',source)
        self.assertIn('"assetsPublishAuthorized":false',source)
        self.assertNotIn('Command::new("git")',source)
        self.assertNotIn('reqwest',source)
        frontend=(STUDIO/'src/publishing-setup.tsx').read_text(encoding='utf-8')
        self.assertIn('Save publishing settings',frontend)
        self.assertIn('Create GitHub draft',frontend)
        self.assertIn('Publish GitHub draft publicly',frontend)
        self.assertIn('LoopRD registry publication and entitlements remain separate',frontend)
        self.assertNotIn('password',frontend.lower())

    def test_windows_cli_hidden_both_layers(self):
        rust=(STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        manager=(ROOT/'tools/local_client/manager_assets.py').read_text(encoding='utf-8')
        self.assertIn('creation_flags(0x08000000)',rust)
        self.assertIn('CREATE_NO_WINDOW',manager)
        self.assertIn('creationflags=',manager)

    def test_native_ipc_only_stored_identity_and_bounded_preview(self):
        rust=(STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        ui=(STUDIO/'src/pack-browser.tsx').read_text(encoding='utf-8')
        self.assertIn('pub(crate) fn review_catalog(id:String, section:String, offset:u32)',rust)
        self.assertIn('pub(crate) fn review_preview(id:String, member:String)',rust)
        self.assertIn('read_review(&id)',rust)
        self.assertIn("'review_catalog'",ui)
        self.assertIn("'review_preview'",ui)
        self.assertNotIn('dangerouslySetInnerHTML',ui)
        self.assertNotIn('<iframe',ui)
        self.assertIn('MAX_PREVIEW = 96 * 1024',(STUDIO/'studio_pack_catalog.py').read_text(encoding='utf-8'))

    def test_component_wiring_and_versioned_source(self):
        ui=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        host=(STUDIO/'src-tauri/src/lib.rs').read_text(encoding='utf-8')
        self.assertIn('<PackBrowser',ui)
        self.assertIn('<PublishingSetup',ui)
        for token in ('review::review_catalog','review::review_preview','studio_publish::studio_publishing_targets','studio_publish::studio_save_publishing_targets'):
            self.assertIn(token,host)
        self.assertIn('0.1.60',ui)
        self.assertEqual(json.loads((ROOT/'project.zr').read_text(encoding='utf-8'))['version'],'0.1.60')

if __name__=='__main__':unittest.main()
