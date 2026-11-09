# Testing and regression rules for tavix

## Required sequence
1. Reproduce the defect or define the acceptance criterion.
2. Add or identify a focused regression test.
3. Run the smallest relevant test while iterating.
4. Run component/integration tests for affected boundaries.
5. Run the complete project suite before packaging.
6. Compile or lint the touched language where supported.
7. Open and validate the produced archive.
8. Extract it into a fresh temporary directory and repeat package-level checks.

## Bug fixes
A bug fix is incomplete without a regression test unless automation is impossible. Then record exact manual reproduction and verification steps.

## Refactoring
Add characterization tests before moving legacy behavior. Separate refactoring from feature work when practical.

## UI work
Test state transitions and commands, not only widget construction. Capture the relevant screen and list exact operator checks.

## Safety and persistence
Exercise invalid input, interrupted writes, restart recovery, duplicate delivery, and protected paths. Durable formats require migration/recovery tests.

## Packaging gate
A handoff package must compile, pass focused and full tests, exclude secrets and active local configuration, open as a readable archive, and pass validation from a fresh extraction.

## Developer contract regression (0.1.9+)
Run `python -m unittest discover -s tests -p test_contract_docs.py -v` whenever package rules, SDK message names/fields, preview API or docs change. This verifies JSON and AsciiDoc presence, known schema/version strings, SDK method inventory, sample package, source limit constants and stable documentation paths. It does not certify the current external Tavi host or full security compatibility. A documentation change must not alter compiled extension bytes or public catalog without separate review.

== Game/app classification acceptance (0.1.10)

Run `python -m unittest discover -s tests -p test_classification.py -v` and the full suite. Verify the classified example packs and installs locally; unclassified packages stay app/[], malformed category tags fail. These tests do *not* claim trusted Tavi host inventory, Atrium invocation or native Tavi 0.3.124 compatibility.

== Asset dependency contract regression (0.1.11)

Run `python -m unittest discover -s tests -p test_asset_dependencies.py -v`. This covers legacy package acceptance, strict dependency and permission requests, lock-consistent forged archives, host-only grant subset checking, JSON schemas and local repository staging. It is **not** proof that Tavi 0.3.141 accepts these manifests or that real Tavi Assets engine/LoopRD entitlements are integrated.

## Registry administration contract (0.1.12)

Run `python -m unittest discover -s tests -p test_registry_admin.py -v`, full unit suite, strict repository check, and package/archive validation of `examples/registry-admin-request`. These are source/specification checks only. Tavi host authorization, LoopRD `ecosystemAdmin`, native confirmations, upload streaming, revocation and end-to-end Windows/Android acceptance require separately reviewed integrations and operator evidence. Do not mark production authorization passed based on these tests.


== Local-file import source acceptance (0.1.13)

Run `python -m unittest discover -s tests -p test_local_file_import.py -v`, `node --test tests/test_local_file_sdk.mjs` where Node is available, `python -m unittest discover -s tests -p test_contract_docs.py -v` and the full suite. Pack and validate `examples/local-file-import` as `.tavix`. Test invalid filters, missing permission, legacy packages, cancellation, bounded reads, detached transport shape and denial on revoked grants. Source tests do not certify Windows WebView2, Android `ACTION_OPEN_DOCUMENT`, native user activation or actual host grants; those require separate Tavi operator acceptance.
