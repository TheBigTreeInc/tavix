# TaviX 0.1.10 — Classification and game inventory contract

This source candidate is based on 0.1.9. Its `tools/tavix_classification.py` validates the optional `manifest.classification` object; the repository staging validator and local package installer/discovery use the same policy. The local preview labels game/app packages. New manifests can use `{"classification":{"type":"game","categories":["cards","solitaire"]}}` while keeping legacy `kind: "app"`. Older manifests default to app/[] in updated consumers. Previously published extension releases and catalog bytes are unchanged.

`docs/TAVIX_CLASSIFICATION.adoc`, `contracts/tavix-classification-v1.schema.json`, `contracts/tavix-installed-games-v1.json`, and `examples/classified-game` establish the source-backed metadata contract and proposed privileged host integration. The latter is explicitly **not implemented** in existing Tavi 0.3.124, Atrium 1.0.5 or TaviX preview. Native Tavi must validate and persist classification in its own trusted registry; authorized Atrium may then request a read-only game inventory and host-controlled launch. No cross-extension private data access is permitted.

For Windows operator review, run:

```powershell
python -m unittest discover -s tests -v
python tools/repository.py check --repository . --strict
python tools/tavix_package.py validate examples/classified-game
python tools/tavix_package.py pack examples/classified-game local-classified-game.tavix
python tools/tavix_package.py validate-archive local-classified-game.tavix
```

The example archive is a development artifact; do not stage or push it without explicit separate review. No active `ziprunner.config.json`, runtime state, private data, or release assets are included or modified in this candidate. The Workboard update keeps operator Review and Done distinct, and publication must be explicitly approved. Structurizr CLI parsing was not performed in this environment; source-level C4 regression tests are part of the Python suite.
