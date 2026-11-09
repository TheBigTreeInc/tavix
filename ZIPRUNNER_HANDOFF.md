# TaviX 0.1.12 — host-mediated asset registry administration contract

**Base:** TaviX 0.1.11. **Status:** TaviX-only source/specification candidate; Windows/operator acceptance and Git publication not approved.

## Implemented

- Optional `assets.registry.admin/v1` manifest permission **request**, independent of `assetDependencies` and the existing `tavi.assets/v1` consumer API.
- TaviX package/archive/repository validators recognize the request and reject unsupported permissions. Local developer installer/inventory marks it as `registryAdminRequested`, with `publisher_trust: unverified` and **no grant**.
- `contracts/tavix-registry-admin-v1.json` method index and strict request/response JSON Schema 2020-12 for `status`, staged upload begin/chunk/commit/abort, records list/get, price proposal, publication and revocation.
- Explicit host-native confirmation requirement for price proposals, publishing and revocation; exact-revision trust, authenticated user, LoopRD `ecosystemAdmin` and per-operation permission checks, idempotency, revocation and audit documented.
- No-op packable request example, developer contract and C4 architecture updates, 11 new source tests and ZipRunner Workboard update.
- Historical staged releases and canonical catalog unchanged. No Tavi, LoopRD, Tavi Assets or Tavi Asset Studio source modified.

## Security and integration blockers

- **No real admin capability is implemented.** Tavi 0.3.141 rejects the permission; Social/Tavi must implement verified host grants, trusted user authentication and forwarding, native confirmation and exact-digest developer-preview approval. LoopRD must implement authoritative `ecosystemAdmin`, per-operation authorization, immutable registry transitions and audit.
- The proposed request/response schema and upload transport need **explicit Social/LoopRD agreement** before a production implementation. Do not enable Tavi Asset Studio's admin UI based on the manifest, local preview, app ID, SHA alone or mock permissions.
- The current `tavi.assets/v1` pack-scoped read/customization grants remain separate; no wallet operations or pack ownership are granted.
- Native Windows/Android, real host/LoopRD integration, operator approval and Git publication remain pending.

## Acceptance

Run the full Python unit suite, strict repository index check, exact-package QA and pack/validate-archive on `examples/registry-admin-request/` on Windows ZipRunner. Review negative security cases (copied app ID, unapproved digest, revoked admin role, stale revision, unsupported method, missing host confirmation, missing LoopRD transport) with Social/LoopRD. Obtain separate operator approval before Git push/tag/release. No post-build publication mechanism has been added.
