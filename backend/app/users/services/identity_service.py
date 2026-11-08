"""User identity service implementation."""

from __future__ import annotations

import math
from typing import Any, Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.exceptions import NotFoundError, ValidationError, ConflictError
from ...shared.logging_config import get_logger, log_audit_event
from ...shared.events.event_bus import EventBus, DomainEvent, EventType, EventSeverity
from ...shared.models.user import User
from ...config.constants import MODULE_USERS, DEFAULT_PER_PAGE, MAX_PER_PAGE
from ..domain.entities.user_profile import UserProfile
from ..domain.entities.identity_lifecycle import (
    UserLifecycleState,
    can_transition,
    validate_transition,
)
from ..domain.interfaces.identity_service import IIdentityService
from ..domain.events.identity_events import (
    UserUpdatedEvent,
    UserDeletedEvent,
    UserStatusChangedEvent,
)

logger = get_logger(MODULE_USERS)


class IdentityService(IIdentityService):
    """Concrete implementation of user identity and profile management.

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

    @staticmethod
    def _build_profile(user: User, active_sessions: int = 0, audit_count: int = 0) -> UserProfile:
        """Build a UserProfile entity from a database User model."""
        return UserProfile(
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
            email=user.email,
            profile_picture=user.profile_picture,
            bio=user.bio,
            account_status=user.account_status,
            role=user.role,
            created_at=user.created_at,
            last_updated=user.updated_at,
            last_login=user.last_login,
            login_count=user.login_count,
            preferred_language=user.preferred_language,
            preferred_theme=user.preferred_theme,
            timezone=user.timezone,
            password_last_changed=user.last_password_change,
            password_algorithm=user.hash_algorithm,
            password_version=user.password_version,
            failed_login_count=user.failed_login_count,
            security_score=user.security_score,
            mfa_enabled=user.mfa_enabled,
            active_session_count=active_sessions,
            audit_history_count=audit_count,
        )

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve a user profile by user ID."""
        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                return None

            session_count = 0
            if hasattr(user, "sessions") and user.sessions:
                session_count = sum(
                    1 for s in user.sessions if s.status == "active" and not s.is_expired
                )

            audit_count = 0
            if hasattr(user, "audit_events"):
                audit_count = len(user.audit_events)

            return self._build_profile(user, active_sessions=session_count, audit_count=audit_count)

    async def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        """Retrieve a user profile by username."""
        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            if user is None:
                return None
            return self._build_profile(user)

    async def update_profile(self, user_id: str, data: dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile fields and publish an update event."""
        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            allowed_fields = {"display_name", "email", "bio", "profile_picture"}
            changed_fields: list[str] = []

            for key, value in data.items():
                if key in allowed_fields and hasattr(user, key):
                    old_value = getattr(user, key)
                    if old_value != value:
                        setattr(user, key, value)
                        changed_fields.append(key)

            if not changed_fields:
                return self._build_profile(user)

            await session.flush()

            event = UserUpdatedEvent(
                user_id=user_id,
                changed_fields=changed_fields,
                correlation_id=user_id,
                metadata={"changed_fields": changed_fields},
            )
            await self._publish_event(event)

            log_audit_event(
                "PROFILE_UPDATED",
                user_id=user_id,
                action="UPDATE",
                resource=f"user:{user_id}",
                logger=logger,
            )

            return self._build_profile(user)

    async def delete_user(self, user_id: str, soft: bool = True) -> bool:
        """Delete a user. Performs soft-delete by default."""
        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            if soft:
                from datetime import datetime, timezone
                user.is_deleted = True
                user.deleted_at = datetime.now(timezone.utc)
                user.account_status = "deleted"
            else:
                await session.delete(user)

            await session.flush()

            event = UserDeletedEvent(
                user_id=user_id,
                correlation_id=user_id,
                metadata={"soft": soft},
            )
            await self._publish_event(event)

            log_audit_event(
                "USER_DELETED",
                user_id=user_id,
                action="DELETE",
                resource=f"user:{user_id}",
                logger=logger,
            )

            return True

    async def search_users(
        self,
        query: str,
        filters: Optional[dict] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Search users by query string with optional filters."""
        per_page = min(per_page, MAX_PER_PAGE)
        filters = filters or {}

        async with await self._get_session() as session:
            stmt = select(User).where(User.is_deleted == False)  # noqa: E712

            if query:
                pattern = f"%{query}%"
                stmt = stmt.where(
                    or_(
                        User.username.ilike(pattern),
                        User.display_name.ilike(pattern),
                        User.email.ilike(pattern),
                    )
                )

            if filters.get("role"):
                stmt = stmt.where(User.role == filters["role"])
            if filters.get("status"):
                stmt = stmt.where(User.account_status == filters["status"])

            # Count total
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total = total_result.scalar() or 0

            # Paginate
            sort_column = getattr(User, filters.get("sort_by", "created_at"), User.created_at)
            descending = filters.get("descending", True)
            if descending:
                sort_column = sort_column.desc()
            stmt = stmt.order_by(sort_column).offset((page - 1) * per_page).limit(per_page)

            result = await session.execute(stmt)
            users = result.scalars().all()

            items = [self._build_profile(u).to_safe_dict() for u in users]
            pages = math.ceil(total / per_page) if per_page > 0 else 0

            return {
                "status": "success",
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages,
            }

    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """List users with pagination and optional filters."""
        return await self.search_users(
            query="",
            filters={"role": role, "status": status},
            page=page,
            per_page=per_page,
        )

    async def update_user_status(self, user_id: str, status: str, reason: str = "") -> bool:
        """Update a user's account status with lifecycle validation."""
        async with await self._get_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user is None:
                raise NotFoundError(f"User {user_id} not found.")

            # Map string to lifecycle state for validation
            try:
                current_state = UserLifecycleState(user.account_status)
                target_state = UserLifecycleState(status)
            except ValueError:
                raise ValidationError(f"Invalid status value: {status}")

            validate_transition(current_state, target_state)

            previous_status = user.account_status
            user.account_status = status
            await session.flush()

            event = UserStatusChangedEvent(
                user_id=user_id,
                previous_status=previous_status,
                new_status=status,
                reason=reason,
                correlation_id=user_id,
                metadata={"reason": reason},
            )
            await self._publish_event(event)

            log_audit_event(
                "USER_STATUS_CHANGED",
                user_id=user_id,
                action="UPDATE_STATUS",
                resource=f"user:{user_id}",
                logger=logger,
            )

            logger.info(
                "user_status_changed",
                user_id=user_id,
                previous=previous_status,
                new=status,
                reason=reason,
            )
            return True

    async def get_user_count(self) -> dict[str, int]:
        """Return user counts grouped by account status."""
        async with await self._get_session() as session:
            result = await session.execute(
                select(User.account_status, func.count(User.id))
                .where(User.is_deleted == False)  # noqa: E712
                .group_by(User.account_status)
            )
            counts = {row[0]: row[1] for row in result.all()}
            counts["total"] = sum(counts.values())
            return counts
