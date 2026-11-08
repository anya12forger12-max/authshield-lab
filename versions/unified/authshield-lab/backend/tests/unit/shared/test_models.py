"""Tests for database models: to_dict, to_safe_dict."""

from datetime import UTC, datetime

from app.shared.models.application_settings import ApplicationSettings
from app.shared.models.password_history import PasswordHistory
from app.shared.models.user import User


def _make_user(**overrides):
    now = datetime.now(UTC)
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
    user.last_login = overrides.get("last_login")
    user.last_password_change = overrides.get("last_password_change")
    user.last_failed_login = overrides.get("last_failed_login")
    user.created_by = overrides.get("created_by")
    user.updated_by = overrides.get("updated_by")
    user.deleted_at = overrides.get("deleted_at")
    user.mfa_secret = overrides.get("mfa_secret")
    user.profile_picture = overrides.get("profile_picture")
    user.bio = overrides.get("bio")
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
        now = datetime.now(UTC)
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
        ph.created_at = datetime.now(UTC)
        ph.updated_at = datetime.now(UTC)
        d = ph.to_dict()
        assert "password_hash" not in d

    def test_to_dict_includes_hash_when_requested(self):
        ph = PasswordHistory()
        ph.id = "ph-001"
        ph.user_id = "u-001"
        ph.password_hash = "$argon2id$"
        ph.hash_algorithm = "argon2id"
        ph.version = 1
        ph.created_at = datetime.now(UTC)
        ph.updated_at = datetime.now(UTC)
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
        s.created_at = datetime.now(UTC)
        s.updated_at = datetime.now(UTC)
        d = s.to_dict()
        assert d["value"]["theme"] == "dark"

    def test_to_dict_sensitive_redacts(self):
        s = ApplicationSettings()
        s.id = "s-002"
        s.key = "api.key"
        s.value = {"key": "secret123"}
        s.is_sensitive = True
        s.category = "security"
        s.created_at = datetime.now(UTC)
        s.updated_at = datetime.now(UTC)
        d = s.to_dict()
        assert d["value"] is None

    def test_to_dict_sensitive_with_override(self):
        s = ApplicationSettings()
        s.id = "s-003"
        s.key = "api.key"
        s.value = {"key": "secret123"}
        s.is_sensitive = True
        s.category = "security"
        s.created_at = datetime.now(UTC)
        s.updated_at = datetime.now(UTC)
        d = s.to_dict(include_sensitive=True)
        assert d["value"]["key"] == "secret123"
