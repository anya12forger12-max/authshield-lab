"""Identity domain events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class IdentityEvent:
    """Base class for all identity domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = ""
    module: str = "users"
    severity: str = "info"
    user_id: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class UserCreatedEvent(IdentityEvent):
    """Published when a new user account is created."""

    event_type: str = "user.created"


@dataclass
class UserUpdatedEvent(IdentityEvent):
    """Published when user data is updated."""

    event_type: str = "user.updated"
    changed_fields: list[str] = field(default_factory=list)


@dataclass
class UserDeletedEvent(IdentityEvent):
    """Published when a user is deleted (soft or hard)."""

    event_type: str = "user.deleted"


@dataclass
class UserStatusChangedEvent(IdentityEvent):
    """Published when a user's account status changes."""

    event_type: str = "user.status_changed"
    previous_status: str = ""
    new_status: str = ""
    reason: str = ""


@dataclass
class RoleAssignedEvent(IdentityEvent):
    """Published when a role is assigned to a user."""

    event_type: str = "role.assigned"
    role_name: str = ""


@dataclass
class RoleRemovedEvent(IdentityEvent):
    """Published when a role is removed from a user."""

    event_type: str = "role.removed"
    role_name: str = ""


@dataclass
class ProfileUpdatedEvent(IdentityEvent):
    """Published when user profile fields are updated."""

    event_type: str = "user.profile_updated"
    changed_fields: list[str] = field(default_factory=list)


@dataclass
class PreferenceChangedEvent(IdentityEvent):
    """Published when user preferences are changed."""

    event_type: str = "user.preferences_changed"
    preference_type: str = ""


@dataclass
class DeviceRegisteredEvent(IdentityEvent):
    """Published when a new device is registered for a user."""

    event_type: str = "device.registered"
    device_id: str = ""


@dataclass
class DeviceRemovedEvent(IdentityEvent):
    """Published when a device is removed from a user."""

    event_type: str = "device.removed"
    device_id: str = ""
