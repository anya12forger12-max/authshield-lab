"""AutomationWorkflow, WorkflowStep, and WorkflowRun entities."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum


class WorkflowStatus(str, Enum):
    """Lifecycle status of an automation workflow."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStep:
    """A single step inside an automation workflow."""

    def __init__(
        self,
        id: str | None = None,
        step_type: str = "action",
        action: str = "",
        params: dict | None = None,
        order: int = 0,
        on_failure: str = "stop",
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.step_type: str = step_type
        self.action: str = action
        self.params: dict = params if params is not None else {}
        self.order: int = order
        self.on_failure: str = on_failure

    def set_param(self, key: str, value: object) -> None:
        """Add or update a parameter on this step."""
        self.params[key] = value

    def remove_param(self, key: str) -> None:
        """Remove a parameter from this step."""
        self.params.pop(key, None)

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "step_type": self.step_type,
            "action": self.action,
            "params": dict(self.params),
            "order": self.order,
            "on_failure": self.on_failure,
        }


class AutomationWorkflow:
    """An automation workflow that chains multiple steps together."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        description: str = "",
        workflow_type: str = "custom",
        steps: list[WorkflowStep] | None = None,
        schedule: str = "",
        enabled: bool = True,
        last_run: datetime | None = None,
        next_run: datetime | None = None,
        status: WorkflowStatus = WorkflowStatus.IDLE,
        created_at: datetime | None = None,
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.name: str = name
        self.description: str = description
        self.workflow_type: str = workflow_type
        self.steps: list[WorkflowStep] = steps if steps is not None else []
        self.schedule: str = schedule
        self.enabled: bool = enabled
        self.last_run: datetime | None = last_run
        self.next_run: datetime | None = next_run
        self.status: WorkflowStatus = status
        self.created_at: datetime = created_at or datetime.now(timezone.utc)

    def add_step(self, step: WorkflowStep) -> None:
        """Append a step and re-order the list."""
        self.steps.append(step)
        self.steps.sort(key=lambda s: s.order)

    def remove_step(self, step_id: str) -> None:
        """Remove a step by its ID."""
        self.steps = [s for s in self.steps if s.id != step_id]

    def reorder_steps(self) -> None:
        """Re-sort steps by their ``order`` attribute."""
        self.steps.sort(key=lambda s: s.order)

    def get_step(self, step_id: str) -> WorkflowStep | None:
        """Look up a step by its ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def mark_running(self) -> None:
        """Transition the workflow to the running state."""
        self.status = WorkflowStatus.RUNNING

    def mark_completed(self) -> None:
        """Transition the workflow to the completed state."""
        self.status = WorkflowStatus.COMPLETED
        self.last_run = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        """Transition the workflow to the failed state."""
        self.status = WorkflowStatus.FAILED
        self.last_run = datetime.now(timezone.utc)

    def enable(self) -> None:
        """Enable this workflow."""
        self.enabled = True

    def disable(self) -> None:
        """Disable this workflow."""
        self.enabled = False

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "workflow_type": self.workflow_type,
            "steps": [s.to_dict() for s in self.steps],
            "schedule": self.schedule,
            "enabled": self.enabled,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }


class WorkflowRun:
    """A single execution record for an automation workflow."""

    def __init__(
        self,
        id: str | None = None,
        workflow_id: str = "",
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        status: str = "pending",
        results: list[dict] | None = None,
        errors: list[str] | None = None,
    ) -> None:
        self.id: str = id or str(uuid.uuid4())
        self.workflow_id: str = workflow_id
        self.started_at: datetime = started_at or datetime.now(timezone.utc)
        self.ended_at: datetime | None = ended_at
        self.status: str = status
        self.results: list[dict] = results if results is not None else []
        self.errors: list[str] = errors if errors is not None else []

    def finish(self, status: str = "completed") -> None:
        """Mark the run as finished."""
        self.status = status
        self.ended_at = datetime.now(timezone.utc)

    def add_result(self, result: dict) -> None:
        """Append a step result."""
        self.results.append(result)

    def add_error(self, error: str) -> None:
        """Record an error that occurred during execution."""
        self.errors.append(error)

    @property
    def duration_seconds(self) -> float:
        """Calculate elapsed time in seconds."""
        if self.ended_at is None:
            return 0.0
        delta = self.ended_at - self.started_at
        return delta.total_seconds()

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "status": self.status,
            "results": list(self.results),
            "errors": list(self.errors),
            "duration_seconds": self.duration_seconds,
        }
