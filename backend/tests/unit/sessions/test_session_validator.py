"""Tests for session validators."""

import pytest

from app.shared.validation.validator import Validator, ValidationResult


@pytest.fixture
def validator():
    return Validator()


class TestSessionValidation:
    def test_validate_required_non_none(self, validator):
        result = validator.validate_required("value", "field")
        assert result.is_valid is True

    def test_validate_required_none(self, validator):
        result = validator.validate_required(None, "field")
        assert result.is_valid is False

    def test_validate_required_empty_string(self, validator):
        result = validator.validate_required("", "field")
        assert result.is_valid is False

    def test_validate_required_whitespace(self, validator):
        result = validator.validate_required("   ", "field")
        assert result.is_valid is False

    def test_validate_length_valid(self, validator):
        result = validator.validate_length("hello", "session_id", min_len=3, max_len=10)
        assert result.is_valid is True

    def test_validate_length_too_short(self, validator):
        result = validator.validate_length("ab", "session_id", min_len=5)
        assert result.is_valid is False

    def test_validate_length_too_long(self, validator):
        result = validator.validate_length("a" * 100, "session_id", max_len=50)
        assert result.is_valid is False

    def test_validate_length_non_string(self, validator):
        result = validator.validate_length(123, "field")
        assert result.is_valid is False
        assert any(e.code == "TYPE" for e in result.errors)

    def test_validate_format_valid(self, validator):
        result = validator.validate_format("abc-123", "session_id", r"^[a-z]+-\d+$")
        assert result.is_valid is True

    def test_validate_format_invalid(self, validator):
        result = validator.validate_format("ABC", "session_id", r"^[a-z]+$")
        assert result.is_valid is False

    def test_validate_format_custom_message(self, validator):
        result = validator.validate_format("BAD123", "token", r"^[a-z]+$", "Invalid token format")
        assert result.is_valid is False
        assert result.errors[0].message == "Invalid token format"
