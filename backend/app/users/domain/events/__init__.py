"""User domain events."""

from .identity_events import (
    DeviceRegisteredEvent,
    DeviceRemovedEvent,
    IdentityEvent,
    PreferenceChangedEvent,
    ProfileUpdatedEvent,
    RoleAssignedEvent,
    RoleRemovedEvent,
    UserCreatedEvent,
    UserDeletedEvent,
    UserStatusChangedEvent,
    UserUpdatedEvent,
)

__all__ = [
    "DeviceRegisteredEvent",
    "DeviceRemovedEvent",
    "IdentityEvent",
    "PreferenceChangedEvent",
    "ProfileUpdatedEvent",
    "RoleAssignedEvent",
    "RoleRemovedEvent",
    "UserCreatedEvent",
    "UserDeletedEvent",
    "UserStatusChangedEvent",
    "UserUpdatedEvent",
]
