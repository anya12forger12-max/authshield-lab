"""Production domain events."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ProductionDomainEvent:
    """Base class for production domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = ""
    module: str = "production"
    severity: str = "info"
    metadata: dict = field(default_factory=dict)


@dataclass
class ReleaseCreatedEvent(ProductionDomainEvent):
    """Published when a new release is created."""

    event_type: str = "production.release_created"
    release_id: str = ""
    version: str = ""
    name: str = ""


@dataclass
class ReleasePublishedEvent(ProductionDomainEvent):
    """Published when a release transitions to stable."""

    event_type: str = "production.release_published"
    release_id: str = ""
    version: str = ""
    status: str = ""


@dataclass
class CertificationCompletedEvent(ProductionDomainEvent):
    """Published when a certification process completes."""

    event_type: str = "production.certification_completed"
    certification_id: str = ""
    cert_type: str = ""
    status: str = ""


@dataclass
class GovernanceReviewCompletedEvent(ProductionDomainEvent):
    """Published when a governance review is finished."""

    event_type: str = "production.governance_review_completed"
    review_id: str = ""
    area: str = ""
    status: str = ""
    score: float = 0.0


@dataclass
class MigrationCompletedEvent(ProductionDomainEvent):
    """Published when a version migration finishes."""

    event_type: str = "production.migration_completed"
    migration_id: str = ""
    from_version: str = ""
    to_version: str = ""
    status: str = ""


@dataclass
class KnowledgeEntryCreatedEvent(ProductionDomainEvent):
    """Published when a new knowledge entry is added."""

    event_type: str = "production.knowledge_entry_created"
    entry_id: str = ""
    title: str = ""
    category: str = ""
