"""Canonical .tavia validation via an explicit Tavi Assets source checkout.

The subprocess reports only allowlisted canonical validation reasons, never raw
tracebacks, local paths, package contents, or environment-derived credentials.
"""
from __future__ import annotations
import hashlib
import io
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

MAX_UPLOAD = 32 * 1024 * 1024

# Diagnostic copy of the suffix allowlist in Tavi Assets 0.1.16 core.SUFFIXES.
# Only used *after* the canonical validator rejects an archive, never to grant
# support for a resource or to bypass canonical validation.
TAVIA_RESOURCE_SUFFIXES = frozenset(('.svg', '.png', '.webp', '.jpg', '.jpeg',
                                    '.ogg', '.wav', '.mp3', '.json'))
_SAFE_MEMBER = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._/-]{0,95}$')


def _unsupported_resource_diagnostic(archive_bytes):
    """Explain a canonical suffix rejection without exposing untrusted ZIP paths.

    Filename reporting is deliberately constrained to simple *relative archive*
    paths; no host paths, filenames containing credentials, or arbitrary text can
    escape into the operator's persistent event journal.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            unsupported = [entry.filename for entry in archive.infolist()
                           if entry.filename != 'manifest.json'
                           and not entry.filename.lower().endswith(tuple(TAVIA_RESOURCE_SUFFIXES))]
    except (zipfile.BadZipFile, EOFError, OSError, ValueError):
        return ('', 0, '')
    if not unsupported:
        return ('', 0, '')
    # A rejected archive may have malicious names. Never log a nonconforming
    # path verbatim, even when its extension is recognized as unsupported.
    first = unsupported[0]
    if (not _SAFE_MEMBER.fullmatch(first) or '..' in first.split('/') or
            first.startswith('/') or any(fragment in first.lower() for fragment in
                ('token', 'secret', 'password', 'ghp_', 'github_pat_',
                 'bearer', 'credential', 'key=', 'auth'))):
        first = '[unsafe archive member name hidden]'
    suffixes = sorted({Path(name).suffix.lower() or '(none)' for name in unsupported})
    # Restrict output to established ASCII extensions rather than arbitrary names.
    suffixes = [s if re.fullmatch(r'\.[a-z0-9]{1,12}', s)
                else '(other)' for s in suffixes]
    types = ', '.join(dict.fromkeys(suffixes[:6]))
    return (first, len(unsupported), types[:72])

# Canonical AssetError messages from the pinned Tavi Assets 0.1.16 validator.
# Do not expose arbitrary subprocess stderr to an unprivileged browser response.
KNOWN_REASONS = frozenset((
    'missing or oversized TAVIA archive', 'invalid TAVIA entry count',
    'unsupported TAVIA entry', 'unsafe TAVIA entry', 'TAVIA unpack limit exceeded',
    'unsupported TAVIA resource type', 'TAVIA entry size mismatch',
    'TAVIA incomplete entry', 'TAVIA has missing or unexpected files',
    'duplicate JSON key', 'oversized JSON document', 'invalid JSON document',
    'unsafe path', 'reserved Windows asset path', 'unsafe or unsupported asset path',
    'unsafe SVG markup', 'invalid SVG', 'invalid SVG namespace',
    'active or unsupported SVG element', 'active or unsupported SVG attribute',
    'content type does not match asset file', 'asset source must be a directory',
    'unsupported manifest schema', 'invalid pack ID', 'invalid pack version',
    'unsupported host compatibility', 'invalid pack type',
    'missing or excessive files', 'missing or excessive resources',
    'case-colliding asset names', 'invalid file digest', 'symlink in asset path',
    'missing or escaped file', 'invalid file size', 'oversized asset pack',
    'integrity failure', 'invalid capability name', 'invalid resource declaration',
    'missing resource default', 'invalid variants', 'invalid variant',
    'variants must have one media type',
    # Confirmed metadata.py _token() message: reject camelCase names such as cardNumber.
    'invalid attribute key',
))
MARKER = 'TAVIX_INSPECT_RESULT:'

_INSPECT = r'''import json,sys,tempfile,zipfile
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1])/'src'))
try:
 from tavi_assets.tavia import unpack_tavia
 from tavi_assets.core import AssetError
 with tempfile.TemporaryDirectory(prefix='tavix-tavia-inspect-') as d:
  m=unpack_tavia(sys.argv[2],d)
  result={'id':m['id'],'version':m['version'],'display':m.get('display',{}),
   'type':m.get('type',''), 'resources':list(m.get('resources',{})),
   'objects':list(m.get('objects',{})), 'collections':list(m.get('collections',{})),
   'filesCount':len(m.get('files',{}))}
 print('TAVIX_INSPECT_RESULT:'+json.dumps({'ok':True,'result':result}))
except AssetError as e:
 print('TAVIX_INSPECT_RESULT:'+json.dumps({'ok':False,'reason':str(e)}))
except (zipfile.BadZipFile,EOFError):
 print('TAVIX_INSPECT_RESULT:'+json.dumps({'ok':False,'reason':'invalid TAVIA archive'}))
except Exception:
 print('TAVIX_INSPECT_RESULT:'+json.dumps({'ok':False,'reason':'unexpected validator failure'}))
'''


class AssetImportError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.public_message = message


def require_assets_source(root):
    if not root:
        raise AssetImportError('TAVIA_SOURCE_MISSING',
                               'Tavi Assets checkout not connected. Restart with --assets-root pointing to its source folder.')
    root = Path(root).resolve()
    descriptor = root / 'project.zr'
    if not descriptor.is_file() or json.loads(descriptor.read_text(encoding='utf-8')).get('project_key') != 'tavi-assets':
        raise AssetImportError('TAVIA_SOURCE_INVALID', 'Configured Assets root is not a Tavi Assets source checkout')
    if not (root / 'src/tavi_assets/tavia.py').is_file():
        raise AssetImportError('TAVIA_VALIDATOR_MISSING', 'Canonical TAVIA validator is missing from Assets checkout')
    return root


def inspect_tavia(data, assets_root):
    if not data:
        raise AssetImportError('TAVIA_EMPTY', 'TAVIA archive is empty')
    if len(data) > MAX_UPLOAD:
        raise AssetImportError('TAVIA_TOO_LARGE', 'TAVIA archive exceeds 32 MiB upload limit')
    source_root = require_assets_source(assets_root)
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            if len(members) > 1000 or sum(i.file_size for i in members) > 160*1024*1024:
                raise AssetImportError('TAVIA_ARCHIVE_LIMIT', 'TAVIA exceeds archive entry or unpack limits')
    except (zipfile.BadZipFile, EOFError) as exc:
        raise AssetImportError('TAVIA_ARCHIVE_INVALID', 'File is not a valid .tavia ZIP archive') from exc
    with tempfile.TemporaryDirectory(prefix='tavix-manager-') as d:
        path = Path(d) / 'candidate.tavia'
        path.write_bytes(data)
        try:
            result = subprocess.run([sys.executable, '-I', '-c', _INSPECT, str(source_root), str(path)],
                                    cwd=str(source_root), capture_output=True, text=True, timeout=30,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                                    env={k:v for k,v in os.environ.items() if not k.startswith('LOOPRD_')})
        except subprocess.TimeoutExpired as exc:
            raise AssetImportError('TAVIA_VALIDATOR_TIMEOUT', 'Canonical asset validation timed out') from exc
        if result.returncode:
            raise AssetImportError('TAVIA_VALIDATOR_FAILED',
                                   'Canonical asset validator could not run; verify the Assets checkout and Python environment')
        lines = [line[len(MARKER):] for line in result.stdout.splitlines() if line.startswith(MARKER)]
        if len(lines) != 1:
            raise AssetImportError('TAVIA_VALIDATOR_PROTOCOL', 'Canonical validator returned no structured result')
        try:
            response = json.loads(lines[0])
        except (ValueError, TypeError) as exc:
            raise AssetImportError('TAVIA_VALIDATOR_PROTOCOL', 'Canonical validator returned invalid structured data') from exc
        if response.get('ok') is not True:
            reason = response.get('reason')
            if reason in KNOWN_REASONS:
                if reason == 'unsupported TAVIA resource type':
                    member, count, types = _unsupported_resource_diagnostic(data)
                    if count:
                        # Do not reclassify a rejected archive as safe. The
                        # canonical Assets validator remains authoritative.
                        label = f'{member} ({types})' if member else types
                        info = f'{label}; {count} unsupported file(s)'
                        message = ('Asset validation failed: unsupported TAVIA resource type. '
                                   f'Found {info}. Only image/audio/JSON resources are allowed. '
                                   'Remove or convert the file and rebuild the .tavia; '
                                   'for apps use .tavix instead.')
                        raise AssetImportError('TAVIA_VALIDATION_REJECTED', message)
                raise AssetImportError('TAVIA_VALIDATION_REJECTED', 'Asset validation failed: ' + reason)
            if reason == 'invalid TAVIA archive':
                raise AssetImportError('TAVIA_ARCHIVE_INVALID', 'File is not a valid .tavia ZIP archive')
            raise AssetImportError('TAVIA_VALIDATOR_FAILED',
                                   'Canonical validator failed; inspect the Assets checkout with tools/tavia.py inspect')
        meta = response.get('result')
        if not isinstance(meta, dict) or not all(isinstance(meta.get(k), str) for k in ('id','version')):
            raise AssetImportError('TAVIA_VALIDATOR_PROTOCOL', 'Canonical validator returned invalid pack metadata')
    meta['sha256'] = hashlib.sha256(data).hexdigest()
    meta['status'] = 'validated_local_draft'
    return meta
