"""User domain entities."""

from .user_profile import UserProfile
from .role import RoleEntity
from .permission import PermissionEntity
from .identity_lifecycle import (
    UserLifecycleState,
    LifecycleTransition,
    VALID_LIFECYCLE_TRANSITIONS,
    can_transition,
    validate_transition,
)

__all__ = [
    "UserProfile",
    "RoleEntity",
    "PermissionEntity",
    "UserLifecycleState",
    "LifecycleTransition",
    "VALID_LIFECYCLE_TRANSITIONS",
    "can_transition",
    "validate_transition",
]
