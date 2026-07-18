"""Audit event repository -- immutable audit trail queries."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.audit_event import AuditEvent
from ..logging_config import get_logger
from .base_repository import BaseRepository

logger = get_logger(__name__)


class AuditRepository(BaseRepository[AuditEvent]):
    """Async repository for :class:`AuditEvent` entities.

    Audit events are **immutable** -- the inherited ``update`` method is
    deliberately not re-exposed.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AuditEvent, session)

    # ------------------------------------------------------------------
    # Disabled mutation helpers
    # ------------------------------------------------------------------

    async def update(self, id: str, data: dict[str, Any]) -> None:  # type: ignore[override]
        """Stub -- audit events are immutable after creation.

        Raises ``RuntimeError`` unconditionally.
        """
        raise RuntimeError("AuditEvent records are immutable and cannot be updated.")

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def get_by_user(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> dict:
        """Return a paginated list of audit events for *user_id*."""
        base = AuditEvent.user_id == user_id

        count_stmt = select(func.count()).select_from(AuditEvent).where(base)
        total: int = (await self._session.execute(count_stmt)).scalar()  # type: ignore[assignment]

        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        stmt = (
            select(AuditEvent)
            .where(base)
            .order_by(desc(AuditEvent.timestamp))
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

    async def get_by_module(
        self, module: str, page: int = 1, per_page: int = 20
    ) -> dict:
        """Return a paginated list of audit events for the given *module*."""
        base = AuditEvent.module == module

        count_stmt = select(func.count()).select_from(AuditEvent).where(base)
        total: int = (await self._session.execute(count_stmt)).scalar()  # type: ignore[assignment]

        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        stmt = (
            select(AuditEvent)
            .where(base)
            .order_by(desc(AuditEvent.timestamp))
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

    async def get_by_event_type(
        self, event_type: str, page: int = 1, per_page: int = 20
    ) -> dict:
        """Return a paginated list of audit events matching *event_type*."""
        base = AuditEvent.event_type == event_type

        count_stmt = select(func.count()).select_from(AuditEvent).where(base)
        total: int = (await self._session.execute(count_stmt)).scalar()  # type: ignore[assignment]

        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        stmt = (
            select(AuditEvent)
            .where(base)
            .order_by(desc(AuditEvent.timestamp))
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

    async def get_by_correlation_id(
        self, correlation_id: str
    ) -> list[AuditEvent]:
        """Return all events sharing the same *correlation_id*.

        Useful for tracing a single request across multiple audit records.
        """
        stmt = (
            select(AuditEvent)
            .where(AuditEvent.correlation_id == correlation_id)
            .order_by(AuditEvent.timestamp)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_time_range(
        self,
        start: datetime,
        end: datetime,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Return audit events within the ``[start, end]`` time window."""
        base = AuditEvent.timestamp.between(start, end)

        count_stmt = select(func.count()).select_from(AuditEvent).where(base)
        total: int = (await self._session.execute(count_stmt)).scalar()  # type: ignore[assignment]

        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        stmt = (
            select(AuditEvent)
            .where(base)
            .order_by(desc(AuditEvent.timestamp))
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

    async def search(
        self,
        filters: dict[str, Any],
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Generic filtered search over audit events.

        Supported filter keys include: ``module``, ``event_type``,
        ``severity``, ``user_id``, ``administrator_id``, ``result``,
        ``ip_address``.
        """
        stmt = select(AuditEvent)
        count_stmt = select(func.count()).select_from(AuditEvent)

        for key, value in filters.items():
            col = getattr(AuditEvent, key, None)
            if col is not None:
                stmt = stmt.where(col == value)
                count_stmt = count_stmt.where(col == value)

        total: int = (await self._session.execute(count_stmt)).scalar()  # type: ignore[assignment]

        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        stmt = stmt.order_by(desc(AuditEvent.timestamp)).offset(offset).limit(per_page)
        items = list((await self._session.execute(stmt)).scalars().all())
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }
