"""Assessment mapper domain entity for exercise-to-outcome mapping."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CompletionRule:
    """A rule that governs when an exercise is considered complete."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_type: str = ""
    description: str = ""
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "rule_type": self.rule_type,
            "description": self.description,
            "required": self.required,
        }


@dataclass
class AssessmentMapper:
    """Maps exercises to learning objectives, competencies, and rubrics.

    Provides the bridge between what a learner does in an exercise
    and how their performance is evaluated against educational goals.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exercise_id: str = ""
    learning_objectives: list[str] = field(default_factory=list)
    competencies: list[str] = field(default_factory=list)
    assessment_criteria: list[str] = field(default_factory=list)
    rubrics: list[dict[str, Any]] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    completion_rules: dict[str, Any] = field(default_factory=dict)
    passing_threshold: float = 0.7
    instructor_notes: str = ""

    def add_completion_rule(self, rule: CompletionRule) -> None:
        """Add a completion rule to the mapper."""
        self.completion_rules[rule.id] = rule.to_dict()

    def remove_completion_rule(self, rule_id: str) -> bool:
        """Remove a completion rule by ID. Returns True if removed."""
        if rule_id in self.completion_rules:
            del self.completion_rules[rule_id]
            return True
        return False

    def get_completion_rules_list(self) -> list[CompletionRule]:
        """Return all completion rules as CompletionRule instances."""
        rules: list[CompletionRule] = []
        for rule_id, rule_data in self.completion_rules.items():
            if isinstance(rule_data, dict):
                rules.append(
                    CompletionRule(
                        id=rule_id,
                        rule_type=rule_data.get("rule_type", ""),
                        description=rule_data.get("description", ""),
                        required=rule_data.get("required", True),
                    )
                )
        return rules

    def check_passing(self, score: float) -> bool:
        """Return True if the score meets or exceeds the passing threshold."""
        return score >= self.passing_threshold

    def validate(self) -> list[str]:
        """Validate the mapper configuration and return error messages."""
        errors: list[str] = []

        if not self.exercise_id:
            errors.append("Exercise ID is required")

        if not self.learning_objectives:
            errors.append("At least one learning objective is required")

        if not self.assessment_criteria:
            errors.append("At least one assessment criterion is required")

        if not (0.0 <= self.passing_threshold <= 1.0):
            errors.append("Passing threshold must be between 0.0 and 1.0")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "exercise_id": self.exercise_id,
            "learning_objectives": list(self.learning_objectives),
            "competencies": list(self.competencies),
            "assessment_criteria": list(self.assessment_criteria),
            "rubrics": list(self.rubrics),
            "evidence_requirements": list(self.evidence_requirements),
            "completion_rules": dict(self.completion_rules),
            "passing_threshold": self.passing_threshold,
            "instructor_notes": self.instructor_notes,
        }
