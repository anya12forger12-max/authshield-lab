"""Pydantic response models for the users API."""

from __future__ import annotations

from typing import Optional, Any
from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    """Safe user profile data for API responses."""

    user_id: str = ""
    username: str = ""
    display_name: str = ""
    email: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    account_status: str = "active"
    role: str = "student"
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    last_login: Optional[str] = None
    login_count: int = 0
    preferred_language: str = "en"
    preferred_theme: str = "dark"
    timezone: str = "UTC"
    mfa_enabled: bool = False
    active_session_count: int = 0


class UserListResponse(BaseModel):
    """Paginated list of user profiles."""

    status: str = "success"
    items: list[UserProfileResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
    pages: int = 0


class RoleResponse(BaseModel):
    """Role data with permissions."""

    role_id: str = ""
    name: str = ""
    display_name: str = ""
    description: str = ""
    is_builtin: bool = False
    is_active: bool = True
    version: int = 1
    permissions: list[str] = Field(default_factory=list)
    created_at: Optional[str] = None


class RoleListResponse(BaseModel):
    """Paginated list of roles."""

    status: str = "success"
    items: list[RoleResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
    pages: int = 0


class PreferenceResponse(BaseModel):
    """User preference data."""

    user_id: str = ""
    theme: str = "dark"
    accent_color: str = ""
    language: str = "en"
    timezone: str = "UTC"
    accessibility: dict[str, Any] = Field(default_factory=dict)
    notifications: dict[str, Any] = Field(default_factory=dict)


class DeviceResponse(BaseModel):
    """Device data."""

    device_id: str = ""
    user_id: str = ""
    device_name: str = ""
    device_type: str = ""
    platform: str = ""
    is_active: bool = True
    is_trusted: bool = False
    last_seen: Optional[str] = None
    registered_at: Optional[str] = None


class DeviceListResponse(BaseModel):
    """List of devices."""

    status: str = "success"
    items: list[DeviceResponse] = Field(default_factory=list)
    total: int = 0


class AdminUserResponse(BaseModel):
    """Full admin-level user data."""

    user_id: str = ""
    username: str = ""
    display_name: str = ""
    email: Optional[str] = None
    account_status: str = "active"
    role: str = "student"
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    last_login: Optional[str] = None
    login_count: int = 0
    failed_login_count: int = 0
    security_score: int = 50
    mfa_enabled: bool = False
    trusted_device_count: int = 0
    active_session_count: int = 0
    audit_history_count: int = 0
    password_last_changed: Optional[str] = None
    password_algorithm: str = ""
    password_version: int = 0
