"""Analytics domain events."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AnalyticsDomainEvent:
    """Base class for analytics domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = ""
    module: str = "analytics"
    severity: str = "info"
    metadata: dict = field(default_factory=dict)


@dataclass
class AnalyticsDashboardGenerated(AnalyticsDomainEvent):
    """Published when an educational analytics dashboard is generated."""

    event_type: str = "analytics.dashboard_generated"
    dashboard_id: str = ""


@dataclass
class QualityDashboardGenerated(AnalyticsDomainEvent):
    """Published when a learning quality dashboard is generated."""

    event_type: str = "analytics.quality_dashboard_generated"
    dashboard_id: str = ""


@dataclass
class CurriculumEvaluated(AnalyticsDomainEvent):
    """Published when a curriculum evaluation is completed."""

    event_type: str = "analytics.curriculum_evaluated"
    evaluation_id: str = ""


@dataclass
class ContentHealthChecked(AnalyticsDomainEvent):
    """Published when a content health check is performed."""

    event_type: str = "analytics.content_health_checked"
    dashboard_id: str = ""


@dataclass
class ProgramEvaluated(AnalyticsDomainEvent):
    """Published when a program evaluation is completed."""

    event_type: str = "analytics.program_evaluated"
    evaluation_id: str = ""


@dataclass
class ImprovementPlanCreated(AnalyticsDomainEvent):
    """Published when a new improvement plan is created."""

    event_type: str = "analytics.improvement_plan_created"
    plan_id: str = ""
