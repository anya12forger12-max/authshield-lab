"""Tests for PasswordPolicyService."""

import pytest
from unittest.mock import MagicMock

from app.shared.validation.validator import Validator, ValidationResult


class PasswordPolicyService:
    """Minimal password policy service for testing validation logic."""

    def __init__(self, min_length=12, require_uppercase=True, require_lowercase=True,
                 require_digit=True, require_special=True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special

    def validate_password(self, password: str) -> ValidationResult:
        validator = Validator()
        policy = {
            "min_length": self.min_length,
            "require_uppercase": self.require_uppercase,
            "require_lowercase": self.require_lowercase,
            "require_number": self.require_digit,
            "require_special": self.require_special,
        }
        return validator.validate_password(password, policy)

    def check_strength(self, password: str) -> dict:
        score = 0
        checks = {
            "length": len(password) >= self.min_length,
            "uppercase": bool(__import__("re").search(r"[A-Z]", password)),
            "lowercase": bool(__import__("re").search(r"[a-z]", password)),
            "digit": bool(__import__("re").search(r"[0-9]", password)),
            "special": bool(__import__("re").search(r"[!@#$%^&*(),.?\":{}|<>\-_=+\[\]\\;'/`~]", password)),
        }
        score = sum(checks.values())
        return {"score": score, "max_score": 5, "checks": checks}


@pytest.fixture
def policy_service():
    return PasswordPolicyService()


@pytest.fixture
def custom_policy():
    return PasswordPolicyService(min_length=8, require_special=False)


class TestValidatePassword:
    def test_strong_password(self, policy_service):
        result = policy_service.validate_password("MyS3cur3P@ssw0rd!")
        assert result.is_valid is True

    def test_too_short(self, policy_service):
        result = policy_service.validate_password("Short1!")
        assert result.is_valid is False

    def test_no_uppercase(self, policy_service):
        result = policy_service.validate_password("alllowercase123!")
        assert result.is_valid is False
        assert any(e.code == "UPPERCASE" for e in result.errors)

    def test_no_lowercase(self, policy_service):
        result = policy_service.validate_password("ALLUPPERCASE123!")
        assert result.is_valid is False
        assert any(e.code == "LOWERCASE" for e in result.errors)

    def test_no_digit(self, policy_service):
        result = policy_service.validate_password("NoDigitsHere!!")
        assert result.is_valid is False
        assert any(e.code == "NUMBER" for e in result.errors)

    def test_no_special(self, policy_service):
        result = policy_service.validate_password("NoSpecialChar123")
        assert result.is_valid is False
        assert any(e.code == "SPECIAL" for e in result.errors)

    def test_empty_password(self, policy_service):
        result = policy_service.validate_password("")
        assert result.is_valid is False

    def test_custom_policy_relaxed(self, custom_policy):
        result = custom_policy.validate_password("Short1!x")
        assert result.is_valid is True

    def test_custom_policy_no_special_required(self, custom_policy):
        result = custom_policy.validate_password("NoSpecialButOk1")
        assert result.is_valid is True


class TestCheckStrength:
    def test_strong_password(self, policy_service):
        strength = policy_service.check_strength("MyS3cur3P@ssw0rd!")
        assert strength["score"] == 5
        assert all(strength["checks"].values())

    def test_weak_password(self, policy_service):
        strength = policy_service.check_strength("weak")
        assert strength["score"] < 5

    def test_only_lowercase(self, policy_service):
        strength = policy_service.check_strength("lowercaseonly")
        assert strength["checks"]["lowercase"] is True
        assert strength["checks"]["uppercase"] is False
        assert strength["checks"]["digit"] is False

    def test_score_range(self, policy_service):
        strength = policy_service.check_strength("Pass1!")
        assert 0 <= strength["score"] <= 5

    def test_max_score(self, policy_service):
        strength = policy_service.check_strength("Aa1!")
        assert strength["max_score"] == 5
