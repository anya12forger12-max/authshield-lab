"""Governance domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class GovernanceArea(str, Enum):
    """Areas subject to governance review."""

    ARCHITECTURE = "architecture"
    DOCUMENTATION = "documentation"
    ACCESSIBILITY = "accessibility"
    SECURITY = "security"
    QUALITY = "quality"
    LOCALIZATION = "localization"
    PLUGIN = "plugin"
    SDK = "sdk"


@dataclass
class GovernanceReview:
    """A scheduled or completed governance review."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    area: GovernanceArea = GovernanceArea.QUALITY
    title: str = ""
    description: str = ""
    status: str = "pending"
    reviewer: str = ""
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    recommendations: list[str] = field(default_factory=list)


@dataclass
class GovernancePolicy:
    """A policy governing a specific area of the project."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    area: GovernanceArea = GovernanceArea.QUALITY
    name: str = ""
    description: str = ""
    requirements: list[str] = field(default_factory=list)
    review_frequency_days: int = 30
    last_reviewed_at: datetime | None = None


@dataclass
class AuditCheck:
    """A single check within an architecture audit."""

    name: str = ""
    category: str = ""
    status: str = "pass"
    details: str = ""


@dataclass
class ArchitectureAudit:
    """An architecture audit containing multiple checks."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    checks: list[AuditCheck] = field(default_factory=list)
    overall_status: str = "pending"
    score: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class GovernanceReport:
    """A compiled governance report with findings and score."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    area: GovernanceArea = GovernanceArea.QUALITY
    reviews: list[GovernanceReview] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    score: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
