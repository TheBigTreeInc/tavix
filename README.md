> **Studio candidate 0.1.57:** Publishing now has four compact task-focused tabs (Catalog, Connections, GitHub releases and Tavi Assets / LoopRD). Navigation preserves unsaved local catalog drafts. See `docs/QA_0.1.57.adoc`. Native Windows QA and operator acceptance pending.

> **TaviX Studio 0.1.49 UX candidate:** The page title, notification history and Refresh now share a compact top row; importing starts with the trusted native file picker and then offers a blueprint or Custom/unmapped state in a modal. Review screens start with the queue, not permanent banners or large import cards. No publisher or entitlement permission changes. See `docs/QA_0.1.49.adoc`.

> **TaviX Studio 0.1.48 Windows QA repair:** Blueprint tests now isolate both `HOME` and `LOCALAPPDATA` and their Python subprocesses. This corrects two `BLUEPRINT_ALREADY_IMPORTED` test errors from the Windows full-checkout run without touching the real operator blueprint library, relaxing duplicate protection, or changing publisher permissions. See `docs/QA_0.1.48.adoc`.

> **TaviX Studio 0.1.47:** Asset blueprints are now a searchable source-labelled library with safe local JSON imports, and Connections can explicitly check saved publishing destination HTTPS reachability without credentials. Remote publishing and authenticated service connections are **still not implemented**. See `docs/TAVIX_STUDIO_BLUEPRINT_SOURCES_047.adoc` and `docs/QA_0.1.47.adoc`.

## TaviX Studio 0.1.46 — Unicode review and Tarot metadata diagnostics

The native Studio reviewer now emits ASCII-safe JSON on its Python-to-Rust stdout boundary, preventing Windows code-page encoding of Unicode pack titles from becoming `STUDIO_VALIDATOR_PROTOCOL`. The canonical Tavi Assets `invalid attribute key` rejection is exposed as a fixed safe diagnostic without bypassing validation or auto-approving a pack. The separately repaired Obsidian Tarot v0.1.2 corrects invalid camelCase metadata keys; Studio does not alter imported packages. See `docs/QA_0.1.46.adoc`. The 0.1.45 game/version picker and 0.1.44 asset grid are retained.

## TaviX Studio 0.1.45 — choose game, then version

In **Games & apps**, Studio now groups source candidates by package ID, presents one searchable list entry per game/app, and lets the operator select the exact available version in the adjacent details pane. This is a read-only source inventory and does not change installation, review or publication. See `docs/QA_0.1.45.adoc`. Cross-project intent for verified per-device `.tavia` distribution and shared Tavi asset caching is recorded in `docs/TAVIA_CLIENT_ASSET_DELIVERY_045.adoc` as target architecture, not a deployed feature.

> **TaviX Studio 0.1.44 visual asset grid:** In native package inspection, Grid/List toggles between a responsive thumbnail grid and the previous detailed list. Only currently paged items request original SHA-bound verified artwork with three concurrent native preview calls; invalid images become placeholders. Review and publication gates remain unchanged. See `docs/QA_0.1.44.adoc`.

> **TaviX Studio 0.1.43 operator review UX:** A successful native 0.1.42 window/asset-preview was observed. The new submission review keeps blueprint selection next to the selected pack, explains Tarot resource-ID mismatch, and provides a compact paginated, digest-verified artwork inspector. Windows post-update exact-candidate verification and local human acceptance remain pending. See `docs/QA_0.1.43.adoc`.

> **TaviX Studio 0.1.42 build-verification repair:** The native builder now resolves the Cargo output relative to the *active* Studio checkout. A stale executable from another source root cannot satisfy a test or produce a verified launch copy. Package browsing, SHA-bound previews, local-only publishing destinations and independent operator approval remain unchanged. See `docs/QA_0.1.43.adoc`.

> **TaviX Studio 0.1.41 pack browsing and publication configuration:** Imported `.tavia` and `.tavix` submissions now have a read-only paginated archive browser (resources, objects, collections, files, optional dependencies), with safe, hash-checked SVG/PNG/JPEG/WebP preview. Windows validator subprocesses use no-window flags. Studio can save intended GitHub owner/repository and LoopRD HTTPS hostname **without credentials**; actual authenticated remote publication and developer preview distribution are still unimplemented and disabled. See `docs/QA_0.1.41.adoc` and `docs/TAVIX_STUDIO_PACK_BROWSER_041.adoc`.

> **TaviX Studio 0.1.40 Windows running-executable repair:** Cargo's normal `target/release/tavix-studio.exe` was locked by an already-running Studio during ZipRunner 0.1.39, despite 204 passing tests and a successful Vite frontend build. Studio now compiles using a dedicated persistent `studio-managed-build` Cargo target and launches an immutable SHA-256-verified per-version copy. The first build needs one additional Cargo dependency compilation/cache; no process shutdown or path deletion is performed. See `docs/QA_0.1.40.adoc`.

> **TaviX Studio 0.1.38 stale-runtime and validator isolation:** The operator's screenshots show a v0.1.36-style Connections placeholder and generic, global "Validator did not return structured data" while the v0.1.37 source contains a native Assets picker and copyable Events report. 0.1.38 visibly displays the compiled UI version, refuses to launch a source-stale EXE using the managed launcher, bundles blueprint descriptions natively, and gives page-scoped safe validator errors. Rebuild the actual Windows executable after source overlay. See `docs/QA_0.1.38.adoc`.

> **TaviX Studio 0.1.36 Windows Rust repair:** Fixes operator-reproduced Rust E0308 in review persistence (`Result<(), &str>` instead of `Result<(), String>`) and unused Path import. The frontend already compiled in operator 0.1.35, native executable and review operation still require actual Windows verification. See `docs/QA_0.1.36.adoc`.

> **TaviX 0.1.34 Windows native Studio TypeScript repair:** Fixes the operator-reproduced PatternFly 6 `Title size="sm"` TS2322 error in the designer checklist by using supported `md`; source regression test added. Full Windows native build and launch still require verification. See `docs/QA_0.1.34.adoc`.

> **TaviX 0.1.33 Windows QA repair:** Corrects 0.1.32 Windows test failures caused by implicit CP1252 decoding of the PatternFly UI text and missing exact release-safety handoff wording. Existing native Studio submit/review/feedback behavior is preserved, publishing disabled. See `docs/QA_0.1.33.adoc`.

> **TaviX 0.1.31 recipe adoption:** ZipRunner 1.2.304.300 does not automatically adopt `project.zr` from an overlay. Review the native build/start fields in its project Configuration panel or import `tavix-studio-0.1.31.zr` into the existing `tavix` project, save, then apply the 0.1.31 ZIP to trigger a real Windows Studio build. Source ingestion alone will not compile or launch Studio. See `docs/QA_0.1.31.adoc`.

> **ZipRunner 0.1.29 repair:** 0.1.28 failed pre-overlay (21 post-update tests > 20). The repaired candidate combines related diagnostics without losing test coverage; native Studio acceptance remains pending. See `docs/QA_0.1.29.adoc`.

## 0.1.28 — PatternFly native desktop shell (source candidate)

TaviX Studio adds a separate **Tauri 2 / Rust** operator desktop application with a **PatternFly 6 / React** layout under `tools/studio-desktop/`. Node is for builds, not a live management server. This first pass is read-only: local packages, Git status, Assets checkout availability and existing event IDs. Import, store mutation, publish and preview remain in the tested Python management console until the native Rust migration passes operator acceptance. See `docs/TAVIX_STUDIO_DESKTOP_028.adoc`; Cargo/Windows native build not yet tested.

## 0.1.27 — TAVIA unsupported-resource diagnostics (source candidate)

Following the reproduced `unsupported TAVIA resource type` failure, the management suite now identifies a safe *archive member* and rejected suffix/count in its existing Events panel, plus guidance for rebuilding a valid data-only pack. The canonical Tavi Assets validator remains the only authority; TaviX does not remove unexpected files, accept new formats, or publish automatically. The actual operator-rejected pack has not been supplied and must be checked independently. See [`docs/TAVIX_TAVIA_RESOURCE_DIAGNOSTICS_027.adoc`](docs/TAVIX_TAVIA_RESOURCE_DIAGNOSTICS_027.adoc).

## 0.1.26 — Local diagnostic Events panel (source candidate)

The local TaviX management console now records **bounded, redacted, persistent** operator events in its private user directory. A failed `.tavia` import reports `errorCode` + `eventId` and shows a safe canonical Tavi Assets validator reason where one is available. Open **Events** to filter, copy a diagnostic report, or export JSON for debugging. It logs no API keys, archive content or full local file paths and is distinct from LoopRD's authoritative audit log. See `docs/TAVIX_MANAGEMENT_EVENTS_026.adoc`. This is not an extension host permission or automatic publication feature.

> New in 0.1.25: the local TaviX preview is a six-section **Management Suite** with canonical TAVIA draft validation, proposed Gold values, GitHub identity, and receipt-gated LoopRD operator actions. Remote Git push/store publishing still requires a separately approved exact-diff workflow. See [`docs/TAVIX_MANAGEMENT_SUITE_025.adoc`](docs/TAVIX_MANAGEMENT_SUITE_025.adoc).

# TaviX — extension tooling, local preview and reviewed distribution

> Previous 0.1.24 candidate: An **unpublished**, read-only ZipRunner Operations TaviX app candidate (`examples/ziprunner-operations-0.1.0`) and a proposed host relay contract; see `docs/TAVIX_ZIPRUNNER_STATUS_024.adoc`. The actual Tavi host has no implemented relay yet, so the viewer correctly reports Connection required.


**Source/tooling version: 0.1.49 · Package standard: `tavix/1.0` · Manifest and host wire: `tavi.extension/v1`**

TaviX provides a reviewed, immutable distribution repository for compiled Tavi extensions, plus Python pack/validate/staging tools and a **standalone loopback development client** for opening `.tavix` panels on a PC without Tavi. It does **not** include the Tavi messenger, a game server, the production Tavi SDK host or trusted publisher signing. The `extensions/` tree contains distributed application builds, not their original authoring source.

## Klondike 0.1.2 — first approved-pack consumer candidate

The staged Klondike 0.1.2 release requests only `assets.read` for the optional, explicit `org.tavi.cards.standard` / `card.back` capability. It vendors the read-only Tavi Assets 0.1.16 consumer SDK and displays verified host media; disabled, missing, unsupported or revoked assets fall back to the bundled card design. No new purchases, pack installation, Wallet, code execution, game-rule modification or publisher permission has been added. The historical approved Klondike 0.1.1 package remains immutable. This is source-staged and requires Windows/Android consent and operator publication acceptance. See `docs/KLONDIKE_ASSET_CONSUMER_0123.adoc`.


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


## Offline Store Editor — private developer example (0.1.17)

`examples/store-editor/` is a packable local **TaviX Store Editor**. Open a user-supplied `.tavix`, verify its archive/lock, edit the Store name/summary/artwork, switch catalog/detail previews at phone/tablet/desktop widths, and export a draft or a bumped-version `.tavix` with regenerated integrity data. This tool neither stages nor publishes packages and cannot set Wallet/Gold prices. Cover art and gallery remain a clearly marked preview concept until Tavi adds a reviewed media metadata contract. See `docs/TAVIX_STORE_EDITOR_001.adoc`.

## Windows test encoding portability repair (0.1.18)

The 0.1.17 ZipRunner build failed on Windows because Store Editor tests read UTF-8 HTML with the system CP1252 default. Source test reads now explicitly use UTF-8 and include a regression guard. The Store Editor package, immutable published extensions, public catalog and host/wallet authority are unchanged. Windows ZipRunner execution and native Store Editor acceptance remain operator gates.

## Klondike Games catalog review candidate (0.1.19)

`extensions/example.org.klondike/0.1.1/` and `tavi.repository.json` now include a technically validated, **operator-unpublished** Games entry based on the exact supplied `klondike-0.1.1-store-artwork.tavix` SHA-256. The existing identity `example.org.klondike` and `publisher=example-org` are preserved to avoid silently replacing sideloaded identities. The `source` metadata points to the TaviX **distribution** repository, not a separately verified authoring repository. `license=NOASSERTION` is not rights confirmation. These issues block authorized public publication until reviewed. Store shows icon/summary; cover and browser screenshots are packaged but require separate Social gallery support. Details: `docs/KLONDIKE_STORE_PUBLICATION_0119.adoc`. No Git push, Pages deploy, native mobile test or release approval is implied.

## 0.1.22 Windows ZipRunner Workboard metadata repair

The 0.1.21 archive was rejected **before any source update or Python build** by ZipRunner 1.2.304.278: `TAVIX-KLONDIKE-DRAFT-ARCHIVE-021 requires non-empty operator_checks (max 20)`. The 0.1.22 overlay contains all 0.1.21 source paths (the migration was never applied) and supplies explicit operator acceptance checks for every Workboard `implemented` and `remaining` item. `tests/test_workboard_operator_checks.py` prevents reintroducing the metadata defect. Existing game assets, catalog entries, stage/archive logic, local config and Git/Pages approval gates are untouched.

## 0.1.21 Klondike test repair (Windows overlay)

The staged 0.1.19 `example.org.klondike` draft is NOT the approved public identity. ZipRunner 0.1.20 uses non-deleting overlays; the old release directory may remain and causes `build_index()` to discover both game identities. In 0.1.21 the first build stage `tools/klondike_legacy_draft_archive.py` validates the old draft's exact immutable SHA-256 and the approved `inc.thebigtree.tavi.klondike` release, then moves **only** the verified obsolete draft to Git-ignored `.tavix-local/archived-staging-drafts/`, preserving all bytes for operator inspection. `--check-only` reports planned changes without moving. Unknown files, publisher mismatches or an occupied backup path cause a hard failure. The published `tavi.repository.json` still contains only Atrium, Companion 0.6.40, and Klondike. No Git commit, push, tag, public publication or device install occurs.

## Local Management Suite (0.1.25)

Launch with `python tools/local-client/server.py --assets-root ../tavi-assets` and open `http://127.0.0.1:8765/tools/local-client/index.html`. TaviX manages `.tavix` local package preview and repository catalog inventory. The canonical Tavi Assets checkout validates imported `.tavia` drafts; LoopRD stages and publishes only through its existing scoped, receipt-gated operator CLI. A local Gold value proposal is not an authoritative offer or wallet transaction. GitHub PAT verification is read-only; pushing source or Pages releases is intentionally not enabled. Secrets are OS-protected on Windows, otherwise keyring-backed or memory-only, never supplied to TaviX extensions. Full details: `docs/TAVIX_MANAGEMENT_SUITE_025.adoc` and `openapi.yaml`.

### Native TaviX Studio on Windows (0.1.30)

The single intended desktop operator application is `tools/studio-desktop/` (PatternFly 6 + Tauri 2/Rust). The Tauri icon resource required on Windows is now included; the source-controlled ZipRunner `build` compiles a native executable and `start` launches it directly. See `tools/studio-desktop/README.md` for manual launch and pending native operator acceptance. The Python local management server is an explicitly temporary compatibility path for capabilities not yet migrated to native Rust. It is not started by native Studio, and no remote publication happens automatically.

## Native Studio review workflow (0.1.32)

`tools/studio-desktop` adds PatternFly submission review of `.tavix` games/apps and `.tavia` packs, with canonical validation, designer blueprint completeness, per-package reviewer notes and feedback/developer-preview/local-approval ZIP exports. The official store publish action is deliberately disabled pending reviewed Git and LoopRD integration. See `docs/TAVIX_STUDIO_REVIEW_032.adoc` and the Studio-local blueprint contract `contracts/tavix-studio-asset-blueprint-v1.schema.json`. Neither Tavi nor Tavi Assets runtime authority is changed by this candidate.

### 0.1.35 Native Studio Windows npm recovery

The managed Studio build skips npm reinstallation on healthy dependencies, incrementally repairs a partially installed node_modules directory after EBUSY, validates required TypeScript/Vite/Tauri commands, and fails closed when incomplete. See `docs/QA_0.1.35.adoc`. No Git or LoopRD publishing changes.

## Native Studio source connections and diagnostics (0.1.37)

The operator confirmed native Studio 0.1.36 launches. Studio 0.1.37 adds operator-selected Tavi Assets source validation, bounded native readiness and copyable, privacy-safe import failure codes. Local source preferences live in the user profile; they never authorize GitHub/LoopRD publishing. See `docs/QA_0.1.37.adoc`.

### Studio import protocol repair 0.1.39

The native Studio preserves specific TAVIA validation errors and returns a single sanitized diagnostic response for unexpected adapter faults. New asset submissions start without an assumed 54-card blueprint. Existing store approval gates and original package bytes are unchanged; see `docs/QA_0.1.39.adoc`.

## 0.1.50 Windows encoding QA repair
Use UTF-8 explicitly when Python tests read repository source or JSON on Windows; see `docs/QA_0.1.50.adoc`. The 0.1.49 Studio UX and private operator profile are unchanged. Build, Git, LoopRD and release approvals remain separate.

## Windows Studio 0.1.52 QA fix

Windows 0.1.50 failed an overbroad encoding regression on 25 pre-existing implicit source reads in seven old tests. Studio 0.1.52 retains strict UTF-8 checks for new/Studio tests, tracks legacy ceilings and documents their separate migration in docs/QA_0.1.52.adoc. Native publish and operator gates are unchanged.

## Studio 0.1.52 — TAVIB and publishing

See `docs/TAVIB_STUDIO_PUBLISHING_052.adoc` for native app-provided `.tavib` imports, immutable local provenance, read-only GitHub release state and operator-confirmed GitHub draft/public distribution steps. The proposed blueprint container is not yet Tavi Assets canonical; LoopRD/official Store publisher integration is not implemented. Source checkout Git pull/push is not invoked by Studio.

## Studio 0.1.53 — publishing readiness and compact Connections

This source overlay moves GitHub/LoopRD status out of oversized Connections cards, reports GitHub gateway **source availability** without asserting authentication, shows independent live/public GitHub release discovery and `gh` login in Publishing, and distinguishes locally approved submissions with external dependencies from store-ready remotely published packages. Unsaved destination edits block remote actions, and receipts remain bound to the selected digest and repository. Existing exact-SHA and operator permission gates remain. See `docs/QA_0.1.53.adoc` and `docs/STUDIO_PUBLISHING_CONNECTIONS_053.adoc`. Windows native 0.1.53 acceptance and disposable GitHub publishing verification remain pending. No Git push or public release.

## Studio 0.1.54 — LoopRD DAPI adapter and embedded TAVIB inspection

Native Publishing now configures separate approved `/admin` and `/catalog` DAPI paths, verifies scoped live read/inspect responses, and provides exact-review/receipt-gated `stage` and `publish` actions for `.tavia`. Credentials must be short-lived, server-issued and injected into the trusted native Studio process; the Tavi/Social ecosystemAdmin delegation broker is not provided by this source. The Blueprint Import from TaviX dialog now offers an Inspect detail panel (exact resources, prefix minima, optional assets, checklist, readme and optional WebP) before import. See `docs/QA_0.1.54.adoc`. Windows native build and live disposable-registry acceptance are pending. No Git push or public release.

## Studio 0.1.57 — catalog release metadata table

Publishing begins with a searchable table of local `.tavix` applications, `.tavia` packs, `.tavib` blueprints and read-only discovered LoopRD versions. Price in Gold (blank=unset, 0=free), Listed, Testing and a short description are operator-local **publication drafts** stored by native Rust under the private profile. These fields are not live catalog mutations: the currently specified Tavi Assets `store-offer/v1` has illustrative `displayGoldPrice`, but official store listing/testing state and authoritative pricing require new, owner-approved LoopRD contracts. All release, service-token and receipt gates remain separate. See `docs/QA_0.1.57.adoc`. No Git push or public release.

## Studio 0.1.58 — blueprints are not store merchandise

`.tavib` schematics describe compatibility between `.tavia` asset packs and `.tavix` applications. They must not be priced, listed, tested as merchandise or granted entitlements. Studio Publishing > Catalog shows only applications (`.tavix`) and installable asset packs (`.tavia`); Asset blueprints and submission review continue to import and validate schematics. Older blueprint-only draft records remain in the private profile for safe migration, but are not exposed in the Publishing table and cannot be saved through the native catalog command. Live Tavi Store contracts still require separate Tavi Assets/LoopRD owner adoption.

## Studio 0.1.60 — GitHub source catalog synchronization (candidate)

Open **Publishing → Catalog → Sync from GitHub** (or Overview → **Sync GitHub catalog**). The new **GitHub catalog sync** tab fetches pinned `TheBigTreeInc/tavi-assets/catalog.source.json` and the generated `catalog.json`, reports revision and differences, and prepares a draft metadata entry for one locally approved `.tavia` asset pack. The native GitHub CLI browser-login button avoids pasting PATs into Studio. A GitHub **draft pull request** can be created only after two confirmations with exact SHA-256 and a fresh Git revision; no public archive upload, public index regeneration, Wallet price, LoopRD publish or automatic release occurs. This initial phase is a source-catalog proposal workflow, not end-to-end Store publication; see `docs/QA_0.1.60.adoc`.
