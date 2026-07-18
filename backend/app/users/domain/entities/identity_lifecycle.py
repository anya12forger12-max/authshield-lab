"""User lifecycle state machine."""

from __future__ import annotations

from enum import Enum
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone


class UserLifecycleState(str, Enum):
    """All possible lifecycle states for a user."""

    ANONYMOUS = "anonymous"
    REGISTERED = "registered"
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    AUTHENTICATED = "authenticated"
    ACTIVE_SESSION = "active_session"
    IDLE = "idle"
    LOGGED_OUT = "logged_out"
    LOCKED = "locked"
    DISABLED = "disabled"
    SUSPENDED = "suspended"
    PASSWORD_RESET_REQUIRED = "password_reset_required"
    ARCHIVED = "archived"
    DELETED = "deleted"
    UNKNOWN = "unknown"


VALID_LIFECYCLE_TRANSITIONS: dict[UserLifecycleState, set[UserLifecycleState]] = {
    UserLifecycleState.ANONYMOUS: {UserLifecycleState.REGISTERED},
    UserLifecycleState.REGISTERED: {
        UserLifecycleState.PENDING_VERIFICATION,
        UserLifecycleState.ACTIVE,
    },
    UserLifecycleState.PENDING_VERIFICATION: {
        UserLifecycleState.ACTIVE,
        UserLifecycleState.DISABLED,
    },
    UserLifecycleState.ACTIVE: {
        UserLifecycleState.AUTHENTICATED,
        UserLifecycleState.LOCKED,
        UserLifecycleState.DISABLED,
        UserLifecycleState.SUSPENDED,
        UserLifecycleState.ARCHIVED,
        UserLifecycleState.DELETED,
    },
    UserLifecycleState.AUTHENTICATED: {UserLifecycleState.ACTIVE_SESSION},
    UserLifecycleState.ACTIVE_SESSION: {UserLifecycleState.IDLE},
    UserLifecycleState.IDLE: {
        UserLifecycleState.ACTIVE_SESSION,
        UserLifecycleState.LOGGED_OUT,
    },
    UserLifecycleState.LOGGED_OUT: {
        UserLifecycleState.AUTHENTICATED,
        UserLifecycleState.ARCHIVED,
        UserLifecycleState.DELETED,
    },
    UserLifecycleState.LOCKED: {
        UserLifecycleState.ACTIVE,
        UserLifecycleState.DISABLED,
        UserLifecycleState.DELETED,
    },
    UserLifecycleState.DISABLED: {
        UserLifecycleState.ACTIVE,
        UserLifecycleState.ARCHIVED,
        UserLifecycleState.DELETED,
    },
    UserLifecycleState.SUSPENDED: {
        UserLifecycleState.ACTIVE,
        UserLifecycleState.DISABLED,
    },
    UserLifecycleState.PASSWORD_RESET_REQUIRED: {
        UserLifecycleState.ACTIVE,
        UserLifecycleState.DISABLED,
    },
    UserLifecycleState.ARCHIVED: {
        UserLifecycleState.ACTIVE,
        UserLifecycleState.DELETED,
    },
    UserLifecycleState.DELETED: set(),
    UserLifecycleState.UNKNOWN: {
        UserLifecycleState.ACTIVE,
        UserLifecycleState.REGISTERED,
    },
}


@dataclass
class LifecycleTransition:
    """Records a single lifecycle state transition."""

    from_state: UserLifecycleState
    to_state: UserLifecycleState
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str = ""
    actor_id: Optional[str] = None


def can_transition(current: UserLifecycleState, target: UserLifecycleState) -> bool:
    """Return ``True`` if transitioning from *current* to *target* is allowed."""
    allowed = VALID_LIFECYCLE_TRANSITIONS.get(current, set())
    return target in allowed


def validate_transition(current: UserLifecycleState, target: UserLifecycleState) -> None:
    """Raise ``ValueError`` if the transition is not allowed.

    Parameters
    ----------
    current:
        The current lifecycle state.
    target:
        The desired target state.

    Raises
    ------
    ValueError
        If the transition from *current* to *target* is invalid.
    """
    if not can_transition(current, target):
        allowed = VALID_LIFECYCLE_TRANSITIONS.get(current, set())
        allowed_names = sorted(s.value for s in allowed) or ["(none)"]
        raise ValueError(
            f"Invalid lifecycle transition: {current.value} -> {target.value}. "
            f"Allowed targets from {current.value}: {', '.join(allowed_names)}"
        )
