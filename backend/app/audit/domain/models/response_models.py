"""Pydantic response models for the audit API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AuditEntryResponse(BaseModel):
    """Single audit entry for API responses."""

    audit_id: str = ""
    event_id: str = ""
    correlation_id: str = ""
    timestamp: str | None = None
    user_id: str | None = None
    username: str | None = None
    administrator_id: str | None = None
    module: str = ""
    event_type: str = ""
    severity: str = "info"
    description: str = ""
    resource_type: str | None = None
    resource_id: str | None = None
    previous_state: dict | None = None
    new_state: dict | None = None
    metadata: dict | None = None
    result: str = "success"
    ip_address: str = "127.0.0.1"


class AuditListResponse(BaseModel):
    """Paginated list of audit entries."""

    status: str = "success"
    items: list[AuditEntryResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
    pages: int = 0


class AuditStatsResponse(BaseModel):
    """Audit statistics."""

    total_events: int = 0
    events_by_module: dict[str, int] = Field(default_factory=dict)
    events_by_severity: dict[str, int] = Field(default_factory=dict)
    events_by_type: dict[str, int] = Field(default_factory=dict)
    events_by_result: dict[str, int] = Field(default_factory=dict)
    unique_users: int = 0
    events_today: int = 0
    average_events_per_day: float = 0.0
