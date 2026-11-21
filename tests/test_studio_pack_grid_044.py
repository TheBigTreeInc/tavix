"""0.1.47 read-only grid: bounded safe thumbnail transport and reversible list view."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools/studio-desktop'

class PackGrid044(unittest.TestCase):
    def test_grid_and_list_are_both_available_and_keep_the_native_page(self):
        browser=(STUDIO/'src/pack-browser.tsx').read_text(encoding='utf-8')
        self.assertIn("useState<'grid'|'list'>('grid')",browser)
        self.assertIn('aria-label="Package view"',browser)
        self.assertIn("aria-pressed={view==='grid'}",browser)
        self.assertIn("aria-pressed={view==='list'}",browser)
        self.assertIn('<PackGrid id={id}',browser)
        self.assertIn('view===\'grid\'?',browser)
        self.assertIn('className="studio-pack-list"',browser)
        self.assertIn('const PAGE_SIZE = 12',browser)
        self.assertIn('offset+PAGE_SIZE',browser)
        self.assertIn('setView(\'grid\')',browser)
        self.assertNotIn('dangerouslySetInnerHTML',browser)
        self.assertNotIn('<iframe',browser)

    def test_thumbnails_are_bounded_cancelled_and_digest_bound(self):
        grid=(STUDIO/'src/pack-grid.tsx').read_text(encoding='utf-8')
        rust=(STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        catalog=(STUDIO/'studio_pack_catalog.py').read_text(encoding='utf-8')
        self.assertIn('MAX_VISIBLE = 12',grid)
        self.assertIn('MAX_CONCURRENT = 3',grid)
        self.assertIn('items.slice(0,MAX_VISIBLE)',grid)
        self.assertIn('new Set(',grid)
        self.assertIn("invoke<Preview>('review_preview',{id,member})",grid)
        self.assertIn('if(alive) setThumbs(',grid)
        self.assertIn('return ()=>{alive=false;}',grid)
        self.assertIn('safeDataUrl(image.dataUrl)',grid)
        self.assertIn('Artwork unavailable',grid)
        self.assertIn('onPreview(member)',grid)
        self.assertIn('read_review(&id)',rust)
        self.assertIn('MAX_PREVIEW = 96 * 1024',catalog)
        self.assertIn('hashlib.sha256(data).hexdigest()!=digest',catalog)
        for bad in ('fetch(', 'document.createElement', 'iframe', 'dangerouslySetInnerHTML', 'localStorage', 'http://'):
            self.assertNotIn(bad,grid)

    def test_adaptive_tile_and_keyboard_access(self):
        grid=(STUDIO/'src/pack-grid.tsx').read_text(encoding='utf-8')
        style=(STUDIO/'src/studio.css').read_text(encoding='utf-8')
        self.assertIn('type="button"',grid)
        self.assertIn('aria-label={\'Inspect artwork for \'+title}',grid)
        self.assertIn('loading="lazy"',grid)
        self.assertIn('studio-pack-tile-action:focus-visible',style)
        self.assertIn('grid-template-columns:repeat(auto-fill,minmax(',style)
        self.assertIn('@media(max-width:780px)',style)

    def test_044_version_workboard_and_approval(self):
        project=json.loads((ROOT/'project.zr').read_text(encoding='utf-8'))
        manifest=json.loads((ROOT/'ziprunner-manifest.json').read_text(encoding='utf-8'))
        wb=json.loads((ROOT/'.ziprunner-workboard-update.json').read_text(encoding='utf-8'))
        for version in [project['version'],manifest['project']['version'],wb['version']]:
            self.assertEqual(version,'0.1.60')
        self.assertEqual(manifest['project']['base_version'],'0.1.58')
        self.assertIn('TAVIX-STUDIO-PACK-GRID-044',[i['id'] for i in wb['implemented']])
        self.assertFalse(set(i['id'] for i in wb['implemented']) & set(i['id'] for i in wb['remaining']))
        self.assertEqual(project['post_build_mechanisms'],[])
        self.assertTrue((ROOT/'docs/QA_0.1.47.adoc').is_file())

if __name__=='__main__': unittest.main()
