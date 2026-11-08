"""Application settings and configuration model."""

from __future__ import annotations

from sqlalchemy import String, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ..base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..logging_config import get_logger

logger = get_logger(__name__)


class ApplicationSettings(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """Key-value store for runtime-adjustable application settings."""

    __tablename__ = "application_settings"

    key: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    value_type: Mapped[str] = mapped_column(String(32), nullable=False, default="json")
    description: Mapped[str | None] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(
        String(32), nullable=False, default="general"
    )
    is_sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    environment: Mapped[str] = mapped_column(
        String(32), nullable=False, default="all"
    )

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Serialize the setting to a dictionary.

        Parameters
        ----------
        include_sensitive:
            When ``False`` (default) the ``value`` field is redacted for
            settings marked as sensitive.
        """
        result: dict = {
            "id": self.id,
            "key": self.key,
            "value_type": self.value_type,
            "description": self.description,
            "category": self.category,
            "is_sensitive": self.is_sensitive,
            "environment": self.environment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_sensitive or not self.is_sensitive:
            result["value"] = self.value
        else:
            result["value"] = None
        return result

    def __repr__(self) -> str:
        return f"<ApplicationSettings id={self.id!r} key={self.key!r}>"
