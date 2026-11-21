"""Local operator diagnostic journal: bounded, redacted, never an audit authority.

This is diagnostic data, not the LoopRD authoritative audit log. Events are written
outside the Git source tree and intentionally do not contain payloads or secrets.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import threading
import tempfile
from uuid import uuid4

MAX_EVENTS = 400
MAX_BYTES = 512 * 1024
LEVELS = frozenset(('info', 'warning', 'error'))
# Only these fixed, non-secret attributes may ever be stored in an event.
DETAIL_FIELDS = frozenset(('format', 'sizeBytes', 'packId', 'version', 'fileCount',
                           'resourceCount', 'objectCount', 'collectionCount',
                           'requestMethod', 'httpStatus'))
_SECRET = re.compile(
    r'(?i)(?:bearer\s+\S+|github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9_]+|'
    r'(?:token|password|secret|authorization|api[_ -]?key)\s*[:=]\s*\S+|'
    r'https?://[^/\s@]+@[^/\s]+)'
)
_PATH = re.compile(r'(?:[A-Za-z]:\\|/(?:home|Users|mnt|tmp|var)/)\S+')


def redact(value: str) -> str:
    """A defense-in-depth scrub; event callers must also use safe constant messages."""
    if not isinstance(value, str):
        return 'Event detail unavailable'
    s = _SECRET.sub('[redacted]', value)
    s = _PATH.sub('[local path omitted]', s)
    s = re.sub(r'[\r\n\t\x00-\x1f]', ' ', s)
    return s[:240]


class EventJournal:
    def __init__(self, private_root):
        self.root = Path(private_root).resolve()
        self.path = self.root / 'events.jsonl'
        self._lock = threading.RLock()

    def _events(self):
        try:
            # Do not read an unbounded file from a compromised/old local instance.
            with self.path.open('rb') as stream:
                if self.path.stat().st_size > MAX_BYTES * 8:
                    stream.seek(-MAX_BYTES * 8, os.SEEK_END)
                    stream.readline()  # discard incomplete leading line
                content = stream.read(MAX_BYTES * 8)
        except FileNotFoundError:
            return []
        result = []
        for line in content.splitlines()[-MAX_EVENTS:]:
            try:
                item = json.loads(line)
                if isinstance(item, dict) and item.get('schema') == 'tavix.event/v1':
                    result.append(item)
            except (ValueError, UnicodeDecodeError):
                continue
        return result[-MAX_EVENTS:]

    def record(self, level, action, code, message, details=None):
        if level not in LEVELS:
            raise ValueError('Unknown event level')
        if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,63}', action):
            raise ValueError('Invalid diagnostic action')
        if not re.fullmatch(r'[A-Z][A-Z0-9_]{0,63}', code):
            raise ValueError('Invalid diagnostic code')
        extra = {}
        for key, value in (details or {}).items():
            if key not in DETAIL_FIELDS:
                continue
            if isinstance(value, bool) or not isinstance(value, (str, int)):
                continue
            if isinstance(value, int):
                if 0 <= value <= 2**32: extra[key] = value
            else:
                extra[key] = redact(value)[:120]
        event = {'schema':'tavix.event/v1', 'id': uuid4().hex[:12],
                 'at':datetime.now(timezone.utc).isoformat(timespec='seconds'),
                 'level':level, 'action':action, 'code':code,
                 'message':redact(message), 'details':extra}
        with self._lock:
            existing = self._events()
            existing.append(event)
            existing = existing[-MAX_EVENTS:]
            while len(json.dumps(existing, ensure_ascii=False).encode('utf-8')) > MAX_BYTES and existing:
                existing.pop(0)
            self.root.mkdir(parents=True, mode=0o700, exist_ok=True)
            # Unique O_EXCL temporary file prevents following a pre-existing symlink.
            descriptor, temp_name = tempfile.mkstemp(prefix='.events-', suffix='.new', dir=self.root)
            temporary = Path(temp_name)
            try:
                with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as out:
                    for row in existing:
                        out.write(json.dumps(row, ensure_ascii=False, separators=(',',':')) + '\n')
                os.chmod(temporary, 0o600)
                os.replace(temporary, self.path)
            finally:
                temporary.unlink(missing_ok=True)
        return event

    def list(self, level='all', limit=MAX_EVENTS):
        if level != 'all' and level not in LEVELS:
            raise ValueError('Unknown event filter')
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_EVENTS:
            raise ValueError('Invalid event limit')
        with self._lock:
            results = self._events()
        total = len(results)
        if level != 'all': results = [item for item in results if item['level'] == level]
        return {'schema':'tavix.events/v1', 'events':list(reversed(results[-limit:])),
                'totalEvents':total,
                'retention':{'maxEvents':MAX_EVENTS, 'maxBytes':MAX_BYTES},
                'diagnosticOnly':True}
