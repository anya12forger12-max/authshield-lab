# Authentication Architecture

## Overview

AuthShieldLab's authentication system is a multi-layered security pipeline that handles user registration, login, session management, and password security. The architecture follows Domain-Driven Design principles with clear separation between domain entities, services, repositories, and API layers.

The system is designed for **local-only** operation -- all authentication happens within the user's machine with no external network calls. This constraint simplifies the threat model while providing a realistic platform for security education.

## Authentication Pipeline (13-Step)

Every authentication request passes through a 13-step pipeline that enforces security at each layer:

```
1. Request Ingress
   └─► Rate limiting check (5 attempts/minute)
   └─► Request size validation

2. Input Validation
   └─► Pydantic model validation (RegistrationRequest/LoginRequest)
   └─► AuthenticationValidator field checks

3. Pre-Authentication Security
   └─► Account lockout check (5 failed attempts -> 15 min lockout)
   └─► IP reputation check (local-only enforcement)

4. User Lookup
   └─► UserRepository.get_by_username()
   └─► Account status verification (active, not locked/disabled)

5. Password Verification
   └─► PasswordHasher.verify_password() with Argon2id
   └─► Timing-safe comparison

6. Account Status Evaluation
   └─► Check AccountStatus transitions (ACTIVE, PENDING_VERIFICATION, etc.)
   └─► Determine if re-authentication is needed

7. Session Creation
   └─► Generate session_id (UUID v4)
   └─► Set expiry (absolute + idle timeout)
   └─► Record device/platform metadata

8. Security Scoring
   └─► Update user security_score based on behavior
   └─► Record login_count and last_login

9. Event Publishing
   └─► AuthenticationEventPublisher fires domain events
   └─► EventBus notifies subscribers (audit, monitoring)

10. Audit Logging
    └─► AuditEvent creation with correlation_id
    └─► Record outcome, duration, security_flags

11. Response Assembly
    └─► AuthenticationResult construction
    └─► Serialization to LoginResponse

12. Session Store
    └─► SessionRepository.create() persists session
    └─► Active session count tracking

13. Response Delivery
    └─► Token generation (access_token)
    └─► Set-Cookie headers
    └─► Correlation ID for tracing
```

## Service Interfaces

### IAuthenticationService

The core authentication service defines the contract for all authentication operations:

```python
class IAuthenticationService(ABC):
    @abstractmethod
    async def register(self, request: RegistrationRequest) -> AuthenticationResult: ...

    @abstractmethod
    async def login(self, request: LoginRequest) -> AuthenticationResult: ...

    @abstractmethod
    async def logout(self, user_id: str, session_id: str) -> None: ...

    @abstractmethod
    async def validate_session(self, session_id: str) -> bool: ...
```

### IPasswordService

Password hashing and verification:

```python
class IPasswordService(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str: ...

    @abstractmethod
    def verify_password(self, password: str, hash: str) -> bool: ...

    @abstractmethod
    def get_algorithm_info(self) -> dict: ...
```

### ISessionService

Session lifecycle management:

```python
class ISessionService(ABC):
    @abstractmethod
    async def create_session(self, user_id: str, metadata: dict) -> Session: ...

    @abstractmethod
    async def validate_session(self, session_id: str) -> bool: ...

    @abstractmethod
    async def renew_session(self, session_id: str) -> Session: ...

    @abstractmethod
    async def destroy_session(self, session_id: str) -> None: ...

    @abstractmethod
    async def destroy_all_user_sessions(self, user_id: str) -> int: ...
```

### IAuthenticationEventPublisher

Event-driven communication for authentication operations:

```python
class IAuthenticationEventPublisher(ABC):
    @abstractmethod
    async def publish_authentication_requested(self, username: str, correlation_id: str) -> None: ...

    @abstractmethod
    async def publish_authentication_succeeded(self, result: AuthenticationResult) -> None: ...

    @abstractmethod
    async def publish_authentication_failed(self, result: AuthenticationResult) -> None: ...
```

## Event-Driven Design

The authentication module communicates with the rest of the system exclusively through domain events on the EventBus:

| Event | Trigger | Subscribers |
|-------|---------|-------------|
| `authentication.requested` | Login attempt initiated | Audit, Monitoring |
| `authentication.succeeded` | Successful login | Audit, Session Tracking |
| `authentication.failed` | Failed login attempt | Audit, Lockout Monitor |
| `registration.requested` | Registration initiated | Audit |
| `registration.completed` | New user created | Audit, Welcome Service |
| `session.created` | New session established | Audit, Session Tracker |
| `session.expired` | Session timeout | Cleanup, Audit |
| `session.destroyed` | Logout or revocation | Audit, Cleanup |
| `password.changed` | Password updated | Audit, History |
| `password.policy_violation` | Weak password attempt | Security Monitor |

Events are published asynchronously and do not block the authentication response. Handler failures are caught individually so one failing subscriber cannot prevent others from running.

## State Diagrams

### Account Status Lifecycle

```
                    ┌─────────────┐
                    │   UNKNOWN   │
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │  PENDING_VERIFICATION   │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
         ┌───►│         ACTIVE          │◄───┐
         │    └──┬──┬──┬──┬──┬─────────┘    │
         │       │  │  │  │  │               │
         │       │  │  │  │  └──► ARCHIVED ──┘
         │       │  │  │  └────► PASSWORD_RESET_REQUIRED ──┘
         │       │  │  └───────► SUSPENDED ──► ACTIVE
         │       │  └──────────► DISABLED ──► ACTIVE
         │       └─────────────► LOCKED ──► ACTIVE
         │                          │
         │                          └──► DELETED
         │
         └──── (from PENDING, LOCKED, DISABLED, SUSPENDED, ARCHIVED)
```

### Session Lifecycle

```
    ┌─────────┐
    │  ACTIVE  │◄────────┐
    └────┬────┘         │
         │              │
    ┌────▼────┐         │
    │   IDLE   │─────────┘ (renewal)
    └────┬────┘
         │
    ┌────▼────┐
    │ EXPIRED  │ (terminal)
    └─────────┘

    Alternative paths from ACTIVE:
    ACTIVE ──► REVOKED ──► (terminal)
    ACTIVE ──► TERMINATED ──► (terminal)
    ACTIVE ──► INVALID ──► (terminal)
```

## Extension Points

1. **Password Hashing Algorithms**: The `IPasswordService` interface allows swapping Argon2id for bcrypt, scrypt, or PBKDF2 without changing business logic.

2. **Event Subscribers**: New audit rules, monitoring hooks, or notification services can be added by subscribing to existing event types on the EventBus.

3. **Validation Rules**: The `AuthenticationValidator` and Pydantic models can be extended with custom field validators.

4. **Session Strategies**: Session metadata (device tracking, trust levels, IP binding) can be enriched through the session creation pipeline.

5. **Policy Engine Integration**: Security policies can be evaluated at the pre-authentication step to enforce rate limits, IP blocks, or behavioral rules.

## Security Considerations

1. **Password Storage**: Passwords are hashed with Argon2id (memory-hard) with configurable time cost, memory cost, and parallelism. The hash is never returned in API responses.

2. **Timing-Safe Comparison**: Password verification uses constant-time comparison to prevent timing attacks.

3. **Account Lockout**: After 5 failed attempts, the account is locked for 15 minutes. Failed attempts are tracked with timestamps for sliding-window detection.

4. **Session Security**: Sessions use UUID v4 identifiers, have configurable absolute and idle timeouts, and support per-device tracking.

5. **Correlation IDs**: Every authentication flow generates a UUID correlation ID that is carried through events and audit logs for end-to-end tracing.

6. **Sensitive Data Exclusion**: Response models (`to_safe_dict()`) explicitly exclude password hashes, MFA secrets, and internal security counters.

7. **Localhost Enforcement**: All API endpoints are bound to localhost (127.0.0.1, ::1). CORS is locked to localhost origins only. No external network calls are made.

8. **Audit Trail**: Every authentication event (success or failure) is recorded in the immutable audit trail with full context for security analysis.
