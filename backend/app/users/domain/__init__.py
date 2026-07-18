"""User domain layer."""

from .entities import (
    UserProfile,
    RoleEntity,
    PermissionEntity,
    UserLifecycleState,
    LifecycleTransition,
    can_transition,
    validate_transition,
)
from .interfaces import (
    IIdentityService,
    IRoleService,
    IPreferenceService,
    IDeviceService,
)

__all__ = [
    "UserProfile",
    "RoleEntity",
    "PermissionEntity",
    "UserLifecycleState",
    "LifecycleTransition",
    "can_transition",
    "validate_transition",
    "IIdentityService",
    "IRoleService",
    "IPreferenceService",
    "IDeviceService",
]
