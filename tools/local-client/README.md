# TaviX Local Client — initial preview

Run from the TaviX repository checkout on Windows with Python 3.10+:

```powershell
python tools/local-client/server.py
```

Open `http://127.0.0.1:8765/tools/local-client/index.html` in a browser. The server binds only to loopback. It reads local, unpacked extension manifests, validates panel paths stay inside their version directories, and launches those panels. It does not modify the repository index, publish, install into Tavi, or change approval gates.

**Scope / limitations:** This is a browser-based local preview, not yet a native WebView2 client. It does not emulate Tavi's real SDK, accounts, permissions, network identity, install/update, or multiplayer. The account selector is explicitly a visual marker, not an identity simulator. The iframe is not a security boundary for untrusted extensions: run only reviewed packages. Extension network requests may still reach external services. A future host bridge must be implemented against a verified Tavi contract rather than guessed.

Tests: `python -m unittest discover -s tests -v` and `python tools/repository.py check --repository .`.

### Local `.tavix` installation

Use the file picker and **Install local .tavix**. The server accepts raw archive bytes (up to 32 MiB), validates the `tavix.package/v1` lock and file SHA-256 values, checks manifest identity and entrypoint, and stages files into `.tavix-local/<id>/<version>`. The UI supports local preview and removal. Existing versions cannot be silently overwritten. This is local developer tooling, not a production installer or trusted execution sandbox.
