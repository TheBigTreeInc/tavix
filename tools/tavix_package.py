#!/usr/bin/env python3
"""Deterministic TaviX 1.0 offline package builder/validator.

This tool deliberately validates package structure/integrity, not publisher trust.
Manifest semantics are also checked by the JS TaviX validator in the source gate.
"""
from __future__ import annotations
if __package__:
    from .tavix_classification import resolve_classification
    from .tavix_asset_dependencies import validate_asset_dependencies
    from .tavix_registry_admin import validate_registry_admin_request
    from .tavix_local_file_import import validate_local_file_import
else:
    from tavix_classification import resolve_classification
    from tavix_asset_dependencies import validate_asset_dependencies
    from tavix_registry_admin import validate_registry_admin_request
    from tavix_local_file_import import validate_local_file_import
import argparse, hashlib, json, os, pathlib, re, stat, sys, zipfile

STANDARD='tavix/1.0'
LOCK_SCHEMA='tavix.package/v1'
ALLOWED_EXT={'.html','.css','.js','.mjs','.png','.svg','.webp','.json'}
SKIP={'tavix.lock.json'}
SAFE=re.compile(r'^[A-Za-z0-9_.\-/]+$')
FORBIDDEN={'.git','node_modules','secrets','runtime','.venv','__pycache__','target'}
EPOCH=(1980,1,1,0,0,0)

def _path(root:pathlib.Path,p:pathlib.Path)->str:
    rel=p.relative_to(root).as_posix()
    parts=pathlib.PurePosixPath(rel).parts
    if not rel or rel.startswith('/') or '..' in parts or not SAFE.fullmatch(rel):
        raise ValueError(f'unsafe TaviX path: {rel!r}')
    if any(part in FORBIDDEN for part in parts) or any(part.startswith('.env') for part in parts):
        raise ValueError(f'private/runtime TaviX path is forbidden: {rel}')
    return rel

def _files(root:pathlib.Path):
    out=[]
    for p in sorted(root.rglob('*')):
        if p.is_symlink(): raise ValueError(f'symlinks are forbidden: {_path(root,p)}')
        if not p.is_file(): continue
        rel=_path(root,p)
        if rel in SKIP: continue
        if pathlib.PurePosixPath(rel).suffix.lower() not in ALLOWED_EXT:
            raise ValueError(f'unsupported TaviX file type: {rel}')
        size=p.stat().st_size
        if size>1_000_000: raise ValueError(f'TaviX file exceeds 1 MiB: {rel}')
        data=p.read_bytes()
        out.append({'path':rel,'size':size,'sha256':hashlib.sha256(data).hexdigest()})
    return out

def validate(root:pathlib.Path):
    root=root.resolve()
    manifest_path=root/'manifest.json'
    if not manifest_path.is_file(): raise ValueError('manifest.json is required at package root')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('schema')!='tavi.extension/v1': raise ValueError('TaviX 1.0 requires tavi.extension/v1 manifest')
    if 'kind' in manifest and manifest['kind'] != 'app': raise ValueError('TaviX v1 kind must remain app; use classification.type for games')
    resolve_classification(manifest)
    validate_asset_dependencies(manifest)
    validate_registry_admin_request(manifest)
    validate_local_file_import(manifest)
    entry=manifest.get('entrypoints',{}).get('panel')
    if not isinstance(entry,str) or not (root/entry).is_file(): raise ValueError('manifest panel entrypoint is missing')
    icon=manifest.get('icon')
    if icon is not None and (not isinstance(icon,str) or not (root/icon).is_file()): raise ValueError('manifest icon is missing')
    files=_files(root)
    paths={x['path'] for x in files}
    if 'manifest.json' not in paths or entry not in paths or icon is not None and icon not in paths:
        raise ValueError('required manifest assets are absent')
    return {'schema':LOCK_SCHEMA,'standard':STANDARD,'applicationId':manifest.get('id'),'version':manifest.get('version'),'files':files}

def lock_bytes(lock):
    return (json.dumps(lock,separators=(',',':'),sort_keys=True,ensure_ascii=False)+'\n').encode('utf-8')

def pack(root:pathlib.Path,output:pathlib.Path):
    root=root.resolve(); lock=validate(root); lock_data=lock_bytes(lock)
    output=output.resolve(); output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for item in lock['files']:
            data=(root/item['path']).read_bytes(); info=zipfile.ZipInfo(item['path'],EPOCH); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=(stat.S_IFREG|0o644)<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        info=zipfile.ZipInfo('tavix.lock.json',EPOCH); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=(stat.S_IFREG|0o644)<<16
        z.writestr(info,lock_data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return lock

def validate_archive(path:pathlib.Path):
    with zipfile.ZipFile(path,'r') as z:
        names=z.namelist()
        if len(names)!=len(set(names)): raise ValueError('duplicate TaviX archive path')
        if any(n.startswith('/') or '..' in pathlib.PurePosixPath(n).parts or '\\' in n for n in names): raise ValueError('unsafe TaviX archive path')
        if 'manifest.json' not in names or 'tavix.lock.json' not in names: raise ValueError('TaviX archive metadata missing')
        lock=json.loads(z.read('tavix.lock.json'))
        if lock.get('schema')!=LOCK_SCHEMA or lock.get('standard')!=STANDARD: raise ValueError('unsupported TaviX lock')
        manifest=json.loads(z.read('manifest.json'))
        if 'kind' in manifest and manifest['kind'] != 'app': raise ValueError('TaviX v1 kind must remain app; use classification.type for games')
        resolve_classification(manifest)
        validate_asset_dependencies(manifest)
        validate_registry_admin_request(manifest)
        validate_local_file_import(manifest)
        if lock.get('applicationId')!=manifest.get('id') or lock.get('version')!=manifest.get('version'): raise ValueError('TaviX manifest/lock identity mismatch')
        expected={x['path']:x for x in lock.get('files',[])}
        if set(names)!=(set(expected)|{'tavix.lock.json'}): raise ValueError('TaviX lock/archive file mismatch')
        for name,item in expected.items():
            data=z.read(name)
            if len(data)!=item.get('size') or hashlib.sha256(data).hexdigest()!=item.get('sha256'): raise ValueError(f'TaviX asset digest mismatch: {name}')
        return lock

def main(argv=None):
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    v=sub.add_parser('validate');v.add_argument('path')
    a=sub.add_parser('validate-archive');a.add_argument('path')
    b=sub.add_parser('pack');b.add_argument('directory');b.add_argument('output')
    ns=p.parse_args(argv)
    try:
        if ns.cmd=='validate': result=validate(pathlib.Path(ns.path))
        elif ns.cmd=='validate-archive': result=validate_archive(pathlib.Path(ns.path))
        else: result=pack(pathlib.Path(ns.directory),pathlib.Path(ns.output))
        print(json.dumps({k:v for k,v in result.items() if k!='files'},sort_keys=True))
    except (OSError,ValueError,json.JSONDecodeError,zipfile.BadZipFile) as e:
        print(f'TaviX package error: {e}',file=sys.stderr);return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
