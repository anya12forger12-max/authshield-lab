# Error Handling Architecture

## Overview

AuthShield Lab implements a unified error handling strategy that separates errors
by layer, provides machine-readable error codes, follows RFC 7807 Problem Details
for API responses, and ensures errors are never silently swallowed. Every error
is logged, and user-facing messages use plain language.

---

## Error Hierarchy

```
AuthShieldError (base)
├── DomainError
│   ├── BusinessRuleViolation
│   ├── EntityNotFound
│   ├── InvalidStateTransition
│   ├── ValueObjectValidationFailed
│   └── DomainEventError
├── ApplicationError
│   ├── UseCaseFailed
│   ├── AuthorizationDenied
│   ├── ValidationError
│   ├── IdempotencyConflict
│   └── ConcurrencyConflict
├── InfrastructureError
│   ├── DatabaseError
│   │   ├── ConnectionFailed
│   │   ├── QueryFailed
│   │   ├── IntegrityViolation
│   │   └── TransactionFailed
│   ├── FileSystemError
│   │   ├── FileNotFound
│   │   ├── PermissionDenied
│   │   └── InsufficientStorage
│   ├── ConfigurationError
│   │   ├── MissingConfiguration
│   │   ├── InvalidConfiguration
│   │   └── ReadOnlyConfiguration
│   ├── NetworkError
│   │   ├── ConnectionTimeout
│   │   ├── ServiceUnavailable
│   │   └── DnsResolutionFailed
│   └── ExternalServiceError
│       ├── SmtpError
│       ├── PluginRegistryError
│       └── TimeServiceError
├── PluginError
│   ├── PluginLoadFailed
│   ├── PluginManifestInvalid
│   ├── IncompatiblePlugin
│   ├── PluginSecurityViolation
│   ├── PluginRuntimeError
│   └── PluginDependencyMissing
├── SecurityError
│   ├── AuthenticationFailed
│   ├── AccountLocked
│   ├── TokenExpired
│   ├── TokenRevoked
│   ├── TokenReuseDetected
│   ├── SessionExpired
│   ├── RateLimited
│   ├── BruteForceDetected
│   ├── MFARequired
│   ├── InvalidMFACode
│   └── PasswordResetExpired
└── AccessError
    ├── ResourceNotFound
    ├── Forbidden
    ├── Conflict
    └── Gone
```

---

## Domain Errors

Domain errors represent violations of business rules. They are defined in the
domain layer and carry no infrastructure knowledge.

### BusinessRuleViolation

```python
class BusinessRuleViolation(DomainError):
    """Raised when a business rule is violated."""

    def __init__(self, rule: str, message: str, context: dict | None = None) -> None:
        super().__init__(message)
        self.rule = rule
        self.context = context or {}

    @property
    def error_code(self) -> str:
        return "DOMAIN-BRV-001"
```

**Examples:**
- `BusinessRuleViolation("BR-AUTH-001", "Account locked after 5 failed attempts")`
- `BusinessRuleViolation("BR-COURSE-014", "Course capacity exceeded", {"capacity": 500})`
- `BusinessRuleViolation("BR-ASSESS-001", "Maximum attempts reached", {"max_attempts": 3})`

### EntityNotFound

```python
class EntityNotFound(DomainError):
    """Raised when a required entity cannot be found."""

    def __init__(self, entity_type: str, identifier: UUID | str) -> None:
        self.entity_type = entity_type
        self.identifier = identifier
        super().__init__(f"{entity_type} with identifier '{identifier}' not found")

    @property
    def error_code(self) -> str:
        return "DOMAIN-ENF-001"
```

### InvalidStateTransition

```python
class InvalidStateTransition(DomainError):
    """Raised when an entity state transition is not allowed."""

    def __init__(self, entity_type: str, current_state: str, target_state: str) -> None:
        self.entity_type = entity_type
        self.current_state = current_state
        self.target_state = target_state
        super().__init__(
            f"{entity_type} cannot transition from '{current_state}' to '{target_state}'"
        )

    @property
    def error_code(self) -> str:
        return "DOMAIN-IST-001"
```

**Examples:**
- `InvalidStateTransition("Course", "archived", "published")`
- `InvalidStateTransition("AssessmentAttempt", "submitted", "in_progress")`

### ValueObjectValidationFailed

```python
class ValueObjectValidationFailed(DomainError):
    """Raised when a value object fails validation."""

    def __init__(self, value_object: str, errors: list[str]) -> None:
        self.value_object = value_object
        self.errors = errors
        super().__init__(f"Validation failed for {value_object}: {'; '.join(errors)}")

    @property
    def error_code(self) -> str:
        return "DOMAIN-VVF-001"
```

---

## Application Errors

Application errors represent failures in use case execution that are not
strictly domain violations.

### AuthorizationDenied

```python
class AuthorizationDenied(ApplicationError):
    """Raised when the actor lacks required permissions."""

    def __init__(self, message: str = "Access denied", required_permission: str | None = None) -> None:
        self.required_permission = required_permission
        super().__init__(message)

    @property
    def error_code(self) -> str:
        return "APP-AUTH-001"
```

### ValidationError

```python
class ValidationError(ApplicationError):
    """Raised when input validation fails at the application layer."""

    def __init__(self, field_errors: dict[str, list[str]]) -> None:
        self.field_errors = field_errors
        messages = "; ".join(
            f"{field}: {', '.join(errors)}"
            for field, errors in field_errors.items()
        )
        super().__init__(f"Validation failed: {messages}")

    @property
    def error_code(self) -> str:
        return "APP-VAL-001"
```

### IdempotencyConflict

```python
class IdempotencyConflict(ApplicationError):
    """Raised when an idempotent request conflicts with a previous execution."""

    def __init__(self, idempotency_key: str) -> None:
        self.idempotency_key = idempotency_key
        super().__init__(f"Request with key '{idempotency_key}' already processed")

    @property
    def error_code(self) -> str:
        return "APP-IDC-001"
```

### ConcurrencyConflict

```python
class ConcurrencyConflict(ApplicationError):
    """Raised when a concurrent modification is detected."""

    def __init__(self, resource: str, version_expected: int, version_actual: int) -> None:
        self.resource = resource
        self.version_expected = version_expected
        self.version_actual = version_actual
        super().__init__(
            f"Conflict on {resource}: expected version {version_expected}, "
            f"found version {version_actual}"
        )

    @property
    def error_code(self) -> str:
        return "APP-CCF-001"
```

---

## Infrastructure Errors

Infrastructure errors represent failures in external systems and resources.

### DatabaseError

```python
class DatabaseError(InfrastructureError):
    """Base class for database-related errors."""

    def __init__(self, message: str, query: str | None = None) -> None:
        self.query = query
        super().__init__(message)


class ConnectionFailed(DatabaseError):
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        super().__init__(f"Failed to connect to database at {host}:{port}")

    @property
    def error_code(self) -> str:
        return "INF-DBE-001"


class QueryFailed(DatabaseError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Query execution failed: {reason}")

    @property
    def error_code(self) -> str:
        return "INF-DBE-002"


class IntegrityViolation(DatabaseError):
    def __init__(self, constraint: str) -> None:
        self.constraint = constraint
        super().__init__(f"Database integrity violation: {constraint}")

    @property
    def error_code(self) -> str:
        return "INF-DBE-003"


class TransactionFailed(DatabaseError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Transaction failed: {reason}")

    @property
    def error_code(self) -> str:
        return "INF-DBE-004"
```

### FileSystemError

```python
class FileSystemError(InfrastructureError):
    def __init__(self, path: str, operation: str, reason: str) -> None:
        self.path = path
        self.operation = operation
        super().__init__(f"File system error during {operation} on {path}: {reason}")


class FileNotFound(FileSystemError):
    def __init__(self, path: str) -> None:
        super().__init__(path, "read", "file not found")

    @property
    def error_code(self) -> str:
        return "INF-FSE-001"


class InsufficientStorage(FileSystemError):
    def __init__(self, required_bytes: int, available_bytes: int) -> None:
        self.required_bytes = required_bytes
        self.available_bytes = available_bytes
        super().__init__("", "write", f"Need {required_bytes} bytes, {available_bytes} available")

    @property
    def error_code(self) -> str:
        return "INF-FSE-002"
```

### ConfigurationError

```python
class ConfigurationError(InfrastructureError):
    def __init__(self, key: str, message: str) -> None:
        self.key = key
        super().__init__(message)


class MissingConfiguration(ConfigurationError):
    def __init__(self, key: str) -> None:
        super().__init__(key, f"Required configuration '{key}' is missing")

    @property
    def error_code(self) -> str:
        return "INF-CFG-001"


class InvalidConfiguration(ConfigurationError):
    def __init__(self, key: str, reason: str) -> None:
        super().__init__(key, f"Invalid value for '{key}': {reason}")

    @property
    def error_code(self) -> str:
        return "INF-CFG-002"
```

---

## Plugin Errors

```python
class PluginError(InfrastructureError):
    def __init__(self, plugin_id: str, message: str) -> None:
        self.plugin_id = plugin_id
        super().__init__(message)


class PluginLoadFailed(PluginError):
    def __init__(self, plugin_id: str, reason: str) -> None:
        super().__init__(plugin_id, f"Failed to load plugin '{plugin_id}': {reason}")

    @property
    def error_code(self) -> str:
        return "PLG-LOAD-001"


class IncompatiblePlugin(PluginError):
    def __init__(self, plugin_id: str, required: str, actual: str) -> None:
        self.required = required
        self.actual = actual
        super().__init__(
            plugin_id,
            f"Plugin '{plugin_id}' requires version {required}, system is {actual}",
        )

    @property
    def error_code(self) -> str:
        return "PLG-COMP-001"


class PluginSecurityViolation(PluginError):
    def __init__(self, plugin_id: str, violation: str) -> None:
        super().__init__(plugin_id, f"Security violation in '{plugin_id}': {violation}")

    @property
    def error_code(self) -> str:
        return "PLG-SEC-001"


class PluginRuntimeError(PluginError):
    def __init__(self, plugin_id: str, hook: str, reason: str) -> None:
        self.hook = hook
        super().__init__(plugin_id, f"Plugin '{plugin_id}' failed in hook '{hook}': {reason}")

    @property
    def error_code(self) -> str:
        return "PLG-RUN-001"
```

---

## Security Errors

```python
class SecurityError(AuthShieldError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class AuthenticationFailed(SecurityError):
    def __init__(self, reason: str = "Invalid credentials") -> None:
        self.reason = reason
        super().__init__(reason)

    @property
    def error_code(self) -> str:
        return "SEC-AUTH-001"


class AccountLocked(SecurityError):
    def __init__(self, locked_until: datetime) -> None:
        self.locked_until = locked_until
        super().__init__(
            f"Account locked until {locked_until.isoformat()}"
        )

    @property
    def error_code(self) -> str:
        return "SEC-AUTH-002"


class TokenExpired(SecurityError):
    def __init__(self) -> None:
        super().__init__("Token has expired")

    @property
    def error_code(self) -> str:
        return "SEC-TKN-001"


class TokenRevoked(SecurityError):
    def __init__(self) -> None:
        super().__init__("Token has been revoked")

    @property
    def error_code(self) -> str:
        return "SEC-TKN-002"


class RateLimited(SecurityError):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after} seconds")

    @property
    def error_code(self) -> str:
        return "SEC-RL-001"


class MFARequired(SecurityError):
    def __init__(self) -> None:
        super().__init__("Multi-factor authentication required")

    @property
    def error_code(self) -> str:
        return "SEC-MFA-001"
```

---

## Error Code Schema

Format: `MODULE-CATEGORY-NNN`

| Module | Code | Meaning |
|---|---|---|
| DOMAIN | BRV | Business Rule Violation |
| DOMAIN | ENF | Entity Not Found |
| DOMAIN | IST | Invalid State Transition |
| DOMAIN | VVF | Value Object Validation Failed |
| APP | AUTH | Authorization Denied |
| APP | VAL | Validation Error |
| APP | IDC | Idempotency Conflict |
| APP | CCF | Concurrency Conflict |
| INF | DBE | Database Error |
| INF | FSE | File System Error |
| INF | CFG | Configuration Error |
| INF | NET | Network Error |
| INF | EXT | External Service Error |
| PLG | LOAD | Plugin Load Error |
| PLG | COMP | Plugin Compatibility Error |
| PLG | SEC | Plugin Security Error |
| PLG | RUN | Plugin Runtime Error |
| SEC | AUTH | Authentication Error |
| SEC | TKN | Token Error |
| SEC | RL | Rate Limit Error |
| SEC | MFA | MFA Error |
| SEC | PWD | Password Error |

---

## Error Response Format (RFC 7807)

All API errors follow RFC 7807 Problem Details:

```json
{
  "type": "https://authshield.lab/errors/business-rule-violation",
  "title": "Business Rule Violation",
  "status": 422,
  "detail": "Course capacity exceeded. Maximum 500 students allowed.",
  "instance": "/api/v1/courses/abc-123/enroll",
  "error_code": "DOMAIN-BRV-001",
  "rule": "BR-COURSE-014",
  "extensions": {
    "capacity": 500,
    "current_enrollment": 500
  }
}
```

### HTTP Status Code Mapping

| Error Type | HTTP Status |
|---|---|
| EntityNotFound | 404 |
| ValidationFailed | 422 |
| AuthorizationDenied | 403 |
| AuthenticationFailed | 401 |
| AccountLocked | 423 |
| TokenExpired | 401 |
| RateLimited | 429 |
| ConcurrencyConflict | 409 |
| DatabaseError | 503 |
| FileSystemError | 500 |
| ConfigurationError | 500 |
| PluginError | 500 |
| BusinessRuleViolation | 422 |

---

## Error Logging Patterns

```python
# In application services and handlers:

try:
    result = await handler.handle(command)
except AuthenticationFailed as exc:
    logger.warning(
        "Authentication failed",
        email=command.email,
        ip=command.ip_address,
        error_code=exc.error_code,
    )
    raise
except AccountLocked as exc:
    logger.error(
        "Account locked",
        email=command.email,
        locked_until=exc.locked_until.isoformat(),
        error_code=exc.error_code,
    )
    raise
except BusinessRuleViolation as exc:
    logger.info(
        "Business rule violated",
        rule=exc.rule,
        context=exc.context,
        error_code=exc.error_code,
    )
    raise
except DatabaseError as exc:
    logger.error(
        "Database error",
        query=exc.query,
        error=str(exc),
        exc_info=True,
    )
    raise
except Exception as exc:
    logger.critical(
        "Unhandled exception",
        error=str(exc),
        exc_info=True,
    )
    raise
```

### Structured Logging Format

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "ERROR",
  "logger": "authshield.application.services.auth",
  "message": "Account locked",
  "error_code": "SEC-AUTH-002",
  "actor": "user@example.com",
  "ip": "192.168.1.100",
  "context": {
    "locked_until": "2025-01-15T11:30:00Z",
    "failed_attempts": 5
  },
  "trace_id": "abc-123-def-456"
}
```

---

## Error Recovery Strategies

### Retry with Exponential Backoff

```python
async def with_retry(
    operation: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (DatabaseError, NetworkError),
) -> Any:
    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except retryable_exceptions as exc:
            if attempt == max_retries:
                raise
            delay = base_delay * (backoff_factor ** attempt)
            logger.warning(
                f"Retryable error, attempt {attempt + 1}/{max_retries}",
                error=str(exc),
                delay=delay,
            )
            await asyncio.sleep(delay)
```

### Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60) -> None:
        self._failure_count = 0
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._state = "closed"
        self._last_failure_time: float | None = None

    async def call(self, operation: Callable) -> Any:
        if self._state == "open":
            if self._time_since_last_failure() > self._recovery_timeout:
                self._state = "half-open"
            else:
                raise ServiceUnavailable("Circuit breaker is open")

        try:
            result = await operation()
            if self._state == "half-open":
                self._state = "closed"
                self._failure_count = 0
            return result
        except Exception:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._failure_count >= self._failure_threshold:
                self._state = "open"
            raise
```

### Graceful Degradation

```python
class NotificationService:
    async def send_notification(self, user_id: UUID, message: str) -> None:
        try:
            await self._push_service.send(user_id, message)
        except (NetworkError, ServiceUnavailable):
            logger.warning("Push notification failed, falling back to email")
            try:
                user = await self._user_repo.find_by_id(user_id)
                await self._email_service.send(user.email, message)
            except SmtpError:
                logger.error("Both push and email failed, queuing for retry")
                await self._retry_queue.add(user_id, message)
```

---

## User-Facing Error Messages

All user-facing messages use plain language, avoid technical jargon, and include
actionable guidance where possible.

| Error Code | Technical Message | User-Facing Message |
|---|---|---|
| SEC-AUTH-001 | Authentication failed | The email or password you entered is incorrect. Please try again. |
| SEC-AUTH-002 | Account locked | Your account has been temporarily locked due to multiple failed sign-in attempts. Please try again in {time}. |
| SEC-TKN-001 | Token expired | Your session has expired. Please sign in again. |
| APP-AUTH-001 | Authorization denied | You don't have permission to perform this action. Contact your administrator if you believe this is an error. |
| DOMAIN-ENF-001 | Entity not found | The item you're looking for doesn't exist or may have been removed. |
| DOMAIN-BRV-001 | Business rule violated | This action cannot be completed. {specific reason}. |
| APP-VAL-001 | Validation error | Please check your input: {field-specific errors}. |
| INF-DBE-001 | Connection failed | We're having trouble connecting to our servers. Please try again in a few moments. |
| INF-FSE-002 | Insufficient storage | Not enough storage space available. Please free up space or contact support. |
| PLG-LOAD-001 | Plugin load failed | The plugin could not be loaded. It may be corrupted or incompatible. |
| SEC-RL-001 | Rate limited | Too many requests. Please wait {seconds} seconds before trying again. |

---

## Error Handling Middleware

```python
from fastapi import Request
from fastapi.responses import JSONResponse


async def error_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except AuthShieldError as exc:
        status_code = _map_error_to_status(exc)
        return JSONResponse(
            status_code=status_code,
            content={
                "type": f"https://authshield.lab/errors/{type(exc).__name__}",
                "title": type(exc).__name__,
                "status": status_code,
                "detail": _user_facing_message(exc),
                "error_code": getattr(exc, "error_code", "UNKNOWN"),
                "instance": str(request.url),
            },
            headers=_extra_headers(exc),
        )
    except Exception as exc:
        logger.critical("Unhandled exception", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "type": "https://authshield.lab/errors/internal",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred. Please try again later.",
                "error_code": "INF-INT-001",
            },
        )


def _extra_headers(exc: AuthShieldError) -> dict[str, str]:
    headers = {}
    if isinstance(exc, RateLimited):
        headers["Retry-After"] = str(exc.retry_after)
    if isinstance(exc, AccountLocked):
        headers["Retry-After"] = str(int((exc.locked_until - datetime.now()).total_seconds()))
    return headers
```
