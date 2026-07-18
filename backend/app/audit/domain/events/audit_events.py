"""Audit domain events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class AuditDomainEvent:
    """Base class for audit domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = ""
    module: str = "audit"
    severity: str = "info"
    user_id: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class AuditEventRecordedEvent(AuditDomainEvent):
    """Published when an audit event is recorded."""

    event_type: str = "audit.event_recorded"
    audit_event_id: str = ""


@dataclass
class AuditEventQueriedEvent(AuditDomainEvent):
    """Published when audit events are queried (for audit-of-audit)."""

    event_type: str = "audit.event_queried"
    query_module: str = ""


@dataclass
class AuditExportedEvent(AuditDomainEvent):
    """Published when audit data is exported."""

    event_type: str = "audit.exported"
    export_format: str = "json"
    record_count: int = 0
