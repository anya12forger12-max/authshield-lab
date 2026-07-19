"""Course management service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.content import Course
from ..domain.events.content_events import (
    CourseCreated,
    CoursePublished,
    CourseArchived,
    AccessibilityReviewCompleted,
)
from ..domain.interfaces.content_repository import CourseRepository
from ..validators.content_validator import ContentValidator


class CourseService:
    """Service for creating, querying, updating, and publishing courses.

    Parameters
    ----------
    repo:
        Repository for course persistence.
    validator:
        Content validation rules.
    """

    def __init__(self, repo: CourseRepository, validator: ContentValidator | None = None) -> None:
        self._repo = repo
        self._validator = validator or ContentValidator()
        self._events: list[Any] = []

    def _record_event(self, event: Any) -> None:
        self._events.append(event)

    async def create_course(
        self,
        title: str,
        description: str,
        difficulty: str = "beginner",
        learning_objectives: list[str] | None = None,
        prerequisites: list[str] | None = None,
        estimated_hours: float = 0.0,
        target_audience: str = "",
        required_competencies: list[str] | None = None,
        tags: list[str] | None = None,
        created_by: str = "",
    ) -> Course:
        """Create a new course, validate, persist, and emit a creation event."""
        course = Course(
            title=title,
            description=description,
            difficulty=difficulty,
            learning_objectives=learning_objectives or [],
            prerequisites=prerequisites or [],
            estimated_hours=estimated_hours,
            target_audience=target_audience,
            required_competencies=required_competencies or [],
            tags=tags or [],
            created_by=created_by,
        )
        validation_errors = self._validator.validate_course_structure(
            {
                "title": course.title,
                "description": course.description,
                "difficulty": course.difficulty,
                "learning_objectives": course.learning_objectives,
                "tags": course.tags,
                "estimated_hours": course.estimated_hours,
            }
        )
        if not validation_errors.is_valid:
            error_messages = [e.message for e in validation_errors.errors]
            raise ValueError(f"Course validation failed: {'; '.join(error_messages)}")
        await self._repo.save(course)
        event = CourseCreated(
            course_id=course.id,
            title=course.title,
            created_by=course.created_by,
            correlation_id=course.id,
            message=f"Course '{course.title}' created.",
        )
        self._record_event(event)
        return course

    async def get_course(self, course_id: str) -> Optional[Course]:
        """Retrieve a course by ID."""
        return await self._repo.find_by_id(course_id)

    async def list_courses(
        self,
        offset: int = 0,
        limit: int = 20,
        filters: dict | None = None,
    ) -> dict[str, Any]:
        """List courses with pagination and optional filters."""
        if filters:
            courses = await self._repo.search("", filters=filters)
            total = len(courses)
            paginated = courses[offset : offset + limit]
        else:
            courses = await self._repo.find_all(offset=offset, limit=limit)
            total = await self._repo.count()
            paginated = courses
        import math
        pages = math.ceil(total / limit) if limit > 0 else 0
        return {
            "items": [c.__dict__ for c in paginated],
            "total": total,
            "offset": offset,
            "limit": limit,
            "pages": pages,
        }

    async def update_course(self, course_id: str, updates: dict[str, Any]) -> Course:
        """Apply partial updates to a course."""
        course = await self._repo.find_by_id(course_id)
        if course is None:
            raise ValueError(f"Course {course_id} not found.")
        allowed_fields = {
            "title",
            "description",
            "difficulty",
            "learning_objectives",
            "prerequisites",
            "estimated_hours",
            "target_audience",
            "required_competencies",
            "tags",
        }
        for key, value in updates.items():
            if key in allowed_fields:
                setattr(course, key, value)
        course.updated_at = datetime.now(timezone.utc)
        validation_errors = course.validate()
        if validation_errors:
            raise ValueError(f"Course validation failed: {'; '.join(validation_errors)}")
        await self._repo.save(course)
        return course

    async def publish_course(self, course_id: str) -> Course:
        """Validate and publish a course."""
        course = await self._repo.find_by_id(course_id)
        if course is None:
            raise ValueError(f"Course {course_id} not found.")
        validation_errors = course.validate()
        if validation_errors:
            raise ValueError(
                f"Cannot publish course with validation errors: {'; '.join(validation_errors)}"
            )
        if not course.learning_objectives:
            raise ValueError("Cannot publish course without learning objectives.")
        course.publish()
        await self._repo.save(course)
        event = CoursePublished(
            course_id=course.id,
            title=course.title,
            version=course.version,
            correlation_id=course.id,
            message=f"Course '{course.title}' published (v{course.version}).",
        )
        self._record_event(event)
        return course

    async def archive_course(self, course_id: str) -> Course:
        """Archive a course."""
        course = await self._repo.find_by_id(course_id)
        if course is None:
            raise ValueError(f"Course {course_id} not found.")
        course.archive()
        await self._repo.save(course)
        event = CourseArchived(
            course_id=course.id,
            title=course.title,
            correlation_id=course.id,
            message=f"Course '{course.title}' archived.",
        )
        self._record_event(event)
        return course

    async def clone_course(self, course_id: str, new_title: str | None = None) -> Course:
        """Clone a course with a fresh ID and draft status."""
        source = await self._repo.find_by_id(course_id)
        if source is None:
            raise ValueError(f"Source course {course_id} not found.")
        cloned = source.clone(new_title=new_title)
        await self._repo.save(cloned)
        return cloned

    async def search_courses(
        self,
        query: str,
        filters: dict | None = None,
    ) -> list[Course]:
        """Search courses by keyword and optional filters."""
        return await self._repo.search(query, filters=filters)

    async def validate_course(self, course_id: str) -> dict[str, Any]:
        """Run full validation on a course and return results."""
        course = await self._repo.find_by_id(course_id)
        if course is None:
            raise ValueError(f"Course {course_id} not found.")
        structure_result = self._validator.validate_course_structure(
            {
                "title": course.title,
                "description": course.description,
                "difficulty": course.difficulty,
                "learning_objectives": course.learning_objectives,
                "tags": course.tags,
                "estimated_hours": course.estimated_hours,
            }
        )
        errors = [e.message for e in structure_result.errors]
        warnings = [w.message for w in structure_result.warnings]
        return {
            "course_id": course.id,
            "is_valid": structure_result.is_valid,
            "errors": errors,
            "warnings": warnings,
        }

    async def get_course_stats(self, course_id: str) -> dict[str, Any]:
        """Return statistics for a specific course."""
        course = await self._repo.find_by_id(course_id)
        if course is None:
            raise ValueError(f"Course {course_id} not found.")
        return {
            "course_id": course.id,
            "title": course.title,
            "status": course.status,
            "version": course.version,
            "difficulty": course.difficulty,
            "learning_objectives_count": len(course.learning_objectives),
            "prerequisites_count": len(course.prerequisites),
            "required_competencies_count": len(course.required_competencies),
            "tags_count": len(course.tags),
            "estimated_hours": course.estimated_hours,
        }
