# TaviX 0.1.7 — legacy ZipRunner build command repair

## Evidence from the 0.1.6 Windows failure

The operator log for 0.1.6 recorded 24/24 unit tests passing, then `python tools/repository.py check --repository .` failing with a stale/modified catalog. Critically, the new `python tools/ziprunner_catalog_preflight.py --repository .` step was **not called**, even though it was present in the ZIP's `project.zr`. The existing project appears to retain its own build commands. We cannot infer the particular mismatching catalog bytes from this log.

## Bounded source-only fix

`tools/repository.py check` now attempts the pre-existing safe `preflight()` **only when** the strict check fails with the stale-index exception. If preflight rejects the discrepancy, the command exits nonzero without rewriting. If it repairs a known-safe difference (formatting/CRLF or older catalog pointing to already validated newer release), it reruns strict `check_index()` before reporting success. The JSON output includes preflight reason, SHA-256 values and any version upgrades; `operator_review_required=true` on reconciliation.

`check_index()` itself is not changed and remains a strict, read-only test. The CLI `check --strict` never runs reconciliation, allowing separate final validation. Staging remains strictly validated as before, with no automatic publisher or Git changes. All distribution `.tavix` payloads and immutable manifests/locks are untouched.

## How to verify on Windows

1. Import this source ZIP to the **existing** TaviX ZipRunner project, preserving active configuration, Git and operator approvals.
2. Confirm the build log executes the existing two commands, and the final check reports a JSON `index_preflight` result or a specific refusal.
3. In PowerShell, run `python tools/repository.py check --repository . --strict` after the build.
4. Review `git diff -- tavi.repository.json` and all changes before any authorized commit or push.
5. Start `python tools/local-client/server.py`, test installing and removing a known `.tavix` package, and record operator acceptance separately.

If the checker still refuses, do **not** force an unconditional `repository.py index`. Supply the JSON/error and a list of local extension version directories for targeted repair.

## Local regression evidence

30 Python tests pass, including six new subprocess tests covering existing CLI check with CRLF/validated overlay, strict read-only failure, tampered publisher refusal, unreviewed-app refusal and strict check on a clean tree. Windows host acceptance not observed.
