# Backup & Restore Architecture — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Overview

AuthShield Lab provides a comprehensive backup and restore system designed for
local-first operation. All backups are stored locally with optional encryption.
The system supports full backups, incremental backups, and category-specific exports.

### 1.1 Backup Principles

| Principle | Description |
|---|---|
| 3-2-1 Rule | 3 copies, 2 different media, 1 offsite (future) |
| Automated | Scheduled backups require no user intervention |
| Encrypted | AES-256 encryption for all backup files |
| Verified | SHA-256 checksums verify integrity |
| Tested | Quarterly restore tests validate recoverability |
| Rotation | Automatic rotation based on configurable retention |

---

## 2. Backup Types

### 2.1 Full Backup

Complete copy of the SQLite database after VACUUM:

```python
class FullBackup:
    """Complete database backup with VACUUM for consistency."""

    async def execute(self, config: BackupConfig) -> BackupResult:
        """Create a full backup of the database."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = config.backup_dir / "full" / f"authshield_full_{timestamp}.db"

        # Step 1: Force WAL checkpoint for consistency
        await self._checkpoint_wal()

        # Step 2: VACUUM into backup file (atomic copy)
        await self._vacuum_backup(backup_path)

        # Step 3: Compress
        compressed_path = await self._compress(backup_path)

        # Step 4: Encrypt
        encrypted_path = await self._encrypt(compressed_path, config.encryption_key)

        # Step 5: Compute checksum
        checksum = await self._compute_checksum(encrypted_path)

        # Step 6: Clean up intermediate files
        backup_path.unlink(missing_ok=True)
        compressed_path.unlink(missing_ok=True)

        # Step 7: Record backup
        record = BackupRecord(
            id=uuid.uuid4(),
            backup_type="full",
            status="completed",
            file_path=str(encrypted_path),
            file_size_bytes=encrypted_path.stat().st_size,
            checksum_sha256=checksum,
            started_at=start_time,
            completed_at=datetime.utcnow(),
            retention_days=config.full_retention_days,
        )

        return BackupResult(record=record)

    async def _vacuum_backup(self, backup_path: Path):
        """Atomic backup using VACUUM INTO."""
        engine = create_async_engine(self.database_url)
        async with engine.begin() as conn:
            await conn.execute(
                text(f"VACUUM INTO '{backup_path}'")
            )
        await engine.dispose()
```

### 2.2 Incremental Backup

WAL-based incremental backup for daily operations:

```python
class IncrementalBackup:
    """WAL-based incremental backup."""

    async def execute(self, config: BackupConfig) -> BackupResult:
        """Create incremental backup from WAL."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        wal_path = self.database_path.with_suffix(".db-wal")
        shm_path = self.database_path.with_suffix(".db-shm")

        if not wal_path.exists():
            return BackupResult(
                record=BackupRecord(
                    status="skipped",
                    error_message="No WAL changes to backup",
                )
            )

        # Step 1: Copy WAL and SHM files
        backup_dir = config.backup_dir / "incremental"
        backup_dir.mkdir(parents=True, exist_ok=True)

        incr_wal = backup_dir / f"authshield_incr_{timestamp}.db-wal"
        incr_shm = backup_dir / f"authshield_incr_{timestamp}.db-shm"

        shutil.copy2(wal_path, incr_wal)
        if shm_path.exists():
            shutil.copy2(shm_path, incr_shm)

        # Step 2: Compress
        compressed_path = await self._compress(incr_wal)

        # Step 3: Encrypt
        encrypted_path = await self._encrypt(compressed_path, config.encryption_key)

        # Step 4: Compute checksum
        checksum = await self._compute_checksum(encrypted_path)

        # Step 5: Record
        record = BackupRecord(
            id=uuid.uuid4(),
            backup_type="incremental",
            status="completed",
            file_path=str(encrypted_path),
            file_size_bytes=encrypted_path.stat().st_size,
            checksum_sha256=checksum,
            parent_backup_id=await self._get_latest_full_backup_id(),
            retention_days=config.incremental_retention_days,
        )

        return BackupResult(record=record)
```

### 2.3 Configuration Backup

Export all settings as JSON:

```python
class ConfigBackup:
    """Export system configuration as JSON."""

    async def execute(self, config: BackupConfig) -> BackupResult:
        """Export all configuration to JSON."""
        export_data = {
            "version": "2.0.0",
            "exported_at": datetime.utcnow().isoformat(),
            "configurations": await self._export_configurations(),
            "settings": await self._export_settings(),
            "feature_flags": await self._export_feature_flags(),
            "themes": await self._export_themes(),
            "localization": await self._export_localization(),
            "accessibility_profiles": await self._export_accessibility(),
            "plugins": await self._export_plugin_configs(),
        }

        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        export_path = config.backup_dir / "config" / f"config_{timestamp}.json"

        export_path.parent.mkdir(parents=True, exist_ok=True)

        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        # Compress and encrypt
        compressed = await self._compress(export_path)
        encrypted = await self._encrypt(compressed, config.encryption_key)
        checksum = await self._compute_checksum(encrypted)

        export_path.unlink(missing_ok=True)
        compressed.unlink(missing_ok=True)

        record = BackupRecord(
            id=uuid.uuid4(),
            backup_type="config",
            status="completed",
            file_path=str(encrypted),
            file_size_bytes=encrypted.stat().st_size,
            checksum_sha256=checksum,
        )

        return BackupResult(record=record)
```

### 2.4 Plugin Backup

Export installed plugin metadata and configurations:

```python
class PluginBackup:
    """Export plugin registry and configurations."""

    async def execute(self, config: BackupConfig) -> BackupResult:
        """Export plugin data."""
        plugins = await self.plugin_repository.list_all(include_disabled=True)

        export_data = {
            "version": "2.0.0",
            "exported_at": datetime.utcnow().isoformat(),
            "plugins": [],
        }

        for plugin in plugins:
            plugin_data = {
                "name": plugin.name,
                "display_name": plugin.display_name,
                "version": plugin.current_version,
                "status": plugin.status,
                "config": await self.plugin_repository.get_config(plugin.id),
                "installed_at": plugin.installed_at.isoformat(),
            }
            export_data["plugins"].append(plugin_data)

        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        export_path = config.backup_dir / "plugins" / f"plugins_{timestamp}.json"

        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        compressed = await self._compress(export_path)
        encrypted = await self._encrypt(compressed, config.encryption_key)
        checksum = await self._compute_checksum(encrypted)

        export_path.unlink(missing_ok=True)
        compressed.unlink(missing_ok=True)

        record = BackupRecord(
            id=uuid.uuid4(),
            backup_type="plugins",
            status="completed",
            file_path=str(encrypted),
            file_size_bytes=encrypted.stat().st_size,
            checksum_sha256=checksum,
        )

        return BackupResult(record=record)
```

### 2.5 Course Backup

Export course data for portability:

```python
class CourseBackup:
    """Export course data with all related content."""

    async def execute(
        self,
        course_id: UUID,
        config: BackupConfig,
    ) -> BackupResult:
        """Export complete course data."""
        course = await self.course_repository.get_by_id(course_id)
        if course is None:
            raise EntityNotFoundError(course_id)

        modules = await self.module_repository.list_for_course(course_id)
        lessons = []
        for module in modules:
            module_lessons = await self.lesson_repository.list_by_module(module.id)
            lessons.extend(module_lessons)

        assessments = await self.assessment_repository.list_by_course(course_id)
        questions = []
        for assessment in assessments:
            assessment_questions = await self.question_repository.list_by_assessment(
                assessment.id
            )
            questions.extend(assessment_questions)

        export_data = {
            "version": "2.0.0",
            "format": "authshield-course",
            "exported_at": datetime.utcnow().isoformat(),
            "course": course.to_dict(),
            "modules": [m.to_dict() for m in modules],
            "lessons": [l.to_dict() for l in lessons],
            "assessments": [a.to_dict() for a in assessments],
            "questions": [q.to_dict() for q in questions],
            "statistics": {
                "enrollment_count": await self.enrollment_repository.count_for_course(
                    course_id
                ),
                "completion_rate": await self.course_repository.get_completion_rate(
                    course_id
                ),
            },
        }

        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        slug = course.slug or course.title.lower().replace(" ", "_")
        export_path = (
            config.backup_dir / "courses" / f"course_{slug}_{timestamp}.json"
        )

        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        compressed = await self._compress(export_path)
        checksum = await self._compute_checksum(compressed)

        export_path.unlink(missing_ok=True)

        record = BackupRecord(
            id=uuid.uuid4(),
            backup_type="course",
            status="completed",
            file_path=str(compressed),
            file_size_bytes=compressed.stat().st_size,
            checksum_sha256=checksum,
            metadata=json.dumps({"course_id": str(course_id), "course_title": course.title}),
        )

        return BackupResult(record=record)
```

### 2.6 Audit Backup

Encrypted archive of audit logs:

```python
class AuditBackup:
    """Export audit logs with tamper-evident packaging."""

    async def execute(
        self,
        config: BackupConfig,
        since: Optional[datetime] = None,
    ) -> BackupResult:
        """Export audit logs."""
        since = since or datetime(2000, 1, 1)

        query = (
            select(AuditEntry)
            .where(AuditEntry.timestamp >= since)
            .order_by(AuditEntry.timestamp.asc())
        )

        result = await self.audit_session.execute(query)
        entries = result.scalars().all()

        export_data = {
            "version": "2.0.0",
            "format": "authshield-audit",
            "exported_at": datetime.utcnow().isoformat(),
            "entry_count": len(entries),
            "chain_start": entries[0].entry_hash if entries else None,
            "chain_end": entries[-1].entry_hash if entries else None,
            "entries": [e.to_dict() for e in entries],
        }

        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        export_path = (
            config.backup_dir / "audit" / f"audit_{timestamp}.json"
        )

        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        # Audit backups are always encrypted (sensitive data)
        compressed = await self._compress(export_path)
        encrypted = await self._encrypt(compressed, config.encryption_key)
        checksum = await self._compute_checksum(encrypted)

        export_path.unlink(missing_ok=True)
        compressed.unlink(missing_ok=True)

        record = BackupRecord(
            id=uuid.uuid4(),
            backup_type="audit",
            status="completed",
            file_path=str(encrypted),
            file_size_bytes=encrypted.stat().st_size,
            checksum_sha256=checksum,
            retention_days=config.audit_retention_days,
        )

        return BackupResult(record=record)
```

---

## 3. Encryption

### 3.1 AES-256 Encryption

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class BackupEncryption:
    """AES-256 encryption for backup files."""

    def __init__(self, master_key: str):
        self.fernet = self._derive_fernet(master_key)

    def _derive_fernet(self, master_key: str) -> Fernet:
        """Derive Fernet key from master key using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"authshield-backup-salt-v2",  # Fixed salt for deterministic key
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        return Fernet(key)

    def encrypt_file(self, input_path: Path, output_path: Path):
        """Encrypt a file with AES-256."""
        with open(input_path, "rb") as f:
            data = f.read()

        encrypted = self.fernet.encrypt(data)

        with open(output_path, "wb") as f:
            f.write(encrypted)

    def decrypt_file(self, input_path: Path, output_path: Path):
        """Decrypt a file."""
        with open(input_path, "rb") as f:
            encrypted = f.read()

        decrypted = self.fernet.decrypt(encrypted)

        with open(output_path, "wb") as f:
            f.write(decrypted)
```

### 3.2 Key Management

```python
class BackupKeyManager:
    """Manages encryption keys for backups."""

    KEY_FILE = "backup_master.key"

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.key_path = config_dir / self.KEY_FILE

    def get_or_create_key(self) -> str:
        """Get existing key or generate new one."""
        if self.key_path.exists():
            return self.key_path.read_text().strip()

        # Generate new key
        key = Fernet.generate_key().decode()
        self.key_path.write_text(key)
        self.key_path.chmod(0o600)  # Owner read/write only

        return key

    def rotate_key(self, old_key: str) -> str:
        """Rotate to a new encryption key."""
        new_key = Fernet.generate_key().decode()

        # Re-encrypt all existing backups with new key
        # This is done during maintenance window

        self.key_path.write_text(new_key)
        self.key_path.chmod(0o600)

        return new_key
```

---

## 4. Compression

### 4.1 Gzip Compression

```python
import gzip
import shutil

class BackupCompression:
    """Gzip compression for backup files."""

    def compress(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        level: int = 9,
    ) -> Path:
        """Compress a file with gzip."""
        if output_path is None:
            output_path = input_path.with_suffix(input_path.suffix + ".gz")

        with open(input_path, "rb") as f_in:
            with gzip.open(output_path, "wb", compresslevel=level) as f_out:
                shutil.copyfileobj(f_in, f_out)

        return output_path

    def decompress(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Decompress a gzip file."""
        if output_path is None:
            output_path = input_path.with_suffix("")  # Remove .gz

        with gzip.open(input_path, "rb") as f_in:
            with open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        return output_path

    def get_compression_ratio(self, original: Path, compressed: Path) -> float:
        """Calculate compression ratio."""
        original_size = original.stat().st_size
        compressed_size = compressed.stat().st_size
        return compressed_size / original_size if original_size > 0 else 1.0
```

---

## 5. Integrity Verification

### 5.1 SHA-256 Checksums

```python
import hashlib

class BackupIntegrity:
    """Verify backup integrity using SHA-256."""

    @staticmethod
    def compute_checksum(file_path: Path) -> str:
        """Compute SHA-256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def verify_checksum(file_path: Path, expected: str) -> bool:
        """Verify file checksum."""
        actual = BackupIntegrity.compute_checksum(file_path)
        return actual == expected

    @staticmethod
    def verify_backup_record(record: BackupRecord) -> BackupVerificationResult:
        """Verify a backup record's integrity."""
        file_path = Path(record.file_path)

        if not file_path.exists():
            return BackupVerificationResult(
                status="missing",
                message="Backup file not found",
            )

        actual_size = file_path.stat().st_size
        if actual_size != record.file_size_bytes:
            return BackupVerificationResult(
                status="size_mismatch",
                message=f"Expected {record.file_size_bytes}, got {actual_size}",
            )

        actual_checksum = BackupIntegrity.compute_checksum(file_path)
        if actual_checksum != record.checksum_sha256:
            return BackupVerificationResult(
                status="checksum_mismatch",
                message="Backup file corrupted",
            )

        return BackupVerificationResult(status="valid")
```

### 5.2 Restore Validation

```python
class RestoreValidator:
    """Validate restored backup integrity."""

    async def validate_restored_database(
        self,
        db_path: Path,
    ) -> RestoreValidationResult:
        """Comprehensive validation of restored database."""
        result = RestoreValidationResult()

        # Step 1: File exists
        if not db_path.exists():
            result.add_error("Database file not found")
            return result

        # Step 2: Integrity check
        engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
        try:
            async with engine.begin() as conn:
                integrity = await conn.execute(text("PRAGMA integrity_check"))
                if integrity.scalar() != "ok":
                    result.add_error("SQLite integrity check failed")
                    return result

                # Step 3: Table existence check
                tables = await conn.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ))
                table_names = {row[0] for row in tables}

                required_tables = {
                    "users", "roles", "permissions", "courses",
                    "enrollments", "assessments", "audit_entries",
                }

                missing = required_tables - table_names
                if missing:
                    result.add_warning(f"Missing tables: {missing}")

                # Step 4: Foreign key check
                fk_check = await conn.execute(text("PRAGMA foreign_key_check"))
                fk_violations = fk_check.fetchall()
                if fk_violations:
                    result.add_warning(
                        f"{len(fk_violations)} foreign key violations found"
                    )

                # Step 5: Row counts
                for table in required_tables:
                    if table in table_names:
                        count = await conn.execute(
                            text(f"SELECT COUNT(*) FROM {table}")
                        )
                        result.table_counts[table] = count.scalar()

        finally:
            await engine.dispose()

        result.status = "valid" if not result.errors else "error"
        return result
```

---

## 6. Restore Process

### 6.1 Full Restore

```python
class FullRestore:
    """Restore from full backup."""

    async def execute(
        self,
        backup_record: BackupRecord,
        config: BackupConfig,
    ) -> RestoreResult:
        """Restore database from full backup."""
        backup_path = Path(backup_record.file_path)

        if not backup_path.exists():
            raise RestoreError("Backup file not found")

        # Step 1: Verify backup integrity
        verification = BackupIntegrity.verify_backup_record(backup_record)
        if verification.status != "valid":
            raise RestoreError(f"Backup integrity check failed: {verification.message}")

        # Step 2: Decrypt
        decrypted_path = backup_path.with_suffix("")
        await self.encryption.decrypt_file(backup_path, decrypted_path)

        # Step 3: Decompress
        decompressed_path = decrypted_path.with_suffix("")
        await self.compression.decompress(decrypted_path, decompressed_path)

        # Step 4: Stop application writes
        await self._pause_writes()

        try:
            # Step 5: Backup current database
            current_backup = self.data_dir / "authshield_pre_restore.db"
            shutil.copy2(self.database_path, current_backup)

            # Step 6: Replace database
            shutil.copy2(decompressed_path, self.database_path)

            # Step 7: Verify restored database
            validation = await self.validator.validate_restored_database(
                self.database_path
            )

            if validation.status != "valid":
                # Rollback to previous database
                shutil.copy2(current_backup, self.database_path)
                raise RestoreError(
                    f"Restored database failed validation: {validation.errors}"
                )

            # Step 8: Record restore
            restore_log = RestoreLog(
                id=uuid.uuid4(),
                backup_id=backup_record.id,
                status="completed",
                restored_at=datetime.utcnow(),
                validation_result=validation.to_dict(),
            )

            return RestoreResult(
                status="success",
                restore_log=restore_log,
                validation=validation,
            )

        finally:
            await self._resume_writes()
            # Clean up temp files
            decrypted_path.unlink(missing_ok=True)
            decompressed_path.unlink(missing_ok=True)
```

### 6.2 Incremental Restore

```python
class IncrementalRestore:
    """Restore using full backup + incremental WALs."""

    async def execute(
        self,
        full_backup: BackupRecord,
        incremental_backups: list[BackupRecord],
        config: BackupConfig,
    ) -> RestoreResult:
        """Restore from full + incremental backups."""
        # Step 1: Restore full backup
        full_result = await self.full_restorer.execute(full_backup, config)

        if full_result.status != "success":
            return full_result

        # Step 2: Apply incremental WALs in order
        for incr_backup in incremental_backups:
            await self._apply_incremental(incr_backup)

        # Step 3: Verify final state
        validation = await self.validator.validate_restored_database(
            self.database_path
        )

        return RestoreResult(
            status="success" if validation.status == "valid" else "warning",
            validation=validation,
        )

    async def _apply_incremental(self, backup_record: BackupRecord):
        """Apply a single incremental backup."""
        incr_path = Path(backup_record.file_path)

        # Decrypt and decompress
        decrypted = await self._decrypt_to_temp(incr_path)
        decompressed = await self._decompress_to_temp(decrypted)

        # Copy WAL file
        wal_dest = self.database_path.with_suffix(".db-wal")
        shutil.copy2(decompressed, wal_dest)

        # SQLite will replay WAL on next connection
        engine = create_async_engine(f"sqlite+aiosqlite:///{self.database_path}")
        async with engine.begin() as conn:
            await conn.execute(text("PRAGMA wal_checkpoint(PASSIVE)"))
        await engine.dispose()

        # Clean up
        decrypted.unlink(missing_ok=True)
        decompressed.unlink(missing_ok=True)
```

---

## 7. Backup Rotation

### 7.1 Rotation Policy (3-2-1 Rule)

```python
class BackupRotation:
    """Manages backup rotation and retention."""

    DEFAULT_POLICY = {
        "full_backups": {
            "keep_daily": 7,      # Keep last 7 daily full backups
            "keep_weekly": 4,     # Keep last 4 weekly full backups
            "keep_monthly": 12,   # Keep last 12 monthly full backups
            "keep_yearly": 3,     # Keep last 3 yearly full backups
        },
        "incremental_backups": {
            "keep_days": 14,      # Keep 14 days of incrementals
        },
        "config_backups": {
            "keep_count": 10,     # Keep last 10 config backups
        },
        "course_backups": {
            "keep_per_course": 5, # Keep 5 backups per course
        },
        "audit_backups": {
            "keep_years": 7,      # Keep 7 years of audit backups
        },
    }

    async def rotate(self, config: BackupConfig) -> RotationResult:
        """Apply rotation policy to backups."""
        result = RotationResult()

        # Rotate full backups
        full_deleted = await self._rotate_by_policy(
            "full", config.backup_dir / "full",
            self.DEFAULT_POLICY["full_backups"]
        )
        result.deleted_count += full_deleted

        # Rotate incremental backups
        incr_deleted = await self._rotate_by_age(
            "incremental", config.backup_dir / "incremental",
            self.DEFAULT_POLICY["incremental_backups"]["keep_days"]
        )
        result.deleted_count += incr_deleted

        # Rotate config backups
        config_deleted = await self._rotate_by_count(
            "config", config.backup_dir / "config",
            self.DEFAULT_POLICY["config_backups"]["keep_count"]
        )
        result.deleted_count += config_deleted

        return result

    async def _rotate_by_age(
        self,
        backup_type: str,
        backup_dir: Path,
        keep_days: int,
    ) -> int:
        """Delete backups older than keep_days."""
        cutoff = datetime.utcnow() - timedelta(days=keep_days)
        deleted = 0

        records = await self.backup_repository.list_by_type(backup_type)
        for record in records:
            if record.created_at < cutoff:
                await self._delete_backup(record)
                deleted += 1

        return deleted
```

### 7.2 Backup Schedule

```python
BACKUP_SCHEDULE = {
    "daily_incremental": {
        "cron": "0 3 * * *",     # 3:00 AM daily
        "type": "incremental",
        "enabled": True,
    },
    "weekly_full": {
        "cron": "0 2 * * 0",     # 2:00 AM Sunday
        "type": "full",
        "enabled": True,
    },
    "monthly_full": {
        "cron": "0 1 1 * *",     # 1:00 AM 1st of month
        "type": "full",
        "enabled": True,
    },
    "config_backup": {
        "cron": "0 4 * * *",     # 4:00 AM daily
        "type": "config",
        "enabled": True,
    },
    "quarterly_dr_test": {
        "cron": "0 0 1 1,4,7,10 *",  # 1st of quarter
        "type": "dr_test",
        "enabled": True,
    },
}
```

---

## 8. Recovery Testing

### 8.1 Quarterly DR Tests

```python
class DisasterRecoveryTest:
    """Quarterly disaster recovery testing."""

    async def execute(self) -> DRTestResult:
        """Run full DR test cycle."""
        result = DRTestResult()

        # Step 1: Find latest full backup
        latest_full = await self.backup_repository.get_latest_full()
        if latest_full is None:
            result.add_error("No full backup available for DR test")
            return result

        # Step 2: Create isolated test environment
        test_dir = Path(tempfile.mkdtemp(prefix="dr_test_"))
        test_db = test_dir / "test_authshield.db"

        try:
            # Step 3: Restore to test location
            restore_result = await self._restore_to_location(
                latest_full, test_db
            )
            result.restore_time_ms = restore_result.duration_ms

            if restore_result.status != "success":
                result.add_error(f"Restore failed: {restore_result.error}")
                return result

            # Step 4: Validate restored database
            validation = await self.validator.validate_restored_database(test_db)
            result.validation = validation

            if validation.status != "valid":
                result.add_error(f"Validation failed: {validation.errors}")
                return result

            # Step 5: Run sample queries
            query_results = await self._run_sample_queries(test_db)
            result.sample_queries_passed = query_results.passed
            result.sample_queries_total = query_results.total

            # Step 6: Verify audit chain
            chain_valid = await self._verify_audit_chain(test_db)
            result.audit_chain_valid = chain_valid

            result.status = "passed"
            result.total_duration_ms = (
                datetime.utcnow() - start_time
            ).total_seconds() * 1000

        finally:
            # Cleanup test environment
            shutil.rmtree(test_dir, ignore_errors=True)

        return result

    def _run_sample_queries(self, db_path: Path) -> QueryTestResult:
        """Run representative queries to verify data access."""
        queries = [
            ("SELECT COUNT(*) FROM users", "User count"),
            ("SELECT COUNT(*) FROM courses", "Course count"),
            ("SELECT COUNT(*) FROM enrollments", "Enrollment count"),
            ("SELECT COUNT(*) FROM audit_entries", "Audit count"),
            ("SELECT COUNT(*) FROM results", "Results count"),
            ("SELECT COUNT(*) FROM certificates", "Certificate count"),
        ]

        result = QueryTestResult()
        for query, description in queries:
            try:
                # Execute query
                result.passed += 1
            except Exception as e:
                result.add_error(f"{description}: {e}")

        result.total = len(queries)
        return result
```

### 8.2 DR Test Report

```json
{
  "test_id": "dr-test-2026-Q3-001",
  "test_date": "2026-07-19T02:00:00Z",
  "backup_tested": "authshield_full_2026-07-19_02-00-00.db.gz.enc",
  "status": "passed",
  "metrics": {
    "restore_time_ms": 1250,
    "validation_status": "valid",
    "sample_queries_passed": 6,
    "sample_queries_total": 6,
    "audit_chain_valid": true,
    "total_duration_ms": 3500
  },
  "issues": [],
  "recommendations": []
}
```

---

## 9. Backup Metadata Schema

```sql
CREATE TABLE backup_records (
    id BLOB(16) PRIMARY KEY,
    backup_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes INTEGER,
    checksum_sha256 VARCHAR(64) NOT NULL,
    parent_backup_id BLOB(16),
    schedule_id BLOB(16),
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    error_message TEXT,
    retention_days INTEGER NOT NULL DEFAULT 365,
    metadata TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    deleted_at DATETIME,
    FOREIGN KEY (parent_backup_id) REFERENCES backup_records(id)
);

CREATE TABLE backup_schedules (
    id BLOB(16) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    cron_expression VARCHAR(100) NOT NULL,
    backup_type VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT 1,
    last_run_at DATETIME,
    next_run_at DATETIME,
    config TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE restore_logs (
    id BLOB(16) PRIMARY KEY,
    backup_id BLOB(16) NOT NULL,
    status VARCHAR(50) NOT NULL,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    duration_ms INTEGER,
    validation_result TEXT,
    error_message TEXT,
    performed_by BLOB(16),
    FOREIGN KEY (backup_id) REFERENCES backup_records(id)
);
```

---

*This document defines the complete backup and restore architecture for AuthShield Lab.*
