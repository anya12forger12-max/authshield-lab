"""Complete event type registry for all AuthShieldLab modules."""

from __future__ import annotations

from .event_bus import EventType

EVENT_CATEGORIES: dict[str, list[EventType]] = {
    "authentication": [
        EventType.AUTHENTICATION_REQUESTED,
        EventType.AUTHENTICATION_SUCCEEDED,
        EventType.AUTHENTICATION_FAILED,
    ],
    "registration": [
        EventType.REGISTRATION_REQUESTED,
        EventType.REGISTRATION_COMPLETED,
        EventType.REGISTRATION_FAILED,
    ],
    "session": [
        EventType.SESSION_CREATED,
        EventType.SESSION_EXPIRED,
        EventType.SESSION_DESTROYED,
        EventType.SESSION_RENEWED,
        EventType.SESSION_REVOKED,
    ],
    "user": [
        EventType.USER_CREATED,
        EventType.USER_UPDATED,
        EventType.USER_DELETED,
        EventType.USER_STATUS_CHANGED,
        EventType.USER_PROFILE_UPDATED,
        EventType.USER_PREFERENCES_CHANGED,
    ],
    "role": [
        EventType.ROLE_ASSIGNED,
        EventType.ROLE_REMOVED,
        EventType.ROLE_CREATED,
        EventType.ROLE_UPDATED,
    ],
    "password": [
        EventType.PASSWORD_VERIFIED,
        EventType.PASSWORD_CHANGED,
        EventType.PASSWORD_POLICY_VIOLATION,
    ],
    "audit": [
        EventType.AUDIT_EVENT,
        EventType.AUDIT_LOGGED,
    ],
    "policy": [
        EventType.POLICY_EVALUATED,
        EventType.POLICY_DECISION,
        EventType.POLICY_REGISTERED,
        EventType.POLICY_ENABLED,
        EventType.POLICY_DISABLED,
    ],
    "config": [
        EventType.CONFIG_CHANGED,
        EventType.CONFIG_VALIDATED,
    ],
    "system": [
        EventType.APPLICATION_STARTED,
        EventType.APPLICATION_STOPPED,
        EventType.ERROR_OCCURRED,
    ],
}


def get_events_by_category(category: str) -> list[EventType]:
    """Return all event types belonging to *category*.

    Parameters
    ----------
    category:
        One of the keys in :data:`EVENT_CATEGORIES`.

    Raises
    ------
    KeyError
        If *category* does not exist in the registry.
    """
    return list(EVENT_CATEGORIES[category])


def get_all_categories() -> list[str]:
    """Return a sorted list of all registered category names."""
    return sorted(EVENT_CATEGORIES.keys())
