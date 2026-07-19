"""Learning quality dashboard domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LearningQualityDashboard:
    """Comprehensive learning quality metrics dashboard."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    completion_rates: float = 0.0
    learning_objective_achievement: float = 0.0
    competency_growth: float = 0.0
    assessment_distribution: dict[str, float] = field(default_factory=dict)
    lab_completion: float = 0.0
    portfolio_progress: float = 0.0
    certification_progress: float = 0.0
    reflection_participation: float = 0.0
    instructor_review_status: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class LongitudinalComparison:
    """Term-over-term metric comparison."""

    term: str = ""
    value: float = 0.0
    change_pct: float = 0.0
    trend: str = "stable"


@dataclass
class QualityIndicator:
    """Single quality indicator with benchmark and trend."""

    name: str = ""
    value: float = 0.0
    benchmark: float = 0.0
    status: str = "unknown"
    trend: str = "stable"
