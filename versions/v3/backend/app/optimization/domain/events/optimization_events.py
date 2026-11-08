"""Optimization domain event definitions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class OptimizationDomainEvent:
    """Base class for all optimization domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    module: str = "optimization"
    severity: str = "info"
    metadata: dict = field(default_factory=dict)


@dataclass
class BenchmarkCompleted(OptimizationDomainEvent):
    """Published when a benchmark run finishes."""

    event_type: str = "optimization.benchmark.completed"
    benchmark_id: str = ""
    benchmark_name: str = ""
    category: str = ""
    value: float = 0.0
    passed: bool = True


@dataclass
class OptimizationDashboardGenerated(OptimizationDomainEvent):
    """Published when a new optimization dashboard is generated."""

    event_type: str = "optimization.dashboard.generated"
    dashboard_id: str = ""
    overall_health: str = ""


@dataclass
class CompatibilityReportGenerated(OptimizationDomainEvent):
    """Published when a cross-platform compatibility report is generated."""

    event_type: str = "optimization.compatibility.report_generated"
    report_id: str = ""
    platforms_checked: int = 0
    overall_status: str = ""


@dataclass
class FeatureFlagToggled(OptimizationDomainEvent):
    """Published when a feature flag is toggled."""

    event_type: str = "optimization.feature_flag.toggled"
    flag_id: str = ""
    flag_name: str = ""
    enabled: bool = False


@dataclass
class AIGenerationRequested(OptimizationDomainEvent):
    """Published when an AI content generation is requested."""

    event_type: str = "optimization.ai.generation_requested"
    content_id: str = ""
    ai_type: str = ""


@dataclass
class ContentReviewCompleted(OptimizationDomainEvent):
    """Published when an instructor completes an AI content review."""

    event_type: str = "optimization.ai.review_completed"
    audit_id: str = ""
    content_id: str = ""
    approved: bool = False


@dataclass
class SustainabilityReportGenerated(OptimizationDomainEvent):
    """Published when a sustainability dashboard is generated."""

    event_type: str = "optimization.sustainability.report_generated"
    overall_score: float = 0.0
    health_label: str = ""


@dataclass
class ReleaseWorkflowAdvanced(OptimizationDomainEvent):
    """Published when a release workflow advances to the next stage."""

    event_type: str = "optimization.release.workflow_advanced"
    workflow_id: str = ""
    release_id: str = ""
    previous_stage: str = ""
    current_stage: str = ""
