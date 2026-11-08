"""Lesson management service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.content import Lesson
from ..domain.events.content_events import LessonCreated
from ..domain.interfaces.content_repository import LessonRepository
from ..validators.content_validator import ContentValidator


class LessonService:
    """Service for managing lessons within courses.

    Parameters
    ----------
    repo:
        Repository for lesson persistence.
    validator:
        Content validation rules.
    """

    def __init__(self, repo: LessonRepository, validator: ContentValidator | None = None) -> None:
        self._repo = repo
        self._validator = validator or ContentValidator()
        self._events: list[Any] = []

    def _record_event(self, event: Any) -> None:
        self._events.append(event)

    async def create_lesson(
        self,
        course_id: str,
        title: str,
        content: str = "",
        order: int = 0,
        lesson_type: str = "theory",
        estimated_minutes: int = 30,
        learning_objectives: list[str] | None = None,
        media_refs: list[str] | None = None,
        accessible: bool = True,
    ) -> Lesson:
        """Create a new lesson, validate, persist, and emit a creation event."""
        title_result = self._validator.validate_title(title)
        if not title_result.is_valid:
            error_messages = [e.message for e in title_result.errors]
            raise ValueError(f"Lesson validation failed: {'; '.join(error_messages)}")
        if order <= 0:
            existing = await self._repo.find_by_course(course_id)
            order = max((l.order for l in existing), default=0) + 1
        lesson = Lesson(
            course_id=course_id,
            title=title,
            content=content,
            order=order,
            lesson_type=lesson_type,
            estimated_minutes=estimated_minutes,
            learning_objectives=learning_objectives or [],
            media_refs=media_refs or [],
            accessible=accessible,
        )
        await self._repo.save(lesson)
        event = LessonCreated(
            lesson_id=lesson.id,
            course_id=lesson.course_id,
            title=lesson.title,
            correlation_id=lesson.course_id,
            message=f"Lesson '{lesson.title}' created in course {lesson.course_id}.",
        )
        self._record_event(event)
        return lesson

    async def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """Retrieve a single lesson by ID."""
        return await self._repo.find_by_id(lesson_id)

    async def list_lessons_by_course(self, course_id: str) -> list[Lesson]:
        """List all lessons for a course, ordered by their ``order`` field."""
        return await self._repo.find_by_course(course_id)

    async def update_lesson(self, lesson_id: str, updates: dict[str, Any]) -> Lesson:
        """Apply partial updates to a lesson."""
        lesson = await self._repo.find_by_id(lesson_id)
        if lesson is None:
            raise ValueError(f"Lesson {lesson_id} not found.")
        allowed_fields = {
            "title",
            "content",
            "order",
            "lesson_type",
            "estimated_minutes",
            "learning_objectives",
            "media_refs",
            "accessible",
            "localized",
        }
        for key, value in updates.items():
            if key in allowed_fields:
                setattr(lesson, key, value)
        if "title" in updates:
            title_result = self._validator.validate_title(lesson.title)
            if not title_result.is_valid:
                error_messages = [e.message for e in title_result.errors]
                raise ValueError(f"Lesson validation failed: {'; '.join(error_messages)}")
        await self._repo.save(lesson)
        return lesson

    async def reorder_lessons(self, course_id: str, ordered_ids: list[str]) -> bool:
        """Reorder lessons within a course.

        ``ordered_ids`` specifies the new order. Any lesson in the course not
        present in the list is moved to the end.
        """
        existing = await self._repo.find_by_course(course_id)
        existing_ids = [l.id for l in existing]
        missing = [lid for lid in existing_ids if lid not in ordered_ids]
        full_order = ordered_ids + missing
        success = await self._repo.reorder(course_id, full_order)
        return success

    async def attach_media(self, lesson_id: str, media_id: str) -> Lesson:
        """Attach a media asset reference to a lesson."""
        lesson = await self._repo.find_by_id(lesson_id)
        if lesson is None:
            raise ValueError(f"Lesson {lesson_id} not found.")
        if media_id not in lesson.media_refs:
            lesson.media_refs.append(media_id)
            await self._repo.save(lesson)
        return lesson

    async def remove_media(self, lesson_id: str, media_id: str) -> Lesson:
        """Remove a media asset reference from a lesson."""
        lesson = await self._repo.find_by_id(lesson_id)
        if lesson is None:
            raise ValueError(f"Lesson {lesson_id} not found.")
        if media_id in lesson.media_refs:
            lesson.media_refs.remove(media_id)
            await self._repo.save(lesson)
        return lesson

    async def validate_lesson(self, lesson_id: str) -> dict[str, Any]:
        """Validate a lesson and return a results dict."""
        lesson = await self._repo.find_by_id(lesson_id)
        if lesson is None:
            raise ValueError(f"Lesson {lesson_id} not found.")
        errors: list[str] = []
        warnings: list[str] = []
        title_result = self._validator.validate_title(lesson.title)
        if not title_result.is_valid:
            errors.extend(e.message for e in title_result.errors)
        if not lesson.content:
            warnings.append("Lesson content is empty.")
        valid_types = {"theory", "lab", "quiz", "discussion"}
        if lesson.lesson_type not in valid_types:
            errors.append(f"Invalid lesson_type '{lesson.lesson_type}'.")
        if lesson.estimated_minutes < 1:
            warnings.append("Estimated minutes is less than 1.")
        if not lesson.accessible:
            warnings.append("Lesson is not marked as accessible.")
        return {
            "lesson_id": lesson.id,
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    async def get_lesson_count(self, course_id: str) -> int:
        """Return the number of lessons in a course."""
        lessons = await self._repo.find_by_course(course_id)
        return len(lessons)
