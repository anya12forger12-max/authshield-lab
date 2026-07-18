"""Authentication orchestration service - the main entry point."""

from __future__ import annotations

from ...shared.logging_config import get_logger
from ...config.constants import MODULE_AUTH
from ..domain.entities.authentication_result import (
    AuthenticationOutcome,
    AuthenticationResult,
    FailureReason,
)
from ..domain.interfaces.authentication_service import IAuthenticationService
from ..domain.interfaces.session_service import ISessionService
from ..domain.models.request_models import LoginRequest, LogoutRequest
from .login_service import LoginService
from .logout_service import LogoutService

logger = get_logger(MODULE_AUTH)


class AuthenticationService(IAuthenticationService):
    """Top-level authentication orchestrator.

    Delegates to specialized services for login, logout, and session management.
    This is the single entry point that the API layer interacts with.

    Parameters
    ----------
    login_service:
        Handles credential verification and session creation.
    logout_service:
        Handles session termination.
    session_service:
        Handles session validation and renewal.
    """

    def __init__(
        self,
        login_service: LoginService,
        logout_service: LogoutService,
        session_service: ISessionService,
    ) -> None:
        self._login_service = login_service
        self._logout_service = logout_service
        self._session_service = session_service

    async def authenticate(
        self, request: LoginRequest, correlation_id: str = ""
    ) -> AuthenticationResult:
        """Authenticate a user with the given login request.

        Parameters
        ----------
        request:
            Login credentials and metadata.
        correlation_id:
            Optional request correlation ID.

        Returns
        -------
        AuthenticationResult
        """
        return await self._login_service.authenticate(request, correlation_id)

    async def logout(
        self, user_id: str, request: LogoutRequest, correlation_id: str = ""
    ) -> AuthenticationResult:
        """Log out a user by terminating their session(s).

        Parameters
        ----------
        user_id:
            The ID of the user logging out.
        request:
            Logout request with optional session targeting.
        correlation_id:
            Optional request correlation ID.

        Returns
        -------
        AuthenticationResult
        """
        return await self._logout_service.logout(user_id, request, correlation_id)

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
        try:
            is_valid = await self._session_service.validate_session(session_id)

            if is_valid:
                return AuthenticationResult(
                    outcome=AuthenticationOutcome.SUCCESS,
                    session_id=session_id,
                    message="Session is valid.",
                )
            else:
                return AuthenticationResult(
                    outcome=AuthenticationOutcome.FAILURE,
                    failure_reason=FailureReason.SESSION_EXPIRED,
                    session_id=session_id,
                    error_code="INVALID_SESSION",
                    message="Session is invalid or has expired.",
                )
        except Exception:
            logger.exception(
                "session_validation_error", session_id=session_id
            )
            return AuthenticationResult(
                outcome=AuthenticationOutcome.FAILURE,
                failure_reason=FailureReason.INTERNAL_ERROR,
                session_id=session_id,
                error_code="VALIDATION_ERROR",
                message="An internal error occurred during session validation.",
            )

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
        try:
            renewed = await self._session_service.renew_session(session_id)

            if renewed:
                return AuthenticationResult(
                    outcome=AuthenticationOutcome.SUCCESS,
                    session_id=session_id,
                    message="Session renewed successfully.",
                )
            else:
                return AuthenticationResult(
                    outcome=AuthenticationOutcome.FAILURE,
                    failure_reason=FailureReason.INVALID_SESSION,
                    session_id=session_id,
                    error_code="INVALID_SESSION",
                    message="Session could not be renewed. It may not exist or has expired.",
                )
        except Exception:
            logger.exception(
                "session_renewal_error", session_id=session_id
            )
            return AuthenticationResult(
                outcome=AuthenticationOutcome.FAILURE,
                failure_reason=FailureReason.INTERNAL_ERROR,
                session_id=session_id,
                error_code="RENEWAL_ERROR",
                message="An internal error occurred during session renewal.",
            )
