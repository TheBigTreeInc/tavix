"""Managed TaviX Studio launcher: use the verified versioned release copy."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from studio_binary import StudioBinaryError, ready_binary

STUDIO = Path(__file__).resolve().parent
ROOT = STUDIO.parents[1]
# Cargo's incremental output is NEVER launched directly; it must remain writable.
EXE = STUDIO / 'src-tauri' / 'target' / 'release' / 'tavix-studio.exe'


def main() -> int:
    if sys.platform != 'win32':
        print('TaviX Studio native start is currently supported only on Windows.', file=sys.stderr)
        return 2
    sources = [STUDIO / 'package.json', STUDIO / 'src/main.tsx', STUDIO / 'src/pack-browser.tsx', STUDIO / 'src/publishing-setup.tsx',
               STUDIO / 'src-tauri/src/lib.rs', STUDIO / 'src-tauri/src/review.rs',
               STUDIO / 'src-tauri/src/studio_connection.rs',
               STUDIO / 'src-tauri/src/studio_publish.rs', STUDIO / 'studio_pack_catalog.py',
               STUDIO / 'src-tauri/tauri.conf.json',
               STUDIO / 'src-tauri/Cargo.toml']
    try:
        package_version = json.loads(sources[0].read_text(encoding='utf-8'))['version']
        tauri_version = json.loads((STUDIO / 'src-tauri/tauri.conf.json').read_text(encoding='utf-8'))['version']
        if package_version != tauri_version:
            print('ERROR: Studio frontend and Tauri source versions disagree.', file=sys.stderr)
            return 2
        exe = ready_binary(STUDIO, package_version, sources)
    except (OSError, ValueError, KeyError, StudioBinaryError) as exc:
        print(f'ERROR: {exc}. Close the old Studio window and run '
              'python tools/studio-desktop/build_windows.py', file=sys.stderr)
        return 2
    # ZipRunner manages this process handle. Never execute Cargo's mutable output.
    return subprocess.call([str(exe)], cwd=str(ROOT), env={**os.environ,
                                                            'TAVIX_REPO_ROOT': str(ROOT)})


if __name__ == '__main__':
    raise SystemExit(main())
