"""Tests for database models: to_dict, to_safe_dict."""

import pytest
from datetime import datetime, timezone

from app.shared.models.user import User
from app.shared.models.session import Session
from app.shared.models.audit_event import AuditEvent
from app.shared.models.role import Role, Permission
from app.shared.models.device import Device
from app.shared.models.password_history import PasswordHistory
from app.shared.models.user_preference import UserPreference
from app.shared.models.authentication_attempt import AuthenticationAttempt
from app.shared.models.application_settings import ApplicationSettings


def _make_user(**overrides):
    now = datetime.now(timezone.utc)
    defaults = {
        "username": "alice",
        "display_name": "Alice Smith",
        "email": "alice@example.com",
        "password_hash": "$argon2id$hashed",
        "hash_algorithm": "argon2id",
        "account_status": "active",
        "role": "student",
        "is_deleted": False,
        "mfa_enabled": False,
        "security_score": 50,
        "login_count": 0,
        "preferred_language": "en",
        "preferred_theme": "dark",
        "timezone": "UTC",
        "failed_login_count": 0,
        "password_version": 1,
    }
    defaults.update(overrides)
    user = User()
    for key, value in defaults.items():
        setattr(user, key, value)
    user.id = overrides.get("id", "u-001")
    user.created_at = overrides.get("created_at", now)
    user.updated_at = overrides.get("updated_at", now)
    user.last_login = overrides.get("last_login", None)
    user.last_password_change = overrides.get("last_password_change", None)
    user.last_failed_login = overrides.get("last_failed_login", None)
    user.created_by = overrides.get("created_by", None)
    user.updated_by = overrides.get("updated_by", None)
    user.deleted_at = overrides.get("deleted_at", None)
    user.mfa_secret = overrides.get("mfa_secret", None)
    user.profile_picture = overrides.get("profile_picture", None)
    user.bio = overrides.get("bio", None)
    return user


class TestUserModel:
    def test_to_dict_excludes_sensitive(self):
        user = _make_user()
        d = user.to_dict()
        assert "password_hash" not in d
        assert "mfa_secret" not in d
        assert "failed_login_count" not in d

    def test_to_dict_includes_safe_fields(self):
        user = _make_user()
        d = user.to_dict()
        assert d["username"] == "alice"
        assert d["email"] == "alice@example.com"
        assert d["account_status"] == "active"

    def test_to_dict_with_sensitive(self):
        user = _make_user(password_hash="$argon2id$", mfa_secret="secret")
        d = user.to_dict(include_sensitive=True)
        assert d["password_hash"] == "$argon2id$"
        assert d["mfa_secret"] == "secret"
        assert d["failed_login_count"] == 0

    def test_to_safe_dict(self):
        user = _make_user(password_hash="$argon2id$")
        d = user.to_safe_dict()
        assert "password_hash" not in d
        assert "mfa_secret" not in d

    def test_serializes_dates(self):
        now = datetime.now(timezone.utc)
        user = _make_user(created_at=now, updated_at=now, last_login=now)
        d = user.to_dict()
        assert d["created_at"] == now.isoformat()
        assert d["last_login"] == now.isoformat()

    def test_none_dates(self):
        user = _make_user(last_login=None, last_password_change=None)
        d = user.to_dict()
        assert d["last_login"] is None
        assert d["last_password_change"] is None

    def test_repr(self):
        user = _make_user()
        r = repr(user)
        assert "alice" in r
        assert "active" in r


class TestPasswordHistoryModel:
    def test_to_dict_excludes_hash(self):
        ph = PasswordHistory()
        ph.id = "ph-001"
        ph.user_id = "u-001"
        ph.hash_algorithm = "argon2id"
        ph.version = 1
        ph.created_at = datetime.now(timezone.utc)
        ph.updated_at = datetime.now(timezone.utc)
        d = ph.to_dict()
        assert "password_hash" not in d

    def test_to_dict_includes_hash_when_requested(self):
        ph = PasswordHistory()
        ph.id = "ph-001"
        ph.user_id = "u-001"
        ph.password_hash = "$argon2id$"
        ph.hash_algorithm = "argon2id"
        ph.version = 1
        ph.created_at = datetime.now(timezone.utc)
        ph.updated_at = datetime.now(timezone.utc)
        d = ph.to_dict(include_hash=True)
        assert d["password_hash"] == "$argon2id$"


class TestApplicationSettingsModel:
    def test_to_dict_non_sensitive(self):
        s = ApplicationSettings()
        s.id = "s-001"
        s.key = "theme.default"
        s.value = {"theme": "dark"}
        s.value_type = "json"
        s.is_sensitive = False
        s.category = "ui"
        s.environment = "all"
        s.created_at = datetime.now(timezone.utc)
        s.updated_at = datetime.now(timezone.utc)
        d = s.to_dict()
        assert d["value"]["theme"] == "dark"

    def test_to_dict_sensitive_redacts(self):
        s = ApplicationSettings()
        s.id = "s-002"
        s.key = "api.key"
        s.value = {"key": "secret123"}
        s.is_sensitive = True
        s.category = "security"
        s.created_at = datetime.now(timezone.utc)
        s.updated_at = datetime.now(timezone.utc)
        d = s.to_dict()
        assert d["value"] is None

    def test_to_dict_sensitive_with_override(self):
        s = ApplicationSettings()
        s.id = "s-003"
        s.key = "api.key"
        s.value = {"key": "secret123"}
        s.is_sensitive = True
        s.category = "security"
        s.created_at = datetime.now(timezone.utc)
        s.updated_at = datetime.now(timezone.utc)
        d = s.to_dict(include_sensitive=True)
        assert d["value"]["key"] == "secret123"
