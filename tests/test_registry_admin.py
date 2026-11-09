"""Registry admin contract source tests; no host/LoopRD implementation or authorization."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.tavix_registry_admin import REGISTRY_ADMIN_FEATURE, validate_registry_admin_request
from tools.tavix_asset_dependencies import PUBLISHABLE_PERMISSIONS, validate_asset_dependencies
from tools.tavix_package import validate, pack, validate_archive
from tools.local_client import local_packages

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT/'examples/registry-admin-request'

def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def manifest():return load('examples/registry-admin-request/manifest.json')

class RegistryAdminTests(unittest.TestCase):
    def test_permission_is_explicit_request_not_grant(self):
        m=manifest()
        self.assertEqual(m['permissions'],['ui.panel',REGISTRY_ADMIN_FEATURE])
        self.assertTrue(validate_registry_admin_request(m))
        self.assertEqual(validate_asset_dependencies(m),[])
        self.assertIn(REGISTRY_ADMIN_FEATURE,PUBLISHABLE_PERMISSIONS)
        self.assertNotIn('assetDependencies',m)
        self.assertNotIn('grants',m)

    def test_existing_apps_are_unaffected(self):
        for name in ('examples/hello-tavix/manifest.json','examples/classified-game/manifest.json','examples/asset-consumer/manifest.json'):
            self.assertFalse(validate_registry_admin_request(load(name)),name)
        self.assertTrue(validate(ROOT/'examples/hello-tavix'))

    def test_invalid_permission_request_is_rejected(self):
        for perms in ([REGISTRY_ADMIN_FEATURE],['ui.panel',REGISTRY_ADMIN_FEATURE,REGISTRY_ADMIN_FEATURE],['ui.panel','assets.registry.admin/v2'],['ui.panel','registry.admin']):
            m=manifest();m['permissions']=perms
            with self.subTest(perms=perms),self.assertRaises(ValueError):
                validate_asset_dependencies(m)
                validate_registry_admin_request(m)

    def test_package_archive_and_local_preview_do_not_grant(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'request.tavix'
            lock=pack(EXAMPLE,out)
            self.assertEqual(validate_archive(out),lock)
            local=local_packages.install(out.read_bytes(),Path(tmp)/'installed')
            self.assertTrue(local['registryAdminRequested'])
            self.assertEqual(local['publisher_trust'],'unverified')
            self.assertNotIn('grants',local)
            self.assertTrue(local_packages.installed(Path(tmp)/'installed')[0]['registryAdminRequested'])

    def test_repository_stage_accepts_request_without_grant(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'repo';root.mkdir();(root/'project.zr').write_text('{}')
            tool=str(ROOT/'tools/repository.py')
            for args in (['index','--repository',str(root)],
                         ['stage','--repository',str(root),'--input',str(EXAMPLE),'--source-url','https://github.com/example/registry-admin-request','--license','MIT'],
                         ['check','--repository',str(root),'--strict']):
                done=subprocess.run([sys.executable,tool,*args],capture_output=True,text=True)
                self.assertEqual(done.returncode,0,done.stderr)
            idx=json.loads((root/'tavi.repository.json').read_text())
            self.assertIn(REGISTRY_ADMIN_FEATURE,idx['extensions'][0]['manifest']['permissions'])
            self.assertNotIn('grants',idx['extensions'][0])

    def test_version_negotiation_contract_is_fail_closed(self):
        c=load('contracts/tavix-registry-admin-v1.json')
        self.assertEqual(c['feature'],REGISTRY_ADMIN_FEATURE)
        self.assertEqual(c['wire']['channel'],'tavi.extension/v1')
        self.assertEqual(c['wire']['standard'],'tavix/1.0')
        self.assertEqual(c['wire']['featureApiVersion'],'1.0.0')
        self.assertEqual(c['status'],'proposed_for_Social_LoopRD_review_not_implemented')
        self.assertFalse(c['authorization']['grantByAppIdAlone'])
        self.assertTrue(c['authorization']['requiresApprovedPublisherAndExactDigest'])
        self.assertTrue(c['authorization']['requiresExplicitHostApproval'])
        self.assertTrue(c['authorization']['requiresAuthenticatedUser'])
        self.assertTrue(c['authorization']['revalidateEachOperation'])
        self.assertFalse(c['authorization']['credentialsInApp'])
        self.assertFalse(c['authorization']['directDatabaseOrNetworkFromApp'])
        self.assertEqual(c['canonicalAssets']['consumerFeature'],'tavi.assets/v1')
        self.assertEqual(set(c['authorization']['hostNativeConfirmationRequiredFor']),{'price.propose','publish','revoke'})

    def test_schemas_compile_and_cover_exact_methods(self):
        try:import jsonschema
        except ImportError:self.skipTest('jsonschema optional in source checkout')
        req=load('contracts/tavix-registry-admin-request-v1.schema.json')
        res=load('contracts/tavix-registry-admin-response-v1.schema.json')
        jsonschema.Draft202012Validator.check_schema(req)
        jsonschema.Draft202012Validator.check_schema(res)
        names={case['properties']['method']['const'] for case in req['oneOf']}
        contract=load('contracts/tavix-registry-admin-v1.json')
        self.assertEqual(names,set(contract['methods']))
        self.assertEqual(len(res['$defs'])-1,len(names))

    def test_valid_wire_examples(self):
        try:import jsonschema
        except ImportError:self.skipTest('jsonschema optional in source checkout')
        req=load('contracts/tavix-registry-admin-request-v1.schema.json')
        res=load('contracts/tavix-registry-admin-response-v1.schema.json')
        def request(method,params):return {'channel':'tavi.extension/v1','direction':'request','id':7,'method':'assets.registry.admin.'+method,'params':params}
        def result(schema,**kwargs):return {'channel':'tavi.extension/v1','direction':'response','id':7,'ok':True,'result':{'schema':'tavix.registry-admin.'+schema+'/v1',**kwargs}}
        jsonschema.validate(request('status',{}),req)
        jsonschema.validate(request('stage.begin',{'fileName':'cards.tavia','byteLength':100,'sha256':'a'*64,'idempotencyKey':'a'*24}),req)
        jsonschema.validate(request('stage.chunk',{'uploadId':'b'*24,'offset':0,'dataBase64':'YWJj'}),req)
        jsonschema.validate(request('stage.commit',{'uploadId':'b'*24,'sha256':'a'*64,'idempotencyKey':'c'*24}),req)
        jsonschema.validate(request('price.propose',{'recordId':'d'*24,'expectedRevision':1,'priceGold':0,'idempotencyKey':'e'*24}),req)
        jsonschema.validate(request('publish',{'recordId':'d'*24,'expectedRevision':2,'idempotencyKey':'e'*24}),req)
        jsonschema.validate(request('revoke',{'recordId':'d'*24,'expectedRevision':3,'reason':'content removed','idempotencyKey':'e'*24}),req)
        jsonschema.validate(result('status',apiVersion='1.0.0',allowedOperations=['status'],maxUploadBytes=1000000,maxChunkBytes=65536),res)
        jsonschema.validate({'channel':'tavi.extension/v1','direction':'response','id':7,'ok':False,'error':'permission_denied'},res)

    def test_wire_rejects_unsafe_extra_fields(self):
        try:import jsonschema
        except ImportError:self.skipTest('jsonschema optional in source checkout')
        req=load('contracts/tavix-registry-admin-request-v1.schema.json')
        base={'channel':'tavi.extension/v1','direction':'request','id':1,'method':'assets.registry.admin.publish','params':{'recordId':'a'*24,'expectedRevision':1,'idempotencyKey':'b'*24}}
        for change in (lambda x:x['params'].update({'confirmed':True}),
                       lambda x:x['params'].update({'userId':'admin'}),
                       lambda x:x['params'].update({'token':'secret'}),
                       lambda x:x.update({'actor':'admin'}),
                       lambda x:x.update({'method':'wallet.purchase'}),
                       lambda x:x['params'].update({'expectedRevision':0}),
                       lambda x:x['params'].update({'url':'https://looprd.example'})):
            bad=copy.deepcopy(base);change(bad)
            with self.subTest(bad=bad):
                self.assertFalse(jsonschema.Draft202012Validator(req).is_valid(bad))

    def test_wire_rejects_invalid_price_and_filename(self):
        try:import jsonschema
        except ImportError:self.skipTest('jsonschema optional in source checkout')
        req=load('contracts/tavix-registry-admin-request-v1.schema.json')
        cases=[('price.propose',{'recordId':'a'*24,'expectedRevision':1,'priceGold':-1,'idempotencyKey':'b'*24}),
               ('price.propose',{'recordId':'a'*24,'expectedRevision':1,'priceGold':1000001,'idempotencyKey':'b'*24}),
               ('stage.begin',{'fileName':'../evil.tavia','byteLength':1,'sha256':'a'*64,'idempotencyKey':'b'*24}),
               ('stage.begin',{'fileName':'a.tavix','byteLength':1,'sha256':'a'*64,'idempotencyKey':'b'*24})]
        for method,params in cases:
            msg={'channel':'tavi.extension/v1','direction':'request','id':1,'method':'assets.registry.admin.'+method,'params':params}
            with self.subTest(method=method):
                self.assertFalse(jsonschema.Draft202012Validator(req).is_valid(msg))

    def test_machine_index_and_docs(self):
        idx=load('contracts/tavix-1.0.json')
        self.assertEqual(idx['documentationVersion'],'0.1.12')
        self.assertEqual(idx['package']['registryAdmin']['permission'],REGISTRY_ADMIN_FEATURE)
        self.assertFalse(idx['hostWire']['proposedRegistryAdmin']['currentTavi_0_3_141_support'])
        for path in ['docs/TAVIX_REGISTRY_ADMIN.adoc','contracts/tavix-registry-admin-v1.json','contracts/tavix-registry-admin-request-v1.schema.json','contracts/tavix-registry-admin-response-v1.schema.json','examples/registry-admin-request/manifest.json']:
            self.assertTrue((ROOT/path).is_file(),path)
        for path in ['docs/INDEX.adoc','README.md','AGENTS.md','architecture/c4/README.adoc']:
            self.assertIn('assets.registry.admin/v1',(ROOT/path).read_text(),path)
        self.assertIn('registryAdminContract',(ROOT/'architecture/c4/workspace.dsl').read_text())

if __name__=='__main__':unittest.main()
