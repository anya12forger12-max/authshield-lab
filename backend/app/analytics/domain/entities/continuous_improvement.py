"""Continuous improvement domain entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ActionPlanStatus(str, Enum):
    """Lifecycle status of an action plan."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


@dataclass
class ActionPlan:
    """Improvement action plan."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    owner: str = ""
    status: ActionPlanStatus = ActionPlanStatus.NOT_STARTED
    target_date: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ActionPlanItem:
    """Individual item within an action plan."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    plan_id: str = ""
    description: str = ""
    status: str = "pending"
    evidence: list[str] = field(default_factory=list)
    review_date: str = ""


@dataclass
class ImprovementMetric:
    """A single tracked improvement metric."""

    name: str = ""
    current_value: float = 0.0
    target_value: float = 0.0
    trend: str = "stable"


@dataclass
class ImprovementInitiative:
    """A tracked improvement initiative."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    start_date: str = ""
    end_date: str = ""
    progress_pct: float = 0.0
    assignees: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


@dataclass
class ImprovementReport:
    """Periodic report on an improvement initiative."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    initiative_id: str = ""
    period: str = ""
    progress: float = 0.0
    findings: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class HistoricalComparison:
    """Compare metrics across two time periods."""

    period_a: str = ""
    period_b: str = ""
    metrics: dict[str, dict[str, float]] = field(default_factory=dict)
    changes: dict[str, float] = field(default_factory=dict)
