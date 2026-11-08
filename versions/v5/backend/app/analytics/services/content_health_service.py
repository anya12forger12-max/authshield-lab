"""Content health service – monitor content, generate health reports, maintenance schedules."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus
from ..domain.entities.content_health import (
    ContentHealthDashboard,
    ContentHealthItem,
    MaintenanceSchedule,
    MaintenanceScheduleItem,
)
from ..domain.interfaces import (
    IContentHealthDashboardRepository,
    IContentHealthRepository,
    IMaintenanceScheduleRepository,
)
from ..domain.events.analytics_events import ContentHealthChecked

logger = get_logger("analytics.content_health_service")


class ContentHealthService:
    """Monitors content health, generates reports, and schedules maintenance.

    Parameters
    ----------
    content_repo:
        Repository for content health items.
    dashboard_repo:
        Repository for content health dashboards.
    schedule_repo:
        Repository for maintenance schedules.
    event_bus:
        Optional event bus for domain events.
    """

    def __init__(
        self,
        content_repo: IContentHealthRepository,
        dashboard_repo: IContentHealthDashboardRepository,
        schedule_repo: IMaintenanceScheduleRepository,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._content_repo = content_repo
        self._dashboard_repo = dashboard_repo
        self._schedule_repo = schedule_repo
        self._event_bus = event_bus

    async def _publish_event(self, event: Any) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def add_content_item(
        self,
        content_id: str,
        content_type: str = "",
        title: str = "",
        version_status: str = "current",
        broken_refs: int = 0,
        missing_metadata: int = 0,
        doc_completeness: float = 0.0,
        localization_status: str = "incomplete",
        a11y_status: str = "unknown",
        last_reviewed_days: int = 0,
        publication_quality: float = 0.0,
        dependency_health: float = 0.0,
    ) -> ContentHealthItem:
        """Add or update a content health item."""
        existing = await self._content_repo.get_by_content_id(content_id)
        if existing is not None:
            updated = await self._content_repo.update(existing.id, {
                "content_type": content_type,
                "title": title,
                "version_status": version_status,
                "broken_refs": broken_refs,
                "missing_metadata": missing_metadata,
                "doc_completeness": doc_completeness,
                "localization_status": localization_status,
                "a11y_status": a11y_status,
                "last_reviewed_days": last_reviewed_days,
                "publication_quality": publication_quality,
                "dependency_health": dependency_health,
            })
            return updated if updated else existing

        item = ContentHealthItem(
            id=str(uuid.uuid4()),
            content_id=content_id,
            content_type=content_type,
            title=title,
            version_status=version_status,
            broken_refs=broken_refs,
            missing_metadata=missing_metadata,
            doc_completeness=doc_completeness,
            localization_status=localization_status,
            a11y_status=a11y_status,
            last_reviewed_days=last_reviewed_days,
            publication_quality=publication_quality,
            dependency_health=dependency_health,
        )
        created = await self._content_repo.create(item)
        logger.info("content_health_item_added", content_id=content_id)
        return created

    async def get_content_item(self, content_id: str) -> Optional[ContentHealthItem]:
        """Retrieve a content health item by content ID."""
        return await self._content_repo.get_by_content_id(content_id)

    async def list_all_items(self) -> list[ContentHealthItem]:
        """List all tracked content health items."""
        return await self._content_repo.get_all()

    async def generate_health_dashboard(self) -> ContentHealthDashboard:
        """Generate an aggregated content health dashboard."""
        items = await self._content_repo.get_all()

        healthy = 0
        needs_attention = 0
        critical = 0
        by_type: dict[str, int] = {}

        for item in items:
            ctype = item.content_type or "unknown"
            by_type[ctype] = by_type.get(ctype, 0) + 1

            score = self._compute_health_score(item)
            if score >= 80.0:
                healthy += 1
            elif score >= 50.0:
                needs_attention += 1
            else:
                critical += 1

        dashboard = ContentHealthDashboard(
            id=str(uuid.uuid4()),
            total_items=len(items),
            healthy=healthy,
            needs_attention=needs_attention,
            critical=critical,
            by_type=by_type,
            generated_at=datetime.now(timezone.utc),
        )

        await self._dashboard_repo.create(dashboard)
        logger.info(
            "content_health_dashboard_generated",
            dashboard_id=dashboard.id,
            total_items=len(items),
            healthy=healthy,
            needs_attention=needs_attention,
            critical=critical,
        )

        await self._publish_event(
            ContentHealthChecked(
                dashboard_id=dashboard.id,
                module="analytics",
            )
        )

        return dashboard

    async def get_latest_dashboard(self) -> Optional[ContentHealthDashboard]:
        """Retrieve the most recent content health dashboard."""
        return await self._dashboard_repo.get_latest()

    async def generate_maintenance_schedule(self) -> MaintenanceSchedule:
        """Generate a prioritized maintenance schedule for content items."""
        items = await self._content_repo.get_all()
        schedule_items: list[MaintenanceScheduleItem] = []

        for item in items:
            actions = self._determine_maintenance_actions(item)
            for action, priority in actions:
                schedule_items.append(MaintenanceScheduleItem(
                    content_id=item.content_id,
                    title=item.title,
                    action=action,
                    priority=priority,
                    due_date=self._compute_due_date(priority),
                ))

        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        schedule_items.sort(key=lambda s: priority_order.get(s.priority, 4))

        schedule = MaintenanceSchedule(
            id=str(uuid.uuid4()),
            items=schedule_items,
            generated_at=datetime.now(timezone.utc),
        )

        await self._schedule_repo.create(schedule)
        logger.info(
            "maintenance_schedule_generated",
            schedule_id=schedule.id,
            item_count=len(schedule_items),
        )

        return schedule

    async def get_maintenance_schedules(self) -> list[MaintenanceSchedule]:
        """Retrieve all generated maintenance schedules."""
        return await self._schedule_repo.get_all()

    async def get_items_needing_attention(self) -> list[ContentHealthItem]:
        """Retrieve content items that need attention."""
        items = await self._content_repo.get_all()
        return [
            item for item in items
            if self._compute_health_score(item) < 80.0
        ]

    async def get_critical_items(self) -> list[ContentHealthItem]:
        """Retrieve critically unhealthy content items."""
        items = await self._content_repo.get_all()
        return [
            item for item in items
            if self._compute_health_score(item) < 50.0
        ]

    def _compute_health_score(self, item: ContentHealthItem) -> float:
        """Compute a health score (0-100) for a content item."""
        score = 100.0

        if item.broken_refs > 0:
            score -= item.broken_refs * 10.0
        if item.missing_metadata > 0:
            score -= item.missing_metadata * 5.0
        if item.doc_completeness < 100.0:
            score -= (100.0 - item.doc_completeness) * 0.2
        if item.a11y_status == "non_compliant":
            score -= 20.0
        elif item.a11y_status == "partial":
            score -= 10.0
        elif item.a11y_status == "unknown":
            score -= 5.0
        if item.localization_status == "incomplete":
            score -= 5.0
        if item.last_reviewed_days > 90:
            score -= min((item.last_reviewed_days - 90) * 0.5, 20.0)
        if item.version_status == "outdated":
            score -= 15.0
        if item.publication_quality < 80.0:
            score -= (80.0 - item.publication_quality) * 0.1
        if item.dependency_health < 80.0:
            score -= (80.0 - item.dependency_health) * 0.1

        return max(0.0, min(100.0, round(score, 2)))

    def _determine_maintenance_actions(
        self, item: ContentHealthItem
    ) -> list[tuple[str, str]]:
        """Determine maintenance actions and priorities for a content item."""
        actions: list[tuple[str, str]] = []

        if item.broken_refs > 0:
            actions.append((f"Fix {item.broken_refs} broken reference(s)", "critical"))

        if item.a11y_status == "non_compliant":
            actions.append(("Remediate accessibility violations", "high"))
        elif item.a11y_status == "unknown":
            actions.append(("Run accessibility audit", "medium"))

        if item.missing_metadata > 0:
            actions.append((f"Add {item.missing_metadata} missing metadata field(s)", "high"))

        if item.doc_completeness < 70.0:
            actions.append(("Complete documentation", "high"))
        elif item.doc_completeness < 90.0:
            actions.append(("Improve documentation completeness", "medium"))

        if item.localization_status == "incomplete":
            actions.append(("Complete localization", "medium"))

        if item.version_status == "outdated":
            actions.append(("Update to current version", "high"))
        elif item.version_status == "deprecated":
            actions.append(("Plan deprecation or replacement", "high"))

        if item.last_reviewed_days > 180:
            actions.append(("Schedule comprehensive review", "medium"))
        elif item.last_reviewed_days > 90:
            actions.append(("Schedule periodic review", "low"))

        if item.publication_quality < 60.0:
            actions.append(("Improve publication quality", "high"))
        elif item.publication_quality < 80.0:
            actions.append(("Enhance publication quality", "medium"))

        if item.dependency_health < 60.0:
            actions.append(("Resolve dependency issues", "critical"))
        elif item.dependency_health < 80.0:
            actions.append(("Update dependencies", "medium"))

        return actions

    def _compute_due_date(self, priority: str) -> str:
        """Compute a due date string based on priority."""
        now = datetime.now(timezone.utc)
        if priority == "critical":
            due = now
        elif priority == "high":
            from datetime import timedelta
            due = now + timedelta(days=7)
        elif priority == "medium":
            from datetime import timedelta
            due = now + timedelta(days=30)
        else:
            from datetime import timedelta
            due = now + timedelta(days=90)
        return due.strftime("%Y-%m-%d")
