"""Catalog table is editable locally but cannot create a store offer or grant permissions."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools/studio-desktop'

class CatalogManagement055(unittest.TestCase):
    def test_native_commands_are_registered_and_are_profile_local(self):
        rust=(STUDIO/'src-tauri/src/studio_catalog.rs').read_text(encoding='utf-8')
        bridge=(STUDIO/'src-tauri/src/lib.rs').read_text(encoding='utf-8')
        self.assertIn('mod studio_catalog',bridge)
        self.assertIn('studio_catalog::studio_catalog_drafts',bridge)
        self.assertIn('studio_catalog::studio_catalog_save_draft',bridge)
        self.assertIn('review::state_root()',rust)
        self.assertIn('CATALOG_ROW_UNKNOWN',rust)
        self.assertIn('MAX_ROWS',rust)
        self.assertIn('MAX_DRAFT_BYTES',rust)
        self.assertIn('publicationAuthorized',rust)
        self.assertIn('remoteApplied',rust)
        self.assertNotIn('LOOPRD_ASSETS_PUBLISH_TOKEN',rust)
        self.assertNotIn('gh release',rust)
        self.assertNotIn('std::env::set_var',rust)

    def test_table_lists_only_merchandise_and_separates_live_status(self):
        ui=(STUDIO/'src/catalog-manager.tsx').read_text(encoding='utf-8')
        helper=(STUDIO/'src/catalog-rows.mjs').read_text(encoding='utf-8')
        publishing=(STUDIO/'src/publishing-setup.tsx').read_text(encoding='utf-8')
        self.assertIn('Catalog &amp; release metadata',ui)
        for token in ['Gold price','Listed','Testing','Save draft','Local drafts',
                      'studio_catalog_drafts','studio_catalog_save_draft']:
            self.assertIn(token,ui)
        self.assertIn('TAVIA · asset pack',helper)
        self.assertIn('TAVIX · application',helper)
        self.assertNotIn('TAVIB · blueprint',helper)
        self.assertIn('Not returned',helper)
        self.assertIn('registryCatalog?.packs',publishing)
        self.assertIn('registryInspection?.versions',publishing)
        self.assertIn('<PublishingSetup approved={reviews}/>',(STUDIO/'src/main.tsx').read_text(encoding='utf-8'))

    def test_never_confuses_store_price_with_authoritative_transaction(self):
        ui=(STUDIO/'src/catalog-manager.tsx').read_text(encoding='utf-8')
        self.assertIn('not supported by the current remote registry API',ui)
        self.assertIn('do not change the official Tavi Store',ui)
        self.assertIn('remoteApplied!==false',ui)
        # Existing exact manifest approval and native service-token gate stay independent.
        rust=(STUDIO/'src-tauri/src/studio_publish.rs').read_text(encoding='utf-8')
        self.assertIn('exact_looprd_source',rust)
        self.assertIn('operator_receipt()',rust)

if __name__=='__main__':unittest.main()
