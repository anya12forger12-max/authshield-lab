"""Session repository with domain-specific query helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.session import Session
from ..logging_config import get_logger
from .base_repository import BaseRepository

logger = get_logger(__name__)


class SessionRepository(BaseRepository[Session]):
    """Async repository for :class:`Session` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Session, session)

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    async def get_by_session_id(self, session_id: str) -> Session | None:
        """Return the session matching *session_id*, or ``None``."""
        stmt = select(Session).where(Session.session_id == session_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_user(self, user_id: str) -> list[Session]:
        """Return all active, non-expired sessions for *user_id*."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(Session)
            .where(
                Session.user_id == user_id,
                Session.status == "active",
                Session.expires_at > now,
            )
            .order_by(desc(Session.last_activity))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Expiry management
    # ------------------------------------------------------------------

    async def get_expired_sessions(
        self, before_datetime: datetime | None = None
    ) -> list[Session]:
        """Return sessions whose absolute expiry is before *before_datetime*.

        Parameters
        ----------
        before_datetime:
            The cutoff.  Defaults to ``datetime.now(timezone.utc)``.
        """
        cutoff = before_datetime or datetime.now(timezone.utc)
        stmt = (
            select(Session)
            .where(Session.expires_at <= cutoff, Session.status == "active")
            .order_by(Session.expires_at)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_expired(self) -> int:
        """Soft-delete all sessions that have expired.

        Returns the number of affected rows.
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(Session)
            .where(Session.expires_at <= now, Session.status == "active")
            .values(status="expired")
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        count = result.rowcount  # type: ignore[attr-defined]
        logger.info("expired_sessions_cleaned", count=count)
        return count  # type: ignore[return-value]

    async def delete_all_user_sessions(self, user_id: str) -> int:
        """Mark every session for *user_id* as revoked.

        Returns the number of affected rows.
        """
        stmt = (
            update(Session)
            .where(
                Session.user_id == user_id,
                Session.status == "active",
            )
            .values(status="revoked")
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        count = result.rowcount  # type: ignore[attr-defined]
        logger.info("all_user_sessions_revoked", user_id=user_id, count=count)
        return count  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Activity tracking
    # ------------------------------------------------------------------

    async def update_last_activity(self, session_id: str) -> Session | None:
        """Bump ``last_activity`` to now for the given session.

        Returns the updated session or ``None`` if not found.
        """
        stmt = select(Session).where(Session.session_id == session_id)
        result = await self._session.execute(stmt)
        session = result.scalar_one_or_none()
        if session is None:
            return None

        session.last_activity = datetime.now(timezone.utc)
        self._session.add(session)
        await self._session.flush()
        return session

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------

    async def count_active_sessions(self, user_id: str) -> int:
        """Count the active, non-expired sessions for *user_id*."""
        now = datetime.now(timezone.utc)
        stmt = select(func.count()).select_from(Session).where(
            Session.user_id == user_id,
            Session.status == "active",
            Session.expires_at > now,
        )
        result = await self._session.execute(stmt)
        return result.scalar()  # type: ignore[return-value]
