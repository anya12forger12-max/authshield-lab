"""Audit entry entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class AuditEntry:
    """Domain entity representing an immutable audit trail entry."""

    audit_id: str = ""
    correlation_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    user_id: str | None = None
    username: str | None = None
    administrator_id: str | None = None
    module: str = ""
    event_type: str = ""
    severity: str = "info"
    description: str = ""
    resource_type: str | None = None
    resource_id: str | None = None
    previous_state: dict | None = None
    new_state: dict | None = None
    metadata: dict | None = None
    result: str = "success"
    ip_address: str = "127.0.0.1"

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "audit_id": self.audit_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "username": self.username,
            "administrator_id": self.administrator_id,
            "module": self.module,
            "event_type": self.event_type,
            "severity": self.severity,
            "description": self.description,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "metadata": self.metadata,
            "result": self.result,
            "ip_address": self.ip_address,
        }
