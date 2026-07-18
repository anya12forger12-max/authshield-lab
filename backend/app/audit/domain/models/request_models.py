"""Pydantic request models for the audit API."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class AuditSearchRequest(BaseModel):
    """Request body for searching audit events."""

    user_id: Optional[str] = None
    module: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[str] = None
    result: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class AuditFilters(BaseModel):
    """Query filters for audit listing."""

    user_id: Optional[str] = None
    module: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[str] = None
    result: Optional[str] = None
    correlation_id: Optional[str] = None
