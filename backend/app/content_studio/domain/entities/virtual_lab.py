"""Virtual lab domain entities for the Content Production Studio."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class LabStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


@dataclass
class LabStep:
    """A single step in a virtual lab exercise."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    lab_id: str = ""
    step_number: int = 0
    title: str = ""
    instructions: str = ""
    hints: list[str] = field(default_factory=list)
    expected_result: str = ""
    validation_rules: dict = field(default_factory=dict)

    def add_hint(self, hint: str) -> None:
        if hint not in self.hints:
            self.hints.append(hint)

    def remove_hint(self, hint: str) -> bool:
        if hint in self.hints:
            self.hints.remove(hint)
            return True
        return False

    def update_validation_rules(self, rules: dict) -> None:
        self.validation_rules.update(rules)

    def validate_result(self, learner_result: str) -> bool:
        exact_match = self.validation_rules.get("exact_match", False)
        if exact_match:
            return learner_result.strip() == self.expected_result.strip()
        contains = self.validation_rules.get("contains", [])
        if isinstance(contains, list) and contains:
            result_lower = learner_result.lower()
            return all(item.lower() in result_lower for item in contains)
        return bool(learner_result.strip())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "lab_id": self.lab_id,
            "step_number": self.step_number,
            "title": self.title,
            "instructions": self.instructions,
            "hints": self.hints,
            "expected_result": self.expected_result,
            "validation_rules": self.validation_rules,
        }


@dataclass
class VirtualLab:
    """A virtual lab exercise with guided steps."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    lab_type: str = "hands_on"
    learning_objectives: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    steps: list[LabStep] = field(default_factory=list)
    expected_outcomes: list[str] = field(default_factory=list)
    reflection_questions: list[str] = field(default_factory=list)
    assessment_criteria: dict = field(default_factory=dict)
    a11y_instructions: str = ""
    estimated_minutes: int = 60
    status: LabStatus = LabStatus.DRAFT
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_step(self, step: LabStep) -> None:
        step.lab_id = self.id
        step.step_number = len(self.steps) + 1
        self.steps.append(step)
        self.updated_at = datetime.now(timezone.utc)

    def remove_step(self, step_id: str) -> bool:
        for i, step in enumerate(self.steps):
            if step.id == step_id:
                self.steps.pop(i)
                self._renumber_steps()
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False

    def reorder_steps(self, step_ids: list[str]) -> bool:
        step_map = {s.id: s for s in self.steps}
        reordered: list[LabStep] = []
        for idx, sid in enumerate(step_ids):
            step = step_map.get(sid)
            if step is None:
                return False
            step.step_number = idx + 1
            reordered.append(step)
        self.steps = reordered
        self.updated_at = datetime.now(timezone.utc)
        return True

    def update_status(self, new_status: LabStatus) -> None:
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def increment_version(self) -> None:
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)

    def get_step_count(self) -> int:
        return len(self.steps)

    def add_learning_objective(self, objective: str) -> None:
        if objective not in self.learning_objectives:
            self.learning_objectives.append(objective)
            self.updated_at = datetime.now(timezone.utc)

    def add_expected_outcome(self, outcome: str) -> None:
        if outcome not in self.expected_outcomes:
            self.expected_outcomes.append(outcome)
            self.updated_at = datetime.now(timezone.utc)

    def add_reflection_question(self, question: str) -> None:
        if question not in self.reflection_questions:
            self.reflection_questions.append(question)
            self.updated_at = datetime.now(timezone.utc)

    def update_assessment_criteria(self, criteria: dict) -> None:
        self.assessment_criteria.update(criteria)
        self.updated_at = datetime.now(timezone.utc)

    def calculate_estimated_minutes(self) -> int:
        per_step = 10
        return len(self.steps) * per_step

    def _renumber_steps(self) -> None:
        for i, step in enumerate(self.steps):
            step.step_number = i + 1

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "lab_type": self.lab_type,
            "learning_objectives": self.learning_objectives,
            "prerequisites": self.prerequisites,
            "steps": [s.to_dict() for s in self.steps],
            "expected_outcomes": self.expected_outcomes,
            "reflection_questions": self.reflection_questions,
            "assessment_criteria": self.assessment_criteria,
            "a11y_instructions": self.a11y_instructions,
            "estimated_minutes": self.estimated_minutes,
            "status": self.status.value,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "step_count": self.get_step_count(),
        }


@dataclass
class LabTemplate:
    """A reusable template for creating virtual labs."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    template_type: str = ""
    description: str = ""
    steps_template: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def add_step_template(self, step_data: dict) -> None:
        step_number = len(self.steps_template) + 1
        step_data.setdefault("step_number", step_number)
        self.steps_template.append(step_data)

    def remove_step_template(self, index: int) -> bool:
        if 0 <= index < len(self.steps_template):
            self.steps_template.pop(index)
            for i, step in enumerate(self.steps_template):
                step["step_number"] = i + 1
            return True
        return False

    def get_step_count(self) -> int:
        return len(self.steps_template)

    def update_metadata(self, metadata: dict) -> None:
        self.metadata.update(metadata)

    def create_lab_from_template(self, name: str) -> VirtualLab:
        lab = VirtualLab(name=name, description=self.description, lab_type=self.template_type)
        for step_data in self.steps_template:
            step = LabStep(
                title=step_data.get("title", ""),
                instructions=step_data.get("instructions", ""),
                hints=list(step_data.get("hints", [])),
                expected_result=step_data.get("expected_result", ""),
                validation_rules=dict(step_data.get("validation_rules", {})),
            )
            lab.add_step(step)
        return lab

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "template_type": self.template_type,
            "description": self.description,
            "steps_template": self.steps_template,
            "metadata": self.metadata,
            "step_count": self.get_step_count(),
        }
