"""Session management service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any


class ISessionManagementService(ABC):
    """Interface for advanced session management operations."""

    @abstractmethod
    async def get_current_session(self, session_id: str) -> Optional[dict]:
        """Retrieve full details for a single session."""
        ...

    @abstractmethod
    async def get_user_active_sessions(self, user_id: str) -> list[dict]:
        """Return all active sessions for a user."""
        ...

    @abstractmethod
    async def get_all_user_sessions(
        self, user_id: str, include_expired: bool = False
    ) -> list[dict]:
        """Return all sessions for a user, optionally including expired ones."""
        ...

    @abstractmethod
    async def terminate_session(self, session_id: str, reason: str = "") -> bool:
        """Terminate a single session by ID."""
        ...

    @abstractmethod
    async def terminate_all_sessions(self, user_id: str, reason: str = "") -> int:
        """Terminate all sessions for a user. Return count terminated."""
        ...

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired sessions. Return count removed."""
        ...

    @abstractmethod
    async def get_session_stats(self, user_id: Optional[str] = None) -> dict:
        """Return session statistics, optionally filtered by user."""
        ...

    @abstractmethod
    async def search_sessions(
        self,
        filters: Optional[dict] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Search sessions with filters and pagination."""
        ...
