"""Learner console service for assignment, progress, and submission."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.console import LearnerSession, Submission, SessionStatus
from ..domain.interfaces import LearnerSessionRepositoryInterface
from ...shared.events.event_bus import EventBus, DomainEvent, EventType, get_event_bus


class LearnerConsoleService:
    """Service layer for learner exercise sessions.

    Manages the full lifecycle of learner sessions: assignment, progress
    tracking, evidence collection, submission, reflection, and completion.
    """

    def __init__(
        self,
        repository: LearnerSessionRepositoryInterface,
        event_bus: EventBus | None = None,
    ) -> None:
        self._repo = repository
        self._event_bus = event_bus or get_event_bus()

    async def assign_exercise(
        self,
        learner_id: str,
        exercise_id: str,
        accessibility_settings: dict[str, Any] | None = None,
    ) -> LearnerSession:
        """Assign an exercise to a learner by creating a new session."""
        session = LearnerSession(
            id=str(uuid.uuid4()),
            learner_id=learner_id,
            exercise_id=exercise_id,
            accessibility_settings=accessibility_settings or {},
        )
        return await self._repo.create(session)

    async def start_session(self, session_id: str) -> LearnerSession:
        """Start a learner session."""
        session = await self._repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.start()
        updated = await self._repo.update(
            session_id,
            {"status": session.status, "started_at": session.started_at},
        )
        if updated is None:
            raise ValueError("Failed to start session")

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Learner session started: {session_id}",
            metadata={
                "session_id": session_id,
                "learner_id": session.learner_id,
                "exercise_id": session.exercise_id,
            },
        )
        await self._event_bus.publish(event)
        return updated

    async def get_session(self, session_id: str) -> Optional[LearnerSession]:
        """Retrieve a learner session by ID."""
        return await self._repo.get_by_id(session_id)

    async def list_sessions(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """List all learner sessions with pagination."""
        return await self._repo.get_all(page=page, per_page=per_page)

    async def update_progress(
        self, session_id: str, progress: float
    ) -> LearnerSession:
        """Update the progress of a learner session."""
        session = await self._repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.progress = max(0.0, min(1.0, progress))
        updated = await self._repo.update(
            session_id,
            {"progress": session.progress},
        )
        if updated is None:
            raise ValueError("Failed to update progress")
        return updated

    async def add_evidence(
        self, session_id: str, evidence_item: str
    ) -> LearnerSession:
        """Add an evidence item to a learner session."""
        session = await self._repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.add_evidence(evidence_item)
        updated = await self._repo.update(
            session_id,
            {"evidence": session.evidence, "progress": session.progress},
        )
        if updated is None:
            raise ValueError("Failed to add evidence")
        return updated

    async def add_reflection(
        self, session_id: str, reflection: str
    ) -> LearnerSession:
        """Add a reflection journal entry."""
        session = await self._repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.add_reflection(reflection)
        updated = await self._repo.update(
            session_id,
            {"reflection_journal": session.reflection_journal},
        )
        if updated is None:
            raise ValueError("Failed to add reflection")
        return updated

    async def update_notes(
        self, session_id: str, notes: str
    ) -> LearnerSession:
        """Update learner notes."""
        session = await self._repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.notes = notes
        updated = await self._repo.update(
            session_id,
            {"notes": notes},
        )
        if updated is None:
            raise ValueError("Failed to update notes")
        return updated

    async def submit(
        self, session_id: str, content: str
    ) -> Submission:
        """Submit work for a learner session."""
        session = await self._repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        submission = session.submit(content)
        updated = await self._repo.update(
            session_id,
            {"submissions": [s.to_dict() for s in session.submissions]},
        )
        if updated is None:
            raise ValueError("Failed to record submission")

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Submission received for session {session_id}",
            metadata={
                "session_id": session_id,
                "submission_id": submission.id,
                "exercise_id": session.exercise_id,
                "learner_id": session.learner_id,
            },
        )
        await self._event_bus.publish(event)
        return submission

    async def complete_session(self, session_id: str) -> LearnerSession:
        """Mark a learner session as completed."""
        session = await self._repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.complete()
        updated = await self._repo.update(
            session_id,
            {"status": session.status, "progress": session.progress},
        )
        if updated is None:
            raise ValueError("Failed to complete session")

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Learner session completed: {session_id}",
            metadata={
                "session_id": session_id,
                "learner_id": session.learner_id,
                "exercise_id": session.exercise_id,
            },
        )
        await self._event_bus.publish(event)
        return updated

    async def get_by_learner(self, learner_id: str) -> list[LearnerSession]:
        """Return all sessions for a learner."""
        return await self._repo.get_by_learner(learner_id)

    async def get_by_exercise(self, exercise_id: str) -> list[LearnerSession]:
        """Return all sessions for an exercise."""
        return await self._repo.get_by_exercise(exercise_id)

    async def update_accessibility_settings(
        self, session_id: str, settings: dict[str, Any]
    ) -> LearnerSession:
        """Update accessibility settings for a session."""
        session = await self._repo.get_by_id(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")
        session.accessibility_settings.update(settings)
        updated = await self._repo.update(
            session_id,
            {"accessibility_settings": session.accessibility_settings},
        )
        if updated is None:
            raise ValueError("Failed to update accessibility settings")
        return updated
