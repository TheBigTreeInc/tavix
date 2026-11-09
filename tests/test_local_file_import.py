"""Local file request/SDK source tests; no native Windows/Android picker acceptance."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.tavix_local_file_import import validate_local_file_import, FEATURE, PERMISSION, MAX_CHUNK_BYTES
from tools.tavix_package import pack, validate, validate_archive
from tools.local_client import local_packages
from tools.tavix_asset_dependencies import PUBLISHABLE_PERMISSIONS

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'examples/local-file-import'

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def example():return load('examples/local-file-import/manifest.json')

class LocalFileImportTests(unittest.TestCase):
    def test_manifest_and_legacy(self):
        m=example()
        self.assertEqual(validate_local_file_import(m),m['fileImports'])
        self.assertIsNone(validate_local_file_import({'permissions':['ui.panel']}))
        self.assertEqual(FEATURE,'tavix.local-file-import/v1')
        self.assertIn(PERMISSION,PUBLISHABLE_PERMISSIONS)
        self.assertEqual(MAX_CHUNK_BYTES,65536)

    def test_declared_field_and_permission_must_match(self):
        m=example()
        for transform in [lambda x:x.pop('fileImports'),lambda x:x['permissions'].remove(PERMISSION),lambda x:x['permissions'].append(PERMISSION),lambda x:x['permissions'].remove('ui.panel')]:
            candidate=copy.deepcopy(m);transform(candidate)
            with self.subTest(candidate=candidate),self.assertRaises(ValueError):validate_local_file_import(candidate)

    def test_fail_closed_invalid_filter_and_limits(self):
        m=example()
        for key,bad in [('extensions',[]),('extensions',['.TAVIA']),('extensions',['../tavia']),('extensions',['.*']),('extensions',['.tavia','.tavia']),('mimeTypes',['*/*']),('mimeTypes',['application/*']),('mimeTypes',['application/zip','application/zip']),('maxBytes',True),('maxBytes',0),('maxBytes',134217729),('maxBytes','1024')]:
            candidate=copy.deepcopy(m);candidate['fileImports'][key]=bad
            with self.subTest(key=key,bad=bad),self.assertRaises(ValueError):validate_local_file_import(candidate)
        for extra in [{'directories':True},{'allowPaths':True},{'upload':True}]:
            candidate=copy.deepcopy(m);candidate['fileImports'].update(extra)
            with self.assertRaises(ValueError):validate_local_file_import(candidate)

    def test_pack_archive_and_local_installer(self):
        with tempfile.TemporaryDirectory() as d:
            archive=Path(d)/'local-file.tavix'
            lock=pack(EXAMPLE,archive)
            self.assertEqual(validate_archive(archive),lock)
            self.assertEqual(lock['applicationId'],example()['id'])
            installed=local_packages.install(archive.read_bytes(),Path(d)/'installed')
            self.assertEqual(installed['fileImports'],example()['fileImports'])
            self.assertEqual(local_packages.installed(Path(d)/'installed')[0]['fileImports'],example()['fileImports'])
            self.assertEqual(installed['publisher_trust'],'unverified')

    def test_archive_rejects_invalid_file_import_even_with_valid_hashes(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'src';src.mkdir()
            import shutil
            shutil.copytree(EXAMPLE,src,dirs_exist_ok=True)
            m=json.loads((src/'manifest.json').read_text());m['fileImports']['maxBytes']=999999999
            (src/'manifest.json').write_text(json.dumps(m))
            with self.assertRaises(ValueError):validate(src)

    def test_archive_rejects_invalid_manifest_even_with_consistent_lock(self):
        import hashlib, zipfile
        with tempfile.TemporaryDirectory() as d:
            archive=Path(d)/'valid.tavix';pack(EXAMPLE,archive)
            with zipfile.ZipFile(archive) as z: members={n:z.read(n) for n in z.namelist()}
            manifest=json.loads(members['manifest.json']);manifest['fileImports']['extensions']=['.*']
            members['manifest.json']=(json.dumps(manifest)+'\n').encode()
            lock=json.loads(members['tavix.lock.json'])
            for f in lock['files']:
                if f['path']=='manifest.json':
                    f['size']=len(members['manifest.json']);f['sha256']=hashlib.sha256(members['manifest.json']).hexdigest()
            members['tavix.lock.json']=json.dumps(lock).encode()
            changed=Path(d)/'invalid.tavix'
            with zipfile.ZipFile(changed,'w') as z:
                for n,data in members.items():z.writestr(n,data)
            with self.assertRaises(ValueError):validate_archive(changed)

    def test_repository_staging_accepts_request_without_grant(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d)/'repo';repo.mkdir();(repo/'project.zr').write_text('{}')
            tool=ROOT/'tools/repository.py'
            for args in [('index','--repository',str(repo)),('stage','--repository',str(repo),'--input',str(EXAMPLE),'--source-url','https://github.com/example/local-file-test','--license','MIT'),('check','--repository',str(repo),'--strict')]:
                proc=subprocess.run([sys.executable,str(tool),*args],capture_output=True,text=True)
                self.assertEqual(proc.returncode,0,proc.stderr)
            entry=json.loads((repo/'tavi.repository.json').read_text())['extensions'][0]
            self.assertEqual(entry['manifest']['fileImports'],example()['fileImports'])
            self.assertNotIn('grants',entry)

    def test_json_schemas_examples(self):
        try:from jsonschema import Draft202012Validator
        except ImportError:self.skipTest('jsonschema optional dependency unavailable')
        manifest=load('contracts/tavix-local-file-import-v1.schema.json')
        request=load('contracts/tavix-local-file-request-v1.schema.json')
        response=load('contracts/tavix-local-file-response-v1.schema.json')
        for schema in (manifest,request,response):Draft202012Validator.check_schema(schema)
        Draft202012Validator(manifest).validate(example()['fileImports'])
        req={'channel':'tavi.extension/v1','direction':'request','id':1,'method':'files.local.pick','params':{'accept':{'extensions':['.tavia'],'mimeTypes':['application/zip']},'maxBytes':1048576}}
        Draft202012Validator(request).validate(req)
        selected={'channel':'tavi.extension/v1','direction':'response','id':1,'ok':True,'result':{'status':'selected','file':{'handle':'abcdefghABCDEFGH','name':'cards.tavia','size':3,'mimeType':'application/zip'},'limits':{'maxChunkBytes':65536}}}
        Draft202012Validator(response).validate(selected)
        cancelled={'channel':'tavi.extension/v1','direction':'response','id':1,'ok':True,'result':{'status':'cancelled'}}
        Draft202012Validator(response).validate(cancelled)
        denied={'channel':'tavi.extension/v1','direction':'response','id':1,'ok':False,'error':'Permission revoked','errorCode':'PERMISSION_DENIED'}
        Draft202012Validator(response).validate(denied)
        for bad in [dict(req,params={'path':'C:/secret.txt'}),dict(req,method='files.local.enumerate'),dict(req,params={'accept':{'extensions':['.*'],'mimeTypes':['application/zip']},'maxBytes':1048576})]:
            with self.assertRaises(Exception):Draft202012Validator(request).validate(bad)
        for bad in [dict(selected,result={**selected['result'],'path':'C:/private'}),dict(denied,errorCode='SILENT_GRANT')]:
            with self.assertRaises(Exception):Draft202012Validator(response).validate(bad)

    def test_sdk_reference_app_is_self_contained_and_host_negotiated(self):
        sdk=(ROOT/'sdk/tavix-sdk.mjs').read_bytes()
        self.assertEqual(sdk,(EXAMPLE/'ui/tavix-sdk.mjs').read_bytes())
        js=(EXAMPLE/'ui/main.js').read_text()
        self.assertIn('sdk.localFiles.negotiate()',js)
        self.assertIn('pickCancelable(accept,maxBytes)',js)
        self.assertIn('sdk.localFiles.read(',js)
        self.assertIn('sdk.localFiles.close(',js)
        self.assertNotIn('fetch(',js)
        self.assertNotIn('registry.admin',js)
        self.assertNotIn('<input type="file"',(EXAMPLE/'ui/index.html').read_text())

    def test_node_sdk_transport_contract(self):
        try:subprocess.run(['node','--version'],capture_output=True,check=True)
        except (FileNotFoundError,subprocess.CalledProcessError):self.skipTest('Node.js unavailable')
        run=subprocess.run(['node','--test','tests/test_local_file_sdk.mjs'],cwd=ROOT,capture_output=True,text=True,timeout=25)
        self.assertEqual(run.returncode,0,run.stdout+'\n'+run.stderr)

if __name__=='__main__':unittest.main()
