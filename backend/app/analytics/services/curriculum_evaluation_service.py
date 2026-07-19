"""Curriculum evaluation service – balance, coverage, gaps, alignment, recommendations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ...shared.events.event_bus import EventBus
from ..domain.entities.curriculum_evaluation import (
    CurriculumEvaluationResult,
    EvaluationRecommendation,
    PrerequisiteGap,
    TopicAnalysis,
)
from ..domain.interfaces import (
    ICurriculumEvaluationRepository,
    IEvaluationRecommendationRepository,
)
from ..domain.events.analytics_events import CurriculumEvaluated

logger = get_logger("analytics.curriculum_evaluation_service")


class CurriculumEvaluationService:
    """Evaluates curriculum balance, coverage, gaps, and generates recommendations.

    Parameters
    ----------
    evaluation_repo:
        Repository for curriculum evaluation persistence.
    recommendation_repo:
        Repository for evaluation recommendation persistence.
    event_bus:
        Optional event bus for domain events.
    """

    def __init__(
        self,
        evaluation_repo: ICurriculumEvaluationRepository,
        recommendation_repo: IEvaluationRecommendationRepository,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._evaluation_repo = evaluation_repo
        self._recommendation_repo = recommendation_repo
        self._event_bus = event_bus

    async def _publish_event(self, event: Any) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def evaluate_curriculum(
        self,
        topics: list[str],
        competencies: list[str],
        mapped_competencies: Optional[list[str]] = None,
        existing_content: Optional[list[dict[str, Any]]] = None,
        review_frequency_days: int = 30,
    ) -> CurriculumEvaluationResult:
        """Run a full curriculum evaluation.

        Analyzes balance, topic coverage, redundancy, prerequisite gaps,
        assessment alignment, a11y, localization, and freshness.
        """
        curriculum_balance = self._compute_curriculum_balance(topics, existing_content or [])
        topic_coverage = self._compute_topic_coverage(topics, existing_content or [])
        redundant_content = self._detect_redundancy(existing_content or [])
        missing_prerequisites = self._detect_missing_prerequisites(existing_content or [])
        total_comps = len(competencies)
        mapped = len(mapped_competencies) if mapped_competencies else 0
        coverage_pct = (mapped / total_comps * 100) if total_comps > 0 else 0.0

        result = CurriculumEvaluationResult(
            id=str(uuid.uuid4()),
            curriculum_balance=curriculum_balance,
            topic_coverage=topic_coverage,
            redundant_content=redundant_content,
            missing_prerequisites=missing_prerequisites,
            assessment_alignment=self._compute_assessment_alignment(existing_content or []),
            a11y_coverage=self._compute_a11y_coverage(existing_content or []),
            localization_coverage=self._compute_localization_coverage(existing_content or []),
            content_freshness=self._compute_content_freshness(existing_content or []),
            review_frequency_days=review_frequency_days,
            generated_at=datetime.now(timezone.utc),
        )

        await self._evaluation_repo.create(result)
        logger.info("curriculum_evaluated", evaluation_id=result.id)

        await self._publish_event(
            CurriculumEvaluated(
                evaluation_id=result.id,
                module="analytics",
            )
        )

        return result

    async def get_evaluation(self, evaluation_id: str) -> Optional[CurriculumEvaluationResult]:
        """Retrieve a specific curriculum evaluation by ID."""
        return await self._evaluation_repo.get_by_id(evaluation_id)

    async def list_evaluations(
        self, page: int = 1, per_page: int = 20
    ) -> dict:
        """List all curriculum evaluations with pagination."""
        return await self._evaluation_repo.get_all(page=page, per_page=per_page)

    async def generate_recommendations(
        self,
        evaluation: CurriculumEvaluationResult,
    ) -> list[EvaluationRecommendation]:
        """Generate actionable recommendations based on evaluation results."""
        recommendations: list[EvaluationRecommendation] = []

        if evaluation.assessment_alignment < 70.0:
            rec = EvaluationRecommendation(
                id=str(uuid.uuid4()),
                category="alignment",
                priority="high",
                recommendation="Increase assessment alignment with learning objectives",
                rationale=f"Current alignment score is {evaluation.assessment_alignment}%, below 70% threshold",
                impact="Improved learner outcomes and clearer competency mapping",
                effort="medium",
            )
            await self._recommendation_repo.create(rec)
            recommendations.append(rec)

        if evaluation.a11y_coverage < 80.0:
            rec = EvaluationRecommendation(
                id=str(uuid.uuid4()),
                category="accessibility",
                priority="high",
                recommendation="Improve accessibility coverage across curriculum content",
                rationale=f"Current a11y coverage is {evaluation.a11y_coverage}%, below 80% threshold",
                impact="Broader learner inclusivity and regulatory compliance",
                effort="high",
            )
            await self._recommendation_repo.create(rec)
            recommendations.append(rec)

        if evaluation.localization_coverage < 75.0:
            rec = EvaluationRecommendation(
                id=str(uuid.uuid4()),
                category="localization",
                priority="medium",
                recommendation="Expand localization coverage for multilingual support",
                rationale=f"Current localization is {evaluation.localization_coverage}%, below 75% threshold",
                impact="Wider reach for non-native-English-speaking learners",
                effort="high",
            )
            await self._recommendation_repo.create(rec)
            recommendations.append(rec)

        if evaluation.content_freshness < 80.0:
            rec = EvaluationRecommendation(
                id=str(uuid.uuid4()),
                category="freshness",
                priority="medium",
                recommendation="Review and update outdated content assets",
                rationale=f"Content freshness score is {evaluation.content_freshness}%, below 80% threshold",
                impact="Up-to-date and relevant learning materials",
                effort="medium",
            )
            await self._recommendation_repo.create(rec)
            recommendations.append(rec)

        if len(evaluation.redundant_content) > 0:
            rec = EvaluationRecommendation(
                id=str(uuid.uuid4()),
                category="redundancy",
                priority="low",
                recommendation="Consolidate redundant content to reduce maintenance burden",
                rationale=f"Detected {len(evaluation.redundant_content)} redundant content items",
                impact="Reduced maintenance overhead and improved learner experience",
                effort="low",
            )
            await self._recommendation_repo.create(rec)
            recommendations.append(rec)

        if len(evaluation.missing_prerequisites) > 0:
            rec = EvaluationRecommendation(
                id=str(uuid.uuid4()),
                category="prerequisites",
                priority="high",
                recommendation="Address missing prerequisite relationships in curriculum",
                rationale=f"Detected {len(evaluation.missing_prerequisites)} missing prerequisite gaps",
                impact="Improved learner preparedness and reduced frustration",
                effort="medium",
            )
            await self._recommendation_repo.create(rec)
            recommendations.append(rec)

        if not recommendations:
            rec = EvaluationRecommendation(
                id=str(uuid.uuid4()),
                category="general",
                priority="low",
                recommendation="Curriculum is in good standing – continue periodic reviews",
                rationale="All metrics are within acceptable thresholds",
                impact="Sustained quality through ongoing monitoring",
                effort="low",
            )
            await self._recommendation_repo.create(rec)
            recommendations.append(rec)

        return recommendations

    async def get_recommendations(self) -> list[EvaluationRecommendation]:
        """Retrieve all stored recommendations."""
        return await self._recommendation_repo.get_all()

    async def analyze_topics(
        self,
        topics: list[str],
        existing_content: Optional[list[dict[str, Any]]] = None,
    ) -> list[TopicAnalysis]:
        """Analyze individual topics for coverage and redundancy."""
        content = existing_content or []
        analyses: list[TopicAnalysis] = []

        for topic in topics:
            topic_items = [
                c for c in content
                if topic.lower() in c.get("title", "").lower()
                or topic.lower() in c.get("topic", "").lower()
            ]
            coverage = (len(topic_items) / len(content) * 100) if content else 0.0
            redundancy = self._topic_redundancy_score(topic_items)
            gaps = self._topic_gaps(topic, topic_items)

            analyses.append(TopicAnalysis(
                topic=topic,
                coverage_pct=round(coverage, 2),
                redundancy_score=round(redundancy, 2),
                gaps=gaps,
            ))

        return analyses

    async def analyze_prerequisite_gaps(
        self,
        existing_content: Optional[list[dict[str, Any]]] = None,
    ) -> list[PrerequisiteGap]:
        """Analyze missing prerequisite relationships."""
        raw_gaps = self._detect_missing_prerequisites(existing_content or [])
        return [
            PrerequisiteGap(
                missing_from=g.get("missing_from", ""),
                needed_by=g.get("needed_by", ""),
                severity=g.get("severity", "medium"),
            )
            for g in raw_gaps
        ]

    def _compute_curriculum_balance(
        self, topics: list[str], content: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Compute balance scores per topic."""
        balance: dict[str, float] = {}
        total = len(content) if content else 1
        for topic in topics:
            count = sum(
                1 for c in content
                if topic.lower() in c.get("topic", "").lower()
                or topic.lower() in c.get("title", "").lower()
            )
            balance[topic] = round((count / total) * 100, 2)
        return balance

    def _compute_topic_coverage(
        self, topics: list[str], content: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Compute coverage percentage per topic."""
        return self._compute_curriculum_balance(topics, content)

    def _detect_redundancy(
        self, content: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Detect potentially redundant content items."""
        redundant: list[dict[str, Any]] = []
        titles = [c.get("title", "") for c in content]
        seen: dict[str, int] = {}
        for i, title in enumerate(titles):
            normalized = title.lower().strip()
            if normalized in seen:
                redundant.append({
                    "original_index": seen[normalized],
                    "duplicate_index": i,
                    "title": title,
                    "reason": "duplicate_title",
                })
            else:
                seen[normalized] = i
        return redundant

    def _detect_missing_prerequisites(
        self, content: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Detect missing prerequisite relationships."""
        gaps: list[dict[str, Any]] = []
        for item in content:
            declared_prereqs = item.get("prerequisites", [])
            available_titles = {c.get("title", "") for c in content}
            for prereq in declared_prereqs:
                if prereq not in available_titles:
                    gaps.append({
                        "missing_from": prereq,
                        "needed_by": item.get("title", ""),
                        "severity": "high",
                    })
        return gaps

    def _compute_assessment_alignment(
        self, content: list[dict[str, Any]]
    ) -> float:
        """Compute assessment alignment score."""
        with_assessments = sum(
            1 for c in content if c.get("has_assessment", False)
        )
        return round(
            (with_assessments / len(content) * 100) if content else 0.0, 2
        )

    def _compute_a11y_coverage(
        self, content: list[dict[str, Any]]
    ) -> float:
        """Compute accessibility coverage percentage."""
        accessible = sum(
            1 for c in content if c.get("a11y_compliant", False)
        )
        return round(
            (accessible / len(content) * 100) if content else 0.0, 2
        )

    def _compute_localization_coverage(
        self, content: list[dict[str, Any]]
    ) -> float:
        """Compute localization coverage percentage."""
        localized = sum(
            1 for c in content if c.get("localized", False)
        )
        return round(
            (localized / len(content) * 100) if content else 0.0, 2
        )

    def _compute_content_freshness(
        self, content: list[dict[str, Any]]
    ) -> float:
        """Compute content freshness score based on last review dates."""
        now = datetime.now(timezone.utc)
        fresh_count = 0
        for item in content:
            last_reviewed = item.get("last_reviewed_days", 0)
            if isinstance(last_reviewed, (int, float)) and last_reviewed <= 90:
                fresh_count += 1
        return round(
            (fresh_count / len(content) * 100) if content else 0.0, 2
        )

    def _topic_redundancy_score(self, items: list[dict[str, Any]]) -> float:
        """Compute a redundancy score for a set of topic items."""
        if len(items) <= 1:
            return 0.0
        titles = [i.get("title", "").lower() for i in items]
        unique = len(set(titles))
        return round(((len(items) - unique) / len(items)) * 100, 2)

    def _topic_gaps(
        self, topic: str, items: list[dict[str, Any]]
    ) -> list[str]:
        """Identify gaps in topic coverage."""
        gaps: list[str] = []
        expected_components = ["introduction", "practice", "assessment", "review"]
        covered = {
            i.get("type", "").lower() for i in items
        }
        for component in expected_components:
            if component not in covered:
                gaps.append(f"Missing {component} for topic '{topic}'")
        return gaps
