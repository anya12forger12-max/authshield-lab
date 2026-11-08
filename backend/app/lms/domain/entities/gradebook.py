"""Gradebook domain entities for the LMS module."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class GradingCategory(str, Enum):
    """Categories for grade items."""

    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    EXAM = "exam"
    PROJECT = "project"
    PARTICIPATION = "participation"
    PRACTICAL = "practical"


@dataclass
class GradeItem:
    """A single gradable item within a gradebook."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    gradebook_id: str = ""
    name: str = ""
    category: GradingCategory = GradingCategory.ASSIGNMENT
    points_possible: float = 100.0
    weight: float = 1.0
    due_date: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "gradebook_id": self.gradebook_id,
            "name": self.name,
            "category": self.category.value,
            "points_possible": self.points_possible,
            "weight": self.weight,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }


@dataclass
class GradeEntry:
    """A recorded score for a learner on a specific grade item."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    grade_item_id: str = ""
    learner_id: str = ""
    score: float = 0.0
    graded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    feedback: Optional[str] = None
    graded_by: Optional[str] = None

    @property
    def percentage(self) -> float:
        """Return the score as a fraction of the possible points.

        This is a basic indicator; actual percentage depends on the
        GradeItem's ``points_possible`` which must be supplied externally.
        """
        return self.score

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "grade_item_id": self.grade_item_id,
            "learner_id": self.learner_id,
            "score": self.score,
            "graded_at": self.graded_at.isoformat(),
            "feedback": self.feedback,
            "graded_by": self.graded_by,
        }


@dataclass
class GradeScale:
    """Maps percentage ranges to letter grades."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    scale: dict[str, tuple[float, float]] = field(default_factory=dict)

    def get_letter_grade(self, percentage: float) -> str:
        """Return the letter grade for the given percentage.

        The ``scale`` dict maps letter grades like ``"A"`` to a tuple
        ``(lower_bound, upper_bound)`` inclusive.
        """
        for letter, (low, high) in self.scale.items():
            if low <= percentage <= high:
                return letter
        return "F"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "scale": {k: list(v) for k, v in self.scale.items()},
        }


@dataclass
class GradebookEntry:
    """Aggregates grade items and entries for a specific course."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str = ""
    items: list[GradeItem] = field(default_factory=list)

    def add_item(self, item: GradeItem) -> None:
        item.gradebook_id = self.id
        self.items.append(item)

    def get_item(self, item_id: str) -> Optional[GradeItem]:
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def calculate_weighted_average(
        self,
        entries: list[GradeEntry],
    ) -> float:
        """Calculate the weighted average across all grade items.

        Parameters
        ----------
        entries:
            All grade entries for the learner within this gradebook.

        Returns
        -------
        float
            The weighted average percentage (0-100), or 0.0 if no items exist.
        """
        entries_by_item: dict[str, list[GradeEntry]] = {}
        for entry in entries:
            entries_by_item.setdefault(entry.grade_item_id, []).append(entry)

        total_weighted_score = 0.0
        total_weight = 0.0

        for item in self.items:
            item_entries = entries_by_item.get(item.id, [])
            if not item_entries or item.points_possible <= 0:
                continue
            best_score = max(e.score for e in item_entries)
            percentage = (best_score / item.points_possible) * 100.0
            total_weighted_score += percentage * item.weight
            total_weight += item.weight

        if total_weight <= 0:
            return 0.0
        return round(total_weighted_score / total_weight, 2)

    def calculate_letter_grade(
        self,
        entries: list[GradeEntry],
        grade_scale: GradeScale,
    ) -> str:
        """Calculate the letter grade using the provided grade scale.

        Parameters
        ----------
        entries:
            All grade entries for the learner within this gradebook.
        grade_scale:
            The grade scale to use for mapping percentages to letters.

        Returns
        -------
        str
            The letter grade.
        """
        average = self.calculate_weighted_average(entries)
        return grade_scale.get_letter_grade(average)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "course_id": self.course_id,
            "items": [i.to_dict() for i in self.items],
        }
