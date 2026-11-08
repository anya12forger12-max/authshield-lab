"""Pydantic request models for the audit API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AuditSearchRequest(BaseModel):
    """Request body for searching audit events."""

    user_id: str | None = None
    module: str | None = None
    event_type: str | None = None
    severity: str | None = None
    result: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class AuditFilters(BaseModel):
    """Query filters for audit listing."""

    user_id: str | None = None
    module: str | None = None
    event_type: str | None = None
    severity: str | None = None
    result: str | None = None
    correlation_id: str | None = None
