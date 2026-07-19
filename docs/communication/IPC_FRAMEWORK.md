# Inter-Process Communication Framework

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

AuthShield Lab operates as a dual-process architecture: an Electron main process (Node.js) hosting the React frontend and a Python backend process running FastAPI. The IPC framework governs all communication between these processes, between frontend components, between backend services, and between the platform and plugins.

### 1.1 Communication Layers

```
┌────────────────────────────────────────────────────────────┐
│                     Electron Main Process                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ React UI     │  │ IPC Handler  │  │ Plugin Host  │     │
│  │ (Renderer)   │  │ (Main)       │  │ (Sandboxed)  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
│  ───────┼─────────────────┼──────────────────┼─────────── │
│         │         IPC Bridge Layer            │              │
│  ───────┼─────────────────┼──────────────────┼─────────── │
│         │                 │                  │              │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐     │
│  │ FastAPI      │  │ Event Bus    │  │ SDK Runtime  │     │
│  │ Application  │  │ (asyncio)    │  │ (Facade)     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
│  ───────┼─────────────────┼──────────────────┼─────────── │
│         │      Service Layer (20 Services)    │              │
│  ───────┼─────────────────┼──────────────────┼─────────── │
│         │                 │                  │              │
│  ┌──────┴─────────────────┴──────────────────┴───────┐     │
│  │              Data Access Layer (SQLAlchemy)         │     │
│  └────────────────────────────┬───────────────────────┘     │
│                               │                             │
│  ┌────────────────────────────┴───────────────────────┐     │
│  │                    SQLite (WAL)                      │     │
│  └────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────┘
```

---

## 2. Communication Patterns

### 2.1 Request/Response Pattern

The synchronous request/response pattern is used for operations that require immediate confirmation of success or failure.

**Characteristics:**
- Caller blocks until response is received
- Strict timeout enforcement
- Exactly one response per request
- Correlation ID for request tracing
- Typed request and response payloads

**Flow:**

```
Caller                    Router                   Handler
  │                         │                         │
  │──── Request ──────────>│                         │
  │    (correlation_id)     │──── Route + Validate ─>│
  │                         │                         │── Process
  │                         │                         │── Return
  │                         │<──── Response ──────────│
  │<── Response ───────────│                         │
  │    (correlation_id)     │                         │
```

**Implementation:**

```python
@dataclass
class Request:
    id: str                    # UUIDv4 correlation ID
    service: str               # Target service name
    method: str                # Method to invoke
    payload: dict              # Request data
    timeout: float = 30.0      # Seconds
    metadata: dict = field(default_factory=dict)

@dataclass
class Response:
    request_id: str            # Correlates to Request.id
    success: bool
    data: Any | None
    error: ServiceError | None
    duration_ms: float
    metadata: dict = field(default_factory=dict)
```

**Timeout Handling:**

| Scenario | Action |
|----------|--------|
| Response within timeout | Return response to caller |
| Timeout exceeded | Return timeout error; cancel pending handler work |
| Handler crash | Return service error with details |
| Network partition (Electron IPC) | Return connection error; trigger health check |

### 2.2 Publish/Subscribe Pattern

The publish/subscribe pattern is the primary mechanism for decoupled, asynchronous communication between services and plugins.

**Characteristics:**
- Decoupled publishers and subscribers
- Multiple subscribers per event
- At-least-once delivery guarantee
- Event ordering per publisher
- No ordering guarantee across publishers
- Non-blocking for publishers

**Flow:**

```
Publisher              Event Bus              Subscriber A    Subscriber B
  │                       │                      │               │
  │── Publish Event ────>│                      │               │
  │   (event_type)        │── Match + Route ────>│               │
  │                       │── Match + Route ──────────────────>│
  │<── Ack ──────────────│                      │               │
  │                       │                      │── Process ───>│
  │                       │                      │── Ack ───────>│
  │                       │                      │               │── Process
  │                       │<─────────────────────────────────────│── Ack
```

**Event Bus Implementation:**

```python
class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._dead_letter_queue: list[Event] = []
        self._event_log: list[Event] = []
        self._lock = asyncio.Lock()

    async def publish(self, event: Event) -> PublishResult:
        """Publish event to all matching subscribers."""
        ...

    async def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        filter_fn: Callable | None = None,
    ) -> Subscription:
        """Subscribe to events matching the type and optional filter."""
        ...

    async def unsubscribe(self, subscription: Subscription) -> None:
        """Remove subscription."""
        ...
```

### 2.3 Notifications Pattern (Fire-and-Forget)

Used for non-critical information delivery where acknowledgment is not required.

**Characteristics:**
- No response expected
- No delivery guarantee (best-effort)
- No correlation tracking
- Minimal overhead
- Used for UI updates, progress indicators, non-critical logging

**Implementation:**

```python
@dataclass
class Notification:
    type: str                  # e.g., "ui.toast", "progress.update"
    payload: dict
    priority: str = "normal"   # "low", "normal", "high", "critical"
    ttl: float = 5.0           # Seconds before auto-dismiss
```

### 2.4 Background Workers Pattern

Long-running operations are delegated to background workers to avoid blocking the main event loop.

**Characteristics:**
- Async task execution
- Progress reporting
- Cancellation support
- Result collection
- Error isolation

**Flow:**

```
Caller              Task Queue            Worker Pool            Result Store
  │                    │                      │                      │
  │── Submit Task ───>│                      │                      │
  │<── Task ID ───────│                      │                      │
  │                    │── Assign Task ──────>│                      │
  │                    │                      │── Execute            │
  │── Progress ─────────────────────────────>│── Report ──────────>│
  │<── Progress ─────────────────────────────────────────────────────│
  │                    │                      │── Complete           │
  │── Get Result ──────────────────────────────────────────────────>│
  │<── Result ──────────────────────────────────────────────────────│
```

**Worker Implementation:**

```python
class BackgroundWorker:
    def __init__(self, max_workers: int = 4):
        self._semaphore = asyncio.Semaphore(max_workers)
        self._tasks: dict[str, AsyncTask] = {}
        self._results: dict[str, TaskResult] = {}

    async def submit(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        progress_callback: Callable | None = None,
    ) -> str:
        """Submit task and return task ID."""
        ...

    async def cancel(self, task_id: str) -> bool:
        """Cancel a running task cooperatively."""
        ...

    async def get_result(self, task_id: str, timeout: float = None) -> TaskResult:
        """Wait for and retrieve task result."""
        ...
```

### 2.5 Job Queue Pattern

Persistent job queue for operations that must survive application restarts.

**Characteristics:**
- Disk-persisted jobs
- Priority ordering
- Retry with backoff
- Dead letter queue
- Status tracking (pending, running, completed, failed, cancelled)

**Job States:**

```
                    ┌──────────┐
                    │ PENDING  │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
              ┌─────│ RUNNING  │─────┐
              │     └────┬─────┘     │
              │          │           │
         ┌────▼───┐ ┌────▼───┐ ┌────▼────┐
         │COMPLETED│ │ FAILED │ │CANCELLED│
         └────────┘ └────┬───┘ └─────────┘
                         │
                    ┌────▼─────┐
                    │ RETRYING │
                    └────┬─────┘
                         │ (max retries exceeded)
                    ┌────▼──────────┐
                    │ DEAD LETTER   │
                    └───────────────┘
```

### 2.6 Task Scheduling Pattern

Cron-like scheduling for periodic tasks such as backup, cleanup, and health checks.

**Implementation:**

```python
@dataclass
class ScheduledTask:
    name: str
    func: Callable
    schedule: str              # Cron expression or interval
    enabled: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None
    max_runtime: float = 300.0 # Seconds

class TaskScheduler:
    async def schedule(self, task: ScheduledTask) -> None:
        """Register a periodic task."""
        ...

    async def unschedule(self, name: str) -> None:
        """Remove a scheduled task."""
        ...

    async def run_now(self, name: str) -> TaskResult:
        """Trigger immediate execution of a scheduled task."""
        ...
```

---

## 3. Cancellation Model

All long-running operations support cooperative cancellation through `CancellationToken` objects.

```python
class CancellationToken:
    def __init__(self):
        self._cancelled = False
        self._callbacks: list[Callable] = []
        self._lock = asyncio.Lock()

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    async def cancel(self) -> None:
        async with self._lock:
            self._cancelled = True
            for cb in self._callbacks:
                await cb()

    def register_callback(self, callback: Callable) -> None:
        self._callbacks.append(callback)

    def throw_if_cancelled(self) -> None:
        if self._cancelled:
            raise OperationCancelledError()
```

**Usage Pattern:**

```python
async def long_operation(token: CancellationToken):
    for item in large_dataset:
        token.throw_if_cancelled()
        await process(item)
        await asyncio.sleep(0)  # Yield control
    token.throw_if_cancelled()
    await finalize()
```

---

## 4. Timeout Configuration

| Operation Type | Default Timeout | Maximum Timeout | Configurable |
|---------------|----------------|-----------------|--------------|
| Authentication | 5s | 15s | Yes |
| Authorization | 2s | 5s | No |
| Database Query | 10s | 30s | Yes |
| File I/O | 30s | 120s | Yes |
| Plugin Execution | 30s | 300s | Yes |
| Report Generation | 60s | 600s | Yes |
| Backup/Restore | 300s | 3600s | Yes |
| Diagnostics | 15s | 60s | Yes |
| UI Operations | 2s | 10s | No |
| Event Processing | 5s | 30s | Yes |

**Timeout Escalation:**

```
Level 1: Soft Warning  → Log warning, continue processing
Level 2: Hard Timeout  → Cancel operation, return timeout error
Level 3: Force Kill    → Terminate worker, log critical error
```

---

## 5. Retry Strategy

### 5.1 Exponential Backoff with Jitter

```python
def calculate_retry_delay(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    multiplier: float = 2.0,
    jitter: float = 0.5,
) -> float:
    delay = min(base_delay * (multiplier ** attempt), max_delay)
    jitter_range = delay * jitter
    return delay + random.uniform(-jitter_range, jitter_range)
```

### 5.2 Retry Policies by Error Category

| Error Category | Max Retries | Base Delay | Multiplier | Jitter |
|---------------|-------------|------------|------------|--------|
| Network Transient | 5 | 0.5s | 2.0 | 0.3 |
| Database Locked | 3 | 0.1s | 2.0 | 0.2 |
| Service Unavailable | 3 | 1.0s | 3.0 | 0.5 |
| Plugin Error | 1 | 1.0 | 1.0 | 0.0 |
| Validation Error | 0 | 0 | 0 | 0 |
| Authentication Error | 0 | 0 | 0 | 0 |

### 5.3 Retry Decision Matrix

```
Is error retryable?
├── Yes
│   ├── Attempts remaining?
│   │   ├── Yes → Calculate delay → Wait → Retry
│   │   └── No  → Return failure with exhaustion error
│   └── Circuit breaker open?
│       ├── Yes → Wait for recovery → Retry
│       └── No  → Calculate delay → Wait → Retry
└── No
    → Return failure immediately
```

---

## 6. Circuit Breaker

### 6.1 State Machine

```
         Success                    Failure threshold exceeded
    ┌─────────────┐            ┌─────────────────┐
    │   CLOSED    │───────────>│      OPEN       │
    │ (normal)    │            │ (failing fast)  │
    └─────────────┘            └────────┬────────┘
         ^                              │
         │                              │ Recovery timeout
         │            ┌─────────────────▼────────┐
         │            │    HALF-OPEN             │
         └────────────│ (testing recovery)       │
              Success └──────────────────────────┘
```

### 6.2 Configuration

```python
@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5       # Failures before opening
    success_threshold: int = 3       # Successes before closing from half-open
    recovery_timeout: float = 30.0   # Seconds before half-open
    monitoring_window: float = 60.0  # Window for failure counting
    half_open_max_calls: int = 3     # Test calls in half-open state
```

### 6.3 Per-Service Breakers

| Service | Failure Threshold | Recovery Timeout |
|---------|-------------------|------------------|
| Authentication | 3 | 60s |
| Database | 5 | 10s |
| Plugin Runtime | 3 | 30s |
| Configuration | 2 | 5s |
| Event Bus | 10 | 5s |

---

## 7. Graceful Shutdown

### 7.1 Shutdown Protocol

```
Phase 1: Signal (0-5s)
├── Stop accepting new work
├── Notify all services of impending shutdown
└── Start shutdown timer

Phase 2: Drain (5-30s)
├── Complete in-flight requests (up to timeout)
├── Flush pending events to log
├── Cancel background workers
└── Persist job queue state

Phase 3: Cleanup (30-60s)
├── Close database connections
├── Flush audit log
├── Flush logging
├── Close event bus
└── Release resources

Phase 4: Terminate (60s)
└── Force exit if still running
```

### 7.2 Shutdown Hooks

```python
class ShutdownManager:
    def __init__(self):
        self._hooks: list[tuple[int, Callable]] = []  # (priority, hook)
        self._phase = ShutdownPhase.IDLE

    def register_hook(self, priority: int, hook: Callable) -> None:
        """Register a shutdown hook with priority (lower = earlier)."""
        ...

    async def shutdown(self, timeout: float = 60.0) -> None:
        """Execute graceful shutdown."""
        ...

    async def force_shutdown(self) -> None:
        """Force immediate termination."""
        ...
```

---

## 8. IPC Message Contracts

### 8.1 Message Format

All IPC messages follow a standard envelope format:

```python
@dataclass
class IPCMessage:
    version: str = "1.0"
    id: str = ""                    # UUIDv4
    correlation_id: str = ""        # For request/response pairing
    source: str = ""                # Originating service/component
    destination: str = ""           # Target service/component
    type: str = ""                  # Message type
    timestamp: str = ""             # ISO 8601
    headers: dict = field(default_factory=dict)
    payload: Any = None
    priority: str = "normal"
    ttl: float = 30.0
```

### 8.2 Message Versioning

- Message version is part of the envelope
- Receivers must handle unknown fields gracefully
- Breaking changes require new message version
- Migration period: 2 minor versions minimum

### 8.3 Message Validation

Every message is validated at the boundary:

```python
class MessageValidator:
    def validate(self, message: IPCMessage) -> ValidationResult:
        errors = []
        if not message.id:
            errors.append("Missing message ID")
        if not message.source:
            errors.append("Missing source")
        if not message.destination:
            errors.append("Missing destination")
        if not message.type:
            errors.append("Missing message type")
        if message.ttl <= 0:
            errors.append("Invalid TTL")
        return ValidationResult(valid=len(errors) == 0, errors=errors)
```

---

## 9. Message Lifecycle

```
1. CREATION
   ├── Assign message ID
   ├── Set timestamp
   ├── Set correlation ID (if request/response)
   ├── Validate payload against schema
   └── Apply message headers

2. ROUTING
   ├── Validate source permission
   ├── Resolve destination
   ├── Check circuit breaker state
   ├── Apply rate limiting
   ├── Enqueue in message queue
   └── Apply priority ordering

3. PROCESSING
   ├── Dequeue message
   ├── Validate message (check TTL, format)
   ├── Acquire processing lock
   ├── Execute handler
   ├── Capture result
   ├── Release processing lock
   └── Record duration

4. ACKNOWLEDGMENT
   ├── On success: ack to sender, update metrics
   ├── On failure: retry logic evaluation
   ├── On timeout: cancel and ack failure
   ├── On circuit open: queue for later or reject
   └── Log completion
```

---

## 10. Performance Characteristics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Request/Response latency (p50) | <5ms | In-process calls |
| Request/Response latency (p99) | <50ms | In-process calls |
| Event publication latency | <1ms | Time to publish |
| Event delivery latency (p50) | <5ms | Time to handler start |
| Event delivery latency (p99) | <50ms | Time to handler start |
| Background worker throughput | 1000 tasks/sec | Task submission rate |
| Circuit breaker trip time | <100ms | Time to state change |
| Graceful shutdown time | <30s | Signal to termination |
| Message throughput | 10,000 msgs/sec | Sustained rate |

---

## 11. Monitoring and Observability

### 11.1 Metrics Collected

| Metric | Type | Labels |
|--------|------|--------|
| `ipc.request.duration` | Histogram | service, method, status |
| `ipc.request.count` | Counter | service, method, status |
| `ipc.event.published` | Counter | event_type, source |
| `ipc.event.delivered` | Counter | event_type, subscriber |
| `ipc.event.failed` | Counter | event_type, error_code |
| `ipc.circuit.state` | Gauge | service (0=closed, 1=half, 2=open) |
| `ipc.worker.active` | Gauge | worker_id |
| `ipc.worker.queued` | Gauge | queue_name |
| `ipc.shutdown.duration` | Histogram | phase |

### 11.2 Logging Requirements

- All IPC messages logged at DEBUG level
- Errors logged at ERROR level with full context
- Slow operations logged at WARN level (>100ms)
- Circuit breaker state changes logged at INFO level
- Shutdown events logged at INFO level

---

## 12. Testing Strategies

| Pattern | Test Type | Description |
|---------|-----------|-------------|
| Request/Response | Unit | Mock handler, verify response |
| Publish/Subscribe | Integration | Verify event delivery |
| Cancellation | Unit | Verify cooperative cancellation |
| Timeout | Integration | Verify timeout enforcement |
| Circuit Breaker | Unit | Verify state transitions |
| Retry | Unit | Verify retry with mock failures |
| Graceful Shutdown | Integration | Verify drain behavior |
| Message Validation | Unit | Verify schema validation |
