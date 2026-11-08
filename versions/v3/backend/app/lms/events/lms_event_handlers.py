"""LMS domain event handlers."""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LmsEventHandler:
    """Handles LMS domain events for logging, auditing, and side effects."""

    def __init__(self) -> None:
        self._handlers_registered = False

    def register_handlers(self, event_bus: Any) -> None:
        """Register all LMS event handlers on the provided event bus."""
        if self._handlers_registered:
            return

        from ..domain.events.lms_events import (
            ClassroomCreated,
            ClassroomUpdated,
            EnrollmentCreated,
            EnrollmentCompleted,
            GradeSubmitted,
            CompetencyAchieved,
            AssessmentAttempted,
            PortfolioItemAdded,
            CalendarEventCreated,
        )

        event_bus.subscribe_classroom_created(self._on_classroom_created)
        event_bus.subscribe_classroom_updated(self._on_classroom_updated)
        event_bus.subscribe_enrollment_created(self._on_enrollment_created)
        event_bus.subscribe_enrollment_completed(self._on_enrollment_completed)
        event_bus.subscribe_grade_submitted(self._on_grade_submitted)
        event_bus.subscribe_competency_achieved(self._on_competency_achieved)
        event_bus.subscribe_assessment_attempted(self._on_assessment_attempted)
        event_bus.subscribe_portfolio_item_added(self._on_portfolio_item_added)
        event_bus.subscribe_calendar_event_created(self._on_calendar_event_created)

        self._handlers_registered = True
        logger.info("lms_event_handlers_registered")

    def _on_classroom_created(self, event: Any) -> None:
        logger.info(
            "LMS Event: Classroom created",
            extra={
                "classroom_id": getattr(event, "classroom_id", ""),
                "classroom_name": getattr(event, "classroom_name", ""),
                "instructor_id": getattr(event, "instructor_id", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_classroom_updated(self, event: Any) -> None:
        logger.info(
            "LMS Event: Classroom updated",
            extra={
                "classroom_id": getattr(event, "classroom_id", ""),
                "changes": getattr(event, "changes", {}),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_enrollment_created(self, event: Any) -> None:
        logger.info(
            "LMS Event: Enrollment created",
            extra={
                "enrollment_id": getattr(event, "enrollment_id", ""),
                "learner_id": getattr(event, "learner_id", ""),
                "course_id": getattr(event, "course_id", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_enrollment_completed(self, event: Any) -> None:
        logger.info(
            "LMS Event: Enrollment completed",
            extra={
                "enrollment_id": getattr(event, "enrollment_id", ""),
                "learner_id": getattr(event, "learner_id", ""),
                "course_id": getattr(event, "course_id", ""),
                "grade": getattr(event, "grade", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_grade_submitted(self, event: Any) -> None:
        logger.info(
            "LMS Event: Grade submitted",
            extra={
                "grade_entry_id": getattr(event, "grade_entry_id", ""),
                "learner_id": getattr(event, "learner_id", ""),
                "score": getattr(event, "score", 0.0),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_competency_achieved(self, event: Any) -> None:
        logger.info(
            "LMS Event: Competency achieved",
            extra={
                "progress_id": getattr(event, "progress_id", ""),
                "learner_id": getattr(event, "learner_id", ""),
                "competency_id": getattr(event, "competency_id", ""),
                "status": getattr(event, "status", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_assessment_attempted(self, event: Any) -> None:
        logger.info(
            "LMS Event: Assessment attempted",
            extra={
                "attempt_id": getattr(event, "attempt_id", ""),
                "assessment_id": getattr(event, "assessment_id", ""),
                "learner_id": getattr(event, "learner_id", ""),
                "score": getattr(event, "score", 0.0),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_portfolio_item_added(self, event: Any) -> None:
        logger.info(
            "LMS Event: Portfolio item added",
            extra={
                "portfolio_id": getattr(event, "portfolio_id", ""),
                "item_id": getattr(event, "item_id", ""),
                "learner_id": getattr(event, "learner_id", ""),
                "item_type": getattr(event, "item_type", ""),
                "event_id": getattr(event, "event_id", ""),
            },
        )

    def _on_calendar_event_created(self, event: Any) -> None:
        logger.info(
            "LMS Event: Calendar event created",
            extra={
                "calendar_id": getattr(event, "calendar_id", ""),
                "event_id": getattr(event, "event_id", ""),
                "event_title": getattr(event, "event_title", ""),
                "event_type_detail": getattr(event, "event_type_detail", ""),
            },
        )
