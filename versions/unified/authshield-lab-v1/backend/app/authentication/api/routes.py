"""Authentication API routes."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from ...shared.exceptions import AuthShieldException, ValidationError
from ...shared.logging_config import get_logger
from ...shared.responses import ErrorResponse, SuccessResponse
from ...config.constants import MODULE_AUTH
from ..domain.entities.authentication_result import AuthenticationOutcome
from ..domain.models.request_models import (
    LoginRequest,
    LogoutRequest,
    PasswordChangeRequest,
    RegistrationRequest,
    SessionRenewalRequest,
    SessionValidationRequest,
)
from ..domain.models.response_models import (
    AuthenticationResponse,
    LoginResponse,
    LogoutResponse,
    RegistrationResponse,
)

logger = get_logger(MODULE_AUTH)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------------------------------------------------------
# Dependency injection placeholder — these will be wired up at app startup.
# Services are set via the ``configure_dependencies`` function.
# ---------------------------------------------------------------------------

_authentication_service: Any = None
_registration_service: Any = None
_password_policy_service: Any = None


def configure_dependencies(
    authentication_service: Any,
    registration_service: Any,
    password_policy_service: Any,
) -> None:
    """Wire the service instances for the router.

    Called once during application startup with fully constructed services.
    """
    global _authentication_service, _registration_service, _password_policy_service  # noqa: PLW0603
    _authentication_service = authentication_service
    _registration_service = registration_service
    _password_policy_service = password_policy_service


def _get_correlation_id(x_request_id: str | None = Header(None)) -> str:
    """Extract or generate a correlation ID from the request header."""
    return x_request_id or str(uuid.uuid4())


def _get_auth_service() -> Any:
    """Return the configured authentication service (raises if not configured)."""
    if _authentication_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured.",
        )
    return _authentication_service


def _get_registration_service() -> Any:
    """Return the configured registration service."""
    if _registration_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Registration service not configured.",
        )
    return _registration_service


def _get_password_policy_service() -> Any:
    """Return the configured password policy service."""
    if _password_policy_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password policy service not configured.",
        )
    return _password_policy_service


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=SuccessResponse[RegistrationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    request: RegistrationRequest,
    correlation_id: str = Depends(_get_correlation_id),
    service: Any = Depends(_get_registration_service),
) -> SuccessResponse[RegistrationResponse]:
    """Register a new user with username, password, and display name."""
    result = await service.register(request, correlation_id)

    if not result.is_success:
        status_code = status.HTTP_400_BAD_REQUEST
        if result.error_code == "USERNAME_TAKEN":
            status_code = status.HTTP_409_CONFLICT
        elif result.error_code == "EMAIL_TAKEN":
            status_code = status.HTTP_409_CONFLICT
        elif result.error_code == "PASSWORD_POLICY_VIOLATION":
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        elif result.error_code in ("HASH_ERROR", "USER_CREATE_ERROR"):
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        raise HTTPException(
            status_code=status_code,
            detail={
                "message": result.message,
                "error_code": result.error_code,
                "correlation_id": correlation_id,
            },
        )

    response_data = RegistrationResponse(
        success=True,
        message=result.message,
        timestamp=result.timestamp,
        correlation_id=correlation_id,
        user_id=result.user_id,
        username=result.username,
    )

    return SuccessResponse(
        message="Registration successful.",
        data=response_data,
    )


@router.get(
    "/register/check-username/{username}",
    summary="Check username availability",
)
async def check_username(
    username: str,
    service: Any = Depends(_get_registration_service),
) -> SuccessResponse[dict[str, Any]]:
    """Check whether a username is available for registration."""
    available = await service.check_username_availability(username)
    return SuccessResponse(
        message="Username check complete.",
        data={"username": username, "available": available},
    )


@router.get(
    "/register/check-email/{email}",
    summary="Check email availability",
)
async def check_email(
    email: str,
    service: Any = Depends(_get_registration_service),
) -> SuccessResponse[dict[str, Any]]:
    """Check whether an email is available for registration."""
    available = await service.check_email_availability(email)
    return SuccessResponse(
        message="Email check complete.",
        data={"email": email, "available": available},
    )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


@router.post(
    "/login",
    response_model=SuccessResponse[LoginResponse],
    summary="Authenticate a user",
)
async def login(
    request: LoginRequest,
    correlation_id: str = Depends(_get_correlation_id),
    service: Any = Depends(_get_auth_service),
) -> SuccessResponse[LoginResponse]:
    """Authenticate with username and password.

    Returns an access token and session information on success.
    """
    result = await service.authenticate(request, correlation_id)

    if not result.is_success:
        status_code = status.HTTP_401_UNAUTHORIZED
        if result.failure_reason.value == "account_locked":
            status_code = status.HTTP_423_LOCKED
        elif result.failure_reason.value == "account_disabled":
            status_code = status.HTTP_403_FORBIDDEN
        elif result.failure_reason.value == "account_suspended":
            status_code = status.HTTP_403_FORBIDDEN

        raise HTTPException(
            status_code=status_code,
            detail={
                "message": result.message,
                "error_code": result.error_code,
                "correlation_id": correlation_id,
            },
        )

    user_info: dict[str, Any] | None = None
    if result.metadata.get("display_name"):
        user_info = {
            "user_id": result.user_id,
            "username": result.username,
            "display_name": result.metadata["display_name"],
        }

    response_data = LoginResponse(
        success=True,
        message=result.message,
        timestamp=result.timestamp,
        correlation_id=correlation_id,
        session_id=result.session_id,
        user=user_info,
    )

    return SuccessResponse(
        message="Login successful.",
        data=response_data,
    )


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


@router.post(
    "/logout",
    response_model=SuccessResponse[LogoutResponse],
    summary="Log out a user",
)
async def logout(
    request: LogoutRequest,
    correlation_id: str = Depends(_get_correlation_id),
    x_user_id: str | None = Header(None, alias="X-User-ID"),
    service: Any = Depends(_get_auth_service),
) -> SuccessResponse[LogoutResponse]:
    """Log out the current user.

    If no session_id is provided, all sessions for the user are terminated.
    """
    user_id = x_user_id
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-ID header is required for logout.",
        )

    result = await service.logout(user_id, request, correlation_id)

    if not result.is_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": result.message,
                "error_code": result.error_code,
                "correlation_id": correlation_id,
            },
        )

    response_data = LogoutResponse(
        success=True,
        message=result.message,
        timestamp=result.timestamp,
        correlation_id=correlation_id,
        session_terminated=bool(result.session_id),
    )

    return SuccessResponse(
        message="Logout successful.",
        data=response_data,
    )


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------


@router.post(
    "/session/validate",
    response_model=SuccessResponse[AuthenticationResponse],
    summary="Validate a session",
)
async def validate_session(
    request: SessionValidationRequest,
    correlation_id: str = Depends(_get_correlation_id),
    service: Any = Depends(_get_auth_service),
) -> SuccessResponse[AuthenticationResponse]:
    """Validate whether a session is still active and usable."""
    result = await service.validate_session(request.session_id)

    response_data = AuthenticationResponse(
        success=result.is_success,
        message=result.message,
        error_code=result.error_code,
        timestamp=result.timestamp,
        correlation_id=correlation_id,
    )

    return SuccessResponse(
        message="Session validation complete.",
        data=response_data,
    )


@router.post(
    "/session/renew",
    response_model=SuccessResponse[AuthenticationResponse],
    summary="Renew a session",
)
async def renew_session(
    request: SessionRenewalRequest,
    correlation_id: str = Depends(_get_correlation_id),
    service: Any = Depends(_get_auth_service),
) -> SuccessResponse[AuthenticationResponse]:
    """Extend the timeout of an active session."""
    result = await service.renew_session(request.session_id)

    if not result.is_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": result.message,
                "error_code": result.error_code,
                "correlation_id": correlation_id,
            },
        )

    response_data = AuthenticationResponse(
        success=True,
        message=result.message,
        timestamp=result.timestamp,
        correlation_id=correlation_id,
    )

    return SuccessResponse(
        message="Session renewed successfully.",
        data=response_data,
    )


# ---------------------------------------------------------------------------
# Password
# ---------------------------------------------------------------------------


@router.post(
    "/password/change",
    response_model=SuccessResponse[AuthenticationResponse],
    summary="Change user password",
)
async def change_password(
    request: PasswordChangeRequest,
    correlation_id: str = Depends(_get_correlation_id),
    x_user_id: str | None = Header(None, alias="X-User-ID"),
    service: Any = Depends(_get_auth_service),
) -> SuccessResponse[AuthenticationResponse]:
    """Change the authenticated user's password.

    Requires the current password and confirmation of the new password.
    """
    user_id = x_user_id
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-ID header is required.",
        )

    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Passwords do not match.",
                "error_code": "PASSWORD_MISMATCH",
                "correlation_id": correlation_id,
            },
        )

    # Delegate to password policy validation
    policy = _get_password_policy_service()
    policy_result = policy.validate_password(request.new_password)

    if not policy_result.get("is_valid", True):
        errors = policy_result.get("errors", [])
        error_messages = [
            e.get("message", str(e)) if isinstance(e, dict) else str(e)
            for e in errors
        ]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "New password does not meet policy requirements.",
                "error_code": "PASSWORD_POLICY_VIOLATION",
                "correlation_id": correlation_id,
                "policy_errors": error_messages,
            },
        )

    response_data = AuthenticationResponse(
        success=True,
        message="Password change accepted. Implementation pending user repository integration.",
        timestamp=datetime.now(timezone.utc),
        correlation_id=correlation_id,
    )

    return SuccessResponse(
        message="Password change processed.",
        data=response_data,
    )


@router.get(
    "/password/policy",
    summary="Get password policy",
)
async def get_password_policy(
    service: Any = Depends(_get_password_policy_service),
) -> SuccessResponse[dict[str, Any]]:
    """Return the current password policy configuration."""
    policy_config = service.get_policy_config()

    return SuccessResponse(
        message="Password policy retrieved.",
        data=policy_config,
    )


@router.post(
    "/password/strength",
    summary="Check password strength",
)
async def check_password_strength(
    request: dict[str, Any],
    service: Any = Depends(_get_password_policy_service),
) -> SuccessResponse[dict[str, Any]]:
    """Evaluate the strength of a password (0-100 score).

    Expects ``{"password": "..."}`` in the request body.
    """
    password = request.get("password", "")
    if not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password field is required.",
        )

    result = service.check_strength(password)

    return SuccessResponse(
        message="Password strength evaluated.",
        data=result,
    )
