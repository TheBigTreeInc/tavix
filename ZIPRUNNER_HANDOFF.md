# TaviX 0.1.0 — ZipRunner intake and first release staging

**Project:** `tavix` · **Git remote:** `https://github.com/TheBigTreeInc/tavix.git` · **local checkout:** sibling to Atrium/Companion at `C:\Users\dorbi\source\tavix`.

The new repository was confirmed accessible and empty on 2026-10-25. This artifact is an initial complete source+compiled distribution snapshot, for **ZipRunner's existing Git review/push flow**, not a GitHub push or release.

`extensions/` contains exactly two reviewed-candidate compiled payloads:
- `inc.thebigtree.tavi.atrium/1.0.2/` from Atrium 0.5.37/0.5.38 static Tavi UI.
- `org.tavi.community.companion/0.6.30/` from the supplied compiled Companion bundle.

Every release directory contains compiled UI, `manifest.json`, a deterministic `.tavix` archive, `tavix.lock.json` asset hashes, and `release.metadata.json`. Root `tavi.repository.json` enumerates the latest valid versions under `https://thebigtreeinc.github.io/tavix/`.

**Build command:** `python -m unittest discover -s tests -v && python tools/repository.py check --repository .`. Strict failure on altered compiled assets, stale catalog, cross-publisher takeover or same-version content collision.

**Atrium** v0.5.38 adds the post-build calls `node tools/build_tavi_extension.mjs` and `node tools/stage_tavix.mjs` to its ZipRunner recipe. No Git operations. CI/Pages for standalone Atrium remain separate.

**Companion:** exact 0.6.30 *compiled* release is already staged. Its current source was not attached. For the producer's next source release add `node ../tavix/tools/stage-companion.mjs` after `npm run build` (see `docs/COMPANION_POSTBUILD.adoc`). Do **not** overwrite source with 0.6.27. Do not claim the original uncompiled Companion source has been examined.

**Operator checks:** import this ZIP under `tavix` without replacing any existing different checkout; attach Git remote in ZipRunner Git profiles; run tests and inspect both releases; run same Atrium build twice and confirm idempotence; try a changed same-version artifact and verify rejection; inspect Git diff (source+compiled assets) and push after review; enable GitHub Pages via GitHub Actions; open `https://thebigtreeinc.github.io/tavix/tavi.repository.json` and add this URL in Tavi App Store. Existing 0.3.108 first-party Atrium repository link is separate, so account/source migrations must remain opt-in.

**Not performed:** Git push/commit, GitHub Pages deployment, native Windows/Android acceptance, Companion 0.6.30 source build, backend migration, release approval or installation into user's Tavi.
