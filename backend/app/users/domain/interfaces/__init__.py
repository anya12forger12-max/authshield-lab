"""User domain interfaces."""

from .identity_service import IIdentityService
from .role_service import IRoleService
from .preference_service import IPreferenceService
from .device_service import IDeviceService

__all__ = [
    "IIdentityService",
    "IRoleService",
    "IPreferenceService",
    "IDeviceService",
]
