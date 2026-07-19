"""Enrollment domain entities for the LMS module."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class EnrollmentStatus(str, Enum):
    """Status of a learner's enrollment in a course."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    WAITLISTED = "waitlisted"


@dataclass
class Enrollment:
    """Represents a learner's enrollment in a course."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str = ""
    course_id: str = ""
    status: EnrollmentStatus = EnrollmentStatus.PENDING
    enrolled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    grade: Optional[str] = None

    def activate(self) -> None:
        """Transition enrollment to active."""
        if self.status != EnrollmentStatus.PENDING:
            raise ValueError(f"Cannot activate enrollment in '{self.status.value}' status.")
        self.status = EnrollmentStatus.ACTIVE

    def complete(self, grade: Optional[str] = None) -> None:
        """Mark the enrollment as completed."""
        if self.status != EnrollmentStatus.ACTIVE:
            raise ValueError(f"Cannot complete enrollment in '{self.status.value}' status.")
        self.status = EnrollmentStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.grade = grade

    def drop(self) -> None:
        """Drop the enrollment."""
        if self.status in (EnrollmentStatus.COMPLETED, EnrollmentStatus.DROPPED):
            raise ValueError(f"Cannot drop enrollment in '{self.status.value}' status.")
        self.status = EnrollmentStatus.DROPPED

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "learner_id": self.learner_id,
            "course_id": self.course_id,
            "status": self.status.value,
            "enrolled_at": self.enrolled_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "grade": self.grade,
        }


@dataclass
class WaitlistEntry:
    """A position on the waitlist for a course."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str = ""
    course_id: str = ""
    position: int = 1
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "learner_id": self.learner_id,
            "course_id": self.course_id,
            "position": self.position,
            "added_at": self.added_at.isoformat(),
        }


@dataclass
class CourseEnrollmentConfig:
    """Enrollment configuration for a course."""

    max_learners: int = 30
    enrollment_start: Optional[datetime] = None
    enrollment_end: Optional[datetime] = None
    prerequisites: list[str] = field(default_factory=list)

    def is_open(self) -> bool:
        """Return ``True`` if the current time is within the enrollment window."""
        now = datetime.now(timezone.utc)
        if self.enrollment_start and now < self.enrollment_start:
            return False
        if self.enrollment_end and now > self.enrollment_end:
            return False
        return True

    def can_enroll(
        self,
        current_enrollment: int,
        completed_prerequisites: Optional[list[str]] = None,
    ) -> bool:
        """Return ``True`` if a learner is eligible to enroll."""
        if not self.is_open():
            return False
        if current_enrollment >= self.max_learners:
            return False
        if self.prerequisites:
            completed = completed_prerequisites or []
            missing = set(self.prerequisites) - set(completed)
            if missing:
                return False
        return True

    def add_to_waitlist(
        self,
        current_enrollment: int,
        current_waitlist_size: int,
    ) -> int:
        """Return the next waitlist position.

        Returns
        -------
        int
            The 1-based position assigned to the new waitlist entry, or -1
            if enrollment is still open and the learner should enroll directly.
        """
        if self.can_enroll(current_enrollment):
            return -1
        return current_waitlist_size + 1

    def to_dict(self) -> dict:
        return {
            "max_learners": self.max_learners,
            "enrollment_start": self.enrollment_start.isoformat() if self.enrollment_start else None,
            "enrollment_end": self.enrollment_end.isoformat() if self.enrollment_end else None,
            "prerequisites": list(self.prerequisites),
        }
