#!/usr/bin/env python3
"""TaviX review-staging and reproducible static tavi.repository/v1 catalog.

No Git operations, credentials, network access or automatic publication.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import urlparse

from tavix_package import validate, pack, validate_archive

APP_ID = re.compile(r'^[a-z][a-z0-9.-]{2,118}$')
VERSION = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')
SAFE_SOURCE = re.compile(r'^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$')
LICENSE = re.compile(r'^[A-Za-z0-9.\-+]{1,50}$')
INDEX = 'tavi.repository.json'
RELEASE = 'release.metadata.json' # administrative metadata, never shipped inside .tavix

def canonical(data):
    return (json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)+'\n').encode('utf-8')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def normalize_base(value):
    u = urlparse(value)
    if u.scheme != 'https' or u.netloc.lower() != 'thebigtreeinc.github.io' or u.query or u.fragment or u.params or not u.path.endswith('/tavix/'):
        raise ValueError('Public base must be https://thebigtreeinc.github.io/tavix/')
    return 'https://thebigtreeinc.github.io/tavix/'

def metadata(manifest, source, license_id):
    if not APP_ID.fullmatch(manifest.get('id','')) or not VERSION.fullmatch(manifest.get('version','')):
        raise ValueError('Unsafe application id/version')
    if not SAFE_SOURCE.fullmatch(source):
        raise ValueError('Publisher source must be an explicit GitHub HTTPS repository URL')
    if not LICENSE.fullmatch(license_id):
        raise ValueError('Invalid SPDX license identifier')
    return {'source':source.rstrip('/'), 'license':license_id}

def validate_manifest(m):
    if not isinstance(m,dict) or set(m)-{'schema','id','version','name','summary','publisher','kind','hostApi','entrypoints','contributions','permissions','platforms','icon'}:
        raise ValueError('Unexpected extension manifest fields')
    if m.get('schema')!='tavi.extension/v1' or m.get('kind')!='app':raise ValueError('Invalid extension identity')
    if not isinstance(m.get('name'),str) or not 1<=len(m['name'].strip())<=60:raise ValueError('Invalid name')
    if not isinstance(m.get('summary'),str) or not 1<=len(m['summary'].strip())<=240:raise ValueError('Invalid summary')
    if not re.fullmatch(r'[a-z0-9-]{2,64}',m.get('publisher','')):raise ValueError('Invalid publisher')
    h=m.get('hostApi')
    if not isinstance(h,dict) or set(h)!={'min','maxExclusive'} or not all(VERSION.fullmatch(h.get(x,'')) for x in h):raise ValueError('Invalid host API range')
    if not isinstance(m.get('permissions'),list) or 'ui.panel' not in m['permissions'] or len(set(m['permissions']))!=len(m['permissions']) or set(m['permissions'])-{'ui.panel','ui.toast','storage.private'}:raise ValueError('Unsupported permissions')
    if not isinstance(m.get('contributions'),list) or len(m['contributions'])>12:raise ValueError('Invalid contributions')
    for c in m['contributions']:
        if not isinstance(c,dict) or c.get('slot') not in ('app.launcher','app.store') or c.get('action')!='openPanel':raise ValueError('Unsupported contribution')
    if 'platforms' in m and (not isinstance(m['platforms'],list) or not m['platforms'] or set(m['platforms'])-{'web','windows','android'}):raise ValueError('Unsupported platform')
    return True

def release_path(root, app_id, version):
    return root/'extensions'/app_id/version

def run_stage(root:Path, source_dir:Path, source_url:str, license_id:str):
    root=root.resolve(); source_dir=source_dir.resolve()
    if not (root/'project.zr').is_file():
        raise ValueError('TaviX repository checkout not detected (project.zr missing)')
    check_index(root)
    lock=validate(source_dir)
    manifest=json.loads((source_dir/'manifest.json').read_bytes())
    validate_manifest(manifest)
    info=metadata(manifest,source_url,license_id)
    app_id=manifest['id']; version=manifest['version']
    dest=release_path(root,app_id,version)
    root_extensions=(root/'extensions').resolve()
    if dest.resolve().is_relative_to(root_extensions) is False:raise ValueError('Invalid destination')
    # Compare payload before changing any published release. A changed same-version
    # build MUST bump its version; never replace reviewed bytes silently.
    expected={x['path']:x['sha256'] for x in lock['files']}
    if dest.exists():
        existing=dest/'tavix.lock.json'
        if not existing.is_file():raise ValueError('Existing version has no integrity lock')
        old=json.loads(existing.read_text('utf-8'))
        if {x['path']:x['sha256'] for x in old.get('files',[])}!=expected:
            raise ValueError('Immutable release collision: bump extension version')
        previous=json.loads((dest/RELEASE).read_text('utf-8'))
        if previous!=info:raise ValueError('Existing release publisher metadata changed')
        archive=dest/(app_id+'-'+version+'.tavix')
        if not archive.is_file():raise ValueError('Existing release archive missing')
        validate_archive(archive)
        status='unchanged'
    else:
        root_extensions.mkdir(parents=True,exist_ok=True)
        temp=Path(tempfile.mkdtemp(prefix='.staging-',dir=root_extensions))
        try:
            for item in lock['files']:
                src=source_dir/item['path']; out=temp/item['path']
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src,out)
            archive=temp/(app_id+'-'+version+'.tavix')
            pack(temp,archive)
            validate_archive(archive)
            (temp/'tavix.lock.json').write_bytes(canonical(lock))
            (temp/RELEASE).write_bytes(canonical(info))
            dest.parent.mkdir(parents=True,exist_ok=True)
            temp.rename(dest)
            status='staged'
        finally:
            if temp.exists():shutil.rmtree(temp)
    write_index(root)
    return {'status':status,'id':app_id,'version':version,'relativePath':dest.relative_to(root).as_posix()}

def validate_release(path):
    lock=json.loads((path/'tavix.lock.json').read_text('utf-8'))
    manifest=json.loads((path/'manifest.json').read_text('utf-8'))
    validate_manifest(manifest)
    if lock.get('schema')!='tavix.package/v1' or lock.get('standard')!='tavix/1.0' or lock.get('applicationId')!=manifest.get('id') or lock.get('version')!=manifest.get('version'):
        raise ValueError('Invalid release integrity metadata '+str(path))
    for item in lock.get('files',[]):
        rel=item['path']
        if not isinstance(rel,str) or rel.startswith('/') or '..' in Path(rel).parts or '\\' in rel:
            raise ValueError('Unsafe release asset path')
        asset=path/rel
        if not asset.is_file() or asset.is_symlink() or asset.stat().st_size != item['size'] or digest(asset.read_bytes()) != item['sha256']:
            raise ValueError('Changed or missing release asset '+str(asset))
    if path.name!=manifest['version'] or path.parent.name!=manifest['id']:raise ValueError('Release path does not match manifest')
    archive=path/(manifest['id']+'-'+manifest['version']+'.tavix')
    if not archive.is_file() or validate_archive(archive)!=lock:raise ValueError('Release archive verification failed')
    info=json.loads((path/RELEASE).read_text('utf-8'))
    metadata(manifest,info['source'],info['license'])
    if set(info)!=set(('source','license')):raise ValueError('Unexpected release metadata')
    # Every release directory contains only validated assets and the three generated files.
    expected=set(x['path'] for x in lock['files'])|{'tavix.lock.json',RELEASE,archive.name}
    actual=set(x.relative_to(path).as_posix() for x in path.rglob('*') if x.is_file())
    if actual!=expected:raise ValueError('Unexpected or missing release files '+str(path))
    return manifest,info,archive

def semver(value):
    core,_,pre=value.partition('-')
    major,minor,patch=[int(x) for x in core.split('.')]
    return (major,minor,patch, 1 if not pre else 0, pre)

def build_index(root):
    root=root.resolve(); base=normalize_base('https://thebigtreeinc.github.io/tavix/')
    ext=root/'extensions'; found={}; owners={}
    if ext.exists():
        for manifest_path in sorted(ext.glob('*/*/manifest.json')):
            release=manifest_path.parent; manifest,info,archive=validate_release(release)
            app=manifest['id']; version=manifest['version']
            owner=(manifest['publisher'],info['source'])
            if app in owners and owners[app]!=owner:raise ValueError('Publisher identity/source takeover for '+app)
            owners[app]=owner
            if app not in found or semver(version)>semver(found[app][0]):
                entry={
                  'manifest':manifest,
                  'entrypoint':base+release.relative_to(root).as_posix()+'/'+manifest['entrypoints']['panel'],
                  'source':info['source'], 'license':info['license'],
                  'release':{'revision':digest(archive.read_bytes())}
                }
                found[app]=(version,entry)
    data={'schema':'tavi.repository/v1','name':'TheBigTreeInc TaviX extensions','extensions':[found[id][1] for id in sorted(found)]}
    raw=canonical(data)
    if len(raw)>160000:raise ValueError('Catalog exceeds Tavi index size limit')
    return raw

def write_index(root):
    raw=build_index(root)
    target=root/INDEX
    if target.is_file() and target.read_bytes()==raw:return False
    tmp=target.with_suffix('.json.tmp');tmp.write_bytes(raw);tmp.replace(target)
    return True

def check_index(root):
    target=root/INDEX
    if not target.is_file():raise ValueError('Missing repository index')
    if target.read_bytes()!=build_index(root):raise ValueError('Stale or modified repository index (regenerate with python tools/repository.py index --repository .; LF bytes required)')
    return True

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
    stage=sub.add_parser('stage');stage.add_argument('--repository',required=True);stage.add_argument('--input',required=True);stage.add_argument('--source-url',required=True);stage.add_argument('--license',default='NOASSERTION')
    chk=sub.add_parser('check');chk.add_argument('--repository',default='.')
    gen=sub.add_parser('index');gen.add_argument('--repository',default='.')
    ns=p.parse_args()
    try:
        if ns.action=='stage':r=run_stage(Path(ns.repository),Path(ns.input),ns.source_url,ns.license)
        elif ns.action=='index':r={'updated':write_index(Path(ns.repository))}
        else:r={'valid':check_index(Path(ns.repository))}
        print(json.dumps(r,sort_keys=True))
    except (OSError,ValueError,TypeError,KeyError,RuntimeError,json.JSONDecodeError) as e:
        print('TAVIX_REPOSITORY_ERROR: '+str(e),file=sys.stderr);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
