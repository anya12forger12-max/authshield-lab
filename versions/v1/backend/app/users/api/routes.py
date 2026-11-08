"""Users API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.database import get_db_session
from ...shared.events.event_bus import get_event_bus
from ...shared.responses import SuccessResponse, PaginatedResponse, ErrorResponse
from ...shared.exceptions import NotFoundError, ValidationError, ConflictError
from ..services.identity_service import IdentityService
from ..services.role_service import RoleService
from ..services.preference_service import PreferenceService
from ..services.device_service import DeviceService
from ..domain.models.request_models import (
    UpdateProfileRequest,
    UpdateStatusRequest,
    AssignRoleRequest,
    UpdatePreferencesRequest,
    ExportRequest,
)
from ..domain.models.response_models import (
    UserProfileResponse,
    UserListResponse,
    PreferenceResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


def _get_identity_service(session: AsyncSession = Depends(get_db_session)) -> IdentityService:
    return IdentityService(session_factory=lambda: session, event_bus=get_event_bus())


def _get_role_service(session: AsyncSession = Depends(get_db_session)) -> RoleService:
    return RoleService(session_factory=lambda: session, event_bus=get_event_bus())


def _get_preference_service(session: AsyncSession = Depends(get_db_session)) -> PreferenceService:
    return PreferenceService(session_factory=lambda: session, event_bus=get_event_bus())


def _get_device_service() -> DeviceService:
    return DeviceService(event_bus=get_event_bus())


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    role: str | None = Query(default=None),
    status: str | None = Query(default=None),
    identity_service: IdentityService = Depends(_get_identity_service),
):
    """List all users with pagination and optional filters (admin)."""
    try:
        result = await identity_service.list_users(
            page=page, per_page=per_page, role=role, status=status
        )
        return UserListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user(
    identity_service: IdentityService = Depends(_get_identity_service),
):
    """Get the current authenticated user's profile.

    In a real implementation this would extract the user_id from the JWT
    token.  For now we return a placeholder.
    """
    # TODO: Extract user_id from authentication context / JWT
    raise HTTPException(status_code=401, detail="Authentication required.")


@router.get("/search", response_model=UserListResponse)
async def search_users(
    q: str = Query(default="", max_length=128),
    role: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    identity_service: IdentityService = Depends(_get_identity_service),
):
    """Search users by query string."""
    try:
        result = await identity_service.search_users(
            query=q,
            filters={"role": role, "status": status},
            page=page,
            per_page=per_page,
        )
        return UserListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(
    user_id: str,
    identity_service: IdentityService = Depends(_get_identity_service),
):
    """Get a specific user's profile."""
    try:
        profile = await identity_service.get_user_profile(user_id)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
        return UserProfileResponse(**profile.to_safe_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: str,
    request: UpdateProfileRequest,
    identity_service: IdentityService = Depends(_get_identity_service),
):
    """Update a user's profile fields."""
    try:
        data = request.model_dump(exclude_none=True)
        profile = await identity_service.update_profile(user_id, data)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
        return UserProfileResponse(**profile.to_safe_dict())
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    identity_service: IdentityService = Depends(_get_identity_service),
):
    """Soft-delete a user."""
    try:
        success = await identity_service.delete_user(user_id, soft=True)
        return SuccessResponse(message="User deleted.", data={"user_id": user_id})
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: str,
    request: UpdateStatusRequest,
    identity_service: IdentityService = Depends(_get_identity_service),
):
    """Update a user's account status (admin)."""
    try:
        success = await identity_service.update_user_status(
            user_id, request.status, request.reason
        )
        return SuccessResponse(
            message=f"User status updated to {request.status}.",
            data={"user_id": user_id, "status": request.status},
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/preferences", response_model=PreferenceResponse)
async def get_user_preferences(
    user_id: str,
    preference_service: PreferenceService = Depends(_get_preference_service),
):
    """Get a user's preferences."""
    try:
        prefs = await preference_service.get_preferences(user_id)
        if prefs is None:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
        return PreferenceResponse(**prefs)
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/preferences", response_model=PreferenceResponse)
async def update_user_preferences(
    user_id: str,
    request: UpdatePreferencesRequest,
    preference_service: PreferenceService = Depends(_get_preference_service),
):
    """Update a user's preferences."""
    try:
        data = request.model_dump(exclude_none=True)
        prefs = await preference_service.update_preferences(user_id, data)
        if prefs is None:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
        return PreferenceResponse(**prefs)
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/sessions")
async def get_user_sessions(
    user_id: str,
    identity_service: IdentityService = Depends(_get_identity_service),
):
    """Get a user's sessions (delegates to sessions module)."""
    # This endpoint is a convenience proxy; real implementation delegates
    # to the sessions module's own service.
    try:
        profile = await identity_service.get_user_profile(user_id)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
        return SuccessResponse(
            message="User sessions.",
            data={"user_id": user_id, "active_session_count": profile.active_session_count},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/audit")
async def get_user_audit(
    user_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
):
    """Get a user's audit history (delegates to audit module)."""
    return SuccessResponse(
        message="User audit history.",
        data={"user_id": user_id, "page": page, "per_page": per_page},
    )


@router.post("/{user_id}/export")
async def export_user_data(
    user_id: str,
    request: ExportRequest,
    identity_service: IdentityService = Depends(_get_identity_service),
):
    """Export all user data in the requested format."""
    try:
        profile = await identity_service.get_user_profile(user_id)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found.")

        if request.format == "json":
            return SuccessResponse(
                message="User data exported.",
                data=profile.to_admin_dict(),
            )
        else:
            # CSV export would be implemented here
            return SuccessResponse(
                message="CSV export not yet implemented.",
                data=None,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
