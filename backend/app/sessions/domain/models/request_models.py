"""Pydantic request models for the sessions API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TerminateSessionRequest(BaseModel):
    """Request body for terminating a session."""

    reason: str = Field(default="user_request", max_length=256)


class SessionSearchRequest(BaseModel):
    """Request body for searching sessions."""

    user_id: str | None = None
    status: str | None = None
    platform: str | None = None
    authentication_method: str | None = None
    ip_address: str | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class SessionFilters(BaseModel):
    """Query filters for session listing."""

    user_id: str | None = None
    status: str | None = None
    include_expired: bool = False
