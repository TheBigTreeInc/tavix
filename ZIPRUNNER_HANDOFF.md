# TaviX 0.1.11 — asset dependency and requested permission contract

**Base:** TaviX 0.1.10 source ZIP. **Scope:** TaviX-only package tooling, schemas, local developer preview metadata, documentation and tests. **Status:** source candidate, not published or operator-accepted.

## Implemented

- Optional strict `manifest.assetDependencies`: versioned pack IDs, semantic capabilities, required/optional packs and per-pack requested customization.
- `assets.read` and `assets.preferences.write` **requested** permission names, validated against declared dependencies; not runtime grants.
- Host-only `tavix.asset-grants/v1` schema and pure grant-subset checker; no entitlement or permission issuance.
- Archive/packager/repository/local preview validation and read-only display of requested pack IDs.
- Versioned JSON schemas, Tavi Assets card-pack example, developer contract, C4 updates and negative regression tests.
- Existing game/app classification and historical staged release bytes remain unchanged.

## Cross-project source evidence

- Tavi 0.3.141: guarded `tavi.assets/v1` host dispatch with 11 methods exists; `assetGrants` returns null, no Assets engine is attached, and the strict manifest validator rejects new asset dependency fields and permission tokens.
- Tavi Assets 0.1.7: proposed dependency request, data-only pack spec, reference portable JavaScript service and consumer SDK; no production Tavi installation, authenticated entitlements or purchases proven.
- Atrium 0.5.77: no production shared-asset integration demonstrated by supplied source.
- Tavi 0.3.141 now has guarded `games.installed.list/open` source dispatch for trusted Atrium; operator/native acceptance still separate.

## Remaining and acceptance

Tavi must accept the new manifest field/permissions, derive trusted grants bound to verified installed revision and authenticated session, enforce pack/capability pairs and pack-specific customization consent, and connect the reviewed Assets engine. The current Tavi flat grants are insufficient for mixed per-pack write approvals. Tavi Assets must deliver production-ready storage, storefront and entitlement integration. No local declaration can purchase packs or grant ownership.

Windows ZipRunner, native Windows/Android host, operator acceptance, Git push, tag and publication are **not verified/authorized**. Source tests and archive integrity do not establish those gates. Existing operator-managed configuration and approval requirements must be preserved.

## Source QA evidence

Linux source checkout: **70 Python unit tests passed**, strict repository check passed, classified and asset-dependent example packaging validated, catalog preflight unchanged, and 105 staged extension/catalog files preserved byte-for-byte. Exact extracted-ZIP verification and ZIP SHA-256 are reported with the downloadable handoff. Structurizr CLI was not installed; the C4 source-contract tests passed, not a DSL parser. Windows build, Android, real Tavi Assets host and operator acceptance remain pending.
