"""Operator-local management facade; no app/extension can invoke privileged operations.

The local console is a development tool, NOT Tavi's trusted production host.
Mutations here create local drafts only; registry publish and Git push are separate gates.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from urllib.parse import urlsplit
import os

from tools.local_client.manager_assets import inspect_tavia, require_assets_source
from tools.local_client.manager_secrets import SecretStore
from tools.local_client.manager_events import EventJournal

REPO = re.compile(r'^[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}$')
PACK_ID = re.compile(r'^[a-z0-9][a-z0-9._-]{0,126}$')
VERSION = re.compile(r'^\d+\.\d+\.\d+$')
MAX_PRICE = 1_000_000


def checked_https(endpoint, suffix):
    parts = urlsplit(endpoint)
    if (parts.scheme != 'https' or not parts.hostname or parts.username or parts.password
            or parts.query or parts.fragment or parts.port and not (1 <= parts.port <= 65535)):
        raise ValueError('Use an approved HTTPS LoopRD DAPI endpoint')
    if not endpoint.endswith(suffix) or '//' in parts.path or '..' in parts.path:
        raise ValueError('Expected the exact LoopRD ' + suffix + ' DAPI endpoint')
    return endpoint


def safe_json(data, cap=256*1024):
    blob = json.dumps(data, ensure_ascii=False)
    if len(blob.encode()) > cap:
        raise ValueError('Remote response exceeds bounded display size')
    def scrub(value):
        if isinstance(value, list):
            return [scrub(v) for v in value]
        if isinstance(value, dict):
            return {k: scrub(v) for k,v in value.items()
                    if not any(s in k.lower() for s in ('token','secret','password','authorization','credential'))}
        return value
    return scrub(data)


def api_request(url, token, operation=None):
    if not token:
        raise ValueError('Required scoped credential is not connected')
    headers = {'Accept':'application/vnd.github+json' if operation is None else 'application/json',
               'Authorization':'Bearer '+token, 'User-Agent':'TaviX-local-suite/0.1.27'}
    payload = None if operation is None else json.dumps({'op':operation}).encode('utf-8')
    if payload is not None: headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=payload, headers=headers,
                                 method='GET' if payload is None else 'POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read(256*1024 + 1)
    except urllib.error.HTTPError as exc:
        raise ValueError('Remote service refused the request (HTTP '+str(exc.code)+')') from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ValueError('Remote service unavailable') from None
    if len(raw) > 256*1024: raise ValueError('Remote response exceeds bounded display size')
    result = json.loads(raw)
    if operation is not None and (not isinstance(result, dict) or result.get('ok') is not True):
        raise ValueError('LoopRD denied this operation')
    return safe_json(result)


class Management:
    def __init__(self, root, assets_root=None, private_root=None, secrets=None):
        self.root = Path(root).resolve()
        self.assets_root = None
        self.private = Path(private_root or Path.home()/'.tavix-suite').resolve()
        if self.private.is_relative_to(self.root):
            raise ValueError('Operator data must be outside the TaviX source repository')
        self.secrets = secrets or SecretStore(self.private)
        self.events = EventJournal(self.private)
        self.lock = threading.RLock()
        if assets_root is None:
            adjacent = self.root.parent / 'tavi-assets'
            if adjacent.is_dir(): assets_root = adjacent
        if assets_root is not None:
            self.assets_root = require_assets_source(assets_root)
        self._settings = self._read_json('settings.json', {})

    def _read_json(self, name, default):
        file = self.private / name
        if not file.is_file(): return default
        value = json.loads(file.read_text(encoding='utf-8'))
        if not isinstance(value, type(default)): raise ValueError('Invalid local management state')
        return value

    def _write_json(self, name, value):
        self.private.mkdir(parents=True, mode=0o700, exist_ok=True)
        file = self.private / name
        tmp = self.private / (name+'.new')
        tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        os.chmod(tmp, 0o600)
        os.replace(tmp, file)

    def git_status(self):
        def run(*args):
            result = subprocess.run(['git','-C',str(self.root), *args], capture_output=True,
                                    text=True, timeout=7, encoding='utf-8', errors='replace')
            return result.stdout.strip() if result.returncode == 0 else None
        branch = run('branch','--show-current')
        sha = run('rev-parse','HEAD')
        changes = run('status','--porcelain=v1','--untracked-files=no')
        return {'available': sha is not None, 'branch':branch, 'head':sha,
                'trackedDirty':bool(changes), 'trackedChangeCount':len(changes.splitlines()) if changes else 0,
                'pushAuthorized':False}

    def bootstrap(self):
        catalog = self._read_repository()
        return {'schema':'tavix.manager/v1', 'title':'TaviX Management Suite',
                'assetsSourceReady':self.assets_root is not None,
                'credentialsPersistent':self.secrets.persistent,
                'githubConnected':bool(self.secrets.get('github')),
                'githubRepository':self._settings.get('githubRepository','TheBigTreeInc/tavix'),
                'looprdConfigured':bool(self._settings.get('looprdCatalog') and self._settings.get('looprdAdmin')),
                'looprdCatalogEndpoint':self._settings.get('looprdCatalog',''),
                'looprdAdminEndpoint':self._settings.get('looprdAdmin',''),
                'looprdReadConnected':bool(self.secrets.get('looprd_read')),
                'looprdIngestConnected':bool(self.secrets.get('looprd_ingest')),
                'looprdPublishConnected':bool(self.secrets.get('looprd_publish')),
                'catalog':catalog, 'git':self.git_status(),
                'assetDrafts':self.asset_drafts(), 'priceDrafts':self.price_drafts(),
                'diagnosticEvents':len(self.events.list()['events']),
                'remoteMutationsEnabled':False, 'walletMutationsEnabled':False}

    def _read_repository(self):
        catalog = json.loads((self.root/'tavi.repository.json').read_text(encoding='utf-8'))
        items=[]
        for x in catalog.get('extensions',[]):
            m=x.get('manifest', {})
            items.append({'id':m.get('id'), 'name':m.get('name'), 'version':m.get('version'),
                          'kind':(m.get('classification') or {}).get('type','app'),
                          'publisher':m.get('publisher'),'permissions':m.get('permissions',[]),
                          'dependencies':[p.get('packId') for p in m.get('assetDependencies',[])],
                          'source':x.get('source'), 'status':'catalog_candidate'})
        return items

    def asset_drafts(self):
        return list(self._read_json('assets.json', {}).values())

    def import_tavia(self, payload):
        meta = inspect_tavia(payload, self.assets_root)
        file_name = meta['sha256'] + '.tavia'
        with self.lock:
            saved = self._read_json('assets.json', {})
            self.private.mkdir(mode=0o700, parents=True, exist_ok=True)
            folder = self.private/'asset-drafts'
            folder.mkdir(mode=0o700, parents=True, exist_ok=True)
            target = folder/file_name
            if not target.exists():
                with target.open('xb') as writer: writer.write(payload)
                os.chmod(target, 0o600)
            saved[meta['sha256']] = meta
            self._write_json('assets.json', saved)
        return meta

    def price_drafts(self):
        return list(self._read_json('prices.json', {}).values())

    def set_price_draft(self, data):
        if not isinstance(data, dict) or 'kind' not in data:
            raise ValueError('Price draft requires a supported kind')
        kind = data['kind']
        if kind not in ('asset-pack','asset-object','game','store-listing'):
            raise ValueError('Unsupported price draft type')
        required={'kind','id','version','priceGold'}
        if kind=='asset-object':required.add('packId')
        if set(data)!=required:
            raise ValueError('Price draft fields do not match its type')
        item_id, version, price = (data[k] for k in ('id','version','priceGold'))
        if (not isinstance(item_id,str) or not PACK_ID.fullmatch(item_id) or
                not isinstance(version,str) or not VERSION.fullmatch(version)):
            raise ValueError('Invalid draft identity or version')
        pack = data.get('packId')
        if kind=='asset-object' and (not isinstance(pack,str) or not PACK_ID.fullmatch(pack)):
            raise ValueError('Asset object value must be scoped to an exact pack')
        if isinstance(price,bool) or not isinstance(price,int) or not 0<=price<=MAX_PRICE:
            raise ValueError('Price must be an integer from 0 to 1,000,000 Gold')
        row={'kind':kind,'id':item_id,'version':version,'priceGold':price,
             'state':'local_proposal_only', 'walletAuthority':False}
        if pack:row['packId']=pack
        with self.lock:
            drafts = self._read_json('prices.json', {})
            drafts['|'.join((kind,pack or '',item_id,version))] = row
            self._write_json('prices.json', drafts)
        return row

    def connect_github(self, data):
        if not isinstance(data,dict) or set(data) != {'repository','token'}:
            raise ValueError('Expected repository and token')
        repository, token = data['repository'], data['token']
        if not isinstance(repository,str) or not REPO.fullmatch(repository):
            raise ValueError('Expected owner/repository')
        if not isinstance(token,str) or len(token)<16: raise ValueError('GitHub token required')
        user=api_request('https://api.github.com/user',token)
        repo=api_request('https://api.github.com/repos/'+repository,token)
        self.secrets.put('github', token)
        self._settings['githubRepository']=repository
        self._write_json('settings.json',self._settings)
        return {'connected':True,'login':user.get('login'),'repository':repo.get('full_name'),
                'private':repo.get('private'), 'permissions':repo.get('permissions',{}),
                'credentialsPersistent':self.secrets.persistent}

    def github_status(self):
        repository=self._settings.get('githubRepository','TheBigTreeInc/tavix')
        token=self.secrets.get('github')
        if not token: raise ValueError('Connect a GitHub credential first')
        repo=api_request('https://api.github.com/repos/'+repository,token)
        return {'repository':repo.get('full_name'), 'defaultBranch':repo.get('default_branch'),
                'private':repo.get('private'), 'permissions':repo.get('permissions',{}),
                'publishing':'operator_review_required'}

    def connect_looprd(self, data):
        if not isinstance(data,dict) or set(data) != {'catalog','admin','readToken','ingestToken','publishToken'}:
            raise ValueError('Expected catalog/admin URLs and three scope-specific tokens')
        catalog=checked_https(data['catalog'],'/catalog')
        admin=checked_https(data['admin'],'/admin')
        if urlsplit(catalog).netloc != urlsplit(admin).netloc:
            raise ValueError('Catalog and admin must use the same approved LoopRD host')
        for field,kind in [('readToken','looprd_read'),('ingestToken','looprd_ingest'),('publishToken','looprd_publish')]:
            if data[field]: self.secrets.put(kind,data[field])
        self._settings.update({'looprdCatalog':catalog,'looprdAdmin':admin})
        self._write_json('settings.json',self._settings)
        return {'configured':True,'readConnected':bool(self.secrets.get('looprd_read')),
                'ingestConnected':bool(self.secrets.get('looprd_ingest')),
                'publishConnected':bool(self.secrets.get('looprd_publish')),
                'credentialsPersistent':self.secrets.persistent}

    def looprd_read(self, action):
        if action not in ('catalog','inspect','audit'): raise ValueError('Unsupported read-only LoopRD action')
        url = self._settings.get('looprdCatalog' if action=='catalog' else 'looprdAdmin')
        if not url: raise ValueError('Configure LoopRD endpoints first')
        token = self.secrets.get('looprd_read' if action=='catalog' else 'looprd_ingest')
        return api_request(checked_https(url,'/catalog' if action=='catalog' else '/admin'),token,action)

    def _run_assets_operator(self, args, token_name, receipt):
        source_root=require_assets_source(self.assets_root)
        token=self.secrets.get(token_name)
        if not token or len(token)<32:
            raise ValueError('Required scoped LoopRD credential not connected')
        if not isinstance(receipt, dict):
            raise ValueError('Separate operator-approved receipt required')
        with tempfile.TemporaryDirectory(prefix='tavix-receipt-') as directory:
            receipt_path=Path(directory)/'approval.json'
            receipt_path.write_text(json.dumps(receipt),encoding='utf-8')
            os.chmod(receipt_path,0o600)
            env={k:v for k,v in os.environ.items() if not k.startswith('LOOPRD_')}
            env['LOOPRD_ASSETS_INGEST_TOKEN' if token_name=='looprd_ingest' else 'LOOPRD_ASSETS_PUBLISH_TOKEN']=token
            result=subprocess.run([sys.executable,*args,'--approval-receipt',str(receipt_path),'--execute'],
                                  cwd=str(source_root),env=env,text=True,capture_output=True,timeout=120)
            if result.returncode:
                # Never relay subprocess stdout/stderr: remote may reflect sensitive material.
                raise ValueError('Canonical Tavi Assets operator action was rejected; check local server logs and approvals')
            try:
                return safe_json(json.loads(result.stdout))
            except json.JSONDecodeError as exc:
                raise ValueError('Unexpected canonical operator response') from exc

    def stage_tavia(self, payload):
        if not isinstance(payload,dict) or set(payload)!={'sha256','receipt'}:
            raise ValueError('Stage requires exact sha256 and separate receipt')
        digest=payload['sha256']; receipt=payload['receipt']
        if not isinstance(digest,str) or not re.fullmatch(r'[0-9a-f]{64}',digest):
            raise ValueError('Invalid archive digest')
        if not isinstance(receipt,dict) or set(receipt)!={'action','approvedSha256','endpoint'}:
            raise ValueError('Stage receipt must bind action, SHA-256 and endpoint')
        url=self._settings.get('looprdAdmin')
        if not url or receipt!={'action':'stage','approvedSha256':digest,'endpoint':url}:
            raise ValueError('Stage approval must match exact archive digest and configured endpoint')
        if digest not in self._read_json('assets.json',{}):
            raise ValueError('Import and validate this TAVIA file first')
        archive=self.private/'asset-drafts'/(digest+'.tavia')
        if not archive.is_file() or hashlib.sha256(archive.read_bytes()).hexdigest()!=digest:
            raise ValueError('Local draft integrity mismatch')
        args=[str(require_assets_source(self.assets_root)/'tools/ziprunner-tavia-postrun.py'),str(archive)]
        return self._run_assets_operator(args,'looprd_ingest',receipt)

    def transition_tavia(self,payload):
        if not isinstance(payload,dict) or set(payload)!={'action','packId','version','manifestSha256','receipt'}:
            raise ValueError('Transition requires exact action, pack, version, manifest digest and receipt')
        action, pack, version, digest= (payload[k] for k in ('action','packId','version','manifestSha256'))
        if action not in ('publish','revoke') or not isinstance(pack,str) or not PACK_ID.fullmatch(pack) or not isinstance(version,str) or not VERSION.fullmatch(version):
            raise ValueError('Unsupported transition or malformed pack identity')
        if not isinstance(digest,str) or not re.fullmatch(r'[0-9a-f]{64}',digest):
            raise ValueError('Expected exact manifest SHA-256')
        endpoint=self._settings.get('looprdAdmin')
        receipt=payload['receipt']
        if not endpoint or not isinstance(receipt,dict) or receipt != {'action':action,'packId':pack,'version':version,'manifestSha256':digest,'endpoint':endpoint}:
            raise ValueError('Independent exact-manifest operator approval is required')
        args=[str(require_assets_source(self.assets_root)/'tools/looprd-registry.py'), action,
              '--url',endpoint,'--pack-id',pack,'--version',version]
        return self._run_assets_operator(args,'looprd_publish',receipt)
