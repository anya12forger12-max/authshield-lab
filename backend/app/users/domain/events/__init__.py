"""User domain events."""

from .identity_events import (
    IdentityEvent,
    UserCreatedEvent,
    UserUpdatedEvent,
    UserDeletedEvent,
    UserStatusChangedEvent,
    RoleAssignedEvent,
    RoleRemovedEvent,
    ProfileUpdatedEvent,
    PreferenceChangedEvent,
    DeviceRegisteredEvent,
    DeviceRemovedEvent,
)

__all__ = [
    "IdentityEvent",
    "UserCreatedEvent",
    "UserUpdatedEvent",
    "UserDeletedEvent",
    "UserStatusChangedEvent",
    "RoleAssignedEvent",
    "RoleRemovedEvent",
    "ProfileUpdatedEvent",
    "PreferenceChangedEvent",
    "DeviceRegisteredEvent",
    "DeviceRemovedEvent",
]
