"""Pydantic request models for the sessions API."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class TerminateSessionRequest(BaseModel):
    """Request body for terminating a session."""

    reason: str = Field(default="user_request", max_length=256)


class SessionSearchRequest(BaseModel):
    """Request body for searching sessions."""

    user_id: Optional[str] = None
    status: Optional[str] = None
    platform: Optional[str] = None
    authentication_method: Optional[str] = None
    ip_address: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class SessionFilters(BaseModel):
    """Query filters for session listing."""

    user_id: Optional[str] = None
    status: Optional[str] = None
    include_expired: bool = False
