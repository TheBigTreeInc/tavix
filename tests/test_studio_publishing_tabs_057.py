"""Source regression: Publishing must not vertically stack unrelated workflows.

Native/Windows UI acceptance remains required; these checks don't prove visual layout.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'tools/studio-desktop/src/publishing-setup.tsx'
CSS=ROOT/'tools/studio-desktop/src/studio.css'
CATALOG=ROOT/'tools/studio-desktop/src/catalog-manager.tsx'

class PublishingTabs057(unittest.TestCase):
    def test_five_accessible_panels_and_catalog_default(self):
        ui=SRC.read_text(encoding='utf-8')
        for label in ('Catalog','GitHub catalog sync','Connections','GitHub releases','Tavi Assets / LoopRD'):
            self.assertIn("label:'"+label+"'",ui)
        self.assertIn("useState<PublishingPane>('catalog')",ui)
        self.assertEqual(ui.count('<section id="studio-publishing-panel-'),5)
        self.assertEqual(ui.count('</section>'),5)
        self.assertIn('role="tablist"',ui)
        self.assertIn('role="tab"',ui)
        self.assertIn('role="tabpanel"',ui)
        self.assertIn('aria-selected={activePane===pane.id}',ui)
        self.assertIn("hidden={activePane!=='catalog'}",ui)
        self.assertIn("hidden={activePane!=='githubCatalog'}",ui)
        self.assertIn("hidden={activePane!=='settings'}",ui)
        self.assertIn("hidden={activePane!=='github'}",ui)
        self.assertIn("hidden={activePane!=='registry'}",ui)
        for key in ("event.key==='ArrowRight'","event.key==='ArrowLeft'","event.key==='Home'","event.key==='End'"):
            self.assertIn(key,ui)
        css=CSS.read_text(encoding='utf-8')
        self.assertIn('.studio-publishing-pane[hidden]{display:none!important}',css)
        self.assertIn('.studio-publishing-tab:focus-visible',css)

    def test_catalog_stays_mounted_and_separately_scrolled(self):
        ui=SRC.read_text(encoding='utf-8')
        self.assertEqual(ui.count('<CatalogManager'),1)
        self.assertIn('hidden={activePane',ui)
        self.assertNotIn("activePane==='catalog'&&<CatalogManager",ui)
        css=CSS.read_text(encoding='utf-8')
        self.assertIn('.studio-publishing-pane .studio-catalog-scroller',css)
        # A small ZipRunner overlay may omit the unchanged catalog component.
        # Full checkout runs still confirm its native save path and scroller.
        if CATALOG.is_file():
            catalog=CATALOG.read_text(encoding='utf-8')
            self.assertIn('studio-catalog-scroller',catalog)
            self.assertIn('studio_catalog_save_draft',catalog)

    def test_remote_privilege_gates_unchanged_and_actions_in_correct_panels(self):
        ui=SRC.read_text(encoding='utf-8')
        registry=ui.index('id="studio-publishing-panel-registry"')
        github=ui.index('id="studio-publishing-panel-github"')
        self.assertLess(registry,github)
        self.assertLess(registry,ui.index('>Stage in LoopRD…</Button>'))
        self.assertLess(github,ui.index('>Publish GitHub draft publicly…</Button>'))
        for check in ('confirmDigest:digest','operatorApproved:true','confirmedReceipt?.status',
                      'readiness.mayRequestGitHubWrite','registry?.inspect','registry.publishCredentialPresent',
                      'window.confirm','window.prompt','studio_github_create_draft','studio_looprd_publish'):
            self.assertIn(check,ui)
        self.assertIn("onClick={()=>setActivePane('settings')}>Open connections",ui)
        self.assertIn("onClick={()=>setActivePane('github')}>Choose approved package",ui)
        self.assertNotIn('localStorage',ui)
        self.assertNotIn('fetch(',ui)

if __name__=='__main__': unittest.main()
