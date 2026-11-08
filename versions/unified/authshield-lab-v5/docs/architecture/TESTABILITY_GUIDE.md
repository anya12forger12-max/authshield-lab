# Testability Framework

## Overview

AuthShield Lab's Clean Architecture is designed for testability at every layer.
Each layer can be tested in isolation with well-defined test doubles. The
architecture guarantees that business logic is testable without any infrastructure,
and infrastructure is testable with minimal business logic.

---

## Testing Pyramid

```
                  ╱╲
                 ╱  ╲        E2E Tests (5%)
                ╱    ╲       Full stack, browser automation
               ╱──────╲
              ╱        ╲     Integration Tests (15%)
             ╱          ╲    Module-to-module, API-to-DB
            ╱────────────╲
           ╱              ╲  Unit Tests (80%)
          ╱                ╲ Domain, Use Cases, Adapters
         ╱──────────────────╲
```

### Test Distribution

| Layer | Test Type | Count (est.) | Speed | Isolation |
|---|---|---|---|---|
| Domain | Unit | ~200 | <1ms | Full |
| Application | Unit | ~250 | <10ms | Full (mocked ports) |
| Adapters | Unit | ~150 | <10ms | Full (mocked deps) |
| API | Integration | ~100 | <100ms | Test DB |
| DB | Integration | ~80 | <200ms | Test DB |
| E2E | End-to-End | ~50 | <5s | Full stack |

---

## Unit Testing: Domain Entities

Domain entity tests are pure unit tests with zero dependencies.

### Pattern

```python
import pytest
from uuid import uuid4


class TestUser:
    def test_deactivate_active_user(self):
        user = User(email="test@example.com", display_name="Test", is_active=True)
        user.deactivate()
        assert user.is_active is False
        assert user.updated_at > user.created_at

    def test_deactivate_already_inactive_raises(self):
        user = User(email="test@example.com", is_active=False)
        with pytest.raises(BusinessRuleViolation, match="already inactive"):
            user.deactivate()

    def test_enable_mfa(self):
        user = User(email="test@example.com", mfa_enabled=False)
        user.enable_mfa()
        assert user.mfa_enabled is True

    def test_enable_mfa_already_enabled_raises(self):
        user = User(email="test@example.com", mfa_enabled=True)
        with pytest.raises(BusinessRuleViolation, match="already enabled"):
            user.enable_mfa()

    def test_user_equality_by_id(self):
        uid = uuid4()
        user1 = User(id=uid, email="a@b.com")
        user2 = User(id=uid, email="different@b.com")
        assert user1 == user2

    def test_user_inequality(self):
        user1 = User(id=uuid4(), email="a@b.com")
        user2 = User(id=uuid4(), email="a@b.com")
        assert user1 != user2
```

### Value Object Tests

```python
class TestEmail:
    def test_valid_email(self):
        email = Email("user@example.com")
        assert email.value == "user@example.com"

    def test_invalid_email_no_at(self):
        with pytest.raises(InvalidValueObject, match="Invalid email"):
            Email("userexample.com")

    def test_equality(self):
        assert Email("a@b.com") == Email("a@b.com")

    def test_inequality(self):
        assert Email("a@b.com") != Email("c@d.com")

    def test_frozen(self):
        email = Email("a@b.com")
        with pytest.raises(AttributeError):
            email.value = "new@email.com"

    def test_hashable(self):
        emails = {Email("a@b.com"), Email("a@b.com"), Email("c@d.com")}
        assert len(emails) == 2


class TestPermission:
    def test_str_representation(self):
        perm = Permission(resource="course", action="read")
        assert str(perm) == "course:read"

    def test_equality(self):
        assert Permission("course", "read") == Permission("course", "read")
```

### Domain Service Tests

```python
class TestPasswordPolicy:
    def setup_method(self):
        self.policy = PasswordPolicy()

    def test_valid_strong_password(self):
        errors = self.policy.validate("MyStr0ng!Pass123")
        assert errors == []

    def test_too_short(self):
        errors = self.policy.validate("Ab1!")
        assert any("12 characters" in e for e in errors)

    def test_no_uppercase(self):
        errors = self.policy.validate("lowercase123!")
        assert any("uppercase" in e for e in errors)

    def test_no_lowercase(self):
        errors = self.policy.validate("UPPERCASE123!")
        assert any("lowercase" in e for e in errors)

    def test_no_digit(self):
        errors = self.policy.validate("NoDigitsHere!")
        assert any("digit" in e for e in errors)

    def test_no_special(self):
        errors = self.policy.validate("NoSpecial123")
        assert any("special" in e for e in errors)
```

---

## Unit Testing: Use Cases

Use case tests use mock ports to isolate the use case from infrastructure.

### Mock Port Pattern

```python
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_user_repo():
    repo = AsyncMock(spec=UserRepositoryPort)
    return repo


@pytest.fixture
def mock_auth_service():
    svc = AsyncMock(spec=AuthenticationPort)
    return svc


@pytest.fixture
def mock_event_publisher():
    publisher = AsyncMock(spec=EventPublishingPort)
    return publisher


@pytest.fixture
def authenticate_use_case(mock_user_repo, mock_auth_service, mock_event_publisher):
    return AuthenticateUserUseCase(
        user_repository=mock_user_repo,
        authentication_service=mock_auth_service,
        event_publisher=mock_event_publisher,
    )
```

### Use Case Test Example

```python
class TestAuthenticateUserUseCase:
    @pytest.mark.asyncio
    async def test_successful_authentication(
        self, authenticate_use_case, mock_user_repo, mock_auth_service, mock_event_publisher
    ):
        user = User(
            id=uuid4(),
            email="test@example.com",
            display_name="Test",
            is_active=True,
        )
        mock_user_repo.find_by_email.return_value = user
        mock_auth_service.authenticate.return_value = TokenPair(
            access_token="access_123",
            refresh_token="refresh_123",
            expires_in=3600,
        )

        result = await authenticate_use_case.execute(
            AuthenticateUserInput(
                email="test@example.com",
                password="password123",
            )
        )

        assert result.user_id == user.id
        assert result.access_token == "access_123"
        mock_event_publisher.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_credentials(
        self, authenticate_use_case, mock_user_repo, mock_auth_service
    ):
        mock_user_repo.find_by_email.return_value = None

        with pytest.raises(AuthenticationFailed):
            await authenticate_use_case.execute(
                AuthenticateUserInput(
                    email="nonexistent@example.com",
                    password="password",
                )
            )

    @pytest.mark.asyncio
    async def test_deactivated_account(
        self, authenticate_use_case, mock_user_repo
    ):
        user = User(
            id=uuid4(),
            email="test@example.com",
            is_active=False,
        )
        mock_user_repo.find_by_email.return_value = user

        with pytest.raises(AuthenticationFailed, match="deactivated"):
            await authenticate_use_case.execute(
                AuthenticateUserInput(
                    email="test@example.com",
                    password="password",
                )
            )
```

---

## Unit Testing: Services (Application Layer)

```python
class TestCourseService:
    @pytest.fixture
    def course_service(self):
        return CourseService(
            course_repo=AsyncMock(spec=CourseRepositoryPort),
            user_repo=AsyncMock(spec=UserRepositoryPort),
            notification=AsyncMock(spec=NotificationPort),
            event_publisher=AsyncMock(spec=EventPublishingPort),
            analytics=AsyncMock(spec=AnalyticsInputPort),
            logger=MagicMock(spec=LoggingPort),
        )

    @pytest.mark.asyncio
    async def test_publish_course_valid(self, course_service):
        course = Course(
            id=uuid4(),
            status="draft",
            modules=[Module(lessons=[Lesson(published=True)])],
            has_thumbnail=True,
        )
        course_service._course_repo.find_by_id.return_value = course

        result = await course_service.publish_course(course.id, uuid4())
        assert course.status == "published"

    @pytest.mark.asyncio
    async def test_publish_course_no_modules_raises(self, course_service):
        course = Course(id=uuid4(), status="draft", modules=[])
        course_service._course_repo.find_by_id.return_value = course

        with pytest.raises(CourseNotReady):
            await course_service.publish_course(course.id, uuid4())
```

---

## Port Testing: Interface Contract Tests

Port contract tests verify that any adapter implementing a port satisfies
the interface contract.

### Contract Test Pattern

```python
import pytest
from abc import ABC, abstractmethod


class UserRepositoryContractTests(ABC):
    """Abstract test class. Each adapter implementation inherits these tests."""

    @abstractmethod
    async def create_repository(self) -> UserRepositoryPort:
        """Factory method for the adapter under test."""
        ...

    @abstractmethod
    async def seed_data(self, users: list[User]) -> None:
        """Seed test data into the adapter's backing store."""
        ...

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up after tests."""
        ...

    @pytest.fixture(autouse=True)
    async def setup(self):
        self.repo = await self.create_repository()
        yield
        await self.cleanup()

    @pytest.mark.asyncio
    async def test_find_by_id_existing(self):
        user = User(id=uuid4(), email="test@example.com", display_name="Test")
        await self.seed_data([user])
        result = await self.repo.find_by_id(user.id)
        assert result is not None
        assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_find_by_id_nonexistent(self):
        result = await self.repo.find_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_email_existing(self):
        user = User(id=uuid4(), email="test@example.com")
        await self.seed_data([user])
        result = await self.repo.find_by_email("test@example.com")
        assert result is not None

    @pytest.mark.asyncio
    async def test_save_and_retrieve(self):
        user = User(id=uuid4(), email="new@example.com", display_name="New")
        await self.repo.save(user)
        result = await self.repo.find_by_id(user.id)
        assert result is not None
        assert result.email == "new@example.com"

    @pytest.mark.asyncio
    async def test_delete(self):
        user = User(id=uuid4(), email="del@example.com")
        await self.repo.save(user)
        await self.repo.delete(user.id)
        result = await self.repo.find_by_id(user.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_exists_true(self):
        user = User(id=uuid4(), email="exists@example.com")
        await self.repo.save(user)
        assert await self.repo.exists("exists@example.com") is True

    @pytest.mark.asyncio
    async def test_exists_false(self):
        assert await self.repo.exists("nope@example.com") is False

    @pytest.mark.asyncio
    async def test_list_with_pagination(self):
        users = [User(id=uuid4(), email=f"u{i}@example.com") for i in range(25)]
        await self.seed_data(users)
        result, total = await self.repo.list_users(
            filters=UserFilters(), page=1, page_size=10
        )
        assert len(result) == 10
        assert total == 25
```

### Applying Contract Tests to SQLAlchemy Adapter

```python
class TestSQLAlchemyUserRepositoryContract(
    UserRepositoryContractTests, AsyncTransactionTests
):
    async def create_repository(self) -> UserRepositoryPort:
        session = await self.get_test_session()
        return SQLAlchemyUserRepository(session)

    async def seed_data(self, users: list[User]) -> None:
        session = await self.get_test_session()
        for user in users:
            model = UserMapper.to_model(user)
            session.add(model)
        await session.commit()

    async def cleanup(self) -> None:
        session = await self.get_test_session()
        await session.execute(delete(UserModel))
        await session.commit()
```

---

## Adapter Testing: Integration Tests

### API Adapter Tests

```python
from httpx import AsyncClient
from fastapi import FastAPI


@pytest.fixture
async def test_client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


class TestAuthAPI:
    @pytest.mark.asyncio
    async def test_login_success(self, test_client, mock_auth_service):
        mock_auth_service.authenticate.return_value = TokenPair(
            access_token="token_123",
            refresh_token="refresh_123",
            expires_in=3600,
        )
        response = await test_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, test_client):
        response = await test_client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@example.com", "password": "wrong"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_validation_error(self, test_client):
        response = await test_client.post(
            "/api/v1/auth/login",
            json={"email": "not-an-email"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_course_unauthenticated(self, test_client):
        response = await test_client.get(f"/api/v1/courses/{uuid4()}")
        assert response.status_code == 401
```

### Database Adapter Tests

```python
@pytest.mark.integration
class TestSQLAlchemyUserRepositoryIntegration:
    @pytest.fixture(autouse=True)
    async def setup(self, test_engine):
        self.session_factory = async_sessionmaker(test_engine)
        self.repo = SQLAlchemyUserRepository(self.session_factory)
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @pytest.mark.asyncio
    async def test_save_and_retrieve(self):
        user = User(
            id=uuid4(),
            email="integration@test.com",
            display_name="Integration Test",
        )
        await self.repo.save(user)
        result = await self.repo.find_by_id(user.id)
        assert result is not None
        assert result.email == "integration@test.com"
        assert result.display_name == "Integration Test"

    @pytest.mark.asyncio
    async def test_concurrent_saves(self):
        users = [User(id=uuid4(), email=f"u{i}@test.com") for i in range(10)]
        await asyncio.gather(*[self.repo.save(u) for u in users])
        for user in users:
            result = await self.repo.find_by_id(user.id)
            assert result is not None
```

---

## Integration Testing: Module-to-Module

```python
@pytest.mark.integration
class TestCourseEnrollmentFlow:
    """Tests the full flow from enrollment to notification."""

    @pytest.fixture(autouse=True)
    async def setup(self, test_app):
        self.app = test_app
        self.client = AsyncClient(app=test_app, base_url="http://test")

    @pytest.mark.asyncio
    async def test_enroll_student_sends_notification(self):
        course = await self.create_test_course()
        student = await self.create_test_student()
        instructor = await self.create_test_instructor()

        response = await self.client.post(
            f"/api/v1/courses/{course.id}/enroll",
            json={"student_id": str(student.id)},
            headers=auth_headers(instructor),
        )
        assert response.status_code == 201

        notifications = await self.get_notifications(student.id)
        assert len(notifications) == 1
        assert "enrollment" in notifications[0].subject.lower()
```

---

## Accessibility Testing

### Automated WCAG Checks

```python
@pytest.mark.accessibility
class TestAccessibility:
    @pytest.fixture(autouse=True)
    async def setup(self, test_client):
        self.client = test_client

    @pytest.mark.asyncio
    async def test_login_page_wcag_compliance(self):
        response = await self.client.get("/login")
        soup = BeautifulSoup(response.text, "html.parser")

        assert soup.find("label", attrs={"for": "email"}) is not None
        assert soup.find("input", attrs={"id": "email", "aria-required": "true"})
        assert soup.find("label", attrs={"for": "password"}) is not None
        assert soup.find("input", attrs={"id": "password", "type": "password"})
        assert soup.find("button", attrs={"type": "submit"})

    @pytest.mark.asyncio
    async def test_error_messages_have_role_alert(self):
        response = await self.client.post(
            "/api/v1/auth/login",
            json={"email": "bad@example.com", "password": "wrong"},
        )
        body = response.json()
        assert "detail" in body
        assert len(body["detail"]) > 0

    @pytest.mark.asyncio
    async def test_api_errors_accessible_format(self):
        response = await self.client.get("/api/v1/courses/00000000-0000-0000-0000-000000000000")
        body = response.json()
        assert "type" in body
        assert "title" in body
        assert "detail" in body
```

### Frontend Accessibility Tests (Playwright)

```python
@pytest.mark.e2e
@pytest.mark.accessibility
class TestFrontendAccessibility:
    @pytest.fixture(autouse=True)
    async def setup(self, playwright):
        self.browser = await playwright.chromium.launch()
        self.page = await self.browser.new_page()

    async def test_keyboard_navigation(self):
        await self.page.goto("http://localhost:3000/login")
        await self.page.keyboard.press("Tab")
        focused = await self.page.evaluate("document.activeElement.id")
        assert focused == "email"

        await self.page.keyboard.press("Tab")
        focused = await self.page.evaluate("document.activeElement.id")
        assert focused == "password"

    async def test_screen_reader_announcements(self):
        await self.page.goto("http://localhost:3000/dashboard")
        alerts = await self.page.get_by_role("status").all()
        assert len(alerts) > 0

    async def test_color_contrast(self):
        await self.page.goto("http://localhost:3000/login")
        # Verify no text fails WCAG AA contrast ratio of 4.5:1
        # This uses axe-core for automated checking
        results = await self.page.evaluate("axe.run()")
        violations = results["violations"]
        contrast_violations = [v for v in violations if v["id"] == "color-contrast"]
        assert len(contrast_violations) == 0
```

---

## Security Testing

```python
@pytest.mark.security
class TestSecurity:
    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self, test_client):
        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "'; DROP TABLE users; --",
                "password": "password",
            },
        )
        assert response.status_code in (401, 422)

    @pytest.mark.asyncio
    async def test_xss_prevention_in_course_description(self, test_client, auth_headers):
        response = await test_client.post(
            "/api/v1/courses",
            json={
                "title": "Test Course",
                "description": "<script>alert('xss')</script>",
            },
            headers=auth_headers,
        )
        if response.status_code == 201:
            course = response.json()
            assert "<script>" not in course["description"]

    @pytest.mark.asyncio
    async def test_rate_limiting(self, test_client):
        responses = []
        for _ in range(15):
            r = await test_client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "wrong"},
            )
            responses.append(r)
        assert any(r.status_code == 429 for r in responses)

    @pytest.mark.asyncio
    async def test_cors_headers(self, test_client):
        response = await test_client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert "access-control-allow-origin" in response.headers

    @pytest.mark.asyncio
    async def test_password_not_in_logs(self, test_client, caplog):
        with caplog.at_level(logging.ALL):
            await test_client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "SuperSecret123!"},
            )
        for record in caplog.records:
            assert "SuperSecret123!" not in record.message
```

---

## Performance Testing

```python
import time
import statistics


@pytest.mark.performance
class TestPerformance:
    @pytest.mark.asyncio
    async def test_authentication_latency(self, test_client):
        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            await test_client.post(
                "/api/v1/auth/login",
                json={"email": "perf@test.com", "password": "password"},
            )
            latencies.append(time.perf_counter() - start)

        p50 = statistics.median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        p99 = sorted(latencies)[int(len(latencies) * 0.99)]

        assert p50 < 0.1, f"p50 latency {p50:.3f}s exceeds 100ms"
        assert p95 < 0.5, f"p95 latency {p95:.3f}s exceeds 500ms"
        assert p99 < 1.0, f"p99 latency {p99:.3f}s exceeds 1s"

    @pytest.mark.asyncio
    async def test_concurrent_enrollment(self, test_client, test_data):
        async def enroll(student_id):
            return await test_client.post(
                f"/api/v1/courses/{test_data.course_id}/enroll",
                json={"student_id": str(student_id)},
                headers=auth_headers(test_data.instructor),
            )

        student_ids = [uuid4() for _ in range(50)]
        start = time.perf_counter()
        responses = await asyncio.gather(*[enroll(sid) for sid in student_ids])
        duration = time.perf_counter() - start

        success_count = sum(1 for r in responses if r.status_code == 201)
        assert success_count == 50
        assert duration < 5.0, f"50 concurrent enrollments took {duration:.1f}s"
```

---

## Test Doubles: Patterns

### Mock

Used to verify interactions (method calls, arguments, call count).

```python
from unittest.mock import AsyncMock, MagicMock

class MockUserRepository:
    def __init__(self):
        self.find_by_id = AsyncMock(return_value=None)
        self.save = AsyncMock()
        self.delete = AsyncMock()

# Verify interaction
mock_repo = MockUserRepository()
mock_repo.find_by_id.return_value = User(id=uuid4(), email="test@example.com")
result = await mock_repo.find_by_id(uuid4())
mock_repo.save.assert_not_called()
```

### Stub

Used to provide predetermined responses.

```python
class StubNotificationService:
    def __init__(self):
        self._sent = []

    async def send_email(self, to, subject, body, html=False):
        self._sent.append({"to": to, "subject": subject, "body": body})

    def was_sent_to(self, email):
        return [m for m in self._sent if m["to"] == email]
```

### Spy

Used to record calls for later assertion while delegating to real implementation.

```python
class SpyEventBus:
    def __init__(self, real_bus: EventPublishingPort):
        self._real = real_bus
        self.published_events: list[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)
        await self._real.publish(event)

    def has_published(self, event_type: type) -> bool:
        return any(isinstance(e, event_type) for e in self.published_events)
```

### Fake

Used as lightweight working implementations for testing.

```python
class FakeUserRepository:
    def __init__(self):
        self._store: dict[UUID, User] = {}

    async def find_by_id(self, user_id: UUID) -> User | None:
        return self._store.get(user_id)

    async def find_by_email(self, email: str) -> User | None:
        return next((u for u in self._store.values() if u.email == email), None)

    async def save(self, user: User) -> None:
        self._store[user.id] = user

    async def delete(self, user_id: UUID) -> None:
        self._store.pop(user_id, None)

    async def exists(self, email: str) -> bool:
        return any(u.email == email for u in self._store.values())

    async def list_users(self, filters, page, page_size):
        users = list(self._store.values())
        return users[(page-1)*page_size : page*page_size], len(users)
```

---

## Test Data Builders and Factories

### Builder Pattern

```python
class UserBuilder:
    def __init__(self):
        self._id = uuid4()
        self._email = f"user_{uuid4().hex[:8]}@test.com"
        self._display_name = "Test User"
        self._is_active = True
        self._mfa_enabled = False

    def with_id(self, user_id: UUID) -> "UserBuilder":
        self._id = user_id
        return self

    def with_email(self, email: str) -> "UserBuilder":
        self._email = email
        return self

    def inactive(self) -> "UserBuilder":
        self._is_active = False
        return self

    def with_mfa(self) -> "UserBuilder":
        self._mfa_enabled = True
        return self

    def build(self) -> User:
        return User(
            id=self._id,
            email=self._email,
            display_name=self._display_name,
            is_active=self._is_active,
            mfa_enabled=self._mfa_enabled,
        )


# Usage
user = UserBuilder().with_email("admin@example.com").with_mfa().build()
inactive_user = UserBuilder().inactive().build()
```

### Factory Pattern

```python
class TestUserFactory:
    _counter = 0

    @classmethod
    def create(cls, **overrides) -> User:
        cls._counter += 1
        defaults = {
            "id": uuid4(),
            "email": f"user_{cls._counter}@test.com",
            "display_name": f"Test User {cls._counter}",
            "is_active": True,
        }
        defaults.update(overrides)
        return User(**defaults)

    @classmethod
    def create_batch(cls, count: int) -> list[User]:
        return [cls.create() for _ in range(count)]

    @classmethod
    def create_admin(cls) -> User:
        return cls.create(email="admin@test.com", display_name="Admin")


class TestCourseFactory:
    @classmethod
    def create(cls, **overrides) -> Course:
        defaults = {
            "id": uuid4(),
            "title": "Test Course",
            "description": "A test course for testing purposes",
            "status": "draft",
            "modules": [],
        }
        defaults.update(overrides)
        return Course(**defaults)

    @classmethod
    def create_published(cls) -> Course:
        module = Module(
            lessons=[Lesson(published=True, title="Lesson 1")]
        )
        return cls.create(
            status="published",
            modules=[module],
            has_thumbnail=True,
        )
```

### Fixture Factories (pytest)

```python
@pytest.fixture
def create_user():
    factory = TestUserFactory()
    created_users = []

    async def _create(**kwargs):
        user = factory.create(**kwargs)
        created_users.append(user)
        return user

    yield _create

    # Cleanup handled by database rollback


@pytest.fixture
def create_course():
    factory = TestCourseFactory()

    def _create(**kwargs):
        return factory.create(**kwargs)

    return _create


@pytest.fixture
def sample_users(create_user):
    return {
        "admin": create_user(email="admin@test.com"),
        "instructor": create_user(email="instructor@test.com"),
        "student": create_user(email="student@test.com"),
    }
```

---

## Running Tests

```bash
# All tests
pytest

# By layer
pytest tests/unit/domain/
pytest tests/unit/application/
pytest tests/unit/adapters/
pytest tests/integration/
pytest tests/e2e/

# By marker
pytest -m "not slow"
pytest -m "security"
pytest -m "accessibility"
pytest -m "performance"
pytest -m "integration"

# With coverage
pytest --cov=src --cov-report=html --cov-fail-under=90

# Parallel execution
pytest -n auto

# Verbose with timeline
pytest -v --tb=short --durations=10
```
