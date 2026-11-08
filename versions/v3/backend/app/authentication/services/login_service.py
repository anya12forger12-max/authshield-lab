"""Login (authentication) service implementation."""

from __future__ import annotations

import time

from ...shared.exceptions import (
    AccountLockedError,
    AuthenticationError,
    ValidationError,
)
from ...shared.logging_config import get_logger, log_audit_event, log_security_event
from ...config.constants import MODULE_AUTH
from ..domain.entities.account_status import AccountStatus
from ..domain.entities.authentication_result import (
    AuthenticationOutcome,
    AuthenticationResult,
    FailureReason,
)
from ..domain.interfaces.event_publisher import IAuthenticationEventPublisher
from ..domain.interfaces.password_service import IPasswordHashingService
from ..domain.interfaces.repository_interfaces import IUserRepository
from ..domain.interfaces.session_service import ISessionService
from ..domain.models.request_models import LoginRequest

logger = get_logger(MODULE_AUTH)


class LoginService:
    """Handles user login with credential verification and session creation.

    Security notes:
    - Never reveals whether a username exists (uniform error messages).
    - Tracks failed attempts and triggers account lockout.
    - Publishes detailed events for audit trail.

    Parameters
    ----------
    user_repository:
        Persistence layer for user records.
    password_hashing_service:
        Delegates password verification.
    session_service:
        Manages user session creation.
    event_publisher:
        Publishes authentication lifecycle events.
    max_failed_attempts:
        Number of failed logins before lockout.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hashing_service: IPasswordHashingService,
        session_service: ISessionService,
        event_publisher: IAuthenticationEventPublisher,
        max_failed_attempts: int = 5,
    ) -> None:
        self._user_repo = user_repository
        self._password_hasher = password_hashing_service
        self._session_service = session_service
        self._event_publisher = event_publisher
        self._max_failed_attempts = max_failed_attempts

    async def authenticate(
        self, request: LoginRequest, correlation_id: str = ""
    ) -> AuthenticationResult:
        """Authenticate a user with the given login credentials.

        Parameters
        ----------
        request:
            Login credentials and metadata.
        correlation_id:
            Request correlation ID for distributed tracing.

        Returns
        -------
        AuthenticationResult
            Contains outcome, user info, session ID (on success), and timing.
        """
        start_time = time.monotonic()
        username = request.username

        await self._event_publisher.publish_authentication_requested(
            username, correlation_id
        )

        logger.info(
            "login_attempt",
            username=username,
            correlation_id=correlation_id,
        )

        # Find user by username
        user = await self._user_repo.get_by_username(username)

        if user is None:
            log_security_event(
                "login_user_not_found",
                logger=logger,
                username=username,
                correlation_id=correlation_id,
            )
            return self._build_failure(
                FailureReason.INVALID_CREDENTIALS,
                "Invalid username or password.",
                username=username,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="INVALID_CREDENTIALS",
            )

        user_id = str(getattr(user, "id", None) or user.get("id", ""))
        user_status = getattr(user, "status", None) or user.get("status", "active")
        hashed_password = getattr(user, "hashed_password", None) or user.get("hashed_password", "")

        # Check account status
        status_check = self._check_account_status(user_status, username, user_id, correlation_id, start_time)
        if status_check is not None:
            return status_check

        # Verify password
        try:
            password_valid = await self._password_hasher.verify_password(
                request.password, hashed_password
            )
        except Exception:
            logger.exception(
                "password_verification_error",
                user_id=user_id,
                correlation_id=correlation_id,
            )
            return self._build_failure(
                FailureReason.INTERNAL_ERROR,
                "An internal error occurred during authentication.",
                username=username,
                user_id=user_id,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="VERIFY_ERROR",
            )

        if not password_valid:
            await self._handle_failed_password(
                user, user_id, username, correlation_id, start_time
            )
            return self._build_failure(
                FailureReason.INVALID_CREDENTIALS,
                "Invalid username or password.",
                username=username,
                user_id=user_id,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="INVALID_CREDENTIALS",
            )

        # Reset failed login attempts on success
        await self._reset_failed_attempts(user, user_id)

        # Create session
        try:
            session_id = await self._session_service.create_session(
                user_id=user_id,
                auth_method="password",
                device_id=request.device_id,
                platform=request.platform,
            )
        except Exception:
            logger.exception(
                "session_creation_error",
                user_id=user_id,
                correlation_id=correlation_id,
            )
            return self._build_failure(
                FailureReason.INTERNAL_ERROR,
                "An internal error occurred during authentication.",
                username=username,
                user_id=user_id,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="SESSION_ERROR",
            )

        await self._event_publisher.publish_session_created(
            session_id, user_id, correlation_id
        )

        duration_ms = (time.monotonic() - start_time) * 1000

        log_audit_event(
            "LOGIN_SUCCESS",
            user_id=user_id,
            action="LOGIN",
            resource=f"user:{username}",
            logger=logger,
        )

        display_name = getattr(user, "display_name", None) or user.get("display_name", username)

        result = AuthenticationResult(
            outcome=AuthenticationOutcome.SUCCESS,
            user_id=user_id,
            username=username,
            account_status=user_status,
            session_id=session_id,
            correlation_id=correlation_id,
            authentication_duration_ms=duration_ms,
            message="Login successful.",
            metadata={"display_name": display_name},
        )

        await self._event_publisher.publish_authentication_succeeded(result)

        logger.info(
            "login_success",
            user_id=user_id,
            username=username,
            session_id=session_id,
            correlation_id=correlation_id,
            duration_ms=round(duration_ms, 2),
        )

        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_account_status(
        self,
        user_status: str,
        username: str,
        user_id: str,
        correlation_id: str,
        start_time: float,
    ) -> AuthenticationResult | None:
        """Check if the account status allows login. Returns a failure result or None."""
        if user_status == AccountStatus.LOCKED.value:
            log_security_event(
                "login_attempt_locked_account",
                logger=logger,
                username=username,
                user_id=user_id,
                correlation_id=correlation_id,
            )
            return self._build_failure(
                FailureReason.ACCOUNT_LOCKED,
                "Account is locked. Please contact support or try again later.",
                username=username,
                user_id=user_id,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="ACCOUNT_LOCKED",
            )

        if user_status == AccountStatus.DISABLED.value:
            log_security_event(
                "login_attempt_disabled_account",
                logger=logger,
                username=username,
                user_id=user_id,
                correlation_id=correlation_id,
            )
            return self._build_failure(
                FailureReason.ACCOUNT_DISABLED,
                "Account is disabled. Please contact support.",
                username=username,
                user_id=user_id,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="ACCOUNT_DISABLED",
            )

        if user_status == AccountStatus.SUSPENDED.value:
            log_security_event(
                "login_attempt_suspended_account",
                logger=logger,
                username=username,
                user_id=user_id,
                correlation_id=correlation_id,
            )
            return self._build_failure(
                FailureReason.ACCOUNT_SUSPENDED,
                "Account has been suspended. Please contact support.",
                username=username,
                user_id=user_id,
                correlation_id=correlation_id,
                start_time=start_time,
                error_code="ACCOUNT_SUSPENDED",
            )

        return None

    async def _handle_failed_password(
        self,
        user: object,
        user_id: str,
        username: str,
        correlation_id: str,
        start_time: float,
    ) -> None:
        """Handle a failed password attempt, potentially locking the account."""
        failed_attempts = getattr(user, "failed_login_attempts", None)
        if failed_attempts is None and isinstance(user, dict):
            failed_attempts = user.get("failed_login_attempts", 0)

        new_count = (failed_attempts or 0) + 1

        update_data: dict = {"failed_login_attempts": new_count}

        if new_count >= self._max_failed_attempts:
            update_data["status"] = AccountStatus.LOCKED.value
            await self._user_repo.update(user_id, update_data)

            log_security_event(
                "account_locked_max_attempts",
                logger=logger,
                username=username,
                user_id=user_id,
                failed_attempts=new_count,
                correlation_id=correlation_id,
            )

            await self._event_publisher.publish_authentication_failed(
                AuthenticationResult(
                    outcome=AuthenticationOutcome.LOCKED,
                    failure_reason=FailureReason.ACCOUNT_LOCKED,
                    user_id=user_id,
                    username=username,
                    correlation_id=correlation_id,
                    security_flags=["max_failed_attempts"],
                    metadata={"failed_attempts": new_count},
                )
            )
        else:
            await self._user_repo.update(user_id, update_data)

            log_security_event(
                "login_failed_password",
                logger=logger,
                username=username,
                user_id=user_id,
                failed_attempts=new_count,
                correlation_id=correlation_id,
            )

            await self._event_publisher.publish_authentication_failed(
                AuthenticationResult(
                    outcome=AuthenticationOutcome.FAILURE,
                    failure_reason=FailureReason.INVALID_CREDENTIALS,
                    user_id=user_id,
                    username=username,
                    correlation_id=correlation_id,
                    authentication_duration_ms=(time.monotonic() - start_time) * 1000,
                    metadata={"failed_attempts": new_count},
                )
            )

    async def _reset_failed_attempts(self, user: object, user_id: str) -> None:
        """Reset the failed login attempts counter after a successful login."""
        failed_attempts = getattr(user, "failed_login_attempts", None)
        if failed_attempts is None and isinstance(user, dict):
            failed_attempts = user.get("failed_login_attempts", 0)

        if failed_attempts and failed_attempts > 0:
            await self._user_repo.update(user_id, {"failed_login_attempts": 0})

    @staticmethod
    def _build_failure(
        failure_reason: FailureReason,
        message: str,
        *,
        username: str = "",
        user_id: str | None = None,
        correlation_id: str = "",
        start_time: float = 0.0,
        error_code: str = "",
    ) -> AuthenticationResult:
        """Construct a failure AuthenticationResult."""
        duration_ms = (time.monotonic() - start_time) * 1000 if start_time else 0.0
        return AuthenticationResult(
            outcome=AuthenticationOutcome.FAILURE,
            failure_reason=failure_reason,
            user_id=user_id,
            username=username,
            correlation_id=correlation_id,
            authentication_duration_ms=duration_ms,
            error_code=error_code,
            message=message,
        )
