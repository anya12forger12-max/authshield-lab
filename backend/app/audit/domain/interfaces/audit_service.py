"""Audit service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any

from ..entities.audit_entry import AuditEntry


class IAuditService(ABC):
    """Interface for audit trail management operations."""

    @abstractmethod
    async def record_event(self, entry: AuditEntry) -> str:
        """Record an audit event and return its ID."""
        ...

    @abstractmethod
    async def get_audit_trail(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> dict:
        """Return the audit trail for a specific user."""
        ...

    @abstractmethod
    async def get_module_audit(
        self, module: str, page: int = 1, per_page: int = 20
    ) -> dict:
        """Return audit events for a specific module."""
        ...

    @abstractmethod
    async def search_audit(
        self, filters: Optional[dict] = None, page: int = 1, per_page: int = 20
    ) -> dict:
        """Search audit events with filters and pagination."""
        ...

    @abstractmethod
    async def get_by_correlation_id(self, correlation_id: str) -> list[dict]:
        """Return all audit events sharing a correlation ID."""
        ...

    @abstractmethod
    async def get_audit_stats(self) -> dict:
        """Return aggregate audit statistics."""
        ...

    @abstractmethod
    async def export_audit(
        self, filters: Optional[dict] = None, format: str = "json"
    ) -> Any:
        """Export audit events in the specified format."""
        ...
