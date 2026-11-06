# Exact-package QA

Run `python tools/local-client/qa.py --repository . --extension inc.thebigtree.tavi.atrium --version 1.0.5 --output qa-result.json`.

The report verifies the staged manifest, local panel entrypoint, archive CRC, member paths, and SHA-256. It does **not** prove Tavi SDK behavior, installation, real identities, multiplayer, Checkers rules, or native Tavi operation. No external services are contacted. Reports are local evidence only.
