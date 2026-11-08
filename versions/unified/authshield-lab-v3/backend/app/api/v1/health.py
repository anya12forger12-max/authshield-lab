"""Health check endpoints."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter

from app.config.settings import get_settings
from app.shared.responses import SuccessResponse

router = APIRouter(prefix="/health", tags=["health"])

_start_time: float = time.time()


@router.get("", response_model=SuccessResponse)
async def health_check() -> SuccessResponse:
    """Return application status, version, and uptime."""
    settings = get_settings()
    uptime_seconds = time.time() - _start_time

    return SuccessResponse(
        message="Application is healthy",
        data={
            "status": "healthy",
            "application": settings.app.name,
            "version": settings.app.version,
            "environment": settings.app.environment.value,
            "uptime_seconds": round(uptime_seconds, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/ready", response_model=SuccessResponse)
async def readiness_check() -> SuccessResponse:
    """Readiness probe – returns 200 when the app can serve traffic."""
    return SuccessResponse(
        message="Application is ready",
        data={
            "status": "ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.get("/live", response_model=SuccessResponse)
async def liveness_check() -> SuccessResponse:
    """Liveness probe – lightweight check that the process is running."""
    return SuccessResponse(
        message="Application is alive",
        data={
            "status": "alive",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
