"""Tests for Pydantic response models."""

import pytest
from datetime import datetime, timezone

from app.authentication.domain.models.response_models import (
    AuthenticationResponse,
    RegistrationResponse,
    LoginResponse,
    LogoutResponse,
    SessionResponse,
)


class TestAuthenticationResponse:
    def test_success_response(self):
        resp = AuthenticationResponse(success=True, message="OK")
        assert resp.success is True
        assert resp.message == "OK"
        assert resp.error_code is None

    def test_error_response(self):
        resp = AuthenticationResponse(
            success=False,
            message="Invalid credentials",
            error_code="INVALID_CREDENTIALS",
        )
        assert resp.success is False
        assert resp.error_code == "INVALID_CREDENTIALS"

    def test_default_timestamp(self):
        resp = AuthenticationResponse(success=True)
        assert isinstance(resp.timestamp, datetime)

    def test_with_metadata(self):
        resp = AuthenticationResponse(
            success=True, metadata={"source": "api"}
        )
        assert resp.metadata["source"] == "api"

    def test_correlation_id_default(self):
        resp = AuthenticationResponse(success=True)
        assert resp.correlation_id == ""


class TestRegistrationResponse:
    def test_with_user_details(self):
        resp = RegistrationResponse(
            success=True,
            message="Registration successful",
            user_id="u-001",
            username="alice",
        )
        assert resp.user_id == "u-001"
        assert resp.username == "alice"

    def test_defaults(self):
        resp = RegistrationResponse(success=True)
        assert resp.user_id is None
        assert resp.username is None


class TestLoginResponse:
    def test_with_tokens(self):
        resp = LoginResponse(
            success=True,
            access_token="eyJ...",
            expires_in=1800,
            session_id="s-001",
        )
        assert resp.access_token == "eyJ..."
        assert resp.token_type == "bearer"
        assert resp.expires_in == 1800

    def test_with_user_data(self):
        user_data = {"id": "u1", "username": "alice", "role": "admin"}
        resp = LoginResponse(success=True, user=user_data)
        assert resp.user["username"] == "alice"

    def test_default_token_type(self):
        resp = LoginResponse(success=True)
        assert resp.token_type == "bearer"


class TestLogoutResponse:
    def test_session_terminated(self):
        resp = LogoutResponse(success=True, session_terminated=True)
        assert resp.session_terminated is True

    def test_default_not_terminated(self):
        resp = LogoutResponse(success=True)
        assert resp.session_terminated is False


class TestSessionResponse:
    def test_valid_session_response(self):
        now = datetime.now(timezone.utc)
        resp = SessionResponse(
            session_id="s-001",
            user_id="u-001",
            created_at=now,
            expires_at=now,
            last_activity=now,
            status="active",
        )
        assert resp.session_id == "s-001"
        assert resp.status == "active"
        assert resp.is_current is False

    def test_with_optional_fields(self):
        now = datetime.now(timezone.utc)
        resp = SessionResponse(
            session_id="s-001",
            user_id="u-001",
            created_at=now,
            expires_at=now,
            last_activity=now,
            status="active",
            authentication_method="password",
            platform="linux",
            is_current=True,
        )
        assert resp.authentication_method == "password"
        assert resp.platform == "linux"
        assert resp.is_current is True
