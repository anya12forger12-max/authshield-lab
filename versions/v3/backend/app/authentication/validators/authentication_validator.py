"""Authentication-specific validators."""

from __future__ import annotations

import re

from ...shared.validation.validator import ValidationResult, Validator
from ...config.constants import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_REQUIRE_DIGIT,
    PASSWORD_REQUIRE_LOWERCASE,
    PASSWORD_REQUIRE_SPECIAL,
    PASSWORD_REQUIRE_UPPERCASE,
    PASSWORD_SPECIAL_CHARACTERS,
)


class AuthenticationValidator(Validator):
    """Domain-specific validation for authentication operations."""

    def validate_login_request(
        self, username: str, password: str
    ) -> ValidationResult:
        """Validate login request fields.

        Parameters
        ----------
        username:
            The username to validate.
        password:
            The password to validate.

        Returns
        -------
        ValidationResult
        """
        result = ValidationResult()

        username_check = self.validate_required(username, "username")
        if not username_check.is_valid:
            result.merge(username_check)

        password_check = self.validate_required(password, "password")
        if not password_check.is_valid:
            result.merge(password_check)

        return result

    def validate_registration_request(
        self,
        username: str,
        password: str,
        confirm_password: str,
        display_name: str,
    ) -> ValidationResult:
        """Validate registration request fields comprehensively.

        Parameters
        ----------
        username:
            The desired username.
        password:
            The desired password.
        confirm_password:
            Password confirmation.
        display_name:
            User's display name.

        Returns
        -------
        ValidationResult
        """
        result = ValidationResult()

        # Username validation
        username_check = self.validate_required(username, "username")
        if not username_check.is_valid:
            result.merge(username_check)
        else:
            length_check = self.validate_length(
                username, "username", min_len=4, max_len=32
            )
            if not length_check.is_valid:
                result.merge(length_check)
            elif not re.match(r"^[a-zA-Z0-9_-]+$", username):
                result.add_error(
                    "username",
                    "Username may only contain letters, digits, underscores, and hyphens.",
                    "format",
                )

        # Password validation
        password_check = self.validate_required(password, "password")
        if not password_check.is_valid:
            result.merge(password_check)
        else:
            length_check = self.validate_length(
                password, "password", min_len=PASSWORD_MIN_LENGTH, max_len=PASSWORD_MAX_LENGTH
            )
            if not length_check.is_valid:
                result.merge(length_check)

        # Confirm password
        if password and confirm_password and password != confirm_password:
            result.add_error(
                "confirm_password", "Passwords do not match.", "mismatch"
            )

        # Display name
        name_check = self.validate_required(display_name, "display_name")
        if not name_check.is_valid:
            result.merge(name_check)
        else:
            length_check = self.validate_length(
                display_name, "display_name", min_len=1, max_len=64
            )
            if not length_check.is_valid:
                result.merge(length_check)

        return result

    def validate_password_change(
        self,
        current_password: str,
        new_password: str,
        confirm_password: str,
    ) -> ValidationResult:
        """Validate password change request fields.

        Parameters
        ----------
        current_password:
            The user's current password.
        new_password:
            The desired new password.
        confirm_password:
            Confirmation of the new password.

        Returns
        -------
        ValidationResult
        """
        result = ValidationResult()

        if not current_password:
            result.add_error(
                "current_password", "Current password is required.", "required"
            )

        if not new_password:
            result.add_error(
                "new_password", "New password is required.", "required"
            )
        else:
            length_check = self.validate_length(
                new_password, "new_password", min_len=PASSWORD_MIN_LENGTH, max_len=PASSWORD_MAX_LENGTH
            )
            if not length_check.is_valid:
                result.merge(length_check)

            # New password must differ from current
            if current_password and new_password == current_password:
                result.add_error(
                    "new_password",
                    "New password must be different from the current password.",
                    "same_password",
                )

        if new_password and confirm_password and new_password != confirm_password:
            result.add_error(
                "confirm_password", "Passwords do not match.", "mismatch"
            )

        return result


_validator_instance: AuthenticationValidator | None = None


def get_authentication_validator() -> AuthenticationValidator:
    """Return a cached ``AuthenticationValidator`` singleton."""
    global _validator_instance  # noqa: PLW0603
    if _validator_instance is None:
        _validator_instance = AuthenticationValidator()
    return _validator_instance
