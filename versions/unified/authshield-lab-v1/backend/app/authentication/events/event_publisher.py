"""Event publisher implementation for authentication events."""

from __future__ import annotations

import logging
from typing import Any

from ..domain.entities.authentication_result import AuthenticationResult
from ..domain.interfaces.event_publisher import IAuthenticationEventPublisher
from ...shared.events.event_bus import (
    DomainEvent,
    EventBus,
    EventSeverity,
    EventType,
    get_event_bus,
)

logger = logging.getLogger(__name__)


class AuthenticationEventPublisher(IAuthenticationEventPublisher):
    """Translates authentication operations into domain events on the shared bus."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._event_bus = event_bus or get_event_bus()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _publish(
        self,
        event_type: EventType,
        *,
        message: str = "",
        severity: EventSeverity = EventSeverity.INFO,
        source_user_id: str | None = None,
        target_user_id: str | None = None,
        session_id: str | None = None,
        correlation_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Create and publish a DomainEvent."""
        event = DomainEvent(
            event_type=event_type,
            module="authentication",
            severity=severity,
            message=message,
            source_user_id=source_user_id,
            target_user_id=target_user_id,
            session_id=session_id,
            correlation_id=correlation_id,
            metadata=metadata or {},
        )
        try:
            await self._event_bus.publish(event)
        except Exception:
            logger.exception(
                "Failed to publish event %s (correlation_id=%s)",
                event_type.value,
                correlation_id,
            )

    # ------------------------------------------------------------------
    # Authentication events
    # ------------------------------------------------------------------

    async def publish_authentication_requested(
        self, username: str, correlation_id: str
    ) -> None:
        await self._publish(
            EventType.AUTHENTICATION_REQUESTED,
            message=f"Authentication requested for user: {username}",
            correlation_id=correlation_id,
            metadata={"username": username},
        )

    async def publish_authentication_succeeded(
        self, result: AuthenticationResult
    ) -> None:
        await self._publish(
            EventType.AUTHENTICATION_SUCCEEDED,
            message=f"Authentication succeeded for user_id={result.user_id}",
            source_user_id=result.user_id,
            session_id=result.session_id,
            correlation_id=result.correlation_id,
            metadata={
                "authentication_duration_ms": result.authentication_duration_ms,
                "account_status": result.account_status,
            },
        )

    async def publish_authentication_failed(
        self, result: AuthenticationResult
    ) -> None:
        severity = EventSeverity.WARNING
        if result.security_flags:
            severity = EventSeverity.ERROR

        await self._publish(
            EventType.AUTHENTICATION_FAILED,
            message=f"Authentication failed: {result.failure_reason.value}",
            severity=severity,
            source_user_id=result.user_id,
            correlation_id=result.correlation_id,
            metadata={
                "failure_reason": result.failure_reason.value,
                "security_flags": result.security_flags,
                "username": result.username,
            },
        )

    # ------------------------------------------------------------------
    # Registration events
    # ------------------------------------------------------------------

    async def publish_registration_requested(
        self, username: str, correlation_id: str
    ) -> None:
        await self._publish(
            EventType.REGISTRATION_REQUESTED,
            message=f"Registration requested for user: {username}",
            correlation_id=correlation_id,
            metadata={"username": username},
        )

    async def publish_registration_completed(
        self, result: AuthenticationResult
    ) -> None:
        await self._publish(
            EventType.REGISTRATION_COMPLETED,
            message=f"Registration completed for user_id={result.user_id}",
            source_user_id=result.user_id,
            correlation_id=result.correlation_id,
            metadata={"username": result.username},
        )

    # ------------------------------------------------------------------
    # Session events
    # ------------------------------------------------------------------

    async def publish_session_created(
        self, session_id: str, user_id: str, correlation_id: str
    ) -> None:
        await self._publish(
            EventType.SESSION_CREATED,
            message=f"Session created: {session_id}",
            source_user_id=user_id,
            session_id=session_id,
            correlation_id=correlation_id,
        )

    async def publish_session_expired(self, session_id: str, user_id: str) -> None:
        await self._publish(
            EventType.SESSION_EXPIRED,
            message=f"Session expired: {session_id}",
            source_user_id=user_id,
            session_id=session_id,
        )

    async def publish_session_destroyed(
        self, session_id: str, user_id: str
    ) -> None:
        await self._publish(
            EventType.SESSION_DESTROYED,
            message=f"Session destroyed: {session_id}",
            source_user_id=user_id,
            session_id=session_id,
        )

    # ------------------------------------------------------------------
    # Logout events
    # ------------------------------------------------------------------

    async def publish_logout(
        self, user_id: str, session_id: str, correlation_id: str
    ) -> None:
        await self._publish(
            EventType.SESSION_DESTROYED,
            message=f"Logout completed for user_id={user_id}",
            source_user_id=user_id,
            session_id=session_id,
            correlation_id=correlation_id,
            metadata={"termination_reason": "logout"},
        )
