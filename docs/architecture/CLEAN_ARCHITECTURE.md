# Clean Architecture Implementation Blueprint

## Overview

AuthShield Lab implements Uncle Bob's Clean Architecture with strict layer separation,
dependency inversion, and explicit boundary contracts. All dependencies point inward
toward the domain. No outer layer may be referenced by an inner layer.

```
┌─────────────────────────────────────────────────┐
│          Frameworks & Drivers (Layer 4)          │
│   FastAPI · SQLAlchemy · React · Electron · CLI  │
├─────────────────────────────────────────────────┤
│          Interface Adapters (Layer 3)            │
│   Controllers · Presenters · Gateways · Mappers  │
├─────────────────────────────────────────────────┤
│        Application Business Rules (Layer 2)      │
│   Use Cases · Application Services · DTOs        │
├─────────────────────────────────────────────────┤
│        Enterprise Business Rules (Layer 1)       │
│   Entities · Value Objects · Domain Services     │
└─────────────────────────────────────────────────┘
```

---

## Layer 1: Enterprise Business Rules (Domain)

### Purpose

Encapsulate the core business logic, invariants, and policies of AuthShield Lab.
This layer is completely independent of frameworks, databases, UI, or any external
system. It defines **what** the business is, not **how** it is implemented.

### Responsibilities

- Define domain entities with identity and lifecycle
- Define value objects as immutable, identity-less descriptors
- Enforce business invariants through entity methods and domain services
- Define domain events that represent business-significant state changes
- Express business rules as first-class code, not scattered conditionals
- Define repository interfaces (output ports) that persistence must satisfy
- Define domain-specific exceptions for business rule violations

### Allowed Dependencies

- Standard Python libraries (dataclasses, enum, uuid, datetime)
- Nothing else. Zero external dependencies.

### Forbidden Dependencies

- SQLAlchemy, Pydantic, FastAPI, or any framework
- Any repository implementation
- Any infrastructure code
- Any adapter or presenter code
- Database drivers, HTTP libraries, file system access

### Ownership

Domain entities, value objects, domain events, domain services, repository interfaces,
and business rule validators.

### Lifecycle

Changes only when the business rules themselves change. Technology migrations,
UI redesigns, and infrastructure upgrades must never require domain modifications.

### Testing Strategy

- Pure unit tests with no mocks or setup
- Domain entity behavior tests
- Value object equality and validation tests
- Domain service orchestration tests
- Business rule invariant tests
- Domain event emission tests

### Entities

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=False)
class User:
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    display_name: str = ""
    is_active: bool = True
    mfa_enabled: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def deactivate(self) -> None:
        if not self.is_active:
            raise BusinessRuleViolation("Cannot deactivate an already inactive user")
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def enable_mfa(self) -> None:
        if self.mfa_enabled:
            raise BusinessRuleViolation("MFA is already enabled")
        self.mfa_enabled = True
        self.updated_at = datetime.now(timezone.utc)
```

### Value Objects

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise InvalidValueObject("Invalid email format")


@dataclass(frozen=True)
class Permission:
    resource: str
    action: str

    def __str__(self) -> str:
        return f"{self.resource}:{self.action}"
```

### Domain Services

```python
class PasswordPolicy:
    """Encapsulates business rules for password validation."""

    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True

    def validate(self, password: str) -> list[str]:
        errors: list[str] = []
        if len(password) < self.MIN_LENGTH:
            errors.append(f"Password must be at least {self.MIN_LENGTH} characters")
        if self.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain an uppercase letter")
        if self.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain a lowercase letter")
        if self.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            errors.append("Password must contain a digit")
        if self.REQUIRE_SPECIAL and not any(not c.isalnum() for c in password):
            errors.append("Password must contain a special character")
        return errors
```

---

## Layer 2: Application Business Rules (Use Cases)

### Purpose

Orchestrate the flow of data to and from domain entities. Use cases contain
application-specific business rules that coordinate domain objects, enforce
application-level validation, and manage transactions.

### Responsibilities

- Implement use case workflows as single-responsibility classes
- Coordinate multiple domain entities within a single operation
- Manage application-level transactions
- Enforce authorization policies via port interfaces
- Publish domain events after successful operations
- Translate between input DTOs and domain entities
- Handle cross-cutting concerns through decorators

### Allowed Dependencies

- Layer 1 (Domain): entities, value objects, domain services, repository interfaces
- Python standard library

### Forbidden Dependencies

- Any framework, library, or infrastructure component
- Concrete repository implementations
- HTTP, database, or file system access
- Direct use of ORM models or database sessions

### Ownership

Use case classes, input/output DTOs, application service orchestration,
and use case validators.

### Lifecycle

Changes when application workflows change. Adding new features typically means
adding new use cases. Modifying existing use cases should be rare and carefully
reviewed.

### Testing Strategy

- Use case tests with mock ports (input and output)
- Verify correct domain entity interaction
- Verify event publishing
- Verify authorization enforcement
- Verify transaction boundaries

### Use Case Pattern

```python
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AuthenticateUserInput:
    email: str
    password: str
    mfa_code: str | None = None


@dataclass(frozen=True)
class AuthenticateUserOutput:
    user_id: UUID
    access_token: str
    refresh_token: str
    expires_in: int


class AuthenticateUserUseCase:
    """Authenticate a user with email and password, optionally with MFA."""

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        authentication_service: AuthenticationPort,
        event_publisher: EventPublishingPort,
    ) -> None:
        self._user_repository = user_repository
        self._authentication_service = authentication_service
        self._event_publisher = event_publisher

    async def execute(self, input_dto: AuthenticateUserInput) -> AuthenticateUserOutput:
        user = await self._user_repository.find_by_email(input_dto.email)
        if user is None:
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed("Account is deactivated")

        tokens = await self._authentication_service.authenticate(
            user=user,
            password=input_dto.password,
            mfa_code=input_dto.mfa_code,
        )

        await self._event_publisher.publish(
            UserAuthenticated(user_id=user.id)
        )

        return AuthenticateUserOutput(
            user_id=user.id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.expires_in,
        )
```

---

## Layer 3: Interface Adapters

### Purpose

Convert data between the format most convenient for use cases and domain entities
and the format required by external agencies such as databases, web frameworks,
or UIs. This layer contains the boundary between the application and the outside world.

### Responsibilities

- FastAPI route handlers that parse HTTP requests into use case inputs
- Pydantic models that validate and serialize API request/response payloads
- SQLAlchemy models that map domain entities to database tables
- Presenter classes that format use case outputs for API responses
- Event handlers that translate domain events into infrastructure actions
- Adapter classes that bridge port interfaces to concrete implementations
- Mappers that convert between domain objects and persistence models

### Allowed Dependencies

- Layer 1 (Domain): entities, value objects, repository interfaces
- Layer 2 (Use Cases): use case classes, input/output DTOs
- Framework libraries (FastAPI, SQLAlchemy, Pydantic) as implementation tools

### Forbidden Dependencies

- Direct dependency between adapters (communicate through ports only)
- Frameworks referencing domain internals (use mappers to isolate)
- Business logic in controllers or mappers

### Ownership

FastAPI routers, Pydantic schemas, SQLAlchemy models, repository implementations,
event handler registrations, and adapter classes.

### Lifecycle

Changes when external interfaces change (API versioning, database schema changes,
frontend contract changes). Adapters are the most volatile layer.

### Testing Strategy

- API adapter tests with FastAPI TestClient
- Repository adapter tests with test databases
- Mapper tests for correct data transformation
- Contract tests ensuring adapter compliance with port interfaces

### REST API Adapter (Controller)

```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/login", response_model=AuthenticateUserResponse)
async def login(
    request: AuthenticateUserRequest,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
) -> AuthenticateUserResponse:
    try:
        output = await use_case.execute(
            AuthenticateUserInput(
                email=request.email,
                password=request.password,
                mfa_code=request.mfa_code,
            )
        )
        return AuthenticateUserResponse.from_output(output)
    except AuthenticationFailed as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )
```

### Database Adapter (Repository)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class SQLAlchemyUserRepository(UserRepositoryPort):
    """Adapts SQLAlchemy persistence to the UserRepositoryPort interface."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return UserMapper.to_domain(model)

    async def save(self, user: User) -> None:
        model = UserMapper.to_model(user)
        self._session.add(model)
        await self._session.flush()
```

---

## Layer 4: Frameworks & Drivers

### Purpose

The outermost layer containing all framework-specific code, database configuration,
HTTP server setup, UI rendering, and external tool integrations. This layer wires
everything together.

### Responsibilities

- FastAPI application factory and middleware configuration
- SQLAlchemy engine, session factory, and migration management
- Electron main process and IPC bridge
- React application shell, routing, and global state
- Dependency injection container setup
- Logging and monitoring configuration
- Static file serving and CORS configuration
- CLI command definitions

### Allowed Dependencies

- All inner layers (Domain, Application, Adapters)
- All third-party frameworks and libraries
- System-level resources (file system, network, process)

### Forbidden Dependencies

- No business logic should live here
- No domain entities should be created or modified here

### Ownership

Application configuration, dependency wiring, middleware, migrations,
build scripts, and deployment configuration.

### Lifecycle

Changes when upgrading frameworks, adding middleware, changing database engines,
or modifying deployment targets. This layer absorbs the impact of technology changes.

### Testing Strategy

- Smoke tests for application startup
- End-to-end tests through the full stack
- Performance and load tests
- Deployment verification tests

### Application Bootstrap

```python
from fastapi import FastAPI


def create_application() -> FastAPI:
    app = FastAPI(title="AuthShield Lab", version="1.0.0")

    # Layer 4: Wire adapters to use cases
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine)

    user_repository = SQLAlchemyUserRepository(session_factory)
    event_bus = InMemoryEventBus()
    auth_service = JWTAuthenticationService(SECRET_KEY)

    authenticate_user = AuthenticateUserUseCase(
        user_repository=user_repository,
        authentication_service=auth_service,
        event_publisher=event_bus,
    )

    # Layer 3: Register adapters (controllers)
    app.include_router(create_auth_router(authenticate_user))

    return app
```

---

## The Dependency Rule

The central rule of this architecture: **dependencies may point only inward**.

```
Layer 4 ──→ Layer 3 ──→ Layer 2 ──→ Layer 1
Frameworks   Adapters    Use Cases   Domain
```

### Verification Checklist

- [ ] Domain never imports from any outer layer
- [ ] Use cases never import from adapters or frameworks
- [ ] Adapters communicate only through port interfaces
- [ ] No framework decorator appears in domain or application code
- [ ] Repository interfaces are defined in the domain layer
- [ ] Domain events are published through port interfaces
- [ ] Database models are never exposed beyond the adapter layer
- [ ] API schemas are never leaked into the domain layer

### Dependency Inversion Example

```python
# Domain layer defines the port (interface)
class UserRepositoryPort(Protocol):
    async def find_by_id(self, user_id: UUID) -> User | None: ...
    async def find_by_email(self, email: str) -> User | None: ...
    async def save(self, user: User) -> None: ...
    async def delete(self, user_id: UUID) -> None: ...

# Adapter layer implements the port
class SQLAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, user_id: UUID) -> User | None:
        # SQLAlchemy implementation
        ...

# Use case depends only on the port
class GetUserUseCase:
    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: UUID) -> User | None:
        return await self._user_repo.find_by_id(user_id)
```

---

## Interface / Protocol Patterns for Ports

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class NotificationPort(Protocol):
    async def send_email(self, to: str, subject: str, body: str) -> None: ...
    async def send_push(self, user_id: UUID, title: str, body: str) -> None: ...


@runtime_checkable
class LoggingPort(Protocol):
    def info(self, message: str, **context: object) -> None: ...
    def warning(self, message: str, **context: object) -> None: ...
    def error(self, message: str, **context: object) -> None: ...


@runtime_checkable
class ConfigurationPort(Protocol):
    async def get(self, key: str) -> str | None: ...
    async def set(self, key: str, value: str) -> None: ...
    async def delete(self, key: str) -> None: ...


@runtime_checkable
class EventPublishingPort(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...
```

---

## Concrete Implementation Patterns for Adapters

### In-Memory Event Bus

```python
from collections import defaultdict


class InMemoryEventBus(EventPublishingPort):
    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent], handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers[type(event)]:
            await handler(event)
```

### File System Backup Adapter

```python
import aiofiles


class LocalFileSystemBackupStorage(BackupStoragePort):
    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path

    async def store(self, backup_id: UUID, data: bytes) -> Path:
        path = self._base_path / f"{backup_id}.zip"
        async with aiofiles.open(path, "wb") as f:
            await f.write(data)
        return path

    async def retrieve(self, backup_id: UUID) -> bytes:
        path = self._base_path / f"{backup_id}.zip"
        async with aiofiles.open(path, "rb") as f:
            return await f.read()
```

---

## Layer Interaction Matrix

| Source Layer | Target Layer | Communication Mechanism |
|---|---|---|
| Frameworks (4) | Adapters (3) | Constructor injection, DI container |
| Adapters (3) | Use Cases (2) | Use case method invocation |
| Use Cases (2) | Domain (1) | Direct method calls on entities |
| Use Cases (2) | Adapters (3) | Port interface method calls (DIP) |
| Domain (1) | Use Cases (2) | Domain events via event port |
| Adapters (3) | Frameworks (4) | Framework-specific APIs |

---

## File Organization

```
src/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── events/
│   ├── services/
│   ├── ports/
│   │   ├── input/
│   │   └── output/
│   └── exceptions/
├── application/
│   ├── use_cases/
│   ├── dto/
│   ├── services/
│   └── validators/
├── adapters/
│   ├── api/
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── middleware/
│   ├── persistence/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── mappers/
│   ├── events/
│   ├── filesystem/
│   └── plugins/
├── infrastructure/
│   ├── config/
│   ├── database/
│   ├── logging/
│   └── di/
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── stores/
    │   └── services/
    └── electron/
        └── main.ts
```
