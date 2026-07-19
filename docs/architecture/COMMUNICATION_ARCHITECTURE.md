# Communication Architecture — AuthShield Lab

> Version: 1.0  
> Last Updated: 2026-07-19  
> Status: Current

---

## 1. Communication Overview

AuthShield Lab employs **seven distinct communication patterns**, each suited to specific interaction requirements. All communication occurs within localhost — no network sockets or external connections.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      COMMUNICATION PATTERNS                         │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │  Direct      │  │  Domain      │  │  Application               │ │
│  │  Calls       │  │  Events      │  │  Events                    │ │
│  │  (sync)      │  │  (async)     │  │  (user-facing)             │ │
│  └─────────────┘  └──────────────┘  └────────────────────────────┘ │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │  Internal   │  │  Pub/Sub     │  │  Command/Query              │ │
│  │  Messaging  │  │  (Event Bus) │  │  Dispatch (CQRS-lite)       │ │
│  └─────────────┘  └──────────────┘  └────────────────────────────┘ │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │  Plugin     │  │  Background  │  │  Task                      │ │
│  │  Messaging  │  │  Workers     │  │  Scheduling                 │ │
│  └─────────────┘  └──────────────┘  └────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Communication Pattern Definitions

### 2.1 Direct Calls (Synchronous, Intra-Module)

| Attribute | Value |
|---|---|
| **Pattern** | Synchronous method invocation |
| **Scope** | Within a single module |
| **Latency** | ~0ms (same process) |
| **Error Model** | Exceptions |

**Description:**
Direct calls are used when one component within a module needs to invoke another component in the same module. These are standard Python method calls with no serialization overhead.

**Usage Rules:**
- Only within module boundaries (never cross-module)
- Must not perform I/O (network, disk) — delegate to infrastructure
- Must complete within 10ms (fail-fast if slower)
- Return `Result<T, E>` instead of raising exceptions where possible
- Log entry and exit at DEBUG level

**Example:**
```python
class AuthenticationService:
    def authenticate(self, credentials: LoginCredentials) -> Result[AuthToken, AuthError]:
        # Direct call within auth module
        user = self.user_repository.find_by_email(credentials.email)
        if user is None:
            return Result.err(InvalidCredentialsError())
        
        # Direct call to password verifier
        verified = self.password_service.verify(
            credentials.password, 
            user.hashed_password
        )
        if not verified:
            return Result.err(InvalidCredentialsError())
        
        # Direct call to token generator
        token = self.token_service.generate(user.id)
        return Result.ok(token)
```

---

### 2.2 Domain Events (Asynchronous, Cross-Module)

| Attribute | Value |
|---|---|
| **Pattern** | Publish/subscribe via event bus |
| **Scope** | Cross-module communication |
| **Latency** | ~1ms (in-process event bus) |
| **Error Model** | Event handler failure isolation |

**Description:**
Domain events represent significant state changes in the business domain. They are published after successful state transitions and consumed by interested modules asynchronously.

**Event Lifecycle:**
```
1. Domain entity produces event (e.g., UserLoggedIn)
2. Event added to aggregate's event collection
3. Unit of Work publishes events after commit
4. EventBus routes to all registered handlers
5. Handlers execute independently (failure isolation)
6. Events persisted to audit log
```

**Event Contract:**
```python
@dataclass(frozen=True)
class DomainEvent:
    event_id: EntityID          # Unique ULID
    event_type: str             # e.g., "UserLoggedIn"
    aggregate_id: EntityID      # Source aggregate
    aggregate_type: str         # e.g., "User"
    timestamp: Timestamp        # When it occurred
    version: int                # Event version for schema evolution
    payload: dict[str, Any]     # Event-specific data
    metadata: dict[str, Any]    # Request ID, correlation ID, etc.
```

**Handler Registration:**
```python
event_bus.subscribe("UserLoggedIn", auth_handler.on_user_logged_in)
event_bus.subscribe("UserLoggedIn", session_handler.on_user_logged_in)
event_bus.subscribe("UserLoggedIn", audit_handler.on_user_logged_in)
event_bus.subscribe("UserLoggedIn", analytics_handler.on_user_logged_in)
```

**Failure Isolation:**
- Each handler is executed in a try/except block
- Handler failure does not prevent other handlers from executing
- Failed handlers are logged and retried per retry policy
- Dead letter queue for persistent failures

**Guarantees:**
- **At-least-once delivery** (handlers must be idempotent)
- **Ordered within aggregate** (events from same aggregate are ordered)
- **Not ordered across aggregates** (concurrent events may interleave)
- **Eventually consistent** (consumers see events within 100ms typically)

---

### 2.3 Application Events (User-Facing)

| Attribute | Value |
|---|---|
| **Pattern** | Structured response via IPC |
| **Scope** | Backend → Frontend (renderer) |
| **Latency** | ~5ms (IPC serialization) |
| **Error Model** | HTTP-style error responses |

**Description:**
Application events are user-facing notifications sent from the backend to the renderer via Electron IPC. They trigger UI updates like toast notifications, navigation changes, and data refreshes.

**Event Types:**
| Type | Description | UI Action |
|---|---|---|
| `notification` | Informational message | Toast notification |
| `alert` | Warning requiring attention | Alert banner |
| `error` | Error requiring user action | Error modal |
| `redirect` | Navigation instruction | Route change |
| `refresh` | Data update available | Refetch data |
| `progress` | Operation progress | Progress bar |
| `confirmation` | Action confirmation | Success toast |

**IPC Message Contract:**
```typescript
interface ApplicationEvent {
  type: 'notification' | 'alert' | 'error' | 'redirect' | 'refresh' | 'progress' | 'confirmation';
  module: string;          // Source module
  action: string;          // Event action
  data: Record<string, unknown>;
  timestamp: string;       // ISO 8601
  requestId?: string;      // Correlation ID
  priority: 'low' | 'normal' | 'high';
}
```

**IPC Flow:**
```
Backend (FastAPI) → IPC Bridge → Preload Script → Renderer (React)
                                                        │
                                                        ▼
                                                  Zustand Store Update
                                                        │
                                                        ▼
                                                  React Component Re-render
```

---

### 2.4 Internal Messaging (Infrastructure)

| Attribute | Value |
|---|---|
| **Pattern** | In-process message passing |
| **Scope** | Infrastructure layer internal communication |
| **Latency** | ~0ms (same process) |
| **Error Model** | Exceptions with fallback |

**Description:**
Internal messaging handles infrastructure-level communication between non-domain components: configuration changes, logging dispatch, cache invalidation, and background task coordination.

**Message Types:**
| Message | Producer | Consumer | Purpose |
|---|---|---|---|
| `ConfigChanged` | ConfigService | All services | Configuration reload |
| `CacheInvalidated` | Any service | CacheService | Cache eviction |
| `LogFlush` | LoggingService | File sinks | Force log write |
| `TaskScheduled` | SchedulerService | TaskRunner | Execute background task |
| `ShutdownSignal` | Main process | All services | Graceful shutdown |
| `HealthCheck` | SchedulerService | All services | Liveness probe |

---

### 2.5 Publish/Subscribe (Event Bus)

| Attribute | Value |
|---|---|
| **Pattern** | Async pub/sub with topic routing |
| **Scope** | Application-wide |
| **Latency** | ~1ms (in-process) |
| **Error Model** | Handler isolation, retry, dead letter |

**Description:**
The event bus is the central nervous system of AuthShield Lab. It routes domain events, application events, and infrastructure messages between all components.

**Event Bus Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│                      EVENT BUS                           │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Topic   │  │  Topic   │  │  Topic   │  ...          │
│  │ Router   │  │ Router   │  │ Router   │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │              │              │                    │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐              │
│  │ Handler  │  │ Handler  │  │ Handler  │              │
│  │ Queue    │  │ Queue    │  │ Queue    │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

**Topic Hierarchy:**
```
auth.*
  auth.user.logged_in
  auth.user.logged_out
  auth.authentication.failed
  auth.mfa.created
  auth.password.changed

users.*
  users.user.created
  users.user.updated
  users.user.deactivated
  users.role.assigned

sessions.*
  sessions.session.created
  sessions.session.terminated
  sessions.session.expired

audit.*
  audit.entry.created
  audit.security.detected

policies.*
  policies.policy.created
  policies.policy.violation

plugins.*
  plugins.plugin.installed
  plugins.plugin.crashed
```

**Subscription API:**
```python
# Wildcard subscription
event_bus.subscribe("auth.*", handler)

# Specific topic
event_bus.subscribe("auth.user.logged_in", handler)

# With filter
event_bus.subscribe(
    "auth.*",
    handler,
    filter=lambda event: event.payload.get("method") == "password"
)
```

---

### 2.6 Command Dispatch (CQRS-lite)

| Attribute | Value |
|---|---|
| **Pattern** | Command → Handler → Result |
| **Scope** | Application layer |
| **Latency** | ~1ms dispatch + handler execution |
| **Error Model** | Result monad |

**Description:**
Commands represent user intentions to change system state. Each command has exactly one handler that validates, executes, and returns a result.

**Command Contract:**
```python
@dataclass(frozen=True)
class Command:
    command_id: EntityID
    command_type: str
    timestamp: Timestamp
    user_id: EntityID
    payload: dict[str, Any]
    metadata: dict[str, Any]

class CommandHandler(ABC):
    @abstractmethod
    def handle(self, command: Command) -> Result[CommandResult, CommandError]:
        ...
```

**Dispatch Flow:**
```
User Action → IPC → CommandFactory → CommandDispatcher → CommandHandler
                                                              │
                                                              ▼
                                                        Domain Service
                                                              │
                                                              ▼
                                                        Repository (write)
                                                              │
                                                              ▼
                                                        Result<Success, Error>
                                                              │
                                                              ▼
                                                        IPC Response → UI
```

**Command Types:**
| Command | Handler | Description |
|---|---|---|
| `LoginCommand` | `LoginHandler` | Authenticate user |
| `CreateUserCommand` | `CreateUserHandler` | Register new user |
| `CreateCourseCommand` | `CreateCourseHandler` | Create educational course |
| `StartSimulationCommand` | `StartSimulationHandler` | Launch attack simulation |
| `GenerateReportCommand` | `GenerateReportHandler` | Create analytics report |
| `InstallPluginCommand` | `InstallPluginHandler` | Add new plugin |

---

### 2.7 Query Dispatch

| Attribute | Value |
|---|---|
| **Pattern** | Query → Handler → Response (read-only) |
| **Scope** | Application layer |
| **Latency** | ~1ms dispatch + handler execution |
| **Error Model** | Result monad |

**Description:**
Queries represent requests for data without state mutation. Queries are optimized for read performance and may use caching.

**Query Contract:**
```python
@dataclass(frozen=True)
class Query:
    query_id: EntityID
    query_type: str
    timestamp: Timestamp
    filters: dict[str, Any]
    pagination: PaginationParams
    sort: SortParams | None

class QueryHandler(ABC):
    @abstractmethod
    def handle(self, query: Query) -> Result[QueryResult, QueryError]:
        ...
```

**Query Types:**
| Query | Handler | Cacheable | Description |
|---|---|---|---|
| `GetUserQuery` | `GetUserHandler` | Yes (5min) | Fetch user by ID |
| `ListUsersQuery` | `ListUsersHandler` | Yes (1min) | Paginated user list |
| `GetCourseQuery` | `GetCourseHandler` | Yes (10min) | Course details |
| `GetAuditLogsQuery` | `GetAuditLogsHandler` | No | Real-time audit data |
| `GetMetricsQuery` | `GetMetricsHandler` | Yes (30s) | Analytics data |

---

### 2.8 Plugin Messaging

| Attribute | Value |
|---|---|
| **Pattern** | Sandboxed message passing via SDK |
| **Scope** | Plugin ↔ Core system |
| **Latency** | ~2ms (serialization + sandbox) |
| **Error Model** | Timeout + isolation |

**Description:**
Plugins communicate with the core system through a restricted messaging interface provided by the SDK. Plugins cannot directly call core methods — all communication is via structured messages.

**Plugin Message Flow:**
```
Plugin Code → SDK Interface → Message Validation → Sandbox Boundary
                                                          │
                                                          ▼
                                                   Core Message Handler
                                                          │
                                                          ▼
                                                   Response (or error)
                                                          │
                                                          ▼
                                                   Sandbox Boundary
                                                          │
                                                          ▼
                                                   Plugin Receives Response
```

**Message Types:**
| Direction | Message | Description |
|---|---|---|
| Plugin → Core | `EventPublish` | Plugin publishes event |
| Plugin → Core | `DataQuery` | Plugin requests data |
| Plugin → Core | `ConfigRead` | Plugin reads configuration |
| Plugin → Core | `LogEntry` | Plugin writes to log |
| Core → Plugin | `EventNotification` | Event delivered to plugin |
| Core → Plugin | `ConfigChanged` | Configuration updated |
| Core → Plugin | `ShutdownRequest` | Plugin unload requested |

**Sandbox Restrictions:**
- Max message size: 1MB
- Max messages per second: 100
- Max concurrent messages: 10
- Message timeout: 100ms
- No recursive message sending (max depth: 3)

---

### 2.9 Background Workers

| Attribute | Value |
|---|---|
| **Pattern** | Asyncio task execution |
| **Scope** | Infrastructure layer |
| **Latency** | Variable (task-dependent) |
| **Error Model** | Task isolation, retry, dead letter |

**Description:**
Background workers execute long-running or deferred tasks without blocking the main request/response cycle. They use Python's asyncio for cooperative multitasking.

**Worker Types:**
| Worker | Purpose | Schedule | Timeout |
|---|---|---|---|
| `BackupWorker` | Automated backups | Daily at 02:00 | 30 min |
| `LogRotationWorker` | Log file rotation | Daily at 00:00 | 5 min |
| `AnalyticsWorker` | Metric aggregation | Every 5 min | 10 min |
| `HealthCheckWorker` | System health probe | Every 60s | 10s |
| `CacheEvictionWorker` | Expired cache cleanup | Every 1 min | 1 min |
| `PluginHealthWorker` | Plugin health monitoring | Every 5 min | 2 min |

**Worker Lifecycle:**
```
1. SchedulerService registers worker with interval
2. SchedulerService creates asyncio.Task for worker
3. Worker executes at scheduled interval
4. Worker reports result to SchedulerService
5. On failure: retry per policy, then dead letter
6. On shutdown: graceful cancellation with timeout
```

---

### 2.10 Task Scheduling

| Attribute | Value |
|---|---|
| **Pattern** | Cron-like scheduling with asyncio |
| **Scope** | Infrastructure layer |
| **Latency** | Timer-based precision |
| **Error Model** | Isolated task execution |

**Description:**
The scheduler manages periodic and one-shot tasks. It supports cron expressions for complex schedules and simple intervals for recurring tasks.

**Schedule Types:**
```python
# Interval-based
scheduler.every(5).minutes.do(analytics_worker.aggregate)

# Cron-based
scheduler.cron("0 2 * * *").do(backup_worker.run)

# One-shot
scheduler.at(datetime(2026, 7, 20, 10, 0)).do(reports_worker.generate)

# Event-triggered
scheduler.on("UserLoggedIn").do(defense_worker.check_rate_limit)
```

---

## 3. Message Contracts

### 3.1 Standard Message Header

Every message in the system carries a standard header:

```python
@dataclass(frozen=True)
class MessageHeader:
    message_id: str           # ULID
    message_type: str         # "command" | "query" | "event" | "notification"
    timestamp: str            # ISO 8601 UTC
    source: str               # Module name
    correlation_id: str       # For request tracing
    causation_id: str | None  # ID of message that caused this one
    version: int              # Schema version
```

### 3.2 Message Validation

All messages are validated against their schema before dispatch:
- Required fields must be present
- Types must match schema definition
- Payload size must be within limits
- Timestamp must be within acceptable clock skew (5 minutes)

---

## 4. Retry Strategy

### 4.1 Retry Policies

| Policy | Max Retries | Delay | Backoff | Use Case |
|---|---|---|---|---|
| `Immediate` | 3 | 0ms | None | Transient errors |
| `Linear` | 5 | 100ms | +100ms | Database operations |
| `Exponential` | 4 | 200ms | ×2 | External integrations |
| `Fixed` | 3 | 1000ms | None | Plugin operations |
| `NoRetry` | 0 | — | — | Idempotent operations |

### 4.2 Retry Rules

- Domain event handlers: `Exponential` (max 4 retries)
- Database writes: `Linear` (max 5 retries)
- IPC messages: `Immediate` (max 3 retries)
- Plugin messages: `Fixed` (max 3 retries)
- Background tasks: `Exponential` (max 3 retries)
- Never retry: Commands with side effects (unless idempotent)

---

## 5. Failure Handling

### 5.1 Failure Categories

| Category | Examples | Strategy |
|---|---|---|
| **Transient** | Database lock, timeout | Retry with backoff |
| **Permanent** | Validation error, not found | Return error to caller |
| **Systemic** | Disk full, memory exhausted | Log + alert + degrade |
| **Corruption** | Invalid data, schema mismatch | Log + quarantine + alert |

### 5.2 Failure Isolation Rules

1. **Handler Failure Isolation**: One event handler's failure must not prevent other handlers from executing.
2. **Module Failure Isolation**: One module's failure must not crash other modules.
3. **Plugin Failure Isolation**: A plugin crash must not affect the host application.
4. **Worker Failure Isolation**: A background task failure must not affect foreground operations.

### 5.3 Dead Letter Queue

Events that fail all retries are moved to a dead letter queue (DLQ):
- DLQ stored in-memory with max 1000 entries
- DLQ entries logged at ERROR level
- DLQ entries include full event payload and error context
- DLQ can be inspected via developer tools
- DLQ entries can be manually replayed

---

## 6. Timeout Management

### 6.1 Timeout Budgets

| Operation | Timeout | Rationale |
|---|---|---|
| FastAPI request handler | 30s | User patience threshold |
| Database query | 10s | Query complexity limit |
| Event handler execution | 5s | Handler complexity limit |
| IPC message round-trip | 2s | UI responsiveness |
| Plugin message handler | 100ms | Plugin sandbox limit |
| Background task | 30min | Task complexity limit |
| Backup operation | 30min | Data size consideration |
| Health check | 10s | Liveness probe limit |

### 6.2 Timeout Handling

When a timeout occurs:
1. Operation is cancelled (asyncio.CancelledError)
2. Error logged with full context
3. Caller receives `TimeoutError` result
4. If critical: system enters degraded mode
5. If plugin: plugin is marked unhealthy

---

## 7. Error Propagation Rules

### 7.1 Error Propagation Chain

```
Domain Layer (InvariantViolation)
    │
    ▼
Application Layer (wraps in Result<T, E>)
    │
    ▼
Infrastructure Layer (logs + classifies)
    │
    ▼
Integration Layer (serializes for IPC)
    │
    ▼
Presentation Layer (renders to user)
```

### 7.2 Error Transformation Rules

| Layer | Error Type | Transformation |
|---|---|---|
| Domain | `InvariantViolation` | Preserved as-is |
| Application | Wraps domain errors | `Result.err(domain_error)` |
| Infrastructure | Adds context | Logs + wraps with infrastructure context |
| Integration | Serializes | Converts to JSON for IPC |
| Presentation | Renders | Maps to user-friendly message |

### 7.3 Error Log Enrichment

Every error logged includes:
- Timestamp (ISO 8601)
- Error type and message
- Stack trace (at DEBUG level)
- Correlation ID (for request tracing)
- User ID (if authenticated)
- Module name
- Operation being performed
- Input parameters (sanitized)

### 7.4 User-Facing Error Messages

| Error Category | User Message Style | Example |
|---|---|---|
| Validation | "Please fix: {field} {issue}" | "Please fix: Email is not valid" |
| Not Found | "{Resource} not found" | "Course not found" |
| Permission | "You don't have permission to {action}" | "You don't have permission to delete users" |
| Conflict | "{Resource} already exists" | "User with this email already exists" |
| System | "Something went wrong. Please try again." | Generic fallback |
| Timeout | "Operation timed out. Please try again." | Timeout fallback |

---

## 8. Communication Performance

### 8.1 Latency Budgets

| Pattern | Target P50 | Target P99 | Max Acceptable |
|---|---|---|---|
| Direct Call | < 1ms | < 5ms | 10ms |
| Domain Event | < 1ms | < 5ms | 10ms |
| Application Event (IPC) | < 5ms | < 20ms | 50ms |
| Command Dispatch | < 2ms | < 10ms | 20ms |
| Query Dispatch | < 2ms | < 10ms | 20ms |
| Plugin Message | < 5ms | < 20ms | 100ms |
| Background Worker | N/A | N/A | Per task budget |

### 8.2 Throughput Limits

| Pattern | Max Throughput | Throttle Strategy |
|---|---|---|
| Event Publishing | 10,000 events/sec | In-process (no I/O) |
| Command Execution | 1,000 commands/sec | Queue + backpressure |
| Query Execution | 5,000 queries/sec | Cache + connection pool |
| IPC Messages | 2,000 messages/sec | Batch + debounce |
| Plugin Messages | 100 messages/sec | Rate limit per plugin |
