"""Authentication result model - returned by every authentication attempt."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AuthenticationOutcome(str, Enum):
    """High-level outcome of an authentication attempt."""

    SUCCESS = "success"
    FAILURE = "failure"
    MFA_REQUIRED = "mfa_required"
    LOCKED = "locked"
    DISABLED = "disabled"
    SUSPENDED = "suspended"
    PASSWORD_EXPIRED = "password_expired"
    UNKNOWN = "unknown"


class FailureReason(str, Enum):
    """Specific reason when authentication does not succeed."""

    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_DISABLED = "account_disabled"
    ACCOUNT_SUSPENDED = "account_suspended"
    ACCOUNT_NOT_FOUND = "account_not_found"
    PASSWORD_EXPIRED = "password_expired"
    PASSWORD_POLICY_VIOLATION = "password_policy_violation"
    RATE_LIMITED = "rate_limited"
    INVALID_SESSION = "invalid_session"
    SESSION_EXPIRED = "session_expired"
    VALIDATION_FAILED = "validation_failed"
    INTERNAL_ERROR = "internal_error"
    NONE = "none"


@dataclass
class AuthenticationResult:
    """Unified result object for all authentication operations.

    Carries enough context for logging, event publishing, and API responses
    while keeping sensitive data (e.g. passwords) out of the structure.
    """

    outcome: AuthenticationOutcome
    failure_reason: FailureReason = FailureReason.NONE
    user_id: str | None = None
    username: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    account_status: str | None = None
    session_id: str | None = None
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    authentication_duration_ms: float = 0.0
    security_flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    message: str = ""

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def is_success(self) -> bool:
        """True when the outcome indicates a successful authentication."""
        return self.outcome == AuthenticationOutcome.SUCCESS

    @property
    def is_failure(self) -> bool:
        """True when the outcome indicates a failed authentication."""
        return self.outcome in {
            AuthenticationOutcome.FAILURE,
            AuthenticationOutcome.LOCKED,
            AuthenticationOutcome.DISABLED,
            AuthenticationOutcome.SUSPENDED,
            AuthenticationOutcome.PASSWORD_EXPIRED,
            AuthenticationOutcome.UNKNOWN,
        }

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_response_dict(self) -> dict[str, Any]:
        """Serialize to a dict suitable for API responses.

        Includes correlation_id and timing for debugging but excludes
        any internal-only fields.
        """
        data: dict[str, Any] = {
            "outcome": self.outcome.value,
            "success": self.is_success,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }
        if self.failure_reason != FailureReason.NONE:
            data["failure_reason"] = self.failure_reason.value
        if self.user_id:
            data["user_id"] = self.user_id
        if self.username:
            data["username"] = self.username
        if self.session_id:
            data["session_id"] = self.session_id
        if self.account_status:
            data["account_status"] = self.account_status
        if self.error_code:
            data["error_code"] = self.error_code
        if self.authentication_duration_ms > 0:
            data["authentication_duration_ms"] = round(self.authentication_duration_ms, 2)
        if self.security_flags:
            data["security_flags"] = self.security_flags
        if self.warnings:
            data["warnings"] = self.warnings
        return data

    def to_safe_dict(self) -> dict[str, Any]:
        """Serialize to a dict with all sensitive information stripped.

        Suitable for external logging or non-privileged consumers.
        """
        return {
            "outcome": self.outcome.value,
            "success": self.is_success,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "failure_reason": self.failure_reason.value
            if self.failure_reason != FailureReason.NONE
            else None,
        }
