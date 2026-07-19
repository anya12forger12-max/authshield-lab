# Audit Architecture — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Overview

AuthShield Lab maintains a comprehensive, tamper-evident audit trail of all
system mutations. The audit system uses hash chain integrity, async writes,
and structured event logging to provide reliable forensic capabilities.

### 1.1 Audit Principles

| Principle | Description |
|---|---|
| Comprehensive | Every mutation produces an audit entry |
| Tamper-evident | Hash chain links entries for integrity verification |
| Append-only | Audit entries are never modified or deleted |
| Async writes | Audit entries written asynchronously to avoid blocking |
| Structured | Consistent schema with typed fields |
| Retained | Configurable retention (default 7 years) |

---

## 2. Tracked Events

### 2.1 Event Categories

| Category | Actions | Examples |
|---|---|---|
| **Authentication** | login, logout, login_failed, password_change, password_reset, mfa_enable, mfa_disable, mfa_verify | User logs in, fails password, changes MFA |
| **Authorization** | role_assign, role_revoke, permission_grant, permission_revoke, access_denied | Admin assigns role, permission check fails |
| **User Management** | user_create, user_update, user_delete, user_suspend, user_activate, user_lock | Admin creates/deletes user |
| **Configuration** | config_set, config_delete, config_export, feature_flag_toggle | Admin changes system settings |
| **Plugin Events** | plugin_install, plugin_uninstall, plugin_enable, plugin_disable, plugin_update, plugin_error | Plugin lifecycle events |
| **Learning Events** | enrollment_create, enrollment_complete, lesson_start, lesson_complete, progress_update, session_start, session_end | Student learning activities |
| **Assessment Events** | assessment_start, assessment_submit, assessment_graded, answer_submitted, result_published | Assessment lifecycle |
| **Certificate Events** | certificate_issue, certificate_revoke, certificate_verify | Certificate lifecycle |
| **Administrative** | backup_create, backup_restore, migration_start, migration_complete, system_config_change | System administration |
| **Security Events** | suspicious_activity, brute_force_detected, account_locked, unauthorized_access, data_breach疑似 | Security incidents |
| **Accessibility Events** | a11y_profile_update, a11y_settings_change | Accessibility preference changes |
| **Data Events** | import_start, import_complete, export_start, export_complete | Data import/export |

### 2.2 Event Action Constants

```python
class AuditAction:
    """Constants for all audit action types."""

    # Authentication
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    PASSWORD_CHANGE = "auth.password_change"
    PASSWORD_RESET = "auth.password_reset"
    MFA_ENABLE = "auth.mfa_enable"
    MFA_DISABLE = "auth.mfa_disable"
    MFA_VERIFY = "auth.mfa_verify"
    SESSION_CREATE = "auth.session_create"
    SESSION_EXPIRE = "auth.session_expire"
    SESSION_REVOKE = "auth.session_revoke"

    # Authorization
    ROLE_ASSIGN = "authz.role_assign"
    ROLE_REVOKE = "authz.role_revoke"
    PERMISSION_GRANT = "authz.permission_grant"
    PERMISSION_REVOKE = "authz.permission_revoke"
    ACCESS_DENIED = "authz.access_denied"

    # User Management
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_RESTORE = "user.restore"
    USER_SUSPEND = "user.suspend"
    USER_ACTIVATE = "user.activate"
    USER_LOCK = "user.lock"
    USER_UNLOCK = "user.unlock"

    # Configuration
    CONFIG_SET = "config.set"
    CONFIG_DELETE = "config.delete"
    CONFIG_EXPORT = "config.export"
    CONFIG_IMPORT = "config.import"
    FEATURE_FLAG_TOGGLE = "config.feature_flag_toggle"

    # Plugin
    PLUGIN_INSTALL = "plugin.install"
    PLUGIN_UNINSTALL = "plugin.uninstall"
    PLUGIN_ENABLE = "plugin.enable"
    PLUGIN_DISABLE = "plugin.disable"
    PLUGIN_UPDATE = "plugin.update"
    PLUGIN_ERROR = "plugin.error"

    # Learning
    ENROLLMENT_CREATE = "learning.enrollment_create"
    ENROLLMENT_COMPLETE = "learning.enrollment_complete"
    ENROLLMENT_DROP = "learning.enrollment_drop"
    LESSON_START = "learning.lesson_start"
    LESSON_COMPLETE = "learning.lesson_complete"
    PROGRESS_UPDATE = "learning.progress_update"
    SESSION_START = "learning.session_start"
    SESSION_END = "learning.session_end"
    COMPETENCY_ACHIEVE = "learning.competency_achieve"

    # Assessment
    ASSESSMENT_START = "assessment.start"
    ASSESSMENT_SUBMIT = "assessment.submit"
    ASSESSMENT_GRADED = "assessment.graded"
    ANSWER_SUBMIT = "assessment.answer_submit"
    RESULT_PUBLISH = "assessment.result_publish"

    # Certificate
    CERTIFICATE_ISSUE = "certificate.issue"
    CERTIFICATE_REVOKE = "certificate.revoke"
    CERTIFICATE_VERIFY = "certificate.verify"

    # Administrative
    BACKUP_CREATE = "admin.backup_create"
    BACKUP_RESTORE = "admin.backup_restore"
    MIGRATION_START = "admin.migration_start"
    MIGRATION_COMPLETE = "admin.migration_complete"
    SYSTEM_START = "admin.system_start"
    SYSTEM_STOP = "admin.system_stop"

    # Security
    SUSPICIOUS_ACTIVITY = "security.suspicious_activity"
    BRUTE_FORCE = "security.brute_force"
    ACCOUNT_LOCKED = "security.account_locked"
    UNAUTHORIZED_ACCESS = "security.unauthorized_access"
    DATA_EXPORT = "security.data_export"

    # Accessibility
    A11Y_PROFILE_UPDATE = "a11y.profile_update"
    A11Y_SETTINGS_CHANGE = "a11y.settings_change"

    # Data
    IMPORT_START = "data.import_start"
    IMPORT_COMPLETE = "data.import_complete"
    EXPORT_START = "data.export_start"
    EXPORT_COMPLETE = "data.export_complete"
```

---

## 3. Audit Entry Schema

### 3.1 Core Schema

```sql
CREATE TABLE audit_entries (
    id BLOB(16) PRIMARY KEY,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id BLOB(16),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id BLOB(16),
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    metadata TEXT,
    previous_hash VARCHAR(64),
    entry_hash VARCHAR(64) NOT NULL,
    -- Audit entries are append-only, no soft delete columns
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 1
);
```

### 3.2 Entry Fields

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 primary key |
| `timestamp` | DATETIME | NOT NULL | Event timestamp (UTC) |
| `user_id` | BLOB(16) | NULL | Actor user ID (NULL for system) |
| `action` | VARCHAR(100) | NOT NULL | Action type (see AuditAction) |
| `entity_type` | VARCHAR(100) | NOT NULL | Entity type affected |
| `entity_id` | BLOB(16) | NULL | Entity ID affected |
| `old_value` | TEXT | NULL | Previous state (JSON) |
| `new_value` | TEXT | NULL | New state (JSON) |
| `ip_address` | VARCHAR(45) | NULL | Client IP address |
| `user_agent` | VARCHAR(500) | NULL | Client user agent |
| `metadata` | TEXT | NULL | Additional context (JSON) |
| `previous_hash` | VARCHAR(64) | NULL | Hash of previous entry (chain) |
| `entry_hash` | VARCHAR(64) | NOT NULL | SHA-256 hash of this entry |

### 3.3 Audit Entry Model

```python
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
import hashlib
import json

@dataclass
class AuditEntry:
    """Immutable audit entry record."""

    action: str
    entity_type: str
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[UUID] = None
    entity_id: Optional[UUID] = None
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[dict] = None
    previous_hash: Optional[str] = None
    entry_hash: str = ""

    def compute_hash(self, previous_hash: Optional[str] = None) -> str:
        """Compute SHA-256 hash for this entry."""
        data_parts = [
            str(self.id),
            self.timestamp.isoformat(),
            str(self.user_id) if self.user_id else "",
            self.action,
            self.entity_type,
            str(self.entity_id) if self.entity_id else "",
            previous_hash or "",
        ]
        data = "|".join(data_parts)
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        """Serialize entry to dictionary."""
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.isoformat(),
            "user_id": str(self.user_id) if self.user_id else None,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }

    def to_search_text(self) -> str:
        """Generate searchable text for full-text search."""
        parts = [
            self.action,
            self.entity_type,
            str(self.user_id) if self.user_id else "",
            str(self.entity_id) if self.entity_id else "",
        ]
        return " ".join(parts)
```

---

## 4. Hash Chain Integrity

### 4.1 Chain Construction

```python
class AuditChainManager:
    """Manages the audit hash chain for tamper detection."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def append_entry(self, entry: AuditEntry) -> AuditEntry:
        """Append entry to chain with hash computation."""
        # Get previous entry's hash
        previous_hash = await self._get_last_hash()

        # Compute this entry's hash
        entry.previous_hash = previous_hash
        entry.entry_hash = entry.compute_hash(previous_hash)

        # Store entry
        self.session.add(entry)
        await self.session.flush()

        return entry

    async def _get_last_hash(self) -> Optional[str]:
        """Get hash of the most recent audit entry."""
        result = await self.session.execute(
            select(AuditEntry.entry_hash)
            .order_by(AuditEntry.timestamp.desc(), AuditEntry.id.desc())
            .limit(1)
        )
        row = result.fetchone()
        return row[0] if row else None
```

### 4.2 Chain Verification

```python
class AuditChainVerifier:
    """Verifies integrity of the audit hash chain."""

    async def verify(
        self,
        session: AsyncSession,
        start_id: Optional[UUID] = None,
        end_id: Optional[UUID] = None,
    ) -> ChainVerificationResult:
        """Verify hash chain integrity."""
        query = (
            select(AuditEntry)
            .order_by(AuditEntry.timestamp.asc(), AuditEntry.id.asc())
        )

        if start_id:
            query = query.where(AuditEntry.id >= start_id)
        if end_id:
            query = query.where(AuditEntry.id <= end_id)

        result = await session.execute(query)
        entries = list(result.scalars().all())

        if not entries:
            return ChainVerificationResult(
                status="empty",
                entries_checked=0,
                message="No audit entries to verify",
            )

        previous_hash = None
        broken_at_index = None
        broken_entry = None

        for idx, entry in enumerate(entries):
            # Verify chain link
            if entry.previous_hash != previous_hash:
                broken_at_index = idx
                broken_entry = entry
                break

            # Verify entry hash
            expected_hash = entry.compute_hash(previous_hash)
            if entry.entry_hash != expected_hash:
                broken_at_index = idx
                broken_entry = entry
                break

            previous_hash = entry.entry_hash

        if broken_at_index is not None:
            return ChainVerificationResult(
                status="broken",
                entries_checked=broken_at_index + 1,
                broken_entry_id=broken_entry.id,
                broken_entry_timestamp=broken_entry.timestamp,
                expected_previous_hash=previous_hash,
                actual_previous_hash=broken_entry.previous_hash,
                message=f"Chain broken at entry {broken_entry.id}",
            )

        return ChainVerificationResult(
            status="valid",
            entries_checked=len(entries),
            chain_start_id=entries[0].id,
            chain_end_id=entries[-1].id,
            chain_start_hash=entries[0].entry_hash,
            chain_end_hash=entries[-1].entry_hash,
        )


@dataclass
class ChainVerificationResult:
    """Result of audit chain verification."""
    status: str  # "valid", "broken", "empty"
    entries_checked: int
    broken_entry_id: Optional[UUID] = None
    broken_entry_timestamp: Optional[datetime] = None
    expected_previous_hash: Optional[str] = None
    actual_previous_hash: Optional[str] = None
    chain_start_id: Optional[UUID] = None
    chain_end_id: Optional[UUID] = None
    chain_start_hash: Optional[str] = None
    chain_end_hash: Optional[str] = None
    message: Optional[str] = None
```

---

## 5. Retention Policy

### 5.1 Retention Configuration

```python
RETENTION_POLICY = {
    # Default retention periods (in days)
    "default": 2555,  # 7 years

    # Action-specific retention
    "auth.login": 2555,              # 7 years
    "auth.login_failed": 365,        # 1 year
    "auth.logout": 365,              # 1 year
    "auth.password_change": 2555,    # 7 years
    "auth.mfa_enable": 2555,         # 7 years
    "authz.role_assign": 2555,       # 7 years
    "authz.permission_grant": 2555,  # 7 years
    "user.create": 2555,             # 7 years
    "user.delete": 2555,             # 7 years (legal requirement)
    "config.set": 365,               # 1 year
    "plugin.install": 365,           # 1 year
    "learning.enrollment_create": 2555,  # 7 years
    "assessment.submit": 2555,       # 7 years
    "certificate.issue": -1,         # Never expire
    "security.*": 3650,              # 10 years
    "admin.backup_create": 365,      # 1 year
    "admin.migration_complete": 2555, # 7 years
}
```

### 5.2 Retention Enforcement

```python
class AuditRetentionManager:
    """Enforces audit log retention policy."""

    async def enforce_retention(
        self,
        session: AsyncSession,
        dry_run: bool = False,
    ) -> RetentionResult:
        """Archive or annotate entries past retention period."""
        result = RetentionResult()

        for action, retention_days in RETENTION_POLICY.items():
            if retention_days == -1:
                continue  # Never expire

            cutoff = datetime.utcnow() - timedelta(days=retention_days)

            # Find entries past retention
            query = (
                select(AuditEntry)
                .where(AuditEntry.action == action)
                .where(AuditEntry.timestamp < cutoff)
            )

            entries = await session.execute(query)
            expired = list(entries.scalars().all())

            if expired and not dry_run:
                # Archive before marking
                archive_path = await self._archive_entries(expired)

                # Mark as archived (not deleted — audit is append-only)
                for entry in expired:
                    entry.metadata = entry.metadata or {}
                    entry.metadata["archived"] = True
                    entry.metadata["archive_path"] = str(archive_path)
                    entry.metadata["archived_at"] = datetime.utcnow().isoformat()

                result.archived_count += len(expired)

            result.total_expired += len(expired)

        return result
```

---

## 6. Search & Filtering

### 6.1 Search Capabilities

```python
class AuditSearcher:
    """Search and filter audit entries."""

    async def search_by_user(
        self,
        user_id: UUID,
        pagination: PaginationSpecification = None,
    ) -> PaginatedResult[AuditEntry]:
        """Search audit entries by user."""
        query = (
            select(AuditEntry)
            .where(AuditEntry.user_id == user_id)
            .order_by(AuditEntry.timestamp.desc())
        )

        return await self._execute_paginated(query, pagination)

    async def search_by_action(
        self,
        action: str,
        pagination: PaginationSpecification = None,
    ) -> PaginatedResult[AuditEntry]:
        """Search audit entries by action type."""
        query = (
            select(AuditEntry)
            .where(AuditEntry.action == action)
            .order_by(AuditEntry.timestamp.desc())
        )

        return await self._execute_paginated(query, pagination)

    async def search_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        pagination: PaginationSpecification = None,
    ) -> PaginatedResult[AuditEntry]:
        """Search audit entries by entity."""
        query = (
            select(AuditEntry)
            .where(AuditEntry.entity_type == entity_type)
            .where(AuditEntry.entity_id == entity_id)
            .order_by(AuditEntry.timestamp.desc())
        )

        return await self._execute_paginated(query, pagination)

    async def search_by_time_range(
        self,
        start: datetime,
        end: datetime,
        filters: Optional[list[FilterSpecification]] = None,
        pagination: PaginationSpecification = None,
    ) -> PaginatedResult[AuditEntry]:
        """Search audit entries by time range."""
        query = (
            select(AuditEntry)
            .where(AuditEntry.timestamp >= start)
            .where(AuditEntry.timestamp <= end)
            .order_by(AuditEntry.timestamp.desc())
        )

        if filters:
            for f in filters:
                query = query.where(f.to_clause())

        return await self._execute_paginated(query, pagination)

    async def search_combined(
        self,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        pagination: PaginationSpecification = None,
    ) -> PaginatedResult[AuditEntry]:
        """Combined search with multiple criteria."""
        query = select(AuditEntry)

        if user_id:
            query = query.where(AuditEntry.user_id == user_id)
        if action:
            query = query.where(AuditEntry.action == action)
        if entity_type:
            query = query.where(AuditEntry.entity_type == entity_type)
        if entity_id:
            query = query.where(AuditEntry.entity_id == entity_id)
        if start:
            query = query.where(AuditEntry.timestamp >= start)
        if end:
            query = query.where(AuditEntry.timestamp <= end)
        if ip_address:
            query = query.where(AuditEntry.ip_address == ip_address)

        query = query.order_by(AuditEntry.timestamp.desc())

        return await self._execute_paginated(query, pagination)

    async def full_text_search(
        self,
        search_term: str,
        pagination: PaginationSpecification = None,
    ) -> PaginatedResult[AuditEntry]:
        """Full-text search across audit fields."""
        query = (
            select(AuditEntry)
            .where(
                AuditEntry.action.contains(search_term)
                | AuditEntry.entity_type.contains(search_term)
                | AuditEntry.old_value.contains(search_term)
                | AuditEntry.new_value.contains(search_term)
            )
            .order_by(AuditEntry.timestamp.desc())
        )

        return await self._execute_paginated(query, pagination)
```

### 6.2 Filter Specifications

```python
class AuditFilter:
    """Pre-built audit filter specifications."""

    @staticmethod
    def failed_logins(since: Optional[datetime] = None) -> FilterSpecification:
        """Filter for failed login attempts."""
        spec = FilterSpecification("action", "eq", "auth.login_failed")
        if since:
            spec = spec.and_(FilterSpecification("timestamp", "gte", since))
        return spec

    @staticmethod
    def security_events() -> FilterSpecification:
        """Filter for all security events."""
        return FilterSpecification("action", "like", "security.*")

    @staticmethod
    def admin_actions() -> FilterSpecification:
        """Filter for administrative actions."""
        return FilterSpecification("action", "like", "admin.*")

    @staticmethod
    def config_changes() -> FilterSpecification:
        """Filter for configuration changes."""
        return FilterSpecification("action", "like", "config.*")

    @staticmethod
    def entity_history(entity_type: str, entity_id: UUID) -> list[FilterSpecification]:
        """Get filters for entity history."""
        return [
            FilterSpecification("entity_type", "eq", entity_type),
            FilterSpecification("entity_id", "eq", entity_id),
        ]

    @staticmethod
    def user_activity(user_id: UUID) -> FilterSpecification:
        """Filter for all activity by a user."""
        return FilterSpecification("user_id", "eq", user_id)

    @staticmethod
    def recent(hours: int = 24) -> FilterSpecification:
        """Filter for recent entries."""
        since = datetime.utcnow() - timedelta(hours=hours)
        return FilterSpecification("timestamp", "gte", since)
```

---

## 7. Export

### 7.1 JSON Export

```python
class AuditJSONExporter:
    """Export audit entries as JSON."""

    async def export(
        self,
        session: AsyncSession,
        filters: Optional[list[FilterSpecification]] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Export audit entries to JSON."""
        query = select(AuditEntry)
        if filters:
            for f in filters:
                query = query.where(f.to_clause())
        query = query.order_by(AuditEntry.timestamp.asc())

        result = await session.execute(query)
        entries = result.scalars().all()

        export_data = {
            "version": "2.0",
            "format": "authshield-audit",
            "exported_at": datetime.utcnow().isoformat(),
            "entry_count": len(entries),
            "chain_start": entries[0].entry_hash if entries else None,
            "chain_end": entries[-1].entry_hash if entries else None,
            "entries": [e.to_dict() for e in entries],
        }

        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            output_path = Path(f"audit_export_{timestamp}.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, default=str)

        return output_path
```

### 7.2 CSV Export

```python
class AuditCSVExporter:
    """Export audit entries as CSV."""

    COLUMNS = [
        "id", "timestamp", "user_id", "action", "entity_type",
        "entity_id", "old_value", "new_value", "ip_address",
        "user_agent", "entry_hash",
    ]

    async def export(
        self,
        session: AsyncSession,
        filters: Optional[list[FilterSpecification]] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Export audit entries to CSV."""
        query = select(AuditEntry)
        if filters:
            for f in filters:
                query = query.where(f.to_clause())
        query = query.order_by(AuditEntry.timestamp.asc())

        result = await session.execute(query)
        entries = result.scalars().all()

        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            output_path = Path(f"audit_export_{timestamp}.csv")

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=self.COLUMNS)
            writer.writeheader()

            for entry in entries:
                row = {
                    "id": str(entry.id),
                    "timestamp": entry.timestamp.isoformat(),
                    "user_id": str(entry.user_id) if entry.user_id else "",
                    "action": entry.action,
                    "entity_type": entry.entity_type,
                    "entity_id": str(entry.entity_id) if entry.entity_id else "",
                    "old_value": json.dumps(entry.old_value) if entry.old_value else "",
                    "new_value": json.dumps(entry.new_value) if entry.new_value else "",
                    "ip_address": entry.ip_address or "",
                    "user_agent": entry.user_agent or "",
                    "entry_hash": entry.entry_hash,
                }
                writer.writerow(row)

        return output_path
```

---

## 8. Performance Optimization

### 8.1 Async Audit Writes

```python
class AsyncAuditWriter:
    """Writes audit entries asynchronously to avoid blocking."""

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the async audit writer worker."""
        self._worker_task = asyncio.create_task(self._process_queue())

    async def stop(self):
        """Stop the async audit writer worker."""
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

    async def write(self, entry: AuditEntry):
        """Queue an audit entry for async writing."""
        await self._queue.put(entry)

    async def _process_queue(self):
        """Process queued audit entries in batches."""
        while True:
            batch = []

            # Collect batch
            try:
                entry = await asyncio.wait_for(
                    self._queue.get(), timeout=1.0
                )
                batch.append(entry)

                # Drain additional entries
                while not self._queue.empty() and len(batch) < 100:
                    batch.append(self._queue.get_nowait())

            except asyncio.TimeoutError:
                continue

            # Write batch
            if batch:
                await self._write_batch(batch)

    async def _write_batch(self, batch: list[AuditEntry]):
        """Write a batch of audit entries."""
        async with async_session_factory() as session:
            async with session.begin():
                for entry in batch:
                    session.add(entry)
                await session.commit()
```

### 8.2 Index Strategy

```sql
-- Primary search indexes
CREATE INDEX idx_audit_timestamp
    ON audit_entries(timestamp DESC);

CREATE INDEX idx_audit_user
    ON audit_entries(user_id)
    WHERE user_id IS NOT NULL;

CREATE INDEX idx_audit_action
    ON audit_entries(action);

CREATE INDEX idx_audit_entity
    ON audit_entries(entity_type, entity_id)
    WHERE entity_id IS NOT NULL;

CREATE INDEX idx_audit_ip
    ON audit_entries(ip_address)
    WHERE ip_address IS NOT NULL;

-- Composite indexes for common queries
CREATE INDEX idx_audit_user_time
    ON audit_entries(user_id, timestamp DESC)
    WHERE user_id IS NOT NULL;

CREATE INDEX idx_audit_action_time
    ON audit_entries(action, timestamp DESC);

CREATE INDEX idx_audit_entity_time
    ON audit_entries(entity_type, entity_id, timestamp DESC)
    WHERE entity_id IS NOT NULL;

-- Hash chain verification
CREATE INDEX idx_audit_hash
    ON audit_entries(entry_hash);

CREATE INDEX idx_audit_previous_hash
    ON audit_entries(previous_hash);
```

### 8.3 Query Performance

```python
class AuditQueryOptimizer:
    """Optimizes audit query performance."""

    async def get_entity_history_optimized(
        self,
        entity_type: str,
        entity_id: UUID,
        session: AsyncSession,
    ) -> list[AuditEntry]:
        """Optimized entity history query."""
        # Uses composite index idx_audit_entity_time
        query = (
            select(AuditEntry)
            .where(AuditEntry.entity_type == entity_type)
            .where(AuditEntry.entity_id == entity_id)
            .order_by(AuditEntry.timestamp.desc())
            .limit(1000)  # Limit for performance
        )

        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_recent_activity_optimized(
        self,
        hours: int = 24,
        session: AsyncSession = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Optimized recent activity query."""
        since = datetime.utcnow() - timedelta(hours=hours)

        # Uses idx_audit_timestamp
        query = (
            select(AuditEntry)
            .where(AuditEntry.timestamp >= since)
            .order_by(AuditEntry.timestamp.desc())
            .limit(limit)
        )

        result = await session.execute(query)
        return list(result.scalars().all())
```

---

## 9. Audit Statistics

### 9.1 Metrics Collection

```python
class AuditMetrics:
    """Collects and reports audit statistics."""

    async def get_statistics(
        self,
        session: AsyncSession,
        period_days: int = 30,
    ) -> AuditStatistics:
        """Get audit statistics for a time period."""
        since = datetime.utcnow() - timedelta(days=period_days)

        # Total entries
        total = await session.execute(
            select(func.count(AuditEntry.id))
            .where(AuditEntry.timestamp >= since)
        )

        # By action
        by_action = await session.execute(
            select(AuditEntry.action, func.count(AuditEntry.id))
            .where(AuditEntry.timestamp >= since)
            .group_by(AuditEntry.action)
            .order_by(func.count(AuditEntry.id).desc())
        )

        # By user
        by_user = await session.execute(
            select(AuditEntry.user_id, func.count(AuditEntry.id))
            .where(AuditEntry.timestamp >= since)
            .where(AuditEntry.user_id.isnot(None))
            .group_by(AuditEntry.user_id)
            .order_by(func.count(AuditEntry.id).desc())
            .limit(10)
        )

        # Failed logins
        failed_logins = await session.execute(
            select(func.count(AuditEntry.id))
            .where(AuditEntry.action == "auth.login_failed")
            .where(AuditEntry.timestamp >= since)
        )

        return AuditStatistics(
            period_days=period_days,
            total_entries=total.scalar(),
            by_action=dict(by_action.fetchall()),
            top_users=[(str(uid), count) for uid, count in by_user.fetchall()],
            failed_logins=failed_logins.scalar(),
        )
```

---

*This document defines the complete audit architecture for AuthShield Lab.*
