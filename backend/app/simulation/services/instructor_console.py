"""Instructor console service for session management and feedback."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.console import InstructorSession, SessionStatus
from ..domain.entities.results import ExerciseResult, ImprovementRecommendation
from ..domain.interfaces import (
    InstructorSessionRepositoryInterface,
    ResultsRepositoryInterface,
)
from ...shared.events.event_bus import EventBus, DomainEvent, EventType, get_event_bus


class InstructorConsoleService:
    """Service layer for instructor-led exercise sessions.

    Manages the full lifecycle of instructor sessions: launch, monitor,
    pause, resume, complete, review, and feedback.
    """

    def __init__(
        self,
        session_repository: InstructorSessionRepositoryInterface,
        results_repository: ResultsRepositoryInterface,
        event_bus: EventBus | None = None,
    ) -> None:
        self._session_repo = session_repository
        self._results_repo = results_repository
        self._event_bus = event_bus or get_event_bus()

    async def launch_session(
        self,
        instructor_id: str,
        exercise_id: str,
    ) -> InstructorSession:
        """Launch a new instructor session for an exercise."""
        session = InstructorSession(
            id=str(uuid.uuid4()),
            instructor_id=instructor_id,
            exercise_id=exercise_id,
        )
        session.launch()
        created = await self._session_repo.create(session)

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Instructor session launched for exercise {exercise_id}",
            metadata={
                "session_id": created.id,
                "instructor_id": instructor_id,
                "exercise_id": exercise_id,
            },
        )
        await self._event_bus.publish(event)
        return created

    async def get_session(self, session_id: str) -> Optional[InstructorSession]:
        """Retrieve an instructor session by ID."""
        return await self._session_repo.get_by_id(session_id)

    async def list_sessions(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """List all instructor sessions with pagination."""
        return await self._session_repo.get_all(page=page, per_page=per_page)

    async def pause_session(self, session_id: str) -> InstructorSession:
        """Pause an active session."""
        session = await self._session_repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.pause()
        updated = await self._session_repo.update(
            session_id,
            {"status": session.status, "paused_at": session.paused_at},
        )
        if updated is None:
            raise ValueError("Failed to pause session")
        return updated

    async def resume_session(self, session_id: str) -> InstructorSession:
        """Resume a paused session."""
        session = await self._session_repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.resume()
        updated = await self._session_repo.update(
            session_id,
            {"status": session.status, "paused_at": None},
        )
        if updated is None:
            raise ValueError("Failed to resume session")
        return updated

    async def complete_session(self, session_id: str) -> InstructorSession:
        """Complete a session."""
        session = await self._session_repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.complete()
        updated = await self._session_repo.update(
            session_id,
            {"status": session.status, "ended_at": session.ended_at},
        )
        if updated is None:
            raise ValueError("Failed to complete session")
        return updated

    async def add_notes(self, session_id: str, notes: str) -> InstructorSession:
        """Add or update instructor notes on a session."""
        session = await self._session_repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        updated = await self._session_repo.update(
            session_id,
            {"notes": notes, "updated_at": datetime.now(timezone.utc)},
        )
        if updated is None:
            raise ValueError("Failed to update notes")
        return updated

    async def get_active_sessions(
        self, instructor_id: str
    ) -> list[InstructorSession]:
        """Return all active sessions for an instructor."""
        sessions = await self._session_repo.get_by_instructor(instructor_id)
        return [s for s in sessions if s.status == SessionStatus.ACTIVE]

    async def monitor_session(
        self, session_id: str
    ) -> dict[str, Any]:
        """Get monitoring data for an active session."""
        session = await self._session_repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        elapsed = session.get_elapsed_seconds()
        return {
            "session_id": session.id,
            "status": session.status,
            "elapsed_seconds": elapsed,
            "is_paused": session.status == SessionStatus.PAUSED,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "notes": session.notes,
        }

    async def review_and_grade(
        self,
        session_id: str,
        result_id: str,
        scores: dict[str, float],
        feedback: str,
        competency_updates: dict[str, float] | None = None,
        recommendations: list[dict[str, str]] | None = None,
    ) -> ExerciseResult:
        """Review a learner's work and provide graded feedback."""
        result = await self._results_repo.get_by_id(result_id)
        if result is None:
            raise ValueError(f"Result {result_id} not found")

        for criterion, score in scores.items():
            result.add_assessment_score(criterion, score)

        result.instructor_feedback = feedback

        if competency_updates:
            for competency, progress in competency_updates.items():
                result.update_competency(competency, progress)

        if recommendations:
            for rec in recommendations:
                result.add_improvement(
                    ImprovementRecommendation(
                        category=rec.get("category", ""),
                        priority=rec.get("priority", "medium"),
                        recommendation=rec.get("recommendation", ""),
                        rationale=rec.get("rationale", ""),
                    )
                )

        result.mark_complete()
        updated = await self._results_repo.update(
            result_id,
            {
                "assessment_scores": result.assessment_scores,
                "instructor_feedback": result.instructor_feedback,
                "competency_progress": result.competency_progress,
                "completion_status": result.completion_status,
                "completed_at": result.completed_at,
            },
        )
        if updated is None:
            raise ValueError("Failed to update results")

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Instructor reviewed result {result_id}",
            metadata={
                "session_id": session_id,
                "result_id": result_id,
                "overall_score": result.calculate_overall_score(),
            },
        )
        await self._event_bus.publish(event)
        return updated
