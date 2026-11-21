"""Private Windows Studio executable handoff; immutable per-build launch copies.

Cargo keeps its normal incremental target/release path. A managed Studio process
runs a content-addressed copy instead, so a future Cargo build need not overwrite
the open executable. This module never stops processes or removes old releases.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

SCHEMA = 'tavix.studio.binary-launch/v1'
VERSION = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')
DIGEST = re.compile(r'^[0-9a-f]{64}$')
NAME = 'tavix-studio.exe'


class StudioBinaryError(ValueError):
    pass


def runtime_root(studio: Path) -> Path:
    return studio / 'src-tauri' / 'target' / 'studio-launch'


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        while part := handle.read(1024 * 1024):
            digest.update(part)
    return digest.hexdigest()


def _valid_pe(path: Path) -> bool:
    try:
        with path.open('rb') as handle:
            return handle.read(2) == b'MZ'
    except OSError:
        return False


def stage_build(studio: Path, binary: Path, version: str) -> Path:
    """Install one immutable, versioned launch copy after an actual Cargo build.

    The `current.json` pointer changes only after full copy/hash validation. Never
    overwrite a previously staged executable, including one still running.
    """
    if not VERSION.fullmatch(version):
        raise StudioBinaryError('Invalid Studio source version')
    if not binary.is_file() or not _valid_pe(binary):
        raise StudioBinaryError('Cargo executable is missing or not a Windows PE')
    sha = _hash(binary)
    folder = runtime_root(studio) / version / sha[:16]
    staged = folder / NAME
    folder.mkdir(parents=True, exist_ok=True)
    if staged.exists():
        if not _valid_pe(staged) or _hash(staged) != sha:
            raise StudioBinaryError('Existing immutable Studio launch copy has changed')
    else:
        fd, temp_name = tempfile.mkstemp(prefix='.tavix-stage-', suffix='.tmp', dir=folder)
        try:
            with os.fdopen(fd, 'wb') as out, binary.open('rb') as source:
                shutil.copyfileobj(source, out, 1024 * 1024)
                out.flush()
                os.fsync(out.fileno())
            temp = Path(temp_name)
            if not _valid_pe(temp) or _hash(temp) != sha:
                raise StudioBinaryError('Studio launch copy failed verification')
            # This destination is content-addressed. Never delete/replace it.
            if staged.exists():
                if _hash(staged) != sha:
                    raise StudioBinaryError('Existing immutable Studio launch copy has changed')
            else:
                temp.rename(staged)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    state = {'schema': SCHEMA, 'version': version, 'sha256': sha}
    manifest = runtime_root(studio) / 'current.json'
    fd, temp_name = tempfile.mkstemp(prefix='.tavix-launch-', suffix='.json.tmp', dir=runtime_root(studio))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(state, handle, sort_keys=True, separators=(',', ':'))
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, manifest)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    return staged


def ready_binary(studio: Path, version: str, sources: list[Path]) -> Path:
    """Verify source version, freshness, immutable path and bytes before launch."""
    if not VERSION.fullmatch(version):
        raise StudioBinaryError('Invalid Studio source version')
    manifest = runtime_root(studio) / 'current.json'
    try:
        data = json.loads(manifest.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise StudioBinaryError('No verified Studio build: run the native Windows builder') from exc
    if (not isinstance(data, dict) or set(data) != {'schema', 'version', 'sha256'}
            or data['schema'] != SCHEMA or data['version'] != version
            or not isinstance(data['sha256'], str) or not DIGEST.fullmatch(data['sha256'])):
        raise StudioBinaryError('Studio build receipt does not match current source')
    sha = data['sha256']
    binary = runtime_root(studio) / version / sha[:16] / NAME
    if not binary.is_file() or not _valid_pe(binary) or _hash(binary) != sha:
        raise StudioBinaryError('Studio build receipt does not match executable bytes')
    try:
        if manifest.stat().st_mtime + 0.001 < max(p.stat().st_mtime for p in sources):
            raise StudioBinaryError('Studio executable is older than current source; rebuild first')
    except OSError as exc:
        raise StudioBinaryError('Cannot verify Studio source freshness') from exc
    return binary
