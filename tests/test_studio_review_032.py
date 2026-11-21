"""Studio local review and handoff source-contract regression (no remote writes)."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools/studio-desktop/review_cli.py'
SPEC = importlib.util.spec_from_file_location('studio_review_cli', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class StudioReviewTests(unittest.TestCase):
    def test_blueprint_catalog_exact_cards_and_dice(self):
        profiles = {v['id']:v for v in MODULE.available_blueprints(ROOT)}
        self.assertTrue({'cards-standard-54','cards-back-only','dice-d6-2d','tarot-standard-78'}<=profiles.keys())
        bp,_ = MODULE._load_blueprint(ROOT, 'cards-standard-54')
        self.assertEqual(len(bp['requiredResources']), 53)
        self.assertEqual(bp['requiredPrefixes'], {'card.face.joker.':1})
        self.assertEqual(profiles['cards-standard-54']['requiredCount'],54)
        self.assertEqual(profiles['dice-d6-2d']['requiredCount'],6)

    def test_rejected_tavia_reports_missing_resources_and_missing_validator(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'test.tavia'
            manifest={'schema':'tavi.assets.pack/v1','id':'org.example.unfinished','version':'0.1.0',
                      'type':'playing-cards','compatibility':{'host':'tavi-assets/v1'},
                      'files':{},'resources':{'card.back':{'default':'back.svg'}}}
            with zipfile.ZipFile(path,'w') as z:z.writestr('manifest.json',json.dumps(manifest))
            review=MODULE.inspect(path, ROOT, None, 'cards-standard-54')
            self.assertFalse(review['canonicalValid'])
            self.assertFalse(review['storeReady'])
            self.assertEqual(review['blueprint']['present'],1)
            self.assertEqual(review['blueprint']['required'],54)
            self.assertEqual(sum(i['code']=='BLUEPRINT_MISSING_RESOURCE' for i in review['issues']),52)
            self.assertEqual(sum(i['code']=='BLUEPRINT_MISSING_GROUP' for i in review['issues']),1)
            self.assertTrue(any(i['code']=='TAVIA_VALIDATOR_MISSING' for i in review['issues']))

    def test_unsafe_and_oversized_names_rejected_before_canonical_validation(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.tavia'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('manifest.json','{}')
                z.writestr('../escape.txt','bad')
            r=MODULE.inspect(path,ROOT,None,'cards-back-only')
            self.assertTrue(any(i['code']=='ARCHIVE_REJECTED' for i in r['issues']))
            self.assertFalse(r['storeReady'])

    def test_feedback_handoff_contains_exact_original_and_external_adoc(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d); source=directory/'original.tavia'
            with zipfile.ZipFile(source,'w') as z:z.writestr('manifest.json','{}')
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            review={'sha256':digest,'kind':'tavia','packageId':'org.example.pack','version':'0.1.0',
                    'canonicalValid':False,'status':'changes_requested',
                    'blueprint':{'id':'cards-standard-54'},
                    'reviewerNote':'Replace missing faces and provide a readable joker',
                    'issues':[{'code':'MISSING_CARD','severity':'blocking','message':'Missing spades ace'}]}
            record=directory/'record.json';record.write_text(json.dumps(review))
            dest=directory/'feedback.zip'
            result=MODULE.export(source,record,dest,ROOT,'feedback')
            self.assertEqual(result['filename'],'feedback.zip')
            self.assertNotIn('path',result)
            with zipfile.ZipFile(dest) as z:
                self.assertEqual(z.read('submission/org.example.pack-0.1.0.tavia'),source.read_bytes())
                self.assertIn('feedback/REVIEW.adoc',z.namelist())
                self.assertIn('feedback/review.json',z.namelist())
                self.assertIn('blueprint/cards-standard-54.json',z.namelist())
                self.assertIn('blueprint/cards-standard-54.adoc',z.namelist())
                self.assertIn('Replace missing faces',z.read('feedback/REVIEW.adoc').decode())
            with self.assertRaises(ValueError):MODULE.export(source,record,directory/'preview.zip',ROOT,'preview')


    def test_unsupported_asset_document_is_named_in_feedback(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'invalid.tavia'
            manifest={'schema':'tavi.assets.pack/v1','id':'org.example.invalid','version':'0.1.0',
                'type':'playing-cards','compatibility':{'host':'tavi-assets/v1'},
                'files':{},'resources':{'card.back':{'default':'back.svg'}}}
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('manifest.json',json.dumps(manifest))
                z.writestr('docs/README.adoc','designer notes are not a TAVIA resource')
            assets=Path(os.environ.get('TAVI_ASSETS_ROOT', ROOT.parent/'tavi-assets'))
            if not (assets/'src/tavi_assets/tavia.py').is_file():
                self.skipTest('Canonical Assets checkout not supplied for test')
            review=MODULE.inspect(path,ROOT,assets,'cards-back-only')
            self.assertFalse(review['canonicalValid'])
            diagnostics=' '.join(x['message'] for x in review['issues'])
            self.assertIn('docs/README.adoc',diagnostics)
            self.assertIn('outer feedback ZIP',diagnostics)

    def test_preview_and_approval_separate_from_publication(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);pkg=root/'game.tavix'
            pkg.write_bytes(b'original-package')
            sha=hashlib.sha256(pkg.read_bytes()).hexdigest()
            record=root/'report.json'
            review={'sha256':sha,'kind':'tavix','packageId':'org.example.game','version':'1.0.0',
                    'canonicalValid':True,'status':'draft','issues':[],'reviewerNote':'', 'blueprint':None}
            record.write_text(json.dumps(review))
            MODULE.export(pkg,record,root/'preview.zip',ROOT,'preview')
            with self.assertRaises(ValueError):MODULE.export(pkg,record,root/'approval.zip',ROOT,'approval')
            review['status']='review_approved';record.write_text(json.dumps(review))
            MODULE.export(pkg,record,root/'approval.zip',ROOT,'approval')
            with zipfile.ZipFile(root/'approval.zip') as z:
                self.assertIn(b'NOT publication authority',z.read('feedback/REVIEW.adoc'))

    def test_native_ipc_no_publisher_or_browser_path(self):
        rust = (ROOT/'tools/studio-desktop/src-tauri/src/review.rs').read_text(encoding='utf-8')
        entry = (ROOT/'tools/studio-desktop/src-tauri/src/lib.rs').read_text(encoding='utf-8')
        frontend = (ROOT/'tools/studio-desktop/src/main.tsx').read_text(encoding='utf-8')
        self.assertIn('rfd::FileDialog',rust)
        self.assertIn('review::review_import',entry)
        self.assertIn('review::review_export',entry)
        self.assertIn('Official store publication queue',frontend)
        self.assertIn('Publish to official store — integration pending',frontend)
        self.assertNotIn('reqwest',rust)
        self.assertNotIn('Command::new("git")',rust)
        self.assertIn('review_decide',frontend)
        self.assertIn('changes_requested',frontend)

if __name__=='__main__':unittest.main()
