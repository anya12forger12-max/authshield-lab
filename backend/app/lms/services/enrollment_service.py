"""Enrollment management service for the LMS module."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.enrollment import CourseEnrollmentConfig, EnrollmentStatus
from ..domain.events.lms_events import EnrollmentCompleted, EnrollmentCreated
from ..domain.interfaces.lms_interfaces import IEnrollmentRepository
from ..validators.lms_validator import validate_enrollment_data

logger = logging.getLogger(__name__)


class EnrollmentService:
    """Service for managing course enrollments and waitlists."""

    def __init__(self, enrollment_repo: IEnrollmentRepository) -> None:
        self._repo = enrollment_repo

    def create_enrollment(self, data: dict[str, Any]) -> dict[str, Any]:
        validation = validate_enrollment_data(data)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.to_dict()}")

        learner_id = data.get("learner_id", "")
        course_id = data.get("course_id", "")

        existing = self._repo.get_by_learner(learner_id)
        for e in existing:
            if e["course_id"] == course_id and e["status"] not in ("dropped", "waitlisted"):
                raise ValueError(f"Learner '{learner_id}' is already enrolled in course '{course_id}'.")

        enrollment = self._repo.create(data)
        event = EnrollmentCreated(
            enrollment_id=enrollment["id"],
            learner_id=learner_id,
            course_id=course_id,
        )
        logger.info(
            "enrollment_created",
            extra={"enrollment_id": enrollment["id"], "event_id": event.event_id},
        )
        return enrollment

    def get_enrollment(self, enrollment_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_by_id(enrollment_id)

    def list_enrollments(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        course_id: Optional[str] = None,
        learner_id: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._repo.get_all(
            page=page,
            per_page=per_page,
            status=status,
            course_id=course_id,
            learner_id=learner_id,
        )

    def update_enrollment(
        self, enrollment_id: str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        existing = self._repo.get_by_id(enrollment_id)
        if not existing:
            raise ValueError(f"Enrollment '{enrollment_id}' not found.")
        return self._repo.update(enrollment_id, data)

    def delete_enrollment(self, enrollment_id: str) -> bool:
        if not self._repo.get_by_id(enrollment_id):
            raise ValueError(f"Enrollment '{enrollment_id}' not found.")
        return self._repo.delete(enrollment_id)

    def activate_enrollment(self, enrollment_id: str) -> dict[str, Any]:
        enrollment = self._repo.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment '{enrollment_id}' not found.")
        if enrollment["status"] != "pending":
            raise ValueError(f"Cannot activate enrollment in '{enrollment['status']}' status.")
        return self._repo.update(enrollment_id, {"status": "active"}) or enrollment

    def complete_enrollment(
        self, enrollment_id: str, grade: Optional[str] = None
    ) -> dict[str, Any]:
        enrollment = self._repo.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment '{enrollment_id}' not found.")
        if enrollment["status"] != "active":
            raise ValueError(f"Cannot complete enrollment in '{enrollment['status']}' status.")

        now = datetime.now(timezone.utc).isoformat()
        updated = self._repo.update(enrollment_id, {
            "status": "completed",
            "completed_at": now,
            "grade": grade,
        })
        if updated:
            event = EnrollmentCompleted(
                enrollment_id=enrollment_id,
                learner_id=enrollment.get("learner_id", ""),
                course_id=enrollment.get("course_id", ""),
                grade=grade or "",
            )
            logger.info("enrollment_completed", extra={"enrollment_id": enrollment_id, "event_id": event.event_id})
        return updated or enrollment

    def drop_enrollment(self, enrollment_id: str) -> dict[str, Any]:
        enrollment = self._repo.get_by_id(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment '{enrollment_id}' not found.")
        if enrollment["status"] in ("completed", "dropped"):
            raise ValueError(f"Cannot drop enrollment in '{enrollment['status']}' status.")
        return self._repo.update(enrollment_id, {"status": "dropped"}) or enrollment

    def get_learner_enrollments(self, learner_id: str) -> list[dict[str, Any]]:
        return self._repo.get_by_learner(learner_id)

    def get_course_enrollments(self, course_id: str) -> list[dict[str, Any]]:
        return self._repo.get_by_course(course_id)

    def get_enrollment_count(self, course_id: str) -> int:
        return self._repo.count_by_course(course_id)

    def can_enroll(
        self,
        course_id: str,
        config: Optional[CourseEnrollmentConfig] = None,
        completed_prerequisites: Optional[list[str]] = None,
    ) -> bool:
        if config is None:
            config = CourseEnrollmentConfig()
        current_count = self._repo.count_by_course(course_id)
        return config.can_enroll(current_count, completed_prerequisites)

    def get_active_enrollments_count(self, course_id: str) -> int:
        enrollments = self._repo.get_by_course(course_id)
        return len([e for e in enrollments if e["status"] == "active"])
