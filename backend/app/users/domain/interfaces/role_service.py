"""Role management service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any

from ..entities.role import RoleEntity


class IRoleService(ABC):
    """Interface for role and permission management operations."""

    @abstractmethod
    async def get_role(self, role_id: str) -> Optional[RoleEntity]:
        """Retrieve a role by ID."""
        ...

    @abstractmethod
    async def get_role_by_name(self, name: str) -> Optional[RoleEntity]:
        """Retrieve a role by its unique name."""
        ...

    @abstractmethod
    async def list_roles(self, page: int = 1, per_page: int = 20) -> dict:
        """List roles with pagination."""
        ...

    @abstractmethod
    async def create_role(self, data: dict[str, Any]) -> RoleEntity:
        """Create a new role."""
        ...

    @abstractmethod
    async def update_role(self, role_id: str, data: dict[str, Any]) -> Optional[RoleEntity]:
        """Update an existing role."""
        ...

    @abstractmethod
    async def delete_role(self, role_id: str) -> bool:
        """Delete a role."""
        ...

    @abstractmethod
    async def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign a role to a user."""
        ...

    @abstractmethod
    async def remove_role(self, user_id: str, role_name: str) -> bool:
        """Remove a role from a user."""
        ...

    @abstractmethod
    async def get_user_roles(self, user_id: str) -> list[RoleEntity]:
        """Return all roles assigned to a user."""
        ...

    @abstractmethod
    async def get_role_permissions(self, role_name: str) -> list[str]:
        """Return all permission names for a given role."""
        ...

    @abstractmethod
    async def add_permission(self, role_name: str, permission: str) -> bool:
        """Add a permission to a role."""
        ...

    @abstractmethod
    async def remove_permission(self, role_name: str, permission: str) -> bool:
        """Remove a permission from a role."""
        ...
