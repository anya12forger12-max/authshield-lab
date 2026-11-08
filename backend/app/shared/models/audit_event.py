"""Audit event database model -- immutable audit trail."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Text, Index, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base_model import Base, UUIDPrimaryKeyMixin
from ..logging_config import get_logger

logger = get_logger(__name__)


class AuditEvent(UUIDPrimaryKeyMixin, Base):
    """Immutable record of a security or operational audit event.

    Once created an ``AuditEvent`` must never be mutated -- there is no
    ``update`` helper and the ``__init__`` method is intentionally minimal.
    """

    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    correlation_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # --- Who ---
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    administrator_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # --- What ---
    module: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="info")
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # --- Target ---
    resource_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # --- Details ---
    previous_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    # --- Result ---
    result: Mapped[str] = mapped_column(String(16), nullable=False, default="success")
    ip_address: Mapped[str] = mapped_column(
        String(45), nullable=False, default="127.0.0.1"
    )

    # --- Relationships ---
    user: Mapped[User | None] = relationship(
        "User", back_populates="audit_events", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_audit_module_timestamp", "module", "timestamp"),
        Index("ix_audit_event_type", "event_type"),
    )

    def __init__(self, **kwargs: object) -> None:
        """Initialise an immutable audit event.

        All keyword arguments are forwarded to the SQLAlchemy constructor.
        After creation the row must not be updated.
        """
        super().__init__(**kwargs)

    def to_dict(self) -> dict:
        """Serialize the audit event to a dictionary."""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "username": self.username,
            "administrator_id": self.administrator_id,
            "module": self.module,
            "event_type": self.event_type,
            "severity": self.severity,
            "description": self.description,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "metadata_json": self.metadata_json,
            "result": self.result,
            "ip_address": self.ip_address,
        }

    def __repr__(self) -> str:
        return (
            f"<AuditEvent id={self.id!r} event_type={self.event_type!r} "
            f"severity={self.severity!r}>"
        )


# Forward reference for the User relationship.
from ..models.user import User  # noqa: E402, F401
