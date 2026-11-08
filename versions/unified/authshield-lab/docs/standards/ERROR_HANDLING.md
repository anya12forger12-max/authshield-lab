# Error Handling Standards — AuthShield Lab

This document defines the standards for error handling, logging, recovery, and
user-facing messaging across the AuthShield Lab codebase.

---

## 1. Exception Hierarchy

All application exceptions inherit from `AuthShieldException`. This provides a
single catch point for global error handlers and ensures consistent error
structure.

```
BaseException
└── Exception
    └── AuthShieldException
        ├── AuthenticationError (401)
        │   ├── InvalidCredentialsError
        │   ├── TokenExpiredError
        │   └── TokenRevokedError
        ├── AuthorizationError (403)
        │   ├── InsufficientPermissionsError
        │   └── AccountLockedError
        ├── NotFoundError (404)
        ├── ConflictError (409)
        │   ├── DuplicateEmailError
        │   └── DuplicateUsernameError
        ├── ValidationError (422)
        │   ├── SchemaValidationError
        │   └── BusinessRuleError
        ├── RateLimitError (429)
        ├── ExternalServiceError (502)
        │   ├── ServiceUnavailableError
        │   ├── ServiceTimeoutError
        │   └── ServiceResponseError
        └── InternalError (500)
            ├── DatabaseError
            │   ├── DatabaseIntegrityError
            │   ├── DatabaseOperationalError
            │   └── DatabaseProgrammingError
            └── ConfigurationError
```

### 1.1 Base exception class

```python
from __future__ import annotations

from typing import Any


class AuthShieldException(Exception):
    """Base exception for all AuthShield application errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "about:blank",
            "title": self.code,
            "status": self.status_code,
            "detail": self.message,
        }
```

### 1.2 Module-specific exceptions

```python
class AuthenticationError(AuthShieldException):
    def __init__(self, message: str = "Authentication required", **details: Any) -> None:
        super().__init__(message, code="AUTHENTICATION_ERROR", status_code=401, details=details)


class InvalidCredentialsError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password", code="INVALID_CREDENTIALS")


class TokenExpiredError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__("Token has expired", code="TOKEN_EXPIRED")


class TokenRevokedError(AuthenticationError):
    def __init__(self) -> None:
        super().__init__("Token has been revoked", code="TOKEN_REVOKED")


class AuthorizationError(AuthShieldException):
    def __init__(self, message: str = "Insufficient permissions", **details: Any) -> None:
        super().__init__(message, code="AUTHORIZATION_ERROR", status_code=403, details=details)


class InsufficientPermissionsError(AuthorizationError):
    def __init__(self, required_permission: str) -> None:
        super().__init__(
            f"Missing required permission: {required_permission}",
            code="INSUFFICIENT_PERMISSIONS",
            required_permission=required_permission,
        )


class AccountLockedError(AuthorizationError):
    def __init__(self, reason: str = "Too many failed login attempts") -> None:
        super().__init__(reason, code="ACCOUNT_LOCKED")


class NotFoundError(AuthShieldException):
    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(
            f"{resource} '{identifier}' not found",
            code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)},
        )


class ConflictError(AuthShieldException):
    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(message, code="CONFLICT", status_code=409, details=details)


class DuplicateEmailError(ConflictError):
    def __init__(self, email: str) -> None:
        super__(f"An account with email '{email}' already exists", email=email)


class DuplicateUsernameError(ConflictError):
    def __init__(self, username: str) -> None:
        super().__init__(f"Username '{username}' is already taken", username=username)


class ValidationError(AuthShieldException):
    def __init__(self, message: str = "Validation failed", **details: Any) -> None:
        super().__init__(message, code="VALIDATION_ERROR", status_code=422, details=details)


class BusinessRuleError(ValidationError):
    def __init__(self, rule: str, message: str) -> None:
        super().__init__(message, code="BUSINESS_RULE_VIOLATION", rule=rule)


class RateLimitError(AuthShieldException):
    def __init__(self, retry_after: int = 60) -> None:
        super().__init__(
            f"Rate limit exceeded. Retry after {retry_after} seconds.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after},
        )


class ExternalServiceError(AuthShieldException):
    def __init__(self, service: str, message: str, **details: Any) -> None:
        super().__init__(
            f"External service error ({service}): {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details={"service": service, **details},
        )


class ServiceTimeoutError(ExternalServiceError):
    def __init__(self, service: str, timeout: float) -> None:
        super().__init__(service, f"Request timed out after {timeout}s", timeout=timeout)


class ServiceUnavailableError(ExternalServiceError):
    def __init__(self, service: str) -> None:
        super().__init__(service, "Service is currently unavailable")


class InternalError(AuthShieldException):
    def __init__(self, message: str = "An internal error occurred", **details: Any) -> None:
        super().__init__(message, code="INTERNAL_ERROR", status_code=500, details=details)


class DatabaseError(InternalError):
    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(message, code="DATABASE_ERROR", **details)


class ConfigurationError(InternalError):
    def __init__(self, setting: str, message: str) -> None:
        super().__init__(f"Configuration error for '{setting}': {message}", setting=setting)
```

---

## 2. HTTP Error Responses (RFC 7807 Problem Details)

All error responses follow the [RFC 7807](https://www.rfc-editor.org/rfc/rfc7807)
`application/problem+json` format.

### 2.1 Response structure

```json
{
  "type": "about:blank",
  "title": "NOT_FOUND",
  "status": 404,
  "detail": "User '550e8400-e29b-41d4-a716-446655440000' not found.",
  "instance": "/api/v1/users/550e8400-e29b-41d4-a716-446655440000"
}
```

### 2.2 Global exception handler

```python
import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AuthShieldException)
    async def authshield_handler(
        request: Request, exc: AuthShieldException
    ) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
        logger.error(
            "authshield.error",
            extra={
                "correlation_id": correlation_id,
                "code": exc.code,
                "status_code": exc.status_code,
                "detail": exc.message,
                "path": str(request.url),
                "exc_details": exc.details,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                **exc.to_dict(),
                "instance": str(request.url),
                "correlation_id": correlation_id,
            },
            headers={"X-Correlation-ID": correlation_id},
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
        logger.critical(
            "authshield.unhandled",
            extra={"correlation_id": correlation_id, "path": str(request.url)},
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={
                "type": "about:blank",
                "title": "INTERNAL_ERROR",
                "status": 500,
                "detail": "An unexpected error occurred.",
                "instance": str(request.url),
                "correlation_id": correlation_id,
            },
            headers={"X-Correlation-ID": correlation_id},
        )
```

---

## 3. Validation Errors (Pydantic)

### 3.1 Custom error formatting

Override Pydantic's default error format to produce user-friendly messages.

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    user_friendly = []
    for error in errors:
        loc = " → ".join(str(l) for l in error["loc"])
        user_friendly.append({
            "field": loc,
            "message": _humanize_error(error),
            "type": error["type"],
        })
    return JSONResponse(
        status_code=422,
        content={
            "type": "about:blank",
            "title": "VALIDATION_ERROR",
            "status": 422,
            "detail": "One or more fields are invalid.",
            "errors": user_friendly,
        },
    )


def _humanize_error(error: dict) -> str:
    mapping = {
        "string_too_short": "Value is too short",
        "string_too_long": "Value is too long",
        "value_error": "Invalid value",
        "missing": "This field is required",
        "string_pattern_mismatch": "Invalid format",
    }
    return mapping.get(error["type"], error.get("msg", "Invalid value"))
```

### 3.2 Rules

- Always return a list of field-level errors, not a single generic message.
- Include the field path so the frontend can map errors to form fields.
- Never expose internal Pydantic error details (e.g., regex patterns) to the
  user.

---

## 4. Database Errors

Catch and translate SQLAlchemy errors into domain-specific exceptions.

```python
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    ProgrammingError,
    SQLAlchemyError,
)


async def handle_db_error(exc: SQLAlchemyError, context: str = "") -> None:
    if isinstance(exc, IntegrityError):
        original = str(exc.orig).lower()
        if "unique" in original or "duplicate" in original:
            raise ConflictError(
                f"A record with the same value already exists. {context}"
            )
        elif "foreign key" in original:
            raise ValidationError(
                f"Referenced record does not exist. {context}"
            )
        raise DatabaseIntegrityError(str(exc))
    elif isinstance(exc, OperationalError):
        raise DatabaseOperationalError(f"Database operation failed: {context}")
    elif isinstance(exc, ProgrammingError):
        raise DatabaseProgrammingError(f"Invalid query: {context}")
    raise DatabaseError(f"Database error: {context}")
```

### Rules

- Never expose raw database error messages to the user.
- Log the full exception including stack trace.
- Map database errors to the appropriate domain exception.

---

## 5. External Service Errors

### 5.1 Timeout handling

```python
import asyncio
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")


def with_timeout(seconds: float) -> Callable:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise ServiceTimeoutError(service=func.__name__, timeout=seconds)
        return wrapper
    return decorator


@with_timeout(seconds=10.0)
async def call_external_api(endpoint: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint)
        response.raise_for_status()
        return response.json()
```

### 5.2 Connection failure handling

```python
async def fetch_with_retry(
    url: str,
    *,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> dict[str, Any]:
    last_exception: Exception | None = None

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            last_exception = e
            delay = base_delay * (2 ** attempt)
            logger.warning(
                "external.connect_failed",
                extra={"url": url, "attempt": attempt + 1, "retry_after": delay},
            )
            await asyncio.sleep(delay)
        except httpx.TimeoutException as e:
            raise ServiceTimeoutError(service="http", timeout=10.0) from e

    raise ServiceUnavailableError(service="http")
```

---

## 6. Error Logging

### 6.1 Structured logging context

Every log entry must include:

- **`correlation_id`**: UUID tying together all logs for a single request.
- **`timestamp`**: ISO 8601 UTC timestamp.
- **`level`**: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- **`logger`**: Module path.
- **`message`**: Human-readable description.
- **`extra`**: Additional structured context.

```python
import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def process_request(request: Request) -> Response:
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id

    logger.info(
        "request.received",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": request.client.host,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    try:
        response = await _handle_request(request)
        logger.info(
            "request.completed",
            extra={
                "correlation_id": correlation_id,
                "status_code": response.status_code,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        return response
    except AuthShieldException as exc:
        logger.error(
            "request.failed",
            extra={
                "correlation_id": correlation_id,
                "error_code": exc.code,
                "status_code": exc.status_code,
                "detail": exc.message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        raise
```

### 6.2 Log levels

| Level     | When to use                                       |
| --------- | ------------------------------------------------- |
| `DEBUG`   | Diagnostic info, variable values, query text      |
| `INFO`    | Normal operations: request received, job completed|
| `WARNING` | Recoverable issues: retry needed, rate limited    |
| `ERROR`   | Application errors: failed request, validation    |
| `CRITICAL`| System failures: unhandled exception, DB down     |

### 6.3 Rules

- Never log sensitive data: passwords, tokens, API keys, PII.
- Use structured logging (key-value pairs), not free-form strings.
- Every error log must include the correlation ID.
- Use the `extra` parameter, not string interpolation, for context data.

---

## 7. User-Facing Error Messages

### 7.1 Principles

- Be **specific** but not **technical**. Users should understand what went wrong
  and what they can do about it.
- Never expose stack traces, SQL queries, or internal implementation details.
- Provide actionable guidance where possible.

### 7.2 Examples

| Error code             | User-facing message                                  | Technical detail (logged)           |
| ---------------------- | ---------------------------------------------------- | ----------------------------------- |
| `INVALID_CREDENTIALS`  | "Invalid email or password."                         | Auth failed for user_id=abc         |
| `TOKEN_EXPIRED`        | "Your session has expired. Please log in again."     | JWT exp=1700000000, now=1700000001  |
| `ACCOUNT_LOCKED`       | "Account locked due to too many failed attempts. Try again in 15 minutes." | Lock until 2024-01-01T00:15:00Z |
| `VALIDATION_ERROR`     | "The email address format is invalid."               | Regex `^[^@]+@[^@]+$` failed        |
| `RATE_LIMIT_EXCEEDED`  | "Too many requests. Please wait 30 seconds."         | 101/100 requests in 60s window      |
| `NOT_FOUND`            | "The requested resource was not found."              | User `abc` not in `users` table     |
| `INTERNAL_ERROR`       | "Something went wrong. Please try again later."     | [correlation_id logged]             |

### 7.3 Localization

- All user-facing messages are in English.
- Future localization should use message keys (error codes), not translated
  strings in the backend. The frontend maps codes to translated strings.

---

## 8. Error Recovery Strategies

### 8.1 Automatic retry with exponential backoff

```python
import asyncio
import random
from typing import TypeVar, Callable, Any

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter: bool = True,
    **kwargs: Any,
) -> Any:
    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except (ServiceTimeoutError, ServiceUnavailableError) as exc:
            last_exception = exc
            if attempt == max_retries:
                break
            delay = min(base_delay * (2 ** attempt), max_delay)
            if jitter:
                delay = random.uniform(0, delay)
            logger.warning(
                "retry.attempt",
                extra={
                    "attempt": attempt + 1,
                    "max_retries": max_retries,
                    "delay": delay,
                    "error": str(exc),
                },
            )
            await asyncio.sleep(delay)

    raise last_exception  # type: ignore[misc]
```

### 8.2 Circuit breaker

For services that may be down for extended periods, implement a circuit breaker
to fail fast instead of retrying repeatedly.

```python
import time
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: float = 0.0

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        if self.state == CircuitState.OPEN:
            if time.monotonic() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise ServiceUnavailableError(service="circuit_breaker")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("circuit_breaker.opened", extra={"failures": self.failure_count})
```

---

## 9. Dead Letter Queue

For async jobs that fail after all retry attempts, route to a dead letter queue
(DLQ) for manual inspection.

```python
class DeadLetterQueue:
    async def publish(
        self,
        job: dict[str, Any],
        *,
        error: Exception,
        attempt_count: int,
    ) -> None:
        entry = {
            "job": job,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "attempt_count": attempt_count,
            "failed_at": datetime.now(timezone.utc).isoformat(),
        }
        await self._store(entry)
        logger.error(
            "dlq.published",
            extra={"job_type": job.get("type"), "error": str(error)},
        )

    async def retry(self, entry_id: str) -> None:
        entry = await self._retrieve(entry_id)
        await self._requeue(entry["job"])
        await self._remove(entry_id)

    async def _store(self, entry: dict) -> None:
        ...

    async def _retrieve(self, entry_id: str) -> dict:
        ...

    async def _remove(self, entry_id: str) -> None:
        ...

    async def _requeue(self, job: dict) -> None:
        ...
```

---

## 10. Summary of Rules

1. Every exception must inherit from `AuthShieldException`.
2. Every error response follows RFC 7807 Problem Details format.
3. Every log entry includes a `correlation_id`.
4. Never expose internal details (stack traces, SQL, paths) to users.
5. Never log sensitive data (passwords, tokens, API keys).
6. Map database errors to domain exceptions.
7. Use exponential backoff for transient failures.
8. Route permanently failed jobs to a dead letter queue.
9. Provide actionable user-facing error messages.
10. Test error paths with the same rigor as happy paths.
