"""Tests for user identity lifecycle transitions."""

import pytest

from app.users.domain.entities.identity_lifecycle import (
    UserLifecycleState,
    VALID_LIFECYCLE_TRANSITIONS,
    LifecycleTransition,
    can_transition,
    validate_transition,
)


class TestUserLifecycleState:
    def test_all_states_are_strings(self):
        for state in UserLifecycleState:
            assert isinstance(state.value, str)

    def test_key_state_values(self):
        assert UserLifecycleState.ACTIVE.value == "active"
        assert UserLifecycleState.LOCKED.value == "locked"
        assert UserLifecycleState.DELETED.value == "deleted"


class TestValidTransitions:
    def test_anonymous_to_registered(self):
        assert can_transition(UserLifecycleState.ANONYMOUS, UserLifecycleState.REGISTERED)

    def test_registered_to_active(self):
        assert can_transition(UserLifecycleState.REGISTERED, UserLifecycleState.ACTIVE)

    def test_active_to_authenticated(self):
        assert can_transition(UserLifecycleState.ACTIVE, UserLifecycleState.AUTHENTICATED)

    def test_authenticated_to_active_session(self):
        assert can_transition(UserLifecycleState.AUTHENTICATED, UserLifecycleState.ACTIVE_SESSION)

    def test_active_session_to_idle(self):
        assert can_transition(UserLifecycleState.ACTIVE_SESSION, UserLifecycleState.IDLE)

    def test_idle_to_logged_out(self):
        assert can_transition(UserLifecycleState.IDLE, UserLifecycleState.LOGGED_OUT)

    def test_active_to_locked(self):
        assert can_transition(UserLifecycleState.ACTIVE, UserLifecycleState.LOCKED)

    def test_locked_to_active(self):
        assert can_transition(UserLifecycleState.LOCKED, UserLifecycleState.ACTIVE)

    def test_deleted_has_no_transitions(self):
        assert VALID_LIFECYCLE_TRANSITIONS[UserLifecycleState.DELETED] == set()

    def test_active_to_disabled(self):
        assert can_transition(UserLifecycleState.ACTIVE, UserLifecycleState.DISABLED)

    def test_active_to_suspended(self):
        assert can_transition(UserLifecycleState.ACTIVE, UserLifecycleState.SUSPENDED)

    def test_active_to_archived(self):
        assert can_transition(UserLifecycleState.ACTIVE, UserLifecycleState.ARCHIVED)


class TestInvalidTransitions:
    def test_anonymous_to_active_invalid(self):
        assert can_transition(UserLifecycleState.ANONYMOUS, UserLifecycleState.ACTIVE) is False

    def test_active_to_anonymous_invalid(self):
        assert can_transition(UserLifecycleState.ACTIVE, UserLifecycleState.ANONYMOUS) is False

    def test_deleted_to_anything_invalid(self):
        for state in UserLifecycleState:
            if state != UserLifecycleState.DELETED:
                assert can_transition(UserLifecycleState.DELETED, state) is False

    def test_locked_to_authenticated_invalid(self):
        assert can_transition(UserLifecycleState.LOCKED, UserLifecycleState.AUTHENTICATED) is False

    def test_suspended_to_authenticated_invalid(self):
        assert can_transition(UserLifecycleState.SUSPENDED, UserLifecycleState.AUTHENTICATED) is False

    def test_logged_out_to_active_session_invalid(self):
        assert can_transition(UserLifecycleState.LOGGED_OUT, UserLifecycleState.ACTIVE_SESSION) is False


class TestValidateTransition:
    def test_valid_does_not_raise(self):
        validate_transition(UserLifecycleState.ACTIVE, UserLifecycleState.LOCKED)

    def test_invalid_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid lifecycle transition"):
            validate_transition(UserLifecycleState.DELETED, UserLifecycleState.ACTIVE)

    def test_error_message_includes_states(self):
        with pytest.raises(ValueError, match="deleted -> active"):
            validate_transition(UserLifecycleState.DELETED, UserLifecycleState.ACTIVE)

    def test_error_message_includes_allowed_targets(self):
        with pytest.raises(ValueError, match="Allowed targets"):
            validate_transition(UserLifecycleState.DELETED, UserLifecycleState.ACTIVE)


class TestLifecycleTransitionDataclass:
    def test_default_fields(self):
        t = LifecycleTransition(
            from_state=UserLifecycleState.ACTIVE,
            to_state=UserLifecycleState.LOCKED,
        )
        assert t.from_state == UserLifecycleState.ACTIVE
        assert t.to_state == UserLifecycleState.LOCKED
        assert t.reason == ""
        assert t.actor_id is None

    def test_with_reason(self):
        t = LifecycleTransition(
            from_state=UserLifecycleState.ACTIVE,
            to_state=UserLifecycleState.LOCKED,
            reason="too_many_failed_attempts",
        )
        assert t.reason == "too_many_failed_attempts"

    def test_with_actor(self):
        t = LifecycleTransition(
            from_state=UserLifecycleState.ACTIVE,
            to_state=UserLifecycleState.DISABLED,
            actor_id="admin-001",
        )
        assert t.actor_id == "admin-001"

    def test_timestamp_is_set(self):
        t = LifecycleTransition(
            from_state=UserLifecycleState.ACTIVE,
            to_state=UserLifecycleState.LOCKED,
        )
        assert t.timestamp is not None
