#!/usr/bin/env python3
"""Provisional source-side .tavix packer for bounded schematics/*.tavib.

Works on top of the existing TaviX Python package contract without altering its
legacy allowed-extensions policy. The Studio importer validates the inner TAVIB.
This does not declare Tavi Assets canonical ratification or publisher trust.
"""
from __future__ import annotations
import argparse,hashlib,shutil,stat,sys,tempfile,zipfile
from pathlib import Path

from tavix_package import validate,validate_archive,lock_bytes,EPOCH
sys.path.insert(0,str(Path(__file__).parent/'studio-desktop'))
from studio_tavib import parse_tavib,MEMBER,MAX_INNER,MAX_BPS

def pack_with_blueprints(source:Path,destination:Path):
    source=source.resolve();destination=destination.resolve()
    if destination.is_relative_to(source):raise ValueError('Output must be outside application source')
    if not (source/'manifest.json').is_file():raise ValueError('Missing app manifest')
    inner=[]
    for candidate in sorted(source.rglob('*')):
        if candidate.is_symlink():raise ValueError('Symlinks are not supported')
        if not candidate.is_file():continue
        name=candidate.relative_to(source).as_posix()
        if name.endswith('.tavib'):
            if not MEMBER.fullmatch(name) or candidate.stat().st_size>MAX_INNER:
                raise ValueError('TAVIB path/size invalid')
            blob=candidate.read_bytes()
            blueprint=parse_tavib(blob)
            if MEMBER.fullmatch(name).group(1)!=blueprint['id']:
                raise ValueError('TAVIB path/identity mismatch')
            inner.append((name,blob))
    if len(inner)>MAX_BPS:raise ValueError('Too many embedded TAVIBs')
    with tempfile.TemporaryDirectory(prefix='tavix-tavib-stage-') as tmp:
        staging=Path(tmp)
        for candidate in sorted(source.rglob('*')):
            if not candidate.is_file():continue
            rel=candidate.relative_to(source)
            if rel.as_posix().endswith('.tavib'):continue
            dest=staging/rel;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(candidate,dest,follow_symlinks=False)
        lock=validate(staging)
        paths={item['path'] for item in lock['files']}
        if paths.intersection(name for name,_ in inner):raise ValueError('Duplicate TAVIB path')
        inner_map=dict(inner)
        for name,blob in inner:
            lock['files'].append({'path':name,'size':len(blob),'sha256':hashlib.sha256(blob).hexdigest()})
        lock['files'].sort(key=lambda x:x['path'])
        destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists():raise ValueError('Output already exists; cannot overwrite a release')
        with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for item in lock['files']:
                name=item['path']
                blob=inner_map[name] if name in inner_map else (staging/name).read_bytes()
                info=zipfile.ZipInfo(name,EPOCH);info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=(stat.S_IFREG|0o644)<<16
                z.writestr(info,blob,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
            info=zipfile.ZipInfo('tavix.lock.json',EPOCH);info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(stat.S_IFREG|0o644)<<16
            z.writestr(info,lock_bytes(lock),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        try:validate_archive(destination)
        except Exception:
            destination.unlink(missing_ok=True);raise
    return lock

def main():
    arg=argparse.ArgumentParser(description='Provisional bounded TaviX .tavib packer')
    arg.add_argument('app_directory',type=Path);arg.add_argument('output_tavix',type=Path)
    args=arg.parse_args()
    lock=pack_with_blueprints(args.app_directory,args.output_tavix)
    print('Created verified TaviX archive with',len(lock['files']),'locked files')

if __name__=='__main__':main()
