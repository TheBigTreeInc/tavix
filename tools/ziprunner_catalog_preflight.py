#!/usr/bin/env python3
"""Safely reconcile a copied TaviX source overlay before strict catalog checking.

This is not a publisher, does not access Git/network, and must never trust an
index that differs in unknown ways from validated on-disk releases.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from repository import build_index, canonical, check_index, digest, validate_release, write_index


def _original_catalog_entry(root: Path, entry: dict) -> tuple[str, str]:
    """Verify one old catalog entry against its original immutable release."""
    if not isinstance(entry, dict) or set(entry) != {'manifest','entrypoint','source','license','release'}:
        raise ValueError('Catalog has unexpected extension entry fields')
    m=entry['manifest']
    if not isinstance(m,dict):
        raise ValueError('Invalid extension manifest in catalog')
    app=m.get('id'); version=m.get('version')
    if not isinstance(app,str) or not isinstance(version,str):
        raise ValueError('Catalog extension identity is invalid')
    # Identity validation occurs inside validate_release, which also verifies
    # the immutable bundle files, hashes, publisher metadata and archive.
    # Verify path before accessing files to avoid traversal from catalog input.
    from repository import APP_ID, VERSION
    if not APP_ID.fullmatch(app) or not VERSION.fullmatch(version):
        raise ValueError('Unsafe catalog app ID/version')
    release_dir=root/'extensions'/app/version
    actual_manifest,info,archive=validate_release(release_dir)
    expected={
        'manifest':actual_manifest,
        'entrypoint':f'https://thebigtreeinc.github.io/tavix/extensions/{app}/{version}/{actual_manifest["entrypoints"]["panel"]}',
        'source':info['source'],
        'license':info['license'],
        'release':{'revision':digest(archive.read_bytes())},
    }
    if entry!=expected:
        raise ValueError(f'Catalog entry was modified or mismatches its original release: {app}@{version}')
    return app,version


def preflight(root:Path)->dict:
    root=root.resolve()
    index=root/'tavi.repository.json'
    if not index.is_file():
        raise ValueError('Missing repository index; refusing automatic creation')
    old_bytes=index.read_bytes()
    # Rebuild first; this validates every on-disk version, not merely the
    # versions referenced in the current index.
    desired_bytes=build_index(root)
    before=digest(old_bytes); after=digest(desired_bytes)
    if old_bytes==desired_bytes:
        check_index(root)
        return {'status':'unchanged','index_sha256':after,'reason':'canonical_index'}
    try:
        old=json.loads(old_bytes)
        expected=json.loads(desired_bytes)
    except (UnicodeError, ValueError) as exc:
        raise ValueError('Catalog is not valid JSON; refusing automatic repair') from exc
    if old==expected:
        reason='canonical_line_endings_or_formatting'
        upgrades=[]
    else:
        if not isinstance(old,dict) or set(old)!={'schema','name','extensions'}:
            raise ValueError('Catalog schema or fields changed; refusing automatic repair')
        if old['schema']!=expected['schema'] or old['name']!=expected['name']:
            raise ValueError('Catalog identity changed; refusing automatic repair')
        if not isinstance(old['extensions'],list) or len(old['extensions'])!=len(expected['extensions']):
            raise ValueError('Catalog extension set changed; explicit publisher staging required')
        old_by_id={}
        for entry in old['extensions']:
            app,version=_original_catalog_entry(root,entry)
            if app in old_by_id:
                raise ValueError('Duplicate catalog extension identity')
            old_by_id[app]=(version,entry)
        current_by_id={e['manifest']['id']:e for e in expected['extensions']}
        if set(old_by_id)!=set(current_by_id):
            raise ValueError('New or removed extension in overlay; explicit publisher staging required')
        upgrades=[]
        from repository import semver
        for app,(old_version,old_entry) in old_by_id.items():
            new_entry=current_by_id[app]
            new_version=new_entry['manifest']['version']
            if semver(new_version)<semver(old_version):
                raise ValueError('Catalog would downgrade an extension; refusing automatic repair')
            if old_entry['manifest']['publisher'] != new_entry['manifest']['publisher'] or old_entry['source']!=new_entry['source']:
                raise ValueError('Publisher identity would change; refusing automatic repair')
            if old_version!=new_version:
                upgrades.append({'id':app,'from':old_version,'to':new_version})
            elif old_entry!=new_entry:
                raise ValueError('Current release entry changed without version bump')
        if not upgrades:
            raise ValueError('Unexplained catalog divergence; refusing automatic repair')
        reason='validated_overlay_newer_releases'
    # Only write after every verification succeeds. write_index() uses a
    # canonical binary write; no Git push, publication or release is performed.
    write_index(root)
    check_index(root)
    return {'status':'reconciled','reason':reason,'old_index_sha256':before,
            'index_sha256':after,'upgraded_extensions':upgrades,
            'operator_review_required':True}


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',default='.')
    args=parser.parse_args()
    try:
        print(json.dumps(preflight(Path(args.repository)),sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print('TAVIX_PREFLIGHT_ERROR: '+str(exc),file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
