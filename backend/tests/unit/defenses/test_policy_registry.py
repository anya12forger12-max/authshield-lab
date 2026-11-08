"""Tests for PolicyRegistry: register, unregister, search, enable, disable."""

import pytest
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Policy:
    policy_id: str = ""
    name: str = ""
    enabled: bool = True
    tags: list = field(default_factory=list)


class PolicyRegistry:
    def __init__(self):
        self._policies: dict[str, Policy] = {}

    def register(self, policy: Policy) -> None:
        self._policies[policy.policy_id] = policy

    def unregister(self, policy_id: str) -> bool:
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False

    def get(self, policy_id: str) -> Optional[Policy]:
        return self._policies.get(policy_id)

    def search(self, query: str = "", enabled_only: bool = False) -> list[Policy]:
        results = list(self._policies.values())
        if enabled_only:
            results = [p for p in results if p.enabled]
        if query:
            results = [p for p in results if query.lower() in p.name.lower()]
        return results

    def enable(self, policy_id: str) -> bool:
        policy = self._policies.get(policy_id)
        if policy is None:
            return False
        policy.enabled = True
        return True

    def disable(self, policy_id: str) -> bool:
        policy = self._policies.get(policy_id)
        if policy is None:
            return False
        policy.enabled = False
        return True

    def count(self, enabled_only: bool = False) -> int:
        if enabled_only:
            return sum(1 for p in self._policies.values() if p.enabled)
        return len(self._policies)

    def list_all(self) -> list[Policy]:
        return list(self._policies.values())


@pytest.fixture
def registry():
    return PolicyRegistry()


@pytest.fixture
def populated_registry():
    reg = PolicyRegistry()
    reg.register(Policy(policy_id="p1", name="Rate Limit", tags=["security"]))
    reg.register(Policy(policy_id="p2", name="IP Block", enabled=False, tags=["network"]))
    reg.register(Policy(policy_id="p3", name="Rate Limit Advanced", tags=["security", "advanced"]))
    return reg


class TestRegister:
    def test_register_single(self, registry):
        p = Policy(policy_id="p1", name="Test Policy")
        registry.register(p)
        assert registry.count() == 1

    def test_register_overwrites_existing(self, registry):
        registry.register(Policy(policy_id="p1", name="First"))
        registry.register(Policy(policy_id="p1", name="Second"))
        assert registry.count() == 1
        assert registry.get("p1").name == "Second"


class TestUnregister:
    def test_unregister_existing(self, populated_registry):
        assert populated_registry.unregister("p1") is True
        assert populated_registry.get("p1") is None
        assert populated_registry.count() == 2

    def test_unregister_nonexistent(self, registry):
        assert registry.unregister("nonexistent") is False


class TestGet:
    def test_get_existing(self, populated_registry):
        p = populated_registry.get("p1")
        assert p is not None
        assert p.name == "Rate Limit"

    def test_get_nonexistent(self, populated_registry):
        assert populated_registry.get("missing") is None


class TestSearch:
    def test_search_all(self, populated_registry):
        results = populated_registry.search()
        assert len(results) == 3

    def test_search_by_name(self, populated_registry):
        results = populated_registry.search(query="Rate")
        assert len(results) == 2

    def test_search_enabled_only(self, populated_registry):
        results = populated_registry.search(enabled_only=True)
        assert len(results) == 2

    def test_search_combined(self, populated_registry):
        results = populated_registry.search(query="Rate", enabled_only=True)
        assert len(results) == 2

    def test_search_no_results(self, populated_registry):
        results = populated_registry.search(query="nonexistent")
        assert len(results) == 0


class TestEnableDisable:
    def test_disable(self, populated_registry):
        assert populated_registry.disable("p1") is True
        assert populated_registry.get("p1").enabled is False

    def test_enable(self, populated_registry):
        assert populated_registry.enable("p2") is True
        assert populated_registry.get("p2").enabled is True

    def test_disable_nonexistent(self, registry):
        assert registry.disable("missing") is False

    def test_enable_nonexistent(self, registry):
        assert registry.enable("missing") is False

    def test_count_enabled(self, populated_registry):
        assert populated_registry.count(enabled_only=True) == 2
        populated_registry.disable("p1")
        assert populated_registry.count(enabled_only=True) == 1


class TestListAll:
    def test_list_all(self, populated_registry):
        all_policies = populated_registry.list_all()
        assert len(all_policies) == 3
