"""Authentication domain entities."""

from .account_status import (
    VALID_TRANSITIONS,
    AccountStatus,
    can_transition,
    validate_transition,
)
from .authentication_result import (
    AuthenticationOutcome,
    AuthenticationResult,
    FailureReason,
)
from .session_status import SessionStatus, is_terminal, is_usable

__all__ = [
    "VALID_TRANSITIONS",
    "AccountStatus",
    "AuthenticationOutcome",
    "AuthenticationResult",
    "FailureReason",
    "SessionStatus",
    "can_transition",
    "is_terminal",
    "is_usable",
    "validate_transition",
]
