"""Exercise service for CRUD, search, and filtering."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.exercise import Exercise, ExerciseStatus
from ..domain.interfaces import ExerciseRepositoryInterface
from ...shared.events.event_bus import EventBus, DomainEvent, EventType, get_event_bus


class ExerciseService:
    """Service layer for exercise management.

    Provides CRUD operations, search, filtering, and lifecycle management
    for simulation exercises.
    """

    def __init__(
        self,
        repository: ExerciseRepositoryInterface,
        event_bus: EventBus | None = None,
    ) -> None:
        self._repo = repository
        self._event_bus = event_bus or get_event_bus()

    async def create_exercise(
        self,
        title: str,
        description: str,
        scenario_id: str,
        category: str = "",
        tags: list[str] | None = None,
        difficulty: int = 1,
        learning_outcomes: list[str] | None = None,
        estimated_completion_minutes: int = 30,
    ) -> Exercise:
        """Create and persist a new exercise."""
        exercise = Exercise(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            scenario_id=scenario_id,
            category=category,
            tags=tags or [],
            difficulty=difficulty,
            learning_outcomes=learning_outcomes or [],
            estimated_completion_minutes=estimated_completion_minutes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        errors = exercise.validate()
        if errors:
            raise ValueError(f"Exercise validation failed: {'; '.join(errors)}")

        return await self._repo.create(exercise)

    async def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """Retrieve an exercise by ID."""
        return await self._repo.get_by_id(exercise_id)

    async def list_exercises(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """List all exercises with pagination."""
        return await self._repo.get_all(page=page, per_page=per_page)

    async def update_exercise(
        self, exercise_id: str, data: dict[str, Any]
    ) -> Optional[Exercise]:
        """Update an existing exercise."""
        data["updated_at"] = datetime.now(timezone.utc)
        return await self._repo.update(exercise_id, data)

    async def delete_exercise(self, exercise_id: str) -> bool:
        """Delete an exercise by ID."""
        return await self._repo.delete(exercise_id)

    async def search_exercises(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Search exercises by title, category, or tags."""
        return await self._repo.search(query, page=page, per_page=per_page)

    async def get_by_scenario(self, scenario_id: str) -> list[Exercise]:
        """Return all exercises linked to a scenario."""
        return await self._repo.get_by_scenario_id(scenario_id)

    async def get_by_status(self, status: str) -> list[Exercise]:
        """Return all exercises with the given status."""
        return await self._repo.get_by_status(status)

    async def toggle_favorite(self, exercise_id: str) -> Exercise:
        """Toggle the favorite flag on an exercise."""
        exercise = await self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ValueError(f"Exercise {exercise_id} not found")
        exercise.toggle_favorite()
        updated = await self._repo.update(
            exercise_id,
            {"favorite": exercise.favorite, "updated_at": exercise.updated_at},
        )
        if updated is None:
            raise ValueError("Failed to update exercise")
        return updated

    async def update_difficulty(self, exercise_id: str, difficulty: int) -> Exercise:
        """Update the difficulty of an exercise."""
        exercise = await self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ValueError(f"Exercise {exercise_id} not found")
        exercise.update_difficulty(difficulty)
        updated = await self._repo.update(
            exercise_id,
            {"difficulty": exercise.difficulty, "updated_at": exercise.updated_at},
        )
        if updated is None:
            raise ValueError("Failed to update exercise difficulty")
        return updated

    async def clone_exercise(self, exercise_id: str) -> Exercise:
        """Clone an exercise with a new ID and draft status."""
        exercise = await self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ValueError(f"Exercise {exercise_id} not found")
        cloned = exercise.clone()
        return await self._repo.create(cloned)

    async def publish_exercise(self, exercise_id: str) -> Exercise:
        """Transition an exercise to published status."""
        exercise = await self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ValueError(f"Exercise {exercise_id} not found")
        exercise.publish()
        updated = await self._repo.update(
            exercise_id,
            {"status": exercise.status, "updated_at": exercise.updated_at},
        )
        if updated is None:
            raise ValueError("Failed to publish exercise")
        return updated

    async def archive_exercise(self, exercise_id: str) -> Exercise:
        """Transition an exercise to archived status."""
        exercise = await self._repo.get_by_id(exercise_id)
        if exercise is None:
            raise ValueError(f"Exercise {exercise_id} not found")
        exercise.archive()
        updated = await self._repo.update(
            exercise_id,
            {"status": exercise.status, "updated_at": exercise.updated_at},
        )
        if updated is None:
            raise ValueError("Failed to archive exercise")
        return updated

    async def filter_by_difficulty(
        self, min_difficulty: int = 1, max_difficulty: int = 10
    ) -> list[Exercise]:
        """Return all exercises within a difficulty range."""
        result = await self._repo.get_all(page=1, per_page=1000)
        items = result.get("items", [])
        return [
            e for e in items
            if min_difficulty <= e.difficulty <= max_difficulty
        ]

    async def filter_by_category(self, category: str) -> list[Exercise]:
        """Return all exercises in a given category."""
        result = await self._repo.get_all(page=1, per_page=1000)
        items = result.get("items", [])
        return [e for e in items if e.category == category]

    async def get_favorites(self) -> list[Exercise]:
        """Return all exercises marked as favorite."""
        result = await self._repo.get_all(page=1, per_page=1000)
        items = result.get("items", [])
        return [e for e in items if e.favorite]
