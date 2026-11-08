# AuthShield Lab — Data Flow Documentation

> Version: 1.0.0 | Last Updated: 2026-07-19
> Status: Living Document | Owner: Architecture Team

---

## 1. Overview

This document traces the lifecycle of data as it moves through AuthShield Lab. It covers the request lifecycle, event propagation, authentication flow, authorization flow, audit logging, error handling, cache invalidation, and database migrations.

All flows are described at the **module boundary level** — implementation details are omitted in favor of inter-module data movement.

---

## 2. Request Lifecycle

### 2.1 HTTP Request → Response (Full Flow)

```
Client
  │
  │ HTTP Request (POST /api/auth/login)
  │
  ▼
┌──────────────────────┐
│  FastAPI Router      │  (backend/app/api/)
│  - Route matching    │
│  - Request parsing   │
│  - CORS validation   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Middleware Stack     │  (backend/app/)
│  - Rate limiting     │  security module
│  - CSRF validation   │  security module
│  - Session check     │  sessions module
│  - Request logging   │  audit module
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Input Validation    │  packages/validation/
│  - Schema validation │
│  - Sanitization      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Business Logic      │  e.g., auth module
│  - Service layer     │
│  - Domain rules      │
│  - Side effects      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Data Access         │  Module repository
│  - Query / Insert    │
│  - Transaction mgmt  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Response Builder    │  packages/validation/
│  - Serialization     │
│  - Status code       │
│  - Headers           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Post-Processing     │
│  - Audit log (async) │  audit module
│  - Event publish     │  event bus
│  - Cache update      │  optimization module
└──────────┬───────────┘
           │
           ▼
Client
  │
  │ HTTP Response (200 OK, { "session_token": "..." })
```

### 2.2 Request Timing Budget

```
Total: 5000ms
├── Rate limiting:            10ms
├── CSRF validation:           5ms
├── Session check:            50ms
├── Input validation:         20ms
├── Business logic:          300ms
│   ├── Database query:      100ms
│   ├── Password verify:     100ms
│   └── Session create:     100ms
├── Response serialization:   20ms
└── Async post-processing:  no budget (background)
```

---

## 3. Event Propagation Flow

### 3.1 Event Publishing

When a module performs a significant action, it publishes an event to the event bus.

```
Module Action          Event Bus              Subscribers
     │                    │                      │
     │ publish(event) ───►│                      │
     │                    │── dispatch ──────────►│ Audit Logger
     │                    │── dispatch ──────────►│ Analytics
     │                    │── dispatch ──────────►│ Defense (if applicable)
     │                    │                      │
     │◄── return ─────────│                      │
```

### 3.2 Event Propagation Chains

Events can trigger secondary events in other modules:

```
auth.login.success (published by auth)
  │
  ├──► audit.log() (audit module)
  │     └──► audit.event.logged (no further propagation)
  │
  ├──► analytics.track_login() (analytics module)
  │     └──► analytics.metrics.updated (no further propagation)
  │
  ├──► defense.check_login_pattern() (defense module)
  │     └──► defense.alert (if suspicious) (published by defense)
  │           ├──► audit.log(defense.alert)
  │           └──► notification.send(defense.alert) (if configured)
  │
  └──► lms.record_login() (lms module, if learner)
        └──► lms.activity.logged (no further propagation)
```

### 3.3 Event Ordering Guarantees

**Within a single module:** Events from the same module are delivered in publish order.

**Across modules:** Event ordering across modules is **not guaranteed**. Modules must be designed to handle events out of order.

**Correlation ID:** All events in a single user action share the same `correlation_id`, enabling post-hoc ordering.

---

## 4. Authentication Flow

### 4.1 Login Flow

```
Client ──POST /api/auth/login──► Router ──► LoginService
  │                                      │
  │                                      ├── RateLimitCheck (security module)
  │                                      │   └── block if exceeded
  │                                      │
  │                                      ├── GetUser(email) ──► users module
  │                                      │   └── return User | null
  │                                      │
  │                                      ├── VerifyPassword(password, hash)
  │                                      │   └── PasswordVerificationService
  │                                      │
  │                                      ├── MFACheck (if enabled)
  │                                      │   └── verify MFA token
  │                                      │
  │                                      ├── CreateSession(user_id) ──► sessions module
  │                                      │   └── return SessionToken
  │                                      │
  │                                      ├── PublishEvent(auth.login.success)
  │                                      │
  │                                      └── Return SessionToken to Client
  │
  │  Async side effects (via event bus):
  │  ├── audit.log(auth.login.success)
  │  ├── analytics.track_login(user_id)
  │  └── defense.check_login_pattern(user_id, ip)
```

### 4.2 Registration Flow

```
Client ──POST /api/auth/register──► Router ──► RegistrationService
  │                                        │
  │                                        ├── ValidateInput (packages/validation)
  │                                        │
  │                                        ├── CheckPasswordPolicy
  │                                        │   └── PasswordPolicyService
  │                                        │
  │                                        ├── CreateUser ──► users module
  │                                        │   └── return User
  │                                        │
  │                                        ├── CreateCredentials ──► auth module
  │                                        │   └── store hashed password
  │                                        │
  │                                        ├── PublishEvent(auth.register)
  │                                        │
  │                                        └── Return UserRecord to Client
```

### 4.3 Session Validation Flow

```
Every Request:
  │
  ├── Extract token from header/cookie
  │
  ├── ValidateToken ──► sessions module
  │   ├── Token exists? ── No ──► 401 Unauthorized
  │   ├── Token expired? ── Yes ──► 401 Unauthorized
  │   └── Token valid? ── Yes ──► continue
  │
  ├── LoadUser(user_id) ──► users module
  │   ├── User exists? ── No ──► 401 Unauthorized
  │   └── User active? ── No ──► 403 Forbidden
  │
  └── Attach user context to request ──► continue to handler
```

---

## 5. Authorization Flow

### 5.1 Permission Check Flow

```
Handler ──check_permission(user_id, resource, action)──► security module
  │
  ├── LoadUserRoles(user_id) ──► users module
  │   └── return [role_admin, role_editor]
  │
  ├── LoadRolePermissions(roles) ──► users module
  │   └── return [perm.read, perm.write, perm.delete]
  │
  ├── EvaluatePolicies(resource, action, permissions) ──► policies module
  │   ├── Match rules ──► rules module
  │   │   ├── IP whitelist check
  │   │   ├── Time-of-day check
  │   │   └── Rate limit check
  │   └── Return PolicyDecision (allow | deny)
  │
  ├── PolicyDecision = allow? ── Yes ──► continue
  └── PolicyDecision = deny? ── Yes ──► 403 Forbidden + audit.log
```

### 5.2 RBAC Evaluation Tree

```
Request(user_id, resource, action)
  │
  ├── User → Roles
  │   ├── role: admin ──► [perm.all]
  │   ├── role: editor ──► [perm.read, perm.write]
  │   └── role: viewer ──► [perm.read]
  │
  ├── Roles → Permissions (union of all role permissions)
  │   └── final_permissions = union(admin.all, editor.rw, viewer.r)
  │
  ├── Permissions + Policies → Decision
  │   ├── Check: perm.all includes action? ── Yes ──► allow
  │   ├── Check: specific perm includes action? ── Yes ──► check policies
  │   │   ├── Policy allows? ──► allow
  │   │   └── Policy denies? ──► deny
  │   └── No matching perm? ──► deny
  │
  └── Return Decision
```

---

## 6. Audit Logging Flow

### 6.1 Audit Event Capture

```
Module Action
  │
  ├── Sync audit (critical actions):
  │   auth.login.failed ──► audit.log() ──► confirm ──► continue
  │
  └── Async audit (non-critical actions):
      auth.login.success ──► event bus ──► audit.log() ──► (background)
```

### 6.2 Audit Event Pipeline

```
Event Published
  │
  ▼
Event Bus ──dispatch──► AuditMiddleware
  │
  ├── Enrich event
  │   ├── Add timestamp
  │   ├── Resolve user identity
  │   ├── Add IP address (if HTTP context)
  │   └── Add correlation ID
  │
  ├── Serialize event
  │   └── Convert to AuditEntry format
  │
  ├── Write to audit store
  │   ├── SQLite append-only table
  │   └── Confirm write
  │
  └── Publish audit.event.logged (for analytics)
```

### 6.3 Audit Event Schema

```json
{
  "audit_id": "uuid",
  "event_type": "auth.login.success",
  "timestamp": "2026-07-19T10:30:00Z",
  "user_id": "user_123",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "resource": "/api/auth/login",
  "action": "authenticate",
  "result": "success",
  "metadata": {
    "method": "password",
    "mfa_used": true,
    "session_id": "sess_abc"
  },
  "correlation_id": "corr_xyz",
  "retention_days": 365
}
```

---

## 7. Error Handling Flow

### 7.1 Error Propagation Chain

```
Exception Thrown in Module
  │
  ├── Module catches internally?
  │   ├── Yes ──► Handle and return error response
  │   └── No ──► Propagate to caller
  │
  ├── Caller catches?
  │   ├── Yes ──► Wrap in domain error and return
  │   └── No ──► Propagate to middleware
  │
  ├── Global exception handler (FastAPI)
  │   ├── Log error (packages/logging)
  │   ├── Publish error event (event bus)
  │   ├── Format error response
  │   └── Return HTTP error response
  │
  └── Audit log (async)
      └── Record error for security monitoring
```

### 7.2 Error Response Flow

```
Module Error
  │
  ├── Classify error
  │   ├── ValidationError ──► 400 Bad Request
  │   ├── AuthenticationError ──► 401 Unauthorized
  │   ├── AuthorizationError ──► 403 Forbidden
  │   ├── NotFoundError ──► 404 Not Found
  │   ├── ConflictError ──► 409 Conflict
  │   ├── RateLimitError ──► 429 Too Many Requests
  │   └── InternalError ──► 500 Internal Server Error
  │
  ├── Format error body
  │   └── { "error": { "code": "...", "message": "...", "module": "..." } }
  │
  ├── Log error
  │   ├── Level: error (5xx), warn (4xx), info (validation)
  │   └── Include correlation_id for tracing
  │
  └── Return response
```

### 7.3 Circuit Breaker Error Flow

```
Module Call Fails
  │
  ├── Record failure in circuit breaker
  │
  ├── Failure count >= threshold?
  │   ├── No ──► Continue (return error to caller)
  │   └── Yes ──► Open circuit
  │       ├── Publish event: circuit_breaker.opened
  │       ├── Return CircuitOpenError to caller
  │       └── Start recovery timer
  │
  ├── Recovery timer expires?
  │   ├── Yes ──► Half-open state
  │   │   ├── Send probe request
  │   │   ├── Probe succeeds? ──► Close circuit
  │   │   └── Probe fails? ──► Re-open circuit
  │   └── No ──► Stay open
```

---

## 8. Cache Invalidation Flow

### 8.1 Cache Layers

```
┌──────────────────────────────────────────────┐
│                  Request                      │
│                    │                          │
│                    ▼                          │
│  ┌────────────────────────────┐              │
│  │  L1: In-Memory Cache       │  (per-process)│
│  │  TTL: 60s                   │              │
│  └────────────┬───────────────┘              │
│               │ miss                          │
│               ▼                               │
│  ┌────────────────────────────┐              │
│  │  L2: Shared Cache          │  (cross-proc) │
│  │  TTL: 300s                  │              │
│  └────────────┬───────────────┘              │
│               │ miss                          │
│               ▼                               │
│  ┌────────────────────────────┐              │
│  │  Database                  │              │
│  └────────────────────────────┘              │
└──────────────────────────────────────────────┘
```

### 8.2 Cache Invalidation Events

```
Data Mutation
  │
  ├── users.update_user(user_id)
  │   ├── Invalidate L1: user:{user_id}
  │   ├── Invalidate L2: user:{user_id}
  │   ├── Invalidate L2: user_list:*
  │   └── Publish event: users.updated
  │
  ├── content.publish(content_id)
  │   ├── Invalidate L1: content:{content_id}
  │   ├── Invalidate L2: content:{content_id}
  │   ├── Invalidate L2: content_list:*
  │   └── Publish event: content.published
  │
  ├── policies.update_policy(policy_id)
  │   ├── Invalidate L1: policy:{policy_id}
  │   ├── Invalidate L2: policy:{policy_id}
  │   ├── Invalidate L2: policy_list:*
  │   ├── Invalidate L1: policy_evaluation:*
  │   └── Publish event: policies.updated
  │
  └── defense.block(source)
      ├── Invalidate L1: defense_status:{source}
      ├── Invalidate L2: defense_status:{source}
      └── Publish event: defense.blocked
```

### 8.3 Cache Invalidation Strategies

| Strategy | When | Implementation |
|---|---|---|
| **Write-through** | Data is written | Update cache on write |
| **Write-behind** | Data is written | Update cache async (eventual consistency) |
| **Cache-aside** | Data is read | Load from DB on miss, store in cache |
| **Invalidation on event** | Cross-module mutation | Subscribe to `*.updated` events |

### 8.4 Cache Consistency Model

Cache consistency is **eventually consistent**. After a mutation:
1. The primary module updates its data store.
2. The module invalidates its own cache entries.
3. An event is published.
4. Other modules invalidate their cached copies of the affected data.

**Acceptable staleness:** 5 seconds for most data, 0 seconds for security-critical data (sessions, rate limits).

---

## 9. Database Migration Flow

### 9.1 Migration Lifecycle

```
Developer writes migration
  │
  ├── Migration file created
  │   └── backend/app/<module>/migrations/NNN_description.py
  │
  ├── Migration validated (CI)
  │   ├── Syntax check
  │   ├── Schema validation
  │   └── Rollback test
  │
  ├── Migration applied (deploy)
  │   ├── Check current version
  │   ├── Apply pending migrations in order
  │   ├── Verify schema matches expected
  │   └── Update version tracking table
  │
  └── Migration confirmed
      └── Log: migration.applied event
```

### 9.2 Module Migration Isolation

Each module owns its own migrations:

```
backend/app/
├── auth/migrations/
│   ├── 001_create_credentials_table.py
│   ├── 002_add_mfa_columns.py
│   └── 003_add_password_history.py
├── users/migrations/
│   ├── 001_create_users_table.py
│   └── 002_add_roles.py
├── sessions/migrations/
│   ├── 001_create_sessions_table.py
│   └── 002_add_token_rotation.py
└── audit/migrations/
    ├── 001_create_audit_logs_table.py
    └── 002_add_retention_index.py
```

**Rules:**
1. Migrations are applied in module order: `config` → `users` → `auth` → `sessions` → `audit` → `policies` → `rules` → ... (respecting dependency order).
2. A module's migration must not reference another module's tables directly.
3. Cross-module data changes use events, not direct table manipulation.
4. Rollback scripts are mandatory for every migration.

### 9.3 Migration Version Tracking

```python
# migration_version table
{
    "module": "auth",
    "version": "003",
    "description": "add_password_history",
    "applied_at": "2026-07-19T10:00:00Z",
    "checksum": "sha256:abc123..."
}
```

---

## 10. Data Flow Diagrams

### 10.1 System Context Diagram

```
┌─────────────────────────────────────────────┐
│                  Users                       │
│  (Learners, Instructors, Admins, Developers)│
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│            AuthShield Lab                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │   Auth   │ │   LMS    │ │Simulation│   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│       │            │            │           │
│  ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐   │
│  │  Users   │ │ Content  │ │ Defense  │   │
│  └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────┘
```

### 10.2 Data Ownership Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Ownership Map                            │
│                                                                 │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │  users   │───────►│ users, roles, permissions             │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │  auth    │───────►│ auth_credentials, mfa_secrets         │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │ sessions │───────►│ sessions, session_tokens              │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │  audit   │───────►│ audit_logs, audit_events              │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │ policies │───────►│ policies, policy_rules                │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │  rules   │───────►│ rules, rule_conditions                │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │ defense  │───────►│ defense_actions, blocked_sources      │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │ content  │───────►│ content, content_versions, metadata   │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │   lms    │───────►│ learning_paths, enrollments, progress │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │simulation│───────►│ scenarios, sim_sessions, sim_results   │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │developer │───────►│ api_keys, extensions, workflows       │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │quality   │───────►│ quality_reports, check_results        │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │production│───────►│ feature_flags, releases, health_checks│   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │ecosystem │───────►│ plugins, submissions, reviews         │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │certifica.│───────►│ certifications, badges, exams         │   │
│  └──────────┘        └─────────────────────────────────────┘   │
│  ┌──────────┐  owns  ┌─────────────────────────────────────┐   │
│  │ reports  │───────►│ reports, report_schedules              │   │
│  └──────────┘        └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Cross-Module Data Access Patterns

### 1.1 Direct API Access (Synchronous)

```
auth ──GET /users/{id}──► users
lms ──GET /content/{id}──► content
simulation ──POST /defense/analyze──► defense
```

### 1.2 Event-Based Access (Asynchronous)

```
auth ──publish(auth.login.success)──► event bus ──► audit
defense ──publish(defense.blocked)──► event bus ──► audit, notification
lms ──publish(lms.completed)──► event bus ──► analytics, certification
```

### 1.3 Shared Data Access (Forbidden Patterns)

The following patterns are **forbidden**:

| Pattern | Reason | Alternative |
|---|---|---|
| Module A queries Module B's tables directly | Violates data ownership | Use Module B's API |
| Module A writes to Module B's tables | Violates data ownership | Publish an event |
| Module A reads Module B's cache | Violates cache ownership | Use Module B's API |
| Module A creates Module B's entities | Violates domain boundaries | Use Module B's API |

---

## 12. References

- [MODULE_BOUNDARIES.md](./MODULE_BOUNDARIES.md) — Module boundary definitions
- [SERVICE_COMMUNICATION.md](./SERVICE_COMMUNICATION.md) — Communication patterns
- [CROSS_CUTTING_CONCERNS.md](./CROSS_CUTTING_CONCERNS.md) — Cross-cutting implementations
- [WORKSPACE_ARCHITECTURE.md](./WORKSPACE_ARCHITECTURE.md) — Workspace layout
- [DEPENDENCY_GRAPH.json](./DEPENDENCY_GRAPH.json) — Module dependencies
