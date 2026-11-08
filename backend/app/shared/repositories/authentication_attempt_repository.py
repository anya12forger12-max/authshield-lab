"""Authentication attempt repository with brute-force detection helpers."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.authentication_attempt import AuthenticationAttempt
from ..logging_config import get_logger
from .base_repository import BaseRepository

logger = get_logger(__name__)


class AuthenticationAttemptRepository(BaseRepository[AuthenticationAttempt]):
    """Async repository for :class:`AuthenticationAttempt` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AuthenticationAttempt, session)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def get_by_user(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> dict:
        """Return a paginated list of auth attempts for *user_id*."""
        base = AuthenticationAttempt.user_id == user_id

        count_stmt = (
            select(func.count()).select_from(AuthenticationAttempt).where(base)
        )
        total: int = (await self._session.execute(count_stmt)).scalar()  # type: ignore[assignment]

        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        stmt = (
            select(AuthenticationAttempt)
            .where(base)
            .order_by(desc(AuthenticationAttempt.created_at))
            .offset(offset)
            .limit(per_page)
        )
        items = list((await self._session.execute(stmt)).scalars().all())
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def get_failed_attempts(
        self, user_id: str, since_minutes: int = 30
    ) -> list[AuthenticationAttempt]:
        """Return failed auth attempts for *user_id* within the last *since_minutes*."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
        stmt = (
            select(AuthenticationAttempt)
            .where(
                AuthenticationAttempt.user_id == user_id,
                AuthenticationAttempt.outcome == "failure",
                AuthenticationAttempt.created_at >= cutoff,
            )
            .order_by(desc(AuthenticationAttempt.created_at))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_attempts(
        self, username: str, limit: int = 10
    ) -> list[AuthenticationAttempt]:
        """Return the most recent auth attempts for *username* (any outcome)."""
        stmt = (
            select(AuthenticationAttempt)
            .where(AuthenticationAttempt.username_attempted == username)
            .order_by(desc(AuthenticationAttempt.created_at))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_failed_attempts(
        self, user_id: str, since_minutes: int = 30
    ) -> int:
        """Count failed auth attempts for *user_id* within *since_minutes*."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
        stmt = select(func.count()).select_from(AuthenticationAttempt).where(
            AuthenticationAttempt.user_id == user_id,
            AuthenticationAttempt.outcome == "failure",
            AuthenticationAttempt.created_at >= cutoff,
        )
        result = await self._session.execute(stmt)
        return result.scalar()  # type: ignore[return-value]

    async def get_by_correlation_id(
        self, correlation_id: str
    ) -> list[AuthenticationAttempt]:
        """Return all auth attempts sharing the same *correlation_id*.

        Useful for tracing a single authentication flow end-to-end.
        """
        stmt = (
            select(AuthenticationAttempt)
            .where(AuthenticationAttempt.correlation_id == correlation_id)
            .order_by(AuthenticationAttempt.created_at)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
