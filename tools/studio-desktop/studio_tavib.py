"""Bounded, data-only experimental TAVIB transport for TaviX Studio.

Owner contract: Tavi Assets must ratify the container before general publication.
Neither an outer .tavix nor an inner .tavib is executed by this module.
"""
from __future__ import annotations
import base64, hashlib, json, os, re, sys, zipfile
from pathlib import Path
from studio_blueprint_library import validate_blueprint, local_directory, _distinct

CONTAINER_SCHEMA='tavi.assets.blueprint-container/v1'
MEMBER=re.compile(r'^schematics/([a-z0-9][a-z0-9-]{0,70})\.tavib$')
HEX=re.compile(r'^[0-9a-f]{64}$')
MAX_OUTER=48*1024*1024
MAX_INNER=128*1024
MAX_BPS=24
MAX_FILES=4

def _json(raw:bytes):
    return json.loads(raw.decode('utf-8'),object_pairs_hook=_distinct)

def _blueprint(blob:bytes):
    if len(blob)>32768 or not blob: raise ValueError('TAVIB_BLUEPRINT_INVALID')
    obj=validate_blueprint(_json(blob),local=False)
    return obj

def parse_tavib(blob:bytes):
    if not 0<len(blob)<=MAX_INNER: raise ValueError('TAVIB_SIZE_INVALID')
    from io import BytesIO
    with zipfile.ZipFile(BytesIO(blob)) as z:
        items=z.infolist()
        names=[x.filename for x in items]
        if not 2<=len(items)<=MAX_FILES or len(set(x.casefold() for x in names))!=len(names):
            raise ValueError('TAVIB_MEMBERS_INVALID')
        if 'manifest.json' not in names or 'blueprint.json' not in names or any(
            x not in {'manifest.json','blueprint.json','README.md','preview.webp'} for x in names):
            raise ValueError('TAVIB_MEMBERS_INVALID')
        if any(i.flag_bits & 1 or i.is_dir() or i.file_size>32768 or
            i.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED) or
            ((i.external_attr>>16)&0o170000)==0o120000 for i in items):
            raise ValueError('TAVIB_MEMBERS_INVALID')
        if sum(i.file_size for i in items)>65536:raise ValueError('TAVIB_EXPANSION_INVALID')
        manifest=_json(z.read('manifest.json'))
        blueprint_bytes=z.read('blueprint.json')
        blueprint=_blueprint(blueprint_bytes)
        if not isinstance(manifest,dict) or set(manifest)!={'schema','id','version','blueprintSha256'} or \
            manifest.get('schema')!=CONTAINER_SCHEMA or manifest.get('id')!=blueprint['id'] or \
            manifest.get('version')!=blueprint['version'] or manifest.get('blueprintSha256')!=hashlib.sha256(blueprint_bytes).hexdigest():
            raise ValueError('TAVIB_MANIFEST_INVALID')
        if 'README.md' in names:
            readme=z.read('README.md')
            if len(readme)>8192:raise ValueError('TAVIB_MEMBERS_INVALID')
            try:readme.decode('utf-8')
            except UnicodeError:raise ValueError('TAVIB_MEMBERS_INVALID') from None
        if 'preview.webp' in names:
            preview=z.read('preview.webp')
            if not (len(preview)>=12 and preview[:4]==b'RIFF' and preview[8:12]==b'WEBP'):
                raise ValueError('TAVIB_MEMBERS_INVALID')
        return blueprint

def _validated_outer(source:Path,repo:Path):
    if source.suffix.lower()!='.tavix' or source.is_symlink() or not source.is_file() or not 0<source.stat().st_size<=MAX_OUTER:
        raise ValueError('TAVIB_OUTER_INVALID')
    with zipfile.ZipFile(source) as outer_zip:
        infos=outer_zip.infolist()
        if len(infos)>1024 or len({x.filename.casefold() for x in infos})!=len(infos) or \
            any(i.file_size>20*1024*1024 or i.flag_bits & 1 or i.is_dir() for i in infos) or \
            sum(i.file_size for i in infos)>96*1024*1024:
            raise ValueError('TAVIB_OUTER_INVALID')
    sys.path.insert(0,str(repo/'tools'))
    try:
        from tavix_package import validate_archive
        validate_archive(source)
    finally:
        sys.path.pop(0)
    package_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    with zipfile.ZipFile(source) as z:
        outer=_json(z.read('manifest.json'))
        app_id=outer.get('id');app_version=outer.get('version')
        if not isinstance(app_id,str) or not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,126}',app_id) or \
           not isinstance(app_version,str) or not re.fullmatch(r'\d+\.\d+\.\d+',app_version):
            raise ValueError('TAVIB_OUTER_INVALID')
        names=[n for n in z.namelist() if n.endswith('.tavib')]
        if len(names)>MAX_BPS or any(not MEMBER.fullmatch(n) for n in names):raise ValueError('TAVIB_PATH_INVALID')
        parsed=[]
        for name in sorted(names):
            item=z.getinfo(name)
            if item.file_size>MAX_INNER:raise ValueError('TAVIB_SIZE_INVALID')
            inner=z.read(item)
            data=parse_tavib(inner)
            if MEMBER.fullmatch(name).group(1)!=data['id']:raise ValueError('TAVIB_PATH_INVALID')
            digest=hashlib.sha256(inner).hexdigest()
            parsed.append((name,digest,data))
    return package_hash,app_id,app_version,parsed

def discover(source:Path,repo:Path):
    package_hash,app_id,app_version,parsed=_validated_outer(source,repo)
    return {'schema':'tavix.studio.embedded-blueprint-discovery/v1','digest':package_hash,
       'appId':app_id,'appVersion':app_version,'candidates':[
          {'member':path,'id':data['id'],'version':data['version'],'title':data['title'],
           'sha256':digest,'minResources':len(data['requiredResources'])+sum(data.get('requiredPrefixes',{}).values())}
          for path,digest,data in parsed]}

def inspect_member(source:Path,repo:Path,expected_sha:str,member:str) -> dict:
    """Read-only single-blueprint details; no app execution or profile mutations."""
    if not isinstance(expected_sha,str) or not HEX.fullmatch(expected_sha) or \
        not isinstance(member,str) or not MEMBER.fullmatch(member):
        raise ValueError('TAVIB_SELECTION_INVALID')
    digest,app_id,app_version,entries=_validated_outer(source,repo)
    if digest!=expected_sha:raise ValueError('TAVIB_SOURCE_CHANGED')
    found=next(((name,sha,blueprint) for name,sha,blueprint in entries if name==member),None)
    if found is None:raise ValueError('TAVIB_SELECTION_INVALID')
    name,sha,blueprint=found
    # Validating the outer lock and inner manifest above precedes all read access.
    with zipfile.ZipFile(source) as outer:
        raw=outer.read(name)
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('TAVIB_SOURCE_CHANGED')
    with zipfile.ZipFile(__import__('io').BytesIO(raw)) as inner:
        documentation=inner.read('README.md').decode('utf-8') if 'README.md' in inner.namelist() else ''
        preview=inner.read('preview.webp') if 'preview.webp' in inner.namelist() else b''
    return {'schema':'tavix.studio.tavib-inspection/v1','appId':app_id,'appVersion':app_version,
        'appDigest':digest,'member':member,'sha256':sha,'id':blueprint['id'],
        'version':blueprint['version'],'title':blueprint['title'],
        'description':blueprint['description'],'applicablePackTypes':blueprint['applicablePackTypes'],
        'requiredResources':blueprint['requiredResources'],'requiredPrefixes':blueprint.get('requiredPrefixes',{}),
        'optionalResources':blueprint['optionalResources'],'designerChecklist':blueprint['designerChecklist'],
        'readme':documentation[:8192],
        'previewBase64':base64.b64encode(preview).decode('ascii') if preview else None,
        'localOnly':True,'publicationAuthorized':False}

def import_selected(source:Path,repo:Path,expected_sha:str,members:list[str]):
    if not isinstance(expected_sha,str) or not HEX.fullmatch(expected_sha) or not isinstance(members,list) or \
        not 1<=len(members)<=MAX_BPS or any(not isinstance(n,str) or not MEMBER.fullmatch(n) for n in members) or len(set(members))!=len(members):
        raise ValueError('TAVIB_SELECTION_INVALID')
    actual,app_id,app_version,parsed=_validated_outer(source,repo)
    if actual!=expected_sha:raise ValueError('TAVIB_SOURCE_CHANGED')
    available={name:(digest,data) for name,digest,data in parsed}
    if any(name not in available for name in members):raise ValueError('TAVIB_SELECTION_INVALID')
    root=local_directory()
    origin=root/'.origins'
    if origin.exists() and origin.is_symlink():raise ValueError('TAVIB_STORAGE_UNSAFE')
    origin.mkdir(parents=True,exist_ok=True)
    result=[]
    # Preflight *all* requested destinations before writing any of them.
    for name in members:
        digest,data=available[name]
        ident='local-app-'+hashlib.sha256((app_id+'\0'+data['id']+'\0'+data['version']+'\0'+digest).encode()).hexdigest()[:24]
        target=root/(ident+'.json'); provenance=origin/(ident+'.json')
        if target.exists() or provenance.exists():raise ValueError('TAVIB_ALREADY_IMPORTED')
        entry={**data,'id':ident}
        validate_blueprint(entry,local=True)
        record={'schema':'tavix.studio.embedded-blueprint-origin/v1','appId':app_id,'appVersion':app_version,
                'appDigest':actual,'upstreamId':data['id'],'blueprintVersion':data['version'],
                'tavibDigest':digest,'member':name}
        result.append((target,provenance,entry,record))
    written=[]
    try:
        for path,origin_path,entry,record in result:
            for target,raw in ((path,json.dumps(entry,ensure_ascii=True,sort_keys=True).encode('ascii')),
                               (origin_path,json.dumps(record,ensure_ascii=True,sort_keys=True).encode('ascii'))):
                with target.open('xb') as handle:handle.write(raw);handle.flush();os.fsync(handle.fileno())
                written.append(target)
    except Exception:
        for target in written:target.unlink(missing_ok=True)
        raise ValueError('TAVIB_IMPORT_FAILED') from None
    return {'schema':'tavix.studio.embedded-blueprint-import/v1','imported':len(result),
            'ids':[x[2]['id'] for x in result],'originApp':app_id,'publication':False}
