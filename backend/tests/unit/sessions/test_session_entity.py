"""Tests for session entity properties."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

from app.shared.models.session import Session


def _make_session(**overrides):
    now = datetime.now(timezone.utc)
    defaults = {
        "id": "sess-001",
        "session_id": "abc-123",
        "user_id": "u-001",
        "created_at": now,
        "updated_at": now,
        "expires_at": now + timedelta(hours=1),
        "last_activity": now,
        "idle_timeout_minutes": 30,
        "status": "active",
        "authentication_method": "password",
        "platform": None,
        "application_version": None,
        "device_id": None,
        "device_name": None,
        "ip_address": "127.0.0.1",
        "remember_me": False,
        "is_trusted": False,
        "security_level": 1,
    }
    defaults.update(overrides)
    session = Session()
    for key, value in defaults.items():
        setattr(session, key, value)
    return session


class TestSessionIsExpired:
    def test_not_expired_when_future(self):
        s = _make_session(expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
        assert s.is_expired is False

    def test_expired_when_past(self):
        s = _make_session(expires_at=datetime.now(timezone.utc) - timedelta(minutes=1))
        assert s.is_expired is True

    def test_not_expired_at_boundary(self):
        future = datetime.now(timezone.utc) + timedelta(seconds=5)
        s = _make_session(expires_at=future)
        assert s.is_expired is False


class TestSessionIsActive:
    def test_active_when_status_active_and_not_expired(self):
        s = _make_session(status="active", expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
        assert s.is_active is True

    def test_not_active_when_expired(self):
        s = _make_session(status="active", expires_at=datetime.now(timezone.utc) - timedelta(minutes=1))
        assert s.is_active is False

    def test_not_active_when_status_not_active(self):
        s = _make_session(status="revoked", expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
        assert s.is_active is False


class TestSessionIsIdle:
    def test_not_idle_when_recent_activity(self):
        s = _make_session(
            last_activity=datetime.now(timezone.utc),
            idle_timeout_minutes=30,
        )
        assert s.is_idle is False

    def test_idle_when_old_activity(self):
        s = _make_session(
            last_activity=datetime.now(timezone.utc) - timedelta(minutes=45),
            idle_timeout_minutes=30,
        )
        assert s.is_idle is True

    def test_idle_at_boundary(self):
        s = _make_session(
            last_activity=datetime.now(timezone.utc) - timedelta(minutes=31),
            idle_timeout_minutes=30,
        )
        assert s.is_idle is True


class TestSessionIdleTimeMinutes:
    def test_recent_activity(self):
        now = datetime.now(timezone.utc)
        s = _make_session(last_activity=now)
        assert s.idle_time_minutes < 1.0

    def test_old_activity(self):
        past = datetime.now(timezone.utc) - timedelta(minutes=45)
        s = _make_session(last_activity=past)
        assert 44 < s.idle_time_minutes < 46


class TestSessionToDict:
    def test_includes_all_fields(self):
        s = _make_session()
        d = s.to_dict()
        assert d["session_id"] == "abc-123"
        assert d["user_id"] == "u-001"
        assert d["status"] == "active"
        assert d["ip_address"] == "127.0.0.1"
        assert d["remember_me"] is False
        assert d["security_level"] == 1
        assert d["is_expired"] is False
        assert d["is_active"] is True

    def test_serializes_dates(self):
        s = _make_session()
        d = s.to_dict()
        assert isinstance(d["expires_at"], str)
        assert isinstance(d["last_activity"], str)

    def test_repr(self):
        s = _make_session()
        r = repr(s)
        assert "sess-001" in r
        assert "abc-123" in r
