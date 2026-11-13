= TaviX 0.1.22 ZipRunner source handoff

Project: tavix
Version: 0.1.22
Base version: 0.1.20 (0.1.21 was rejected by Workboard parsing before source overlay)

Repair: ZipRunner 1.2.304.278 rejected 0.1.21 because `TAVIX-KLONDIKE-DRAFT-ARCHIVE-021` lacked mandatory `operator_checks`. This self-contained overlay retains every 0.1.21 source change and adds non-empty operator checklists to implemented and remaining Workboard entries, plus regression tests. It preserves the approved TheBigTreeInc Klondike 0.1.1, Companion 0.6.40, guarded legacy draft archive, TaviX Store Editor and original approval gates.

Windows ZipRunner should execute (operator acceptance pending):
* Workboard update parses before any overlay changes
* python tools/klondike_legacy_draft_archive.py --repository .
* python tools/ziprunner_catalog_preflight.py --repository .
* python -m unittest discover -s tests -v
* python tools/repository.py check --repository . --strict
* node --test tests/*.mjs

Next: obtain separate operator approval for the reviewed Git push/Pages publication, then test the Klondike listing and Install button on the phone BEFORE installation.
No Git push or public release is authorized by this ZIP.
