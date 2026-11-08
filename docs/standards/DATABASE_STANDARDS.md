# Database Design Standards — AuthShield Lab

This document defines the standards for database schema design, configuration,
migrations, and optimization in the AuthShield Lab project. The project uses
SQLite as its primary database.

---

## 1. SQLite Configuration

### 1.1 Pragma settings

Apply these pragmas on every connection. Use SQLAlchemy's `event` system or
connection hooks.

```python
from sqlalchemy import event, text


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-64000")  # 64 MB
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()
```

### 1.2 Pragma reference

| Pragma            | Value       | Purpose                                            |
| ----------------- | ----------- | -------------------------------------------------- |
| `journal_mode`    | `WAL`       | Write-Ahead Logging for concurrent reads/writes    |
| `foreign_keys`    | `ON`        | Enforce referential integrity constraints          |
| `busy_timeout`    | `5000`      | Wait up to 5 seconds before returning SQLITE_BUSY  |
| `synchronous`     | `NORMAL`    | Balance between safety and performance in WAL mode |
| `cache_size`      | `-64000`    | 64 MB page cache (negative = KB)                   |
| `temp_store`      | `MEMORY`    | Store temp tables in memory                        |

### 1.3 Connection pooling

- Use SQLAlchemy's `StaticPool` for single-threaded scenarios.
- Use `NullPool` for testing to ensure fresh connections.
- SQLite connections must NOT be shared across threads. Use
  `check_same_thread=False` only when SQLAlchemy guarantees thread safety via
  its pool.

---

## 2. Table Naming Conventions

| Rule              | Convention            | Example              |
| ----------------- | --------------------- | -------------------- |
| Table name        | `snake_case`, plural   | `users`, `api_keys`  |
| Junction table    | `{table1}_{table2}`   | `user_roles`         |
| Prefix            | None (avoid prefixes) | ~~`tbl_users`~~      |
| Reserved words    | Avoid                 | ~~`order`~~, ~~`group`~~ |

---

## 3. Column Naming Conventions

| Element           | Convention              | Example                   |
| ----------------- | ----------------------- | ------------------------- |
| Regular column    | `snake_case`            | `username`, `created_at`  |
| Foreign key       | `{referenced}_id`       | `user_id`, `actor_id`     |
| Boolean           | `is_` / `has_` prefix  | `is_active`, `has_2fa`    |
| Timestamp         | `{event}_at`            | `created_at`, `deleted_at`|
| Counter           | `{noun}_count`          | `login_count`, `retry_count` |
| JSON blob         | `{name}_json`           | `settings_json`, `metadata_json` |
| Type column       | `{noun}_type`           | `notification_type`       |

---

## 4. Index Naming Conventions

Pattern: `idx_{table}_{column(s)}`

| Type           | Pattern                            | Example                              |
| -------------- | ---------------------------------- | ------------------------------------ |
| Single column  | `idx_{table}_{column}`             | `idx_users_email`                    |
| Composite      | `idx_{table}_{col1}_{col2}`        | `idx_audit_logs_actor_action`        |
| Partial/filter | `idx_{table}_{column}_{filter}`    | `idx_users_active_email`             |

Rules:
- Index names must be unique across the database.
- Always create indexes in migration files, not ad-hoc.
- Use lowercase snake_case for index names.

---

## 5. Constraint Naming Conventions

### 5.1 Primary key

Pattern: `pk_{table}` (SQLite auto-generates if not specified)

```sql
-- Implicit
id TEXT PRIMARY KEY

-- Explicit (preferred for clarity)
CONSTRAINT pk_users PRIMARY KEY (id)
```

### 5.2 Foreign key

Pattern: `fk_{table}_{column}`

```sql
CONSTRAINT fk_api_keys_user_id FOREIGN KEY (user_id) REFERENCES users(id)
```

### 5.3 Check constraint

Pattern: `ck_{table}_{constraint_description}`

```sql
CONSTRAINT ck_users_role CHECK (role IN ('admin', 'editor', 'viewer'))
CONSTRAINT ck_users_email CHECK (email LIKE '%@%.%')
```

### 5.4 Unique constraint

Pattern: `uq_{table}_{column(s)}`

```sql
CONSTRAINT uq_users_username UNIQUE (username)
CONSTRAINT uq_users_email UNIQUE (email)
```

---

## 6. Migration Conventions (Alembic)

### 6.1 Directory structure

```
alembic/
├── env.py
├── script.py.mako
└── versions/
    ├── 001_initial_schema.py
    ├── 002_create_audit_logs.py
    ├── 003_add_user_indexes.py
    └── 004_add_settings_column.py
```

### 6.2 Naming

Pattern: `{sequence}_{description}.py`

- Sequence: Zero-padded 3-digit integer.
- Description: Lowercase snake_case, concise.
- Each migration must be reversible (`upgrade()` and `downgrade()`).

### 6.3 SQLite-specific rules

- Use `batch_alter_table()` for all `ALTER TABLE` operations on existing
  tables, because SQLite has limited ALTER TABLE support.
- New tables with all columns can use standard `op.create_table()`.
- Never drop and recreate a table to add a column.

```python
def upgrade() -> None:
    # New table — standard create
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
    )

    # Alter existing table — batch mode
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("phone", sa.String(32), nullable=True))
        batch_op.create_index("idx_users_phone", ["phone"])


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_index("idx_users_phone")
        batch_op.drop_column("phone")

    op.drop_table("notifications")
```

### 6.4 Rules

- Every model change must have a corresponding migration.
- Never modify an existing migration file that has been applied to production.
- Test both `upgrade()` and `downgrade()` paths before merging.
- Use `op.execute()` for raw SQL when Alembic helpers are insufficient.
- Add comments to migrations explaining non-obvious changes.

---

## 7. Seed Data Management

### 7.1 Location

Seed data lives in `authshield/db/seeds/`.

```
authshield/db/seeds/
├── __init__.py
├── roles.py
├── default_admin.py
└── permissions.py
```

### 7.2 Idempotent seeding

All seed functions must be idempotent — safe to run multiple times without
creating duplicates.

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def seed_roles(session: AsyncSession) -> None:
    roles = [
        {"name": "admin", "description": "Full system access"},
        {"name": "editor", "description": "Can edit resources"},
        {"name": "viewer", "description": "Read-only access"},
    ]
    for role_data in roles:
        existing = await session.execute(
            select(Role).where(Role.name == role_data["name"])
        )
        if existing.scalar_one_or_none() is None:
            session.add(Role(**role_data))
    await session.flush()
```

### 7.3 Rules

- Seed data must never contain real credentials.
- Use environment variables for any sensitive seed values.
- Seed functions are called from Alembic migrations or a CLI command.
- Document each seed file with its purpose and dependencies.

---

## 8. Backup Strategy

### 8.1 Backup approach

Since SQLite is a single file, backups are performed by copying the database
file.

```bash
# Hot backup using SQLite backup API (via Python)
python -m authshield.db.backup --output /backups/authshield_$(date +%Y%m%d).db

# Or file-level copy (requires WAL checkpoint first)
sqlite3 authshield.db "PRAGMA wal_checkpoint(TRUNCATE);"
cp authshield.db /backups/authshield_$(date +%Y%m%d).db
```

### 8.2 Backup schedule

| Frequency | Retention  | Storage           |
| --------- | ---------- | ----------------- |
| Hourly    | 24 hours   | Local disk        |
| Daily     | 30 days    | Local + cloud     |
| Weekly    | 12 weeks   | Cloud (cold)      |
| Monthly   | 12 months  | Cloud (archive)   |

### 8.3 Restore procedure

1. Stop the application.
2. Copy the backup file to the database location.
3. Verify integrity: `PRAGMA integrity_check;`
4. Restart the application.
5. Verify data via application health checks.

### 8.4 Rules

- Test backup restoration quarterly.
- Store backups in a different physical location from the primary database.
- Encrypt backups that contain sensitive data.
- Log all backup and restore operations.

---

## 9. Performance Optimization

### 9.1 Index strategy

- Create indexes for columns used in `WHERE` clauses, `JOIN` conditions, and
  `ORDER BY` clauses.
- Avoid over-indexing; each index slows down writes.
- Use composite indexes for queries that filter on multiple columns.

```sql
-- Good: composite index for common query pattern
CREATE INDEX idx_audit_logs_actor_created
ON audit_logs (actor_id, created_at DESC);

-- Bad: redundant index when composite exists
CREATE INDEX idx_audit_logs_actor_id ON audit_logs (actor_id);
```

### 9.2 EXPLAIN usage

Always run `EXPLAIN QUERY PLAN` for slow queries during development.

```python
async def debug_query(session: AsyncSession, stmt: Select) -> None:
    explain_stmt = f"EXPLAIN QUERY PLAN {stmt.compile(compile_kwargs={'literal_binds': True})}"
    result = await session.execute(text(explain_stmt))
    for row in result:
        print(row)
```

### 9.3 Query optimization rules

- Select only the columns you need; avoid `SELECT *`.
- Use `LIMIT` for paginated queries.
- Use `subqueryload` / `selectinload` instead of lazy loading in loops.
- Batch inserts using `session.add_all()` or `executemany()`.
- Avoid `N+1` query patterns — load relationships eagerly or with explicit
  options.

### 9.4 WAL mode benefits

WAL (Write-Ahead Logging) mode allows:
- Concurrent reads while a write is in progress.
- Better performance for read-heavy workloads.
- Crash recovery without data loss.

Always ensure WAL mode is enabled at connection time.

### 9.5 Connection management

- Never hold a connection open longer than necessary.
- Use context managers for all database operations.
- Close cursors explicitly when using raw DBAPI connections.
- Monitor connection pool usage in production.
