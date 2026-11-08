"""Repository interfaces for the authentication domain."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IUserRepository(ABC):
    """Interface for user data persistence."""

    @abstractmethod
    async def create(self, user_data: dict[str, Any]) -> Any:
        """Create a new user record."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Any | None:
        """Retrieve a user by their unique ID."""
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Any | None:
        """Retrieve a user by username (case-insensitive)."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Any | None:
        """Retrieve a user by email address."""
        ...

    @abstractmethod
    async def update(self, user_id: str, data: dict[str, Any]) -> Any | None:
        """Update an existing user record. Returns the updated user or None."""
        ...

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Soft-delete a user. Returns True on success."""
        ...

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Return True if a user with the given username exists."""
        ...

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Return True if a user with the given email exists."""
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        filters: dict | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Search users by query string with pagination.

        Returns a dict with ``items``, ``total``, ``page``, ``per_page``, ``pages``.
        """
        ...


class ISessionRepository(ABC):
    """Interface for session data persistence."""

    @abstractmethod
    async def create(self, session_data: dict[str, Any]) -> Any:
        """Create a new session record."""
        ...

    @abstractmethod
    async def get_by_id(self, session_id: str) -> Any | None:
        """Retrieve a session by its ID."""
        ...

    @abstractmethod
    async def get_active_by_user(self, user_id: str) -> list[Any]:
        """Return all active sessions for a user."""
        ...

    @abstractmethod
    async def update(self, session_id: str, data: dict[str, Any]) -> Any | None:
        """Update an existing session record."""
        ...

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Delete a session. Returns True on success."""
        ...

    @abstractmethod
    async def delete_expired(self) -> int:
        """Delete all expired sessions and return the count removed."""
        ...

    @abstractmethod
    async def delete_all_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user. Returns the count removed."""
        ...


class IAuditRepository(ABC):
    """Interface for audit log persistence."""

    @abstractmethod
    async def create(self, audit_data: dict[str, Any]) -> Any:
        """Create a new audit log entry."""
        ...

    @abstractmethod
    async def get_by_id(self, audit_id: str) -> Any | None:
        """Retrieve an audit entry by ID."""
        ...

    @abstractmethod
    async def get_by_user(
        self, user_id: str, page: int = 1, per_page: int = 50
    ) -> dict:
        """Return paginated audit entries for a user."""
        ...

    @abstractmethod
    async def search(
        self, filters: dict | None = None, page: int = 1, per_page: int = 50
    ) -> dict:
        """Search audit entries with filters and pagination."""
        ...
