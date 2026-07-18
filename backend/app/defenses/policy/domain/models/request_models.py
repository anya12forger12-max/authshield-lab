"""Policy request models with validation."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CreatePolicyRequest(BaseModel):
    """Request payload for creating a new policy."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=128, description="Policy name")
    description: str = Field(default="", max_length=512, description="Policy description")
    category: str = Field(default="authentication", description="Policy category")
    priority: int = Field(default=100, ge=1, le=1000, description="Evaluation priority (lower = higher)")
    author: str = Field(default="system", max_length=64, description="Policy author")
    configuration: dict[str, Any] = Field(default_factory=dict, description="Policy-specific configuration")
    dependencies: list[str] = Field(default_factory=list, description="Policy IDs this depends on")
    risk_weight: float = Field(default=1.0, ge=0.0, le=10.0, description="Risk score multiplier")
    supported_event_types: list[str] = Field(default_factory=list, description="Event types this policy handles")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")


class UpdatePolicyRequest(BaseModel):
    """Request payload for updating an existing policy."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = Field(None, max_length=512)
    category: str | None = None
    priority: int | None = Field(None, ge=1, le=1000)
    configuration: dict[str, Any] | None = None
    dependencies: list[str] | None = None
    risk_weight: float | None = Field(None, ge=0.0, le=10.0)
    supported_event_types: list[str] | None = None
    metadata: dict[str, Any] | None = None


class EvaluatePolicyRequest(BaseModel):
    """Request payload for evaluating an event against policies."""

    model_config = ConfigDict(str_strip_whitespace=True)

    event_type: str = Field(..., min_length=1, description="Event type to evaluate")
    context: dict[str, Any] = Field(default_factory=dict, description="Evaluation context")
    correlation_id: str = Field(default="", description="Correlation ID for tracing")


class PolicySearchRequest(BaseModel):
    """Request payload for searching policies."""

    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(default="", description="Search query")
    category: str | None = Field(None, description="Filter by category")
    status: str | None = Field(None, description="Filter by status")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")
