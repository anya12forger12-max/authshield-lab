"""Centralized validation framework for AuthShieldLab."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ValidationSeverity(str, Enum):
    """Severity levels for validation findings."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationRule:
    """A single validation finding (error, warning, or info)."""

    rule_id: str
    field_name: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    code: str = ""


@dataclass
class ValidationResult:
    """Aggregated result of one or more validation checks.

    Callers accumulate errors and warnings via :meth:`add_error` /
    :meth:`add_warning` and inspect :attr:`is_valid` to decide whether
    the input is acceptable.
    """

    is_valid: bool = True
    errors: list[ValidationRule] = field(default_factory=list)
    warnings: list[ValidationRule] = field(default_factory=list)

    def add_error(self, field_name: str, message: str, code: str = "") -> None:
        """Record a validation error."""
        self.is_valid = False
        self.errors.append(
            ValidationRule(
                rule_id=str(uuid.uuid4()),
                field_name=field_name,
                message=message,
                severity=ValidationSeverity.ERROR,
                code=code,
            )
        )

    def add_warning(self, field_name: str, message: str, code: str = "") -> None:
        """Record a non-fatal validation warning."""
        self.warnings.append(
            ValidationRule(
                rule_id=str(uuid.uuid4()),
                field_name=field_name,
                message=message,
                severity=ValidationSeverity.WARNING,
                code=code,
            )
        )

    def merge(self, other: ValidationResult) -> None:
        """Merge *other* result into this one.

        After merging, ``self.is_valid`` is ``True`` only if both results
        were valid.
        """
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the result to a plain dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": [
                {
                    "rule_id": e.rule_id,
                    "field_name": e.field_name,
                    "message": e.message,
                    "severity": e.severity.value,
                    "code": e.code,
                }
                for e in self.errors
            ],
            "warnings": [
                {
                    "rule_id": w.rule_id,
                    "field_name": w.field_name,
                    "message": w.message,
                    "severity": w.severity.value,
                    "code": w.code,
                }
                for w in self.warnings
            ],
        }


# Pre-compiled patterns ------------------------------------------------

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]+$")
_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)


class Validator:
    """Stateless validator with composable validation rules.

    All public ``validate_*`` methods return a :class:`ValidationResult`
    so callers can inspect individual findings without exceptions.
    """

    def validate_username(self, username: str) -> ValidationResult:
        """Validate a username: length 3-32, alphanumeric with ``. _ -``."""
        result = ValidationResult()

        if not username or not username.strip():
            result.add_error("username", "Username is required", "REQUIRED")
            return result

        username = username.strip()

        if len(username) < 3:
            result.add_error(
                "username",
                "Username must be at least 3 characters long",
                "MIN_LENGTH",
            )
        if len(username) > 32:
            result.add_error(
                "username",
                "Username must be at most 32 characters long",
                "MAX_LENGTH",
            )
        if not _USERNAME_RE.match(username):
            result.add_error(
                "username",
                "Username may only contain letters, digits, dots, hyphens, and underscores",
                "INVALID_CHARS",
            )

        return result

    def validate_password(
        self, password: str, policy: Optional[dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate a password against a (configurable) policy.

        Parameters
        ----------
        password:
            The plaintext password to validate.
        policy:
            Optional override dict with keys: ``min_length``, ``require_uppercase``,
            ``require_lowercase``, ``require_number``, ``require_special``.
        """
        result = ValidationResult()

        if not password:
            result.add_error("password", "Password is required", "REQUIRED")
            return result

        p: dict[str, Any] = {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_number": True,
            "require_special": True,
        }
        if policy:
            p.update(policy)

        if len(password) < p["min_length"]:
            result.add_error(
                "password",
                f"Password must be at least {p['min_length']} characters long",
                "MIN_LENGTH",
            )
        if p["require_uppercase"] and not re.search(r"[A-Z]", password):
            result.add_error(
                "password",
                "Password must contain at least one uppercase letter",
                "UPPERCASE",
            )
        if p["require_lowercase"] and not re.search(r"[a-z]", password):
            result.add_error(
                "password",
                "Password must contain at least one lowercase letter",
                "LOWERCASE",
            )
        if p["require_number"] and not re.search(r"[0-9]", password):
            result.add_error(
                "password",
                "Password must contain at least one number",
                "NUMBER",
            )
        if p["require_special"] and not re.search(
            r"[!@#$%^&*(),.?\":{}|<>\-_=+\[\]\\;'/`~]", password
        ):
            result.add_error(
                "password",
                "Password must contain at least one special character",
                "SPECIAL",
            )

        return result

    def validate_email(self, email: str) -> ValidationResult:
        """Validate an email address against a basic regex pattern."""
        result = ValidationResult()

        if not email or not email.strip():
            result.add_error("email", "Email address is required", "REQUIRED")
            return result

        email = email.strip()
        if not _EMAIL_RE.match(email):
            result.add_error("email", "Invalid email address", "INVALID")

        return result

    def validate_display_name(self, name: str) -> ValidationResult:
        """Validate a display name: 1-100 characters, no control characters."""
        result = ValidationResult()

        if not name or not name.strip():
            result.add_error("display_name", "Display name is required", "REQUIRED")
            return result

        name = name.strip()

        if len(name) > 100:
            result.add_error(
                "display_name",
                "Display name must be at most 100 characters long",
                "MAX_LENGTH",
            )

        if any(ord(c) < 32 for c in name):
            result.add_error(
                "display_name",
                "Display name contains control characters",
                "INVALID_CHARS",
            )

        return result

    def validate_required(self, value: Any, field_name: str) -> ValidationResult:
        """Check that *value* is not ``None`` or empty."""
        result = ValidationResult()
        if value is None or (isinstance(value, str) and not value.strip()):
            result.add_error(field_name, f"{field_name} is required", "REQUIRED")
        return result

    def validate_length(
        self,
        value: str,
        field_name: str,
        min_len: int = 0,
        max_len: int = 255,
    ) -> ValidationResult:
        """Check that *value* length falls within ``[min_len, max_len]``."""
        result = ValidationResult()
        if not isinstance(value, str):
            result.add_error(field_name, f"{field_name} must be a string", "TYPE")
            return result
        length = len(value)
        if length < min_len:
            result.add_error(
                field_name,
                f"{field_name} must be at least {min_len} characters",
                "MIN_LENGTH",
            )
        if length > max_len:
            result.add_error(
                field_name,
                f"{field_name} must be at most {max_len} characters",
                "MAX_LENGTH",
            )
        return result

    def validate_format(
        self,
        value: str,
        field_name: str,
        pattern: str,
        message: str = "",
    ) -> ValidationResult:
        """Check *value* against an arbitrary regex *pattern*."""
        result = ValidationResult()
        if not isinstance(value, str):
            result.add_error(field_name, f"{field_name} must be a string", "TYPE")
            return result
        if not re.match(pattern, value):
            msg = message or f"{field_name} does not match the expected format"
            result.add_error(field_name, msg, "FORMAT")
        return result

    def sanitize_input(self, value: str) -> str:
        """Strip leading/trailing whitespace and collapse multiple spaces."""
        if not isinstance(value, str):
            return value  # type: ignore[return-value]
        return re.sub(r"\s+", " ", value.strip())

    def normalize_username(self, username: str) -> str:
        """Normalize a username: lowercase, strip, collapse separators."""
        username = username.strip().lower()
        username = re.sub(r"[_.-]+", ".", username)
        username = username.strip(".")
        return username


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_validator: Optional[Validator] = None


def get_validator() -> Validator:
    """Return the global :class:`Validator` instance."""
    global _validator  # noqa: PLW0603
    if _validator is None:
        _validator = Validator()
    return _validator
