"""Publishing workflow service for content versioning and lifecycle."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.content import Course, CourseStatus
from ..domain.events.content_events import (
    CoursePublished,
    CourseArchived,
    ContentVersioned,
)
from ..domain.interfaces.content_repository import CourseRepository
from ..validators.content_validator import ContentValidator


class PublishingService:
    """Service for publishing, unpublishing, versioning, and rolling back content.

    Parameters
    ----------
    course_repo:
        Repository for course persistence.
    validator:
        Content validation rules.
    """

    def __init__(
        self,
        course_repo: CourseRepository,
        validator: ContentValidator | None = None,
    ) -> None:
        self._course_repo = course_repo
        self._validator = validator or ContentValidator()
        self._version_history: dict[str, list[dict[str, Any]]] = {}
        self._events: list[Any] = []

    def _record_event(self, event: Any) -> None:
        self._events.append(event)

    def _snapshot(self, course: Course) -> dict[str, Any]:
        """Create an immutable snapshot dict of a course's current state."""
        return {
            "snapshot_id": str(uuid.uuid4()),
            "content_id": course.id,
            "content_type": "course",
            "version": course.version,
            "title": course.title,
            "description": course.description,
            "difficulty": course.difficulty,
            "learning_objectives": list(course.learning_objectives),
            "prerequisites": list(course.prerequisites),
            "estimated_hours": course.estimated_hours,
            "target_audience": course.target_audience,
            "required_competencies": list(course.required_competencies),
            "status": course.status,
            "tags": list(course.tags),
            "created_by": course.created_by,
            "created_at": course.created_at.isoformat(),
            "updated_at": course.updated_at.isoformat(),
            "snapshot_created_at": datetime.now(timezone.utc).isoformat(),
        }

    async def publish(self, content_id: str, content_type: str = "course") -> dict[str, Any]:
        """Publish content of the given type.

        Only courses are currently supported.
        """
        if content_type != "course":
            raise ValueError(f"Publishing for '{content_type}' is not yet supported.")
        course = await self._course_repo.find_by_id(content_id)
        if course is None:
            raise ValueError(f"Course {content_id} not found.")
        validation_errors = course.validate()
        if validation_errors:
            raise ValueError(
                f"Cannot publish: validation errors: {'; '.join(validation_errors)}"
            )
        if not course.learning_objectives:
            raise ValueError("Cannot publish content without learning objectives.")
        previous_status = course.status
        previous_version = course.version
        course.publish()
        await self._course_repo.save(course)
        self._append_version_history(content_id, course)
        event = CoursePublished(
            course_id=course.id,
            title=course.title,
            version=course.version,
            correlation_id=content_id,
            message=f"Course '{course.title}' published (v{course.version}).",
            metadata={"previous_status": previous_status},
        )
        self._record_event(event)
        return {
            "content_id": course.id,
            "content_type": content_type,
            "status": course.status,
            "version": course.version,
            "previous_version": previous_version,
        }

    async def unpublish(self, content_id: str, content_type: str = "course") -> dict[str, Any]:
        """Revert published content back to draft."""
        if content_type != "course":
            raise ValueError(f"Unpublishing for '{content_type}' is not yet supported.")
        course = await self._course_repo.find_by_id(content_id)
        if course is None:
            raise ValueError(f"Course {content_id} not found.")
        if course.status != CourseStatus.PUBLISHED.value:
            raise ValueError(f"Course is not published (current status: {course.status}).")
        course.status = CourseStatus.DRAFT.value
        course.updated_at = datetime.now(timezone.utc)
        await self._course_repo.save(course)
        self._append_version_history(content_id, course)
        event = CourseArchived(
            course_id=course.id,
            title=course.title,
            correlation_id=content_id,
            message=f"Course '{course.title}' unpublished.",
            metadata={"previous_status": CourseStatus.PUBLISHED.value},
        )
        self._record_event(event)
        return {
            "content_id": course.id,
            "content_type": content_type,
            "status": course.status,
            "version": course.version,
        }

    async def create_version(self, content_id: str, content_type: str = "course") -> dict[str, Any]:
        """Bump the version of content without changing its status."""
        if content_type != "course":
            raise ValueError(f"Versioning for '{content_type}' is not yet supported.")
        course = await self._course_repo.find_by_id(content_id)
        if course is None:
            raise ValueError(f"Course {content_id} not found.")
        previous_version = course.version
        course.update_version()
        await self._course_repo.save(course)
        self._append_version_history(content_id, course)
        event = ContentVersioned(
            content_id=course.id,
            content_type=content_type,
            previous_version=previous_version,
            new_version=course.version,
            correlation_id=content_id,
            message=f"Course '{course.title}' versioned: v{previous_version} → v{course.version}.",
        )
        self._record_event(event)
        return {
            "content_id": course.id,
            "content_type": content_type,
            "previous_version": previous_version,
            "new_version": course.version,
        }

    async def get_version_history(self, content_id: str) -> list[dict[str, Any]]:
        """Return the version history snapshots for content."""
        return list(self._version_history.get(content_id, []))

    async def rollback(self, version_id: str, content_type: str = "course") -> dict[str, Any]:
        """Rollback content to a specific snapshot version.

        ``version_id`` is the ``snapshot_id`` from a version history entry.
        """
        if content_type != "course":
            raise ValueError(f"Rollback for '{content_type}' is not yet supported.")
        for _cid, snapshots in self._version_history.items():
            for snap in snapshots:
                if snap["snapshot_id"] == version_id:
                    course = await self._course_repo.find_by_id(snap["content_id"])
                    if course is None:
                        raise ValueError(f"Course {snap['content_id']} not found.")
                    course.title = snap["title"]
                    course.description = snap["description"]
                    course.difficulty = snap["difficulty"]
                    course.learning_objectives = list(snap["learning_objectives"])
                    course.prerequisites = list(snap["prerequisites"])
                    course.estimated_hours = snap["estimated_hours"]
                    course.target_audience = snap["target_audience"]
                    course.required_competencies = list(snap["required_competencies"])
                    course.tags = list(snap["tags"])
                    course.version += 1
                    course.updated_at = datetime.now(timezone.utc)
                    await self._course_repo.save(course)
                    self._append_version_history(course.id, course)
                    return {
                        "content_id": course.id,
                        "content_type": content_type,
                        "restored_from_snapshot": version_id,
                        "new_version": course.version,
                    }
        raise ValueError(f"Version snapshot {version_id} not found.")

    async def validate_before_publish(
        self, content_id: str, content_type: str = "course"
    ) -> dict[str, Any]:
        """Pre-publish validation check."""
        if content_type != "course":
            raise ValueError(f"Validation for '{content_type}' is not yet supported.")
        course = await self._course_repo.find_by_id(content_id)
        if course is None:
            raise ValueError(f"Course {content_id} not found.")
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
            "content_id": course.id,
            "content_type": content_type,
            "can_publish": structure_result.is_valid,
            "errors": errors,
            "warnings": warnings,
        }

    async def get_published_content(self, content_type: str = "course") -> list[dict[str, Any]]:
        """Return all published content of the given type."""
        if content_type != "course":
            return []
        courses = await self._course_repo.find_all(offset=0, limit=10000)
        published = [c for c in courses if c.status == CourseStatus.PUBLISHED.value]
        return [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "difficulty": c.difficulty,
                "version": c.version,
                "status": c.status,
                "tags": c.tags,
                "estimated_hours": c.estimated_hours,
                "updated_at": c.updated_at.isoformat(),
            }
            for c in published
        ]

    def _append_version_history(self, content_id: str, course: Course) -> None:
        """Append a snapshot to the version history for the given content."""
        if content_id not in self._version_history:
            self._version_history[content_id] = []
        self._version_history[content_id].append(self._snapshot(course))
