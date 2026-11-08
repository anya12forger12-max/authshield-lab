"""Program evaluation service – evaluations, executive summaries, export."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus
from ..domain.entities.program_evaluation import ExecutiveSummary, ProgramEvaluation
from ..domain.interfaces import (
    IExecutiveSummaryRepository,
    IProgramEvaluationRepository,
)
from ..domain.events.analytics_events import ProgramEvaluated

logger = get_logger("analytics.program_evaluation_service")


class ProgramEvaluationService:
    """Generates program evaluations, executive summaries, and exports.

    Parameters
    ----------
    evaluation_repo:
        Repository for program evaluation persistence.
    summary_repo:
        Repository for executive summary persistence.
    event_bus:
        Optional event bus for domain events.
    """

    def __init__(
        self,
        evaluation_repo: IProgramEvaluationRepository,
        summary_repo: IExecutiveSummaryRepository,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._evaluation_repo = evaluation_repo
        self._summary_repo = summary_repo
        self._event_bus = event_bus

    async def _publish_event(self, event: Any) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def generate_evaluation(
        self,
        program_name: str,
        period: str = "",
        effectiveness_score: float = 0.0,
        competency_coverage: float = 0.0,
        course_performance: Optional[dict[str, float]] = None,
        resource_utilization: float = 0.0,
        instructor_workload: Optional[dict[str, float]] = None,
        certification_outcomes: Optional[dict[str, float]] = None,
        a11y_readiness: float = 0.0,
        governance_compliance: float = 0.0,
        doc_health: float = 0.0,
    ) -> ProgramEvaluation:
        """Generate a comprehensive program evaluation."""
        evaluation = ProgramEvaluation(
            id=str(uuid.uuid4()),
            program_name=program_name,
            period=period,
            effectiveness_score=effectiveness_score,
            competency_coverage=competency_coverage,
            course_performance=course_performance or {},
            resource_utilization=resource_utilization,
            instructor_workload=instructor_workload or {},
            certification_outcomes=certification_outcomes or {},
            a11y_readiness=a11y_readiness,
            governance_compliance=governance_compliance,
            doc_health=doc_health,
            generated_at=datetime.now(timezone.utc),
        )

        await self._evaluation_repo.create(evaluation)
        logger.info(
            "program_evaluated",
            evaluation_id=evaluation.id,
            program_name=program_name,
        )

        await self._publish_event(
            ProgramEvaluated(
                evaluation_id=evaluation.id,
                module="analytics",
            )
        )

        return evaluation

    async def get_evaluation(self, evaluation_id: str) -> Optional[ProgramEvaluation]:
        """Retrieve a specific program evaluation by ID."""
        return await self._evaluation_repo.get_by_id(evaluation_id)

    async def list_evaluations(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all program evaluations with pagination."""
        return await self._evaluation_repo.get_all(page=page, per_page=per_page)

    async def generate_executive_summary(
        self,
        evaluations: Optional[list[ProgramEvaluation]] = None,
    ) -> ExecutiveSummary:
        """Generate a high-level executive summary from evaluations."""
        if evaluations is None:
            result = await self._evaluation_repo.get_all(page=1, per_page=100)
            evaluations = result.get("items", [])

        if not evaluations:
            summary = ExecutiveSummary(
                overall_health=0.0,
                key_findings=["No program evaluations available"],
                recommendations=["Conduct initial program evaluation"],
                priorities=["Establish evaluation baseline"],
                generated_at=datetime.now(timezone.utc),
            )
            await self._summary_repo.create(summary)
            return summary

        avg_effectiveness = (
            sum(e.effectiveness_score for e in evaluations) / len(evaluations)
        )
        avg_competency = (
            sum(e.competency_coverage for e in evaluations) / len(evaluations)
        )
        avg_resource = (
            sum(e.resource_utilization for e in evaluations) / len(evaluations)
        )

        overall_health = (
            avg_effectiveness * 0.4
            + avg_competency * 0.3
            + avg_resource * 0.3
        )

        key_findings: list[str] = []
        recommendations: list[str] = []
        priorities: list[str] = []

        if avg_effectiveness < 70.0:
            key_findings.append(
                f"Program effectiveness score ({avg_effectiveness:.1f}%) is below target"
            )
            recommendations.append("Review and enhance program curriculum and delivery methods")
            priorities.append("Improve program effectiveness")

        if avg_competency < 75.0:
            key_findings.append(
                f"Competency coverage ({avg_competency:.1f}%) has gaps"
            )
            recommendations.append("Map additional competencies to program content")
            priorities.append("Expand competency coverage")

        if avg_resource < 60.0:
            key_findings.append(
                f"Resource utilization ({avg_resource:.1f}%) indicates underutilization"
            )
            recommendations.append("Optimize resource allocation and usage")
            priorities.append("Improve resource utilization")

        for evaluation in evaluations:
            if evaluation.a11y_readiness < 70.0:
                key_findings.append(
                    f"Program '{evaluation.program_name}' a11y readiness is low"
                )
                recommendations.append(
                    f"Improve accessibility readiness for '{evaluation.program_name}'"
                )
                break

        for evaluation in evaluations:
            if evaluation.governance_compliance < 80.0:
                key_findings.append(
                    f"Governance compliance ({evaluation.governance_compliance:.1f}%) needs improvement"
                )
                priorities.append("Achieve governance compliance target")
                break

        if not key_findings:
            key_findings.append("All programs are performing within acceptable parameters")
        if not recommendations:
            recommendations.append("Continue monitoring and maintain current standards")
        if not priorities:
            priorities.append("Sustain current performance levels")

        summary = ExecutiveSummary(
            overall_health=round(overall_health, 2),
            key_findings=key_findings,
            recommendations=recommendations,
            priorities=priorities,
            generated_at=datetime.now(timezone.utc),
        )

        await self._summary_repo.create(summary)
        logger.info(
            "executive_summary_generated",
            overall_health=overall_health,
        )

        return summary

    async def get_latest_summary(self) -> Optional[ExecutiveSummary]:
        """Retrieve the most recently generated executive summary."""
        return await self._summary_repo.get_latest()

    async def export_evaluation(
        self,
        evaluation_id: str,
        format_type: str = "json",
    ) -> Optional[dict[str, Any]]:
        """Export a program evaluation in the specified format."""
        evaluation = await self._evaluation_repo.get_by_id(evaluation_id)
        if evaluation is None:
            return None

        data = {
            "id": evaluation.id,
            "program_name": evaluation.program_name,
            "period": evaluation.period,
            "effectiveness_score": evaluation.effectiveness_score,
            "competency_coverage": evaluation.competency_coverage,
            "course_performance": evaluation.course_performance,
            "resource_utilization": evaluation.resource_utilization,
            "instructor_workload": evaluation.instructor_workload,
            "certification_outcomes": evaluation.certification_outcomes,
            "a11y_readiness": evaluation.a11y_readiness,
            "governance_compliance": evaluation.governance_compliance,
            "doc_health": evaluation.doc_health,
            "generated_at": evaluation.generated_at.isoformat(),
        }

        if format_type == "json":
            return {"format": "json", "data": data}
        elif format_type == "csv":
            rows: list[dict[str, str]] = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    rows.append({"metric": key, "value": json.dumps(value)})
                else:
                    rows.append({"metric": key, "value": str(value)})
            return {"format": "csv", "data": rows}
        else:
            return {"format": format_type, "data": data}
