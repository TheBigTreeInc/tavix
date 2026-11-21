"""Local-only TaviX extension preview. No production Tavi SDK impersonation."""
import argparse
import secrets
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from tools.local_client.manager import Management
from tools.local_client.manager_assets import AssetImportError
from tools.local_client import local_packages
from tools.tavix_classification import resolve_classification
from tools.tavix_asset_dependencies import validate_asset_dependencies
from tools.tavix_registry_admin import validate_registry_admin_request
from tools.tavix_local_file_import import validate_local_file_import
from urllib.parse import unquote, parse_qs

import json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
STORAGE = ROOT / ".tavix-local"


def discover(root=ROOT):
    found = []
    for path in sorted((root / "extensions").glob("*/*/manifest.json")):
        try:
            m = json.loads(path.read_text(encoding="utf-8"))
            panel = m.get("entrypoints", {}).get("panel")
            if not isinstance(panel, str) or not panel or panel.startswith("/") or "\\" in panel:
                continue
            base = path.parent.resolve()
            entry = (base / panel).resolve()
            if not entry.is_relative_to(base) or not entry.is_file():
                continue
            found.append({"id": m["id"], "version": m["version"], "name": m.get("name", m["id"]), "classification": resolve_classification(m), "assetDependencies": validate_asset_dependencies(m), "registryAdminRequested": validate_registry_admin_request(m), "fileImports": validate_local_file_import(m), "panel": "/" + entry.relative_to(root.resolve()).as_posix(), "permissions": m.get("permissions", [])})
        except (ValueError, KeyError, OSError, TypeError):
            continue
    return found


class Handler(SimpleHTTPRequestHandler):
    manager = None
    csrf_token = None

    def safe_request(self):
        port=self.server.server_port
        host=self.headers.get('Host','')
        origin=self.headers.get('Origin','')
        if host not in (f'127.0.0.1:{port}', f'localhost:{port}'):
            return False
        if origin != f'http://{host}' or self.headers.get('X-TaviX-Local-CSRF') != self.csrf_token:
            return False
        return True

    def send_json(self, status, obj):
        data = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def body(self, max_length):
        value=self.headers.get('Content-Length','')
        if not value.isdecimal(): raise ValueError('Content length required')
        size=int(value)
        if size <= 0 or size > max_length: raise ValueError('Request exceeds permitted size')
        data=self.rfile.read(size)
        if len(data) != size: raise ValueError('Incomplete request body')
        return data

    def event(self, level, action, code, message, details=None):
        """Only operator API events, never payloads, tokens or arbitrary filenames."""
        try:
            return self.manager.events.record(level, action, code, message, details)
        except (OSError, ValueError):
            return None  # Diagnostics must never make an otherwise safe API fail.

    def issue(self, status, action, exc, details=None):
        if isinstance(exc, AssetImportError):
            code, message = exc.code, exc.public_message
        elif isinstance(exc, (ValueError, KeyError, TypeError, json.JSONDecodeError)):
            code = 'REQUEST_INVALID'
            # Existing API exceptions have fixed, developer-controlled messages.
            # A diagnostic store never captures request bodies or raw credential values.
            message = str(exc)[:220]
        else:
            code = 'SERVICE_UNAVAILABLE'
            message = 'Local management service unavailable; inspect the configured checkout and permissions'
        event = self.event('error', action, code, message, details)
        return self.send_json(status, {'error':message, 'errorCode':code,
                                       'eventId':event['id'] if event else None})

    def do_POST(self):
        path=urlparse(self.path).path
        action={
            '/__local_client/install':'package.install',
            '/__manager/v1/assets/import':'assets.import',
            '/__manager/v1/prices':'storefront.price_draft',
            '/__manager/v1/github/connect':'github.connect',
            '/__manager/v1/looprd/connect':'looprd.connect',
            '/__manager/v1/looprd/stage':'looprd.stage',
            '/__manager/v1/looprd/transition':'looprd.transition',
            '/__manager/v1/events/client':'ui.diagnostic',
        }.get(path,'http.unknown')
        if not self.safe_request():
            return self.issue(403,action,ValueError('Local operator origin and CSRF approval required'))
        details={'requestMethod':'POST'}
        if path == '/__manager/v1/assets/import':
            try:
                details['sizeBytes'] = int(self.headers.get('Content-Length','-1'))
            except ValueError:
                pass
            details['format']='tavia'
        if path == '/__local_client/install': details['format']='tavix'
        try:
            if path == '/__local_client/install':
                result = local_packages.install(self.body(local_packages.MAX_ARCHIVE), STORAGE)
                self.event('info',action,'PACKAGE_INSTALLED','Local TaviX package validated and installed',
                           {'format':'tavix','packId':result.get('id',''),'version':result.get('version','')})
                return self.send_json(201, result)
            if path == '/__manager/v1/assets/import':
                result=self.manager.import_tavia(self.body(32*1024*1024))
                self.event('info',action,'TAVIA_DRAFT_VALIDATED','TAVIA validated and saved as a local draft',
                           {'format':'tavia','sizeBytes':details.get('sizeBytes',0),
                            'packId':result['id'],'version':result['version'],
                            'resourceCount':len(result.get('resources',[])),
                            'objectCount':len(result.get('objects',[]))})
                return self.send_json(201, result)
            if path.startswith('/__manager/v1/'):
                if self.headers.get('Content-Type','').split(';')[0] != 'application/json':
                    raise ValueError('JSON content type required')
                payload=json.loads(self.body(16*1024).decode('utf-8'))
                if path == '/__manager/v1/events/client':
                    # Only known UI error kinds may reach disk; no untrusted messages.
                    fixed={'UI_UNCAUGHT_ERROR':'Browser UI encountered an uncaught error',
                           'UI_UNHANDLED_REJECTION':'Browser UI operation rejected unexpectedly',
                           'UI_NETWORK_ERROR':'Browser could not reach a management endpoint'}
                    if not isinstance(payload,dict) or set(payload) != {'code'} or payload['code'] not in fixed:
                        raise ValueError('Unsupported browser diagnostic code')
                    event=self.event('error','ui.diagnostic',payload['code'],fixed[payload['code']])
                    return self.send_json(201, {'recorded':bool(event),'eventId':event['id'] if event else None})
                if path == '/__manager/v1/looprd/stage':
                    result=self.manager.stage_tavia(payload)
                elif path == '/__manager/v1/looprd/transition':
                    result=self.manager.transition_tavia(payload)
                elif path == '/__manager/v1/prices':
                    result=self.manager.set_price_draft(payload)
                elif path == '/__manager/v1/github/connect':
                    result=self.manager.connect_github(payload)
                elif path == '/__manager/v1/looprd/connect':
                    result=self.manager.connect_looprd(payload)
                else:
                    return self.send_error(404)
                self.event('info',action,'OPERATION_ACCEPTED','Operator action completed',
                           {'requestMethod':'POST'})
                return self.send_json(201 if path == '/__manager/v1/prices' else 200,result)
            return self.send_error(404)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError, __import__('zipfile').BadZipFile) as exc:
            return self.issue(400,action,exc,details)
        except (OSError, TimeoutError, __import__('subprocess').TimeoutExpired) as exc:
            return self.issue(503,action,exc,details)

    def do_DELETE(self):
        if not self.safe_request():
            return self.issue(403,'package.remove',ValueError('Local operator origin and CSRF approval required'))
        if not self.path.startswith('/__local_client/install/'): return self.send_error(404)
        parts = self.path.split('/')
        if len(parts) != 5: return self.send_error(404)
        try:
            local_packages.remove(STORAGE, unquote(parts[3]), unquote(parts[4]))
            self.event('info','package.remove','PACKAGE_REMOVED','Local TaviX package removed')
            self.send_json(200, {'removed': True})
        except (ValueError, OSError) as exc:
            self.issue(400,'package.remove',exc)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path=urlparse(self.path).path
        if path.startswith('/__manager/v1/'):
            if self.headers.get('Host','') not in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'):
                return self.send_json(403, {'error':'Loopback host required'})
            try:
                if path == '/__manager/v1/events':
                    raw=parse_qs(urlparse(self.path).query,keep_blank_values=True)
                    if set(raw)-{'level'} or len(raw.get('level',['all']))!=1:
                        raise ValueError('Unsupported event filter')
                    return self.send_json(200,self.manager.events.list(level=raw.get('level',['all'])[0]))
                if path == '/__manager/v1/bootstrap':
                    state=self.manager.bootstrap()
                    state['csrf']=self.csrf_token
                    return self.send_json(200,state)
                if path == '/__manager/v1/github':
                    return self.send_json(200,self.manager.github_status())
                if path.startswith('/__manager/v1/looprd/'):
                    action=path.split('/')[-1]
                    return self.send_json(200,self.manager.looprd_read(action))
                return self.send_error(404)
            except (ValueError, KeyError, TypeError) as exc:
                return self.issue(400,'manager.read',exc)
            except (OSError, TimeoutError):
                return self.issue(503,'manager.read',OSError('unavailable'))
        if urlparse(self.path).path == "/__local_client/apps":
            payload = json.dumps(discover()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if urlparse(self.path).path == "/__local_client/installed":
            return self.send_json(200, local_packages.installed(STORAGE))
        if urlparse(self.path).path.startswith("/__local_packages/"):
            rel = unquote(urlparse(self.path).path[len("/__local_packages/"):])
            target = (STORAGE / rel).resolve()
            if not target.is_relative_to(STORAGE.resolve()) or not target.is_file(): return self.send_error(404)
            import mimetypes
            data = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(str(target))[0] or "application/octet-stream")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--assets-root", type=Path, default=None, help="Canonical Tavi Assets source checkout for .tavia validation")
    parser.add_argument("--private-root", type=Path, default=None, help="Operator data directory outside this repository")
    args = parser.parse_args()
    Handler.manager = Management(ROOT, assets_root=args.assets_root, private_root=args.private_root)
    Handler.manager.events.record('info','manager.start','MANAGER_STARTED','Local TaviX management server started')
    if Handler.manager.assets_root is None:
        Handler.manager.events.record('warning','assets.config','TAVIA_SOURCE_MISSING',
                                      'Tavi Assets checkout not connected; use --assets-root for TAVIA imports')
    Handler.csrf_token = secrets.token_urlsafe(32)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"TaviX Local Client: http://127.0.0.1:{server.server_port}/tools/local-client/index.html", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
