# Testing Guide

## Test Structure

Tests are organized into three tiers:

```
backend/tests/
├── unit/                    # Fast, isolated tests
│   ├── authentication/      # Auth domain tests
│   ├── users/               # User domain tests
│   ├── sessions/            # Session tests
│   ├── audit/               # Audit tests
│   ├── defenses/            # Policy engine tests
│   └── shared/              # Shared infrastructure tests
├── integration/             # Database and cross-module tests
│   ├── conftest.py          # SQLite in-memory fixtures
│   ├── test_authentication_flow.py
│   ├── test_user_lifecycle.py
│   └── test_session_lifecycle.py
└── e2e/                     # End-to-end tests (future)
```

## Running Tests

### All Tests

```bash
cd backend
pytest
```

### Specific Module

```bash
pytest tests/unit/authentication/
pytest tests/unit/shared/test_event_bus.py
```

### With Verbose Output

```bash
pytest -v
```

### With Coverage

```bash
pytest --cov=app --cov-report=html
```

### Specific Test Class or Function

```bash
pytest tests/unit/authentication/test_authentication_entities.py::TestAccountStatus::test_can_transition_valid
```

## Writing Unit Tests

### Principles

1. **Isolation**: Each test is independent with no shared state
2. **Speed**: Tests complete in <100ms
3. **Clarity**: Test names describe the scenario and expected outcome
4. **Determinism**: No time-dependent or order-dependent tests

### Test File Naming

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<action>_<scenario>_<expected>`

### Example

```python
import pytest
from unittest.mock import AsyncMock

from app.authentication.domain.entities.authentication_result import (
    AuthenticationResult,
    AuthenticationOutcome,
)

class TestAuthenticationResult:
    def test_success_result(self):
        result = AuthenticationResult(outcome=AuthenticationOutcome.SUCCESS)
        assert result.is_success is True

    def test_failure_result(self):
        result = AuthenticationResult(outcome=AuthenticationOutcome.FAILURE)
        assert result.is_failure is True
```

## Writing Integration Tests

### Database Tests

Integration tests use SQLite in-memory databases:

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def session(engine):
    factory = async_sessionmaker(bind=engine, class_=AsyncSession)
    async with factory() as session:
        yield session
        await session.rollback()
```

### Cross-Module Tests

Integration tests verify interactions between modules:

```python
class TestAuthenticationFlow:
    @pytest.mark.asyncio
    async def test_register_then_login(self, session):
        # 1. Create user via registration service
        # 2. Login with credentials
        # 3. Verify session created
        # 4. Logout
        # 5. Verify session destroyed
        pass
```

## Mocking Patterns

### AsyncMock for Services

```python
@pytest.fixture
def mock_user_repo():
    repo = AsyncMock()
    repo.get_by_username = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    return repo
```

### Mock for Event Bus

```python
@pytest.fixture
def mock_event_bus():
    bus = AsyncMock()
    bus.publish = AsyncMock()
    return bus
```

### Mock for Password Hasher

```python
@pytest.fixture
def mock_hasher():
    hasher = MagicMock()
    hasher.hash_password.return_value = "$argon2id$hashed"
    hasher.verify_password.return_value = True
    return hasher
```

### Patching Singletons

```python
from unittest.mock import patch

def test_something():
    with patch("app.shared.events.event_bus.get_event_bus") as mock_get:
        mock_get.return_value = AsyncMock()
        # test code
```

## Test Fixtures

### Shared Fixtures (unit/conftest.py)

- `event_loop`: Session-scoped asyncio event loop
- `mock_session`: AsyncMock for SQLAlchemy sessions
- `mock_event_bus`: EventBus mock
- `mock_user_repository`: User repository mock
- `mock_session_repository`: Session repository mock
- `mock_audit_repository`: Audit repository mock
- `mock_password_hasher`: Password hasher mock
- `mock_performance_monitor`: Performance monitor mock

### Integration Fixtures (integration/conftest.py)

- `engine`: In-memory SQLite async engine
- `db_session`: Async session with rollback
- `sample_user_data`: Pre-configured user creation data

## Coverage Requirements

- **Unit tests**: >90% line coverage per module
- **Integration tests**: >80% for critical flows
- **No coverage requirement**: E2E tests (manual verification)

### Coverage Report

```bash
pytest --cov=app --cov-report=term-missing
```

### Coverage by Module

| Module | Target | Focus |
|--------|--------|-------|
| authentication | 95% | All entities, validators, publishers |
| users | 90% | Lifecycle, roles, permissions |
| sessions | 90% | Entity properties, validators |
| audit | 85% | Audit event creation, immutability |
| defenses | 85% | Policy engine, rule evaluation |
| shared | 90% | EventBus, validators, exceptions, models |

## Best Practices

1. **Test one thing per test method**: Each test verifies a single behavior
2. **Use descriptive names**: `test_login_fails_with_wrong_password` not `test_login`
3. **Arrange-Act-Assert**: Clear three-phase structure
4. **Avoid test interdependence**: Tests can run in any order
5. **Use fixtures for setup**: Shared state via pytest fixtures, not global variables
6. **Mock external boundaries**: Mock repositories, not business logic
7. **Test edge cases**: Empty inputs, boundary values, error paths
8. **Keep tests fast**: Unit tests <100ms, integration tests <1s
