"""User domain entities."""

from .identity_lifecycle import (
    VALID_LIFECYCLE_TRANSITIONS,
    LifecycleTransition,
    UserLifecycleState,
    can_transition,
    validate_transition,
)
from .permission import PermissionEntity
from .role import RoleEntity
from .user_profile import UserProfile

__all__ = [
    "VALID_LIFECYCLE_TRANSITIONS",
    "LifecycleTransition",
    "PermissionEntity",
    "RoleEntity",
    "UserLifecycleState",
    "UserProfile",
    "can_transition",
    "validate_transition",
]
