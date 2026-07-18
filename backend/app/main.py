"""AuthShieldLab – FastAPI application entry point."""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.config.constants import (
    HEADER_REQUEST_ID,
    HEADER_X_CONTENT_TYPE,
    HEADER_X_FRAME_OPTIONS,
    HEADER_X_XSS_PROTECTION,
    HEADER_PERMISSIONS_POLICY,
    HEADER_REFERRER_POLICY,
    HEADER_SECURITY_POLICY,
)
from app.config.settings import get_settings
from app.shared.database import close_db, init_db
from app.shared.logging_config import RequestLoggingMiddleware, get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan – startup and shutdown events."""
    settings = get_settings()
    setup_logging(
        log_level=settings.app.log_level.value,
        json_output=not settings.app.debug,
    )
    logger = get_logger("lifeship.startup")

    logger.info(
        "application_starting",
        application=settings.app.name,
        version=settings.app.version,
        environment=settings.app.environment.value,
        debug=settings.app.debug,
    )

    await init_db()
    logger.info("database_initialized")

    logger.info(
        "application_started",
        application=settings.app.name,
        version=settings.app.version,
    )

    yield

    logger = get_logger("lifeship.shutdown")
    logger.info("application_shutting_down")

    await close_db()
    logger.info("database_closed")

    logger.info("application_stopped")


app = FastAPI(
    title="AuthShieldLab",
    description="Enterprise Authentication Security Training Platform API",
    version=get_settings().app.version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


# ------------------------------------------------------------------
# Security headers middleware
# ------------------------------------------------------------------


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next) -> Response:  # noqa: ANN001
    """Attach security-related HTTP headers to every response."""
    response: Response = await call_next(request)

    response.headers[HEADER_X_FRAME_OPTIONS] = "DENY"
    response.headers[HEADER_X_CONTENT_TYPE] = "nosniff"
    response.headers[HEADER_X_XSS_PROTECTION] = "0"
    response.headers[HEADER_REFERRER_POLICY] = "strict-origin-when-cross-origin"
    response.headers[HEADER_PERMISSIONS_POLICY] = "camera=(), microphone=(), geolocation=()"
    response.headers[HEADER_SECURITY_POLICY] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )

    return response


# ------------------------------------------------------------------
# Request ID middleware
# ------------------------------------------------------------------


@app.middleware("http")
async def request_id_middleware(request: Request, call_next) -> Response:  # noqa: ANN001
    """Inject a unique request ID into every request and response."""
    request_id = request.headers.get(HEADER_REQUEST_ID) or str(uuid.uuid4())
    request.state.request_id = request_id

    response: Response = await call_next(request)
    response.headers[HEADER_REQUEST_ID] = request_id

    return response


# ------------------------------------------------------------------
# CORS middleware (localhost only)
# ------------------------------------------------------------------


def _configure_cors() -> None:
    """Add CORS middleware locked to localhost origins."""
    settings = get_settings()

    if not settings.validate_localhost_only():
        raise RuntimeError(
            "CORS configuration contains non-localhost origins. "
            "AuthShieldLab requires all origins to be localhost-only."
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allowed_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )


_configure_cors()

# Structured logging middleware (ASGI level)
app.add_middleware(RequestLoggingMiddleware)

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------

app.include_router(api_v1_router)


@app.get("/api/health", tags=["health"])
async def root_health_check() -> dict:
    """Top-level health check (convenience alias)."""
    settings = get_settings()
    return {
        "status": "healthy",
        "application": settings.app.name,
        "version": settings.app.version,
    }
