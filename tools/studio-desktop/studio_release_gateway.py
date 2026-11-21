"""Operator-initiated GitHub release gateway for explicitly public artifacts.

Uses an existing authenticated `gh` installation; never accepts a token, arbitrary
command, executable path, URL, or source file from the renderer. GitHub releases
are NOT LoopRD/Tavi Assets registry publications or Store entitlements.
"""
from __future__ import annotations
import hashlib,json,os,re,shutil,subprocess,urllib.request,urllib.error,ssl
from pathlib import Path
from studio_publisher_probe import REPO,NoRedirect

HEX=re.compile(r'^[0-9a-f]{64}$')
TAG=re.compile(r'^tavi-(?:tavix|tavia)-[a-z0-9][a-z0-9._-]{0,126}-v\d+\.\d+\.\d+$')
MAX_SOURCE=48*1024*1024

def _gh(args:list[str], *, timeout=40):
    if shutil.which('gh') is None:raise ValueError('GITHUB_CLI_MISSING')
    env={**os.environ,'GH_PROMPT_DISABLED':'1','GIT_TERMINAL_PROMPT':'0'}
    try:
        proc=subprocess.run(['gh',*args],capture_output=True,env=env,timeout=timeout,check=False)
    except (OSError,subprocess.TimeoutExpired):raise ValueError('GITHUB_COMMAND_FAILED') from None
    if proc.returncode:raise ValueError('GITHUB_COMMAND_FAILED')
    return proc.stdout[:262144]

def connection():
    if shutil.which('gh') is None:
        return {'authenticated':False,'code':'GITHUB_CLI_MISSING','howToConnect':'Install GitHub CLI and run gh auth login outside Studio'}
    try:
        _gh(['auth','status','-h','github.com'],timeout=8)
        return {'authenticated':True,'code':'GITHUB_AUTH_PRESENT','howToConnect':''}
    except ValueError:
        return {'authenticated':False,'code':'GITHUB_AUTH_REQUIRED','howToConnect':'Run gh auth login outside Studio'}

def _clean(value,maximum=120):
    return ''.join(c for c in value if c.isprintable() and c not in '\r\n\t')[:maximum]

def _fetch_public(repo):
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect(),
                                        urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    req=urllib.request.Request('https://api.github.com/repos/'+repo+'/releases?per_page=20',
        headers={'User-Agent':'TaviX-Studio-Public-Releases/1','Accept':'application/vnd.github+json'},method='GET')
    with opener.open(req,timeout=6) as response:
        if int(response.headers.get('Content-Length','0') or '0')>256*1024:raise ValueError('GITHUB_RESPONSE_TOO_LARGE')
        return response.read(256*1024+1)

def public_catalog(repo):
    """Read-only public approved index visibility; NOT entitlement validation."""
    if not REPO.fullmatch(repo):raise ValueError('PUBLISH_DESTINATION_INVALID')
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect(),
                                        urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    url='https://raw.githubusercontent.com/'+repo+'/main/catalog.json'
    req=urllib.request.Request(url,headers={'User-Agent':'TaviX-Studio-Catalog-Read/1'},method='GET')
    try:
        with opener.open(req,timeout=5) as reply: blob=reply.read(128*1024+1)
    except urllib.error.HTTPError as exc:
        return {'status':'not_published' if exc.code==404 else 'unverified','code':'CATALOG_NOT_FOUND' if exc.code==404 else 'CATALOG_HTTP_ERROR'}
    except (OSError,TimeoutError,urllib.error.URLError,ValueError):
        return {'status':'unverified','code':'CATALOG_UNREACHABLE'}
    if len(blob)>128*1024:return {'status':'unverified','code':'CATALOG_TOO_LARGE'}
    try:
        index=json.loads(blob)
        if not isinstance(index,dict) or not isinstance(index.get('schema'),str):raise ValueError()
        entries=sum(len(index.get(key,[])) for key in ('packs','schematics') if isinstance(index.get(key),list))
        return {'status':'visible','code':'PUBLIC_CATALOG_FOUND','schema':_clean(index['schema'],100),'entries':min(entries,100000)}
    except (ValueError,UnicodeError,TypeError):
        return {'status':'unverified','code':'CATALOG_INVALID'}

def releases(repo):
    if not REPO.fullmatch(repo):raise ValueError('PUBLISH_DESTINATION_INVALID')
    auth=connection()
    scope='public_only'
    if auth['authenticated']:
        try:
            blob=_gh(['api','--method','GET',f'repos/{repo}/releases','-f','per_page=20'],timeout=12)
            scope='authenticated'
        except ValueError:blob=_fetch_public(repo)
    else:blob=_fetch_public(repo)
    if len(blob)>262144:raise ValueError('GITHUB_RESPONSE_TOO_LARGE')
    data=json.loads(blob)
    if not isinstance(data,list):raise ValueError('GITHUB_RESPONSE_INVALID')
    entries=[]
    for item in data[:20]:
        if not isinstance(item,dict):continue
        tag=item.get('tag_name');url=item.get('html_url')
        if not isinstance(tag,str) or len(tag)>180:continue
        if not isinstance(url,str) or not re.fullmatch(r'https://github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/releases/tag/[A-Za-z0-9_.%-]+',url):
            url=''
        entries.append({'tag':_clean(tag,180),'title':_clean(str(item.get('name','')),140),
            'publishedAt':_clean(str(item.get('published_at') or ''),40),
            'draft':bool(item.get('draft')),'prerelease':bool(item.get('prerelease')),'url':url})
    return {'schema':'tavix.studio.github-release-list/v1','repository':repo,'scope':scope,
            'authenticated':auth['authenticated'],'authCode':auth['code'],'releases':entries,
            'officialStorePublished':False,'catalog':public_catalog(repo)}

def _identity(package:Path, expected:str,record:Path):
    if not HEX.fullmatch(expected) or package.is_symlink() or not package.is_file() or \
       not 0<package.stat().st_size<=MAX_SOURCE or record.is_symlink() or not record.is_file() or record.stat().st_size>100000:
        raise ValueError('RELEASE_SOURCE_INVALID')
    data=json.loads(record.read_text(encoding='utf-8'))
    if data.get('sha256')!=expected or data.get('status')!='review_approved' or \
       data.get('canonicalValid') is not True or data.get('storeReady') is not True:
        raise ValueError('RELEASE_APPROVAL_REQUIRED')
    h=hashlib.sha256()
    with package.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    if h.hexdigest()!=expected:raise ValueError('RELEASE_SOURCE_CHANGED')
    kind=data.get('kind');ident=data.get('packageId');version=data.get('version')
    if kind not in ('tavix','tavia') or not isinstance(ident,str) or not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,126}',ident) or \
        not isinstance(version,str) or not re.fullmatch(r'\d+\.\d+\.\d+',version):
        raise ValueError('RELEASE_IDENTITY_INVALID')
    return kind,ident,version

def _tag(kind,ident,version):return f'tavi-{kind}-{ident}-v{version}'

def _receipt_path(record:Path):
    # `reviews/<sha>.json` and sibling `publication-receipts/<sha>.json`
    root=record.parent.parent
    dest=root/'publication-receipts'
    if dest.exists() and dest.is_symlink():raise ValueError('RELEASE_RECEIPT_UNSAFE')
    dest.mkdir(parents=True,exist_ok=True)
    return dest/record.name

def draft(repo,package,record,expected):
    if not REPO.fullmatch(repo):raise ValueError('PUBLISH_DESTINATION_INVALID')
    package=Path(package);record=Path(record)
    kind,ident,version=_identity(package,expected,record)
    if not connection()['authenticated']:raise ValueError('GITHUB_AUTH_REQUIRED')
    tag=_tag(kind,ident,version)
    receipt=_receipt_path(record)
    if receipt.exists():raise ValueError('RELEASE_ALREADY_PREPARED')
    # Tag, title and notes are derived from validated local review; never from renderer.
    _gh(['release','create',tag,str(package)+'#'+ident+'-'+version+'.'+kind,
         '--repo',repo,'--draft','--title',ident+' '+version,
         '--notes','TaviX Studio exact-artifact review SHA-256: '+expected+'\n'
                   'GitHub distribution only; NOT LoopRD entitlement or official Store publication.'],timeout=70)
    data={'schema':'tavix.studio.github-release-receipt/v1','repo':repo,'tag':tag,
          'sha256':expected,'status':'draft','kind':kind,'id':ident,'version':version}
    with receipt.open('xb') as handle:
        handle.write(json.dumps(data,sort_keys=True).encode('ascii'));handle.flush();os.fsync(handle.fileno())
    return {'status':'draft','tag':tag,'digestPrefix':expected[:12],'officialStorePublished':False}

def publish(repo,record,expected):
    if not REPO.fullmatch(repo) or not HEX.fullmatch(expected):raise ValueError('PUBLISH_DESTINATION_INVALID')
    record=Path(record);receipt=_receipt_path(record)
    if receipt.is_symlink() or not receipt.is_file() or receipt.stat().st_size>4096:raise ValueError('RELEASE_DRAFT_REQUIRED')
    data=json.loads(receipt.read_text(encoding='utf-8'))
    if data.get('schema')!='tavix.studio.github-release-receipt/v1' or data.get('repo')!=repo or \
       data.get('sha256')!=expected or data.get('status')!='draft' or not TAG.fullmatch(data.get('tag','')):
        raise ValueError('RELEASE_DRAFT_REQUIRED')
    if not connection()['authenticated']:raise ValueError('GITHUB_AUTH_REQUIRED')
    _gh(['release','edit',data['tag'],'--repo',repo,'--draft=false'],timeout=40)
    data['status']='public'
    tmp=receipt.with_suffix('.json.new')
    with tmp.open('xb') as handle:
        handle.write(json.dumps(data,sort_keys=True).encode('ascii'));handle.flush();os.fsync(handle.fileno())
    os.replace(tmp,receipt)
    return {'status':'public','tag':data['tag'],'digestPrefix':expected[:12],
            'officialStorePublished':False}

def receipt(expected,record):
    if not HEX.fullmatch(expected):raise ValueError('RELEASE_IDENTITY_INVALID')
    path=_receipt_path(Path(record))
    if not path.exists():return {'status':'none'}
    if path.is_symlink() or path.stat().st_size>4096:raise ValueError('RELEASE_RECEIPT_UNSAFE')
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('sha256')!=expected or data.get('status') not in ('draft','public'):
        raise ValueError('RELEASE_RECEIPT_UNSAFE')
    return {'status':data['status'],'tag':data['tag'],'repo':data['repo'],'officialStorePublished':False}
