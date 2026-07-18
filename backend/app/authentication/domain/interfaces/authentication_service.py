"""Authentication service interface - depends only on abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.authentication_result import AuthenticationResult
from ..models.request_models import LoginRequest, LogoutRequest


class IAuthenticationService(ABC):
    """Top-level orchestration interface for authentication operations."""

    @abstractmethod
    async def authenticate(
        self, request: LoginRequest, correlation_id: str = ""
    ) -> AuthenticationResult:
        """Authenticate a user with the given login request.

        Parameters
        ----------
        request:
            Login credentials and metadata.
        correlation_id:
            Optional request correlation ID for distributed tracing.

        Returns
        -------
        AuthenticationResult
        """
        ...

    @abstractmethod
    async def logout(
        self, user_id: str, request: LogoutRequest, correlation_id: str = ""
    ) -> AuthenticationResult:
        """Log out a user, optionally terminating all sessions.

        Parameters
        ----------
        user_id:
            The ID of the user logging out.
        request:
            Logout request with optional session_id or terminate_all flag.
        correlation_id:
            Optional request correlation ID.

        Returns
        -------
        AuthenticationResult
        """
        ...

    @abstractmethod
    async def validate_session(self, session_id: str) -> AuthenticationResult:
        """Validate whether a session is currently active and usable.

        Parameters
        ----------
        session_id:
            The session token to validate.

        Returns
        -------
        AuthenticationResult
        """
        ...

    @abstractmethod
    async def renew_session(self, session_id: str) -> AuthenticationResult:
        """Renew / extend an active session.

        Parameters
        ----------
        session_id:
            The session token to renew.

        Returns
        -------
        AuthenticationResult
        """
        ...
