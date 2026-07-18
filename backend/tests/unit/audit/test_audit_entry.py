"""Tests for AuditEntry entity (AuditEvent model)."""

import pytest
from datetime import datetime, timezone

from app.shared.models.audit_event import AuditEvent


def _make_audit(**overrides):
    now = datetime.now(timezone.utc)
    defaults = {
        "correlation_id": "corr-001",
        "module": "authentication",
        "event_type": "login.success",
        "severity": "info",
        "description": "User logged in successfully",
        "result": "success",
        "ip_address": "127.0.0.1",
    }
    defaults.update(overrides)
    event = AuditEvent(**defaults)
    return event


class TestAuditEventCreation:
    def test_creates_with_defaults(self):
        event = AuditEvent(
            correlation_id="corr-001",
            module="authentication",
            event_type="login",
            description="Test event",
            result="success",
            ip_address="127.0.0.1",
        )
        assert event.correlation_id == "corr-001"
        assert event.result == "success"

    def test_creates_with_all_fields(self):
        event = _make_audit()
        assert event.correlation_id == "corr-001"
        assert event.severity == "info"


class TestAuditEventToDict:
    def test_includes_core_fields(self):
        event = _make_audit()
        d = event.to_dict()
        assert d["correlation_id"] == "corr-001"
        assert d["module"] == "authentication"
        assert d["event_type"] == "login.success"
        assert d["severity"] == "info"
        assert d["result"] == "success"
        assert d["ip_address"] == "127.0.0.1"

    def test_includes_user_info(self):
        event = _make_audit(user_id="u1", username="alice")
        d = event.to_dict()
        assert d["user_id"] == "u1"
        assert d["username"] == "alice"

    def test_includes_resource_info(self):
        event = _make_audit(resource_type="user", resource_id="u-001")
        d = event.to_dict()
        assert d["resource_type"] == "user"
        assert d["resource_id"] == "u-001"

    def test_includes_state_changes(self):
        event = _make_audit(
            previous_state={"status": "active"},
            new_state={"status": "locked"},
        )
        d = event.to_dict()
        assert d["previous_state"]["status"] == "active"
        assert d["new_state"]["status"] == "locked"


class TestAuditEventImmutability:
    def test_event_fields_can_be_set_at_creation(self):
        event = _make_audit(description="Immutable test")
        assert event.description == "Immutable test"

    def test_repr(self):
        event = _make_audit()
        r = repr(event)
        assert "login.success" in r
        assert "info" in r
