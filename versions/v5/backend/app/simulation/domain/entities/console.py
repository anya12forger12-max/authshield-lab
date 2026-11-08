"""Console domain entities for instructor and learner sessions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SessionStatus(str, Enum):
    """Lifecycle status for instructor and learner sessions."""

    NOT_STARTED = "not_started"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Submission:
    """A learner submission within an exercise session."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    content: str = ""
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    feedback: str = ""
    grade: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "content": self.content,
            "submitted_at": self.submitted_at.isoformat(),
            "feedback": self.feedback,
            "grade": self.grade,
        }


@dataclass
class InstructorSession:
    """An instructor-led session for guiding learners through an exercise.

    Tracks instructor activity including launch, pause, resume, and
    feedback lifecycle.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    instructor_id: str = ""
    exercise_id: str = ""
    status: SessionStatus = SessionStatus.NOT_STARTED
    started_at: datetime | None = None
    paused_at: datetime | None = None
    ended_at: datetime | None = None
    notes: str = ""

    def launch(self) -> None:
        """Transition the session to active and record the start time."""
        if self.status != SessionStatus.NOT_STARTED:
            raise ValueError(
                f"Cannot launch session from '{self.status.value}' status"
            )
        self.status = SessionStatus.ACTIVE
        self.started_at = datetime.now(timezone.utc)

    def pause(self) -> None:
        """Pause an active session."""
        if self.status != SessionStatus.ACTIVE:
            raise ValueError(
                f"Cannot pause session from '{self.status.value}' status"
            )
        self.status = SessionStatus.PAUSED
        self.paused_at = datetime.now(timezone.utc)

    def resume(self) -> None:
        """Resume a paused session."""
        if self.status != SessionStatus.PAUSED:
            raise ValueError(
                f"Cannot resume session from '{self.status.value}' status"
            )
        self.status = SessionStatus.ACTIVE
        self.paused_at = None

    def complete(self) -> None:
        """Complete the session."""
        if self.status not in (SessionStatus.ACTIVE, SessionStatus.PAUSED):
            raise ValueError(
                f"Cannot complete session from '{self.status.value}' status"
            )
        self.status = SessionStatus.COMPLETED
        self.ended_at = datetime.now(timezone.utc)

    def get_elapsed_seconds(self) -> float:
        """Calculate elapsed active time in seconds."""
        if self.started_at is None:
            return 0.0
        end = self.ended_at or datetime.now(timezone.utc)
        elapsed = (end - self.started_at).total_seconds()
        if self.paused_at is not None and self.ended_at is None:
            paused_duration = (datetime.now(timezone.utc) - self.paused_at).total_seconds()
            elapsed -= paused_duration
        return max(0.0, elapsed)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "instructor_id": self.instructor_id,
            "exercise_id": self.exercise_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "notes": self.notes,
        }


@dataclass
class LearnerSession:
    """A learner's individual session for completing an exercise.

    Tracks progress, evidence collection, reflection, accessibility,
    and submission history.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str = ""
    exercise_id: str = ""
    status: SessionStatus = SessionStatus.NOT_STARTED
    started_at: datetime | None = None
    progress: float = 0.0
    evidence: list[str] = field(default_factory=list)
    notes: str = ""
    reflection_journal: list[str] = field(default_factory=list)
    accessibility_settings: dict[str, Any] = field(default_factory=dict)
    submissions: list[Submission] = field(default_factory=list)

    def start(self) -> None:
        """Start the learner session."""
        if self.status != SessionStatus.NOT_STARTED:
            raise ValueError(
                f"Cannot start session from '{self.status.value}' status"
            )
        self.status = SessionStatus.ACTIVE
        self.started_at = datetime.now(timezone.utc)

    def add_evidence(self, evidence_item: str) -> None:
        """Record an evidence item."""
        self.evidence.append(evidence_item)
        self._update_progress()

    def add_reflection(self, reflection: str) -> None:
        """Add a reflection journal entry."""
        self.reflection_journal.append(reflection)

    def submit(self, content: str) -> Submission:
        """Create and record a submission."""
        submission = Submission(session_id=self.id, content=content)
        self.submissions.append(submission)
        return submission

    def complete(self) -> None:
        """Mark the session as completed."""
        if self.status != SessionStatus.ACTIVE:
            raise ValueError(
                f"Cannot complete session from '{self.status.value}' status"
            )
        self.status = SessionStatus.COMPLETED
        self.progress = 1.0

    def _update_progress(self) -> None:
        """Update progress based on evidence count (capped at 1.0)."""
        self.progress = min(1.0, len(self.evidence) * 0.1)

    def get_submission_count(self) -> int:
        """Return total number of submissions."""
        return len(self.submissions)

    def get_average_grade(self) -> float:
        """Return average grade across all graded submissions."""
        graded = [s for s in self.submissions if s.grade > 0]
        if not graded:
            return 0.0
        return sum(s.grade for s in graded) / len(graded)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "learner_id": self.learner_id,
            "exercise_id": self.exercise_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "progress": self.progress,
            "evidence": list(self.evidence),
            "notes": self.notes,
            "reflection_journal": list(self.reflection_journal),
            "accessibility_settings": dict(self.accessibility_settings),
            "submissions": [s.to_dict() for s in self.submissions],
        }
