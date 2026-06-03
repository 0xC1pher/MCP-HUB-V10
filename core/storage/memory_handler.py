"""
MemoryHandler - Replaces file-based memory with mempalace drawers.
"""
import json
from typing import Dict, List, Optional


class MemoryHandler:
    """Memory CRUD backed by mempalace. No more text files in data/memories/."""

    def __init__(self, config: Dict = None, token_manager=None, wing: str = "hub"):
        self.wing = wing
        self.token_manager = token_manager
        self._backend = None

    def _get_backend(self):
        if self._backend is None:
            from ..mempalace_backend import MempalaceMemoryHandler
            self._backend = MempalaceMemoryHandler(wing=self.wing)
        return self._backend

    def create(self, file_path: str, content: str,
               session_id: str = None) -> str:
        backend = self._get_backend()
        return backend.create(file_path, content, session_id)

    def read(self, file_path: str, session_id: str = None) -> str:
        backend = self._get_backend()
        return backend.read(file_path, session_id)

    def read_optimized(self, file_path: str, max_tokens: int = 2000,
                       session_id: str = None) -> str:
        text = self.read(file_path, session_id)
        if self.token_manager and len(text) > max_tokens * 4:
            return text[:max_tokens * 4]
        return text

    def update(self, file_path: str, content: str,
               session_id: str = None) -> str:
        self.delete(file_path, session_id)
        return self.create(file_path, content, session_id)

    def delete(self, file_path: str, session_id: str = None) -> str:
        backend = self._get_backend()
        return backend.delete(file_path, session_id)

    def list_memories(self, session_id: str = None) -> List[str]:
        backend = self._get_backend()
        return backend.list_memories(session_id)
