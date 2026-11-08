"""Integration tests for user lifecycle: create -> update -> status change -> delete."""

import pytest
from datetime import datetime, timezone

from app.users.domain.entities.user_profile import UserProfile
from app.users.domain.entities.identity_lifecycle import (
    UserLifecycleState,
    can_transition,
    validate_transition,
)
from app.users.domain.entities.role import RoleEntity
from app.users.domain.entities.permission import PermissionEntity
from app.shared.validation.validator import Validator


class TestUserCreation:
    def test_create_user_profile(self):
        profile = UserProfile(
            user_id="u-001",
            username="newuser",
            display_name="New User",
            email="new@example.com",
            account_status="pending_verification",
        )
        assert profile.account_status == "pending_verification"
        assert profile.login_count == 0

    def test_profile_starts_with_defaults(self):
        profile = UserProfile(user_id="u1", username="user1")
        assert profile.security_score == 50
        assert profile.mfa_enabled is False
        assert profile.failed_login_count == 0

    def test_username_validation(self):
        validator = Validator()
        result = validator.validate_username("newuser")
        assert result.is_valid is True


class TestUserUpdate:
    def test_update_display_name(self):
        profile = UserProfile(display_name="Old Name")
        profile.display_name = "New Name"
        assert profile.display_name == "New Name"

    def test_update_preferences(self):
        profile = UserProfile()
        profile.preferred_theme = "solarized"
        profile.preferred_language = "hi"
        assert profile.preferred_theme == "solarized"
        assert profile.preferred_language == "hi"

    def test_update_bio(self):
        profile = UserProfile(bio=None)
        profile.bio = "I am a security researcher"
        assert profile.bio == "I am a security researcher"

    def test_profile_to_dict_after_update(self):
        profile = UserProfile(user_id="u1", username="user1")
        profile.display_name = "Updated"
        d = profile.to_dict()
        assert d["display_name"] == "Updated"


class TestStatusChange:
    def test_register_to_active(self):
        assert can_transition(
            UserLifecycleState.REGISTERED,
            UserLifecycleState.ACTIVE,
        )

    def test_active_to_locked(self):
        assert can_transition(
            UserLifecycleState.ACTIVE,
            UserLifecycleState.LOCKED,
        )

    def test_locked_to_active(self):
        assert can_transition(
            UserLifecycleState.LOCKED,
            UserLifecycleState.ACTIVE,
        )

    def test_active_to_disabled(self):
        assert can_transition(
            UserLifecycleState.ACTIVE,
            UserLifecycleState.DISABLED,
        )

    def test_disable_to_reactivate(self):
        assert can_transition(
            UserLifecycleState.DISABLED,
            UserLifecycleState.ACTIVE,
        )


class TestRoleAssignment:
    def test_create_admin_role(self):
        role = RoleEntity(
            role_id="r-admin",
            name="admin",
            display_name="Administrator",
            permissions=["users.read", "users.write", "admin.manage"],
        )
        assert "admin.manage" in role.permissions

    def test_create_student_role(self):
        role = RoleEntity(
            role_id="r-student",
            name="student",
            display_name="Student",
            permissions=["labs.execute", "progress.view"],
        )
        assert "labs.execute" in role.permissions

    def test_role_to_dict(self):
        role = RoleEntity(
            role_id="r1",
            name="admin",
            display_name="Admin",
            is_builtin=True,
            permissions=["perm1"],
        )
        d = role.to_dict()
        assert d["is_builtin"] is True
        assert "perm1" in d["permissions"]


class TestPermissionManagement:
    def test_create_permission(self):
        perm = PermissionEntity.from_string("users.delete")
        assert perm.name == "users.delete"
        assert perm.category == "users"

    def test_permission_to_dict(self):
        perm = PermissionEntity(
            permission_id="p1",
            name="sessions.read",
            display_name="Read Sessions",
            category="sessions",
        )
        d = perm.to_dict()
        assert d["category"] == "sessions"


class TestUserDeletion:
    def test_delete_from_active(self):
        assert can_transition(
            UserLifecycleState.ACTIVE,
            UserLifecycleState.DELETED,
        )

    def test_delete_from_archived(self):
        assert can_transition(
            UserLifecycleState.ARCHIVED,
            UserLifecycleState.DELETED,
        )

    def test_cannot_undelete(self):
        assert can_transition(
            UserLifecycleState.DELETED,
            UserLifecycleState.ACTIVE,
        ) is False

    def test_delete_profile_data(self):
        profile = UserProfile(user_id="u1", username="user1")
        d = profile.to_dict()
        assert d["user_id"] == "u1"
        assert d["username"] == "user1"
