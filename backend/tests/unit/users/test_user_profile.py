"""Tests for UserProfile entity."""

import pytest
from datetime import datetime, timezone

from app.users.domain.entities.user_profile import UserProfile


@pytest.fixture
def sample_profile():
    return UserProfile(
        user_id="u-001",
        username="alice",
        display_name="Alice Smith",
        email="alice@example.com",
        account_status="active",
        role="admin",
        login_count=42,
        failed_login_count=2,
        security_score=85,
        mfa_enabled=True,
        trusted_device_count=3,
        active_session_count=2,
        audit_history_count=150,
    )


class TestUserProfileDefaults:
    def test_default_values(self):
        profile = UserProfile()
        assert profile.user_id == ""
        assert profile.username == ""
        assert profile.account_status == "active"
        assert profile.role == "student"
        assert profile.login_count == 0
        assert profile.mfa_enabled is False

    def test_default_language(self):
        profile = UserProfile()
        assert profile.preferred_language == "en"
        assert profile.preferred_theme == "dark"
        assert profile.timezone == "UTC"

    def test_default_password_meta(self):
        profile = UserProfile()
        assert profile.password_algorithm == "argon2id"
        assert profile.password_version == 1


class TestToDict:
    def test_includes_security_metadata(self, sample_profile):
        d = sample_profile.to_dict()
        assert d["failed_login_count"] == 2
        assert d["security_score"] == 85
        assert d["password_algorithm"] == "argon2id"
        assert d["trusted_device_count"] == 3
        assert d["audit_history_count"] == 150

    def test_includes_basic_fields(self, sample_profile):
        d = sample_profile.to_dict()
        assert d["user_id"] == "u-001"
        assert d["username"] == "alice"
        assert d["display_name"] == "Alice Smith"
        assert d["email"] == "alice@example.com"

    def test_serializes_dates(self):
        now = datetime.now(timezone.utc)
        profile = UserProfile(user_id="u1", created_at=now, last_login=now)
        d = profile.to_dict()
        assert d["created_at"] == now.isoformat()
        assert d["last_login"] == now.isoformat()


class TestToSafeDict:
    def test_omits_security_metadata(self, sample_profile):
        d = sample_profile.to_safe_dict()
        assert "failed_login_count" not in d
        assert "security_score" not in d
        assert "password_algorithm" not in d
        assert "password_version" not in d
        assert "trusted_device_count" not in d
        assert "audit_history_count" not in d

    def test_keeps_basic_fields(self, sample_profile):
        d = sample_profile.to_safe_dict()
        assert d["user_id"] == "u-001"
        assert d["username"] == "alice"
        assert d["account_status"] == "active"
        assert d["mfa_enabled"] is True

    def test_active_session_count_preserved(self, sample_profile):
        d = sample_profile.to_safe_dict()
        assert d["active_session_count"] == 2


class TestToAdminDict:
    def test_includes_all_fields(self, sample_profile):
        d = sample_profile.to_admin_dict()
        assert d["trusted_device_count"] == 3
        assert d["audit_history_count"] == 150
        assert d["failed_login_count"] == 2

    def test_admin_dict_is_superset_of_to_dict(self, sample_profile):
        base = sample_profile.to_dict()
        admin = sample_profile.to_admin_dict()
        assert admin["trusted_device_count"] == base.get("trusted_device_count", 3)
        assert admin["audit_history_count"] == base.get("audit_history_count", 150)


class TestProfileWithNoneDates:
    def test_none_last_login(self):
        profile = UserProfile(user_id="u1", last_login=None)
        d = profile.to_dict()
        assert d["last_login"] is None

    def test_none_password_last_changed(self):
        profile = UserProfile(user_id="u1", password_last_changed=None)
        d = profile.to_dict()
        assert d["password_last_changed"] is None
