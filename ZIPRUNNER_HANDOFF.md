# TaviX 0.1.18 — Windows encoding portability repair

Base: 0.1.17 (unaccepted Windows build candidate). Corrected implicit source-test `.read_text()` calls in `tests/test_store_editor.py` to explicitly request UTF-8 and added a regression guard. Windows Python default CP1252 previously raised `UnicodeDecodeError` on editor HTML. No runtime functionality, Store catalog, previously published extension bytes, signing, host permissions, wallet or approval gates changed.

Re-run all three existing ZipRunner build commands, especially `python -m unittest discover -s tests -v`, on the Windows operator machine. Native editor file-picker/export acceptance is still pending. No Git push/public release authorized.
