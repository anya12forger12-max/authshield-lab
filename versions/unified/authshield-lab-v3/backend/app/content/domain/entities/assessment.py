"""Assessment domain entities – rubrics, grading scales, and criteria."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AssessmentType(str, Enum):
    QUIZ = "quiz"
    EXAM = "exam"
    PROJECT = "project"
    LAB = "lab"
    PEER_REVIEW = "peer_review"
    PORTFOLIO = "portfolio"


class AssessmentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class GradingScale:
    """Maps letter grades to numeric ranges with a passing threshold."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    grades: dict[str, dict[str, float]] = field(default_factory=dict)
    passing_grade: str = "C"


@dataclass
class CriterionLevel:
    """A single performance level within an assessment criterion."""

    level: str = ""
    label: str = ""
    description: str = ""
    score: float = 0.0


@dataclass
class AssessmentCriteria:
    """One criterion in a rubric with its performance levels and weight."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rubric_id: str = ""
    name: str = ""
    description: str = ""
    levels: list[CriterionLevel] = field(default_factory=list)
    weight: float = 1.0


@dataclass
class Rubric:
    """A grading rubric composed of multiple criteria."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    criteria: list[AssessmentCriteria] = field(default_factory=list)
    version: int = 1

    def total_weight(self) -> float:
        """Return the sum of all criteria weights."""
        return sum(c.weight for c in self.criteria)


@dataclass
class Assessment:
    """Represents a formal assessment (quiz, exam, project, etc.)."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    assessment_type: str = AssessmentType.QUIZ.value
    description: str = ""
    rubric_id: str = ""
    questions: list[str] = field(default_factory=list)
    passing_score: float = 70.0
    time_limit: int = 0
    version: int = 1
    status: str = AssessmentStatus.DRAFT.value
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def activate(self) -> Assessment:
        """Set the assessment to active status."""
        self.status = AssessmentStatus.ACTIVE.value
        self.updated_at = datetime.now(timezone.utc)
        return self

    def archive(self) -> Assessment:
        """Set the assessment to archived status."""
        self.status = AssessmentStatus.ARCHIVED.value
        self.updated_at = datetime.now(timezone.utc)
        return self

    def validate(self) -> list[str]:
        """Return validation errors (empty list means valid)."""
        errors: list[str] = []
        if not self.title or not self.title.strip():
            errors.append("Assessment title is required.")
        if self.passing_score < 0 or self.passing_score > 100:
            errors.append("Passing score must be between 0 and 100.")
        if self.time_limit < 0:
            errors.append("Time limit must be non-negative.")
        return errors
