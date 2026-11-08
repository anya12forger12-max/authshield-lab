"""Security policy engine API routes."""

from __future__ import annotations

from fastapi import APIRouter

from .routes import router as policy_router

router = APIRouter()
router.include_router(policy_router)
