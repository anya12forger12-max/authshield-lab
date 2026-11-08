"""Certification and validation domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class CertificationType(str, Enum):
    """Types of certification the platform can earn."""

    ACCESSIBILITY = "accessibility"
    SECURITY = "security"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    LOCALIZATION = "localization"
    PLUGIN = "plugin"
    SDK = "sdk"
    RELEASE = "release"


@dataclass
class Certification:
    """A certification awarded to a subsystem or the platform."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    cert_type: CertificationType = CertificationType.QUALITY
    status: str = "pending"
    certified_at: datetime | None = None
    expires_at: datetime | None = None
    evidence: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    approved_by: str = ""


@dataclass
class CertificationRequirement:
    """A single requirement that must be met for certification."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    certification_id: str = ""
    requirement: str = ""
    description: str = ""
    met: bool = False
    evidence: str = ""


@dataclass
class ProductionValidation:
    """A validation result for a specific subsystem."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    subsystem: str = ""
    status: str = "pass"
    checks: dict[str, bool] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: str = ""


@dataclass
class HealthIndicator:
    """A single health metric with threshold evaluation."""

    name: str = ""
    value: float = 0.0
    threshold: float = 0.0
    status: str = "healthy"


@dataclass
class ProjectHealth:
    """Aggregated project health report."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    indicators: list[HealthIndicator] = field(default_factory=list)
    overall_score: float = 0.0
    grade: str = "F"
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
