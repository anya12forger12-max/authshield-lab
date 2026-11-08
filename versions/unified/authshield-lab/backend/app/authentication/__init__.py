"""AuthShieldLab - Authentication Module.

Provides the complete authentication engine including:
- Domain entities (account/session status, authentication results)
- Domain models (request/response)
- Domain interfaces (service and repository contracts)
- Domain events (lifecycle events)
- Service implementations (registration, login, logout, session, password)
- API routes (FastAPI router)
"""

from .api import configure_dependencies
from .api import router as auth_router
from .domain.entities import (
    AccountStatus,
    AuthenticationOutcome,
    AuthenticationResult,
    FailureReason,
    SessionStatus,
    can_transition,
    is_terminal,
    is_usable,
    validate_transition,
)
from .domain.interfaces import (
    IAuthenticationEventPublisher,
    IAuthenticationService,
    IPasswordHashingService,
    IPasswordPolicyService,
    IRegistrationService,
    ISessionService,
    IUserRepository,
)
from .domain.models import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    PasswordChangeRequest,
    RegistrationRequest,
    RegistrationResponse,
    SessionResponse,
    SessionValidationRequest,
)
from .services import (
    AuthenticationService,
    LoginService,
    LogoutService,
    PasswordPolicyService,
    PasswordVerificationService,
    RegistrationService,
    SessionService,
)

__all__ = [
    # Entities
    "AccountStatus",
    "AuthenticationOutcome",
    "AuthenticationResult",
    # Services
    "AuthenticationService",
    "FailureReason",
    # Interfaces
    "IAuthenticationEventPublisher",
    "IAuthenticationService",
    "IPasswordHashingService",
    "IPasswordPolicyService",
    "IRegistrationService",
    "ISessionService",
    "IUserRepository",
    # Models
    "LoginRequest",
    "LoginResponse",
    "LoginService",
    "LogoutRequest",
    "LogoutResponse",
    "LogoutService",
    "PasswordChangeRequest",
    "PasswordPolicyService",
    "PasswordVerificationService",
    "RegistrationRequest",
    "RegistrationResponse",
    "RegistrationService",
    "SessionResponse",
    "SessionService",
    "SessionStatus",
    "SessionValidationRequest",
    # API
    "auth_router",
    "can_transition",
    "configure_dependencies",
    "is_terminal",
    "is_usable",
    "validate_transition",
]
