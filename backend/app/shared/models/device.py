"""Device tracking database model."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, Boolean, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from ..base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..logging_config import get_logger

logger = get_logger(__name__)


class Device(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """Tracks client devices that have authenticated against the platform."""

    __tablename__ = "devices"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    friendly_name: Mapped[str] = mapped_column(String(128), nullable=False)
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    operating_system: Mapped[str] = mapped_column(String(128), nullable=False)
    application_version: Mapped[str] = mapped_column(String(32), nullable=False)

    is_trusted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    risk_level: Mapped[str] = mapped_column(
        String(16), nullable=False, default="low"
    )

    last_seen: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    session_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("ix_devices_user_active", "user_id", "is_active"),
    )

    def to_dict(self) -> dict:
        """Serialize the device record to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "friendly_name": self.friendly_name,
            "platform": self.platform,
            "operating_system": self.operating_system,
            "application_version": self.application_version,
            "is_trusted": self.is_trusted,
            "is_active": self.is_active,
            "risk_level": self.risk_level,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "session_count": self.session_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<Device id={self.id!r} device_id={self.device_id!r} "
            f"platform={self.platform!r}>"
        )
