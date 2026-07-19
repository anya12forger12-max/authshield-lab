"""LMS validation rules for all LMS domain operations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from ...shared.validation.validator import ValidationResult


def validate_classroom_data(data: dict[str, Any]) -> ValidationResult:
    """Validate classroom creation/update data."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Classroom name is required", "REQUIRED")
    elif len(str(name)) > 255:
        result.add_error("name", "Classroom name must be at most 255 characters", "MAX_LENGTH")

    capacity = data.get("capacity", 30)
    if not isinstance(capacity, (int, float)) or capacity < 1:
        result.add_error("capacity", "Capacity must be at least 1", "MIN_VALUE")
    elif capacity > 10000:
        result.add_error("capacity", "Capacity must be at most 10000", "MAX_VALUE")

    instructor_id = data.get("instructor_id", "")
    if not instructor_id or not str(instructor_id).strip():
        result.add_error("instructor_id", "Instructor ID is required", "REQUIRED")

    status = data.get("status", "active")
    valid_statuses = {"active", "inactive", "archived"}
    if status not in valid_statuses:
        result.add_error("status", f"Status must be one of: {valid_statuses}", "INVALID_VALUE")

    return result


def validate_enrollment_data(data: dict[str, Any]) -> ValidationResult:
    """Validate enrollment creation data."""
    result = ValidationResult()

    learner_id = data.get("learner_id", "")
    if not learner_id or not str(learner_id).strip():
        result.add_error("learner_id", "Learner ID is required", "REQUIRED")

    course_id = data.get("course_id", "")
    if not course_id or not str(course_id).strip():
        result.add_error("course_id", "Course ID is required", "REQUIRED")

    status = data.get("status", "pending")
    valid_statuses = {"pending", "active", "completed", "dropped", "waitlisted"}
    if status not in valid_statuses:
        result.add_error("status", f"Status must be one of: {valid_statuses}", "INVALID_VALUE")

    return result


def validate_grade_data(data: dict[str, Any]) -> ValidationResult:
    """Validate grade entry data."""
    result = ValidationResult()

    score = data.get("score")
    if score is None:
        result.add_error("score", "Score is required", "REQUIRED")
    elif not isinstance(score, (int, float)):
        result.add_error("score", "Score must be a number", "TYPE")
    elif score < 0:
        result.add_error("score", "Score cannot be negative", "MIN_VALUE")

    points_possible = data.get("points_possible")
    if points_possible is not None:
        if not isinstance(points_possible, (int, float)):
            result.add_error("points_possible", "Points possible must be a number", "TYPE")
        elif points_possible <= 0:
            result.add_error("points_possible", "Points possible must be greater than 0", "MIN_VALUE")
        elif score is not None and isinstance(score, (int, float)) and score > points_possible:
            result.add_error("score", "Score cannot exceed points possible", "MAX_VALUE")

    grade_item_id = data.get("grade_item_id", "")
    if not grade_item_id or not str(grade_item_id).strip():
        result.add_error("grade_item_id", "Grade item ID is required", "REQUIRED")

    learner_id = data.get("learner_id", "")
    if not learner_id or not str(learner_id).strip():
        result.add_error("learner_id", "Learner ID is required", "REQUIRED")

    return result


def validate_competency_data(data: dict[str, Any]) -> ValidationResult:
    """Validate competency creation data."""
    result = ValidationResult()

    name = data.get("name", "")
    if not name or not str(name).strip():
        result.add_error("name", "Competency name is required", "REQUIRED")
    elif len(str(name)) > 255:
        result.add_error("name", "Competency name must be at most 255 characters", "MAX_LENGTH")

    domain = data.get("domain", "")
    if not domain or not str(domain).strip():
        result.add_error("domain", "Domain is required", "REQUIRED")

    level = data.get("level", "beginner")
    valid_levels = {"beginner", "intermediate", "advanced", "expert"}
    if level not in valid_levels:
        result.add_error("level", f"Level must be one of: {valid_levels}", "INVALID_VALUE")

    return result


def validate_assessment_data(data: dict[str, Any]) -> ValidationResult:
    """Validate assessment creation data."""
    result = ValidationResult()

    title = data.get("title", "")
    if not title or not str(title).strip():
        result.add_error("title", "Assessment title is required", "REQUIRED")
    elif len(str(title)) > 255:
        result.add_error("title", "Title must be at most 255 characters", "MAX_LENGTH")

    course_id = data.get("course_id", "")
    if not course_id or not str(course_id).strip():
        result.add_error("course_id", "Course ID is required", "REQUIRED")

    assessment_type = data.get("assessment_type", "quiz")
    valid_types = {"quiz", "exam", "project", "portfolio", "practical"}
    if assessment_type not in valid_types:
        result.add_error(
            "assessment_type",
            f"Assessment type must be one of: {valid_types}",
            "INVALID_VALUE",
        )

    passing_score = data.get("passing_score", 70.0)
    if not isinstance(passing_score, (int, float)):
        result.add_error("passing_score", "Passing score must be a number", "TYPE")
    elif passing_score < 0:
        result.add_error("passing_score", "Passing score cannot be negative", "MIN_VALUE")

    attempts_allowed = data.get("attempts_allowed", 1)
    if not isinstance(attempts_allowed, int) or attempts_allowed < 1:
        result.add_error("attempts_allowed", "Attempts allowed must be at least 1", "MIN_VALUE")

    time_limit = data.get("time_limit_minutes")
    if time_limit is not None:
        if not isinstance(time_limit, int) or time_limit < 1:
            result.add_error("time_limit_minutes", "Time limit must be at least 1 minute", "MIN_VALUE")

    return result


def validate_calendar_event_data(data: dict[str, Any]) -> ValidationResult:
    """Validate academic calendar event data."""
    result = ValidationResult()

    title = data.get("title", "")
    if not title or not str(title).strip():
        result.add_error("title", "Event title is required", "REQUIRED")

    event_type = data.get("event_type", "class")
    valid_types = {"class", "exam", "assignment", "holiday", "break", "workshop"}
    if event_type not in valid_types:
        result.add_error(
            "event_type",
            f"Event type must be one of: {valid_types}",
            "INVALID_VALUE",
        )

    start_time = data.get("start_time")
    end_time = data.get("end_time")
    if start_time and end_time:
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
        if hasattr(start_time, "timestamp") and hasattr(end_time, "timestamp"):
            if end_time <= start_time:
                result.add_error("end_time", "End time must be after start time", "INVALID_VALUE")

    return result


def validate_portfolio_data(data: dict[str, Any]) -> ValidationResult:
    """Validate portfolio creation data."""
    result = ValidationResult()

    learner_id = data.get("learner_id", "")
    if not learner_id or not str(learner_id).strip():
        result.add_error("learner_id", "Learner ID is required", "REQUIRED")

    title = data.get("title", "")
    if not title or not str(title).strip():
        result.add_error("title", "Portfolio title is required", "REQUIRED")
    elif len(str(title)) > 255:
        result.add_error("title", "Title must be at most 255 characters", "MAX_LENGTH")

    return result


def validate_portfolio_item_data(data: dict[str, Any]) -> ValidationResult:
    """Validate portfolio item creation data."""
    result = ValidationResult()

    title = data.get("title", "")
    if not title or not str(title).strip():
        result.add_error("title", "Item title is required", "REQUIRED")

    item_type = data.get("item_type", "project")
    valid_types = {"certificate", "project", "assessment", "reflection", "badge"}
    if item_type not in valid_types:
        result.add_error(
            "item_type",
            f"Item type must be one of: {valid_types}",
            "INVALID_VALUE",
        )

    return result


def validate_classroom_capacity(
    current_members: int, capacity: int, add_count: int = 1
) -> ValidationResult:
    """Validate that adding members won't exceed classroom capacity."""
    result = ValidationResult()
    new_total = current_members + add_count
    if new_total > capacity:
        result.add_error(
            "capacity",
            f"Adding {add_count} member(s) would exceed capacity "
            f"({current_members}/{capacity})",
            "CAPACITY_EXCEEDED",
        )
    return result


def validate_enrollment_rules(
    is_open: bool,
    is_full: bool,
    has_prerequisites: bool,
    already_enrolled: bool,
) -> ValidationResult:
    """Validate enrollment eligibility rules."""
    result = ValidationResult()

    if already_enrolled:
        result.add_error(
            "enrollment",
            "Learner is already enrolled in this course",
            "ALREADY_ENROLLED",
        )

    if not is_open:
        result.add_error(
            "enrollment",
            "Enrollment window is not open",
            "ENROLLMENT_CLOSED",
        )

    if is_full:
        result.add_warning(
            "enrollment",
            "Course is full; learner will be placed on waitlist",
            "COURSE_FULL",
        )

    if not has_prerequisites:
        result.add_error(
            "prerequisites",
            "Learner has not completed all prerequisites",
            "PREREQUISITES_MISSING",
        )

    return result
