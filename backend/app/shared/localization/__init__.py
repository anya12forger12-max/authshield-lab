"""Localization infrastructure for multi-language support."""

from .manager import LocalizationManager, get_localization, t
from .strings import STRINGS, SUPPORTED_LANGUAGES

__all__ = [
    "LocalizationManager",
    "STRINGS",
    "SUPPORTED_LANGUAGES",
    "get_localization",
    "t",
]
