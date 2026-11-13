"""Exact Klondike 0.1.2 optional asset consumer build; not host acceptance."""
import hashlib
import json
from pathlib import Path
import unittest
from tools.tavix_package import validate,validate_archive
from tools.tavix_asset_dependencies import validate_asset_dependencies

ROOT=Path(__file__).resolve().parents[1]
APP='inc.thebigtree.tavi.klondike'
NEW=ROOT/'extensions'/APP/'0.1.2'
OLD=ROOT/'extensions'/APP/'0.1.1'
ORIGINAL_SHA='da4ecd43299c0f05e49beebc5a51fed7146325be8b54b663ac2327103025be92'

class KlondikeAssetConsumerTests(unittest.TestCase):
    def test_latest_candidate_is_valid_and_declares_optional_read_only_card_back(self):
        manifest=json.loads((NEW/'manifest.json').read_text(encoding='utf-8'))
        source=ROOT/'examples'/'klondike-assets-0.1.2'
        self.assertEqual(manifest,json.loads((source/'manifest.json').read_text()))
        self.assertEqual(manifest['version'],'0.1.2')
        self.assertEqual(set(manifest['permissions']),{'ui.panel','storage.private','assets.read'})
        self.assertEqual(validate_asset_dependencies(manifest),[{'packId':'org.tavi.cards.standard','compatibility':{'min':'0.1.0','maxExclusive':'1.0.0'},'capabilities':['card.back'],'optional':True,'requestCustomization':False}])
        self.assertEqual(validate_archive(NEW/f'{APP}-0.1.2.tavix'),validate(source))
        self.assertEqual(json.loads((NEW/'tavix.lock.json').read_text()),validate(source))

    def test_only_overlay_assets_changed_and_legacy_package_is_immutable(self):
        self.assertEqual(hashlib.sha256((OLD/f'{APP}-0.1.1.tavix').read_bytes()).hexdigest(),ORIGINAL_SHA)
        self.assertEqual((NEW/'ui/klondike.js').read_bytes(),(OLD/'ui/klondike.js').read_bytes())
        self.assertIn("import('./asset-integration.mjs')",(NEW/'ui/boot.js').read_text(encoding='utf-8'))
        self.assertIn('createTaviAssetsClient',(NEW/'ui/asset-integration.mjs').read_text(encoding='utf-8'))
        self.assertNotIn('assets.preferences.write',json.loads((NEW/'manifest.json').read_text())['permissions'])

    def test_static_catalog_candidate_points_to_exact_new_archive(self):
        catalog=json.loads((ROOT/'tavi.repository.json').read_text(encoding='utf-8'))
        rows=[r for r in catalog['extensions'] if r['manifest']['id']==APP]
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['manifest']['version'],'0.1.2')
        archive=NEW/f'{APP}-0.1.2.tavix'
        self.assertEqual(rows[0]['release']['revision'],hashlib.sha256(archive.read_bytes()).hexdigest())
        self.assertTrue(rows[0]['entrypoint'].endswith('/0.1.2/ui/index.html'))

if __name__=='__main__': unittest.main()
