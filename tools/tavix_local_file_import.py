"""TaviX optional local-file picker request validation; not a native picker or grant.

A manifest is a declaration, not proof of consent, host support, or access.
"""
from __future__ import annotations
import re

FEATURE = 'tavix.local-file-import/v1'
PERMISSION = 'files.local.import'
MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_CHUNK_BYTES = 64 * 1024
MAX_FILTERS = 16
EXTENSION = re.compile(r'^\.[a-z0-9]{1,12}$')
MIME = re.compile(r'^[a-z0-9][a-z0-9.+-]*/[a-z0-9][a-z0-9.+-]*$')


def validate_local_file_import(manifest: dict) -> dict | None:
    """Validate the optional *request*; never grant filesystem access.

    fileImports and files.local.import must be declared together. Missing both
    preserves existing packages. No glob, wildcard, path or broad directory API.
    """
    if not isinstance(manifest, dict):
        raise ValueError('Invalid TaviX manifest')
    permissions = manifest.get('permissions', [])
    if not isinstance(permissions, list) or any(not isinstance(p, str) for p in permissions):
        raise ValueError('Invalid manifest permissions')
    requested = PERMISSION in permissions
    has_field = 'fileImports' in manifest
    if requested != has_field:
        raise ValueError('fileImports and files.local.import must be declared together')
    if not requested:
        return None
    if 'ui.panel' not in permissions or permissions.count(PERMISSION) != 1:
        raise ValueError('Local file import requires ui.panel and unique permission')
    declaration = manifest['fileImports']
    if not isinstance(declaration, dict) or set(declaration) != {'extensions', 'mimeTypes', 'maxBytes'}:
        raise ValueError('Invalid fileImports fields')
    extensions, mime_types, max_bytes = (declaration[k] for k in ('extensions', 'mimeTypes', 'maxBytes'))
    for values, pattern, label in ((extensions, EXTENSION, 'extensions'), (mime_types, MIME, 'MIME types')):
        if not isinstance(values, list) or not 1 <= len(values) <= MAX_FILTERS or any(not isinstance(v, str) or not pattern.fullmatch(v) for v in values) or len(set(values)) != len(values):
            raise ValueError(f'Invalid fileImports {label}')
    if type(max_bytes) is not int or not 1 <= max_bytes <= MAX_FILE_BYTES:
        raise ValueError('Invalid fileImports maxBytes')
    return {'extensions': list(extensions), 'mimeTypes': list(mime_types), 'maxBytes': max_bytes}
