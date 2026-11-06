"""Local-only TaviX extension preview. No production Tavi SDK impersonation."""
import argparse
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
from tools.local_client import local_packages
from urllib.parse import unquote

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
            found.append({"id": m["id"], "version": m["version"], "name": m.get("name", m["id"]), "panel": "/" + entry.relative_to(root.resolve()).as_posix(), "permissions": m.get("permissions", [])})
        except (ValueError, KeyError, OSError, TypeError):
            continue
    return found


class Handler(SimpleHTTPRequestHandler):
    def send_json(self, status, obj):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/__local_client/install": return self.send_error(404)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > local_packages.MAX_ARCHIVE: raise ValueError("Invalid upload size")
            result = local_packages.install(self.rfile.read(size), STORAGE)
            self.send_json(201, result)
        except (ValueError, OSError, __import__("zipfile").BadZipFile, KeyError) as exc:
            self.send_json(400, {"error": str(exc)})

    def do_DELETE(self):
        if not self.path.startswith("/__local_client/install/"): return self.send_error(404)
        parts = self.path.split("/")
        if len(parts) != 5: return self.send_error(404)
        try:
            local_packages.remove(STORAGE, unquote(parts[3]), unquote(parts[4]))
            self.send_json(200, {"removed": True})
        except (ValueError, OSError) as exc:
            self.send_json(400, {"error": str(exc)})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
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
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"TaviX Local Client: http://127.0.0.1:{server.server_port}/tools/local-client/index.html", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
