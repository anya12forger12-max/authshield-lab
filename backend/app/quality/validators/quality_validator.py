from __future__ import annotations

from typing import Any


class ValidationError(Exception):
    pass


class QualityValidator:
    @staticmethod
    def validate_score(score: float, max_score: float) -> None:
        if score < 0:
            raise ValidationError("Score cannot be negative")
        if max_score <= 0:
            raise ValidationError("Max score must be positive")
        if score > max_score:
            raise ValidationError("Score cannot exceed max score")

    @staticmethod
    def validate_category(category: str) -> str:
        cleaned = category.strip().lower()
        if not cleaned:
            raise ValidationError("Category cannot be empty")
        return cleaned

    @staticmethod
    def validate_test_case(data: dict[str, Any]) -> dict[str, Any]:
        if not data.get("name"):
            raise ValidationError("Test case name is required")
        valid_types = {"unit", "integration", "e2e", "ui", "a11y", "localization", "performance", "regression", "backup_restore", "plugin_compat", "package_validation"}
        if data.get("test_type") and data["test_type"] not in valid_types:
            raise ValidationError(f"Invalid test type: {data['test_type']}")
        return data

    @staticmethod
    def validate_status(status: str) -> str:
        valid = {"pass", "fail", "warning", "skipped", "not_run", "passed", "failed"}
        if status not in valid:
            raise ValidationError(f"Invalid status: {status}")
        return status

    @staticmethod
    def validate_version(version: str) -> str:
        if not version.strip():
            raise ValidationError("Version cannot be empty")
        return version.strip()

    @staticmethod
    def validate_non_empty(value: str, field_name: str) -> str:
        if not value.strip():
            raise ValidationError(f"{field_name} cannot be empty")
        return value.strip()
