"""Event bus infrastructure for cross-cutting module communication."""

from .event_bus import (
    DomainEvent,
    EventBus,
    EventHandler,
    EventSeverity,
    EventType,
    get_event_bus,
    reset_event_bus,
)
from .domain_event_types import (
    EVENT_CATEGORIES,
    get_all_categories,
    get_events_by_category,
)

__all__ = [
    "DomainEvent",
    "EventBus",
    "EventHandler",
    "EventSeverity",
    "EventType",
    "EVENT_CATEGORIES",
    "get_all_categories",
    "get_event_bus",
    "get_events_by_category",
    "reset_event_bus",
]
