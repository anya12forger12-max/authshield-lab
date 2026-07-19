# Transaction Management — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Overview

AuthShield Lab uses SQLAlchemy 2.0 async sessions with explicit transaction
management. Since SQLite supports only one writer at a time (with WAL enabling
concurrent readers), transactions are designed to be short-lived and well-scoped.

### 1.1 Transaction Principles

| Principle | Description |
|---|---|
| Short-lived | Transactions should complete within 100ms |
| Explicit boundaries | Every use case defines its own transaction scope |
| Automatic rollback | Unhandled exceptions trigger automatic rollback |
| Idempotent writes | Commands use idempotency keys for safe retries |
| Audit on commit | Audit entries written only on successful commit |

---

## 2. Transaction Scope

### 2.1 Per-Use-Case Transactions

Each API endpoint or use case creates its own transaction:

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def create_enrollment(
    user_id: UUID,
    course_id: UUID,
    session: AsyncSession,
    actor_id: UUID,
) -> Enrollment:
    """Create enrollment with enrollment count update — single transaction."""
    async with session.begin():
        # 1. Validate course exists and is active
        course = await course_repository.get_by_id(course_id)
        if course is None or course.status != "active":
            raise ValidationError("Course not available for enrollment")

        # 2. Check for duplicate enrollment
        existing = await enrollment_repository.get_by_user_and_course(user_id, course_id)
        if existing is not None:
            raise DuplicateEnrollmentError(user_id, course_id)

        # 3. Create enrollment
        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
            status="active",
            enrolled_at=datetime.utcnow(),
        )
        enrollment = await enrollment_repository.create(enrollment, actor_id)

        # 4. Update enrollment count (denormalized)
        await course_repository.increment_enrollment_count(course_id)

        # 5. Send notification
        await notification_service.send(
            user_id=user_id,
            template="enrollment_created",
            context={"course_title": course.title},
        )

        return enrollment
    # session.begin() auto-commits on success, auto-rolls back on exception
```

### 2.2 Per-Aggregate Transactions

Changes within a single aggregate root are atomic:

```python
async def update_course_with_modules(
    course_id: UUID,
    module_data: list[ModuleData],
    session: AsyncSession,
    actor_id: UUID,
) -> Course:
    """Update course and all its modules — single transaction."""
    async with session.begin():
        course = await course_repository.get_by_id(course_id)
        if course is None:
            raise EntityNotFoundError(course_id)

        # Update course
        course.title = module_data.title
        course.description = module_data.description
        await course_repository.update(course, actor_id, module_data.version)

        # Replace modules
        await module_repository.delete_all_for_course(course_id, actor_id)
        for idx, mod_data in enumerate(module_data.modules):
            module = CourseModule(
                course_id=course_id,
                title=mod_data.title,
                description=mod_data.description,
                sort_order=idx,
            )
            await module_repository.create(module, actor_id)

        return course
```

### 2.3 Cross-Aggregate Transactions

When operations span multiple aggregates, use compensation for consistency:

```python
async def complete_assessment(
    attempt_id: UUID,
    answers: list[AnswerData],
    session: AsyncSession,
    actor_id: UUID,
) -> Result:
    """Complete assessment — cross-aggregate with compensation."""
    try:
        async with session.begin():
            # 1. Grade attempt (assessment aggregate)
            attempt = await attempt_repository.get_by_id(attempt_id)
            attempt.status = "submitted"
            attempt.submitted_at = datetime.utcnow()
            await attempt_repository.update(attempt, actor_id, attempt.version)

            # 2. Grade answers (assessment aggregate)
            for answer_data in answers:
                answer = Answer(
                    attempt_id=attempt_id,
                    question_id=answer_data.question_id,
                    selected_option_id=answer_data.selected_option_id,
                    answer_text=answer_data.text,
                )
                await answer_repository.create(answer, actor_id)

            # 3. Create result (assessment aggregate)
            result = grade_attempt(attempt, answers)
            await result_repository.create(result, actor_id)

            # 4. Update progress (learning aggregate)
            await progress_service.update_progress(
                user_id=attempt.user_id,
                assessment_id=attempt.assessment_id,
                passed=result.passed,
                session=session,
            )

            # 5. Issue certificate if course completed (learning aggregate)
            if result.passed:
                course_completed = await enrollment_service.check_completion(
                    attempt.user_id,
                    attempt.course_id,
                    session=session,
                )
                if course_completed:
                    await certificate_service.issue(
                        attempt.user_id,
                        attempt.course_id,
                        session=session,
                    )

            return result

    except Exception:
        # Automatic rollback — all changes undone
        raise
```

---

## 3. Isolation Levels

### 3.1 SQLite Isolation

SQLite in WAL mode supports:

| Isolation Level | Behavior | AuthShield Lab Usage |
|---|---|---|
| **DEFERRED** | Lock acquired on first read | Default for read-only operations |
| **IMMEDIATE** | Lock acquired on statement start | Default for write transactions |
| **EXCLUSIVE** | Full database lock | Only for VACUUM, schema changes |

### 3.2 SQLAlchemy Configuration

```python
# Default: READ COMMITTED equivalent via IMMEDIATE transactions
engine = create_async_engine(
    "sqlite+aiosqlite:///./data/authshield.db",
    isolation_level="AUTOCOMMIT",  # Manual transaction control
)

# Per-transaction isolation
async with session.begin():
    # This transaction uses IMMEDIATE locking
    await session.execute(text("PRAGMA journal_mode = WAL"))
    ...
```

### 3.3 Read Consistency

Since SQLite WAL provides snapshot isolation for reads:

```python
async def get_course_with_stats(course_id: UUID, session: AsyncSession):
    """Read-consistent view of course with statistics."""
    async with session.begin():
        # All reads within this block see a consistent snapshot
        course = await course_repository.get_by_id(course_id, session)
        modules = await module_repository.list_for_course(course_id, session)
        enrollment_count = await enrollment_repository.count_for_course(course_id, session)
        avg_score = await result_repository.average_score_for_course(course_id, session)

        return CourseDetail(
            course=course,
            modules=modules,
            enrollment_count=enrollment_count,
            average_score=avg_score,
        )
```

---

## 4. Retry Strategy

### 4.1 Exponential Backoff

```python
import asyncio
import random

class RetryPolicy:
    """Exponential backoff retry policy for transient failures."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 0.1,
        max_delay: float = 5.0,
        exponential_base: float = 2.0,
        retryable_exceptions: tuple = (SQLAlchemyError, ConnectionError),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions

    async def execute(self, operation, *args, **kwargs):
        """Execute operation with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await operation(*args, **kwargs)

            except self.retryable_exceptions as e:
                last_exception = e

                if attempt == self.max_retries:
                    break

                delay = min(
                    self.base_delay * (self.exponential_base ** attempt)
                    + random.uniform(0, 0.1),
                    self.max_delay,
                )
                logger.warning(
                    f"Retry {attempt + 1}/{self.max_retries} "
                    f"after {delay:.2f}s: {e}"
                )
                await asyncio.sleep(delay)

            except NonRetryableError:
                raise

        raise RetryExhaustedError(last_exception, self.max_retries)


class RetryExhaustedError(Exception):
    """All retry attempts exhausted."""
    def __init__(self, last_exception: Exception, attempts: int):
        self.last_exception = last_exception
        self.attempts = attempts
        super().__init__(
            f"Retry exhausted after {attempts} attempts. "
            f"Last error: {last_exception}"
        )
```

### 4.2 Retryable vs Non-Retryable Errors

| Error Type | Retryable? | Action |
|---|---|---|
| `SQLITE_BUSY` | Yes | Retry with backoff |
| `SQLITE_LOCKED` | Yes | Retry with backoff |
| `SQLITE_CORRUPT` | No | Alert, halt operations |
| `SQLITE_CONSTRAINT` (unique) | No | Return conflict error |
| `IntegrityError` | No | Return validation error |
| `ConnectionError` | Yes | Retry with backoff |
| `TimeoutError` | Yes | Retry with backoff |
| `VersionConflictError` | No | Return conflict to client |
| `EntityNotFoundError` | No | Return 404 |
| Permission error | No | Return 403 |

### 4.3 SQLite-Specific Retries

```python
async def execute_with_sqlite_retry(session: AsyncSession, operation):
    """Execute with SQLite-specific retry handling."""
    max_retries = 3

    for attempt in range(max_retries):
        try:
            async with session.begin():
                return await operation(session)

        except OperationalError as e:
            if "database is locked" in str(e) or "busy" in str(e):
                if attempt < max_retries - 1:
                    delay = 0.1 * (2 ** attempt) + random.uniform(0, 0.05)
                    await asyncio.sleep(delay)
                    continue
            raise

        except Exception:
            raise
```

---

## 5. Rollback Policy

### 5.1 Automatic Rollback

SQLAlchemy sessions automatically rollback on:

```python
# 1. Exception within session.begin() context
async with session.begin():
    raise ValueError("Something went wrong")
# Session auto-rollbacks, no data persisted

# 2. Session.close() without commit
session = async_session_factory()
# ... operations ...
await session.close()  # Auto-rollback if not committed

# 3. Session expiration after transaction end
```

### 5.2 Manual Compensation

For cross-aggregate operations that can't be in one transaction:

```python
class CompensationManager:
    """Manages compensating transactions for multi-step operations."""

    def __init__(self):
        self._compensations: list[Callable] = []

    def register(self, compensation: Callable):
        """Register a compensating action."""
        self._compensations.append(compensation)

    async def execute_with_compensation(self, operations: list[Callable]):
        """Execute operations, rolling back completed steps on failure."""
        completed = []

        for operation in operations:
            try:
                result = await operation()
                completed.append((operation, result))
            except Exception as e:
                # Compensate in reverse order
                for completed_op, _ in reversed(completed):
                    try:
                        comp = self._find_compensation(completed_op)
                        if comp:
                            await comp()
                    except Exception as comp_error:
                        logger.error(f"Compensation failed: {comp_error}")
                raise


# Usage
compensation = CompensationManager()

async def transfer_learning_data(source_user_id, target_user_id):
    """Transfer learning data with compensation."""
    compensation = CompensationManager()

    try:
        # Step 1: Copy enrollments
        enrollments = await copy_enrollments(source_user_id, target_user_id)
        compensation.register(lambda: delete_copied_enrollments(target_user_id))

        # Step 2: Copy progress
        progress = await copy_progress(source_user_id, target_user_id)
        compensation.register(lambda: delete_copied_progress(target_user_id))

        # Step 3: Copy certificates
        certs = await copy_certificates(source_user_id, target_user_id)
        compensation.register(lambda: delete_copied_certificates(target_user_id))

    except Exception:
        await compensation.compensate_all()
        raise
```

### 5.3 Savepoints (Nested Transactions)

```python
async def complex_operation(session: AsyncSession):
    """Use savepoints for partial rollback within a transaction."""
    async with session.begin():
        # Main transaction
        user = await create_user(session)

        try:
            async with session.begin_nested():
                # Savepoint — can rollback independently
                await assign_roles(session, user.id)
                await create_enrollment(session, user.id)
        except Exception:
            # Savepoint rolled back, main transaction continues
            logger.warning("Role assignment failed, continuing without roles")

        # This still commits
        await send_welcome_notification(session, user.id)
```

---

## 6. Consistency Guarantees

### 6.1 Strong Consistency (Within Aggregate)

```python
# Single-aggregate operations are strongly consistent
async def update_user_profile(user_id, profile_data, session):
    async with session.begin():
        user = await user_repo.get_by_id(user_id)
        user.display_name = profile_data.display_name
        user.avatar_url = profile_data.avatar_url
        await user_repo.update(user, actor_id=user_id, expected_version=profile_data.version)
        # Guaranteed: user profile is atomically updated
```

### 6.2 Eventual Consistency (Cross-Aggregate)

```python
# Cross-aggregate operations use eventual consistency
async def enroll_and_notify(user_id, course_id, session):
    # Enrollment is committed
    async with session.begin():
        enrollment = await create_enrollment(user_id, course_id)

    # Notification is eventual — may arrive slightly later
    await notification_service.send_async(
        user_id=user_id,
        template="enrollment_welcome",
        data={"course_id": course_id},
    )
    # Consistency: enrollment is guaranteed, notification is best-effort
```

### 6.3 Consistency Patterns

| Pattern | Scope | Guarantee |
|---|---|---|
| Synchronous write | Single aggregate | Strong |
| Synchronous read | Within snapshot | Consistent |
| Eventual notification | Cross-aggregate | Best-effort |
| Denormalized counters | Cross-aggregate | Eventual |
| Audit entries | Separate database | Eventual |
| Cache invalidation | Application layer | Eventual |

---

## 7. Concurrency Control

### 7.1 Optimistic Locking

Every entity uses a `version` column for optimistic concurrency:

```python
async def update_course(course_data, session, actor_id):
    """Optimistic locking prevents lost updates."""
    async with session.begin():
        # Read current state
        current = await course_repo.get_by_id(course_data.id)

        # Check version matches what client expects
        if current.version != course_data.expected_version:
            raise VersionConflictError(
                entity_id=course_data.id,
                expected_version=course_data.expected_version,
                actual_version=current.version,
            )

        # Apply update with version increment
        current.title = course_data.title
        current.version += 1
        current.updated_at = datetime.utcnow()
        current.updated_by = actor_id

        # SQL: UPDATE ... WHERE id = ? AND version = ?
        rows = await session.execute(
            update(Course)
            .where(Course.id == course_data.id)
            .where(Course.version == course_data.expected_version)
            .values(
                title=course_data.title,
                version=course_data.expected_version + 1,
                updated_at=datetime.utcnow(),
                updated_by=actor_id,
            )
        )

        if rows.rowcount == 0:
            raise VersionConflictError(
                course_data.id,
                course_data.expected_version,
                course_data.expected_version + 1,
            )
```

### 7.2 Client Response on Conflict

```python
# API returns version conflict with current state
{
    "error": "version_conflict",
    "message": "Entity was modified by another operation",
    "current_version": 5,
    "your_version": 3,
    "current_state": {
        "id": "...",
        "title": "Updated by someone else",
        "version": 5
    }
}
```

---

## 8. Conflict Resolution

### 8.1 Resolution Strategies

| Strategy | Use Case | Implementation |
|---|---|---|
| **Last-Write-Wins** | Low-collision data | Compare `updated_at` timestamps |
| **Version Check** | All entities | Reject if version mismatch |
| **Manual Merge** | Conflicting edits | Present both versions to user |
| **Auto-Merge** | Non-overlapping fields | Merge non-conflicting changes |
| **Field-Level Locking** | Specific fields | Lock individual fields during edit |

### 8.2 Last-Write-Wins Implementation

```python
async def lww_merge(
    local: Entity,
    remote: Entity,
    server: Entity,
) -> Entity:
    """Last-write-wins merge for three-way comparison."""
    if server.version >= local.version and server.version >= remote.version:
        return server  # Server is most recent
    elif local.version >= remote.version:
        return local   # Local is more recent
    else:
        return remote  # Remote is more recent


async def field_level_merge(
    local: dict,
    remote: dict,
    server: dict,
    conflict_fields: list[str],
) -> dict:
    """Merge non-conflicting fields, flag conflicts."""
    merged = {}

    for field in set(list(local.keys()) + list(remote.keys())):
        if field in conflict_fields:
            if local.get(field) != remote.get(field):
                # Actual conflict — needs manual resolution
                merged[field] = {
                    "status": "conflict",
                    "local": local.get(field),
                    "remote": remote.get(field),
                    "server": server.get(field),
                }
            else:
                merged[field] = local.get(field)
        else:
            # Non-conflicting: use most recent
            merged[field] = local.get(field) or remote.get(field)

    return merged
```

### 8.3 Conflict Resolution for Offline Sync

```python
class OfflineConflictResolver:
    """Resolves conflicts between offline queue and server state."""

    STRATEGIES = {
        "users": "version_check",
        "courses": "manual_merge",
        "enrollments": "last_write_wins",
        "progress": "auto_merge_fields",
        "notifications": "server_wins",
        "audit_entries": "append_only",
        "settings": "last_write_wins",
    }

    async def resolve(
        self,
        entity_type: str,
        local_version: dict,
        server_version: dict,
    ) -> dict:
        """Resolve conflict based on entity type strategy."""
        strategy = self.STRATEGIES.get(entity_type, "version_check")

        if strategy == "version_check":
            raise VersionConflictError(
                local_version["id"],
                local_version["version"],
                server_version["version"],
            )

        elif strategy == "last_write_wins":
            if local_version["updated_at"] > server_version["updated_at"]:
                return local_version
            return server_version

        elif strategy == "server_wins":
            return server_version

        elif strategy == "auto_merge_fields":
            return await self.auto_merge(entity_type, local_version, server_version)

        elif strategy == "manual_merge":
            return await self.flag_for_manual_merge(
                entity_type, local_version, server_version
            )
```

---

## 9. Idempotency

### 9.1 Idempotency Keys

Every command includes a client-generated idempotency key:

```python
class IdempotencyManager:
    """Ensures operations are safe to retry."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_and_store(
        self,
        key: str,
        operation_type: str,
    ) -> Optional[dict]:
        """Check if operation already executed. Return result if cached."""
        query = select(IdempotencyRecord).where(
            IdempotencyRecord.key == key,
            IdempotencyRecord.expires_at > datetime.utcnow(),
        )
        result = await self.session.execute(query)
        record = result.scalar_one_or_none()

        if record:
            return json.loads(record.result_json)
        return None

    async def store(
        self,
        key: str,
        operation_type: str,
        result: dict,
        ttl_hours: int = 24,
    ):
        """Store operation result for idempotency check."""
        record = IdempotencyRecord(
            key=key,
            operation_type=operation_type,
            result_json=json.dumps(result),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=ttl_hours),
        )
        self.session.add(record)
```

### 9.2 Idempotent API Endpoints

```python
@router.post("/enrollments")
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_session),
):
    """Create enrollment — safe to retry with same idempotency key."""
    idempotency = IdempotencyManager(session)

    # Check if already processed
    existing = await idempotency.check_and_store(idempotency_key, "enrollment.create")
    if existing:
        return EnrollmentResponse(**existing)

    # Process enrollment
    enrollment = await enrollment_service.create(
        user_id=enrollment_data.user_id,
        course_id=enrollment_data.course_id,
        session=session,
    )

    # Store result
    result = enrollment.to_dict()
    await idempotency.store(idempotency_key, "enrollment.create", result)

    return EnrollmentResponse(**result)
```

### 9.3 Idempotency Record Schema

```sql
CREATE TABLE idempotency_records (
    id BLOB(16) PRIMARY KEY,
    key VARCHAR(255) NOT NULL UNIQUE,
    operation_type VARCHAR(100) NOT NULL,
    result_json TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL
);

CREATE INDEX idx_idempotency_key ON idempotency_records(key);
CREATE INDEX idx_idempotency_expires ON idempotency_records(expires_at);
```

---

## 10. Offline Transaction Queue

### 10.1 Operation Log

For future offline-first scenarios, a local operation log tracks pending changes:

```sql
CREATE TABLE offline_operation_queue (
    id BLOB(16) PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,  -- create, update, delete
    entity_type VARCHAR(100) NOT NULL,
    entity_id BLOB(16) NOT NULL,
    payload TEXT NOT NULL,               -- JSON serialized entity data
    idempotency_key VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, processing, completed, failed
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    last_error TEXT,
    last_attempt_at DATETIME,
    completed_at DATETIME
);

CREATE INDEX idx_oq_status ON offline_operation_queue(status);
CREATE INDEX idx_oq_created ON offline_operation_queue(created_at);
CREATE INDEX idx_oq_entity ON offline_operation_queue(entity_type, entity_id);
```

### 10.2 Queue Processing

```python
class OfflineQueueProcessor:
    """Processes offline operations when connectivity is restored."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.retry_policy = RetryPolicy(max_retries=3)

    async def process_pending(self) -> ProcessingResult:
        """Process all pending operations in FIFO order."""
        result = ProcessingResult()

        pending = await self._get_pending_operations()

        for operation in pending:
            try:
                await self._process_operation(operation)
                result.succeeded.append(operation.id)
            except NonRetryableError as e:
                await self._mark_failed(operation, str(e))
                result.failed.append((operation.id, str(e)))
            except Exception as e:
                if operation.retry_count >= operation.max_retries:
                    await self._mark_failed(operation, str(e))
                    result.failed.append((operation.id, str(e)))
                else:
                    await self._increment_retry(operation)

        return result

    async def _process_operation(self, operation: OfflineOperation):
        """Process a single operation."""
        handler = self._get_handler(operation.operation_type, operation.entity_type)
        await handler(operation.payload)

        await self.session.execute(
            update(OfflineOperationQueue)
            .where(OfflineOperationQueue.id == operation.id)
            .values(
                status="completed",
                completed_at=datetime.utcnow(),
            )
        )
```

---

## 11. Unit of Work Pattern

### 11.1 Implementation

```python
class UnitOfWork:
    """Manages transaction boundaries and coordinates repositories."""

    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self):
        self._session = self._session_factory()

        # Initialize repositories with shared session
        self.users = UserRepository(self._session)
        self.courses = CourseRepository(self._session)
        self.enrollments = EnrollmentRepository(self._session)
        self.assessments = AssessmentRepository(self._session)
        self.audit = AuditRepository(self._session)
        self.notifications = NotificationRepository(self._session)
        self.config = ConfigurationRepository(self._session)
        self.plugins = PluginRepository(self._session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self._session.close()

    async def commit(self):
        """Commit all changes in the unit of work."""
        await self._session.commit()

    async def rollback(self):
        """Rollback all changes."""
        await self._session.rollback()

    async def flush(self):
        """Flush changes to database without committing."""
        await self._session.flush()
```

### 11.2 Usage Pattern

```python
async def enroll_user_in_course(
    user_id: UUID,
    course_id: UUID,
    uow: UnitOfWork,
    actor_id: UUID,
) -> Enrollment:
    """Use case: enroll user in course."""
    async with uow:
        # All operations share the same session/transaction

        # Validate
        course = await uow.courses.get_by_id(course_id)
        if course is None:
            raise EntityNotFoundError(course_id)

        existing = await uow.enrollments.get_by_user_and_course(user_id, course_id)
        if existing:
            raise DuplicateEnrollmentError(user_id, course_id)

        # Create enrollment
        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
            status="active",
        )
        enrollment = await uow.enrollments.create(enrollment, actor_id)

        # Update course enrollment count
        course.enrollment_count += 1
        await uow.courses.update(course, actor_id, course.version)

        # Create notification
        notification = Notification(
            user_id=user_id,
            title="Course Enrollment",
            body=f"You have been enrolled in {course.title}",
            notification_type="info",
        )
        await uow.notifications.create(notification)

        # Audit
        await uow.audit.create_entry(
            user_id=actor_id,
            action="enrollment.create",
            entity_type="enrollment",
            entity_id=enrollment.id,
        )

        # Auto-commit on exit (no exception)
        return enrollment
```

### 11.3 Unit of Work Factory

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_uow():
    """Factory for creating unit of work instances."""
    async with async_session_factory() as session:
        async with UnitOfWork(lambda: session) as uow:
            yield uow

# FastAPI dependency
async def get_unit_of_work() -> UnitOfWork:
    """FastAPI dependency for unit of work."""
    async with get_uow() as uow:
        yield uow
```

---

## 12. Transaction Monitoring

### 12.1 Performance Metrics

```python
class TransactionMetrics:
    """Track transaction performance."""

    def __init__(self):
        self.transaction_count = 0
        self.total_duration_ms = 0.0
        self.slow_transactions = []

    async def track(self, name: str, operation):
        """Track operation execution time."""
        start = time.monotonic()
        try:
            result = await operation()
            duration_ms = (time.monotonic() - start) * 1000

            self.transaction_count += 1
            self.total_duration_ms += duration_ms

            if duration_ms > 100:  # Slow threshold: 100ms
                self.slow_transactions.append({
                    "name": name,
                    "duration_ms": round(duration_ms, 2),
                    "timestamp": datetime.utcnow().isoformat(),
                })

            logger.info(f"Transaction {name}: {duration_ms:.2f}ms")
            return result

        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000
            logger.error(f"Transaction {name} failed after {duration_ms:.2f}ms: {e}")
            raise

    @property
    def average_duration_ms(self) -> float:
        if self.transaction_count == 0:
            return 0.0
        return self.total_duration_ms / self.transaction_count
```

### 12.2 Deadlock Detection

SQLite doesn't have traditional deadlocks (single-writer), but WAL mode can
produce SQLITE_BUSY errors under high concurrency:

```python
class ConcurrencyMonitor:
    """Monitor and handle SQLite concurrency issues."""

    def __init__(self):
        self.busy_count = 0
        self.lock_wait_time_ms = 0.0

    async def on_sqlite_busy(self, wait_time_ms: float):
        """Called when SQLITE_BUSY is encountered."""
        self.busy_count += 1
        self.lock_wait_time_ms += wait_time_ms

        if self.busy_count > 100:
            logger.warning(
                f"High SQLITE_BUSY count: {self.busy_count}. "
                f"Consider increasing busy_timeout."
            )

    def get_metrics(self) -> dict:
        return {
            "busy_count": self.busy_count,
            "total_lock_wait_ms": round(self.lock_wait_time_ms, 2),
            "average_lock_wait_ms": round(
                self.lock_wait_time_ms / max(1, self.busy_count), 2
            ),
        }
```

---

*This document defines the complete transaction management strategy for AuthShield Lab.*
