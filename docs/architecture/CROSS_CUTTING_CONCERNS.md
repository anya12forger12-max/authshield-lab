# AuthShield Lab — Cross-Cutting Concerns

> Version: 1.0.0 | Last Updated: 2026-07-19
> Status: Living Document | Owner: Architecture Team

---

## 1. Overview

Cross-cutting concerns are behaviors that span multiple modules. This document defines how AuthShield Lab handles logging, security, accessibility, localization, configuration, error handling, performance, and monitoring across all modules.

Each concern has a **primary implementation module**, **per-module integration points**, and **enforcement mechanisms**.

---

## 2. Logging

### 2.1 Structured Logging Framework

AuthShield Lab uses `structlog` for all logging. Every module integrates with the shared logging module (`packages/logging/`).

**Global Configuration:**

```python
# packages/logging/config.py
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
```

### 2.2 Per-Module Logging Patterns

Each module logs with a module-specific logger name:

```python
# In auth module
import structlog
logger = structlog.get_logger("auth")

logger.info("login.success", user_id=user.id, method="password")
logger.warning("login.failed", email=email, reason="invalid_password")
logger.error("login.error", exc_info=True, user_id=user.id)

# In sessions module
logger = structlog.get_logger("sessions")
logger.info("session.created", session_id=session.id, user_id=user.id)
logger.info("session.expired", session_id=session.id)

# In defense module
logger = structlog.get_logger("defense")
logger.warning("defense.blocked", source=source, reason="rate_limit")
logger.error("defense.alert", threat_level="high", source=source)
```

### 2.3 Log Levels by Module

| Module | Default Level | Production Level | Reason |
|---|---|---|---|
| `auth` | INFO | INFO | Security-relevant events |
| `users` | INFO | WARNING | User lifecycle events |
| `sessions` | INFO | WARNING | Session events |
| `audit` | WARNING | WARNING | Audit pipeline health |
| `policies` | INFO | WARNING | Policy evaluations |
| `rules` | INFO | WARNING | Rule evaluations |
| `defense` | WARNING | WARNING | Defense actions |
| `content` | INFO | WARNING | Content operations |
| `lms` | INFO | INFO | Learning events (analytics) |
| `simulation` | INFO | INFO | Simulation events |
| `developer` | INFO | WARNING | Developer tooling |
| `quality` | INFO | WARNING | Quality checks |
| `production` | WARNING | WARNING | Production health |
| `ecosystem` | INFO | WARNING | Plugin lifecycle |
| `certification` | INFO | WARNING | Certification events |
| `analytics` | INFO | INFO | Analytics pipeline |
| `learning` | INFO | INFO | Learning events |

### 2.4 Logging Rules

1. **No secrets in logs.** The logging module sanitizes values matching secret patterns.
2. **No PII in logs.** User emails and names are redacted; only user IDs are logged.
3. **Correlation IDs propagate.** Every log entry includes the `correlation_id` from the request context.
4. **Log rotation.** Log files rotate daily, retained for 30 days.
5. **Structured format only.** No free-text log messages — all entries are key-value pairs.

### 2.5 Log Sanitization

```python
# packages/logging/sanitizers.py
SENSITIVE_KEYS = {"password", "token", "secret", "api_key", "credit_card", "ssn"}

def sanitize_log_entry(entry: dict) -> dict:
    for key, value in entry.items():
        if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
            entry[key] = "[REDACTED]"
        elif isinstance(value, dict):
            entry[key] = sanitize_log_entry(value)
    return entry
```

---

## 3. Security

### 3.1 Authentication Middleware

All protected routes require authentication via the `auth` module's middleware:

```python
# backend/app/middleware/auth.py
class AuthenticationMiddleware:
    """Validates session tokens on protected routes."""
    
    EXEMPT_PATHS = [
        "/api/auth/login",
        "/api/auth/register",
        "/api/health",
        "/docs",
    ]
    
    async def __call__(self, request, call_next):
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return JSONResponse(status_code=401, content={"error": "Missing token"})
        
        session = await session_service.validate(token)
        if session is None:
            return JSONResponse(status_code=401, content={"error": "Invalid token"})
        
        request.state.user_id = session.user_id
        return await call_next(request)
```

### 3.2 Input Validation

All inputs are validated against schemas before reaching business logic:

```python
# packages/validation/middleware.py
from pydantic import BaseModel, Field, validator

class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator("email")
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()
```

**Validation rules per module:**

| Module | Key Validations |
|---|---|
| `auth` | Email format, password complexity, MFA token length |
| `users` | Name length, role validity, email uniqueness |
| `sessions` | Token format, TTL bounds |
| `policies` | Policy DSL syntax, rule references |
| `content` | Title length, content type, metadata schema |
| `lms` | Path structure, enrollment limits, grade ranges |
| `simulation` | Scenario structure, action types, timeout bounds |

### 3.3 CSRF Protection

CSRF tokens are validated on all state-changing requests:

```python
# backend/app/middleware/csrf.py
class CSRFMiddleware:
    def __init__(self, secret_key: str):
        self._secret_key = secret_key
    
    async def __call__(self, request, call_next):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return await call_next(request)
        
        token = request.headers.get("X-CSRF-Token")
        if not token or not self._verify_token(token):
            return JSONResponse(status_code=403, content={"error": "CSRF validation failed"})
        
        return await call_next(request)
```

### 3.4 Rate Limiting

Rate limiting is enforced by the `security` module:

```python
# security module configuration
RATE_LIMITS = {
    "auth/login": {"max": 5, "window": 60},        # 5 attempts per minute
    "auth/register": {"max": 3, "window": 300},     # 3 per 5 minutes
    "api/default": {"max": 100, "window": 60},      # 100 per minute
    "api/admin": {"max": 200, "window": 60},        # 200 per minute
}
```

### 3.5 Security Headers

All responses include security headers:

```python
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}
```

### 3.6 Password Hashing

```python
# auth module — password hashing
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

### 3.7 Security Audit Trail

Every security-relevant action is logged via the `audit` module:

| Action | Module | Event Type |
|---|---|---|
| Login success | `auth` | `auth.login.success` |
| Login failure | `auth` | `auth.login.failed` |
| Password change | `auth` | `auth.password.changed` |
| MFA setup | `auth` | `auth.mfa.enabled` |
| Session created | `sessions` | `sessions.created` |
| Session revoked | `sessions` | `sessions.revoked` |
| Permission denied | `security` | `security.permission.denied` |
| Rate limit hit | `security` | `security.rate_limit.exceeded` |
| Defense action | `defense` | `defense.blocked` |
| Plugin installed | `ecosystem` | `ecosystem.plugin.installed` |

---

## 4. Accessibility

### 4.1 WCAG 2.2 AA Compliance

All UI components must meet WCAG 2.2 AA standards. Compliance is enforced via:

1. **axe-core** automated testing in CI.
2. **Manual audit** quarterly (reports in `accessibility/audits/`).
3. **Developer training** via `docs/accessibility/ACCESSIBILITY_GUIDE.md`.

### 4.2 Per-Module Accessibility Requirements

| Module | UI Components | WCAG Requirements |
|---|---|---|
| `auth` | Login form, registration form, MFA input | 1.3.1 (Info and Relationships), 1.4.3 (Contrast), 2.4.7 (Focus Visible) |
| `users` | User list, profile form, role manager | 1.3.1, 1.4.3, 2.4.6 (Headings), 3.3.2 (Labels) |
| `lms` | Learning paths, progress bars, quizzes | 1.1.1 (Alt Text), 1.3.1, 1.4.3, 2.1.1 (Keyboard), 2.4.3 (Focus Order) |
| `simulation` | Scenario builder, attack panel, results | 1.1.1, 1.3.1, 1.4.3, 2.1.1, 4.1.2 (Name/Role/Value) |
| `content` | Content viewer, editor, search | 1.1.1, 1.3.1, 1.4.3, 2.4.1 (Bypass Blocks) |
| `developer` | API explorer, extension manager | 1.3.1, 1.4.3, 2.1.1, 3.3.2 |
| `reports` | Report viewer, chart components | 1.1.1 (chart alternatives), 1.3.1, 1.4.3 |
| `analytics` | Dashboard, metric cards, charts | 1.1.1, 1.3.1, 1.4.3, 2.4.6 |

### 4.3 Accessibility Testing

```python
# tests/accessibility/conftest.py
import axe

@pytest.mark.a11y
def test_login_form_accessibility(page):
    """Login form must pass axe-core scan."""
    page.goto("/login")
    results = axe.run(page)
    assert results.violations == [], f"A11y violations: {results.violations}"
```

### 4.4 Keyboard Navigation

All interactive elements must be keyboard-navigable:
- Tab order follows visual order.
- Focus indicators are visible (minimum 3:1 contrast ratio).
- Modal dialogs trap focus.
- Escape key closes modals.
- Enter/Space activates buttons.

### 4.5 Screen Reader Support

- All images have `alt` text.
- Form inputs have associated `<label>` elements.
- ARIA roles are used for custom components.
- Live regions (`aria-live`) are used for dynamic content updates.
- Error messages are associated with inputs via `aria-describedby`.

---

## 5. Localization (i18n)

### 5.1 Translation Framework

Translations are stored in `localization/locales/` and loaded via the shared config module:

```python
# packages/config/i18n.py
def get_translator(locale: str) -> Translator:
    """Load translations for the given locale."""
    path = f"localization/locales/{locale}.json"
    with open(path) as f:
        translations = json.load(f)
    return Translator(translations, fallback=translations.get("en", {}))
```

### 5.2 Translation Key Convention

```json
{
  "auth": {
    "login": {
      "title": "Sign In",
      "email_label": "Email Address",
      "password_label": "Password",
      "submit_button": "Sign In",
      "error": {
        "invalid_credentials": "The email or password you entered is incorrect.",
        "rate_limited": "Too many attempts. Please try again in {minutes} minutes.",
        "account_locked": "Your account has been locked. Contact support."
      }
    }
  },
  "users": {
    "profile": {
      "title": "Your Profile",
      "name_label": "Full Name",
      "email_label": "Email Address"
    }
  }
}
```

### 5.3 Per-Module i18n Coverage

| Module | Strings | Coverage | Status |
|---|---|---|---|
| `auth` | 25 | 100% | Complete |
| `users` | 18 | 100% | Complete |
| `sessions` | 8 | 100% | Complete |
| `lms` | 45 | 95% | In Progress |
| `simulation` | 35 | 90% | In Progress |
| `content` | 20 | 85% | In Progress |
| `developer` | 15 | 80% | In Progress |
| `reports` | 12 | 75% | In Progress |
| `analytics` | 10 | 70% | Planned |

### 5.4 i18n Rules

1. All user-facing strings must be externalized (no hardcoded strings in UI code).
2. String interpolation uses named placeholders: `{minutes}`, `{count}`, `{name}`.
3. Pluralization uses CLDR rules: `{count} {count, plural, one {item} other {items}}`.
4. Date/number formatting follows locale conventions.
5. RTL layout is supported via CSS logical properties.

---

## 6. Configuration

### 6.1 Settings Hierarchy

Configuration is loaded in strict priority order (highest to lowest):

```
1. Environment Variables (AUTHSHIELD_<MODULE>_<KEY>)
2. Local config file (./authshield.local.json)
3. User config file (~/.config/authshield/config.json)
4. App config (apps/<app>/config/<env>.json)
5. Shared config (configs/shared.json)
6. Package defaults (packages/config/defaults.json)
```

### 6.2 Per-Module Configuration

Each module declares its configuration schema:

```python
# packages/config/schemas/auth.py
from pydantic import BaseModel, Field

class AuthConfig(BaseModel):
    session_ttl: int = Field(default=3600, ge=60, le=86400)
    max_login_attempts: int = Field(default=5, ge=1, le=20)
    lockout_duration: int = Field(default=900, ge=60, le=7200)
    password_min_length: int = Field(default=8, ge=6, le=128)
    password_require_uppercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = True
    mfa_enabled: bool = False
    mfa_issuer: str = "AuthShield Lab"
```

### 6.3 Configuration Validation

All configuration is validated at startup against the schema. Invalid configuration causes an immediate failure:

```python
# Startup validation
try:
    config = load_config()
    validate_all_schemas(config)
except ValidationError as e:
    logger.critical("Configuration validation failed", errors=e.errors())
    sys.exit(1)
```

### 6.4 Configuration Access Pattern

```python
# In any module
from packages.config import get_config

config = get_config("auth")
ttl = config.session_ttl  # Typed, validated, with default
```

---

## 7. Error Handling

### 7.1 Global Error Handler

FastAPI's exception handler catches all unhandled exceptions:

```python
# backend/app/middleware/error_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse

async def global_error_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = request.state.correlation_id
    
    logger.error(
        "unhandled_exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        method=request.method,
        correlation_id=correlation_id,
        exc_info=True,
    )
    
    # Publish error event for monitoring
    await event_bus.publish(Event(
        type="system.unhandled_error",
        source="global_error_handler",
        payload={
            "exception_type": type(exc).__name__,
            "path": request.url.path,
        },
        metadata={"correlation_id": correlation_id},
    ))
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "correlation_id": correlation_id,
            }
        },
    )
```

### 7.2 Module-Specific Error Types

```python
# packages/errors/base.py
class AuthShieldError(Exception):
    """Base error for all AuthShield modules."""
    code: str = "UNKNOWN_ERROR"
    status_code: int = 500
    module: str = "unknown"

class AuthenticationError(AuthShieldError):
    code = "AUTH_ERROR"
    status_code = 401
    module = "auth"

class AuthorizationError(AuthShieldError):
    code = "FORBIDDEN"
    status_code = 403
    module = "security"

class ValidationError(AuthShieldError):
    code = "VALIDATION_ERROR"
    status_code = 400
    module = "validation"

class NotFoundError(AuthShieldError):
    code = "NOT_FOUND"
    status_code = 404

class ConflictError(AuthShieldError):
    code = "CONFLICT"
    status_code = 409

class RateLimitError(AuthShieldError):
    code = "RATE_LIMITED"
    status_code = 429
    module = "security"
```

### 7.3 Error Handling per Module

| Module | Primary Errors | Handling Strategy |
|---|---|---|
| `auth` | `AuthenticationError`, `RateLimitError` | Log + audit + return error |
| `users` | `NotFoundError`, `ConflictError` | Log + return error |
| `sessions` | `NotFoundError`, `ExpiredError` | Log + audit + return error |
| `policies` | `PolicyViolationError` | Log + audit + defense action |
| `defense` | `DefenseBlockedError` | Log + audit + alert |
| `simulation` | `SimulationError`, `TimeoutError` | Log + audit + return error |
| `quality` | `QualityViolationError` | Log + return report |
| `production` | `ProductionError` | Log + audit + alert |

---

## 8. Performance

### 8.1 Caching Strategy

| Data Type | Cache Layer | TTL | Invalidation |
|---|---|---|---|
| User profiles | L1 + L2 | 60s / 300s | On `users.updated` event |
| Session tokens | L1 only | Session TTL | On session destroy |
| Policies | L1 + L2 | 300s / 3600s | On `policies.updated` event |
| Content | L1 + L2 | 120s / 600s | On `content.published` event |
| Learning paths | L1 + L2 | 300s / 1800s | On path update event |
| Audit logs | None (append-only) | N/A | Never (immutable) |
| Feature flags | L1 only | 30s | On flag toggle event |

### 8.2 Pagination

All list endpoints use cursor-based pagination:

```python
# packages/validation/pagination.py
class PaginationParams(BaseModel):
    cursor: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = "desc"

class PaginatedResponse(BaseModel):
    items: list
    next_cursor: Optional[str]
    has_more: bool
    total: int
```

### 8.3 Database Connection Pooling

```python
# packages/config/database.py
DATABASE_POOL_CONFIG = {
    "min_connections": 2,
    "max_connections": 10,
    "connection_timeout": 5.0,
    "idle_timeout": 300.0,
    "max_lifetime": 3600.0,
}
```

### 8.4 Query Optimization

- All list queries use indexed columns for filtering.
- N+1 query patterns are forbidden (enforced by linter).
- Eager loading is used for related data within a module.
- Cross-module data access uses the owning module's API (which may cache).

### 8.5 Performance Budgets

| Operation | Budget | Measurement |
|---|---|---|
| API response time (p95) | < 200ms | `api.response_time.p95` |
| API response time (p99) | < 500ms | `api.response_time.p99` |
| Database query (p95) | < 50ms | `db.query_time.p95` |
| Event bus dispatch (p95) | < 1ms | `event_bus.dispatch_time.p95` |
| Cache read (p95) | < 1ms | `cache.read_time.p95` |
| Authentication flow | < 300ms | `auth.flow_time.p95` |
| Page load (LCP) | < 2.5s | `web.lcp` |
| First Input Delay | < 100ms | `web.fid` |

---

## 9. Monitoring

### 9.1 Health Checks

Every module exposes a health check endpoint:

```python
# Module health check pattern
def check_auth_health() -> HealthStatus:
    checks = {
        "database": check_database_connection(),
        "event_bus": check_event_bus_health(),
        "cache": check_cache_health(),
    }
    
    status = "healthy" if all(c["status"] == "ok" for c in checks.values()) else "degraded"
    
    return HealthStatus(
        module="auth",
        status=status,
        checks=checks,
        timestamp=datetime.utcnow().isoformat(),
    )
```

### 9.2 Metrics Collection

| Metric Category | Metrics | Module |
|---|---|---|
| **Request** | `http_requests_total`, `http_request_duration_seconds` | All API modules |
| **Auth** | `auth_login_attempts_total`, `auth_login_failures_total` | `auth` |
| **Session** | `sessions_active_total`, `sessions_created_total` | `sessions` |
| **Defense** | `defense_actions_total`, `defense_blocks_total` | `defense` |
| **Event Bus** | `event_bus_published_total`, `event_bus_dispatched_total` | `event-bus` |
| **Database** | `db_query_duration_seconds`, `db_connections_active` | All DB modules |
| **Cache** | `cache_hits_total`, `cache_misses_total` | `optimization` |
| **LMS** | `lms_enrollments_total`, `lms_completions_total` | `lms` |
| **Quality** | `quality_checks_total`, `quality_violations_total` | `quality` |
| **Production** | `production_releases_total`, `production_health_score` | `production` |

### 9.3 Alerting Rules

| Alert | Condition | Severity | Module |
|---|---|---|---|
| High error rate | 5xx rate > 5% for 5 min | Critical | All |
| Auth lockout spike | Lockouts > 50/hour | High | `auth` |
| Defense alert surge | Alerts > 100/hour | Critical | `defense` |
| Event bus backlog | Queue depth > 1000 | High | `event-bus` |
| Database connection pool exhaustion | Active connections > 90% of max | Critical | All DB modules |
| Cache hit rate drop | Hit rate < 80% for 10 min | Medium | `optimization` |
| Circuit breaker open | Any circuit open > 5 min | High | All |
| Health check failure | Module health != "healthy" for 3 min | High | All |

### 9.4 Observability Stack

```
┌─────────────────────────────────────────────────────┐
│                  Application Layer                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │  structlog│ │ metrics  │ │traces    │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │                    │
│       ▼            ▼            ▼                    │
│  ┌─────────────────────────────────────┐           │
│  │         OpenTelemetry Collector      │           │
│  └────┬────────┬────────┬──────────────┘           │
│       │        │        │                          │
│       ▼        ▼        ▼                          │
│  ┌────────┐ ┌────────┐ ┌────────┐                 │
│  │  Logs  │ │Metrics │ │Traces  │                 │
│  │( Loki) │ │(Prom)  │ │(Jaeger)│                 │
│  └────────┘ └────────┘ └────────┘                 │
└─────────────────────────────────────────────────────┘
```

---

## 10. Cross-Cutting Concern Enforcement

### 10.1 CI Gates

| Gate | Tool | Failure Behavior |
|---|---|---|
| Lint (boundary check) | `tools/linters/boundary-check.py` | Block merge |
| Type check | mypy / pyright | Block merge |
| Test coverage | pytest-cov (> 80%) | Block merge |
| Security scan | bandit, secret-scanner | Block merge |
| Accessibility scan | axe-core | Block merge (UI changes) |
| Schema validation | `tools/validators/validate-schemas.py` | Block merge |
| License check | license-checker | Block merge |
| Performance regression | benchmark suite | Block merge (> 10% regression) |

### 10.2 Pre-Commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: boundary-check
        name: Architecture Boundary Check
        entry: python tools/linters/boundary-check.py
        language: system
        files: \.py$
      - id: secret-scan
        name: Secret Scanner
        entry: python security/tools/secret-scanner.py
        language: system
      - id: schema-validate
        name: Schema Validation
        entry: python tools/validators/validate-schemas.py
        language: system
```

---

## 11. References

- [WORKSPACE_ARCHITECTURE.md](./WORKSPACE_ARCHITECTURE.md) — Workspace layout
- [MODULE_BOUNDARIES.md](./MODULE_BOUNDARIES.md) — Module boundaries
- [SERVICE_COMMUNICATION.md](./SERVICE_COMMUNICATION.md) — Communication patterns
- [DATA_FLOW.md](./DATA_FLOW.md) — Data lifecycle
- [LOGGING_ARCHITECTURE.md](../standards/LOGGING_ARCHITECTURE.md) — Logging standards
- [SECURITY_ENGINEERING.md](../standards/SECURITY_ENGINEERING.md) — Security standards
- [ACCESSIBILITY_FOUNDATION.md](../standards/ACCESSIBILITY_FOUNDATION.md) — A11y standards
- [LOCALIZATION_FOUNDATION.md](../standards/LOCALIZATION_FOUNDATION.md) — i18n standards
- [CONFIGURATION_MANAGEMENT.md](../standards/CONFIGURATION_MANAGEMENT.md) — Config standards
- [QUALITY_STANDARDS.md](../standards/QUALITY_STANDARDS.md) — Quality standards
