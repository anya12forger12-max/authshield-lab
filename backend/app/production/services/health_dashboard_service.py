"""Health dashboard service for project health metrics."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from ...shared.logging_config import get_logger
from ..domain.entities.certification import HealthIndicator, ProjectHealth
from ..domain.interfaces import IProjectHealthRepository

logger = get_logger("production.health_dashboard_service")

DEFAULT_INDICATORS: list[dict] = [
    {"name": "code_coverage", "value": 85.0, "threshold": 70.0},
    {"name": "test_pass_rate", "value": 98.0, "threshold": 90.0},
    {"name": "lint_score", "value": 95.0, "threshold": 80.0},
    {"name": "documentation_coverage", "value": 72.0, "threshold": 60.0},
    {"name": "dependency_freshness", "value": 90.0, "threshold": 75.0},
    {"name": "security_scan_score", "value": 99.0, "threshold": 90.0},
    {"name": "performance_score", "value": 88.0, "threshold": 70.0},
    {"name": "accessibility_score", "value": 80.0, "threshold": 70.0},
]


class HealthDashboardService:
    """Collects health indicators and generates project health scores.

    Parameters
    ----------
    health_repo:
        Repository for project health persistence.
    """

    def __init__(self, health_repo: IProjectHealthRepository) -> None:
        self._health_repo = health_repo

    @staticmethod
    def _evaluate_indicator_status(value: float, threshold: float) -> str:
        """Determine indicator health status based on value vs threshold."""
        if value >= threshold:
            return "healthy"
        if value >= threshold * 0.7:
            return "degraded"
        return "unhealthy"

    @staticmethod
    def _compute_grade(score: float) -> str:
        """Map a 0-100 score to a letter grade."""
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"

    async def collect_health_indicators(
        self, custom_indicators: Optional[list[dict]] = None
    ) -> list[HealthIndicator]:
        """Collect all health indicators, using defaults or custom values."""
        indicator_data = custom_indicators or DEFAULT_INDICATORS
        indicators: list[HealthIndicator] = []
        for data in indicator_data:
            value = data.get("value", 0.0)
            threshold = data.get("threshold", 0.0)
            status = self._evaluate_indicator_status(value, threshold)
            indicators.append(
                HealthIndicator(
                    name=data.get("name", ""),
                    value=value,
                    threshold=threshold,
                    status=status,
                )
            )
        return indicators

    async def generate_health_report(
        self, custom_indicators: Optional[list[dict]] = None
    ) -> ProjectHealth:
        """Generate a complete project health report."""
        indicators = await self.collect_health_indicators(custom_indicators)

        if indicators:
            total_score = sum(ind.value for ind in indicators)
            overall_score = total_score / len(indicators)
        else:
            overall_score = 0.0

        grade = self._compute_grade(overall_score)

        health = ProjectHealth(
            id=str(uuid.uuid4()),
            indicators=indicators,
            overall_score=round(overall_score, 2),
            grade=grade,
            generated_at=datetime.now(timezone.utc),
        )
        await self._health_repo.create(health)
        logger.info(
            "health_report_generated",
            health_id=health.id,
            score=overall_score,
            grade=grade,
        )
        return health

    async def get_latest_health(self) -> Optional[ProjectHealth]:
        """Retrieve the most recent health report."""
        return await self._health_repo.get_latest()

    async def get_health_history(self) -> list[ProjectHealth]:
        """Retrieve all historical health reports."""
        return await self._health_repo.get_all()

    async def get_indicator_trend(
        self, indicator_name: str
    ) -> list[dict]:
        """Get historical values for a specific indicator."""
        history = await self._health_repo.get_all()
        trend: list[dict] = []
        for report in history:
            for indicator in report.indicators:
                if indicator.name == indicator_name:
                    trend.append(
                        {
                            "date": report.generated_at.isoformat()
                            if report.generated_at
                            else "",
                            "value": indicator.value,
                            "status": indicator.status,
                        }
                    )
        return sorted(
            trend,
            key=lambda x: x["date"],
            reverse=True,
        )

    async def get_unhealthy_indicators(self) -> list[dict]:
        """Find indicators currently in a degraded or unhealthy state."""
        latest = await self._health_repo.get_latest()
        if latest is None:
            return []
        return [
            {
                "name": ind.name,
                "value": ind.value,
                "threshold": ind.threshold,
                "status": ind.status,
            }
            for ind in latest.indicators
            if ind.status in ("degraded", "unhealthy")
        ]
