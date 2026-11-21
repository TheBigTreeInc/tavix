"""0.1.47 keeps games and apps grouped by identity, not version cards."""
from pathlib import Path
import json
import unittest
ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools/studio-desktop'
class StudioGameVersions045(unittest.TestCase):
    def test_game_first_selector_and_controlled_version(self):
        source=(STUDIO/'src/package-selector.tsx').read_text(encoding='utf-8')
        main=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        self.assertIn("<PackageSelector packages={snapshot?.packages||[]}/>", main)
        self.assertIn('groupPackages(packages)',source)
        self.assertIn('aria-label="Select game or application"',source)
        self.assertIn('type="search"',source)
        self.assertIn('id="studio-package-version"',source)
        self.assertIn('value={chosen.version}',source)
        self.assertIn('selected.versions.map(version=>',source)
        self.assertIn('chosenVersions[selected.id]',source)
        self.assertIn('Read-only manifest inventory',source)
        self.assertNotIn('review_approve',source)
        self.assertNotIn('dangerouslySetInnerHTML',source)
        self.assertNotIn('invoke(',source)
    def test_mobile_and_source_authority(self):
        css=(STUDIO/'src/studio.css').read_text(encoding='utf-8')
        model=(STUDIO/'src/package-catalog.mjs').read_text(encoding='utf-8')
        native=(STUDIO/'src-tauri/src/lib.rs').read_text(encoding='utf-8')
        self.assertIn('studio-package-picker',css)
        self.assertIn('@media(max-width:780px)',css)
        self.assertIn('grouped.get(pkg.id)',model)
        self.assertIn('compareVersions(b.version,a.version)',model)
        self.assertIn('fn packages(root: &Path)',native)
        self.assertIn('results.len() >= 250',native)
    def test_version_workboard_and_cross_project_contract(self):
        board=json.loads((ROOT/'.ziprunner-workboard-update.json').read_text(encoding='utf-8'))
        manifest=json.loads((ROOT/'ziprunner-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(board['version'],'0.1.60')
        self.assertEqual(manifest['project']['version'],'0.1.60')
        self.assertEqual(manifest['project']['base_version'],'0.1.58')
        self.assertIn('TAVIX-STUDIO-GAME-VERSION-PICKER-045',[x['id'] for x in board['implemented']])
        self.assertIn('TAVIX-TAVIA-CLIENT-CACHE-CONTRACT-045',[x['id'] for x in board['implemented']])
        self.assertTrue((ROOT/'docs/TAVIA_CLIENT_ASSET_DELIVERY_045.adoc').exists())
        self.assertTrue((ROOT/'docs/QA_0.1.47.adoc').exists())
        self.assertFalse(set(x['id'] for x in board['implemented'])&set(x['id'] for x in board['remaining']))
        self.assertEqual(json.loads((ROOT/'project.zr').read_text(encoding='utf-8'))['post_build_mechanisms'],[])
if __name__=='__main__':unittest.main()
