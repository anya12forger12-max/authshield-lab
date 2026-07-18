"""Preference management service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any


class IPreferenceService(ABC):
    """Interface for user preference management operations."""

    @abstractmethod
    async def get_preferences(self, user_id: str) -> Optional[dict]:
        """Retrieve all preferences for a user."""
        ...

    @abstractmethod
    async def update_preferences(self, user_id: str, data: dict[str, Any]) -> Optional[dict]:
        """Update user preferences with the given data."""
        ...

    @abstractmethod
    async def update_theme(self, user_id: str, theme: str, accent_color: str = "") -> bool:
        """Update the user's theme and optional accent colour."""
        ...

    @abstractmethod
    async def update_accessibility(self, user_id: str, settings: dict[str, Any]) -> bool:
        """Update accessibility settings for a user."""
        ...

    @abstractmethod
    async def update_language(self, user_id: str, language: str) -> bool:
        """Update the user's preferred language."""
        ...

    @abstractmethod
    async def reset_to_defaults(self, user_id: str) -> bool:
        """Reset all preferences to their default values."""
        ...

    @abstractmethod
    async def export_preferences(self, user_id: str) -> dict:
        """Export user preferences as a dictionary."""
        ...

    @abstractmethod
    async def import_preferences(self, user_id: str, data: dict[str, Any]) -> bool:
        """Import preferences from a dictionary."""
        ...
