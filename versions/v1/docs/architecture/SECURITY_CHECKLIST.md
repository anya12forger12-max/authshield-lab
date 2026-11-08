# Security Review Checklist

This checklist covers security requirements for AuthShieldLab's Python backend. Every item must be verified before code is merged.

## Password Security

- [ ] **No plaintext passwords**: Passwords are never stored, logged, or returned in API responses
- [ ] **Argon2id hashing**: All passwords hashed with Argon2id (memory-hard algorithm)
- [ ] **No password in response models**: `to_safe_dict()` excludes `password_hash` and `mfa_secret`
- [ ] **Timing-safe comparison**: Password verification uses constant-time comparison
- [ ] **Password history**: Previous hashes are tracked to prevent reuse

## SQL Injection Prevention

- [ ] **Parameterized queries**: All database queries use SQLAlchemy ORM parameterized statements
- [ ] **No raw SQL**: Raw SQL strings with user input are prohibited
- [ ] **ORM-only data access**: All data access goes through SQLAlchemy ORM
- [ ] **Search parameterization**: LIKE searches use parameterized values (`%{query}%`)

## Secrets Management

- [ ] **No hardcoded secrets**: API keys, passwords, and tokens are never hardcoded
- [ ] **Environment variables**: All secrets loaded from environment variables via Pydantic Settings
- [ ] **Auto-generated secret key**: `SecurityConfig` auto-generates `secret_key` if not provided
- [ ] **No secrets in logs**: Log redaction prevents secret leakage

## Cryptographic Security

- [ ] **No insecure randomness**: All random values use `secrets` module (CSPRNG)
- [ ] **UUID v4**: Session IDs and correlation IDs use `uuid.uuid4()`
- [ ] **Secure token generation**: Tokens generated with `secrets.token_urlsafe()`

## Exception Handling

- [ ] **No unsafe exceptions**: All exceptions are typed (`AuthShieldException` hierarchy)
- [ ] **No exposed stack traces**: API responses never include raw exception messages
- [ ] **Structured error responses**: All errors use `to_dict()` with status, error class, and message
- [ ] **No bare `except`**: All except clauses catch specific exception types

## Input Validation

- [ ] **Pydantic models**: All API inputs validated via Pydantic request models
- [ ] **Field constraints**: Min/max length, regex patterns, required fields enforced
- [ ] **AuthenticationValidator**: Domain-specific validation for auth operations
- [ ] **Username format**: Alphanumeric with `_` and `-` only
- [ ] **Email format**: Basic regex validation
- [ ] **Password strength**: Minimum length, complexity requirements enforced

## Output Sanitization

- [ ] **No password hashes in responses**: `to_safe_dict()` strips all credential material
- [ ] **No MFA secrets in responses**: MFA secrets excluded from safe serialization
- [ ] **No internal state in API responses**: Security scores, failed attempt counts hidden from non-admin consumers
- [ ] **Consistent response models**: All API responses use typed Pydantic models

## Session Security

- [ ] **UUID v4 session IDs**: Cryptographically random session identifiers
- [ ] **Absolute timeout**: Sessions have configurable maximum lifetime
- [ ] **Idle timeout**: Sessions expire after inactivity period
- [ ] **Session revocation**: Users can terminate sessions (single or all)
- [ ] **No session fixation**: New session ID generated on every login
- [ ] **Device tracking**: Sessions associated with device metadata

## Authentication Security

- [ ] **Account lockout**: Accounts locked after configurable failed attempts
- [ ] **Rate limiting**: Login attempts limited to 5/minute
- [ ] **Brute force detection**: Failed attempt tracking with timestamps
- [ ] **Account status transitions**: State machine prevents invalid state changes

## Network Security

- [ ] **Localhost-only binding**: Server binds to 127.0.0.1/::1 only
- [ ] **CORS locked to localhost**: Only localhost origins permitted
- [ ] **No external network calls**: Application makes zero external HTTP requests
- [ ] **Network target blocking**: Known public IPs and domains blocked

## Audit Trail

- [ ] **Immutable audit records**: `AuditEvent` records cannot be updated after creation
- [ ] **Correlation IDs**: Every request traced with unique correlation ID
- [ ] **All auth events logged**: Login success/failure, registration, logout recorded
- [ ] **Security event logging**: Policy violations, rate limits, lockouts logged

## Code Security

- [ ] **No eval/exec**: Dynamic code execution is prohibited
- [ ] **No pickle deserialization**: Untrusted data never deserialized with pickle
- [ ] **No subprocess injection**: No shell command execution with user input
- [ ] **No file system writes to user-controlled paths**: All file operations use whitelisted directories

## Dependency Security

- [ ] **Known dependencies only**: All imports from approved dependency list
- [ ] **No deprecated libraries**: Deprecated packages replaced with maintained alternatives
- [ ] **Version pinning**: All dependencies pinned to specific versions

## Error Handling Patterns

- [ ] **No bare `except`**: All exception handlers catch specific types
- [ ] **No exception swallowing**: Caught exceptions are logged or re-raised
- [ ] **Graceful degradation**: Non-critical failures don't crash the application
- [ ] **No information leakage**: Error messages don't reveal internal implementation details

## Data Protection

- [ ] **Soft delete**: User accounts soft-deleted (not hard-deleted) by default
- [ ] **Password history**: Previous password hashes retained for reuse detection
- [ ] **Sensitive field masking**: Database models support safe serialization
- [ ] **No credentials in metadata**: Event metadata excludes passwords and secrets

## Compliance

- [ ] **OWASP Top 10**: Addressed all applicable OWASP Top 10 categories
- [ ] **Local-first design**: No data leaves the user's machine
- [ ] **No telemetry**: No external analytics or tracking
- [ ] **No phone-home**: Application never contacts external servers

## Review Process

1. Run the test suite: `pytest tests/`
2. Check for hardcoded strings: `grep -r "password" --include="*.py"`
3. Verify no `eval()` or `exec()`: `grep -r "eval\|exec" --include="*.py"`
4. Verify no raw SQL: `grep -r "text(" --include="*.py"`
5. Review all exception handling for bare excepts
6. Verify `to_safe_dict()` excludes sensitive fields for all models
7. Confirm CORS and binding configuration
