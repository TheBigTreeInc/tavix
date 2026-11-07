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
