"""Authentication domain entities."""

from .account_status import (
    AccountStatus,
    VALID_TRANSITIONS,
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
    "AccountStatus",
    "VALID_TRANSITIONS",
    "AuthenticationOutcome",
    "AuthenticationResult",
    "FailureReason",
    "SessionStatus",
    "can_transition",
    "is_terminal",
    "is_usable",
    "validate_transition",
]
