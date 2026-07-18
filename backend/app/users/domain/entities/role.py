"""Role entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RoleEntity:
    """Domain entity representing a named role with associated permissions."""

    role_id: str = ""
    name: str = ""
    display_name: str = ""
    description: str = ""
    is_builtin: bool = False
    is_active: bool = True
    version: int = 1
    permissions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "role_id": self.role_id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "is_builtin": self.is_builtin,
            "is_active": self.is_active,
            "version": self.version,
            "permissions": list(self.permissions),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
