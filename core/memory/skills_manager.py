"""
Skills Manager - Knowledge skills backed by mempalace drawers.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SkillsManager:
    """Skills manager backed by mempalace drawers."""

    def __init__(self, config: Dict = None, vector_engine=None,
                 token_manager=None, wing: str = "hub"):
        self.wing = wing
        self.vector_engine = vector_engine
        self.token_manager = token_manager
        self.skills_cache: Dict[str, Dict] = {}

    def create_skill(self, skill_id: str, content: str,
                     description: str = "") -> str:
        """Create a skill in mempalace."""
        from .mempalace_backend import add_drawer, Room
        data = json.dumps({
            "skill_id": skill_id, "description": description,
            "content": content, "created_at": datetime.now().isoformat(),
        }, default=str)
        add_drawer(wing=self.wing, room=Room.SKILLS,
                   content=data, added_by="skills_tool")
        self.skills_cache[skill_id] = {"description": description}
        return f"Skill created: {skill_id}"

    def search_skills(self, query: str) -> List[Dict]:
        """Search skills via mempalace."""
        from .mempalace_backend import search, Room
        results = search(query=query, wing=self.wing, room=Room.SKILLS,
                         limit=10)
        skills = []
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if "skill_id" in data:
                    skills.append(data)
            except (json.JSONDecodeError, TypeError):
                continue
        return skills

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """Get a specific skill."""
        skills = self.search_skills(skill_id)
        for s in skills:
            if s.get("skill_id") == skill_id:
                return s
        return None

    def list_skills(self) -> List[str]:
        """List all skill IDs."""
        from .mempalace_backend import list_drawers, Room
        drawers = list_drawers(wing=self.wing, room=Room.SKILLS, limit=200)
        ids = []
        for d in drawers:
            try:
                data = json.loads(d.get("content", "{}"))
                if "skill_id" in data:
                    ids.append(data["skill_id"])
            except (json.JSONDecodeError, TypeError):
                continue
        return ids

    def delete_skill(self, skill_id: str) -> bool:
        """Delete a skill."""
        from .mempalace_backend import search, delete_drawer, Room
        results = search(query=skill_id, wing=self.wing, room=Room.SKILLS,
                         limit=5)
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if data.get("skill_id") == skill_id:
                    delete_drawer(r.get("id", ""))
                    self.skills_cache.pop(skill_id, None)
                    return True
            except (json.JSONDecodeError, TypeError):
                continue
        return False

    def get_stats(self) -> Dict:
        return {
            "total_skills": len(self.skills_cache),
            "backend": "mempalace",
        }
