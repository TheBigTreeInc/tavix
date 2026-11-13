= TaviX 0.1.23 — Klondike optional card-back consumer candidate

Project: tavix
Version: 0.1.23
Base: 0.1.22 (approved TheBigTreeInc Klondike 0.1.1 remains immutable)

Implemented: immutable Klondike 0.1.2 staging with `assets.read`, approved `org.tavi.cards.standard` / `card.back` request, source-pinned read-only Assets SDK, host negotiation, guarded media and bundled fallback. Node negative tests and exact archive validation. No Wallet, install, file access, remote packs or extra grants.

Important source note: The previous 0.1.22 ZipRunner overlay assumes a complete current Git checkout with Companion 0.6.40. The older 0.1.19 full ZIP does not contain that release. Rebuilt source on this host could not run full canonical repo checks against the incomplete historical reconstruction; native ZipRunner must re-run all gates on actual current checkout.

Acceptance: Node/client and package fixtures can run off-host; full repository/Windows, detached, Android and user-consent QA remain pending. Inspect the exact Git diff. Never auto-push, tag or publish.

No Git push or public release is authorized by this source ZIP.
