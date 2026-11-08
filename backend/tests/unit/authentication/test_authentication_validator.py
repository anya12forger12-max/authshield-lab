"""Tests for AuthenticationValidator."""

import pytest

from app.authentication.validators.authentication_validator import (
    AuthenticationValidator,
    get_authentication_validator,
)


@pytest.fixture
def validator():
    return AuthenticationValidator()


class TestValidateLoginRequest:
    def test_valid_login(self, validator):
        result = validator.validate_login_request("alice", "SecurePass123!")
        assert result.is_valid is True

    def test_empty_username(self, validator):
        result = validator.validate_login_request("", "password123")
        assert result.is_valid is False
        assert any(e.field_name == "username" for e in result.errors)

    def test_whitespace_username(self, validator):
        result = validator.validate_login_request("   ", "password123")
        assert result.is_valid is False

    def test_empty_password(self, validator):
        result = validator.validate_login_request("alice", "")
        assert result.is_valid is False
        assert any(e.field_name == "password" for e in result.errors)

    def test_both_valid(self, validator):
        result = validator.validate_login_request("bob", "GoodPass1!")
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestValidateRegistrationRequest:
    def test_valid_registration(self, validator):
        result = validator.validate_registration_request(
            "alice", "SecurePass123!", "SecurePass123!", "Alice Smith"
        )
        assert result.is_valid is True

    def test_short_username(self, validator):
        result = validator.validate_registration_request(
            "ab", "SecurePass123!", "SecurePass123!", "Alice"
        )
        assert result.is_valid is False

    def test_long_username(self, validator):
        result = validator.validate_registration_request(
            "a" * 33, "SecurePass123!", "SecurePass123!", "Alice"
        )
        assert result.is_valid is False

    def test_invalid_username_chars(self, validator):
        result = validator.validate_registration_request(
            "alice@smith", "SecurePass123!", "SecurePass123!", "Alice"
        )
        assert result.is_valid is False

    def test_password_mismatch(self, validator):
        result = validator.validate_registration_request(
            "alice", "SecurePass123!", "DifferentPass123!", "Alice"
        )
        assert result.is_valid is False
        assert any(e.code == "mismatch" for e in result.errors)

    def test_empty_display_name(self, validator):
        result = validator.validate_registration_request(
            "alice", "SecurePass123!", "SecurePass123!", ""
        )
        assert result.is_valid is False

    def test_short_password(self, validator):
        result = validator.validate_registration_request(
            "alice", "short", "short", "Alice"
        )
        assert result.is_valid is False

    def test_multiple_errors(self, validator):
        result = validator.validate_registration_request(
            "", "", "", ""
        )
        assert result.is_valid is False
        assert len(result.errors) >= 3


class TestValidatePasswordChange:
    def test_valid_change(self, validator):
        result = validator.validate_password_change(
            "OldPass123!", "NewSecurePass1!", "NewSecurePass1!"
        )
        assert result.is_valid is True

    def test_missing_current(self, validator):
        result = validator.validate_password_change(
            "", "NewPass456!", "NewPass456!"
        )
        assert result.is_valid is False
        assert any(e.field_name == "current_password" for e in result.errors)

    def test_missing_new(self, validator):
        result = validator.validate_password_change(
            "OldPass123!", "", ""
        )
        assert result.is_valid is False
        assert any(e.field_name == "new_password" for e in result.errors)

    def test_same_password(self, validator):
        result = validator.validate_password_change(
            "SamePass123!", "SamePass123!", "SamePass123!"
        )
        assert result.is_valid is False
        assert any(e.code == "same_password" for e in result.errors)

    def test_mismatch_confirmation(self, validator):
        result = validator.validate_password_change(
            "OldPass123!", "NewPass456!", "Different789!"
        )
        assert result.is_valid is False
        assert any(e.code == "mismatch" for e in result.errors)

    def test_short_new_password(self, validator):
        result = validator.validate_password_change(
            "OldPass123!", "short", "short"
        )
        assert result.is_valid is False


class TestGetAuthenticationValidator:
    def test_returns_singleton(self):
        v1 = get_authentication_validator()
        v2 = get_authentication_validator()
        assert v1 is v2

    def test_is_correct_type(self):
        v = get_authentication_validator()
        assert isinstance(v, AuthenticationValidator)
