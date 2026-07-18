"""Registration service implementation."""

from __future__ import annotations

import time
from typing import Any

from ...shared.exceptions import ConflictError, ValidationError
from ...shared.logging_config import get_logger, log_audit_event, log_security_event
from ...config.constants import MODULE_AUTH
from ..domain.entities.authentication_result import (
    AuthenticationOutcome,
    AuthenticationResult,
    FailureReason,
)
from ..domain.interfaces.event_publisher import IAuthenticationEventPublisher
from ..domain.interfaces.password_service import IPasswordHashingService, IPasswordPolicyService
from ..domain.interfaces.repository_interfaces import IUserRepository
from ..domain.interfaces.registration_service import IRegistrationService
from ..domain.models.request_models import RegistrationRequest

logger = get_logger(MODULE_AUTH)


class RegistrationService(IRegistrationService):
    """Handles new user registration with validation, hashing, and event publishing.

    Parameters
    ----------
    user_repository:
        Persistence layer for user records.
    password_hashing_service:
        Delegates password hashing to the configured algorithm.
    password_policy_service:
        Enforces password strength policy.
    event_publisher:
        Publishes registration lifecycle events.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hashing_service: IPasswordHashingService,
        password_policy_service: IPasswordPolicyService,
        event_publisher: IAuthenticationEventPublisher,
    ) -> None:
        self._user_repo = user_repository
        self._password_hasher = password_hashing_service
        self._password_policy = password_policy_service
        self._event_publisher = event_publisher

    async def register(
        self, request: RegistrationRequest, correlation_id: str = ""
    ) -> AuthenticationResult:
        """Register a new user account.

        Flow: validate -> check availability -> validate password policy ->
        hash password -> create user -> publish event -> return result.

        Parameters
        ----------
        request:
            Registration payload from the API layer.
        correlation_id:
            Request correlation ID for distributed tracing.

        Returns
        -------
        AuthenticationResult
        """
        start_time = time.monotonic()

        logger.info(
            "registration_attempt",
            username=request.username,
            correlation_id=correlation_id,
        )

        # Publish registration requested event
        await self._event_publisher.publish_registration_requested(
            request.username, correlation_id
        )

        # Validate passwords match
        if request.password != request.confirm_password:
            return self._build_failure(
                FailureReason.VALIDATION_FAILED,
                "Passwords do not match.",
                username=request.username,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="PASSWORD_MISMATCH",
            )

        # Validate password policy
        policy_result = self._password_policy.validate_password(
            request.password, username=request.username
        )
        if not policy_result.get("is_valid", True):
            errors = policy_result.get("errors", [])
            error_messages = [e.get("message", str(e)) if isinstance(e, dict) else str(e) for e in errors]
            return self._build_failure(
                FailureReason.PASSWORD_POLICY_VIOLATION,
                "Password does not meet policy requirements.",
                username=request.username,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="PASSWORD_POLICY_VIOLATION",
                metadata={"policy_errors": error_messages},
            )

        # Check username availability
        if await self._user_repo.exists_by_username(request.username):
            log_security_event(
                "registration_username_taken",
                logger=logger,
                username=request.username,
                correlation_id=correlation_id,
            )
            return self._build_failure(
                FailureReason.VALIDATION_FAILED,
                "An account with this username already exists.",
                username=request.username,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="USERNAME_TAKEN",
            )

        # Check email availability if provided
        if request.email:
            if await self._user_repo.exists_by_email(request.email):
                return self._build_failure(
                    FailureReason.VALIDATION_FAILED,
                    "An account with this email already exists.",
                    username=request.username,
                    correlation_id=correlation_id,
                    start_time=start_time,
                    error_code="EMAIL_TAKEN",
                )

        # Hash password
        try:
            hashed_password = await self._password_hasher.hash_password(
                request.password
            )
        except Exception:
            logger.exception("password_hash_error", correlation_id=correlation_id)
            return self._build_failure(
                FailureReason.INTERNAL_ERROR,
                "An internal error occurred during registration.",
                username=request.username,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="HASH_ERROR",
            )

        # Create user
        try:
            user_data: dict[str, Any] = {
                "username": request.username,
                "hashed_password": hashed_password,
                "display_name": request.display_name,
                "email": request.email,
                "status": "active",
            }
            user = await self._user_repo.create(user_data)
        except Exception:
            logger.exception("user_create_error", correlation_id=correlation_id)
            return self._build_failure(
                FailureReason.INTERNAL_ERROR,
                "An internal error occurred during registration.",
                username=request.username,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="USER_CREATE_ERROR",
            )

        user_id = getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None)

        duration_ms = (time.monotonic() - start_time) * 1000

        log_audit_event(
            "USER_CREATED",
            user_id=user_id,
            action="CREATE",
            resource=f"user:{request.username}",
            logger=logger,
        )

        result = AuthenticationResult(
            outcome=AuthenticationOutcome.SUCCESS,
            user_id=str(user_id) if user_id else None,
            username=request.username,
            correlation_id=correlation_id,
            authentication_duration_ms=duration_ms,
            message="Registration successful.",
        )

        await self._event_publisher.publish_registration_completed(result)

        logger.info(
            "registration_success",
            user_id=user_id,
            username=request.username,
            correlation_id=correlation_id,
            duration_ms=round(duration_ms, 2),
        )

        return result

    async def check_username_availability(self, username: str) -> bool:
        """Return True if the username is not already taken."""
        return not await self._user_repo.exists_by_username(username)

    async def check_email_availability(self, email: str) -> bool:
        """Return True if the email is not already in use."""
        return not await self._user_repo.exists_by_email(email)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_failure(
        failure_reason: FailureReason,
        message: str,
        *,
        username: str = "",
        correlation_id: str = "",
        start_time: float = 0.0,
        error_code: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AuthenticationResult:
        """Construct a failure AuthenticationResult."""
        duration_ms = (time.monotonic() - start_time) * 1000 if start_time else 0.0
        return AuthenticationResult(
            outcome=AuthenticationOutcome.FAILURE,
            failure_reason=failure_reason,
            username=username,
            correlation_id=correlation_id,
            authentication_duration_ms=duration_ms,
            error_code=error_code,
            message=message,
            metadata=metadata or {},
        )
