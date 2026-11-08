"""Policy response models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class PolicyResponse(BaseModel):
    """Response for a single policy."""

    policy_id: str
    name: str
    description: str = ""
    category: str
    priority: int = 100
    status: str = "draft"
    version: int = 1
    author: str = "system"
    configuration: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)
    risk_weight: float = 1.0
    supported_event_types: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


class PolicyListResponse(BaseModel):
    """Paginated list of policies."""

    status: str = Field(default="success")
    items: list[PolicyResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 20
    pages: int = 0


class PolicyDecisionResponse(BaseModel):
    """Response for a policy evaluation result."""

    decision_id: str = ""
    policy_id: str = ""
    rule_id: str = ""
    result: str = "unknown"
    reason: str = ""
    severity: str = "info"
    risk_score: float = 0.0
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PolicyMetricsResponse(BaseModel):
    """Response for policy engine metrics."""

    total_evaluations: int = 0
    evaluations_by_policy: dict[str, int] = Field(default_factory=dict)
    evaluations_by_result: dict[str, int] = Field(default_factory=dict)
    average_evaluation_time_ms: float = 0.0
    total_policies: int = 0
    active_policies: int = 0
    error_count: int = 0
