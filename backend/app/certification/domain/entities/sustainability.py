"""Sustainability domain entities: dependency lifecycle, API stability, ownership, docs freshness."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class DependencyStatus(str, Enum):
    """Lifecycle status for a tracked dependency."""

    SUPPORTED = "supported"
    DEPRECATED = "deprecated"
    END_OF_LIFE = "end_of_life"


@dataclass
class DependencyLifecycle:
    """Tracks the lifecycle health of a single dependency."""

    name: str = ""
    version: str = ""
    end_of_life_date: str | None = None
    status: DependencyStatus = DependencyStatus.SUPPORTED
    update_available: bool = False
    latest_version: str = ""

    def is_active(self) -> bool:
        """Return ``True`` when the dependency is still supported."""
        return self.status == DependencyStatus.SUPPORTED

    def needs_action(self) -> bool:
        """Return ``True`` when an update is available or the dep is deprecated."""
        return self.update_available or self.status != DependencyStatus.SUPPORTED

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "end_of_life_date": self.end_of_life_date,
            "status": self.status.value,
            "update_available": self.update_available,
            "latest_version": self.latest_version,
        }


@dataclass
class APIStabilityReport:
    """Summary of API surface stability for a given version."""

    version: str = ""
    endpoints: int = 0
    deprecated: int = 0
    breaking_changes: int = 0
    stability_score: float = 100.0

    def recalculate_score(self) -> float:
        """Recompute ``stability_score`` from the endpoint counts."""
        if self.endpoints <= 0:
            self.stability_score = 100.0
            return self.stability_score
        penalty = (self.deprecated * 0.5) + (self.breaking_changes * 2.0)
        raw = max(0.0, 100.0 - penalty)
        self.stability_score = min(raw, 100.0)
        return self.stability_score

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "version": self.version,
            "endpoints": self.endpoints,
            "deprecated": self.deprecated,
            "breaking_changes": self.breaking_changes,
            "stability_score": self.stability_score,
        }


@dataclass
class ModuleOwnership:
    """Records who owns a module and its last health review date."""

    module: str = ""
    owner: str = ""
    last_reviewed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    health: float = 100.0

    def needs_review(self, max_days: int = 30) -> bool:
        """Return ``True`` if the last review is older than *max_days*."""
        delta = datetime.now(timezone.utc) - self.last_reviewed
        return delta.days > max_days

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "module": self.module,
            "owner": self.owner,
            "last_reviewed": self.last_reviewed.isoformat(),
            "health": self.health,
        }


@dataclass
class DocumentationFreshness:
    """Tracks how stale documentation is for a component."""

    component: str = ""
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    days_stale: int = 0
    status: str = "fresh"

    def recalculate(self) -> None:
        """Recompute ``days_stale`` and ``status`` from ``last_updated``."""
        delta = datetime.now(timezone.utc) - self.last_updated
        self.days_stale = delta.days
        if self.days_stale <= 7:
            self.status = "fresh"
        elif self.days_stale <= 30:
            self.status = "aging"
        elif self.days_stale <= 90:
            self.status = "stale"
        else:
            self.status = "critical"

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "component": self.component,
            "last_updated": self.last_updated.isoformat(),
            "days_stale": self.days_stale,
            "status": self.status,
        }


@dataclass
class SustainabilityDashboard:
    """Aggregated sustainability view across the entire platform."""

    dependencies: list[DependencyLifecycle] = field(default_factory=list)
    api_stability: APIStabilityReport = field(default_factory=APIStabilityReport)
    ownership: list[ModuleOwnership] = field(default_factory=list)
    documentation: list[DocumentationFreshness] = field(default_factory=list)
    technical_debt_hours: float = 0.0
    maintenance_score: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def compute_maintenance_score(self) -> float:
        """Derive a 0-100 score from dependency health and doc freshness."""
        dep_score = 100.0
        if self.dependencies:
            supported = sum(1 for d in self.dependencies if d.is_active())
            dep_score = (supported / len(self.dependencies)) * 100.0

        doc_score = 100.0
        if self.documentation:
            fresh = sum(1 for d in self.documentation if d.status in ("fresh", "aging"))
            doc_score = (fresh / len(self.documentation)) * 100.0

        api_score = self.api_stability.stability_score
        self.maintenance_score = (dep_score + doc_score + api_score) / 3.0
        return self.maintenance_score

    def deprecated_dependencies(self) -> list[DependencyLifecycle]:
        """Return dependencies that are deprecated or end-of-life."""
        return [d for d in self.dependencies if not d.is_active()]

    def stale_docs(self) -> list[DocumentationFreshness]:
        """Return documentation entries marked stale or critical."""
        return [d for d in self.documentation if d.status in ("stale", "critical")]

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "dependencies": [d.to_dict() for d in self.dependencies],
            "api_stability": self.api_stability.to_dict(),
            "ownership": [o.to_dict() for o in self.ownership],
            "documentation": [d.to_dict() for d in self.documentation],
            "technical_debt_hours": self.technical_debt_hours,
            "maintenance_score": self.maintenance_score,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class RoadmapItem:
    """A single item on the maintenance roadmap."""

    description: str = ""
    category: str = ""
    effort_hours: float = 0.0
    status: str = "planned"
    target_date: str = ""

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "description": self.description,
            "category": self.category,
            "effort_hours": self.effort_hours,
            "status": self.status,
            "target_date": self.target_date,
        }


@dataclass
class MaintenanceRoadmap:
    """Ordered list of planned maintenance work items."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    items: list[RoadmapItem] = field(default_factory=list)
    priority: str = "medium"
    estimated_hours: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def recalculate_hours(self) -> float:
        """Sum effort across all items."""
        self.estimated_hours = sum(i.effort_hours for i in self.items)
        return self.estimated_hours

    def items_by_status(self, status: str) -> list[RoadmapItem]:
        """Filter items by their ``status`` field."""
        return [i for i in self.items if i.status == status]

    def add_item(self, item: RoadmapItem) -> None:
        """Append a roadmap item and refresh estimated hours."""
        self.items.append(item)
        self.recalculate_hours()

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "items": [i.to_dict() for i in self.items],
            "priority": self.priority,
            "estimated_hours": self.estimated_hours,
            "created_at": self.created_at.isoformat(),
        }
