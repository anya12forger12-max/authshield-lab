"""Instructor-facing service that composes other LMS services for common workflows."""

from __future__ import annotations

import logging
from typing import Any, Optional

from .classroom_service import ClassroomService
from .enrollment_service import EnrollmentService
from .gradebook_service import GradebookService
from .assessment_service import AssessmentLmsService
from .competency_service import CompetencyService

logger = logging.getLogger(__name__)


class InstructorService:
    """High-level service exposing common instructor workflows."""

    def __init__(
        self,
        classroom_service: ClassroomService,
        enrollment_service: EnrollmentService,
        gradebook_service: GradebookService,
        assessment_service: AssessmentLmsService,
        competency_service: CompetencyService,
    ) -> None:
        self._classrooms = classroom_service
        self._enrollments = enrollment_service
        self._gradebook = gradebook_service
        self._assessments = assessment_service
        self._competencies = competency_service

    def create_course_classroom(
        self,
        instructor_id: str,
        name: str,
        description: str = "",
        capacity: int = 30,
    ) -> dict[str, Any]:
        """Create a classroom and auto-enroll the instructor."""
        classroom = self._classrooms.create_classroom({
            "name": name,
            "description": description,
            "capacity": capacity,
            "instructor_id": instructor_id,
            "status": "active",
        })
        self._classrooms.add_member(classroom["id"], instructor_id, role="instructor")
        logger.info(
            "instructor_course_classroom_created",
            extra={"classroom_id": classroom["id"], "instructor_id": instructor_id},
        )
        return classroom

    def enroll_learner(
        self,
        classroom_id: str,
        learner_id: str,
        auto_activate: bool = True,
    ) -> dict[str, Any]:
        """Enroll a learner in a classroom and create an enrollment record."""
        member = self._classrooms.add_member(classroom_id, learner_id, role="learner")
        enrollment_data: dict[str, Any] = {
            "learner_id": learner_id,
            "course_id": classroom_id,
            "status": "active" if auto_activate else "pending",
        }
        enrollment = self._enrollments.create_enrollment(enrollment_data)
        logger.info(
            "instructor_learner_enrolled",
            extra={"classroom_id": classroom_id, "learner_id": learner_id},
        )
        return {"member": member, "enrollment": enrollment}

    def record_grade(
        self,
        gradebook_id: str,
        grade_item_id: str,
        learner_id: str,
        score: float,
        feedback: Optional[str] = None,
    ) -> dict[str, Any]:
        """Record a grade for a learner on a specific grade item."""
        entry = self._gradebook.add_grade_entry(grade_item_id, {
            "learner_id": learner_id,
            "score": score,
            "feedback": feedback,
        })
        logger.info(
            "instructor_grade_recorded",
            extra={"grade_item_id": grade_item_id, "learner_id": learner_id, "score": score},
        )
        return entry

    def create_assessment_for_course(
        self,
        course_id: str,
        title: str,
        assessment_type: str = "quiz",
        passing_score: float = 70.0,
        attempts_allowed: int = 1,
        time_limit_minutes: Optional[int] = None,
    ) -> dict[str, Any]:
        """Create and publish an assessment for a course."""
        assessment = self._assessments.create_assessment({
            "title": title,
            "assessment_type": assessment_type,
            "course_id": course_id,
            "passing_score": passing_score,
            "attempts_allowed": attempts_allowed,
            "time_limit_minutes": time_limit_minutes,
            "status": "draft",
        })
        published = self._assessments.publish_assessment(assessment["id"])
        logger.info(
            "instructor_assessment_created",
            extra={"assessment_id": assessment["id"], "course_id": course_id},
        )
        return published

    def assess_competency(
        self,
        learner_id: str,
        competency_id: str,
        achieved: bool = False,
        assessor_id: Optional[str] = None,
        evidence: Optional[str] = None,
    ) -> dict[str, Any]:
        """Assess a learner's competency progress."""
        if achieved:
            result = self._competencies.achieve_competency(
                learner_id, competency_id, assessor_id=assessor_id, evidence=evidence
            )
        else:
            result = self._competencies.start_competency(learner_id, competency_id)
        logger.info(
            "instructor_competency_assessed",
            extra={"learner_id": learner_id, "competency_id": competency_id, "achieved": achieved},
        )
        return result

    def get_classroom_roster(self, classroom_id: str) -> dict[str, Any]:
        """Get the full roster for a classroom with enrollment status."""
        members = self._classrooms.get_members(classroom_id)
        roster: list[dict[str, Any]] = []
        for member in members:
            learner_id = member.get("user_id", "")
            enrollments = self._enrollments.get_learner_enrollments(learner_id)
            course_enrollment = None
            for e in enrollments:
                if e.get("course_id") == classroom_id:
                    course_enrollment = e
                    break
            roster.append({
                "member": member,
                "enrollment": course_enrollment,
            })
        return {"classroom_id": classroom_id, "roster": roster}

    def get_course_analytics(self, course_id: str) -> dict[str, Any]:
        """Get aggregated analytics for a course."""
        enrollment_count = self._enrollments.get_enrollment_count(course_id)
        enrollments = self._enrollments.get_course_enrollments(course_id)
        status_counts: dict[str, int] = {}
        for e in enrollments:
            s = e.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1

        return {
            "course_id": course_id,
            "total_enrollments": enrollment_count,
            "status_counts": status_counts,
        }
