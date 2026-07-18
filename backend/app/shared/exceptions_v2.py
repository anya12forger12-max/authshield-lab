"""Extended exception hierarchy for AuthShieldLab modules.

These exceptions complement the base :mod:`exceptions` hierarchy with
domain-specific error types required by future modules.
"""

from __future__ import annotations

from typing import Any

from .exceptions import AuthShieldException


class HashingException(AuthShieldException):
    """Raised when a password hashing or verification operation fails."""

    def __init__(
        self,
        message: str = "Password hashing error",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=500, detail=detail)


class SessionException(AuthShieldException):
    """Raised for general session-management errors."""

    def __init__(
        self,
        message: str = "Session error",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=401, detail=detail)


class RepositoryException(AuthShieldException):
    """Raised when a data-access / repository layer operation fails."""

    def __init__(
        self,
        message: str = "Repository error",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=500, detail=detail)


class PolicyException(AuthShieldException):
    """Raised when a policy evaluation encounters an error."""

    def __init__(
        self,
        message: str = "Policy evaluation error",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=500, detail=detail)


class LocalizationException(AuthShieldException):
    """Raised for localization / translation failures."""

    def __init__(
        self,
        message: str = "Localization error",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=500, detail=detail)


class AccessibilityException(AuthShieldException):
    """Raised when an accessibility requirement is violated."""

    def __init__(
        self,
        message: str = "Accessibility error",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=422, detail=detail)


class EventBusException(AuthShieldException):
    """Raised when the event bus encounters a failure."""

    def __init__(
        self,
        message: str = "Event bus error",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=500, detail=detail)
