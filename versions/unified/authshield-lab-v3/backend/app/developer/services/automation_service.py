"""Automation workflow service."""

from __future__ import annotations

from datetime import datetime, timezone

from app.developer.domain.entities.automation import (
    AutomationWorkflow,
    WorkflowRun,
    WorkflowStatus,
    WorkflowStep,
)


class AutomationService:
    """Create, run, schedule, monitor, and cancel automation workflows."""

    def __init__(self) -> None:
        self._workflows: dict[str, AutomationWorkflow] = {}
        self._runs: dict[str, WorkflowRun] = {}

    def create_workflow(
        self,
        name: str,
        description: str = "",
        workflow_type: str = "custom",
        steps: list[WorkflowStep] | None = None,
        schedule: str = "",
        enabled: bool = True,
    ) -> AutomationWorkflow:
        """Create a new automation workflow."""
        wf = AutomationWorkflow(
            name=name,
            description=description,
            workflow_type=workflow_type,
            steps=steps,
            schedule=schedule,
            enabled=enabled,
        )
        self._workflows[wf.id] = wf
        return wf

    def get_workflow(self, workflow_id: str) -> AutomationWorkflow | None:
        """Retrieve a workflow by its ID."""
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> list[AutomationWorkflow]:
        """Return all workflows."""
        return list(self._workflows.values())

    def list_enabled_workflows(self) -> list[AutomationWorkflow]:
        """Return only enabled workflows."""
        return [w for w in self._workflows.values() if w.enabled]

    def add_step(
        self,
        workflow_id: str,
        step_type: str = "action",
        action: str = "",
        params: dict | None = None,
        order: int = 0,
        on_failure: str = "stop",
    ) -> WorkflowStep | None:
        """Add a step to a workflow."""
        wf = self._workflows.get(workflow_id)
        if wf is None:
            return None
        step = WorkflowStep(
            step_type=step_type,
            action=action,
            params=params,
            order=order,
            on_failure=on_failure,
        )
        wf.add_step(step)
        return step

    def remove_step(self, workflow_id: str, step_id: str) -> bool:
        """Remove a step from a workflow."""
        wf = self._workflows.get(workflow_id)
        if wf is None:
            return False
        wf.remove_step(step_id)
        return True

    def run_workflow(self, workflow_id: str) -> WorkflowRun | None:
        """Execute a workflow synchronously (simulated)."""
        wf = self._workflows.get(workflow_id)
        if wf is None or not wf.enabled:
            return None
        if wf.status == WorkflowStatus.RUNNING:
            return None
        wf.mark_running()
        run = WorkflowRun(workflow_id=workflow_id)
        self._runs[run.id] = run
        try:
            for step in wf.steps:
                run.add_result({
                    "step_id": step.id,
                    "action": step.action,
                    "status": "completed",
                    "output": f"Step '{step.action}' executed successfully",
                })
            run.finish("completed")
            wf.mark_completed()
        except Exception as exc:
            run.add_error(str(exc))
            run.finish("failed")
            wf.mark_failed()
        return run

    def get_run(self, run_id: str) -> WorkflowRun | None:
        """Retrieve a workflow run by ID."""
        return self._runs.get(run_id)

    def list_runs(self, workflow_id: str | None = None) -> list[WorkflowRun]:
        """Return runs, optionally filtered by workflow."""
        if workflow_id is None:
            return list(self._runs.values())
        return [r for r in self._runs.values() if r.workflow_id == workflow_id]

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        wf = self._workflows.get(workflow_id)
        if wf is None:
            return False
        if wf.status != WorkflowStatus.RUNNING:
            return False
        wf.mark_failed()
        return True

    def enable_workflow(self, workflow_id: str) -> bool:
        """Enable a workflow."""
        wf = self._workflows.get(workflow_id)
        if wf is None:
            return False
        wf.enable()
        return True

    def disable_workflow(self, workflow_id: str) -> bool:
        """Disable a workflow."""
        wf = self._workflows.get(workflow_id)
        if wf is None:
            return False
        wf.disable()
        return True

    def update_workflow(
        self,
        workflow_id: str,
        name: str | None = None,
        description: str | None = None,
        schedule: str | None = None,
    ) -> AutomationWorkflow | None:
        """Update mutable fields of a workflow."""
        wf = self._workflows.get(workflow_id)
        if wf is None:
            return None
        if name is not None:
            wf.name = name
        if description is not None:
            wf.description = description
        if schedule is not None:
            wf.schedule = schedule
        return wf

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow and its run history."""
        if workflow_id not in self._workflows:
            return False
        del self._workflows[workflow_id]
        to_remove = [
            rid for rid, r in self._runs.items() if r.workflow_id == workflow_id
        ]
        for rid in to_remove:
            del self._runs[rid]
        return True

    def get_workflow_stats(self, workflow_id: str) -> dict:
        """Return execution statistics for a workflow."""
        runs = [r for r in self._runs.values() if r.workflow_id == workflow_id]
        total = len(runs)
        completed = sum(1 for r in runs if r.status == "completed")
        failed = sum(1 for r in runs if r.status == "failed")
        avg_duration = (
            sum(r.duration_seconds for r in runs) / total if total > 0 else 0.0
        )
        return {
            "workflow_id": workflow_id,
            "total_runs": total,
            "completed": completed,
            "failed": failed,
            "success_rate": round(completed / total, 4) if total else 0.0,
            "average_duration_seconds": round(avg_duration, 2),
        }
