# Unified Error Handling Contracts

## Document Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Status | Authoritative |
| Last Updated | 2026-07-19 |
| Owner | Architecture Team |
| Classification | Internal |

---

## 1. Overview

AuthShield Lab uses a unified error handling system across all services, APIs, and plugin interfaces. Every error is categorized, coded, typed, and formatted consistently to enable automated handling, user-friendly messaging, and developer diagnostics.

### 1.1 Error Design Principles

| Principle | Description |
|-----------|-------------|
| Machine-Readable | Every error has a unique code for programmatic handling |
| Human-Readable | Every error has a plain-language message for users |
| Contextual | Every error includes sufficient detail for developers |
| Recoverable | Every error includes recovery guidance when applicable |
| Correlated | Every error carries a correlation ID for tracing |
| Logged | Every error is logged with full context |

---

## 2. Error Code Schema

### 2.1 Format

```
MODULE-CATEGORY-NNN
```

| Component | Description | Examples |
|-----------|-------------|---------|
| MODULE | Two-to-four letter module identifier | `AUTH`, `COURSE`, `PLUGIN` |
| CATEGORY | Three-letter error category | `VAL`, `SEC`, `TMO` |
| NNN | Three-digit sequential number | `001`, `002`, `099` |

### 2.2 Module Identifiers

| Module | Prefix | Description |
|--------|--------|-------------|
| Authentication | `AUTH` | User authentication and session management |
| Authorization | `AUTHZ` | Access control and permissions |
| Identity | `IDENT` | User profiles and preferences |
| Course Management | `COURSE` | Course CRUD and publishing |
| Learning Engine | `LEARN` | Student progress and enrollment |
| Assessment Engine | `ASSESS` | Assessments and scoring |
| Certificate | `CERT` | Certificate generation and issuance |
| Reporting | `REPORT` | Report generation and retrieval |
| Analytics | `ANALYT` | Analytics and metrics |
| Configuration | `CONFIG` | Platform configuration |
| Localization | `L10N` | Internationalization |
| Accessibility | `A11Y` | Accessibility features |
| Notifications | `NOTIF` | User notifications |
| Backup | `BACKUP` | Data backup and restore |
| Audit | `AUDIT` | Audit logging |
| Logging | `LOG` | Structured logging |
| Plugin Runtime | `PLUGIN` | Plugin lifecycle management |
| SDK Runtime | `SDK` | SDK API surface |
| Diagnostics | `DIAG` | System diagnostics |
| Help System | `HELP` | Help content and documentation |
| Administration | `ADMIN` | Administrative operations |
| System | `SYS` | Platform-level errors |
| Event Bus | `EBUS` | Event bus operations |
| IPC | `IPC` | Inter-process communication |
| Database | `DB` | Data access layer |
| File System | `FS` | File operations |

### 2.3 Category Codes

| Category | Code | Description |
|----------|------|-------------|
| Validation | `VAL` | Input validation failures |
| Authorization | `AUTH` | Permission and access control errors |
| Authentication | `SEC` | Identity verification errors |
| Timeout | `TMO` | Operation timeout errors |
| Service Unavailable | `UNAV` | Service not available |
| Plugin Failure | `PLUG` | Plugin execution errors |
| Version Mismatch | `VER` | Compatibility errors |
| Configuration | `CONF` | Configuration errors |
| Accessibility | `A11Y` | Accessibility errors |
| Localization | `L10N` | Localization errors |
| Not Found | `NF` | Resource not found |
| Conflict | `CNFL` | State conflict errors |
| Rate Limit | `RATE` | Rate limiting errors |
| Integrity | `INTG` | Data integrity errors |
| Quota | `QUOT` | Resource quota exceeded |

---

## 3. Error Response Format

### 3.1 Standard Error Envelope (RFC 7807)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ErrorResponse",
  "type": "object",
  "required": ["code", "message", "severity", "correlation_id", "timestamp"],
  "properties": {
    "code": {
      "type": "string",
      "pattern": "^[A-Z]+-[A-Z]+-\\d{3}$",
      "description": "Unique error code"
    },
    "message": {
      "type": "string",
      "description": "User-facing error message (plain language)"
    },
    "details": {
      "type": "object",
      "description": "Developer-facing error context"
    },
    "severity": {
      "type": "string",
      "enum": ["low", "medium", "high", "critical"],
      "description": "Error severity level"
    },
    "correlation_id": {
      "type": "string",
      "description": "Request/operation correlation ID"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Error occurrence timestamp"
    },
    "recovery": {
      "type": "object",
      "description": "Recovery guidance",
      "properties": {
        "action": { "type": "string" },
        "retry_after": { "type": "number" },
        "documentation_url": { "type": "string" }
      }
    },
    "errors": {
      "type": "array",
      "description": "Nested validation errors",
      "items": {
        "type": "object",
        "properties": {
          "field": { "type": "string" },
          "code": { "type": "string" },
          "message": { "type": "string" },
          "rejected_value": {}
        }
      }
    }
  }
}
```

### 3.2 Minimal Error Response

```json
{
  "code": "AUTH-AUTH-001",
  "message": "Invalid credentials. Please check your username and password.",
  "severity": "medium",
  "correlation_id": "req-abc-123",
  "timestamp": "2026-07-19T12:00:00Z"
}
```

### 3.3 Full Error Response with Recovery

```json
{
  "code": "DB-UNAV-001",
  "message": "Unable to connect to the database. The application will retry automatically.",
  "details": {
    "database": "authshield.db",
    "error": "SQLITE_BUSY",
    "attempt": 3,
    "max_attempts": 5
  },
  "severity": "high",
  "correlation_id": "req-def-456",
  "timestamp": "2026-07-19T12:00:00Z",
  "recovery": {
    "action": "Automatic retry in progress",
    "retry_after": 5.0
  }
}
```

### 3.4 Validation Error Response

```json
{
  "code": "COURSE-VAL-001",
  "message": "One or more fields contain invalid values.",
  "severity": "low",
  "correlation_id": "req-ghi-789",
  "timestamp": "2026-07-19T12:00:00Z",
  "errors": [
    {
      "field": "title",
      "code": "COURSE-VAL-001",
      "message": "Title is required and cannot be empty",
      "rejected_value": ""
    },
    {
      "field": "difficulty_level",
      "code": "COURSE-VAL-003",
      "message": "Must be one of: beginner, intermediate, advanced, expert",
      "rejected_value": "easy"
    }
  ]
}
```

---

## 4. Error Categories and Handling

### 4.1 Validation Errors

| Code Range | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| `*-VAL-001` | Required field missing | Low | User correction |
| `*-VAL-002` | Invalid field format | Low | User correction |
| `*-VAL-003` | Value out of range | Low | User correction |
| `*-VAL-004` | Invalid enum value | Low | User correction |
| `*-VAL-005` | String too long | Low | User correction |
| `*-VAL-006` | String too short | Low | User correction |
| `*-VAL-010` | Resource not found | Low | Verify resource ID |

**Recovery Strategy:** Display validation errors inline; no retry needed.

### 4.2 Authentication Errors

| Code Range | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| `AUTH-SEC-001` | Rate limit exceeded | Medium | Wait and retry |
| `AUTH-SEC-002` | Invalid credentials | Medium | Re-enter credentials |
| `AUTH-SEC-003` | Account locked | High | Contact administrator |
| `AUTH-SEC-004` | Account disabled | High | Contact administrator |
| `AUTH-SEC-005` | Token expired | Low | Refresh token |
| `AUTH-SEC-006` | Token revoked | Medium | Re-authenticate |

**Recovery Strategy:** Exponential backoff for rate limits; token refresh for expiry.

### 4.3 Authorization Errors

| Code Range | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| `AUTHZ-AUTH-001` | Insufficient permissions | Medium | Request elevation |
| `AUTHZ-AUTH-002` | Role required | Medium | Assign role |
| `AUTHZ-AUTH-003` | Resource access denied | Medium | Request access |
| `AUTHZ-AUTH-004` | Self-modification denied | Low | Use admin interface |

**Recovery Strategy:** Inform user of required permissions; suggest admin contact.

### 4.4 Timeout Errors

| Code Range | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| `*-TMO-001` | Operation timed out | Medium | Retry with backoff |
| `*-TMO-002` | Connection timed out | High | Check connectivity |
| `*-TMO-003` | Processing timeout | Medium | Simplify request |

**Recovery Strategy:** Retry with exponential backoff; reduce request complexity.

### 4.5 Service Unavailable Errors

| Code Range | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| `*-UNAV-001` | Service not initialized | High | Wait for initialization |
| `*-UNAV-002` | Service degraded | Medium | Retry or use fallback |
| `*-UNAV-003` | Service shutting down | High | Wait for restart |
| `*-UNAV-004` | Circuit breaker open | High | Wait for recovery |

**Recovery Strategy:** Wait for service health recovery; implement circuit breaker patterns.

### 4.6 Plugin Errors

| Code Range | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| `PLUGIN-PLUG-001` | Plugin failed to load | Medium | Check plugin compatibility |
| `PLUGIN-PLUG-002` | Plugin crashed | High | Restart plugin |
| `PLUGIN-PLUG-003` | Plugin timeout | Medium | Check plugin code |
| `PLUGIN-PLUG-004` | Plugin quota exceeded | Medium | Reduce plugin usage |
| `PLUGIN-PLUG-005` | Plugin dependency missing | High | Install dependency |

**Recovery Strategy:** Isolate failed plugin; auto-disable on repeated failures.

### 4.7 Version Mismatch Errors

| Code Range | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| `*-VER-001` | SDK version incompatible | High | Update SDK or plugin |
| `*-VER-002` | API version not supported | Medium | Use supported version |
| `*-VER-003` | Protocol version mismatch | High | Update client |

**Recovery Strategy:** Check compatibility matrix; update to compatible version.

### 4.8 Configuration Errors

| Code Range | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| `CONFIG-CONF-001` | Invalid configuration value | Medium | Correct configuration |
| `CONFIG-CONF-002` | Missing required configuration | High | Set configuration |
| `CONFIG-CONF-003` | Configuration file corrupted | High | Restore from backup |
| `CONFIG-CONF-004` | Configuration read-only | Low | Use admin interface |

**Recovery Strategy:** Reset to defaults; restore from backup.

### 4.9 Database Errors

| Code Range | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| `DB-INTG-001` | Data integrity violation | High | Check data consistency |
| `DB-UNAV-001` | Database locked | Medium | Retry after delay |
| `DB-UNAV-002` | Database corrupted | Critical | Restore from backup |
| `DB-QUOT-001` | Storage quota exceeded | High | Free space or expand |
| `DB-NF-001` | Record not found | Low | Verify record exists |

**Recovery Strategy:** Automatic retry for locks; backup restore for corruption.

---

## 5. Error Severity Levels

| Level | Description | User Impact | System Impact | Logging |
|-------|-------------|-------------|---------------|---------|
| `low` | Minor issues, easily recoverable | Minimal | None | DEBUG |
| `medium` | Issues requiring user action | Moderate | None | WARNING |
| `high` | Significant issues affecting functionality | Significant | Degraded | ERROR |
| `critical` | Severe issues affecting system stability | Complete | Failed | CRITICAL |

### 5.1 Severity Escalation Rules

| Condition | Escalation |
|-----------|-----------|
| Same error 3+ times in 5 minutes | Low → Medium |
| Same error 10+ times in 1 hour | Medium → High |
| Service failure detected | Any → High |
| Data integrity issue | Any → Critical |
| Security breach detected | Any → Critical |

---

## 6. User-Facing Error Messages

### 6.1 Principles

- Written in plain language (8th-grade reading level)
- No technical jargon
- Include actionable guidance
- Never expose internal details
- Localized to user's locale

### 6.2 Message Templates

| Code | User Message |
|------|-------------|
| `AUTH-SEC-002` | "Invalid username or password. Please try again." |
| `AUTH-SEC-005` | "Your session has expired. Please sign in again." |
| `AUTH-SEC-001` | "Too many failed attempts. Please wait {retry_after} seconds." |
| `AUTHZ-AUTH-001` | "You don't have permission to perform this action." |
| `COURSE-VAL-001` | "Please provide a course title." |
| `COURSE-NF-001` | "The course you're looking for was not found." |
| `PLUGIN-PLUG-001` | "A plugin failed to load. It has been temporarily disabled." |
| `DB-UNAV-001` | "The system is temporarily busy. Please try again in a moment." |
| `CONFIG-CONF-003` | "Configuration data appears corrupted. Please contact your administrator." |
| `BACKUP-INTG-001` | "Backup file appears corrupted. Please try creating a new backup." |
| `SDK-TMO-001` | "The operation took too long. Please try again." |
| `SYS-UNAV-001` | "The system is starting up. Please wait a moment." |

### 6.3 Message Interpolation

User messages support variable interpolation:

```
"Too many failed attempts. Please wait {retry_after} seconds."
"You have {attempts_remaining} attempts remaining before your account is locked."
"Course '{course_title}' has been published successfully."
```

---

## 7. Developer Error Messages

### 7.1 Details Object

The `details` object in error responses provides context for developers:

```python
@dataclass
class ErrorDetails:
    service: str              # e.g., "authentication_service"
    method: str               # e.g., "authenticate_user"
    parameters: dict          # Input parameters (redacted sensitive values)
    stack_trace: str | None   # Only in development mode
    internal_error: str | None  # Original exception message
    database_query: str | None  # SQL query if DB error (redacted)
    plugin_id: str | None     # Plugin context if applicable
    sdk_method: str | None    # SDK method if applicable
```

### 7.2 Development Mode

In development mode, additional details are included:
- Full stack traces
- Internal error messages
- SQL queries
- Full parameter values (no redaction)

---

## 8. Error Logging Requirements

### 8.1 Log Entry Format

```json
{
  "timestamp": "2026-07-19T12:00:00Z",
  "level": "ERROR",
  "logger": "authshield.authentication",
  "message": "Authentication failed",
  "error_code": "AUTH-SEC-002",
  "correlation_id": "req-abc-123",
  "user_id": null,
  "plugin_id": null,
  "service": "authentication_service",
  "method": "authenticate_user",
  "duration_ms": 150,
  "context": {
    "username": "[REDACTED]",
    "attempt_number": 3,
    "source_ip": "127.0.0.1"
  },
  "exception": {
    "type": "AuthenticationError",
    "message": "Invalid credentials",
    "stack_trace": "..."
  }
}
```

### 8.2 Logging Rules

| Rule | Description |
|------|-------------|
| All errors logged | Every error response generates a log entry |
| Sensitive data redacted | Passwords, tokens, PII are never logged |
| Correlation ID propagated | Same ID in response and log entry |
| Duration captured | All error logs include operation duration |
| Stack traces in debug | Full traces only in development mode |
| Audit for security | Security errors logged to audit trail |

---

## 9. Error Correlation

### 9.1 Correlation ID Generation

```python
import uuid

def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracing."""
    return f"req-{uuid.uuid4().hex[:12]}"
```

### 9.2 Correlation Flow

```
1. Client generates or provides correlation_id
2. ID attached to request context
3. All service calls within request share the ID
4. Error responses include the ID
5. Log entries include the ID
6. Audit entries include the ID
7. Developer can trace full request lifecycle using the ID
```

### 9.3 Cross-Service Correlation

When an error occurs across service boundaries, the correlation ID propagates:

```
API Handler (req-abc-123)
  → Authentication Service (req-abc-123)
    → Authorization Service (req-abc-123)
      → Error: AUTHZ-AUTH-001 (req-abc-123)
```

All log entries for this request share `req-abc-123`, enabling complete trace reconstruction.

---

## 10. Complete Error Code Reference

### 10.1 Authentication Module

| Code | Category | Message | Severity |
|------|----------|---------|----------|
| `AUTH-VAL-001` | Validation | Invalid username format | Low |
| `AUTH-VAL-002` | Validation | Missing password | Low |
| `AUTH-SEC-001` | Authentication | Rate limit exceeded | Medium |
| `AUTH-SEC-002` | Authentication | Invalid credentials | Medium |
| `AUTH-SEC-003` | Authentication | Account locked | High |
| `AUTH-SEC-004` | Authentication | Account disabled | High |
| `AUTH-SEC-005` | Authentication | Token expired | Low |
| `AUTH-SEC-006` | Authentication | Token revoked | Medium |
| `AUTH-TMO-001` | Timeout | Authentication timeout | Medium |
| `AUTH-NF-001` | Not Found | User not found | Low |
| `AUTH-UNAV-001` | Unavailable | Authentication service unavailable | High |

### 10.2 Authorization Module

| Code | Category | Message | Severity |
|------|----------|---------|----------|
| `AUTHZ-AUTH-001` | Authorization | Insufficient permissions | Medium |
| `AUTHZ-AUTH-002` | Authorization | Role required | Medium |
| `AUTHZ-AUTH-003` | Authorization | Resource access denied | Medium |
| `AUTHZ-AUTH-004` | Authorization | Self-modification denied | Low |
| `AUTHZ-VAL-001` | Validation | Invalid role name | Low |
| `AUTHZ-VAL-002` | Validation | Cannot assign admin role to self | Low |
| `AUTHZ-NF-001` | Not Found | Role not found | Low |
| `AUTHZ-UNAV-001` | Unavailable | Authorization service unavailable | High |

### 10.3 Course Management Module

| Code | Category | Message | Severity |
|------|----------|---------|----------|
| `COURSE-VAL-001` | Validation | Title is required | Low |
| `COURSE-VAL-002` | Validation | Title exceeds maximum length | Low |
| `COURSE-VAL-003` | Validation | Invalid difficulty level | Low |
| `COURSE-VAL-004` | Validation | Invalid prerequisite course ID | Low |
| `COURSE-VAL-005` | Validation | Course has no lessons | Low |
| `COURSE-VAL-006` | Validation | Lessons fail validation | Low |
| `COURSE-VAL-007` | Validation | Course not in publishable state | Low |
| `COURSE-VAL-008` | Validation | Prerequisite course not published | Low |
| `COURSE-VAL-010` | Not Found | Course not found | Low |
| `COURSE-CNFL-001` | Conflict | Course already published | Low |
| `COURSE-CNFL-002` | Conflict | Course has active enrollments | Medium |
| `COURSE-AUTH-001` | Authorization | Cannot modify course | Medium |
| `COURSE-UNAV-001` | Unavailable | Course service unavailable | High |

### 10.4 Plugin Module

| Code | Category | Message | Severity |
|------|----------|---------|----------|
| `PLUGIN-VAL-001` | Validation | Invalid plugin package | Medium |
| `PLUGIN-VAL-002` | Validation | Plugin manifest malformed | Medium |
| `PLUGIN-SEC-001` | Security | Plugin signature verification failed | High |
| `PLUGIN-SEC-002` | Security | Prohibited capabilities declared | High |
| `PLUGIN-VER-001` | Version | SDK version incompatible | High |
| `PLUGIN-PLUG-001` | Plugin Failure | Plugin failed to load | Medium |
| `PLUGIN-PLUG-002` | Plugin Failure | Plugin crashed | High |
| `PLUGIN-PLUG-003` | Plugin Failure | Plugin timeout | Medium |
| `PLUGIN-PLUG-004` | Plugin Failure | Plugin quota exceeded | Medium |
| `PLUGIN-PLUG-005` | Plugin Failure | Plugin dependency missing | High |
| `PLUGIN-NF-001` | Not Found | Plugin not found | Low |
| `PLUGIN-UNAV-001` | Unavailable | Plugin runtime unavailable | High |

### 10.5 SDK Module

| Code | Category | Message | Severity |
|------|----------|---------|----------|
| `SDK-PERM-001` | Permission | API call not permitted | Medium |
| `SDK-RATE-001` | Rate Limit | SDK rate limit exceeded | Medium |
| `SDK-VAL-001` | Validation | SDK input validation failed | Low |
| `SDK-TMO-001` | Timeout | SDK call timed out | Medium |
| `SDK-DEP-001` | Deprecation | Deprecated API usage | Low |
| `SDK-STOR-001` | Quota | Storage quota exceeded | Medium |
| `SDK-UNAV-001` | Unavailable | SDK runtime unavailable | High |

### 10.6 System Module

| Code | Category | Message | Severity |
|------|----------|---------|----------|
| `SYS-UNAV-001` | Unavailable | System still initializing | High |
| `SYS-UNAV-002` | Unavailable | System shutting down | High |
| `SYS-INTG-001` | Integrity | Internal consistency error | Critical |
| `SYS-QUOT-001` | Quota | System resource limit reached | High |
| `SYS-RATE-001` | Rate Limit | System-wide rate limit exceeded | High |

---

## 11. Error Recovery Strategies by Context

| Context | Strategy |
|---------|----------|
| CLI Operation | Display error, suggest corrective action, exit with code |
| UI Operation | Display toast/dialog with error, highlight affected field |
| Background Task | Log error, retry per policy, notify admin if critical |
| Plugin Operation | Isolate plugin, log error, auto-disable if repeated |
| IPC Call | Return error to caller, update circuit breaker |
| Event Handler | Log error, move to dead letter queue if persistent |
| Scheduled Task | Log error, skip execution, retry on next schedule |
| API Request | Return RFC 7807 response with appropriate HTTP status |
