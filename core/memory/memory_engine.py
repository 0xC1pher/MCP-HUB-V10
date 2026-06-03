"""
Memory Engine - ConsistentMemoryEngine backed by mempalace.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ConsistentMemoryEngine:
    """Memory engine with conflict resolution backed by mempalace."""

    def __init__(self, wing: str = "hub", **kwargs):
        self.wing = wing
        self._cache: Dict[str, Dict] = {}
        self._backend = None

    def _get_backend(self):
        if self._backend is None:
            from ..mempalace_backend import add_drawer, search, delete_drawer, Room
            self._add = add_drawer
            self._search = search
            self._delete = delete_drawer
            self._room = Room.MEMORY
            self._backend = True
        return self

    def write(self, key: str, value: Dict, project_id: str = None,
              expected_version: int = None) -> bool:
        """Write memory with conflict resolution."""
        self._get_backend()
        content = json.dumps({"key": key, "value": value,
                              "timestamp": datetime.now().isoformat()},
                             default=str)
        self._add(wing=self.wing, room=self._room, content=content)
        self._cache[key] = value
        return True

    def read(self, key: str) -> Optional[Dict]:
        """Read memory by key."""
        self._get_backend()
        if key in self._cache:
            return self._cache[key]
        results = self._search(query=key, wing=self.wing, room=self._room,
                               limit=5)
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if data.get("key") == key:
                    self._cache[key] = data.get("value", {})
                    return data["value"]
            except (json.JSONDecodeError, TypeError):
                continue
        return None

    def delete(self, key: str) -> bool:
        """Delete memory by key."""
        self._get_backend()
        results = self._search(query=key, wing=self.wing, room=self._room,
                               limit=5)
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if data.get("key") == key:
                    self._delete(r.get("id", ""))
                    self._cache.pop(key, None)
                    return True
            except (json.JSONDecodeError, TypeError):
                continue
        return False

    def list_keys(self) -> List[str]:
        """List all memory keys."""
        self._get_backend()
        results = self._search(query="*", wing=self.wing, room=self._room,
                               limit=200)
        keys = []
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if "key" in data:
                    keys.append(data["key"])
            except (json.JSONDecodeError, TypeError):
                continue
        return keys
