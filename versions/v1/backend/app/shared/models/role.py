"""Role and Permission database models with many-to-many association tables."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Boolean,
    Text,
    JSON,
    Table,
    Column,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..logging_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Association tables
# ---------------------------------------------------------------------------

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permissions.id"), primary_key=True),
)

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("role_id", String(36), ForeignKey("roles.id"), primary_key=True),
)


class Role(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """Named role that aggregates permissions."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    permissions: Mapped[list[Permission]] = relationship(
        "Permission", secondary=role_permissions, lazy="selectin"
    )

    def to_dict(self) -> dict:
        """Serialize the role to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "is_builtin": self.is_builtin,
            "is_active": self.is_active,
            "version": self.version,
            "metadata_json": self.metadata_json,
            "permissions": [p.to_dict() for p in self.permissions],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Role id={self.id!r} name={self.name!r}>"


class Permission(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    """Granular permission attached to one or more roles."""

    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def to_dict(self) -> dict:
        """Serialize the permission to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Permission id={self.id!r} name={self.name!r}>"
