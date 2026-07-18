"""Authentication response models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AuthenticationResponse(BaseModel):
    """Base response for authentication operations."""

    success: bool
    message: str = ""
    error_code: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class RegistrationResponse(AuthenticationResponse):
    """Response for user registration."""

    user_id: str | None = None
    username: str | None = None


class LoginResponse(AuthenticationResponse):
    """Response for user login."""

    access_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None
    session_id: str | None = None
    user: dict[str, Any] | None = None


class LogoutResponse(AuthenticationResponse):
    """Response for user logout."""

    session_terminated: bool = False


class SessionResponse(BaseModel):
    """Response for session information."""

    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    status: str
    authentication_method: str | None = None
    platform: str | None = None
    is_current: bool = False
