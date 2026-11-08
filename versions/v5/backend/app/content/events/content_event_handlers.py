"""Content domain event handlers – logging, stats, and accessibility triggers."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from ..domain.events.content_events import (
    ContentEvent,
    CourseCreated,
    CoursePublished,
    CourseArchived,
    LessonCreated,
    QuizCreated,
    QuizGraded,
    MediaUploaded,
    AssessmentCompleted,
    ContentVersioned,
    AccessibilityReviewCompleted,
)

logger = logging.getLogger(__name__)

# In-memory stats counters (reset on process restart)
_stats: dict[str, Any] = {
    "courses_created": 0,
    "courses_published": 0,
    "courses_archived": 0,
    "lessons_created": 0,
    "quizzes_created": 0,
    "quizzes_graded": 0,
    "media_uploaded": 0,
    "assessments_completed": 0,
    "versions_created": 0,
    "accessibility_reviews": 0,
    "accessibility_issues_total": 0,
}

# Log of recently processed events
_recent_events: list[dict[str, Any]] = []
_MAX_RECENT = 500


def _append_recent(event: ContentEvent, handler_name: str) -> None:
    """Append an entry to the recent-events ring buffer."""
    entry = {
        "event_id": event.event_id,
        "event_type": getattr(event, "event_type", event.__class__.__name__),
        "handler": handler_name,
        "timestamp": event.timestamp.isoformat(),
        "message": event.message,
    }
    _recent_events.append(entry)
    if len(_recent_events) > _MAX_RECENT:
        _recent_events[:] = _recent_events[-_MAX_RECENT:]


async def handle_course_created(event: CourseCreated) -> None:
    """Log course creation and update stats."""
    _stats["courses_created"] += 1
    _append_recent(event, "handle_course_created")
    logger.info(
        "content.course.created | id=%s title='%s' created_by='%s'",
        event.course_id,
        event.title,
        event.created_by,
    )


async def handle_course_published(event: CoursePublished) -> None:
    """Log course publication and update stats."""
    _stats["courses_published"] += 1
    _append_recent(event, "handle_course_published")
    logger.info(
        "content.course.published | id=%s title='%s' version=%d",
        event.course_id,
        event.title,
        event.version,
    )


async def handle_course_archived(event: CourseArchived) -> None:
    """Log course archival and update stats."""
    _stats["courses_archived"] += 1
    _append_recent(event, "handle_course_archived")
    logger.info(
        "content.course.archived | id=%s title='%s'",
        event.course_id,
        event.title,
    )


async def handle_lesson_created(event: LessonCreated) -> None:
    """Log lesson creation and update stats."""
    _stats["lessons_created"] += 1
    _append_recent(event, "handle_lesson_created")
    logger.info(
        "content.lesson.created | id=%s course=%s title='%s'",
        event.lesson_id,
        event.course_id,
        event.title,
    )


async def handle_quiz_created(event: QuizCreated) -> None:
    """Log quiz creation and update stats."""
    _stats["quizzes_created"] += 1
    _append_recent(event, "handle_quiz_created")
    logger.info(
        "content.quiz.created | id=%s course=%s title='%s'",
        event.quiz_id,
        event.course_id,
        event.title,
    )


async def handle_quiz_graded(event: QuizGraded) -> None:
    """Log quiz grading, update stats, and flag accessibility if needed."""
    _stats["quizzes_graded"] += 1
    _append_recent(event, "handle_quiz_graded")
    logger.info(
        "content.quiz.graded | id=%s score=%.1f passing=%.1f passed=%s",
        event.quiz_id,
        event.score,
        event.passing_score,
        event.passed,
    )


async def handle_media_uploaded(event: MediaUploaded) -> None:
    """Log media upload and update stats."""
    _stats["media_uploaded"] += 1
    _append_recent(event, "handle_media_uploaded")
    logger.info(
        "content.media.uploaded | id=%s type='%s' title='%s'",
        event.asset_id,
        event.media_type,
        event.title,
    )


async def handle_assessment_completed(event: AssessmentCompleted) -> None:
    """Log assessment completion and update stats."""
    _stats["assessments_completed"] += 1
    _append_recent(event, "handle_assessment_completed")
    logger.info(
        "content.assessment.completed | id=%s score=%.1f passed=%s",
        event.assessment_id,
        event.score,
        event.passed,
    )


async def handle_content_versioned(event: ContentVersioned) -> None:
    """Log content versioning and update stats."""
    _stats["versions_created"] += 1
    _append_recent(event, "handle_content_versioned")
    logger.info(
        "content.versioned | id=%s type='%s' v%d → v%d",
        event.content_id,
        event.content_type,
        event.previous_version,
        event.new_version,
    )


async def handle_accessibility_review(event: AccessibilityReviewCompleted) -> None:
    """Log accessibility review and update stats."""
    _stats["accessibility_reviews"] += 1
    _stats["accessibility_issues_total"] += event.issues_found
    _append_recent(event, "handle_accessibility_review")
    log_fn = logger.info if event.passed else logger.warning
    log_fn(
        "content.accessibility.review_completed | id=%s type='%s' issues=%d passed=%s",
        event.content_id,
        event.content_type,
        event.issues_found,
        event.passed,
    )


def get_content_stats() -> dict[str, Any]:
    """Return a snapshot of the in-memory content stats counters."""
    return dict(_stats)


def get_recent_events(limit: int = 50) -> list[dict[str, Any]]:
    """Return the most recent content events."""
    return list(reversed(_recent_events[-limit:]))


def reset_stats() -> None:
    """Reset all stats counters to zero (useful in tests)."""
    for key in _stats:
        _stats[key] = 0
    _recent_events.clear()
