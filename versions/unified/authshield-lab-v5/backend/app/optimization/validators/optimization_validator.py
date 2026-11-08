"""Optimization module validation rules."""

from __future__ import annotations

from typing import Any

from ...shared.validation.validator import ValidationResult


def validate_performance_metric_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for creating a performance metric."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Metric name is required", "REQUIRED")
    elif len(str(name)) > 255:
        result.add_error("name", "Metric name must be at most 255 characters", "MAX_LENGTH")

    value = data.get("value")
    if value is None:
        result.add_error("value", "Value is required", "REQUIRED")
    elif not isinstance(value, (int, float)):
        result.add_error("value", "Value must be a number", "TYPE")

    unit = data.get("unit", "")
    if not unit or not str(unit).strip():
        result.add_warning("unit", "Unit is recommended for clarity", "MISSING_UNIT")

    category = data.get("category", "")
    if not category or not str(category).strip():
        result.add_warning("category", "Category is recommended for filtering", "MISSING_CATEGORY")

    return result


def validate_benchmark_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for running a benchmark."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Benchmark name is required", "REQUIRED")

    value = data.get("value")
    if value is None:
        result.add_error("value", "Value is required", "REQUIRED")
    elif not isinstance(value, (int, float)):
        result.add_error("value", "Value must be a number", "TYPE")

    threshold = data.get("threshold")
    if threshold is not None:
        if not isinstance(threshold, (int, float)):
            result.add_error("threshold", "Threshold must be a number", "TYPE")
        elif float(threshold) < 0:
            result.add_error("threshold", "Threshold cannot be negative", "MIN_VALUE")

    return result


def validate_feature_flag_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for creating a feature flag."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Flag name is required", "REQUIRED")
    elif len(str(name)) > 255:
        result.add_error("name", "Flag name must be at most 255 characters", "MAX_LENGTH")
    elif not all(c.isalnum() or c in "._-" for c in str(name).strip()):
        result.add_error(
            "name", "Flag name may only contain letters, digits, dots, hyphens, underscores", "INVALID_CHARS"
        )

    category = data.get("category", "")
    if category and len(str(category)) > 100:
        result.add_error("category", "Category must be at most 100 characters", "MAX_LENGTH")

    return result


def validate_config_profile_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for creating a config profile."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Profile name is required", "REQUIRED")
    elif len(str(name)) > 255:
        result.add_error("name", "Profile name must be at most 255 characters", "MAX_LENGTH")

    target_audience = data.get("target_audience", "")
    if not target_audience or not str(target_audience).strip():
        result.add_warning("target_audience", "Target audience is recommended", "MISSING_AUDIENCE")

    settings = data.get("settings")
    if settings is not None and not isinstance(settings, dict):
        result.add_error("settings", "Settings must be a dictionary", "TYPE")

    return result


def validate_release_workflow_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for creating a release workflow."""
    result = ValidationResult()

    release_id = data.get("release_id", "")
    if not release_id or not str(release_id).strip():
        result.add_error("release_id", "Release ID is required", "REQUIRED")

    version = data.get("version", "")
    if not version or not str(version).strip():
        result.add_error("version", "Version is required", "REQUIRED")

    created_by = data.get("created_by", "")
    if not created_by or not str(created_by).strip():
        result.add_warning("created_by", "Created-by is recommended for accountability", "MISSING_AUTHOR")

    return result


def validate_release_approval_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for creating a release approval."""
    result = ValidationResult()

    workflow_id = data.get("workflow_id", "")
    if not workflow_id or not str(workflow_id).strip():
        result.add_error("workflow_id", "Workflow ID is required", "REQUIRED")

    approver = data.get("approver", "")
    if not approver or not str(approver).strip():
        result.add_error("approver", "Approver is required", "REQUIRED")

    stage = data.get("stage", "")
    from ..domain.entities.release_governance import ReleaseStage as _RS
    valid_stages = {s.value for s in _RS}
    if stage and stage not in valid_stages:
        result.add_error("stage", f"Stage must be one of: {valid_stages}", "INVALID_VALUE")

    return result


def validate_compatibility_check_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for a compatibility check."""
    result = ValidationResult()

    platforms = data.get("platforms", [])
    if not platforms or not isinstance(platforms, list):
        result.add_error("platforms", "At least one platform is required", "REQUIRED")

    components = data.get("components", [])
    if not components or not isinstance(components, list):
        result.add_error("components", "At least one component is required", "REQUIRED")

    return result


def validate_sustainability_metric_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for creating a sustainability metric."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Metric name is required", "REQUIRED")

    score = data.get("score")
    if score is None:
        result.add_error("score", "Score is required", "REQUIRED")
    elif not isinstance(score, (int, float)):
        result.add_error("score", "Score must be a number", "TYPE")

    max_score = data.get("max_score", 100.0)
    if isinstance(max_score, (int, float)) and max_score <= 0:
        result.add_error("max_score", "Max score must be greater than 0", "MIN_VALUE")

    return result


def validate_technical_debt_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for creating a technical debt item."""
    result = ValidationResult()

    description = data.get("description", "")
    if not description or not str(description).strip():
        result.add_error("description", "Description is required", "REQUIRED")

    severity = data.get("severity", "low")
    valid_severities = {"low", "medium", "high", "critical"}
    if severity not in valid_severities:
        result.add_error("severity", f"Severity must be one of: {valid_severities}", "INVALID_VALUE")

    estimated_hours = data.get("estimated_hours")
    if estimated_hours is not None:
        if not isinstance(estimated_hours, (int, float)):
            result.add_error("estimated_hours", "Estimated hours must be a number", "TYPE")
        elif float(estimated_hours) < 0:
            result.add_error("estimated_hours", "Estimated hours cannot be negative", "MIN_VALUE")

    return result


def validate_diagnostic_trace_data(data: dict[str, Any]) -> ValidationResult:
    """Validate data for creating a diagnostic trace."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Trace name is required", "REQUIRED")

    spans = data.get("spans", [])
    if spans and not isinstance(spans, list):
        result.add_error("spans", "Spans must be a list", "TYPE")
    else:
        for idx, span in enumerate(spans):
            if not isinstance(span, dict):
                result.add_error(f"spans[{idx}]", "Each span must be a dictionary", "TYPE")
            else:
                if "name" not in span or not span.get("name"):
                    result.add_error(f"spans[{idx}].name", "Span name is required", "REQUIRED")
                if "start_ms" not in span:
                    result.add_error(f"spans[{idx}].start_ms", "start_ms is required", "REQUIRED")
                if "end_ms" not in span:
                    result.add_error(f"spans[{idx}].end_ms", "end_ms is required", "REQUIRED")

    return result
