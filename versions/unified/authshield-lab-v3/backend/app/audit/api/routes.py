"""Audit API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.database import get_db_session
from ...shared.events.event_bus import get_event_bus
from ...shared.responses import SuccessResponse
from ...shared.exceptions import NotFoundError
from ..services.audit_service import AuditService
from ..domain.models.request_models import AuditSearchRequest
from ..domain.models.response_models import (
    AuditEntryResponse,
    AuditListResponse,
    AuditStatsResponse,
)

router = APIRouter(prefix="/audit", tags=["audit"])


def _get_audit_service(
    session: AsyncSession = Depends(get_db_session),
) -> AuditService:
    return AuditService(session_factory=lambda: session, event_bus=get_event_bus())


@router.get("", response_model=AuditListResponse)
async def list_audit_events(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    module: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    service: AuditService = Depends(_get_audit_service),
):
    """List audit events with optional filters."""
    try:
        filters = {}
        if module:
            filters["module"] = module
        if severity:
            filters["severity"] = severity

        result = await service.search_audit(
            filters=filters, page=page, per_page=per_page
        )
        return AuditListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=AuditStatsResponse)
async def get_audit_stats(
    service: AuditService = Depends(_get_audit_service),
):
    """Get aggregate audit statistics."""
    try:
        stats = await service.get_audit_stats()
        return AuditStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=AuditListResponse)
async def get_user_audit_trail(
    user_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    service: AuditService = Depends(_get_audit_service),
):
    """Get the audit trail for a specific user."""
    try:
        result = await service.get_audit_trail(
            user_id=user_id, page=page, per_page=per_page
        )
        return AuditListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/module/{module}", response_model=AuditListResponse)
async def get_module_audit(
    module: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    service: AuditService = Depends(_get_audit_service),
):
    """Get audit events for a specific module."""
    try:
        result = await service.get_module_audit(
            module=module, page=page, per_page=per_page
        )
        return AuditListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/correlation/{correlation_id}")
async def get_audit_by_correlation(
    correlation_id: str,
    service: AuditService = Depends(_get_audit_service),
):
    """Get all audit events sharing a correlation ID."""
    try:
        items = await service.get_by_correlation_id(correlation_id)
        if not items:
            raise HTTPException(
                status_code=404,
                detail=f"No audit events found for correlation ID: {correlation_id}",
            )
        return SuccessResponse(
            message="Audit events found.",
            data={"items": items, "total": len(items)},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}", response_model=AuditEntryResponse)
async def get_audit_event(
    event_id: str,
    service: AuditService = Depends(_get_audit_service),
):
    """Get a specific audit event by ID."""
    try:
        result = await service.search_audit(
            filters={"correlation_id": event_id}, page=1, per_page=1
        )
        items = result.get("items", [])
        if not items:
            raise HTTPException(
                status_code=404, detail=f"Audit event {event_id} not found."
            )
        return AuditEntryResponse(**items[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=AuditListResponse)
async def search_audit_events(
    request: AuditSearchRequest,
    service: AuditService = Depends(_get_audit_service),
):
    """Search audit events with filters."""
    try:
        filters = request.model_dump(exclude_none=True)
        page = filters.pop("page", 1)
        per_page = filters.pop("per_page", 20)
        result = await service.search_audit(
            filters=filters, page=page, per_page=per_page
        )
        return AuditListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
