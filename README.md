# TaviX — extension tooling, local preview and reviewed distribution

**Source/tooling version: 0.1.13 · Package standard: `tavix/1.0` · Manifest and host wire: `tavi.extension/v1`**

TaviX provides a reviewed, immutable distribution repository for compiled Tavi extensions, plus Python pack/validate/staging tools and a **standalone loopback development client** for opening `.tavix` panels on a PC without Tavi. It does **not** include the Tavi messenger, a game server, the production Tavi SDK host or trusted publisher signing. The `extensions/` tree contains distributed application builds, not their original authoring source.

## Developer contracts — start here

**Other projects (Atrium, Companion, Tavi integrations and future games) should read these before changing extension/package code:**

| Source | Purpose |
| --- | --- |
| [`docs/INDEX.adoc`](docs/INDEX.adoc) | Canonical developer-doc directory and stable retrieval URLs |
| [`docs/TAVIX_LOCAL_FILE_IMPORT.adoc`](docs/TAVIX_LOCAL_FILE_IMPORT.adoc) | Native file picker proposal, bounded binary read, cancellation, Windows/Android and detached host boundaries |
| [`contracts/tavix-local-file-import-v1.json`](contracts/tavix-local-file-import-v1.json) | Machine-readable negotiated feature and four methods |
| [`sdk/tavix-sdk.mjs`](sdk/tavix-sdk.mjs) | Reference SDK with `sdk.localFiles` (not native Tavi implementation) |
| [`docs/TAVIX_ASSET_DEPENDENCIES.adoc`](docs/TAVIX_ASSET_DEPENDENCIES.adoc) | Requested asset packs/capabilities, permission grants and host-only authorization boundary |
| [`contracts/tavix-asset-dependencies-v1.schema.json`](contracts/tavix-asset-dependencies-v1.schema.json) | Optional asset dependency manifest field schema |
| [`contracts/tavix-asset-grants-v1.schema.json`](contracts/tavix-asset-grants-v1.schema.json) | Host-only approved grant projection schema; not an extension field |
| [`docs/TAVIX_CLASSIFICATION.adoc`](docs/TAVIX_CLASSIFICATION.adoc) | Game/app categories, legacy fallback, proposed secure Tavi inventory and Atrium launch boundaries |
| [`contracts/tavix-classification-v1.schema.json`](contracts/tavix-classification-v1.schema.json) | JSON Schema for optional `manifest.classification` |
| [`contracts/tavix-installed-games-v1.json`](contracts/tavix-installed-games-v1.json) | Host inventory/open contract: Tavi 0.3.141 has guarded source dispatch; native/operator acceptance remains pending |
| [`docs/TAVIX_CONTRACT.adoc`](docs/TAVIX_CONTRACT.adoc) | Observed TaviX wire protocol, SDK, host negotiation and permissions |
| [`docs/TAVIX_PACKAGE_FORMAT.adoc`](docs/TAVIX_PACKAGE_FORMAT.adoc) | Manifest, lockfile, archive, integrity, catalog and staging rules |
| [`contracts/tavix-1.0.json`](contracts/tavix-1.0.json) | Machine-readable protocol and documentation-discovery snapshot |
| [`docs/DEVELOPER_GUIDE.adoc`](docs/DEVELOPER_GUIDE.adoc) | Build/test/install a small application on Windows or another PC |
| [`examples/hello-tavix/`](examples/hello-tavix/) | Self-contained panel with CSS and JS for local smoke testing |
| [`architecture/c4/README.adoc`](architecture/c4/README.adoc) / [`workspace.dsl`](architecture/c4/workspace.dsl) | TaviX-owned C4 boundaries (source-grounded) |

To retrieve these files from another component **after an operator-approved push**, use GitHub source URLs, for example:

`https://raw.githubusercontent.com/TheBigTreeInc/tavix/main/contracts/tavix-1.0.json`

Replace `main` with a reviewed commit SHA when reproducibility matters. The GitHub Pages public store publishes compiled extension assets and `tavi.repository.json`, **not** this source documentation. No automatic sync between projects is implied. The agent maintenance rules in `AGENTS.md` and repository tests require the contract snapshot and docs to change when implemented SDK/package interfaces change.

## Local PC development client (without Tavi)

From the TaviX checkout:

```powershell
python tools/local-client/server.py
```

Open `http://127.0.0.1:8765/tools/local-client/index.html`. Browse installed repository versions, or choose a `.tavix` file and click **Install local .tavix**. The local client validates the archive and hashes, installs into ignored `.tavix-local/<id>/<version>/`, opens the panel and supports removal; same-version replacement requires explicit removal first. It listens only on `127.0.0.1`.

**Important limitations:** this is an HTTP/browser *developer preview*, not a native WebView2 client or production Tavi runtime. It has no real authenticated Tavi identity, messaging, wallet, game host API, permissions enforcement, multiplayer or rollback. The iframe is not a trusted security sandbox; run reviewed packages only. Successful rendering does not prove a Tavi Windows/Android embedded view will work.

## Build and validate a package

From this checkout:

```powershell
python tools/tavix_package.py validate examples/hello-tavix
python tools/tavix_package.py pack examples/hello-tavix hello-0.1.0.tavix
python tools/tavix_package.py validate-archive hello-0.1.0.tavix
python -m unittest discover -s tests -v
python tools/repository.py check --repository . --strict
```

Remove the temporary output before a ZipRunner source update. A `.tavix` is a ZIP with validated `manifest.json`, versioned assets and a generated `tavix.lock.json` containing SHA-256 file hashes. These hashes do **not** establish publisher authenticity. The current validator does not fully check transitive HTML/CSS/JS references; browser/host verification is still necessary.

## Reviewed producer staging and published App Store

The repository uses `extensions/<application-id>/<version>/` for immutable, compiled artifacts, with a canonical root `tavi.repository.json` index. After a producer's reviewed build (example: Atrium):

```shell
python ../tavix/tools/repository.py stage --repository ../tavix --input dist-tavi --source-url https://github.com/TheBigTreeInc/atrium --license NOASSERTION
```

This stages **one** release and updates the catalog only after verifying immutable assets. Repeating identical bytes is a no-op; changing bytes under an existing version is rejected. It never commits or pushes. The producer source and licensing provenance must be reviewed separately.

The published catalog URL is:

`https://thebigtreeinc.github.io/tavix/tavi.repository.json`

Tavi may add this under **Apps → App Store → Extension repositories** where its UI supports it. Publisher identity, package install/update consent and UI embedding are Tavi's responsibility. Existing installed publisher sources are not silently switched. The root `tavi.repository.json` is a static App Store feed, not a live API or a signed package registry.

## ZipRunner, GitHub and acceptance gates

Import a versioned `tavix-*-ziprunner.zip` into the existing ZipRunner project (`tavix`); preserve the operator-managed configuration, source overlay exclusions and Git profile. Run the unit tests and repository strict check. Review changes and exact-package test evidence before any operator-authorized push. The repository's external `.github/workflows/pages.yml` workflow publishes on relevant **main-branch pushes** and runs tests/catalog validation. A local build, a preview, a previous commit's CI result and source staging are **not** operator acceptance or publication authorization.

## Architecture and provenance

The Structurizr DSL source of truth is `architecture/c4/workspace.dsl`; the AsciiDoc explanation is `architecture/c4/README.adoc`. Tavi, Atrium, Companion, LoopRD, GitHub Pages and ZipRunner are external to TaviX's implementation boundary. TaviX includes historical Atrium and Companion *compiled* releases; these are not a claim to own the upstream engines or their original source.

For historical context, the Windows LF/catalog repairs are documented in `RECONCILIATION_0.1.2.md`, `REPAIR_0.1.6.md` and `REPAIR_0.1.7.md`. `tools/local-client/QA.md` explains the scope of exact-package QA; `docs/COMPANION_POSTBUILD.adoc` describes optional producer staging. Legacy Build and Workboard review states remain independent of this documentation-only update.

## Game/app classification (0.1.10)

New manifests may optionally include `"classification": {"type":"game","categories":["cards","solitaire"]}` while retaining `"kind":"app"` for the existing v1 envelope. The TaviX packager and loopback installer validate the classification, and the local preview shows Game/App labels. Unclassified packages resolve to app/[] in new consumers. Existing staged release bytes stay unchanged. See `docs/TAVIX_CLASSIFICATION.adoc` for complete taxonomy, examples and trust boundaries.

**Compatibility:** Tavi 0.3.124 explicitly rejects unknown manifest fields; it **cannot install newly classified manifests** until Tavi adds classification validation and registry persistence. The `games.installed.list` / `games.installed.open` capabilities are now present in Tavi 0.3.141 source for authorized Atrium sessions, but native/operator acceptance and Atrium consumption remain separate; the TaviX local preview does not implement them. Only a Tavi-authorized Atrium session may see installed game descriptors; it must never read a game's private storage or launch arbitrary URLs. No release is published automatically.

## Asset dependency requests (0.1.11)

An extension may declare optional `assetDependencies` and request `assets.read` and, when applicable, `assets.preferences.write`. The TaviX package validator and repository staging check exact pack IDs, compatibility ranges, capability names and requested permission consistency. This **does not** grant access, install content, purchase assets, or change any existing release. The host alone must approve pack/capability pairs, check verified installed content and LoopRD entitlements, and obtain user consent for customization.

The supplied **Tavi 0.3.141** source has a guarded `tavi.assets/v1` dispatcher, but its strict manifest validator rejects these new fields/permissions, and the runtime has **no connected Assets engine or approved grants**. Tavi Assets 0.1.7 provides reference services/SDK but is not yet production-integrated. Do not publish the new example as host-compatible until Tavi implements and verifies the contract. See `docs/TAVIX_ASSET_DEPENDENCIES.adoc` and `examples/asset-consumer/manifest.json`.

The older 0.3.124 classification incompatibility noted above is historical: Tavi 0.3.141 source accepts game classification, while native/operator acceptance is separate.


## Trusted registry administration contract candidate (0.1.12)

`docs/TAVIX_REGISTRY_ADMIN.adoc`, `contracts/tavix-registry-admin-v1.json`, `contracts/tavix-registry-admin-request-v1.schema.json` and `contracts/tavix-registry-admin-response-v1.schema.json` specify the optional **request-only** `assets.registry.admin/v1` capability for Tavi Asset Studio and future approved applications. `examples/registry-admin-request/manifest.json` is a packable no-op fixture. TaviX does **not** provide host admin grants, LoopRD registry transport, native confirmations or publication; Tavi 0.3.141 does not support this permission. No change to `tavi.assets/v1`, existing pack-scoped asset grants, staged releases, operator approval gates or wallet authority.


## Native local-file import proposal (0.1.13)

`manifest.fileImports` plus `permissions: ["ui.panel", "files.local.import"]` requests a host-mediated native picker with declared `.tavia`/MIME filters and a bounded maximum file size. `tavix.local-file-import/v1` is advertised only by an operational, approved Tavi host. `sdk.localFiles.negotiate()` checks both the feature and the granted permission. `files.local.pick/read/close/cancel` use the existing `tavi.extension/v1` message channel, 128 MiB max file size and 64 KiB max base64 read chunks. A complete reference app is in `examples/local-file-import/`. Tavi 0.3.141 and the TaviX browser preview do not provide the native picker; Windows/Android implementation belongs to Social/Tavi. This request cannot upload or publish `.tavia` packs and does not grant `assets.registry.admin/v1`.

## Integrated UI kit (0.1.14)

Use `docs/TAVIX_UI_KIT_001.adoc` and `contracts/tavix-ui-kit-v1.json` for shared icons, typography, and independent app identity icons. The offline `sdk/ui-kit/` source and `examples/ui-kit/` package demonstrate the actual CSS and SVG assets; they never require host permissions. See `docs/INDEX.adoc` and `docs/DEVELOPER_GUIDE.adoc`.
