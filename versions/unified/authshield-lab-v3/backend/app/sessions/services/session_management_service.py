"""Session management service implementation."""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.exceptions import NotFoundError, ValidationError
from ...shared.logging_config import get_logger, log_audit_event
from ...shared.events.event_bus import EventBus, DomainEvent
from ...shared.models.session import Session
from ...config.constants import MODULE_SESSIONS, DEFAULT_PER_PAGE, MAX_PER_PAGE
from ..domain.interfaces.session_management_service import ISessionManagementService
from ..domain.events.session_events import (
    SessionDestroyedEvent,
    SessionRevokedEvent,
    SessionExpiredEvent,
)

logger = get_logger(MODULE_SESSIONS)


def _build_session_dict(session: Session) -> dict:
    """Build a dictionary from a Session database model."""
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "expires_at": session.expires_at.isoformat() if session.expires_at else None,
        "last_activity": session.last_activity.isoformat() if session.last_activity else None,
        "idle_timeout_minutes": session.idle_timeout_minutes,
        "status": session.status,
        "authentication_method": session.authentication_method,
        "platform": session.platform,
        "application_version": session.application_version,
        "device_id": session.device_id,
        "device_name": session.device_name,
        "ip_address": session.ip_address,
        "remember_me": session.remember_me,
        "is_trusted": session.is_trusted,
        "security_level": session.security_level,
        "is_expired": session.is_expired,
        "is_idle": session.is_idle,
        "duration_minutes": round(
            (
                (datetime.now(timezone.utc) - session.created_at).total_seconds() / 60.0
                if session.created_at
                else 0.0
            ),
            2,
        ),
    }


class SessionManagementService(ISessionManagementService):
    """Concrete implementation of advanced session management.

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

    async def get_current_session(self, session_id: str) -> Optional[dict]:
        """Retrieve full details for a single session."""
        async with await self._get_session() as session:
            result = await session.execute(
                select(Session).where(Session.session_id == session_id)
            )
            sess = result.scalar_one_or_none()
            if sess is None:
                return None
            return _build_session_dict(sess)

    async def get_user_active_sessions(self, user_id: str) -> list[dict]:
        """Return all active sessions for a user."""
        async with await self._get_session() as session:
            result = await session.execute(
                select(Session).where(
                    Session.user_id == user_id,
                    Session.status == "active",
                ).order_by(Session.last_activity.desc())
            )
            sessions = result.scalars().all()
            return [
                _build_session_dict(s)
                for s in sessions
                if not s.is_expired
            ]

    async def get_all_user_sessions(
        self, user_id: str, include_expired: bool = False
    ) -> list[dict]:
        """Return all sessions for a user, optionally including expired ones."""
        async with await self._get_session() as session:
            stmt = select(Session).where(Session.user_id == user_id)
            if not include_expired:
                stmt = stmt.where(Session.status == "active")

            stmt = stmt.order_by(Session.created_at.desc())
            result = await session.execute(stmt)
            sessions = result.scalars().all()

            if include_expired:
                return [_build_session_dict(s) for s in sessions]
            return [_build_session_dict(s) for s in sessions if not s.is_expired]

    async def terminate_session(self, session_id: str, reason: str = "") -> bool:
        """Terminate a single session by ID."""
        async with await self._get_session() as session:
            result = await session.execute(
                select(Session).where(Session.session_id == session_id)
            )
            sess = result.scalar_one_or_none()
            if sess is None:
                raise NotFoundError(f"Session {session_id} not found.")

            previous_status = sess.status
            sess.status = "revoked"
            await session.flush()

            event = SessionDestroyedEvent(
                user_id=sess.user_id,
                session_id=session_id,
                correlation_id=session_id,
                metadata={"reason": reason, "previous_status": previous_status},
            )
            await self._publish_event(event)

            log_audit_event(
                "SESSION_TERMINATED",
                user_id=sess.user_id,
                action="TERMINATE",
                resource=f"session:{session_id}",
                logger=logger,
            )

            logger.info(
                "session_terminated",
                session_id=session_id,
                user_id=sess.user_id,
                reason=reason,
            )
            return True

    async def terminate_all_sessions(self, user_id: str, reason: str = "") -> int:
        """Terminate all active sessions for a user. Return count terminated."""
        async with await self._get_session() as session:
            result = await session.execute(
                select(Session).where(
                    Session.user_id == user_id,
                    Session.status == "active",
                )
            )
            sessions = result.scalars().all()

            count = 0
            for sess in sessions:
                sess.status = "revoked"
                count += 1

            await session.flush()

            if count > 0:
                event = SessionRevokedEvent(
                    user_id=user_id,
                    correlation_id=user_id,
                    reason=reason,
                    metadata={"terminated_count": count},
                )
                await self._publish_event(event)

                log_audit_event(
                    "ALL_SESSIONS_TERMINATED",
                    user_id=user_id,
                    action="TERMINATE_ALL",
                    resource=f"user:{user_id}",
                    logger=logger,
                )

                logger.info(
                    "all_sessions_terminated",
                    user_id=user_id,
                    count=count,
                    reason=reason,
                )

            return count

    async def cleanup_expired(self) -> int:
        """Clean up expired sessions. Return count removed."""
        async with await self._get_session() as session:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)

            result = await session.execute(
                select(Session).where(
                    Session.status == "active",
                    Session.expires_at < now,
                )
            )
            expired = result.scalars().all()

            count = 0
            for sess in expired:
                sess.status = "expired"
                count += 1

                event = SessionExpiredEvent(
                    user_id=sess.user_id,
                    session_id=sess.session_id,
                    correlation_id=sess.session_id,
                )
                await self._publish_event(event)

            await session.flush()

            if count > 0:
                log_audit_event(
                    "EXPIRED_SESSIONS_CLEANED",
                    action="CLEANUP",
                    resource=f"sessions:expired",
                    logger=logger,
                )
                logger.info("expired_sessions_cleaned", count=count)

            return count

    async def get_session_stats(self, user_id: Optional[str] = None) -> dict:
        """Return session statistics, optionally filtered by user."""
        async with await self._get_session() as session:
            stmt = select(Session)
            if user_id:
                stmt = stmt.where(Session.user_id == user_id)

            result = await session.execute(stmt)
            sessions = result.scalars().all()

            total = len(sessions)
            statuses = Counter(s.status for s in sessions)
            platforms = Counter(s.platform for s in sessions if s.platform)
            auth_methods = Counter(s.authentication_method for s in sessions)
            unique_users = len(set(s.user_id for s in sessions))

            active = statuses.get("active", 0)
            expired_count = statuses.get("expired", 0)
            revoked = statuses.get("revoked", 0)

            from datetime import timedelta
            now = datetime.now(timezone.utc)
            idle_count = sum(
                1 for s in sessions
                if s.status == "active"
                and (now - s.last_activity) > timedelta(minutes=s.idle_timeout_minutes)
            )

            return {
                "total_sessions": total,
                "active_sessions": active,
                "expired_sessions": expired_count,
                "idle_sessions": idle_count,
                "revoked_sessions": revoked,
                "unique_users": unique_users,
                "average_duration_minutes": 0.0,
                "most_active_platform": platforms.most_common(1)[0][0] if platforms else "",
                "most_common_auth_method": auth_methods.most_common(1)[0][0] if auth_methods else "",
            }

    async def search_sessions(
        self,
        filters: Optional[dict] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Search sessions with filters and pagination."""
        per_page = min(per_page, MAX_PER_PAGE)
        filters = filters or {}

        async with await self._get_session() as session:
            stmt = select(Session)

            if filters.get("user_id"):
                stmt = stmt.where(Session.user_id == filters["user_id"])
            if filters.get("status"):
                stmt = stmt.where(Session.status == filters["status"])
            if filters.get("platform"):
                stmt = stmt.where(Session.platform == filters["platform"])
            if filters.get("authentication_method"):
                stmt = stmt.where(Session.authentication_method == filters["authentication_method"])
            if filters.get("ip_address"):
                stmt = stmt.where(Session.ip_address == filters["ip_address"])

            # Count
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total = total_result.scalar() or 0

            # Paginate
            stmt = stmt.order_by(Session.created_at.desc()).offset(
                (page - 1) * per_page
            ).limit(per_page)

            result = await session.execute(stmt)
            sessions = result.scalars().all()

            items = [_build_session_dict(s) for s in sessions]
            pages = math.ceil(total / per_page) if per_page > 0 else 0

            return {
                "status": "success",
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages,
            }
