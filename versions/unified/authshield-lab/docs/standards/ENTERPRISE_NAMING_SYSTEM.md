# Enterprise Naming System

> Canonical naming conventions for the AuthShield Lab platform. Every identifier in
> the codebase must follow these rules to ensure consistency, discoverability, and
> maintainability across all 20+ modules.

---

## Table of Contents

1. [Module Naming](#module-naming)
2. [Class Naming](#class-naming)
3. [Function Naming](#function-naming)
4. [Variable Naming](#variable-naming)
5. [Constant Naming](#constant-naming)
6. [File Naming](#file-naming)
7. [API Endpoint Naming](#api-endpoint-naming)
8. [Database Naming](#database-naming)
9. [Index Naming](#index-naming)
10. [Event Naming](#event-naming)
11. [Error Naming](#error-naming)
12. [Configuration Naming](#configuration-naming)
13. [URL Naming Conventions](#url-naming-conventions)
14. [Header Naming Conventions](#header-naming-conventions)
15. [Environment Variable Naming](#environment-variable-naming)
16. [Migration Naming](#migration-naming)
17. [Logging & Telemetry Naming](#logging--telemetry-naming)
18. [Review Checklist](#review-checklist)

---

## Module Naming

### Python Modules (snake_case)

All Python module and package names use **snake_case** with no hyphens or camelCase.

```
auth/
  authentication_service.py
  session_manager.py
  token_encoder.py

users/
  user_repository.py
  user_profile_schema.py
  password_validator.py

audit/
  audit_log_writer.py
  compliance_report_generator.py
```

### Installable Packages (kebab-case)

Distribution packages distributed via PyPI or internal registries use **kebab-case**:

```
authshield-auth
authshield-users
authshield-audit
authshield-sessions
authshield-simulator
authshield-analytics
authshield-lms
```

### Module Naming Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Use snake_case for Python files | `user_service.py` | `userService.py` |
| Use kebab-case for package names | `authshield-core` | `authshield_core` |
| Plural nouns for collections | `users/` | `user/` |
| Singular nouns for singletons | `config.py` | `configs.py` |
| Descriptive, not abbreviated | `authentication.py` | `auth.py` |
| Avoid generic names | `password_hasher.py` | `utils.py` |

---

## Class Naming

### PascalCase with Suffixes

All classes use **PascalCase** with descriptive suffixes that communicate role:

| Suffix | Purpose | Example |
|---|---|---|
| `Service` | Business logic orchestration | `AuthenticationService`, `CourseEnrollmentService` |
| `Repository` | Data access abstraction | `UserRepository`, `SessionRepository` |
| `Controller` | HTTP request handling | `AuthController`, `UserController` |
| `Schema` | Data validation / serialization | `UserCreateSchema`, `LoginRequestSchema` |
| `Event` | Domain or integration events | `UserCreatedEvent`, `SessionExpiredEvent` |
| `Handler` | Event or command handling | `LoginAttemptHandler`, `PasswordResetHandler` |
| `Factory` | Object creation logic | `TokenFactory`, `CourseFactory` |
| `Builder` | Complex object construction | `QueryBuilder`, `ReportBuilder` |
| `Validator` | Validation logic | `EmailValidator`, `PolicyValidator` |
| `Middleware` | Request/response interception | `AuthenticationMiddleware`, `RateLimitMiddleware` |
| `Provider` | Dependency or resource supply | `ConfigProvider`, `CacheProvider` |
| `Adapter` | External system integration | `SmtpAdapter`, `LdapAdapter` |
| `Gateway` | External API boundary | `PaymentGateway`, `SsoGateway` |
| `Mapper` | Object-to-object transformation | `UserMapper`, `AuditLogMapper` |
| `Exception` | Error types | `AuthenticationError`, `ValidationError` |
| `Configuration` | Config data classes | `DatabaseConfiguration`, `SecurityConfiguration` |

### Class Naming Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Always PascalCase | `UserProfileService` | `user_profile_service` |
| Include role suffix | `CourseRepository` | `Course` |
| Use domain terms, not technical | `LearnerProgress` | `ProgressData` |
| Interface prefixes (optional) | `IAuthenticationProvider` | `AuthenticationProviderInterface` |
| Abstract base classes | `BaseController`, `AbstractService` | `Controller`, `Service` |

---

## Function Naming

### snake_case with Semantic Prefixes

Functions use **snake_case** with prefixes that communicate intent:

| Prefix | Purpose | Example |
|---|---|---|
| `get_` | Retrieve existing data | `get_user_by_id`, `get_active_sessions` |
| `create_` | Persist new entities | `create_user`, `create_enrollment` |
| `update_` | Modify existing entities | `update_user_profile`, `update_session_expiry` |
| `delete_` | Remove entities (soft or hard) | `delete_expired_tokens`, `delete_user` |
| `validate_` | Check conditions, raise on failure | `validate_email_format`, `validate_permissions` |
| `process_` | Transform or orchestrate | `process_login`, `process_assessment_submission` |
| `handle_` | Respond to events or commands | `handle_password_reset`, `handle_rate_limit` |
| `find_` | Search or query collections | `find_active_courses`, `find_users_by_role` |
| `send_` | Dispatch messages or notifications | `send_welcome_email`, `send_alert` |
| `generate_` | Produce new data deterministically | `generate_token`, `generate_report` |
| `compute_` | Calculate derived values | `compute_score`, `compute_risk_level` |
| `is_` / `has_` / `can_` | Boolean predicates | `is_authenticated`, `has_permission`, `can_enroll` |
| `build_` | Assemble complex objects | `build_query`, `build_certificate` |
| `parse_` | Deserialize or extract | `parse_jwt`, `parse_request_body` |
| `serialize_` | Convert to wire format | `serialize_user_response` |

### Function Naming Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Always snake_case | `get_user_by_id` | `getUserById` |
| Use semantic prefix | `create_session` | `session_create` |
| Boolean functions start with `is_`/`has_`/`can_` | `is_active` | `active`, `get_active` |
| Private helpers prefixed with `_` | `_hash_password` | `hashPassword` |
| Avoid abbreviations | `authentication` | `auth` |
| Group by domain, not technical layer | `user.create()` | `create_user_record()` |

---

## Variable Naming

### snake_case, Descriptive, No Abbreviations

```python
# Good
user_authentication_token = generate_token()
failed_login_attempt_count = 0
maximum_retry_attempts = 3
session_expiration_timestamp = datetime.utcnow()

# Bad
uat = generate_token()
flac = 0
mra = 3
set = datetime.utcnow()
```

### Variable Naming Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Always snake_case | `user_email` | `userEmail` |
| No single-letter variables (except loops) | `iteration_index` | `i` |
| No abbreviations | `authentication_method` | `auth_method` |
| Booleans: `is_`/`has_`/`was_` prefix | `is_locked` | `locked` |
| Collections: plural nouns | `enrolled_courses` | `enrolled_course` |
| Avoid generic names | `response_body` | `data` |

---

## Constant Naming

### UPPER_SNAKE_CASE

```python
# Application Constants
MAX_LOGIN_ATTEMPTS = 5
DEFAULT_SESSION_TIMEOUT_MINUTES = 30
AUTHENTICATION_TOKEN_ALGORITHM = "HS256"
PASSWORD_MINIMUM_LENGTH = 12

# Module Constants
CACHE_KEY_PREFIX_AUTH = "authshield:auth"
CACHE_KEY_PREFIX_SESSION = "authshield:session"

# Environment Keys (as constants)
ENVIRONMENT_DATABASE_URL = "AUTHSHIELD_DATABASE_URL"
ENVIRONMENT_SECRET_KEY = "AUTHSHIELD_SECRET_KEY"
```

### Constant Naming Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Always UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` | `maxRetryCount` |
| Module-level constants at file top | `DEFAULT_PAGE_SIZE` | inline magic numbers |
| Enum values UPPER_SNAKE_CASE | `UserRole.ADMIN` | `UserRole.admin` |
| No Hungarian notation | `MAX_SESSIONS` | `intMaxSessions` |

---

## File Naming

### Python Modules (snake_case)

```
auth/
  __init__.py
  authentication_service.py
  authentication_middleware.py
  authentication_exceptions.py
  token_encoder.py
  token_decoder.py
  session_manager.py
  session_repository.py
  login_attempt_handler.py
  password_reset_handler.py
```

### Frontend Components (PascalCase)

```
src/
  components/
    LoginForm.tsx
    PasswordResetForm.tsx
    SessionIndicator.tsx
    MfaVerification.tsx
  pages/
    DashboardPage.tsx
    CourseCatalogPage.tsx
    AssessmentPage.tsx
  hooks/
    useAuthentication.ts
    useSession.ts
    useCourseProgress.ts
```

### Configuration Files

```
config/
  development.toml
  production.toml
  testing.toml
  logging.yaml
  security.yaml
  database.yaml
```

---

## API Endpoint Naming

### RESTful Conventions

All endpoints use **kebab-case** with **plural nouns** and **versioned prefixes**:

```
/api/v1/users
/api/v1/users/{user_id}
/api/v1/users/{user_id}/sessions
/api/v1/users/{user_id}/enrollments

/api/v1/courses
/api/v1/courses/{course_id}/lessons
/api/v1/courses/{course_id}/assessments

/api/v1/sessions
/api/v1/sessions/{session_id}/validate

/api/v1/audit-logs
/api/v1/policies
/api/v1/roles
/api/v1/permissions
```

### Endpoint Naming Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Use kebab-case | `/api/v1/audit-logs` | `/api/v1/auditLogs` |
| Use plural nouns | `/api/v1/users` | `/api/v1/user` |
| Version prefix | `/api/v1/users` | `/api/users` |
| Nouns, not verbs | `POST /api/v1/users` | `POST /api/v1/createUser` |
| Nested resources for relationships | `/users/{id}/sessions` | `/user-sessions` |
| Action sub-resources when needed | `/users/{id}/activate` | `/activateUser` |

---

## Database Naming

### Tables (snake_case, singular)

```sql
CREATE TABLE user (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    display_name VARCHAR(128) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE session (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user(id),
    token VARCHAR(512) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE course (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty_level VARCHAR(32) NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Columns (snake_case)

```sql
-- Good
first_name VARCHAR(64)
last_login_at TIMESTAMP
password_hash_algorithm VARCHAR(32)
is_email_verified BOOLEAN

-- Bad
firstName VARCHAR(64)
last_login TIMESTAMP   -- ambiguous
hash_algo VARCHAR(32)
email_verified BOOLEAN
```

### Database Naming Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Tables: singular snake_case | `user` | `users`, `User` |
| Columns: snake_case | `created_at` | `createdAt` |
| Foreign keys: `{referenced_table}_id` | `user_id` | `userId`, `user_uuid` |
| Join tables: `{table1}_{table2}` | `user_role` | `userRoles` |
| Boolean columns: `is_`/`has_`/`was_` | `is_active` | `active` |
| Timestamps: `_at` suffix | `created_at` | `created` |
| Primary key | `id` | `pk`, `_id` |

---

## Index Naming

### idx_{table}_{column(s)}

```sql
-- Single column
CREATE INDEX idx_user_email ON user (email);
CREATE INDEX idx_session_user_id ON session (user_id);
CREATE INDEX idx_session_expires_at ON session (expires_at);

-- Composite
CREATE INDEX idx_user_email_active ON user (email, is_active);
CREATE INDEX idx_audit_log_user_created ON audit_log (user_id, created_at);

-- Unique
CREATE UNIQUE INDEX idx_unique_user_email ON user (email);

-- Partial
CREATE INDEX idx_active_session_user ON session (user_id)
    WHERE is_revoked = FALSE;
```

---

## Event Naming

### Past-Tense Verbs (PascalCase)

Domain events use **past-tense verbs** in PascalCase to clearly indicate something that already happened:

| Event | Module | Trigger |
|---|---|---|
| `UserCreated` | users | New user registered |
| `UserDeactivated` | users | Admin deactivated user |
| `PasswordChanged` | auth | User changed password |
| `PasswordResetRequested` | auth | User requested password reset |
| `SessionCreated` | sessions | Successful login |
| `SessionExpired` | sessions | Token reached expiry |
| `SessionRevoked` | sessions | Explicit logout |
| `MfaChallengeIssued` | auth | MFA challenge sent |
| `MfaChallengeVerified` | auth | MFA code verified |
| `CourseEnrolled` | lms | User enrolled in course |
| `CourseCompleted` | lms | User completed all lessons |
| `AssessmentSubmitted` | lms | User submitted assessment |
| `AssessmentGraded` | lms | Assessment auto-graded |
| `CertificateIssued` | certification | Certificate generated |
| `LoginAttemptFailed` | auth | Failed authentication |
| `PermissionDenied` | authorization | Authorization check failed |
| `PolicyViolationDetected` | policies | Security policy violated |
| `SimulationStarted` | simulation | Attack simulation launched |
| `SimulationCompleted` | simulation | Attack simulation finished |
| `AlertTriggered` | defense | Security alert fired |

---

## Error Naming

### NounError Pattern

Errors use **PascalCase** with the `Error` suffix, named after the domain concept:

```python
# Authentication errors
class AuthenticationError(Exception): ...
class InvalidCredentialsError(AuthenticationError): ...
class AccountLockedError(AuthenticationError): ...
class MfaRequiredError(AuthenticationError): ...
class TokenExpiredError(AuthenticationError): ...

# Validation errors
class ValidationError(Exception): ...
class EmailFormatError(ValidationError): ...
class PasswordComplexityError(ValidationError): ...

# Authorization errors
class AuthorizationError(Exception): ...
class InsufficientPermissionsError(AuthorizationError): ...
class RoleNotFoundError(AuthorizationError): ...

# Resource errors
class NotFoundError(Exception): ...
class UserNotFoundError(NotFoundError): ...
class CourseNotFoundError(NotFoundError): ...

# Conflict errors
class ConflictError(Exception): ...
class DuplicateEnrollmentError(ConflictError): ...
class SessionConflictError(ConflictError): ...

# Rate limiting
class RateLimitError(Exception): ...
class TooManyLoginAttemptsError(RateLimitError): ...

# Infrastructure errors
class InfrastructureError(Exception): ...
class DatabaseConnectionError(InfrastructureError): ...
class CacheConnectionError(InfrastructureError): ...
class ExternalServiceError(InfrastructureError): ...
```

---

## Configuration Naming

### Hierarchical Dot Notation

```yaml
authshield:
  authentication:
    provider: "local"
    password:
      minimum_length: 12
      hash_algorithm: "argon2id"
      max_attempts: 5
      lockout_duration_minutes: 30
    mfa:
      enabled: true
      provider: "totp"
      code_expiry_seconds: 300
  session:
    timeout_minutes: 30
    renewal_threshold_minutes: 5
    max_concurrent: 5
  authorization:
    default_role: "learner"
    rbac_enabled: true
  database:
    host: "localhost"
    port: 5432
    name: "authshield"
    pool:
      min_size: 5
      max_size: 20
  cache:
    backend: "redis"
    ttl_seconds: 3600
  logging:
    level: "INFO"
    format: "json"
```

### Config Naming Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Hierarchical keys | `auth.password.min_length` | `passwordMinLength` |
| Lowercase snake_case | `session.timeout_minutes` | `sessionTimeoutMinutes` |
| Booleans: `is_`/`has_`/`enable_` | `mfa.is_enabled` | `mfa.enabled` (inconsistently) |
| Durations: explicit unit suffix | `lockout_duration_minutes` | `lockout_duration` |
| Plural for collections | `allowed_origins` | `allowed_origin` |

---

## URL Naming Conventions

### Web Routes (kebab-case)

```
/                       (landing page)
/login
/register
/forgot-password
/reset-password/{token}
/dashboard
/courses
/courses/{course-slug}
/courses/{course-slug}/lessons/{lesson-slug}
/profile
/settings
/settings/security
/audit-logs
/admin
/admin/users
/admin/policies
```

### URL Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Kebab-case segments | `/forgot-password` | `/forgotPassword` |
| Slugs for human-readable | `/courses/python-101` | `/courses/abc123` |
| No trailing slashes | `/courses` | `/courses/` |
| No file extensions | `/api/v1/users` | `/api/v1/users.json` |

---

## Header Naming Conventions

### HTTP Headers (Kebab-Case)

Standard headers follow RFC conventions. Custom headers use a consistent prefix:

```
# Standard headers (already defined by HTTP spec)
Content-Type
Authorization
Accept
X-Request-ID

# Custom application headers
X-AuthShield-Version
X-AuthShield-Request-ID
X-AuthShield-RateLimit-Remaining
X-AuthShield-RateLimit-Reset
X-AuthShield-Session-Expiry

# Correlation headers
X-Correlation-ID
X-Trace-ID
```

### Header Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Kebab-case | `X-AuthShield-Version` | `X-AuthShield-Version` |
| Custom prefix | `X-AuthShield-*` | `X-Custom-App-*` |
| No underscores | `X-Request-ID` | `X-Request_ID` |
| Capitalize words | `Content-Type` | `content-type` |

---

## Environment Variable Naming

### AUTHSHIELD_{MODULE}_{SETTING}

All environment variables use **UPPER_SNAKE_CASE** with a consistent prefix:

```bash
# Application
AUTHSHIELD_APP_NAME="AuthShield Lab"
AUTHSHIELD_APP_ENVIRONMENT="production"
AUTHSHIELD_APP_DEBUG=false
AUTHSHIELD_APP_SECRET_KEY="..."

# Database
AUTHSHIELD_DATABASE_HOST="localhost"
AUTHSHIELD_DATABASE_PORT="5432"
AUTHSHIELD_DATABASE_NAME="authshield"
AUTHSHIELD_DATABASE_USER="authshield_app"
AUTHSHIELD_DATABASE_PASSWORD="..."
AUTHSHIELD_DATABASE_POOL_MIN="5"
AUTHSHIELD_DATABASE_POOL_MAX="20"

# Redis / Cache
AUTHSHIELD_CACHE_HOST="localhost"
AUTHSHIELD_CACHE_PORT="6379"
AUTHSHIELD_CACHE_DB="0"
AUTHSHIELD_CACHE_TTL="3600"

# Authentication
AUTHSHIELD_AUTH_PROVIDER="local"
AUTHSHIELD_AUTH_SESSION_TIMEOUT="30"
AUTHSHIELD_AUTH_MFA_ENABLED="true"

# External Services
AUTHSHIELD_SMTP_HOST="smtp.example.com"
AUTHSHIELD_SMTP_PORT="587"
AUTHSHIELD_SMTP_USERNAME="..."
AUTHSHIELD_SMTP_PASSWORD="..."

# Logging
AUTHSHIELD_LOG_LEVEL="INFO"
AUTHSHIELD_LOG_FORMAT="json"

# Rate Limiting
AUTHSHIELD_RATE_LIMIT_ENABLED="true"
AUTHSHIELD_RATE_LIMIT_MAX_REQUESTS="100"
AUTHSHIELD_RATE_LIMIT_WINDOW_SECONDS="60"
```

### Environment Variable Rules

| Rule | Example | Counter-Example |
|---|---|---|
| Always UPPER_SNAKE_CASE | `AUTHSHIELD_DATABASE_HOST` | `AUTHSHIELD_database_host` |
| Module prefix | `AUTHSHIELD_AUTH_*` | `AUTH_*` |
| Explicit value types as strings | `AUTHSHIELD_PORT="5432"` | `AUTHSHIELD_PORT=5432` |
| No secrets in defaults | Use vault / secret manager | Hardcoded passwords |
| Suffix for array-like values | `AUTHSHIELD_ALLOWED_ORIGINS="..."` | — |

---

## Migration Naming

### Sequential Timestamps

```python
# Alembic-style
001_create_user_table.py
002_create_session_table.py
003_add_email_index_to_user.py
004_create_course_table.py
005_add_mfa_columns_to_user.py
006_create_audit_log_table.py
007_add_rbac_tables.py
```

---

## Logging & Telemetry Naming

### Structured Log Fields

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "authshield.authentication.service",
  "event": "user_login_successful",
  "user_id": "usr_a1b2c3d4",
  "session_id": "sess_x9y8z7w6",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0",
  "mfa_method": "totp",
  "latency_ms": 45
}
```

### Span & Metric Names

```
# Distributed tracing spans
auth.authentication.validate_credentials
auth.authentication.verify_mfa
auth.session.create
auth.session.validate
users.user.create
courses.course.enroll
simulations.attack.execute

# Prometheus-style metrics
authshield_login_attempts_total
authshield_login_failures_total
authshield_active_sessions
authshield_session_duration_seconds
authshield_api_request_duration_seconds
authshield_rate_limit_hits_total
```

---

## Review Checklist

Before merging any code, verify:

- [ ] All module names are snake_case (Python) or kebab-case (packages)
- [ ] All class names are PascalCase with appropriate suffixes
- [ ] All function names use semantic snake_case prefixes
- [ ] All variables are descriptive with no abbreviations
- [ ] All constants are UPPER_SNAKE_CASE
- [ ] All API endpoints are kebab-case with version prefix
- [ ] All table names are singular snake_case
- [ ] All event names are past-tense PascalCase
- [ ] All error names are PascalCase with Error suffix
- [ ] All env vars follow AUTHSHIELD_{MODULE}_{SETTING} pattern
- [ ] All indexes follow idx_{table}_{column} pattern
- [ ] No generic names (data, result, info, util, helper) are used
- [ ] All naming is consistent with existing patterns in the codebase

---

*Last updated: 2025-01-15*
*Owner: AuthShield Lab Engineering*
