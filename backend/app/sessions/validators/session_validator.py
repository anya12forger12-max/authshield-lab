"""Session-specific validators."""

from __future__ import annotations

from typing import Any

from ...shared.validation.validator import Validator, ValidationResult

_session_validator = Validator()


def validate_session_data(data: dict[str, Any]) -> ValidationResult:
    """Validate session creation / update data."""
    result = ValidationResult()

    user_id = data.get("user_id", "")
    if not user_id:
        result.add_error("user_id", "User ID is required.", "required")

    ip_address = data.get("ip_address", "")
    if ip_address:
        # Basic IP format check
        parts = ip_address.split(".")
        if len(parts) != 4:
            # Could be IPv6; skip deep validation for now
            pass
        else:
            for part in parts:
                try:
                    num = int(part)
                    if num < 0 or num > 255:
                        result.add_error(
                            "ip_address",
                            f"Invalid IP address: {ip_address}",
                            "invalid_format",
                        )
                        break
                except ValueError:
                    result.add_error(
                        "ip_address",
                        f"Invalid IP address: {ip_address}",
                        "invalid_format",
                    )
                    break

    idle_timeout = data.get("idle_timeout_minutes")
    if idle_timeout is not None:
        if not isinstance(idle_timeout, (int, float)) or idle_timeout < 1 or idle_timeout > 1440:
            result.add_error(
                "idle_timeout_minutes",
                "Idle timeout must be between 1 and 1440 minutes.",
                "out_of_range",
            )

    security_level = data.get("security_level")
    if security_level is not None:
        if not isinstance(security_level, int) or security_level < 1 or security_level > 5:
            result.add_error(
                "security_level",
                "Security level must be between 1 and 5.",
                "out_of_range",
            )

    return result


def validate_session_filters(filters: dict[str, Any]) -> ValidationResult:
    """Validate session search / filter parameters."""
    result = ValidationResult()

    status = filters.get("status")
    if status is not None:
        valid_statuses = {"active", "expired", "revoked", "idle"}
        if status not in valid_statuses:
            result.add_error(
                "status",
                f"Invalid status filter '{status}'. Must be one of: {', '.join(sorted(valid_statuses))}",
                "invalid_value",
            )

    page = filters.get("page", 1)
    if page is not None and (not isinstance(page, int) or page < 1):
        result.add_error("page", "Page must be a positive integer.", "invalid_value")

    per_page = filters.get("per_page", 20)
    if per_page is not None:
        if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
            result.add_error(
                "per_page",
                "Per page must be between 1 and 100.",
                "out_of_range",
            )

    return result
