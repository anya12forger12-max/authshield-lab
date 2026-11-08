"""Analytics service for the LMS module - provides cross-cutting data insights."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from .classroom_service import ClassroomService
from .enrollment_service import EnrollmentService
from .gradebook_service import GradebookService
from .competency_service import CompetencyService
from .assessment_service import AssessmentLmsService

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Provides analytics and reporting across the LMS module."""

    def __init__(
        self,
        classroom_service: ClassroomService,
        enrollment_service: EnrollmentService,
        gradebook_service: GradebookService,
        competency_service: CompetencyService,
        assessment_service: AssessmentLmsService,
    ) -> None:
        self._classrooms = classroom_service
        self._enrollments = enrollment_service
        self._gradebook = gradebook_service
        self._competencies = competency_service
        self._assessments = assessment_service

    def get_learner_overview(self, learner_id: str) -> dict[str, Any]:
        """Get a comprehensive overview for a single learner."""
        enrollments = self._enrollments.get_learner_enrollments(learner_id)
        competency_progress = self._competencies.get_learner_progress(learner_id)
        competency_summary = self._competencies.get_learner_summary(learner_id)

        gradebook_averages: dict[str, float] = {}
        for enrollment in enrollments:
            course_id = enrollment.get("course_id", "")
            gradebook = self._gradebook.get_gradebook_by_course(course_id)
            if gradebook:
                avg = self._gradebook.calculate_learner_average(gradebook["id"], learner_id)
                gradebook_averages[course_id] = avg

        return {
            "learner_id": learner_id,
            "total_enrollments": len(enrollments),
            "enrollment_statuses": _count_by_field(enrollments, "status"),
            "competency_summary": competency_summary,
            "gradebook_averages": gradebook_averages,
            "overall_average": _safe_average(list(gradebook_averages.values())),
        }

    def get_course_analytics(self, course_id: str) -> dict[str, Any]:
        """Get analytics for a specific course."""
        enrollments = self._enrollments.get_course_enrollments(course_id)
        enrollment_count = len(enrollments)
        status_counts = _count_by_field(enrollments, "status")

        gradebook = self._gradebook.get_gradebook_by_course(course_id)
        grade_stats: dict[str, Any] = {}
        if gradebook:
            grade_stats = self._gradebook.get_course_statistics(gradebook["id"])

        assessment_count = len(self._assessments.list_assessments_by_course(course_id))

        return {
            "course_id": course_id,
            "total_enrollments": enrollment_count,
            "enrollment_status_counts": status_counts,
            "grade_statistics": grade_stats,
            "total_assessments": assessment_count,
            "active_enrollments": status_counts.get("active", 0),
            "completion_rate": _safe_percentage(
                status_counts.get("completed", 0), enrollment_count
            ),
        }

    def get_platform_overview(self) -> dict[str, Any]:
        """Get high-level platform analytics."""
        classrooms = self._classrooms.list_classrooms(per_page=10000)
        total_classrooms = classrooms.get("total", 0)
        active_classrooms = len([
            c for c in classrooms.get("items", [])
            if c.get("status") == "active"
        ])

        all_enrollments_result = self._enrollments.list_enrollments(per_page=10000)
        all_enrollments = all_enrollments_result.get("items", [])
        total_enrollments = len(all_enrollments)
        enrollment_status_counts = _count_by_field(all_enrollments, "status")

        total_learners = len({e.get("learner_id") for e in all_enrollments})
        total_courses = len({e.get("course_id") for e in all_enrollments})

        all_competencies = self._competencies.list_competencies()

        return {
            "total_classrooms": total_classrooms,
            "active_classrooms": active_classrooms,
            "total_enrollments": total_enrollments,
            "enrollment_status_counts": enrollment_status_counts,
            "total_learners": total_learners,
            "total_courses": total_courses,
            "total_competencies": len(all_competencies),
            "platform_average_completion_rate": _safe_percentage(
                enrollment_status_counts.get("completed", 0), total_enrollments
            ),
        }

    def get_top_performers(
        self, course_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get top performers in a course by gradebook average."""
        gradebook = self._gradebook.get_gradebook_by_course(course_id)
        if not gradebook:
            return []

        enrollments = self._enrollments.get_course_enrollments(course_id)
        learner_ids = list({e.get("learner_id") for e in enrollments if e.get("learner_id")})

        performers: list[dict[str, Any]] = []
        for lid in learner_ids:
            avg = self._gradebook.calculate_learner_average(gradebook["id"], lid)
            performers.append({
                "learner_id": lid,
                "average_score": avg,
            })

        performers.sort(key=lambda p: p["average_score"], reverse=True)
        return performers[:limit]

    def get_competency_heatmap(self, learner_id: str) -> dict[str, Any]:
        """Get a competency progress heatmap for a learner."""
        all_competencies = self._competencies.list_competencies()
        learner_progress = self._competencies.get_learner_progress(learner_id)
        progress_by_competency: dict[str, dict[str, Any]] = {}
        for p in learner_progress:
            cid = p.get("competency_id", "")
            progress_by_competency[cid] = p

        heatmap: list[dict[str, Any]] = []
        for comp in all_competencies:
            cid = comp.get("id", "")
            progress = progress_by_competency.get(cid)
            heatmap.append({
                "competency_id": cid,
                "competency_name": comp.get("name", ""),
                "domain": comp.get("domain", ""),
                "level": comp.get("level", ""),
                "status": progress.get("status", "not_started") if progress else "not_started",
                "evidence_count": len(progress.get("evidence_json", "[]").split(",")) if progress else 0,
            })

        return {"learner_id": learner_id, "heatmap": heatmap}

    def get_assessment_analytics(self, assessment_id: str) -> dict[str, Any]:
        """Get analytics for a specific assessment."""
        return self._assessments.get_assessment_statistics(assessment_id)

    def get_learner_progress_report(self, learner_id: str) -> dict[str, Any]:
        """Generate a full progress report for a learner."""
        overview = self.get_learner_overview(learner_id)
        competency_summary = self._competencies.get_learner_summary(learner_id)

        return {
            "learner_id": learner_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "enrollment_overview": {
                "total": overview["total_enrollments"],
                "statuses": overview["enrollment_statuses"],
            },
            "academic_performance": {
                "overall_average": overview["overall_average"],
                "course_averages": overview["gradebook_averages"],
            },
            "competency_progress": competency_summary,
        }


def _count_by_field(items: list[dict[str, Any]], field_name: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        val = str(item.get(field_name, "unknown"))
        counts[val] = counts.get(val, 0) + 1
    return counts


def _safe_average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def _safe_percentage(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((part / total) * 100.0, 2)
