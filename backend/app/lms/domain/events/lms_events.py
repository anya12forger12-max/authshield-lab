"""LMS domain event definitions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LmsDomainEvent:
    """Base class for all LMS domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    module: str = "lms"
    severity: str = "info"
    metadata: dict = field(default_factory=dict)


@dataclass
class ClassroomCreated(LmsDomainEvent):
    """Published when a new classroom is created."""

    event_type: str = "lms.classroom.created"
    classroom_id: str = ""
    classroom_name: str = ""
    instructor_id: str = ""


@dataclass
class ClassroomUpdated(LmsDomainEvent):
    """Published when a classroom is updated."""

    event_type: str = "lms.classroom.updated"
    classroom_id: str = ""
    classroom_name: str = ""
    changes: dict = field(default_factory=dict)


@dataclass
class EnrollmentCreated(LmsDomainEvent):
    """Published when a new enrollment is created."""

    event_type: str = "lms.enrollment.created"
    enrollment_id: str = ""
    learner_id: str = ""
    course_id: str = ""


@dataclass
class EnrollmentCompleted(LmsDomainEvent):
    """Published when an enrollment is completed."""

    event_type: str = "lms.enrollment.completed"
    enrollment_id: str = ""
    learner_id: str = ""
    course_id: str = ""
    grade: str = ""


@dataclass
class GradeSubmitted(LmsDomainEvent):
    """Published when a grade is submitted."""

    event_type: str = "lms.grade.submitted"
    grade_entry_id: str = ""
    learner_id: str = ""
    grade_item_id: str = ""
    score: float = 0.0


@dataclass
class CompetencyAchieved(LmsDomainEvent):
    """Published when a learner achieves a competency."""

    event_type: str = "lms.competency.achieved"
    progress_id: str = ""
    learner_id: str = ""
    competency_id: str = ""
    status: str = ""


@dataclass
class AssessmentAttempted(LmsDomainEvent):
    """Published when a learner submits an assessment attempt."""

    event_type: str = "lms.assessment.attempted"
    attempt_id: str = ""
    assessment_id: str = ""
    learner_id: str = ""
    attempt_number: int = 0
    score: float = 0.0


@dataclass
class PortfolioItemAdded(LmsDomainEvent):
    """Published when an item is added to a portfolio."""

    event_type: str = "lms.portfolio.item_added"
    portfolio_id: str = ""
    item_id: str = ""
    learner_id: str = ""
    item_type: str = ""


@dataclass
class CalendarEventCreated(LmsDomainEvent):
    """Published when an academic calendar event is created."""

    event_type: str = "lms.calendar.event_created"
    calendar_id: str = ""
    event_id: str = ""
    event_title: str = ""
    event_type_detail: str = ""
