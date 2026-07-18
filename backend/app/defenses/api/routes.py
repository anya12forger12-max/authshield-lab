"""Security policy management API routes."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from ..policy.domain.entities.policy_entity import PolicyCategory, PolicyStatus
from ..policy.domain.models.request_models import (
    CreatePolicyRequest,
    EvaluatePolicyRequest,
    PolicySearchRequest,
    UpdatePolicyRequest,
)
from ..policy.domain.models.response_models import (
    PolicyDecisionResponse,
    PolicyListResponse,
    PolicyMetricsResponse,
    PolicyResponse,
)
from ..policy.validators.policy_validator import (
    validate_policy_data,
    validate_status_transition,
)
from ...shared.responses import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/policies", tags=["policies"])

# ---------------------------------------------------------------------------
# These will be injected at application startup.  For now they are
# module-level singletons that are lazily created on first request.
# ---------------------------------------------------------------------------
_engine: Any = None
_registry: Any = None


def _get_engine() -> Any:
    """Lazy-load the policy engine."""
    global _engine  # noqa: PLW0603
    if _engine is None:
        from ..policy.services.policy_engine import PolicyEngine
        from ..policy.registry.policy_registry import PolicyRegistry
        from ...shared.events.event_bus import get_event_bus
        from ...shared.monitoring.performance import get_performance_monitor

        registry = PolicyRegistry()
        _engine = PolicyEngine(
            registry=registry,
            event_bus=get_event_bus(),
            performance_monitor=get_performance_monitor(),
        )
    return _engine


def _get_registry() -> Any:
    """Lazy-load the policy registry."""
    global _registry  # noqa: PLW0603
    if _registry is None:
        from ..policy.registry.policy_registry import PolicyRegistry
        _registry = PolicyRegistry()
    return _registry


def _policy_to_response(policy: Any) -> PolicyResponse:
    """Convert a SecurityPolicy entity to a PolicyResponse model."""
    config_dict = policy.configuration.to_dict() if hasattr(policy.configuration, "to_dict") else {}
    return PolicyResponse(
        policy_id=policy.policy_id,
        name=policy.name,
        description=policy.description,
        category=policy.category.value,
        priority=policy.priority,
        status=policy.status.value,
        version=policy.version,
        author=policy.author,
        configuration=config_dict,
        dependencies=list(policy.dependencies),
        risk_weight=policy.risk_weight,
        supported_event_types=list(policy.supported_event_types),
        metadata=dict(policy.metadata),
        created_at=policy.created_at.isoformat(),
        updated_at=policy.updated_at.isoformat(),
    )


# ------------------------------------------------------------------
# List policies
# ------------------------------------------------------------------

@router.get("", response_model=PolicyListResponse)
async def list_policies(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> PolicyListResponse:
    """List all policies with optional filtering and pagination."""
    engine = _get_engine()

    cat = PolicyCategory(category) if category else None
    stat = PolicyStatus(status) if status else None

    all_policies = await engine.list_policies(category=cat, status=stat)

    total = len(all_policies)
    pages = max(1, (total + per_page - 1) // per_page)
    offset = (page - 1) * per_page
    page_items = all_policies[offset : offset + per_page]

    return PolicyListResponse(
        items=[_policy_to_response(p) for p in page_items],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


# ------------------------------------------------------------------
# Create policy
# ------------------------------------------------------------------

@router.post("", response_model=PolicyResponse, status_code=201)
async def create_policy(request: CreatePolicyRequest) -> PolicyResponse:
    """Create a new security policy."""
    engine = _get_engine()

    data = request.model_dump()
    validation = validate_policy_data(data)
    if not validation.is_valid:
        raise HTTPException(
            status_code=422,
            detail=validation.to_dict(),
        )

    from ..policy.domain.entities.policy_entity import (
        PolicyConfiguration,
        PolicyStatus,
        SecurityPolicy,
    )
    from ..policy.domain.entities.policy_entity import PolicyCategory as PC

    config_data = data.pop("configuration", {})
    configuration = PolicyConfiguration.from_dict(config_data)

    policy = SecurityPolicy(
        name=data["name"],
        description=data.get("description", ""),
        category=PC(data.get("category", "authentication")),
        priority=data.get("priority", 100),
        author=data.get("author", "system"),
        configuration=configuration,
        dependencies=data.get("dependencies", []),
        risk_weight=data.get("risk_weight", 1.0),
        supported_event_types=data.get("supported_event_types", []),
        metadata=data.get("metadata", {}),
    )

    success = await engine.register_policy(policy)
    if not success:
        raise HTTPException(status_code=409, detail="Policy already exists")

    return _policy_to_response(policy)


# ------------------------------------------------------------------
# Get policy
# ------------------------------------------------------------------

@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str) -> PolicyResponse:
    """Retrieve a single policy by ID."""
    engine = _get_engine()

    policy = await engine.get_policy(policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_id}' not found")

    return _policy_to_response(policy)


# ------------------------------------------------------------------
# Update policy
# ------------------------------------------------------------------

@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str, request: UpdatePolicyRequest
) -> PolicyResponse:
    """Update an existing policy's configuration."""
    engine = _get_engine()

    existing = await engine.get_policy(policy_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_id}' not found")

    data = request.model_dump(exclude_unset=True)
    validation = validate_policy_data({**existing.to_dict(), **data})
    if not validation.is_valid:
        raise HTTPException(status_code=422, detail=validation.to_dict())

    updated = await engine.update_policy(policy_id, data)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update policy")

    return _policy_to_response(updated)


# ------------------------------------------------------------------
# Delete policy
# ------------------------------------------------------------------

@router.delete("/{policy_id}")
async def delete_policy(policy_id: str) -> SuccessResponse:
    """Delete a policy."""
    engine = _get_engine()

    success = await engine.unregister_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_id}' not found")

    return SuccessResponse(
        message=f"Policy '{policy_id}' deleted successfully",
        data={"policy_id": policy_id},
    )


# ------------------------------------------------------------------
# Enable / disable
# ------------------------------------------------------------------

@router.post("/{policy_id}/enable", response_model=PolicyResponse)
async def enable_policy(policy_id: str) -> PolicyResponse:
    """Enable a policy."""
    engine = _get_engine()

    policy = await engine.get_policy(policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_id}' not found")

    validation = validate_status_transition(policy.status.value, "enabled")
    if not validation.is_valid:
        raise HTTPException(status_code=422, detail=validation.to_dict())

    success = await engine.enable_policy(policy_id)
    if not success:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot enable policy in '{policy.status.value}' status",
        )

    updated = await engine.get_policy(policy_id)
    return _policy_to_response(updated)


@router.post("/{policy_id}/disable", response_model=PolicyResponse)
async def disable_policy(policy_id: str) -> PolicyResponse:
    """Disable a policy."""
    engine = _get_engine()

    policy = await engine.get_policy(policy_id)
    if policy is None:
        raise HTTPException(status_code=404, detail=f"Policy '{policy_id}' not found")

    validation = validate_status_transition(policy.status.value, "disabled")
    if not validation.is_valid:
        raise HTTPException(status_code=422, detail=validation.to_dict())

    success = await engine.disable_policy(policy_id)
    if not success:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot disable policy in '{policy.status.value}' status",
        )

    updated = await engine.get_policy(policy_id)
    return _policy_to_response(updated)


# ------------------------------------------------------------------
# Evaluate
# ------------------------------------------------------------------

@router.post("/evaluate", response_model=list[PolicyDecisionResponse])
async def evaluate_policies(request: EvaluatePolicyRequest) -> list[PolicyDecisionResponse]:
    """Evaluate an event against all applicable policies."""
    engine = _get_engine()

    decisions = await engine.evaluate(
        event_type=request.event_type,
        context=request.context,
        correlation_id=request.correlation_id,
    )

    return [
        PolicyDecisionResponse(
            decision_id=d.decision_id,
            policy_id=d.policy_id,
            rule_id=d.rule_id,
            result=d.result.value,
            reason=d.reason,
            severity=d.severity,
            risk_score=d.risk_score,
            execution_time_ms=d.execution_time_ms,
            metadata=d.metadata,
            correlation_id=d.correlation_id,
            timestamp=d.timestamp.isoformat(),
        )
        for d in decisions
    ]


# ------------------------------------------------------------------
# Metrics
# ------------------------------------------------------------------

@router.get("/metrics", response_model=PolicyMetricsResponse)
async def get_metrics() -> PolicyMetricsResponse:
    """Return policy engine metrics."""
    engine = _get_engine()
    metrics = engine.get_metrics()

    return PolicyMetricsResponse(
        total_evaluations=metrics.get("total_evaluations", 0),
        evaluations_by_policy=metrics.get("evaluations_by_policy", {}),
        evaluations_by_result=metrics.get("evaluations_by_result", {}),
        average_evaluation_time_ms=metrics.get("average_evaluation_time_ms", 0.0),
        total_policies=metrics.get("total_policies", 0),
        active_policies=metrics.get("active_policies", 0),
        error_count=metrics.get("error_count", 0),
    )


# ------------------------------------------------------------------
# Export / import
# ------------------------------------------------------------------

@router.post("/export")
async def export_policies() -> SuccessResponse:
    """Export all policies as JSON."""
    registry = _get_registry()
    data = await registry.export_policies()
    return SuccessResponse(
        message=f"Exported {data['total']} policies",
        data=data,
    )


@router.post("/import")
async def import_policies(request: dict[str, Any]) -> SuccessResponse:
    """Import policies from a previously exported payload."""
    registry = _get_registry()
    count = await registry.import_policies(request)
    return SuccessResponse(
        message=f"Imported {count} policies",
        data={"imported_count": count},
    )
