"""Source and contract checks for optional classification; NOT Tavi host acceptance."""
import importlib.util
import json
import pathlib
import tempfile
import unittest
import zipfile
from hashlib import sha256

from tools.tavix_classification import (
    APP_CATEGORIES, GAME_CATEGORIES, MAX_CATEGORIES, PRIMARY_TYPES,
    resolve_classification,
)
from tools.tavix_package import lock_bytes, pack, validate, validate_archive

ROOT = pathlib.Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location('installed_dev_packages', ROOT/'tools/local-client/local_packages.py')
local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local)


def write_source(root, classification=None):
    root.mkdir(parents=True, exist_ok=True)
    m = {
        'schema':'tavi.extension/v1', 'id':'example.org.test', 'kind':'app',
        'version':'1.0.0', 'name':'Test', 'entrypoints':{'panel':'index.html'},
    }
    if classification is not None:
        m['classification'] = classification
    (root/'manifest.json').write_text(json.dumps(m), encoding='utf-8')
    (root/'index.html').write_text('<h1>Test</h1>', encoding='utf-8')
    return m


class ClassificationTests(unittest.TestCase):
    def test_legacy_fallback_is_app_not_guessed_from_name(self):
        self.assertEqual(resolve_classification({'name':'Solitaire'}),{'type':'app','categories':[]})
        self.assertEqual(resolve_classification({'classification':{'type':'app'}}),{'type':'app','categories':[]})

    def test_known_game_categories_and_retained_order(self):
        self.assertEqual(resolve_classification({'classification':{'type':'game','categories':['cards','solitaire']}}),
                         {'type':'game','categories':['cards','solitaire']})
        self.assertEqual(resolve_classification({'classification':{'type':'game'}}),{'type':'game','categories':[]})

    def test_invalid_classification_rejected(self):
        invalid = [
            None, [], 'game', {}, {'type':'boardgame'},
            {'type':'Game'}, {'type':'game','categories':'cards'},
            {'type':'game','categories':['cards','cards']},
            {'type':'game','categories':['productivity']},
            {'type':'app','categories':['solitaire']},
            {'type':'game','categories':['cards','Cards']},
            {'type':'game','categories':['unknown']},
            {'type':'game','categories':['cards']*9},
            {'type':'game','categories':['cards'], 'private':'x'},
        ]
        for x in invalid:
            with self.subTest(invalid=x), self.assertRaises(ValueError):
                resolve_classification({'classification':x})

    def test_packaged_game_validate_lock_and_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            m=write_source(root/'source',{'type':'game','categories':['cards','solitaire']})
            lock=validate(root/'source')
            dest=root/'test.tavix'
            pack(root/'source',dest)
            self.assertEqual(validate_archive(dest),lock)
            with zipfile.ZipFile(dest) as z:
                self.assertEqual(json.loads(z.read('manifest.json'))['classification'],m['classification'])

    def test_packager_rejects_invalid_classification_before_archiving(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            write_source(root/'source',{'type':'game','categories':['productivity']})
            with self.assertRaisesRegex(ValueError,'category'):
                pack(root/'source',root/'out.tavix')

    def test_archive_validator_rejects_invalid_even_when_lock_hash_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            write_source(root/'source')
            archive=root/'valid.tavix';pack(root/'source',archive)
            with zipfile.ZipFile(archive) as z:
                files={n:z.read(n) for n in z.namelist()}
            manifest=json.loads(files['manifest.json'])
            manifest['classification']={'type':'game','categories':['utility']}
            files['manifest.json']=(json.dumps(manifest)+'\n').encode()
            lock=json.loads(files['tavix.lock.json'])
            for f in lock['files']:
                if f['path']=='manifest.json':
                    f['size']=len(files['manifest.json'])
                    f['sha256']=sha256(files['manifest.json']).hexdigest()
            files['tavix.lock.json']=lock_bytes(lock)
            forged=root/'bad.tavix'
            with zipfile.ZipFile(forged,'w') as z:
                for name,b in files.items():z.writestr(name,b)
            with self.assertRaisesRegex(ValueError,'category'):
                validate_archive(forged)

    def test_local_installed_inventory_retains_validated_classification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            write_source(root/'source',{'type':'game','categories':['cards','solitaire']})
            archive=root/'game.tavix';pack(root/'source',archive)
            record=local.install(archive.read_bytes(),root/'store')
            self.assertEqual(record['classification'],{'type':'game','categories':['cards','solitaire']})
            self.assertEqual(local.installed(root/'store')[0]['classification'],record['classification'])
            self.assertEqual(record['publisher_trust'],'unverified')
            local.remove(root/'store','example.org.test','1.0.0')
            self.assertEqual(local.installed(root/'store'),[])

    def test_local_installed_inventory_legacy_defaults_to_app(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            write_source(root/'source')
            archive=root/'app.tavix';pack(root/'source',archive)
            local.install(archive.read_bytes(),root/'store')
            self.assertEqual(local.installed(root/'store')[0]['classification'], {'type':'app','categories':[]})

    def test_discover_repository_manifests_normalize_classification(self):
        import sys
        sys.path.insert(0,str(ROOT/'tools/local-client'))
        import server
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            source=root/'extensions'/'example.org.test'/'1.0.0'
            write_source(source,{'type':'game','categories':['cards']})
            discovered=server.discover(root)
            self.assertEqual(discovered[0]['classification'],{'type':'game','categories':['cards']})
            bad=json.loads((source/'manifest.json').read_text())
            bad['classification']['categories']=['utility']
            (source/'manifest.json').write_text(json.dumps(bad))
            self.assertEqual(server.discover(root),[])

    def test_machine_schema_and_docs_track_python_policy(self):
        schema=json.loads((ROOT/'contracts/tavix-classification-v1.schema.json').read_text())
        self.assertEqual(schema['properties']['type']['enum'],list(PRIMARY_TYPES))
        self.assertEqual(schema['properties']['categories']['maxItems'],MAX_CATEGORIES)
        self.assertEqual(schema['allOf'][0]['then']['properties']['categories']['items']['enum'],list(GAME_CATEGORIES))
        self.assertEqual(schema['allOf'][0]['else']['properties']['categories']['items']['enum'],list(APP_CATEGORIES))
        idx=json.loads((ROOT/'contracts/tavix-1.0.json').read_text())
        self.assertEqual(idx['package']['classification']['legacyDefault'],{'type':'app','categories':[]})
        self.assertFalse(idx['package']['classification']['tavi_0_3_124_accepts_classification'])
        proposed=json.loads((ROOT/'contracts/tavix-installed-games-v1.json').read_text())
        self.assertEqual(proposed['status'],'proposed-requires-tavi-and-atrium-implementation')
        self.assertEqual(set(proposed['methods']),{'games.installed.list','games.installed.open'})
        for path in ('docs/TAVIX_CLASSIFICATION.adoc','README.md','AGENTS.md','docs/INDEX.adoc',
                     'docs/TAVIX_CONTRACT.adoc','docs/TAVIX_PACKAGE_FORMAT.adoc'):
            self.assertIn('classification',(ROOT/path).read_text().lower())

    def test_json_schema_accepts_examples_and_rejects_invalid_when_validator_available(self):
        try:import jsonschema
        except ImportError:self.skipTest('optional jsonschema not installed; source tests still run')
        schema=json.loads((ROOT/'contracts/tavix-classification-v1.schema.json').read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        validate_fragment=jsonschema.Draft202012Validator(schema)
        validate_fragment.validate({'type':'game','categories':['cards','solitaire']})
        validate_fragment.validate({'type':'app'})
        for entry in ({'type':'game','categories':['utility']}, {'type':'app','categories':['cards']},
                      {'type':'game','categories':['cards','cards']}, {'type':'unknown'}):
            self.assertFalse(validate_fragment.is_valid(entry))

    def test_repository_stages_and_catalogs_classified_game(self):
        import subprocess
        import sys
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            repo=root/'repo';repo.mkdir()
            (repo/'project.zr').write_text('{}')
            tool=str(ROOT/'tools/repository.py')
            first=subprocess.run([sys.executable,tool,'index','--repository',str(repo)],capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            source=root/'game'
            shutil.copytree(ROOT/'examples/classified-game',source)
            staged=subprocess.run([sys.executable,tool,'stage','--repository',str(repo),'--input',str(source),
                                   '--source-url','https://github.com/example/source','--license','MIT'],capture_output=True,text=True)
            self.assertEqual(staged.returncode,0,staged.stderr)
            catalog=json.loads((repo/'tavi.repository.json').read_text())
            self.assertEqual(catalog['extensions'][0]['manifest']['classification'],
                             {'type':'game','categories':['cards','solitaire']})
            checked=subprocess.run([sys.executable,tool,'check','--repository',str(repo),'--strict'],capture_output=True,text=True)
            self.assertEqual(checked.returncode,0,checked.stderr)

    def test_game_kind_must_be_legacy_app_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            m=write_source(root/'source',{'type':'game','categories':['cards']})
            m['kind']='game'
            (root/'source/manifest.json').write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError,'kind must remain app'):
                pack(root/'source',root/'bad.tavix')

    def test_new_example_is_complete_packable_and_tavi_requires_update(self):
        source=ROOT/'examples/classified-game'
        with tempfile.TemporaryDirectory() as tmp:
            archive=pathlib.Path(tmp)/'classified.tavix'
            pack(source,archive)
            self.assertEqual(validate_archive(archive)['applicationId'],'example.org.solitaire')
        self.assertIn('Tavi 0.3.124 rejects', (ROOT/'examples/CLASSIFIED_GAME.adoc').read_text())

    def test_workboard_boundaries_and_version(self):
        update=json.loads((ROOT/'.ziprunner-workboard-update.json').read_text())
        done={x['id'] for x in update['implemented']}
        pending={x['id'] for x in update['remaining']}
        self.assertFalse(done & pending)
        self.assertIn('TAVIX-ASSET-CONTRACT-001',done)
        self.assertIn('TAVIX-CLASSIFICATION-001', {x['id'] for x in json.loads((ROOT/'ziprunner-manifest.json').read_text())['planned_work']})
        for fname in ('project.zr','tavix.zr','.ziprunner-post-update-tests.json'):
            self.assertEqual(json.loads((ROOT/fname).read_text())['version'],'0.1.13')
        self.assertEqual(json.loads((ROOT/'ziprunner-manifest.json').read_text())['project']['version'],'0.1.13')


if __name__=='__main__':unittest.main()
