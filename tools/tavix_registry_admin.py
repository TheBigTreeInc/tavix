"""TaviX request-only registry admin capability. NEVER issues runtime grants."""
from __future__ import annotations

REGISTRY_ADMIN_FEATURE = 'assets.registry.admin/v1'


def validate_registry_admin_request(manifest: dict) -> bool:
    """Return whether an app requests the privileged feature, not whether it is approved."""
    if not isinstance(manifest, dict):
        raise ValueError('Invalid TaviX manifest')
    permissions = manifest.get('permissions', [])
    if not isinstance(permissions, list) or any(not isinstance(p, str) for p in permissions):
        raise ValueError('Invalid manifest permissions')
    requested = REGISTRY_ADMIN_FEATURE in permissions
    if requested and ('ui.panel' not in permissions or permissions.count(REGISTRY_ADMIN_FEATURE) != 1):
        raise ValueError('Registry administration request requires ui.panel and unique permission')
    return requested
