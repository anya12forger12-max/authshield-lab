"""Content health monitoring domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ContentHealthItem:
    """Health status of a single content asset."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    content_type: str = ""
    title: str = ""
    version_status: str = "current"
    broken_refs: int = 0
    missing_metadata: int = 0
    doc_completeness: float = 0.0
    localization_status: str = "incomplete"
    a11y_status: str = "unknown"
    last_reviewed_days: int = 0
    publication_quality: float = 0.0
    dependency_health: float = 0.0


@dataclass
class ContentHealthDashboard:
    """Aggregated content health overview."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    total_items: int = 0
    healthy: int = 0
    needs_attention: int = 0
    critical: int = 0
    by_type: dict[str, int] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MaintenanceScheduleItem:
    """Single item in a maintenance schedule."""

    content_id: str = ""
    title: str = ""
    action: str = ""
    priority: str = "medium"
    due_date: str = ""


@dataclass
class MaintenanceSchedule:
    """Scheduled maintenance actions for content assets."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    items: list[MaintenanceScheduleItem] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
