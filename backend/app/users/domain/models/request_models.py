"""Pydantic request models for the users API."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    """Request body for updating a user profile."""

    display_name: Optional[str] = Field(default=None, max_length=64)
    email: Optional[str] = Field(default=None, max_length=254)
    bio: Optional[str] = Field(default=None, max_length=1024)
    profile_picture: Optional[str] = Field(default=None, max_length=512)


class UserSearchRequest(BaseModel):
    """Request body for searching users."""

    query: str = Field(default="", max_length=128)
    role: Optional[str] = None
    status: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at")
    descending: bool = Field(default=True)


class UpdateStatusRequest(BaseModel):
    """Request body for updating a user's account status."""

    status: str = Field(..., max_length=32)
    reason: str = Field(default="", max_length=512)


class AssignRoleRequest(BaseModel):
    """Request body for assigning a role to a user."""

    role_name: str = Field(..., max_length=32)


class UpdatePreferencesRequest(BaseModel):
    """Request body for updating user preferences."""

    theme: Optional[str] = Field(default=None, max_length=32)
    accent_color: Optional[str] = Field(default=None, max_length=32)
    language: Optional[str] = Field(default=None, max_length=10)
    accessibility: Optional[dict] = None
    notifications: Optional[dict] = None


class ExportRequest(BaseModel):
    """Request body for exporting user data."""

    format: str = Field(default="json", pattern="^(json|csv)$")


class AdminCreateUserRequest(BaseModel):
    """Request body for admin user creation."""

    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=64)
    email: Optional[str] = Field(default=None, max_length=254)
    role: str = Field(default="student", max_length=32)
