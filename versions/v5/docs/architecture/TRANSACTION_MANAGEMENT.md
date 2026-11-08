# Transaction Management

## Overview

AuthShield Lab manages transactions across multiple aggregates and services using
database-level atomicity, the Saga pattern for cross-aggregate operations,
compensation actions, idempotency keys, and event-driven eventual consistency.

---

## Strategy Selection Matrix

| Scenario | Strategy | Consistency | Complexity |
|---|---|---|---|
| Single aggregate mutation | Database transaction | Strong | Low |
| Multi-aggregate same DB | Database transaction | Strong | Medium |
| Cross-service operation | Saga pattern | Eventual | High |
| External API calls | Outbox pattern | Eventual | High |
| Read-heavy operations | CQRS + cache | Eventual | Medium |
| File system + DB | Saga with compensation | Eventual | High |

---

## Atomic Operations (Database Transactions)

Single-aggregate operations use direct database transactions managed by
SQLAlchemy async sessions.

### Repository Transaction Pattern

```python
class SQLAlchemyUserRepository:
    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory

    async def save(self, user: User) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                model = UserMapper.to_model(user)
                session.add(model)

    async def save_with_events(
        self, user: User, events: list[DomainEvent]
    ) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                model = UserMapper.to_model(user)
                session.add(model)
                for event in events:
                    outbox_entry = OutboxEntry.from_domain_event(event)
                    session.add(outbox_entry)
```

### Unit of Work Pattern

```python
class UnitOfWork:
    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._repositories: dict[type, Any] = {}
        self._events: list[DomainEvent] = []

    async def __aenter__(self) -> "UnitOfWork":
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self._session.close()

    @property
    def users(self) -> UserRepositoryPort:
        if "users" not in self._repositories:
            self._repositories["users"] = SQLAlchemyUserRepository(self._session)
        return self._repositories["users"]

    @property
    def courses(self) -> CourseRepositoryPort:
        if "courses" not in self._repositories:
            self._repositories["courses"] = SQLAlchemyCourseRepository(self._session)
        return self._repositories["courses"]

    def collect_events(self) -> list[DomainEvent]:
        events = []
        for repo in self._repositories.values():
            if hasattr(repo, "collect_events"):
                events.extend(repo.collect_events())
        return events

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
```

### Unit of Work Usage in Use Cases

```python
class EnrollStudentUseCase:
    def __init__(self, uow_factory: Callable[..., UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    async def execute(self, input_dto: EnrollStudentInput) -> EnrollStudentOutput:
        async with self._uow_factory() as uow:
            course = await uow.courses.find_by_id(input_dto.course_id)
            if course is None:
                raise EntityNotFound("Course", input_dto.course_id)

            if course.enrollment_count >= course.capacity:
                raise BusinessRuleViolation("BR-COURSE-014", "Course is full")

            enrollment = Enrollment(
                course_id=input_dto.course_id,
                student_id=input_dto.student_id,
            )

            course.increment_enrollment()
            await uow.courses.save(course)
            await uow.enrollments.save(enrollment)

            events = [
                StudentEnrolled(
                    course_id=input_dto.course_id,
                    student_id=input_dto.student_id,
                )
            ]

            await uow.commit()
            await self._event_publisher.publish_many(events)

            return EnrollStudentOutput(enrollment_id=enrollment.id)
```

---

## Saga Pattern for Multi-Aggregate Operations

### Saga Definition

A saga is a sequence of local transactions where each step publishes events
that trigger the next step. If any step fails, previously executed steps
are compensated (undone).

### Saga Orchestrator

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SagaStepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    name: str
    execute: Callable[..., Awaitable[Any]]
    compensate: Callable[..., Awaitable[None]]
    status: SagaStepStatus = SagaStepStatus.PENDING
    result: Any = None
    error: Exception | None = None


class Saga:
    def __init__(self, name: str) -> None:
        self.name = name
        self.steps: list[SagaStep] = []
        self.context: dict[str, Any] = {}
        self.saga_id: UUID = uuid4()

    def add_step(
        self,
        name: str,
        execute: Callable[..., Awaitable[Any]],
        compensate: Callable[..., Awaitable[None]],
    ) -> "Saga":
        self.steps.append(SagaStep(name=name, execute=execute, compensate=compensate))
        return self

    async def execute(self, logger: LoggingPort) -> SagaResult:
        completed_steps: list[SagaStep] = []

        for step in self.steps:
            try:
                logger.info(
                    f"Saga {self.name}: executing step '{step.name}'",
                    saga_id=str(self.saga_id),
                )
                step.result = await step.execute(self.context)
                step.status = SagaStepStatus.COMPLETED
                self.context[step.name] = step.result
                completed_steps.append(step)

            except Exception as exc:
                step.status = SagaStepStatus.FAILED
                step.error = exc
                logger.error(
                    f"Saga {self.name}: step '{step.name}' failed",
                    saga_id=str(self.saga_id),
                    error=str(exc),
                )

                await self._compensate(completed_steps, logger)

                return SagaResult(
                    success=False,
                    failed_step=step.name,
                    error=exc,
                    context=self.context,
                )

        logger.info(
            f"Saga {self.name}: completed successfully",
            saga_id=str(self.saga_id),
        )
        return SagaResult(success=True, context=self.context)

    async def _compensate(
        self, completed_steps: list[SagaStep], logger: LoggingPort
    ) -> None:
        for step in reversed(completed_steps):
            try:
                logger.info(
                    f"Saga {self.name}: compensating step '{step.name}'",
                    saga_id=str(self.saga_id),
                )
                await step.compensate(self.context)
                step.status = SagaStepStatus.COMPENSATED
            except Exception as exc:
                logger.critical(
                    f"Saga {self.name}: compensation failed for '{step.name}'",
                    saga_id=str(self.saga_id),
                    error=str(exc),
                )
```

### Enrollment Saga Example

```python
async def create_enrollment_saga(
    course_id: UUID,
    student_id: UUID,
    payment_amount: float | None,
) -> Saga:
    saga = Saga("enrollment")

    async def reserve_seat(ctx: dict) -> ReservationResult:
        return await course_service.reserve_seat(course_id)

    async def compensate_reserve(ctx: dict) -> None:
        await course_service.release_seat(course_id)

    async def process_payment(ctx: dict) -> PaymentResult:
        if payment_amount and payment_amount > 0:
            return await payment_service.charge(student_id, payment_amount)
        return PaymentResult(skippped=True)

    async def compensate_payment(ctx: dict) -> None:
        if "process_payment" in ctx and not ctx["process_payment"].skipped:
            await payment_service.refund(ctx["process_payment"].transaction_id)

    async def create_enrollment(ctx: dict) -> EnrollmentResult:
        return await enrollment_service.create(course_id, student_id)

    async def compensate_enrollment(ctx: dict) -> None:
        if "create_enrollment" in ctx:
            await enrollment_service.cancel(ctx["create_enrollment"].enrollment_id)

    async def send_notification(ctx: dict) -> None:
        await notification_service.send_enrollment_confirmation(student_id, course_id)

    saga.add_step("reserve_seat", reserve_seat, compensate_reserve)
    saga.add_step("process_payment", process_payment, compensate_payment)
    saga.add_step("create_enrollment", create_enrollment, compensate_enrollment)
    saga.add_step("send_notification", send_notification, lambda ctx: None)

    return saga
```

---

## Compensation Actions

Each compensation action must be idempotent and must undo the effect of the
corresponding forward action.

### Compensation Patterns

```python
class CompensationRegistry:
    def __init__(self) -> None:
        self._compensations: dict[str, Callable] = {}

    def register(self, action: str, compensation: Callable) -> None:
        self._compensations[action] = compensation

    async def compensate(self, action: str, context: dict) -> None:
        if action in self._compensations:
            await self._compensations[action](context)


# Registration
registry = CompensationRegistry()
registry.register("enroll_student", compensation_unenroll_student)
registry.register("charge_payment", compensation_refund_payment)
registry.register("create_certificate", compensation_revoke_certificate)
registry.register("provision_simulation", compensation_deprovision_simulation)
registry.register("send_email", compensation_send_cancellation_email)
```

### Compensation Types

| Forward Action | Compensation | Notes |
|---|---|---|
| Enroll student | Unenroll student | Refund if paid |
| Charge payment | Refund payment | Idempotent refund |
| Issue certificate | Revoke certificate | With reason |
| Provision sandbox | Deprovision sandbox | Auto-cleanup |
| Publish course | Unpublish course | Notify enrolled |
| Install plugin | Remove plugin | Archive config |

---

## Idempotency Keys

Every command that mutates state can carry an idempotency key. If the same key
is used twice, the second request returns the cached result instead of executing
the command again.

### Idempotency Implementation

```python
import hashlib
import json
from datetime import datetime, timedelta, timezone


@dataclass
class IdempotencyRecord:
    key: str
    request_hash: str
    response_status: int
    response_body: dict
    created_at: datetime
    expires_at: datetime


class IdempotencyService:
    def __init__(
        self,
        repository: IdempotencyRepositoryPort,
        ttl: timedelta = timedelta(hours=24),
    ) -> None:
        self._repository = repository
        self._ttl = ttl

    def generate_key(self, actor_id: UUID, command_type: str, payload: dict) -> str:
        raw = f"{actor_id}:{command_type}:{json.dumps(payload, sort_keys=True)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def check(self, key: str) -> IdempotencyRecord | None:
        record = await self._repository.find_by_key(key)
        if record and record.expires_at > datetime.now(timezone.utc):
            return record
        if record:
            await self._repository.delete(key)
        return None

    async def store(
        self, key: str, payload: dict, status: int, response: dict
    ) -> None:
        request_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()
        now = datetime.now(timezone.utc)
        record = IdempotencyRecord(
            key=key,
            request_hash=request_hash,
            response_status=status,
            response_body=response,
            created_at=now,
            expires_at=now + self._ttl,
        )
        await self._repository.save(record)
```

### Idempotency Middleware

```python
async def idempotency_middleware(request: Request, call_next):
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key or request.method not in ("POST", "PUT", "PATCH"):
        return await call_next(request)

    existing = await idempotency_service.check(idempotency_key)
    if existing:
        return JSONResponse(
            status_code=existing.response_status,
            content=existing.response_body,
            headers={"X-Idempotent-Replay": "true"},
        )

    response = await call_next(request)
    if 200 <= response.status_code < 300:
        body = json.loads(response.body)
        await idempotency_service.store(
            idempotency_key, {}, response.status_code, body
        )

    return response
```

---

## Retry Policies

### Exponential Backoff with Jitter

```python
import random
from typing import TypeVar, Callable, Awaitable

T = TypeVar("T")


async def retry_with_backoff(
    operation: Callable[..., Awaitable[T]],
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception], Awaitable[None]] | None = None,
) -> T:
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return await operation(*args)
        except retryable_exceptions as exc:
            last_exception = exc
            if attempt == max_retries:
                break

            delay = min(base_delay * (backoff_factor ** attempt), max_delay)
            if jitter:
                delay = delay * (0.5 + random.random())

            if on_retry:
                await on_retry(attempt + 1, exc)

            await asyncio.sleep(delay)

    raise RetryExhausted(
        f"All {max_retries} retries exhausted",
        last_exception=last_exception,
    )


class RetryExhausted(Exception):
    def __init__(self, message: str, last_exception: Exception | None) -> None:
        self.last_exception = last_exception
        super().__init__(message)
```

### Retry Policies by Error Type

| Error Type | Max Retries | Base Delay | Backoff | Notes |
|---|---|---|---|---|
| DatabaseError (transient) | 3 | 1s | 2x | Connection timeouts |
| NetworkError | 5 | 0.5s | 2x | External API calls |
| FileSystemError | 2 | 2s | 3x | Disk pressure |
| ServiceUnavailable | 4 | 5s | 2x | Third-party outages |
| RateLimited | 3 | 30s | 1x | Respect Retry-After |
| AuthenticationFailed | 0 | — | — | No retry |
| BusinessRuleViolation | 0 | — | — | No retry |
| ValidationError | 0 | — | — | No retry |

---

## Offline Transaction Queuing

When the application loses connectivity (e.g., Electron desktop app goes offline),
commands are queued locally and replayed when connectivity is restored.

### Offline Queue

```python
from enum import Enum


class QueueStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueuedCommand:
    id: UUID = field(default_factory=uuid4)
    command_type: str = ""
    payload: dict = field(default_factory=dict)
    idempotency_key: str = ""
    status: QueueStatus = QueueStatus.PENDING
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    attempts: int = 0
    max_attempts: int = 5
    last_error: str | None = None
    next_retry_at: datetime | None = None


class OfflineCommandQueue:
    def __init__(self, storage: LocalStoragePort) -> None:
        self._storage = storage

    async def enqueue(self, command_type: str, payload: dict) -> QueuedCommand:
        key = f"{command_type}:{uuid4()}"
        queued = QueuedCommand(
            command_type=command_type,
            payload=payload,
            idempotency_key=key,
        )
        await self._storage.save_queued_command(queued)
        return queued

    async def process_queue(self, dispatcher: CommandDispatcher) -> None:
        pending = await self._storage.get_pending_commands()
        for cmd in pending:
            cmd.status = QueueStatus.PROCESSING
            cmd.attempts += 1
            try:
                await dispatcher.dispatch(cmd.command_type, cmd.payload)
                cmd.status = QueueStatus.COMPLETED
            except Exception as exc:
                cmd.status = QueueStatus.FAILED if cmd.attempts >= cmd.max_attempts else QueueStatus.PENDING
                cmd.last_error = str(exc)
                cmd.next_retry_at = self._calculate_next_retry(cmd.attempts)
            await self._storage.save_queued_command(cmd)

    def _calculate_next_retry(self, attempts: int) -> datetime:
        delay = min(30 * (2 ** (attempts - 1)), 3600)
        return datetime.now(timezone.utc) + timedelta(seconds=delay)
```

---

## Audit Logging Within Transactions

Audit logs are written within the same transaction as the business operation
to ensure consistency between the action and its audit record.

### Audit Within Transaction

```python
class AuditedUnitOfWork(UnitOfWork):
    def __init__(self, session_factory, audit_logger: AuditLoggerPort) -> None:
        super().__init__(session_factory)
        self._audit_logger = audit_logger
        self._audit_entries: list[AuditEntry] = []

    def audit(
        self, actor: str, action: str, resource: str, outcome: str, details: dict | None = None
    ) -> None:
        entry = AuditEntry(
            actor=actor,
            action=action,
            resource=resource,
            outcome=outcome,
            details=details or {},
            timestamp=datetime.now(timezone.utc),
        )
        self._audit_entries.append(entry)

    async def commit(self) -> None:
        for entry in self._audit_entries:
            model = AuditLogMapper.to_model(entry)
            self._session.add(model)
        await super().commit()
        for entry in self._audit_entries:
            await self._audit_logger.log(entry)
```

---

## Consistency Guarantees

### Strong Consistency (Within Single Transaction)

Used when all operations target the same database and must be atomic:

- User creation + default role assignment
- Assessment start + attempt record creation
- Course publication + status change
- Certificate issuance + signature generation

### Eventual Consistency (Cross-Service)

Used when operations span multiple services or include external systems:

- Course enrollment + email notification
- Plugin installation + system configuration update
- Backup creation + metadata update
- Assessment grading + certificate eligibility check

### Eventual Consistency Patterns

```python
class ConsistencyManager:
    async def with_eventual_consistency(
        self,
        primary_operation: Callable[..., Awaitable[Any]],
        side_effects: list[Callable[..., Awaitable[None]]],
        logger: LoggingPort,
    ) -> Any:
        result = await primary_operation()

        for side_effect in side_effects:
            try:
                await side_effect()
            except Exception as exc:
                logger.warning(
                    "Side effect failed, will retry",
                    error=str(exc),
                )
                await self._schedule_retry(side_effect)

        return result
```

---

## Conflict Resolution Strategies

### Last-Write-Wins

```python
class LastWriteWinsResolver:
    def resolve(self, local: Entity, remote: Entity, base: Entity) -> Entity:
        if local.updated_at >= remote.updated_at:
            return local
        return remote
```

### Version-Based Optimistic Locking

```python
class OptimisticLockResolver:
    async def resolve(
        self, entity: Entity, expected_version: int, repo: RepositoryPort
    ) -> Entity:
        current = await repo.find_by_id(entity.id)
        if current.version != expected_version:
            raise ConcurrencyConflict(
                resource=type(entity).__name__,
                version_expected=expected_version,
                version_actual=current.version,
            )
        entity.version = current.version + 1
        entity.updated_at = datetime.now(timezone.utc)
        await repo.save(entity)
        return entity
```

### Three-Way Merge

```python
class ThreeWayMergeResolver:
    def resolve(
        self,
        base: dict,
        local: dict,
        remote: dict,
    ) -> tuple[dict, list[str]]:
        merged = {}
        conflicts = []

        all_keys = set(base.keys()) | set(local.keys()) | set(remote.keys())
        for key in all_keys:
            base_val = base.get(key)
            local_val = local.get(key)
            remote_val = remote.get(key)

            if local_val == remote_val:
                merged[key] = local_val
            elif local_val == base_val:
                merged[key] = remote_val
            elif remote_val == base_val:
                merged[key] = local_val
            else:
                conflicts.append(key)
                merged[key] = local_val

        return merged, conflicts
```
