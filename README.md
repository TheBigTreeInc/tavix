# TaviX application repository

This repository is the **static, reviewed distribution output** for TaviX 1.0 apps. It is not an alternative Tavi client, game server, or source-code repository.

All compiled versions are immutable:

```
extensions/
  <application-id>/
    <version>/
      manifest.json
      ui/
      <application-id>-<version>.tavix
      tavix.lock.json
      release.metadata.json

tavi.repository.json
```

The **root `extensions/` directory** contains packaged releases and the root `tavi.repository.json` is the Tavi App Store feed. GitHub Pages hosts the *same relative structure* at `https://thebigtreeinc.github.io/tavix/`. This is **not a signed package registry**; sha256 locks check content integrity but do not prove publisher identity. A Tavi user explicitly approves installs and updates.

## ZipRunner

Import the current versioned `tavix-*-ziprunner.zip` into the existing ZipRunner project with key `tavix` at `C:\Users\dorbi\source\tavix`, bound to `https://github.com/TheBigTreeInc/tavix.git` through the existing Git profile. Keep its normal Git review/push step; **no build script commits or pushes**.

## Producer staging

Once a producer build passes, run from that producer's checkout (or use its configured post-build script):

```sh
python ../tavix/tools/repository.py stage --repository ../tavix --input dist-tavi --source-url https://github.com/TheBigTreeInc/atrium --license NOASSERTION
```

Output is staged under `extensions/<id>/<version>/`. Repeating the same build is a no-op. Reusing a version with different bytes fails and preserves the last good release. The repository index is updated atomically **only after** assets are packaged and validated. The script never stages other applications, does not delete historical versions, and does not use `git` or GitHub credentials.

```sh
python tools/repository.py check --repository .
python -m unittest discover -s tests -v
```

The ZipRunner Git view then shows changes to this repository. Review them and push the `tavix` project separately. GitHub Pages publishes the reviewed commit once Pages is enabled with **GitHub Actions** under Settings → Pages. Never treat local staging or a successful source build as operator approval.

## Tavi configuration

The repository URL after Pages is enabled:

`https://thebigtreeinc.github.io/tavix/tavi.repository.json`

Until a Tavi client explicitly adds that URL to its default repositories, add it through **Apps → App Store → Extension repositories**. Existing installed publisher sources are not silently switched to this repository.

## Responsibility

- Publisher: build and test, then stage *only* compiled TaviX assets.
- TaviX checkout: verify packages and produce one consistent static index.
- ZipRunner: review the checkout diff, commit and push on user approval.
- GitHub Pages: serve public versioned content.
- Tavi: discover apps and let users opt into install/update.

## Initial Companion release provenance

The initial `org.tavi.community.companion` **0.6.30** payload is the supplied *compiled* Tavi extension bundle. Its catalog source points to this `tavix` distribution repository, where the exact distributed JavaScript/HTML assets are browsable. It is **not a claim** that the original uncompiled Companion engine source is hosted in this repository. The independent Companion source project's current build must adopt the post-build staging helper before future releases become fully automated. Do not publish a claimed open-source license until its publisher supplies one.

## Windows build repair (0.1.1)

The 0.1.0 test fixture created its empty catalog with `Path.write_text()`. On Windows, default newline translation introduced CRLF bytes; `check_index()` correctly rejected them because the generated catalog is canonical LF. The fixture now uses `build_index()` and `write_bytes()` on every OS. Strict verification, compiled release checksums, and the published catalog remain unchanged.

## Local extension preview (0.1.3)

Run `python tools/local-client/server.py`, then open `http://127.0.0.1:8765/tools/local-client/index.html`. See `tools/local-client/README.md` for scope and limitations. This preview does not alter publication approval gates.

## 0.1.4 bounded package QA

See `tools/local-client/QA.md` for exact-package integrity checks and explicit exclusions. This is not a multiplayer or real-Tavi acceptance test.

## Local `.tavix` development installation (0.1.5)

Run `python tools/local-client/server.py` and open `http://127.0.0.1:8765/tools/local-client/index.html`. Choose a `.tavix` file and select **Install local .tavix**. The development server validates the archive and file hashes, installs immutable versioned assets into `.tavix-local/` and exposes the panel in a sandboxed preview iframe. Local packages can be removed. Installing the same version again requires explicit removal; no automatic replacement or rollback is implied. The local storage is never published.

**Security boundary:** This is a loopback-only development preview, not the production Tavi SDK or a trusted publisher verification. Do not install untrusted extensions in this preview: HTML/JS may still access its own origin, and the preview is not a hardened security sandbox. There is no production Tavi integration, native file picker, authenticated test identity or multiplayer proof. The source package contains no runtime `.tavix-local/` contents.

## Windows ZipRunner catalog repair (0.1.6)

For the 0.1.5 Windows overlay failure, the ZipRunner build runs a bounded catalog preflight before the normal unit tests and strict index check. See `REPAIR_0.1.6.md` for exact safety conditions and the differences it may reconcile. This preflight **does not approve or publish** catalog changes. Inspect the resulting Git diff and machine-readable preflight output before any authorized push.

## Windows persisted build-command repair (0.1.7)

Some existing ZipRunner projects keep their *operator-owned* build commands and do not replace them from `project.zr`. The 0.1.6 Windows log ran the older two-command sequence, so its separate preflight did not execute. The unchanged command `python tools/repository.py check --repository .` now detects only a stale catalog and calls the **same bounded preflight**, then performs the original strict check again. It prints machine-readable index evidence. Invalid releases, unexpected applications and publisher changes still fail without rewriting.

For explicitly read-only validation, run `python tools/repository.py check --repository . --strict`. The new-project build ends with this strict-only command after the preflight. No active ZipRunner config or Git permissions are altered, and no publishing occurs. See `REPAIR_0.1.7.md`.

## C4 architecture baseline (0.1.8)

`architecture/c4/workspace.dsl` is the Structurizr DSL source of truth for TaviX containers/components and `architecture/c4/README.adoc` is the corresponding AsciiDoc evidence and boundary document. Maintain both when TaviX responsibilities, interfaces, storage or deployment change. This does not introduce new Tavi runtime capabilities; CLI validation is separately recorded when run.
