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

# ====================================================================
# Version 3.0 – Content Studio
# ====================================================================

try:
    from ...content.api.content_routes import router as content_router

    api_v1_router.include_router(content_router)
except (ImportError, AttributeError):
    pass

try:
    from ...lms.api.lms_routes import router as lms_router

    api_v1_router.include_router(lms_router)
except (ImportError, AttributeError):
    pass

try:
    from ...simulation.api.simulation_routes import router as simulation_router

    api_v1_router.include_router(simulation_router)
except (ImportError, AttributeError):
    pass

try:
    from ...developer.api.developer_routes import router as developer_router

    api_v1_router.include_router(developer_router)
except (ImportError, AttributeError):
    pass

try:
    from ...quality.api.quality_routes import router as quality_router

    api_v1_router.include_router(quality_router)
except (ImportError, AttributeError):
    pass

try:
    from ...production.api.production_routes import router as production_router

    api_v1_router.include_router(production_router)
except (ImportError, AttributeError):
    pass

# ====================================================================
# Version 4.0 – Ecosystem & Optimization
# ====================================================================

try:
    from ...ecosystem.api.ecosystem_routes import router as ecosystem_router

    api_v1_router.include_router(ecosystem_router)
except (ImportError, AttributeError):
    pass

try:
    from ...optimization.api.optimization_routes import router as optimization_router

    api_v1_router.include_router(optimization_router)
except (ImportError, AttributeError):
    pass

# ====================================================================
# Version 5.0 – Collaboration, Standards, Content Studio V5, Analytics, Certification
# ====================================================================

try:
    from ...collaboration.api.collaboration_routes import router as collaboration_router

    api_v1_router.include_router(collaboration_router)
except (ImportError, AttributeError):
    pass

try:
    from ...standards.api.standards_routes import router as standards_router

    api_v1_router.include_router(standards_router)
except (ImportError, AttributeError):
    pass

try:
    from ...content_studio.api.content_studio_routes import router as content_studio_router

    api_v1_router.include_router(content_studio_router)
except (ImportError, AttributeError):
    pass

try:
    from ...analytics.api.analytics_routes import router as analytics_router

    api_v1_router.include_router(analytics_router)
except (ImportError, AttributeError):
    pass

try:
    from ...certification.api.certification_routes import router as certification_router

    api_v1_router.include_router(certification_router)
except (ImportError, AttributeError):
    pass
