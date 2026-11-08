"""Gradebook management service for the LMS module."""

from __future__ import annotations

import logging
from typing import Any, Optional

from ..domain.events.lms_events import GradeSubmitted
from ..domain.interfaces.lms_interfaces import IGradebookRepository
from ..validators.lms_validator import validate_grade_data

logger = logging.getLogger(__name__)


class GradebookService:
    """Service for managing gradebooks, items, and entries."""

    def __init__(self, gradebook_repo: IGradebookRepository) -> None:
        self._repo = gradebook_repo

    def create_gradebook(self, course_id: str) -> dict[str, Any]:
        existing = self._repo.get_by_course(course_id)
        if existing:
            raise ValueError(f"Gradebook already exists for course '{course_id}'.")
        return self._repo.create({"course_id": course_id})

    def get_gradebook(self, entry_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_by_id(entry_id)

    def get_gradebook_by_course(self, course_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_by_course(course_id)

    def update_gradebook(self, entry_id: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        if not self._repo.get_by_id(entry_id):
            raise ValueError(f"Gradebook '{entry_id}' not found.")
        return self._repo.update(entry_id, data)

    def delete_gradebook(self, entry_id: str) -> bool:
        if not self._repo.get_by_id(entry_id):
            raise ValueError(f"Gradebook '{entry_id}' not found.")
        return self._repo.delete(entry_id)

    def add_grade_item(self, gradebook_id: str, item_data: dict[str, Any]) -> dict[str, Any]:
        gradebook = self._repo.get_by_id(gradebook_id)
        if not gradebook:
            raise ValueError(f"Gradebook '{gradebook_id}' not found.")

        if "name" not in item_data or not str(item_data["name"]).strip():
            raise ValueError("Grade item name is required.")
        if item_data.get("points_possible", 100.0) <= 0:
            raise ValueError("Points possible must be greater than 0.")

        return self._repo.add_grade_item(gradebook_id, item_data)

    def add_grade_entry(
        self, item_id: str, entry_data: dict[str, Any]
    ) -> dict[str, Any]:
        validation = validate_grade_data(entry_data)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.to_dict()}")

        entry = self._repo.add_grade_entry(item_id, entry_data)
        event = GradeSubmitted(
            grade_entry_id=entry["id"],
            learner_id=entry.get("learner_id", ""),
            grade_item_id=item_id,
            score=entry.get("score", 0.0),
        )
        logger.info(
            "grade_submitted",
            extra={"grade_entry_id": entry["id"], "event_id": event.event_id},
        )
        return entry

    def get_grade_entries(
        self,
        gradebook_id: Optional[str] = None,
        item_id: Optional[str] = None,
        learner_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return self._repo.get_grade_entries(item_id=item_id, learner_id=learner_id)

    def get_learner_grades(
        self, gradebook_id: str, learner_id: str
    ) -> list[dict[str, Any]]:
        return self._repo.get_grade_entries(learner_id=learner_id)

    def calculate_learner_average(
        self, gradebook_id: str, learner_id: str
    ) -> float:
        gradebook = self._repo.get_by_id(gradebook_id)
        if not gradebook:
            raise ValueError(f"Gradebook '{gradebook_id}' not found.")

        entries = self._repo.get_grade_entries(learner_id=learner_id)
        items = gradebook.get("items", [])

        entries_by_item: dict[str, list[dict[str, Any]]] = {}
        for entry in entries:
            gi_id = entry.get("grade_item_id", "")
            entries_by_item.setdefault(gi_id, []).append(entry)

        total_weighted = 0.0
        total_weight = 0.0
        for item in items:
            item_id = item.get("id", "")
            item_entries = entries_by_item.get(item_id, [])
            if not item_entries:
                continue
            points_possible = item.get("points_possible", 100.0)
            weight = item.get("weight", 1.0)
            if points_possible <= 0:
                continue
            best = max(e.get("score", 0.0) for e in item_entries)
            pct = (best / points_possible) * 100.0
            total_weighted += pct * weight
            total_weight += weight

        if total_weight <= 0:
            return 0.0
        return round(total_weighted / total_weight, 2)

    def get_course_statistics(self, gradebook_id: str) -> dict[str, Any]:
        gradebook = self._repo.get_by_id(gradebook_id)
        if not gradebook:
            raise ValueError(f"Gradebook '{gradebook_id}' not found.")

        items = gradebook.get("items", [])
        all_entries = self._repo.get_grade_entries()

        scores: list[float] = []
        for entry in all_entries:
            score = entry.get("score")
            if score is not None:
                scores.append(score)

        if not scores:
            return {
                "gradebook_id": gradebook_id,
                "total_items": len(items),
                "total_entries": 0,
                "average_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0,
            }

        return {
            "gradebook_id": gradebook_id,
            "total_items": len(items),
            "total_entries": len(scores),
            "average_score": round(sum(scores) / len(scores), 2),
            "min_score": min(scores),
            "max_score": max(scores),
        }
