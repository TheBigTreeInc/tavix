"""Safe local Studio health and review diagnostic journal (not an audit ledger).

Never returns operator absolute paths, usernames, credentials, raw stacktraces,
raw package/manifest names or untrusted error strings to the renderer.
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
import sys
from datetime import datetime, timezone

SCHEMA = 'tavix.studio.diagnostics/v1'
MAX_EVENTS = 48
MAX_BYTES = 32768
CODES = {'INSPECT_OK', 'ARCHIVE_REJECTED', 'IDENTITY_INVALID', 'VERSION_INVALID', 'TAVIA_VALIDATOR_MISSING',
         'TAVIA_CANONICAL_REJECTED', 'TAVIA_ARCHIVE_REJECTED', 'TAVIA_TOO_LARGE', 'TAVIA_VALIDATOR_UNAVAILABLE', 'TAVIA_VALIDATOR_UNEXPECTED', 'TAVIA_VALIDATOR_FAILED',
         'TAVIA_VALIDATOR_TIMEOUT', 'TAVIA_VALIDATOR_PROTOCOL', 'TAVIA_SOURCE_INVALID', 'REVIEW_INTERNAL_FAILURE', 'TAVIX_CANONICAL_REJECTED', 'TAVIX_VALIDATOR_MISSING',
         'BLUEPRINT_TYPE_MISMATCH', 'BLUEPRINT_MISSING_RESOURCE', 'BLUEPRINT_MISSING_GROUP',
         'MANIFEST_SCHEMA_INVALID', 'BLUEPRINT_NOT_SELECTED', 'REVIEW_OPERATION_REJECTED',
         'ASSET_VALIDATOR_UNAVAILABLE', 'TAVIA_RESOURCE_UNSUPPORTED'}


def _private_journal() -> Path:
    if sys.platform == 'win32':
        base = os.environ.get('LOCALAPPDATA')
        if not base:
            raise OSError('Local operator profile unavailable')
        folder = Path(base) / 'TaviXStudio'
    else:
        folder = Path.home() / '.local/share/tavix-studio'
    return folder / 'diagnostics.json'


def _load() -> list[dict]:
    path = _private_journal()
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        return []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, list):
            return []
        results = []
        for item in data[-MAX_EVENTS:]:
            if not isinstance(item, dict) or item.get('code') not in CODES or item.get('operation') not in ('inspect','recheck','cli'):
                continue
            stamp = item.get('at', '')
            if not isinstance(stamp, str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00', stamp):
                continue
            digest = item.get('digestPrefix', '')
            if not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{12}|', digest):
                digest = ''
            results.append({'at': stamp, 'operation': item['operation'], 'code': item['code'],
                            'kind': item.get('kind') if item.get('kind') in ('tavia','tavix') else '',
                            'digestPrefix': digest})
        return results
    except (ValueError, UnicodeError, OSError):
        return []


def record(operation: str, codes: list[str], kind: str = '', digest: str = '') -> None:
    """Best-effort fixed-schema event logging; never interrupts package review."""
    try:
        path = _private_journal()
        if path.is_symlink() or path.parent.is_symlink():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        entries = _load()
        for code in list(dict.fromkeys(codes))[:6]:
            if code not in CODES or operation not in ('inspect','recheck','cli'):
                continue
            entries.append({'at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                            'operation':operation, 'code':code,
                            'kind':kind if kind in ('tavia','tavix') else '',
                            'digestPrefix': digest[:12] if len(digest) == 64 and all(x in '0123456789abcdef' for x in digest) else ''})
        path.write_text(json.dumps(entries[-MAX_EVENTS:], separators=(',', ':')), encoding='utf-8')
    except (OSError, UnicodeError, ValueError):
        pass


def recent() -> list[dict]:
    try:
        return _load()
    except OSError:
        return []


def health(repo: Path, assets: Path | None, source: str = 'sibling') -> dict:
    checks = []
    def add(check_id, status, code, message, next_step=''):
        checks.append({'id':check_id,'status':status,'code':code,'message':message,'nextStep':next_step})
    if (repo/'tools/tavix_package.py').is_file():
        add('tavix-validator','ready','TAVIX_VALIDATOR_READY','TaviX canonical validator found')
    else:
        add('tavix-validator','blocked','TAVIX_VALIDATOR_MISSING','TaviX package validator is missing','Restore tools/tavix_package.py in the TaviX checkout')
    if assets is None:
        add('tavia-validator','blocked','TAVIA_SOURCE_MISSING','Tavi Assets source not connected',
            'Select the tavi-assets project folder in Connections; it must contain project.zr and src/tavi_assets/tavia.py')
    else:
        try:
            descriptor = json.loads((assets/'project.zr').read_text(encoding='utf-8'))
            if descriptor.get('project_key') != 'tavi-assets' or not (assets/'src/tavi_assets/tavia.py').is_file():
                raise ValueError('invalid source')
            sys.path.insert(0,str(assets/'src'))
            try:
                from tavi_assets.tavia import unpack_tavia  # noqa: F401
            finally:
                sys.path.pop(0)
            add('tavia-validator','ready','TAVIA_VALIDATOR_READY','Canonical Tavi Assets validator loads. Package-level validation is checked separately during import')
        except (ValueError, ImportError, OSError, KeyError, TypeError):
            add('tavia-validator','blocked','TAVIA_VALIDATOR_UNAVAILABLE','Tavi Assets source is present but its canonical validator could not be loaded',
                'Check the chosen tavi-assets checkout and its Python runtime dependencies')
    # This check describes source capability only; it never claims GitHub login,
    # successful network reads or publication authorization. Publishing owns live state.
    if (repo/'tools/studio-desktop/studio_release_gateway.py').is_file():
        add('github','ready','GITHUB_RELEASE_GATEWAY_AVAILABLE',
            'Operator-only GitHub release gateway is installed; login and live releases are checked separately in Publishing',
            'Open Publishing to configure the repository and check GitHub sign-in')
    else:
        add('github','pending','GITHUB_RELEASE_GATEWAY_MISSING',
            'GitHub release gateway source is absent', 'Restore the current Studio publisher source')
    if (repo/'tools/studio-desktop/studio_looprd_adapter.py').is_file():
        add('looprd','ready','LOOPRD_NATIVE_ADAPTER_AVAILABLE',
            'Native LoopRD DAPI adapter is installed; scoped credentials, verified paths and server permissions are checked separately',
            'Open Publishing to save verified DAPI paths, test actual scopes and review remote catalog state')
    else:
        add('looprd','pending','LOOPRD_NATIVE_ADAPTER_MISSING',
            'Trusted LoopRD publisher adapter is not installed', 'Restore the current Studio adapter source')
    return {'schema':SCHEMA,'source':source if source in ('operator','environment','sibling') else 'unknown',
            'checks':checks,'recentAttempts':recent(),'diagnosticOnly':True}
