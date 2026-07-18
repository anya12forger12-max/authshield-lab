"""Tests for AuthorizationEngine: register policy, evaluate (currently not enforced)."""

import pytest
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AuthorizationPolicy:
    policy_id: str = ""
    name: str = ""
    required_permissions: list[str] = field(default_factory=list)
    allowed_roles: list[str] = field(default_factory=list)
    enabled: bool = True


class AuthorizationEngine:
    def __init__(self):
        self._policies: dict[str, AuthorizationPolicy] = {}

    def register_policy(self, policy: AuthorizationPolicy) -> None:
        self._policies[policy.policy_id] = policy

    def evaluate(self, user_roles: list[str], user_permissions: list[str], required_permissions: list[str]) -> dict:
        missing = [p for p in required_permissions if p not in user_permissions]
        allowed = len(missing) == 0
        return {
            "allowed": allowed,
            "missing_permissions": missing,
            "policies_evaluated": len(self._policies),
        }

    def get_policy(self, policy_id: str) -> Optional[AuthorizationPolicy]:
        return self._policies.get(policy_id)

    def remove_policy(self, policy_id: str) -> bool:
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False

    def count_policies(self) -> int:
        return len(self._policies)


@pytest.fixture
def engine():
    return AuthorizationEngine()


class TestRegisterPolicy:
    def test_register(self, engine):
        p = AuthorizationPolicy(
            policy_id="auth-001",
            name="Admin Access",
            required_permissions=["admin.manage"],
            allowed_roles=["admin"],
        )
        engine.register_policy(p)
        assert engine.count_policies() == 1

    def test_get_policy(self, engine):
        p = AuthorizationPolicy(policy_id="p1", name="Test")
        engine.register_policy(p)
        assert engine.get_policy("p1") is not None
        assert engine.get_policy("p1").name == "Test"

    def test_remove_policy(self, engine):
        engine.register_policy(AuthorizationPolicy(policy_id="p1"))
        assert engine.remove_policy("p1") is True
        assert engine.get_policy("p1") is None
        assert engine.count_policies() == 0

    def test_remove_nonexistent(self, engine):
        assert engine.remove_policy("missing") is False


class TestEvaluate:
    def test_allowed_when_permissions_match(self, engine):
        result = engine.evaluate(
            user_roles=["admin"],
            user_permissions=["admin.manage", "users.read"],
            required_permissions=["users.read"],
        )
        assert result["allowed"] is True
        assert result["missing_permissions"] == []

    def test_denied_when_permission_missing(self, engine):
        result = engine.evaluate(
            user_roles=["user"],
            user_permissions=["users.read"],
            required_permissions=["admin.manage"],
        )
        assert result["allowed"] is False
        assert "admin.manage" in result["missing_permissions"]

    def test_multiple_permissions_required(self, engine):
        result = engine.evaluate(
            user_roles=["user"],
            user_permissions=["users.read"],
            required_permissions=["users.read", "users.write", "admin.manage"],
        )
        assert result["allowed"] is False
        assert len(result["missing_permissions"]) == 2

    def test_empty_required(self, engine):
        result = engine.evaluate(
            user_roles=["user"],
            user_permissions=[],
            required_permissions=[],
        )
        assert result["allowed"] is True

    def test_policies_evaluated_count(self, engine):
        engine.register_policy(AuthorizationPolicy(policy_id="p1"))
        engine.register_policy(AuthorizationPolicy(policy_id="p2"))
        result = engine.evaluate(["user"], ["perm"], ["perm"])
        assert result["policies_evaluated"] == 2
