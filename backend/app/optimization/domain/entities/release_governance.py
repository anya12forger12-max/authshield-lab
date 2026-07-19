"""Release governance domain entities for managing release workflows."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ReleaseStage(str, Enum):
    """Stages in the release workflow pipeline."""

    PLANNING = "planning"
    DEVELOPMENT = "development"
    REVIEW = "review"
    A11Y_VALIDATION = "a11y_validation"
    SECURITY_VALIDATION = "security_validation"
    PERF_VALIDATION = "perf_validation"
    DOC_REVIEW = "doc_review"
    LOCALIZATION_REVIEW = "localization_review"
    APPROVAL = "approval"
    PACKAGING = "packaging"
    DISTRIBUTION = "distribution"
    LTS = "lts"


@dataclass
class ReleaseWorkflow:
    """Tracks a release through its lifecycle stages."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    version: str = ""
    current_stage: ReleaseStage = ReleaseStage.PLANNING
    stage_history: list[dict] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    def advance(self, notes: str = "") -> ReleaseStage:
        """Move to the next stage in the pipeline."""
        stages = list(ReleaseStage)
        current_idx = stages.index(self.current_stage)
        if current_idx < len(stages) - 1:
            self.stage_history.append({
                "stage": self.current_stage.value,
                "exited_at": datetime.now(timezone.utc).isoformat(),
                "notes": notes,
            })
            self.current_stage = stages[current_idx + 1]
        return self.current_stage

    def is_complete(self) -> bool:
        """Return True if the workflow has reached the final stage."""
        return self.current_stage == ReleaseStage.DISTRIBUTION or self.completed_at is not None

    def complete(self) -> None:
        """Mark the workflow as completed."""
        self.completed_at = datetime.now(timezone.utc)

    def progress_pct(self) -> float:
        """Return how far along the workflow is (0-100)."""
        stages = list(ReleaseStage)
        current_idx = stages.index(self.current_stage)
        return round((current_idx / (len(stages) - 1)) * 100.0, 1)

    def stages_remaining(self) -> list[str]:
        """Return the names of stages not yet completed."""
        stages = list(ReleaseStage)
        current_idx = stages.index(self.current_stage)
        return [s.value for s in stages[current_idx + 1:]]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "release_id": self.release_id,
            "version": self.version,
            "current_stage": self.current_stage.value,
            "stage_history": list(self.stage_history),
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress_pct": self.progress_pct(),
            "stages_remaining": self.stages_remaining(),
        }


@dataclass
class ReleaseApproval:
    """A single approval record for a release stage."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    stage: ReleaseStage = ReleaseStage.PLANNING
    approver: str = ""
    approved: bool = False
    comments: str = ""
    approved_at: datetime | None = None

    def approve(self, comments: str = "") -> None:
        """Record approval."""
        self.approved = True
        self.comments = comments or self.comments
        self.approved_at = datetime.now(timezone.utc)

    def reject(self, comments: str = "") -> None:
        """Record rejection."""
        self.approved = False
        self.comments = comments or self.comments

    def is_pending(self) -> bool:
        """Return True if this approval has not been decided yet."""
        return self.approved_at is None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "stage": self.stage.value,
            "approver": self.approver,
            "approved": self.approved,
            "comments": self.comments,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }


@dataclass
class ReleaseGate:
    """A quality gate that must pass before a release can proceed."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    gate_type: str = ""
    required: bool = True
    passed: bool = False
    evidence: str = ""
    checked_at: datetime | None = None

    def check(self, passed: bool, evidence: str = "") -> None:
        """Record the gate check result."""
        self.passed = passed
        self.evidence = evidence or self.evidence
        self.checked_at = datetime.now(timezone.utc)

    def is_blocking(self) -> bool:
        """Return True if this gate is required and has not yet passed."""
        return self.required and not self.passed

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "release_id": self.release_id,
            "gate_type": self.gate_type,
            "required": self.required,
            "passed": self.passed,
            "evidence": self.evidence,
            "checked_at": self.checked_at.isoformat() if self.checked_at else None,
        }


@dataclass
class ReleaseChecklistItem:
    """A single item on the release checklist."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_id: str = ""
    item: str = ""
    category: str = ""
    completed: bool = False
    assignee: str = ""
    due_date: str = ""
    completed_at: datetime | None = None

    def complete(self) -> None:
        """Mark this checklist item as done."""
        self.completed = True
        self.completed_at = datetime.now(timezone.utc)

    def uncomplete(self) -> None:
        """Mark this checklist item as not done."""
        self.completed = False
        self.completed_at = None

    def is_overdue(self) -> bool:
        """Return True if the due date has passed and item is not complete."""
        if self.completed or not self.due_date:
            return False
        try:
            due = datetime.fromisoformat(self.due_date)
            return datetime.now(timezone.utc) > due
        except ValueError:
            return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "release_id": self.release_id,
            "item": self.item,
            "category": self.category,
            "completed": self.completed,
            "assignee": self.assignee,
            "due_date": self.due_date,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
