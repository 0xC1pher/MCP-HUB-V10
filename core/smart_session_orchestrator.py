"""
Smart Session Orchestrator - Session lifecycle backed by mempalace drawers.
No more JSON state files in data/smart_sessions/.
"""
import os
import re
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SmartSessionOrchestrator:
    """Smart session orchestrator backed by mempalace."""

    def __init__(self, wing: str = "hub", server=None, **kwargs):
        self.wing = wing
        self.server = server
        self._state: Dict = {
            "project_sessions": {},
            "indexed_projects": {},
            "statistics": {"sessions_created": 0, "sessions_reused": 0,
                           "auto_indexes": 0},
        }
        self._backend = None

    def _get_backend(self):
        if self._backend is None:
            from .mempalace_backend import add_drawer, search, Room
            self._add = add_drawer
            self._search = search
            self._room = Room.CONTEXT
            self._backend = True
        return self

    def _load_state(self) -> Dict:
        """Load orchestrator state from mempalace."""
        self._get_backend()
        results = self._search(query="orchestrator_state", wing=self.wing,
                               room=self._room, limit=1)
        if results:
            try:
                self._state = json.loads(results[0].get("content", "{}"))
            except (json.JSONDecodeError, TypeError):
                pass
        return self._state

    def _save_state(self) -> None:
        """Save orchestrator state to mempalace."""
        self._get_backend()
        self._add(wing=self.wing, room=self._room,
                  content=json.dumps(self._state, default=str),
                  source_file="orchestrator_state")

    def _get_project_hash(self, project_path: str) -> str:
        return hashlib.md5(project_path.encode()).hexdigest()[:12]

    async def smart_initialize(self, project_path: str, context: str = None,
                               force_new_session: bool = False) -> Dict:
        """Initialize or reuse a session for a project."""
        self._load_state()
        project_hash = self._get_project_hash(project_path)
        existing = self._state["project_sessions"].get(project_hash)

        if existing and not force_new_session:
            self._state["statistics"]["sessions_reused"] += 1
            self._save_state()
            return {
                "session_id": existing["session_id"],
                "reused": True,
                "project_path": project_path,
            }

        # Create new session
        session_id = f"smart_{project_hash}_{int(datetime.now().timestamp())}"
        session_data = {
            "session_id": session_id,
            "project_path": project_path,
            "session_type": "feature",
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
        }
        self._state["project_sessions"][project_hash] = session_data
        self._state["statistics"]["sessions_created"] += 1
        self._save_state()

        return {
            "session_id": session_id,
            "reused": False,
            "project_path": project_path,
        }

    async def smart_query(self, query: str, project_path: str = None,
                          auto_session: bool = True) -> Dict:
        """Smart query with automatic session management."""
        if auto_session and project_path:
            init_result = await self.smart_initialize(project_path)
            session_id = init_result["session_id"]
        else:
            session_id = None

        # Delegate to server if available
        if self.server:
            args = {"query": query, "top_k": 5}
            if session_id:
                args["session_id"] = session_id
            try:
                result = self.server._handle_tools_call({
                    "name": "get_context", "arguments": args
                })
                return {"session_id": session_id, "result": result}
            except Exception as e:
                logger.error("Smart query failed", error=str(e))

        return {"session_id": session_id, "query": query}

    def get_project_session(self, project_path: str) -> Optional[str]:
        """Get session ID for a project."""
        self._load_state()
        project_hash = self._get_project_hash(project_path)
        session = self._state["project_sessions"].get(project_hash)
        return session["session_id"] if session else None

    def get_statistics(self) -> Dict:
        """Get orchestrator statistics."""
        self._load_state()
        return self._state.get("statistics", {})

    def get_all_project_sessions(self) -> List[Dict]:
        """Get all project sessions."""
        self._load_state()
        return list(self._state.get("project_sessions", {}).values())
