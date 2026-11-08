"""Pydantic response models for the sessions API."""

from __future__ import annotations

from typing import Optional, Any
from pydantic import BaseModel, Field


class SessionDetailResponse(BaseModel):
    """Full session detail for API responses."""

    session_id: str = ""
    user_id: str = ""
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    last_activity: Optional[str] = None
    status: str = "active"
    authentication_method: str = "password"
    platform: Optional[str] = None
    device_name: Optional[str] = None
    ip_address: str = "127.0.0.1"
    is_expired: bool = False
    is_idle: bool = False
    duration_minutes: float = 0.0


class SessionListResponse(BaseModel):
    """Paginated list of sessions."""

    status: str = "success"
    items: list[SessionDetailResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
    pages: int = 0


class SessionStatsResponse(BaseModel):
    """Session statistics."""

    total_sessions: int = 0
    active_sessions: int = 0
    expired_sessions: int = 0
    idle_sessions: int = 0
    revoked_sessions: int = 0
    unique_users: int = 0
    average_duration_minutes: float = 0.0
    most_active_platform: str = ""
    most_common_auth_method: str = ""
