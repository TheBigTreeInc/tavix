#!/usr/bin/env python3
"""Archive only the verified, superseded Klondike staging draft.

This is a local source-tree reconciliation, not a catalog publisher. It never
performs Git operations, deletes another project's files, or touches config,
secrets, runtime state or active releases. The previous draft is moved into
an ignored, operator-inspectable backup. Unknown or altered content fails closed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repository import validate_release

OLD_APP = 'example.org.klondike'
NEW_APP = 'inc.thebigtree.tavi.klondike'
VERSION = '0.1.1'
OLD_SHA256 = 'c11a9945e8f9f604c366dd496ae3b7f1195af61df58a3c59b6299ce1d45c4ffc'
NEW_SHA256 = 'da4ecd43299c0f05e49beebc5a51fed7146325be8b54b663ac2327103025be92'
APPROVED_CATALOG_IDS = {'inc.thebigtree.tavi.atrium', NEW_APP, 'org.tavi.community.companion'}


def _archive_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive_legacy_draft(root: Path, *, check_only: bool = False) -> dict:
    root = root.resolve()
    legacy = root / 'extensions' / OLD_APP / VERSION
    current = root / 'extensions' / NEW_APP / VERSION
    backup = root / '.tavix-local' / 'archived-staging-drafts' / (OLD_APP + '-' + VERSION + '-' + OLD_SHA256[:12])
    if not legacy.exists() and not legacy.is_symlink():
        return {'status': 'no_legacy_draft', 'changed': False}
    if legacy.is_symlink() or not legacy.is_dir() or any(p.is_symlink() for p in legacy.rglob('*')):
        raise ValueError('Unsafe legacy Klondike draft: symlink or unexpected path; no changes made')
    if backup.exists() or backup.is_symlink():
        raise ValueError('Legacy Klondike archive destination already exists; refusing overwrite')
    if not current.is_dir() or current.is_symlink():
        raise ValueError('Approved TheBigTreeInc Klondike release missing; refusing draft archival')

    # Verify both immutable release directories fully, not only the manifest.
    legacy_manifest, legacy_meta, legacy_archive = validate_release(legacy)
    current_manifest, current_meta, current_archive = validate_release(current)
    if (legacy_manifest.get('id'), legacy_manifest.get('version'), legacy_manifest.get('publisher')) != (OLD_APP, VERSION, 'example-org'):
        raise ValueError('Legacy Klondike identity changed; refusing archival')
    if legacy_meta != {'source': 'https://github.com/TheBigTreeInc/tavix', 'license': 'NOASSERTION'} or _archive_sha(legacy_archive) != OLD_SHA256:
        raise ValueError('Legacy Klondike draft does not match reviewed 0.1.19 bytes; refusing archival')
    if (current_manifest.get('id'), current_manifest.get('version'), current_manifest.get('publisher')) != (NEW_APP, VERSION, 'thebigtreeinc'):
        raise ValueError('Approved Klondike identity changed; refusing archival')
    if current_meta != {'source': 'https://github.com/TheBigTreeInc/tavix', 'license': 'NOASSERTION'} or _archive_sha(current_archive) != NEW_SHA256:
        raise ValueError('Approved Klondike package does not match reviewed 0.1.20 bytes; refusing archival')

    catalog_path = root / 'tavi.repository.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    if catalog.get('schema') != 'tavi.repository/v1':
        raise ValueError('Unexpected catalog schema; refusing archival')
    entries = catalog.get('extensions')
    if not isinstance(entries, list) or {e.get('manifest', {}).get('id') for e in entries} != APPROVED_CATALOG_IDS:
        raise ValueError('Active catalog must contain only the approved Klondike, Atrium and Companion')
    approved = next(e for e in entries if e['manifest']['id'] == NEW_APP)
    if approved.get('release', {}).get('revision') != NEW_SHA256:
        raise ValueError('Active catalog does not reference approved Klondike package')
    companion = next(e for e in entries if e['manifest']['id'] == 'org.tavi.community.companion')
    if companion['manifest'].get('version') != '0.6.40':
        raise ValueError('Active catalog does not preserve Companion 0.6.40')
    companion_release = root / 'extensions' / 'org.tavi.community.companion' / '0.6.40'
    try:
        companion_manifest, companion_meta, companion_archive = validate_release(companion_release)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ValueError('Validated Companion 0.6.40 release missing or invalid; refusing draft archival') from exc
    if companion['manifest'] != companion_manifest or companion['source'] != companion_meta['source'] or companion['release']['revision'] != _archive_sha(companion_archive):
        raise ValueError('Companion 0.6.40 bytes do not match the catalog; refusing draft archival')

    if check_only:
        return {'status': 'would_archive_verified_legacy_draft', 'changed': False,
                'source': legacy.relative_to(root).as_posix(), 'destination': backup.relative_to(root).as_posix()}
    # Same-volume rename: no deletion. .tavix-local is ignored by Git and not
    # scanned by build_index; the operator can inspect/recover the exact bytes.
    backup.parent.mkdir(parents=True, exist_ok=True)
    legacy.rename(backup)
    return {'status': 'archived_verified_legacy_draft', 'changed': True,
            'backup': backup.relative_to(root).as_posix(), 'original_archive_sha256': OLD_SHA256,
            'approved_archive_sha256': NEW_SHA256}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', default='.')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    try:
        result = archive_legacy_draft(Path(args.repository), check_only=args.check_only)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print('TAVIX_KLONDIKE_DRAFT_ARCHIVE_ERROR: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
