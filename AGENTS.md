# Agent entry point for tavix

Read in this order before changing code:

1. `INSTRUCT.md` — product intent and non-negotiable behavior.
2. `DESIGN.adoc` — architecture, data boundaries, and update flow.
3. `PROJECT_PLAN.adoc` — accepted milestones, current scope, and risks.
4. `ENGINEERING_STANDARD.adoc` — size, design, dependency, and regression rules.
5. `CODING.md` — implementation and LLM/agent guardrails.
6. `TESTING.md` — focused, full-suite, package, and regression validation.
7. `project.zr` — ZipRunner overlay/build/start/release behavior.

## Working contract
- Use the current source tree as the source of truth.
- Keep each change bounded to the accepted task. For a generated engineering pass, honor its review-versus-extraction stage.
- Preserve behavior and local configuration unless replacement is explicit.
- Add a regression test for every defect.
- Do not grow files already above the configured limit without extracting a coherent responsibility.
- Update design, schemas, and docs when their contract changes.
- Automated work requires a covered design boundary with exact references and no unresolved decision gaps.
- A missing decision blocks only the affected card; do not halt unrelated covered work or choose a default silently.
- Run focused tests first and the full suite before producing an artifact.
- Manager/QA may technically approve a completed candidate for operator testing, but only the operator may mark it Done after observable checks pass.
- Failed operator checks return the exact managed task to bounded development; do not require manual board-state movement.
- Never apply, promote, publish, push, tag, or release without explicit authority.

Machine-readable thresholds live in `ziprunner.quality.json`.

## TaviX architecture maintenance (from 0.1.8)

Maintain `architecture/c4/workspace.dsl` (Structurizr DSL) and `architecture/c4/README.adoc` (AsciiDoc) in the same pass when component responsibilities, exposed interfaces, storage or deployment change. Start with source evidence. Keep external Tavi, Atrium, Companion, ZipRunner and GitHub internals out of TaviX-owned containers. Preserve established C4 element IDs and view keys. Validate with Structurizr CLI if installed; distinguish a Python source-contract test from DSL parser validation.

## TaviX developer contract / cross-product retrieval (0.1.9+)

Before implementing or changing a `.tavix` package, host SDK call, manifest, permission, staging, repository feed or local-preview API, read `docs/INDEX.adoc`, `docs/TAVIX_CONTRACT.adoc`, `docs/TAVIX_PACKAGE_FORMAT.adoc`, and `contracts/tavix-1.0.json`. Read `docs/DEVELOPER_GUIDE.adoc` for applications and the minimal `examples/hello-tavix` fixture for local preview. Other projects should consume reviewed pinned GitHub source revisions; the public GitHub Pages feed is NOT the developer-contract host.

In every pass that changes any of the above interfaces, update the machine-readable contract, AsciiDoc contract and README in the *same versioned source ZIP*. Do not change the `tavix/1.0` protocol identity merely because the TaviX toolchain version changes. Distinguish verified Tavi host methods from SDK wrapper conveniences, and preserve unverified external behaviors as explicit limitations. Run `python -m unittest discover -s tests -p test_contract_docs.py -v` and the full test suite; source-alignment tests prevent obvious drift but are not host runtime acceptance. If an interface/architecture relationship changes, also update both C4 files. Do not auto-publish source docs, update other repositories, or approve operator gates.

## Classification and game-inventory contract (0.1.10+)

For any manifest, installer, local inventory, SDK, Atrium launch or Tavi host change, read `docs/TAVIX_CLASSIFICATION.adoc`, `contracts/tavix-classification-v1.schema.json` and `contracts/tavix-installed-games-v1.json` in addition to the existing contracts. Preserve the `kind: app` v1 envelope and the default classification app/[] for existing manifests. Do not claim Tavi/Atrium support until implemented and verified in those projects. Classification never grants permission or supplies a launch URL. Update both C4 source files and source-binding regression tests when actual TaviX responsibilities change.

## Shared asset dependency contract (0.1.11+)

Read `docs/TAVIX_ASSET_DEPENDENCIES.adoc`, `contracts/tavix-asset-dependencies-v1.schema.json` and `contracts/tavix-asset-grants-v1.schema.json` before changing manifests, permission allowlists, package validation, repository staging or Tavi/Tavi Assets integration. The manifest is a request, not a grant. Tavi owns authenticated host-only grants and must enforce pack/capability *pairs* and per-pack customization; LoopRD/Wallet owns purchases and entitlements; Tavi Assets owns packs and the engine. Do not infer live support from Tavi 0.3.141's dormant bridge. Keep the index, schemas, C4 and source-backed tests synchronized; never publish or modify other repos without approval.

## Privileged registry administration contract (0.1.12+)

Before modifying any privileged extension permission, host feature negotiation, `.tavia` staging, Gold price proposal, publication or revocation wire, read `docs/TAVIX_REGISTRY_ADMIN.adoc` and all three `contracts/tavix-registry-admin-*v1*.json` files. `assets.registry.admin/v1` is a manifest request only; it is not an authorization grant, ownership, wallet permission or substitute for `tavi.assets/v1`. Tavi/Social owns exact-revision host trust, native confirmation and authenticated forwarding; LoopRD alone authorizes `ecosystemAdmin` and registry operations. Do not enable admin controls, invent service credentials, stage/publish assets or auto-push contracts. Keep C4, index, schemas, tests and approval gates synchronized.


## Local-file import capability (0.1.13+)

Before changing file-import permissions, picker methods, SDK wrappers or native host assumptions, read `docs/TAVIX_LOCAL_FILE_IMPORT.adoc`, `contracts/tavix-local-file-import-v1.json` and the three `contracts/tavix-local-file-*v1.schema.json` files. `files.local.import` is a manifest request only; the `tavix.local-file-import/v1` host feature must be negotiated independently of permission approval. No unrestricted filesystem paths, file URLs, broad storage permissions, uploads or automatic registry publication. Tavi owns Windows/Android native pickers and embedded/detached session routing; TaviX only defines/validates requests and provides a reference SDK. Run `tests/test_local_file_import.py`, `tests/test_local_file_sdk.mjs`, contract docs and the full suite. Keep C4, Workboard and release gates synchronized.

## UI kit source parity (0.1.14+)

If changing an application icon, typography, theme or public UI helper, update `docs/TAVIX_UI_KIT_001.adoc`, `contracts/tavix-ui-kit-v1.json`, `sdk/ui-kit/` and the packable `examples/ui-kit/` together, with source-bound regression tests. This kit is independent from host SDK grants, and source parity is not Windows/Android operator acceptance.

## Local Management Suite (0.1.25+)

Before modifying the local test UI, operator credentials, `.tavia` import, draft Gold values, or LoopRD/GitHub controls, read `docs/TAVIX_MANAGEMENT_SUITE_025.adoc`, `openapi.yaml`, and Tavi Assets' `looprd/INTEGRATION.adoc`. Preserve owner boundaries: no TaviX duplicate asset validator, no direct prices/entitlements from local drafts, no secrets in package payload or JavaScript state, no automatic Git pushes. Every mutation requires local origin and CSRF; independent exact-artifact operator receipts and backend scope checks remain required for remote actions. Run `tests/test_manager_suite_025.py`, full source, strict repository and Windows operator acceptance.

## Local diagnostics (0.1.26+)

Read `docs/TAVIX_MANAGEMENT_EVENTS_026.adoc` before modifying import diagnostics or event logging. Diagnostics are bounded, private, credential-free and never authoritative for Git, Wallet or LoopRD. Preserve safe canonical Assets error allowlists, event IDs, CSRF checks and local-only browser/export behavior; run `tests/test_manager_events_026.py` and all previous tests.


## Native Studio desktop boundary (0.1.28+)

Before modifying `tools/studio-desktop/`, read `docs/TAVIX_STUDIO_DESKTOP_028.adoc` and current PatternFly/Tauri versioned documentation. Rust owns trusted operator commands; Node only builds the PatternFly UI. Keep untrusted TaviX previews separate from operator IPC and retain the existing Python console until native acceptance. No GitHub/LoopRD/Wallet authority or secret-handling is delegated to web content. Cargo/native build and dependency-lock verification are explicit operator checks, not inferred from static tests.

## ZipRunner post-update limit (0.1.29)

Post-update test stamps are limited to 20 entries by ZipRunner 1.2.304.299. Retain both suites when combining related checks, and run `tests/test_post_update_stamp_029.py`. The native 0.1.28 Studio source remains unchanged.

## Studio Windows build/launch (0.1.30)

The canonical operator application is `tools/studio-desktop` (PatternFly + Rust/Tauri). Review `docs/QA_0.1.30.adoc` and `tools/studio-desktop/README.md` before altering build/start. Tauri Windows resource icons must be present in source. `project.zr` may start the built Studio binary only after a successful native build; never use the Python preview server as an implicit fallback. Preserve all existing TaviX/Tavi Assets/LoopRD contracts and operator approval gates. Do not ship `node_modules`, compiled `target`, local secrets, generated lockfiles of unknown provenance or preview data.

## Native Studio ZipRunner recipe (0.1.31)

Portable `project.zr` in a source archive is a *review-only proposal* in ZipRunner 1.2.304.300, not active host configuration. The `recipes/tavix-studio.zr` file is a standalone proposal template for import into the *existing* `tavix` project. The operator must review and approve build/start changes and preserve local paths and approval gates. A successful ZIP build with old active settings does not prove a native Studio build. See `docs/QA_0.1.31.adoc`.

## Native Studio submission review (0.1.32)

Read `docs/TAVIX_STUDIO_REVIEW_032.adoc`, `contracts/tavix-studio-asset-blueprint-v1.schema.json` and `tools/studio-desktop/review_cli.py` before editing native package review/blueprint logic. The Rust-native chooser and per-user review storage must never expose arbitrary operator paths to the privileged renderer. Canonical TaviX or Tavi Assets validation is required and independent from designer completeness and local review approval. Feedback ZIPs wrap the unchanged package and external `.adoc` guidance; never insert README/ADOC into `.tavia`. A local preview or review approval never publishes to GitHub, LoopRD or the Wallet. Run `tests/test_studio_review_032.py` and full source checks, then actual Windows native build/operator acceptance.

## Native Studio source connections and diagnostics (0.1.37)

The operator confirmed native Studio 0.1.36 launches. Studio 0.1.37 adds operator-selected Tavi Assets source validation, bounded native readiness and copyable, privacy-safe import failure codes. Local source preferences live in the user profile; they never authorize GitHub/LoopRD publishing. See `docs/QA_0.1.37.adoc`.

## Studio 0.1.38 operator screenshots
The operator confirmed 0.1.36 built/ran, but subsequent screenshots show the pre-0.1.37 Connections placeholder and a global Python validator error. Never infer an installed source update rebuilds the executable. Native Studio version must be visibly displayed and managed launcher must fail safely on a stale binary. Bundled asset blueprint listing must not require a Python process; canonical TAVIA validation still does. No Git/LoopRD publishing changes.

## Native Studio package browsing / publishing destinations (0.1.41)

Before editing package contents or publish setup, read `docs/TAVIX_STUDIO_PACK_BROWSER_041.adoc`. Pack viewer must only read the exact retained SHA-bound original, paginate and validate safe declared image previews, never execute app JavaScript or treat a preview as canonical approval. Publication destination fields are non-secret local configuration only; GitHub and LoopRD remote operations remain independently unimplemented and gated, with no publisher credentials in the renderer or package. Run `tests/test_studio_pack_browser_041.py` and Windows Tauri build before operator acceptance.

## Native Studio builder isolation repair (0.1.43)

Resolve the executable path relative to the active Studio checkout inside the native build call, not from an import-time cached constant. A successful subprocess exit without a PE under that checkout must fail closed. Preserve the no-process-kill/immutable-launch design and approval gates. See `docs/QA_0.1.43.adoc`; Windows native build is operator acceptance only.

## Native Studio operator review UX (0.1.43)

Review `docs/QA_0.1.43.adoc` before editing blueprint selection or package browser layout. Asset blueprint checks still use exact declared resource IDs, never visual count alone. `tarot.card.*` does not auto-map to `tarot.major.*` / `tarot.minor.*`; a separate evidence-backed mapping decision is pending. Browse only private SHA-bound packages, keep a 12-row native page, never execute package code, preserve approval/publishing gates and test the focused 0.1.43 source contract and Windows native behavior.

## Native Studio package grid (0.1.44)

Before editing `src/pack-grid.tsx`, review `docs/QA_0.1.44.adoc`. Keep the 12-entry native page and three-concurrent original-preview limit, stale-request cleanup, keyboard-accessible Grid/List selection and unchanged data-only SHA-bound artwork preview policy. No package or publisher authority from thumbnails; run focused 0.1.44 checks and Windows Tauri acceptance.

## Shared TAVIA client delivery boundary (0.1.45)

Before adding Studio distribution, Tavi client asset requests or `.tavia` host support, read `docs/TAVIA_CLIENT_ASSET_DELIVERY_045.adoc`. The operator-confirmed *target* is per-device downloaded, canonical-SHA-verified `.tavia` packages in a shared Tavi-managed cache, with central LoopRD entitlements and host-mediated reuse across games. TaviX Studio remains an inspection/approval tool, not a trusted client cache or entitlement server. Do not claim these pending cross-project integrations already run or treat public archive availability as paid-pack access control.

## 0.1.46 Windows IPC boundary

The Python `review_cli.py` native output must stay ASCII-safe JSON (`ensure_ascii=True`), so decoded Unicode text does not depend on Windows stdout code pages when Rust parses its response. Only fixed, known canonical asset validation reasons may be shown to UI. Never report arbitrary stderr or weaken content/entitlement/publisher gates. See `docs/QA_0.1.46.adoc`.

## 0.1.48 Windows QA regression

Tests invoking Studio blueprint import MUST isolate both `HOME` and `LOCALAPPDATA` (and pass both to Python subprocesses). On Windows production code correctly uses `%LOCALAPPDATA%/TaviXStudio/blueprints`; `HOME` alone is not a safe test sandbox. Do not delete user-imported blueprints to make tests pass. Preserve `BLUEPRINT_ALREADY_IMPORTED`, native service-authorization, operator review and publication gates. See `docs/QA_0.1.48.adoc`.

## 0.1.49 Studio compact UI contract

Do not reintroduce full-width success banners, repeated global page intro text, or permanent tall import/queue statistic cards ahead of Submission review. Native Tauri picker owns file selection and digest-bound retention; only after that step may renderer display the optional blueprint/custom modal. Custom/unmapped imports remain local, not store-ready, and no automatic semantic resource ID mapping is authorized. Changing/clearing a previous blueprint uses `review_recheck` to reset review approval. Refresh must not unmount the entire content. Keep readable native Windows select contrast and operator-only publication boundary. Regression: `tests/test_studio_compact_workflow_049.py` and `tests/test_studio_import_flow_049.mjs`. See `docs/QA_0.1.49.adoc`.

### 0.1.50 Windows encoding QA repair
Use UTF-8 explicitly when Python tests read repository source or JSON on Windows; see `docs/QA_0.1.50.adoc`. The 0.1.49 Studio UX and private operator profile are unchanged. Build, Git, LoopRD and release approvals remain separate.

## Windows Studio 0.1.52 QA fix

Windows 0.1.50 failed an overbroad encoding regression on 25 pre-existing implicit source reads in seven old tests. Studio 0.1.52 retains strict UTF-8 checks for new/Studio tests, tracks legacy ceilings and documents their separate migration in docs/QA_0.1.52.adoc. Native publish and operator gates are unchanged.

## Studio 0.1.53 — publishing readiness and compact Connections

This source overlay moves GitHub/LoopRD status out of oversized Connections cards, reports GitHub gateway **source availability** without asserting authentication, shows independent live/public GitHub release discovery and `gh` login in Publishing, and distinguishes locally approved submissions with external dependencies from store-ready remotely published packages. Unsaved destination edits block remote actions, and receipts remain bound to the selected digest and repository. Existing exact-SHA and operator permission gates remain. See `docs/QA_0.1.53.adoc` and `docs/STUDIO_PUBLISHING_CONNECTIONS_053.adoc`. Windows native 0.1.53 acceptance and disposable GitHub publishing verification remain pending. No Git push or public release.

## Studio 0.1.54 — LoopRD DAPI adapter and embedded TAVIB inspection

Native Publishing now configures separate approved `/admin` and `/catalog` DAPI paths, verifies scoped live read/inspect responses, and provides exact-review/receipt-gated `stage` and `publish` actions for `.tavia`. Credentials must be short-lived, server-issued and injected into the trusted native Studio process; the Tavi/Social ecosystemAdmin delegation broker is not provided by this source. The Blueprint Import from TaviX dialog now offers an Inspect detail panel (exact resources, prefix minima, optional assets, checklist, readme and optional WebP) before import. See `docs/QA_0.1.54.adoc`. Windows native build and live disposable-registry acceptance are pending. No Git push or public release.

## Studio 0.1.57 — catalog release metadata table

Publishing begins with a searchable table of local `.tavix` applications, `.tavia` packs, `.tavib` blueprints and read-only discovered LoopRD versions. Price in Gold (blank=unset, 0=free), Listed, Testing and a short description are operator-local **publication drafts** stored by native Rust under the private profile. These fields are not live catalog mutations: the currently specified Tavi Assets `store-offer/v1` has illustrative `displayGoldPrice`, but official store listing/testing state and authoritative pricing require new, owner-approved LoopRD contracts. All release, service-token and receipt gates remain separate. See `docs/QA_0.1.57.adoc`. No Git push or public release.

## 0.1.58 Studio blueprint boundary

TAVIB is validation/compatibility metadata, **not a saleable shop SKU**. Publishing catalog drafts include only app and asset-pack submissions, never blueprint definitions; imported blueprints remain discoverable via Asset blueprints and available to review. Preserve any old operator blueprint draft bytes rather than deleting them; reject new blueprint publication drafts natively. The remote store offer contract is owned by Tavi Assets/LoopRD and must separately adopt this exclusion. Do not waive receipt gates or infer remote publication.
