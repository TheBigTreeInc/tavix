"""TaviX v1 optional *requests* for Tavi Assets; never an authorization grant.

Keep this source validator aligned with contracts/tavix-asset-dependencies-v1.schema.json.
No host, entitlement, download or wallet state is read here.
"""
from __future__ import annotations
import re

PACK_ID = re.compile(r'^[a-z0-9][a-z0-9._-]{0,126}$')
CAPABILITY = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$')
VERSION = re.compile(r'^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$')
MAX_DEPENDENCIES = 16
MAX_CAPABILITIES_PER_PACK = 32
MAX_TOTAL_CAPABILITIES = 256
ASSET_PERMISSIONS = frozenset({'assets.read', 'assets.preferences.write'})
REGISTRY_ADMIN_PERMISSION = 'assets.registry.admin/v1'
PUBLISHABLE_PERMISSIONS = frozenset({'ui.panel', 'ui.toast', 'storage.private', REGISTRY_ADMIN_PERMISSION}) | ASSET_PERMISSIONS


def _semver(value: str):
    return tuple(int(part) for part in value.split('.'))


def validate_asset_dependencies(manifest: dict) -> list[dict]:
    """Validate requested asset dependencies and matching *requested* permissions.

    Returns normalized descriptions for tooling, not host-issued grants. A missing
    field is the legacy case. This function does not issue or approve access.
    """
    if not isinstance(manifest, dict):
        raise ValueError('Invalid extension manifest')
    permissions = manifest.get('permissions')
    # Historical package-only fixtures may omit permissions entirely; Tavi's
    # production repository validator still requires ui.panel. Do not make
    # the new optional asset feature retroactively invalidate those archives.
    if 'assetDependencies' not in manifest and permissions is None:
        return []
    if not isinstance(permissions, list) or any(not isinstance(p, str) for p in permissions):
        raise ValueError('Invalid extension permissions')
    if len(permissions) > 10 or len(set(permissions)) != len(permissions):
        raise ValueError('Invalid or duplicate extension permissions')
    if set(permissions) - PUBLISHABLE_PERMISSIONS:
        raise ValueError('Unsupported extension permissions')
    if 'ui.panel' not in permissions:
        raise ValueError('ui.panel permission required')
    if 'assetDependencies' not in manifest:
        if ASSET_PERMISSIONS.intersection(permissions):
            raise ValueError('Asset permissions require declared assetDependencies')
        return []
    raw = manifest['assetDependencies']
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_DEPENDENCIES:
        raise ValueError('assetDependencies must contain 1–16 packs')
    if 'assets.read' not in permissions:
        raise ValueError('assetDependencies require assets.read permission request')
    seen = set()
    all_caps = set()
    result = []
    customization_requested = False
    for dep in raw:
        if not isinstance(dep, dict) or set(dep) - {'packId','compatibility','capabilities','optional','requestCustomization'}:
            raise ValueError('Invalid asset dependency fields')
        if set(dep) & {'packId','compatibility','capabilities','optional'} != {'packId','compatibility','capabilities','optional'}:
            raise ValueError('Missing required asset dependency fields')
        pack_id = dep['packId']
        if not isinstance(pack_id, str) or not PACK_ID.fullmatch(pack_id) or pack_id in seen:
            raise ValueError('Invalid or duplicate asset packId')
        seen.add(pack_id)
        comp = dep['compatibility']
        if not isinstance(comp, dict) or set(comp) != {'min','maxExclusive'}:
            raise ValueError('Invalid asset compatibility range')
        minimum, maximum = comp['min'], comp['maxExclusive']
        if (not isinstance(minimum, str) or not isinstance(maximum, str)
                or not VERSION.fullmatch(minimum) or not VERSION.fullmatch(maximum)
                or _semver(minimum) >= _semver(maximum)):
            raise ValueError('Invalid asset compatibility range')
        caps = dep['capabilities']
        if (not isinstance(caps, list) or not 1 <= len(caps) <= MAX_CAPABILITIES_PER_PACK
                or any(not isinstance(cap, str) or not CAPABILITY.fullmatch(cap) for cap in caps)
                or len(set(caps)) != len(caps)):
            raise ValueError('Invalid asset capabilities')
        all_caps.update(caps)
        if len(all_caps) > MAX_TOTAL_CAPABILITIES:
            raise ValueError('Too many asset capabilities')
        if type(dep['optional']) is not bool or type(dep.get('requestCustomization', False)) is not bool:
            raise ValueError('Invalid asset optional/customization flag')
        customization_requested |= dep.get('requestCustomization', False)
        result.append({
            'packId': pack_id,
            'compatibility': {'min': minimum, 'maxExclusive': maximum},
            'capabilities': list(caps),
            'optional': dep['optional'],
            'requestCustomization': dep.get('requestCustomization', False),
        })
    if customization_requested != ('assets.preferences.write' in permissions):
        raise ValueError('Asset customization request and assets.preferences.write permission must agree')
    return result
