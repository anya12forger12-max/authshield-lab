"""Content Production Studio validation rules."""

from __future__ import annotations

from typing import Any

from ...shared.validation.validator import ValidationResult


def validate_program_data(data: dict[str, Any]) -> ValidationResult:
    """Validate program creation/update data."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Program name is required", "REQUIRED")
    elif len(str(name)) > 255:
        result.add_error("name", "Program name must be at most 255 characters", "MAX_LENGTH")

    department = data.get("department", "")
    if not department or not str(department).strip():
        result.add_error("department", "Department is required", "REQUIRED")

    status = data.get("status", "draft")
    valid_statuses = {"draft", "active", "archived"}
    if status not in valid_statuses:
        result.add_error("status", f"Status must be one of: {valid_statuses}", "INVALID_VALUE")

    return result


def validate_course_data(data: dict[str, Any]) -> ValidationResult:
    """Validate course design creation/update data."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Course name is required", "REQUIRED")
    elif len(str(name)) > 255:
        result.add_error("name", "Course name must be at most 255 characters", "MAX_LENGTH")

    program_id = data.get("program_id", "")
    if not program_id or not str(program_id).strip():
        result.add_error("program_id", "Program ID is required", "REQUIRED")

    status = data.get("status", "draft")
    valid_statuses = {"draft", "review", "published", "archived"}
    if status not in valid_statuses:
        result.add_error("status", f"Status must be one of: {valid_statuses}", "INVALID_VALUE")

    estimated_hours = data.get("estimated_hours")
    if estimated_hours is not None:
        if not isinstance(estimated_hours, (int, float)):
            result.add_error("estimated_hours", "Estimated hours must be a number", "TYPE")
        elif estimated_hours < 0:
            result.add_error("estimated_hours", "Estimated hours cannot be negative", "MIN_VALUE")

    return result


def validate_lesson_data(data: dict[str, Any]) -> ValidationResult:
    """Validate lesson creation data."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Lesson name is required", "REQUIRED")
    elif len(str(name)) > 255:
        result.add_error("name", "Lesson name must be at most 255 characters", "MAX_LENGTH")

    estimated_minutes = data.get("estimated_minutes")
    if estimated_minutes is not None:
        if not isinstance(estimated_minutes, int):
            result.add_error("estimated_minutes", "Estimated minutes must be an integer", "TYPE")
        elif estimated_minutes < 1:
            result.add_error("estimated_minutes", "Estimated minutes must be at least 1", "MIN_VALUE")

    return result


def validate_content_block_data(data: dict[str, Any]) -> ValidationResult:
    """Validate content block creation data."""
    result = ValidationResult()

    block_type = data.get("block_type", "text")
    valid_types = {
        "text", "image", "diagram", "table", "code_sample",
        "question", "reflection", "glossary_ref", "simulation", "resource",
    }
    if block_type not in valid_types:
        result.add_error("block_type", f"Block type must be one of: {valid_types}", "INVALID_VALUE")

    content = data.get("content", "")
    if not content or not str(content).strip():
        result.add_error("content", "Content is required", "REQUIRED")

    return result


def validate_activity_data(data: dict[str, Any]) -> ValidationResult:
    """Validate interactive activity creation data."""
    result = ValidationResult()

    activity_type = data.get("activity_type", "mcq")
    valid_types = {
        "mcq", "matching", "drag_drop", "timeline_ordering",
        "scenario_analysis", "log_analysis", "policy_review",
        "config_review", "architecture_review", "reflection",
    }
    if activity_type not in valid_types:
        result.add_error("activity_type", f"Activity type must be one of: {valid_types}", "INVALID_VALUE")

    title = data.get("title", "")
    if not title or not str(title).strip():
        result.add_error("title", "Activity title is required", "REQUIRED")

    return result


def validate_virtual_lab_data(data: dict[str, Any]) -> ValidationResult:
    """Validate virtual lab creation/update data."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Lab name is required", "REQUIRED")
    elif len(str(name)) > 255:
        result.add_error("name", "Lab name must be at most 255 characters", "MAX_LENGTH")

    lab_type = data.get("lab_type", "hands_on")
    valid_types = {"hands_on", "guided", "self-paced", "assessment", "simulation"}
    if lab_type not in valid_types:
        result.add_error("lab_type", f"Lab type must be one of: {valid_types}", "INVALID_VALUE")

    status = data.get("status", "draft")
    valid_statuses = {"draft", "published"}
    if status not in valid_statuses:
        result.add_error("status", f"Status must be one of: {valid_statuses}", "INVALID_VALUE")

    estimated_minutes = data.get("estimated_minutes")
    if estimated_minutes is not None:
        if not isinstance(estimated_minutes, int):
            result.add_error("estimated_minutes", "Estimated minutes must be an integer", "TYPE")
        elif estimated_minutes < 1:
            result.add_error("estimated_minutes", "Estimated minutes must be at least 1", "MIN_VALUE")

    return result


def validate_lab_step_data(data: dict[str, Any]) -> ValidationResult:
    """Validate lab step creation data."""
    result = ValidationResult()

    title = data.get("title", "")
    if not title or not str(title).strip():
        result.add_error("title", "Step title is required", "REQUIRED")

    instructions = data.get("instructions", "")
    if not instructions or not str(instructions).strip():
        result.add_error("instructions", "Step instructions are required", "REQUIRED")

    return result


def validate_multimedia_asset_data(data: dict[str, Any]) -> ValidationResult:
    """Validate multimedia asset creation data."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Asset name is required", "REQUIRED")

    asset_type = data.get("asset_type", "image")
    valid_types = {
        "image", "svg", "audio", "caption", "transcript",
        "pdf", "sample_doc", "synthetic_log", "config_file", "icon",
    }
    if asset_type not in valid_types:
        result.add_error("asset_type", f"Asset type must be one of: {valid_types}", "INVALID_VALUE")

    file_path = data.get("file_path", "")
    if not file_path or not str(file_path).strip():
        result.add_error("file_path", "File path is required", "REQUIRED")

    return result


def validate_template_data(data: dict[str, Any]) -> ValidationResult:
    """Validate content template creation data."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Template name is required", "REQUIRED")
    elif len(str(name)) > 255:
        result.add_error("name", "Template name must be at most 255 characters", "MAX_LENGTH")

    template_type = data.get("template_type", "lesson")
    valid_types = {"course", "lesson", "assessment", "lab", "doc", "report", "a11y", "curriculum"}
    if template_type not in valid_types:
        result.add_error("template_type", f"Template type must be one of: {valid_types}", "INVALID_VALUE")

    return result


def validate_publish_request_data(data: dict[str, Any]) -> ValidationResult:
    """Validate publish request data."""
    result = ValidationResult()

    content_id = data.get("content_id", "")
    if not content_id or not str(content_id).strip():
        result.add_error("content_id", "Content ID is required", "REQUIRED")

    content_type = data.get("content_type", "")
    if not content_type or not str(content_type).strip():
        result.add_error("content_type", "Content type is required", "REQUIRED")

    requested_by = data.get("requested_by", "")
    if not requested_by or not str(requested_by).strip():
        result.add_error("requested_by", "Requested by is required", "REQUIRED")

    return result


def validate_review_data(data: dict[str, Any]) -> ValidationResult:
    """Validate editorial review creation data."""
    result = ValidationResult()

    content_id = data.get("content_id", "")
    if not content_id or not str(content_id).strip():
        result.add_error("content_id", "Content ID is required", "REQUIRED")

    content_type = data.get("content_type", "")
    if not content_type or not str(content_type).strip():
        result.add_error("content_type", "Content type is required", "REQUIRED")

    submitter = data.get("submitter", "")
    if not submitter or not str(submitter).strip():
        result.add_error("submitter", "Submitter is required", "REQUIRED")

    return result


def validate_review_comment_data(data: dict[str, Any]) -> ValidationResult:
    """Validate review comment data."""
    result = ValidationResult()

    author = data.get("author", "")
    if not author or not str(author).strip():
        result.add_error("author", "Author is required", "REQUIRED")

    comment = data.get("comment", "")
    if not comment or not str(comment).strip():
        result.add_error("comment", "Comment text is required", "REQUIRED")

    severity = data.get("severity")
    if severity is not None:
        valid_severities = {"info", "suggestion", "warning", "critical"}
        if severity not in valid_severities:
            result.add_error("severity", f"Severity must be one of: {valid_severities}", "INVALID_VALUE")

    return result
