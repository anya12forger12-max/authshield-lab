"""SQLAlchemy ORM models for the simulation module."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from ....shared.base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ScenarioModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for simulation scenarios."""

    __tablename__ = "simulation_scenarios"

    title: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")
    learning_objectives_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    prerequisites_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    target_audience: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    required_competencies_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    tags_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    scenario_type: Mapped[str] = mapped_column(String(64), nullable=False, default="AuthenticationReview")
    scenario_metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True, default=None)


class DatasetModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for synthetic datasets."""

    __tablename__ = "simulation_datasets"

    name: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    seed: Mapped[int] = mapped_column(Integer, nullable=False, default=42)
    metadata_creator: Mapped[str] = mapped_column(String(256), nullable=False, default="system")
    metadata_generation_date: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    metadata_total_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_checksum: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class DatasetArtifactModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for individual artifacts within a dataset."""

    __tablename__ = "simulation_dataset_artifacts"

    dataset_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    artifact_type: Mapped[str] = mapped_column(String(32), nullable=False, default="auth_log")
    name: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    content_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class TimelineModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for simulation timelines."""

    __tablename__ = "simulation_timelines"

    name: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    scenario_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    total_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class TimelineEventModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for individual events within a timeline."""

    __tablename__ = "simulation_timeline_events"

    timeline_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    timestamp_offset_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    data_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    milestone: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    instructor_annotation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    learner_checkpoint: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    replay_marker: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class TimelineBranchModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for branch paths within a timeline."""

    __tablename__ = "simulation_timeline_branches"

    timeline_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    source_event_id: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    target_event_id: Mapped[str] = mapped_column(String(36), nullable=False, default="")
    condition: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ExerciseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for exercises."""

    __tablename__ = "simulation_exercises"

    title: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    scenario_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    tags_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    learning_outcomes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    estimated_completion_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")


class InstructorSessionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for instructor-led sessions."""

    __tablename__ = "simulation_instructor_sessions"

    instructor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    exercise_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started")
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")


class LearnerSessionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for learner exercise sessions."""

    __tablename__ = "simulation_learner_sessions"

    learner_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    exercise_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started")
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    reflection_journal_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    accessibility_settings_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class SubmissionModel(Base, UUIDPrimaryKeyMixin):
    """ORM model for learner submissions."""

    __tablename__ = "simulation_submissions"

    session_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    feedback: Mapped[str] = mapped_column(Text, nullable=False, default="")
    grade: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ExerciseResultModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ORM model for exercise assessment results."""

    __tablename__ = "simulation_exercise_results"

    session_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    exercise_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    completion_status: Mapped[str] = mapped_column(String(20), nullable=False, default="incomplete")
    assessment_scores_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    competency_progress_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    reflection_responses_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    instructor_feedback: Mapped[str] = mapped_column(Text, nullable=False, default="")
    rubric_results_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    accessibility_usage_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    time_on_task_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    improvement_recommendations_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
