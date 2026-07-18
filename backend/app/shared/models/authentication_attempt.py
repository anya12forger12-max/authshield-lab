"""Authentication attempt tracking model."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..logging_config import get_logger

logger = get_logger(__name__)


class AuthenticationAttempt(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """Records every authentication attempt for brute-force detection and auditing."""

    __tablename__ = "authentication_attempts"

    correlation_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    username_attempted: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )

    outcome: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )  # success | failure
    failure_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)

    authentication_method: Mapped[str] = mapped_column(
        String(32), nullable=False, default="password"
    )
    authentication_duration_ms: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )

    ip_address: Mapped[str] = mapped_column(
        String(45), nullable=False, default="127.0.0.1"
    )
    platform: Mapped[str | None] = mapped_column(String(64), nullable=True)
    device_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    security_flags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    __table_args__ = (
        Index("ix_auth_attempts_user_time", "user_id", "created_at"),
        Index("ix_auth_attempts_outcome", "outcome"),
    )

    def to_dict(self) -> dict:
        """Serialize the authentication attempt to a dictionary."""
        return {
            "id": self.id,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "username_attempted": self.username_attempted,
            "outcome": self.outcome,
            "failure_reason": self.failure_reason,
            "authentication_method": self.authentication_method,
            "authentication_duration_ms": self.authentication_duration_ms,
            "ip_address": self.ip_address,
            "platform": self.platform,
            "device_id": self.device_id,
            "security_flags": self.security_flags,
            "metadata_json": self.metadata_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<AuthenticationAttempt id={self.id!r} "
            f"username={self.username_attempted!r} outcome={self.outcome!r}>"
        )
