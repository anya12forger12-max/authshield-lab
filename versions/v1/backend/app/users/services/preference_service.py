"""User preference management service implementation."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.exceptions import NotFoundError, ValidationError
from ...shared.logging_config import get_logger, log_audit_event
from ...shared.events.event_bus import EventBus, DomainEvent
from ...shared.models.user import User
from ...config.constants import MODULE_USERS
from ..domain.interfaces.preference_service import IPreferenceService
from ..domain.events.identity_events import PreferenceChangedEvent

logger = get_logger(MODULE_USERS)

DEFAULT_PREFERENCES: dict[str, Any] = {
    "theme": "dark",
    "accent_color": "",
    "language": "en",
    "timezone": "UTC",
    "accessibility": {
        "high_contrast": False,
        "large_text": False,
        "screen_reader": False,
        "reduced_motion": False,
        "keyboard_navigation": False,
    },
    "notifications": {
        "email_notifications": True,
        "security_alerts": True,
        "session_alerts": True,
        "login_notifications": False,
    },
}


class PreferenceService(IPreferenceService):
    """Concrete implementation of user preference management.

    Preferences are stored on the User model directly (denormalized) as
    well as in an optional UserPreference table when richer structure is
    needed.  This service operates on the User model columns for the
    core fields.

    Parameters
    ----------
    session_factory:
        Callable that returns an ``AsyncSession``.
    event_bus:
        In-process event bus for publishing domain events.
    """

    def __init__(self, session_factory: Any, event_bus: Optional[EventBus] = None) -> None:
        self._session_factory = session_factory
        self._event_bus = event_bus

    async def _get_session(self) -> AsyncSession:
        return await self._session_factory()

    async def _publish_event(self, event: DomainEvent) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def get_preferences(self, user_id: str) -> Optional[dict]:
        """Retrieve all preferences for a user."""
        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            return {
                "user_id": user.id,
                "theme": user.preferred_theme,
                "accent_color": "",
                "language": user.preferred_language,
                "timezone": user.timezone,
                "accessibility": dict(DEFAULT_PREFERENCES["accessibility"]),
                "notifications": dict(DEFAULT_PREFERENCES["notifications"]),
            }

    async def update_preferences(self, user_id: str, data: dict[str, Any]) -> Optional[dict]:
        """Update user preferences with the given data."""
        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            changed: list[str] = []

            if "theme" in data and data["theme"]:
                user.preferred_theme = data["theme"]
                changed.append("theme")

            if "language" in data and data["language"]:
                user.preferred_language = data["language"]
                changed.append("language")

            if "timezone" in data and data["timezone"]:
                user.timezone = data["timezone"]
                changed.append("timezone")

            await session.flush()

            if changed:
                event = PreferenceChangedEvent(
                    user_id=user_id,
                    preference_type=",".join(changed),
                    correlation_id=user_id,
                )
                await self._publish_event(event)

                log_audit_event(
                    "PREFERENCES_UPDATED",
                    user_id=user_id,
                    action="UPDATE",
                    resource=f"preferences:{user_id}",
                    logger=logger,
                )

            return await self.get_preferences(user_id)

    async def update_theme(self, user_id: str, theme: str, accent_color: str = "") -> bool:
        """Update the user's theme and optional accent colour."""
        valid_themes = {"dark", "light", "system", "high-contrast"}
        if theme not in valid_themes:
            raise ValidationError(
                f"Invalid theme '{theme}'. Must be one of: {', '.join(sorted(valid_themes))}"
            )

        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            user.preferred_theme = theme
            await session.flush()

            event = PreferenceChangedEvent(
                user_id=user_id,
                preference_type="theme",
                correlation_id=user_id,
                metadata={"theme": theme, "accent_color": accent_color},
            )
            await self._publish_event(event)

            log_audit_event(
                "THEME_UPDATED",
                user_id=user_id,
                action="UPDATE",
                resource=f"theme:{theme}",
                logger=logger,
            )

            return True

    async def update_accessibility(self, user_id: str, settings: dict[str, Any]) -> bool:
        """Update accessibility settings for a user."""
        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            # Validate accessibility keys
            valid_keys = {
                "high_contrast", "large_text", "screen_reader",
                "reduced_motion", "keyboard_navigation",
            }
            for key in settings:
                if key not in valid_keys:
                    raise ValidationError(f"Unknown accessibility setting: {key}")

            event = PreferenceChangedEvent(
                user_id=user_id,
                preference_type="accessibility",
                correlation_id=user_id,
                metadata=settings,
            )
            await self._publish_event(event)

            log_audit_event(
                "ACCESSIBILITY_UPDATED",
                user_id=user_id,
                action="UPDATE",
                resource=f"accessibility:{user_id}",
                logger=logger,
            )

            return True

    async def update_language(self, user_id: str, language: str) -> bool:
        """Update the user's preferred language."""
        if not language or len(language) > 10:
            raise ValidationError("Invalid language code.")

        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            user.preferred_language = language
            await session.flush()

            event = PreferenceChangedEvent(
                user_id=user_id,
                preference_type="language",
                correlation_id=user_id,
                metadata={"language": language},
            )
            await self._publish_event(event)

            return True

    async def reset_to_defaults(self, user_id: str) -> bool:
        """Reset all preferences to their default values."""
        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            user.preferred_theme = DEFAULT_PREFERENCES["theme"]
            user.preferred_language = DEFAULT_PREFERENCES["language"]
            user.timezone = DEFAULT_PREFERENCES["timezone"]
            await session.flush()

            event = PreferenceChangedEvent(
                user_id=user_id,
                preference_type="reset",
                correlation_id=user_id,
            )
            await self._publish_event(event)

            log_audit_event(
                "PREFERENCES_RESET",
                user_id=user_id,
                action="RESET",
                resource=f"preferences:{user_id}",
                logger=logger,
            )

            return True

    async def export_preferences(self, user_id: str) -> dict:
        """Export user preferences as a dictionary."""
        prefs = await self.get_preferences(user_id)
        if prefs is None:
            raise NotFoundError(f"User {user_id} not found.")
        return prefs

    async def import_preferences(self, user_id: str, data: dict[str, Any]) -> bool:
        """Import preferences from a dictionary."""
        allowed_keys = {"theme", "language", "timezone", "accent_color", "accessibility", "notifications"}
        filtered = {k: v for k, v in data.items() if k in allowed_keys}

        if not filtered:
            return False

        result = await self.update_preferences(user_id, filtered)
        return result is not None
