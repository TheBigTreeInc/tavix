#!/usr/bin/env python3
"""Generate a deterministic provisional data-only TAVIB from an authored JSON.

Contract authority remains Tavi Assets; never equate generating this local file
with a reviewed, trusted, or published blueprint.
"""
from __future__ import annotations
import argparse,hashlib,json,stat,zipfile
from pathlib import Path
from studio_blueprint_library import _distinct,validate_blueprint
from studio_tavib import CONTAINER_SCHEMA,parse_tavib

EPOCH=(1980,1,1,0,0,0)

def build(source:Path,target:Path):
    if source.is_symlink() or source.suffix.lower()!='.json' or not source.is_file() or source.stat().st_size>32768:
        raise ValueError('Source blueprint must be a small local JSON file')
    raw=source.read_bytes()
    bp=validate_blueprint(json.loads(raw.decode('utf-8'),object_pairs_hook=_distinct),local=False)
    manifest={'schema':CONTAINER_SCHEMA,'id':bp['id'],'version':bp['version'],
              'blueprintSha256':hashlib.sha256(raw).hexdigest()}
    target=target.resolve()
    if target.exists() or target.suffix.lower()!='.tavib':raise ValueError('Output must be a new .tavib file')
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in [('blueprint.json',raw),('manifest.json',json.dumps(manifest,sort_keys=True,separators=(',',':')).encode('ascii'))]:
            info=zipfile.ZipInfo(name,EPOCH);info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(stat.S_IFREG|0o644)<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    try:parse_tavib(target.read_bytes())
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return target

if __name__=='__main__':
    args=argparse.ArgumentParser(description='Build a provisional portable TAVIB')
    args.add_argument('source_blueprint',type=Path);args.add_argument('output_tavib',type=Path)
    ns=args.parse_args();print(build(ns.source_blueprint,ns.output_tavib))
