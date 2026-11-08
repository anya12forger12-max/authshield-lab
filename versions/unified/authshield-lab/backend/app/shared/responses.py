"""Standard API response models."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success envelope."""

    status: str = Field(default="success", description="Response status")
    message: str = Field(default="OK", description="Human-readable message")
    data: T | None = Field(default=None, description="Response payload")

    model_config = {"json_schema_extra": {"example": {"status": "success", "message": "OK"}}}


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    status: str = Field(default="error", description="Response status")
    error: str = Field(description="Error class name")
    message: str = Field(description="Human-readable error description")
    detail: Any = Field(default=None, description="Structured error detail")
    request_id: str | None = Field(
        default=None, description="Correlation ID for the failing request"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "error",
                "error": "ValidationError",
                "message": "Invalid input.",
                "detail": None,
                "request_id": "abc-123",
            }
        }
    }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    status: str = Field(default="success", description="Response status")
    items: list[T] = Field(default_factory=list, description="Page items")
    total: int = Field(description="Total number of items across all pages")
    page: int = Field(description="Current page number (1-indexed)")
    per_page: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "items": [],
                "total": 0,
                "page": 1,
                "per_page": 20,
                "pages": 0,
            }
        }
    }
