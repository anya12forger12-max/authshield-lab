# Event Bus Architecture

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

The Event Bus is the central nervous system of AuthShield Lab. It enables decoupled, asynchronous communication between all 20 services and the plugin ecosystem. Built on Python's `asyncio`, it operates entirely in-memory with optional persistent logging for durability requirements.

### 1.1 Design Goals

| Goal | Implementation |
|------|---------------|
| Decoupling | Publishers and subscribers have no direct references |
| Performance | Sub-5ms delivery for in-process events |
| Reliability | At-least-once delivery with dead letter queue |
| Observability | Full event logging with correlation tracking |
| Extensibility | Plugins can subscribe and publish via SDK |
| Ordering | Guaranteed ordering per publisher identity |
| Resilience | Failed handlers don't block the bus |

---

## 2. Event Categories

### 2.1 Domain Events

Domain events represent significant business state changes within the platform.

| Event Type | Publisher | Subscribers | Payload Schema |
|-----------|-----------|-------------|----------------|
| `course.created` | Course Management | Analytics, Notifications, Audit | `CourseCreatedPayload` |
| `course.updated` | Course Management | Analytics, Notifications | `CourseUpdatedPayload` |
| `course.published` | Course Management | Learning Engine, Analytics, Notifications | `CoursePublishedPayload` |
| `course.archived` | Course Management | Learning Engine, Analytics | `CourseArchivedPayload` |
| `lesson.started` | Learning Engine | Analytics, Reporting | `LessonStartedPayload` |
| `lesson.completed` | Learning Engine | Assessment, Analytics, Reporting | `LessonCompletedPayload` |
| `assessment.started` | Assessment Engine | Analytics, Learning Engine | `AssessmentStartedPayload` |
| `assessment.submitted` | Assessment Engine | Learning Engine, Analytics, Reporting | `AssessmentSubmittedPayload` |
| `assessment.passed` | Assessment Engine | Certificate, Learning Engine, Analytics | `AssessmentPassedPayload` |
| `assessment.failed` | Assessment Engine | Learning Engine, Analytics | `AssessmentFailedPayload` |
| `certificate.issued` | Certificate Service | Analytics, Notifications, Audit | `CertificateIssuedPayload` |
| `student.enrolled` | Learning Engine | Course Management, Analytics, Notifications | `StudentEnrolledPayload` |
| `student.progress.updated` | Learning Engine | Analytics, Reporting | `StudentProgressUpdatedPayload` |

**Ordering Guarantee:** Per-course ordering guaranteed. Cross-course events may interleave.

**Delivery Guarantee:** At-least-once. Subscribers must be idempotent.

**Persistence:** Event log retained for 30 days in memory; optionally persisted to audit log.

### 2.2 Application Events

Application events represent user interface interactions and application-level state changes.

| Event Type | Publisher | Subscribers | Payload Schema |
|-----------|-----------|-------------|----------------|
| `app.view.changed` | UI Layer | Analytics, Accessibility | `ViewChangedPayload` |
| `app.action.performed` | UI Layer | Analytics, Audit | `ActionPerformedPayload` |
| `app.search.executed` | UI Layer | Analytics | `SearchExecutedPayload` |
| `app.error.occurred` | All Services | Logging, Diagnostics, Notifications | `ErrorOccurredPayload` |
| `app.session.started` | Authentication | Analytics, Audit | `SessionStartedPayload` |
| `app.session.ended` | Authentication | Analytics, Audit | `SessionEndedPayload` |
| `app.focus.changed` | Accessibility | Accessibility | `FocusChangedPayload` |

**Ordering Guarantee:** Per-source ordering guaranteed.

**Delivery Guarantee:** Best-effort for UI events; at-least-once for session events.

**Persistence:** Retained for 7 days in memory.

### 2.3 System Events

System events represent infrastructure and lifecycle changes.

| Event Type | Publisher | Subscribers | Payload Schema |
|-----------|-----------|-------------|----------------|
| `system.startup` | Platform | All Services | `StartupPayload` |
| `system.shutdown` | Platform | All Services | `ShutdownPayload` |
| `system.health.degraded` | Diagnostics | Notifications, Logging | `HealthDegradedPayload` |
| `system.health.recovered` | Diagnostics | Notifications, Logging | `HealthRecoveredPayload` |
| `system.memory.warning` | Diagnostics | Logging, Notifications | `MemoryWarningPayload` |
| `system.storage.low` | Diagnostics | Notifications, Backup | `StorageLowPayload` |
| `system.error.critical` | All Services | Logging, Diagnostics, Notifications | `CriticalErrorPayload` |

**Ordering Guarantee:** Global ordering (system events are rare and critical).

**Delivery Guarantee:** At-least-once with synchronous audit logging.

**Persistence:** Permanent retention in audit log.

### 2.4 Plugin Events

Plugin events represent plugin lifecycle and communication.

| Event Type | Publisher | Subscribers | Payload Schema |
|-----------|-----------|-------------|----------------|
| `plugin.installed` | Plugin Runtime | Analytics, Notifications | `PluginInstalledPayload` |
| `plugin.enabled` | Plugin Runtime | Analytics, Notifications | `PluginEnabledPayload` |
| `plugin.disabled` | Plugin Runtime | Analytics, Notifications | `PluginDisabledPayload` |
| `plugin.uninstalled` | Plugin Runtime | Analytics | `PluginUninstalledPayload` |
| `plugin.error` | Plugin Runtime | Diagnostics, Logging, Notifications | `PluginErrorPayload` |
| `plugin.permission.requested` | Plugin Runtime | Authorization, Audit | `PluginPermissionRequestPayload` |
| `plugin.event` | Plugin | Other Plugins (via bus only) | `PluginEventPayload` |

**Ordering Guarantee:** Per-plugin ordering guaranteed.

**Delivery Guarantee:** At-least-once for lifecycle events; best-effort for plugin-to-plugin.

**Persistence:** Retained for 30 days.

### 2.5 Audit Events

Audit events are immutable records of security-relevant actions.

| Event Type | Publisher | Subscribers | Payload Schema |
|-----------|-----------|-------------|----------------|
| `audit.user.login` | Authentication | Audit Service | `AuditLoginPayload` |
| `audit.user.logout` | Authentication | Audit Service | `AuditLogoutPayload` |
| `audit.user.created` | Administration | Audit Service | `AuditUserCreatedPayload` |
| `audit.user.deleted` | Administration | Audit Service | `AuditUserDeletedPayload` |
| `audit.role.assigned` | Authorization | Audit Service | `AuditRoleAssignedPayload` |
| `audit.role.revoked` | Authorization | Audit Service | `AuditRoleRevokedPayload` |
| `audit.permission.denied` | Authorization | Audit Service | `AuditPermissionDeniedPayload` |
| `audit.config.changed` | Configuration | Audit Service | `AuditConfigChangedPayload` |
| `audit.backup.created` | Backup | Audit Service | `AuditBackupCreatedPayload` |
| `audit.data.exported` | Backup | Audit Service | `AuditDataExportedPayload` |

**Ordering Guarantee:** Strict global ordering (critical for compliance).

**Delivery Guarantee:** Synchronous at-least-once; platform blocks on audit delivery failure.

**Persistence:** Permanent; append-only log with integrity checksums.

### 2.6 Accessibility Events

Accessibility events support screen readers and assistive technologies.

| Event Type | Publisher | Subscribers | Payload Schema |
|-----------|-----------|-------------|----------------|
| `a11y.announcement` | Accessibility Service | UI Layer | `AnnouncementPayload` |
| `a11y.focus.moved` | Accessibility Service | UI Layer | `FocusMovedPayload` |
| `a11y.profile.updated` | Identity Service | UI Layer, Accessibility | `A11yProfileUpdatedPayload` |
| `a11y.shortcut.activated` | UI Layer | Various Services | `ShortcutActivatedPayload` |
| `a11y.contrast.requested` | UI Layer | Accessibility | `ContrastRequestedPayload` |

**Ordering Guarantee:** Per-user ordering guaranteed.

**Delivery Guarantee:** At-least-once (critical for accessibility compliance).

**Persistence:** 90-day retention for compliance.

### 2.7 Security Events

Security events detect and respond to threats.

| Event Type | Publisher | Subscribers | Payload Schema |
|-----------|-----------|-------------|----------------|
| `security.login.failed` | Authentication | Audit, Notifications | `LoginFailedPayload` |
| `security.brute_force.detected` | Authentication | Audit, Notifications, Diagnostics | `BruteForceDetectedPayload` |
| `security.unauthorized.access` | Authorization | Audit, Notifications | `UnauthorizedAccessPayload` |
| `security.plugin.tamper.detected` | Plugin Runtime | Audit, Notifications, Diagnostics | `PluginTamperPayload` |
| `security.integrity.violation` | Audit Service | Diagnostics, Notifications | `IntegrityViolationPayload` |

**Ordering Guarantee:** Strict global ordering.

**Delivery Guarantee:** Synchronous at-least-once with immediate notification.

**Persistence:** Permanent with integrity verification.

### 2.8 Configuration Events

Configuration events propagate setting changes.

| Event Type | Publisher | Subscribers | Payload Schema |
|-----------|-----------|-------------|----------------|
| `config.updated` | Configuration | All Services (filtered) | `ConfigUpdatedPayload` |
| `config.security.updated` | Configuration | Authentication, Authorization | `SecurityConfigUpdatedPayload` |
| `config.policies.updated` | Configuration | Authorization | `PoliciesConfigUpdatedPayload` |
| `config.accessibility.updated` | Configuration | Accessibility, UI Layer | `AccessibilityConfigUpdatedPayload` |
| `config.localization.updated` | Configuration | Localization, UI Layer | `LocalizationConfigUpdatedPayload` |

**Ordering Guarantee:** Per-setting ordering guaranteed.

**Delivery Guarantee:** At-least-once with confirmation.

**Persistence:** Retained for 30 days.

### 2.9 Lifecycle Events

Lifecycle events manage service state transitions.

| Event Type | Publisher | Subscribers | Payload Schema |
|-----------|-----------|-------------|----------------|
| `service.initialized` | Service Registry | Diagnostics | `ServiceInitializedPayload` |
| `service.ready` | Service Registry | Diagnostics | `ServiceReadyPayload` |
| `service.degraded` | Service Registry | Diagnostics, Notifications | `ServiceDegradedPayload` |
| `service.failed` | Service Registry | Diagnostics, Notifications | `ServiceFailedPayload` |
| `service.recovered` | Service Registry | Diagnostics, Notifications | `ServiceRecoveredPayload` |

**Ordering Guarantee:** Global ordering (lifecycle events are sequential).

**Delivery Guarantee:** At-least-once with synchronous handling.

**Persistence:** 30-day retention.

### 2.10 Backup Events

Backup events track data protection operations.

| Event Type | Publisher | Subscribers | Payload Schema |
|-----------|-----------|-------------|----------------|
| `backup.started` | Backup Service | Notifications, Audit | `BackupStartedPayload` |
| `backup.completed` | Backup Service | Notifications, Audit | `BackupCompletedPayload` |
| `backup.failed` | Backup Service | Notifications, Audit, Diagnostics | `BackupFailedPayload` |
| `backup.restored` | Backup Service | Notifications, Audit | `BackupRestoredPayload` |
| `backup.scheduled` | Backup Service | Audit | `BackupScheduledPayload` |
| `backup.expired` | Backup Service | Audit | `BackupExpiredPayload` |

**Ordering Guarantee:** Per-backup-operation ordering.

**Delivery Guarantee:** At-least-once.

**Persistence:** Retained for 90 days.

---

## 3. Event Bus Implementation

### 3.1 Core Architecture

```python
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine
from uuid import uuid4

@dataclass
class Event:
    id: str = field(default_factory=lambda: str(uuid4()))
    type: str = ""
    source: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    correlation_id: str = ""
    payload: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    version: str = "1.0"
    priority: str = "normal"

@dataclass
class Subscription:
    id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""
    handler: Callable[..., Coroutine] | None = None
    filter_fn: Callable[[Event], bool] | None = None
    priority: int = 0
    max_retries: int = 3
    is_active: bool = True

@dataclass
class PublishResult:
    event_id: str
    subscribers_notified: int
    subscribers_failed: int
    duration_ms: float
    errors: list[str] = field(default_factory=list)
```

### 3.2 Asyncio-Based Event Bus

```python
class AsyncEventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Subscription]] = {}
        self._wildcard_subscribers: list[Subscription] = []
        self._event_log: asyncio.Queue[Event] = asyncio.Queue(maxsize=10000)
        self._dead_letter_queue: list[tuple[Event, str]] = []
        self._processing_lock = asyncio.Lock()
        self._metrics = EventBusMetrics()
        self._handlers: dict[str, set[str]] = {}  # event_type -> handler_ids

    async def publish(self, event: Event) -> PublishResult:
        """Publish event to all matching subscribers asynchronously."""
        start = asyncio.get_event_loop().time()
        notified = 0
        failed = 0
        errors = []

        # Record in event log
        try:
            self._event_log.put_nowait(event)
        except asyncio.QueueFull:
            self._metrics.dropped_events += 1

        # Route to exact-match subscribers
        exact_subs = self._subscribers.get(event.type, [])
        # Route to wildcard subscribers
        wildcard_subs = [
            s for s in self._wildcard_subscribers
            if s.filter_fn is None or s.filter_fn(event)
        ]

        all_subs = sorted(
            exact_subs + wildcard_subs,
            key=lambda s: s.priority,
            reverse=True,
        )

        for sub in all_subs:
            if not sub.is_active:
                continue
            try:
                if sub.filter_fn and not sub.filter_fn(event):
                    continue
                await asyncio.wait_for(
                    sub.handler(event),
                    timeout=30.0,
                )
                notified += 1
                self._metrics.record_delivery(sub.event_type, success=True)
            except asyncio.TimeoutError:
                failed += 1
                errors.append(f"Handler {sub.id} timed out")
                self._metrics.record_delivery(sub.event_type, success=False)
            except Exception as e:
                failed += 1
                errors.append(f"Handler {sub.id} error: {str(e)}")
                self._metrics.record_delivery(sub.event_type, success=False)
                await self._handle_dead_letter(event, str(e))

        elapsed = (asyncio.get_event_loop().time() - start) * 1000

        return PublishResult(
            event_id=event.id,
            subscribers_notified=notified,
            subscribers_failed=failed,
            duration_ms=elapsed,
            errors=errors,
        )

    async def subscribe(
        self,
        event_type: str,
        handler: Callable[..., Coroutine],
        filter_fn: Callable[[Event], bool] | None = None,
        priority: int = 0,
        max_retries: int = 3,
    ) -> Subscription:
        """Subscribe to events of the given type."""
        sub = Subscription(
            event_type=event_type,
            handler=handler,
            filter_fn=filter_fn,
            priority=priority,
            max_retries=max_retries,
        )

        if event_type == "*":
            self._wildcard_subscribers.append(sub)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(sub)

        self._metrics.record_subscription(event_type)
        return sub

    async def unsubscribe(self, subscription: Subscription) -> None:
        """Remove a subscription."""
        subscription.is_active = False
        if subscription.event_type == "*":
            self._wildcard_subscribers = [
                s for s in self._wildcard_subscribers if s.id != subscription.id
            ]
        elif subscription.event_type in self._subscribers:
            self._subscribers[subscription.event_type] = [
                s for s in self._subscribers[subscription.event_type]
                if s.id != subscription.id
            ]

    async def _handle_dead_letter(self, event: Event, error: str) -> None:
        """Move failed event to dead letter queue."""
        self._dead_letter_queue.append((event, error))
        if len(self._dead_letter_queue) > 1000:
            self._dead_letter_queue = self._dead_letter_queue[-500:]

    async def replay_events(
        self,
        event_type: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[Event]:
        """Replay events from the log."""
        events = []
        temp = []
        while not self._event_log.empty():
            event = self._event_log.get_nowait()
            temp.append(event)
            if event_type and event.type != event_type:
                continue
            if since and event.timestamp < since.isoformat():
                continue
            events.append(event)
            if len(events) >= limit:
                break
        # Restore queue
        for e in temp:
            self._event_log.put_nowait(e)
        return events
```

---

## 4. Event Schemas

### 4.1 Standard Event Envelope

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EventEnvelope",
  "type": "object",
  "required": ["id", "type", "source", "timestamp", "payload"],
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid"
    },
    "type": {
      "type": "string",
      "pattern": "^[a-z]+\\.[a-z]+\\.[a-z]+$"
    },
    "source": {
      "type": "string",
      "minLength": 1
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "correlation_id": {
      "type": "string",
      "format": "uuid"
    },
    "payload": {
      "type": "object"
    },
    "metadata": {
      "type": "object"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$"
    },
    "priority": {
      "type": "string",
      "enum": ["low", "normal", "high", "critical"]
    }
  }
}
```

### 4.2 Course Published Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CoursePublishedPayload",
  "type": "object",
  "required": ["course_id", "course_title", "published_by", "lesson_count"],
  "properties": {
    "course_id": { "type": "string", "format": "uuid" },
    "course_title": { "type": "string", "minLength": 1, "maxLength": 200 },
    "published_by": { "type": "string", "format": "uuid" },
    "lesson_count": { "type": "integer", "minimum": 1 },
    "category": { "type": "string" },
    "difficulty_level": {
      "type": "string",
      "enum": ["beginner", "intermediate", "advanced", "expert"]
    },
    "estimated_duration_minutes": { "type": "integer", "minimum": 1 }
  }
}
```

### 4.3 Assessment Submitted Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AssessmentSubmittedPayload",
  "type": "object",
  "required": ["assessment_id", "student_id", "course_id", "score", "passed"],
  "properties": {
    "assessment_id": { "type": "string", "format": "uuid" },
    "student_id": { "type": "string", "format": "uuid" },
    "course_id": { "type": "string", "format": "uuid" },
    "score": { "type": "number", "minimum": 0, "maximum": 100 },
    "passed": { "type": "boolean" },
    "time_taken_seconds": { "type": "integer", "minimum": 0 },
    "questions_total": { "type": "integer", "minimum": 1 },
    "questions_correct": { "type": "integer", "minimum": 0 },
    "submitted_at": { "type": "string", "format": "date-time" }
  }
}
```

---

## 5. Event Versioning Strategy

### 5.1 Version Format

Events use a two-part version: `major.minor`

- **Minor version** bump: New optional fields added to payload; existing fields unchanged
- **Major version** bump: Fields removed, renamed, or type-changed; new event type created

### 5.2 Compatibility Rules

| Change Type | Version Action | Subscriber Impact |
|-------------|---------------|-------------------|
| New optional field | Minor bump | None (forward compatible) |
| New required field | Major bump | Must update handler |
| Field removed | Major bump | Must update handler |
| Field renamed | Major bump | Must update handler |
| Field type changed | Major bump | Must update handler |
| New event type | None | No impact |

### 5.3 Subscriber Version Handling

Subscribers must declare the event version they support. The event bus routes events to subscribers that support the event version or lower major version with compatible payload.

---

## 6. Dead Letter Queue

### 6.1 Purpose

Failed events that exceed maximum retry attempts are placed in the dead letter queue for later inspection and potential replay.

### 6.2 Dead Letter Entry

```python
@dataclass
class DeadLetterEntry:
    event: Event
    error: str
    attempt_count: int
    first_failure_at: str
    last_failure_at: str
    handler_id: str
    subscriber_id: str
```

### 6.3 Dead Letter Operations

| Operation | Description |
|-----------|-------------|
| List | View all dead letter entries with filtering |
| Replay | Re-attempt delivery of a specific dead letter entry |
| Retry All | Re-attempt all dead letter entries |
| Purge | Remove all dead letter entries |
| Export | Export dead letter entries for external analysis |

### 6.4 Dead Letter Thresholds

| Threshold | Value | Action |
|-----------|-------|--------|
| Max entries | 1,000 | Oldest entries archived |
| Auto-archive age | 7 days | Moved to audit log |
| Retry attempts per entry | 3 | Then moved to DLQ |
| Alert threshold | 10 entries | System notification |

---

## 7. Event Replay Capability

### 7.1 Replay Scenarios

| Scenario | Use Case | Scope |
|----------|---------|-------|
| Plugin initialization | New plugin needs historical events | Since plugin install time |
| Service recovery | Service needs to rebuild state | Since last known good state |
| Debug investigation | Developer investigating issue | Specific time range |
| Audit compliance | Regulatory audit requirement | Full retention period |

### 7.2 Replay Implementation

```python
class EventReplay:
    async def replay_for_subscriber(
        self,
        subscriber_id: str,
        event_type: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 1000,
    ) -> ReplayResult:
        """Replay events for a specific subscriber."""
        ...

    async def replay_for_time_range(
        self,
        start: datetime,
        end: datetime,
        event_types: list[str] | None = None,
    ) -> ReplayResult:
        """Replay all events within a time range."""
        ...

    async def replay_to_point(
        self,
        point_in_time: datetime,
    ) -> ReplayResult:
        """Replay events up to a specific point in time."""
        ...
```

### 7.3 Replay Constraints

- Replay does not re-execute handlers; it only re-delivers events
- Subscribers must handle duplicate events idempotently
- Replay is rate-limited to prevent event storm
- Maximum replay window: 30 days

---

## 8. Event Correlation

### 8.1 Correlation ID Propagation

Every event generated as part of a user action chain shares the same correlation ID. This enables tracing a complete user journey across multiple services.

```python
# Example correlation flow
correlation_id = str(uuid4())  # Generated at entry point

# Authentication service publishes
await event_bus.publish(Event(
    type="auth.user.authenticated",
    source="authentication_service",
    correlation_id=correlation_id,
    payload={"user_id": user_id},
))

# Learning engine publishes (same correlation)
await event_bus.publish(Event(
    type="learning.student.enrolled",
    source="learning_engine_service",
    correlation_id=correlation_id,
    payload={"student_id": user_id, "course_id": course_id},
))
```

### 8.2 Correlation Query

```python
class CorrelationTracker:
    async def get_event_chain(
        self,
        correlation_id: str,
    ) -> list[Event]:
        """Get all events sharing a correlation ID."""
        ...

    async def get_duration(
        self,
        correlation_id: str,
    ) -> float:
        """Get total duration of an event chain."""
        ...

    async def get_failure_points(
        self,
        correlation_id: str,
    ) -> list[Event]:
        """Get failed events in a correlation chain."""
        ...
```

---

## 9. Event Bus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `events.published.total` | Counter | Total events published |
| `events.delivered.total` | Counter | Total successful deliveries |
| `events.failed.total` | Counter | Total failed deliveries |
| `events.dead_letter.total` | Counter | Total dead letter entries |
| `events.replay.total` | Counter | Total replay operations |
| `events.publish.latency` | Histogram | Time from publish to return |
| `events.delivery.latency` | Histogram | Time from publish to handler start |
| `events.subscribers.active` | Gauge | Active subscriber count |
| `events.queue.depth` | Gauge | Event log queue depth |
| `events.dropped.total` | Counter | Events dropped due to full log |

---

## 10. Event Bus Lifecycle

### 10.1 Initialization

```
1. Create event bus instance
2. Register system event handlers
3. Register audit event handlers
4. Start event log processor
5. Load persistent subscriptions
6. Signal system.startup event
```

### 10.2 Operation

```
1. Accept publishes from all services
2. Route to matching subscribers
3. Handle failures with retry logic
4. Move dead letters to DLQ
5. Process replay requests
6. Collect metrics
```

### 10.3 Shutdown

```
1. Stop accepting new publishes
2. Drain in-flight events (up to timeout)
3. Flush event log to persistence
4. Flush dead letter queue
5. Notify all subscribers of shutdown
6. Release resources
```
