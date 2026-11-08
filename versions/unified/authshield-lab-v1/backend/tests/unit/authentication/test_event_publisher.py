"""Tests for AuthenticationEventPublisher."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.shared.events.event_bus import EventBus, EventType, DomainEvent, EventSeverity
from app.authentication.events.event_publisher import AuthenticationEventPublisher
from app.authentication.domain.entities.authentication_result import (
    AuthenticationResult,
    AuthenticationOutcome,
    FailureReason,
)


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def publisher(event_bus):
    return AuthenticationEventPublisher(event_bus=event_bus)


class TestPublishAuthenticationRequested:
    @pytest.mark.asyncio
    async def test_publishes_correct_event_type(self, publisher, event_bus):
        await publisher.publish_authentication_requested("alice", "corr-1")
        log = event_bus.get_event_log(event_type=EventType.AUTHENTICATION_REQUESTED)
        assert len(log) == 1

    @pytest.mark.asyncio
    async def test_includes_metadata(self, publisher, event_bus):
        await publisher.publish_authentication_requested("alice", "corr-1")
        log = event_bus.get_event_log()
        event = log[0]
        assert event.metadata["username"] == "alice"
        assert event.correlation_id == "corr-1"

    @pytest.mark.asyncio
    async def test_module_is_authentication(self, publisher, event_bus):
        await publisher.publish_authentication_requested("alice", "corr-1")
        event = event_bus.get_event_log()[0]
        assert event.module == "authentication"


class TestPublishAuthenticationSucceeded:
    @pytest.mark.asyncio
    async def test_publishes_event(self, publisher, event_bus):
        result = AuthenticationResult(
            outcome=AuthenticationOutcome.SUCCESS,
            user_id="u1",
            session_id="s1",
            correlation_id="corr-2",
        )
        await publisher.publish_authentication_succeeded(result)
        log = event_bus.get_event_log(event_type=EventType.AUTHENTICATION_SUCCEEDED)
        assert len(log) == 1

    @pytest.mark.asyncio
    async def test_event_has_user_id(self, publisher, event_bus):
        result = AuthenticationResult(
            outcome=AuthenticationOutcome.SUCCESS,
            user_id="u1",
            session_id="s1",
        )
        await publisher.publish_authentication_succeeded(result)
        event = event_bus.get_event_log()[0]
        assert event.source_user_id == "u1"
        assert event.session_id == "s1"


class TestPublishAuthenticationFailed:
    @pytest.mark.asyncio
    async def test_publishes_event(self, publisher, event_bus):
        result = AuthenticationResult(
            outcome=AuthenticationOutcome.FAILURE,
            failure_reason=FailureReason.INVALID_CREDENTIALS,
            correlation_id="corr-3",
        )
        await publisher.publish_authentication_failed(result)
        log = event_bus.get_event_log(event_type=EventType.AUTHENTICATION_FAILED)
        assert len(log) == 1

    @pytest.mark.asyncio
    async def test_severity_warning_without_flags(self, publisher, event_bus):
        result = AuthenticationResult(
            outcome=AuthenticationOutcome.FAILURE,
            failure_reason=FailureReason.INVALID_CREDENTIALS,
        )
        await publisher.publish_authentication_failed(result)
        event = event_bus.get_event_log()[0]
        assert event.severity == EventSeverity.WARNING

    @pytest.mark.asyncio
    async def test_severity_error_with_flags(self, publisher, event_bus):
        result = AuthenticationResult(
            outcome=AuthenticationOutcome.FAILURE,
            security_flags=["brute_force_detected"],
        )
        await publisher.publish_authentication_failed(result)
        event = event_bus.get_event_log()[0]
        assert event.severity == EventSeverity.ERROR


class TestPublishRegistrationEvents:
    @pytest.mark.asyncio
    async def test_registration_requested(self, publisher, event_bus):
        await publisher.publish_registration_requested("bob", "corr-4")
        log = event_bus.get_event_log(event_type=EventType.REGISTRATION_REQUESTED)
        assert len(log) == 1
        assert log[0].metadata["username"] == "bob"

    @pytest.mark.asyncio
    async def test_registration_completed(self, publisher, event_bus):
        result = AuthenticationResult(
            outcome=AuthenticationOutcome.SUCCESS,
            user_id="u2",
            username="bob",
        )
        await publisher.publish_registration_completed(result)
        log = event_bus.get_event_log(event_type=EventType.REGISTRATION_COMPLETED)
        assert len(log) == 1


class TestPublishSessionEvents:
    @pytest.mark.asyncio
    async def test_session_created(self, publisher, event_bus):
        await publisher.publish_session_created("sess-1", "u1", "corr-5")
        log = event_bus.get_event_log(event_type=EventType.SESSION_CREATED)
        assert len(log) == 1
        assert log[0].session_id == "sess-1"

    @pytest.mark.asyncio
    async def test_session_expired(self, publisher, event_bus):
        await publisher.publish_session_expired("sess-1", "u1")
        log = event_bus.get_event_log(event_type=EventType.SESSION_EXPIRED)
        assert len(log) == 1

    @pytest.mark.asyncio
    async def test_session_destroyed(self, publisher, event_bus):
        await publisher.publish_session_destroyed("sess-1", "u1")
        log = event_bus.get_event_log(event_type=EventType.SESSION_DESTROYED)
        assert len(log) == 1

    @pytest.mark.asyncio
    async def test_logout(self, publisher, event_bus):
        await publisher.publish_logout("u1", "sess-1", "corr-6")
        log = event_bus.get_event_log(event_type=EventType.SESSION_DESTROYED)
        assert len(log) == 1
        assert log[0].metadata["termination_reason"] == "logout"


class TestPublisherErrorHandling:
    @pytest.mark.asyncio
    async def test_publish_does_not_raise_on_handler_failure(self, publisher, event_bus):
        async def failing_handler(event):
            raise RuntimeError("handler broke")

        event_bus.subscribe(EventType.AUTHENTICATION_REQUESTED, failing_handler)
        await publisher.publish_authentication_requested("alice", "corr-7")
        assert len(event_bus.get_event_log()) == 1

    @pytest.mark.asyncio
    async def test_publish_does_not_raise_on_bus_failure(self, publisher):
        bus = AsyncMock()
        bus.publish = AsyncMock(side_effect=RuntimeError("bus error"))
        publisher._event_bus = bus
        await publisher.publish_authentication_requested("alice", "corr-8")
        bus.publish.assert_called_once()
