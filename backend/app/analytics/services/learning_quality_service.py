"""Learning quality service – quality dashboards, longitudinal comparisons, indicators."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus
from ..domain.entities.learning_quality import (
    LearningQualityDashboard,
    LongitudinalComparison,
    QualityIndicator,
)
from ..domain.interfaces import IQualityDashboardRepository
from ..domain.events.analytics_events import QualityDashboardGenerated

logger = get_logger("analytics.learning_quality_service")


class LearningQualityService:
    """Manages learning quality dashboards, comparisons, and indicators.

    Parameters
    ----------
    dashboard_repo:
        Repository for quality dashboard persistence.
    event_bus:
        Optional event bus for domain events.
    """

    def __init__(
        self,
        dashboard_repo: IQualityDashboardRepository,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._dashboard_repo = dashboard_repo
        self._event_bus = event_bus

    async def _publish_event(self, event: Any) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def generate_dashboard(
        self,
        completion_rates: float = 0.0,
        learning_objective_achievement: float = 0.0,
        competency_growth: float = 0.0,
        assessment_distribution: Optional[dict[str, float]] = None,
        lab_completion: float = 0.0,
        portfolio_progress: float = 0.0,
        certification_progress: float = 0.0,
        reflection_participation: float = 0.0,
        instructor_review_status: float = 0.0,
    ) -> LearningQualityDashboard:
        """Generate a comprehensive learning quality dashboard."""
        dashboard = LearningQualityDashboard(
            id=str(uuid.uuid4()),
            completion_rates=completion_rates,
            learning_objective_achievement=learning_objective_achievement,
            competency_growth=competency_growth,
            assessment_distribution=assessment_distribution or {},
            lab_completion=lab_completion,
            portfolio_progress=portfolio_progress,
            certification_progress=certification_progress,
            reflection_participation=reflection_participation,
            instructor_review_status=instructor_review_status,
            generated_at=datetime.now(timezone.utc),
        )

        await self._dashboard_repo.create(dashboard)
        logger.info("quality_dashboard_generated", dashboard_id=dashboard.id)

        await self._publish_event(
            QualityDashboardGenerated(
                dashboard_id=dashboard.id,
                module="analytics",
            )
        )

        return dashboard

    async def get_dashboard(self, dashboard_id: str) -> Optional[LearningQualityDashboard]:
        """Retrieve a specific quality dashboard by ID."""
        return await self._dashboard_repo.get_by_id(dashboard_id)

    async def get_latest_dashboard(self) -> Optional[LearningQualityDashboard]:
        """Retrieve the most recently generated quality dashboard."""
        return await self._dashboard_repo.get_latest()

    async def list_dashboards(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all quality dashboards with pagination."""
        return await self._dashboard_repo.get_all(page=page, per_page=per_page)

    async def generate_longitudinal_comparisons(
        self,
        current_dashboard: LearningQualityDashboard,
        previous_dashboard: Optional[LearningQualityDashboard] = None,
        term: str = "current",
        previous_term: str = "previous",
    ) -> list[LongitudinalComparison]:
        """Generate term-over-term comparisons for key quality metrics."""
        comparisons: list[LongitudinalComparison] = []

        metric_pairs = [
            ("completion_rates", current_dashboard.completion_rates),
            ("learning_objective_achievement", current_dashboard.learning_objective_achievement),
            ("competency_growth", current_dashboard.competency_growth),
            ("lab_completion", current_dashboard.lab_completion),
            ("portfolio_progress", current_dashboard.portfolio_progress),
            ("certification_progress", current_dashboard.certification_progress),
            ("reflection_participation", current_dashboard.reflection_participation),
            ("instructor_review_status", current_dashboard.instructor_review_status),
        ]

        for metric_name, current_value in metric_pairs:
            prev_value = 0.0
            if previous_dashboard is not None:
                prev_value = getattr(previous_dashboard, metric_name, 0.0)

            change_pct = 0.0
            if prev_value != 0.0:
                change_pct = ((current_value - prev_value) / abs(prev_value)) * 100

            trend = "stable"
            if change_pct > 2.0:
                trend = "improving"
            elif change_pct < -2.0:
                trend = "declining"

            comparisons.append(LongitudinalComparison(
                term=term,
                value=round(current_value, 2),
                change_pct=round(change_pct, 2),
                trend=trend,
            ))

        return comparisons

    async def generate_quality_indicators(
        self,
        dashboard: Optional[LearningQualityDashboard] = None,
    ) -> list[QualityIndicator]:
        """Generate quality indicators with benchmarks and trend assessment."""
        if dashboard is None:
            dashboard = await self._dashboard_repo.get_latest()

        indicators: list[QualityIndicator] = []

        benchmark_data: list[tuple[str, float, float]] = [
            ("Completion Rates", dashboard.completion_rates if dashboard else 0.0, 85.0),
            ("Learning Objective Achievement", dashboard.learning_objective_achievement if dashboard else 0.0, 80.0),
            ("Competency Growth", dashboard.competency_growth if dashboard else 0.0, 75.0),
            ("Lab Completion", dashboard.lab_completion if dashboard else 0.0, 90.0),
            ("Portfolio Progress", dashboard.portfolio_progress if dashboard else 0.0, 70.0),
            ("Certification Progress", dashboard.certification_progress if dashboard else 0.0, 65.0),
            ("Reflection Participation", dashboard.reflection_participation if dashboard else 0.0, 60.0),
            ("Instructor Review Status", dashboard.instructor_review_status if dashboard else 0.0, 80.0),
        ]

        for name, value, benchmark in benchmark_data:
            if value >= benchmark:
                status = "exceeds"
                trend = "improving"
            elif value >= benchmark * 0.9:
                status = "meets"
                trend = "stable"
            elif value >= benchmark * 0.7:
                status = "approaching"
                trend = "stable"
            else:
                status = "below"
                trend = "declining"

            indicators.append(QualityIndicator(
                name=name,
                value=round(value, 2),
                benchmark=benchmark,
                status=status,
                trend=trend,
            ))

        return indicators

    async def compute_overall_quality_score(
        self, dashboard: Optional[LearningQualityDashboard] = None
    ) -> float:
        """Compute a single overall quality score (0-100) from the dashboard."""
        if dashboard is None:
            dashboard = await self._dashboard_repo.get_latest()
        if dashboard is None:
            return 0.0

        weights: dict[str, float] = {
            "completion_rates": 0.20,
            "learning_objective_achievement": 0.20,
            "competency_growth": 0.15,
            "lab_completion": 0.15,
            "portfolio_progress": 0.10,
            "certification_progress": 0.10,
            "reflection_participation": 0.05,
            "instructor_review_status": 0.05,
        }

        total = 0.0
        for field_name, weight in weights.items():
            value = getattr(dashboard, field_name, 0.0)
            total += value * weight

        return round(total, 2)
