"""0.1.60: TAVIB is non-commercial compatibility metadata, never storefront inventory.

These source-level guards accompany the Node inventory tests. Actual Windows
native compilation and operator QA are independent release gates.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / 'tools/studio-desktop'

class BlueprintNotMerchandise058(unittest.TestCase):
    def test_blueprints_remain_for_matching_but_not_for_publishing(self):
        main=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        pub=(STUDIO/'src/publishing-setup.tsx').read_text(encoding='utf-8')
        ui=(STUDIO/'src/catalog-manager.tsx').read_text(encoding='utf-8')
        rows=(STUDIO/'src/catalog-rows.mjs').read_text(encoding='utf-8')
        self.assertIn('<BlueprintLibrary blueprints={blueprints}',main)
        self.assertIn('<ImportSetupDialog item={importSetup} blueprints={blueprints}',main)
        self.assertIn('<PublishingSetup approved={reviews}/>',main)
        self.assertNotIn('blueprints={blueprints}',pub)
        self.assertNotIn('blueprints={blueprints}',ui)
        self.assertNotIn('Blueprints · TAVIB',ui)
        self.assertNotIn('for (const blueprint of blueprints)',rows)
        self.assertNotIn('blueprint:',rows)
        declaration=(STUDIO/'src/catalog-rows.d.mts').read_text(encoding='utf-8')
        self.assertIn('publicationRows(reviews:any[],published:any[],inspected:any[],registryChecked:boolean)',declaration)
        self.assertNotIn('blueprints:any[]',declaration)
        self.assertIn('TAVIA · asset pack',rows)
        self.assertIn('TAVIX · application',rows)
        self.assertIn('not store items',ui)

    def test_native_draft_refuses_blueprint_and_preserves_historical_bytes(self):
        rust=(STUDIO/'src-tauri/src/studio_catalog.rs').read_text(encoding='utf-8')
        self.assertIn('CATALOG_ROW_NOT_SELLABLE',rust)
        self.assertIn('if key.starts_with("blueprint:")',rust)
        self.assertIn('entries.retain(|key, _| !key.starts_with("blueprint:"))',rust)
        self.assertIn('let mut record = load()?;',rust)
        self.assertIn('Some("tavix") | Some("tavia")',rust)
        self.assertIn('catalog-drafts.json',rust)
        self.assertIn('entries.insert(row_key.clone(),row.clone())',rust)
        self.assertNotIn('remove_file(&draft_path()',rust)
        self.assertIn('"remoteApplied":false',rust)

if __name__=='__main__':unittest.main()
