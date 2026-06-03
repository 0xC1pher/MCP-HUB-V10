"""
Event Store - PersistentEventStore backed by mempalace KG + drawers.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PersistentEventStore:
    """Event store backed by mempalace. No more SQLite database."""

    def __init__(self, db_path: str = None, wing: str = "hub"):
        self.wing = wing
        self._backend = None

    def _get_backend(self):
        if self._backend is None:
            from ..mempalace_backend import add_drawer, search, kg_add, kg_query, Room
            self._add = add_drawer
            self._search = search
            self._kg_add = kg_add
            self._kg_query = kg_query
            self._room = Room.EVENTS
            self._backend = True
        return self

    async def append(self, project_id: str, mcp_source: str,
                     event_type: str, data: Dict, version: int = None) -> None:
        """Append an event to mempalace."""
        self._get_backend()
        event = {
            "project_id": project_id,
            "mcp_source": mcp_source,
            "event_type": event_type,
            "data": data,
            "version": version or int(datetime.now().timestamp()),
            "timestamp": datetime.now().isoformat(),
        }
        self._add(wing=self.wing, room=self._room,
                  content=json.dumps(event, default=str),
                  source_file=f"event:{event_type}")
        # Also add to KG for temporal queries
        self._kg_add(subject=project_id, predicate="has_event",
                     obj=event_type, valid_from=event["timestamp"][:10])

    async def query(self, project_id: str = None,
                    event_type: str = None, limit: int = 50) -> List[Dict]:
        """Query events."""
        self._get_backend()
        query = f"{project_id or ''} {event_type or ''}".strip()
        results = self._search(query=query or "event", wing=self.wing,
                               room=self._room, limit=limit)
        events = []
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if project_id and data.get("project_id") != project_id:
                    continue
                if event_type and data.get("event_type") != event_type:
                    continue
                events.append(data)
            except (json.JSONDecodeError, TypeError):
                continue
        return events

    async def get_version(self, project_id: str) -> int:
        """Get latest version for project."""
        events = await self.query(project_id=project_id, limit=1)
        if events:
            return events[-1].get("version", 0)
        return 0

    async def get_state(self, project_id: str) -> Dict:
        """Reconstruct project state from events."""
        events = await self.query(project_id=project_id, limit=1000)
        state = {}
        for event in events:
            event_type = event.get("event_type", "")
            data = event.get("data", {})
            if event_type == "state_update":
                state.update(data)
            elif event_type == "feature_added":
                state[f"feature:{data.get('name', '')}"] = data
        return state
