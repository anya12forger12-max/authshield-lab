"""Domain events for the Standards module."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class FrameworkCreated:
    """Raised when a new competency framework is created."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str = ""
    name: str = ""
    version: str = ""
    created_by: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FrameworkUpdated:
    """Raised when a competency framework is updated."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str = ""
    changes: list[str] = field(default_factory=list)
    updated_by: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MappingCreated:
    """Raised when a new curriculum mapping is created."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mapping_id: str = ""
    source_id: str = ""
    target_id: str = ""
    coverage_level: str = ""
    created_by: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BulkMappingCompleted:
    """Raised when a bulk mapping operation finishes."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    total: int = 0
    mapped: int = 0
    unmapped: int = 0
    gaps: list[str] = field(default_factory=list)
    initiated_by: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReadinessReviewAdvanced:
    """Raised when a readiness review advances to the next stage."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    review_id: str = ""
    old_stage: str = ""
    new_stage: str = ""
    actor: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EvidenceCollected:
    """Raised when evidence is added to a collection."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    collection_id: str = ""
    evidence_item_id: str = ""
    evidence_type: str = ""
    collected_by: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class QualityDashboardGenerated:
    """Raised when an academic quality dashboard is generated."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dashboard_id: str = ""
    framework_id: str = ""
    overall_score: float = 0.0
    health_status: str = ""
    generated_by: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
