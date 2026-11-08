"""Educational analytics domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LearningProgress:
    """Aggregated learner progress metrics."""

    learner_id: str = ""
    courses_enrolled: int = 0
    courses_completed: int = 0
    competencies_achieved: int = 0
    avg_score: float = 0.0
    total_time_hours: float = 0.0
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CourseCompletion:
    """Course-level completion and performance data."""

    course_id: str = ""
    course_name: str = ""
    enrolled: int = 0
    completed: int = 0
    in_progress: int = 0
    dropped: int = 0
    completion_rate: float = 0.0
    avg_score: float = 0.0


@dataclass
class AssessmentOutcome:
    """Assessment-level analytics including item analysis."""

    assessment_id: str = ""
    title: str = ""
    total_attempts: int = 0
    passed: int = 0
    failed: int = 0
    avg_score: float = 0.0
    pass_rate: float = 0.0
    question_difficulty: dict[str, float] = field(default_factory=dict)
    question_discrimination: dict[str, float] = field(default_factory=dict)


@dataclass
class CurriculumCoverage:
    """Curriculum alignment and gap analysis."""

    framework_id: str = ""
    total_competencies: int = 0
    mapped_competencies: int = 0
    coverage_pct: float = 0.0
    gaps: list[dict] = field(default_factory=list)
    overlaps: list[dict] = field(default_factory=list)


@dataclass
class ContentUsage:
    """Content access and engagement metrics."""

    content_id: str = ""
    content_type: str = ""
    title: str = ""
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    average_time_minutes: float = 0.0


@dataclass
class EducationalAnalyticsDashboard:
    """Comprehensive educational analytics dashboard."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    learning_progress: LearningProgress = field(default_factory=LearningProgress)
    course_completions: list[CourseCompletion] = field(default_factory=list)
    assessment_outcomes: list[AssessmentOutcome] = field(default_factory=list)
    curriculum_coverage: CurriculumCoverage = field(default_factory=CurriculumCoverage)
    content_usage: list[ContentUsage] = field(default_factory=list)
    a11y_metrics: dict = field(default_factory=dict)
    doc_quality: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FilterOptions:
    """Filter criteria for analytics queries."""

    institution: str | None = None
    campus: str | None = None
    department: str | None = None
    program: str | None = None
    course: str | None = None
    instructor: str | None = None
    term: str | None = None
    date_from: str | None = None
    date_to: str | None = None
