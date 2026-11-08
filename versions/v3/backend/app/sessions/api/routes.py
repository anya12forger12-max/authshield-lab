"""Sessions API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.database import get_db_session
from ...shared.events.event_bus import get_event_bus
from ...shared.responses import SuccessResponse, PaginatedResponse
from ...shared.exceptions import NotFoundError
from ..services.session_management_service import SessionManagementService
from ..domain.models.request_models import TerminateSessionRequest, SessionSearchRequest
from ..domain.models.response_models import (
    SessionDetailResponse,
    SessionListResponse,
    SessionStatsResponse,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _get_session_management_service(
    session: AsyncSession = Depends(get_db_session),
) -> SessionManagementService:
    return SessionManagementService(
        session_factory=lambda: session, event_bus=get_event_bus()
    )


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    service: SessionManagementService = Depends(_get_session_management_service),
):
    """List all sessions (admin)."""
    try:
        result = await service.search_sessions(filters={}, page=page, per_page=per_page)
        return SessionListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active", response_model=SessionListResponse)
async def list_active_sessions(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    service: SessionManagementService = Depends(_get_session_management_service),
):
    """List all active sessions."""
    try:
        result = await service.search_sessions(
            filters={"status": "active"}, page=page, per_page=per_page
        )
        return SessionListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/expired", response_model=SessionListResponse)
async def list_expired_sessions(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    service: SessionManagementService = Depends(_get_session_management_service),
):
    """List all expired sessions."""
    try:
        result = await service.search_sessions(
            filters={"status": "expired"}, page=page, per_page=per_page
        )
        return SessionListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=SessionStatsResponse)
async def get_session_stats(
    user_id: str | None = Query(default=None),
    service: SessionManagementService = Depends(_get_session_management_service),
):
    """Get session statistics."""
    try:
        stats = await service.get_session_stats(user_id=user_id)
        return SessionStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    service: SessionManagementService = Depends(_get_session_management_service),
):
    """Get details for a specific session."""
    try:
        session_data = await service.get_current_session(session_id)
        if session_data is None:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")
        return SessionDetailResponse(**session_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def terminate_session(
    session_id: str,
    request: TerminateSessionRequest = TerminateSessionRequest(),
    service: SessionManagementService = Depends(_get_session_management_service),
):
    """Terminate a session."""
    try:
        success = await service.terminate_session(session_id, reason=request.reason)
        return SuccessResponse(
            message="Session terminated.",
            data={"session_id": session_id, "reason": request.reason},
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/user/{user_id}")
async def terminate_all_user_sessions(
    user_id: str,
    request: TerminateSessionRequest = TerminateSessionRequest(),
    service: SessionManagementService = Depends(_get_session_management_service),
):
    """Terminate all sessions for a user."""
    try:
        count = await service.terminate_all_sessions(user_id, reason=request.reason)
        return SuccessResponse(
            message=f"Terminated {count} sessions.",
            data={"user_id": user_id, "terminated_count": count},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_expired_sessions(
    service: SessionManagementService = Depends(_get_session_management_service),
):
    """Clean up expired sessions."""
    try:
        count = await service.cleanup_expired()
        return SuccessResponse(
            message=f"Cleaned up {count} expired sessions.",
            data={"cleaned_count": count},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SessionListResponse)
async def search_sessions(
    request: SessionSearchRequest,
    service: SessionManagementService = Depends(_get_session_management_service),
):
    """Search sessions with filters."""
    try:
        filters = request.model_dump(exclude_none=True)
        page = filters.pop("page", 1)
        per_page = filters.pop("per_page", 20)
        result = await service.search_sessions(
            filters=filters, page=page, per_page=per_page
        )
        return SessionListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
