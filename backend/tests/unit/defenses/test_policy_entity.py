"""Tests for SecurityPolicy, PolicyDecision, PolicyConfiguration, status transitions."""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone


class PolicyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"
    ARCHIVED = "archived"


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"
    LOG_ONLY = "log_only"


VALID_POLICY_TRANSITIONS = {
    PolicyStatus.DRAFT: {PolicyStatus.ACTIVE, PolicyStatus.ARCHIVED},
    PolicyStatus.ACTIVE: {PolicyStatus.DISABLED, PolicyStatus.ARCHIVED},
    PolicyStatus.DISABLED: {PolicyStatus.ACTIVE, PolicyStatus.ARCHIVED},
    PolicyStatus.ARCHIVED: set(),
}


def can_transition_policy(current: PolicyStatus, target: PolicyStatus) -> bool:
    return target in VALID_POLICY_TRANSITIONS.get(current, set())


@dataclass
class SecurityPolicy:
    policy_id: str = ""
    name: str = ""
    description: str = ""
    status: PolicyStatus = PolicyStatus.DRAFT
    decision: PolicyDecision = PolicyDecision.ALLOW
    priority: int = 0
    rules: list = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    enabled: bool = True

    def to_dict(self) -> dict:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "decision": self.decision.value,
            "priority": self.priority,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class PolicyConfiguration:
    max_policies: int = 100
    evaluation_timeout_ms: int = 50
    log_decisions: bool = True
    default_decision: PolicyDecision = PolicyDecision.ALLOW
    enable_caching: bool = True
    cache_ttl_seconds: int = 300

    def to_dict(self) -> dict:
        return {
            "max_policies": self.max_policies,
            "evaluation_timeout_ms": self.evaluation_timeout_ms,
            "log_decisions": self.log_decisions,
            "default_decision": self.default_decision.value,
            "enable_caching": self.enable_caching,
            "cache_ttl_seconds": self.cache_ttl_seconds,
        }


class TestPolicyStatusTransitions:
    def test_draft_to_active(self):
        assert can_transition_policy(PolicyStatus.DRAFT, PolicyStatus.ACTIVE)

    def test_draft_to_archived(self):
        assert can_transition_policy(PolicyStatus.DRAFT, PolicyStatus.ARCHIVED)

    def test_active_to_disabled(self):
        assert can_transition_policy(PolicyStatus.ACTIVE, PolicyStatus.DISABLED)

    def test_active_to_archived(self):
        assert can_transition_policy(PolicyStatus.ACTIVE, PolicyStatus.ARCHIVED)

    def test_disabled_to_active(self):
        assert can_transition_policy(PolicyStatus.DISABLED, PolicyStatus.ACTIVE)

    def test_disabled_to_archived(self):
        assert can_transition_policy(PolicyStatus.DISABLED, PolicyStatus.ARCHIVED)

    def test_archived_has_no_transitions(self):
        assert VALID_POLICY_TRANSITIONS[PolicyStatus.ARCHIVED] == set()

    def test_draft_to_disabled_invalid(self):
        assert can_transition_policy(PolicyStatus.DRAFT, PolicyStatus.DISABLED) is False

    def test_active_to_draft_invalid(self):
        assert can_transition_policy(PolicyStatus.ACTIVE, PolicyStatus.DRAFT) is False


class TestSecurityPolicy:
    def test_default_values(self):
        p = SecurityPolicy()
        assert p.status == PolicyStatus.DRAFT
        assert p.decision == PolicyDecision.ALLOW
        assert p.priority == 0
        assert p.enabled is True

    def test_to_dict(self):
        p = SecurityPolicy(
            policy_id="pol-001",
            name="Rate Limit",
            description="Limit login attempts",
            status=PolicyStatus.ACTIVE,
            decision=PolicyDecision.DENY,
            priority=10,
        )
        d = p.to_dict()
        assert d["policy_id"] == "pol-001"
        assert d["name"] == "Rate Limit"
        assert d["status"] == "active"
        assert d["decision"] == "deny"
        assert d["priority"] == 10

    def test_with_rules(self):
        p = SecurityPolicy(rules=["rule1", "rule2"])
        assert len(p.rules) == 2


class TestPolicyDecision:
    def test_all_decisions(self):
        assert PolicyDecision.ALLOW.value == "allow"
        assert PolicyDecision.DENY.value == "deny"
        assert PolicyDecision.CHALLENGE.value == "challenge"
        assert PolicyDecision.LOG_ONLY.value == "log_only"


class TestPolicyConfiguration:
    def test_defaults(self):
        config = PolicyConfiguration()
        assert config.max_policies == 100
        assert config.evaluation_timeout_ms == 50
        assert config.log_decisions is True
        assert config.enable_caching is True

    def test_to_dict(self):
        config = PolicyConfiguration(max_policies=50, cache_ttl_seconds=600)
        d = config.to_dict()
        assert d["max_policies"] == 50
        assert d["cache_ttl_seconds"] == 600
        assert d["default_decision"] == "allow"

    def test_custom_config(self):
        config = PolicyConfiguration(
            log_decisions=False, default_decision=PolicyDecision.DENY
        )
        d = config.to_dict()
        assert d["log_decisions"] is False
        assert d["default_decision"] == "deny"
