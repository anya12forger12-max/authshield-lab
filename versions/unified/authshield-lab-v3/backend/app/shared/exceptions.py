"""Custom exception hierarchy for AuthShieldLab."""

from __future__ import annotations

from typing import Any


class AuthShieldException(Exception):
    """Base exception for all AuthShieldLab errors.

    Parameters
    ----------
    message:
        Human-readable error description.
    status_code:
        HTTP status code.
    detail:
        Optional structured error detail (dict or nested error info).
    """

    def __init__(
        self,
        message: str = "An internal error occurred.",
        status_code: int = 500,
        detail: Any = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the exception for API responses."""
        result: dict[str, Any] = {
            "status": "error",
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
        }
        if self.detail is not None:
            result["detail"] = self.detail
        return result


class AuthenticationError(AuthShieldException):
    """Raised when authentication fails (bad credentials, missing token, etc.)."""

    def __init__(
        self,
        message: str = "Authentication failed.",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=401, detail=detail)


class AuthorizationError(AuthShieldException):
    """Raised when the authenticated principal lacks required permissions."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=403, detail=detail)


class SecurityViolationError(AuthShieldException):
    """Raised when a security boundary is breached (e.g. non-localhost target)."""

    def __init__(
        self,
        message: str = (
            "Security violation: operation outside the localhost boundary."
        ),
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=403, detail=detail)


class ValidationError(AuthShieldException):
    """Raised for input validation failures."""

    def __init__(
        self,
        message: str = "Validation error.",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=422, detail=detail)


class NotFoundError(AuthShieldException):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str = "Resource not found.",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=404, detail=detail)


class ConflictError(AuthShieldException):
    """Raised when an operation conflicts with existing state."""

    def __init__(
        self,
        message: str = "Resource conflict.",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=409, detail=detail)


class RateLimitExceededError(AuthShieldException):
    """Raised when a rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=429, detail=detail)


class AccountLockedError(AuthShieldException):
    """Raised when an account is locked due to too many failed attempts."""

    def __init__(
        self,
        message: str = "Account is locked due to too many failed attempts.",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=423, detail=detail)


class SessionExpiredError(AuthShieldException):
    """Raised when a session or token has expired."""

    def __init__(
        self,
        message: str = "Session has expired. Please log in again.",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=401, detail=detail)


class ConfigurationError(AuthShieldException):
    """Raised for invalid or missing application configuration."""

    def __init__(
        self,
        message: str = "Configuration error.",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=500, detail=detail)
