"""Centralized identity validation framework."""

from __future__ import annotations

import re
from typing import Any, Optional

from .validator import Validator, ValidationResult


# Valid user status values
_VALID_USER_STATUSES = {"active", "inactive", "suspended", "locked", "pending", "deleted"}

# Valid status transitions (from -> allowed targets)
_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "active": {"inactive", "suspended", "locked", "deleted"},
    "inactive": {"active", "deleted"},
    "suspended": {"active", "inactive", "deleted"},
    "locked": {"active", "inactive", "deleted"},
    "pending": {"active", "inactive", "deleted"},
    "deleted": set(),
}


class IdentityValidator(Validator):
    """Comprehensive validator for all identity-related operations.

    Extends the base :class:`Validator` with domain-specific validation
    rules for user profiles, roles, permissions, preferences, and
    administrative actions.
    """

    def validate_user_profile(self, data: dict[str, Any]) -> ValidationResult:
        """Validate a user profile creation payload.

        Parameters
        ----------
        data:
            Dictionary with keys: ``username``, ``display_name``,
            ``email`` (optional), and any other profile fields.
        """
        result = ValidationResult()

        username = data.get("username", "")
        username_result = self.validate_username(username)
        result.merge(username_result)

        display_name = data.get("display_name", "")
        if display_name:
            name_result = self.validate_display_name(display_name)
            result.merge(name_result)
        else:
            result.add_error("display_name", "Display name is required", "REQUIRED")

        email = data.get("email", "")
        if email:
            email_result = self.validate_email(email)
            result.merge(email_result)

        if "bio" in data:
            bio = data["bio"]
            if isinstance(bio, str) and len(bio) > 500:
                result.add_error(
                    "bio", "Bio must be at most 500 characters", "MAX_LENGTH"
                )

        return result

    def validate_profile_update(
        self,
        data: dict[str, Any],
        allowed_fields: Optional[list[str]] = None,
    ) -> ValidationResult:
        """Validate a profile update payload.

        Parameters
        ----------
        data:
            Fields to update.
        allowed_fields:
            If provided, only these fields may be updated.
        """
        result = ValidationResult()

        if not data:
            result.add_error("data", "No update data provided", "EMPTY")
            return result

        if allowed_fields is not None:
            for key in data:
                if key not in allowed_fields:
                    result.add_error(
                        key,
                        f"Field '{key}' is not allowed for update",
                        "FORBIDDEN_FIELD",
                    )

        if "username" in data:
            username_result = self.validate_username(data["username"])
            result.merge(username_result)

        if "display_name" in data and data["display_name"]:
            name_result = self.validate_display_name(data["display_name"])
            result.merge(name_result)

        if "email" in data and data["email"]:
            email_result = self.validate_email(data["email"])
            result.merge(email_result)

        if "bio" in data and isinstance(data["bio"], str) and len(data["bio"]) > 500:
            result.add_error("bio", "Bio must be at most 500 characters", "MAX_LENGTH")

        return result

    def validate_role(self, data: dict[str, Any]) -> ValidationResult:
        """Validate role creation/update data.

        Parameters
        ----------
        data:
            Dictionary with keys: ``name``, ``description`` (optional),
            ``permissions`` (optional list of permission names).
        """
        result = ValidationResult()

        name = data.get("name", "")
        if not name or not name.strip():
            result.add_error("name", "Role name is required", "REQUIRED")
        elif len(name.strip()) < 2:
            result.add_error(
                "name", "Role name must be at least 2 characters", "MIN_LENGTH"
            )
        elif len(name.strip()) > 64:
            result.add_error(
                "name", "Role name must be at most 64 characters", "MAX_LENGTH"
            )
        elif not re.match(r"^[a-zA-Z0-9_\- ]+$", name.strip()):
            result.add_error(
                "name",
                "Role name may only contain letters, digits, spaces, hyphens, and underscores",
                "INVALID_CHARS",
            )

        description = data.get("description", "")
        if description and len(description) > 256:
            result.add_error(
                "description",
                "Description must be at most 256 characters",
                "MAX_LENGTH",
            )

        permissions = data.get("permissions", [])
        if permissions and not isinstance(permissions, list):
            result.add_error(
                "permissions", "Permissions must be a list", "TYPE"
            )
        elif permissions:
            for perm in permissions:
                if not isinstance(perm, str) or not perm.strip():
                    result.add_error(
                        "permissions", "Each permission must be a non-empty string", "INVALID"
                    )

        return result

    def validate_permission(self, data: dict[str, Any]) -> ValidationResult:
        """Validate permission creation data.

        Parameters
        ----------
        data:
            Dictionary with keys: ``name``, ``display_name``,
            ``description``, ``category``.
        """
        result = ValidationResult()

        name = data.get("name", "")
        if not name or not name.strip():
            result.add_error("name", "Permission name is required", "REQUIRED")
        elif "." not in name:
            result.add_error(
                "name",
                "Permission name must be in 'resource.action' format",
                "FORMAT",
            )
        elif len(name) > 128:
            result.add_error(
                "name", "Permission name must be at most 128 characters", "MAX_LENGTH"
            )

        display_name = data.get("display_name", "")
        if not display_name or not display_name.strip():
            result.add_error(
                "display_name", "Display name is required", "REQUIRED"
            )

        category = data.get("category", "")
        if not category or not category.strip():
            result.add_error("category", "Category is required", "REQUIRED")

        return result

    def validate_preferences(self, data: dict[str, Any]) -> ValidationResult:
        """Validate user preferences data.

        Parameters
        ----------
        data:
            Dictionary of preference key-value pairs.
        """
        result = ValidationResult()

        if not isinstance(data, dict):
            result.add_error("preferences", "Preferences must be a dictionary", "TYPE")
            return result

        allowed_keys = {
            "language", "theme", "timezone", "email_notifications",
            "push_notifications", "accessibility_mode", "font_size",
            "high_contrast", "screen_reader_optimized", "reduce_motion",
        }

        for key, value in data.items():
            if key not in allowed_keys:
                result.add_warning(
                    key,
                    f"Unknown preference key '{key}'",
                    "UNKNOWN_KEY",
                )

            if key == "language" and isinstance(value, str):
                if len(value) < 2 or len(value) > 5:
                    result.add_error(
                        key, "Language code must be 2-5 characters", "FORMAT"
                    )

            if key == "timezone" and isinstance(value, str):
                if len(value) > 64:
                    result.add_error(
                        key, "Timezone must be at most 64 characters", "MAX_LENGTH"
                    )

            if key == "font_size" and isinstance(value, str):
                if value not in {"small", "medium", "large", "xlarge"}:
                    result.add_error(
                        key,
                        "Font size must be one of: small, medium, large, xlarge",
                        "INVALID_VALUE",
                    )

            if key in {"email_notifications", "push_notifications", "accessibility_mode",
                        "high_contrast", "screen_reader_optimized", "reduce_motion"}:
                if not isinstance(value, bool):
                    result.add_error(
                        key, f"{key} must be a boolean", "TYPE"
                    )

        return result

    def validate_accessibility_profile(self, data: dict[str, Any]) -> ValidationResult:
        """Validate an accessibility profile.

        Parameters
        ----------
        data:
            Dictionary with accessibility settings.
        """
        result = ValidationResult()

        if not isinstance(data, dict):
            result.add_error(
                "accessibility", "Accessibility profile must be a dictionary", "TYPE"
            )
            return result

        boolean_fields = [
            "screen_reader_optimized", "high_contrast", "reduce_motion",
            "keyboard_navigation", "alt_text_enabled", "captions_enabled",
            "large_text", "focus_indicators",
        ]
        for field_name in boolean_fields:
            if field_name in data and not isinstance(data[field_name], bool):
                result.add_error(
                    field_name, f"{field_name} must be a boolean", "TYPE"
                )

        if "preferred_color_scheme" in data:
            scheme = data["preferred_color_scheme"]
            if scheme not in {"light", "dark", "auto", "high_contrast"}:
                result.add_error(
                    "preferred_color_scheme",
                    "Must be one of: light, dark, auto, high_contrast",
                    "INVALID_VALUE",
                )

        if "text_size_multiplier" in data:
            multiplier = data["text_size_multiplier"]
            if not isinstance(multiplier, (int, float)):
                result.add_error(
                    "text_size_multiplier", "Must be a number", "TYPE"
                )
            elif multiplier < 0.5 or multiplier > 3.0:
                result.add_error(
                    "text_size_multiplier",
                    "Must be between 0.5 and 3.0",
                    "OUT_OF_RANGE",
                )

        return result

    def validate_session_ownership(
        self, user_id: str, session_user_id: str
    ) -> ValidationResult:
        """Validate that a user owns a given session.

        Parameters
        ----------
        user_id:
            The ID of the user performing the action.
        session_user_id:
            The user ID associated with the session.
        """
        result = ValidationResult()

        if not user_id:
            result.add_error("user_id", "User ID is required", "REQUIRED")
        if not session_user_id:
            result.add_error(
                "session_user_id", "Session user ID is required", "REQUIRED"
            )
        if user_id and session_user_id and user_id != session_user_id:
            result.add_error(
                "user_id",
                "User does not own this session",
                "OWNERSHIP_MISMATCH",
            )

        return result

    def validate_admin_action(
        self, action: str, target_user_id: str, admin_user_id: str
    ) -> ValidationResult:
        """Validate an administrative action.

        Parameters
        ----------
        action:
            The action being performed (e.g. ``"delete_user"``).
        target_user_id:
            The ID of the user being acted upon.
        admin_user_id:
            The ID of the admin performing the action.
        """
        result = ValidationResult()

        if not action:
            result.add_error("action", "Action is required", "REQUIRED")

        if not target_user_id:
            result.add_error(
                "target_user_id", "Target user ID is required", "REQUIRED"
            )

        if not admin_user_id:
            result.add_error(
                "admin_user_id", "Admin user ID is required", "REQUIRED"
            )

        if target_user_id and admin_user_id and target_user_id == admin_user_id:
            result.add_warning(
                "admin_action",
                "Admin is targeting themselves",
                "SELF_TARGET",
            )

        dangerous_actions = {"delete_user", "change_password", "reset_2fa", "lock_account"}
        if action in dangerous_actions:
            result.add_warning(
                "action",
                f"Action '{action}' is a privileged operation",
                "PRIVILEGED_ACTION",
            )

        return result

    def validate_status_transition(
        self, current_status: str, target_status: str
    ) -> ValidationResult:
        """Validate that a status transition is allowed.

        Parameters
        ----------
        current_status:
            The current status of the entity.
        target_status:
            The desired target status.
        """
        result = ValidationResult()

        if current_status not in _VALID_USER_STATUSES:
            result.add_error(
                "current_status",
                f"Invalid current status: '{current_status}'",
                "INVALID_STATUS",
            )
            return result

        if target_status not in _VALID_USER_STATUSES:
            result.add_error(
                "target_status",
                f"Invalid target status: '{target_status}'",
                "INVALID_STATUS",
            )
            return result

        allowed = _STATUS_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            result.add_error(
                "status_transition",
                f"Cannot transition from '{current_status}' to '{target_status}'",
                "INVALID_TRANSITION",
            )

        return result

    def validate_pagination(self, page: int, per_page: int) -> ValidationResult:
        """Validate pagination parameters.

        Parameters
        ----------
        page:
            The page number (1-indexed).
        per_page:
            Items per page.
        """
        result = ValidationResult()

        if not isinstance(page, int) or page < 1:
            result.add_error("page", "Page must be a positive integer", "INVALID")

        if not isinstance(per_page, int) or per_page < 1:
            result.add_error("per_page", "Per page must be a positive integer", "INVALID")
        elif per_page > 100:
            result.add_error(
                "per_page", "Per page must be at most 100", "MAX_EXCEEDED"
            )

        return result

    def validate_search_query(self, query: str, max_length: int = 200) -> ValidationResult:
        """Validate a search query string.

        Parameters
        ----------
        query:
            The search query to validate.
        max_length:
            Maximum allowed length.
        """
        result = ValidationResult()

        if not query or not query.strip():
            result.add_error("query", "Search query cannot be empty", "EMPTY")
            return result

        if len(query) > max_length:
            result.add_error(
                "query",
                f"Search query must be at most {max_length} characters",
                "MAX_LENGTH",
            )

        suspicious_patterns = ["<script", "javascript:", "onerror=", "onload="]
        query_lower = query.lower()
        for pattern in suspicious_patterns:
            if pattern in query_lower:
                result.add_error(
                    "query",
                    "Search query contains potentially dangerous content",
                    "SECURITY_VIOLATION",
                )
                break

        return result

    def validate_import_data(
        self, data: dict[str, Any], expected_keys: list[str]
    ) -> ValidationResult:
        """Validate bulk import data.

        Parameters
        ----------
        data:
            The data to import.
        expected_keys:
            Keys that must be present in the data.
        """
        result = ValidationResult()

        if not isinstance(data, dict):
            result.add_error("data", "Import data must be a dictionary", "TYPE")
            return result

        for key in expected_keys:
            if key not in data:
                result.add_error(key, f"Missing required key: '{key}'", "MISSING_KEY")

        if "items" in data:
            items = data["items"]
            if not isinstance(items, list):
                result.add_error("items", "Items must be a list", "TYPE")
            elif len(items) == 0:
                result.add_warning("items", "Import contains no items", "EMPTY")
            elif len(items) > 1000:
                result.add_error(
                    "items",
                    "Import cannot contain more than 1000 items",
                    "MAX_EXCEEDED",
                )

        return result


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_identity_validator: Optional[IdentityValidator] = None


def get_identity_validator() -> IdentityValidator:
    """Return the global :class:`IdentityValidator`, creating it lazily."""
    global _identity_validator  # noqa: PLW0603
    if _identity_validator is None:
        _identity_validator = IdentityValidator()
    return _identity_validator
