"""Results domain entities for exercise assessment and feedback."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ImprovementRecommendation:
    """A specific recommendation for learner improvement."""

    category: str = ""
    priority: str = "medium"
    recommendation: str = ""
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "category": self.category,
            "priority": self.priority,
            "recommendation": self.recommendation,
            "rationale": self.rationale,
        }


@dataclass
class ExerciseResult:
    """Comprehensive result record for a completed exercise session.

    Aggregates scores, competency progress, reflections, feedback,
    accessibility usage, and improvement recommendations.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    exercise_id: str = ""
    completion_status: str = "incomplete"
    assessment_scores: dict[str, float] = field(default_factory=dict)
    competency_progress: dict[str, float] = field(default_factory=dict)
    reflection_responses: list[str] = field(default_factory=list)
    instructor_feedback: str = ""
    rubric_results: dict[str, Any] = field(default_factory=dict)
    accessibility_usage: dict[str, Any] = field(default_factory=dict)
    time_on_task_seconds: int = 0
    improvement_recommendations: list[ImprovementRecommendation] = field(
        default_factory=list
    )
    completed_at: datetime | None = None

    def calculate_overall_score(self) -> float:
        """Calculate overall assessment score as a weighted average.

        Returns 0.0 if no scores are available.
        """
        if not self.assessment_scores:
            return 0.0
        return sum(self.assessment_scores.values()) / len(self.assessment_scores)

    def add_assessment_score(self, criterion: str, score: float) -> None:
        """Add or update an assessment score for a criterion."""
        self.assessment_scores[criterion] = max(0.0, min(1.0, score))

    def update_competency(self, competency: str, progress: float) -> None:
        """Update progress for a specific competency."""
        self.competency_progress[competency] = max(0.0, min(1.0, progress))

    def add_improvement(self, recommendation: ImprovementRecommendation) -> None:
        """Add an improvement recommendation."""
        self.improvement_recommendations.append(recommendation)

    def get_high_priority_recommendations(self) -> list[ImprovementRecommendation]:
        """Return only high-priority improvement recommendations."""
        return [
            r for r in self.improvement_recommendations if r.priority == "high"
        ]

    def mark_complete(self) -> None:
        """Mark the result as complete with a timestamp."""
        self.completion_status = "completed"
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "exercise_id": self.exercise_id,
            "completion_status": self.completion_status,
            "assessment_scores": dict(self.assessment_scores),
            "competency_progress": dict(self.competency_progress),
            "reflection_responses": list(self.reflection_responses),
            "instructor_feedback": self.instructor_feedback,
            "rubric_results": dict(self.rubric_results),
            "accessibility_usage": dict(self.accessibility_usage),
            "time_on_task_seconds": self.time_on_task_seconds,
            "improvement_recommendations": [
                r.to_dict() for r in self.improvement_recommendations
            ],
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
