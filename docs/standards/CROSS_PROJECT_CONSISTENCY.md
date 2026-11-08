# Cross-Project Consistency

> Rules ensuring consistent behavior, formatting, and conventions across all 20+ modules
> of AuthShield Lab. Every module must conform to these standards to maintain a unified
> developer and user experience.

---

## Table of Contents

1. [Naming Consistency](#naming-consistency)
2. [API Consistency](#api-consistency)
3. [Database Consistency](#database-consistency)
4. [Event Consistency](#event-consistency)
5. [Error Consistency](#error-consistency)
6. [UI Consistency](#ui-consistency)
7. [Documentation Consistency](#documentation-consistency)

---

## Naming Consistency

### Module Naming Rules

All modules across the project must follow the same naming conventions without exception.

| Layer | Convention | Examples |
|---|---|---|
| Python packages | snake_case | `auth/`, `users/`, `audit/`, `sessions/` |
| Python modules | snake_case | `authentication_service.py`, `user_repository.py` |
| Distribution packages | kebab-case | `authshield-auth`, `authshield-users` |
| Frontend components | PascalCase | `LoginForm.tsx`, `DashboardPage.tsx` |
| Frontend hooks | camelCase with `use` prefix | `useAuthentication.ts`, `useSession.ts` |
| Configuration files | snake_case or lowercase | `security.yaml`, `development.toml` |

### Class Naming Rules

Every class must use PascalCase with a role-specific suffix:

```
Service suffix: AuthenticationService, CourseManagementService
Repository suffix: UserRepository, SessionRepository, AuditLogRepository
Controller suffix: AuthController, UserController, CourseController
Schema suffix: LoginRequestSchema, UserCreateSchema
Event suffix: UserRegistered, SessionExpired
Handler suffix: LoginAttemptHandler, PasswordResetHandler
Factory suffix: TokenFactory, CourseFactory
Builder suffix: QueryBuilder, ReportBuilder
```

### Function Naming Rules

All functions use snake_case with semantic prefixes:

| Module | Consistent Function Names |
|---|---|
| All modules | `get_`, `create_`, `update_`, `delete_`, `validate_` |
| Auth module | `authenticate`, `login`, `logout`, `refresh_token` |
| Session module | `create_session`, `validate_session`, `revoke_session` |
| Users module | `get_user_by_id`, `get_user_by_email`, `create_user` |
| Course module | `create_course`, `publish_course`, `get_course_by_slug` |
| Assessment module | `submit_assessment`, `grade_assessment`, `get_score` |
| Simulation module | `start_simulation`, `complete_step`, `evaluate_result` |
| Audit module | `log_event`, `query_logs`, `export_report` |
| Analytics module | `record_metric`, `generate_report`, `compute_score` |

### Variable Naming Rules

No abbreviations anywhere in the codebase:

```
# Auth module - always descriptive
authentication_method          # Not: auth_method
maximum_login_attempts         # Not: max_attempts (acceptable) or mla
failed_attempt_count           # Not: fail_count
session_expiration_timestamp   # Not: session_exp

# Course module
enrolled_learner_count         # Not: enroll_count
course_difficulty_level         # Not: diff_level
assessment_passing_score       # Not: pass_score

# Simulation module
simulation_execution_duration  # Not: sim_duration
vulnerability_severity_level   # Not: vuln_severity
time_to_detect_seconds         # Not: ttd
```

---

## API Consistency

### Response Format

Every API endpoint must return a consistent response envelope:

```
// Success response
{
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}

// Success list response
{
  "data": [ ... ],
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-15T10:30:00Z",
    "pagination": {
      "total": 150,
      "page": 1,
      "per_page": 25,
      "has_next": true,
      "has_previous": false
    }
  }
}

// Error response
{
  "data": null,
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Email format is invalid",
      "field": "email",
      "details": { "provided": "not-an-email" }
    }
  ],
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### Response Envelope Rules

| Rule | Requirement |
|---|---|
| Always use `data` key | Top-level `data` key for all successful responses |
| Always use `meta` key | Contains request_id, timestamp, and pagination |
| Always use `errors` key | Array of error objects for failures |
| No data in error responses | `data` is `null` when errors are present |
| Pagination in meta | Never at the top level; always nested in `meta.pagination` |
| Timestamps in ISO 8601 | Always UTC: `2025-01-15T10:30:00Z` |

### HTTP Methods

| Method | Purpose | Idempotent | Request Body |
|---|---|---|---|
| `GET` | Retrieve resources | Yes | No |
| `POST` | Create resources or trigger actions | No | Yes |
| `PUT` | Replace a resource entirely | Yes | Yes |
| `PATCH` | Partially update a resource | No | Yes |
| `DELETE` | Remove a resource | Yes | No |

### HTTP Status Codes

| Code | Meaning | When to Use |
|---|---|---|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST creating a resource |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Validation errors, malformed input |
| `401` | Unauthorized | Missing or invalid authentication |
| `403` | Forbidden | Authenticated but not authorized |
| `404` | Not Found | Resource does not exist |
| `409` | Conflict | Duplicate resource, state conflict |
| `422` | Unprocessable Entity | Semantically invalid input |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unexpected server failure |
| `502` | Bad Gateway | Upstream service failure |
| `503` | Service Unavailable | Maintenance or overload |

### Endpoint Naming

All endpoints across all modules must follow the same URL structure:

```
/api/v{version}/{resource}                       # Collection
/api/v{version}/{resource}/{id}                  # Single resource
/api/v{version}/{resource}/{id}/{sub-resource}   # Nested resource
/api/v{version}/{resource}/{id}/{action}          # Action on resource
```

Module-specific endpoint examples:

```
Auth module:
  POST   /api/v1/auth/login
  POST   /api/v1/auth/logout
  POST   /api/v1/auth/refresh
  POST   /api/v1/auth/password-reset
  POST   /api/v1/auth/mfa/verify

Users module:
  GET    /api/v1/users
  GET    /api/v1/users/{user_id}
  POST   /api/v1/users
  PATCH  /api/v1/users/{user_id}
  DELETE /api/v1/users/{user_id}

Sessions module:
  GET    /api/v1/sessions
  GET    /api/v1/sessions/{session_id}
  DELETE /api/v1/sessions/{session_id}

Courses module:
  GET    /api/v1/courses
  GET    /api/v1/courses/{course_id}
  POST   /api/v1/courses
  PATCH  /api/v1/courses/{course_id}
  POST   /api/v1/courses/{course_id}/publish
  GET    /api/v1/courses/{course_id}/modules
  POST   /api/v1/courses/{course_id}/enroll

Assessments module:
  GET    /api/v1/courses/{course_id}/assessments
  GET    /api/v1/assessments/{assessment_id}
  POST   /api/v1/assessments/{assessment_id}/submit
  GET    /api/v1/assessments/{assessment_id}/results

Simulations module:
  GET    /api/v1/simulations
  GET    /api/v1/simulations/{simulation_id}
  POST   /api/v1/simulations/{simulation_id}/start
  POST   /api/v1/simulations/{simulation_id}/complete

Analytics module:
  GET    /api/v1/analytics/overview
  GET    /api/v1/analytics/users/{user_id}
  GET    /api/v1/analytics/courses/{course_id}
  GET    /api/v1/reports
  GET    /api/v1/reports/{report_id}

Audit module:
  GET    /api/v1/audit-logs
  GET    /api/v1/audit-logs/{log_id}
  GET    /api/v1/compliance/reports
```

### Pagination

All list endpoints must support consistent pagination:

```
GET /api/v1/courses?page=1&per_page=25&sort=-created_at&search=python
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | integer | 1 | Page number (1-indexed) |
| `per_page` | integer | 25 | Items per page (max 100) |
| `sort` | string | `-created_at` | Sort field; prefix `-` for descending |
| `search` | string | (none) | Full-text search query |
| `filter[field]` | string | (none) | Field-specific filter |

---

## Database Consistency

### Table Conventions

Every table across all modules must follow:

```
Naming:
  - Singular snake_case: user, session, course, assessment, audit_log
  - Never plural: users, sessions, courses
  - Never PascalCase: User, Session, Course

Required columns (every table):
  - id UUID PRIMARY KEY DEFAULT gen_random_uuid()
  - created_at TIMESTAMP NOT NULL DEFAULT NOW()
  - updated_at TIMESTAMP NOT NULL DEFAULT NOW()

Common columns (where applicable):
  - is_active BOOLEAN DEFAULT TRUE
  - is_deleted BOOLEAN DEFAULT FALSE (soft delete)
  - deleted_at TIMESTAMP NULLABLE
  - version INTEGER DEFAULT 1 (optimistic locking)
```

### Column Type Standards

| Data Type | Use For | Example |
|---|---|---|
| `UUID` | Primary keys, foreign keys | `id UUID PRIMARY KEY` |
| `VARCHAR(255)` | Emails, URLs, short text | `email VARCHAR(255) NOT NULL` |
| `VARCHAR(128)` | Names, titles | `display_name VARCHAR(128) NOT NULL` |
| `VARCHAR(32)` | Enum-like values | `difficulty_level VARCHAR(32) NOT NULL` |
| `TEXT` | Long-form content, descriptions | `description TEXT` |
| `BOOLEAN` | Flags | `is_active BOOLEAN DEFAULT TRUE` |
| `TIMESTAMP` | Dates and times | `created_at TIMESTAMP DEFAULT NOW()` |
| `INTEGER` | Counts, scores, limits | `max_attempts INTEGER DEFAULT 3` |
| `DECIMAL(10,2)` | Precise numbers | `score DECIMAL(5,2)` |
| `JSONB` | Flexible structured data | `metadata JSONB DEFAULT '{}'` |

### Default Value Standards

| Column Pattern | Default | Rationale |
|---|---|---|
| `is_active` | `TRUE` | New resources are active by default |
| `is_published` | `FALSE` | Content requires explicit publishing |
| `is_revoked` | `FALSE` | Sessions start as valid |
| `is_deleted` | `FALSE` | Soft delete opt-in |
| `created_at` | `NOW()` | Auto-set on creation |
| `updated_at` | `NOW()` | Auto-set on update via trigger |
| `version` | `1` | Optimistic locking starts at 1 |
| `max_attempts` | `3` | Reasonable default for retries |
| `page_size` | `25` | Default pagination size |

### Nullable Standards

| Column Pattern | Nullable | Rationale |
|---|---|---|
| `id` | NEVER | Primary key is always required |
| `email` | NEVER | Every user must have an email |
| `created_at` | NEVER | Always set on creation |
| `updated_at` | NEVER | Always set on update |
| `deleted_at` | YES | Only set when soft-deleted |
| `completed_at` | YES | Only set when completed |
| `description` | YES | Optional descriptive text |
| `metadata` | NO (default `{}`) | Use empty JSON, not null |

### Migration Conventions

```
Numbering: Sequential 001, 002, 003...
Naming: Verb-noun description
Examples:
  001_create_user_table.py
  002_create_session_table.py
  003_add_email_index_to_user.py
  004_create_course_tables.py
  005_add_mfa_columns_to_user.py

Rules:
  - Each migration is atomic (all or nothing)
  - Migrations must be reversible (up and down)
  - Never modify a migration that has been applied to production
  - Create a new migration for corrections
  - Test migrations against a copy of production data
```

### Index Conventions

```
Naming pattern: idx_{table}_{column(s)}
Examples:
  idx_user_email ON user (email)
  idx_session_user_id ON session (user_id)
  idx_audit_log_created_at ON audit_log (created_at)
  idx_course_difficulty ON course (difficulty_level)

Unique indexes:
  idx_unique_user_email ON user (email)
  idx_unique_session_token ON session (token)

Partial indexes:
  idx_active_session_user ON session (user_id) WHERE is_revoked = FALSE

Rules:
  - Index all foreign keys
  - Index frequently queried columns
  - Index columns used in WHERE, ORDER BY, JOIN
  - Avoid over-indexing (slows writes)
  - Use partial indexes for filtered queries
```

---

## Event Consistency

### Event Naming

All domain events across all modules must use past-tense PascalCase:

```
Identity events:     UserRegistered, SessionExpired, MfaChallengeVerified
Authorization events: RoleCreated, PermissionRevoked, AccessDenied
Education events:    CourseCompleted, AssessmentGraded, CertificateIssued
Simulation events:   SimulationStarted, VulnerabilityDiscovered
Analytics events:    CompetencyAchieved, ReportGenerated
Operations events:   SecurityAlertTriggered, DeploymentCompleted
```

### Event Payload Format

Every event must include these standard fields:

```
{
  "event_id": "evt_abc123",           // UUID, unique per event
  "event_type": "UserRegistered",     // PascalCase past-tense
  "occurred_at": "2025-01-15T10:30:00Z",  // ISO 8601 UTC
  "aggregate_id": "usr_def456",       // ID of the affected aggregate
  "aggregate_type": "UserAccount",    // Type of affected aggregate
  "version": 1,                       // Event schema version
  "data": { ... },                    // Event-specific payload
  "metadata": {                       // Optional contextual data
    "correlation_id": "req_xyz789",
    "actor_id": "usr_abc123",
    "ip_address": "192.168.1.100"
  }
}
```

### Event Schema Versioning

| Version | Change Type | Example |
|---|---|---|
| Patch (1.0.x) | Backward-compatible additions | Adding optional field to data |
| Minor (1.x.0) | New optional fields | Adding new event type |
| Major (x.0.0) | Breaking changes | Renaming required fields |

### Event Handling Rules

| Rule | Requirement |
|---|---|
| Idempotent handlers | Must handle duplicate events gracefully |
| At-least-once delivery | Handlers must not assume exactly-once |
| Fail-safe handling | Failed handlers must not crash the system |
| Dead letter queue | Unprocessable events go to DLQ |
| Ordering within context | Events within a bounded context maintain order |
| No cross-context ordering | Events across contexts may arrive out of order |

---

## Error Consistency

### Error Code Format

All error codes use UPPER_SNAKE_CASE:

```
AUTHENTICATION_FAILED
INVALID_CREDENTIALS
ACCOUNT_LOCKED
MFA_REQUIRED
TOKEN_EXPIRED
VALIDATION_ERROR
EMAIL_FORMAT_ERROR
PASSWORD_COMPLEXITY_ERROR
USER_NOT_FOUND
COURSE_NOT_FOUND
SESSION_NOT_FOUND
DUPLICATE_ENROLLMENT
INSUFFICIENT_PERMISSIONS
RATE_LIMIT_EXCEEDED
DATABASE_CONNECTION_ERROR
EXTERNAL_SERVICE_ERROR
```

### Error Response Format

```
{
  "code": "AUTHENTICATION_FAILED",
  "message": "Invalid email or password",
  "field": null,
  "details": {
    "attempt_number": 3,
    "remaining_attempts": 2
  }
}
```

### Error Rules

| Rule | Requirement |
|---|---|
| Machine-readable code | ALWAYS include an UPPER_SNAKE_CASE error code |
| Human-readable message | ALWAYS include a clear, non-technical message |
| No stack traces | NEVER expose stack traces in production responses |
| No internal details | NEVER expose database queries, file paths, etc. |
| Field reference | Include `field` when error relates to a specific input field |
| Details object | Include additional context when helpful for debugging |
| Consistent status codes | Always pair error codes with appropriate HTTP status codes |

### Status Code to Error Code Mapping

| HTTP Status | Common Error Codes |
|---|---|
| 400 | `VALIDATION_ERROR`, `MALFORMED_REQUEST` |
| 401 | `AUTHENTICATION_FAILED`, `TOKEN_EXPIRED`, `MFA_REQUIRED` |
| 403 | `INSUFFICIENT_PERMISSIONS`, `ACCOUNT_LOCKED` |
| 404 | `USER_NOT_FOUND`, `COURSE_NOT_FOUND`, `SESSION_NOT_FOUND` |
| 409 | `DUPLICATE_ENROLLMENT`, `SESSION_CONFLICT` |
| 422 | `EMAIL_FORMAT_ERROR`, `PASSWORD_COMPLEXITY_ERROR` |
| 429 | `RATE_LIMIT_EXCEEDED` |
| 500 | `DATABASE_CONNECTION_ERROR`, `INTERNAL_SERVER_ERROR` |
| 502 | `EXTERNAL_SERVICE_ERROR` |

---

## UI Consistency

### Component Patterns

Every UI module must follow the same component structure:

```
ComponentName/
  index.ts                    # Re-export
  ComponentName.tsx           # Main component
  ComponentName.test.tsx      # Tests
  ComponentName.stories.tsx   # Storybook stories (optional)
  styles.module.css           # Scoped styles
```

### Layout Standards

| Element | Spacing | Rationale |
|---|---|---|
| Page padding | 24px | Consistent breathing room |
| Card padding | 16px | Comfortable content spacing |
| Section gap | 32px | Clear visual separation |
| Element gap | 8px | Compact element grouping |
| Inline gap | 4px | Tight inline elements |
| Modal width | 480px / 640px | Standard dialog sizes |

### Component Sizing

| Component | Min Width | Max Width | Notes |
|---|---|---|---|
| Button (primary) | 80px | 320px | Text determines width |
| Button (icon) | 40px | 40px | Fixed square |
| Input field | 200px | 100% | Fills container |
| Card | 280px | 480px | Responsive grid |
| Modal | 480px | 640px | Centered overlay |
| Sidebar | 240px | 280px | Fixed width |
| Page content | 320px | 1200px | Max content width |

### Color Usage

| Usage | Color | CSS Variable |
|---|---|---|
| Primary action | Blue (#2563EB) | `--color-primary` |
| Success | Green (#16A34A) | `--color-success` |
| Warning | Amber (#F59E0B) | `--color-warning` |
| Error / Danger | Red (#DC2626) | `--color-error` |
| Information | Blue (#3B82F6) | `--color-info` |
| Background | Gray (#F9FAFB) | `--color-background` |
| Surface | White (#FFFFFF) | `--color-surface` |
| Text primary | Gray (#111827) | `--color-text-primary` |
| Text secondary | Gray (#6B7280) | `--color-text-secondary` |
| Border | Gray (#E5E7EB) | `--color-border` |

### Typography

| Element | Font Size | Weight | Line Height | Use |
|---|---|---|---|---|
| H1 | 30px | 700 | 36px | Page titles |
| H2 | 24px | 600 | 32px | Section headings |
| H3 | 20px | 600 | 28px | Subsection headings |
| Body | 16px | 400 | 24px | Default text |
| Body small | 14px | 400 | 20px | Secondary text |
| Caption | 12px | 400 | 16px | Labels, timestamps |
| Code | 14px | 400 | 20px | Inline code, code blocks |

### Toast Patterns

| Type | Icon | Color | Auto-dismiss |
|---|---|---|---|
| Success | Checkmark | Green | 3 seconds |
| Error | X | Red | Never (manual dismiss) |
| Warning | Triangle | Amber | 5 seconds |
| Info | Info circle | Blue | 5 seconds |

### Form Patterns

| Pattern | Rule |
|---|---|
| Labels | Always visible above inputs (not placeholders) |
| Validation | Show on blur; show errors below input |
| Required fields | Mark with red asterisk |
| Submit button | Disable while submitting; show loading state |
| Error summary | Show at top of form on submit failure |
| Success feedback | Show toast, not inline message |

---

## Documentation Consistency

### File Structure

Every module documentation file must follow:

```
# Module Name

> One-paragraph description of the module.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [Data Model](#data-model)
5. [Configuration](#configuration)
6. [Events](#events)
7. [Error Handling](#error-handling)
8. [Testing](#testing)
9. [Examples](#examples)

---

## Overview

[Module description and purpose]

## Architecture

[How this module fits into the overall system]

## API Reference

[Endpoint documentation]

## Data Model

[Entity and relationship documentation]

## Configuration

[All configuration options]

## Events

[Domain events this module publishes and subscribes to]

## Error Handling

[Error types and handling patterns]

## Testing

[Testing approach and patterns]

## Examples

[Usage examples]
```

### Documentation Formatting Rules

| Rule | Requirement |
|---|---|
| Headings | ATX style (`#`, `##`, `###`) |
| Code blocks | Fenced with language annotation |
| Tables | Pipe-delimited with header separator |
| Links | Relative paths for internal docs |
| Images | Relative paths, PNG/SVG preferred |
| Line length | No hard limit; keep readable |
| File encoding | UTF-8 |
| Line endings | LF (Unix) |

### Code Example Standards

Every documentation file must include at least one code example per major section:

```python
# Example must be complete and runnable
from authshield.users import UserRepository, UserCreateSchema

async def create_new_user(email: str, name: str) -> User:
    """Create a new user account.

    Args:
        email: The user's email address.
        name: The user's display name.

    Returns:
        The newly created User entity.

    Raises:
        ValidationError: If email format is invalid.
        ConflictError: If email is already registered.
    """
    schema = UserCreateSchema(email=email, display_name=name)
    validated = schema.validate()
    return await user_repository.create(validated)
```

### Cross-Reference Standards

| Reference Type | Format | Example |
|---|---|---|
| Internal doc link | `[Text](../path/to/doc.md)` | `[Naming System](./ENTERPRISE_NAMING_SYSTEM.md)` |
| API endpoint | `` `GET /api/v1/users` `` | Inline code |
| Class reference | `` `UserService` `` | Inline code |
| Function reference | `` `get_user_by_id()` `` | Inline code |
| Event reference | `` `UserRegistered` `` | Inline code |
| Config key | `` `auth.session.timeout_minutes` `` | Inline code |

---

## Enforcement

### Automated Checks

| Check | Tool | When |
|---|---|---|
| Naming conventions | Linter (Ruff/ESLint) | Pre-commit, CI |
| API response format | Schema validation tests | CI |
| Database migration format | Migration linter | CI |
| Event schema validation | Contract tests | CI |
| Error code format | Custom linter rules | Pre-commit |
| Documentation structure | Markdown linter | CI |

### Manual Review

| Check | Reviewer | When |
|---|---|---|
| New event types | Tech lead | PR review |
| New API endpoints | Tech lead | PR review |
| New database tables | Tech lead | PR review |
| Naming consistency | Any reviewer | PR review |
| Documentation completeness | Tech lead | PR review |

### Compliance Matrix

| Standard | Auth | Users | Sessions | Courses | Assessments | Simulations | Analytics | Audit |
|---|---|---|---|---|---|---|---|---|
| Response envelope | Required | Required | Required | Required | Required | Required | Required | Required |
| Error codes | Required | Required | Required | Required | Required | Required | Required | Required |
| Pagination | N/A | Required | Required | Required | Required | Required | Required | Required |
| Event publishing | Required | Required | Required | Required | Required | Required | Required | Required |
| Index conventions | Required | Required | Required | Required | Required | Required | Required | Required |
| Documentation | Required | Required | Required | Required | Required | Required | Required | Required |

---

*Last updated: 2025-01-15*
*Owner: AuthShield Lab Engineering*
