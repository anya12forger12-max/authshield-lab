"""Domain entities for academic quality dashboards and readiness reviews."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ReadinessStage(Enum):
    """Stages of the readiness review pipeline."""

    DRAFT = "draft"
    DEPARTMENT_REVIEW = "department_review"
    FACULTY_REVIEW = "faculty_review"
    A11Y_REVIEW = "a11y_review"
    DOC_REVIEW = "doc_review"
    GOVERNANCE_REVIEW = "governance_review"
    ADMIN_APPROVAL = "admin_approval"
    PUBLICATION = "publication"


STAGE_ORDER: list[ReadinessStage] = list(ReadinessStage)


@dataclass
class ReadinessReviewEvent:
    """An event recorded during a readiness review."""

    review_id: str = ""
    stage: ReadinessStage = ReadinessStage.DRAFT
    actor: str = ""
    action: str = ""
    comments: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "review_id": self.review_id,
            "stage": self.stage.value,
            "actor": self.actor,
            "action": self.action,
            "comments": self.comments,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class AcademicQualityDashboard:
    """Dashboard aggregating academic quality metrics."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    curriculum_balance: float = 0.0
    competency_distribution: dict[str, float] = field(default_factory=dict)
    skills_progression: dict[str, float] = field(default_factory=dict)
    assessment_distribution: dict[str, float] = field(default_factory=dict)
    a11y_health: float = 0.0
    doc_quality: float = 0.0
    localization_readiness: float = 0.0
    content_freshness: float = 0.0
    review_completion: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def overall_score(self) -> float:
        scores = [
            self.curriculum_balance,
            self.a11y_health,
            self.doc_quality,
            self.localization_readiness,
            self.content_freshness,
            self.review_completion,
        ]
        return sum(scores) / len(scores) if scores else 0.0

    def health_status(self) -> str:
        overall = self.overall_score()
        if overall >= 0.8:
            return "healthy"
        if overall >= 0.5:
            return "degraded"
        return "unhealthy"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "curriculum_balance": self.curriculum_balance,
            "competency_distribution": dict(self.competency_distribution),
            "skills_progression": dict(self.skills_progression),
            "assessment_distribution": dict(self.assessment_distribution),
            "a11y_health": self.a11y_health,
            "doc_quality": self.doc_quality,
            "localization_readiness": self.localization_readiness,
            "content_freshness": self.content_freshness,
            "review_completion": self.review_completion,
            "overall_score": self.overall_score(),
            "health_status": self.health_status(),
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class ReadinessReview:
    """Tracks a framework through readiness stages."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    framework_id: str = ""
    current_stage: ReadinessStage = ReadinessStage.DRAFT
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    events: list[ReadinessReviewEvent] = field(default_factory=list)

    def advance(self, actor: str, comments: str = "") -> ReadinessReviewEvent:
        current_idx = STAGE_ORDER.index(self.current_stage)
        if current_idx >= len(STAGE_ORDER) - 1:
            raise RuntimeError("Review is already at the final stage")
        next_stage = STAGE_ORDER[current_idx + 1]
        event = ReadinessReviewEvent(
            review_id=self.id,
            stage=next_stage,
            actor=actor,
            action="advance",
            comments=comments,
        )
        self.current_stage = next_stage
        self.events.append(event)
        if next_stage == ReadinessStage.PUBLICATION:
            self.completed_at = datetime.now(timezone.utc)
        return event

    def reject(self, actor: str, comments: str = "") -> ReadinessReviewEvent:
        current_idx = STAGE_ORDER.index(self.current_stage)
        if current_idx <= 0:
            raise RuntimeError("Cannot reject at draft stage")
        prev_stage = STAGE_ORDER[current_idx - 1]
        event = ReadinessReviewEvent(
            review_id=self.id,
            stage=prev_stage,
            actor=actor,
            action="reject",
            comments=comments,
        )
        self.current_stage = prev_stage
        self.events.append(event)
        return event

    def is_complete(self) -> bool:
        return self.current_stage == ReadinessStage.PUBLICATION

    def progress_pct(self) -> float:
        current_idx = STAGE_ORDER.index(self.current_stage)
        return (current_idx / (len(STAGE_ORDER) - 1)) * 100.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "framework_id": self.framework_id,
            "current_stage": self.current_stage.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress_pct": self.progress_pct(),
            "is_complete": self.is_complete(),
            "events": [e.to_dict() for e in self.events],
        }


@dataclass
class FrameworkComparison:
    """Result of comparing two framework versions."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_a_id: str = ""
    framework_b_id: str = ""
    added_competencies: list[str] = field(default_factory=list)
    removed_competencies: list[str] = field(default_factory=list)
    renamed_elements: list[dict] = field(default_factory=list)
    changed_relationships: list[dict] = field(default_factory=list)
    coverage_differences: dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def has_changes(self) -> bool:
        return bool(
            self.added_competencies
            or self.removed_competencies
            or self.renamed_elements
            or self.changed_relationships
        )

    def change_count(self) -> int:
        return (
            len(self.added_competencies)
            + len(self.removed_competencies)
            + len(self.renamed_elements)
            + len(self.changed_relationships)
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "framework_a_id": self.framework_a_id,
            "framework_b_id": self.framework_b_id,
            "added_competencies": list(self.added_competencies),
            "removed_competencies": list(self.removed_competencies),
            "renamed_elements": list(self.renamed_elements),
            "changed_relationships": list(self.changed_relationships),
            "coverage_differences": dict(self.coverage_differences),
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class LearningOutcomeValidation:
    """Result of validating learning outcomes in a framework."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str = ""
    missing_outcomes: int = 0
    duplicate_outcomes: int = 0
    unmapped_outcomes: int = 0
    weak_coverage: int = 0
    assessment_gaps: int = 0
    doc_gaps: int = 0
    a11y_gaps: int = 0
    recommendations: list[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def total_issues(self) -> int:
        return (
            self.missing_outcomes
            + self.duplicate_outcomes
            + self.unmapped_outcomes
            + self.weak_coverage
            + self.assessment_gaps
            + self.doc_gaps
            + self.a11y_gaps
        )

    def is_valid(self) -> bool:
        return self.total_issues() == 0

    def add_recommendation(self, recommendation: str) -> None:
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "framework_id": self.framework_id,
            "missing_outcomes": self.missing_outcomes,
            "duplicate_outcomes": self.duplicate_outcomes,
            "unmapped_outcomes": self.unmapped_outcomes,
            "weak_coverage": self.weak_coverage,
            "assessment_gaps": self.assessment_gaps,
            "doc_gaps": self.doc_gaps,
            "a11y_gaps": self.a11y_gaps,
            "total_issues": self.total_issues(),
            "is_valid": self.is_valid(),
            "recommendations": list(self.recommendations),
            "validated_at": self.validated_at.isoformat(),
        }
