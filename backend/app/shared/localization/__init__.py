"""Localization infrastructure for multi-language support."""

from .manager import LocalizationManager, get_localization, t
from .strings import STRINGS, SUPPORTED_LANGUAGES

__all__ = [
    "STRINGS",
    "SUPPORTED_LANGUAGES",
    "LocalizationManager",
    "get_localization",
    "t",
]
