# TaviX 0.1.6 — Windows ZipRunner index preflight repair

## Failure reproduced from operator log

`tavix-0.1.5-local-package-installer-ziprunner.zip` was overlaid into an existing Windows checkout by ZipRunner 1.2.304.255. All **18 Python tests passed**, then `python tools/repository.py check --repository .` failed with `Stale or modified repository index`.

The supplied 0.1.5 ZIP passes the same strict index check when freshly extracted on Linux. Therefore the evidence establishes a **post-overlay checkout mismatch** but does **not** establish which Windows file or extra on-disk version caused it. Do not assume that Windows newline conversion was the only cause.

## Source-only repair

- Adds `tools/ziprunner_catalog_preflight.py` as the first build step.
- Validates all release assets and archives before acting.
- Preserves strict `python tools/repository.py check --repository .` as the final build step.
- Leaves the catalog untouched when already canonical.
- Allows canonical LF normalization when parsed JSON is identical to the expected index.
- Allows reconciliation of a previously valid older index to *newer already-present releases* **only** when original entries still match immutable releases, app identities are identical, publishers match, and all extra releases validate.
- Rejects tampered catalog entries, missing/corrupt releases, new unreviewed apps, publisher changes and unexplained index divergence without rewriting the index.
- Prints a machine-readable `reason`, old/new SHA-256 and upgraded extension versions so the Windows operator can review differences.
- Corrects ZIP project and manifest metadata to 0.1.6 (the prior 0.1.5 ZIP still declared 0.1.2 in several version fields).
- Retains 0.1.5 local package installer, all historical extension assets and non-publication gates.

The preflight can change `tavi.repository.json` **inside the local checkout** for an eligible discrepancy. This does **not** push, tag, publish or authorize release. Any change to the catalog must be reviewed by the operator before Git publication. If the preflight rejects an index, inspect the Windows checkout; never force regeneration blindly.

## Checks

```powershell
python tools/ziprunner_catalog_preflight.py --repository .
python -m unittest discover -s tests -v
python tools/repository.py check --repository .
python tools/local-client/qa.py --repository . --extension inc.thebigtree.tavi.atrium --version 1.0.5
```

The negative regression tests include canonical CRLF repair, validated newer-version overlay, catalog tampering rejection, missing release rejection, and new-app rejection. Real Windows acceptance is still pending.
