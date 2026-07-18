"""Session entity for domain logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional


@dataclass
class SessionEntity:
    """Domain entity representing a user session."""

    session_id: str = ""
    user_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    idle_timeout_minutes: int = 30
    status: str = "active"
    authentication_method: str = "password"
    platform: Optional[str] = None
    application_version: Optional[str] = None
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    ip_address: str = "127.0.0.1"
    remember_me: bool = False
    is_trusted: bool = False
    security_level: int = 1

    @property
    def is_expired(self) -> bool:
        """Return ``True`` if the session has exceeded its absolute timeout."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_idle(self) -> bool:
        """Return ``True`` if the session has exceeded its idle timeout."""
        idle_cutoff = datetime.now(timezone.utc) - timedelta(minutes=self.idle_timeout_minutes)
        return self.last_activity < idle_cutoff

    @property
    def is_usable(self) -> bool:
        """Return ``True`` when the session is active and not expired."""
        return self.status == "active" and not self.is_expired

    @property
    def duration_minutes(self) -> float:
        """Return the session duration in minutes since creation."""
        delta = datetime.now(timezone.utc) - self.created_at
        return delta.total_seconds() / 60.0

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "idle_timeout_minutes": self.idle_timeout_minutes,
            "status": self.status,
            "authentication_method": self.authentication_method,
            "platform": self.platform,
            "application_version": self.application_version,
            "device_id": self.device_id,
            "device_name": self.device_name,
            "ip_address": self.ip_address,
            "remember_me": self.remember_me,
            "is_trusted": self.is_trusted,
            "security_level": self.security_level,
            "is_expired": self.is_expired,
            "is_idle": self.is_idle,
            "is_usable": self.is_usable,
            "duration_minutes": round(self.duration_minutes, 2),
        }

    def to_safe_dict(self) -> dict:
        """Serialize to dictionary without internal flags."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "status": self.status,
            "authentication_method": self.authentication_method,
            "platform": self.platform,
            "device_name": self.device_name,
            "is_expired": self.is_expired,
            "duration_minutes": round(self.duration_minutes, 2),
        }
