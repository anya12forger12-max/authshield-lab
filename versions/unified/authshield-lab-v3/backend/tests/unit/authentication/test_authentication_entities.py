"""Tests for authentication domain entities: AccountStatus, SessionStatus, AuthenticationResult."""

import pytest
from datetime import datetime, timezone

from app.authentication.domain.entities.account_status import (
    AccountStatus,
    VALID_TRANSITIONS,
    can_transition,
    validate_transition,
)
from app.authentication.domain.entities.session_status import (
    SessionStatus,
    is_usable,
    is_terminal,
)
from app.authentication.domain.entities.authentication_result import (
    AuthenticationOutcome,
    FailureReason,
    AuthenticationResult,
)


class TestAccountStatus:
    def test_all_statuses_are_strings(self):
        for status in AccountStatus:
            assert isinstance(status.value, str)

    def test_string_values(self):
        assert AccountStatus.ACTIVE.value == "active"
        assert AccountStatus.LOCKED.value == "locked"
        assert AccountStatus.DELETED.value == "deleted"

    def test_valid_transitions_from_active(self):
        targets = VALID_TRANSITIONS[AccountStatus.ACTIVE]
        assert AccountStatus.LOCKED in targets
        assert AccountStatus.DISABLED in targets
        assert AccountStatus.SUSPENDED in targets
        assert AccountStatus.ARCHIVED in targets

    def test_deleted_has_no_transitions(self):
        assert VALID_TRANSITIONS[AccountStatus.DELETED] == set()

    def test_can_transition_valid(self):
        assert can_transition(AccountStatus.ACTIVE, AccountStatus.LOCKED) is True
        assert can_transition(AccountStatus.ACTIVE, AccountStatus.DISABLED) is True

    def test_can_transition_invalid(self):
        assert can_transition(AccountStatus.DELETED, AccountStatus.ACTIVE) is False
        assert can_transition(AccountStatus.ACTIVE, AccountStatus.ACTIVE) is False

    def test_validate_transition_valid(self):
        validate_transition(AccountStatus.ACTIVE, AccountStatus.LOCKED)

    def test_validate_transition_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid account status transition"):
            validate_transition(AccountStatus.DELETED, AccountStatus.ACTIVE)

    def test_pending_verification_can_activate(self):
        assert can_transition(AccountStatus.PENDING_VERIFICATION, AccountStatus.ACTIVE)

    def test_locked_can_reactivate(self):
        assert can_transition(AccountStatus.LOCKED, AccountStatus.ACTIVE)

    def test_unknown_can_transition_to_active(self):
        assert can_transition(AccountStatus.UNKNOWN, AccountStatus.ACTIVE)


class TestSessionStatus:
    def test_active_is_usable(self):
        assert is_usable(SessionStatus.ACTIVE) is True

    def test_idle_is_usable(self):
        assert is_usable(SessionStatus.IDLE) is True

    def test_expired_not_usable(self):
        assert is_usable(SessionStatus.EXPIRED) is False

    def test_revoked_not_usable(self):
        assert is_usable(SessionStatus.REVOKED) is False

    def test_terminated_not_usable(self):
        assert is_usable(SessionStatus.TERMINATED) is False

    def test_invalid_not_usable(self):
        assert is_usable(SessionStatus.INVALID) is False

    def test_locked_not_usable(self):
        assert is_usable(SessionStatus.LOCKED) is False

    def test_expired_is_terminal(self):
        assert is_terminal(SessionStatus.EXPIRED) is True

    def test_revoked_is_terminal(self):
        assert is_terminal(SessionStatus.REVOKED) is True

    def test_terminated_is_terminal(self):
        assert is_terminal(SessionStatus.TERMINATED) is True

    def test_invalid_is_terminal(self):
        assert is_terminal(SessionStatus.INVALID) is True

    def test_active_not_terminal(self):
        assert is_terminal(SessionStatus.ACTIVE) is False

    def test_idle_not_terminal(self):
        assert is_terminal(SessionStatus.IDLE) is False

    def test_string_values(self):
        assert SessionStatus.ACTIVE.value == "active"
        assert SessionStatus.EXPIRED.value == "expired"


class TestAuthenticationResult:
    def _make_result(self, outcome=AuthenticationOutcome.SUCCESS, **kwargs):
        return AuthenticationResult(outcome=outcome, **kwargs)

    def test_success_result(self):
        result = self._make_result(outcome=AuthenticationOutcome.SUCCESS)
        assert result.is_success is True
        assert result.is_failure is False

    def test_failure_result(self):
        result = self._make_result(
            outcome=AuthenticationOutcome.FAILURE,
            failure_reason=FailureReason.INVALID_CREDENTIALS,
        )
        assert result.is_success is False
        assert result.is_failure is True

    def test_locked_is_failure(self):
        result = self._make_result(outcome=AuthenticationOutcome.LOCKED)
        assert result.is_failure is True

    def test_disabled_is_failure(self):
        result = self._make_result(outcome=AuthenticationOutcome.DISABLED)
        assert result.is_failure is True

    def test_default_correlation_id(self):
        r1 = self._make_result()
        r2 = self._make_result()
        assert r1.correlation_id != r2.correlation_id

    def test_default_timestamp_is_recent(self):
        result = self._make_result()
        now = datetime.now(timezone.utc)
        assert abs((now - result.timestamp).total_seconds()) < 5

    def test_to_response_dict_success(self):
        result = self._make_result(
            outcome=AuthenticationOutcome.SUCCESS,
            user_id="u1",
            username="alice",
            message="Welcome",
        )
        d = result.to_response_dict()
        assert d["outcome"] == "success"
        assert d["success"] is True
        assert d["user_id"] == "u1"
        assert d["username"] == "alice"
        assert d["message"] == "Welcome"
        assert "failure_reason" not in d

    def test_to_response_dict_failure_includes_reason(self):
        result = self._make_result(
            outcome=AuthenticationOutcome.FAILURE,
            failure_reason=FailureReason.INVALID_CREDENTIALS,
        )
        d = result.to_response_dict()
        assert d["failure_reason"] == "invalid_credentials"

    def test_to_safe_dict_strips_sensitive_fields(self):
        result = self._make_result(
            outcome=AuthenticationOutcome.SUCCESS,
            user_id="u1",
            username="alice",
            session_id="s1",
            account_status="active",
        )
        d = result.to_safe_dict()
        assert "user_id" not in d
        assert "username" not in d
        assert "session_id" not in d
        assert "account_status" not in d
        assert d["outcome"] == "success"

    def test_to_response_dict_with_metadata(self):
        result = self._make_result(
            outcome=AuthenticationOutcome.SUCCESS,
            security_flags=["new_device"],
            warnings=["weak_password"],
        )
        d = result.to_response_dict()
        assert d["security_flags"] == ["new_device"]
        assert d["warnings"] == ["weak_password"]

    def test_to_response_dict_with_duration(self):
        result = self._make_result(
            outcome=AuthenticationOutcome.SUCCESS,
            authentication_duration_ms=12.345,
        )
        d = result.to_response_dict()
        assert d["authentication_duration_ms"] == 12.35

    def test_mfa_required_outcome(self):
        result = self._make_result(outcome=AuthenticationOutcome.MFA_REQUIRED)
        assert result.is_success is False
        assert result.is_failure is False
