"""Tests for RoleEntity and PermissionEntity."""

import pytest
from datetime import datetime, timezone

from app.users.domain.entities.role import RoleEntity
from app.users.domain.entities.permission import PermissionEntity


class TestRoleEntity:
    def test_default_values(self):
        role = RoleEntity()
        assert role.role_id == ""
        assert role.name == ""
        assert role.is_builtin is False
        assert role.is_active is True
        assert role.version == 1
        assert role.permissions == []

    def test_to_dict(self):
        role = RoleEntity(
            role_id="r-001",
            name="admin",
            display_name="Administrator",
            description="Full access",
            is_builtin=True,
            permissions=["users.read", "users.write", "admin.manage"],
        )
        d = role.to_dict()
        assert d["role_id"] == "r-001"
        assert d["name"] == "admin"
        assert d["display_name"] == "Administrator"
        assert d["is_builtin"] is True
        assert "users.read" in d["permissions"]
        assert len(d["permissions"]) == 3

    def test_to_dict_serializes_created_at(self):
        now = datetime.now(timezone.utc)
        role = RoleEntity(role_id="r1", name="test", created_at=now)
        d = role.to_dict()
        assert d["created_at"] == now.isoformat()

    def test_permissions_is_copy(self):
        role = RoleEntity(permissions=["perm1", "perm2"])
        perms = role.to_dict()["permissions"]
        assert isinstance(perms, list)
        assert "perm1" in perms


class TestPermissionEntity:
    def test_default_values(self):
        perm = PermissionEntity()
        assert perm.permission_id == ""
        assert perm.name == ""
        assert perm.is_active is True

    def test_to_dict(self):
        perm = PermissionEntity(
            permission_id="p-001",
            name="users.read",
            display_name="Read Users",
            description="Can read user profiles",
            category="users",
        )
        d = perm.to_dict()
        assert d["permission_id"] == "p-001"
        assert d["name"] == "users.read"
        assert d["category"] == "users"
        assert d["is_active"] is True

    def test_from_string(self):
        perm = PermissionEntity.from_string("users.read")
        assert perm.name == "users.read"
        assert perm.display_name == "users.read"
        assert perm.category == "users"
        assert perm.description == "Permission: users.read"

    def test_from_string_single_part(self):
        perm = PermissionEntity.from_string("admin")
        assert perm.name == "admin"
        assert perm.category == "admin"

    def test_from_string_deep_nested(self):
        perm = PermissionEntity.from_string("defenses.policy.manage")
        assert perm.name == "defenses.policy.manage"
        assert perm.category == "defenses"

    def test_to_dict_serializes_created_at(self):
        now = datetime.now(timezone.utc)
        perm = PermissionEntity(permission_id="p1", name="test", created_at=now)
        d = perm.to_dict()
        assert d["created_at"] == now.isoformat()
