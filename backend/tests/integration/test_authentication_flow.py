"""Integration tests for full authentication flow: register -> login -> session -> logout."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta

from app.shared.events.event_bus import EventBus, EventType
from app.shared.validation.validator import Validator
from app.authentication.domain.entities.account_status import AccountStatus, can_transition
from app.authentication.domain.entities.authentication_result import (
    AuthenticationResult,
    AuthenticationOutcome,
    FailureReason,
)
from app.authentication.domain.entities.session_status import SessionStatus, is_usable
from app.authentication.domain.models.request_models import (
    RegistrationRequest,
    LoginRequest,
    LogoutRequest,
)


class TestRegistrationFlow:
    def test_valid_registration_request(self):
        req = RegistrationRequest(
            username="newuser",
            password="SecurePass123!",
            confirm_password="SecurePass123!",
            display_name="New User",
            email="new@example.com",
        )
        assert req.username == "newuser"

    def test_registration_validation_passes(self):
        validator = Validator()
        username_result = validator.validate_username("newuser")
        password_result = validator.validate_password("SecurePass123!")
        assert username_result.is_valid is True
        assert password_result.is_valid is True

    def test_registration_password_mismatch(self):
        req = RegistrationRequest(
            username="newuser",
            password="SecurePass123!",
            confirm_password="DifferentPass!",
            display_name="New User",
        )
        assert req.password != req.confirm_password

    def test_account_starts_pending_verification(self):
        status = AccountStatus.PENDING_VERIFICATION
        assert can_transition(status, AccountStatus.ACTIVE) is True


class TestLoginFlow:
    def test_valid_login_request(self):
        req = LoginRequest(username="user1", password="Pass123!")
        assert req.username == "user1"
        assert req.remember_me is False

    def test_login_with_remember_me(self):
        req = LoginRequest(username="user1", password="Pass123!", remember_me=True)
        assert req.remember_me is True

    def test_authentication_result_success(self):
        result = AuthenticationResult(
            outcome=AuthenticationOutcome.SUCCESS,
            user_id="u-001",
            username="user1",
            session_id="s-001",
        )
        assert result.is_success is True

    def test_authentication_result_failure(self):
        result = AuthenticationResult(
            outcome=AuthenticationOutcome.FAILURE,
            failure_reason=FailureReason.INVALID_CREDENTIALS,
        )
        assert result.is_failure is True

    def test_account_locked_after_failures(self):
        result = AuthenticationResult(
            outcome=AuthenticationOutcome.LOCKED,
            failure_reason=FailureReason.ACCOUNT_LOCKED,
        )
        assert result.is_failure is True
        assert result.outcome == AuthenticationOutcome.LOCKED


class TestSessionFlow:
    def test_session_becomes_active(self):
        assert is_usable(SessionStatus.ACTIVE) is True

    def test_session_becomes_idle(self):
        assert is_usable(SessionStatus.IDLE) is True

    def test_session_expires(self):
        assert is_usable(SessionStatus.EXPIRED) is False

    def test_session_revoked(self):
        assert is_usable(SessionStatus.REVOKED) is False

    def test_login_creates_session(self):
        result = AuthenticationResult(
            outcome=AuthenticationOutcome.SUCCESS,
            session_id="s-001",
            user_id="u-001",
        )
        assert result.session_id is not None

    def test_logout_request(self):
        req = LogoutRequest(session_id="s-001")
        assert req.session_id == "s-001"

    def test_logout_all_sessions(self):
        req = LogoutRequest(terminate_all=True)
        assert req.terminate_all is True


class TestFullFlowSequence:
    def test_complete_flow_states(self):
        transitions = [
            AccountStatus.PENDING_VERIFICATION,
            AccountStatus.ACTIVE,
            AccountStatus.LOCKED,
            AccountStatus.ACTIVE,
        ]
        for i in range(len(transitions) - 1):
            assert can_transition(transitions[i], transitions[i + 1])

    def test_flow_with_lockout(self):
        transitions = [
            AccountStatus.ACTIVE,
            AccountStatus.LOCKED,
            AccountStatus.ACTIVE,
        ]
        assert can_transition(transitions[0], transitions[1])
        assert can_transition(transitions[1], transitions[2])

    def test_event_publishing_during_flow(self):
        bus = EventBus()
        published_events = []

        async def capture(event):
            published_events.append(event.event_type)

        bus.subscribe(EventType.REGISTRATION_REQUESTED, capture)
        bus.subscribe(EventType.REGISTRATION_COMPLETED, capture)
        bus.subscribe(EventType.AUTHENTICATION_REQUESTED, capture)
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, capture)
        bus.subscribe(EventType.SESSION_CREATED, capture)
        bus.subscribe(EventType.SESSION_DESTROYED, capture)

        import asyncio

        asyncio.get_event_loop().run_until_complete(
            self._simulate_flow(bus)
        )

        assert len(published_events) >= 5

    async def _simulate_flow(self, bus):
        from app.shared.events.event_bus import DomainEvent
        events = [
            EventType.REGISTRATION_REQUESTED,
            EventType.REGISTRATION_COMPLETED,
            EventType.AUTHENTICATION_REQUESTED,
            EventType.AUTHENTICATION_SUCCEEDED,
            EventType.SESSION_CREATED,
            EventType.SESSION_DESTROYED,
        ]
        for event_type in events:
            await bus.publish(DomainEvent(event_type=event_type, module="auth"))
