"""Account status enumeration and state machine for user lifecycle."""

from __future__ import annotations

from enum import Enum


class AccountStatus(str, Enum):
    """Lifecycle states for a user account."""

    ACTIVE = "active"
    PENDING_VERIFICATION = "pending_verification"
    LOCKED = "locked"
    DISABLED = "disabled"
    SUSPENDED = "suspended"
    PASSWORD_RESET_REQUIRED = "password_reset_required"
    ARCHIVED = "archived"
    DELETED = "deleted"
    UNKNOWN = "unknown"


VALID_TRANSITIONS: dict[AccountStatus, set[AccountStatus]] = {
    AccountStatus.PENDING_VERIFICATION: {
        AccountStatus.ACTIVE,
        AccountStatus.DISABLED,
        AccountStatus.DELETED,
    },
    AccountStatus.ACTIVE: {
        AccountStatus.LOCKED,
        AccountStatus.DISABLED,
        AccountStatus.SUSPENDED,
        AccountStatus.PASSWORD_RESET_REQUIRED,
        AccountStatus.ARCHIVED,
        AccountStatus.DELETED,
    },
    AccountStatus.LOCKED: {
        AccountStatus.ACTIVE,
        AccountStatus.DISABLED,
        AccountStatus.DELETED,
    },
    AccountStatus.DISABLED: {
        AccountStatus.ACTIVE,
        AccountStatus.ARCHIVED,
        AccountStatus.DELETED,
    },
    AccountStatus.SUSPENDED: {
        AccountStatus.ACTIVE,
        AccountStatus.DISABLED,
        AccountStatus.DELETED,
    },
    AccountStatus.PASSWORD_RESET_REQUIRED: {
        AccountStatus.ACTIVE,
        AccountStatus.DISABLED,
        AccountStatus.DELETED,
    },
    AccountStatus.ARCHIVED: {
        AccountStatus.ACTIVE,
        AccountStatus.DELETED,
    },
    AccountStatus.DELETED: set(),
    AccountStatus.UNKNOWN: {
        AccountStatus.ACTIVE,
        AccountStatus.PENDING_VERIFICATION,
        AccountStatus.DISABLED,
        AccountStatus.DELETED,
    },
}


def can_transition(current: AccountStatus, target: AccountStatus) -> bool:
    """Return True if transitioning from *current* to *target* is allowed."""
    allowed = VALID_TRANSITIONS.get(current, set())
    return target in allowed


def validate_transition(current: AccountStatus, target: AccountStatus) -> None:
    """Raise ``ValueError`` if the transition from *current* to *target* is invalid.

    Parameters
    ----------
    current:
        The current account status.
    target:
        The desired target status.

    Raises
    ------
    ValueError
        If the transition is not in the valid set.
    """
    if not can_transition(current, target):
        raise ValueError(
            f"Invalid account status transition: {current.value} -> {target.value}. "
            f"Allowed targets from {current.value}: "
            f"{', '.join(sorted(s.value for s in VALID_TRANSITIONS.get(current, set()))) or '(none)'}"
        )
