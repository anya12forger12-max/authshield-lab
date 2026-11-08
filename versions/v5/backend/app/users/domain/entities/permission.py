"""Permission entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class PermissionEntity:
    """Domain entity representing a granular permission."""

    permission_id: str = ""
    name: str = ""
    display_name: str = ""
    description: str = ""
    category: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "permission_id": self.permission_id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_string(cls, permission_string: str) -> PermissionEntity:
        """Create a PermissionEntity from a dot-separated permission string.

        For example ``"users.read"`` produces an entity with
        ``name="users.read"``, ``category="users"``, and
        ``display_name="users.read"``.
        """
        parts = permission_string.split(".")
        category = parts[0] if parts else ""
        return cls(
            name=permission_string,
            display_name=permission_string,
            description=f"Permission: {permission_string}",
            category=category,
        )
