"""TaviX classification/v1: optional, validated manifest metadata.

This module defines only TaviX source/preview behavior. Tavi's trusted registry,
permissions and host inventory/launch calls remain Tavi-owned integrations.
"""
from __future__ import annotations

PRIMARY_TYPES = ('app', 'game')
MAX_CATEGORIES = 8
GAME_CATEGORIES = (
    'action', 'adventure', 'arcade', 'board', 'cards', 'casual', 'educational',
    'multiplayer', 'puzzle', 'racing', 'role-playing', 'simulation', 'solitaire',
    'sports', 'strategy', 'word',
)
APP_CATEGORIES = (
    'communication', 'creative', 'education', 'entertainment', 'finance',
    'productivity', 'social', 'tools', 'utility', 'wellness',
)


def resolve_classification(manifest: dict) -> dict:
    """Validate optional classification; legacy manifests default to app / [].

    Strictly reject unknown keys and mismatched controlled-vocabulary tags.
    No guesswork from a name, contribution, icon or any game-like content.
    """
    if not isinstance(manifest, dict):
        raise ValueError('TaviX manifest must be an object')
    if 'classification' not in manifest:
        return {'type': 'app', 'categories': []}
    c = manifest['classification']
    if not isinstance(c, dict) or not set(c).issubset({'type', 'categories'}):
        raise ValueError('Invalid TaviX classification fields')
    ptype = c.get('type')
    if not isinstance(ptype, str) or ptype not in PRIMARY_TYPES:
        raise ValueError('Unsupported TaviX classification type')
    categories = c.get('categories', [])
    if not isinstance(categories, list) or len(categories) > MAX_CATEGORIES:
        raise ValueError('Invalid TaviX categories')
    allowed = set(GAME_CATEGORIES if ptype == 'game' else APP_CATEGORIES)
    if any(not isinstance(x, str) or x not in allowed for x in categories) or len(categories) != len(set(categories)):
        raise ValueError('Unsupported or repeated TaviX category')
    return {'type': ptype, 'categories': list(categories)}
