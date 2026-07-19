"""Assessment domain entities for the LMS module."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class AssessmentType(str, Enum):
    """Type of assessment."""

    QUIZ = "quiz"
    EXAM = "exam"
    PROJECT = "project"
    PORTFOLIO = "portfolio"
    PRACTICAL = "practical"


class AssessmentStatus(str, Enum):
    """Status of an assessment."""

    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    ARCHIVED = "archived"


@dataclass
class LmsAssessment:
    """An assessment (quiz, exam, project, etc.) within a course."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    assessment_type: AssessmentType = AssessmentType.QUIZ
    course_id: str = ""
    passing_score: float = 70.0
    time_limit_minutes: Optional[int] = None
    attempts_allowed: int = 1
    status: AssessmentStatus = AssessmentStatus.DRAFT

    def publish(self) -> None:
        if self.status != AssessmentStatus.DRAFT:
            raise ValueError(f"Cannot publish assessment in '{self.status.value}' status.")
        self.status = AssessmentStatus.PUBLISHED

    def close(self) -> None:
        if self.status != AssessmentStatus.PUBLISHED:
            raise ValueError(f"Cannot close assessment in '{self.status.value}' status.")
        self.status = AssessmentStatus.CLOSED

    def archive(self) -> None:
        if self.status == AssessmentStatus.DRAFT:
            raise ValueError("Cannot archive a draft assessment.")
        self.status = AssessmentStatus.ARCHIVED

    def is_passed(self, score: float) -> bool:
        return score >= self.passing_score

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "assessment_type": self.assessment_type.value,
            "course_id": self.course_id,
            "passing_score": self.passing_score,
            "time_limit_minutes": self.time_limit_minutes,
            "attempts_allowed": self.attempts_allowed,
            "status": self.status.value,
        }


@dataclass
class AssessmentAttempt:
    """A single attempt by a learner on an assessment."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    assessment_id: str = ""
    learner_id: str = ""
    attempt_number: int = 1
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: Optional[datetime] = None
    score: Optional[float] = None
    feedback: Optional[str] = None

    def submit(self, score: float, feedback: Optional[str] = None) -> None:
        if self.submitted_at is not None:
            raise ValueError("This attempt has already been submitted.")
        self.submitted_at = datetime.now(timezone.utc)
        self.score = score
        if feedback:
            self.feedback = feedback

    @property
    def is_submitted(self) -> bool:
        return self.submitted_at is not None

    @property
    def is_passed(self) -> bool:
        """Return ``True`` if the score is non-None and >= 70.

        Note: caller should compare against the assessment's passing_score
        for real use; this is a convenience default.
        """
        if self.score is None:
            return False
        return self.score >= 70.0

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.submitted_at is None:
            return None
        delta = self.submitted_at - self.started_at
        return max(0.0, delta.total_seconds())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "learner_id": self.learner_id,
            "attempt_number": self.attempt_number,
            "started_at": self.started_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "score": self.score,
            "feedback": self.feedback,
            "is_submitted": self.is_submitted,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class Submission:
    """Content submitted as part of an assessment attempt."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attempt_id: str = ""
    content: str = ""
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    attachments: list[str] = field(default_factory=list)

    def add_attachment(self, attachment: str) -> None:
        if not attachment.strip():
            raise ValueError("Attachment path cannot be empty.")
        self.attachments.append(attachment.strip())

    def remove_attachment(self, attachment: str) -> bool:
        try:
            self.attachments.remove(attachment)
            return True
        except ValueError:
            return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "attempt_id": self.attempt_id,
            "content": self.content,
            "submitted_at": self.submitted_at.isoformat(),
            "attachments": list(self.attachments),
        }


@dataclass
class QuestionGroup:
    """A weighted group of questions within an assessment."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    assessment_id: str = ""
    name: str = ""
    questions: list[dict[str, Any]] = field(default_factory=list)
    weight: float = 1.0

    def add_question(self, question: dict[str, Any]) -> None:
        if not question:
            raise ValueError("Question data cannot be empty.")
        self.questions.append(question)

    def remove_question(self, index: int) -> dict[str, Any]:
        if index < 0 or index >= len(self.questions):
            raise IndexError(f"Question index {index} out of range.")
        return self.questions.pop(index)

    @property
    def question_count(self) -> int:
        return len(self.questions)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "name": self.name,
            "questions": list(self.questions),
            "weight": self.weight,
            "question_count": self.question_count,
        }
