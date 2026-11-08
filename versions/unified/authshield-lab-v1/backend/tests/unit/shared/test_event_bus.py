"""Tests for EventBus: subscribe, publish, unsubscribe, event log."""

import pytest
from unittest.mock import AsyncMock

from app.shared.events.event_bus import (
    EventBus,
    EventType,
    EventSeverity,
    DomainEvent,
    get_event_bus,
    reset_event_bus,
)


@pytest.fixture
def bus():
    return EventBus()


class TestSubscribe:
    def test_subscribe_single_handler(self, bus):
        handler = AsyncMock()
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, handler)
        assert bus.subscriber_count(EventType.AUTHENTICATION_SUCCEEDED) == 1

    def test_subscribe_multiple_handlers(self, bus):
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, AsyncMock())
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, AsyncMock())
        assert bus.subscriber_count(EventType.AUTHENTICATION_SUCCEEDED) == 2

    def test_subscribe_no_duplicates(self, bus):
        handler = AsyncMock()
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, handler)
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, handler)
        assert bus.subscriber_count(EventType.AUTHENTICATION_SUCCEEDED) == 1

    def test_get_subscribed_types(self, bus):
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, AsyncMock())
        bus.subscribe(EventType.SESSION_CREATED, AsyncMock())
        types = bus.get_subscribed_types()
        assert EventType.AUTHENTICATION_SUCCEEDED in types
        assert EventType.SESSION_CREATED in types


class TestUnsubscribe:
    def test_unsubscribe(self, bus):
        handler = AsyncMock()
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, handler)
        bus.unsubscribe(EventType.AUTHENTICATION_SUCCEEDED, handler)
        assert bus.subscriber_count(EventType.AUTHENTICATION_SUCCEEDED) == 0

    def test_unsubscribe_nonexistent_handler(self, bus):
        bus.unsubscribe(EventType.AUTHENTICATION_SUCCEEDED, AsyncMock())

    def test_unsubscribe_nonexistent_event_type(self, bus):
        bus.unsubscribe(EventType.APPLICATION_STARTED, AsyncMock())


class TestPublish:
    @pytest.mark.asyncio
    async def test_publish_calls_handler(self, bus):
        handler = AsyncMock()
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, handler)
        event = DomainEvent(event_type=EventType.AUTHENTICATION_SUCCEEDED)
        await bus.publish(event)
        handler.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_publish_multiple_handlers(self, bus):
        h1 = AsyncMock()
        h2 = AsyncMock()
        bus.subscribe(EventType.SESSION_CREATED, h1)
        bus.subscribe(EventType.SESSION_CREATED, h2)
        event = DomainEvent(event_type=EventType.SESSION_CREATED)
        await bus.publish(event)
        h1.assert_called_once()
        h2.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_no_subscribers(self, bus):
        event = DomainEvent(event_type=EventType.SESSION_CREATED)
        await bus.publish(event)

    @pytest.mark.asyncio
    async def test_publish_handler_exception_does_not_propagate(self, bus):
        async def failing_handler(event):
            raise RuntimeError("oops")

        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, failing_handler)
        event = DomainEvent(event_type=EventType.AUTHENTICATION_SUCCEEDED)
        await bus.publish(event)

    @pytest.mark.asyncio
    async def test_publish_other_handlers_still_run_after_failure(self, bus):
        async def failing_handler(event):
            raise RuntimeError("oops")

        good_handler = AsyncMock()
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, failing_handler)
        bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, good_handler)
        event = DomainEvent(event_type=EventType.AUTHENTICATION_SUCCEEDED)
        await bus.publish(event)
        good_handler.assert_called_once()


class TestEventLog:
    @pytest.mark.asyncio
    async def test_events_logged(self, bus):
        event = DomainEvent(event_type=EventType.SESSION_CREATED, module="test")
        await bus.publish(event)
        log = bus.get_event_log()
        assert len(log) == 1

    @pytest.mark.asyncio
    async def test_event_log_filtered_by_type(self, bus):
        e1 = DomainEvent(event_type=EventType.AUTHENTICATION_SUCCEEDED)
        e2 = DomainEvent(event_type=EventType.SESSION_CREATED)
        await bus.publish(e1)
        await bus.publish(e2)
        log = bus.get_event_log(event_type=EventType.SESSION_CREATED)
        assert len(log) == 1
        assert log[0].event_type == EventType.SESSION_CREATED

    @pytest.mark.asyncio
    async def test_event_log_limit(self, bus):
        for _ in range(5):
            await bus.publish(DomainEvent(event_type=EventType.SESSION_CREATED))
        log = bus.get_event_log(limit=3)
        assert len(log) == 3

    def test_clear_log(self, bus):
        bus.clear_log()
        assert bus.get_event_log() == []

    @pytest.mark.asyncio
    async def test_log_max_size(self):
        small_bus = EventBus(max_log_size=3)
        for _ in range(5):
            await small_bus.publish(DomainEvent(event_type=EventType.SESSION_CREATED))
        log = small_bus.get_event_log()
        assert len(log) == 3


class TestModuleSingleton:
    def test_get_event_bus_returns_singleton(self):
        reset_event_bus()
        b1 = get_event_bus()
        b2 = get_event_bus()
        assert b1 is b2

    def test_reset_event_bus(self):
        b1 = get_event_bus()
        reset_event_bus()
        b2 = get_event_bus()
        assert b1 is not b2
