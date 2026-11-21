"""Windows-native Studio builder: reuse healthy npm tree; repair an incomplete install.

No broad process termination, destructive cleanup, credential access, installation,
publication, or changes to active ZipRunner configuration are performed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

# The shared release-copy helper is source-owned, not an external dependency.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from studio_binary import StudioBinaryError, stage_build

STUDIO = Path(__file__).resolve().parent
ROOT = STUDIO.parents[1]
# Use one dedicated, reusable Cargo target so the old running executable
# in target/release is never replaced during migration.
BUILD_TARGET = STUDIO / 'src-tauri' / 'target' / 'studio-managed-build'
BIN = BUILD_TARGET / 'release' / 'tavix-studio.exe'
TOOLS = ('tsc', 'vite', 'tauri')


def command_executable(name: str) -> str | None:
    return shutil.which(name)


def _npm_shims_present() -> bool:
    """Windows npm script commands must be available for TypeScript/Vite/Tauri."""
    binaries = STUDIO / 'node_modules' / '.bin'
    return all((binaries / (name + '.cmd')).is_file() for name in TOOLS)


def _npm_install_healthy(npm: str) -> bool:
    if not _npm_shims_present():
        return False
    try:
        # Local package-tree verification, not a package download or update.
        checked = subprocess.run([npm, 'ls', '--depth=0', '--offline'], cwd=STUDIO,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 timeout=90, check=False)
        return checked.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _dependency_command(npm: str) -> list[str]:
    # Re-running npm ci on a populated tree unlinks every package and often
    # fails EBUSY on Windows. Repair a partial tree incrementally instead.
    if (STUDIO / 'node_modules').is_dir():
        return [npm, 'install', '--no-audit', '--no-fund']
    if (STUDIO / 'package-lock.json').is_file():
        return [npm, 'ci', '--no-audit', '--no-fund']
    print('NOTICE: no reviewed package-lock.json; npm will create a local candidate lockfile for separate review.')
    return [npm, 'install', '--no-audit', '--no-fund']


def build_native() -> int:
    if sys.platform != 'win32':
        print('TaviX Studio Windows build: not run on non-Windows (source checks only).')
        return 0
    required = STUDIO / 'src-tauri' / 'icons' / 'icon.ico'
    if not required.is_file() or required.stat().st_size < 100:
        print('ERROR: Studio Windows resource missing: src-tauri/icons/icon.ico', file=sys.stderr)
        return 2
    for tool in ('node', 'npm', 'cargo'):
        if not command_executable(tool):
            print(f'ERROR: {tool} unavailable; native Studio build NOT verified', file=sys.stderr)
            return 2
    config = json.loads((STUDIO / 'src-tauri' / 'tauri.conf.json').read_text(encoding='utf-8'))
    if config['identifier'] != 'inc.thebigtree.tavix.studio':
        print('ERROR: Unexpected Studio application identity', file=sys.stderr)
        return 2
    package_version = json.loads((STUDIO / 'package.json').read_text(encoding='utf-8')).get('version')
    if package_version != config.get('version'):
        print('ERROR: Tauri and frontend source versions disagree; check whether the ZipRunner overlay applied.', file=sys.stderr)
        return 2
    # Resolve the output from the active Studio checkout, not the import-time
    # module constant. The latter can point at an unrelated earlier build when
    # the workspace is changed by tests or a managed invocation.
    build_binary = STUDIO / 'src-tauri' / 'target' / 'studio-managed-build' / 'release' / 'tavix-studio.exe'
    # Never touch the old Cargo output that previous releases launch directly.
    # The dedicated managed Cargo directory is reused for incremental builds.
    if build_binary.is_file():
        try:
            with build_binary.open('r+b'):
                pass  # non-mutating Windows sharing/ACL preflight
        except PermissionError:
            print('ERROR: STUDIO_BUILD_OUTPUT_LOCKED: close the running older TaviX Studio '
                  'window, then retry. No processes were terminated.', file=sys.stderr)
            return 3
    npm = command_executable('npm')
    try:
        if not _npm_install_healthy(npm):
            command = _dependency_command(npm)
            print('Studio frontend dependencies missing or incomplete; attempting npm repair/install.')
            subprocess.run(command, cwd=STUDIO, check=True)
            if not _npm_install_healthy(npm):
                print('ERROR: npm finished, but TypeScript/Vite/Tauri are still missing or invalid. '
                      'Inspect npm logs and node_modules/.bin; do not launch an incomplete build.', file=sys.stderr)
                return 1
        else:
            print('Studio frontend dependencies verified; skipping npm reinstall.')
        subprocess.run([npm, 'run', 'tauri', '--', 'build', '--no-bundle'], cwd=STUDIO,
                       check=True, env={**os.environ, 'TAVIX_REPO_ROOT': str(ROOT),
                                        'CARGO_TARGET_DIR': str(STUDIO / 'src-tauri' / 'target' / 'studio-managed-build')})
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f'ERROR: native Studio build failed: {exc}', file=sys.stderr)
        print('If npm reports EBUSY, close Node/Vite/IDE processes using this Studio folder, '
              'let the lock clear and retry. This script never deletes node_modules or kills processes.',
              file=sys.stderr)
        return 1
    if not build_binary.is_file() or build_binary.read_bytes()[:2] != b'MZ':
        print('ERROR: Tauri exited successfully but Windows executable is missing or invalid', file=sys.stderr)
        return 1
    try:
        staged = stage_build(STUDIO, build_binary, package_version)
    except (OSError, StudioBinaryError) as exc:
        print(f'ERROR: STUDIO_LAUNCH_STAGE_FAILED: {exc}', file=sys.stderr)
        return 1
    print('TaviX Studio native Windows executable built:', build_binary)
    print('Verified managed launch copy:', staged)
    return 0


if __name__ == '__main__':
    raise SystemExit(build_native())
