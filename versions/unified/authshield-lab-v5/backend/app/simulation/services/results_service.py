"""Results service for assessment calculation and recommendations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.results import ExerciseResult, ImprovementRecommendation
from ..domain.interfaces import ResultsRepositoryInterface
from ...shared.events.event_bus import EventBus, DomainEvent, EventType, get_event_bus


class ResultsService:
    """Service layer for exercise results management.

    Handles result calculation, scoring, competency tracking,
    improvement recommendations, and result retrieval.
    """

    def __init__(
        self,
        repository: ResultsRepositoryInterface,
        event_bus: EventBus | None = None,
    ) -> None:
        self._repo = repository
        self._event_bus = event_bus or get_event_bus()

    async def create_result(
        self,
        session_id: str,
        exercise_id: str,
    ) -> ExerciseResult:
        """Create a new empty result record."""
        result = ExerciseResult(
            id=str(uuid.uuid4()),
            session_id=session_id,
            exercise_id=exercise_id,
        )
        return await self._repo.create(result)

    async def get_result(self, result_id: str) -> Optional[ExerciseResult]:
        """Retrieve a result by ID."""
        return await self._repo.get_by_id(result_id)

    async def list_results(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """List all results with pagination."""
        return await self._repo.get_all(page=page, per_page=per_page)

    async def update_result(
        self, result_id: str, data: dict[str, Any]
    ) -> Optional[ExerciseResult]:
        """Update an existing result."""
        return await self._repo.update(result_id, data)

    async def add_score(
        self, result_id: str, criterion: str, score: float
    ) -> ExerciseResult:
        """Add or update a specific assessment score."""
        result = await self._repo.get_by_id(result_id)
        if result is None:
            raise ValueError(f"Result {result_id} not found")
        result.add_assessment_score(criterion, score)
        updated = await self._repo.update(
            result_id,
            {"assessment_scores": result.assessment_scores},
        )
        if updated is None:
            raise ValueError("Failed to update score")
        return updated

    async def update_competency(
        self, result_id: str, competency: str, progress: float
    ) -> ExerciseResult:
        """Update competency progress."""
        result = await self._repo.get_by_id(result_id)
        if result is None:
            raise ValueError(f"Result {result_id} not found")
        result.update_competency(competency, progress)
        updated = await self._repo.update(
            result_id,
            {"competency_progress": result.competency_progress},
        )
        if updated is None:
            raise ValueError("Failed to update competency")
        return updated

    async def add_reflection(
        self, result_id: str, reflection: str
    ) -> ExerciseResult:
        """Add a reflection response to a result."""
        result = await self._repo.get_by_id(result_id)
        if result is None:
            raise ValueError(f"Result {result_id} not found")
        result.reflection_responses.append(reflection)
        updated = await self._repo.update(
            result_id,
            {"reflection_responses": result.reflection_responses},
        )
        if updated is None:
            raise ValueError("Failed to add reflection")
        return updated

    async def set_instructor_feedback(
        self, result_id: str, feedback: str
    ) -> ExerciseResult:
        """Set instructor feedback on a result."""
        result = await self._repo.get_by_id(result_id)
        if result is None:
            raise ValueError(f"Result {result_id} not found")
        result.instructor_feedback = feedback
        updated = await self._repo.update(
            result_id,
            {"instructor_feedback": feedback},
        )
        if updated is None:
            raise ValueError("Failed to set feedback")
        return updated

    async def record_accessibility_usage(
        self, result_id: str, tool: str, details: str
    ) -> ExerciseResult:
        """Record accessibility tool usage."""
        result = await self._repo.get_by_id(result_id)
        if result is None:
            raise ValueError(f"Result {result_id} not found")
        result.accessibility_usage[tool] = details
        updated = await self._repo.update(
            result_id,
            {"accessibility_usage": result.accessibility_usage},
        )
        if updated is None:
            raise ValueError("Failed to record accessibility usage")
        return updated

    async def set_time_on_task(
        self, result_id: str, seconds: int
    ) -> ExerciseResult:
        """Set time on task for a result."""
        result = await self._repo.get_by_id(result_id)
        if result is None:
            raise ValueError(f"Result {result_id} not found")
        result.time_on_task_seconds = max(0, seconds)
        updated = await self._repo.update(
            result_id,
            {"time_on_task_seconds": result.time_on_task_seconds},
        )
        if updated is None:
            raise ValueError("Failed to set time on task")
        return updated

    async def generate_recommendations(
        self, result_id: str
    ) -> list[ImprovementRecommendation]:
        """Auto-generate improvement recommendations based on scores."""
        result = await self._repo.get_by_id(result_id)
        if result is None:
            raise ValueError(f"Result {result_id} not found")

        recommendations: list[ImprovementRecommendation] = []
        overall_score = result.calculate_overall_score()

        if overall_score < 0.5:
            recommendations.append(
                ImprovementRecommendation(
                    category="overall",
                    priority="high",
                    recommendation="Review foundational concepts before retrying",
                    rationale=f"Overall score {overall_score:.1%} is below the mastery threshold",
                )
            )

        for criterion, score in result.assessment_scores.items():
            if score < 0.5:
                recommendations.append(
                    ImprovementRecommendation(
                        category=criterion,
                        priority="high",
                        recommendation=f"Focus improvement efforts on {criterion}",
                        rationale=f"Score of {score:.1%} on {criterion} indicates significant gaps",
                    )
                )
            elif score < 0.7:
                recommendations.append(
                    ImprovementRecommendation(
                        category=criterion,
                        priority="medium",
                        recommendation=f"Additional practice recommended for {criterion}",
                        rationale=f"Score of {score:.1%} on {criterion} is approaching proficiency",
                    )
                )

        for competency, progress in result.competency_progress.items():
            if progress < 0.4:
                recommendations.append(
                    ImprovementRecommendation(
                        category=f"competency:{competency}",
                        priority="high",
                        recommendation=f"Seek additional training in {competency}",
                        rationale=f"Competency progress at {progress:.1%}",
                    )
                )

        result.improvement_recommendations = recommendations
        await self._repo.update(
            result_id,
            {
                "improvement_recommendations": [
                    r.to_dict() for r in recommendations
                ],
            },
        )
        return recommendations

    async def calculate_and_finalize(
        self, result_id: str
    ) -> ExerciseResult:
        """Calculate final scores and mark the result as complete."""
        result = await self._repo.get_by_id(result_id)
        if result is None:
            raise ValueError(f"Result {result_id} not found")

        await self.generate_recommendations(result_id)
        result = await self._repo.get_by_id(result_id)
        if result is None:
            raise ValueError(f"Result {result_id} not found after recommendations")

        result.mark_complete()
        updated = await self._repo.update(
            result_id,
            {
                "completion_status": result.completion_status,
                "completed_at": result.completed_at,
            },
        )
        if updated is None:
            raise ValueError("Failed to finalize result")

        event = DomainEvent(
            event_type=EventType.AUDIT_EVENT,
            module="simulation",
            message=f"Results calculated for result {result_id}",
            metadata={
                "result_id": result_id,
                "session_id": result.session_id,
                "exercise_id": result.exercise_id,
                "overall_score": result.calculate_overall_score(),
            },
        )
        await self._event_bus.publish(event)
        return updated

    async def get_by_session(
        self, session_id: str
    ) -> Optional[ExerciseResult]:
        """Return the result for a given session."""
        return await self._repo.get_by_session(session_id)

    async def get_by_exercise(
        self, exercise_id: str
    ) -> list[ExerciseResult]:
        """Return all results for a given exercise."""
        return await self._repo.get_by_exercise(exercise_id)

    async def get_score_statistics(
        self, exercise_id: str
    ) -> dict[str, Any]:
        """Calculate aggregate score statistics for an exercise."""
        results = await self._repo.get_by_exercise(exercise_id)
        if not results:
            return {
                "exercise_id": exercise_id,
                "count": 0,
                "average_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0,
                "completion_rate": 0.0,
            }

        scores = [r.calculate_overall_score() for r in results]
        completed = [r for r in results if r.completion_status == "completed"]

        return {
            "exercise_id": exercise_id,
            "count": len(results),
            "average_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "completion_rate": len(completed) / len(results),
        }
