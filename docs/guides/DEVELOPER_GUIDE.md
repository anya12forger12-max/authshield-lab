# Developer Guide

## Project Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Architecture Overview

AuthShieldLab follows a modular DDD (Domain-Driven Design) architecture:

```
backend/app/
├── authentication/      # Auth engine (login, register, sessions)
├── users/              # User management (profiles, roles, permissions)
├── sessions/           # Session management
├── audit/              # Audit trail
├── defenses/           # Security policies and rules
│   └── policy/         # Policy engine, registry, rule engine
├── shared/             # Cross-cutting concerns
│   ├── events/         # EventBus (pub/sub)
│   ├── validation/     # Validation framework
│   ├── localization/   # i18n / translation
│   ├── monitoring/     # Performance monitoring
│   ├── models/         # SQLAlchemy ORM models
│   └── repositories/   # Data access layer
└── config/             # Application configuration
```

## Module Structure

Each module follows the same internal structure:

```
module/
├── domain/
│   ├── entities/       # Domain entities (dataclasses)
│   ├── models/         # Pydantic request/response models
│   ├── events/         # Domain event definitions
│   └── interfaces/     # Abstract service interfaces
├── services/           # Business logic implementations
├── repositories/       # Data access implementations
├── validators/         # Domain-specific validation
├── events/             # Event publisher implementations
├── api/                # FastAPI route handlers
└── __init__.py
```

## How to Add a New Module

1. **Create directory structure**:
```bash
mkdir -p backend/app/mymodule/{domain/{entities,models,events,interfaces},services,repositories,validators,events,api}
```

2. **Define domain entities** in `domain/entities/`:
```python
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class MyEntity:
    id: str = ""
    name: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
```

3. **Define interfaces** in `domain/interfaces/`:
```python
from abc import ABC, abstractmethod

class IMyService(ABC):
    @abstractmethod
    async def do_something(self, entity_id: str) -> dict: ...
```

4. **Implement services** in `services/`:
```python
class MyService(IMyService):
    def __init__(self, repository, event_publisher):
        self._repo = repository
        self._events = event_publisher

    async def do_something(self, entity_id: str) -> dict:
        entity = await self._repo.get_by_id(entity_id)
        # business logic
        await self._events.publish_something(entity_id)
        return entity.to_dict()
```

5. **Implement repositories** in `repositories/`:
```python
from ..shared.repositories.base_repository import BaseRepository

class MyRepository(BaseRepository[MyModel]):
    def __init__(self, session):
        super().__init__(MyModel, session)
```

6. **Register in FastAPI router** in `api/router.py`:
```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/my-module", tags=["my-module"])

@router.get("/{entity_id}")
async def get_entity(entity_id: str, service: IMyService = Depends(get_my_service)):
    return await service.do_something(entity_id)
```

## How to Add a New Service

1. Define the interface in `domain/interfaces/`
2. Create the implementation in `services/`
3. Add event publishing for state changes
4. Register the service as a FastAPI dependency
5. Write unit tests with mock dependencies
6. Write integration tests with real database

## How to Add a New API Endpoint

1. Create or extend the router in `api/`
2. Define request/response Pydantic models in `domain/models/`
3. Inject service dependencies via `Depends()`
4. Return typed response models
5. Add validation before business logic calls
6. Publish events for side effects

```python
@router.post("/resource", response_model=MyResponse)
async def create_resource(
    request: CreateRequest,
    service: IMyService = Depends(get_service),
):
    result = await service.create(request.dict())
    return MyResponse(**result)
```

## How to Add Tests

### Unit Tests

Create test files in `backend/tests/unit/<module>/`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.mymodule.services.my_service import MyService

@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def service(mock_repo):
    return MyService(repository=mock_repo)

class TestMyService:
    @pytest.mark.asyncio
    async def test_do_something(self, service, mock_repo):
        mock_repo.get_by_id.return_value = MagicMock(id="1")
        result = await service.do_something("1")
        assert result is not None
        mock_repo.get_by_id.assert_called_once_with("1")
```

### Integration Tests

Create test files in `backend/tests/integration/`:

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

@pytest.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # create tables...
    yield engine
    await engine.dispose()

@pytest.mark.asyncio
async def test_real_database_operation(db_engine):
    # test with real database
    pass
```

## How to Add a New Policy

1. Define a SecurityPolicy with rules in the defenses module
2. Create RuleConditionClauses for the conditions
3. Register the policy with the PolicyRegistry
4. Test the policy evaluation with various contexts

```python
from app.defenses.policy.registry import PolicyRegistry

policy = SecurityPolicy(
    policy_id="brute-force-block",
    name="Brute Force Block",
    description="Block IPs with >10 failed attempts",
    decision=PolicyDecision.DENY,
    rules=[
        SecurityRule(
            conditions=[
                RuleConditionClause("failed_attempts", "gt", 10),
                RuleConditionClause("time_window_minutes", "lte", 5),
            ]
        )
    ]
)
registry.register(policy)
```

## Event Bus Usage

### Subscribing to Events

```python
from app.shared.events.event_bus import get_event_bus, EventType

bus = get_event_bus()

async def handle_auth_success(event):
    print(f"Auth succeeded: {event.source_user_id}")

bus.subscribe(EventType.AUTHENTICATION_SUCCEEDED, handle_auth_success)
```

### Publishing Events

```python
from app.shared.events.event_bus import DomainEvent, EventType, get_event_bus

event = DomainEvent(
    event_type=EventType.USER_CREATED,
    module="users",
    message="New user registered",
    source_user_id="u-001",
    metadata={"username": "alice"},
)
await get_event_bus().publish(event)
```

## Dependency Injection Pattern

Services are wired together through FastAPI's dependency injection:

```python
from fastapi import Depends

def get_user_repository(session: AsyncSession = Depends(get_db_session)):
    return UserRepository(session)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    event_publisher: IAuthenticationEventPublisher = Depends(get_event_publisher),
):
    return AuthenticationService(user_repo, event_publisher)

@router.post("/login")
async def login(
    request: LoginRequest,
    service: IAuthenticationService = Depends(get_auth_service),
):
    return await service.login(request)
```

## Configuration Management

Configuration is managed through Pydantic Settings with environment variable loading:

```python
from app.config.settings import get_settings

settings = get_settings()
print(settings.security.max_login_attempts)  # 5
print(settings.database.url)                  # sqlite+aiosqlite:///./authshieldlab.db
```

Environment variables are prefixed with `APP_`, `SECURITY_`, `DATABASE_`, etc.
