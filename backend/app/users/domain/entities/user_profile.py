"""User profile entity with complete identity metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class UserProfile:
    """Rich user profile entity used by the users domain layer.

    Unlike the raw database model, this entity carries aggregated metadata
    from related tables (sessions, audit events, preferences) and exposes
    multiple serialization depths for different API consumers.
    """

    user_id: str = ""
    username: str = ""
    display_name: str = ""
    email: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    account_status: str = "active"
    role: str = "student"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    login_count: int = 0
    preferred_language: str = "en"
    preferred_theme: str = "dark"
    timezone: str = "UTC"
    # Security metadata
    password_last_changed: Optional[datetime] = None
    password_algorithm: str = "argon2id"
    password_version: int = 1
    failed_login_count: int = 0
    security_score: int = 50
    mfa_enabled: bool = False
    trusted_device_count: int = 0
    active_session_count: int = 0
    audit_history_count: int = 0

    def to_dict(self) -> dict:
        """Serialize to dictionary including security metadata."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "bio": self.bio,
            "account_status": self.account_status,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count,
            "preferred_language": self.preferred_language,
            "preferred_theme": self.preferred_theme,
            "timezone": self.timezone,
            "password_last_changed": self.password_last_changed.isoformat() if self.password_last_changed else None,
            "password_algorithm": self.password_algorithm,
            "password_version": self.password_version,
            "failed_login_count": self.failed_login_count,
            "security_score": self.security_score,
            "mfa_enabled": self.mfa_enabled,
            "trusted_device_count": self.trusted_device_count,
            "active_session_count": self.active_session_count,
            "audit_history_count": self.audit_history_count,
        }

    def to_safe_dict(self) -> dict:
        """Serialize to dictionary without security metadata.

        Safe for external API consumers – omits all credential material
        and internal security counters.
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "bio": self.bio,
            "account_status": self.account_status,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count,
            "preferred_language": self.preferred_language,
            "preferred_theme": self.preferred_theme,
            "timezone": self.timezone,
            "mfa_enabled": self.mfa_enabled,
            "active_session_count": self.active_session_count,
        }

    def to_admin_dict(self) -> dict:
        """Serialize to dictionary with full admin-level details.

        Includes all metadata useful for administrative oversight.
        """
        result = self.to_dict()
        result["trusted_device_count"] = self.trusted_device_count
        result["audit_history_count"] = self.audit_history_count
        return result
