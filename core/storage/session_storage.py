"""
SessionStorage - Replaces JSONL session storage with mempalace drawers.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class SessionStorage:
    """Session storage backed by mempalace. Same API, no JSONL files."""

    def __init__(self, storage_dir: str = "data/sessions",
                 retention_days: int = 30, wing: str = "hub"):
        self.wing = wing
        self.retention_days = retention_days
        self._backend = None

    def _get_backend(self):
        if self._backend is None:
            from ..mempalace_backend import MempalaceSessionManager
            self._backend = MempalaceSessionManager(wing=self.wing)
        return self._backend

    async def save_turn(self, session_id: str, turn_data: Dict) -> None:
        """Save a turn to mempalace."""
        backend = self._get_backend()
        session = backend.create_session(session_id)
        session.add_turn(
            query=turn_data.get("query", ""),
            response=turn_data.get("response", ""),
            metadata=turn_data,
        )

    async def load_session(self, session_id: str) -> List[Dict]:
        """Load session turns from mempalace."""
        backend = self._get_backend()
        session = backend.load_session(session_id)
        if session:
            return session.turns
        return []

    async def save_metadata(self, session_id: str, metadata: Dict) -> None:
        """Save session metadata to mempalace."""
        from ..mempalace_backend import add_drawer
        add_drawer(wing=self.wing, room=f"session_meta_{session_id}",
                   content=json.dumps(metadata, default=str))

    async def load_metadata(self, session_id: str) -> Optional[Dict]:
        """Load session metadata from mempalace."""
        from ..mempalace_backend import search
        results = search(query=session_id, wing=self.wing,
                         room=f"session_meta_{session_id}", limit=1)
        if results:
            try:
                return json.loads(results[0].get("content", "{}"))
            except (json.JSONDecodeError, TypeError):
                pass
        return None

    async def list_sessions(self) -> List[str]:
        """List all session IDs."""
        backend = self._get_backend()
        return backend.list_sessions()

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        backend = self._get_backend()
        return backend.delete_session(session_id)

    async def cleanup_old_sessions(self) -> int:
        """No-op: mempalace manages retention internally."""
        return 0

    async def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get session summary."""
        backend = self._get_backend()
        return backend.get_session_summary(session_id)
