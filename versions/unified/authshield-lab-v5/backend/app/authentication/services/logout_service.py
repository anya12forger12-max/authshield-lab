"""Logout service implementation."""

from __future__ import annotations

import time

from ...shared.logging_config import get_logger, log_audit_event
from ...config.constants import MODULE_AUTH
from ..domain.entities.authentication_result import (
    AuthenticationOutcome,
    AuthenticationResult,
    FailureReason,
)
from ..domain.interfaces.event_publisher import IAuthenticationEventPublisher
from ..domain.interfaces.session_service import ISessionService
from ..domain.models.request_models import LogoutRequest

logger = get_logger(MODULE_AUTH)


class LogoutService:
    """Handles user logout and session termination.

    Parameters
    ----------
    session_service:
        Manages session lifecycle operations.
    event_publisher:
        Publishes logout and session events.
    """

    def __init__(
        self,
        session_service: ISessionService,
        event_publisher: IAuthenticationEventPublisher,
    ) -> None:
        self._session_service = session_service
        self._event_publisher = event_publisher

    async def logout(
        self, user_id: str, request: LogoutRequest, correlation_id: str = ""
    ) -> AuthenticationResult:
        """Log out a user by terminating their session(s).

        Parameters
        ----------
        user_id:
            The ID of the user logging out.
        request:
            Logout request specifying which session(s) to terminate.
        correlation_id:
            Request correlation ID for distributed tracing.

        Returns
        -------
        AuthenticationResult
        """
        start_time = time.monotonic()

        logger.info(
            "logout_attempt",
            user_id=user_id,
            session_id=request.session_id,
            terminate_all=request.terminate_all,
            correlation_id=correlation_id,
        )

        try:
            if request.terminate_all:
                terminated_count = await self._session_service.terminate_all_user_sessions(user_id)
                duration_ms = (time.monotonic() - start_time) * 1000

                log_audit_event(
                    "LOGOUT_ALL_SESSIONS",
                    user_id=user_id,
                    action="LOGOUT",
                    resource=f"user:{user_id}",
                    logger=logger,
                    terminated_count=terminated_count,
                )

                await self._event_publisher.publish_logout(
                    user_id, "all", correlation_id
                )

                logger.info(
                    "logout_all_sessions_success",
                    user_id=user_id,
                    terminated_count=terminated_count,
                    correlation_id=correlation_id,
                    duration_ms=round(duration_ms, 2),
                )

                return AuthenticationResult(
                    outcome=AuthenticationOutcome.SUCCESS,
                    user_id=user_id,
                    correlation_id=correlation_id,
                    authentication_duration_ms=duration_ms,
                    message=f"Logged out successfully. {terminated_count} session(s) terminated.",
                    metadata={"terminated_count": terminated_count},
                )

            if request.session_id:
                terminated = await self._session_service.terminate_session(request.session_id)
                duration_ms = (time.monotonic() - start_time) * 1000

                if terminated:
                    log_audit_event(
                        "LOGOUT",
                        user_id=user_id,
                        action="LOGOUT",
                        resource=f"session:{request.session_id}",
                        logger=logger,
                    )

                    await self._event_publisher.publish_logout(
                        user_id, request.session_id, correlation_id
                    )

                    logger.info(
                        "logout_success",
                        user_id=user_id,
                        session_id=request.session_id,
                        correlation_id=correlation_id,
                        duration_ms=round(duration_ms, 2),
                    )

                    return AuthenticationResult(
                        outcome=AuthenticationOutcome.SUCCESS,
                        user_id=user_id,
                        session_id=request.session_id,
                        correlation_id=correlation_id,
                        authentication_duration_ms=duration_ms,
                        message="Logged out successfully.",
                    )
                else:
                    return AuthenticationResult(
                        outcome=AuthenticationOutcome.FAILURE,
                        failure_reason=FailureReason.INVALID_SESSION,
                        user_id=user_id,
                        correlation_id=correlation_id,
                        authentication_duration_ms=duration_ms,
                        error_code="SESSION_NOT_FOUND",
                        message="Session not found or already terminated.",
                    )

            # No session_id and no terminate_all — terminate all user sessions as a safe default
            terminated_count = await self._session_service.terminate_all_user_sessions(user_id)
            duration_ms = (time.monotonic() - start_time) * 1000

            log_audit_event(
                "LOGOUT_ALL_SESSIONS",
                user_id=user_id,
                action="LOGOUT",
                resource=f"user:{user_id}",
                logger=logger,
                terminated_count=terminated_count,
            )

            await self._event_publisher.publish_logout(
                user_id, "all", correlation_id
            )

            return AuthenticationResult(
                outcome=AuthenticationOutcome.SUCCESS,
                user_id=user_id,
                correlation_id=correlation_id,
                authentication_duration_ms=duration_ms,
                message="Logged out successfully.",
                metadata={"terminated_count": terminated_count},
            )

        except Exception:
            duration_ms = (time.monotonic() - start_time) * 1000
            logger.exception(
                "logout_error",
                user_id=user_id,
                correlation_id=correlation_id,
            )
            return AuthenticationResult(
                outcome=AuthenticationOutcome.FAILURE,
                failure_reason=FailureReason.INTERNAL_ERROR,
                user_id=user_id,
                correlation_id=correlation_id,
                authentication_duration_ms=duration_ms,
                error_code="LOGOUT_ERROR",
                message="An internal error occurred during logout.",
            )
