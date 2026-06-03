"""
Entity Tracker - Entity mention tracking backed by mempalace KG.
"""
import json
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class EntityMention:
    def __init__(self, entity_name: str, session_id: str,
                 turn_id: int, context: str, timestamp: str):
        self.entity_name = entity_name
        self.session_id = session_id
        self.turn_id = turn_id
        self.context = context
        self.timestamp = timestamp

    def to_dict(self) -> Dict:
        return {
            "entity_name": self.entity_name, "session_id": self.session_id,
            "turn_id": self.turn_id, "context": self.context,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EntityMention":
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})


class EntityTracker:
    """Entity tracker backed by mempalace KG + drawers."""

    def __init__(self, wing: str = "hub", code_index: Dict = None, **kwargs):
        self.wing = wing
        self.code_index = code_index or {}
        self.mentions: Dict[str, List[EntityMention]] = defaultdict(list)
        self.session_entities: Dict[str, Set[str]] = defaultdict(set)

    def set_code_index(self, code_index: Dict) -> None:
        self.code_index = code_index

    def extract_entities_from_text(self, text: str) -> List[str]:
        """Extract entity names from text."""
        entities = []
        for name in (list(self.code_index.get("functions", {}).keys()) +
                     list(self.code_index.get("classes", {}).keys())):
            short = name.split(".")[-1]
            if short in text or name in text:
                entities.append(name)
        return entities

    def record_mention(self, entity_name: str, session_id: str,
                       turn_id: int, context: str) -> None:
        """Record an entity mention."""
        mention = EntityMention(
            entity_name=entity_name, session_id=session_id,
            turn_id=turn_id, context=context[:500],
            timestamp=datetime.now().isoformat(),
        )
        self.mentions[entity_name].append(mention)
        self.session_entities[session_id].add(entity_name)
        # Store in KG
        from ..mempalace_backend import kg_add
        kg_add(subject=session_id, predicate="mentions", obj=entity_name)

    def record_turn(self, session_id: str, turn_id: int,
                    query: str, response: str) -> List[str]:
        """Extract and record entities from a conversation turn."""
        text = f"{query} {response}"
        entities = self.extract_entities_from_text(text)
        for ent in entities:
            self.record_mention(ent, session_id, turn_id, text[:500])
        return entities

    def get_entity_history(self, entity_name: str) -> List[EntityMention]:
        return self.mentions.get(entity_name, [])

    def get_sessions_for_entity(self, entity_name: str) -> List[str]:
        sessions = set()
        for m in self.mentions.get(entity_name, []):
            sessions.add(m.session_id)
        return list(sessions)

    def get_entities_for_session(self, session_id: str) -> List[str]:
        return list(self.session_entities.get(session_id, set()))

    def get_last_mention(self, entity_name: str) -> Optional[EntityMention]:
        mentions = self.mentions.get(entity_name, [])
        return mentions[-1] if mentions else None

    def get_related_entities(self, entity_name: str,
                             limit: int = 10) -> List[str]:
        sessions = set()
        for m in self.mentions.get(entity_name, []):
            sessions.add(m.session_id)
        related = set()
        for sid in sessions:
            for e in self.session_entities.get(sid, []):
                if e != entity_name:
                    related.add(e)
        return list(related)[:limit]

    def search_mentions(self, keyword: str) -> Dict[str, List[EntityMention]]:
        results = {}
        for name, mentions in self.mentions.items():
            if keyword.lower() in name.lower():
                results[name] = mentions
        return results

    def save(self) -> bool:
        """Save is handled by mempalace KG."""
        return True

    def load(self) -> bool:
        """Load is handled by mempalace KG."""
        return True

    def get_stats(self) -> Dict:
        return {
            "total_entities_tracked": len(self.mentions),
            "total_mentions": sum(len(v) for v in self.mentions.values()),
            "total_sessions": len(self.session_entities),
            "backend": "mempalace",
        }
