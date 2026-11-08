"""Repository interfaces for the simulation domain."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from ..entities.scenario import Scenario
from ..entities.dataset import SyntheticDataset
from ..entities.timeline import Timeline
from ..entities.exercise import Exercise
from ..entities.console import InstructorSession, LearnerSession
from ..entities.results import ExerciseResult


class ScenarioRepositoryInterface(ABC):
    """Abstract repository for Scenario persistence."""

    @abstractmethod
    async def get_by_id(self, scenario_id: str) -> Optional[Scenario]:
        """Return a scenario by its ID, or None if not found."""

    @abstractmethod
    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Return a paginated list of all scenarios."""

    @abstractmethod
    async def create(self, scenario: Scenario) -> Scenario:
        """Persist a new scenario and return it."""

    @abstractmethod
    async def update(self, scenario_id: str, data: dict[str, Any]) -> Optional[Scenario]:
        """Update an existing scenario and return it."""

    @abstractmethod
    async def delete(self, scenario_id: str) -> bool:
        """Delete a scenario by ID. Returns True if found and deleted."""

    @abstractmethod
    async def search(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Search scenarios by title or description."""

    @abstractmethod
    async def get_by_status(self, status: str) -> list[Scenario]:
        """Return all scenarios with the given status."""


class DatasetRepositoryInterface(ABC):
    """Abstract repository for SyntheticDataset persistence."""

    @abstractmethod
    async def get_by_id(self, dataset_id: str) -> Optional[SyntheticDataset]:
        """Return a dataset by its ID, or None if not found."""

    @abstractmethod
    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Return a paginated list of all datasets."""

    @abstractmethod
    async def create(self, dataset: SyntheticDataset) -> SyntheticDataset:
        """Persist a new dataset and return it."""

    @abstractmethod
    async def delete(self, dataset_id: str) -> bool:
        """Delete a dataset by ID. Returns True if found and deleted."""


class TimelineRepositoryInterface(ABC):
    """Abstract repository for Timeline persistence."""

    @abstractmethod
    async def get_by_id(self, timeline_id: str) -> Optional[Timeline]:
        """Return a timeline by its ID, or None if not found."""

    @abstractmethod
    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Return a paginated list of all timelines."""

    @abstractmethod
    async def create(self, timeline: Timeline) -> Timeline:
        """Persist a new timeline and return it."""

    @abstractmethod
    async def update(self, timeline_id: str, data: dict[str, Any]) -> Optional[Timeline]:
        """Update an existing timeline and return it."""

    @abstractmethod
    async def delete(self, timeline_id: str) -> bool:
        """Delete a timeline by ID. Returns True if found and deleted."""

    @abstractmethod
    async def get_by_scenario_id(self, scenario_id: str) -> list[Timeline]:
        """Return all timelines associated with a scenario."""


class ExerciseRepositoryInterface(ABC):
    """Abstract repository for Exercise persistence."""

    @abstractmethod
    async def get_by_id(self, exercise_id: str) -> Optional[Exercise]:
        """Return an exercise by its ID, or None if not found."""

    @abstractmethod
    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Return a paginated list of all exercises."""

    @abstractmethod
    async def create(self, exercise: Exercise) -> Exercise:
        """Persist a new exercise and return it."""

    @abstractmethod
    async def update(self, exercise_id: str, data: dict[str, Any]) -> Optional[Exercise]:
        """Update an existing exercise and return it."""

    @abstractmethod
    async def delete(self, exercise_id: str) -> bool:
        """Delete an exercise by ID. Returns True if found and deleted."""

    @abstractmethod
    async def search(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Search exercises by title, category, or tags."""

    @abstractmethod
    async def get_by_scenario_id(self, scenario_id: str) -> list[Exercise]:
        """Return all exercises linked to a scenario."""

    @abstractmethod
    async def get_by_status(self, status: str) -> list[Exercise]:
        """Return all exercises with the given status."""


class InstructorSessionRepositoryInterface(ABC):
    """Abstract repository for InstructorSession persistence."""

    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[InstructorSession]:
        """Return an instructor session by ID, or None if not found."""

    @abstractmethod
    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Return a paginated list of all instructor sessions."""

    @abstractmethod
    async def create(self, session: InstructorSession) -> InstructorSession:
        """Persist a new instructor session and return it."""

    @abstractmethod
    async def update(
        self, session_id: str, data: dict[str, Any]
    ) -> Optional[InstructorSession]:
        """Update an existing instructor session and return it."""

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Delete an instructor session by ID."""

    @abstractmethod
    async def get_by_instructor(self, instructor_id: str) -> list[InstructorSession]:
        """Return all sessions for a given instructor."""

    @abstractmethod
    async def get_by_exercise(self, exercise_id: str) -> list[InstructorSession]:
        """Return all sessions for a given exercise."""


class LearnerSessionRepositoryInterface(ABC):
    """Abstract repository for LearnerSession persistence."""

    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[LearnerSession]:
        """Return a learner session by ID, or None if not found."""

    @abstractmethod
    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Return a paginated list of all learner sessions."""

    @abstractmethod
    async def create(self, session: LearnerSession) -> LearnerSession:
        """Persist a new learner session and return it."""

    @abstractmethod
    async def update(
        self, session_id: str, data: dict[str, Any]
    ) -> Optional[LearnerSession]:
        """Update an existing learner session and return it."""

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Delete a learner session by ID."""

    @abstractmethod
    async def get_by_learner(self, learner_id: str) -> list[LearnerSession]:
        """Return all sessions for a given learner."""

    @abstractmethod
    async def get_by_exercise(self, exercise_id: str) -> list[LearnerSession]:
        """Return all sessions for a given exercise."""


class ResultsRepositoryInterface(ABC):
    """Abstract repository for ExerciseResult persistence."""

    @abstractmethod
    async def get_by_id(self, result_id: str) -> Optional[ExerciseResult]:
        """Return an exercise result by ID, or None if not found."""

    @abstractmethod
    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """Return a paginated list of all exercise results."""

    @abstractmethod
    async def create(self, result: ExerciseResult) -> ExerciseResult:
        """Persist a new exercise result and return it."""

    @abstractmethod
    async def update(
        self, result_id: str, data: dict[str, Any]
    ) -> Optional[ExerciseResult]:
        """Update an existing exercise result and return it."""

    @abstractmethod
    async def delete(self, result_id: str) -> bool:
        """Delete an exercise result by ID."""

    @abstractmethod
    async def get_by_session(self, session_id: str) -> Optional[ExerciseResult]:
        """Return the result for a given session."""

    @abstractmethod
    async def get_by_exercise(self, exercise_id: str) -> list[ExerciseResult]:
        """Return all results for a given exercise."""
