# Offline Data Architecture — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Overview

AuthShield Lab is designed as an offline-first, localhost-only application.
All data lives on the user's machine in SQLite. This document defines the
architecture for local-first storage, operation queuing, conflict detection,
integrity verification, recovery, and storage optimization.

### 1.1 Core Principles

| Principle | Description |
|---|---|
| Local-first | SQLite is the single source of truth |
| Always available | Full functionality without network |
| No cloud dependency | No external services required |
| Crash-safe | WAL mode ensures crash recovery |
| Data integrity | Checksums and hash chains throughout |
| Future sync-ready | Architecture supports future multi-device sync |

---

## 2. Local-First Storage Architecture

### 2.1 Storage Layout

```
~/.local/share/authshield/
├── data/
│   ├── authshield.db            # Main database (SQLCipher encrypted)
│   ├── authshield.db-wal        # Write-ahead log
│   ├── authshield.db-shm        # Shared memory file
│   ├── authshield_audit.db      # Audit database (separate, encrypted)
│   ├── authshield_audit.db-wal
│   ├── authshield_audit.db-shm
│   ├── authshield_cache.db      # Query cache
│   └── authshield_fts.db        # Full-text search indexes
├── backups/
│   ├── full/
│   │   ├── authshield_full_2026-07-19_03-00-00.db.gz.enc
│   │   └── authshield_full_2026-07-12_03-00-00.db.gz.enc
│   ├── incremental/
│   │   ├── authshield_incr_2026-07-20_03-00-00.db.wal.enc
│   │   └── ...
│   └── metadata/
│       └── backup_manifest.json
├── uploads/
│   ├── course_assets/
│   ├── user_uploads/
│   └── plugin_packages/
├── exports/
│   ├── courses/
│   ├── reports/
│   └── audit/
├── logs/
│   ├── application.log
│   ├── error.log
│   └── performance.log
├── config/
│   ├── settings.json
│   └── feature_flags.json
└── queue/
    ├── operations.db             # Offline operation queue
    └── operations.db-wal
```

### 2.2 Database File Management

```python
class DatabaseManager:
    """Manages SQLite database files and lifecycle."""

    DATABASES = {
        "main": "authshield.db",
        "audit": "authshield_audit.db",
        "cache": "authshield_cache.db",
        "fts": "authshield_fts.db",
        "queue": "operations.db",
    }

    async def initialize(self):
        """Initialize all database files with proper pragmas."""
        for name, filename in self.DATABASES.items():
            db_path = self.data_dir / filename
            await self._initialize_database(db_path, name)

    async def _initialize_database(self, path: Path, purpose: str):
        """Apply purpose-specific pragmas."""
        engine = create_async_engine(f"sqlite+aiosqlite:///{path}")

        async with engine.begin() as conn:
            if purpose == "main":
                await conn.execute(text("PRAGMA journal_mode = WAL"))
                await conn.execute(text("PRAGMA foreign_keys = ON"))
                await conn.execute(text("PRAGMA busy_timeout = 5000"))
                await conn.execute(text("PRAGMA cache_size = -64000"))
                await conn.execute(text("PRAGMA synchronous = NORMAL"))
                await conn.execute(text("PRAGMA mmap_size = 268435456"))

            elif purpose == "audit":
                await conn.execute(text("PRAGMA journal_mode = WAL"))
                await conn.execute(text("PRAGMA foreign_keys = ON"))
                await conn.execute(text("PRAGMA secure_delete = ON"))
                await conn.execute(text("PRAGMA synchronous = FULL"))

            elif purpose == "cache":
                await conn.execute(text("PRAGMA journal_mode = WAL"))
                await conn.execute(text("PRAGMA synchronous = OFF"))
                await conn.execute(text("PRAGMA cache_size = -32000"))

            elif purpose == "queue":
                await conn.execute(text("PRAGMA journal_mode = WAL"))
                await conn.execute(text("PRAGMA busy_timeout = 10000"))

        await engine.dispose()
```

---

## 3. Operation Queue System

### 3.1 Operation Log Schema

```sql
CREATE TABLE operation_queue (
    id BLOB(16) PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id BLOB(16) NOT NULL,
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    payload TEXT NOT NULL,
    metadata TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    scheduled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    last_error TEXT,
    checksum VARCHAR(64) NOT NULL
);

CREATE INDEX idx_oq_status_priority
    ON operation_queue(status, priority DESC, created_at ASC);

CREATE INDEX idx_oq_entity
    ON operation_queue(entity_type, entity_id);

CREATE INDEX idx_oq_idempotency
    ON operation_queue(idempotency_key);

CREATE INDEX idx_oq_created
    ON operation_queue(created_at);
```

### 3.2 Operation Types

| Type | Description | Reversible | Priority |
|---|---|---|---|
| `create` | Create new entity | Yes (soft-delete) | Normal |
| `update` | Update existing entity | Yes (version restore) | Normal |
| `delete` | Soft-delete entity | Yes (restore) | Normal |
| `bulk_create` | Create multiple entities | Yes | Low |
| `bulk_update` | Update multiple entities | Yes | Low |
| `config_change` | System configuration change | Yes | High |
| `enrollment` | Course enrollment | No | Normal |
| `assessment_submit` | Assessment submission | No | High |
| `certificate_issue` | Certificate issuance | No | High |

### 3.3 Queue Processor

```python
class OperationQueueManager:
    """Manages the offline operation queue."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def enqueue(
        self,
        operation_type: str,
        entity_type: str,
        entity_id: UUID,
        payload: dict,
        idempotency_key: str,
        priority: int = 0,
        scheduled_at: Optional[datetime] = None,
    ) -> OperationRecord:
        """Add operation to the queue."""
        record = OperationQueue(
            id=uuid.uuid4(),
            operation_type=operation_type,
            entity_type=entity_type,
            entity_id=entity_id,
            idempotency_key=idempotency_key,
            payload=json.dumps(payload),
            metadata=json.dumps({
                "user_agent": get_user_agent(),
                "timestamp": datetime.utcnow().isoformat(),
            }),
            status="pending",
            priority=priority,
            scheduled_at=scheduled_at or datetime.utcnow(),
            checksum=self._compute_checksum(payload),
        )

        self.session.add(record)
        await self.session.flush()
        return record

    async def dequeue(
        self,
        batch_size: int = 10,
    ) -> list[OperationRecord]:
        """Get next batch of pending operations."""
        query = (
            select(OperationQueue)
            .where(OperationQueue.status == "pending")
            .where(OperationQueue.scheduled_at <= datetime.utcnow())
            .where(OperationQueue.retry_count < OperationQueue.max_retries)
            .order_by(
                OperationQueue.priority.desc(),
                OperationQueue.created_at.asc(),
            )
            .limit(batch_size)
            .with_for_update()  # Lock rows for processing
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def mark_processing(self, record_id: UUID):
        """Mark operation as being processed."""
        await self.session.execute(
            update(OperationQueue)
            .where(OperationQueue.id == record_id)
            .values(
                status="processing",
                last_attempt_at=datetime.utcnow(),
            )
        )

    async def mark_completed(self, record_id: UUID):
        """Mark operation as completed."""
        await self.session.execute(
            update(OperationQueue)
            .where(OperationQueue.id == record_id)
            .values(
                status="completed",
                processed_at=datetime.utcnow(),
            )
        )

    async def mark_failed(self, record_id: UUID, error: str):
        """Mark operation as failed, increment retry count."""
        await self.session.execute(
            update(OperationQueue)
            .where(OperationQueue.id == record_id)
            .values(
                retry_count=OperationQueue.retry_count + 1,
                last_error=error,
                status=Case(
                    (
                        OperationQueue.retry_count >= OperationQueue.max_retries - 1,
                        "failed",
                    ),
                    else_="pending",
                ),
            )
        )

    async def retry_failed(self, record_id: UUID):
        """Reset a failed operation for retry."""
        await self.session.execute(
            update(OperationQueue)
            .where(OperationQueue.id == record_id)
            .values(
                status="pending",
                retry_count=0,
                last_error=None,
                scheduled_at=datetime.utcnow(),
            )
        )

    async def cleanup_completed(self, older_than_days: int = 30):
        """Remove completed operations older than threshold."""
        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        await self.session.execute(
            delete(OperationQueue)
            .where(OperationQueue.status == "completed")
            .where(OperationQueue.processed_at < cutoff)
        )

    def _compute_checksum(self, payload: dict) -> str:
        """Compute SHA-256 checksum of operation payload."""
        import hashlib
        data = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()
```

---

## 4. Conflict Detection

### 4.1 Version Comparison

```python
class ConflictDetector:
    """Detects conflicts between local and remote (future) state."""

    async def check_version_conflict(
        self,
        entity_type: str,
        entity_id: UUID,
        local_version: int,
        session: AsyncSession,
    ) -> ConflictResult:
        """Check if entity has been modified since local version."""
        model = get_model(entity_type)
        query = select(model).where(model.id == entity_id)
        result = await session.execute(query)
        current = result.scalar_one_or_none()

        if current is None:
            return ConflictResult(status="entity_missing")

        if current.version == local_version:
            return ConflictResult(status="no_conflict")

        return ConflictResult(
            status="conflict",
            local_version=local_version,
            remote_version=current.version,
            current_entity=current,
        )

    async def detect_all_conflicts(
        self,
        pending_operations: list[OperationRecord],
        session: AsyncSession,
    ) -> list[ConflictResult]:
        """Batch conflict detection for all pending operations."""
        conflicts = []

        for op in pending_operations:
            if op.operation_type in ("update", "delete"):
                payload = json.loads(op.payload)
                local_version = payload.get("expected_version", 1)

                result = await self.check_version_conflict(
                    op.entity_type,
                    op.entity_id,
                    local_version,
                    session,
                )

                if result.status == "conflict":
                    conflicts.append(result)

        return conflicts
```

### 4.2 Timestamp Comparison

```python
class TimestampConflictDetector:
    """Detects conflicts using timestamps (for future sync)."""

    def __init__(self, clock_skew_tolerance_ms: int = 5000):
        self.clock_skew_tolerance = timedelta(milliseconds=clock_skew_tolerance_ms)

    def detect(
        self,
        local_entity: dict,
        remote_entity: dict,
    ) -> Optional[ConflictInfo]:
        """Detect conflict between local and remote versions."""
        local_updated = datetime.fromisoformat(local_entity["updated_at"])
        remote_updated = datetime.fromisoformat(remote_entity["updated_at"])

        # Check for clock skew
        time_diff = abs((local_updated - remote_updated).total_seconds() * 1000)

        if time_diff < self.clock_skew_tolerance.total_seconds() * 1000:
            # Within tolerance — use version number
            if local_entity["version"] != remote_entity["version"]:
                return ConflictInfo(
                    type="version_mismatch",
                    local=local_entity,
                    remote=remote_entity,
                )
        else:
            # Different timestamps — last-write-wins
            return ConflictInfo(
                type="timestamp_conflict",
                local=local_entity,
                remote=remote_entity,
                newer="local" if local_updated > remote_updated else "remote",
            )

        return None
```

### 4.3 Conflict Types

| Type | Detection | Resolution |
|---|---|---|
| Version mismatch | `local.version != server.version` | Reject, require client refresh |
| Timestamp conflict | Different `updated_at` values | Last-write-wins or manual merge |
| Entity deleted | Entity not found on server | Handle gracefully |
| Entity created | Duplicate unique constraint | Update existing or reject |
| Reference broken | FK points to deleted entity | Cascade or reject |

---

## 5. Conflict Resolution Strategies

### 5.1 Auto-Resolve

```python
class AutoConflictResolver:
    """Automatically resolves non-destructive conflicts."""

    RESOLUTION_RULES = {
        "progress": "max_percentage",      # Take highest progress
        "notifications": "server_wins",     # Server notifications preferred
        "settings": "merge_fields",         # Merge non-overlapping settings
        "enrollments": "server_wins",       # Server enrollment state preferred
        "competencies": "max_level",        # Take highest competency level
        "configurations": "server_wins",    # Server config preferred
    }

    async def resolve(
        self,
        entity_type: str,
        local: dict,
        remote: dict,
    ) -> dict:
        """Auto-resolve conflict based on entity type rules."""
        rule = self.RESOLUTION_RULES.get(entity_type, "manual_merge")

        if rule == "server_wins":
            return remote

        elif rule == "client_wins":
            return local

        elif rule == "max_percentage":
            return self._merge_by_max(local, remote, "percentage")

        elif rule == "max_level":
            return self._merge_by_max(local, remote, "level_order")

        elif rule == "merge_fields":
            return self._merge_fields(local, remote)

        elif rule == "manual_merge":
            return await self._flag_for_manual_merge(entity_type, local, remote)

        return remote  # Default: server wins

    def _merge_fields(self, local: dict, remote: dict) -> dict:
        """Merge non-overlapping fields, keep higher version for conflicts."""
        merged = {}
        all_keys = set(list(local.keys()) + list(remote.keys()))

        for key in all_keys:
            if key in ("id", "created_at", "created_by"):
                merged[key] = local[key]  # Identity fields from local
            elif local.get(key) == remote.get(key):
                merged[key] = local[key]  # Same value — no conflict
            elif key in local and key not in remote:
                merged[key] = local[key]  # Local only
            elif key in remote and key not in local:
                merged[key] = remote[key]  # Remote only
            else:
                # Both have different values — use higher version
                merged[key] = remote.get(key, local.get(key))

        # Use higher version number
        merged["version"] = max(
            local.get("version", 0),
            remote.get("version", 0),
        ) + 1
        merged["updated_at"] = datetime.utcnow().isoformat()

        return merged
```

### 5.2 Manual Merge

```python
class ManualMergeManager:
    """Manages conflicts requiring user intervention."""

    async def create_merge_request(
        self,
        entity_type: str,
        entity_id: UUID,
        local_version: dict,
        remote_version: dict,
    ) -> MergeRequest:
        """Create a merge request for manual resolution."""
        request = MergeRequest(
            id=uuid.uuid4(),
            entity_type=entity_type,
            entity_id=entity_id,
            local_version=local_version,
            remote_version=remote_version,
            status="pending",
            created_at=datetime.utcnow(),
        )

        await self.session.add(request)
        await self.session.flush()

        # Notify user
        await self.notification_service.send(
            title="Data Conflict Detected",
            body=f"A conflict was detected in {entity_type}. Manual merge required.",
            notification_type="warning",
            category="conflict",
        )

        return request

    async def resolve_merge(
        self,
        request_id: UUID,
        merged_data: dict,
        actor_id: UUID,
    ) -> dict:
        """Apply manually merged data."""
        request = await self.session.get(MergeRequest, request_id)
        if request is None:
            raise EntityNotFoundError(request_id)

        # Validate merged data
        await self._validate_merged_data(request.entity_type, merged_data)

        # Apply merged data
        model = get_model(request.entity_type)
        await self.session.execute(
            update(model)
            .where(model.id == request.entity_id)
            .values(**merged_data)
        )

        # Mark request as resolved
        request.status = "resolved"
        request.resolved_by = actor_id
        request.resolved_at = datetime.utcnow()
        request.resolved_data = json.dumps(merged_data)

        return merged_data
```

### 5.3 Last-Write-Wins

```python
class LastWriteWinsResolver:
    """Simple LWW conflict resolution."""

    def resolve(self, local: dict, remote: dict) -> dict:
        """Return the entity with the most recent updated_at."""
        local_time = datetime.fromisoformat(local.get("updated_at", "2000-01-01"))
        remote_time = datetime.fromisoformat(remote.get("updated_at", "2000-01-01"))

        if local_time >= remote_time:
            return local
        return remote
```

---

## 6. Integrity Verification

### 6.1 Checksum Computation

```python
import hashlib

class IntegrityChecker:
    """Verifies data integrity using checksums."""

    @staticmethod
    def compute_row_checksum(row: dict) -> str:
        """Compute SHA-256 checksum for a database row."""
        # Sort keys for deterministic output
        data = json.dumps(row, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def verify_row_checksum(row: dict, expected_checksum: str) -> bool:
        """Verify a row's checksum."""
        actual = IntegrityChecker.compute_row_checksum(row)
        return actual == expected_checksum

    @staticmethod
    def compute_file_checksum(file_path: Path) -> str:
        """Compute SHA-256 checksum for a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def verify_file_checksum(file_path: Path, expected: str) -> bool:
        """Verify file integrity."""
        actual = IntegrityChecker.compute_file_checksum(file_path)
        return actual == expected
```

### 6.2 Foreign Key Validation

```python
class ReferentialIntegrityChecker:
    """Validates foreign key relationships."""

    FK_DEFINITIONS = {
        ("enrollments", "user_id"): "users",
        ("enrollments", "course_id"): "courses",
        ("progress", "user_id"): "users",
        ("progress", "lesson_id"): "lessons",
        ("progress", "course_id"): "courses",
        ("attempts", "user_id"): "users",
        ("attempts", "assessment_id"): "assessments",
        ("answers", "attempt_id"): "attempts",
        ("answers", "question_id"): "questions",
        ("results", "attempt_id"): "attempts",
        ("results", "user_id"): "users",
        ("results", "assessment_id"): "assessments",
        ("certificates", "user_id"): "users",
        ("certificates", "course_id"): "courses",
        ("notifications", "user_id"): "users",
        ("audit_entries", "user_id"): "users",
        ("course_modules", "course_id"): "courses",
        ("lessons", "module_id"): "course_modules",
        ("questions", "assessment_id"): "assessments",
        ("question_options", "question_id"): "questions",
    }

    async def check_all(self, session: AsyncSession) -> list[IntegrityViolation]:
        """Check all foreign key relationships."""
        violations = []

        for (child_table, fk_column), parent_table in self.FK_DEFINITIONS.items():
            child_violations = await self._check_fk(
                session, child_table, fk_column, parent_table
            )
            violations.extend(child_violations)

        return violations

    async def _check_fk(
        self,
        session: AsyncSession,
        child_table: str,
        fk_column: str,
        parent_table: str,
    ) -> list[IntegrityViolation]:
        """Check foreign key for a specific relationship."""
        query = text(f"""
            SELECT c.id, c.{fk_column}
            FROM {child_table} c
            LEFT JOIN {parent_table} p ON c.{fk_column} = p.id
            WHERE p.id IS NULL
            AND c.is_deleted = 0
            AND c.{fk_column} IS NOT NULL
        """)

        result = await session.execute(query)
        violations = []

        for row in result:
            violations.append(IntegrityViolation(
                table=child_table,
                column=fk_column,
                row_id=row[0],
                foreign_value=row[1],
                expected_table=parent_table,
            ))

        return violations
```

### 6.3 Hash Chain Verification (Audit)

```python
class AuditChainVerifier:
    """Verifies audit log hash chain integrity."""

    async def verify_chain(
        self,
        session: AsyncSession,
        start_id: Optional[UUID] = None,
    ) -> ChainVerificationResult:
        """Verify the complete audit hash chain."""
        query = (
            select(AuditEntry)
            .where(AuditEntry.is_deleted == False)
            .order_by(AuditEntry.timestamp.asc(), AuditEntry.id.asc())
        )

        if start_id:
            query = query.where(AuditEntry.id > start_id)

        result = await session.execute(query)
        entries = list(result.scalars().all())

        if not entries:
            return ChainVerificationResult(
                status="valid",
                entries_checked=0,
            )

        previous_hash = None
        broken_at = None

        for entry in entries:
            # Verify chain link
            if entry.previous_hash != previous_hash:
                broken_at = entry
                break

            # Verify entry hash
            expected_hash = self._compute_hash(entry, previous_hash)
            if entry.entry_hash != expected_hash:
                broken_at = entry
                break

            previous_hash = entry.entry_hash

        if broken_at:
            return ChainVerificationResult(
                status="broken",
                entries_checked=entries.index(broken_at) + 1,
                broken_entry_id=broken_at.id,
                expected_hash=previous_hash,
                actual_hash=broken_at.entry_hash,
            )

        return ChainVerificationResult(
            status="valid",
            entries_checked=len(entries),
            chain_start=entries[0].id,
            chain_end=entries[-1].id,
        )

    def _compute_hash(self, entry: AuditEntry, previous_hash: Optional[str]) -> str:
        """Compute expected hash for an audit entry."""
        data = f"{entry.id}{entry.timestamp}{entry.user_id}{entry.action}"
        data += f"{entry.entity_type}{entry.entity_id}{previous_hash or ''}"
        return hashlib.sha256(data.encode()).hexdigest()
```

---

## 7. Safe Recovery

### 7.1 WAL Replay

```python
class WALRecovery:
    """Recover from WAL (Write-Ahead Log) after crash."""

    async def recover(self, db_path: Path) -> RecoveryResult:
        """Replay WAL to recover consistent state."""
        wal_path = db_path.with_suffix(".db-wal")
        shm_path = db_path.with_suffix(".db-shm")

        if not wal_path.exists():
            return RecoveryResult(status="no_wal", message="No WAL file found")

        # SQLite automatically replays WAL on next connection
        # But we can force a checkpoint for safety
        engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")

        try:
            async with engine.begin() as conn:
                # Force WAL checkpoint
                await conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))

                # Verify integrity
                result = await conn.execute(text("PRAGMA integrity_check"))
                status = result.scalar()

                if status == "ok":
                    return RecoveryResult(
                        status="recovered",
                        message="WAL replayed successfully",
                    )
                else:
                    return RecoveryResult(
                        status="error",
                        message=f"Integrity check failed: {status}",
                    )
        finally:
            await engine.dispose()

    async def verify_recovery(self, db_path: Path) -> bool:
        """Post-recovery integrity verification."""
        engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("PRAGMA integrity_check"))
                return result.scalar() == "ok"
        finally:
            await engine.dispose()
```

### 7.2 Journal Recovery

```python
class JournalRecovery:
    """Recover from SQLite journal (non-WAL mode fallback)."""

    async def recover(self, db_path: Path) -> RecoveryResult:
        """Recover from journal file."""
        journal_path = db_path.with_suffix(".db-journal")

        if not journal_path.exists():
            return RecoveryResult(
                status="no_journal",
                message="No journal file found",
            )

        # SQLite handles journal recovery automatically
        # Force a clean checkpoint
        engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
        try:
            async with engine.begin() as conn:
                # This forces journal replay
                await conn.execute(text("PRAGMA journal_mode = WAL"))
                await conn.execute(text("PRAGMA integrity_check"))

                return RecoveryResult(
                    status="recovered",
                    message="Journal replayed, switched to WAL mode",
                )
        finally:
            await engine.dispose()
```

---

## 8. Data Reconciliation

### 8.1 Multi-Device Sync Preparation

```python
class DataReconciler:
    """Prepares data for future multi-device synchronization."""

    async def generate_sync_manifest(
        self,
        session: AsyncSession,
        since: Optional[datetime] = None,
    ) -> SyncManifest:
        """Generate manifest of changed entities for sync."""
        since = since or datetime(2000, 1, 1)

        changed_entities = []

        # Collect changes from each entity type
        for entity_type in SYNCABLE_ENTITIES:
            changes = await self._get_changes_since(
                session, entity_type, since
            )
            changed_entities.extend(changes)

        return SyncManifest(
            device_id=self.device_id,
            generated_at=datetime.utcnow(),
            changes=changed_entities,
            total_changes=len(changed_entities),
        )

    async def _get_changes_since(
        self,
        session: AsyncSession,
        entity_type: str,
        since: datetime,
    ) -> list[EntityChange]:
        """Get all changes for an entity type since a timestamp."""
        model = get_model(entity_type)
        query = (
            select(model)
            .where(model.updated_at > since)
            .order_by(model.updated_at.asc())
        )

        result = await session.execute(query)
        entities = result.scalars().all()

        return [
            EntityChange(
                entity_type=entity_type,
                entity_id=e.id,
                version=e.version,
                updated_at=e.updated_at,
                is_deleted=e.is_deleted,
                data=e.to_dict(),
            )
            for e in entities
        ]

    async def apply_sync_changes(
        self,
        changes: list[EntityChange],
        session: AsyncSession,
        resolution_strategy: str = "server_wins",
    ) -> SyncResult:
        """Apply received sync changes."""
        result = SyncResult()

        for change in changes:
            try:
                model = get_model(change.entity_type)

                existing = await session.get(model, change.entity_id)

                if existing is None:
                    # New entity — create
                    entity = model.from_dict(change.data)
                    session.add(entity)
                    result.created += 1

                elif change.is_deleted:
                    # Remote deleted — soft-delete locally
                    existing.is_deleted = True
                    existing.deleted_at = datetime.utcnow()
                    result.deleted += 1

                else:
                    # Remote update — apply with conflict resolution
                    resolved = await self._resolve_and_apply(
                        existing, change, resolution_strategy, session
                    )
                    if resolved:
                        result.updated += 1
                    else:
                        result.conflicts += 1

            except Exception as e:
                result.errors.append({
                    "entity_type": change.entity_type,
                    "entity_id": str(change.entity_id),
                    "error": str(e),
                })

        return result
```

### 8.2 Sync Entity Types

```python
SYNCABLE_ENTITIES = [
    "users",
    "roles",
    "permissions",
    "courses",
    "course_modules",
    "lessons",
    "enrollments",
    "progress",
    "assessments",
    "questions",
    "question_options",
    "attempts",
    "answers",
    "results",
    "competencies",
    "competency_levels",
    "user_competencies",
    "certificates",
    "plugins",
    "configurations",
    "settings",
    "themes",
    "localization_keys",
    "translations",
    "accessibility_profiles",
    "notifications",
    "assets",
]

NON_SYNCABLE_ENTITIES = [
    "audit_entries",      # Audit stays local
    "security_events",    # Security stays local
    "backup_records",     # Backup metadata stays local
    "sessions",           # Sessions are device-specific
    "operation_queue",    # Queue is device-specific
]
```

---

## 9. Storage Optimization

### 9.1 VACUUM Strategy

```python
class StorageOptimizer:
    """Manages database storage optimization."""

    async def vacuum_main(self, session: AsyncSession):
        """Full VACUUM on main database."""
        await session.execute(text("VACUUM"))

    async def incremental_vacuum(
        self,
        session: AsyncSession,
        pages_to_free: int = 1000,
    ):
        """Incremental VACUUM — reclaim specific number of pages."""
        await session.execute(text(f"PRAGMA incremental_vacuum({pages_to_free})"))

    async def analyze_tables(self, session: AsyncSession):
        """Update query planner statistics."""
        await session.execute(text("ANALYZE"))

    async def reindex(self, session: AsyncSession):
        """Rebuild all indexes."""
        await session.execute(text("REINDEX"))

    async def get_database_stats(self, session: AsyncSession) -> dict:
        """Get database size and page statistics."""
        page_count = await session.execute(text("PRAGMA page_count"))
        page_size = await session.execute(text("PRAGMA page_size"))
        freelist_count = await session.execute(text("PRAGMA freelist_count"))

        page_count = page_count.scalar()
        page_size = page_size.scalar()
        freelist_count = freelist_count.scalar()

        total_size = page_count * page_size
        free_size = freelist_count * page_size
        used_size = total_size - free_size
        fragmentation = free_size / total_size * 100 if total_size > 0 else 0

        return {
            "total_size_bytes": total_size,
            "used_size_bytes": used_size,
            "free_size_bytes": free_size,
            "page_count": page_count,
            "page_size": page_size,
            "freelist_pages": freelist_count,
            "fragmentation_percent": round(fragmentation, 2),
            "needs_vacuum": fragmentation > 20,
        }

    async def run_maintenance(self, session: AsyncSession):
        """Run full maintenance cycle."""
        stats = await self.get_database_stats(session)

        logger.info(f"Database stats: {stats['total_size_bytes'] / 1024 / 1024:.1f} MB")

        if stats["needs_vacuum"]:
            logger.info(
                f"Fragmentation at {stats['fragmentation_percent']:.1f}%, running VACUUM"
            )
            await self.vacuum_main(session)

        # Always update statistics
        await self.analyze_tables(session)
```

### 9.2 Compaction

```python
class DataCompactor:
    """Compacts data by archiving old records."""

    ARCHIVAL_RULES = {
        "audit_entries": {
            "retain_active_days": 365,
            "archive_after_days": 365,
            "compress": True,
        },
        "notifications": {
            "retain_active_days": 90,
            "archive_after_days": 365,
            "compress": True,
        },
        "learning_sessions": {
            "retain_active_days": 730,
            "archive_after_days": 730,
            "compress": True,
        },
        "diagnostic_logs": {
            "retain_active_days": 30,
            "archive_after_days": 365,
            "compress": True,
        },
        "operation_queue": {
            "retain_active_days": 30,
            "archive_after_days": 0,  # Don't archive, just delete
            "compress": False,
        },
    }

    async def compact(
        self,
        session: AsyncSession,
        entity_type: Optional[str] = None,
    ) -> CompactionResult:
        """Run compaction on specified or all entity types."""
        result = CompactionResult()

        rules = self.ARCHIVAL_RULES
        if entity_type:
            rules = {entity_type: rules.get(entity_type, {})}

        for entity_type, rule in rules.items():
            archived = await self._archive_old_records(
                session, entity_type, rule
            )
            result.archived_count += archived

        return result

    async def _archive_old_records(
        self,
        session: AsyncSession,
        entity_type: str,
        rule: dict,
    ) -> int:
        """Archive old records for an entity type."""
        if rule.get("archive_after_days", 0) == 0:
            # Just delete
            cutoff = datetime.utcnow() - timedelta(days=rule["retain_active_days"])
            model = get_model(entity_type)

            result = await session.execute(
                delete(model).where(
                    model.updated_at < cutoff,
                    model.is_deleted == True,
                )
            )
            return result.rowcount

        # Archive to file before deleting
        cutoff = datetime.utcnow() - timedelta(days=rule["archive_after_days"])
        model = get_model(entity_type)

        query = select(model).where(
            model.updated_at < cutoff,
            model.is_deleted == True,
        )

        result = await session.execute(query)
        records = result.scalars().all()

        if records:
            archive_path = self._write_archive(entity_type, records, rule["compress"])
            logger.info(f"Archived {len(records)} {entity_type} to {archive_path}")

            # Delete archived records
            ids = [r.id for r in records]
            await session.execute(
                delete(model).where(model.id.in_(ids))
            )

        return len(records)
```

### 9.3 Archival File Format

```python
import gzip
import json

class ArchiveWriter:
    """Writes archived records to compressed files."""

    def write_archive(
        self,
        entity_type: str,
        records: list,
        compress: bool = True,
    ) -> Path:
        """Write records to archive file."""
        archive_dir = self.data_dir / "archives" / entity_type
        archive_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{entity_type}_{timestamp}.json"

        if compress:
            filename += ".gz"

        archive_path = archive_dir / filename

        data = [r.to_dict() for r in records]
        json_data = json.dumps(data, indent=2, default=str).encode("utf-8")

        if compress:
            with gzip.open(archive_path, "wb", compresslevel=9) as f:
                f.write(json_data)
        else:
            with open(archive_path, "wb") as f:
                f.write(json_data)

        # Write manifest
        manifest = {
            "entity_type": entity_type,
            "record_count": len(records),
            "compressed": compress,
            "checksum": hashlib.sha256(json_data).hexdigest(),
            "created_at": datetime.utcnow().isoformat(),
        }

        manifest_path = archive_path.with_suffix(".json.manifest")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return archive_path
```

---

## 10. Crash Recovery

### 10.1 WAL Checkpoint Strategy

```python
class CheckpointManager:
    """Manages WAL checkpointing for crash recovery."""

    async def checkpoint(
        self,
        session: AsyncSession,
        mode: str = "passive",
    ):
        """Perform WAL checkpoint.
        
        Modes:
        - PASSIVE: Checkpoint without blocking readers (default)
        - FULL: Checkpoint and block new readers until complete
        - RESTART: Like FULL, but restart WAL if still active
        - TRUNCATE: Like RESTART, but truncate WAL file
        """
        await session.execute(
            text(f"PRAGMA wal_checkpoint({mode.upper()})")
        )

    async def auto_checkpoint(self, session: AsyncSession):
        """Automatic checkpoint based on WAL size."""
        # Check WAL file size
        wal_size = await self._get_wal_size(session)

        if wal_size > 10 * 1024 * 1024:  # > 10MB
            await self.checkpoint(session, "passive")
        elif wal_size > 50 * 1024 * 1024:  # > 50MB
            await self.checkpoint(session, "full")

    async def _get_wal_size(self, session: AsyncSession) -> int:
        """Get WAL file size in bytes."""
        result = await session.execute(
            text("PRAGMA wal_checkpoint(PASSIVE)")
        )
        # WAL checkpoint returns (busy, log, checkpointed)
        row = result.fetchone()
        return row[1] if row else 0  # log = WAL pages
```

### 10.2 Recovery Procedures

```
┌─────────────────────────────────────────────────────────────┐
│                    Crash Recovery Flow                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Application starts                                       │
│     │                                                        │
│  2. Check for WAL file                                       │
│     │                                                        │
│  3. Connect to database (SQLite replays WAL automatically)   │
│     │                                                        │
│  4. Run PRAGMA integrity_check                               │
│     │                                                        │
│  ├── OK ──► Continue normally                                │
│     │                                                        │
│  └── FAIL ──► Check for backup                               │
│                │                                             │
│                ├── Backup found ──► Restore from backup       │
│                │                     │                       │
│                │                     5. Restore database      │
│                │                     6. Replay WAL            │
│                │                     7. Verify integrity      │
│                │                     8. Resume                │
│                │                                             │
│                └── No backup ──► Attempt repair               │
│                                  │                           │
│                                  5. Run REINDEX              │
│                                  6. Run VACUUM               │
│                                  7. Verify integrity         │
│                                  8. Notify user              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 10.3 Startup Recovery

```python
class StartupRecovery:
    """Performs recovery checks on application startup."""

    async def recover(self) -> RecoveryReport:
        """Run full recovery procedure."""
        report = RecoveryReport()

        # Step 1: Check all databases
        for db_name, db_path in self.database_paths.items():
            db_result = await self._recover_database(db_name, db_path)
            report.database_results[db_name] = db_result

            if db_result.status == "error":
                report.has_errors = True

        # Step 2: Verify audit chain
        audit_result = await self._verify_audit_chain()
        report.audit_chain = audit_result

        # Step 3: Check operation queue
        queue_result = await self._check_operation_queue()
        report.queue_status = queue_result

        # Step 4: Clean up temp files
        await self._cleanup_temp_files()

        # Step 5: Run maintenance if needed
        stats = await self.storage_optimizer.get_database_stats(self.main_session)
        if stats.get("needs_vacuum"):
            report.recommendations.append("Run VACUUM to optimize storage")

        return report

    async def _recover_database(
        self,
        name: str,
        path: Path,
    ) -> DatabaseRecoveryResult:
        """Recover a single database."""
        if not path.exists():
            return DatabaseRecoveryResult(
                name=name,
                status="missing",
                message=f"Database file not found: {path}",
            )

        try:
            engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
            async with engine.begin() as conn:
                result = await conn.execute(text("PRAGMA integrity_check"))
                status = result.scalar()

                if status == "ok":
                    return DatabaseRecoveryResult(name=name, status="ok")

                return DatabaseRecoveryResult(
                    name=name,
                    status="error",
                    message=f"Integrity check failed: {status}",
                )
        finally:
            await engine.dispose()
```

---

*This document defines the complete offline data architecture for AuthShield Lab.*
