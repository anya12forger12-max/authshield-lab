"""Sustainability domain entities for long-term platform health tracking."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SustainabilityMetric:
    """A single sustainability measurement."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = ""
    score: float = 0.0
    max_score: float = 100.0
    trend: str = "stable"
    last_checked: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def percentage(self) -> float:
        """Return the score as a percentage of max_score."""
        if self.max_score == 0:
            return 0.0
        return min(100.0, (self.score / self.max_score) * 100.0)

    def is_healthy(self, threshold: float = 70.0) -> bool:
        """Return True if the score percentage exceeds the threshold."""
        return self.percentage() >= threshold

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": round(self.percentage(), 2),
            "trend": self.trend,
            "last_checked": self.last_checked.isoformat(),
        }


@dataclass
class TechnicalDebtItem:
    """A tracked piece of technical debt."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: str = ""
    description: str = ""
    severity: str = "low"
    estimated_hours: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False
    resolved_at: datetime | None = None

    def resolve(self) -> None:
        """Mark this debt item as resolved."""
        self.resolved = True
        self.resolved_at = datetime.now(timezone.utc)

    def reopen(self) -> None:
        """Reopen a resolved debt item."""
        self.resolved = False
        self.resolved_at = None

    def age_days(self) -> float:
        """Return the number of days since this item was created."""
        delta = datetime.now(timezone.utc) - self.created_at
        return delta.total_seconds() / 86400.0

    def is_stale(self, days: int = 90) -> bool:
        """Return True if the unresolved item is older than *days*."""
        return not self.resolved and self.age_days() > days

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "description": self.description,
            "severity": self.severity,
            "estimated_hours": self.estimated_hours,
            "created_at": self.created_at.isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "age_days": round(self.age_days(), 1),
        }


@dataclass
class DependencyHealth:
    """Health status of a single dependency."""

    name: str = ""
    current_version: str = ""
    latest_version: str = ""
    age_days: int = 0
    vulnerabilities: int = 0
    license: str = ""
    update_available: bool = False

    def is_outdated(self) -> bool:
        """Return True if an update is available."""
        return self.update_available

    def has_vulnerabilities(self) -> bool:
        """Return True if any known vulnerabilities exist."""
        return self.vulnerabilities > 0

    def risk_score(self) -> float:
        """Compute a 0-10 risk score (10 = highest risk)."""
        score = 0.0
        if self.vulnerabilities > 0:
            score += min(5.0, float(self.vulnerabilities) * 2.0)
        if self.update_available:
            score += 1.0
        if self.age_days > 365:
            score += 1.0
        if self.license in ("GPL-3.0", "AGPL-3.0", "SSPL-1.0"):
            score += 1.0
        return min(10.0, score)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "age_days": self.age_days,
            "vulnerabilities": self.vulnerabilities,
            "license": self.license,
            "update_available": self.update_available,
            "risk_score": round(self.risk_score(), 2),
        }


@dataclass
class APIStabilityMetric:
    """Stability metric for the platform's API surface."""

    version: str = ""
    endpoints_total: int = 0
    deprecated: int = 0
    breaking_changes: int = 0
    stability_score: float = 100.0

    def calculate_score(self) -> float:
        """Compute a stability score from endpoint statistics."""
        if self.endpoints_total == 0:
            self.stability_score = 100.0
            return self.stability_score
        dep_ratio = self.deprecated / self.endpoints_total
        break_ratio = self.breaking_changes / self.endpoints_total
        self.stability_score = max(0.0, 100.0 - (dep_ratio * 30.0) - (break_ratio * 70.0))
        return round(self.stability_score, 2)

    def deprecation_rate(self) -> float:
        """Return the fraction of deprecated endpoints."""
        if self.endpoints_total == 0:
            return 0.0
        return self.deprecated / self.endpoints_total

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "endpoints_total": self.endpoints_total,
            "deprecated": self.deprecated,
            "breaking_changes": self.breaking_changes,
            "stability_score": self.stability_score,
            "deprecation_rate": round(self.deprecation_rate(), 4),
        }


@dataclass
class LocalizationHealth:
    """Localization completeness for a single language."""

    language: str = ""
    completeness: float = 0.0
    missing_keys: int = 0
    total_keys: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def completeness_pct(self) -> float:
        """Return completeness as a percentage."""
        if self.total_keys == 0:
            return 0.0
        return (self.completeness) * 100.0

    def is_complete(self, threshold: float = 0.95) -> bool:
        """Return True if completeness exceeds the threshold (0-1 scale)."""
        return self.completeness >= threshold

    def to_dict(self) -> dict:
        return {
            "language": self.language,
            "completeness": self.completeness,
            "completeness_pct": round(self.completeness_pct(), 2),
            "missing_keys": self.missing_keys,
            "total_keys": self.total_keys,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class MaintenanceItem:
    """A single item in a maintenance plan."""

    description: str = ""
    category: str = ""
    effort_hours: float = 0.0
    status: str = "pending"
    assignee: str = ""

    def complete(self) -> None:
        """Mark this item as completed."""
        self.status = "completed"

    def start(self) -> None:
        """Mark this item as in-progress."""
        self.status = "in_progress"

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "category": self.category,
            "effort_hours": self.effort_hours,
            "status": self.status,
            "assignee": self.assignee,
        }


@dataclass
class MaintenancePlan:
    """A scheduled maintenance plan with items."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    items: list[MaintenanceItem] = field(default_factory=list)
    priority: str = "medium"
    estimated_hours: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    target_date: str = ""

    def add_item(self, item: MaintenanceItem) -> None:
        """Add an item and recalculate estimated hours."""
        self.items.append(item)
        self._recalculate_hours()

    def remove_item(self, index: int) -> bool:
        """Remove an item by index. Return True if removed."""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self._recalculate_hours()
            return True
        return False

    def _recalculate_hours(self) -> None:
        """Sum effort hours from all items."""
        self.estimated_hours = sum(i.effort_hours for i in self.items)

    def completed_count(self) -> int:
        """Return the number of completed items."""
        return len([i for i in self.items if i.status == "completed"])

    def progress_pct(self) -> float:
        """Return the completion percentage."""
        if not self.items:
            return 0.0
        return (self.completed_count() / len(self.items)) * 100.0

    def is_overdue(self) -> bool:
        """Return True if the target date has passed."""
        if not self.target_date:
            return False
        try:
            target = datetime.fromisoformat(self.target_date)
            return datetime.now(timezone.utc) > target
        except ValueError:
            return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "items": [i.to_dict() for i in self.items],
            "priority": self.priority,
            "estimated_hours": self.estimated_hours,
            "created_at": self.created_at.isoformat(),
            "target_date": self.target_date,
            "completed_count": self.completed_count(),
            "progress_pct": round(self.progress_pct(), 2),
        }


@dataclass
class SustainabilityDashboard:
    """Aggregated sustainability health snapshot."""

    debt_items: int = 0
    dependency_health: float = 0.0
    api_stability: float = 0.0
    localization_health: float = 0.0
    a11y_compliance: float = 0.0
    test_coverage: float = 0.0
    doc_freshness: float = 0.0
    overall_score: float = 0.0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def calculate_overall(self) -> float:
        """Compute the weighted overall score."""
        weights = {
            "debt": 0.15,
            "dep_health": 0.15,
            "api": 0.15,
            "i18n": 0.10,
            "a11y": 0.15,
            "test": 0.15,
            "doc": 0.15,
        }
        debt_score = max(0.0, 100.0 - self.debt_items * 5.0)
        self.overall_score = (
            debt_score * weights["debt"]
            + self.dependency_health * weights["dep_health"]
            + self.api_stability * weights["api"]
            + self.localization_health * weights["i18n"]
            + self.a11y_compliance * weights["a11y"]
            + self.test_coverage * weights["test"]
            + self.doc_freshness * weights["doc"]
        )
        return round(self.overall_score, 2)

    def health_label(self) -> str:
        """Return a human-readable health label."""
        score = self.overall_score or self.calculate_overall()
        if score >= 80:
            return "healthy"
        if score >= 60:
            return "fair"
        return "needs_attention"

    def to_dict(self) -> dict:
        return {
            "debt_items": self.debt_items,
            "dependency_health": self.dependency_health,
            "api_stability": self.api_stability,
            "localization_health": self.localization_health,
            "a11y_compliance": self.a11y_compliance,
            "test_coverage": self.test_coverage,
            "doc_freshness": self.doc_freshness,
            "overall_score": self.overall_score or self.calculate_overall(),
            "health_label": self.health_label(),
            "generated_at": self.generated_at.isoformat(),
        }
