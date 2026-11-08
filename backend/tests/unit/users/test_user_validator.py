"""Tests for IdentityValidator."""

import pytest

from app.shared.validation.validator import Validator, ValidationResult


@pytest.fixture
def validator():
    return Validator()


class TestValidateUsername:
    def test_valid_username(self, validator):
        result = validator.validate_username("alice")
        assert result.is_valid is True

    def test_minimum_length(self, validator):
        result = validator.validate_username("ab")
        assert result.is_valid is False
        assert any(e.code == "MIN_LENGTH" for e in result.errors)

    def test_maximum_length(self, validator):
        result = validator.validate_username("a" * 33)
        assert result.is_valid is False
        assert any(e.code == "MAX_LENGTH" for e in result.errors)

    def test_invalid_characters(self, validator):
        result = validator.validate_username("alice@domain")
        assert result.is_valid is False
        assert any(e.code == "INVALID_CHARS" for e in result.errors)

    def test_dots_allowed(self, validator):
        result = validator.validate_username("alice.smith")
        assert result.is_valid is True

    def test_hyphens_allowed(self, validator):
        result = validator.validate_username("alice-smith")
        assert result.is_valid is True

    def test_underscores_allowed(self, validator):
        result = validator.validate_username("alice_smith")
        assert result.is_valid is True

    def test_empty_username(self, validator):
        result = validator.validate_username("")
        assert result.is_valid is False
        assert any(e.code == "REQUIRED" for e in result.errors)

    def test_whitespace_only(self, validator):
        result = validator.validate_username("   ")
        assert result.is_valid is False

    def test_strips_whitespace(self, validator):
        result = validator.validate_username("  alice  ")
        assert result.is_valid is True


class TestValidatePassword:
    def test_valid_password(self, validator):
        result = validator.validate_password("SecurePass123!")
        assert result.is_valid is True

    def test_empty_password(self, validator):
        result = validator.validate_password("")
        assert result.is_valid is False

    def test_too_short(self, validator):
        result = validator.validate_password("Short1!")
        assert result.is_valid is False
        assert any(e.code == "MIN_LENGTH" for e in result.errors)

    def test_no_uppercase(self, validator):
        result = validator.validate_password("alllowercase123!")
        assert result.is_valid is False
        assert any(e.code == "UPPERCASE" for e in result.errors)

    def test_no_lowercase(self, validator):
        result = validator.validate_password("ALLUPPERCASE123!")
        assert result.is_valid is False
        assert any(e.code == "LOWERCASE" for e in result.errors)

    def test_no_digit(self, validator):
        result = validator.validate_password("NoDigitsHere!!")
        assert result.is_valid is False
        assert any(e.code == "NUMBER" for e in result.errors)

    def test_no_special(self, validator):
        result = validator.validate_password("NoSpecialChar123")
        assert result.is_valid is False
        assert any(e.code == "SPECIAL" for e in result.errors)

    def test_custom_policy_relaxed(self, validator):
        result = validator.validate_password("short1!", policy={"min_length": 4, "require_special": False, "require_uppercase": False})
        assert result.is_valid is True


class TestValidateEmail:
    def test_valid_email(self, validator):
        result = validator.validate_email("user@example.com")
        assert result.is_valid is True

    def test_empty_email(self, validator):
        result = validator.validate_email("")
        assert result.is_valid is False

    def test_invalid_format(self, validator):
        result = validator.validate_email("not-an-email")
        assert result.is_valid is False
        assert any(e.code == "INVALID" for e in result.errors)

    def test_strips_whitespace(self, validator):
        result = validator.validate_email("  user@example.com  ")
        assert result.is_valid is True

    def test_nested_at_sign(self, validator):
        result = validator.validate_email("user@@example.com")
        assert result.is_valid is False


class TestSanitizeInput:
    def test_strips_whitespace(self, validator):
        assert validator.sanitize_input("  hello  ") == "hello"

    def test_collapses_spaces(self, validator):
        assert validator.sanitize_input("hello    world") == "hello world"

    def test_non_string_returns_as_is(self, validator):
        assert validator.sanitize_input(42) == 42

    def test_tabs_and_newlines(self, validator):
        result = validator.sanitize_input("hello\t\tworld\n")
        assert result == "hello world"


class TestNormalizeUsername:
    def test_lowercases(self, validator):
        assert validator.normalize_username("Alice") == "alice"

    def test_collapses_separators(self, validator):
        assert validator.normalize_username("alice_smith-01") == "alice.smith.01"

    def test_strips_dots(self, validator):
        assert validator.normalize_username("alice.") == "alice"

    def test_multiple_dots_collapsed(self, validator):
        assert validator.normalize_username("alice..smith") == "alice.smith"
