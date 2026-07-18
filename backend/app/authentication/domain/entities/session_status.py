"""Session status enumeration and lifecycle."""

from __future__ import annotations

from enum import Enum


class SessionStatus(str, Enum):
    """Lifecycle states for a user session."""

    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INVALID = "invalid"
    TERMINATED = "terminated"
    LOCKED = "locked"
    UNKNOWN = "unknown"


_USABLE_STATUSES: frozenset[SessionStatus] = frozenset(
    {SessionStatus.ACTIVE, SessionStatus.IDLE}
)

_TERMINAL_STATUSES: frozenset[SessionStatus] = frozenset(
    {SessionStatus.EXPIRED, SessionStatus.REVOKED, SessionStatus.TERMINATED, SessionStatus.INVALID}
)


def is_usable(status: SessionStatus) -> bool:
    """Return True if the session can still be used for authentication.

    Only ``ACTIVE`` and ``IDLE`` sessions are considered usable.
    """
    return status in _USABLE_STATUSES


def is_terminal(status: SessionStatus) -> bool:
    """Return True if the session is in a terminal (non-recoverable) state.

    Terminal statuses are ``EXPIRED``, ``REVOKED``, ``TERMINATED``, and ``INVALID``.
    """
    return status in _TERMINAL_STATUSES
