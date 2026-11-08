"""Pure TaviX host-grant *shape/subset* checker; NEVER grants access.

Only a trusted Tavi host may produce the `grant` and verified manifest digest.
The host must still check session, approvals, entitlements, pack versions and
revocation on every request. This helper is not an authorization engine.
"""
from __future__ import annotations
import re
from .tavix_asset_dependencies import (
    PACK_ID, CAPABILITY, VERSION, validate_asset_dependencies,
)

SHA256 = re.compile(r'^[a-f0-9]{64}$')
EXTENSION_ID = re.compile(r'^[a-z][a-z0-9]*(?:[.-][a-z0-9]+){2,}$')


def check_host_grant_subset(manifest: dict, verified_manifest_sha256: str, grant: dict) -> bool:
    """Check host-only projection is a subset of manifest requests.

    Return True for a well-formed projection, including an empty grant list.
    Never treat True as permission approval or proof of pack ownership.
    """
    dependencies = validate_asset_dependencies(manifest)
    if not isinstance(verified_manifest_sha256, str) or not SHA256.fullmatch(verified_manifest_sha256):
        raise ValueError('Host must supply verified manifest digest')
    if not isinstance(grant, dict) or set(grant) != {
        'schema','extensionId','extensionVersion','manifestSha256','scope','grants'
    }:
        raise ValueError('Invalid host asset grant projection')
    if (grant['schema'] != 'tavix.asset-grants/v1' or grant['scope'] != 'host-session'
            or grant['extensionId'] != manifest.get('id')
            or grant['extensionVersion'] != manifest.get('version')
            or not isinstance(grant['extensionId'], str)
            or not EXTENSION_ID.fullmatch(grant['extensionId'])
            or len(grant['extensionId']) > 120
            or not isinstance(grant['extensionVersion'], str)
            or not VERSION.fullmatch(grant['extensionVersion'])
            or grant['manifestSha256'] != verified_manifest_sha256):
        raise ValueError('Asset grant identity, revision or scope mismatch')
    approved = grant['grants']
    if not isinstance(approved, list) or len(approved) > 16:
        raise ValueError('Invalid host grant list')
    requested = {dep['packId']: dep for dep in dependencies}
    seen = set()
    for item in approved:
        if not isinstance(item, dict) or set(item) != {'packId','capabilities','canCustomize'}:
            raise ValueError('Invalid per-pack host grant')
        pack = item['packId']
        if not isinstance(pack, str) or not PACK_ID.fullmatch(pack) or pack in seen or pack not in requested:
            raise ValueError('Host granted undeclared or duplicate pack')
        seen.add(pack)
        caps = item['capabilities']
        if (not isinstance(caps, list) or not 1 <= len(caps) <= 32
                or any(not isinstance(c, str) or not CAPABILITY.fullmatch(c) for c in caps)
                or len(set(caps)) != len(caps) or not set(caps).issubset(requested[pack]['capabilities'])):
            raise ValueError('Host granted undeclared asset capability')
        if type(item['canCustomize']) is not bool:
            raise ValueError('Invalid host customization flag')
        if item['canCustomize'] and (not requested[pack]['requestCustomization']
                                     or 'assets.preferences.write' not in manifest['permissions']):
            raise ValueError('Host granted undeclared asset customization')
    return True
