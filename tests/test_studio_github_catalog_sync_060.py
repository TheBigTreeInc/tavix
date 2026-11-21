"""GitHub catalog source/diff/PR safety tests; all network and CLI calls mocked."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools/studio-desktop'
sys.path.insert(0,str(STUDIO))
import studio_github_catalog as client

REV='a'*40
SOURCE_SHA='b'*40
INDEX_SHA='c'*40
REPO='TheBigTreeInc/tavi-assets'
EMPTY_SOURCE={'schema':client.SOURCE_SCHEMA,'packs':[],'schematics':[]}
EMPTY_INDEX={'schema':client.INDEX_SCHEMA,'packs':[],'schematics':[]}

def fake_api(path):
    if path==f'repos/{REPO}':return {'default_branch':'main'}
    if path==f'repos/{REPO}/git/ref/heads/main':return {'object':{'sha':REV}}
    if path.startswith(f'repos/{REPO}/contents/'):
        if 'catalog.source.json' in path: data,sha=EMPTY_SOURCE,SOURCE_SHA
        else:data,sha=EMPTY_INDEX,INDEX_SHA
        return {'encoding':'base64','content':base64.b64encode(json.dumps(data).encode()).decode(),'sha':sha}
    raise AssertionError('Unexpected '+path)

class GithubCatalogSync060(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)
        self.content=b'reviewed tavia fixture (canonical format checked during actual review)'
        self.digest=hashlib.sha256(self.content).hexdigest()
        self.source=self.p/(self.digest+'.tavia');self.source.write_bytes(self.content)
        self.review=self.p/(self.digest+'.json')
        self.review.write_text(json.dumps({'kind':'tavia','sha256':self.digest,'status':'review_approved',
           'canonicalValid':True,'storeReady':True,'packageId':'org.test.cards','version':'1.2.3'}),encoding='utf-8')

    def test_exact_pinned_remote_snapshot_and_no_write(self):
        with patch.object(client,'_get_api',side_effect=fake_api):
            result=client.sync(REPO)
        self.assertEqual(result['revision'],REV)
        self.assertEqual(result['sourceSha'],SOURCE_SHA)
        self.assertTrue(result['readOnly'])
        self.assertEqual(result['sourceEntries'],0)
        self.assertEqual(result['publicPacks'],0)
        self.assertEqual(result['publicSchematics'],0)
        self.assertFalse(result['goldPricesAuthoritative'])

    def test_preview_adds_draft_only_and_leaves_public_catalog_unmodified(self):
        with patch.object(client,'_get_api',side_effect=fake_api):
            proposal=client.preview(REPO,self.source,self.review,self.digest,REV)
        self.assertEqual(proposal['entry']['status'],'draft')
        self.assertEqual(proposal['entry']['artifact'],'packs/org.test.cards/1.2.3/package.tavia')
        self.assertEqual(proposal['entry']['sha256'],self.digest)
        self.assertEqual(proposal['baseRevision'],REV)
        self.assertFalse(proposal['catalogJsonChanged'])
        self.assertFalse(proposal['assetUploaded'])
        self.assertFalse(proposal['priceChanged'])
        self.assertEqual(len(proposal['proposalSha256']),64)
        with self.assertRaisesRegex(ValueError,'STALE_REVISION'):
            with patch.object(client,'_get_api',side_effect=fake_api):
                client.preview(REPO,self.source,self.review,self.digest,'f'*40)

    def test_rejects_invalid_review_and_modified_bytes(self):
        data=json.loads(self.review.read_text(encoding='utf-8'))
        for status,kind in [('draft','tavia'),('review_approved','tavix'),('review_approved','tavib')]:
            data.update(status=status,kind=kind)
            self.review.write_text(json.dumps(data))
            with patch.object(client,'_get_api',side_effect=fake_api):
                with self.assertRaisesRegex(ValueError,'REVIEW_REQUIRED'):
                    client.preview(REPO,self.source,self.review,self.digest,REV)
        data.update(status='review_approved',kind='tavia')
        self.review.write_text(json.dumps(data))
        self.source.write_bytes(b'altered bytes')
        with patch.object(client,'_get_api',side_effect=fake_api):
            with self.assertRaisesRegex(ValueError,'SOURCE_CHANGED'):
                client.preview(REPO,self.source,self.review,self.digest,REV)

    def test_prepared_pr_requires_current_revision_and_exact_preview(self):
        with patch.object(client,'_get_api',side_effect=fake_api):
            proposal=client.preview(REPO,self.source,self.review,self.digest,REV)
        history=[]
        def fake_cli(args,**kwargs):
            history.append((args,kwargs))
            if args[-1].endswith('/pulls'):
                return {'html_url':f'https://github.com/{REPO}/pull/123'}
            return {}
        with patch.object(client,'_snapshot',return_value={
                'repository':REPO,'branch':'main','revision':REV,'sourceSha':SOURCE_SHA,
                'indexSha':INDEX_SHA,'source':EMPTY_SOURCE,'index':EMPTY_INDEX}),\
             patch.object(client.shutil,'which',return_value='/usr/bin/gh'),\
             patch('studio_release_gateway.connection',return_value={'authenticated':True}),\
             patch.object(client,'_cli',side_effect=fake_cli):
            with self.assertRaisesRegex(ValueError,'CONFIRMATION_REQUIRED'):
                client.prepare(REPO,self.source,self.review,self.digest,REV,'e'*64)
            self.assertFalse(history)
            result=client.prepare(REPO,self.source,self.review,self.digest,REV,proposal['proposalSha256'])
        self.assertEqual(result['status'],'draft_pr_created')
        self.assertFalse(result['publicCatalogUpdated'])
        self.assertFalse(result['entitlementsGranted'])
        self.assertEqual(len(history),3)
        self.assertIn('git/refs',history[0][0][-1])
        self.assertIn('/contents/catalog.source.json',history[1][0][-1])
        self.assertIn('/pulls',history[2][0][-1])
        self.assertEqual(history[2][1]['payload']['draft'],True)
        self.assertTrue(all('contents/catalog.json' not in ' '.join(call) for call,_ in history))
        self.assertNotIn('package.tavia',str(history[1][1]['payload'].keys()))

    def test_cross_repository_and_source_index_inconsistency_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'ASSETS_REPOSITORY_REQUIRED'):
            client.sync('TheBigTreeInc/tavix')
        approved={'id':'org.test.cards','version':'1.2.3','artifact':'packs/org.test.cards/1.2.3/package.tavia',
             'status':'approved','visibility':'public','sha256':self.digest,'approvalReference':'operator:review-12345'}
        with self.assertRaisesRegex(ValueError,'SOURCE_INDEX_MISMATCH'):
            client._catalog_shape({**EMPTY_SOURCE,'packs':[approved]},EMPTY_INDEX)
        with self.assertRaisesRegex(ValueError,'SCHEMA_UNSUPPORTED'):
            client._catalog_shape({'schema':'unknown','packs':[],'schematics':[]},EMPTY_INDEX)

    def test_native_source_and_ui_expose_no_tokens_or_unapproved_write(self):
        pub=(STUDIO/'src/publishing-setup.tsx').read_text(encoding='utf-8')
        rust=(STUDIO/'src-tauri/src/studio_publish.rs').read_text(encoding='utf-8')
        main=(STUDIO/'src-tauri/src/lib.rs').read_text(encoding='utf-8')
        for name in ('studio_github_catalog_sync','studio_github_catalog_preview',
                     'studio_github_catalog_prepare','studio_github_login'):
            self.assertIn(name,pub)
            self.assertIn(name,rust)
            self.assertIn(name,main)
        self.assertIn('operator_approved:bool',rust)
        self.assertIn('confirm_digest!=digest',rust)
        self.assertIn('approved_record(&digest)',rust)
        self.assertIn('kind!="tavia"',rust)
        self.assertIn('Sync from GitHub',pub)
        self.assertIn('Prepare draft GitHub pull request',pub)
        self.assertIn('Review changes',pub)
        self.assertNotIn('localStorage',pub)
        self.assertNotIn('githubToken',pub)
        self.assertNotIn('personalAccessToken',pub)

if __name__=='__main__':unittest.main()
