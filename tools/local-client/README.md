# TaviX local Management Suite — 0.1.26

Run from the TaviX source checkout:

```powershell
python tools/local-client/server.py --assets-root C:\Users\dorbi\source\tavi-assets
```

Open **http://127.0.0.1:8765/tools/local-client/index.html**. If Tavi Assets is checked out alongside TaviX, `--assets-root` is optional; otherwise provide it explicitly. This remains a loopback development server, **not** the native Tavi host SDK.

The new UI includes **Overview**, **Games & apps**, **Assets & objects**, **Storefront**, **Connections**, **Operations**, and **Events**. The former local `.tavix` upload, validation, install/remove, repository preview, account visual marker and sandboxed panel are preserved. The console also validates `.tavia` drafts with the canonical Tavi Assets source checker, inspects resources/objects/collections, stores local Gold-value proposals and shows Git status.

GitHub fine-grained PATs can be verified and saved but **no Git push or storefront publication** is exposed in this pass. LoopRD uses separate read/ingest/publish scoped tokens and approved HTTPS DAPI endpoints; read operations run only on operator request. A stage upload requires an exact archive approval receipt. A publish/revoke needs a *different* exact manifest receipt, privileged server approval and explicit operator confirmation. Nothing auto-applies on import. The application cannot assign itself `ecosystemAdmin`, install unentitled packs or charge a Wallet.

Credentials are DPAPI-encrypted per Windows user outside source or stored with an available secure OS keyring; otherwise they are in memory only. Drafts and nonsecret endpoints are saved to `~/.tavix-suite/`, never version-controlled or distributed. Previewed extensions cannot obtain these credentials via `tavi.extension/v1`. The server uses same-origin and CSRF checks on all mutations; run it only on a trusted PC. Existing local preview is not a hardened untrusted-code sandbox, and remote releases must pass normal Tavi/ZipRunner review.

Full contract, boundaries, manual acceptance and negative cases: [`../../docs/TAVIX_MANAGEMENT_SUITE_025.adoc`](../../docs/TAVIX_MANAGEMENT_SUITE_025.adoc). API description: [`../../openapi.yaml`](management-openapi.yaml).

Tests: `python -m unittest discover -s tests -p test_manager_suite_025.py -v` and the full TaviX repository suite. Tests that use the real Assets source need the optional `TAVI_ASSETS_ROOT` environment variable and do **not** perform any LoopRD network writes.

Events: after a failed `.tavia` import the UI opens **Events**, displaying the canonical validation reason when available and a shareable error ID. Events are saved across restarts in `~/.tavix-suite/events.jsonl`, bounded and redacted; Copy and Export JSON support troubleshooting. See [`../../docs/TAVIX_MANAGEMENT_EVENTS_026.adoc`](../../docs/TAVIX_MANAGEMENT_EVENTS_026.adoc).

## Unsupported `.tavia` resources (0.1.27)

Tavi Assets accepts only data-only `.svg`, `.png`, `.webp`, `.jpg`, `.jpeg`, `.ogg`, `.wav`, `.mp3`, and `.json` resource files, plus root `manifest.json`. Rejected `.md`, `.txt`, `.js`, `.css` or other archive members are **not** harmlessly ignored. The management console records the first safe relative unsupported archive member and the rejected suffix/count after canonical validation. Edit and rebuild the source pack with `python tools/tavia.py build <source-folder> <new-file.tavia>` from your Tavi Assets checkout. If the input is an application, install the `.tavix` in Games & apps instead. No automatic deletion, conversion, installation or entitlement grant is performed.
