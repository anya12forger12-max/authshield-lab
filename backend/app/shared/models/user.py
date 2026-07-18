"""User database model."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, Integer, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base_model import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    SoftDeleteMixin,
    AuditMixin,
)
from ..logging_config import get_logger

logger = get_logger(__name__)


class User(TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin, AuditMixin, Base):
    """Complete user model with authentication, security, and preference data."""

    __tablename__ = "users"

    # --- Authentication ---
    username: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str | None] = mapped_column(
        String(254), unique=True, nullable=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    hash_algorithm: Mapped[str] = mapped_column(
        String(32), nullable=False, default="argon2id"
    )
    password_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # --- Account status ---
    account_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="active", index=True
    )
    role: Mapped[str] = mapped_column(
        String(32), nullable=False, default="student"
    )

    # --- Security metadata ---
    failed_login_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    last_failed_login: Mapped[datetime | None] = mapped_column(nullable=True)
    last_login: Mapped[datetime | None] = mapped_column(nullable=True)
    last_password_change: Mapped[datetime | None] = mapped_column(nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    security_score: Mapped[int] = mapped_column(Integer, nullable=False, default=50)

    # --- Preferences (denormalized quick-access) ---
    preferred_language: Mapped[str] = mapped_column(
        String(10), nullable=False, default="en"
    )
    preferred_theme: Mapped[str] = mapped_column(
        String(32), nullable=False, default="dark"
    )
    timezone: Mapped[str] = mapped_column(
        String(64), nullable=False, default="UTC"
    )

    # --- Profile ---
    profile_picture: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- MFA ---
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # --- Relationships ---
    sessions: Mapped[list[Session]] = relationship(
        "Session", back_populates="user", lazy="selectin"
    )
    audit_events: Mapped[list[AuditEvent]] = relationship(
        "AuditEvent", back_populates="user", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_users_status_role", "account_status", "role"),
    )

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Serialize the user to a dictionary.

        Parameters
        ----------
        include_sensitive:
            When ``True`` include ``password_hash`` and ``mfa_secret`` fields.
            Defaults to ``False`` for safety.
        """
        result: dict = {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "email": self.email,
            "account_status": self.account_status,
            "role": self.role,
            "preferred_language": self.preferred_language,
            "preferred_theme": self.preferred_theme,
            "timezone": self.timezone,
            "profile_picture": self.profile_picture,
            "bio": self.bio,
            "mfa_enabled": self.mfa_enabled,
            "security_score": self.security_score,
            "login_count": self.login_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_password_change": (
                self.last_password_change.isoformat()
                if self.last_password_change
                else None
            ),
            "is_deleted": self.is_deleted,
        }
        if include_sensitive:
            result["password_hash"] = self.password_hash
            result["hash_algorithm"] = self.hash_algorithm
            result["password_version"] = self.password_version
            result["mfa_secret"] = self.mfa_secret
            result["failed_login_count"] = self.failed_login_count
            result["last_failed_login"] = (
                self.last_failed_login.isoformat()
                if self.last_failed_login
                else None
            )
            result["created_by"] = self.created_by
            result["updated_by"] = self.updated_by
            result["deleted_at"] = (
                self.deleted_at.isoformat() if self.deleted_at else None
            )
        return result

    def to_safe_dict(self) -> dict:
        """Serialize the user without ever exposing sensitive fields.

        This is the preferred method for API responses that face external
        consumers.  It explicitly omits ``password_hash``, ``mfa_secret``,
        and all other credential material.
        """
        return self.to_dict(include_sensitive=False)

    def __repr__(self) -> str:
        return f"<User id={self.id!r} username={self.username!r} status={self.account_status!r}>"


# Avoid circular import issues at class-definition time (TYPE_CHECKING is
# only for static analysers, but the relationship strings already handle it).
from ..models.session import Session  # noqa: E402, F401
from ..models.audit_event import AuditEvent  # noqa: E402, F401
