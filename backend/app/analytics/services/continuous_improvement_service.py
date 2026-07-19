"""Continuous improvement service – manage plans, track progress, compare history."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus
from ..domain.entities.continuous_improvement import (
    ActionPlan,
    ActionPlanItem,
    ActionPlanStatus,
    HistoricalComparison,
    ImprovementInitiative,
    ImprovementReport,
)
from ..domain.interfaces import (
    IActionPlanItemRepository,
    IActionPlanRepository,
    IImprovementInitiativeRepository,
    IImprovementReportRepository,
)
from ..domain.events.analytics_events import ImprovementPlanCreated

logger = get_logger("analytics.continuous_improvement_service")


class ContinuousImprovementService:
    """Manages improvement plans, tracks progress, and compares historical data.

    Parameters
    ----------
    plan_repo:
        Repository for action plan persistence.
    plan_item_repo:
        Repository for action plan item persistence.
    initiative_repo:
        Repository for improvement initiative persistence.
    report_repo:
        Repository for improvement report persistence.
    event_bus:
        Optional event bus for domain events.
    """

    def __init__(
        self,
        plan_repo: IActionPlanRepository,
        plan_item_repo: IActionPlanItemRepository,
        initiative_repo: IImprovementInitiativeRepository,
        report_repo: IImprovementReportRepository,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._plan_repo = plan_repo
        self._plan_item_repo = plan_item_repo
        self._initiative_repo = initiative_repo
        self._report_repo = report_repo
        self._event_bus = event_bus

    async def _publish_event(self, event: Any) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def create_action_plan(
        self,
        title: str,
        description: str = "",
        owner: str = "",
        target_date: str = "",
        items: Optional[list[str]] = None,
    ) -> ActionPlan:
        """Create a new action plan with optional items."""
        plan = ActionPlan(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            owner=owner,
            status=ActionPlanStatus.NOT_STARTED,
            target_date=target_date,
            created_at=datetime.now(timezone.utc),
        )
        await self._plan_repo.create(plan)

        if items:
            for item_desc in items:
                plan_item = ActionPlanItem(
                    id=str(uuid.uuid4()),
                    plan_id=plan.id,
                    description=item_desc,
                    status="pending",
                    evidence=[],
                    review_date=target_date,
                )
                await self._plan_item_repo.create(plan_item)

        logger.info("action_plan_created", plan_id=plan.id, title=title)

        await self._publish_event(
            ImprovementPlanCreated(
                plan_id=plan.id,
                module="analytics",
            )
        )

        return plan

    async def get_action_plan(self, plan_id: str) -> Optional[ActionPlan]:
        """Retrieve an action plan by ID."""
        return await self._plan_repo.get_by_id(plan_id)

    async def list_action_plans(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all action plans with pagination."""
        return await self._plan_repo.get_all(page=page, per_page=per_page)

    async def update_plan_status(
        self, plan_id: str, status: str
    ) -> Optional[ActionPlan]:
        """Update the status of an action plan."""
        try:
            plan_status = ActionPlanStatus(status)
        except ValueError:
            raise ValueError(f"Invalid status: {status}. Must be one of: {[s.value for s in ActionPlanStatus]}")

        updated = await self._plan_repo.update(plan_id, {"status": plan_status})
        if updated is not None:
            logger.info("plan_status_updated", plan_id=plan_id, status=status)
        return updated

    async def add_plan_item(
        self,
        plan_id: str,
        description: str,
        review_date: str = "",
    ) -> Optional[ActionPlanItem]:
        """Add an item to an existing action plan."""
        plan = await self._plan_repo.get_by_id(plan_id)
        if plan is None:
            return None

        item = ActionPlanItem(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            description=description,
            status="pending",
            evidence=[],
            review_date=review_date or plan.target_date,
        )
        created = await self._plan_item_repo.create(item)
        logger.info("plan_item_added", plan_id=plan_id, item_id=created.id)
        return created

    async def update_plan_item(
        self,
        item_id: str,
        status: Optional[str] = None,
        evidence: Optional[list[str]] = None,
    ) -> Optional[ActionPlanItem]:
        """Update an action plan item."""
        data: dict[str, Any] = {}
        if status is not None:
            data["status"] = status
        if evidence is not None:
            data["evidence"] = evidence
        return await self._plan_item_repo.update(item_id, data)

    async def get_plan_items(self, plan_id: str) -> list[ActionPlanItem]:
        """Retrieve all items for an action plan."""
        return await self._plan_item_repo.get_by_plan_id(plan_id)

    async def compute_plan_progress(self, plan_id: str) -> dict[str, Any]:
        """Compute progress statistics for an action plan."""
        items = await self._plan_item_repo.get_by_plan_id(plan_id)
        if not items:
            return {"plan_id": plan_id, "total": 0, "completed": 0, "progress_pct": 0.0}

        total = len(items)
        completed = sum(1 for i in items if i.status == "completed")
        in_progress = sum(1 for i in items if i.status == "in_progress")
        progress_pct = (completed / total * 100) if total > 0 else 0.0

        return {
            "plan_id": plan_id,
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": total - completed - in_progress,
            "progress_pct": round(progress_pct, 2),
        }

    async def create_initiative(
        self,
        name: str,
        description: str = "",
        start_date: str = "",
        end_date: str = "",
        assignees: Optional[list[str]] = None,
        metrics: Optional[dict] = None,
    ) -> ImprovementInitiative:
        """Create a new improvement initiative."""
        initiative = ImprovementInitiative(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            progress_pct=0.0,
            assignees=assignees or [],
            metrics=metrics or {},
        )
        created = await self._initiative_repo.create(initiative)
        logger.info("initiative_created", initiative_id=created.id, name=name)
        return created

    async def get_initiative(self, initiative_id: str) -> Optional[ImprovementInitiative]:
        """Retrieve an improvement initiative by ID."""
        return await self._initiative_repo.get_by_id(initiative_id)

    async def list_initiatives(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all improvement initiatives with pagination."""
        return await self._initiative_repo.get_all(page=page, per_page=per_page)

    async def update_initiative(
        self,
        initiative_id: str,
        progress_pct: Optional[float] = None,
        metrics: Optional[dict] = None,
    ) -> Optional[ImprovementInitiative]:
        """Update an improvement initiative."""
        data: dict[str, Any] = {}
        if progress_pct is not None:
            data["progress_pct"] = progress_pct
        if metrics is not None:
            data["metrics"] = metrics
        return await self._initiative_repo.update(initiative_id, data)

    async def generate_improvement_report(
        self,
        initiative_id: str,
        period: str = "",
        progress: float = 0.0,
        findings: Optional[list[str]] = None,
        next_steps: Optional[list[str]] = None,
    ) -> Optional[ImprovementReport]:
        """Generate a periodic improvement report for an initiative."""
        initiative = await self._initiative_repo.get_by_id(initiative_id)
        if initiative is None:
            return None

        report = ImprovementReport(
            id=str(uuid.uuid4()),
            initiative_id=initiative_id,
            period=period,
            progress=progress,
            findings=findings or [],
            next_steps=next_steps or [],
            generated_at=datetime.now(timezone.utc),
        )
        created = await self._report_repo.create(report)
        logger.info(
            "improvement_report_generated",
            report_id=created.id,
            initiative_id=initiative_id,
        )
        return created

    async def get_initiative_reports(self, initiative_id: str) -> list[ImprovementReport]:
        """Retrieve all reports for a specific initiative."""
        return await self._report_repo.get_by_initiative_id(initiative_id)

    async def compare_periods(
        self,
        period_a_label: str,
        period_b_label: str,
        period_a_metrics: dict[str, float],
        period_b_metrics: dict[str, float],
    ) -> HistoricalComparison:
        """Compare metrics across two time periods."""
        all_keys = set(period_a_metrics.keys()) | set(period_b_metrics.keys())

        changes: dict[str, float] = {}
        metrics_data: dict[str, dict[str, float]] = {}

        for key in all_keys:
            val_a = period_a_metrics.get(key, 0.0)
            val_b = period_b_metrics.get(key, 0.0)
            change = 0.0
            if val_a != 0.0:
                change = ((val_b - val_a) / abs(val_a)) * 100
            changes[key] = round(change, 2)
            metrics_data[key] = {"period_a": val_a, "period_b": val_b}

        comparison = HistoricalComparison(
            period_a=period_a_label,
            period_b=period_b_label,
            metrics=metrics_data,
            changes=changes,
        )

        logger.info(
            "period_comparison_generated",
            period_a=period_a_label,
            period_b=period_b_label,
            metrics_count=len(changes),
        )

        return comparison
