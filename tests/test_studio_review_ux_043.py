"""Native 0.1.47 review UX must guide without granting authority."""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools/studio-desktop'

class ReviewUx043(unittest.TestCase):
    def test_selected_submission_can_choose_and_recheck_blueprint_without_import(self):
        source=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        dialog=(STUDIO/'src/import-setup.tsx').read_text(encoding='utf-8')
        self.assertIn('setImportSetup(selected)',source)
        self.assertIn('onConfirm={configureImported}',source)
        self.assertIn("invoke<Submission>('review_recheck',{id:item.sha256,blueprintId:plan.blueprintId})",source)
        self.assertIn('Custom / no blueprint yet',dialog)
        self.assertIn('node.showModal()',dialog)
        self.assertIn('canonicalValid && item.storeReady',source)
        self.assertIn('isDisabled={busy||!isValidated(selected)}',source)
        self.assertIn("storeReady?'Ready for manual review':'Review requirements incomplete'",source)

    def test_no_automatic_tarot_resource_mapping_or_autopublish(self):
        front=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        dialog=(STUDIO/'src/import-setup.tsx').read_text(encoding='utf-8')
        reviewer=(STUDIO/'review_cli.py').read_text(encoding='utf-8')
        self.assertIn('tarot.card.*',dialog)
        self.assertIn('tarot.major.*',dialog)
        self.assertIn('tarot.minor.*',dialog)
        self.assertIn("if item in resources:",reviewer)
        self.assertIn("canonical_valid and bool(identity and version)",reviewer)
        self.assertNotIn('tarot_card_to_major',reviewer)
        self.assertIn('Publish to official store — integration pending',front)
        self.assertIn('<Button isDisabled>Publish to official store',front)

    def test_pack_viewer_is_bounded_responsive_and_read_only(self):
        front=(STUDIO/'src/main.tsx').read_text(encoding='utf-8')
        viewer=(STUDIO/'src/pack-browser.tsx').read_text(encoding='utf-8')
        css=(STUDIO/'src/studio.css').read_text(encoding='utf-8')
        rust=(STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        self.assertIn('<details className="studio-browser-disclosure">',front)
        self.assertIn('const PAGE_SIZE = 12',viewer)
        self.assertIn('offset+PAGE_SIZE',viewer)
        self.assertIn('"12".into()',rust)
        self.assertIn('const token=++previewToken.current',viewer)
        self.assertIn('token===previewToken.current',viewer)
        self.assertIn('previewToken.current+=1',viewer)
        self.assertIn('studio-pack-inspector',viewer)
        self.assertIn('aria-label="Artwork inspector"',viewer)
        self.assertIn('@media(max-width:780px)',css)
        self.assertNotIn('max-height:430px;overflow-y:auto',css)
        self.assertNotIn('dangerouslySetInnerHTML',viewer)
        self.assertNotIn('<iframe',viewer)
        self.assertIn('pub(crate) fn review_preview(id:String, member:String)',rust)
        self.assertIn('read_review(&id)',rust)

    def test_version_and_operator_gates(self):
        p=json.loads((ROOT/'project.zr').read_text(encoding='utf-8'))
        stamp=json.loads((ROOT/'.ziprunner-post-update-tests.json').read_text(encoding='utf-8'))
        wb=json.loads((ROOT/'.ziprunner-workboard-update.json').read_text(encoding='utf-8'))
        update=json.loads((ROOT/'ziprunner-manifest.json').read_text(encoding='utf-8'))
        for v in (p['version'],stamp['version'],wb['version'],update['project']['version']):
            self.assertEqual(v,'0.1.60')
        self.assertEqual(update['project']['base_version'],'0.1.58')
        self.assertIn('TAVIX-STUDIO-REVIEW-UX-043',[i['id'] for i in wb['implemented']])
        self.assertIn('TAVIX-STUDIO-TAROT-RESOURCE-MAPPING-043',[i['id'] for i in wb['remaining']])
        self.assertFalse(set(i['id'] for i in wb['implemented'])&set(i['id'] for i in wb['remaining']))
        self.assertTrue(all(i.get('operator_checks') for i in wb['implemented']+wb['remaining']))
        self.assertIn('post_build_mechanisms',p)
        self.assertEqual(p['post_build_mechanisms'],[])
        self.assertIn('0.1.60',(STUDIO/'src/main.tsx').read_text(encoding='utf-8'))
        self.assertTrue((ROOT/'docs/QA_0.1.47.adoc').is_file())

if __name__=='__main__':unittest.main()
