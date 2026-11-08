"""Production validator for validating data integrity across the module."""

from __future__ import annotations

import re
from typing import Any, Optional

from ...shared.logging_config import get_logger
from ..domain.entities.release_center import Release, ReleaseStatus

logger = get_logger("production.validator")

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$")
VALID_RELEASE_STATUSES = {s.value for s in ReleaseStatus}
VALID_PACKAGE_TYPES = {"installer", "portable", "sdk", "doc_pack"}
VALID_LTS_STATUSES = {"active", "extended", "end_of_life"}
VALID_MIGRATION_STATUSES = {"pending", "in_progress", "completed", "failed", "rolled_back"}
VALID_ADR_STATUSES = {"proposed", "accepted", "deprecated", "superseded"}
VALID_CERT_STATUSES = {"pending", "in_progress", "certified", "failed", "expired"}
VALID_REVIEW_STATUSES = {"pending", "in_progress", "approved", "rejected", "needs_revision"}
VALID_GOVERNANCE_AREAS = {
    "architecture", "documentation", "accessibility",
    "security", "quality", "localization", "plugin", "sdk",
}
VALID_CERT_TYPES = {
    "accessibility", "security", "quality", "performance",
    "documentation", "localization", "plugin", "sdk", "release",
}


class ValidationError(Exception):
    """Raised when production data validation fails."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class ProductionValidator:
    """Validates production entities and data before persistence."""

    @staticmethod
    def validate_version(version: str) -> list[str]:
        """Validate a semantic version string.

        Returns a list of error messages (empty if valid).
        """
        errors: list[str] = []
        if not version:
            errors.append("Version must not be empty")
        elif not VERSION_PATTERN.match(version):
            errors.append(
                f"Version '{version}' does not match pattern X.Y.Z[-prerelease]"
            )
        return errors

    @staticmethod
    def validate_release(release: Release) -> list[str]:
        """Validate a Release entity. Returns list of error messages."""
        errors: list[str] = []

        version_errors = ProductionValidator.validate_version(release.version)
        errors.extend(version_errors)

        if not release.name:
            errors.append("Release name must not be empty")

        if release.status not in VALID_RELEASE_STATUSES:
            errors.append(f"Invalid release status: {release.status}")

        if release.release_date is not None:
            if release.status == ReleaseStatus.IN_DEVELOPMENT:
                errors.append(
                    "In-development releases should not have a release date"
                )

        return errors

    @staticmethod
    def validate_release_package(
        package_type: str, platform: str, checksum: str, file_size: int
    ) -> list[str]:
        """Validate release package fields."""
        errors: list[str] = []
        if package_type not in VALID_PACKAGE_TYPES:
            errors.append(
                f"Invalid package type: {package_type}. "
                f"Must be one of: {VALID_PACKAGE_TYPES}"
            )
        if not platform:
            errors.append("Package platform must not be empty")
        if not checksum:
            errors.append("Package checksum must not be empty")
        if file_size < 0:
            errors.append("Package file size must be non-negative")
        return errors

    @staticmethod
    def validate_lts_status(status: str) -> list[str]:
        """Validate an LTS version status."""
        if status not in VALID_LTS_STATUSES:
            return [
                f"Invalid LTS status: {status}. Must be one of: {VALID_LTS_STATUSES}"
            ]
        return []

    @staticmethod
    def validate_migration_status(status: str) -> list[str]:
        """Validate a migration status."""
        if status not in VALID_MIGRATION_STATUSES:
            return [
                f"Invalid migration status: {status}. "
                f"Must be one of: {VALID_MIGRATION_STATUSES}"
            ]
        return []

    @staticmethod
    def validate_adr_status(status: str) -> list[str]:
        """Validate an ADR status."""
        if status not in VALID_ADR_STATUSES:
            return [
                f"Invalid ADR status: {status}. Must be one of: {VALID_ADR_STATUSES}"
            ]
        return []

    @staticmethod
    def validate_governance_area(area: str) -> list[str]:
        """Validate a governance area."""
        if area not in VALID_GOVERNANCE_AREAS:
            return [
                f"Invalid governance area: {area}. "
                f"Must be one of: {VALID_GOVERNANCE_AREAS}"
            ]
        return []

    @staticmethod
    def validate_review_status(status: str) -> list[str]:
        """Validate a governance review status."""
        if status not in VALID_REVIEW_STATUSES:
            return [
                f"Invalid review status: {status}. "
                f"Must be one of: {VALID_REVIEW_STATUSES}"
            ]
        return []

    @staticmethod
    def validate_certification_status(status: str) -> list[str]:
        """Validate a certification status."""
        if status not in VALID_CERT_STATUSES:
            return [
                f"Invalid certification status: {status}. "
                f"Must be one of: {VALID_CERT_STATUSES}"
            ]
        return []

    @staticmethod
    def validate_certification_type(cert_type: str) -> list[str]:
        """Validate a certification type."""
        if cert_type not in VALID_CERT_TYPES:
            return [
                f"Invalid certification type: {cert_type}. "
                f"Must be one of: {VALID_CERT_TYPES}"
            ]
        return []

    @staticmethod
    def validate_knowledge_entry(
        title: str, category: str, content: str
    ) -> list[str]:
        """Validate a knowledge entry."""
        errors: list[str] = []
        if not title:
            errors.append("Knowledge entry title must not be empty")
        if not category:
            errors.append("Knowledge entry category must not be empty")
        if not content:
            errors.append("Knowledge entry content must not be empty")
        if title and len(title) > 256:
            errors.append("Knowledge entry title must not exceed 256 characters")
        return errors

    @staticmethod
    def validate_coding_standard(
        name: str, category: str, description: str
    ) -> list[str]:
        """Validate a coding standard."""
        errors: list[str] = []
        if not name:
            errors.append("Coding standard name must not be empty")
        if not category:
            errors.append("Coding standard category must not be empty")
        if not description:
            errors.append("Coding standard description must not be empty")
        return errors

    @staticmethod
    def validate_feature_flag_name(name: str) -> list[str]:
        """Validate a feature flag name."""
        errors: list[str] = []
        if not name:
            errors.append("Feature flag name must not be empty")
        elif not re.match(r"^[a-z][a-z0-9_]*$", name):
            errors.append(
                "Feature flag name must start with a lowercase letter "
                "and contain only lowercase letters, digits, and underscores"
            )
        return errors

    @staticmethod
    def validate_all(
        validations: list[list[str]],
    ) -> list[str]:
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
