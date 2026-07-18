"""Application configuration using Pydantic Settings."""

from __future__ import annotations

import secrets
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment profiles."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    EDUCATION = "education"
    DEMO = "demo"


class LogLevel(str, Enum):
    """Supported log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ThemeName(str, Enum):
    """Available UI themes."""

    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    SOLARIZED = "solarized"
    MONOKAI = "monokai"


class ApplicationConfig(BaseSettings):
    """Core application settings."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    name: str = "AuthShieldLab"
    version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    log_level: LogLevel = LogLevel.DEBUG

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        return self.environment == Environment.TESTING

    @property
    def is_education(self) -> bool:
        return self.environment == Environment.EDUCATION

    @property
    def is_demo(self) -> bool:
        return self.environment == Environment.DEMO


class SecurityConfig(BaseSettings):
    """Security-related settings."""

    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = ""
    token_expiry_minutes: int = 30
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    session_timeout_minutes: int = 60
    bcrypt_rounds: int = 12
    argon2_time_cost: int = 3
    argon2_memory_cost: int = 65536
    argon2_parallelism: int = 4

    @model_validator(mode="after")
    def _ensure_secret_key(self) -> "SecurityConfig":
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(64)
        return self


class DatabaseConfig(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str = "sqlite+aiosqlite:///./authshieldlab.db"
    echo: bool = False
    pool_size: int = 5

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        if not v:
            return "sqlite+aiosqlite:///./authshieldlab.db"
        return v


class CorsConfig(BaseSettings):
    """CORS configuration - locked to localhost only."""

    model_config = SettingsConfigDict(
        env_prefix="CORS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    allowed_origins: list[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5173",
        "http://[::1]",
        "http://[::1]:3000",
        "http://[::1]:8000",
        "http://[::1]:5173",
    ]
    allow_credentials: bool = True
    allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    allow_headers: list[str] = ["*"]

    @field_validator("allowed_origins")
    @classmethod
    def _validate_origins(cls, v: list[str]) -> list[str]:
        allowed_hosts = {"localhost", "127.0.0.1", "::1"}
        for origin in v:
            from urllib.parse import urlparse

            parsed = urlparse(origin)
            hostname = (parsed.hostname or "").strip("[]")
            if hostname not in allowed_hosts:
                raise ValueError(
                    f"Origin '{origin}' is not a localhost address. "
                    "Only localhost origins are permitted for security."
                )
        return v


class ThemeConfig(BaseSettings):
    """Theme configuration."""

    model_config = SettingsConfigDict(
        env_prefix="THEME_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    default_theme: ThemeName = ThemeName.LIGHT
    available_themes: list[ThemeName] = [
        ThemeName.LIGHT,
        ThemeName.DARK,
        ThemeName.HIGH_CONTRAST,
        ThemeName.SOLARIZED,
        ThemeName.MONOKAI,
    ]


class AccessibilityConfig(BaseSettings):
    """Accessibility settings."""

    model_config = SettingsConfigDict(
        env_prefix="A11Y_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    high_contrast_default: bool = False
    reduced_motion_default: bool = False
    font_scale_default: float = 1.0
    min_font_scale: float = 0.75
    max_font_scale: float = 2.0

    @field_validator("font_scale_default")
    @classmethod
    def _validate_font_scale(cls, v: float) -> float:
        if v < 0.75 or v > 2.0:
            raise ValueError("font_scale_default must be between 0.75 and 2.0")
        return v


class AppConfig(BaseSettings):
    """Combined application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app: ApplicationConfig = ApplicationConfig()
    security: SecurityConfig = SecurityConfig()
    database: DatabaseConfig = DatabaseConfig()
    cors: CorsConfig = CorsConfig()
    theme: ThemeConfig = ThemeConfig()
    accessibility: AccessibilityConfig = AccessibilityConfig()

    def validate_localhost_only(self) -> bool:
        """Validate that all configured origins are localhost-only."""
        allowed_hosts = {"localhost", "127.0.0.1", "::1"}
        from urllib.parse import urlparse

        for origin in self.cors.allowed_origins:
            parsed = urlparse(origin)
            hostname = (parsed.hostname or "").strip("[]")
            if hostname not in allowed_hosts:
                return False
        return True

    def get_environment_profile(self) -> dict[str, Any]:
        """Return environment-specific overrides."""
        profiles: dict[str, dict[str, Any]] = {
            Environment.DEVELOPMENT: {
                "debug": True,
                "log_level": LogLevel.DEBUG,
                "database_echo": True,
            },
            Environment.TESTING: {
                "debug": True,
                "log_level": LogLevel.DEBUG,
                "database_url": "sqlite+aiosqlite:///./test.db",
            },
            Environment.PRODUCTION: {
                "debug": False,
                "log_level": LogLevel.WARNING,
                "database_echo": False,
            },
            Environment.EDUCATION: {
                "debug": True,
                "log_level": LogLevel.INFO,
                "token_expiry_minutes": 120,
                "session_timeout_minutes": 180,
            },
            Environment.DEMO: {
                "debug": True,
                "log_level": LogLevel.INFO,
                "max_login_attempts": 10,
                "lockout_duration_minutes": 5,
            },
        }
        return profiles.get(self.app.environment, {})


@lru_cache
def get_settings() -> AppConfig:
    """Get cached application settings singleton."""
    return AppConfig()
