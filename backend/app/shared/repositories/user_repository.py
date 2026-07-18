"""User repository with domain-specific query helpers."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..logging_config import get_logger
from .base_repository import BaseRepository

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """Async repository for :class:`User` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    async def get_by_username(self, username: str) -> Optional[User]:
        """Return the user matching *username*, or ``None``."""
        stmt = select(User).where(User.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Return the user matching *email*, or ``None``."""
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Existence checks
    # ------------------------------------------------------------------

    async def exists_by_username(self, username: str) -> bool:
        """Return ``True`` if a user with *username* exists."""
        stmt = select(func.count()).select_from(User).where(User.username == username)
        result = await self._session.execute(stmt)
        count_val: int = result.scalar()  # type: ignore[assignment]
        return count_val > 0

    async def exists_by_email(self, email: str) -> bool:
        """Return ``True`` if a user with *email* exists."""
        stmt = select(func.count()).select_from(User).where(User.email == email)
        result = await self._session.execute(stmt)
        count_val: int = result.scalar()  # type: ignore[assignment]
        return count_val > 0

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    async def get_by_role(self, role: str) -> list[User]:
        """Return all users assigned the given *role*."""
        stmt = select(User).where(User.role == role).order_by(User.username)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> list[User]:
        """Return all users with the given *account_status*."""
        stmt = select(User).where(User.account_status == status).order_by(User.username)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        filters: Optional[dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Case-insensitive search on ``username``, ``display_name``, and ``email``.

        Parameters
        ----------
        query:
            The search string.
        filters:
            Optional equality filters applied in addition to the text search
            (e.g. ``{"account_status": "active"}``).
        page:
            1-indexed page number.
        per_page:
            Maximum items per page.

        Returns
        -------
        dict
            ``{"items": [...], "total": int, "page": int, "per_page": int,
            "pages": int}``
        """
        conditions = [
            User.username.ilike(f"%{query}%"),
            User.display_name.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%"),
        ]
        base_filter = or_(*conditions)

        stmt = select(User).where(base_filter)
        count_stmt = select(func.count()).select_from(User).where(base_filter)

        if filters:
            for key, value in filters.items():
                col = getattr(User, key, None)
                if col is not None:
                    stmt = stmt.where(col == value)
                    count_stmt = count_stmt.where(col == value)

        total_result = await self._session.execute(count_stmt)
        total: int = total_result.scalar()  # type: ignore[assignment]

        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        stmt = stmt.order_by(desc(User.created_at)).offset(offset).limit(per_page)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }
