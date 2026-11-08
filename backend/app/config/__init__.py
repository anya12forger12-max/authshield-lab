"""AuthShield Lab - Configuration Module.

This module provides centralized configuration management for the application.
All settings are loaded from environment variables with sensible defaults.
"""

from app.config.settings import get_settings

settings = get_settings

__all__ = ["settings"]
