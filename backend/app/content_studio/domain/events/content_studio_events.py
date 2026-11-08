"""Content Production Studio domain event definitions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ContentStudioDomainEvent:
    """Base class for all content studio domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    module: str = "content_studio"
    severity: str = "info"
    metadata: dict = field(default_factory=dict)


@dataclass
class CourseDesigned(ContentStudioDomainEvent):
    """Published when a new course design is created."""

    event_type: str = "content_studio.course.designed"
    course_id: str = ""
    course_name: str = ""
    program_id: str = ""
    created_by: str = ""


@dataclass
class LessonCreated(ContentStudioDomainEvent):
    """Published when a new lesson is added to a module."""

    event_type: str = "content_studio.lesson.created"
    lesson_id: str = ""
    module_id: str = ""
    lesson_name: str = ""
    content_block_count: int = 0


@dataclass
class VirtualLabCreated(ContentStudioDomainEvent):
    """Published when a new virtual lab is created."""

    event_type: str = "content_studio.virtual_lab.created"
    lab_id: str = ""
    lab_name: str = ""
    lab_type: str = ""
    step_count: int = 0


@dataclass
class PublishRequested(ContentStudioDomainEvent):
    """Published when content is submitted for publishing."""

    event_type: str = "content_studio.publish.requested"
    request_id: str = ""
    content_id: str = ""
    content_type: str = ""
    version: int = 1
    requested_by: str = ""


@dataclass
class ContentPublished(ContentStudioDomainEvent):
    """Published when content is successfully published."""

    event_type: str = "content_studio.publish.completed"
    content_id: str = ""
    content_type: str = ""
    version: int = 1
    published_by: str = ""


@dataclass
class ReviewAdvanced(ContentStudioDomainEvent):
    """Published when a review moves to the next stage."""

    event_type: str = "content_studio.review.advanced"
    review_id: str = ""
    content_id: str = ""
    from_stage: str = ""
    to_stage: str = ""


@dataclass
class A11yValidationCompleted(ContentStudioDomainEvent):
    """Published when accessibility validation finishes."""

    event_type: str = "content_studio.a11y.validation_completed"
    report_id: str = ""
    content_id: str = ""
    compliance_pct: float = 0.0
    total_checks: int = 0
    passed_checks: int = 0


@dataclass
class TemplateCreated(ContentStudioDomainEvent):
    """Published when a new content template is created."""

    event_type: str = "content_studio.template.created"
    template_id: str = ""
    template_name: str = ""
    template_type: str = ""
    created_by: str = ""
