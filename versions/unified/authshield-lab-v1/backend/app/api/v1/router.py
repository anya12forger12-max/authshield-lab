"""Main v1 API router – aggregates all module sub-routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)

# ------------------------------------------------------------------
# Register module routers here as they are implemented.
# Uses try/except to gracefully handle missing modules.
# ------------------------------------------------------------------

try:
    from ...authentication.api.routes import router as auth_router

    api_v1_router.include_router(auth_router)
except (ImportError, AttributeError):
    pass

try:
    from ...users.api.routes import router as users_router

    api_v1_router.include_router(users_router)
except (ImportError, AttributeError):
    pass

try:
    from ...sessions.api.routes import router as sessions_router

    api_v1_router.include_router(sessions_router)
except (ImportError, AttributeError):
    pass

try:
    from ...audit.api.routes import router as audit_router

    api_v1_router.include_router(audit_router)
except (ImportError, AttributeError):
    pass

try:
    from ...defenses.api.routes import router as defenses_router

    api_v1_router.include_router(defenses_router)
except (ImportError, AttributeError):
    pass
