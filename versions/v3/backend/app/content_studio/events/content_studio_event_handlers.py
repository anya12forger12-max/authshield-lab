"""Content Production Studio domain event handlers."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ContentStudioEventHandler:
    """Handles content studio domain events for logging, auditing, and side effects."""

    def __init__(self) -> None:
        self._handlers_registered = False

    def register_handlers(self, event_bus: Any) -> None:
        """Register all content studio event handlers on the provided event bus."""
        if self._handlers_registered:
            return

        from ..domain.events.content_studio_events import (
            A11yValidationCompleted,
            ContentPublished,
            CourseDesigned,
            LessonCreated,
            PublishRequested,
            ReviewAdvanced,
            TemplateCreated,
            VirtualLabCreated,
        )

        event_bus.subscribe_course_designed(self._on_course_designed)
        event_bus.subscribe_lesson_created(self._on_lesson_created)
        event_bus.subscribe_virtual_lab_created(self._on_virtual_lab_created)
        event_bus.subscribe_publish_requested(self._on_publish_requested)
        event_bus.subscribe_content_published(self._on_content_published)
        event_bus.subscribe_review_advanced(self._on_review_advanced)
        event_bus.subscribe_a11y_validation_completed(self._on_a11y_validation_completed)
        event_bus.subscribe_template_created(self._on_template_created)

        self._handlers_registered = True
        logger.info("content_studio_event_handlers_registered")

    def _on_course_designed(self, event: Any) -> None:
        logger.info(
            "Content Studio Event: Course designed",
            extra={
                "course_id": getattr(event, "course_id", ""),
                "course_name": getattr(event, "course_name", ""),
                "program_id": getattr(event, "program_id", ""),
                "created_by": getattr(event, "created_by", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_lesson_created(self, event: Any) -> None:
        logger.info(
            "Content Studio Event: Lesson created",
            extra={
                "lesson_id": getattr(event, "lesson_id", ""),
                "module_id": getattr(event, "module_id", ""),
                "lesson_name": getattr(event, "lesson_name", ""),
                "content_block_count": getattr(event, "content_block_count", 0),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_virtual_lab_created(self, event: Any) -> None:
        logger.info(
            "Content Studio Event: Virtual lab created",
            extra={
                "lab_id": getattr(event, "lab_id", ""),
                "lab_name": getattr(event, "lab_name", ""),
                "lab_type": getattr(event, "lab_type", ""),
                "step_count": getattr(event, "step_count", 0),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_publish_requested(self, event: Any) -> None:
        logger.info(
            "Content Studio Event: Publish requested",
            extra={
                "request_id": getattr(event, "request_id", ""),
                "content_id": getattr(event, "content_id", ""),
                "content_type": getattr(event, "content_type", ""),
                "version": getattr(event, "version", 1),
                "requested_by": getattr(event, "requested_by", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_content_published(self, event: Any) -> None:
        logger.info(
            "Content Studio Event: Content published",
            extra={
                "content_id": getattr(event, "content_id", ""),
                "content_type": getattr(event, "content_type", ""),
                "version": getattr(event, "version", 1),
                "published_by": getattr(event, "published_by", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_review_advanced(self, event: Any) -> None:
        logger.info(
            "Content Studio Event: Review advanced",
            extra={
                "review_id": getattr(event, "review_id", ""),
                "content_id": getattr(event, "content_id", ""),
                "from_stage": getattr(event, "from_stage", ""),
                "to_stage": getattr(event, "to_stage", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_a11y_validation_completed(self, event: Any) -> None:
        logger.info(
            "Content Studio Event: A11y validation completed",
            extra={
                "report_id": getattr(event, "report_id", ""),
                "content_id": getattr(event, "content_id", ""),
                "compliance_pct": getattr(event, "compliance_pct", 0.0),
                "total_checks": getattr(event, "total_checks", 0),
                "passed_checks": getattr(event, "passed_checks", 0),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_template_created(self, event: Any) -> None:
        logger.info(
            "Content Studio Event: Template created",
            extra={
                "template_id": getattr(event, "template_id", ""),
                "template_name": getattr(event, "template_name", ""),
                "template_type": getattr(event, "template_type", ""),
                "created_by": getattr(event, "created_by", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )
