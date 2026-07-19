# AuthShield Lab — Service Communication Patterns

> Version: 1.0.0 | Last Updated: 2026-07-19
> Status: Living Document | Owner: Architecture Team

---

## 1. Overview

AuthShield Lab uses a combination of in-process event-driven communication and structured synchronous API calls between modules. This document defines the event bus architecture, synchronous call patterns, message patterns, error propagation, circuit breaker patterns, retry policies, and timeout management.

**Key principle:** Modules communicate through well-defined contracts. Direct function calls across module boundaries are forbidden — all cross-module communication goes through the event bus or the module's public API.

---

## 2. Event Bus Architecture

### 2.1 In-Process Event Bus

The primary communication mechanism is an **in-process event bus** implemented in `packages/event-bus/`. This bus runs within a single Python process and handles all cross-module event dispatch.

```
┌──────────────────────────────────────────────────────────┐
│                     Python Process                        │
│                                                          │
│  ┌─────────┐  publish   ┌──────────────┐  dispatch  ┌──────────┐ │
│  │  auth   │ ─────────► │              │ ─────────► │  users   │ │
│  └─────────┘            │  Event Bus   │            └──────────┘ │
│  ┌─────────┐  publish   │  (in-memory) │  dispatch  ┌──────────┐ │
│  │ sessions│ ─────────► │              │ ─────────► │  audit   │ │
│  └─────────┘            │              │            └──────────┘ │
│  ┌─────────┐  publish   │              │  dispatch  ┌──────────┐ │
│  │ defense │ ─────────► │              │ ─────────► │ policies │ │
│  └─────────┘            └──────────────┘            └──────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Event Bus API

```python
from packages.event_bus import EventBus, Event, EventHandler

bus = EventBus()

# Publishing an event
await bus.publish(Event(
    type="auth.login.success",
    source="auth",
    payload={"user_id": "123", "method": "password"},
    metadata={"correlation_id": "abc-123"}
))

# Subscribing to events
@bus.subscribe("auth.login.success")
async def on_login_success(event: Event) -> None:
    await audit.log(event)

# Wildcard subscriptions
@bus.subscribe("auth.*")
async def on_any_auth_event(event: Event) -> None:
    pass

# Category subscriptions
@bus.subscribe("defense.*")
async def on_any_defense_event(event: Event) -> None:
    pass
```

### 2.3 Cross-Module Event Flow

```
Module A ──publish──► Event Bus ──dispatch──► Subscriber B
                                            ──dispatch──► Subscriber C
                                            ──dispatch──► Subscriber D
```

**Rules:**
1. Publishing is async — the publisher does not wait for subscribers.
2. Subscribers are invoked in registration order (deterministic).
3. Subscriber failures are caught and logged — they do not block other subscribers.
4. Events are delivered at-most-once (no guaranteed delivery for in-process).

---

## 3. Synchronous API Calls

### 3.1 When Synchronous Calls Are Allowed

Synchronous calls between modules are permitted **only** when:

1. The calling module needs an **immediate result** to continue processing.
2. The called module's API is in the **same layer or lower layer**.
3. The response is needed within the same request lifecycle.

**Examples:**
- `auth` calls `users.get_user()` during login to verify the user exists.
- `lms` calls `content.get_content()` to load lesson material.
- `simulation` calls `defense.analyze()` to evaluate a defense response.

### 3.2 Forbidden Synchronous Calls

Synchronous calls are **forbidden** when:
- The call crosses into a higher layer (e.g., Core calling Application).
- The call is in a hot path (request latency budget exceeded).
- The call would create a circular dependency.

### 3.3 Synchronous Call Pattern

```python
# In auth module — calling users module synchronously
from packages.users import UserService

class LoginService:
    def __init__(self, user_service: UserService):
        self._user_service = user_service
    
    async def login(self, credentials: LoginRequest) -> SessionToken:
        # Synchronous call to users — allowed (same layer)
        user = await self._user_service.get_user_by_email(credentials.email)
        if user is None:
            raise AuthenticationError("Invalid credentials")
        
        # Continue with authentication...
        return await self._create_session(user.id)
```

---

## 4. Message Patterns

### 4.1 Publish/Subscribe (Primary Pattern)

Used for event-driven side effects: audit logging, analytics collection, notification dispatch.

```
Publisher                    Event Bus                 Subscribers
    │                            │                          │
    │── Event("auth.login") ────►│── dispatch ─────────────►│ audit
    │                            │── dispatch ─────────────►│ analytics
    │                            │── dispatch ─────────────►│ defense
```

**When to use:**
- The publisher does not need the subscriber's response.
- Multiple subscribers need to react to the same event.
- The side effect is optional (failure should not fail the operation).

### 4.2 Request/Reply Pattern

Used for synchronous data retrieval where the caller needs the result.

```
Caller                    Target Module
    │                            │
    │── GetUser(id) ────────────►│
    │                            │── query database
    │◄── User(id, name, email) ──│
```

**When to use:**
- The caller needs data from another module to continue.
- The operation is part of the request lifecycle.
- The response is required (not optional).

### 4.3 Event Sourcing Pattern

Used for `audit` module — all state changes are recorded as an immutable sequence of events.

```
┌─────────────────────────────────────────────────────┐
│                    Event Store                       │
│                                                     │
│  Event 1: auth.login.success   (user=123, ts=001)  │
│  Event 2: sessions.created     (sid=abc, ts=002)   │
│  Event 3: simulation.started   (sim=xyz, ts=003)   │
│  Event 4: simulation.completed (sim=xyz, ts=004)   │
│  Event 5: auth.logout          (user=123, ts=005)   │
│                                                     │
│  ── Rebuild current state by replaying events ──   │
└─────────────────────────────────────────────────────┘
```

**When to use:**
- Audit trail must be complete and immutable.
- State can be reconstructed from events.
- Temporal queries are required ("what happened at time T?").

### 4.4 Fan-Out Pattern

Used when a single event triggers actions in multiple modules.

```
                    Event Bus
                   ┌────┴────┐
    publish ───────┤         ├──────► audit.log()
                   │         ├──────► analytics.track()
                   │         ├──────► defense.analyze()
                   │         ├──────► notification.send()
```

**When to use:**
- A single action has cross-cutting effects.
- The effects are independent and can be parallelized.

### 4.5 Dead Letter Pattern

Failed event deliveries are routed to a dead letter queue for inspection.

```
Event ──► Subscriber (fails) ──► Retry (fails) ──► Dead Letter Queue
                                                        │
                                                        ▼
                                               Dead Letter Processor
                                               (log, alert, manual review)
```

---

## 5. Error Propagation

### 5.1 Error Categories

| Category | Examples | Propagation |
|---|---|---|
| **Transient** | Database timeout, network blip | Retry with backoff |
| **Permanent** | Invalid input, permission denied | Return error to caller |
| **Systemic** | Service unavailable, disk full | Circuit breaker + alert |
| **Data** | Constraint violation, corruption | Log + reject + alert |

### 5.2 Error Propagation Rules

**Rule 1: Never swallow errors silently.** All errors must be logged at the module boundary.

**Rule 2: Error context must be preserved.** When re-raising, include the original error as `__cause__`.

```python
try:
    user = await user_service.get_user(user_id)
except UserNotFoundError as exc:
    raise AuthenticationError(f"User {user_id} not found") from exc
```

**Rule 3: Module-specific errors stay within the module.** Only domain-level errors cross module boundaries.

```python
# Internal error (stays within auth module)
class PasswordHashError(Exception): ...

# Public error (crosses module boundary)
class AuthenticationError(Exception): ...
```

**Rule 4: Event handler errors do not propagate.** Subscriber failures are logged and do not affect the publisher.

```python
@bus.subscribe("auth.login.success")
async def on_login(event: Event) -> None:
    try:
        await audit.log(event)
    except Exception:
        logger.exception("Audit logging failed for auth.login.success")
        # Do NOT re-raise — the publisher is unaffected
```

### 5.3 Error Response Format

All module APIs return errors in a consistent format:

```python
{
    "error": {
        "code": "AUTH_INVALID_CREDENTIALS",
        "message": "The provided credentials are invalid.",
        "module": "auth",
        "details": {},
        "correlation_id": "abc-123"
    }
}
```

---

## 6. Circuit Breaker Patterns

### 6.1 Purpose

Circuit breakers protect the system from cascading failures when a dependent module is unavailable.

### 6.2 States

```
        ┌──────────┐
   ┌───►│  CLOSED  │──── (failure threshold exceeded) ────┐
   │    │ (normal) │                                       │
   │    └──────────┘                                       │
   │                                                       ▼
   │    ┌──────────┐                               ┌──────────┐
   └────│ HALF-OPEN│◄── (probe succeeds) ─────────│  OPEN    │
        │ (probe)  │                               │ (reject) │
        └──────────┘                               └──────────┘
              │                                           │
              └── (probe fails) ──────────────────────────┘
```

### 6.3 Configuration

```python
circuit_breaker = CircuitBreaker(
    failure_threshold=5,        # failures before opening
    recovery_timeout=30,        # seconds before half-open
    probe_interval=5,           # seconds between probes
    half_open_max_probes=1,     # probes before closing
)
```

### 6.4 Module-Specific Circuit Breakers

| Module Pair | Threshold | Recovery | Reason |
|---|---|---|---|
| `auth` → `users` | 5 failures | 30s | User lookup is critical for login |
| `lms` → `content` | 10 failures | 60s | Content can be cached |
| `simulation` → `defense` | 3 failures | 15s | Defense must respond quickly |
| `analytics` → `lms` | 20 failures | 120s | Analytics can be delayed |

### 6.5 Circuit Breaker Events

When a circuit breaker trips, it publishes an event:

```python
{
    "event_type": "circuit_breaker.opened",
    "source": "event_bus",
    "payload": {
        "source_module": "auth",
        "target_module": "users",
        "failure_count": 5,
        "last_error": "ConnectionTimeout"
    }
}
```

---

## 7. Retry Policies

### 7.1 Retry Strategy

All retries use **exponential backoff with jitter** to prevent thundering herds.

```python
@retry(
    max_retries=3,
    base_delay=1.0,       # seconds
    max_delay=30.0,       # seconds
    exponential_base=2,
    jitter=True,
    retryable_exceptions=[TransientError, TimeoutError],
)
async def call_with_retry(func, *args):
    return await func(*args)
```

### 7.2 Retry Configuration per Module

| Module | Max Retries | Base Delay | Max Delay | Retryable Errors |
|---|---|---|---|---|
| `auth` → `users` | 2 | 0.5s | 2s | Timeout, ConnectionError |
| `auth` → `sessions` | 2 | 0.5s | 2s | Timeout |
| `lms` → `content` | 3 | 1s | 10s | Timeout, NotFound |
| `defense` → `policies` | 1 | 0.1s | 0.5s | Timeout |
| `simulation` → `defense` | 1 | 0.2s | 1s | Timeout |
| `analytics` → all | 3 | 2s | 30s | Any transient |

### 7.3 Idempotency

Retried operations **must** be idempotent. If an operation is not naturally idempotent, it must include an idempotency key:

```python
result = await call_with_retry(
    audit.log,
    AuditEvent(
        type="auth.login.success",
        idempotency_key=f"login-{user_id}-{timestamp}"
    )
)
```

---

## 8. Timeout Management

### 8.1 Timeout Budgets

Every request has a total timeout budget. Module calls within the request must respect their share of the budget.

```
Total request budget: 5000ms
├── auth.login:                    500ms
│   ├── users.get_user:            200ms
│   ├── password.verify:           100ms
│   └── sessions.create:           200ms
├── Response serialization:         50ms
└── Audit logging (async):     no budget (background)
```

### 8.2 Timeout Configuration

```python
# Global default
DEFAULT_TIMEOUT = 5.0  # seconds

# Module-specific overrides
MODULE_TIMEOUTS = {
    "auth": {"users.get_user": 2.0, "sessions.create": 2.0},
    "lms": {"content.get_content": 5.0},
    "defense": {"policies.evaluate": 0.5},
    "simulation": {"defense.analyze": 1.0},
}
```

### 8.3 Timeout Propagation

When a module call times out:
1. The caller receives a `TimeoutError`.
2. The error is logged with the module pair and duration.
3. If a circuit breaker exists, the failure is recorded.
4. The caller decides whether to retry or fail the request.

### 8.4 Deadline Propagation

For chained calls, a deadline is propagated to ensure the total budget is respected:

```python
async def login(request: LoginRequest, deadline: float):
    remaining = deadline - time.monotonic()
    
    user = await user_service.get_user(
        request.user_id,
        timeout=min(remaining, 2.0)
    )
    
    remaining = deadline - time.monotonic()
    session = await session_service.create(
        user.id,
        timeout=min(remaining, 2.0)
    )
    
    return session
```

---

## 9. Event Bus Implementation Details

### 9.1 Event Bus Class

```python
class EventBus:
    """In-process event bus with type-safe subscriptions."""
    
    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}
        self._middleware: list[EventMiddleware] = []
    
    async def publish(self, event: Event) -> None:
        """Publish an event to all matching subscribers."""
        handlers = self._match_handlers(event.type)
        
        for handler in handlers:
            try:
                for mw in self._middleware:
                    event = await mw.process(event)
                await handler(event)
            except Exception:
                logger.exception(
                    "Event handler failed",
                    event_type=event.type,
                    handler=handler.__name__,
                )
    
    def subscribe(self, pattern: str):
        """Decorator to subscribe to events matching the pattern."""
        def decorator(func):
            self._handlers.setdefault(pattern, []).append(func)
            return func
        return decorator
```

### 9.2 Event Middleware

Middleware can be registered to process events before they reach subscribers:

```python
class AuditMiddleware(EventMiddleware):
    """Logs all events for audit purposes."""
    async def process(self, event: Event) -> Event:
        await self.audit_service.log(event)
        return event

class CorrelationMiddleware(EventMiddleware):
    """Ensures all events have a correlation ID."""
    async def process(self, event: Event) -> Event:
        if not event.metadata.correlation_id:
            event.metadata.correlation_id = str(uuid4())
        return event
```

### 9.3 Event Bus Health

The event bus exposes health metrics:

```python
{
    "status": "healthy",
    "events_published_total": 15420,
    "events_dispatched_total": 15420,
    "handler_failures_total": 3,
    "average_dispatch_time_ms": 0.42,
    "registered_handlers": 45,
    "subscribed_patterns": 22,
}
```

---

## 10. Communication Patterns Summary

| Pattern | Mechanism | When to Use | Example |
|---|---|---|---|
| Pub/Sub | Event bus | Side effects, analytics, audit | `auth` publishes `login.success` → `audit`, `analytics` subscribe |
| Request/Reply | Module API | Data retrieval in request lifecycle | `lms` calls `content.get_content()` |
| Event Sourcing | Audit store | Immutable history, temporal queries | All state changes recorded in `audit` |
| Fan-Out | Event bus | Multiple independent reactions | `simulation.completed` → `quality`, `analytics`, `lms` |
| Dead Letter | DLQ processor | Failed event handling | Unprocessable events logged for review |
| Circuit Breaker | Middleware | Failure protection | `auth` → `users` circuit breaker |
| Retry | Middleware | Transient error recovery | Content loading retry on timeout |

---

## 11. Monitoring & Observability

### 11.1 Metrics

| Metric | Type | Description |
|---|---|---|
| `event_bus.published.total` | Counter | Total events published |
| `event_bus.dispatched.total` | Counter | Total events dispatched to subscribers |
| `event_bus.handler.failures.total` | Counter | Failed handler invocations |
| `event_bus.dispatch.duration.ms` | Histogram | Time to dispatch an event |
| `circuit_breaker.state` | Gauge | Current state (0=closed, 1=half-open, 2=open) |
| `sync_call.duration.ms` | Histogram | Synchronous API call latency |
| `sync_call.failures.total` | Counter | Failed synchronous API calls |
| `retry.attempts.total` | Counter | Total retry attempts |

### 11.2 Health Checks

```python
def check_event_bus_health() -> HealthStatus:
    return HealthStatus(
        status="healthy" if bus.handler_failures < 100 else "degraded",
        details={
            "registered_handlers": len(bus._handlers),
            "failure_rate": bus.handler_failures / bus.events_published,
        }
    )
```

---

## 12. References

- [MODULE_BOUNDARIES.md](./MODULE_BOUNDARIES.md) — Module boundary definitions
- [DATA_FLOW.md](./DATA_FLOW.md) — Data lifecycle and request flow
- [CROSS_CUTTING_CONCERNS.md](./CROSS_CUTTING_CONCERNS.md) — Logging and error handling
- [WORKSPACE_ARCHITECTURE.md](./WORKSPACE_ARCHITECTURE.md) — Workspace layout
- [DEPENDENCY_GRAPH.json](./DEPENDENCY_GRAPH.json) — Module dependencies
