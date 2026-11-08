# AuthShield Lab — Coding Conventions

> Version 1.0 · Last Updated: 2026-07-19 · Owner: Engineering Team

---

## Table of Contents

1. [Python 3.12+ Conventions](#1-python-312-conventions)
2. [FastAPI Conventions](#2-fastapi-conventions)
3. [SQLAlchemy 2.0 Conventions](#3-sqlalchemy-20-conventions)
4. [React / TypeScript Conventions](#4-react--typescript-conventions)
5. [SQL Conventions](#5-sql-conventions)
6. [Git Conventions](#6-git-conventions)
7. [File Organization Conventions](#7-file-organization-conventions)
8. [Import Ordering Conventions](#8-import-ordering-conventions)
9. [Error Handling Patterns](#9-error-handling-patterns)
10. [Logging Patterns](#10-logging-patterns)
11. [Configuration Patterns](#11-configuration-patterns)

---

## 1. Python 3.12+ Conventions

### 1.1 Type Hints

Every function signature must include type hints for all parameters and return values. No exceptions.

```python
# CORRECT
def calculate_risk_score(findings: list[Finding], weights: dict[str, float]) -> RiskScore:
    ...

async def authenticate_user(
    credential: Credential,
    user_repository: UserRepository,
) -> AuthResult:
    ...

# INCORRECT — missing return type, missing parameter types
def calculate_risk_score(findings, weights):
    ...
```

**Rules:**
- Use built-in generics (`list`, `dict`, `tuple`, `set`) instead of `typing` equivalents (`List`, `Dict`, `Tuple`, `Set`). Python 3.12+ supports lowercase generics natively.
- Use `X | None` instead of `Optional[X]`.
- Use `X | Y` instead of `Union[X, Y]`.
- Use `TypeAlias` for complex type definitions: `UserId = int`.
- Use `TypeVar` and `Generic` for generic classes.
- Always annotate `self` and `cls` parameters implicitly (never add type hints to them).
- Use `Callable[[int, str], bool]` for function types. Use `collections.abc.Callable` in new code.

```python
from collections.abc import Callable
from typing import TypeAlias

UserId: TypeAlias = int
Handler: TypeAlias = Callable[[str, int], bool]
```

### 1.2 Dataclasses

Use `@dataclass(frozen=True)` for value objects and immutable data structures. Use regular `@dataclass` for mutable DTOs that are serialized/deserialized.

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise ValueError(f"Invalid email address: {self.value}")

@dataclass
class CreateUserRequest:
    username: str
    email: EmailAddress
    role: UserRole = UserRole.STUDENT
    created_at: datetime = field(default_factory=datetime.utcnow)
```

**Rules:**
- Prefer frozen dataclasses for domain entities and value objects.
- Use `field(default_factory=...)` for mutable default values (lists, dicts, datetimes).
- Validate invariants in `__post_init__` for value objects.
- Do not put business logic in dataclasses — use separate service or use-case classes.
- Use `__slots__` (`@dataclass(slots=True)`) for performance-critical dataclasses.

### 1.3 Async/Await

All I/O operations must use `async/await`. Never block the event loop with synchronous I/O.

```python
# CORRECT — async I/O
async def get_user_by_id(user_id: int) -> User | None:
    async with self.session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

# INCORRECT — blocking the event loop
def get_user_by_id(user_id: int) -> User | None:
    result = self.session.execute(select(User).where(User.id == user_id))  # BLOCKING
    return result.scalar_one_off()
```

**Rules:**
- All FastAPI route handlers must be `async def` unless they exclusively call synchronous library functions that cannot be avoided.
- All repository methods that perform database access must be `async`.
- Use `asyncio.gather()` for concurrent independent operations.
- Use `asyncio.create_task()` for fire-and-forget background work within a request.
- Never use `asyncio.run()` inside async functions — it creates a new event loop.
- Use `await` on every coroutine — never store a coroutine in a variable without awaiting it.

### 1.4 Protocol Classes

Use `typing.Protocol` for structural subtyping. Prefer protocols over abstract base classes for defining interfaces.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Authenticator(Protocol):
    """Protocol for all authentication methods."""

    async def authenticate(self, credential: Credential) -> AuthResult:
        """Validate a credential and return the authentication result."""
        ...

    async def enroll(self, user_id: int) -> EnrollmentData:
        """Enroll a user for this authentication method."""
        ...

@runtime_checkable
class UserRepository(Protocol):
    """Protocol for user persistence."""

    async def get_by_id(self, user_id: int) -> User | None: ...
    async def get_by_email(self, email: EmailAddress) -> User | None: ...
    async def save(self, user: User) -> None: ...
    async def delete(self, user_id: int) -> None: ...
```

**Rules:**
- Define protocols in the `domain/` layer where the interface is consumed, not where the implementation lives.
- Use `@runtime_checkable` only when `isinstance()` checks are needed at runtime.
- Protocol methods must have complete type signatures.
- One protocol per concern — split large protocols into focused interfaces.

### 1.5 Pattern Matching

Use Python 3.10+ structural pattern matching (`match/case`) when it improves readability over chained conditionals.

```python
match event:
    case AuthEvent(kind="login", status="failed"):
        await handle_failed_login(event)
    case AuthEvent(kind="login", status="success"):
        await handle_successful_login(event)
    case AuthEvent(kind="enrollment"):
        await handle_enrollment(event)
    case _:
        logger.warning("Unhandled auth event: %s", event.kind)
```

### 1.6 f-strings and String Formatting

- Use f-strings for all string formatting.
- Use `:` format specifiers for alignment and precision: `f"{value:.2f}"`.
- Never use `%` formatting or `.format()` in new code.

```python
logger.info("User %s authenticated from IP %s", user.username, request.client.host)
display = f"Risk score: {score:.1f}/100 (confidence: {confidence:.0%})"
```

### 1.7 comprehensions and Generators

- Use list comprehensions for simple transformations.
- Use generator expressions for large datasets or when only a single pass is needed.
- Keep comprehensions readable — if a comprehension spans more than 2 lines, refactor to a loop.

```python
# Simple comprehension
active_user_ids: list[int] = [u.id for u in users if u.is_active]

# Generator for large datasets
async def stream_audit_logs() -> AsyncGenerator[AuditLog, None]:
    async for row in cursor:
        yield AuditLog.from_row(row)
```

---

## 2. FastAPI Conventions

### 2.1 Route Organization

Each bounded context has its own router module. Routers are composed in the main application factory.

```
api/
  routers/
    identity.py       ← /api/v1/auth/*, /api/v1/users/*
    education.py      ← /api/v1/courses/*, /api/v1/lessons/*
    security.py       ← /api/v1/threats/*, /api/v1/audit/*
    platform.py       ← /api/v1/config/*, /api/v1/health/*
```

**Rules:**
- Every route must have a `response_model` declared.
- Every route must have a `summary` and `description` via the decorator or docstring.
- Use HTTP status codes correctly: 201 for creation, 204 for deletion, 400 for validation, 404 for not found, 409 for conflict.
- Group related routes using APIRouter with a prefix and tags.

```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and issue JWT",
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
) -> TokenResponse:
    """Authenticate a user with username and password.

    Returns a JWT access token and refresh token on success.
    Returns 401 if credentials are invalid.
    """
    ...
```

### 2.2 Dependency Injection

Use FastAPI's `Depends()` for all service and repository injection. Dependencies are defined in a dedicated `dependencies.py` module per bounded context.

```python
from fastapi import Depends

async def get_user_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session=db_session)

async def get_authentication_service(
    user_repo: UserRepository = Depends(get_user_repository),
    token_service: TokenService = Depends(get_token_service),
) -> AuthenticationService:
    return AuthenticationService(
        user_repository=user_repo,
        token_service=token_service,
    )
```

**Rules:**
- Dependencies that use database sessions must use `yield` for proper session lifecycle management.
- Prefer `async def` dependencies for anything that performs I/O.
- Use `Depends(use_class)` for classes and `Depends(get_factory)` for factory functions.
- Scope dependencies appropriately — request-scoped vs. application-scoped.

### 2.3 Request/Response Models

Define separate Pydantic models for requests and responses. Never expose SQLAlchemy models directly.

```python
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["alice"])
    password: str = Field(..., min_length=8, examples=["securePassword123"])

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")

class UserResponse(BaseModel):
    id: int = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    role: str = Field(..., description="User role")
    created_at: str = Field(..., description="Account creation timestamp")
```

**Rules:**
- Use `Field()` with descriptions for all model fields.
- Include `examples` in request models for auto-generated API documentation.
- Use `model_config = ConfigDict(from_attributes=True)` for ORM mode when mapping from SQLAlchemy.
- Use `model_validator` for cross-field validation.
- Response models must never include sensitive data (password hashes, internal IDs unless needed).

### 2.4 Error Handling

Use FastAPI's exception handlers for consistent error responses.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class ApplicationError(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, code: str, status_code: int = 400) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code

class NotFoundError(ApplicationError):
    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
        )

class AuthenticationError(ApplicationError):
    def __init__(self, reason: str = "Invalid credentials") -> None:
        super().__init__(
            message=reason,
            code="AUTHENTICATION_FAILED",
            status_code=401,
        )

def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
        )
```

**Rules:**
- All application errors extend `ApplicationError`.
- Never return raw exception messages to the client — use structured error codes.
- Log the full exception details server-side with tracebacks.
- Never expose stack traces, SQL queries, or internal paths in error responses.

### 2.5 Pydantic V2 Conventions

- Use `model_validator(mode='before')` for pre-validation transforms.
- Use `model_validator(mode='after')` for post-validation cross-field checks.
- Use `field_validator` for individual field validation.
- Use `ConfigDict` instead of inner `class Config`.
- Use `model_json_schema()` for generating documentation, not manual schema definitions.

---

## 3. SQLAlchemy 2.0 Conventions

### 3.1 Model Definitions

Use SQLAlchemy 2.0 `Mapped` and `mapped_column` syntax.

```python
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_users_role_active", "role", "is_active"),
    )
```

**Rules:**
- Use `Mapped[type]` for all columns — never the legacy `Column()` syntax.
- Define `__tablename__` explicitly on every model.
- Add `index=True` on columns that are frequently queried.
- Use composite indexes for frequently-filtered column combinations.
- Always include `created_at` and `updated_at` timestamps.
- Define `cascade` rules on relationships explicitly.

### 3.2 Async Sessions

All database access uses async sessions. Never use synchronous sessions in application code.

```python
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./authshield.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**Rules:**
- Use `aiosqlite` as the SQLite async driver.
- Use `expire_on_commit=False` to prevent lazy-loading after commit.
- Always wrap session usage in try/except with explicit commit/rollback.
- Use `select()` with `where()` — never `session.query()`.
- Close sessions properly using context managers.

### 3.3 Repository Pattern

Implement repositories as concrete classes that conform to the Protocol defined in the domain layer.

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save(self, user: User) -> None:
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=EmailAddress(model.email),
            role=UserRole(model.role),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, user: User) -> UserModel:
        return UserModel(
            id=user.id,
            username=user.username,
            email=user.email.value,
            role=user.role.value,
            is_active=user.is_active,
        )
```

**Rules:**
- Repository classes live in `infrastructure/repositories/`.
- Convert between SQLAlchemy models and domain entities at the repository boundary.
- Never return SQLAlchemy model instances to the application layer.
- Use `select()` construction, not string queries.
- Use `flush()` in repositories, `commit()` in the session lifecycle (dependency injection).

### 3.4 Migrations

- Use Alembic for database migrations.
- Migration files are generated via `alembic revision --autogenerate -m "description"`.
- Every migration must be reversible — implement both `upgrade()` and `downgrade()`.
- Review autogenerated migrations before committing — Alembic cannot detect all changes.
- Never modify a migration that has been applied to production. Create a new migration to fix issues.

---

## 4. React / TypeScript Conventions

### 4.1 Component Structure

- Use functional components exclusively — no class components.
- One component per file. File name matches component name in PascalCase.
- Components that render complex UIs are composed of smaller, focused sub-components.
- Export the component as default export; named exports for types and hooks.

```typescript
// UserProfile.tsx
import React from 'react';
import { User } from '../../domain/types';

interface UserProfileProps {
  user: User;
  onEdit: (userId: number) => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ user, onEdit }) => {
  return (
    <div className="user-profile">
      <h2>{user.username}</h2>
      <p>{user.email}</p>
      <button onClick={() => onEdit(user.id)}>Edit Profile</button>
    </div>
  );
};

export default UserProfile;
```

### 4.2 Hooks Conventions

- Custom hooks are prefixed with `use`.
- One responsibility per custom hook — extract into multiple hooks if the hook handles multiple concerns.
- Hooks that fetch data use a standard pattern with loading, error, and data states.
- Always clean up side effects in the return function of `useEffect`.

```typescript
// useAuthentication.ts
import { useState, useCallback } from 'react';
import { apiClient } from '../infrastructure/apiClient';
import { AuthResult, LoginCredentials } from '../domain/types';

interface UseAuthenticationResult {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export function useAuthentication(): UseAuthenticationResult {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (credentials: LoginCredentials): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const result: AuthResult = await apiClient.post('/api/v1/auth/login', credentials);
      setIsAuthenticated(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback((): void => {
    setIsAuthenticated(false);
  }, []);

  return { login, logout, isAuthenticated, isLoading, error };
}
```

### 4.3 State Management

- Use React hooks (`useState`, `useReducer`, `useContext`) for component-local state.
- Use the Context API for shared state that spans multiple components (e.g., auth state, theme).
- Avoid prop-drilling beyond 3 levels — use Context or composition patterns.
- State updates must be immutable — never mutate state objects directly.

```typescript
// CORRECT — immutable update
setUser({ ...user, username: newUsername });

// INCORRECT — mutation
user.username = newUsername;
setUser(user);
```

### 4.4 TypeScript Conventions

- Use `interface` for object shapes that may be extended. Use `type` for unions, intersections, and computed types.
- Avoid `any` — use `unknown` and narrow with type guards.
- Use `readonly` for props interfaces and state that should not be mutated.
- Use discriminated unions for state machines and variant types.

```typescript
// Discriminated union for async state
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: string };

// Usage
function CourseList() {
  const [state, setState] = useState<AsyncState<Course[]>>({ status: 'idle' });

  // Exhaustive handling with switch
  switch (state.status) {
    case 'idle':
      return <button onClick={loadCourses}>Load Courses</button>;
    case 'loading':
      return <Spinner />;
    case 'success':
      return <CourseGrid courses={state.data} />;
    case 'error':
      return <ErrorMessage message={state.error} />;
  }
}
```

### 4.5 File and Folder Organization

```
frontend/src/
  components/         ← Reusable UI components
    common/           ← Generic components (Button, Modal, Spinner, Input)
    layout/           ← Layout components (Header, Sidebar, Footer)
    features/         ← Feature-specific components
  hooks/              ← Custom React hooks
  domain/             ← TypeScript types, interfaces, and constants
  infrastructure/     ← API client, storage adapters, Electron IPC
  contexts/           ← React Context providers
  styles/             ← Global styles, theme configuration
  utils/              ← Pure utility functions
  __tests__/          ← Test files mirroring src/ structure
```

### 4.6 Styling

- Use CSS Modules for component-scoped styles.
- Define a consistent design token system (colors, spacing, typography) in `styles/tokens.css`.
- Use CSS custom properties for theme values.
- Avoid inline styles except for dynamic values that cannot be predetermined.

---

## 5. SQL Conventions

### 5.1 Naming

| Object | Convention | Example |
|---|---|---|
| Tables | `snake_case`, plural | `users`, `course_modules`, `audit_logs` |
| Columns | `snake_case` | `created_at`, `user_id`, `is_active` |
| Primary keys | `id` | `id` |
| Foreign keys | `{referenced_table_singular}_id` | `user_id`, `course_id` |
| Indexes | `ix_{table}_{columns}` | `ix_users_email`, `ix_audit_logs_created_at` |
| Unique constraints | `uq_{table}_{columns}` | `uq_users_email`, `uq_users_username` |
| Check constraints | `ck_{table}_{description}` | `ck_users_role_valid` |

### 5.2 Indexing Strategy

- Index all foreign key columns.
- Index columns used in `WHERE` clauses frequently.
- Index columns used in `ORDER BY` for common queries.
- Use composite indexes for multi-column `WHERE` and `ORDER BY` patterns — place the most selective column first.
- Avoid over-indexing: each index slows writes. Target a maximum of 5 indexes per table.
- Use partial indexes for queries that filter on a fixed condition (e.g., `WHERE is_active = true`).

### 5.3 Migration Naming

Migration file names follow the pattern: `{revision}_{description}.py`

```
001_create_users_table.py
002_add_email_index.py
003_create_enrollment_table.py
```

### 5.4 Data Integrity

- Use `NOT NULL` for all columns that must always have a value.
- Use `DEFAULT` values for columns that have a sensible default.
- Use `CHECK` constraints for enum-like values where the database should enforce validity.
- Use foreign key constraints — never rely on application-level referential integrity alone.
- Use `ON DELETE CASCADE` or `ON DELETE SET NULL` explicitly on every foreign key.

---

## 6. Git Conventions

### 6.1 Branch Naming

| Branch Type | Pattern | Example |
|---|---|---|
| Feature | `feature/{issue-id}-{short-description}` | `feature/42-totp-authentication` |
| Bug fix | `fix/{issue-id}-{short-description}` | `fix/108-login-race-condition` |
| Hotfix | `hotfix/{issue-id}-{short-description}` | `hotfix/200-sql-injection` |
| Documentation | `docs/{description}` | `docs/api-reference-update` |
| Refactor | `refactor/{description}` | `refactor/repository-pattern` |
| Release | `release/{version}` | `release/1.2.0` |

### 6.2 Commit Messages

Follow the Conventional Commits specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no feature change, no bug fix)
- `test`: Adding or updating tests
- `chore`: Build, CI, dependency updates, configuration changes
- `perf`: Performance improvement

**Scope:** The bounded context or component affected: `auth`, `courses`, `api`, `frontend`, `db`, `ci`.

**Rules:**
- Subject line: imperative mood, lowercase, no period, max 72 characters.
- Body: wrap at 72 characters, explain what and why (not how).
- Footer: reference issues with `Closes #123` or `Fixes #123`.

```
feat(auth): add TOTP two-factor authentication

Implement TOTP-based 2FA using the pyotp library. Users can enroll
a TOTP device, which generates a shared secret and provisioning URI.
During login, a second factor is required after password verification.

The implementation follows the AuthenticatorProtocol and can be swapped
with other 2FA methods (HOTP, WebAuthn) via the plugin system.

Closes #42
```

### 6.3 Merge Strategy

- **Feature branches → `main`:** Squash and merge. This keeps the `main` branch history clean with one commit per feature.
- **Hotfix branches → `main`:** Create a merge commit (no squash) to preserve the hotfix context.
- **Release branches → `main`:** Create a merge commit.
- **No force-pushing** to `main`, `release/*`, or `hotfix/*` branches under any circumstances.

### 6.4 Pull Request Requirements

- PR title follows the same format as commit messages: `type(scope): description`.
- PR description includes: what changed, why it changed, how to test, screenshots (for UI changes), and migration steps (if applicable).
- PRs are linked to the relevant issue.
- All CI checks pass before merge.
- Minimum review approvals met (see `ENGINEERING_HANDBOOK.md`).
- Branch is up-to-date with `main` (rebase if needed).

---

## 7. File Organization Conventions

### 7.1 Backend Directory Structure

```
backend/
  src/
    domain/
      __init__.py
      identity/
        entities/           ← User, Role, Credential
        value_objects/      ← EmailAddress, CredentialHash
        events/             ← UserRegistered, UserAuthenticated
        repositories/       ← UserRepository Protocol
      education/
        entities/           ← Course, Lesson, Assessment
        value_objects/      ← CourseModuleId, Score
        events/             ← LessonCompleted
        repositories/       ← CourseRepository Protocol
      security/
        entities/           ← Threat, Vulnerability, AuditEntry
        value_objects/      ← RiskScore, Severity
        events/             ← ThreatDetected
        repositories/       ← AuditRepository Protocol
      platform/
        entities/           ← Configuration, Plugin
        value_objects/      ← PluginId, ConfigKey
        events/             ← PluginInstalled
        repositories/       ← ConfigurationRepository Protocol
      events/
        bus.py              ← Event bus implementation
        base.py             ← BaseDomainEvent class
    application/
      identity/
        register_user.py
        authenticate_user.py
        manage_credentials.py
      education/
        complete_lesson.py
        submit_assessment.py
        track_progress.py
      security/
        scan_threat.py
        record_audit_entry.py
      platform/
        install_plugin.py
        update_configuration.py
    infrastructure/
      repositories/
        sqlalchemy_user_repository.py
        sqlalchemy_course_repository.py
        ...
      database/
        engine.py
        session.py
        migrations/
      events/
        sqlalchemy_event_store.py
      config/
        settings.py
        paths.py
    api/
      app.py
      dependencies.py
      routers/
        identity.py
        education.py
        security.py
        platform.py
      schemas/
        identity.py
        education.py
        security.py
        platform.py
      middleware/
        error_handler.py
        logging_middleware.py
  tests/
    unit/
    integration/
    e2e/
  alembic/
```

### 7.2 Frontend Directory Structure

```
frontend/
  src/
    components/
      common/
        Button/
          Button.tsx
          Button.module.css
          Button.test.tsx
          index.ts
        Modal/
          Modal.tsx
          Modal.module.css
          Modal.test.tsx
          index.ts
      layout/
        AppLayout.tsx
        Sidebar.tsx
        Header.tsx
      features/
        authentication/
          LoginForm.tsx
          RegistrationForm.tsx
          MFASetup.tsx
        courses/
          CourseList.tsx
          CourseDetail.tsx
          LessonPlayer.tsx
        dashboard/
          Dashboard.tsx
          ProgressChart.tsx
    hooks/
      useAuthentication.ts
      useCourses.ts
      useApiCall.ts
    domain/
      types.ts
      constants.ts
      enums.ts
    infrastructure/
      apiClient.ts
      storage.ts
      electronBridge.ts
    contexts/
      AuthContext.tsx
      ThemeContext.tsx
    styles/
      globals.css
      tokens.css
      reset.css
    utils/
      formatters.ts
      validators.ts
      dateHelpers.ts
  public/
    index.html
    manifest.json
```

---

## 8. Import Ordering Conventions

### 8.1 Python Import Order

Imports are organized in four groups, separated by blank lines:

```python
# Group 1: Standard library
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

# Group 2: Third-party packages
import pyotp
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, String
from sqlalchemy.ext.asyncio import AsyncSession

# Group 3: Local application — domain layer
from src.domain.identity.entities import User
from src.domain.identity.value_objects import EmailAddress
from src.domain.identity.events import UserRegistered

# Group 4: Local application — infrastructure and API
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.api.schemas.identity import UserResponse
```

**Rules:**
- Use absolute imports — never relative imports (`from .module import X`).
- Sort imports alphabetically within each group.
- Use `isort` for automated import sorting with the project configuration.
- Do not use `import *` under any circumstances.
- Group 2 (third-party) order: `fastapi`, `pydantic`, `sqlalchemy`, then alphabetical.
- Group 3/4 (local) order: `domain` before `application` before `infrastructure` before `api`.

### 8.2 TypeScript Import Order

```typescript
// Group 1: React and external libraries
import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

// Group 2: Internal domain types
import { Course, Lesson } from '../domain/types';
import { API_BASE_URL } from '../domain/constants';

// Group 3: Shared components
import { Button } from '../components/common/Button';
import { Spinner } from '../components/common/Spinner';

// Group 4: Custom hooks and utilities
import { useApiCall } from '../hooks/useApiCall';
import { formatDate } from '../utils/formatters';
```

---

## 9. Error Handling Patterns

### 9.1 Python Error Hierarchy

```
ApplicationError (base)
  ├── ValidationError          (400) — Input validation failures
  ├── AuthenticationError      (401) — Auth credential failures
  ├── AuthorizationError       (403) — Permission denied
  ├── NotFoundError            (404) — Resource not found
  ├── ConflictError            (409) — State conflicts (duplicate, version mismatch)
  ├── RateLimitError           (429) — Too many requests
  └── InternalError            (500) — Unexpected server errors
```

### 9.2 Error Handling Rules

1. **Never catch and swallow exceptions silently.** Every `except` block must either re-raise, log, or return an appropriate error response.
2. **Be specific with exception catching.** Catch `ValueError`, not `Exception`. Only catch `Exception` in top-level handlers.
3. **Log at the point of failure.** Include context: what operation was attempted, what input was received, what the expected outcome was.
4. **Use structured error responses.** All API errors return a consistent JSON shape: `{"error": {"code": "...", "message": "..."}}`.
5. **Sanitize error messages for the client.** Internal details (stack traces, SQL queries, file paths) are logged server-side, never returned to the client.

```python
# CORRECT
try:
    user = await user_repo.get_by_id(user_id)
except SQLAlchemyError as exc:
    logger.error("Database error fetching user %d: %s", user_id, exc)
    raise InternalError("Failed to retrieve user") from exc

if user is None:
    raise NotFoundError("User", user_id)

# INCORRECT — catches too broadly, swallows error
try:
    user = await user_repo.get_by_id(user_id)
except:
    return None
```

### 9.3 Frontend Error Handling

- Use error boundaries for React component error recovery.
- Display user-friendly error messages — never raw error objects or stack traces.
- Log client-side errors to the backend error logging endpoint.
- Use toast notifications for transient errors (network failures, validation).
- Use inline validation messages for form field errors.

---

## 10. Logging Patterns

### 10.1 Log Levels

| Level | When to Use | Example |
|---|---|---|
| `DEBUG` | Detailed diagnostic information | SQL queries, cache hit/miss, request/response bodies |
| `INFO` | Significant business events | User login, course completion, plugin installed |
| `WARNING` | Unexpected but recoverable situations | Deprecated API usage, retry attempts, configuration fallbacks |
| `ERROR` | Errors that require attention | Failed authentication, database errors, external service failures |
| `CRITICAL` | System-threatening failures | Database corruption, out-of-memory, security breach detected |

### 10.2 Logging Configuration

```python
import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

def configure_logging(log_level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        stream=sys.stdout,
    )
    # Suppress noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
```

### 10.3 Structured Logging

Use structured logging with context variables for machine-parseable logs:

```python
import structlog

logger = structlog.get_logger()

# CORRECT — structured context
logger.info(
    "user_authenticated",
    user_id=user.id,
    method="totp",
    ip_address=request.client.host,
    duration_ms=elapsed_ms,
)

# INCORRECT — unstructured string interpolation
logger.info(f"User {user.id} authenticated via TOTP from {request.client.host} in {elapsed_ms}ms")
```

### 10.4 Logging Rules

1. **Never log sensitive data.** Passwords, credential hashes, MFA secrets, and API keys must never appear in logs.
2. **Log the who, what, when, and outcome.** Every security-relevant event must include: user identity, action performed, timestamp, and success/failure.
3. **Use consistent log levels.** Do not use `ERROR` for expected conditions or `INFO` for debugging.
4. **Include correlation IDs.** Pass a unique request ID through the middleware so logs from a single request can be traced.
5. **Keep log messages actionable.** A log entry should tell the reader what happened and what to do about it.

---

## 11. Configuration Patterns

### 11.1 Settings Hierarchy

Configuration is loaded in the following priority order (later overrides earlier):

1. **Defaults:** Hardcoded defaults in the settings module.
2. **Config file:** `config/settings.yaml` (for offline-only operation, no environment variables needed).
3. **Command-line arguments:** Override specific settings for one-off runs.

### 11.2 Settings Implementation

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass(frozen=True)
class DatabaseSettings:
    path: Path = field(default_factory=lambda: Path("data/authshield.db"))
    echo_sql: bool = False
    pool_size: int = 5

@dataclass(frozen=True)
class SecuritySettings:
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

@dataclass(frozen=True)
class ApplicationSettings:
    app_name: str = "AuthShield Lab"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
```

### 11.3 Configuration Rules

1. **Use frozen dataclasses** for settings — configuration should be immutable at runtime.
2. **Never commit secrets** to version control. Use a placeholder in config files; document the expected values.
3. **Validate configuration at startup.** Fail fast if required settings are missing or invalid.
4. **Document every setting.** Each field must have a description (via docstring or inline comment).
5. **Provide sensible defaults** for all settings. The application should work out-of-the-box for development.
6. **Environment-specific config** lives in separate files: `config/settings.dev.yaml`, `config/settings.prod.yaml`.

---

*This document is a living artifact. Propose changes via PR to the repository. All changes require approval from the Engineering Lead and at least one Senior Engineer.*
