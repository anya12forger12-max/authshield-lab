"""Sustainability service — metrics, debt tracking, dependencies, maintenance."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.sustainability import (
    DependencyHealth,
    LocalizationHealth,
    MaintenanceItem,
    MaintenancePlan,
    SustainabilityDashboard,
    SustainabilityMetric,
    TechnicalDebtItem,
)
from ..domain.events.optimization_events import SustainabilityReportGenerated
from ..domain.interfaces.optimization_interfaces import ISustainabilityRepository

logger = logging.getLogger(__name__)


class SustainabilityService:
    """Tracks sustainability metrics, technical debt, and maintenance plans."""

    def __init__(self, repo: ISustainabilityRepository) -> None:
        self._repo = repo

    # ------------------------------------------------------------------
    # Sustainability Metrics
    # ------------------------------------------------------------------

    def create_metric(self, data: dict[str, Any]) -> dict[str, Any]:
        metric = SustainabilityMetric(
            name=data.get("name", ""),
            category=data.get("category", ""),
            score=float(data.get("score", 0.0)),
            max_score=float(data.get("max_score", 100.0)),
            trend=data.get("trend", "stable"),
        )
        return self._repo.create_metric(metric.to_dict())

    def get_metric(self, metric_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_metric_by_id(metric_id)

    def list_metrics(self) -> list[dict[str, Any]]:
        return self._repo.get_all_metrics()

    def update_metric(self, metric_id: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        return self._repo.update_metric(metric_id, data)

    def delete_metric(self, metric_id: str) -> bool:
        return self._repo.delete_metric(metric_id)

    # ------------------------------------------------------------------
    # Technical Debt
    # ------------------------------------------------------------------

    def create_debt_item(self, data: dict[str, Any]) -> dict[str, Any]:
        item = TechnicalDebtItem(
            category=data.get("category", ""),
            description=data.get("description", ""),
            severity=data.get("severity", "low"),
            estimated_hours=float(data.get("estimated_hours", 0.0)),
        )
        return self._repo.create_debt_item(item.to_dict())

    def get_debt_item(self, item_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_debt_item_by_id(item_id)

    def list_debt_items(self, resolved: Optional[bool] = None) -> list[dict[str, Any]]:
        return self._repo.get_all_debt_items(resolved=resolved)

    def resolve_debt_item(self, item_id: str) -> Optional[dict[str, Any]]:
        item = self._repo.get_debt_item_by_id(item_id)
        if not item:
            return None
        return self._repo.update_debt_item(item_id, {
            "resolved": True,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        })

    def reopen_debt_item(self, item_id: str) -> Optional[dict[str, Any]]:
        item = self._repo.get_debt_item_by_id(item_id)
        if not item:
            return None
        return self._repo.update_debt_item(item_id, {
            "resolved": False,
            "resolved_at": None,
        })

    def delete_debt_item(self, item_id: str) -> bool:
        return self._repo.delete_debt_item(item_id)

    def debt_summary(self) -> dict[str, Any]:
        all_items = self._repo.get_all_debt_items()
        unresolved = [i for i in all_items if not i.get("resolved", False)]
        total_hours = sum(float(i.get("estimated_hours", 0)) for i in unresolved)
        by_severity: dict[str, int] = {}
        for item in unresolved:
            sev = item.get("severity", "low")
            by_severity[sev] = by_severity.get(sev, 0) + 1
        return {
            "total_items": len(all_items),
            "unresolved_items": len(unresolved),
            "total_estimated_hours": total_hours,
            "by_severity": by_severity,
        }

    # ------------------------------------------------------------------
    # Dependency Health
    # ------------------------------------------------------------------

    def assess_dependency(self, data: dict[str, Any]) -> dict[str, Any]:
        dep = DependencyHealth(
            name=data.get("name", ""),
            current_version=data.get("current_version", ""),
            latest_version=data.get("latest_version", ""),
            age_days=int(data.get("age_days", 0)),
            vulnerabilities=int(data.get("vulnerabilities", 0)),
            license=data.get("license", ""),
            update_available=data.get("update_available", False),
        )
        return dep.to_dict()

    def assess_dependencies(self, dependencies: list[dict[str, Any]]) -> dict[str, Any]:
        results = [self.assess_dependency(d) for d in dependencies]
        total_risk = sum(r.get("risk_score", 0) for r in results)
        avg_risk = total_risk / len(results) if results else 0.0
        vulnerable_count = sum(1 for r in results if r.get("vulnerabilities", 0) > 0)
        return {
            "dependencies": results,
            "total_count": len(results),
            "vulnerable_count": vulnerable_count,
            "average_risk_score": round(avg_risk, 2),
        }

    # ------------------------------------------------------------------
    # API Stability
    # ------------------------------------------------------------------

    def assess_api_stability(self, data: dict[str, Any]) -> dict[str, Any]:
        endpoints_total = int(data.get("endpoints_total", 0))
        deprecated = int(data.get("deprecated", 0))
        breaking_changes = int(data.get("breaking_changes", 0))
        if endpoints_total == 0:
            score = 100.0
        else:
            dep_ratio = deprecated / endpoints_total
            break_ratio = breaking_changes / endpoints_total
            score = max(0.0, 100.0 - (dep_ratio * 30.0) - (break_ratio * 70.0))
        return {
            "version": data.get("version", ""),
            "endpoints_total": endpoints_total,
            "deprecated": deprecated,
            "breaking_changes": breaking_changes,
            "stability_score": round(score, 2),
        }

    # ------------------------------------------------------------------
    # Localization Health
    # ------------------------------------------------------------------

    def assess_localization(self, data: dict[str, Any]) -> dict[str, Any]:
        health = LocalizationHealth(
            language=data.get("language", ""),
            completeness=float(data.get("completeness", 0.0)),
            missing_keys=int(data.get("missing_keys", 0)),
            total_keys=int(data.get("total_keys", 0)),
        )
        return health.to_dict()

    # ------------------------------------------------------------------
    # Maintenance Plans
    # ------------------------------------------------------------------

    def create_maintenance_plan(self, data: dict[str, Any]) -> dict[str, Any]:
        plan = MaintenancePlan(
            title=data.get("title", ""),
            priority=data.get("priority", "medium"),
            target_date=data.get("target_date", ""),
        )
        for item_data in data.get("items", []):
            item = MaintenanceItem(
                description=item_data.get("description", ""),
                category=item_data.get("category", ""),
                effort_hours=float(item_data.get("effort_hours", 0.0)),
                assignee=item_data.get("assignee", ""),
            )
            plan.add_item(item)
        return self._repo.create_metric({"plan_data": plan.to_dict(), "type": "maintenance_plan"})

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def generate_dashboard(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        data = data or {}
        debt_items = self._repo.get_all_debt_items(resolved=False)

        dashboard = SustainabilityDashboard(
            debt_items=len(debt_items),
            dependency_health=float(data.get("dependency_health", 75.0)),
            api_stability=float(data.get("api_stability", 85.0)),
            localization_health=float(data.get("localization_health", 80.0)),
            a11y_compliance=float(data.get("a11y_compliance", 70.0)),
            test_coverage=float(data.get("test_coverage", 75.0)),
            doc_freshness=float(data.get("doc_freshness", 65.0)),
        )
        dashboard.calculate_overall()

        event = SustainabilityReportGenerated(
            overall_score=dashboard.overall_score,
            health_label=dashboard.health_label(),
        )
        logger.info(
            "sustainability_dashboard_generated",
            extra={"overall_score": dashboard.overall_score, "event_id": event.event_id},
        )
        return dashboard.to_dict()
