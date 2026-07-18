"""Shared repository layer."""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .session_repository import SessionRepository
from .audit_repository import AuditRepository
from .role_repository import RoleRepository
from .preference_repository import PreferenceRepository
from .device_repository import DeviceRepository
from .authentication_attempt_repository import AuthenticationAttemptRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "SessionRepository",
    "AuditRepository",
    "RoleRepository",
    "PreferenceRepository",
    "DeviceRepository",
    "AuthenticationAttemptRepository",
]
