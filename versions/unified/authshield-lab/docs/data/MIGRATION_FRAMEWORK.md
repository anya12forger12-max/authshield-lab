# Migration Framework — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Overview

AuthShield Lab uses Alembic for async database migrations. This document defines
the complete migration strategy including schema upgrades, rollbacks, validation,
data migrations, and failure recovery.

### 1.1 Migration Principles

| Principle | Description |
|---|---|
| Async-first | All migrations execute via asyncio |
| Backward compatible | Each migration must support rollback |
| Data-safe | Data migrations are reversible where possible |
| Audited | All migrations logged with timestamps |
| Tested | Every migration has upgrade + downgrade tests |

---

## 2. Alembic Async Configuration

### 2.1 Project Structure

```
migrations/
├── env.py                    # Async migration environment
├── script.py.mako            # Migration script template
├── alembic.ini               # Alembic configuration
└── versions/
    ├── 001_initial_schema.py
    ├── 002_add_mfa_factors.py
    ├── 003_add_competencies.py
    ├── 004_add_plugins.py
    ├── 005_add_localization.py
    ├── 006_add_accessibility.py
    ├── 007_add_analytics.py
    ├── 008_add_backup_system.py
    ├── 009_enhance_audit_chain.py
    ├── 010_add_offline_queue.py
    ├── 011_add_notifications.py
    ├── 012_add_themes.py
    ├── 013_enhance_courses.py
    ├── 014_add_institutions.py
    ├── 015_add_assets.py
    └── ...
```

### 2.2 Environment Configuration

```python
# migrations/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import MetaData
from alembic import context

# Alembic Config
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata
target_metadata = Base.metadata

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

target_metadata.naming_convention = convention


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Required for SQLite ALTER TABLE
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 2.3 Migration Script Template

```python
# migrations/script.py.mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Apply migration."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Reverse migration."""
    ${downgrades if downgrades else "pass"}
```

---

## 3. Schema Upgrade Migrations

### 3.1 Initial Schema Migration

```python
# migrations/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: None
Create Date: 2026-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable WAL mode
    op.execute("PRAGMA journal_mode = WAL")
    op.execute("PRAGMA foreign_keys = ON")

    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.LargeBinary(16), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en"),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("last_login_at", sa.DateTime, nullable=True),
        sa.Column("last_login_ip", sa.String(45), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime, nullable=True),
        sa.Column("email_verified_at", sa.DateTime, nullable=True),
        sa.Column("mfa_enabled", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("mfa_secret", sa.String(255), nullable=True),
        sa.Column("metadata", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.LargeBinary(16), nullable=True),
        sa.Column("updated_by", sa.LargeBinary(16), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("deleted_by", sa.LargeBinary(16), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
    )

    # Create indexes for users
    op.create_index("idx_users_email", "users", ["email"], unique=True,
                    postgresql_where=sa.text("is_deleted = 0"))
    op.create_index("idx_users_status", "users", ["status"],
                    postgresql_where=sa.text("is_deleted = 0"))

    # Roles table
    op.create_table(
        "roles",
        sa.Column("id", sa.LargeBinary(16), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("priority", sa.Integer, nullable=False, server_default="0"),
        sa.Column("metadata", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.LargeBinary(16), nullable=True),
        sa.Column("updated_by", sa.LargeBinary(16), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("deleted_by", sa.LargeBinary(16), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
    )

    # Permissions table
    op.create_table(
        "permissions",
        sa.Column("id", sa.LargeBinary(16), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("metadata", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.LargeBinary(16), nullable=True),
        sa.Column("updated_by", sa.LargeBinary(16), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("deleted_by", sa.LargeBinary(16), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
    )

    # User-Roles junction
    op.create_table(
        "user_roles",
        sa.Column("id", sa.LargeBinary(16), primary_key=True),
        sa.Column("user_id", sa.LargeBinary(16), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role_id", sa.LargeBinary(16), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("assigned_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("assigned_by", sa.LargeBinary(16), nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("metadata", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.LargeBinary(16), nullable=True),
        sa.Column("updated_by", sa.LargeBinary(16), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("deleted_by", sa.LargeBinary(16), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
    )

    # Role-Permissions junction
    op.create_table(
        "role_permissions",
        sa.Column("id", sa.LargeBinary(16), primary_key=True),
        sa.Column("role_id", sa.LargeBinary(16), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("permission_id", sa.LargeBinary(16), sa.ForeignKey("permissions.id"), nullable=False),
        sa.Column("granted_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("granted_by", sa.LargeBinary(16), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.LargeBinary(16), nullable=True),
        sa.Column("updated_by", sa.LargeBinary(16), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("deleted_by", sa.LargeBinary(16), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
    )

    # Continue with courses, modules, lessons, etc...
    # (abbreviated for space — full migration includes all tables)

    # Record schema version
    op.execute(
        "INSERT INTO schema_metadata (key, value) VALUES ('schema_version', '001')"
    )


def downgrade() -> None:
    """Reverse migration."""
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")

    op.execute(
        "DELETE FROM schema_metadata WHERE key = 'schema_version'"
    )
```

### 3.2 Example: Add MFA Factors Migration

```python
# migrations/versions/002_add_mfa_factors.py
"""Add MFA factors table

Revision ID: 002
Revises: 001
Create Date: 2026-02-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mfa_factors",
        sa.Column("id", sa.LargeBinary(16), primary_key=True),
        sa.Column("user_id", sa.LargeBinary(16), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("factor_type", sa.String(50), nullable=False),
        sa.Column("secret_encrypted", sa.String(500), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("last_used_at", sa.DateTime, nullable=True),
        sa.Column("backup_codes_hash", sa.Text, nullable=True),
        sa.Column("metadata", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.LargeBinary(16), nullable=True),
        sa.Column("updated_by", sa.LargeBinary(16), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("deleted_by", sa.LargeBinary(16), nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
    )

    op.create_index("idx_mfa_user_id", "mfa_factors", ["user_id"],
                    postgresql_where=sa.text("is_deleted = 0"))

    # Add MFA columns to users table
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("mfa_enabled", sa.Boolean, nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("mfa_secret", sa.String(255), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("mfa_secret")
        batch_op.drop_column("mfa_enabled")

    op.drop_index("idx_mfa_user_id", table_name="mfa_factors")
    op.drop_table("mfa_factors")
```

---

## 4. Data Migration Migrations

### 4.1 Data Transformation

```python
# migrations/versions/010_data_migrate_user_status.py
"""Data migration: normalize user status values

Revision ID: 010
Revises: 009
Create Date: 2026-06-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Transform status values from old format to new format."""
    connection = op.get_bind()

    # Map old status values to new format
    status_mapping = {
        "Active": "active",
        "Inactive": "inactive",
        "Suspended": "suspended",
        "Pending": "pending",
        "active": "active",
        "inactive": "inactive",
        "suspended": "suspended",
        "pending": "pending",
    }

    # Update each status value
    for old_status, new_status in status_mapping.items():
        if old_status != new_status:
            connection.execute(
                sa.text(
                    "UPDATE users SET status = :new_status "
                    "WHERE status = :old_status AND is_deleted = 0"
                ),
                {"new_status": new_status, "old_status": old_status},
            )

    # Add CHECK constraint for status
    with op.batch_alter_table("users") as batch_op:
        batch_op.create_check_constraint(
            "chk_users_status",
            "status IN ('active', 'inactive', 'suspended', 'pending')"
        )


def downgrade() -> None:
    """Reverse data migration."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("chk_users_status", type_="check")
```

### 4.2 Batch Data Migration (Large Datasets)

```python
# migrations/versions/015_batch_migrate_progress.py
"""Batch data migration: normalize progress records

Revision ID: 015
Revises: 014
Create Date: 2026-07-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None

BATCH_SIZE = 1000


def upgrade() -> None:
    """Batch migrate progress records."""
    connection = op.get_bind()

    # Process in batches to avoid locking
    while True:
        result = connection.execute(
            sa.text(
                "SELECT id FROM progress "
                "WHERE status_old IS NOT NULL "
                "AND is_deleted = 0 "
                "LIMIT :batch_size"
            ),
            {"batch_size": BATCH_SIZE},
        )

        rows = result.fetchall()
        if not rows:
            break

        ids = [row[0] for row in rows]

        # Update batch
        connection.execute(
            sa.text(
                "UPDATE progress SET "
                "status = CASE "
                "  WHEN status_old = 'NOT_STARTED' THEN 'not_started' "
                "  WHEN status_old = 'IN_PROGRESS' THEN 'in_progress' "
                "  WHEN status_old = 'COMPLETED' THEN 'completed' "
                "  ELSE status_old "
                "END, "
                "status_old = NULL, "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE id IN :ids"
            ),
            {"ids": tuple(ids)},
        )

        # Log progress
        print(f"Migrated {len(ids)} progress records")


def downgrade() -> None:
    """Reverse batch migration."""
    connection = op.get_bind()

    connection.execute(
        sa.text(
            "UPDATE progress SET "
            "status_old = UPPER(status), "
            "status = 'unknown' "
            "WHERE is_deleted = 0"
        )
    )
```

---

## 5. Rollback Support

### 5.1 Rollback Strategy

```python
class MigrationRollback:
    """Handles migration rollback operations."""

    async def rollback_to_revision(
        self,
        target_revision: str,
        session: AsyncSession,
    ) -> RollbackResult:
        """Rollback to a specific revision."""
        # Step 1: Verify target revision exists
        if not await self._revision_exists(target_revision):
            raise MigrationError(f"Revision not found: {target_revision}")

        # Step 2: Create backup before rollback
        backup_result = await self._create_pre_rollback_backup(session)

        # Step 3: Execute rollback
        try:
            await self._alembic_downgrade(target_revision)

            # Step 4: Validate rollback
            validation = await self._validate_rollback(target_revision)

            return RollbackResult(
                status="success",
                target_revision=target_revision,
                backup_id=backup_result.record.id,
                validation=validation,
            )

        except Exception as e:
            # Step 5: Restore from backup on failure
            await self._restore_from_backup(backup_result.record)
            raise MigrationError(f"Rollback failed: {e}")

    async def _validate_rollback(self, target_revision: str) -> ValidationResult:
        """Validate database state after rollback."""
        result = ValidationResult()

        # Integrity check
        integrity = await self._check_integrity()
        if integrity != "ok":
            result.add_error(f"Integrity check failed: {integrity}")

        # Check required tables exist
        tables = await self._get_table_names()
        expected = self._get_expected_tables_for_revision(target_revision)
        missing = expected - set(tables)
        if missing:
            result.add_error(f"Missing tables after rollback: {missing}")

        return result
```

### 5.2 Rollback Matrix

```python
ROLLBACK_MATRIX = {
    "002": {
        "description": "Rollback MFA factors",
        "downgrade": "Drop mfa_factors table, remove mfa columns from users",
        "data_loss": "MFA configurations will be lost",
        "pre_check": "Verify no active MFA sessions",
    },
    "003": {
        "description": "Rollback competencies",
        "downgrade": "Drop competency tables, remove user_competencies",
        "data_loss": "User competency records will be lost",
        "pre_check": "Export competency data first",
    },
    "004": {
        "description": "Rollback plugins",
        "downgrade": "Drop plugin tables",
        "data_loss": "Plugin configurations will be lost",
        "pre_check": "Disable all plugins first",
    },
}
```

---

## 6. Version Detection

### 6.1 Alembic Version Table

```sql
-- Alembic manages this table automatically
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
```

### 6.2 Version Checking

```python
class MigrationVersionChecker:
    """Checks and reports migration version status."""

    async def get_current_version(self, session: AsyncSession) -> str:
        """Get current alembic version."""
        result = await session.execute(
            text("SELECT version_num FROM alembic_version")
        )
        row = result.fetchone()
        return row[0] if row else "none"

    async def get_pending_migrations(self, session: AsyncSession) -> list[str]:
        """Get list of pending (not yet applied) migrations."""
        current = await self.get_current_version(session)
        all_revisions = self._get_all_revisions()

        if current == "none":
            return all_revisions

        current_idx = all_revisions.index(current) if current in all_revisions else -1
        return all_revisions[current_idx + 1:]

    async def check_compatibility(
        self,
        session: AsyncSession,
        min_version: str,
    ) -> CompatibilityResult:
        """Check if current version meets minimum requirement."""
        current = await self.get_current_version(session)

        if self._compare_versions(current, min_version) < 0:
            return CompatibilityResult(
                compatible=False,
                current_version=current,
                required_version=min_version,
                message=f"Database version {current} < required {min_version}",
            )

        return CompatibilityResult(
            compatible=True,
            current_version=current,
            required_version=min_version,
        )
```

---

## 7. Migration Validation

### 7.1 Pre-Migration Checks

```python
class PreMigrationValidator:
    """Validates database state before migration."""

    async def validate(
        self,
        target_revision: str,
        session: AsyncSession,
    ) -> ValidationResult:
        """Run pre-migration validation."""
        result = ValidationResult()

        # 1. Integrity check
        integrity = await session.execute(text("PRAGMA integrity_check"))
        if integrity.scalar() != "ok":
            result.add_error("Database integrity check failed")
            return result

        # 2. Foreign key check
        fk_check = await session.execute(text("PRAGMA foreign_key_check"))
        fk_violations = fk_check.fetchall()
        if fk_violations:
            result.add_warning(f"{len(fk_violations)} foreign key violations found")

        # 3. Disk space check
        disk_space = await self._check_disk_space()
        if disk_space < 100 * 1024 * 1024:  # Less than 100MB
            result.add_warning(f"Low disk space: {disk_space / 1024 / 1024:.1f} MB")

        # 4. WAL size check
        wal_size = await self._check_wal_size(session)
        if wal_size > 50 * 1024 * 1024:  # Greater than 50MB
            result.add_warning(f"WAL file large: {wal_size / 1024 / 1024:.1f} MB")

        # 5. Lock check
        lock_status = await self._check_locks(session)
        if lock_status.has_locks:
            result.add_error("Active locks detected — cannot migrate")

        return result
```

### 7.2 Post-Migration Validation

```python
class PostMigrationValidator:
    """Validates database state after migration."""

    async def validate(
        self,
        applied_revision: str,
        session: AsyncSession,
    ) -> ValidationResult:
        """Run post-migration validation."""
        result = ValidationResult()

        # 1. Integrity check
        integrity = await session.execute(text("PRAGMA integrity_check"))
        if integrity.scalar() != "ok":
            result.add_error("Database integrity check failed after migration")

        # 2. Version check
        version = await self._get_current_version(session)
        if version != applied_revision:
            result.add_error(
                f"Version mismatch: expected {applied_revision}, got {version}"
            )

        # 3. Table existence check
        expected_tables = self._get_expected_tables(applied_revision)
        actual_tables = await self._get_table_names(session)
        missing = expected_tables - set(actual_tables)
        if missing:
            result.add_error(f"Missing tables: {missing}")

        # 4. Index existence check
        expected_indexes = self._get_expected_indexes(applied_revision)
        actual_indexes = await self._get_index_names(session)
        missing_indexes = expected_indexes - set(actual_indexes)
        if missing_indexes:
            result.add_warning(f"Missing indexes: {missing_indexes}")

        # 5. Data sampling
        sample_result = await self._sample_data(session)
        if not sample_result.passed:
            result.add_error(f"Data sampling failed: {sample_result.error}")

        return result
```

---

## 8. Compatibility Matrix

```python
COMPATIBILITY_MATRIX = {
    # Format Version: (min_migration, max_migration, notes)
    "1.0.0": ("001", "009", "Initial release"),
    "1.1.0": ("001", "012", "Added localization and themes"),
    "1.2.0": ("001", "015", "Added institutions and assets"),
    "2.0.0": ("001", None, "Current version"),
}

class CompatibilityMatrix:
    """Manages version compatibility."""

    def get_compatible_range(self, app_version: str) -> tuple[str, Optional[str]]:
        """Get compatible migration range for app version."""
        return COMPATIBILITY_MATRIX.get(app_version, ("001", None))

    def check_migration_compatibility(
        self,
        migration_version: str,
        app_version: str,
    ) -> bool:
        """Check if migration is compatible with app version."""
        min_rev, max_rev, _ = COMPATIBILITY_MATRIX.get(
            app_version, ("001", None)
        )

        if migration_version < min_rev:
            return False
        if max_rev and migration_version > max_rev:
            return False
        return True
```

---

## 9. Failure Recovery

### 9.1 Migration Failure Handler

```python
class MigrationFailureHandler:
    """Handles migration failures gracefully."""

    async def handle_failure(
        self,
        error: Exception,
        migration_revision: str,
        session: AsyncSession,
    ) -> RecoveryResult:
        """Handle migration failure."""
        # 1. Log the failure
        await self._log_failure(error, migration_revision)

        # 2. Check if partial migration occurred
        current_version = await self._get_current_version(session)
        partial = current_version != migration_revision

        if partial:
            # 3a. Partial migration — rollback
            logger.error(f"Partial migration detected. Rolling back to {current_version}")
            rollback_result = await self._rollback_to_safety(session)

            return RecoveryResult(
                status="rolled_back",
                error=str(error),
                rolled_back_to=rollback_result.target_revision,
            )
        else:
            # 3b. Migration not started — just report error
            return RecoveryResult(
                status="failed",
                error=str(error),
                recommendation="Check migration script for errors",
            )

    async def _rollback_to_safety(self, session: AsyncSession) -> RollbackResult:
        """Rollback to last known good state."""
        # Find last successful migration
        last_good = await self._find_last_successful_migration(session)

        # Execute rollback
        await self._alembic_downgrade(last_good)

        return RollbackResult(
            target_revision=last_good,
            status="success",
        )
```

---

## 10. Audit Logging

### 10.1 Migration Audit Trail

```python
class MigrationAuditor:
    """Logs all migration operations."""

    async def log_migration_start(
        self,
        revision: str,
        direction: str,
        actor: Optional[str] = None,
    ):
        """Log migration start."""
        entry = AuditEntry(
            action=f"migration.{direction}.start",
            entity_type="schema",
            entity_id=revision,
            metadata=json.dumps({
                "direction": direction,
                "actor": actor or "system",
                "started_at": datetime.utcnow().isoformat(),
            }),
        )
        await self.session.add(entry)
        await self.session.flush()

    async def log_migration_complete(
        self,
        revision: str,
        direction: str,
        duration_ms: float,
        success: bool,
        error: Optional[str] = None,
    ):
        """Log migration completion."""
        entry = AuditEntry(
            action=f"migration.{direction}.complete",
            entity_type="schema",
            entity_id=revision,
            metadata=json.dumps({
                "direction": direction,
                "duration_ms": duration_ms,
                "success": success,
                "error": error,
                "completed_at": datetime.utcnow().isoformat(),
            }),
        )
        await self.session.add(entry)
        await self.session.flush()
```

---

## 11. Zero-Downtime Strategy

### 11.1 Additive-Only Migrations

```python
# Safe migration pattern: additive-only changes
def upgrade() -> None:
    """Additive migration — no breaking changes."""
    # Add new column with default
    op.add_column(
        "users",
        sa.Column("new_field", sa.String(100), nullable=True, server_default="default"),
    )

    # Add new table
    op.create_table(
        "new_feature",
        sa.Column("id", sa.LargeBinary(16), primary_key=True),
        # ...
    )

    # Add new index
    op.create_index("idx_new_feature", "new_feature", ["column_name"])


def downgrade() -> None:
    """Reverse additive migration."""
    op.drop_index("idx_new_feature", table_name="new_feature")
    op.drop_table("new_feature")
    op.drop_column("users", "new_field")
```

### 11.2 Two-Phase Migration Pattern

```python
# Phase 1: Add new structure (backward compatible)
def upgrade_phase1() -> None:
    """Phase 1: Add new column."""
    op.add_column(
        "users",
        sa.Column("email_normalized", sa.String(255), nullable=True),
    )

# Phase 2: Populate data (after code deployment)
def upgrade_phase2() -> None:
    """Phase 2: Populate normalized emails."""
    op.execute(
        "UPDATE users SET email_normalized = LOWER(email) "
        "WHERE email_normalized IS NULL AND is_deleted = 0"
    )

# Phase 3: Enforce constraint (after all data migrated)
def upgrade_phase3() -> None:
    """Phase 3: Make column NOT NULL."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "email_normalized",
            nullable=False,
            server_default="",
        )
```

---

*This document defines the complete migration framework for AuthShield Lab.*
