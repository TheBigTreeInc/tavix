"""Operator-local designer blueprint import and discovery.

A blueprint is a bounded review aid, never a canonical asset validator,
publisher identity, entitlement or store approval. No remote fetches or scripts.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re

ID = re.compile(r'^[a-z0-9][a-z0-9-]{0,70}$')
RESOURCE = re.compile(r'^[a-z][a-z0-9._-]{0,126}$')
VERSION = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')
MAX_BLUEPRINT = 32768
REQUIRED = {'schema','id','version','title','description','applicablePackTypes',
            'requiredResources','optionalResources','designerChecklist'}
ALLOWED = REQUIRED | {'requiredPrefixes'}


def local_directory() -> Path:
    base = os.environ.get('LOCALAPPDATA') if os.name == 'nt' else os.environ.get('HOME')
    if not base:
        raise ValueError('Local operator profile unavailable')
    root = Path(base) / ('TaviXStudio' if os.name == 'nt' else '.local/share/tavix-studio')
    path = root / 'blueprints'
    if (root.exists() and root.is_symlink()) or (path.exists() and path.is_symlink()):
        raise ValueError('Unsafe blueprint storage')
    path.mkdir(parents=True, exist_ok=True)
    return path


def _string(value, limit: int, *, nonempty=True) -> bool:
    return (isinstance(value,str) and (bool(value.strip()) if nonempty else True)
            and len(value)<=limit and not any(ord(c)<32 for c in value))


def validate_blueprint(data: object, *, local: bool) -> dict:
    if not isinstance(data,dict) or set(data) - ALLOWED or not REQUIRED.issubset(data):
        raise ValueError('BLUEPRINT_SCHEMA_INVALID')
    if data['schema']!='tavix.studio.asset-blueprint/v1':
        raise ValueError('BLUEPRINT_SCHEMA_INVALID')
    ident = data['id']
    if not isinstance(ident,str) or not ID.fullmatch(ident) or (local and not ident.startswith('local-')):
        raise ValueError('BLUEPRINT_ID_INVALID')
    if not isinstance(data['version'],str) or not VERSION.fullmatch(data['version']):
        raise ValueError('BLUEPRINT_VERSION_INVALID')
    if not _string(data['title'],160) or not _string(data['description'],1200,nonempty=False):
        raise ValueError('BLUEPRINT_TEXT_INVALID')
    types = data['applicablePackTypes']
    if not isinstance(types,list) or not 1<=len(types)<=32 or not all(isinstance(x,str) and RESOURCE.fullmatch(x) for x in types) or len(set(types))!=len(types):
        raise ValueError('BLUEPRINT_TYPES_INVALID')
    for key, limit in (('requiredResources',256),('optionalResources',256)):
        values=data[key]
        if not isinstance(values,list) or len(values)>limit or not all(isinstance(x,str) and RESOURCE.fullmatch(x) for x in values) or len(set(values))!=len(values):
            raise ValueError('BLUEPRINT_RESOURCES_INVALID')
    prefixes=data.get('requiredPrefixes',{})
    if not isinstance(prefixes,dict) or len(prefixes)>16 or any(not isinstance(k,str) or not RESOURCE.fullmatch(k) or type(v) is not int or not 1<=v<=64 for k,v in prefixes.items()):
        raise ValueError('BLUEPRINT_PREFIXES_INVALID')
    if not data['requiredResources'] and not prefixes:
        raise ValueError('BLUEPRINT_REQUIREMENTS_EMPTY')
    checks=data['designerChecklist']
    if not isinstance(checks,list) or not 1<=len(checks)<=64 or not all(_string(x,1000) for x in checks):
        raise ValueError('BLUEPRINT_CHECKLIST_INVALID')
    return data


def _read(path: Path, *, local: bool) -> dict:
    if path.is_symlink() or not path.is_file() or not 1<=path.stat().st_size<=MAX_BLUEPRINT:
        raise ValueError('BLUEPRINT_FILE_INVALID')
    try:
        data=json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_distinct)
    except (UnicodeError, OSError, ValueError, TypeError) as exc:
        raise ValueError('BLUEPRINT_JSON_INVALID') from exc
    return validate_blueprint(data,local=local)


def _distinct(pairs):
    data={}
    for key,value in pairs:
        if key in data: raise ValueError('BLUEPRINT_DUPLICATE_KEY')
        data[key]=value
    return data


def load(repo: Path, ident: str) -> tuple[dict,str|None]:
    if not isinstance(ident,str) or not ID.fullmatch(ident):
        raise ValueError('Invalid blueprint ID')
    if ident.startswith('local-'):
        path = local_directory() / (ident+'.json')
        if not path.exists(): raise ValueError('Blueprint unavailable')
        data=_read(path,local=True)
        adoc=None
    else:
        path = repo / 'tools/studio-desktop/blueprints' / (ident+'.json')
        if not path.exists(): raise ValueError('Blueprint unavailable')
        data=_read(path,local=False)
        adoc=str(path.with_suffix('.adoc'))
    if data['id']!=ident:
        raise ValueError('Unsupported blueprint contract')
    return data,adoc


def import_blueprint(source: Path) -> dict:
    if source.is_symlink() or not source.is_file() or not 1<=source.stat().st_size<=MAX_BLUEPRINT:
        raise ValueError('BLUEPRINT_FILE_INVALID')
    raw=source.read_bytes()
    if not 1<=len(raw)<=MAX_BLUEPRINT:
        raise ValueError('BLUEPRINT_FILE_INVALID')
    try:
        data=validate_blueprint(json.loads(raw.decode('utf-8'), object_pairs_hook=_distinct),local=True)
    except (ValueError, TypeError, UnicodeError) as exc:
        raise ValueError('BLUEPRINT_JSON_INVALID') from exc
    destination=local_directory() / (data['id']+'.json')
    # Preserve exact validated bytes, with immutable local identity.
    if destination.exists():
        raise ValueError('BLUEPRINT_ALREADY_IMPORTED')
    with destination.open('xb') as out:
        out.write(raw)
        out.flush();os.fsync(out.fileno())
    return {'id':data['id'],'origin':'operator','status':'imported_local_only'}


def local_entries() -> list[tuple[dict,str]]:
    entries=[]
    for path in sorted(local_directory().glob('local-*.json'))[:100]:
        try:
            data=_read(path,local=True)
            if path.stem==data['id']:
                entries.append((data,hashlib.sha256(path.read_bytes()).hexdigest()[:12]))
        except (ValueError, OSError):
            continue
    return entries


def local_readme(ident: str) -> str:
    return ('= Local designer blueprint '+ident+'\n\n'
            'This operator-imported JSON is a local review aid, not a Tavi Assets package schema, '
            'publication grant or server entitlement. Review the enclosed exact JSON requirements.\n')


def app_origin(ident: str) -> dict | None:
    if not isinstance(ident,str) or not ID.fullmatch(ident) or not ident.startswith('local-app-'):
        return None
    path=local_directory()/'.origins'/(ident+'.json')
    if not path.is_file() or path.is_symlink() or path.stat().st_size>4096:
        return None
    try:
        record=_distinct_json(path.read_bytes())
        if record.get('schema')!='tavix.studio.embedded-blueprint-origin/v1' or not isinstance(record.get('appId'),str):
            return None
        return record
    except (OSError,ValueError,TypeError,UnicodeError):return None

def _distinct_json(raw):
    return json.loads(raw.decode('utf-8'),object_pairs_hook=_distinct)
