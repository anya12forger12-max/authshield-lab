"""Internationalisation / localization manager."""

from __future__ import annotations

import logging
from typing import Any, Optional

from .strings import STRINGS

logger = logging.getLogger(__name__)


class LocalizationManager:
    """Manages internationalization and string translation.

    The manager holds an in-memory copy of all translation strings and
    exposes a ``t()`` method that resolves a dotted key to the appropriate
    language string, falling back to the default language when a translation
    is missing.
    """

    def __init__(self, default_language: str = "en") -> None:
        self._default_language = default_language
        self._current_language = default_language
        self._strings: dict[str, dict[str, str]] = STRINGS
        self._fallback_language = "en"

    def set_language(self, language: str) -> None:
        """Set the active language for subsequent ``t()`` calls.

        Parameters
        ----------
        language:
            ISO 639-1 language code (e.g. ``"en"``).

        Raises
        ------
        KeyError
            If *language* is not present in the translation catalogue.
        """
        if language not in self._strings:
            available = ", ".join(sorted(self._strings.keys()))
            raise KeyError(
                f"Language '{language}' is not available. "
                f"Available languages: {available}"
            )
        self._current_language = language

    def get_language(self) -> str:
        """Return the currently active language code."""
        return self._current_language

    def t(self, key: str, **kwargs: Any) -> str:
        """Translate *key* using the current language.

        If the key is missing for the current language the fallback language
        (``en``) is tried.  If ``kwargs`` are supplied they are interpolated
        into the translated string using :meth:`str.format_map`.

        Parameters
        ----------
        key:
            Dotted translation key (e.g. ``"auth.login.success"``).
        **kwargs:
            Named substitution values for ``{placeholder}`` tokens in the
            string.

        Returns
        -------
        str
            The translated (and interpolated) string.  Returns the raw key
            itself if no translation is found in any language.
        """
        translated = self._resolve(key, self._current_language)
        if translated is None:
            translated = self._resolve(key, self._fallback_language)
        if translated is None:
            logger.warning("Missing translation key: %s", key)
            return key
        if kwargs:
            try:
                return translated.format_map(kwargs)
            except (KeyError, IndexError):
                logger.warning(
                    "Failed to interpolate kwargs for key '%s': %s", key, kwargs
                )
                return translated
        return translated

    def _resolve(self, key: str, language: str) -> Optional[str]:
        """Return the raw string for *key* under *language*, or ``None``."""
        lang_strings = self._strings.get(language)
        if lang_strings is None:
            return None
        return lang_strings.get(key)

    def get_available_languages(self) -> list[str]:
        """Return a sorted list of language codes that have translations."""
        return sorted(self._strings.keys())

    def has_translation(self, key: str, language: Optional[str] = None) -> bool:
        """Check whether a translation exists for *key*.

        Parameters
        ----------
        key:
            Dotted translation key.
        language:
            Language to check.  Defaults to the current language.
        """
        lang = language or self._current_language
        lang_strings = self._strings.get(lang)
        if lang_strings is None:
            return False
        return key in lang_strings

    def get_missing_keys(self, language: str) -> list[str]:
        """Return translation keys present in the default language but absent in *language*.

        Parameters
        ----------
        language:
            The language code to compare against the default language.
        """
        default_keys = set(self._strings.get(self._default_language, {}).keys())
        lang_keys = set(self._strings.get(language, {}).keys())
        return sorted(default_keys - lang_keys)


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_localization_manager: Optional[LocalizationManager] = None


def get_localization() -> LocalizationManager:
    """Return the global :class:`LocalizationManager`, creating it lazily."""
    global _localization_manager  # noqa: PLW0603
    if _localization_manager is None:
        _localization_manager = LocalizationManager()
    return _localization_manager


def t(key: str, **kwargs: Any) -> str:
    """Convenience shortcut for ``get_localization().t(key, **kwargs)``."""
    return get_localization().t(key, **kwargs)
