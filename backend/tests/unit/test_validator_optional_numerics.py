"""Regression tests for optional-numeric-field validation.

The validators used to write the numeric range guard as::

    if (value is not None and not isinstance(value, int)) or value < 1:

The ``is not None`` short-circuit only protected the *first* ``or`` clause. A
``dict.get()`` returns ``None`` for an absent key, so the moment any caller
omitted the optional field the comparison ``None < 1`` executed and raised
``TypeError: '<' not supported between instances of 'NoneType' and 'int'``.

That meant the validation layer crashed on the *most common* input (a payload
that simply does not mention an optional field) instead of validating it.

These tests drive the real validator functions -- no mocks -- so a regression
is a hard failure rather than something a permissive fake silently absorbs.
"""

from __future__ import annotations

import pytest

from app.lms.validators.lms_validator import validate_assessment_data
from app.sessions.validators.session_validator import (
    validate_session_data,
    validate_session_filters,
)


def _fields(result) -> set[str]:
    return {err.field_name for err in result.errors}


class TestSessionDataOptionalNumerics:
    """validate_session_data: absent optional numerics must not raise."""

    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param({}, id="completely-empty"),
            pytest.param({"user_id": "u1"}, id="only-user-id"),
            pytest.param({"user_id": "u1", "idle_timeout_minutes": 30}, id="idle-only"),
            pytest.param({"user_id": "u1", "security_level": 3}, id="security-only"),
            pytest.param(
                {"user_id": "u1", "idle_timeout_minutes": 30, "security_level": 3},
                id="both-present",
            ),
        ],
    )
    def test_absent_optional_numeric_never_raises(self, payload):
        # The bug: any of these raised TypeError before the fix.
        result = validate_session_data(payload)
        assert "idle_timeout_minutes" not in _fields(result)
        assert "security_level" not in _fields(result)

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (0, "out_of_range"),
            (-1, "out_of_range"),
            (1441, "out_of_range"),
            ("abc", "out_of_range"),
            (None, None),
        ],
    )
    def test_idle_timeout_bounds(self, value, expected):
        result = validate_session_data({"user_id": "u1", "idle_timeout_minutes": value})
        if expected is None:
            assert "idle_timeout_minutes" not in _fields(result)
        else:
            assert "idle_timeout_minutes" in _fields(result)

    @pytest.mark.parametrize("value", [0, 6, "x"])
    def test_security_level_bounds(self, value):
        result = validate_session_data({"user_id": "u1", "security_level": value})
        assert "security_level" in _fields(result)


class TestSessionFiltersPagination:
    """validate_session_filters: pagination must validate, not crash or bypass."""

    def test_empty_filters_are_accepted(self):
        result = validate_session_filters({})
        assert "page" not in _fields(result)
        assert "per_page" not in _fields(result)

    @pytest.mark.parametrize("value", [0, -5, "x", None, True])
    def test_invalid_page_is_rejected(self, value):
        # page=None used to slip through the `is not None and (...)` guard,
        # so a caller could hand None to the repository unchecked.
        result = validate_session_filters({"page": value})
        assert "page" in _fields(result)

    @pytest.mark.parametrize("value", [0, 101, "x", None, True])
    def test_invalid_per_page_is_rejected(self, value):
        result = validate_session_filters({"per_page": value})
        assert "per_page" in _fields(result)

    @pytest.mark.parametrize("value", [1, 50, 100])
    def test_valid_pagination_accepted(self, value):
        result = validate_session_filters({"page": value, "per_page": value})
        assert "page" not in _fields(result)
        assert "per_page" not in _fields(result)


class TestAssessmentTimeLimit:
    """validate_assessment_data: same defect shape in the LMS validators."""

    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param({}, id="empty"),
            pytest.param({"title": "quiz"}, id="title-only"),
        ],
    )
    def test_absent_time_limit_never_raises(self, payload):
        result = validate_assessment_data(payload)
        assert "time_limit_minutes" not in _fields(result)

    @pytest.mark.parametrize("value", [0, -1, "x"])
    def test_invalid_time_limit_rejected(self, value):
        result = validate_assessment_data({"time_limit_minutes": value})
        assert "time_limit_minutes" in _fields(result)
