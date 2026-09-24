"""User domain layer."""

from .entities import (
    LifecycleTransition,
    PermissionEntity,
    RoleEntity,
    UserLifecycleState,
    UserProfile,
    can_transition,
    validate_transition,
)
from .interfaces import (
    IDeviceService,
    IIdentityService,
    IPreferenceService,
    IRoleService,
)

__all__ = [
    "IDeviceService",
    "IIdentityService",
    "IPreferenceService",
    "IRoleService",
    "LifecycleTransition",
    "PermissionEntity",
    "RoleEntity",
    "UserLifecycleState",
    "UserProfile",
    "can_transition",
    "validate_transition",
]
