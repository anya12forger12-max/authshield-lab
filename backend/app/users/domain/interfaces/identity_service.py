"""Identity service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any

from ..entities.user_profile import UserProfile


class IIdentityService(ABC):
    """Interface for user identity and profile management operations."""

    @abstractmethod
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve a user profile by user ID."""
        ...

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        """Retrieve a user profile by username."""
        ...

    @abstractmethod
    async def update_profile(self, user_id: str, data: dict[str, Any]) -> Optional[UserProfile]:
        """Update a user's profile fields."""
        ...

    @abstractmethod
    async def delete_user(self, user_id: str, soft: bool = True) -> bool:
        """Delete a user (soft or hard)."""
        ...

    @abstractmethod
    async def search_users(
        self,
        query: str,
        filters: Optional[dict] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Search users by query string with optional filters."""
        ...

    @abstractmethod
    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """List users with pagination and optional role/status filters."""
        ...

    @abstractmethod
    async def update_user_status(self, user_id: str, status: str, reason: str = "") -> bool:
        """Update a user's account status."""
        ...

    @abstractmethod
    async def get_user_count(self) -> dict[str, int]:
        """Return user counts grouped by status."""
        ...
