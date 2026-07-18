"""Authentication request models with validation."""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegistrationRequest(BaseModel):
    """Request payload for user registration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(
        ..., min_length=4, max_length=32, description="Username"
    )
    password: str = Field(
        ..., min_length=8, max_length=128, description="Password"
    )
    confirm_password: str = Field(
        ..., min_length=8, max_length=128, description="Password confirmation"
    )
    display_name: str = Field(
        ..., min_length=1, max_length=64, description="Display name"
    )
    email: str | None = Field(None, max_length=254, description="Optional email")

    @field_validator("username")
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Username must be alphanumeric with underscores/hyphens only."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username may only contain letters, digits, underscores, and hyphens."
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password_not_empty(cls, v: str) -> str:
        """Ensure password is not whitespace-only after stripping."""
        if not v or not v.strip():
            raise ValueError("Password cannot be empty or whitespace-only.")
        return v

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str) -> str:
        """Display name must not be empty after stripping."""
        if not v or not v.strip():
            raise ValueError("Display name cannot be empty.")
        return v.strip()


class LoginRequest(BaseModel):
    """Request payload for user login."""

    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(..., min_length=1, max_length=32)
    password: str = Field(..., min_length=1, max_length=128)
    remember_me: bool = Field(default=False)
    device_id: str | None = Field(None, max_length=128)
    platform: str | None = Field(None, max_length=64)


class LogoutRequest(BaseModel):
    """Request payload for user logout."""

    session_id: str | None = None
    terminate_all: bool = False


class SessionValidationRequest(BaseModel):
    """Request payload for session validation."""

    session_id: str = Field(..., min_length=1)
    user_id: str | None = None


class SessionRenewalRequest(BaseModel):
    """Request payload for session renewal."""

    session_id: str = Field(..., min_length=1)
    extend_idle_timeout: bool = True


class PasswordChangeRequest(BaseModel):
    """Request payload for password change."""

    model_config = ConfigDict(str_strip_whitespace=True)

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
