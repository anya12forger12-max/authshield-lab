"""Role repository with permission and user-role association helpers."""

from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.role import Role, Permission, role_permissions, user_roles
from ..logging_config import get_logger
from .base_repository import BaseRepository

logger = get_logger(__name__)


class RoleRepository(BaseRepository[Role]):
    """Async repository for :class:`Role` entities and role/user associations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Role, session)

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    async def get_by_name(self, name: str) -> Role | None:
        """Return the role matching *name*, or ``None``."""
        stmt = select(Role).where(Role.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_builtin_roles(self) -> list[Role]:
        """Return all roles flagged as built-in."""
        stmt = select(Role).where(Role.is_builtin == True).order_by(Role.name)  # noqa: E712
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # User-role associations
    # ------------------------------------------------------------------

    async def get_user_roles(self, user_id: str) -> list[Role]:
        """Return all roles assigned to *user_id*."""
        stmt = (
            select(Role)
            .join(user_roles, Role.id == user_roles.c.role_id)
            .where(user_roles.c.user_id == user_id)
            .order_by(Role.name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Insert a user-role association.

        Returns ``True`` if the association was created, ``False`` if it
        already existed.
        """
        # Check for existing association
        stmt = select(func.count()).select_from(user_roles).where(
            user_roles.c.user_id == user_id,
            user_roles.c.role_id == role_id,
        )
        count_result = await self._session.execute(stmt)
        if count_result.scalar() > 0:  # type: ignore[union-attr]
            return False

        await self._session.execute(
            user_roles.insert().values(user_id=user_id, role_id=role_id)
        )
        await self._session.flush()
        logger.info("role_assigned", user_id=user_id, role_id=role_id)
        return True

    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Remove a user-role association.

        Returns ``True`` if a row was deleted.
        """
        stmt = user_roles.delete().where(
            user_roles.c.user_id == user_id,
            user_roles.c.role_id == role_id,
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        deleted = result.rowcount > 0  # type: ignore[attr-defined]
        if deleted:
            logger.info("role_removed", user_id=user_id, role_id=role_id)
        return deleted  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Role-permission associations
    # ------------------------------------------------------------------

    async def get_role_permissions(self, role_id: str) -> list[Permission]:
        """Return all permissions attached to *role_id*."""
        stmt = (
            select(Permission)
            .join(role_permissions, Permission.id == role_permissions.c.permission_id)
            .where(role_permissions.c.role_id == role_id)
            .order_by(Permission.name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_permission_to_role(
        self, role_id: str, permission_id: str
    ) -> bool:
        """Attach a permission to a role.

        Returns ``True`` if the association was created, ``False`` if it
        already existed.
        """
        stmt = select(func.count()).select_from(role_permissions).where(
            role_permissions.c.role_id == role_id,
            role_permissions.c.permission_id == permission_id,
        )
        count_result = await self._session.execute(stmt)
        if count_result.scalar() > 0:  # type: ignore[union-attr]
            return False

        await self._session.execute(
            role_permissions.insert().values(
                role_id=role_id, permission_id=permission_id
            )
        )
        await self._session.flush()
        logger.info(
            "permission_added_to_role",
            role_id=role_id,
            permission_id=permission_id,
        )
        return True

    async def remove_permission_from_role(
        self, role_id: str, permission_id: str
    ) -> bool:
        """Remove a permission from a role.

        Returns ``True`` if a row was deleted.
        """
        stmt = role_permissions.delete().where(
            role_permissions.c.role_id == role_id,
            role_permissions.c.permission_id == permission_id,
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        deleted = result.rowcount > 0  # type: ignore[attr-defined]
        if deleted:
            logger.info(
                "permission_removed_from_role",
                role_id=role_id,
                permission_id=permission_id,
            )
        return deleted  # type: ignore[return-value]
