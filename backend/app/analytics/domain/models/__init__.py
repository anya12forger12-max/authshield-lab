"""SQLAlchemy ORM models for the analytics module."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ....shared.base_model import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class LearningProgressModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for learner progress snapshots."""

    __tablename__ = "analytics_learning_progress"

    learner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    courses_enrolled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    courses_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    competencies_achieved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_time_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class CourseCompletionModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for course completion metrics."""

    __tablename__ = "analytics_course_completions"

    course_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    course_name: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    enrolled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    in_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dropped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class AssessmentOutcomeModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for assessment outcomes."""

    __tablename__ = "analytics_assessment_outcomes"

    assessment_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pass_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    question_difficulty: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    question_discrimination: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class CurriculumCoverageModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for curriculum coverage."""

    __tablename__ = "analytics_curriculum_coverage"

    framework_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    total_competencies: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mapped_competencies: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coverage_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    gaps: Mapped[list | None] = mapped_column(JSON, nullable=True)
    overlaps: Mapped[list | None] = mapped_column(JSON, nullable=True)


class ContentUsageModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for content usage analytics."""

    __tablename__ = "analytics_content_usage"

    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    title: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    access_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_accessed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    average_time_minutes: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class EducationalAnalyticsDashboardModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for analytics dashboards."""

    __tablename__ = "analytics_dashboards"

    learning_progress_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    curriculum_coverage_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    a11y_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    doc_quality: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class LearningQualityDashboardModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for learning quality dashboards."""

    __tablename__ = "analytics_quality_dashboards"

    completion_rates: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    learning_objective_achievement: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    competency_growth: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    assessment_distribution: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    lab_completion: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    portfolio_progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    certification_progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reflection_participation: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    instructor_review_status: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class CurriculumEvaluationModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for curriculum evaluations."""

    __tablename__ = "analytics_curriculum_evaluations"

    curriculum_balance: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    topic_coverage: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    redundant_content: Mapped[list | None] = mapped_column(JSON, nullable=True)
    missing_prerequisites: Mapped[list | None] = mapped_column(JSON, nullable=True)
    assessment_alignment: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    a11y_coverage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    localization_coverage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    content_freshness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    review_frequency_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ContentHealthItemModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for content health items."""

    __tablename__ = "analytics_content_health_items"

    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    title: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    version_status: Mapped[str] = mapped_column(String(32), default="current", nullable=False)
    broken_refs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    missing_metadata: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    doc_completeness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    localization_status: Mapped[str] = mapped_column(String(32), default="incomplete", nullable=False)
    a11y_status: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)
    last_reviewed_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    publication_quality: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    dependency_health: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class ContentHealthDashboardModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for content health dashboards."""

    __tablename__ = "analytics_content_health_dashboards"

    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    healthy: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    needs_attention: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    by_type: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ProgramEvaluationModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for program evaluations."""

    __tablename__ = "analytics_program_evaluations"

    program_name: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    period: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    effectiveness_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    competency_coverage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    course_performance: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    resource_utilization: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    instructor_workload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    certification_outcomes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    a11y_readiness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    governance_compliance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    doc_health: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ActionPlanModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for improvement action plans."""

    __tablename__ = "analytics_action_plans"

    title: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    description: Mapped[str] = mapped_column(String(1024), default="", nullable=False)
    owner: Mapped[str] = mapped_column(String(36), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="not_started", nullable=False)
    target_date: Mapped[str] = mapped_column(String(32), default="", nullable=False)


class ActionPlanItemModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for action plan items."""

    __tablename__ = "analytics_action_plan_items"

    plan_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(1024), default="", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    evidence: Mapped[list | None] = mapped_column(JSON, nullable=True)
    review_date: Mapped[str] = mapped_column(String(32), default="", nullable=False)


class ImprovementInitiativeModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for improvement initiatives."""

    __tablename__ = "analytics_improvement_initiatives"

    name: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    description: Mapped[str] = mapped_column(String(1024), default="", nullable=False)
    start_date: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    end_date: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    progress_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    assignees: Mapped[list | None] = mapped_column(JSON, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class ImprovementReportModel(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """ORM model for improvement reports."""

    __tablename__ = "analytics_improvement_reports"

    initiative_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    findings: Mapped[list | None] = mapped_column(JSON, nullable=True)
    next_steps: Mapped[list | None] = mapped_column(JSON, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
