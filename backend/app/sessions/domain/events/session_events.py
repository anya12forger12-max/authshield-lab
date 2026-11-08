"""Session domain events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class SessionEvent:
    """Base class for all session domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = ""
    module: str = "sessions"
    severity: str = "info"
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class SessionCreatedEvent(SessionEvent):
    """Published when a new session is created."""

    event_type: str = "session.created"
    authentication_method: str = "password"


@dataclass
class SessionExpiredEvent(SessionEvent):
    """Published when a session expires."""

    event_type: str = "session.expired"


@dataclass
class SessionDestroyedEvent(SessionEvent):
    """Published when a session is terminated."""

    event_type: str = "session.destroyed"
    termination_reason: str = ""


@dataclass
class SessionRenewedEvent(SessionEvent):
    """Published when a session is renewed / extended."""

    event_type: str = "session.renewed"


@dataclass
class SessionRevokedEvent(SessionEvent):
    """Published when a session is administratively revoked."""

    event_type: str = "session.revoked"
    reason: str = ""


@dataclass
class SessionIdleEvent(SessionEvent):
    """Published when a session becomes idle."""

    event_type: str = "session.idle"
