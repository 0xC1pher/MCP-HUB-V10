"""
Session Manager - Multi-session coordination backed by mempalace.
"""
from typing import Dict, List, Optional
from enum import Enum
import logging
from datetime import datetime

from ..mempalace_backend import (
    MempalaceSession,
    MempalaceSessionManager,
)

logger = logging.getLogger(__name__)

SessionType = Enum('SessionType', [
    'FEATURE_IMPLEMENTATION', 'BUG_FIXING', 'CODE_REVIEW',
    'REFACTORING', 'GENERAL'
])

SessionStrategy = Enum('SessionStrategy', ['TRIMMING', 'SUMMARIZING'])


class SessionManager:
    """Session manager backed by mempalace."""

    def __init__(self, storage=None, default_strategy=None,
                 auto_save: bool = True, wing: str = "hub", **kwargs):
        self.wing = wing
        self.default_strategy = default_strategy or SessionStrategy.TRIMMING
        self.auto_save = auto_save
        self._backend = MempalaceSessionManager(wing=wing)

    def create_session(self, session_id: str, session_type=None,
                       strategy=None) -> MempalaceSession:
        strat = strategy.value if hasattr(strategy, 'value') else (strategy or "trimming")
        return self._backend.create_session(session_id, strategy=strat)

    def load_session(self, session_id: str) -> Optional[MempalaceSession]:
        return self._backend.load_session(session_id)

    def add_turn_to_session(self, session_id: str, query: str,
                            response: str, **kwargs) -> None:
        self._backend.add_turn_to_session(session_id, query, response, **kwargs)

    def list_sessions(self) -> List[str]:
        return self._backend.list_sessions()

    def delete_session(self, session_id: str) -> bool:
        return self._backend.delete_session(session_id)

    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        return self._backend.get_session_summary(session_id)
