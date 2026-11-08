"""Preference repository with user-centric convenience methods."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user_preference import UserPreference
from ..logging_config import get_logger
from .base_repository import BaseRepository

logger = get_logger(__name__)


class PreferenceRepository(BaseRepository[UserPreference]):
    """Async repository for :class:`UserPreference` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(UserPreference, session)

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    async def get_by_user_id(self, user_id: str) -> UserPreference | None:
        """Return the preference record for *user_id*, or ``None``."""
        stmt = select(UserPreference).where(UserPreference.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    async def create_default_preferences(self, user_id: str) -> UserPreference:
        """Insert a row of sensible defaults for *user_id*.

        If a preference row already exists for this user the existing row is
        returned unchanged (idempotent).
        """
        existing = await self.get_by_user_id(user_id)
        if existing is not None:
            return existing

        prefs = UserPreference(user_id=user_id)
        self._session.add(prefs)
        await self._session.flush()
        logger.info("default_preferences_created", user_id=user_id)
        return prefs  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Targeted updates
    # ------------------------------------------------------------------

    async def update_theme(self, user_id: str, theme: str) -> UserPreference | None:
        """Update the theme preference for *user_id*.

        Returns the updated record or ``None`` if no preference row exists.
        """
        prefs = await self.get_by_user_id(user_id)
        if prefs is None:
            return None

        prefs.theme = theme
        self._session.add(prefs)
        await self._session.flush()
        logger.info("theme_updated", user_id=user_id, theme=theme)
        return prefs

    async def update_accessibility(
        self, user_id: str, settings: dict[str, Any]
    ) -> UserPreference | None:
        """Patch one or more accessibility settings for *user_id*.

        Parameters
        ----------
        user_id:
            The owning user.
        settings:
            Mapping of ``UserPreference`` attribute name -> new value.
            Recognised keys include ``high_contrast``, ``reduced_motion``,
            ``font_size``, ``font_family``, ``dyslexia_font``, ``zoom_level``,
            ``line_spacing``, ``letter_spacing``, ``screen_reader_optimized``,
            ``keyboard_shortcut_profile``, ``color_blind_palette``.

        Returns
        -------
        UserPreference | None
            The updated record or ``None`` if no preference row exists.
        """
        prefs = await self.get_by_user_id(user_id)
        if prefs is None:
            return None

        for key, value in settings.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)

        self._session.add(prefs)
        await self._session.flush()
        logger.info("accessibility_updated", user_id=user_id, keys=list(settings.keys()))
        return prefs

    async def update_language(
        self, user_id: str, language: str
    ) -> UserPreference | None:
        """Update the language preference for *user_id*."""
        prefs = await self.get_by_user_id(user_id)
        if prefs is None:
            return None

        prefs.language = language
        self._session.add(prefs)
        await self._session.flush()
        logger.info("language_updated", user_id=user_id, language=language)
        return prefs
