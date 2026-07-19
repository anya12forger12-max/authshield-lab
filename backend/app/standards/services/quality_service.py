"""Service layer for academic quality dashboards, readiness reviews, and outcome validation."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.standards.domain.entities.quality import (
    AcademicQualityDashboard,
    FrameworkComparison,
    LearningOutcomeValidation,
    ReadinessReview,
    ReadinessReviewEvent,
)
from app.standards.domain.events.standards_events import (
    QualityDashboardGenerated,
    ReadinessReviewAdvanced,
)
from app.standards.domain.interfaces.standards_interfaces import (
    AbstractAcademicQualityDashboardRepository,
    AbstractFrameworkComparisonRepository,
    AbstractFrameworkRepository,
    AbstractLearningOutcomeValidationRepository,
    AbstractReadinessReviewRepository,
)
from app.standards.events.standards_event_handlers import get_event_bus
from app.standards.validators.standards_validator import StandardsValidator

logger = logging.getLogger(__name__)


class QualityService:
    """Manages academic quality dashboards, readiness reviews, and validations."""

    def __init__(
        self,
        dashboard_repo: AbstractAcademicQualityDashboardRepository | None = None,
        review_repo: AbstractReadinessReviewRepository | None = None,
        comparison_repo: AbstractFrameworkComparisonRepository | None = None,
        validation_repo: AbstractLearningOutcomeValidationRepository | None = None,
        framework_repo: AbstractFrameworkRepository | None = None,
    ) -> None:
        from app.standards.repositories.standards_repository_impl import (
            InMemoryAcademicQualityDashboardRepository,
            InMemoryFrameworkComparisonRepository,
            InMemoryFrameworkRepository,
            InMemoryLearningOutcomeValidationRepository,
            InMemoryReadinessReviewRepository,
        )

        self._dashboards = dashboard_repo or InMemoryAcademicQualityDashboardRepository()
        self._reviews = review_repo or InMemoryReadinessReviewRepository()
        self._comparisons = comparison_repo or InMemoryFrameworkComparisonRepository()
        self._validations = validation_repo or InMemoryLearningOutcomeValidationRepository()
        self._frameworks = framework_repo or InMemoryFrameworkRepository()
        self._validator = StandardsValidator()
        self._bus = get_event_bus()

    # ------------------------------------------------------------------
    # Quality Dashboard
    # ------------------------------------------------------------------

    def generate_dashboard(
        self,
        curriculum_balance: float = 0.0,
        competency_distribution: dict[str, float] | None = None,
        skills_progression: dict[str, float] | None = None,
        assessment_distribution: dict[str, float] | None = None,
        a11y_health: float = 0.0,
        doc_quality: float = 0.0,
        localization_readiness: float = 0.0,
        content_freshness: float = 0.0,
        review_completion: float = 0.0,
    ) -> AcademicQualityDashboard:
        dashboard = AcademicQualityDashboard(
            curriculum_balance=curriculum_balance,
            competency_distribution=competency_distribution or {},
            skills_progression=skills_progression or {},
            assessment_distribution=assessment_distribution or {},
            a11y_health=a11y_health,
            doc_quality=doc_quality,
            localization_readiness=localization_readiness,
            content_freshness=content_freshness,
            review_completion=review_completion,
        )
        self._dashboards.save(dashboard)
        event = QualityDashboardGenerated(
            dashboard_id=dashboard.id,
            overall_score=dashboard.overall_score(),
            health_status=dashboard.health_status(),
        )
        self._bus.dispatch(event)
        logger.info("Dashboard generated: id=%s overall=%.2f status=%s", dashboard.id, dashboard.overall_score(), dashboard.health_status())
        return dashboard

    def get_latest_dashboard(self) -> AcademicQualityDashboard | None:
        return self._dashboards.find_latest()

    def list_dashboards(self) -> list[AcademicQualityDashboard]:
        return self._dashboards.find_all()

    # ------------------------------------------------------------------
    # Readiness Reviews
    # ------------------------------------------------------------------

    def create_review(
        self,
        name: str,
        framework_id: str,
        created_by: str = "",
    ) -> ReadinessReview:
        self._validator.validate_non_empty(name, "name")
        self._validator.validate_non_empty(framework_id, "framework_id")
        review = ReadinessReview(
            name=name,
            framework_id=framework_id,
            created_by=created_by,
        )
        self._reviews.save(review)
        logger.info("Readiness review created: id=%s name=%s", review.id, review.name)
        return review

    def get_review(self, review_id: str) -> ReadinessReview | None:
        return self._reviews.get_by_id(review_id)

    def list_reviews(self) -> list[ReadinessReview]:
        return self._reviews.list_all()

    def list_reviews_by_framework(self, framework_id: str) -> list[ReadinessReview]:
        return self._reviews.list_by_framework(framework_id)

    def advance_review(
        self,
        review_id: str,
        actor: str,
        comments: str = "",
    ) -> ReadinessReview | None:
        review = self._reviews.get_by_id(review_id)
        if review is None:
            return None
        old_stage = review.current_stage.value
        try:
            event = review.advance(actor=actor, comments=comments)
        except RuntimeError as exc:
            logger.warning("Cannot advance review %s: %s", review_id, exc)
            return None
        self._reviews.save(review)
        adv_event = ReadinessReviewAdvanced(
            review_id=review_id,
            old_stage=old_stage,
            new_stage=review.current_stage.value,
            actor=actor,
        )
        self._bus.dispatch(adv_event)
        return review

    def reject_review(
        self,
        review_id: str,
        actor: str,
        comments: str = "",
    ) -> ReadinessReview | None:
        review = self._reviews.get_by_id(review_id)
        if review is None:
            return None
        try:
            review.reject(actor=actor, comments=comments)
        except RuntimeError as exc:
            logger.warning("Cannot reject review %s: %s", review_id, exc)
            return None
        self._reviews.save(review)
        return review

    def delete_review(self, review_id: str) -> bool:
        return self._reviews.delete(review_id)

    # ------------------------------------------------------------------
    # Learning Outcome Validation
    # ------------------------------------------------------------------

    def validate_learning_outcomes(self, framework_id: str) -> LearningOutcomeValidation:
        fw = self._frameworks.get_by_id(framework_id)
        if fw is None:
            raise ValueError(f"Framework {framework_id} not found")
        missing = 0
        duplicates: set[str] = set()
        names_seen: set[str] = set()
        unmapped = 0
        weak = 0
        for comp in fw.competencies:
            if not comp.description:
                missing += 1
            if comp.name in names_seen:
                duplicates.add(comp.name)
            names_seen.add(comp.name)
            if not comp.skills:
                unmapped += 1
            if comp.level in ("", "basic"):
                weak += 1
        obj_descriptions: set[str] = set()
        obj_dupes = 0
        for obj in fw.learning_objectives:
            if obj.description in obj_descriptions:
                obj_dupes += 1
            obj_descriptions.add(obj.description)
        assessment_gaps = sum(1 for c in fw.competencies if not c.skills)
        doc_gaps = sum(1 for c in fw.competencies if not c.description)
        a11y_gaps = len([a for a in fw.knowledge_areas if not a.skill_ids])
        recommendations: list[str] = []
        if missing > 0:
            recommendations.append(f"Add descriptions to {missing} competencies")
        if duplicates:
            recommendations.append(f"Resolve {len(duplicates)} duplicate competency names")
        if unmapped > 0:
            recommendations.append(f"Map skills to {unmapped} competencies")
        if weak > 0:
            recommendations.append(f"Raise level for {weak} low-level competencies")
        if assessment_gaps > 0:
            recommendations.append(f"Add assessments for {assessment_gaps} competencies")
        if doc_gaps > 0:
            recommendations.append(f"Improve documentation for {doc_gaps} competencies")
        if a11y_gaps > 0:
            recommendations.append(f"Add skills to {a11y_gaps} knowledge areas")
        validation = LearningOutcomeValidation(
            framework_id=framework_id,
            missing_outcomes=missing,
            duplicate_outcomes=len(duplicates),
            unmapped_outcomes=unmapped,
            weak_coverage=weak,
            assessment_gaps=assessment_gaps,
            doc_gaps=doc_gaps,
            a11y_gaps=a11y_gaps,
            recommendations=recommendations,
        )
        self._validations.save(validation)
        return validation

    def get_validation(self, validation_id: str) -> LearningOutcomeValidation | None:
        return self._validations.get_by_id(validation_id)

    def list_validations(self, framework_id: str) -> list[LearningOutcomeValidation]:
        return self._validations.list_by_framework(framework_id)
