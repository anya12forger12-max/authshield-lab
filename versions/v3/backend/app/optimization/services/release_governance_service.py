"""Release governance service — workflows, approvals, gates, checklists."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.release_governance import (
    ReleaseApproval,
    ReleaseChecklistItem,
    ReleaseGate,
    ReleaseStage,
    ReleaseWorkflow,
)
from ..domain.events.optimization_events import ReleaseWorkflowAdvanced
from ..domain.interfaces.optimization_interfaces import IReleaseRepository

logger = logging.getLogger(__name__)


class ReleaseGovernanceService:
    """Manages release workflows, stages, approvals, gates, and checklists."""

    def __init__(self, repo: IReleaseRepository) -> None:
        self._repo = repo

    # ------------------------------------------------------------------
    # Workflows
    # ------------------------------------------------------------------

    def create_workflow(self, data: dict[str, Any]) -> dict[str, Any]:
        workflow = ReleaseWorkflow(
            release_id=data.get("release_id", ""),
            version=data.get("version", ""),
            created_by=data.get("created_by", ""),
        )
        if data.get("initial_stage"):
            try:
                workflow.current_stage = ReleaseStage(data["initial_stage"])
            except ValueError:
                pass
        return self._repo.create_workflow(workflow.to_dict())

    def get_workflow(self, workflow_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_workflow_by_id(workflow_id)

    def get_workflow_by_release(self, release_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_workflow_by_release_id(release_id)

    def list_workflows(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        return self._repo.get_all_workflows(page=page, per_page=per_page)

    def advance_workflow(
        self, workflow_id: str, notes: str = ""
    ) -> dict[str, Any]:
        """Advance a workflow to the next stage."""
        workflow_data = self._repo.get_workflow_by_id(workflow_id)
        if not workflow_data:
            raise ValueError(f"Workflow '{workflow_id}' not found.")

        stages = list(ReleaseStage)
        try:
            current = ReleaseStage(workflow_data["current_stage"])
        except ValueError:
            current = ReleaseStage.PLANNING

        current_idx = stages.index(current)
        if current_idx >= len(stages) - 1:
            return workflow_data

        previous_stage = current.value
        history = list(workflow_data.get("stage_history", []))
        history.append({
            "stage": previous_stage,
            "exited_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
        })

        next_stage = stages[current_idx + 1]
        updates = {
            "current_stage": next_stage.value,
            "stage_history": history,
        }
        result = self._repo.update_workflow(workflow_id, updates)

        event = ReleaseWorkflowAdvanced(
            workflow_id=workflow_id,
            release_id=workflow_data.get("release_id", ""),
            previous_stage=previous_stage,
            current_stage=next_stage.value,
        )
        logger.info(
            "workflow_advanced",
            extra={
                "workflow_id": workflow_id,
                "from_stage": previous_stage,
                "to_stage": next_stage.value,
                "event_id": event.event_id,
            },
        )
        return result or workflow_data

    def complete_workflow(self, workflow_id: str) -> Optional[dict[str, Any]]:
        """Mark a workflow as completed."""
        workflow = self._repo.get_workflow_by_id(workflow_id)
        if not workflow:
            return None
        return self._repo.update_workflow(workflow_id, {
            "completed_at": datetime.now(timezone.utc).isoformat(),
        })

    # ------------------------------------------------------------------
    # Approvals
    # ------------------------------------------------------------------

    def create_approval(self, data: dict[str, Any]) -> dict[str, Any]:
        stage_str = data.get("stage", "planning")
        try:
            stage = ReleaseStage(stage_str)
        except ValueError:
            stage = ReleaseStage.PLANNING
        approval = ReleaseApproval(
            workflow_id=data.get("workflow_id", ""),
            stage=stage,
            approver=data.get("approver", ""),
        )
        return self._repo.create_approval(approval.to_dict())

    def approve(
        self, approval_id: str, comments: str = ""
    ) -> Optional[dict[str, Any]]:
        """Record an approval."""
        approvals = self._repo.get_approvals_for_workflow(approval_id)
        for a in approvals:
            if a["id"] == approval_id:
                return self._repo.update_approval(approval_id, {
                    "approved": True,
                    "comments": comments,
                    "approved_at": datetime.now(timezone.utc).isoformat(),
                })
        return None

    def reject(
        self, approval_id: str, comments: str = ""
    ) -> Optional[dict[str, Any]]:
        """Record a rejection."""
        approvals_list = self._repo.get_approvals_for_workflow(approval_id)
        for a in approvals_list:
            if a["id"] == approval_id:
                return self._repo.update_approval(approval_id, {
                    "approved": False,
                    "comments": comments,
                })
        return None

    def get_approvals_for_workflow(self, workflow_id: str) -> list[dict[str, Any]]:
        return self._repo.get_approvals_for_workflow(workflow_id)

    # ------------------------------------------------------------------
    # Gates
    # ------------------------------------------------------------------

    def create_gate(self, data: dict[str, Any]) -> dict[str, Any]:
        gate = ReleaseGate(
            release_id=data.get("release_id", ""),
            gate_type=data.get("gate_type", ""),
            required=data.get("required", True),
        )
        return self._repo.create_gate(gate.to_dict())

    def check_gate(
        self, gate_id: str, passed: bool, evidence: str = ""
    ) -> Optional[dict[str, Any]]:
        """Record a gate check result."""
        gates = self._repo.get_gates_for_release(gate_id)
        for g in gates:
            if g["id"] == gate_id:
                return self._repo.update_gate(gate_id, {
                    "passed": passed,
                    "evidence": evidence,
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                })
        return None

    def get_gates_for_release(self, release_id: str) -> list[dict[str, Any]]:
        return self._repo.get_gates_for_release(release_id)

    def all_required_gates_passed(self, release_id: str) -> bool:
        """Return True if all required gates for a release have passed."""
        gates = self._repo.get_gates_for_release(release_id)
        required_gates = [g for g in gates if g.get("required", True)]
        return all(g.get("passed", False) for g in required_gates)

    # ------------------------------------------------------------------
    # Checklists
    # ------------------------------------------------------------------

    def create_checklist_item(self, data: dict[str, Any]) -> dict[str, Any]:
        item = ReleaseChecklistItem(
            release_id=data.get("release_id", ""),
            item=data.get("item", ""),
            category=data.get("category", ""),
            assignee=data.get("assignee", ""),
            due_date=data.get("due_date", ""),
        )
        return self._repo.create_checklist_item(item.to_dict())

    def complete_checklist_item(self, item_id: str) -> Optional[dict[str, Any]]:
        """Mark a checklist item as completed."""
        return self._repo.update_checklist_item(item_id, {
            "completed": True,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        })

    def uncomplete_checklist_item(self, item_id: str) -> Optional[dict[str, Any]]:
        """Mark a checklist item as not completed."""
        return self._repo.update_checklist_item(item_id, {
            "completed": False,
            "completed_at": None,
        })

    def get_checklist_for_release(self, release_id: str) -> list[dict[str, Any]]:
        return self._repo.get_checklist_for_release(release_id)

    def checklist_progress(self, release_id: str) -> dict[str, Any]:
        """Return checklist completion statistics for a release."""
        items = self._repo.get_checklist_for_release(release_id)
        completed = [i for i in items if i.get("completed", False)]
        return {
            "release_id": release_id,
            "total": len(items),
            "completed": len(completed),
            "progress_pct": round(
                (len(completed) / len(items) * 100.0) if items else 0.0, 2
            ),
        }

    def is_release_ready(self, release_id: str) -> dict[str, Any]:
        """Check if a release is ready for distribution."""
        gates_ok = self.all_required_gates_passed(release_id)
        checklist = self.checklist_progress(release_id)
        all_items_done = checklist["completed"] == checklist["total"] and checklist["total"] > 0
        ready = gates_ok and all_items_done
        return {
            "release_id": release_id,
            "gates_passed": gates_ok,
            "checklist_complete": all_items_done,
            "ready_for_distribution": ready,
        }
