# SQLAlchemy 2.0 Standards — AuthShield Lab

This document defines the coding standards for all SQLAlchemy usage in the
AuthShield Lab project. We use SQLAlchemy 2.0 with async sessions and SQLite.

---

## 1. Engine & Session Setup

### 1.1 Engine configuration

```python
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def create_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},  # SQLite-specific
    )
```

### 1.2 Session factory

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
```

### 1.3 Session-per-request dependency

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Rules

- Always use `expire_on_commit=False` to avoid lazy-load issues after commit.
- Always commit/rollback in a `try/except` block.
- Never store a session on a class instance; pass it as a parameter.

---

## 2. Model Conventions

### 2.1 Base class

Define a single `Base` using `DeclarativeBase` with a common set of mixins.

```python
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
```

### 2.2 Model definition

```python
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="viewer", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    api_keys: Mapped[list["ApiKey"]] = relationship(
        back_populates="user",
        lazy="selectin",
    )
```

### 2.3 Naming conventions

| Element          | Convention            | Example                    |
| ---------------- | --------------------- | -------------------------- |
| Model class      | `PascalCase`, singular | `User`, `AuditLog`        |
| `__tablename__`  | `snake_case`, plural   | `users`, `audit_logs`     |
| Column attribute | `snake_case`           | `created_at`, `user_id`   |
| Foreign key      | `{referenced}_id`      | `user_id`                 |
| Relationship     | Plural for collections, singular for single | `users`, `user` |

---

## 3. Relationship Patterns

### 3.1 Lazy loading strategies

| Strategy     | Use case                                           |
| ------------ | -------------------------------------------------- |
| `"select"`   | Default. Lazy load on access. Not recommended for async. |
| `"selectin"` | Eagerly load collections via `SELECT ... WHERE IN`. Best for lists. |
| `"joined"`   | Eagerly load via `JOIN`. Good for single related objects. |
| `"subquery"` | Like joined, but uses a subquery. Rarely needed.   |
| `"raise"`    | Raise an error if accessed. Use to enforce explicit loading. |

### 3.2 Recommended patterns

```python
class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    api_keys: Mapped[list["ApiKey"]] = relationship(
        back_populates="user",
        lazy="selectin",
    )
    profile: Mapped["Profile | None"] = relationship(
        back_populates="user",
        lazy="joined",
    )
    # Use "raise" for expensive or optional relationships
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
        lazy="raise",
    )
```

### 3.3 Explicit loading in queries

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload


stmt = (
    select(User)
    .where(User.is_active.is_(True))
    .options(selectinload(User.api_keys))
)
result = await session.execute(stmt)
users = result.scalars().all()
```

---

## 4. Query Patterns

Always use the 2.0-style `select()` API. Never use the legacy `session.query()`.

### 4.1 Basic select

```python
stmt = select(User).where(User.is_active.is_(True)).order_by(User.created_at.desc())
result = await session.execute(stmt)
users = result.scalars().all()
```

### 4.2 Single row

```python
stmt = select(User).where(User.id == user_id)
result = await session.execute(stmt)
user = result.scalar_one_or_none()
```

### 4.3 Aggregations

```python
from sqlalchemy import func

stmt = select(func.count(User.id)).where(User.role == "admin")
admin_count = await session.scalar(stmt)
```

### 4.4 Inserts

```python
user = User(username="alice", email="alice@example.com")
session.add(user)
await session.flush()  # get the generated id without committing
```

### 4.5 Bulk inserts

```python
users = [User(username=f"user_{i}", email=f"user_{i}@example.com") for i in range(100)]
session.add_all(users)
await session.flush()
```

### 4.6 Updates

```python
from sqlalchemy import update

stmt = (
    update(User)
    .where(User.role == "viewer")
    .values(role="viewer_readonly")
    .execution_options(synchronize_session="fetch")
)
await session.execute(stmt)
```

### 4.7 Deletes

```python
from sqlalchemy import delete

stmt = delete(ApiKey).where(ApiKey.user_id == user_id)
await session.execute(stmt)
```

---

## 5. Index Strategy

### 5.1 Single-column indexes

Define indexes on the model using `Index` in `__table_args__`.

```python
class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    actor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)

    __table_args__ = (
        Index("idx_audit_logs_actor_id", "actor_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_created_at", "created_at"),
    )
```

### 5.2 Composite indexes

```python
__table_args__ = (
    Index("idx_audit_logs_actor_action", "actor_id", "action"),
    Index("idx_audit_logs_created_at_actor", "created_at", "actor_id"),
)
```

### 5.3 Index naming

Pattern: `idx_{table}_{column(s)}`

| Table        | Columns                  | Index name                                  |
| ------------ | ------------------------ | ------------------------------------------- |
| `users`      | `email`                  | `idx_users_email`                           |
| `audit_logs` | `actor_id`, `action`     | `idx_audit_logs_actor_action`               |
| `api_keys`   | `user_id`, `is_active`   | `idx_api_keys_user_id_is_active`            |

---

## 6. Migration Strategy (Alembic)

### 6.1 Setup

```
alembic/
├── env.py
├── script.py.mako
└── versions/
    ├── 001_create_users.py
    ├── 002_create_api_keys.py
    └── 003_add_user_role_index.py
```

### 6.2 Migration naming

Pattern: `{sequence}_{description}.py`

- Use lowercase snake_case for the description.
- Sequence is zero-padded to 3 digits.
- Each migration must be idempotent where possible.

### 6.3 Rules

- Every model change must have a corresponding Alembic migration.
- Never edit an existing migration that has been merged to `main`.
- Always test both upgrade and downgrade paths.
- Use `batch_alter_table` for SQLite schema changes that alter existing
  tables (SQLite has limited ALTER TABLE support).

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("phone", sa.String(32), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("phone")
```

---

## 7. Soft Delete Pattern

Use a `deleted_at` timestamp column instead of physically deleting rows.

```python
class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
    )

    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class User(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"
    # ...


class UserManager:
    async def soft_delete(self, session: AsyncSession, user: User) -> None:
        user.deleted_at = datetime.now(timezone.utc)
        await session.flush()

    async def get_active(self, session: AsyncSession, user_id: str) -> User | None:
        stmt = select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
```

### Filter convention

Always filter out soft-deleted rows explicitly. Never rely on application-level
filtering alone — add a query helper.

```python
def active_only(stmt: Select) -> Select:
    return stmt.where(
        column("deleted_at").is_(None)  # or use the model's column
    )
```

---

## 8. Audit Trail Pattern

Every mutation to critical data must create an audit log entry.

```python
class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    actor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_audit_logs_actor_id", "actor_id"),
        Index("idx_audit_logs_resource", "resource_type", "resource_id"),
        Index("idx_audit_logs_created_at", "created_at"),
    )


async def log_audit(
    session: AsyncSession,
    *,
    actor_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    old_value: str | None = None,
    new_value: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    entry = AuditLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_value=old_value,
        new_value=new_value,
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    session.add(entry)
    return entry
```

---

## 9. UUID Primary Keys

Use UUIDs as primary keys for all tables. Store as `String(36)` (UUID
representation) since SQLite does not have a native UUID type.

```python
from uuid import uuid4


class UUIDPrimaryKeyMixin:
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
```

### Rules

- Generate UUIDs at the application layer, not in the database.
- Use UUIDv4 for random identifiers.
- Use UUIDv7 (time-ordered) for identifiers that will be sorted or indexed
  for range queries.
- Always serialize UUIDs as strings in JSON responses.

---

## 10. JSON Column Patterns

SQLite does not have a native JSON column type. Store JSON as `Text` and
handle serialization at the application layer.

```python
import json

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column


class SettingsMixin:
    settings_json: Mapped[str] = mapped_column(
        Text,
        default="{}",
        nullable=False,
    )

    @hybrid_property
    def settings(self) -> dict[str, Any]:
        return json.loads(self.settings_json)

    @settings.setter
    def settings(self, value: dict[str, Any]) -> None:
        self.settings_json = json.dumps(value)


class User(UUIDPrimaryKeyMixin, TimestampMixin, SettingsMixin, Base):
    __tablename__ = "users"
    # ...
```

### Querying JSON fields

```python
# SQLite JSON functions
from sqlalchemy import func, text

# Find users with a specific setting
stmt = select(User).where(
    text("json_extract(settings_json, '$.theme') = :theme")
).params(theme="dark")
```

### Rules

- Validate JSON structure using Pydantic models at the application boundary.
- Never store sensitive data (passwords, tokens) in JSON columns.
- Keep JSON columns small; prefer normalized tables for frequently queried data.
