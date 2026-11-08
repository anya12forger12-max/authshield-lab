"""Curriculum evaluation domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class CurriculumEvaluationResult:
    """Full curriculum evaluation output."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    curriculum_balance: dict[str, float] = field(default_factory=dict)
    topic_coverage: dict[str, float] = field(default_factory=dict)
    redundant_content: list[dict] = field(default_factory=list)
    missing_prerequisites: list[dict] = field(default_factory=list)
    assessment_alignment: float = 0.0
    a11y_coverage: float = 0.0
    localization_coverage: float = 0.0
    content_freshness: float = 0.0
    review_frequency_days: int = 30
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EvaluationRecommendation:
    """Actionable recommendation from curriculum evaluation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str = ""
    priority: str = "medium"
    recommendation: str = ""
    rationale: str = ""
    impact: str = ""
    effort: str = ""


@dataclass
class TopicAnalysis:
    """Per-topic analysis result."""

    topic: str = ""
    coverage_pct: float = 0.0
    redundancy_score: float = 0.0
    gaps: list[str] = field(default_factory=list)


@dataclass
class PrerequisiteGap:
    """Missing prerequisite relationship."""

    missing_from: str = ""
    needed_by: str = ""
    severity: str = "medium"
