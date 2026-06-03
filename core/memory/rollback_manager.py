"""
Rollback Manager - PersistentRollbackManager backed by mempalace drawers.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PersistentRollbackManager:
    """Rollback manager backed by mempalace. No more JSON checkpoint files."""

    def __init__(self, wing: str = "hub", max_checkpoints: int = 10, **kwargs):
        self.wing = wing
        self.max_checkpoints = max_checkpoints
        self._backend = None

    def _get_backend(self):
        if self._backend is None:
            from ..mempalace_backend import add_drawer, search, delete_drawer, Room
            self._add = add_drawer
            self._search = search
            self._delete = delete_drawer
            self._room = Room.CHECKPOINTS
            self._backend = True
        return self

    def create_checkpoint(self, project_id: str, version: int,
                          state: Dict, description: str = "") -> str:
        """Create a checkpoint in mempalace."""
        self._get_backend()
        checkpoint = {
            "id": f"cp_{project_id}_{version}",
            "project_id": project_id,
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "state": state,
            "description": description,
        }
        self._add(wing=self.wing, room=self._room,
                  content=json.dumps(checkpoint, default=str),
                  source_file=f"checkpoint:{project_id}")
        self._cleanup_checkpoints(project_id)
        return checkpoint["id"]

    def rollback_to_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Rollback to a specific checkpoint."""
        self._get_backend()
        results = self._search(query=checkpoint_id, wing=self.wing,
                               room=self._room, limit=5)
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if data.get("id") == checkpoint_id:
                    return data.get("state", {})
            except (json.JSONDecodeError, TypeError):
                continue
        return None

    def get_latest_checkpoint(self, project_id: str) -> Optional[Dict]:
        """Get latest checkpoint for a project."""
        self._get_backend()
        results = self._search(query=project_id, wing=self.wing,
                               room=self._room, limit=10)
        checkpoints = []
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if data.get("project_id") == project_id:
                    checkpoints.append(data)
            except (json.JSONDecodeError, TypeError):
                continue
        if checkpoints:
            checkpoints.sort(key=lambda c: c.get("version", 0), reverse=True)
            return checkpoints[0]
        return None

    def list_checkpoints(self, project_id: str) -> List[Dict]:
        """List checkpoints for a project."""
        self._get_backend()
        results = self._search(query=project_id, wing=self.wing,
                               room=self._room, limit=100)
        checkpoints = []
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if data.get("project_id") == project_id:
                    checkpoints.append({
                        "id": data.get("id"),
                        "version": data.get("version"),
                        "timestamp": data.get("timestamp"),
                        "description": data.get("description"),
                    })
            except (json.JSONDecodeError, TypeError):
                continue
        return sorted(checkpoints, key=lambda c: c.get("version", 0))

    def _cleanup_checkpoints(self, project_id: str) -> None:
        """Keep only max_checkpoints per project."""
        cps = self.list_checkpoints(project_id)
        if len(cps) > self.max_checkpoints:
            for cp in cps[:-self.max_checkpoints]:
                results = self._search(query=cp["id"], wing=self.wing,
                                       room=self._room, limit=5)
                for r in results:
                    if cp["id"] in r.get("content", ""):
                        self._delete(r.get("id", ""))
                        break
