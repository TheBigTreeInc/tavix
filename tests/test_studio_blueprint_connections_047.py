"""Source-bound regression checks for Studio 0.1.47 blueprint library and safe service reachability."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from contextlib import contextmanager
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
STUDIO=ROOT/'tools/studio-desktop'
sys.path.insert(0,str(STUDIO))
from studio_blueprint_library import import_blueprint,load,local_entries,validate_blueprint
from studio_publisher_probe import probe,NoRedirect


def fixture():
    return {'schema':'tavix.studio.asset-blueprint/v1','id':'local-tarot-test','version':'1.0.0',
            'title':'Local Tarot — audited','description':'Independent reviewer authored profile.',
            'applicablePackTypes':['tarot'],'requiredResources':['tarot.card.00','card.back'],
            'requiredPrefixes':{'tarot.card.':56},'optionalResources':[],
            'designerChecklist':['Review all 78 face IDs and both back choices.']}

@contextmanager
def isolated_studio_profile(directory):
    """Isolate BOTH OS locations; Windows Studio uses LOCALAPPDATA, not HOME.

    Tests must never read or mutate an operator's existing Studio profile.
    The production storage choice and immutable-import behavior stay intact.
    """
    with patch.dict(os.environ, {'HOME': str(directory), 'LOCALAPPDATA': str(directory)}):
        profile = (Path(directory) / ('TaviXStudio/blueprints' if os.name == 'nt'
                                      else '.local/share/tavix-studio/blueprints'))
        yield profile


class BlueprintConnections047(unittest.TestCase):
    def test_bundled_profiles_unchanged_and_known_origin(self):
        from review_cli import available_blueprints
        with tempfile.TemporaryDirectory() as directory, isolated_studio_profile(directory) as profile:
            data=available_blueprints(ROOT)
            self.assertEqual(len([p for p in data if p['origin']=='bundled']),4)
            self.assertEqual(len([p for p in data if p['origin']=='operator']),0)
            built,_=load(ROOT,'tarot-standard-78')
            self.assertEqual(built['version'],'1.0.0')

    def test_local_profile_import_is_immutable_and_exportable(self):
        with tempfile.TemporaryDirectory() as directory, isolated_studio_profile(directory) as profile:
            source=Path(directory)/'candidate.json'
            source.write_text(json.dumps(fixture(),ensure_ascii=False),encoding='utf-8')
            result=import_blueprint(source)
            self.assertEqual(result['status'],'imported_local_only')
            imported=local_entries()
            self.assertEqual(len(imported),1)
            self.assertEqual(imported[0][0]['id'],'local-tarot-test')
            read,adoc=load(ROOT,'local-tarot-test')
            self.assertIsNone(adoc)
            self.assertEqual(read['requiredPrefixes']['tarot.card.'],56)
            with self.assertRaisesRegex(ValueError,'BLUEPRINT_ALREADY_IMPORTED'):
                import_blueprint(source)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                             hashlib.sha256((profile/'local-tarot-test.json').read_bytes()).hexdigest())

    def test_export_cannot_use_changed_local_blueprint(self):
        import review_cli
        import zipfile
        with tempfile.TemporaryDirectory() as directory, isolated_studio_profile(directory) as profile:
            folder=Path(directory);template=folder/'template.json'
            template.write_text(json.dumps(fixture()),encoding='utf-8')
            import_blueprint(template)
            archive=folder/'deck.tavia'
            manifest={'schema':'tavi.assets.pack/v1','id':'org.example.deck','version':'1.0.0',
                      'type':'tarot','compatibility':{'host':'tavi-assets/v1'},'files':{},
                      'resources':{'card.back':{'default':'assets/back.webp'},'tarot.card.00':{'default':'assets/card.webp'}}}
            with zipfile.ZipFile(archive,'w') as z:z.writestr('manifest.json',json.dumps(manifest))
            report=review_cli.inspect(archive,ROOT,None,'local-tarot-test')
            self.assertEqual(report['blueprint']['origin'],'operator')
            self.assertEqual(len(report['blueprint']['sourceDigest']),64)
            report['status']='changes_requested';report['reviewerNote']='Test'
            record=folder/'review.json';record.write_text(json.dumps(report),encoding='utf-8')
            good=folder/'handoff.zip'
            review_cli.export(archive,record,good,ROOT,'feedback')
            with zipfile.ZipFile(good) as z:
                self.assertIn('blueprint/local-tarot-test.json',z.namelist())
                self.assertIn('blueprint/local-tarot-test.adoc',z.namelist())
            profile_file=profile/'local-tarot-test.json'
            modified=fixture();modified['title']='Changed after review'
            profile_file.write_text(json.dumps(modified),encoding='utf-8')
            rejected=folder/'rejected.zip'
            with self.assertRaisesRegex(ValueError,'Local blueprint changed'):
                review_cli.export(archive,record,rejected,ROOT,'feedback')
            self.assertFalse(rejected.exists())

    def test_blueprint_input_fails_closed(self):
        bads=[{'id':'tarot-standard-78'}, {'id':'../escape'}, {'requiredResources':[],'requiredPrefixes':{}},
              {'requiredResources':['tarot.card.00','tarot.card.00']},
              {'requiredPrefixes':{'tarot.card.':999}},
              {'designerChecklist':['']}, {'version':'2.0.0-unstable'},
              {'tags':['untrusted']}, {'applicablePackTypes':[]}]
        for changes in bads:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):validate_blueprint({**fixture(),**changes},local=True)
        with tempfile.TemporaryDirectory() as directory, isolated_studio_profile(directory) as profile:
            file=Path(directory)/'bad.json'
            file.write_text('{"schema":"tavix.studio.asset-blueprint/v1","id":"local-x","id":"local-y"}',encoding='utf-8')
            with self.assertRaises(ValueError):import_blueprint(file)
            file.write_bytes(b'x'*32769)
            with self.assertRaisesRegex(ValueError,'BLUEPRINT_FILE_INVALID'):import_blueprint(file)

    def test_separate_profiles_allow_same_import_id_without_touching_external_profile(self):
        # Regression for Windows 0.1.47: HOME-only overrides allowed tests to
        # import into %LOCALAPPDATA%\TaviXStudio, poisoning the operator profile.
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for directory in (first, second):
                with isolated_studio_profile(directory) as profile:
                    source=Path(directory)/'candidate.json'
                    source.write_text(json.dumps(fixture()),encoding='utf-8')
                    self.assertEqual(import_blueprint(source)['status'],'imported_local_only')
                    self.assertTrue((profile/'local-tarot-test.json').is_file())
                    with self.assertRaisesRegex(ValueError,'BLUEPRINT_ALREADY_IMPORTED'):
                        import_blueprint(source)

    def test_cli_import_reports_safe_messages_not_profile_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'custom.json'
            source.write_text(json.dumps(fixture()),encoding='utf-8')
            env={**os.environ,'HOME':directory,'LOCALAPPDATA':directory}
            cmd=[sys.executable,'-I',str(STUDIO/'review_cli.py'),'blueprint_import',str(ROOT),str(source)]
            result=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stdout)
            self.assertEqual(json.loads(result.stdout)['result']['origin'],'operator')
            imported = Path(directory) / ('TaviXStudio/blueprints' if os.name == 'nt'
                                          else '.local/share/tavix-studio/blueprints') / 'local-tarot-test.json'
            self.assertTrue(imported.is_file(), 'CLI must import only into its temporary profile')
            result=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=20)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(json.loads(result.stdout)['code'],'BLUEPRINT_ALREADY_IMPORTED')
            self.assertNotIn(directory,result.stdout)

    def test_readonly_probe_validates_hosts_and_does_not_authenticate(self):
        with patch('studio_publisher_probe._probe',side_effect=lambda url,service:{'service':service,'status':'responding','code':'HTTPS_RESPONSE_RECEIVED'}) as request:
            result=probe('TheBigTreeInc/tavix','https://api.thebigtree.life')
            self.assertEqual(request.call_count,2)
            self.assertEqual(request.call_args_list[0].args[0],'https://api.github.com/repos/TheBigTreeInc/tavix')
            self.assertEqual(request.call_args_list[1].args[0],'https://api.thebigtree.life/')
            self.assertFalse(result['authenticated'])
            self.assertFalse(result['publishingAvailable'])
        for hostile in ['http://example.org','https://host.example/x','https://me@host.example','https://host.example?key=abc','https://localhost:1234']:
            with self.subTest(hostile=hostile),self.assertRaises(ValueError):probe('',hostile)
        self.assertIsNone(NoRedirect().redirect_request(None,None,302,'found',{},'https://example.org'))

    def test_native_wiring_and_security_gates(self):
        rust=(STUDIO/'src-tauri/src/lib.rs').read_text(encoding='utf-8')
        self.assertIn('review::review_import_blueprint',rust)
        self.assertIn('studio_publish::studio_probe_publishing_targets',rust)
        native=(STUDIO/'src-tauri/src/review.rs').read_text(encoding='utf-8')
        self.assertIn('rfd::FileDialog::new().add_filter("Designer blueprint JSON"',native)
        self.assertIn('script_call("blueprint_import"',native)
        targets=(STUDIO/'src-tauri/src/studio_publish.rs').read_text(encoding='utf-8')
        self.assertIn('let (repo,endpoint,admin,catalog)=load_profile()?;',targets)
        self.assertIn('valid_api_path',targets)
        self.assertIn('studio_looprd_connect',targets)
        self.assertIn('"remotePublishAvailable":false',targets)
        self.assertIn('"githubWriteAuthorized":false',targets)
        self.assertIn('"assetsPublishAuthorized":false',targets)
        ui=(STUDIO/'src/blueprint-library.tsx').read_text(encoding='utf-8')
        self.assertIn('Import blueprint JSON',ui)
        self.assertIn('Where blueprints come from',ui)
        self.assertIn('Imported locally',ui)
        self.assertNotIn('dangerouslySetInnerHTML',ui)

if __name__=='__main__':unittest.main()
