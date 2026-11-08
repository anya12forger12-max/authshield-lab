"""Tests for Validator: validate_username, validate_password, validate_email, sanitize_input."""

import pytest

from app.shared.validation.validator import (
    Validator,
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
    get_validator,
)


@pytest.fixture
def validator():
    return Validator()


class TestValidationResult:
    def test_initial_state(self):
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_add_error(self):
        result = ValidationResult()
        result.add_error("field", "error msg", "CODE")
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field_name == "field"
        assert result.errors[0].code == "CODE"

    def test_add_warning(self):
        result = ValidationResult()
        result.add_warning("field", "warning msg")
        assert result.is_valid is True
        assert len(result.warnings) == 1

    def test_merge_both_valid(self):
        r1 = ValidationResult()
        r2 = ValidationResult()
        r1.merge(r2)
        assert r1.is_valid is True

    def test_merge_one_invalid(self):
        r1 = ValidationResult()
        r2 = ValidationResult()
        r2.add_error("f", "msg")
        r1.merge(r2)
        assert r1.is_valid is False

    def test_to_dict(self):
        result = ValidationResult()
        result.add_error("field", "msg", "CODE")
        d = result.to_dict()
        assert d["is_valid"] is False
        assert len(d["errors"]) == 1
        assert d["errors"][0]["severity"] == "error"


class TestValidateUsername:
    def test_valid(self, validator):
        result = validator.validate_username("alice")
        assert result.is_valid is True

    def test_minimum_length(self, validator):
        result = validator.validate_username("ab")
        assert result.is_valid is False

    def test_maximum_length(self, validator):
        result = validator.validate_username("a" * 33)
        assert result.is_valid is False

    def test_empty(self, validator):
        result = validator.validate_username("")
        assert result.is_valid is False

    def test_special_chars(self, validator):
        result = validator.validate_username("alice@domain")
        assert result.is_valid is False

    def test_dots_hyphens_underscores(self, validator):
        result = validator.validate_username("alice.smith-01")
        assert result.is_valid is True


class TestValidatePassword:
    def test_valid(self, validator):
        result = validator.validate_password("SecurePass123!")
        assert result.is_valid is True

    def test_empty(self, validator):
        result = validator.validate_password("")
        assert result.is_valid is False

    def test_too_short(self, validator):
        result = validator.validate_password("short")
        assert result.is_valid is False

    def test_no_uppercase(self, validator):
        result = validator.validate_password("alllowercase123!")
        assert result.is_valid is False

    def test_no_lowercase(self, validator):
        result = validator.validate_password("ALLUPPERCASE123!")
        assert result.is_valid is False

    def test_no_digit(self, validator):
        result = validator.validate_password("NoDigitsHere!!")
        assert result.is_valid is False

    def test_no_special(self, validator):
        result = validator.validate_password("NoSpecialChar123")
        assert result.is_valid is False


class TestValidateEmail:
    def test_valid(self, validator):
        result = validator.validate_email("user@example.com")
        assert result.is_valid is True

    def test_empty(self, validator):
        result = validator.validate_email("")
        assert result.is_valid is False

    def test_invalid(self, validator):
        result = validator.validate_email("not-email")
        assert result.is_valid is False


class TestSanitizeInput:
    def test_strips_whitespace(self, validator):
        assert validator.sanitize_input("  hello  ") == "hello"

    def test_collapses_spaces(self, validator):
        assert validator.sanitize_input("hello    world") == "hello world"

    def test_non_string(self, validator):
        assert validator.sanitize_input(42) == 42


class TestGetValidator:
    def test_singleton(self):
        v1 = get_validator()
        v2 = get_validator()
        assert v1 is v2

    def test_type(self):
        assert isinstance(get_validator(), Validator)
