"""Virtual lab service — lab CRUD, steps, and templates."""

from __future__ import annotations

import logging
from typing import Any, Optional

from ..domain.entities.virtual_lab import LabStatus, LabTemplate, LabStep, VirtualLab
from ..domain.events.content_studio_events import VirtualLabCreated
from ..domain.interfaces.content_studio_interfaces import ILabTemplateRepository, IVirtualLabRepository

logger = logging.getLogger(__name__)


class VirtualLabService:
    """Service for managing virtual labs, steps, and templates."""

    def __init__(
        self,
        lab_repo: IVirtualLabRepository,
        template_repo: ILabTemplateRepository,
    ) -> None:
        self._lab_repo = lab_repo
        self._template_repo = template_repo

    def create_lab(self, data: dict[str, Any]) -> dict[str, Any]:
        lab = VirtualLab(
            name=data.get("name", ""),
            description=data.get("description", ""),
            lab_type=data.get("lab_type", "hands_on"),
            learning_objectives=data.get("learning_objectives", []),
            prerequisites=data.get("prerequisites", []),
            expected_outcomes=data.get("expected_outcomes", []),
            reflection_questions=data.get("reflection_questions", []),
            assessment_criteria=data.get("assessment_criteria", {}),
            a11y_instructions=data.get("a11y_instructions", ""),
            estimated_minutes=data.get("estimated_minutes", 60),
            status=LabStatus(data.get("status", "draft")),
        )
        result = self._lab_repo.create({
            "id": lab.id,
            "name": lab.name,
            "description": lab.description,
            "lab_type": lab.lab_type,
            "learning_objectives": lab.learning_objectives,
            "prerequisites": lab.prerequisites,
            "steps": [],
            "expected_outcomes": lab.expected_outcomes,
            "reflection_questions": lab.reflection_questions,
            "assessment_criteria": lab.assessment_criteria,
            "a11y_instructions": lab.a11y_instructions,
            "estimated_minutes": lab.estimated_minutes,
            "status": lab.status.value,
            "version": lab.version,
        })

        event = VirtualLabCreated(
            lab_id=lab.id,
            lab_name=lab.name,
            lab_type=lab.lab_type,
        )
        logger.info("virtual_lab_created", extra={"lab_id": result["id"], "event_id": event.event_id})
        return result

    def get_lab(self, lab_id: str) -> Optional[dict[str, Any]]:
        return self._lab_repo.get_by_id(lab_id)

    def list_labs(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        return self._lab_repo.get_all(page=page, per_page=per_page, status=status)

    def update_lab(self, lab_id: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        existing = self._lab_repo.get_by_id(lab_id)
        if not existing:
            raise ValueError(f"Virtual lab '{lab_id}' not found.")
        if "status" in data:
            valid = {s.value for s in LabStatus}
            if data["status"] not in valid:
                raise ValueError(f"Invalid status '{data['status']}'. Must be one of: {valid}")
        data["version"] = existing.get("version", 1) + 1
        return self._lab_repo.update(lab_id, data)

    def delete_lab(self, lab_id: str) -> bool:
        if not self._lab_repo.get_by_id(lab_id):
            raise ValueError(f"Virtual lab '{lab_id}' not found.")
        return self._lab_repo.delete(lab_id)

    def add_step(self, lab_id: str, step_data: dict[str, Any]) -> dict[str, Any]:
        existing = self._lab_repo.get_by_id(lab_id)
        if not existing:
            raise ValueError(f"Virtual lab '{lab_id}' not found.")

        step = LabStep(
            title=step_data.get("title", ""),
            instructions=step_data.get("instructions", ""),
            hints=step_data.get("hints", []),
            expected_result=step_data.get("expected_result", ""),
            validation_rules=step_data.get("validation_rules", {}),
        )
        steps = existing.get("steps", [])
        step.step_number = len(steps) + 1
        step_dict = step.to_dict()
        steps.append(step_dict)
        self._lab_repo.update(lab_id, {"steps": steps})
        logger.info("lab_step_added", extra={"lab_id": lab_id, "step_id": step.id})
        return step_dict

    def update_step(
        self, lab_id: str, step_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        existing = self._lab_repo.get_by_id(lab_id)
        if not existing:
            raise ValueError(f"Virtual lab '{lab_id}' not found.")

        steps = existing.get("steps", [])
        for step in steps:
            if step["id"] == step_id:
                for key in ("title", "instructions", "hints", "expected_result", "validation_rules"):
                    if key in data:
                        step[key] = data[key]
                self._lab_repo.update(lab_id, {"steps": steps})
                return step
        raise ValueError(f"Step '{step_id}' not found in lab '{lab_id}'.")

    def remove_step(self, lab_id: str, step_id: str) -> bool:
        existing = self._lab_repo.get_by_id(lab_id)
        if not existing:
            raise ValueError(f"Virtual lab '{lab_id}' not found.")

        steps = existing.get("steps", [])
        for i, step in enumerate(steps):
            if step["id"] == step_id:
                steps.pop(i)
                for j, s in enumerate(steps):
                    s["step_number"] = j + 1
                self._lab_repo.update(lab_id, {"steps": steps})
                return True
        return False

    def reorder_steps(self, lab_id: str, step_ids: list[str]) -> bool:
        existing = self._lab_repo.get_by_id(lab_id)
        if not existing:
            raise ValueError(f"Virtual lab '{lab_id}' not found.")

        steps = existing.get("steps", [])
        step_map = {s["id"]: s for s in steps}
        reordered: list[dict[str, Any]] = []
        for idx, sid in enumerate(step_ids):
            step = step_map.get(sid)
            if step is None:
                return False
            step["step_number"] = idx + 1
            reordered.append(step)
        self._lab_repo.update(lab_id, {"steps": reordered})
        return True

    def search_labs(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        return self._lab_repo.search(query, page=page, per_page=per_page)

    def update_lab_status(self, lab_id: str, status: str) -> Optional[dict[str, Any]]:
        valid_statuses = {s.value for s in LabStatus}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
        return self._lab_repo.update(lab_id, {"status": status})

    def create_template(self, data: dict[str, Any]) -> dict[str, Any]:
        template = LabTemplate(
            name=data.get("name", ""),
            template_type=data.get("template_type", ""),
            description=data.get("description", ""),
            steps_template=data.get("steps_template", []),
            metadata=data.get("metadata", {}),
        )
        result = self._template_repo.create({
            "id": template.id,
            "name": template.name,
            "template_type": template.template_type,
            "description": template.description,
            "steps_template": template.steps_template,
            "metadata": template.metadata,
        })
        logger.info("lab_template_created", extra={"template_id": result["id"]})
        return result

    def get_template(self, template_id: str) -> Optional[dict[str, Any]]:
        return self._template_repo.get_by_id(template_id)

    def list_templates(self) -> list[dict[str, Any]]:
        return self._template_repo.get_all()

    def delete_template(self, template_id: str) -> bool:
        if not self._template_repo.get_by_id(template_id):
            raise ValueError(f"Template '{template_id}' not found.")
        return self._template_repo.delete(template_id)

    def create_lab_from_template(
        self, template_id: str, lab_name: str
    ) -> dict[str, Any]:
        template_data = self._template_repo.get_by_id(template_id)
        if not template_data:
            raise ValueError(f"Template '{template_id}' not found.")

        lab_data = {
            "name": lab_name,
            "description": template_data.get("description", ""),
            "lab_type": template_data.get("template_type", ""),
            "steps": [],
        }
        for step_data in template_data.get("steps_template", []):
            step = LabStep(
                title=step_data.get("title", ""),
                instructions=step_data.get("instructions", ""),
                hints=step_data.get("hints", []),
                expected_result=step_data.get("expected_result", ""),
                validation_rules=step_data.get("validation_rules", {}),
            )
            lab_data["steps"].append(step.to_dict())

        return self.create_lab(lab_data)
