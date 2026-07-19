"""Analytics module validator for data integrity checks."""

from __future__ import annotations

from typing import Any

from ...shared.logging_config import get_logger
from ..domain.entities.analytics import (
    AssessmentOutcome,
    ContentUsage,
    CurriculumCoverage,
    EducationalAnalyticsDashboard,
    FilterOptions,
    LearningProgress,
    CourseCompletion,
)
from ..domain.entities.content_health import ContentHealthItem
from ..domain.entities.continuous_improvement import ActionPlanStatus

logger = get_logger("analytics.validator")

VALID_CONTENT_TYPES = {"lesson", "quiz", "lab", "video", "document", "interactive", "podcast"}
VALID_A11Y_STATUSES = {"compliant", "partial", "non_compliant", "unknown"}
VALID_LOCALIZATION_STATUSES = {"complete", "incomplete", "in_progress", "not_required"}
VALID_VERSION_STATUSES = {"current", "outdated", "deprecated", "draft"}
VALID_ACTION_PLAN_STATUSES = {s.value for s in ActionPlanStatus}
VALID_TREND_VALUES = {"improving", "stable", "declining"}
VALID_QUALITY_INDICATOR_STATUSES = {"exceeds", "meets", "approaching", "below", "unknown"}


class ValidationError(Exception):
    """Raised when analytics data validation fails."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class AnalyticsValidator:
    """Validates analytics entities and data before persistence."""

    @staticmethod
    def validate_learning_progress(progress: LearningProgress) -> list[str]:
        """Validate a LearningProgress entity."""
        errors: list[str] = []
        if not progress.learner_id:
            errors.append("Learner ID must not be empty")
        if progress.courses_enrolled < 0:
            errors.append("Courses enrolled must be non-negative")
        if progress.courses_completed < 0:
            errors.append("Courses completed must be non-negative")
        if progress.courses_completed > progress.courses_enrolled:
            errors.append("Courses completed cannot exceed courses enrolled")
        if progress.competencies_achieved < 0:
            errors.append("Competencies achieved must be non-negative")
        if not (0.0 <= progress.avg_score <= 100.0):
            errors.append("Average score must be between 0 and 100")
        if progress.total_time_hours < 0:
            errors.append("Total time hours must be non-negative")
        return errors

    @staticmethod
    def validate_course_completion(completion: CourseCompletion) -> list[str]:
        """Validate a CourseCompletion entity."""
        errors: list[str] = []
        if not completion.course_id:
            errors.append("Course ID must not be empty")
        if completion.enrolled < 0:
            errors.append("Enrolled count must be non-negative")
        if completion.completed < 0:
            errors.append("Completed count must be non-negative")
        if completion.in_progress < 0:
            errors.append("In-progress count must be non-negative")
        if completion.dropped < 0:
            errors.append("Dropped count must be non-negative")
        if not (0.0 <= completion.completion_rate <= 100.0):
            errors.append("Completion rate must be between 0 and 100")
        if not (0.0 <= completion.avg_score <= 100.0):
            errors.append("Average score must be between 0 and 100")
        return errors

    @staticmethod
    def validate_assessment_outcome(outcome: AssessmentOutcome) -> list[str]:
        """Validate an AssessmentOutcome entity."""
        errors: list[str] = []
        if not outcome.assessment_id:
            errors.append("Assessment ID must not be empty")
        if outcome.total_attempts < 0:
            errors.append("Total attempts must be non-negative")
        if outcome.passed < 0:
            errors.append("Passed count must be non-negative")
        if outcome.failed < 0:
            errors.append("Failed count must be non-negative")
        if outcome.passed + outcome.failed > outcome.total_attempts:
            errors.append("Passed + failed cannot exceed total attempts")
        if not (0.0 <= outcome.pass_rate <= 100.0):
            errors.append("Pass rate must be between 0 and 100")
        for q_id, diff in outcome.question_difficulty.items():
            if not (0.0 <= diff <= 1.0):
                errors.append(f"Question difficulty for '{q_id}' must be between 0 and 1")
        for q_id, disc in outcome.question_discrimination.items():
            if not (-1.0 <= disc <= 1.0):
                errors.append(f"Question discrimination for '{q_id}' must be between -1 and 1")
        return errors

    @staticmethod
    def validate_curriculum_coverage(coverage: CurriculumCoverage) -> list[str]:
        """Validate a CurriculumCoverage entity."""
        errors: list[str] = []
        if not coverage.framework_id:
            errors.append("Framework ID must not be empty")
        if coverage.total_competencies < 0:
            errors.append("Total competencies must be non-negative")
        if coverage.mapped_competencies < 0:
            errors.append("Mapped competencies must be non-negative")
        if coverage.mapped_competencies > coverage.total_competencies:
            errors.append("Mapped competencies cannot exceed total competencies")
        if not (0.0 <= coverage.coverage_pct <= 100.0):
            errors.append("Coverage percentage must be between 0 and 100")
        return errors

    @staticmethod
    def validate_content_usage(usage: ContentUsage) -> list[str]:
        """Validate a ContentUsage entity."""
        errors: list[str] = []
        if not usage.content_id:
            errors.append("Content ID must not be empty")
        if usage.access_count < 0:
            errors.append("Access count must be non-negative")
        if usage.average_time_minutes < 0:
            errors.append("Average time minutes must be non-negative")
        return errors

    @staticmethod
    def validate_content_health_item(item: ContentHealthItem) -> list[str]:
        """Validate a ContentHealthItem entity."""
        errors: list[str] = []
        if not item.content_id:
            errors.append("Content ID must not be empty")
        if item.content_type and item.content_type not in VALID_CONTENT_TYPES:
            errors.append(
                f"Invalid content type: '{item.content_type}'. "
                f"Must be one of: {VALID_CONTENT_TYPES}"
            )
        if item.a11y_status not in VALID_A11Y_STATUSES:
            errors.append(
                f"Invalid a11y status: '{item.a11y_status}'. "
                f"Must be one of: {VALID_A11Y_STATUSES}"
            )
        if item.localization_status not in VALID_LOCALIZATION_STATUSES:
            errors.append(
                f"Invalid localization status: '{item.localization_status}'. "
                f"Must be one of: {VALID_LOCALIZATION_STATUSES}"
            )
        if item.version_status not in VALID_VERSION_STATUSES:
            errors.append(
                f"Invalid version status: '{item.version_status}'. "
                f"Must be one of: {VALID_VERSION_STATUSES}"
            )
        if item.broken_refs < 0:
            errors.append("Broken refs must be non-negative")
        if item.missing_metadata < 0:
            errors.append("Missing metadata must be non-negative")
        if not (0.0 <= item.doc_completeness <= 100.0):
            errors.append("Doc completeness must be between 0 and 100")
        if not (0.0 <= item.publication_quality <= 100.0):
            errors.append("Publication quality must be between 0 and 100")
        if not (0.0 <= item.dependency_health <= 100.0):
            errors.append("Dependency health must be between 0 and 100")
        if item.last_reviewed_days < 0:
            errors.append("Last reviewed days must be non-negative")
        return errors

    @staticmethod
    def validate_filter_options(filters: FilterOptions) -> list[str]:
        """Validate filter options."""
        errors: list[str] = []
        if filters.date_from and filters.date_to:
            if filters.date_from > filters.date_to:
                errors.append("date_from must be before date_to")
        return errors

    @staticmethod
    def validate_action_plan_status(status: str) -> list[str]:
        """Validate an action plan status string."""
        if status not in VALID_ACTION_PLAN_STATUSES:
            return [
                f"Invalid action plan status: '{status}'. "
                f"Must be one of: {VALID_ACTION_PLAN_STATUSES}"
            ]
        return []

    @staticmethod
    def validate_all(validations: list[list[str]]) -> list[str]:
        """Combine multiple validation result lists into a single error list."""
        combined: list[str] = []
        for errors in validations:
            combined.extend(errors)
        return combined

    @staticmethod
    def is_valid(errors: list[str]) -> bool:
        """Check if a validation result list is empty (valid)."""
        return len(errors) == 0

    @staticmethod
    def raise_if_invalid(
        errors: list[str], context: str = "Validation"
    ) -> None:
        """Raise a ValidationError if there are any errors."""
        if errors:
            combined = "; ".join(errors)
            raise ValidationError(context, combined)
