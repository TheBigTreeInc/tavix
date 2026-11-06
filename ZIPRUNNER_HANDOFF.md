# TaviX 0.1.8 — C4 architecture source baseline

Source ZIP includes `architecture/c4/workspace.dsl` and `architecture/c4/README.adoc` at the archive root relative to the project. Based on TaviX 0.1.7 code; no extension payload changes.

## Completed in source
- C4 L3 components for publisher/validator CLI, local preview HTTP server and UI, and the producer staging adapter.
- Minimal L1/L2, two dynamic views, a source-supported local deployment view and AsciiDoc evidence with limitations.
- Regression test `tests/test_c4_architecture.py`, versioned ZipRunner metadata, non-gating post-update test and Workboard review item `TAVIX-C4-001`.

## Verification gates
- Run existing Python tests, strict repository check, and C4 source-contract test against the extracted ZIP.
- Structurizr CLI validation: separate optional authoring/operator check; report actual outcome.
- Windows ZipRunner build, fresh post-update checks, Git/Pages and operator acceptance remain independent; no auto push/tag/release.
- New ticket is under Review, not Done, pending operator assessment.
