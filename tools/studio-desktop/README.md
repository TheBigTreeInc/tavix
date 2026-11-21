## 0.1.49 — compact native review workspace

The header includes the selected page, small Notifications dropdown (status/error and source mismatch), and Refresh in one row. Repeated page text/success banners are no longer always visible. The review queue starts immediately after an `Import package…` button and compact counts. After native `.tavia` file selection and digest-bound local retention, a modal offers a source-labelled blueprint or `Custom / no blueprint yet`; the latter remains unmapped and not store-ready. Existing imported files can change/clear blueprint via `review_recheck`, which resets prior approval, without deleting/reimporting files. Refresh keeps the page mounted. Windows selects are high-contrast. This is strictly local review; Git/LoopRD publishing is unchanged and gated. See `../../docs/QA_0.1.49.adoc`.

## 0.1.48 — Windows local blueprint test profile isolation

Repair tests only: scoped `LOCALAPPDATA` and `HOME` for every blueprint import test and CLI subprocess. No user blueprint deletion, import overwrite, privileged publisher connection or native application behavior change. See `../../docs/QA_0.1.48.adoc`.

## 0.1.47 — traceable blueprints and safe publishing reachability

`Asset blueprints` is a searchable source-labelled library: bundled profiles come from the versioned source checkout, and operator-authored `local-*` JSON profiles can be imported through a native file picker into the private Studio `blueprints/` folder. Custom imports must pass the data-only schema; they cannot overwrite built-ins, bypass canonical .tavia validation or approve publication. A reviewed example is at `../../examples/studio-blueprints/local-card-back-example.json`.

`Connections` can now explicitly probe saved GitHub repository and LoopRD HTTPS destinations **without** credentials or mutations. A responsive server is not an authenticated publisher. Native authorized publication still requires a separate trusted adapter and exact-artifact approvals; legacy Python management remains separate. See `../../docs/TAVIX_STUDIO_BLUEPRINT_SOURCES_047.adoc` and `../../docs/QA_0.1.47.adoc`.

## 0.1.46 — Unicode-safe native review output

Native Python review now escapes Unicode on its JSON wire output for compatibility with Windows ANSI stdout pipes. Trusted canonical `invalid attribute key` rejections are reported, not mistaken for validator transport failures. No approval, entitlement or publisher privileges change. See `../../docs/QA_0.1.46.adoc`.

## 0.1.45 — game-first version selection

The **Games & apps** inventory now displays one searchable, keyboard-accessible game/app entry per source package ID, with the available versions selectable in the adjacent detail pane (newest first). Per-package version choices remain visible when returning to a game. This only reads source metadata; it does not install, preview, approve, or publish applications. See `docs/QA_0.1.45.adoc` and the cross-project `.tavia` delivery intent in `docs/TAVIA_CLIENT_ASSET_DELIVERY_045.adoc`.

## 0.1.44 — visual grid for inspected asset packs

Under Assets & objects and Submission review, package inspection now defaults to a responsive Grid showing bounded native-verified thumbnails where the selected resource/file has an approved image. List switches back to the earlier detailed rows. Clicking a visual tile opens the unchanged original-artwork preview. Only twelve visible records are scanned and no more than three thumbnail requests are in flight; failed/unapproved images have placeholders. No native IPC, canonical validator, publisher connection or approval gate changes. See `docs/QA_0.1.44.adoc`.

## 0.1.43 — review guidance and compact safe package inspector

Native Studio shows a blueprint-selection/recheck control beside the selected asset review, including a warning when the generic Tarot profile requires different IDs. The original package remains unchanged. Package contents are collapsed by default on Submission review; opened content displays 12 rows per page and an adjacent digest-checked artwork inspector, avoiding a nested scrollbar. In Assets & objects the browser remains directly visible. No publisher permissions change. See `docs/QA_0.1.43.adoc`.

## 0.1.43 — native build output bound to active checkout

The builder must resolve `src-tauri/target/studio-managed-build/release/tavix-studio.exe` from the *current* Studio root at build time, and must not rely on a module-level cached path. The preceding 0.1.41 Windows ZipRunner run revealed that a mocked build could succeed using an old unrelated executable. With this change a successful Tauri command without an executable at the expected path fails closed. Native Windows/Cargo validation and operator GUI acceptance are separate checks. The old immutable staged copies are never removed.

## 0.1.41 — archive contents, artwork preview and publishing destinations

Studio's Submission review and Assets & objects screens now inspect the exact retained `.tavia`/`.tavix` ZIP without installing or running it. Use Resource/Objects/Collections/Files/Dependencies tabs, 40-row pagination and View artwork on image entries. Preview checks the declared file SHA-256; SVG drawing nodes/attributes are allowlisted and scripts, external URLs and active markup rejected. Import can succeed for local feedback even when canonical validation blocks approval. Python validator subprocesses run hidden on Windows.

Connections, Operations and Official storefront now show a local-only intended publishing destination form. Provide a GitHub `owner/repo` and/or HTTPS hostname for LoopRD. The values are not credentials or verified remote connections. The official publish action stays disabled until native publisher authentication, exact artifact/diff approvals, LoopRD server permission and receipt handling are implemented. No remote requests or Git writes are performed by this form.

## 0.1.38 — native UI version and offline blueprint catalog

Built UI displays its version. On Windows the managed launcher refuses to run an EXE older than relevant source; close the prior window, build, then launch. The four built-in designer blueprints are Rust-embedded, independent of the Python validator. Python failures remain fail-closed for actual .tavia/.tavix validation and are shown as safe scoped codes in Studio. See `../../docs/QA_0.1.38.adoc`.

# TaviX Studio — native read-only foundation (0.1.28)

A **separate native application shell** inside the TaviX source tree. Tauri 2 supplies a Rust host and the system's WebView; PatternFly 6 / React supplies the operator layout. Node is a **build/development tool only**, not an operational HTTP server or trusted asset host.

This is deliberately a small **source candidate**, NOT a complete replacement for the local Python management suite. Existing TaviX preview and Tavi Assets validator remain unchanged. Studio currently shows a read-only TaviX release inventory, Git status, sibling Assets source availability, and sanitized event IDs. Assets, Storefront, Connections, and Operations are visible *migration placeholders*, with no credentials or privileged writes.

A separately distributed Studio executable needs a trusted checkout. Set `TAVIX_REPO_ROOT` to its path, or launch from inside a TaviX checkout; the renderer cannot choose an arbitrary path. A native repository picker is pending.

## Development (Windows)

Prerequisites: Node.js, npm, Rust toolchain, MSVC build tools and WebView2 (as required by Tauri 2). From the current Git checkout:

```powershell
cd tools/studio-desktop
npm install
npm run tauri dev
```

A reproducible `package-lock.json`, native CI build and signed installer are not included in this first candidate. Pin dependencies and generate a reviewed lockfile on a connected build machine before release. This environment lacked Cargo, so no native compile or Windows acceptance is claimed.

## Security and migration

* No browser-facing operator HTTP endpoint is started by the desktop shell; normal application calls use Tauri's IPC commands.
* Rust exposes only `workspace_snapshot` and `recent_events`, with **no user-supplied paths or commands**; package files are inspected read-only with caps on size and count, and no symlink traversal.
* The native events method shows only whitelisted event IDs, codes, levels and timestamps. It does not expose free-text error messages or secret values.
* No Tauri shell, fs, HTTP, SQL or dialog plugin is installed or granted. The capability file allows core application access only.
* **Do not load `.tavix` extensions into the privileged Studio WebView.** A future preview must be separated into its own origin/window/process with no operator IPC capability, and pass explicit sandbox tests before it can replace the existing local preview.
* No GitHub/LoopRD token storage, network requests, publish/ingest, Gold/Wallet, local installer, or operator receipt generation is introduced. The existing Python console remains the functional compatibility path.

## Native operator acceptance gates

1. Build from a reviewed lockfile on Windows, run the app, and observe the same release count and Git state as the command-line tools.
2. Verify no HTTP listener is opened by Studio and no credential or filesystem access is available from the frontend beyond the two named Rust commands.
3. Confirm the Events view contains only sanitized IDs/codes and never free-text messages, secrets or full local paths.
4. Confirm a malicious `.tavix` is never loaded in the privileged native operator origin.
5. Preserve the existing localhost console's `.tavix` installation, `.tavia` validation and receipt-based LoopRD operations; do not mark those migrated until parity acceptance succeeds.

See `docs/TAVIX_STUDIO_DESKTOP_028.adoc` for the rollout and architecture decision.

## Windows startup repair (0.1.30)

The native Studio is the **single intended operator application**. Tavi remains
an end-user client. The old Python management browser is an **unmigrated
compatibility adapter**, not a second desktop app or a service required by this
shell. Neither Tavi nor an installed `.tavix` is an administrator by default.

0.1.28/0.1.29 could not compile on Windows because Tauri required
`src-tauri/icons/icon.ico`, which was absent from the source archive. Version
0.1.30 contains reviewed source icon resources, verified ICO directory entries,
and the following managed commands in `project.zr`:

* `python tools/studio-desktop/build_windows.py` — on Windows: npm dependency
  installation, frontend compilation, Tauri release executable build with
  `--no-bundle`, and executable presence/PE-header check. Does **not** execute
  untrusted packages or publish artifacts. Its stdout/stderr are the native
  build evidence; a non-Windows run explicitly skips this stage.
* `python tools/studio-desktop/run_windows.py` — start the built native
  `src-tauri/target/release/tavix-studio.exe` as a managed process. Sets only
  the trusted checkout location and never launches localhost:8765.

The ZipRunner start command runs after build success, under the existing
operator approval controls. To use Studio directly without ZipRunner, double
click `tools/studio-desktop/launch-windows.cmd` from Explorer or run:

```powershell
cd C:\Users\dorbi\source\tavix
python tools/studio-desktop/build_windows.py
python tools/studio-desktop/run_windows.py
```

`npm install` only runs when building. **The package-lock.json is not included
in this 0.1.30 source candidate:** this authoring environment cannot resolve
npm registry metadata. Any lock generated on the Windows operator workstation
must be reviewed and checked in during a subsequent version before labeling a
native binary reproducible or approving a signed installer. No native Windows
build was performed in the authoring environment. The binary stays under
ZipRunner-protected `src-tauri/target/` and is not shipped in source archives.

If the native build fails, the launcher returns a failure; it must not start
the older Python browser manager as a silent substitute. The existing server
remains manually available for the `.tavia` and remote approval workflows that
are **not yet available** in Studio's native Rust command set.

## Submission review and designer blueprints (0.1.32)

Studio now has a native Submission review queue for `.tavix` and `.tavia` files, designer blueprints with AsciiDoc checklists, local reviewer notes and feedback, developer preview, and locally approved handoff ZIPs. The picker runs inside Rust using `rfd`; no browser-origin file path reaches native commands. `review_cli.py` runs canonical TaviX/Assets validators via a fixed, trusted local source checkout and generates the outer ZIP. Package bytes are not modified or executed. Private copies and review state are retained under the OS user profile, not in Git.

**Official storefront publishing is NOT yet connected**: a Studio review approval is only a local operator decision and can be exported for independently authorized Git/LoopRD review. The old Python console remains a compatibility option; Studio does not run it as a hidden server. For exact security and acceptance, see `docs/TAVIX_STUDIO_REVIEW_032.adoc`.

== Windows dependency recovery (0.1.35)

The managed builder first checks for npm TypeScript/Vite/Tauri script shims and
runs an offline `npm ls --depth=0` health check. If healthy, it skips npm
installation. If a previous `npm ci` failed (e.g. Windows `EBUSY`) and left
`node_modules` incomplete, it uses incremental `npm install` rather than
re-running a destructive `npm ci` over populated files. A completely empty
installation still uses `npm ci` if a local lockfile exists. It never removes
operator-owned files, kills processes or modifies credentials.

If Windows reports `EBUSY` during recovery, close any Studio/Vite/Node sessions
and IDEs that hold files under this source tree, allow file locks to release,
then rerun `python tools/studio-desktop/build_windows.py`. A missing `tsc.cmd`
means the frontend dependencies remain incomplete; do not treat a Rust build as
successful. Verify `npm run build` before launching the Tauri executable.

== Windows Rust review-record fix (0.1.36)

After successful TypeScript/Vite and Cargo dependency compilation, 0.1.35 failed with Rust E0308 in `review.rs:81`. This source fixes the owned error type and removes an unused `Path` import. Run `python tools/studio-desktop/build_windows.py` and `python tools/studio-desktop/run_windows.py` for actual Windows verification. Source tests alone are not native acceptance. See `docs/QA_0.1.36.adoc`.

## Local source connection and diagnostics (0.1.37)

Use **Connections** to select the local `tavi-assets` source checkout or reset to environment/sibling auto-detection. The selected path stays in the private operator profile. **Events** includes a copyable, bounded, sanitized report of validator readiness and import issue codes; no secrets, full paths, reviewer notes or package bytes. GitHub/LoopRD native connections and official publication remain pending. See `docs/QA_0.1.37.adoc`.

## 0.1.39: import diagnostics

The native review CLI keeps one sanitized JSON response even when a trusted validator raises unexpectedly, and retains specific canonical adapter failure codes. New submissions start without a designer blueprint; choose one once the package type is known. Connections readiness confirms that the canonical module loads, not that every candidate archive passes. Use Events → Copy diagnostic report after inspecting any rejected package. Official publishing remains disabled.

## 0.1.40 managed Windows build and launch

Use `python tools/studio-desktop/build_windows.py` from the repository root. It uses `CARGO_TARGET_DIR=tools/studio-desktop/src-tauri/target/studio-managed-build` rather than Cargo's legacy `target/release` executable (which may still be running), then stages a SHA-256-verified immutable copy in `target/studio-launch/<version>/<digest-prefix>/tavix-studio.exe` and atomically writes `target/studio-launch/current.json`. The launcher executes only that verified copy. Both directories are local generated runtime/build state and must not be included in Git or ZipRunner source updates. The first isolated Cargo build may recompile dependencies and consume additional disk. No previous Studio process is stopped, no old executables are deleted and no official-store or remote action is authorized.

Acceptance requires a real Windows Cargo build, visible v0.1.40 header, managed launch from a staged path and a second successful rebuild while that Studio process is still running. Old `target/release` files are intentionally untouched. Remove historical Cargo caches only through separately approved housekeeping.

### 0.1.50 Windows encoding QA repair
Use UTF-8 explicitly when Python tests read repository source or JSON on Windows; see `docs/QA_0.1.50.adoc`. The 0.1.49 Studio UX and private operator profile are unchanged. Build, Git, LoopRD and release approvals remain separate.

## 0.1.52 — portable application blueprints and publishing

Under **Asset blueprints**, select **Import from TaviX…**, choose a verified local application `.tavix`, and select only the `.tavib` files to import. These small data-only schematics are stored under the private Studio profile with app/blueprint SHA-256 provenance; they cannot execute the app or grant entitlement. They may use `requiredPrefixes` with a minimum count of one for partial icon packs. The `.tavib` container remains a **proposed Tavi Assets contract**, not yet source-ratified. See `docs/TAVIB_STUDIO_PUBLISHING_052.adoc` and the source helpers `build_tavib.py` and `tools/tavix_embedded_blueprint_pack.py`.

The **Publishing** page now shows remote public GitHub releases and catalog visibility, detects an operator-authenticated `gh` CLI session, and supports creating a private GitHub release draft followed by an independently confirmed public release for an exact locally approved artifact. Every remote write requires the full SHA-256 typed by the operator. GitHub releases do **not** publish to the official Tavi Assets/LoopRD store, mint Gold, grant entitlements, or update `catalog.json`. LoopRD authenticated admin publication is still blocked until the owner adapter and receipts are available. Studio never pulls, commits or pushes source Git repositories.

## Studio 0.1.53 — publishing readiness and compact Connections

This source overlay moves GitHub/LoopRD status out of oversized Connections cards, reports GitHub gateway **source availability** without asserting authentication, shows independent live/public GitHub release discovery and `gh` login in Publishing, and distinguishes locally approved submissions with external dependencies from store-ready remotely published packages. Unsaved destination edits block remote actions, and receipts remain bound to the selected digest and repository. Existing exact-SHA and operator permission gates remain. See `docs/QA_0.1.53.adoc` and `docs/STUDIO_PUBLISHING_CONNECTIONS_053.adoc`. Windows native 0.1.53 acceptance and disposable GitHub publishing verification remain pending. No Git push or public release.

## 0.1.54 — live LoopRD DAPI client (scoped) and blueprint inspector

Publishing saves strict HTTPS host and deployment-provided relative `/admin` and `/catalog` paths in the private Studio profile. A Connect button checks real LoopRD DAPI scopes, not just HTTPS reachability. Read-only catalog and operator versions are displayed; stage and publish are separately approval/receipt gated. Credentials must be issued by the trusted LoopRD service and injected into the Studio native process as `LOOPRD_ASSETS_READ_TOKEN`, `LOOPRD_ASSETS_INGEST_TOKEN`, `LOOPRD_ASSETS_PUBLISH_TOKEN` (only scopes needed). Never paste credentials into renderer fields, ZIP files, Git or Library. An automatic login broker for Tavi/Social `ecosystemAdmin` is not implemented.

Import from TaviX now offers a detailed read-only inspect view for each `.tavib` before selective import, including an optional embedded WebP (when the blueprint container carries it). No application code is executed.

See `../../docs/QA_0.1.54.adoc`. No native Windows acceptance or live registry write claimed.

## Studio 0.1.57 — catalog release metadata table

Publishing begins with a searchable table of local `.tavix` applications, `.tavia` packs, `.tavib` blueprints and read-only discovered LoopRD versions. Price in Gold (blank=unset, 0=free), Listed, Testing and a short description are operator-local **publication drafts** stored by native Rust under the private profile. These fields are not live catalog mutations: the currently specified Tavi Assets `store-offer/v1` has illustrative `displayGoldPrice`, but official store listing/testing state and authoritative pricing require new, owner-approved LoopRD contracts. All release, service-token and receipt gates remain separate. See `docs/QA_0.1.57.adoc`. No Git push or public release.

## Publishing UI layout 0.1.57

Publishing has separate Catalog, Connections, GitHub releases and Tavi Assets / LoopRD tabs; only one section displays at a time. The catalog component stays mounted, preserving in-progress draft edits while browsing other sections. A tab switch never performs any remote operation, and store prices remain drafts until an owner-approved authoritative metadata API is implemented.

## Blueprint vs. product boundary (0.1.58)

Asset blueprints (`.tavib`) are non-commercial compatibility schematics: import from `.tavix` and use them to validate `.tavia` packs, but do not show them as merchandise in Publishing > Catalog or give them Gold, Listed or Testing fields. Native `studio_catalog_save_draft` rejects `blueprint:` keys; old locally saved blueprint draft entries are preserved on disk but omitted from the response read by Publishing. No canonical Tavi Assets/LoopRD store-offer mutation is implemented here.

## GitHub catalog sync (0.1.60 candidate)

From Publishing's Catalog tab choose **Sync from GitHub**. The dedicated tab reads the exact `TheBigTreeInc/tavi-assets` source and public index at one commit, validates source/index correspondence and shows the revision. Browser sign-in uses installed GitHub CLI via the native process (`gh auth login --web --clipboard`), without tokens in the renderer. Review a locally approved `.tavia` to see a proposed **draft-only** `catalog.source.json` entry; explicitly confirm twice with full digest before creating a GitHub draft PR. No archive bytes are uploaded and `catalog.json` stays unchanged. Remote Gold price, Listed, Testing and LoopRD entitlements are not supported by this GitHub catalog. See `docs/QA_0.1.60.adoc`. No automatic push, publish, merge or release.
