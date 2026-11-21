"""0.1.60 GitHub/LoopRD connection display and local approval separation."""
from pathlib import Path
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools/studio-desktop'
sys.path.insert(0,str(STUDIO))
import studio_diagnostics as diag

class StudioPublishingConnection053(unittest.TestCase):
    def test_gateway_is_present_but_not_a_login_or_store_grant(self):
        health=diag.health(ROOT,None,'sibling')
        github=next(x for x in health['checks'] if x['id']=='github')
        self.assertEqual(github['code'],'GITHUB_RELEASE_GATEWAY_AVAILABLE')
        self.assertIn('separately',github['message'])
        self.assertEqual(next(x for x in health['checks'] if x['id']=='looprd')['status'],
            'ready' if (STUDIO/'studio_looprd_adapter.py').is_file() else 'pending')
        self.assertNotIn('No connection can be established from this screen yet',json.dumps(health))

    def test_connections_has_only_local_validation_rows(self):
        ui=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        self.assertIn('Local validation components',ui)
        self.assertIn("check.id==='tavix-validator'||check.id==='tavia-validator'",ui)
        self.assertIn('Remote services and release settings',ui)
        self.assertIn("setSection('publishing')",ui)
        self.assertIn('studio-health-list',ui)

    def test_publication_state_is_separate_from_local_review_and_dependencies(self):
        ui=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        pub=(STUDIO/'src/publishing-setup.tsx').read_text(encoding='utf-8')
        self.assertIn('Official-store publication has not been verified',ui)
        self.assertIn("selected.issues.some(f=>f.code==='ASSET_DEPENDENCIES_EXTERNAL')",ui)
        self.assertIn('This package has external asset dependencies',pub)
        self.assertIn('official',pub.lower())
        self.assertIn('readiness.mayRequestGitHubWrite',pub)

    def test_auth_and_release_visibility_are_independent(self):
        source=(STUDIO/'src/publishing-setup.tsx').read_text(encoding='utf-8')
        self.assertIn('Promise.allSettled',source)
        self.assertIn("invoke<Auth>('studio_github_auth')",source)
        self.assertIn("invoke<Releases>('studio_github_releases')",source)
        self.assertIn('Check GitHub sign-in',source)
        self.assertIn('confirmedReceipt?.status',source)
        self.assertIn('digest:chosen',source)
        self.assertNotIn('github_token',source)
        self.assertNotIn('looprd_token',source)
        self.assertNotIn('fetch(',source)

if __name__=='__main__':unittest.main()
