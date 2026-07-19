"""Validation utilities for the Standards module."""

from __future__ import annotations

from app.standards.domain.entities.evidence import VALID_EVIDENCE_TYPES


class StandardsValidationError(Exception):
    """Raised when standards validation fails."""


class StandardsValidator:
    """Validates inputs for standards domain operations."""

    VALID_FRAMEWORK_STATUSES: set[str] = {"active", "deprecated", "draft"}
    VALID_COVERAGE_LEVELS: set[str] = {"full", "partial", "none"}
    VALID_REVIEW_STATUSES: set[str] = {"pending", "approved", "rejected", "needs_revision"}

    @staticmethod
    def validate_non_empty(value: str, field_name: str) -> str:
        if not value or not value.strip():
            raise StandardsValidationError(f"{field_name} cannot be empty")
        return value.strip()

    @staticmethod
    def validate_framework_status(status: str) -> str:
        valid = StandardsValidator.VALID_FRAMEWORK_STATUSES
        if status not in valid:
            raise StandardsValidationError(
                f"Invalid framework status: {status}. Must be one of {valid}"
            )
        return status

    @staticmethod
    def validate_coverage_level(level: str) -> str:
        valid = StandardsValidator.VALID_COVERAGE_LEVELS
        if level not in valid:
            raise StandardsValidationError(
                f"Invalid coverage level: {level}. Must be one of {valid}"
            )
        return level

    @staticmethod
    def validate_confidence(confidence: float) -> float:
        if not 0.0 <= confidence <= 1.0:
            raise StandardsValidationError(
                f"Confidence must be between 0.0 and 1.0, got {confidence}"
            )
        return confidence

    @staticmethod
    def validate_review_status(status: str) -> str:
        valid = StandardsValidator.VALID_REVIEW_STATUSES
        if status not in valid:
            raise StandardsValidationError(
                f"Invalid review status: {status}. Must be one of {valid}"
            )
        return status

    @staticmethod
    def validate_evidence_type(evidence_type: str) -> str:
        if evidence_type not in VALID_EVIDENCE_TYPES:
            raise StandardsValidationError(
                f"Invalid evidence type: {evidence_type}. Must be one of {VALID_EVIDENCE_TYPES}"
            )
        return evidence_type

    @staticmethod
    def validate_version(version: str) -> str:
        if not version or not version.strip():
            raise StandardsValidationError("Version cannot be empty")
        return version.strip()

    @staticmethod
    def validate_level(level: str, valid_levels: list[str] | None = None) -> str:
        if valid_levels is None:
            valid_levels = ["beginner", "intermediate", "advanced", "expert"]
        if level not in valid_levels:
            raise StandardsValidationError(
                f"Invalid level: {level}. Must be one of {valid_levels}"
            )
        return level

    @staticmethod
    def validate_positive_integer(value: int, field_name: str) -> int:
        if value < 0:
            raise StandardsValidationError(f"{field_name} must be non-negative, got {value}")
        return value

    @staticmethod
    def validate_score_range(score: float, field_name: str, min_val: float = 0.0, max_val: float = 1.0) -> float:
        if not min_val <= score <= max_val:
            raise StandardsValidationError(
                f"{field_name} must be between {min_val} and {max_val}, got {score}"
            )
        return score

    @staticmethod
    def validate_relationship_type(rel_type: str) -> str:
        valid = {"prerequisite", "corequisite", "related", "part_of", "extends", "depends_on"}
        if rel_type not in valid:
            raise StandardsValidationError(
                f"Invalid relationship type: {rel_type}. Must be one of {valid}"
            )
        return rel_type
