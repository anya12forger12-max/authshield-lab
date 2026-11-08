"""Content domain events."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ContentEvent:
    """Base class for all content domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    module: str = "content"
    message: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class CourseCreated(ContentEvent):
    """Published when a new course is created."""

    event_type: str = "content.course.created"
    course_id: str = ""
    title: str = ""
    created_by: str = ""


@dataclass
class CoursePublished(ContentEvent):
    """Published when a course is published."""

    event_type: str = "content.course.published"
    course_id: str = ""
    title: str = ""
    version: int = 1


@dataclass
class CourseArchived(ContentEvent):
    """Published when a course is archived."""

    event_type: str = "content.course.archived"
    course_id: str = ""
    title: str = ""


@dataclass
class LessonCreated(ContentEvent):
    """Published when a new lesson is created."""

    event_type: str = "content.lesson.created"
    lesson_id: str = ""
    course_id: str = ""
    title: str = ""


@dataclass
class QuizCreated(ContentEvent):
    """Published when a new quiz is created."""

    event_type: str = "content.quiz.created"
    quiz_id: str = ""
    course_id: str = ""
    title: str = ""


@dataclass
class QuizGraded(ContentEvent):
    """Published when a quiz has been graded."""

    event_type: str = "content.quiz.graded"
    quiz_id: str = ""
    score: float = 0.0
    passing_score: float = 70.0
    passed: bool = False


@dataclass
class MediaUploaded(ContentEvent):
    """Published when a media asset is uploaded/registered."""

    event_type: str = "content.media.uploaded"
    asset_id: str = ""
    media_type: str = ""
    title: str = ""


@dataclass
class AssessmentCompleted(ContentEvent):
    """Published when an assessment is completed."""

    event_type: str = "content.assessment.completed"
    assessment_id: str = ""
    score: float = 0.0
    passed: bool = False


@dataclass
class ContentVersioned(ContentEvent):
    """Published when content is versioned."""

    event_type: str = "content.versioned"
    content_id: str = ""
    content_type: str = ""
    previous_version: int = 0
    new_version: int = 0


@dataclass
class AccessibilityReviewCompleted(ContentEvent):
    """Published when an accessibility review is completed."""

    event_type: str = "content.accessibility.review_completed"
    content_id: str = ""
    content_type: str = ""
    issues_found: int = 0
    passed: bool = True
