# Python Style Guide — AuthShield Lab

This document defines the coding standards for all Python code in the AuthShield Lab
project. Every pull request must conform to these rules. CI enforces them via Ruff,
mypy, and pre-commit hooks.

---

## 1. Toolchain

| Tool   | Purpose                    | Key settings                            |
| ------ | -------------------------- | --------------------------------------- |
| Ruff   | Linting + formatting       | line-length 88, double quotes, target py312 |
| isort  | Import sorting             | Managed via Ruff (`[tool.ruff.lint.isort]`) |
| mypy   | Static type checking       | strict mode, python_version 3.12        |
| Black  | Formatting (superseded by Ruff) | Ruff format replaces Black          |

### Ruff configuration (`pyproject.toml`)

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "S", "B", "A", "C4", "SIM", "TCH", "RUF"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["authshield"]
force-single-line = true
lines-after-imports = 1
```

---

## 2. PEP 8 Enforcement

Ruff enforces PEP 8 with the following project-specific overrides:

- **Line length**: 88 characters (Ruff default). Strings may exceed this when
  splitting would reduce readability.
- **Trailing commas**: Always include trailing commas in multi-line collections and
  function signatures. Ruff format handles insertion automatically.
- **Quotes**: Double quotes everywhere. Single quotes only inside double-quoted
  strings or when the string contains a double-quote character.

```python
# Correct
users = [
    "alice",
    "bob",
    "charlie",
]

config = {
    "timeout": 30,
    "retries": 3,
}

# Incorrect
users = ["alice", "bob", "charlie"]
config = {"timeout": 30, "retries": 3}
```

---

## 3. Type Hints

### 3.1 General rules

- Every function signature must have complete type annotations (parameters and
  return type).
- Use `from __future__ import annotations` in every module to enable PEP 604 union
  syntax (`X | Y`) and forward references.
- Never use `Optional[X]`; use `X | None` instead.
- Never use `List`, `Dict`, `Tuple` from `typing`; use the built-in generics
  (`list`, `dict`, `tuple`) since we target Python 3.12+.

```python
from __future__ import annotations


def get_user(user_id: UUID) -> User | None:
    ...


async def create_audit_log(
    *,
    action: str,
    actor_id: UUID,
    metadata: dict[str, str] | None = None,
) -> AuditLog:
    ...
```

### 3.2 Pydantic v2 models

All request/response payloads and internal DTOs use Pydantic v2 `BaseModel`.

```python
from pydantic import BaseModel, Field, field_validator


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-z0-9_]+$")
    email: str = Field(..., max_length=255)
    role: str = Field(default="viewer")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

### 3.3 TypedDict

Use `TypedDict` when representing structured dictionaries that are not API
payloads (e.g., config dicts, typed kwargs).

```python
from typing import TypedDict


class SMTPConfig(TypedDict):
    host: str
    port: int
    username: str
    password: str
    use_tls: bool
```

### 3.4 Protocol and Generic

Use `Protocol` for structural subtyping and `Generic` for reusable type-parameterized
classes.

```python
from typing import Protocol, TypeVar, Generic


class CacheBackend(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str, ttl: int) -> None: ...


T = TypeVar("T")


class Repository(Generic[T]):
    async def get_by_id(self, id: UUID) -> T | None: ...
    async def save(self, entity: T) -> T: ...
    async def delete(self, entity: T) -> None: ...
```

---

## 4. Dataclass Patterns

Use `@dataclass` for simple value objects. Prefer `frozen=True` and `slots=True`
for immutability and memory efficiency.

```python
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class TokenPayload:
    sub: UUID
    exp: datetime
    iat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    jti: UUID = field(default_factory=uuid4)
    scopes: tuple[str, ...] = ()
```

### Rules

- Always use `frozen=True` unless the dataclass is intentionally mutable.
- Always use `slots=True` for memory efficiency.
- Use `field(default_factory=...)` for mutable defaults (list, dict, set).
- Never use bare mutable defaults like `field(default=[])`.

---

## 5. Async/Await Patterns

### 5.1 Async session management

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 5.2 Async generators

```python
async def stream_audit_logs(
    *,
    start: datetime,
    end: datetime,
) -> AsyncGenerator[AuditLog, None]:
    async with async_session_factory() as session:
        stmt = (
            select(AuditLog)
            .where(AuditLog.created_at.between(start, end))
            .order_by(AuditLog.created_at)
        )
        result = await session.stream(stmt)
        async for row in result:
            yield row.scalar()
```

### 5.3 Concurrency patterns

Use `asyncio.gather` for parallel independent I/O. Use `asyncio.TaskGroup`
(Python 3.11+) for structured concurrency with automatic cancellation.

```python
import asyncio


async def enrich_user(user: User) -> EnrichedUser:
    async with asyncio.TaskGroup() as tg:
        roles_task = tg.create_task(fetch_roles(user.id))
        permissions_task = tg.create_task(fetch_permissions(user.id))
        profile_task = tg.create_task(fetch_profile(user.id))

    return EnrichedUser(
        user=user,
        roles=roles_task.result(),
        permissions=permissions_task.result(),
        profile=profile_task.result(),
    )
```

---

## 6. Context Managers

### 6.1 Async context managers

```python
from contextlib import asynccontextmanager


@asynccontextmanager
async def transactional_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 6.2 ExitStack for dynamic resource management

```python
from contextlib import ExitStack


def process_files(paths: list[Path]) -> None:
    with ExitStack() as stack:
        files = [stack.enter_context(open(p)) for p in paths]
        for f in files:
            process(f)
```

---

## 7. Error Handling

### 7.1 Custom exception hierarchy

All application exceptions inherit from `AuthShieldException`. See
`ERROR_HANDLING.md` for the full hierarchy.

```python
class AuthShieldException(Exception):
    """Base exception for all AuthShield errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AuthShieldException):
    def __init__(self, resource: str, identifier: str | UUID) -> None:
        super().__init__(
            f"{resource} '{identifier}' not found",
            code="NOT_FOUND",
            status_code=404,
        )


class ConflictError(AuthShieldException):
    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(message, code="CONFLICT", status_code=409, details=details)
```

### 7.2 Structured logging

```python
import logging
import uuid

logger = logging.getLogger(__name__)


async def transfer_funds(source_id: UUID, dest_id: UUID, amount: Decimal) -> None:
    correlation_id = str(uuid.uuid4())
    logger.info(
        "transfer.initiated",
        extra={
            "correlation_id": correlation_id,
            "source_id": str(source_id),
            "dest_id": str(dest_id),
            "amount": str(amount),
        },
    )
    # ...
```

---

## 8. Docstrings

Use Google-style docstrings. All public functions, classes, and modules must have
docstrings. Private helpers (`_name`) may omit them.

```python
def calculate_risk_score(
    login_event: LoginEvent,
    historical_events: list[LoginEvent],
    *,
    threshold: float = 0.75,
) -> float:
    """Calculate the risk score for a login attempt.

    Compares the current login event against historical patterns to
    produce a score between 0.0 (safe) and 1.0 (certain fraud).

    Args:
        login_event: The current login attempt to evaluate.
        historical_events: Past login events for the same user,
            ordered chronologically.
        threshold: Minimum score at which the login is flagged.

    Returns:
        Risk score as a float in [0.0, 1.0].

    Raises:
        ValueError: If ``historical_events`` is empty.
    """
```

---

## 9. Import Ordering

Ruff enforces import ordering. The canonical order is:

1. `__future__` imports
2. Standard library
3. Third-party packages
4. First-party (`authshield.*`)
5. Local relative imports

Separate each group with a blank line. Alphabetize within each group.

```python
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authshield.db.models import User
from authshield.services.user_service import UserService
```

---

## 10. Naming Conventions

| Element            | Convention        | Example                          |
| ------------------ | ----------------- | -------------------------------- |
| Module             | `snake_case`      | `user_service.py`                |
| Package            | `snake_case`      | `authshield/api/`                |
| Class              | `PascalCase`      | `UserRepository`                 |
| Function / method  | `snake_case`      | `get_active_users()`             |
| Variable           | `snake_case`      | `login_count`                    |
| Constant           | `UPPER_SNAKE_CASE`| `MAX_RETRY_COUNT`                |
| Private attribute  | `_leading_underscore` | `_cache: dict`               |
| Protected method   | `_leading_underscore` | `_validate_input()`          |
| Type variable      | `PascalCase`      | `T`, `ModelT`                    |
| Pydantic model     | `PascalCase`      | `UserCreateRequest`              |
| Exception class    | `PascalCase` + `Error`/`Exception` | `NotFoundError` |
| Boolean variable   | `is_`/`has_`/`can_` prefix | `is_active`, `has_permission` |
| SQLAlchemy model   | `PascalCase`, singular | `User`, `AuditLog`           |
| DB table           | `snake_case`, plural | `users`, `audit_logs`          |
| DB column          | `snake_case`      | `created_at`, `user_id`          |
| API endpoint path  | `kebab-case`      | `/api/v1/audit-logs/`            |

---

## 11. Anti-Patterns to Avoid

### Mutable default arguments

```python
# WRONG
def add_role(role: str, permissions: list[str] = []) -> None:
    permissions.append(role)

# CORRECT
def add_role(role: str, permissions: list[str] | None = None) -> None:
    permissions = permissions or []
    permissions.append(role)
```

### Bare except clauses

```python
# WRONG
try:
    do_something()
except:
    log_error()

# CORRECT
try:
    do_something()
except Exception:
    log_error()
```

### Star imports

```python
# WRONG
from authshield.models import *
from typing import *

# CORRECT
from authshield.models import User, AuditLog
from typing import Any, Protocol
```

### Mutable class attributes shared across instances

```python
# WRONG
class UserService:
    cache: dict = {}  # shared across all instances

# CORRECT
class UserService:
    def __init__(self) -> None:
        self.cache: dict[str, Any] = {}
```

### `isinstance` chains — use `functools.singledispatch` or strategy pattern

```python
# WRONG
def process(value: Any) -> None:
    if isinstance(value, str):
        ...
    elif isinstance(value, int):
        ...

# CORRECT
@singledispatch
def process(value: Any) -> None:
    raise TypeError(f"Unsupported type: {type(value)}")

@process.register(str)
def _(value: str) -> None:
    ...

@process.register(int)
def _(value: int) -> None:
    ...
```

### Shadowing builtins

```python
# WRONG
def filter(items: list) -> list:  # shadows builtin `filter`
    id = str(uuid4())             # shadows builtin `id`
    ...

# CORRECT
def filter_items(items: list[T]) -> list[T]:
    record_id = str(uuid4())
    ...
```

### Ignoring type errors

```python
# WRONG
result = some_dict["key"]  # type: ignore

# CORRECT — only use type: ignore with a specific error code
result = some_dict["key"]  # type: ignore[typeddict-unknown-key]
```

---

## 12. Pre-commit Hooks

All developers must install pre-commit hooks:

```bash
pre-commit install
```

The hooks run Ruff lint, Ruff format, and mypy on every commit. CI runs the same
checks and will reject PRs that fail.

---

## 13. Code Review Checklist

- [ ] All functions have type annotations (params + return)
- [ ] No bare `except:` clauses
- [ ] No mutable default arguments
- [ ] No star imports
- [ ] Public functions have Google-style docstrings
- [ ] Imports follow the ordering convention
- [ ] Names follow the convention table in Section 10
- [ ] Pydantic models use `model_config` with `from_attributes` where needed
- [ ] Dataclasses use `frozen=True` and `slots=True` when appropriate
- [ ] No `print()` statements; use `logging` module instead
- [ ] No `# type: ignore` without an error code
- [ ] Ruff and mypy pass locally before pushing
