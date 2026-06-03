"""
Memory Module - Session & memory management backed by mempalace.
"""
from ..mempalace_backend import (
    MempalaceSession as Session,
    MempalaceSessionManager as SessionManager,
    MempalaceMemoryHandler,
    MempalaceEntityTracker as EntityTracker,
    MempalaceSkillsManager as SkillsManager,
)

# Enums for compatibility
from enum import Enum


class SessionType(Enum):
    FEATURE_IMPLEMENTATION = "feature"
    BUG_FIXING = "bugfix"
    CODE_REVIEW = "review"
    REFACTORING = "refactoring"
    GENERAL = "general"


class SessionStrategy(Enum):
    TRIMMING = "trimming"
    SUMMARIZING = "summarizing"


class TrimmingSession:
    """Compatibility wrapper for TrimmingSession."""
    pass


class SummarizingSession:
    """Compatibility wrapper for SummarizingSession."""
    pass


__all__ = [
    'Session', 'SessionManager', 'SessionType', 'SessionStrategy',
    'TrimmingSession', 'SummarizingSession',
    'MempalaceMemoryHandler', 'EntityTracker', 'SkillsManager',
]
