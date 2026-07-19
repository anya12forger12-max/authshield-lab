"""LMS Dashboard service for providing aggregated views."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from .classroom_service import ClassroomService
from .enrollment_service import EnrollmentService
from .gradebook_service import GradebookService
from .competency_service import CompetencyService
from .assessment_service import AssessmentLmsService
from .calendar_service import CalendarService
from .portfolio_service import PortfolioService

logger = logging.getLogger(__name__)


class LmsDashboardService:
    """Aggregated dashboard view for the LMS module."""

    def __init__(
        self,
        classroom_service: ClassroomService,
        enrollment_service: EnrollmentService,
        gradebook_service: GradebookService,
        competency_service: CompetencyService,
        assessment_service: AssessmentLmsService,
        calendar_service: CalendarService,
        portfolio_service: PortfolioService,
    ) -> None:
        self._classrooms = classroom_service
        self._enrollments = enrollment_service
        self._gradebook = gradebook_service
        self._competencies = competency_service
        self._assessments = assessment_service
        self._calendar = calendar_service
        self._portfolio = portfolio_service

    def get_dashboard_summary(self) -> dict[str, Any]:
        """Return a high-level summary for the LMS dashboard."""
        classrooms = self._classrooms.list_classrooms(per_page=10000)
        total_classrooms = classrooms.get("total", 0)
        active_classrooms = len([
            c for c in classrooms.get("items", [])
            if c.get("status") == "active"
        ])

        all_enrollments_result = self._enrollments.list_enrollments(per_page=10000)
        all_enrollments = all_enrollments_result.get("items", [])
        total_enrollments = len(all_enrollments)
        active_enrollments = len([e for e in all_enrollments if e.get("status") == "active"])
        completed_enrollments = len([e for e in all_enrollments if e.get("status") == "completed"])
        total_learners = len({e.get("learner_id") for e in all_enrollments if e.get("learner_id")})

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "classrooms": {
                "total": total_classrooms,
                "active": active_classrooms,
            },
            "enrollments": {
                "total": total_enrollments,
                "active": active_enrollments,
                "completed": completed_enrollments,
            },
            "total_learners": total_learners,
            "completion_rate": _safe_pct(completed_enrollments, total_enrollments),
        }

    def get_instructor_dashboard(self, instructor_id: str) -> dict[str, Any]:
        """Dashboard view for a specific instructor."""
        classrooms = self._classrooms.list_classrooms(per_page=10000)
        my_classrooms = [
            c for c in classrooms.get("items", [])
            if c.get("instructor_id") == instructor_id
        ]

        classroom_summaries: list[dict[str, Any]] = []
        for classroom in my_classrooms:
            cid = classroom.get("id", "")
            members = self._classrooms.get_members(cid)
            classroom_summaries.append({
                "classroom_id": cid,
                "name": classroom.get("name", ""),
                "status": classroom.get("status", ""),
                "member_count": len(members),
                "capacity": classroom.get("capacity", 0),
            })

        return {
            "instructor_id": instructor_id,
            "total_classrooms": len(my_classrooms),
            "classrooms": classroom_summaries,
        }

    def get_learner_dashboard(self, learner_id: str) -> dict[str, Any]:
        """Dashboard view for a specific learner."""
        enrollments = self._enrollments.get_learner_enrollments(learner_id)
        competency_summary = self._competencies.get_learner_summary(learner_id)
        portfolio = self._portfolio.get_portfolio_by_learner(learner_id)
        portfolio_items = self._portfolio.get_items(portfolio["id"]) if portfolio else []

        grades_summary: list[dict[str, Any]] = []
        for enrollment in enrollments:
            course_id = enrollment.get("course_id", "")
            gradebook = self._gradebook.get_gradebook_by_course(course_id)
            avg = 0.0
            if gradebook:
                avg = self._gradebook.calculate_learner_average(gradebook["id"], learner_id)
            grades_summary.append({
                "course_id": course_id,
                "enrollment_status": enrollment.get("status", ""),
                "average": avg,
                "grade": enrollment.get("grade"),
            })

        return {
            "learner_id": learner_id,
            "enrollment_count": len(enrollments),
            "grades": grades_summary,
            "competency_summary": competency_summary,
            "portfolio_item_count": len(portfolio_items),
        }

    def get_upcoming_deadlines(
        self, calendar_id: Optional[str] = None, days_ahead: int = 30
    ) -> list[dict[str, Any]]:
        """Return upcoming events and deadlines across calendars."""
        calendars = self._calendar.list_calendars()
        upcoming: list[dict[str, Any]] = []

        now = datetime.now(timezone.utc)
        for cal in calendars:
            cal_id = cal.get("id", "")
            if calendar_id and cal_id != calendar_id:
                continue
            events = self._calendar.get_events(cal_id)
            for event in events:
                start_time = event.get("start_time")
                if isinstance(start_time, str):
                    try:
                        start_time = datetime.fromisoformat(start_time)
                    except ValueError:
                        continue
                if start_time and start_time > now:
                    upcoming.append({
                        "calendar_id": cal_id,
                        "event": event,
                        "start_time": start_time.isoformat(),
                    })

        upcoming.sort(key=lambda x: x.get("start_time", ""))
        return upcoming[:50]

    def get_recent_activity(self, limit: int = 20) -> dict[str, Any]:
        """Return recent activity across the LMS module."""
        recent_enrollments = self._enrollments.list_enrollments(per_page=limit)
        items = recent_enrollments.get("items", [])

        activity: list[dict[str, Any]] = []
        for item in items:
            activity.append({
                "type": "enrollment",
                "learner_id": item.get("learner_id", ""),
                "course_id": item.get("course_id", ""),
                "status": item.get("status", ""),
                "timestamp": item.get("enrolled_at", ""),
            })

        activity.sort(key=lambda a: a.get("timestamp", ""), reverse=True)
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "activities": activity[:limit],
            "total": len(activity),
        }


def _safe_pct(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((part / total) * 100.0, 2)
