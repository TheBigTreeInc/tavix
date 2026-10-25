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

Unzip `tavix-0.1.0-ziprunner.zip` into a new ZipRunner project with key `tavix` at `C:\Users\dorbi\source\tavix`, bound to `https://github.com/TheBigTreeInc/tavix.git` through the existing Git profile. Keep its normal Git review/push step; **no build script commits or pushes**.

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
