"""Trusted native-only LoopRD Assets DAPI bridge, matching tavi-assets/looprd/handler.py.

The saved target paths and local reviewed package come from Rust. Credentials are
short-lived *scoped service credentials* provisioned into the native environment,
never renderer input, JSON profile fields or source artifacts. No Social admin
impersonation, login bypass, Git operation or ambient HTTP proxy/redirect.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
import re
import ssl
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

HOST = re.compile(r'^https://[A-Za-z0-9.-]{1,172}$')
PATH = re.compile(r'^/[A-Za-z0-9._/-]{1,179}$')
PACK = re.compile(r'^[a-z0-9][a-z0-9._-]{0,126}$')
VER = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')
HEX = re.compile(r'^[a-f0-9]{64}$')
MAX_ARCHIVE = 48*1024*1024
CHUNK_SIZE = 96*1024

class RegistryError(ValueError):
    pass

def url(host: str, path: str, tail: str) -> str:
    if not isinstance(host,str) or not HOST.fullmatch(host) or '..' in host or host.endswith('.') or host[8:].startswith('.'):
        raise RegistryError('LOOPRD_ENDPOINT_INVALID')
    if not isinstance(path,str) or not PATH.fullmatch(path) or not path.endswith(tail) or '//' in path or any(x in ('.','..','') for x in path[1:].split('/')):
        raise RegistryError('LOOPRD_ENDPOINT_INVALID')
    return host+path

def token_for(scope: str) -> str:
    env={'catalog':'LOOPRD_ASSETS_READ_TOKEN', 'inspect':'LOOPRD_ASSETS_PUBLISH_TOKEN',
         'stage':'LOOPRD_ASSETS_INGEST_TOKEN','publish':'LOOPRD_ASSETS_PUBLISH_TOKEN'}[scope]
    token=os.environ.get(env,'')
    if not token or len(token)<32 or any(ord(c)<33 or ord(c)>126 for c in token):
        raise RegistryError('LOOPRD_SCOPED_TOKEN_REQUIRED')
    return token

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def request(target: str, credential: str, operation: str, **fields) -> dict:
    """Fixed HTTPS POST to an operator-saved path. Never follow redirects/proxies."""
    if len(credential)<32:raise RegistryError('LOOPRD_SCOPED_TOKEN_REQUIRED')
    data=json.dumps({'op':operation,**fields},separators=(',',':')).encode('utf-8')
    if len(data)>260_000:raise RegistryError('LOOPRD_REQUEST_TOO_LARGE')
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),_NoRedirect(),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    req=urllib.request.Request(target,data=data,method='POST',headers={
        'Content-Type':'application/json','Accept':'application/json',
        'Authorization':'Bearer '+credential,'User-Agent':'TaviX-Studio-Native-LoopRD/1'})
    try:
        with opener.open(req,timeout=15) as res:
            if int(res.headers.get('Content-Length','0') or '0')>256000:raise RegistryError('LOOPRD_RESPONSE_TOO_LARGE')
            raw=res.read(256001)
    except urllib.error.HTTPError as exc:
        if exc.code in (401,403):raise RegistryError('LOOPRD_SCOPE_REJECTED') from None
        raise RegistryError('LOOPRD_HTTP_ERROR') from None
    except (OSError,TimeoutError,urllib.error.URLError):
        raise RegistryError('LOOPRD_UNREACHABLE') from None
    if len(raw)>256000:raise RegistryError('LOOPRD_RESPONSE_TOO_LARGE')
    try:result=json.loads(raw)
    except (ValueError,UnicodeError):raise RegistryError('LOOPRD_RESPONSE_INVALID') from None
    if not isinstance(result,dict):raise RegistryError('LOOPRD_RESPONSE_INVALID')
    if result.get('ok') is not True:raise RegistryError('LOOPRD_OPERATION_REJECTED')
    return result

def catalog(host: str, catalog_path: str) -> dict:
    result=request(url(host,catalog_path,'/catalog'),token_for('catalog'),'catalog')
    entries=result.get('packs')
    if not isinstance(entries,list):raise RegistryError('LOOPRD_RESPONSE_INVALID')
    packs=[]
    for row in entries[:250]:
        if not isinstance(row,dict):continue
        pid,ver,digest=row.get('packId'),row.get('version'),row.get('manifestSha256')
        if isinstance(pid,str) and PACK.fullmatch(pid) and isinstance(ver,str) and VER.fullmatch(ver) and isinstance(digest,str) and HEX.fullmatch(digest):
            packs.append({'packId':pid,'version':ver,'manifestSha256':digest,'status':'published'})
    return {'schema':'tavix.studio.looprd-live/v1','scope':'assets:read','connected':True,
            'packs':packs,'truncated':len(entries)>len(packs),'officialStorePublished':False}

def inspect(host: str, admin_path: str) -> dict:
    result=request(url(host,admin_path,'/admin'),token_for('inspect'),'inspect')
    rows=result.get('versions')
    if not isinstance(rows,list):raise RegistryError('LOOPRD_RESPONSE_INVALID')
    versions=[]
    for row in rows[:200]:
        if not isinstance(row,dict):continue
        pid,ver,digest,status=row.get('packId'),row.get('version'),row.get('manifestSha256'),row.get('status')
        if isinstance(pid,str) and PACK.fullmatch(pid) and isinstance(ver,str) and VER.fullmatch(ver) and isinstance(digest,str) and HEX.fullmatch(digest) and status in ('ready','published','revoked','uploading'):
            versions.append({'packId':pid,'version':ver,'manifestSha256':digest,'status':status})
    return {'schema':'tavix.studio.looprd-inspection/v1','scope':'assets:publish',
            'connected':True,'versions':versions}

def connection(host: str, admin_path: str, catalog_path: str) -> dict:
    """Independently test read and publisher scopes; never infer authorization from HEAD."""
    result={'schema':'tavix.studio.looprd-connection/v1','configured':True,'read':False,
            'inspect':False,'ingestCredentialPresent':bool(os.environ.get('LOOPRD_ASSETS_INGEST_TOKEN')),
            'publishCredentialPresent':bool(os.environ.get('LOOPRD_ASSETS_PUBLISH_TOKEN')),
            'serverPublisherApproved':False,'checks':[]}
    for name,func,path in [('catalog',catalog,catalog_path),('admin',inspect,admin_path)]:
        try:
            data=func(host,path)
            result['read' if name=='catalog' else 'inspect']=True
            result['checks'].append({'service':name,'code':'LOOPRD_'+name.upper()+'_AUTHORIZED','count':len(data['packs' if name=='catalog' else 'versions'])})
        except RegistryError as exc:
            result['checks'].append({'service':name,'code':str(exc)})
    return result

def _source(package:Path,review:Path,digest:str) -> tuple[dict,str,str]:
    if not HEX.fullmatch(digest) or package.is_symlink() or not package.is_file() or not 0<package.stat().st_size<=MAX_ARCHIVE or review.is_symlink() or not review.is_file() or review.stat().st_size>100000:
        raise RegistryError('LOOPRD_SOURCE_INVALID')
    row=json.loads(review.read_text(encoding='utf-8'))
    if row.get('sha256')!=digest or row.get('kind')!='tavia' or row.get('status')!='review_approved' or row.get('canonicalValid') is not True or row.get('storeReady') is not True:
        raise RegistryError('LOOPRD_REVIEW_REQUIRED')
    actual=hashlib.sha256(package.read_bytes()).hexdigest()
    if actual!=digest:raise RegistryError('LOOPRD_SOURCE_CHANGED')
    pid,ver=row.get('packageId'),row.get('version')
    if not isinstance(pid,str) or not PACK.fullmatch(pid) or not isinstance(ver,str) or not VER.fullmatch(ver):
        raise RegistryError('LOOPRD_SOURCE_INVALID')
    return row,pid,ver

def _receipt(receipt_file:Path,expected:dict) -> None:
    if receipt_file.is_symlink() or not receipt_file.is_file() or not 0<receipt_file.stat().st_size<=4096:
        raise RegistryError('LOOPRD_RECEIPT_REQUIRED')
    try:
        data=json.loads(receipt_file.read_text(encoding='utf-8'))
    except (ValueError,OSError):raise RegistryError('LOOPRD_RECEIPT_INVALID') from None
    if not isinstance(data,dict) or any(data.get(k)!=v for k,v in expected.items()):
        raise RegistryError('LOOPRD_RECEIPT_INVALID')

def stage(host:str,admin_path:str,package:str,review:str,digest:str,receipt_file:str,assets_root:str) -> dict:
    target=url(host,admin_path,'/admin')
    package,review=Path(package),Path(review)
    _,pid,ver=_source(package,review,digest)
    _receipt(Path(receipt_file),{'action':'stage','approvedSha256':digest,'endpoint':target})
    credential=token_for('stage')
    root=Path(assets_root)
    if root.is_symlink() or not root.is_dir() or not (root/'project.zr').is_file() or not (root/'src/tavi_assets/tavia.py').is_file():
        raise RegistryError('LOOPRD_CANONICAL_ASSETS_REQUIRED')
    try:identity=json.loads((root/'project.zr').read_text(encoding='utf-8'))
    except (OSError,ValueError):raise RegistryError('LOOPRD_CANONICAL_ASSETS_REQUIRED') from None
    if identity.get('project_key')!='tavi-assets':raise RegistryError('LOOPRD_CANONICAL_ASSETS_REQUIRED')
    sys.path.insert(0,str(root/'src'))
    from tavi_assets.tavia import unpack_tavia
    with tempfile.TemporaryDirectory(prefix='tavix-approved-stage-') as folder:
        manifest=unpack_tavia(package,folder)
        if manifest.get('id')!=pid or manifest.get('version')!=ver:raise RegistryError('LOOPRD_SOURCE_INVALID')
        start=request(target,credential,'begin',manifest=manifest)
        for name in sorted(manifest['files']):
            source=Path(folder)/name
            offset=0
            with source.open('rb') as f:
                while chunk:=f.read(CHUNK_SIZE):
                    request(target,credential,'chunk',packId=pid,version=ver,name=name,offset=offset,contentBase64=base64.b64encode(chunk).decode('ascii'))
                    offset+=len(chunk)
        finish=request(target,credential,'finalize',packId=pid,version=ver)
    if finish.get('status')!='ready':raise RegistryError('LOOPRD_STAGE_UNVERIFIED')
    return {'status':'ready','packId':pid,'version':ver,'sha256':digest,
            'published':False,'operatorApprovalRequired':True}

def publish(host:str,admin_path:str,package:str,review:str,digest:str,receipt_file:str) -> dict:
    target=url(host,admin_path,'/admin')
    _,pid,ver=_source(Path(package),Path(review),digest)
    row=inspect(host,admin_path)  # uses publisher scope and verifies current server state
    match=next((x for x in row['versions'] if x['packId']==pid and x['version']==ver),None)
    if match is None or match['status']!='ready':raise RegistryError('LOOPRD_NOT_STAGED')
    _receipt(Path(receipt_file),{'action':'publish','packId':pid,'version':ver,
        'manifestSha256':match['manifestSha256'],'endpoint':target})
    result=request(target,token_for('publish'),'publish',packId=pid,version=ver)
    if result.get('status')!='published':raise RegistryError('LOOPRD_PUBLISH_UNVERIFIED')
    return {'status':'published','packId':pid,'version':ver,
            'manifestSha256':match['manifestSha256'],'archiveSha256':digest,
            'officialRegistryPublished':True,'entitlementsGranted':False}
