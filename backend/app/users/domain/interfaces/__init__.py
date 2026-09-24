"""User domain interfaces."""

from .device_service import IDeviceService
from .identity_service import IIdentityService
from .preference_service import IPreferenceService
from .role_service import IRoleService

__all__ = [
    "IDeviceService",
    "IIdentityService",
    "IPreferenceService",
    "IRoleService",
]
