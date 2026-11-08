"""Audit service implementation."""

from __future__ import annotations

import csv
import io
import json
import math
import uuid
from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.exceptions import NotFoundError, ValidationError
from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus, DomainEvent
from ...shared.models.audit_event import AuditEvent
from ...config.constants import MODULE_AUDIT, DEFAULT_PER_PAGE, MAX_PER_PAGE
from ..domain.entities.audit_entry import AuditEntry
from ..domain.interfaces.audit_service import IAuditService
from ..domain.events.audit_events import (
    AuditEventRecordedEvent,
    AuditEventQueriedEvent,
    AuditExportedEvent,
)

logger = get_logger(MODULE_AUDIT)


def _build_audit_dict(event: AuditEvent) -> dict:
    """Build a dictionary from an AuditEvent database model."""
    return {
        "audit_id": event.id,
        "event_id": event.event_id,
        "correlation_id": event.correlation_id,
        "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        "user_id": event.user_id,
        "username": event.username,
        "administrator_id": event.administrator_id,
        "module": event.module,
        "event_type": event.event_type,
        "severity": event.severity,
        "description": event.description,
        "resource_type": event.resource_type,
        "resource_id": event.resource_id,
        "previous_state": event.previous_state,
        "new_state": event.new_state,
        "metadata": event.metadata_json,
        "result": event.result,
        "ip_address": event.ip_address,
    }


class AuditService(IAuditService):
    """Concrete implementation of audit trail management.

    Audit records are immutable once created.  This service provides
    recording, querying, searching, statistics, and export.

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

    async def record_event(self, entry: AuditEntry) -> str:
        """Record an audit event and return its database ID."""
        async with await self._get_session() as session:
            event_id = entry.audit_id or str(uuid.uuid4())
            correlation_id = entry.correlation_id or str(uuid.uuid4())

            audit_event = AuditEvent(
                event_id=event_id,
                correlation_id=correlation_id,
                timestamp=entry.timestamp,
                user_id=entry.user_id,
                username=entry.username,
                administrator_id=entry.administrator_id,
                module=entry.module,
                event_type=entry.event_type,
                severity=entry.severity,
                description=entry.description,
                resource_type=entry.resource_type,
                resource_id=entry.resource_id,
                previous_state=entry.previous_state,
                new_state=entry.new_state,
                metadata_json=entry.metadata,
                result=entry.result,
                ip_address=entry.ip_address,
            )

            session.add(audit_event)
            await session.flush()

            event = AuditEventRecordedEvent(
                audit_event_id=audit_event.id,
                correlation_id=correlation_id,
                user_id=entry.user_id,
                metadata={"module": entry.module, "event_type": entry.event_type},
            )
            await self._publish_event(event)

            logger.info(
                "audit_event_recorded",
                event_id=event_id,
                module=entry.module,
                event_type=entry.event_type,
            )

            return audit_event.id

    async def get_audit_trail(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> dict:
        """Return the audit trail for a specific user."""
        per_page = min(per_page, MAX_PER_PAGE)

        async with await self._get_session() as session:
            base_stmt = select(AuditEvent).where(AuditEvent.user_id == user_id)

            count_result = await session.execute(
                select(func.count()).select_from(base_stmt.subquery())
            )
            total = count_result.scalar() or 0

            stmt = (
                base_stmt
                .order_by(AuditEvent.timestamp.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            result = await session.execute(stmt)
            events = result.scalars().all()

            items = [_build_audit_dict(e) for e in events]
            pages = math.ceil(total / per_page) if per_page > 0 else 0

            return {
                "status": "success",
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages,
            }

    async def get_module_audit(
        self, module: str, page: int = 1, per_page: int = 20
    ) -> dict:
        """Return audit events for a specific module."""
        per_page = min(per_page, MAX_PER_PAGE)

        async with await self._get_session() as session:
            base_stmt = select(AuditEvent).where(AuditEvent.module == module)

            count_result = await session.execute(
                select(func.count()).select_from(base_stmt.subquery())
            )
            total = count_result.scalar() or 0

            stmt = (
                base_stmt
                .order_by(AuditEvent.timestamp.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            result = await session.execute(stmt)
            events = result.scalars().all()

            items = [_build_audit_dict(e) for e in events]
            pages = math.ceil(total / per_page) if per_page > 0 else 0

            return {
                "status": "success",
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages,
            }

    async def search_audit(
        self, filters: Optional[dict] = None, page: int = 1, per_page: int = 20
    ) -> dict:
        """Search audit events with filters and pagination."""
        per_page = min(per_page, MAX_PER_PAGE)
        filters = filters or {}

        async with await self._get_session() as session:
            stmt = select(AuditEvent)

            if filters.get("user_id"):
                stmt = stmt.where(AuditEvent.user_id == filters["user_id"])
            if filters.get("module"):
                stmt = stmt.where(AuditEvent.module == filters["module"])
            if filters.get("event_type"):
                stmt = stmt.where(AuditEvent.event_type == filters["event_type"])
            if filters.get("severity"):
                stmt = stmt.where(AuditEvent.severity == filters["severity"])
            if filters.get("result"):
                stmt = stmt.where(AuditEvent.result == filters["result"])
            if filters.get("correlation_id"):
                stmt = stmt.where(AuditEvent.correlation_id == filters["correlation_id"])

            if filters.get("start_date"):
                try:
                    start = datetime.fromisoformat(filters["start_date"])
                    stmt = stmt.where(AuditEvent.timestamp >= start)
                except ValueError:
                    pass

            if filters.get("end_date"):
                try:
                    end = datetime.fromisoformat(filters["end_date"])
                    stmt = stmt.where(AuditEvent.timestamp <= end)
                except ValueError:
                    pass

            # Count
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total = total_result.scalar() or 0

            # Paginate
            stmt = stmt.order_by(AuditEvent.timestamp.desc()).offset(
                (page - 1) * per_page
            ).limit(per_page)

            result = await session.execute(stmt)
            events = result.scalars().all()

            items = [_build_audit_dict(e) for e in events]
            pages = math.ceil(total / per_page) if per_page > 0 else 0

            # Query-of-query audit trail
            event = AuditEventQueriedEvent(
                correlation_id=str(uuid.uuid4()),
                query_module=filters.get("module", ""),
                metadata={"filters": filters, "total_results": total},
            )
            await self._publish_event(event)

            return {
                "status": "success",
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages,
            }

    async def get_by_correlation_id(self, correlation_id: str) -> list[dict]:
        """Return all audit events sharing a correlation ID."""
        async with await self._get_session() as session:
            result = await session.execute(
                select(AuditEvent)
                .where(AuditEvent.correlation_id == correlation_id)
                .order_by(AuditEvent.timestamp.asc())
            )
            events = result.scalars().all()
            return [_build_audit_dict(e) for e in events]

    async def get_audit_stats(self) -> dict:
        """Return aggregate audit statistics."""
        async with await self._get_session() as session:
            # Total events
            total_result = await session.execute(select(func.count(AuditEvent.id)))
            total = total_result.scalar() or 0

            # By module
            module_result = await session.execute(
                select(AuditEvent.module, func.count(AuditEvent.id))
                .group_by(AuditEvent.module)
            )
            by_module = {row[0]: row[1] for row in module_result.all()}

            # By severity
            severity_result = await session.execute(
                select(AuditEvent.severity, func.count(AuditEvent.id))
                .group_by(AuditEvent.severity)
            )
            by_severity = {row[0]: row[1] for row in severity_result.all()}

            # By event type
            type_result = await session.execute(
                select(AuditEvent.event_type, func.count(AuditEvent.id))
                .group_by(AuditEvent.event_type)
            )
            by_type = {row[0]: row[1] for row in type_result.all()}

            # By result
            result_result = await session.execute(
                select(AuditEvent.result, func.count(AuditEvent.id))
                .group_by(AuditEvent.result)
            )
            by_result = {row[0]: row[1] for row in result_result.all()}

            # Unique users
            unique_result = await session.execute(
                select(func.count(func.distinct(AuditEvent.user_id)))
            )
            unique_users = unique_result.scalar() or 0

            # Events today
            today_start = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_result = await session.execute(
                select(func.count(AuditEvent.id))
                .where(AuditEvent.timestamp >= today_start)
            )
            events_today = today_result.scalar() or 0

            return {
                "total_events": total,
                "events_by_module": by_module,
                "events_by_severity": by_severity,
                "events_by_type": by_type,
                "events_by_result": by_result,
                "unique_users": unique_users,
                "events_today": events_today,
                "average_events_per_day": round(total / max(1, 30), 2),
            }

    async def export_audit(
        self, filters: Optional[dict] = None, format: str = "json"
    ) -> Any:
        """Export audit events in the specified format."""
        search_result = await self.search_audit(
            filters=filters, page=1, per_page=MAX_PER_PAGE
        )
        items = search_result.get("items", [])

        event = AuditExportedEvent(
            correlation_id=str(uuid.uuid4()),
            export_format=format,
            record_count=len(items),
            metadata={"filters": filters},
        )
        await self._publish_event(event)

        if format == "csv":
            if not items:
                return ""
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)
            return output.getvalue()

        return items
