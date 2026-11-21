"""GitHub-backed Tavi Assets source catalog review and explicit draft PR proposal.

- Studio is the editor; GitHub holds reviewed source revisions.
- A PR for a *draft* source record is not a public pack release, an entitlement,
  or an official LoopRD publication. No package bytes are uploaded here.
- All credentials remain with the existing GitHub CLI; never in renderer/state.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
import re
import secrets
import shutil
import ssl
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from studio_publisher_probe import REPO, NoRedirect

HEX = re.compile(r'^[a-f0-9]{64}$')
GIT_SHA = re.compile(r'^[a-f0-9]{40}(?:[a-f0-9]{24})?$')
IDENT = re.compile(r'^[a-z0-9][a-z0-9._-]{0,126}$')
VERSION = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')
BRANCH = re.compile(r'^[A-Za-z0-9._/-]{1,120}$')
SOURCE_SCHEMA = 'tavi.assets.repository-source/v1'
INDEX_SCHEMA = 'tavi.assets.repository-index/v1'
MAX_CATALOG = 512 * 1024
MAX_ARCHIVE = 48 * 1024 * 1024


def _validate_repo(repo):
    if not isinstance(repo,str) or not REPO.fullmatch(repo):
        raise ValueError('GITHUB_CATALOG_DESTINATION_INVALID')
    # This interface only edits the canonical asset source, never an app catalog.
    if repo.lower() != 'thebigtreeinc/tavi-assets':
        raise ValueError('GITHUB_ASSETS_REPOSITORY_REQUIRED')
    return repo


def _cli(args, *, payload=None, timeout=25):
    if shutil.which('gh') is None:
        raise ValueError('GITHUB_CLI_MISSING')
    env={**os.environ,'GH_HOST':'github.com','GH_PROMPT_DISABLED':'1','GIT_TERMINAL_PROMPT':'0'}
    path=None
    try:
        # Use file input rather than passing JSON or archive bytes through argv.
        if payload is not None:
            with tempfile.NamedTemporaryFile(mode='w',suffix='.json',encoding='utf-8',delete=False) as f:
                json.dump(payload,f,ensure_ascii=False,separators=(',',':'))
                path=f.name
            args=[*args,'--input',path]
        result=subprocess.run(['gh',*args],capture_output=True,timeout=timeout,env=env,check=False)
        if result.returncode or len(result.stdout)>MAX_CATALOG*3:
            raise ValueError('GITHUB_CATALOG_API_FAILED')
        return json.loads(result.stdout)
    except (OSError,subprocess.TimeoutExpired,ValueError) as exc:
        if isinstance(exc,ValueError) and str(exc) in ('GITHUB_CLI_MISSING','GITHUB_CATALOG_API_FAILED'):
            raise
        raise ValueError('GITHUB_CATALOG_API_FAILED') from None
    finally:
        if path:
            try:os.unlink(path)
            except OSError:pass


def _get_api(path):
    """Authenticated gh when present; strict public GitHub API fallback for reads."""
    if shutil.which('gh') is not None:
        try:
            return _cli(['api','--method','GET',path],timeout=16)
        except ValueError:
            pass
    url='https://api.github.com/'+path
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect(),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    req=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json',
        'User-Agent':'TaviX-Studio-Catalog-Sync/1'},method='GET')
    try:
        with opener.open(req,timeout=12) as response:
            if int(response.headers.get('Content-Length','0') or '0')>MAX_CATALOG*3:
                raise ValueError('GITHUB_CATALOG_TOO_LARGE')
            data=response.read(MAX_CATALOG*3+1)
            if len(data)>MAX_CATALOG*3:raise ValueError('GITHUB_CATALOG_TOO_LARGE')
            return json.loads(data)
    except (urllib.error.URLError,OSError,TimeoutError,UnicodeError,json.JSONDecodeError):
        raise ValueError('GITHUB_CATALOG_READ_FAILED') from None


def _content(repo,path,revision):
    response=_get_api(f'repos/{repo}/contents/{path}?ref={revision}')
    if (not isinstance(response,dict) or response.get('encoding')!='base64' or
        not GIT_SHA.fullmatch(str(response.get('sha',''))) or
        not isinstance(response.get('content'),str)):
        raise ValueError('GITHUB_CATALOG_RESPONSE_INVALID')
    try:
        raw=base64.b64decode(response['content'],validate=False)
        if len(raw)>MAX_CATALOG:raise ValueError('GITHUB_CATALOG_TOO_LARGE')
        obj=json.loads(raw.decode('utf-8'))
    except (ValueError,UnicodeError):
        raise ValueError('GITHUB_CATALOG_RESPONSE_INVALID') from None
    if not isinstance(obj,dict):raise ValueError('GITHUB_CATALOG_RESPONSE_INVALID')
    return obj,response['sha']


def _catalog_shape(source,index):
    if (set(source)!={'schema','packs','schematics'} or source.get('schema')!=SOURCE_SCHEMA or
        set(index)!={'schema','packs','schematics'} or index.get('schema')!=INDEX_SCHEMA):
        raise ValueError('GITHUB_CATALOG_SCHEMA_UNSUPPORTED')
    for obj in (source,index):
        for kind in ('packs','schematics'):
            entries=obj[kind]
            if not isinstance(entries,list) or len(entries)>2000:
                raise ValueError('GITHUB_CATALOG_SCHEMA_UNSUPPORTED')
            seen=set()
            for item in entries:
                if not isinstance(item,dict):raise ValueError('GITHUB_CATALOG_SCHEMA_UNSUPPORTED')
                ident,version=item.get('id'),item.get('version')
                if (not isinstance(ident,str) or not IDENT.fullmatch(ident) or
                    not isinstance(version,str) or not VERSION.fullmatch(version) or
                    (ident,version) in seen):raise ValueError('GITHUB_CATALOG_SCHEMA_UNSUPPORTED')
                seen.add((ident,version))
                if kind=='packs':
                    expected_artifact=f'packs/{ident}/{version}/package.tavia'
                else:
                    expected_artifact=f'schematics/{ident}/{version}/blueprint.tavib'
                if item.get('artifact')!=expected_artifact:
                    raise ValueError('GITHUB_CATALOG_SCHEMA_UNSUPPORTED')
                if obj is source:
                    if (set(item)-{'id','version','artifact','sha256','visibility','status','approvalReference','blueprintId'}
                        or item.get('visibility') not in ('public','restricted')
                        or item.get('status') not in ('draft','approved')):
                        raise ValueError('GITHUB_CATALOG_SCHEMA_UNSUPPORTED')
                    if item['status']=='approved' and (item['visibility']!='public' or
                        not HEX.fullmatch(str(item.get('sha256',''))) or not isinstance(item.get('approvalReference'),str)
                        or len(item['approvalReference'])<5):
                        raise ValueError('GITHUB_CATALOG_SCHEMA_UNSUPPORTED')
                else:
                    if (item.get('status')!='approved' or
                        not HEX.fullmatch(str(item.get('sha256',''))) or
                        not isinstance(item.get('bytes'),int) or item['bytes']<1):
                        raise ValueError('GITHUB_CATALOG_SCHEMA_UNSUPPORTED')
    # Any published entry must correspond to an exact approved public source pin.
    for kind in ('packs','schematics'):
        published={(p['id'],p['version']):p for p in index[kind]}
        approved={(p['id'],p['version']):p for p in source[kind]
            if p.get('status')=='approved' and p.get('visibility')=='public'}
        if set(published)!=set(approved):raise ValueError('GITHUB_CATALOG_SOURCE_INDEX_MISMATCH')
        for key,row in published.items():
            s=approved[key]
            if row.get('sha256')!=s.get('sha256') or row.get('artifact')!=s.get('artifact'):
                raise ValueError('GITHUB_CATALOG_SOURCE_INDEX_MISMATCH')


def _snapshot(repo):
    repo=_validate_repo(repo)
    info=_get_api('repos/'+repo)
    branch=info.get('default_branch') if isinstance(info,dict) else None
    if not isinstance(branch,str) or not BRANCH.fullmatch(branch) or '..' in branch:
        raise ValueError('GITHUB_CATALOG_RESPONSE_INVALID')
    ref=_get_api(f'repos/{repo}/git/ref/heads/{branch}')
    revision=ref.get('object',{}).get('sha') if isinstance(ref,dict) else None
    if not isinstance(revision,str) or not GIT_SHA.fullmatch(revision):
        raise ValueError('GITHUB_CATALOG_RESPONSE_INVALID')
    source,source_sha=_content(repo,'catalog.source.json',revision)
    index,index_sha=_content(repo,'catalog.json',revision)
    _catalog_shape(source,index)
    return {'repository':repo,'branch':branch,'revision':revision,
        'sourceSha':source_sha,'indexSha':index_sha,'source':source,'index':index}


def sync(repo):
    s=_snapshot(repo)
    return {'schema':'tavix.studio.github-catalog/v1','repository':s['repository'],
        'branch':s['branch'],'revision':s['revision'],'sourceSha':s['sourceSha'],
        'indexSha':s['indexSha'],'sourceEntries':len(s['source']['packs'])+len(s['source']['schematics']),
        'publicPacks':len(s['index']['packs']),'publicSchematics':len(s['index']['schematics']),
        'packs':[{'id':p['id'],'version':p['version'],'status':p.get('status','unknown'),
                  'visibility':p.get('visibility','unknown'),'sha256':p.get('sha256','')} for p in s['source']['packs'][:250]],
        'publicIndexCurrent':True,'readOnly':True,'goldPricesAuthoritative':False}


def _approved_asset(source_path,review_path,digest):
    if not isinstance(digest,str) or not HEX.fullmatch(digest):raise ValueError('GITHUB_CATALOG_REVIEW_REQUIRED')
    path,review=Path(source_path),Path(review_path)
    if not path.is_file() or path.is_symlink() or not review.is_file() or review.is_symlink():
        raise ValueError('GITHUB_CATALOG_REVIEW_REQUIRED')
    if not 0<path.stat().st_size<=MAX_ARCHIVE or review.stat().st_size>100000:
        raise ValueError('GITHUB_CATALOG_REVIEW_REQUIRED')
    record=json.loads(review.read_text(encoding='utf-8'))
    if (record.get('kind')!='tavia' or record.get('sha256')!=digest or
        record.get('status')!='review_approved' or record.get('canonicalValid') is not True or
        record.get('storeReady') is not True or path.suffix!='.tavia'):
        raise ValueError('GITHUB_CATALOG_REVIEW_REQUIRED')
    ident,version=record.get('packageId'),record.get('version')
    if not isinstance(ident,str) or not IDENT.fullmatch(ident) or not isinstance(version,str) or not VERSION.fullmatch(version):
        raise ValueError('GITHUB_CATALOG_REVIEW_REQUIRED')
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    if h.hexdigest()!=digest:raise ValueError('GITHUB_CATALOG_SOURCE_CHANGED')
    return ident,version


def _plan(snapshot,source_path,review_path,digest):
    ident,version=_approved_asset(source_path,review_path,digest)
    source=snapshot['source']
    if any(x['id']==ident and x['version']==version for x in source['packs']):
        raise ValueError('GITHUB_CATALOG_ENTRY_EXISTS')
    # Draft is intentional: no package blob is uploaded and catalog.json is unchanged.
    # Official publication requires a separate, server-authorized release flow.
    entry={'id':ident,'version':version,
           'artifact':f'packs/{ident}/{version}/package.tavia',
           'sha256':digest,'visibility':'public','status':'draft'}
    updated=json.loads(json.dumps(source))
    updated['packs'].append(entry)
    updated['packs'].sort(key=lambda p:(p['id'],tuple(int(n) for n in p['version'].split('.'))))
    new_text=json.dumps(updated,ensure_ascii=False,indent=2)+'\n'
    new_digest=hashlib.sha256(new_text.encode('utf-8')).hexdigest()
    return entry,new_text,new_digest


def preview(repo,source_path,review_path,digest,expected_revision):
    s=_snapshot(repo)
    if expected_revision!=s['revision']:
        raise ValueError('GITHUB_CATALOG_STALE_REVISION')
    entry,_,proposal_hash=_plan(s,source_path,review_path,digest)
    return {'schema':'tavix.studio.catalog-proposal/v1','repository':s['repository'],
        'baseRevision':s['revision'],'sourceSha':s['sourceSha'],
        'proposalSha256':proposal_hash,'packageSha256':digest,'entry':entry,
        'diff':{'file':'catalog.source.json','action':'add_draft','before':None,'after':entry},
        'catalogJsonChanged':False,'assetUploaded':False,'priceChanged':False,
        'effect':'Draft source entry only. Requires separate approval and artifact publication. No Gold or entitlement change.'}


def prepare(repo,source_path,review_path,digest,expected_revision,proposal_sha):
    if not GIT_SHA.fullmatch(str(expected_revision)) or not HEX.fullmatch(str(proposal_sha)):
        raise ValueError('GITHUB_CATALOG_CONFIRMATION_REQUIRED')
    if shutil.which('gh') is None:raise ValueError('GITHUB_CLI_MISSING')
    from studio_release_gateway import connection
    if not connection()['authenticated']:raise ValueError('GITHUB_AUTH_REQUIRED')
    s=_snapshot(repo)
    if expected_revision!=s['revision']:
        raise ValueError('GITHUB_CATALOG_STALE_REVISION')
    entry,text,new_sha=_plan(s,source_path,review_path,digest)
    if new_sha!=proposal_sha:raise ValueError('GITHUB_CATALOG_CONFIRMATION_REQUIRED')
    branch=f'studio/catalog-draft-{digest[:12]}-{secrets.token_hex(4)}'
    # All write APIs use a fixed, validated repository and generated payloads.
    _cli(['api','--method','POST',f'repos/{repo}/git/refs'],payload={'ref':'refs/heads/'+branch,'sha':s['revision']})
    _cli(['api','--method','PUT',f'repos/{repo}/contents/catalog.source.json'],payload={
        'message':f'Catalog draft: {entry["id"]} {entry["version"]}',
        'content':base64.b64encode(text.encode('utf-8')).decode('ascii'),
        'sha':s['sourceSha'],'branch':branch})
    result=_cli(['api','--method','POST',f'repos/{repo}/pulls'],payload={
        'title':f'Catalog draft: {entry["id"]} {entry["version"]}',
        'head':branch,'base':s['branch'],'draft':True,
        'body':f'Prepared by TaviX Studio from locally approved exact SHA-256 `{digest}`.\n\n'
            'This is **draft metadata only**. No archive is included, `catalog.json` is unchanged, '
            'and merging this PR does not authorize a store listing, a Gold price, or an entitlement. '
            'Do not approve/promote the pack until its separate signed/publication review is complete.'})
    url=result.get('html_url') if isinstance(result,dict) else None
    if not isinstance(url,str) or not re.fullmatch(r'https://github\.com/'+re.escape(repo)+r'/pull/\d+',url,flags=re.IGNORECASE):
        raise ValueError('GITHUB_CATALOG_PR_UNVERIFIED')
    return {'schema':'tavix.studio.catalog-pr/v1','status':'draft_pr_created',
            'url':url,'branch':branch,'repository':repo,
            'baseRevision':s['revision'],'proposalSha256':new_sha,
            'publicCatalogUpdated':False,'officialStorePublished':False,
            'entitlementsGranted':False}


def login():
    """Start a native terminal browser login. Never returns GitHub credentials."""
    if shutil.which('gh') is None:raise ValueError('GITHUB_CLI_MISSING')
    if os.name!='nt':raise ValueError('GITHUB_LOGIN_TERMINAL_REQUIRED')
    flags=getattr(subprocess,'CREATE_NEW_CONSOLE',0)
    env={**os.environ,'GH_HOST':'github.com'}
    env.pop('GH_PROMPT_DISABLED',None)
    try:
        subprocess.Popen(['gh','auth','login','--web','--clipboard','--hostname','github.com',
                          '--git-protocol','https'],env=env,creationflags=flags,
                         stdin=None,stdout=None,stderr=None,close_fds=True)
    except OSError:raise ValueError('GITHUB_LOGIN_LAUNCH_FAILED') from None
    return {'launched':True,'method':'github_cli_browser','credentialsStoredInStudio':False,
            'message':'Finish GitHub sign-in in the opened browser/terminal, then choose Check GitHub sign-in.'}
