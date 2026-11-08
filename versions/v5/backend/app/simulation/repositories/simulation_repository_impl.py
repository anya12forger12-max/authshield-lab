"""In-memory repository implementations for the simulation module."""

from __future__ import annotations

import copy
from typing import Any, Optional

from ..domain.entities.scenario import Scenario
from ..domain.entities.dataset import SyntheticDataset
from ..domain.entities.timeline import Timeline
from ..domain.entities.exercise import Exercise
from ..domain.entities.console import InstructorSession, LearnerSession
from ..domain.entities.results import ExerciseResult
from ..domain.interfaces import (
    ScenarioRepositoryInterface,
    DatasetRepositoryInterface,
    TimelineRepositoryInterface,
    ExerciseRepositoryInterface,
    InstructorSessionRepositoryInterface,
    LearnerSessionRepositoryInterface,
    ResultsRepositoryInterface,
)


class InMemoryScenarioRepository(ScenarioRepositoryInterface):
    """In-memory implementation of the Scenario repository."""

    def __init__(self) -> None:
        self._store: dict[str, Scenario] = {}

    async def get_by_id(self, scenario_id: str) -> Optional[Scenario]:
        scenario = self._store.get(scenario_id)
        return copy.deepcopy(scenario) if scenario else None

    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        items = list(self._store.values())
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page)
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def create(self, scenario: Scenario) -> Scenario:
        self._store[scenario.id] = copy.deepcopy(scenario)
        return copy.deepcopy(scenario)

    async def update(
        self, scenario_id: str, data: dict[str, Any]
    ) -> Optional[Scenario]:
        scenario = self._store.get(scenario_id)
        if scenario is None:
            return None
        for key, value in data.items():
            if hasattr(scenario, key):
                setattr(scenario, key, value)
        self._store[scenario_id] = scenario
        return copy.deepcopy(scenario)

    async def delete(self, scenario_id: str) -> bool:
        if scenario_id in self._store:
            del self._store[scenario_id]
            return True
        return False

    async def search(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        query_lower = query.lower()
        matched = [
            s
            for s in self._store.values()
            if query_lower in s.title.lower()
            or query_lower in s.description.lower()
        ]
        total = len(matched)
        pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": [copy.deepcopy(i) for i in matched[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def get_by_status(self, status: str) -> list[Scenario]:
        return [
            copy.deepcopy(s)
            for s in self._store.values()
            if s.status.value == status
        ]


class InMemoryDatasetRepository(DatasetRepositoryInterface):
    """In-memory implementation of the Dataset repository."""

    def __init__(self) -> None:
        self._store: dict[str, SyntheticDataset] = {}

    async def get_by_id(self, dataset_id: str) -> Optional[SyntheticDataset]:
        dataset = self._store.get(dataset_id)
        return copy.deepcopy(dataset) if dataset else None

    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        items = list(self._store.values())
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def create(self, dataset: SyntheticDataset) -> SyntheticDataset:
        self._store[dataset.id] = copy.deepcopy(dataset)
        return copy.deepcopy(dataset)

    async def delete(self, dataset_id: str) -> bool:
        if dataset_id in self._store:
            del self._store[dataset_id]
            return True
        return False


class InMemoryTimelineRepository(TimelineRepositoryInterface):
    """In-memory implementation of the Timeline repository."""

    def __init__(self) -> None:
        self._store: dict[str, Timeline] = {}

    async def get_by_id(self, timeline_id: str) -> Optional[Timeline]:
        timeline = self._store.get(timeline_id)
        return copy.deepcopy(timeline) if timeline else None

    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        items = list(self._store.values())
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def create(self, timeline: Timeline) -> Timeline:
        self._store[timeline.id] = copy.deepcopy(timeline)
        return copy.deepcopy(timeline)

    async def update(
        self, timeline_id: str, data: dict[str, Any]
    ) -> Optional[Timeline]:
        timeline = self._store.get(timeline_id)
        if timeline is None:
            return None
        for key, value in data.items():
            if hasattr(timeline, key):
                setattr(timeline, key, value)
        self._store[timeline_id] = timeline
        return copy.deepcopy(timeline)

    async def delete(self, timeline_id: str) -> bool:
        if timeline_id in self._store:
            del self._store[timeline_id]
            return True
        return False

    async def get_by_scenario_id(self, scenario_id: str) -> list[Timeline]:
        return [
            copy.deepcopy(t)
            for t in self._store.values()
            if t.scenario_id == scenario_id
        ]


class InMemoryExerciseRepository(ExerciseRepositoryInterface):
    """In-memory implementation of the Exercise repository."""

    def __init__(self) -> None:
        self._store: dict[str, Exercise] = {}

    async def get_by_id(self, exercise_id: str) -> Optional[Exercise]:
        exercise = self._store.get(exercise_id)
        return copy.deepcopy(exercise) if exercise else None

    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        items = list(self._store.values())
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def create(self, exercise: Exercise) -> Exercise:
        self._store[exercise.id] = copy.deepcopy(exercise)
        return copy.deepcopy(exercise)

    async def update(
        self, exercise_id: str, data: dict[str, Any]
    ) -> Optional[Exercise]:
        exercise = self._store.get(exercise_id)
        if exercise is None:
            return None
        for key, value in data.items():
            if hasattr(exercise, key):
                setattr(exercise, key, value)
        self._store[exercise_id] = exercise
        return copy.deepcopy(exercise)

    async def delete(self, exercise_id: str) -> bool:
        if exercise_id in self._store:
            del self._store[exercise_id]
            return True
        return False

    async def search(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        query_lower = query.lower()
        matched = [
            e
            for e in self._store.values()
            if query_lower in e.title.lower()
            or query_lower in e.description.lower()
            or query_lower in e.category.lower()
            or any(query_lower in tag.lower() for tag in e.tags)
        ]
        total = len(matched)
        pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": [copy.deepcopy(i) for i in matched[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def get_by_scenario_id(self, scenario_id: str) -> list[Exercise]:
        return [
            copy.deepcopy(e)
            for e in self._store.values()
            if e.scenario_id == scenario_id
        ]

    async def get_by_status(self, status: str) -> list[Exercise]:
        return [
            copy.deepcopy(e)
            for e in self._store.values()
            if e.status.value == status
        ]


class InMemoryInstructorSessionRepository(InstructorSessionRepositoryInterface):
    """In-memory implementation of the InstructorSession repository."""

    def __init__(self) -> None:
        self._store: dict[str, InstructorSession] = {}

    async def get_by_id(self, session_id: str) -> Optional[InstructorSession]:
        session = self._store.get(session_id)
        return copy.deepcopy(session) if session else None

    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        items = list(self._store.values())
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def create(self, session: InstructorSession) -> InstructorSession:
        self._store[session.id] = copy.deepcopy(session)
        return copy.deepcopy(session)

    async def update(
        self, session_id: str, data: dict[str, Any]
    ) -> Optional[InstructorSession]:
        session = self._store.get(session_id)
        if session is None:
            return None
        for key, value in data.items():
            if hasattr(session, key):
                setattr(session, key, value)
        self._store[session_id] = session
        return copy.deepcopy(session)

    async def delete(self, session_id: str) -> bool:
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False

    async def get_by_instructor(
        self, instructor_id: str
    ) -> list[InstructorSession]:
        return [
            copy.deepcopy(s)
            for s in self._store.values()
            if s.instructor_id == instructor_id
        ]

    async def get_by_exercise(
        self, exercise_id: str
    ) -> list[InstructorSession]:
        return [
            copy.deepcopy(s)
            for s in self._store.values()
            if s.exercise_id == exercise_id
        ]


class InMemoryLearnerSessionRepository(LearnerSessionRepositoryInterface):
    """In-memory implementation of the LearnerSession repository."""

    def __init__(self) -> None:
        self._store: dict[str, LearnerSession] = {}

    async def get_by_id(self, session_id: str) -> Optional[LearnerSession]:
        session = self._store.get(session_id)
        return copy.deepcopy(session) if session else None

    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        items = list(self._store.values())
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def create(self, session: LearnerSession) -> LearnerSession:
        self._store[session.id] = copy.deepcopy(session)
        return copy.deepcopy(session)

    async def update(
        self, session_id: str, data: dict[str, Any]
    ) -> Optional[LearnerSession]:
        session = self._store.get(session_id)
        if session is None:
            return None
        for key, value in data.items():
            if hasattr(session, key):
                setattr(session, key, value)
        self._store[session_id] = session
        return copy.deepcopy(session)

    async def delete(self, session_id: str) -> bool:
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False

    async def get_by_learner(self, learner_id: str) -> list[LearnerSession]:
        return [
            copy.deepcopy(s)
            for s in self._store.values()
            if s.learner_id == learner_id
        ]

    async def get_by_exercise(
        self, exercise_id: str
    ) -> list[LearnerSession]:
        return [
            copy.deepcopy(s)
            for s in self._store.values()
            if s.exercise_id == exercise_id
        ]


class InMemoryResultsRepository(ResultsRepositoryInterface):
    """In-memory implementation of the Results repository."""

    def __init__(self) -> None:
        self._store: dict[str, ExerciseResult] = {}

    async def get_by_id(self, result_id: str) -> Optional[ExerciseResult]:
        result = self._store.get(result_id)
        return copy.deepcopy(result) if result else None

    async def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        items = list(self._store.values())
        total = len(items)
        pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "items": [copy.deepcopy(i) for i in items[start:end]],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def create(self, result: ExerciseResult) -> ExerciseResult:
        self._store[result.id] = copy.deepcopy(result)
        return copy.deepcopy(result)

    async def update(
        self, result_id: str, data: dict[str, Any]
    ) -> Optional[ExerciseResult]:
        result = self._store.get(result_id)
        if result is None:
            return None
        for key, value in data.items():
            if hasattr(result, key):
                setattr(result, key, value)
        self._store[result_id] = result
        return copy.deepcopy(result)

    async def delete(self, result_id: str) -> bool:
        if result_id in self._store:
            del self._store[result_id]
            return True
        return False

    async def get_by_session(
        self, session_id: str
    ) -> Optional[ExerciseResult]:
        for result in self._store.values():
            if result.session_id == session_id:
                return copy.deepcopy(result)
        return None

    async def get_by_exercise(
        self, exercise_id: str
    ) -> list[ExerciseResult]:
        return [
            copy.deepcopy(r)
            for r in self._store.values()
            if r.exercise_id == exercise_id
        ]
