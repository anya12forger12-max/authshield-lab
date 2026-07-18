"""Tests for exception hierarchy and to_dict()."""

import pytest

from app.shared.exceptions import (
    AuthShieldException,
    AuthenticationError,
    AuthorizationError,
    SecurityViolationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    RateLimitExceededError,
    AccountLockedError,
    SessionExpiredError,
    ConfigurationError,
)
from app.shared.exceptions_v2 import (
    HashingException,
    SessionException,
    RepositoryException,
    PolicyException,
    LocalizationException,
    AccessibilityException,
    EventBusException,
)


class TestAuthShieldException:
    def test_default_values(self):
        exc = AuthShieldException()
        assert exc.message == "An internal error occurred."
        assert exc.status_code == 500
        assert exc.detail is None

    def test_custom_message(self):
        exc = AuthShieldException(message="custom error", status_code=418)
        assert exc.message == "custom error"
        assert exc.status_code == 418

    def test_to_dict(self):
        exc = AuthShieldException(message="test error", status_code=500)
        d = exc.to_dict()
        assert d["status"] == "error"
        assert d["error"] == "AuthShieldException"
        assert d["message"] == "test error"
        assert d["status_code"] == 500

    def test_to_dict_with_detail(self):
        exc = AuthShieldException(message="error", detail={"field": "value"})
        d = exc.to_dict()
        assert d["detail"]["field"] == "value"

    def test_to_dict_without_detail(self):
        exc = AuthShieldException(message="error")
        d = exc.to_dict()
        assert "detail" not in d

    def test_is_exception(self):
        exc = AuthShieldException()
        assert isinstance(exc, Exception)

    def test_str_representation(self):
        exc = AuthShieldException(message="test msg")
        assert str(exc) == "test msg"


class TestExceptionHierarchy:
    def test_authentication_error(self):
        exc = AuthenticationError()
        assert exc.status_code == 401
        assert isinstance(exc, AuthShieldException)

    def test_authorization_error(self):
        exc = AuthorizationError()
        assert exc.status_code == 403
        assert isinstance(exc, AuthShieldException)

    def test_security_violation_error(self):
        exc = SecurityViolationError()
        assert exc.status_code == 403

    def test_validation_error(self):
        exc = ValidationError()
        assert exc.status_code == 422

    def test_not_found_error(self):
        exc = NotFoundError()
        assert exc.status_code == 404

    def test_conflict_error(self):
        exc = ConflictError()
        assert exc.status_code == 409

    def test_rate_limit_error(self):
        exc = RateLimitExceededError()
        assert exc.status_code == 429

    def test_account_locked_error(self):
        exc = AccountLockedError()
        assert exc.status_code == 423

    def test_session_expired_error(self):
        exc = SessionExpiredError()
        assert exc.status_code == 401

    def test_configuration_error(self):
        exc = ConfigurationError()
        assert exc.status_code == 500


class TestExceptionToDict:
    def test_authentication_error_to_dict(self):
        exc = AuthenticationError(message="bad creds")
        d = exc.to_dict()
        assert d["error"] == "AuthenticationError"
        assert d["status_code"] == 401

    def test_custom_detail_to_dict(self):
        exc = ValidationError(message="invalid", detail={"field": "email"})
        d = exc.to_dict()
        assert d["detail"]["field"] == "email"


class TestExceptionsV2:
    def test_hashing_exception(self):
        exc = HashingException()
        assert exc.status_code == 500
        assert isinstance(exc, AuthShieldException)

    def test_session_exception(self):
        exc = SessionException()
        assert exc.status_code == 401

    def test_repository_exception(self):
        exc = RepositoryException()
        assert exc.status_code == 500

    def test_policy_exception(self):
        exc = PolicyException()
        assert exc.status_code == 500

    def test_localization_exception(self):
        exc = LocalizationException()
        assert exc.status_code == 500

    def test_accessibility_exception(self):
        exc = AccessibilityException()
        assert exc.status_code == 422

    def test_event_bus_exception(self):
        exc = EventBusException()
        assert exc.status_code == 500

    def test_all_v2_have_to_dict(self):
        for ExcClass in [HashingException, SessionException, RepositoryException,
                         PolicyException, LocalizationException, AccessibilityException,
                         EventBusException]:
            exc = ExcClass(message="test")
            d = exc.to_dict()
            assert d["status"] == "error"
            assert d["message"] == "test"
