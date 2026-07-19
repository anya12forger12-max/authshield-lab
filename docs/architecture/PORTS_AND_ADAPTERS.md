# Ports and Adapters Architecture

## Overview

AuthShield Lab uses the Hexagonal (Ports and Adapters) pattern. The application
core defines **ports** — interfaces that describe what it needs. **Adapters**
are concrete implementations that connect the core to external systems. The core
never knows which adapters are in use.

```
                    ┌──────────────────────┐
    REST API ──────►│  Input Adapter        │
                    │                       │
    CLI ───────────►│  ┌────────────────┐  │
                    │  │  Application   │  │
    Electron ──────►│  │     Core       │  │
                    │  │  (Use Cases)   │  │
    React ─────────►│  └────────────────┘  │
                    │                       │
                    │  Output Adapter ◄─────│──── Database
                    │                       │──── File System
                    │  Output Adapter ◄─────│──── Email
                    └──────────────────────┘
```

---

## Input Ports (Use Case Interfaces)

Input ports define the operations that can be performed on the application.
They are implemented by use cases and consumed by adapters.

### AuthenticationInputPort

```python
from typing import Protocol
from uuid import UUID


class AuthenticationInputPort(Protocol):
    async def authenticate(
        self, email: str, password: str, mfa_code: str | None = None
    ) -> AuthenticationResult: ...

    async def refresh_token(self, refresh_token: str) -> TokenPair: ...

    async def revoke_session(
        self, user_id: UUID, session_id: UUID | None = None
    ) -> RevocationResult: ...

    async def verify_token(self, token: str) -> TokenClaims: ...

    async def enable_mfa(self, user_id: UUID) -> MFASetupResult: ...

    async def verify_mfa(self, user_id: UUID, code: str) -> bool: ...
```

**Responsibilities:** Authenticate users, manage tokens, handle MFA, enforce session policies.

**Error Handling:**
- `AuthenticationFailed` — Invalid credentials
- `AccountLocked` — Too many failed attempts
- `TokenExpired` — Token past expiry
- `TokenRevoked` — Token explicitly revoked
- `MFARequired` — MFA setup needed

### AuthorizationInputPort

```python
class AuthorizationInputPort(Protocol):
    async def authorize(
        self, user_id: UUID, resource: str, action: str, context: dict | None = None
    ) -> AuthorizationResult: ...

    async def assign_role(
        self, user_id: UUID, role_name: str, scope: str | None = None
    ) -> RoleAssignment: ...

    async def revoke_role(
        self, user_id: UUID, role_name: str, scope: str | None = None
    ) -> None: ...

    async def grant_permission(
        self, grantee_id: UUID, permission: str, scope: str | None = None
    ) -> PermissionGrant: ...

    async def revoke_permission(
        self, grantee_id: UUID, permission: str, scope: str | None = None
    ) -> None: ...

    async def list_roles(self, user_id: UUID) -> list[Role]: ...

    async def list_permissions(self, user_id: UUID) -> list[Permission]: ...
```

**Responsibilities:** Evaluate access policies, manage roles and permissions, enforce RBAC.

**Error Handling:**
- `AuthorizationDenied` — Insufficient permissions
- `RoleNotFound` — Invalid role name
- `InsufficientPrivileges` — Assigner lacks authority
- `RoleLimitExceeded` — Maximum roles per user exceeded

### CourseManagementInputPort

```python
class CourseManagementInputPort(Protocol):
    async def create_course(
        self, creator_id: UUID, data: CreateCourseData
    ) -> CourseCreated: ...

    async def publish_course(self, course_id: UUID, actor_id: UUID) -> CoursePublished: ...

    async def archive_course(
        self, course_id: UUID, actor_id: UUID, reason: str | None = None
    ) -> CourseArchived: ...

    async def enroll_student(
        self, course_id: UUID, student_id: UUID
    ) -> EnrollmentCreated: ...

    async def unenroll_student(
        self, course_id: UUID, student_id: UUID
    ) -> EnrollmentRemoved: ...

    async def get_course(self, course_id: UUID) -> CourseDetail: ...

    async def list_courses(
        self, filters: CourseFilters, page: int, page_size: int
    ) -> PaginatedCourses: ...

    async def update_course(
        self, course_id: UUID, actor_id: UUID, data: UpdateCourseData
    ) -> CourseUpdated: ...
```

**Responsibilities:** Full course lifecycle management, enrollment, catalog operations.

**Error Handling:**
- `CourseNotFound`, `DuplicateCourseSlug`, `CourseNotReady`
- `AlreadyEnrolled`, `CourseFull`, `PrerequisitesNotMet`

### AssessmentInputPort

```python
class AssessmentInputPort(Protocol):
    async def create_assessment(
        self, course_id: UUID, data: CreateAssessmentData
    ) -> AssessmentCreated: ...

    async def start_assessment(
        self, assessment_id: UUID, student_id: UUID
    ) -> AssessmentSession: ...

    async def submit_assessment(
        self, attempt_id: UUID, answers: list[AnswerData]
    ) -> SubmissionResult: ...

    async def grade_assessment(
        self, attempt_id: UUID, grades: list[GradeData], feedback: str | None = None
    ) -> GradeResult: ...

    async def get_assessment_results(
        self, assessment_id: UUID, student_id: UUID
    ) -> list[AttemptResult]: ...
```

**Responsibilities:** Assessment lifecycle, grading, attempt management.

**Error Handling:**
- `MaxAttemptsReached`, `AttemptExpired`, `AlreadyGraded`

### PluginManagementInputPort

```python
class PluginManagementInputPort(Protocol):
    async def install_plugin(self, plugin_id: str, version: str | None = None) -> PluginInstalled: ...

    async def update_plugin(self, plugin_id: str, version: str | None = None) -> PluginUpdated: ...

    async def remove_plugin(self, plugin_id: str) -> PluginRemoved: ...

    async def list_plugins(self) -> list[PluginInfo]: ...

    async def get_plugin(self, plugin_id: str) -> PluginDetail: ...

    async def configure_plugin(self, plugin_id: str, config: dict) -> PluginConfigured: ...

    async def enable_plugin(self, plugin_id: str) -> PluginEnabled: ...

    async def disable_plugin(self, plugin_id: str) -> PluginDisabled: ...
```

**Responsibilities:** Plugin lifecycle management, configuration, activation.

### BackupInputPort

```python
class BackupInputPort(Protocol):
    async def create_backup(
        self, backup_type: str = "full", include_plugins: bool = True
    ) -> BackupCreated: ...

    async def restore_backup(self, backup_id: UUID) -> BackupRestored: ...

    async def verify_backup(self, backup_id: UUID) -> BackupVerification: ...

    async def list_backups(self, filters: BackupFilters | None = None) -> list[BackupMetadata]: ...

    async def delete_backup(self, backup_id: UUID) -> BackupDeleted: ...
```

**Responsibilities:** Backup creation, restoration, verification, lifecycle.

### ReportingInputPort

```python
class ReportingInputPort(Protocol):
    async def generate_report(
        self, report_type: str, filters: ReportFilters, format: str = "json"
    ) -> ReportGenerated: ...

    async def export_data(
        self, data_type: str, filters: ExportFilters, format: str = "csv"
    ) -> ExportCreated: ...

    async def import_data(
        self, data_type: str, file_data: bytes, mapping: dict, conflict_strategy: str
    ) -> ImportResult: ...

    async def get_report(self, report_id: UUID) -> ReportData: ...
```

**Responsibilities:** Report generation, data export/import, analytics.

### AnalyticsInputPort

```python
class AnalyticsInputPort(Protocol):
    async def track_event(self, event: AnalyticsEvent) -> None: ...

    async def get_course_analytics(self, course_id: UUID) -> CourseAnalytics: ...

    async def get_student_analytics(self, student_id: UUID) -> StudentAnalytics: ...

    async def get_platform_analytics(self, period: str) -> PlatformAnalytics: ...

    async def get_real_time_metrics(self) -> RealTimeMetrics: ...
```

**Responsibilities:** Event tracking, metric aggregation, analytics retrieval.

---

## Output Ports (Gateway Interfaces)

Output ports define services the application core needs from the outside world.
They are implemented by adapters and consumed by use cases.

### UserRepositoryPort

```python
class UserRepositoryPort(Protocol):
    async def find_by_id(self, user_id: UUID) -> User | None: ...

    async def find_by_email(self, email: str) -> User | None: ...

    async def save(self, user: User) -> None: ...

    async def delete(self, user_id: UUID) -> None: ...

    async def exists(self, email: str) -> bool: ...

    async def list_users(
        self, filters: UserFilters, page: int, page_size: int
    ) -> tuple[list[User], int]: ...

    async def count(self) -> int: ...
```

### CourseRepositoryPort

```python
class CourseRepositoryPort(Protocol):
    async def find_by_id(self, course_id: UUID) -> Course | None: ...

    async def find_by_slug(self, slug: str) -> Course | None: ...

    async def save(self, course: Course) -> None: ...

    async def delete(self, course_id: UUID) -> None: ...

    async def list_published(
        self, page: int, page_size: int
    ) -> tuple[list[Course], int]: ...

    async def list_by_instructor(
        self, instructor_id: UUID
    ) -> list[Course]: ...

    async def count_enrolled(self, course_id: UUID) -> int: ...
```

### AssessmentRepositoryPort

```python
class AssessmentRepositoryPort(Protocol):
    async def find_by_id(self, assessment_id: UUID) -> Assessment | None: ...

    async def save(self, assessment: Assessment) -> None: ...

    async def list_by_course(self, course_id: UUID) -> list[Assessment]: ...

    async def find_attempt(self, attempt_id: UUID) -> AssessmentAttempt | None: ...

    async def save_attempt(self, attempt: AssessmentAttempt) -> None: ...

    async def count_attempts(
        self, assessment_id: UUID, student_id: UUID
    ) -> int: ...
```

### NotificationPort

```python
class NotificationPort(Protocol):
    async def send_email(
        self, to: str, subject: str, body: str, html: bool = False
    ) -> None: ...

    async def send_push(
        self, user_id: UUID, title: str, body: str, data: dict | None = None
    ) -> None: ...

    async def send_in_app(
        self, user_id: UUID, notification: InAppNotification
    ) -> None: ...

    async def broadcast(
        self, user_ids: list[UUID], title: str, body: str
    ) -> None: ...
```

### LoggingPort

```python
class LoggingPort(Protocol):
    def info(self, message: str, **context: object) -> None: ...

    def warning(self, message: str, **context: object) -> None: ...

    def error(self, message: str, exc: Exception | None = None, **context: object) -> None: ...

    def debug(self, message: str, **context: object) -> None: ...

    def audit(self, actor: str, action: str, resource: str, outcome: str) -> None: ...
```

### ConfigurationPort

```python
class ConfigurationPort(Protocol):
    async def get(self, key: str, default: str | None = None) -> str | None: ...

    async def get_int(self, key: str, default: int = 0) -> int: ...

    async def get_bool(self, key: str, default: bool = False) -> bool: ...

    async def set(self, key: str, value: str) -> None: ...

    async def delete(self, key: str) -> None: ...

    async def list_all(self) -> dict[str, str]: ...

    async def export(self) -> dict[str, str]: ...

    async def import_config(self, config: dict[str, str]) -> None: ...
```

### PluginStoragePort

```python
class PluginStoragePort(Protocol):
    async def store(self, plugin_id: str, version: str, data: bytes) -> Path: ...

    async def load(self, plugin_id: str, version: str) -> bytes: ...

    async def delete(self, plugin_id: str, version: str) -> None: ...

    async def list_versions(self, plugin_id: str) -> list[str]: ...

    async def get_manifest(self, plugin_id: str) -> PluginManifest: ...

    async def store_config(self, plugin_id: str, config: dict) -> None: ...

    async def load_config(self, plugin_id: str) -> dict: ...
```

### BackupStoragePort

```python
class BackupStoragePort(Protocol):
    async def store(self, backup_id: UUID, data: bytes, metadata: BackupMetadata) -> Path: ...

    async def retrieve(self, backup_id: UUID) -> bytes: ...

    async def delete(self, backup_id: UUID) -> None: ...

    async def exists(self, backup_id: UUID) -> bool: ...

    async def get_metadata(self, backup_id: UUID) -> BackupMetadata: ...

    async def list_all(self) -> list[BackupMetadata]: ...

    async def get_total_size(self) -> int: ...
```

### EventPublishingPort

```python
class EventPublishingPort(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...

    async def publish_many(self, events: list[DomainEvent]) -> None: ...

    def subscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> SubscriptionHandle: ...

    def unsubscribe(self, handle: SubscriptionHandle) -> None: ...
```

---

## Adapters

### REST API Adapters (FastAPI Routers)

**Responsibilities:**
- Parse HTTP requests into use case input DTOs
- Validate request bodies using Pydantic schemas
- Map use case outputs to HTTP responses
- Handle HTTP-specific concerns (status codes, headers, CORS)
- Rate limiting and request throttling

**Public Contract:**
```python
# router.py
from fastapi import APIRouter, Depends, Query, Path

router = APIRouter(prefix="/api/v1/courses", tags=["courses"])


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: UUID = Path(...),
    use_case: CourseManagementInputPort = Depends(get_course_use_case),
) -> CourseResponse:
    ...

@router.post("/", response_model=CourseResponse, status_code=201)
async def create_course(
    request: CreateCourseRequest,
    use_case: CourseManagementInputPort = Depends(get_course_use_case),
) -> CourseResponse:
    ...

@router.get("/", response_model=PaginatedCoursesResponse)
async def list_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    use_case: CourseManagementInputPort = Depends(get_course_use_case),
) -> PaginatedCoursesResponse:
    ...
```

**Error Handling:** Domain exceptions mapped to HTTP status codes via exception handlers. All errors returned as RFC 7807 Problem Details.

**Dependency Rules:** Router depends only on input ports. Never depends on repositories, domain entities, or infrastructure.

### Database Adapters (SQLAlchemy Repositories)

**Responsibilities:**
- Implement repository port interfaces
- Map between domain entities and SQLAlchemy models
- Manage database sessions
- Handle query optimization
- Enforce database-level constraints

**Public Contract:**
```python
# sqlalchemy_user_repository.py
class SQLAlchemyUserRepository:
    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory

    async def find_by_id(self, user_id: UUID) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            model = result.scalar_one_or_none()
            return UserMapper.to_domain(model) if model else None

    async def save(self, user: User) -> None:
        async with self._session_factory() as session:
            model = UserMapper.to_model(user)
            session.add(model)
            await session.commit()
```

**Error Handling:** Database-specific exceptions (IntegrityError, OperationalError) translated to domain exceptions.

**Dependency Rules:** Adapter depends on domain entities and repository ports. Never depends on use cases.

### File System Adapters

**Responsibilities:**
- Implement backup storage ports
- Handle file I/O with proper error handling
- Manage disk space and cleanup
- Provide file integrity verification

**Public Contract:**
```python
class LocalBackupStorage:
    def __init__(self, base_path: Path, max_backups: int = 30) -> None:
        self._base_path = base_path
        self._max_backups = max_backups

    async def store(self, backup_id: UUID, data: bytes, metadata: BackupMetadata) -> Path:
        ...

    async def retrieve(self, backup_id: UUID) -> bytes:
        ...

    async def list_all(self) -> list[BackupMetadata]:
        ...
```

**Error Handling:** `FileSystemError` for I/O failures, `InsufficientStorage` for disk space issues.

### UI Adapters (React Components + Zustand Stores)

**Responsibilities:**
- Render application state as UI components
- Capture user interactions and translate to API calls
- Manage client-side state with Zustand
- Handle routing and navigation
- Accessibility compliance (WCAG 2.1 AA)

**Public Contract:**
```typescript
// stores/courseStore.ts
interface CourseStore {
  courses: Course[];
  currentCourse: Course | null;
  loading: boolean;
  error: string | null;

  fetchCourses: (page: number, pageSize: number) => Promise<void>;
  fetchCourse: (id: string) => Promise<void>;
  createCourse: (data: CreateCourseData) => Promise<Course>;
  publishCourse: (id: string) => Promise<void>;
}
```

**Error Handling:** API errors caught and displayed via toast notifications. Network errors trigger retry logic.

### Event Adapters (In-Memory Event Bus)

**Responsibilities:**
- Implement event publishing port
- Route events to registered handlers
- Support synchronous and asynchronous handlers
- Provide dead letter queue for failed events

**Public Contract:**
```python
class InMemoryEventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler]] = defaultdict(list)
        self._dead_letters: list[DeadLetter] = []

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as exc:
                self._dead_letters.append(DeadLetter(event=event, error=exc))

    def subscribe(self, event_type: type, handler: EventHandler) -> SubscriptionHandle:
        self._handlers[event_type].append(handler)
        return SubscriptionHandle(...)
```

### Plugin Adapters

**Responsibilities:**
- Discover and load plugins from disk
- Parse and validate plugin manifests
- Execute plugin code in sandboxed environments
- Manage plugin lifecycle (install, update, remove)

**Public Contract:**
```python
class PluginLoader:
    def __init__(self, storage: PluginStoragePort, sandbox: PluginSandbox) -> None:
        self._storage = storage
        self._sandbox = sandbox

    async def discover(self) -> list[PluginManifest]:
        ...

    async def load(self, plugin_id: str) -> LoadedPlugin:
        ...

    async def unload(self, plugin_id: str) -> None:
        ...

    async def execute_hook(self, plugin_id: str, hook: str, context: dict) -> Any:
        ...
```

---

## Adapter Dependency Rules

| Adapter Type | May Depend On | Must Not Depend On |
|---|---|---|
| REST API Router | Input Ports, Pydantic Schemas | Repositories, Domain Entities |
| SQLAlchemy Repository | Domain Entities, Repository Ports | Use Cases, Routers |
| File System Adapter | Domain Entities, Storage Ports | Use Cases, API |
| React Component | API Client, Zustand Stores | Backend Code |
| Event Bus | Domain Events, Handler Interfaces | Repositories, Adapters |
| Plugin Loader | Plugin Ports, Manifest Schema | Domain Entities |

---

## Wiring Adapters to Ports

```python
# infrastructure/di/container.py
def build_container(config: AppConfig) -> Container:
    container = Container()

    # Infrastructure
    engine = create_async_engine(config.database_url)
    session_factory = async_sessionmaker(engine)

    # Output Adapters
    container.register(UserRepositoryPort, SQLAlchemyUserRepository(session_factory))
    container.register(CourseRepositoryPort, SQLAlchemyCourseRepository(session_factory))
    container.register(NotificationPort, EmailNotificationService(config.smtp))
    container.register(LoggingPort, StructuredLogger(config.log_level))
    container.register(ConfigurationPort, SQLiteConfigurationRepository(session_factory))
    container.register(EventPublishingPort, InMemoryEventBus())
    container.register(BackupStoragePort, LocalBackupStorage(config.backup_path))
    container.register(PluginStoragePort, LocalPluginStorage(config.plugin_path))

    # Input Ports (Use Cases)
    container.register(AuthenticationInputPort, AuthenticateUserUseCase(
        user_repository=container.get(UserRepositoryPort),
        authentication_service=container.get(AuthenticationService),
        event_publisher=container.get(EventPublishingPort),
    ))

    return container
```
