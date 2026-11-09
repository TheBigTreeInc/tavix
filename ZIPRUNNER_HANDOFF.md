# 0.1.15 — Next-pass Source Handoff (2026-11-09)

Base: 0.1.14. This package contains only Git-trackable source, docs, tests and update metadata. Native Windows/Android operator acceptance is **not proven**. Existing session data, configuration and publish gates remain external and untouched.

TaviX: portable UI lifecycle controller, refreshed example, and read-only static source/archive kit conformance CLI. No new host privileges.

## Operator review

. Import candidate into ZipRunner and ensure Workboard metadata does not conflict; approval gate remains explicit.
. Run the packaged source checks and verify exact source hash.
. On native Windows, confirm messenger startup and open UI kit example; resize detached window and switch dark/light.
. Test Android phone app viewport, return to portrait chat, and tablet behavior where supported.
. Do not deploy/publish/tag without operator approval.

---

# TaviX 0.1.13 — host-mediated local file import contract and reference SDK

**Base:** TaviX 0.1.12. **Status:** TaviX source candidate; Windows ZipRunner, native Windows/Android operator acceptance and Git publication pending.

## Implemented

- Optional manifest permission `files.local.import` with paired `fileImports` filters for explicit file extensions, MIME types and a 128 MiB maximum. Legacy manifests remain unchanged.
- `tavix.local-file-import/v1` feature negotiation requires both `host.info.features` and `host.capabilities`; a manifest request never grants access.
- Strict request/response JSON Schemas for `files.local.pick`, `files.local.read`, `files.local.close` and `files.local.cancel`, with 64 KiB base64 chunk maximum and explicit cancellation/error codes.
- `sdk/tavix-sdk.mjs` reference client with user-click dispatch, bounded read, cancellation and injectable host-authenticated detached transport adapter; historical Atrium SDK bytes are unchanged.
- Packable `examples/local-file-import` `.tavix` test app, no HTML file input, no network upload, no registry administration or publication.
- Python source/archive/repository/local-install validation, local preview request metadata, documentation, C4, tests and Workboard update.

## External host integration required

- Tavi 0.3.141 does not support `fileImports`, `files.local.import` or the four native picker methods. Social/Tavi must implement native Windows embedded/detached dialog ownership and Android `ACTION_OPEN_DOCUMENT`, scoped file handles, grants, revocation and session routing.
- The TaviX local browser preview does not emulate the native picker. Reference SDK/mock tests are not Windows/Android acceptance.
- No `.tavia` content is uploaded, installed or published. Registry administration remains a separately approved `assets.registry.admin/v1` capability.

## Operator checks

Run Windows ZipRunner full Python tests, strict catalog check, exact-package QA, local-file import reference `.tavix` pack/validate-archive and Node SDK mock tests if Node is available. Inspect denied grants, filter broadening, cancel, file size, session revocation, account switch and detached window behavior in the native host after Social/Tavi implementation. Obtain explicit approval before Git publication.
