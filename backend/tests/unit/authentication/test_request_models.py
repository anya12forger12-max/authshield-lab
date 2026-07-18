"""Tests for Pydantic request models validation."""

import pytest
from pydantic import ValidationError

from app.authentication.domain.models.request_models import (
    RegistrationRequest,
    LoginRequest,
    LogoutRequest,
    PasswordChangeRequest,
    SessionValidationRequest,
    SessionRenewalRequest,
)


class TestRegistrationRequest:
    def test_valid_request(self):
        req = RegistrationRequest(
            username="alice",
            password="SecurePass123!",
            confirm_password="SecurePass123!",
            display_name="Alice Smith",
        )
        assert req.username == "alice"
        assert req.email is None

    def test_valid_with_email(self):
        req = RegistrationRequest(
            username="alice",
            password="SecurePass123!",
            confirm_password="SecurePass123!",
            display_name="Alice",
            email="alice@example.com",
        )
        assert req.email == "alice@example.com"

    def test_invalid_username_special_chars(self):
        with pytest.raises(ValidationError):
            RegistrationRequest(
                username="alice@domain",
                password="SecurePass123!",
                confirm_password="SecurePass123!",
                display_name="Alice",
            )

    def test_username_too_short(self):
        with pytest.raises(ValidationError):
            RegistrationRequest(
                username="ab",
                password="SecurePass123!",
                confirm_password="SecurePass123!",
                display_name="Alice",
            )

    def test_username_too_long(self):
        with pytest.raises(ValidationError):
            RegistrationRequest(
                username="a" * 33,
                password="SecurePass123!",
                confirm_password="SecurePass123!",
                display_name="Alice",
            )

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            RegistrationRequest(
                username="alice",
                password="short",
                confirm_password="short",
                display_name="Alice",
            )

    def test_empty_display_name(self):
        with pytest.raises(ValidationError):
            RegistrationRequest(
                username="alice",
                password="SecurePass123!",
                confirm_password="SecurePass123!",
                display_name="",
            )

    def test_whitespace_stripping(self):
        req = RegistrationRequest(
            username="  alice  ",
            password="SecurePass123!",
            confirm_password="SecurePass123!",
            display_name="  Alice  ",
        )
        assert req.username == "alice"
        assert req.display_name == "Alice"

    def test_underscores_and_hyphens_ok(self):
        req = RegistrationRequest(
            username="alice-smith_01",
            password="SecurePass123!",
            confirm_password="SecurePass123!",
            display_name="Alice",
        )
        assert req.username == "alice-smith_01"


class TestLoginRequest:
    def test_valid_login(self):
        req = LoginRequest(username="alice", password="pass123")
        assert req.username == "alice"
        assert req.remember_me is False

    def test_remember_me(self):
        req = LoginRequest(username="alice", password="pass123", remember_me=True)
        assert req.remember_me is True

    def test_with_device_info(self):
        req = LoginRequest(
            username="alice",
            password="pass123",
            device_id="dev-001",
            platform="linux",
        )
        assert req.device_id == "dev-001"
        assert req.platform == "linux"

    def test_empty_username_rejected(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="", password="pass123")

    def test_empty_password_rejected(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="alice", password="")


class TestLogoutRequest:
    def test_default_values(self):
        req = LogoutRequest()
        assert req.session_id is None
        assert req.terminate_all is False

    def test_with_session_id(self):
        req = LogoutRequest(session_id="sess-123")
        assert req.session_id == "sess-123"

    def test_terminate_all(self):
        req = LogoutRequest(terminate_all=True)
        assert req.terminate_all is True


class TestPasswordChangeRequest:
    def test_valid_change(self):
        req = PasswordChangeRequest(
            current_password="old",
            new_password="newpassword",
            confirm_password="newpassword",
        )
        assert req.current_password == "old"

    def test_new_password_too_short(self):
        with pytest.raises(ValidationError):
            PasswordChangeRequest(
                current_password="old",
                new_password="short",
                confirm_password="short",
            )


class TestSessionValidationRequest:
    def test_valid(self):
        req = SessionValidationRequest(session_id="sess-123")
        assert req.session_id == "sess-123"
        assert req.user_id is None

    def test_with_user_id(self):
        req = SessionValidationRequest(session_id="sess-123", user_id="u1")
        assert req.user_id == "u1"

    def test_empty_session_id_rejected(self):
        with pytest.raises(ValidationError):
            SessionValidationRequest(session_id="")


class TestSessionRenewalRequest:
    def test_valid(self):
        req = SessionRenewalRequest(session_id="sess-123")
        assert req.extend_idle_timeout is True

    def test_without_extend(self):
        req = SessionRenewalRequest(session_id="sess-123", extend_idle_timeout=False)
        assert req.extend_idle_timeout is False
