"""Authentication domain event definitions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AuthenticationEvent:
    """Base class for all authentication domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = ""
    module: str = "authentication"
    severity: str = "info"
    user_id: str | None = None
    username: str | None = None
    session_id: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class AuthenticationRequestedEvent(AuthenticationEvent):
    """Published when an authentication attempt is initiated."""

    event_type: str = "authentication.requested"


@dataclass
class AuthenticationSucceededEvent(AuthenticationEvent):
    """Published when authentication completes successfully."""

    event_type: str = "authentication.succeeded"
    session_id: str | None = None
    authentication_method: str = "password"
    authentication_duration_ms: float = 0.0


@dataclass
class AuthenticationFailedEvent(AuthenticationEvent):
    """Published when authentication fails."""

    event_type: str = "authentication.failed"
    failure_reason: str = ""
    security_flags: list[str] = field(default_factory=list)


@dataclass
class RegistrationRequestedEvent(AuthenticationEvent):
    """Published when a registration attempt is initiated."""

    event_type: str = "registration.requested"


@dataclass
class RegistrationCompletedEvent(AuthenticationEvent):
    """Published when a user is successfully registered."""

    event_type: str = "registration.completed"


@dataclass
class RegistrationFailedEvent(AuthenticationEvent):
    """Published when a registration attempt fails."""

    event_type: str = "registration.failed"
    failure_reason: str = ""


@dataclass
class SessionCreatedEvent(AuthenticationEvent):
    """Published when a new session is created."""

    event_type: str = "session.created"
    authentication_method: str = "password"


@dataclass
class SessionExpiredEvent(AuthenticationEvent):
    """Published when a session expires."""

    event_type: str = "session.expired"


@dataclass
class SessionDestroyedEvent(AuthenticationEvent):
    """Published when a session is terminated."""

    event_type: str = "session.destroyed"
    termination_reason: str = "logout"


@dataclass
class LogoutCompletedEvent(AuthenticationEvent):
    """Published when a logout operation completes."""

    event_type: str = "logout.completed"


@dataclass
class PasswordVerifiedEvent(AuthenticationEvent):
    """Published when a password verification is performed."""

    event_type: str = "password.verified"
    algorithm_used: str = ""


@dataclass
class PasswordChangedEvent(AuthenticationEvent):
    """Published when a password is changed."""

    event_type: str = "password.changed"


@dataclass
class AccountLockedEvent(AuthenticationEvent):
    """Published when an account is locked due to failed attempts."""

    event_type: str = "account.locked"
    lock_reason: str = "max_failed_attempts"
