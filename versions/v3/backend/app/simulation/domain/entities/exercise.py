"""Exercise domain entity for simulation activities."""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ExerciseStatus(str, Enum):
    """Lifecycle status of an exercise."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


_VALID_EXERCISE_TRANSITIONS: dict[ExerciseStatus, set[ExerciseStatus]] = {
    ExerciseStatus.DRAFT: {ExerciseStatus.PUBLISHED},
    ExerciseStatus.PUBLISHED: {ExerciseStatus.ARCHIVED, ExerciseStatus.DRAFT},
    ExerciseStatus.ARCHIVED: {ExerciseStatus.DRAFT},
}


@dataclass
class Exercise:
    """A hands-on exercise tied to one or more simulation scenarios.

    Exercises represent the learner-facing activities that combine
    scenario context with specific tasks, goals, and assessment criteria.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    scenario_id: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)
    difficulty: int = 1
    learning_outcomes: list[str] = field(default_factory=list)
    estimated_completion_minutes: int = 30
    favorite: bool = False
    version: int = 1
    status: ExerciseStatus = ExerciseStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def toggle_favorite(self) -> bool:
        """Toggle the favorite flag and return the new value."""
        self.favorite = not self.favorite
        self.updated_at = datetime.now(timezone.utc)
        return self.favorite

    def update_difficulty(self, new_difficulty: int) -> None:
        """Update difficulty level (clamped to 1–10)."""
        self.difficulty = max(1, min(10, new_difficulty))
        self.updated_at = datetime.now(timezone.utc)

    def clone(self) -> Exercise:
        """Create a deep copy with a new ID, draft status, and version 1."""
        cloned = copy.deepcopy(self)
        cloned.id = str(uuid.uuid4())
        cloned.status = ExerciseStatus.DRAFT
        cloned.version = 1
        cloned.favorite = False
        cloned.created_at = datetime.now(timezone.utc)
        cloned.updated_at = datetime.now(timezone.utc)
        return cloned

    def validate(self) -> list[str]:
        """Validate the exercise and return a list of error messages.

        Returns an empty list if the exercise is valid.
        """
        errors: list[str] = []

        if not self.title or not self.title.strip():
            errors.append("Title is required")
        elif len(self.title) > 256:
            errors.append("Title must be at most 256 characters")

        if not self.description or not self.description.strip():
            errors.append("Description is required")
        elif len(self.description) > 4096:
            errors.append("Description must be at most 4096 characters")

        if not self.scenario_id:
            errors.append("Scenario ID is required")

        if self.difficulty < 1 or self.difficulty > 10:
            errors.append("Difficulty must be between 1 and 10")

        if self.estimated_completion_minutes < 1:
            errors.append("Estimated completion time must be at least 1 minute")

        if not self.learning_outcomes:
            errors.append("At least one learning outcome is required")

        return errors

    def publish(self) -> None:
        """Transition exercise to published status."""
        allowed = _VALID_EXERCISE_TRANSITIONS.get(self.status, set())
        if ExerciseStatus.PUBLISHED not in allowed:
            raise ValueError(
                f"Cannot publish exercise from '{self.status.value}' status. "
                f"Allowed transitions: {[s.value for s in allowed]}"
            )
        self.status = ExerciseStatus.PUBLISHED
        self.updated_at = datetime.now(timezone.utc)

    def archive(self) -> None:
        """Transition exercise to archived status."""
        allowed = _VALID_EXERCISE_TRANSITIONS.get(self.status, set())
        if ExerciseStatus.ARCHIVED not in allowed:
            raise ValueError(
                f"Cannot archive exercise from '{self.status.value}' status. "
                f"Allowed transitions: {[s.value for s in allowed]}"
            )
        self.status = ExerciseStatus.ARCHIVED
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        stat = self.status.value if hasattr(self.status, "value") else self.status
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "scenario_id": self.scenario_id,
            "category": self.category,
            "tags": list(self.tags),
            "difficulty": self.difficulty,
            "learning_outcomes": list(self.learning_outcomes),
            "estimated_completion_minutes": self.estimated_completion_minutes,
            "favorite": self.favorite,
            "version": self.version,
            "status": stat,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
