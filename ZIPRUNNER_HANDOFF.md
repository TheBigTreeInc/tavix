# TaviX Studio 0.1.58 — blueprint merchandise separation

- Project `tavix`, version `0.1.58`, base `0.1.57`; safe incremental ZipRunner source overlay with `delete_missing: false`.
- Only `.tavix` application and `.tavia` asset-pack items appear in Publishing Catalog. `.tavib` blueprints remain importable and used for resource compatibility, never pricing, listing, testing or entitlements.
- Rust catalog draft command fails closed on blueprint identities and preserves historical local draft bytes.
- Run new regression suites and full Windows native build. Operator acceptance remains pending.
- No Git push or public release is authorized by this source overlay. No private credentials or runtime profiles are included.

## 0.1.60 GitHub catalog editor candidate

- Native `studio_github_catalog_sync` fetches the pinned source and generated public index from `TheBigTreeInc/tavi-assets`. This is separate from TaviX application GitHub releases.
- `studio_github_catalog_preview` computes a metadata-only draft source diff for an exact locally approved `.tavia` after SHA-256 verification.
- `studio_github_catalog_prepare` can create a new GitHub branch and **DRAFT PR** only after explicit hash + two user confirmations and a fresh remote revision. No binary upload, `catalog.json` change, official LoopRD publish, Gold offer, or entitlement follows.
- `studio_github_login` opens `gh auth login --web --clipboard` in a native Windows terminal/browser; Studio never takes or persists GitHub tokens. Credential storage belongs to GitHub CLI and the operating system.
- Current source baseline is 0.1.58; 0.1.59 is independently reserved for the managed publishing-eligibility correction. Reconcile before promoting either candidate; do not automatically merge or publish a draft PR.
- Windows Rust and complete Tauri/TypeScript build pending. No actual remote GitHub write performed while preparing this source.
