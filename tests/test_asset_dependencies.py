"""TaviX asset request/grant contract checks; NOT live Tavi or Wallet QA."""
import copy
import json
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from tools.tavix_asset_dependencies import validate_asset_dependencies, PUBLISHABLE_PERMISSIONS
from tools.tavix_asset_grants import check_host_grant_subset
from tools.local_client import local_packages
from tools.tavix_package import validate, pack, validate_archive, lock_bytes

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT/'examples/asset-consumer'


def example():
    return json.loads((EXAMPLE/'manifest.json').read_text())


def projection(manifest):
    return {
        'schema':'tavix.asset-grants/v1',
        'extensionId':manifest['id'],
        'extensionVersion':manifest['version'],
        'manifestSha256':'a'*64,
        'scope':'host-session',
        'grants':[{'packId':'org.tavi.cards.standard','capabilities':['card.back'], 'canCustomize':True}],
    }


class AssetDependencyTests(unittest.TestCase):
    def test_legacy_app_and_game_without_assets_remain_compatible(self):
        for folder in ('examples/hello-tavix','examples/classified-game'):
            m=json.loads((ROOT/folder/'manifest.json').read_text())
            self.assertEqual(validate_asset_dependencies(m),[])
            self.assertTrue(validate(ROOT/folder))

    def test_valid_pack_requests_are_not_grants(self):
        m=example();deps=validate_asset_dependencies(m)
        self.assertEqual(len(deps),1)
        self.assertEqual(deps[0]['packId'],'org.tavi.cards.standard')
        self.assertTrue(deps[0]['requestCustomization'])
        self.assertTrue({'assets.read','assets.preferences.write'}.issubset(PUBLISHABLE_PERMISSIONS))

    def test_missing_or_extra_permissions_fail_closed(self):
        for perms in (['ui.panel'],['ui.panel','assets.read'],['ui.panel','assets.preferences.write'],
                      ['ui.panel','assets.read','assets.preferences.write','assets.own'],
                      ['ui.panel','assets.read','assets.preferences.write','assets.read']):
            m=example();m['permissions']=perms
            with self.subTest(perms=perms),self.assertRaises(ValueError):validate_asset_dependencies(m)
        m=example();del m['assetDependencies']
        with self.assertRaisesRegex(ValueError,'require declared'):validate_asset_dependencies(m)

    def test_read_only_dependency_without_write_permission(self):
        m=example();m['permissions']=['ui.panel','assets.read'];del m['assetDependencies'][0]['requestCustomization']
        self.assertFalse(validate_asset_dependencies(m)[0]['requestCustomization'])

    def test_optional_dependencies_are_not_ownership(self):
        m=example();m['assetDependencies'][0]['optional']=True
        self.assertTrue(validate_asset_dependencies(m)[0]['optional'])

    def test_bad_dependency_fields_and_versions(self):
        bad=[]
        def mutated(fn):
            m=example();fn(m['assetDependencies'][0]);bad.append(m)
        mutated(lambda d:d.update({'path':'/private'}))
        mutated(lambda d:d.update({'packId':'../../private'}))
        mutated(lambda d:d.update({'capabilities':['card.back','card.back']}))
        mutated(lambda d:d.update({'capabilities':['card.back','wallet.purchase']})) # syntactically valid but request not a host grant
        bad.pop() # Capability namespaces are pack-defined; no invented central registry.
        mutated(lambda d:d.update({'capabilities':[]}))
        mutated(lambda d:d.update({'optional':'yes'}))
        mutated(lambda d:d.update({'requestCustomization':1}))
        mutated(lambda d:d.update({'compatibility':{'min':'1.0.0','maxExclusive':'1.0.0'}}))
        mutated(lambda d:d.update({'compatibility':{'min':'1.0.0','maxExclusive':'0.9.0'}}))
        mutated(lambda d:d.update({'compatibility':{'min':'1.0.0','maxExclusive':'1.0.0-beta'}}))
        mutated(lambda d:d.update({'compatibility':{'min':'0.1.0','maxExclusive':'1.0.0','extra':1}}))
        for m in bad:
            with self.subTest(deps=m['assetDependencies']),self.assertRaises(ValueError):validate_asset_dependencies(m)

    def test_duplicate_pack_and_bounds(self):
        m=example();m['assetDependencies']*=2
        with self.assertRaisesRegex(ValueError,'duplicate'):validate_asset_dependencies(m)
        m=example();m['assetDependencies']=[]
        with self.assertRaisesRegex(ValueError,'1–16'):validate_asset_dependencies(m)
        m=example();m['assetDependencies'][0]['capabilities']=['a'+str(i) for i in range(33)]
        with self.assertRaisesRegex(ValueError,'capabilities'):validate_asset_dependencies(m)

    def test_archive_revalidates_even_when_digest_is_forged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);archive=root/'good.tavix'
            pack(EXAMPLE,archive);self.assertEqual(validate_archive(archive)['applicationId'],example()['id'])
            with zipfile.ZipFile(archive) as z: files={name:z.read(name) for name in z.namelist()}
            manifest=json.loads(files['manifest.json'])
            manifest['assetDependencies'][0]['packId']='../../unsafe'
            files['manifest.json']=(json.dumps(manifest)+'\n').encode()
            lock=json.loads(files['tavix.lock.json'])
            for item in lock['files']:
                if item['path']=='manifest.json':
                    item['size']=len(files['manifest.json']);item['sha256']=sha256(files['manifest.json']).hexdigest()
            files['tavix.lock.json']=lock_bytes(lock)
            altered=root/'forged.tavix'
            with zipfile.ZipFile(altered,'w') as z:
                for name,data in files.items():z.writestr(name,data)
            with self.assertRaisesRegex(ValueError,'packId'):validate_archive(altered)

    def test_host_projection_subset_only_never_entitlement(self):
        m=example();g=projection(m)
        self.assertTrue(check_host_grant_subset(m,'a'*64,g))
        for edit in (
            lambda x:x['grants'][0].update({'packId':'org.tavi.private.wallet'}),
            lambda x:x['grants'][0].update({'capabilities':['other.secret']}),
            lambda x:x.update({'manifestSha256':'b'*64}),
            lambda x:x.update({'scope':'extension-provided'}),
            lambda x:x['grants'].append(x['grants'][0].copy()),
        ):
            g=projection(m);edit(g)
            with self.subTest(g=g),self.assertRaises(ValueError):check_host_grant_subset(m,'a'*64,g)
        m=example();m['permissions']=['ui.panel','assets.read'];m['assetDependencies'][0]['requestCustomization']=False
        with self.assertRaisesRegex(ValueError,'customization'):check_host_grant_subset(m,'a'*64,projection(m))
        g=projection(m);g['grants'][0]['canCustomize']=False
        self.assertTrue(check_host_grant_subset(m,'a'*64,g))

    def test_grant_is_host_only_and_schema_validates(self):
        try:import jsonschema
        except ImportError:self.skipTest('optional jsonschema not installed')
        dep=json.loads((ROOT/'contracts/tavix-asset-dependencies-v1.schema.json').read_text())
        grant=json.loads((ROOT/'contracts/tavix-asset-grants-v1.schema.json').read_text())
        jsonschema.Draft202012Validator.check_schema(dep)
        jsonschema.Draft202012Validator.check_schema(grant)
        jsonschema.validate(example()['assetDependencies'],dep)
        jsonschema.validate(projection(example()),grant)
        self.assertFalse(jsonschema.Draft202012Validator(grant).is_valid({'grants':[]}))

    def test_repository_staging_accepts_asset_consumer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'repo';root.mkdir();(root/'project.zr').write_text('{}')
            tool=str(ROOT/'tools/repository.py')
            for args in (['index','--repository',str(root)],
                         ['stage','--repository',str(root),'--input',str(EXAMPLE),
                          '--source-url','https://github.com/example/asset-consumer','--license','MIT'],
                         ['check','--repository',str(root),'--strict']):
                done=subprocess.run([sys.executable,tool,*args],capture_output=True,text=True)
                self.assertEqual(done.returncode,0,done.stderr)
            index=json.loads((root/'tavi.repository.json').read_text())
            self.assertEqual(index['extensions'][0]['manifest']['assetDependencies'],example()['assetDependencies'])

    def test_local_preview_preserves_requests_without_grants(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);archive=root/'example.tavix';pack(EXAMPLE,archive)
            record=local_packages.install(archive.read_bytes(),root/'store')
            self.assertEqual(record['assetDependencies'],validate_asset_dependencies(example()))
            self.assertEqual(local_packages.installed(root/'store')[0]['assetDependencies'],record['assetDependencies'])
            self.assertEqual(record['publisher_trust'],'unverified')
            self.assertNotIn('grants',record)

    def test_contract_source_paths_and_cross_project_status(self):
        j=json.loads((ROOT/'contracts/tavix-1.0.json').read_text())
        self.assertEqual(j['documentationVersion'],'0.1.15')
        self.assertEqual(j['package']['assetDependencies']['field'],'assetDependencies')
        self.assertEqual(j['package']['assetDependencies']['permissions'],['assets.read','assets.preferences.write'])
        self.assertFalse(j['hostWire']['assetAccess']['productionAvailableInTavi_0_3_141'])
        for name in ('docs/TAVIX_ASSET_DEPENDENCIES.adoc','contracts/tavix-asset-dependencies-v1.schema.json',
                     'contracts/tavix-asset-grants-v1.schema.json','tools/tavix_asset_dependencies.py'):
            self.assertTrue((ROOT/name).is_file())

if __name__=='__main__':unittest.main()
