"""Role management service implementation."""

from __future__ import annotations

import math
from typing import Any, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.exceptions import NotFoundError, ConflictError, ValidationError
from ...shared.logging_config import get_logger, log_audit_event
from ...shared.events.event_bus import EventBus, DomainEvent
from ...shared.models.role import Role, Permission, user_roles, role_permissions
from ...shared.models.user import User
from ...config.constants import MODULE_USERS, DEFAULT_PER_PAGE, MAX_PER_PAGE
from ..domain.entities.role import RoleEntity
from ..domain.interfaces.role_service import IRoleService
from ..domain.events.identity_events import RoleAssignedEvent, RoleRemovedEvent

logger = get_logger(MODULE_USERS)

BUILTIN_ROLES = {"administrator", "instructor", "student", "developer", "readonly"}


def _build_role_entity(role: Role) -> RoleEntity:
    """Build a RoleEntity from a database Role model."""
    return RoleEntity(
        role_id=role.id,
        name=role.name,
        display_name=role.display_name,
        description=role.description or "",
        is_builtin=role.is_builtin,
        is_active=role.is_active,
        version=role.version,
        permissions=[p.name for p in role.permissions] if role.permissions else [],
        created_at=role.created_at,
    )


class RoleService(IRoleService):
    """Concrete implementation of role and permission management.

    Parameters
    ----------
    session_factory:
        Callable that returns an ``AsyncSession``.
    event_bus:
        In-process event bus for publishing domain events.
    """

    def __init__(self, session_factory: Any, event_bus: Optional[EventBus] = None) -> None:
        self._session_factory = session_factory
        self._event_bus = event_bus

    async def _get_session(self) -> AsyncSession:
        return await self._session_factory()

    async def _publish_event(self, event: DomainEvent) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def get_role(self, role_id: str) -> Optional[RoleEntity]:
        """Retrieve a role by ID."""
        async with await self._get_session() as session:
            result = await session.execute(select(Role).where(Role.id == role_id))
            role = result.scalar_one_or_none()
            if role is None:
                return None
            return _build_role_entity(role)

    async def get_role_by_name(self, name: str) -> Optional[RoleEntity]:
        """Retrieve a role by its unique name."""
        async with await self._get_session() as session:
            result = await session.execute(select(Role).where(Role.name == name))
            role = result.scalar_one_or_none()
            if role is None:
                return None
            return _build_role_entity(role)

    async def list_roles(self, page: int = 1, per_page: int = 20) -> dict:
        """List roles with pagination."""
        per_page = min(per_page, MAX_PER_PAGE)

        async with await self._get_session() as session:
            count_result = await session.execute(select(func.count(Role.id)))
            total = count_result.scalar() or 0

            stmt = (
                select(Role)
                .order_by(Role.name)
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            result = await session.execute(stmt)
            roles = result.scalars().all()

            items = [_build_role_entity(r).to_dict() for r in roles]
            pages = math.ceil(total / per_page) if per_page > 0 else 0

            return {
                "status": "success",
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages,
            }

    async def create_role(self, data: dict[str, Any]) -> RoleEntity:
        """Create a new role."""
        name = data.get("name", "")
        if not name:
            raise ValidationError("Role name is required.", detail={"field": "name"})

        async with await self._get_session() as session:
            existing = await session.execute(select(Role).where(Role.name == name))
            if existing.scalar_one_or_none() is not None:
                raise ConflictError(f"Role '{name}' already exists.")

            role = Role(
                name=name,
                display_name=data.get("display_name", name.title()),
                description=data.get("description", ""),
                is_builtin=False,
                is_active=data.get("is_active", True),
            )
            session.add(role)
            await session.flush()

            log_audit_event(
                "ROLE_CREATED",
                action="CREATE",
                resource=f"role:{name}",
                logger=logger,
            )

            return _build_role_entity(role)

    async def update_role(self, role_id: str, data: dict[str, Any]) -> Optional[RoleEntity]:
        """Update an existing role."""
        async with await self._get_session() as session:
            result = await session.execute(select(Role).where(Role.id == role_id))
            role = result.scalar_one_or_none()
            if role is None:
                raise NotFoundError(f"Role {role_id} not found.")

            if role.is_builtin:
                raise ValidationError("Cannot modify built-in roles.")

            for key in ("display_name", "description", "is_active"):
                if key in data:
                    setattr(role, key, data[key])

            role.version += 1
            await session.flush()

            log_audit_event(
                "ROLE_UPDATED",
                action="UPDATE",
                resource=f"role:{role.name}",
                logger=logger,
            )

            return _build_role_entity(role)

    async def delete_role(self, role_id: str) -> bool:
        """Delete a role."""
        async with await self._get_session() as session:
            result = await session.execute(select(Role).where(Role.id == role_id))
            role = result.scalar_one_or_none()
            if role is None:
                raise NotFoundError(f"Role {role_id} not found.")

            if role.is_builtin:
                raise ValidationError("Cannot delete built-in roles.")

            role_name = role.name
            await session.delete(role)
            await session.flush()

            log_audit_event(
                "ROLE_DELETED",
                action="DELETE",
                resource=f"role:{role_name}",
                logger=logger,
            )

            return True

    async def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign a role to a user."""
        async with await self._get_session() as session:
            user_result = await session.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            role_result = await session.execute(select(Role).where(Role.name == role_name))
            role = role_result.scalar_one_or_none()
            if role is None:
                raise NotFoundError(f"Role '{role_name}' not found.")

            if not role.is_active:
                raise ValidationError(f"Role '{role_name}' is not active.")

            # Update the user's role field
            user.role = role_name
            await session.flush()

            event = RoleAssignedEvent(
                user_id=user_id,
                role_name=role_name,
                correlation_id=user_id,
            )
            await self._publish_event(event)

            log_audit_event(
                "ROLE_ASSIGNED",
                user_id=user_id,
                action="ASSIGN",
                resource=f"role:{role_name}",
                logger=logger,
            )

            return True

    async def remove_role(self, user_id: str, role_name: str) -> bool:
        """Remove a role from a user."""
        async with await self._get_session() as session:
            user_result = await session.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            if user.role != role_name:
                raise ValidationError(f"User {user_id} does not have role '{role_name}'.")

            user.role = "student"  # Default fallback
            await session.flush()

            event = RoleRemovedEvent(
                user_id=user_id,
                role_name=role_name,
                correlation_id=user_id,
            )
            await self._publish_event(event)

            log_audit_event(
                "ROLE_REMOVED",
                user_id=user_id,
                action="REMOVE",
                resource=f"role:{role_name}",
                logger=logger,
            )

            return True

    async def get_user_roles(self, user_id: str) -> list[RoleEntity]:
        """Return all roles assigned to a user."""
        async with await self._get_session() as session:
            user_result = await session.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            role_result = await session.execute(
                select(Role).where(Role.name == user.role)
            )
            role = role_result.scalar_one_or_none()
            if role is None:
                return []
            return [_build_role_entity(role)]

    async def get_role_permissions(self, role_name: str) -> list[str]:
        """Return all permission names for a given role."""
        async with await self._get_session() as session:
            result = await session.execute(select(Role).where(Role.name == role_name))
            role = result.scalar_one_or_none()
            if role is None:
                raise NotFoundError(f"Role '{role_name}' not found.")
            return [p.name for p in role.permissions] if role.permissions else []

    async def add_permission(self, role_name: str, permission: str) -> bool:
        """Add a permission to a role."""
        async with await self._get_session() as session:
            role_result = await session.execute(select(Role).where(Role.name == role_name))
            role = role_result.scalar_one_or_none()
            if role is None:
                raise NotFoundError(f"Role '{role_name}' not found.")

            perm_result = await session.execute(select(Permission).where(Permission.name == permission))
            perm = perm_result.scalar_one_or_none()
            if perm is None:
                # Create the permission if it doesn't exist
                parts = permission.split(".")
                perm = Permission(
                    name=permission,
                    display_name=permission,
                    description=f"Auto-created: {permission}",
                    category=parts[0] if parts else "",
                )
                session.add(perm)
                await session.flush()

            if role.permissions and perm in role.permissions:
                return True

            if not role.permissions:
                role.permissions = [perm]
            else:
                role.permissions.append(perm)

            role.version += 1
            await session.flush()

            log_audit_event(
                "PERMISSION_ADDED",
                action="ADD_PERMISSION",
                resource=f"role:{role_name}",
                logger=logger,
            )

            return True

    async def remove_permission(self, role_name: str, permission: str) -> bool:
        """Remove a permission from a role."""
        async with await self._get_session() as session:
            role_result = await session.execute(select(Role).where(Role.name == role_name))
            role = role_result.scalar_one_or_none()
            if role is None:
                raise NotFoundError(f"Role '{role_name}' not found.")

            if not role.permissions:
                return True

            role.permissions = [p for p in role.permissions if p.name != permission]
            role.version += 1
            await session.flush()

            log_audit_event(
                "PERMISSION_REMOVED",
                action="REMOVE_PERMISSION",
                resource=f"role:{role_name}",
                logger=logger,
            )

            return True
