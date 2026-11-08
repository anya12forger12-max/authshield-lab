"""Accessibility analytics service – compliance trends, improvement plans."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ..domain.entities.content_health import ContentHealthItem
from ..domain.interfaces import IContentHealthRepository

logger = get_logger("analytics.a11y_analytics_service")


class A11yAnalyticsService:
    """Tracks accessibility compliance trends and generates improvement plans.

    Parameters
    ----------
    content_health_repo:
        Repository for content health items (used for a11y data).
    """

    def __init__(self, content_health_repo: IContentHealthRepository) -> None:
        self._content_health_repo = content_health_repo

    async def get_a11y_overview(self) -> dict[str, Any]:
        """Compute an overview of accessibility compliance across all content."""
        items = await self._content_health_repo.get_all()
        if not items:
            return {
                "total_items": 0,
                "compliant": 0,
                "partial": 0,
                "non_compliant": 0,
                "unknown": 0,
                "compliance_pct": 0.0,
            }

        compliant = sum(1 for i in items if i.a11y_status == "compliant")
        partial = sum(1 for i in items if i.a11y_status == "partial")
        non_compliant = sum(1 for i in items if i.a11y_status == "non_compliant")
        unknown = sum(1 for i in items if i.a11y_status == "unknown")
        total = len(items)
        compliance_pct = (compliant / total * 100) if total > 0 else 0.0

        return {
            "total_items": total,
            "compliant": compliant,
            "partial": partial,
            "non_compliant": non_compliant,
            "unknown": unknown,
            "compliance_pct": round(compliance_pct, 2),
        }

    async def get_compliance_by_type(self) -> dict[str, dict[str, int]]:
        """Compute a11y compliance broken down by content type."""
        items = await self._content_health_repo.get_all()
        by_type: dict[str, dict[str, int]] = {}

        for item in items:
            ctype = item.content_type or "unknown"
            if ctype not in by_type:
                by_type[ctype] = {
                    "total": 0,
                    "compliant": 0,
                    "partial": 0,
                    "non_compliant": 0,
                    "unknown": 0,
                }
            by_type[ctype]["total"] += 1
            status = item.a11y_status
            if status in by_type[ctype]:
                by_type[ctype][status] += 1

        return by_type

    async def get_compliance_trend(self) -> list[dict[str, Any]]:
        """Compute compliance trend by reviewing items sorted by last reviewed."""
        items = await self._content_health_repo.get_all()
        items_sorted = sorted(items, key=lambda i: i.last_reviewed_days)

        trend: list[dict[str, Any]] = []
        cumulative_compliant = 0
        for idx, item in enumerate(items_sorted, start=1):
            if item.a11y_status == "compliant":
                cumulative_compliant += 1
            trend.append({
                "position": idx,
                "content_id": item.content_id,
                "a11y_status": item.a11y_status,
                "cumulative_compliance_pct": round(
                    (cumulative_compliant / idx) * 100, 2
                ),
            })

        return trend

    async def generate_improvement_plan(self) -> dict[str, Any]:
        """Generate an accessibility improvement plan based on current compliance."""
        items = await self._content_health_repo.get_all()
        overview = await self.get_a11y_overview()

        non_compliant_items = [
            {"content_id": i.content_id, "title": i.title, "content_type": i.content_type}
            for i in items
            if i.a11y_status in ("non_compliant", "partial")
        ]

        unknown_items = [
            {"content_id": i.content_id, "title": i.title}
            for i in items
            if i.a11y_status == "unknown"
        ]

        actions: list[dict[str, str]] = []

        if non_compliant_items:
            actions.append({
                "action": "Remediate non-compliant content",
                "priority": "high",
                "description": (
                    f"{len(non_compliant_items)} content items require accessibility remediation. "
                    "Focus on adding alt text, ensuring keyboard navigation, and improving contrast."
                ),
            })

        if unknown_items:
            actions.append({
                "action": "Audit unknown-status content",
                "priority": "medium",
                "description": (
                    f"{len(unknown_items)} content items have not been assessed for accessibility. "
                    "Run WCAG 2.1 AA compliance scans."
                ),
            })

        if overview["compliance_pct"] < 80.0:
            actions.append({
                "action": "Establish a11y review process",
                "priority": "high",
                "description": (
                    f"Current compliance is {overview['compliance_pct']:.1f}%, below 80% target. "
                    "Implement mandatory accessibility review before publication."
                ),
            })

        if not actions:
            actions.append({
                "action": "Maintain current standards",
                "priority": "low",
                "description": "Accessibility compliance is above target. Continue periodic audits.",
            })

        plan = {
            "id": str(uuid.uuid4()),
            "overview": overview,
            "non_compliant_count": len(non_compliant_items),
            "unknown_count": len(unknown_items),
            "actions": actions,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            "a11y_improvement_plan_generated",
            plan_id=plan["id"],
            compliance_pct=overview["compliance_pct"],
        )
        return plan

    async def get_item_a11y_detail(
        self, content_id: str
    ) -> Optional[dict[str, Any]]:
        """Get detailed a11y information for a specific content item."""
        item = await self._content_health_repo.get_by_content_id(content_id)
        if item is None:
            return None

        return {
            "content_id": item.content_id,
            "title": item.title,
            "content_type": item.content_type,
            "a11y_status": item.a11y_status,
            "doc_completeness": item.doc_completeness,
            "localization_status": item.localization_status,
            "missing_metadata": item.missing_metadata,
            "broken_refs": item.broken_refs,
            "last_reviewed_days": item.last_reviewed_days,
        }
