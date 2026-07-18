"""Password policy service implementation."""

from __future__ import annotations

import re
import string
from typing import Any

from ...config.constants import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_REQUIRE_DIGIT,
    PASSWORD_REQUIRE_LOWERCASE,
    PASSWORD_REQUIRE_SPECIAL,
    PASSWORD_REQUIRE_UPPERCASE,
    PASSWORD_SPECIAL_CHARACTERS,
)
from ..domain.interfaces.password_service import IPasswordPolicyService

# Common weak passwords (subset for educational demonstration)
_COMMON_PASSWORDS: frozenset[str] = frozenset({
    "password", "password1", "password123", "123456", "12345678",
    "qwerty", "abc123", "monkey", "master", "dragon", "login",
    "princess", "football", "shadow", "sunshine", "trustno1",
    "iloveyou", "batman", "access", "hello", "charlie", "donald",
    "admin", "passw0rd", "letmein", "welcome", "summer", "winter",
    "spring", "autumn", "master123", "changeme", "secret",
    "123456789", "1234567890", "000000", "111111",
})

# Sequential character patterns
_SEQUENTIAL_PATTERNS: list[str] = [
    "abcdefghijklmnopqrstuvwxyz",
    "zyxwvutsrqponmlkjihgfedcba",
    "01234567890",
    "09876543210",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
]


class PasswordPolicyService(IPasswordPolicyService):
    """Enforces password policy rules and evaluates password strength.

    Rules enforced:
    - Minimum/maximum length
    - Uppercase letter requirement
    - Lowercase letter requirement
    - Digit requirement
    - Special character requirement
    - Maximum repeated characters
    - Sequential character detection
    - Common password detection
    - Username similarity detection
    """

    def validate_password(self, password: str, username: str = "") -> dict:
        """Validate a password against the full policy.

        Parameters
        ----------
        password:
            The password to validate.
        username:
            Optional username to check for similarity.

        Returns
        -------
        dict
            ``{"is_valid": bool, "errors": [...], "warnings": [...]}``
        """
        errors: list[dict[str, str]] = []
        warnings: list[str] = []

        # Minimum length
        if len(password) < PASSWORD_MIN_LENGTH:
            errors.append({
                "field": "password",
                "message": f"Password must be at least {PASSWORD_MIN_LENGTH} characters long.",
                "code": "min_length",
            })

        # Maximum length
        if len(password) > PASSWORD_MAX_LENGTH:
            errors.append({
                "field": "password",
                "message": f"Password must be at most {PASSWORD_MAX_LENGTH} characters long.",
                "code": "max_length",
            })

        # Uppercase requirement
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            errors.append({
                "field": "password",
                "message": "Password must contain at least one uppercase letter.",
                "code": "require_uppercase",
            })

        # Lowercase requirement
        if PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
            errors.append({
                "field": "password",
                "message": "Password must contain at least one lowercase letter.",
                "code": "require_lowercase",
            })

        # Digit requirement
        if PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", password):
            errors.append({
                "field": "password",
                "message": "Password must contain at least one digit.",
                "code": "require_digit",
            })

        # Special character requirement
        if PASSWORD_REQUIRE_SPECIAL:
            has_special = any(c in PASSWORD_SPECIAL_CHARACTERS for c in password)
            if not has_special:
                errors.append({
                    "field": "password",
                    "message": "Password must contain at least one special character.",
                    "code": "require_special",
                })

        # Maximum repeated characters (3+ in a row)
        if re.search(r"(.)\1{2,}", password):
            warnings.append(
                "Password contains three or more repeated characters in a row."
            )

        # Sequential characters
        lower_password = password.lower()
        for pattern in _SEQUENTIAL_PATTERNS:
            for i in range(len(pattern) - 2):
                seq = pattern[i : i + 3]
                if seq in lower_password or seq[::-1] in lower_password:
                    warnings.append(
                        "Password contains sequential characters."
                    )
                    break
            else:
                continue
            break

        # Common password check
        if lower_password in _COMMON_PASSWORDS or password in _COMMON_PASSWORDS:
            errors.append({
                "field": "password",
                "message": "This password is too common. Please choose a more unique password.",
                "code": "common_password",
            })

        # Username similarity
        if username:
            username_lower = username.lower()
            if len(password) >= 3 and username_lower in lower_password:
                errors.append({
                    "field": "password",
                    "message": "Password must not contain the username.",
                    "code": "username_in_password",
                })
            if password.lower() == username_lower:
                errors.append({
                    "field": "password",
                    "message": "Password must not be the same as the username.",
                    "code": "username_match",
                })

        # Character diversity warning
        unique_chars = len(set(password))
        if unique_chars < 5:
            warnings.append(
                "Password uses very few unique characters. "
                "Consider using more variety."
            )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def check_strength(self, password: str) -> dict:
        """Evaluate password strength on a 0-100 scale.

        Parameters
        ----------
        password:
            The password to evaluate.

        Returns
        -------
        dict
            ``{"score": int, "level": str, "feedback": list[str]}``
        """
        score = 0
        feedback: list[str] = []

        # Length scoring (up to 30 points)
        length = len(password)
        if length >= 16:
            score += 30
        elif length >= 12:
            score += 25
        elif length >= 8:
            score += 15
        elif length >= 6:
            score += 8
        else:
            score += 3

        # Character diversity (up to 30 points)
        has_upper = bool(re.search(r"[A-Z]", password))
        has_lower = bool(re.search(r"[a-z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = any(c in PASSWORD_SPECIAL_CHARACTERS for c in password)

        diversity = sum([has_upper, has_lower, has_digit, has_special])
        score += diversity * 7

        if not has_upper:
            feedback.append("Add uppercase letters.")
        if not has_lower:
            feedback.append("Add lowercase letters.")
        if not has_digit:
            feedback.append("Add numbers.")
        if not has_special:
            feedback.append("Add special characters.")

        # Unique character ratio (up to 20 points)
        if password:
            unique_ratio = len(set(password)) / len(password)
            score += int(unique_ratio * 20)

            if unique_ratio < 0.4:
                feedback.append(
                    "Use more unique characters to increase strength."
                )

        # Length bonus (up to 10 points)
        if length >= 20:
            score += 10
        elif length >= 16:
            score += 7
        elif length >= 12:
            score += 5
        elif length >= 8:
            score += 2

        # Penalty for common patterns
        lower_password = password.lower()
        if lower_password in _COMMON_PASSWORDS:
            score = min(score, 10)
            feedback.append("This is a commonly used password.")
        elif any(seq in lower_password for seq in ["password", "qwerty", "abc123"]):
            score -= 15
            feedback.append("Avoid common keyboard patterns and words.")

        # Penalty for repeated characters
        if re.search(r"(.)\1{3,}", password):
            score -= 10
            feedback.append("Avoid four or more repeated characters in a row.")

        # Clamp score
        score = max(0, min(100, score))

        # Determine level
        if score >= 80:
            level = "strong"
        elif score >= 60:
            level = "good"
        elif score >= 40:
            level = "fair"
        elif score >= 20:
            level = "weak"
        else:
            level = "very_weak"

        return {
            "score": score,
            "level": level,
            "feedback": feedback,
        }

    def get_policy_config(self) -> dict:
        """Return the current password policy configuration.

        Returns
        -------
        dict
            Policy settings for display / client-side validation.
        """
        return {
            "min_length": PASSWORD_MIN_LENGTH,
            "max_length": PASSWORD_MAX_LENGTH,
            "require_uppercase": PASSWORD_REQUIRE_UPPERCASE,
            "require_lowercase": PASSWORD_REQUIRE_LOWERCASE,
            "require_digit": PASSWORD_REQUIRE_DIGIT,
            "require_special": PASSWORD_REQUIRE_SPECIAL,
            "special_characters": PASSWORD_SPECIAL_CHARACTERS,
            "max_repeated_characters": 3,
            "check_common_passwords": True,
            "check_username_similarity": True,
            "check_sequential_characters": True,
        }
