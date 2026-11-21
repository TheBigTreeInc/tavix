"""0.1.49 Studio compact native layout and two-phase local import source contract."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'tools/studio-desktop/src/main.tsx').read_text(encoding='utf-8')
DIALOG=(ROOT/'tools/studio-desktop/src/import-setup.tsx').read_text(encoding='utf-8')
CSS=(ROOT/'tools/studio-desktop/src/studio.css').read_text(encoding='utf-8')
RUST=(ROOT/'tools/studio-desktop/src-tauri/src/review.rs').read_text(encoding='utf-8')

class CompactStudioWorkflow049(unittest.TestCase):
    def test_dynamic_title_notification_and_refresh_share_one_masthead(self):
        self.assertIn('<h1 className="studio-header-title">{currentPage}</h1>',SOURCE)
        self.assertIn('studio-notifications',SOURCE)
        self.assertIn('>Refresh',SOURCE)
        self.assertNotIn('<Title headingLevel="h1" size="2xl">',SOURCE)
        self.assertNotIn('<Alert variant="success" title={notice}',SOURCE)
        self.assertNotIn('<Content><p>Review games, applications',SOURCE)
        self.assertIn("const STUDIO_UI_VERSION = '0.1.60'",SOURCE)

    def test_existing_page_kept_mounted_during_refresh(self):
        refresh=SOURCE.split('const refresh = async () => {',1)[1].split('  useEffect(',1)[0]
        self.assertNotIn('setLoading(true)',refresh)
        self.assertIn('setRefreshing(true)',refresh)
        self.assertIn('setRefreshing(false)',refresh)

    def test_import_picker_first_then_dialog_and_known_blueprint(self):
        self.assertIn("invoke<Submission>('review_import',{blueprintId:''})",SOURCE)
        self.assertRegex(SOURCE,r"choose\(item\);setSection\('submissions'\);setPreferredBlueprintId\(''\);setImportSetup\(item\)")
        self.assertIn('setImportSetup(null)',SOURCE)
        self.assertIn("invoke<Submission>('review_recheck',{id:item.sha256,blueprintId:plan.blueprintId})",SOURCE)
        self.assertIn("blueprints.some(bp=>bp.id===choice)",SOURCE)
        self.assertIn("if(operation==='import' && message.includes('Import cancelled'))return;",SOURCE)
        self.assertIn('rfd::FileDialog::new()',RUST)
        self.assertIn('script_call("inspect"',RUST)
        self.assertIn('if let Ok(existing) = read_review(&id) { return Ok(existing); }',RUST)
        self.assertNotIn('input type="file"',DIALOG)
        self.assertNotIn('publish',DIALOG.split('export function ImportSetupDialog',1)[0].lower())

    def test_custom_and_existing_blueprint_are_explicitly_separate(self):
        self.assertIn('Custom / no blueprint yet',DIALOG)
        self.assertIn('not store-ready',DIALOG.lower())
        self.assertIn('review later',DIALOG.lower())
        self.assertIn('node.showModal()',DIALOG)
        self.assertIn('onCancel=',DIALOG)
        self.assertIn('if(busy)event.preventDefault()',DIALOG)
        self.assertIn('This pack stays in the review queue',DIALOG)
        self.assertIn('planBlueprintReview(item.kind',SOURCE)
        self.assertIn('isDisabled={busy||!isValidated(selected)}',SOURCE)
        self.assertIn('isDisabled={busy||selected.status',SOURCE)

    def test_windows_select_contrast_and_compact_queue(self):
        self.assertIn('color-scheme:light;color:#151515;background:#fff',CSS)
        self.assertIn('studio-review-toolbar',CSS)
        self.assertIn('studio-queue-strip',SOURCE)
        self.assertIn('studio-review-grid',SOURCE)
        self.assertNotIn('Optional blueprint for new .tavia imports',SOURCE)
        self.assertIn('Import package…',SOURCE)

    def test_no_extra_privilege_or_raw_paths(self):
        for forbidden in ('shell.open(', 'github_token','looprd_token','fetch(', 'window.location='):
            self.assertNotIn(forbidden,DIALOG)
        self.assertIn('review_decide',SOURCE)
        self.assertIn('review_export',SOURCE)
        self.assertIn('onUse={id=>',SOURCE)
        self.assertTrue((ROOT/'tools/studio-desktop/src/blueprint-review-action.mjs').is_file())

if __name__=='__main__': unittest.main()
