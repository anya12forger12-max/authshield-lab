"""Session database model."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

from sqlalchemy import String, Boolean, Integer, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..logging_config import get_logger

logger = get_logger(__name__)


class Session(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """Tracks user sessions with idle/absolute timeout support."""

    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    # --- Timing ---
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    last_activity: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    idle_timeout_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    # --- Metadata ---
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="active", index=True
    )
    authentication_method: Mapped[str] = mapped_column(
        String(32), nullable=False, default="password"
    )
    platform: Mapped[str | None] = mapped_column(String(64), nullable=True)
    application_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    device_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    device_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ip_address: Mapped[str] = mapped_column(
        String(45), nullable=False, default="127.0.0.1"
    )

    # --- Flags ---
    remember_me: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_trusted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    security_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # --- Relationships ---
    user: Mapped[User] = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index("ix_sessions_user_status", "user_id", "status"),
        Index("ix_sessions_expires", "expires_at"),
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_expired(self) -> bool:
        """Return ``True`` if the session has exceeded its absolute timeout."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_active(self) -> bool:
        """Return ``True`` when the session is not expired and status is active."""
        return self.status == "active" and not self.is_expired

    @property
    def idle_time_minutes(self) -> float:
        """Return the number of minutes since the last recorded activity."""
        now = datetime.now(timezone.utc)
        delta = now - self.last_activity
        return delta.total_seconds() / 60.0

    @property
    def is_idle(self) -> bool:
        """Return ``True`` if the session has exceeded its idle timeout."""
        return self.idle_time_minutes > self.idle_timeout_minutes

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the session to a dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_activity": (
                self.last_activity.isoformat() if self.last_activity else None
            ),
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
            "is_active": self.is_active,
            "idle_time_minutes": round(self.idle_time_minutes, 2),
        }

    def __repr__(self) -> str:
        return (
            f"<Session id={self.id!r} session_id={self.session_id!r} "
            f"status={self.status!r}>"
        )


# Forward reference for type checking only; relationships use string form.
from ..models.user import User  # noqa: E402, F401
