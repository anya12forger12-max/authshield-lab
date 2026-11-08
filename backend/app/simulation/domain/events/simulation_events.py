"""Simulation domain events for decoupled module communication."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ScenarioCreated:
    """Emitted when a new scenario is created."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str = ""
    title: str = ""
    scenario_type: str = ""
    created_by: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "scenario_id": self.scenario_id,
            "title": self.title,
            "scenario_type": self.scenario_type,
            "created_by": self.created_by,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ScenarioPublished:
    """Emitted when a scenario transitions to published status."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str = ""
    title: str = ""
    version: int = 1
    published_by: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "scenario_id": self.scenario_id,
            "title": self.title,
            "version": self.version,
            "published_by": self.published_by,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ScenarioArchived:
    """Emitted when a scenario transitions to archived status."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str = ""
    title: str = ""
    archived_by: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "scenario_id": self.scenario_id,
            "title": self.title,
            "archived_by": self.archived_by,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ExerciseLaunched:
    """Emitted when an exercise session is started."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exercise_id: str = ""
    session_id: str = ""
    launched_by: str = ""
    session_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "exercise_id": self.exercise_id,
            "session_id": self.session_id,
            "launched_by": self.launched_by,
            "session_type": self.session_type,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ExerciseCompleted:
    """Emitted when an exercise session is completed."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exercise_id: str = ""
    session_id: str = ""
    completed_by: str = ""
    overall_score: float = 0.0
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "exercise_id": self.exercise_id,
            "session_id": self.session_id,
            "completed_by": self.completed_by,
            "overall_score": self.overall_score,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DatasetGenerated:
    """Emitted when a synthetic dataset is generated."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dataset_id: str = ""
    name: str = ""
    seed: int = 0
    artifact_count: int = 0
    total_records: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "dataset_id": self.dataset_id,
            "name": self.name,
            "seed": self.seed,
            "artifact_count": self.artifact_count,
            "total_records": self.total_records,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class TimelineCreated:
    """Emitted when a new timeline is created."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timeline_id: str = ""
    scenario_id: str = ""
    event_count: int = 0
    total_duration_ms: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "timeline_id": self.timeline_id,
            "scenario_id": self.scenario_id,
            "event_count": self.event_count,
            "total_duration_ms": self.total_duration_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SubmissionReceived:
    """Emitted when a learner submits work for an exercise."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    submission_id: str = ""
    exercise_id: str = ""
    learner_id: str = ""
    content_preview: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "submission_id": self.submission_id,
            "exercise_id": self.exercise_id,
            "learner_id": self.learner_id,
            "content_preview": self.content_preview,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ResultsCalculated:
    """Emitted when exercise results are computed and stored."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    result_id: str = ""
    session_id: str = ""
    exercise_id: str = ""
    overall_score: float = 0.0
    completion_status: str = ""
    recommendation_count: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "result_id": self.result_id,
            "session_id": self.session_id,
            "exercise_id": self.exercise_id,
            "overall_score": self.overall_score,
            "completion_status": self.completion_status,
            "recommendation_count": self.recommendation_count,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReplayStarted:
    """Emitted when a timeline replay is initiated."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timeline_id: str = ""
    scenario_id: str = ""
    initiated_by: str = ""
    speed_multiplier: float = 1.0
    highlighted_events: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "timeline_id": self.timeline_id,
            "scenario_id": self.scenario_id,
            "initiated_by": self.initiated_by,
            "speed_multiplier": self.speed_multiplier,
            "highlighted_events": list(self.highlighted_events),
            "timestamp": self.timestamp.isoformat(),
        }
