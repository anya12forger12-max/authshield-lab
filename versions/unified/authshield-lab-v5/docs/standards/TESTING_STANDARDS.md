# AuthShield Lab — Testing Standards

> Version 1.0 · Last Updated: 2026-07-19 · Owner: Engineering Team

---

## Table of Contents

1. [Test Pyramid](#1-test-pyramid)
2. [Test Naming Conventions](#2-test-naming-conventions)
3. [Test Organization](#3-test-organization)
4. [Fixtures and Factories](#4-fixtures-and-factories)
5. [Mocking Strategies](#5-mocking-strategies)
6. [Async Testing](#6-async-testing)
7. [Performance Testing](#7-performance-testing)
8. [Security Testing](#8-security-testing)
9. [Accessibility Testing](#9-accessibility-testing)
10. [Code Coverage Requirements](#10-code-coverage-requirements)
11. [Test Data Management](#11-test-data-management)
12. [Flaky Test Policy](#12-flaky-test-policy)

---

## 1. Test Pyramid

AuthShield Lab follows the test pyramid model with three layers. Each layer has a specific purpose, execution speed target, and scope.

```
              +-----------+
              |    E2E    |    ~5% of tests | Slow, broad scope
             /             \
            /   Integration  \   ~25% of tests | Medium speed, moderate scope
           /                 \
          /       Unit        \  ~70% of tests | Fast, narrow scope
         +---------------------+
```

### 1.1 Unit Tests (Target: ~70% of total tests)

**Purpose:** Verify individual functions, methods, and classes in isolation.

**Scope:** A single function or method. All dependencies are mocked or stubbed.

**Speed Target:** Entire suite completes in under 2 minutes. Individual test under 100ms.

**Location:** `tests/unit/`

**When to write:** Every business logic function, every value object, every domain entity method, every utility function, every Protocol implementation in isolation.

**Example:**

```python
import pytest
from src.domain.identity.value_objects import EmailAddress

class TestEmailAddress:
    def test_valid_email_is_accepted(self) -> None:
        email = EmailAddress("user@example.com")
        assert email.value == "user@example.com"

    def test_email_without_at_sign_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid email address"):
            EmailAddress("invalid-email")

    def test_email_equality(self) -> None:
        email1 = EmailAddress("user@example.com")
        email2 = EmailAddress("user@example.com")
        assert email1 == email2

    def test_email_inequality(self) -> None:
        email1 = EmailAddress("user@example.com")
        email2 = EmailAddress("other@example.com")
        assert email1 != email2

    def test_email_is_hashable(self) -> None:
        email = EmailAddress("user@example.com")
        assert hash(email) == hash(EmailAddress("user@example.com"))
```

### 1.2 Integration Tests (Target: ~25% of total tests)

**Purpose:** Verify that multiple components work correctly together, including database interactions, API endpoint behavior, and cross-context communication.

**Scope:** Multiple classes working together, typically through real database connections (using test databases) or real FastAPI test clients.

**Speed Target:** Entire suite completes in under 5 minutes. Individual test under 5 seconds.

**Location:** `tests/integration/`

**When to write:** Every API endpoint (happy + error paths), every repository implementation, every use-case class with real dependencies, event bus dispatch, database migrations.

**Example:**

```python
import pytest
from httpx import AsyncClient, ASGITransport
from src.api.app import create_app
from src.infrastructure.database.engine import create_test_engine

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_register_user_returns_201(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securePassword123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "password" not in data

@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "user1",
            "email": "test@example.com",
            "password": "securePassword123",
        },
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "user2",
            "email": "test@example.com",
            "password": "anotherPassword456",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"
```

### 1.3 End-to-End Tests (Target: ~5% of total tests)

**Purpose:** Verify complete user workflows from the API layer through to database persistence and back, simulating real user interactions.

**Scope:** Full request lifecycle — HTTP request → FastAPI router → use case → repository → database → response.

**Speed Target:** Entire suite completes in under 10 minutes. Individual test under 30 seconds.

**Location:** `tests/e2e/`

**When to write:** Critical user journeys only: registration → login → course enrollment → lesson completion → certificate issuance. Security-critical flows: authentication, MFA, credential management.

**Example:**

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_complete_user_journey(client: AsyncClient) -> None:
    # Step 1: Register
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "journeyuser",
            "email": "journey@example.com",
            "password": "securePassword123",
        },
    )
    assert register_response.status_code == 201

    # Step 2: Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "journeyuser",
            "password": "securePassword123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Step 3: Access protected resource
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = await client.get("/api/v1/users/me", headers=headers)
    assert profile_response.status_code == 200
    assert profile_response.json()["username"] == "journeyuser"
```

---

## 2. Test Naming Conventions

### 2.1 Python Test Naming

Follow the pattern: `test_{method_or_function}_{scenario}_{expected_outcome}`

```python
# Good test names
def test_authenticate_valid_credentials_returns_success() -> None: ...
def test_authenticate_invalid_password_returns_authentication_error() -> None: ...
def test_authenticate_locked_account_returns_account_locked_error() -> None: ...
def test_get_user_by_id_existing_user_returns_user() -> None: ...
def test_get_user_by_id_nonexistent_user_returns_none() -> None: ...
def test_email_address_empty_string_raises_value_error() -> None: ...
def test_calculate_risk_score_empty_findings_returns_zero() -> None: ...
def test_calculate_risk_score_multiple_critical_findings_returns_high_score() -> None: ...
```

**Rules:**
- Use `snake_case` for test function names.
- Prefix all test functions with `test_`.
- Each test name must describe: what is being tested, under what condition, what the expected result is.
- Avoid vague names like `test_auth_works` or `test_error_handling`.
- Test class names use `Test` prefix with PascalCase: `TestUserRepository`, `TestEmailAddress`.

### 2.2 TypeScript/Jest Test Naming

Follow the same principle adapted for Jest: `it('should {expected behavior} when {condition}')`

```typescript
describe('UserRepository', () => {
  describe('getById', () => {
    it('should return a user when a valid ID is provided', async () => {
      // ...
    });

    it('should return null when the user does not exist', async () => {
      // ...
    });

    it('should throw a database error when the connection fails', async () => {
      // ...
    });
  });
});
```

### 2.3 Test File Naming

| Type | Python File Name | TypeScript File Name |
|---|---|---|
| Unit test | `test_{module_name}.py` | `{ModuleName}.test.ts` or `{ModuleName}.spec.ts` |
| Integration test | `test_{module_name}_integration.py` | `{ModuleName}.integration.test.ts` |
| E2E test | `test_{workflow_name}_e2e.py` | `{Workflow}.e2e.test.ts` |

---

## 3. Test Organization

### 3.1 Directory Structure

```
tests/
  unit/
    domain/
      identity/
        test_email_address.py
        test_user.py
        test_user_role.py
      education/
        test_course.py
        test_lesson.py
        test_score.py
      security/
        test_risk_score.py
      events/
        test_event_bus.py
    application/
      identity/
        test_register_user.py
        test_authenticate_user.py
      education/
        test_complete_lesson.py
    infrastructure/
      repositories/
        test_sqlalchemy_user_repository.py
        test_sqlalchemy_course_repository.py
    api/
      routers/
        test_identity_routes.py
        test_education_routes.py
      schemas/
        test_login_request.py
  integration/
    test_user_registration_flow.py
    test_course_enrollment_flow.py
    test_database_migrations.py
    test_event_bus_with_repositories.py
  e2e/
    test_complete_user_journey.py
    test_mfa_enrollment_flow.py
    test_course_completion_journey.py
  fixtures/
    conftest.py
    factories.py
  helpers/
    test_client.py
    database.py
    assertions.py
```

### 3.2 Test Isolation Rules

- Tests must be order-independent. No test should depend on another test having run first.
- Each test must set up its own data and clean up after itself.
- Use database transactions with rollback for test isolation (preferred) or create/drop schemas per test.
- Never share mutable state between tests.
- Tests must not depend on external services, network access, or filesystem state outside the test directory.

### 3.3 conftest.py Hierarchy

```
tests/
  conftest.py              ← Root fixtures: database, event loop, test client
  unit/
    conftest.py            ← Unit-specific fixtures: mocks, stubs
  integration/
    conftest.py            ← Integration fixtures: real database, real services
  e2e/
    conftest.py            ← E2E fixtures: full application setup
```

**Rules:**
- Fixtures at each level are available to all tests in that directory and its subdirectories.
- Prefer the most specific fixture scope — if a fixture is only needed in one test file, define it there.
- Use `autouse=True` sparingly and only for fixtures that must run for every test in a scope (e.g., logging configuration, database cleanup).

---

## 4. Fixtures and Factories

### 4.1 pytest Fixtures

Use pytest fixtures for test setup. Fixtures are defined with `@pytest.fixture` and may be sync or async.

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def sample_user() -> User:
    return User(
        id=1,
        username="testuser",
        email=EmailAddress("test@example.com"),
        role=UserRole.STUDENT,
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )

@pytest.fixture
def mock_user_repository() -> AsyncMock:
    repo = AsyncMock(spec=UserRepository)
    repo.get_by_id.return_value = None
    repo.get_by_email.return_value = None
    repo.save.return_value = None
    return repo

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
```

### 4.2 Factory Pattern

Use factory classes for creating complex test objects with many fields. Factories provide sensible defaults while allowing overrides.

```python
from dataclasses import dataclass, field

class UserFactory:
    """Factory for creating User test instances."""

    _counter: int = 0

    @classmethod
    def create(cls, **overrides: Any) -> User:
        cls._counter += 1
        defaults = {
            "id": cls._counter,
            "username": f"testuser_{cls._counter}",
            "email": EmailAddress(f"user{cls._counter}@example.com"),
            "role": UserRole.STUDENT,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        defaults.update(overrides)
        return User(**defaults)

    @classmethod
    def create_many(cls, count: int, **overrides: Any) -> list[User]:
        return [cls.create(**overrides) for _ in range(count)]

    @classmethod
    def create_admin(cls, **overrides: Any) -> User:
        overrides["role"] = UserRole.ADMIN
        return cls.create(**overrides)

    @classmethod
    def create_inactive(cls, **overrides: Any) -> User:
        overrides["is_active"] = False
        return cls.create(**overrides)

    @classmethod
    def reset(cls) -> None:
        cls._counter = 0
```

### 4.3 Fixture Best Practices

- **Scope fixtures appropriately:** Use `scope="session"` for expensive setup (database engine), `scope="function"` for per-test data.
- **Avoid fixture inheritance chains deeper than 2 levels.** Complex fixture dependencies make tests hard to understand.
- **Name fixtures clearly:** `sample_user`, `mock_user_repository`, `database_session` — not `data`, `fixture1`, `setup`.
- **Document fixture purpose** with docstrings for any non-obvious fixture.
- **Reset factory counters** between test modules to ensure deterministic test IDs.

---

## 5. Mocking Strategies

### 5.1 When to Mock

| Situation | Mock? | Rationale |
|---|---|---|
| Unit testing a use case | YES — mock repositories | Isolate business logic from persistence |
| Unit testing a repository | NO — use real in-memory SQLite | Test actual SQL behavior |
| Unit testing API route | YES — mock services | Isolate routing from business logic |
| Integration test | NO — use real dependencies | Verify components work together |
| External service call | YES — mock HTTP responses | No network access in tests |
| File system operations | YES — use `tmp_path` fixture | Isolate from host filesystem |

### 5.2 Mocking Tools

- **Python:** `unittest.mock` — `MagicMock`, `AsyncMock`, `patch`, `patch.object`
- **TypeScript:** `jest.fn()`, `jest.mock()`, manual mocks in `__mocks__/` directories

### 5.3 Mocking Rules

1. **Prefer `spec` parameter** to constrain mock attributes to those that exist on the real object.
2. **Never mock what you don't own.** Mock at the boundary of your code, not internal implementation details of third-party libraries.
3. **Use `assert_awaited_once_with`** for async mocks to verify exact call arguments.
4. **Verify behavior, not implementation.** Assert on outputs and side effects, not on how many times an internal method was called.
5. **Reset mocks between tests** to prevent state leakage.

```python
# CORRECT — mocking at the boundary with spec
@pytest.fixture
def mock_user_repository() -> AsyncMock:
    repo = AsyncMock(spec=UserRepository)
    return repo

@pytest.mark.asyncio
async def test_register_user_calls_save(
    mock_user_repository: AsyncMock,
) -> None:
    # Arrange
    mock_user_repository.get_by_email.return_value = None
    use_case = RegisterUser(user_repository=mock_user_repository)

    # Act
    result = await use_case(
        username="newuser",
        email=EmailAddress("new@example.com"),
        password="securePassword123",
    )

    # Assert
    mock_user_repository.save.assert_awaited_once()
    saved_user = mock_user_repository.save.call_args[0][0]
    assert saved_user.username == "newuser"

# INCORRECT — mocking implementation details
@patch("src.application.identity.register_user.hash_password")
def test_register_user_hashes_password(mock_hash):
    # This test breaks if the hashing implementation changes
    # even if the behavior (password is hashed) remains correct
    ...
```

### 5.4 AsyncMock Patterns

```python
from unittest.mock import AsyncMock, MagicMock, patch

# Async function mock
async def mock_get_user(user_id: int) -> User | None:
    return UserFactory.create(id=user_id)

mock_repo = AsyncMock(spec=UserRepository)
mock_repo.get_by_id.side_effect = mock_get_user

# Patching an entire module function
with patch("src.infrastructure.database.engine.create_async_engine") as mock_engine:
    mock_engine.return_value = AsyncMock()
    # test code here

# Context manager mock
mock_session = AsyncMock(spec=AsyncSession)
mock_session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
```

---

## 6. Async Testing

### 6.1 pytest-asyncio Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # All async tests run with asyncio automatically
asyncio_default_fixture_loop_scope = "function"  # Fresh event loop per test
```

### 6.2 Async Test Patterns

```python
import pytest
from httpx import AsyncClient

# Async test function — automatically collected by pytest-asyncio
@pytest.mark.asyncio
async def test_async_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

# Async fixture
@pytest.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine)() as session:
        yield session
    await engine.dispose()

# Testing concurrent operations
@pytest.mark.asyncio
async def test_concurrent_operations() -> None:
    tasks = [process_item(i) for i in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    assert all(isinstance(r, Result) for r in results)
```

### 6.3 Async Testing Rules

- All async tests must use `@pytest.mark.asyncio` or be configured with `asyncio_mode = "auto"`.
- Async fixtures must use `AsyncGenerator` return type.
- Never use `asyncio.run()` inside tests — let `pytest-asyncio` manage the event loop.
- Use `asyncio.gather()` to test concurrent scenarios.
- Set appropriate timeouts on async tests to prevent hung tests.
- Use `pytest-asyncio`'s `loop_scope` fixture for database session fixtures to ensure proper cleanup.

### 6.4 FastAPI Test Client

```python
from httpx import AsyncClient, ASGITransport

@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## 7. Performance Testing

### 7.1 Benchmark Tests

Use `pytest-benchmark` for function-level performance benchmarks.

```python
import pytest

def test_benchmark_risk_score_calculation(benchmark) -> None:
    findings = [FindingFactory.create_many(100)]
    result = benchmark(calculate_risk_score, findings, DEFAULT_WEIGHTS)
    assert result.score > 0

def test_benchmark_user_repository_query(benchmark, db_session) -> None:
    repo = SQLAlchemyUserRepository(db_session)
    users = UserFactory.create_many(1000)
    for user in users:
        db_session.add(user)
    db_session.commit()

    benchmark.pedantic(
        lambda: db_session.run_sync(lambda s: s.execute(select(User).limit(10))),
        rounds=100,
    )
```

### 7.2 Load Testing

Load tests simulate concurrent users to identify performance bottlenecks and verify throughput requirements.

**Tool:** Custom async load test script or `locust` / `k6`.

**Scenarios:**

| Scenario | Concurrent Users | Duration | Expected Throughput |
|---|---|---|---|
| Normal load | 10 | 5 min | 100 req/s |
| Peak load | 50 | 5 min | 500 req/s |
| Stress test | 100 | 5 min | 1000 req/s (graceful degradation) |

**Thresholds:**

| Metric | Normal Load | Peak Load | Stress |
|---|---|---|---|
| p50 response time | < 50ms | < 100ms | < 200ms |
| p95 response time | < 100ms | < 200ms | < 500ms |
| p99 response time | < 200ms | < 500ms | < 1000ms |
| Error rate | 0% | < 1% | < 5% |
| Throughput | > 100 req/s | > 500 req/s | > 1000 req/s |

### 7.3 Performance Regression Detection

- Benchmark tests run on every PR that modifies performance-critical code.
- Results are compared against a baseline stored in `tests/performance/baselines.json`.
- Regression threshold: 10% slower than baseline triggers a warning, 25% triggers a failure.
- Baselines are updated monthly by running benchmarks on a dedicated performance testing environment.

---

## 8. Security Testing

### 8.1 Automated Security Tests

| Test Type | Tool | Scope | Frequency |
|---|---|---|---|
| SAST (Static Analysis) | `bandit` | Python source code | Every CI run |
| SAST (JavaScript) | `eslint-plugin-security` | Frontend source code | Every CI run |
| Dependency audit | `pip-audit`, `npm audit` | Third-party dependencies | Every CI run |
| Secret detection | `detect-secrets` | All files | Every commit (pre-commit hook) |
| Container scan | `trivy` | Docker images (if applicable) | On image build |

### 8.2 Authentication Security Tests

```python
@pytest.mark.asyncio
async def test_login_brute_force_protection(client: AsyncClient) -> None:
    """Verify account lockout after max failed attempts."""
    # Register user
    await client.post("/api/v1/auth/register", json={
        "username": "locktest",
        "email": "lock@example.com",
        "password": "securePassword123",
    })

    # Attempt 5 failed logins
    for _ in range(5):
        await client.post("/api/v1/auth/login", json={
            "username": "locktest",
            "password": "wrongpassword",
        })

    # Verify account is locked
    response = await client.post("/api/v1/auth/login", json={
        "username": "locktest",
        "password": "securePassword123",
    })
    assert response.status_code == 423
    assert response.json()["error"]["code"] == "ACCOUNT_LOCKED"

@pytest.mark.asyncio
async def test_password_not_exposed_in_error_messages(client: AsyncClient) -> None:
    """Verify password hashes are never leaked in responses."""
    response = await client.post("/api/v1/auth/login", json={
        "username": "nonexistent",
        "password": "testPassword123",
    })
    response_text = response.text
    assert "testPassword123" not in response_text
    assert "$2b$" not in response_text  # bcrypt hash prefix
    assert "argon2" not in response_text
```

### 8.3 Authorization Security Tests

```python
@pytest.mark.asyncio
async def test_user_cannot_access_other_users_data(client: AsyncClient) -> None:
    """Verify users cannot access other users' private data."""
    # Create user A and get token
    token_a = await register_and_login(client, "userA", "a@example.com")

    # Create user B
    await register_and_login(client, "userB", "b@example.com")

    # User A tries to access User B's profile
    response = await client.get(
        "/api/v1/users/2",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_unauthenticated_access_returns_401(client: AsyncClient) -> None:
    """Verify protected endpoints reject unauthenticated requests."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
```

### 8.4 Input Validation Security Tests

```python
@pytest.mark.asyncio
async def test_sql_injection_prevented(client: AsyncClient) -> None:
    """Verify SQL injection is prevented in user search."""
    response = await client.get(
        "/api/v1/users?search='; DROP TABLE users; --",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Should return empty results, not crash
    assert response.status_code == 200
    assert response.json()["results"] == []

@pytest.mark.asyncio
async def test_path_traversal_prevented(client: AsyncClient) -> None:
    """Verify path traversal is prevented in file operations."""
    response = await client.get(
        "/api/v1/content?file=../../../etc/passwd",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (400, 403, 404)
```

---

## 9. Accessibility Testing

### 9.1 Automated Accessibility Tests

```typescript
import { render, screen } from '@testing-library/react';
import axe, { AxeResults } from 'axe-core';
import { configureAxe } from 'jest-axe';

const axeInstance = configureAxe(render);

describe('LoginForm accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<LoginForm />);
    const results: AxeResults = await axeInstance(container);
    expect(results.violations).toHaveLength(0);
  });
});
```

### 9.2 Manual Accessibility Test Checklist

| Check | Tool/Method | Pass/Fail |
|---|---|---|
| Tab order is logical | Manual keyboard navigation | All interactive elements reachable in order |
| Focus is visible | Visual inspection | Focus ring clearly visible on all elements |
| Color contrast sufficient | Lighthouse / axe-core | ≥ 4.5:1 for normal text |
| All images have alt text | Screen reader / manual | All meaningful images described |
| Forms have labels | Screen reader / manual | Every input has associated label |
| Error messages are text-based | Manual | Errors not conveyed by color alone |
| Content reflows at 200% zoom | Browser zoom | No horizontal scrolling needed |
| Reduced motion respected | CSS media query | Animations disabled when preference set |

### 9.3 Lighthouse CI Integration

```yaml
# In CI pipeline
- name: Run Lighthouse CI
  run: |
    npx lhci autorun \
      --config=lighthouserc.json \
      --assert.assertions.accessibility=above:90 \
      --assert.assertions.performance=above:80
```

---

## 10. Code Coverage Requirements

### 10.1 Coverage Targets

| Test Layer | Minimum Coverage | Target Coverage | Measurement |
|---|---|---|---|
| Unit tests | 80% line coverage | 90% line coverage | `pytest --cov=src --cov-report=term-missing` |
| Integration tests | 60% line coverage (cumulative with unit) | 75% | Same tool |
| Overall (unit + integration) | 80% line coverage | 90% | Combined report |
| Branch coverage | 70% branch coverage | 80% | `pytest --cov-branch` |

### 10.2 Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "src/**/migrations/*",
    "src/**/__main__.py",
    "src/api/app.py",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
    "@overload",
    "raise NotImplementedError",
    "\\.\\.\\.",
]

[tool.coverage.html]
directory = "htmlcov"
```

### 10.3 Coverage Rules

- Coverage thresholds are enforced in CI. PRs that降低 overall coverage below the threshold are blocked.
- New code must have ≥ 90% line coverage. Existing code coverage may remain at the 80% threshold.
- Coverage for `domain/` layer must be ≥ 90% — this is the most critical code.
- Coverage exclusions must be justified and documented in `pyproject.toml` comments.
- Coverage reports are generated on every CI run and attached as artifacts for review.

### 10.4 What Coverage Does NOT Guarantee

- **Coverage does not equal quality.** 100% coverage with poor assertions is meaningless.
- **Coverage cannot detect missing tests** for untested edge cases that happen to execute the same lines.
- **Coverage should guide, not dictate.** If a function has 100% coverage but critical untested behavior, write more tests regardless of coverage numbers.

---

## 11. Test Data Management

### 11.1 Test Data Principles

1. **Synthetic data only.** Never use real user data, production data, or personally identifiable information in tests.
2. **Deterministic where possible.** Tests should produce the same result regardless of when or where they run. Use fixed seeds for random data.
3. **Minimal.** Each test uses only the data it needs. No test should create more data than necessary.
4. **Self-contained.** Each test creates its own data. No test depends on data created by another test.
5. **Clean.** Test data is cleaned up after each test run (database rollback, temp file deletion).

### 11.2 Test Data Patterns

#### Inline Data (Preferred for Simple Cases)
```python
def test_email_validation() -> None:
    valid_emails = ["user@example.com", "admin@company.org", "test+tag@domain.co"]
    invalid_emails = ["", "no-at-sign", "@no-local.com", "spaces in@email.com"]

    for email in valid_emails:
        assert EmailAddress(email).value == email

    for email in invalid_emails:
        with pytest.raises(ValueError):
            EmailAddress(email)
```

#### Factory Data (Preferred for Complex Objects)
```python
@pytest.mark.asyncio
async def test_user_list_pagination(client: AsyncClient, db_session: AsyncSession) -> None:
    users = UserFactory.create_many(25)
    for user in users:
        db_session.add(user)
    await db_session.commit()

    response = await client.get("/api/v1/users?page=1&per_page=10")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 10
    assert response.json()["total"] == 25
```

#### Fixtures for Shared State
```python
@pytest.fixture
async def populated_database(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Database with a standard set of test data for integration tests."""
    users = UserFactory.create_many(5)
    courses = CourseFactory.create_many(3)
    for user in users:
        db_session.add(user)
    for course in courses:
        db_session.add(course)
    await db_session.commit()
    yield
```

### 11.3 Database Test Isolation

```python
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Isolated database session using in-memory SQLite with transaction rollback."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
```

---

## 12. Flaky Test Policy

### 12.1 Definition

A flaky test is a test that produces inconsistent results (passes and fails) across multiple runs without any code changes.

### 12.2 Detection

- CI pipeline tracks test results across runs.
- Any test that fails and then passes on retry without code changes is flagged as flaky.
- Flaky tests are tracked in the `#test-flaky` Slack channel or equivalent.
- Weekly flaky test reports are generated from CI data.

### 12.3 Classification

| Severity | Flakiness Rate | Action |
|---|---|---|
| Critical | Fails > 20% of runs | Fix or skip within 24 hours |
| High | Fails 10-20% of runs | Fix within current sprint |
| Medium | Fails 5-10% of runs | Fix within next sprint |
| Low | Fails < 5% of runs | Track and fix opportunistically |

### 12.4 Common Causes and Fixes

| Cause | Symptom | Fix |
|---|---|---|
| Race condition | Intermittent assertion failures | Add proper synchronization, use deterministic waits |
| Shared state | Failures depend on test order | Ensure test isolation, use fresh fixtures |
| Time dependency | Fails at certain times of day | Use time mocking, avoid real clock dependencies |
| Network dependency | Fails without internet | Mock all external services |
| Database state leak | Failures after specific test combinations | Use transaction rollback isolation |
| Random data | Different results with different inputs | Use fixed random seeds |
| Resource exhaustion | Fails under load | Add resource cleanup, limit concurrent tests |

### 12.5 Flaky Test Remediation Process

1. **Identify:** CI flags the test as flaky. Engineer adds it to the flaky test tracker.
2. **Investigate:** Root cause analysis within 1 business day.
3. **Fix:** Implement the fix and verify with 20+ consecutive runs.
4. **Verify:** Monitor the test for 5 additional CI runs to confirm the fix is effective.
5. **Close:** Remove the flaky test label and update the tracker.

### 12.6 Retry Policy

- **CI retries:** Failed tests are retried once automatically to distinguish flakiness from real failures.
- **Max retries:** 1 retry per test. If it fails again, it is a real failure.
- **Retry logging:** All retries are logged with timestamps and the original error.
- **Flaky test skip:** Tests flagged as Critical or High severity flaky are temporarily skipped with `@pytest.mark.skip(reason="Flaky: tracking issue #123")` while being investigated. The skip must be removed within 5 business days.

---

*This document is a living artifact. Propose changes via PR to the repository. All changes require approval from the Engineering Lead and QA representative.*
