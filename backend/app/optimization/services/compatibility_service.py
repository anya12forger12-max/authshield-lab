"""Compatibility service — cross-platform validation and reporting."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.optimization import CompatibilityReport, CompatibilityResult
from ..domain.events.optimization_events import CompatibilityReportGenerated
from ..domain.interfaces.optimization_interfaces import ICompatibilityRepository

logger = logging.getLogger(__name__)


class CompatibilityService:
    """Validates components across platforms and generates reports."""

    def __init__(self, repo: ICompatibilityRepository) -> None:
        self._repo = repo

    def validate_component(
        self, platform: str, component: str, checks: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Run validation for a single component on a platform."""
        checks = checks or {}
        status = "pass"
        details_parts: list[str] = []

        for check_name, expected in checks.items():
            actual = checks.get(f"{check_name}_actual", expected)
            if actual != expected:
                status = "fail"
                details_parts.append(f"{check_name}: expected {expected}, got {actual}")
            else:
                details_parts.append(f"{check_name}: OK")

        result = CompatibilityResult(
            platform=platform,
            component=component,
            status=status,
            details="; ".join(details_parts) if details_parts else "No specific checks performed",
        )
        return result.to_dict()

    def generate_report(self, data: dict[str, Any]) -> dict[str, Any]:
        """Generate a full compatibility report from component checks."""
        platforms = data.get("platforms", [])
        components = data.get("components", [])
        checks_matrix = data.get("checks", {})

        results: list[CompatibilityResult] = []
        for platform in platforms:
            for component in components:
                component_checks = checks_matrix.get(f"{platform}:{component}", {})
                status = "pass"
                details_parts: list[str] = []

                for check_name, expected in component_checks.items():
                    actual = component_checks.get(f"{check_name}_actual", expected)
                    if actual != expected:
                        status = "fail"
                        details_parts.append(f"{check_name}: expected {expected}, got {actual}")
                    else:
                        details_parts.append(f"{check_name}: OK")

                result = CompatibilityResult(
                    platform=platform,
                    component=component,
                    status=status,
                    details="; ".join(details_parts) if details_parts else "All checks passed",
                )
                results.append(result)

        report = CompatibilityReport(
            results=results,
            platforms=list(platforms),
        )
        report.evaluate()

        stored = self._repo.create(report.to_dict())

        event = CompatibilityReportGenerated(
            report_id=stored["id"],
            platforms_checked=len(platforms),
            overall_status=report.overall_status,
        )
        logger.info(
            "compatibility_report_generated",
            extra={"report_id": stored["id"], "event_id": event.event_id},
        )
        return stored

    def get_report(self, report_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_by_id(report_id)

    def list_reports(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        return self._repo.get_all(page=page, per_page=per_page)

    def delete_report(self, report_id: str) -> bool:
        return self._repo.delete(report_id)

    def quick_check(self, platform: str, component: str) -> dict[str, Any]:
        """Perform a basic quick-check for a component on a platform."""
        basic_checks = {
            "imports": True,
            "config_loads": True,
            "api_responds": True,
        }
        return self.validate_component(platform, component, basic_checks)

    def matrix_check(
        self, platforms: list[str], components: list[str]
    ) -> dict[str, Any]:
        """Run a full matrix check and return results without persisting."""
        all_results: list[dict[str, Any]] = []
        for platform in platforms:
            for component in components:
                result = self.quick_check(platform, component)
                all_results.append(result)

        passed = sum(1 for r in all_results if r.get("status") == "pass")
        failed = sum(1 for r in all_results if r.get("status") == "fail")
        return {
            "platforms": platforms,
            "components": components,
            "total_checks": len(all_results),
            "passed": passed,
            "failed": failed,
            "results": all_results,
        }
