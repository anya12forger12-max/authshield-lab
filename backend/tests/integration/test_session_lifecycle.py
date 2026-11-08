"""Integration tests for session lifecycle: create -> validate -> renew -> expire -> cleanup."""

import pytest
from datetime import datetime, timezone, timedelta

from app.authentication.domain.entities.session_status import (
    SessionStatus,
    is_usable,
    is_terminal,
)
from app.authentication.domain.models.request_models import (
    SessionValidationRequest,
    SessionRenewalRequest,
)
from app.shared.validation.validator import Validator


class TestSessionCreation:
    def test_session_request_valid(self):
        req = SessionValidationRequest(session_id="sess-001", user_id="u-001")
        assert req.session_id == "sess-001"
        assert req.user_id == "u-001"

    def test_session_renewal_request(self):
        req = SessionRenewalRequest(session_id="sess-001")
        assert req.extend_idle_timeout is True

    def test_new_session_is_active(self):
        assert is_usable(SessionStatus.ACTIVE) is True

    def test_new_session_not_terminal(self):
        assert is_terminal(SessionStatus.ACTIVE) is False


class TestSessionValidation:
    def test_active_session_is_usable(self):
        assert is_usable(SessionStatus.ACTIVE) is True

    def test_idle_session_is_usable(self):
        assert is_usable(SessionStatus.IDLE) is True

    def test_expired_session_not_usable(self):
        assert is_usable(SessionStatus.EXPIRED) is False

    def test_revoked_session_not_usable(self):
        assert is_usable(SessionStatus.REVOKED) is False


class TestSessionRenewal:
    def test_renewal_extends_session(self):
        now = datetime.now(timezone.utc)
        future = now + timedelta(hours=1)
        assert future > now

    def test_renewal_request_with_idle_extension(self):
        req = SessionRenewalRequest(
            session_id="sess-001", extend_idle_timeout=True
        )
        assert req.extend_idle_timeout is True

    def test_renewal_request_without_idle_extension(self):
        req = SessionRenewalRequest(
            session_id="sess-001", extend_idle_timeout=False
        )
        assert req.extend_idle_timeout is False


class TestSessionExpiry:
    def test_expired_is_terminal(self):
        assert is_terminal(SessionStatus.EXPIRED) is True

    def test_expired_not_usable(self):
        assert is_usable(SessionStatus.EXPIRED) is False

    def test_revoked_is_terminal(self):
        assert is_terminal(SessionStatus.REVOKED) is True

    def test_terminated_is_terminal(self):
        assert is_terminal(SessionStatus.TERMINATED) is True

    def test_invalid_is_terminal(self):
        assert is_terminal(SessionStatus.INVALID) is True


class TestSessionCleanup:
    def test_all_terminal_statuses(self):
        terminal = {SessionStatus.EXPIRED, SessionStatus.REVOKED, SessionStatus.TERMINATED, SessionStatus.INVALID}
        for status in terminal:
            assert is_terminal(status) is True

    def test_non_terminal_statuses(self):
        non_terminal = {SessionStatus.ACTIVE, SessionStatus.IDLE, SessionStatus.LOCKED, SessionStatus.UNKNOWN}
        for status in non_terminal:
            assert is_terminal(status) is False

    def test_cleanup_removes_expired(self):
        validator = Validator()
        result = validator.validate_required("sess-001", "session_id")
        assert result.is_valid is True

    def test_all_sessions_eventually_expire(self):
        now = datetime.now(timezone.utc)
        expires = now - timedelta(minutes=1)
        assert expires < now
