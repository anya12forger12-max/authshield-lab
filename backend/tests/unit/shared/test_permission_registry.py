"""Tests for PermissionRegistry: register, get, search, categories."""

import pytest
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Permission:
    name: str = ""
    display_name: str = ""
    category: str = ""
    description: str = ""
    is_active: bool = True


class PermissionRegistry:
    def __init__(self):
        self._permissions: dict[str, Permission] = {}

    def register(self, permission: Permission) -> None:
        self._permissions[permission.name] = permission

    def get(self, name: str) -> Optional[Permission]:
        return self._permissions.get(name)

    def search(self, query: str = "", category: str = "") -> list[Permission]:
        results = list(self._permissions.values())
        if category:
            results = [p for p in results if p.category == category]
        if query:
            results = [p for p in results if query.lower() in p.name.lower()]
        return results

    def get_categories(self) -> list[str]:
        return sorted(set(p.category for p in self._permissions.values() if p.category))

    def count(self) -> int:
        return len(self._permissions)

    def get_by_category(self, category: str) -> list[Permission]:
        return [p for p in self._permissions.values() if p.category == category]


@pytest.fixture
def registry():
    return PermissionRegistry()


@pytest.fixture
def populated_registry():
    reg = PermissionRegistry()
    reg.register(Permission(name="users.read", display_name="Read Users", category="users"))
    reg.register(Permission(name="users.write", display_name="Write Users", category="users"))
    reg.register(Permission(name="sessions.read", display_name="Read Sessions", category="sessions"))
    reg.register(Permission(name="admin.manage", display_name="Admin Manage", category="admin"))
    return reg


class TestRegister:
    def test_register(self, registry):
        registry.register(Permission(name="test.perm", category="test"))
        assert registry.count() == 1

    def test_overwrite(self, registry):
        registry.register(Permission(name="perm", display_name="First"))
        registry.register(Permission(name="perm", display_name="Second"))
        assert registry.count() == 1
        assert registry.get("perm").display_name == "Second"


class TestGet:
    def test_get_existing(self, populated_registry):
        p = populated_registry.get("users.read")
        assert p is not None
        assert p.display_name == "Read Users"

    def test_get_nonexistent(self, populated_registry):
        assert populated_registry.get("missing") is None


class TestSearch:
    def test_search_all(self, populated_registry):
        assert len(populated_registry.search()) == 4

    def test_search_by_name(self, populated_registry):
        results = populated_registry.search(query="user")
        assert len(results) == 2

    def test_search_by_category(self, populated_registry):
        results = populated_registry.search(category="admin")
        assert len(results) == 1

    def test_search_combined(self, populated_registry):
        results = populated_registry.search(query="read", category="users")
        assert len(results) == 1


class TestCategories:
    def test_get_categories(self, populated_registry):
        cats = populated_registry.get_categories()
        assert "users" in cats
        assert "sessions" in cats
        assert "admin" in cats

    def test_get_by_category(self, populated_registry):
        users = populated_registry.get_by_category("users")
        assert len(users) == 2

    def test_empty_registry_categories(self, registry):
        assert registry.get_categories() == []
