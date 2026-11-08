# Command-Query Model (CQRS-Lite)

## Overview

AuthShield Lab uses a lightweight CQRS (Command Query Responsibility Segregation)
approach. Commands and queries are separated at the use case level without
duplicating data stores. Commands mutate state and emit events. Queries read
state with filtering, pagination, and projections. Both share the same database
but are accessed through distinct interfaces.

```
         Commands                           Queries
    ┌─────────────────┐              ┌─────────────────┐
    │  CreateUser     │              │  GetUser         │
    │  UpdateUser     │              │  ListCourses     │
    │  DeleteUser     │              │  GetAssessments  │
    │  CreateCourse   │              │  GetCertificates │
    │  PublishCourse  │              │  GetReports      │
    │  EnrollStudent  │              │  GetPlugins      │
    │  StartAssessment│              │  GetAuditLogs    │
    │  SubmitAssessment│             │  GetConfiguration│
    │  InstallPlugin  │              │  GetDiagnostics  │
    │  CreateBackup   │              │                  │
    └────────┬────────┘              └────────┬────────┘
             │                                │
             ▼                                ▼
    ┌─────────────────┐              ┌─────────────────┐
    │ Command Handler  │              │  Query Handler   │
    │ (validates,      │              │  (filters,       │
    │  executes,       │              │   paginates,     │
    │  emits events)   │              │   projects)      │
    └─────────────────┘              └─────────────────┘
```

---

## Commands

Commands represent intent to change state. Every command is a request from an
authenticated actor to perform a single, atomic state transition.

### Command Design Principles

1. Every command is an immutable data class
2. Every command carries actor identity for authorization
3. Every command is validated before handler execution
4. Every command produces zero or more domain events
5. Commands are named in past tense when representing what happened,
   or imperative when representing intent

### User Commands

```python
from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime


@dataclass(frozen=True)
class CreateUserCommand:
    actor_id: UUID
    email: str
    display_name: str
    password: str
    roles: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class UpdateUserCommand:
    actor_id: UUID
    target_user_id: UUID
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None


@dataclass(frozen=True)
class DeleteUserCommand:
    actor_id: UUID
    target_user_id: UUID
    reason: str = ""


@dataclass(frozen=True)
class DeactivateUserCommand:
    actor_id: UUID
    target_user_id: UUID
    reason: str = ""


@dataclass(frozen=True)
class UpdatePreferencesCommand:
    actor_id: UUID
    theme: str | None = None
    font_size: str | None = None
    language: str | None = None
    reduced_motion: bool | None = None
    screen_reader_optimized: bool | None = None
```

### Authentication Commands

```python
@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str
    mfa_code: str | None = None
    ip_address: str = ""
    user_agent: str = ""


@dataclass(frozen=True)
class RefreshTokenCommand:
    refresh_token: str
    ip_address: str = ""


@dataclass(frozen=True)
class RevokeSessionCommand:
    actor_id: UUID
    session_id: UUID | None = None  # None = revoke all
    reason: str = ""


@dataclass(frozen=True)
class EnableMFACommand:
    actor_id: UUID


@dataclass(frozen=True)
class VerifyMFACommand:
    actor_id: UUID
    code: str
```

### Authorization Commands

```python
@dataclass(frozen=True)
class AssignRoleCommand:
    actor_id: UUID
    target_user_id: UUID
    role_name: str
    scope: str | None = None


@dataclass(frozen=True)
class RevokeRoleCommand:
    actor_id: UUID
    target_user_id: UUID
    role_name: str
    scope: str | None = None


@dataclass(frozen=True)
class GrantPermissionCommand:
    actor_id: UUID
    grantee_id: UUID
    permission: str
    scope: str | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True)
class RevokePermissionCommand:
    actor_id: UUID
    grantee_id: UUID
    permission: str
    scope: str | None = None
```

### Course Commands

```python
@dataclass(frozen=True)
class CreateCourseCommand:
    actor_id: UUID
    title: str
    description: str
    modules: list[CreateModuleData] = field(default_factory=list)
    settings: CourseSettings | None = None


@dataclass(frozen=True)
class UpdateCourseCommand:
    actor_id: UUID
    course_id: UUID
    title: str | None = None
    description: str | None = None
    settings: CourseSettings | None = None


@dataclass(frozen=True)
class PublishCourseCommand:
    actor_id: UUID
    course_id: UUID


@dataclass(frozen=True)
class ArchiveCourseCommand:
    actor_id: UUID
    course_id: UUID
    reason: str = ""


@dataclass(frozen=True)
class EnrollStudentCommand:
    actor_id: UUID
    course_id: UUID
    student_id: UUID


@dataclass(frozen=True)
class UnenrollStudentCommand:
    actor_id: UUID
    course_id: UUID
    student_id: UUID
```

### Assessment Commands

```python
@dataclass(frozen=True)
class CreateAssessmentCommand:
    actor_id: UUID
    course_id: UUID
    title: str
    questions: list[QuestionData]
    settings: AssessmentSettings


@dataclass(frozen=True)
class StartAssessmentCommand:
    actor_id: UUID
    assessment_id: UUID
    student_id: UUID


@dataclass(frozen=True)
class SubmitAssessmentCommand:
    actor_id: UUID
    attempt_id: UUID
    answers: list[AnswerData]


@dataclass(frozen=True)
class GradeAssessmentCommand:
    actor_id: UUID
    attempt_id: UUID
    grades: list[QuestionGradeData]
    feedback: str | None = None
```

### Plugin Commands

```python
@dataclass(frozen=True)
class InstallPluginCommand:
    actor_id: UUID
    plugin_id: str
    version: str | None = None


@dataclass(frozen=True)
class UpdatePluginCommand:
    actor_id: UUID
    plugin_id: str
    target_version: str | None = None


@dataclass(frozen=True)
class RemovePluginCommand:
    actor_id: UUID
    plugin_id: str


@dataclass(frozen=True)
class ConfigurePluginCommand:
    actor_id: UUID
    plugin_id: str
    configuration: dict


@dataclass(frozen=True)
class EnablePluginCommand:
    actor_id: UUID
    plugin_id: str


@dataclass(frozen=True)
class DisablePluginCommand:
    actor_id: UUID
    plugin_id: str
```

### Backup Commands

```python
@dataclass(frozen=True)
class CreateBackupCommand:
    actor_id: UUID
    backup_type: str = "full"  # "full" or "incremental"
    include_plugins: bool = True
    description: str = ""


@dataclass(frozen=True)
class RestoreBackupCommand:
    actor_id: UUID
    backup_id: UUID
    confirm: bool = False


@dataclass(frozen=True)
class DeleteBackupCommand:
    actor_id: UUID
    backup_id: UUID
```

### Configuration Commands

```python
@dataclass(frozen=True)
class UpdateSettingCommand:
    actor_id: UUID
    key: str
    value: Any


@dataclass(frozen=True)
class UpdateSettingsCommand:
    actor_id: UUID
    settings: dict[str, Any]


@dataclass(frozen=True)
class ResetSettingsCommand:
    actor_id: UUID
    keys: list[str] | None = None  # None = reset all
```

### Simulation Commands

```python
@dataclass(frozen=True)
class StartSimulationCommand:
    actor_id: UUID
    scenario_id: UUID
    student_id: UUID


@dataclass(frozen=True)
class ExecuteSimulationActionCommand:
    actor_id: UUID
    simulation_id: UUID
    action_type: str
    action_params: dict


@dataclass(frozen=True)
class CompleteSimulationCommand:
    actor_id: UUID
    simulation_id: UUID
```

---

## Queries

Queries represent intent to read state. Every query is a request for data
without side effects.

### Query Design Principles

1. Every query is an immutable data class
2. Queries never modify state
3. Queries support filtering, sorting, and pagination
4. Queries return projections (not domain entities directly)
5. Queries can be cached

### User Queries

```python
@dataclass(frozen=True)
class GetUserQuery:
    requester_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class GetUserByEmailQuery:
    requester_id: UUID
    email: str


@dataclass(frozen=True)
class ListUsersQuery:
    requester_id: UUID
    page: int = 1
    page_size: int = 20
    search: str | None = None
    is_active: bool | None = None
    role: str | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


@dataclass(frozen=True)
class GetUserPreferencesQuery:
    requester_id: UUID
    user_id: UUID
```

### Course Queries

```python
@dataclass(frozen=True)
class GetCourseQuery:
    requester_id: UUID
    course_id: UUID


@dataclass(frozen=True)
class ListCoursesQuery:
    requester_id: UUID
    page: int = 1
    page_size: int = 20
    status: str | None = None  # "draft", "published", "archived"
    instructor_id: UUID | None = None
    search: str | None = None
    category: str | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


@dataclass(frozen=True)
class ListEnrolledCoursesQuery:
    requester_id: UUID
    student_id: UUID
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class GetCourseModulesQuery:
    requester_id: UUID
    course_id: UUID


@dataclass(frozen=True)
class GetCourseEnrollmentsQuery:
    requester_id: UUID
    course_id: UUID
    page: int = 1
    page_size: int = 20
```

### Assessment Queries

```python
@dataclass(frozen=True)
class GetAssessmentQuery:
    requester_id: UUID
    assessment_id: UUID


@dataclass(frozen=True)
class ListAssessmentsQuery:
    requester_id: UUID
    course_id: UUID
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class GetAssessmentAttemptQuery:
    requester_id: UUID
    attempt_id: UUID


@dataclass(frozen=True)
class ListStudentAttemptsQuery:
    requester_id: UUID
    student_id: UUID
    assessment_id: UUID | None = None
    page: int = 1
    page_size: int = 20
```

### Certificate Queries

```python
@dataclass(frozen=True)
class GetCertificateQuery:
    requester_id: UUID | None  # None for public verification
    certificate_id: UUID


@dataclass(frozen=True)
class VerifyCertificateQuery:
    certificate_code: str


@dataclass(frozen=True)
class ListCertificatesQuery:
    requester_id: UUID
    student_id: UUID | None = None
    course_id: UUID | None = None
    page: int = 1
    page_size: int = 20
```

### Report Queries

```python
@dataclass(frozen=True)
class GetReportQuery:
    requester_id: UUID
    report_id: UUID


@dataclass(frozen=True)
class ListReportsQuery:
    requester_id: UUID
    report_type: str | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class GetCourseAnalyticsQuery:
    requester_id: UUID
    course_id: UUID
    period: str = "30d"


@dataclass(frozen=True)
class GetStudentAnalyticsQuery:
    requester_id: UUID
    student_id: UUID
    period: str = "30d"
```

### Plugin Queries

```python
@dataclass(frozen=True)
class ListPluginsQuery:
    requester_id: UUID
    installed_only: bool = False
    enabled_only: bool = False


@dataclass(frozen=True)
class GetPluginQuery:
    requester_id: UUID
    plugin_id: str


@dataclass(frozen=True)
class GetPluginConfigurationQuery:
    requester_id: UUID
    plugin_id: str
```

### Configuration Queries

```python
@dataclass(frozen=True)
class GetSettingQuery:
    requester_id: UUID
    key: str


@dataclass(frozen=True)
class ListSettingsQuery:
    requester_id: UUID
    prefix: str | None = None
    category: str | None = None


@dataclass(frozen=True)
class ExportConfigurationQuery:
    requester_id: UUID
    include_secrets: bool = False
```

### Backup Queries

```python
@dataclass(frozen=True)
class ListBackupsQuery:
    requester_id: UUID
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class GetBackupQuery:
    requester_id: UUID
    backup_id: UUID
```

### Audit Queries

```python
@dataclass(frozen=True)
class GetAuditLogQuery:
    requester_id: UUID
    entry_id: UUID


@dataclass(frozen=True)
class ListAuditLogsQuery:
    requester_id: UUID
    actor_id: UUID | None = None
    action: str | None = None
    resource_type: str | None = None
    resource_id: UUID | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    outcome: str | None = None
    page: int = 1
    page_size: int = 50
    sort_by: str = "timestamp"
    sort_order: str = "desc"
```

### Diagnostics Queries

```python
@dataclass(frozen=True)
class GetSystemInfoQuery:
    requester_id: UUID


@dataclass(frozen=True)
class RunDiagnosticsQuery:
    requester_id: UUID
    checks: list[str] | None = None  # None = all


@dataclass(frozen=True)
class GetDiagnosticsHistoryQuery:
    requester_id: UUID
    limit: int = 10
```

### Simulation Queries

```python
@dataclass(frozen=True)
class GetSimulationQuery:
    requester_id: UUID
    simulation_id: UUID


@dataclass(frozen=True)
class ListSimulationsQuery:
    requester_id: UUID
    student_id: UUID | None = None
    scenario_id: UUID | None = None
    page: int = 1
    page_size: int = 20
```

---

## Command Handlers

Command handlers are the execution units for commands. They validate input,
orchestrate domain objects, persist state, and emit events.

### Handler Pattern

```python
class CreateUserHandler:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        auth_service: AuthenticationPort,
        event_publisher: EventPublishingPort,
        notification_port: NotificationPort,
        logging_port: LoggingPort,
    ) -> None:
        self._user_repo = user_repo
        self._auth_service = auth_service
        self._event_publisher = event_publisher
        self._notification = notification_port
        self._logger = logging_port

    async def handle(self, command: CreateUserCommand) -> CreateUserResult:
        # 1. Authorization
        if not await self._auth_service.is_admin(command.actor_id):
            raise AuthorizationDenied("Only admins can create users")

        # 2. Validation
        if await self._user_repo.exists(command.email):
            raise ValidationFailed("Email already registered")

        # 3. Execute
        user = User(
            email=command.email,
            display_name=command.display_name,
        )
        hashed_password = await self._auth_service.hash_password(command.password)

        await self._user_repo.save(user)
        await self._auth_service.store_credentials(user.id, hashed_password)

        # 4. Emit Events
        event = UserCreated(user_id=user.id, email=user.email)
        await self._event_publisher.publish(event)

        # 5. Log
        self._logger.info(
            "User created",
            actor=command.actor_id,
            target=user.id,
            email=user.email,
        )

        # 6. Notify
        await self._notification.send_email(
            to=user.email,
            subject="Welcome to AuthShield Lab",
            body=f"Welcome, {user.display_name}!",
        )

        return CreateUserResult(user_id=user.id, created_at=user.created_at)
```

### Validation in Handlers

```python
class UpdateCourseHandler:
    async def handle(self, command: UpdateCourseCommand) -> UpdateCourseResult:
        course = await self._course_repo.find_by_id(command.course_id)
        if course is None:
            raise EntityNotFound("Course", command.course_id)

        # Authorization: only instructors assigned to the course can update
        if not await self._auth_service.has_course_role(
            command.actor_id, command.course_id, "instructor"
        ):
            raise AuthorizationDenied("Not an instructor for this course")

        # Validation
        if command.title is not None:
            if len(command.title) < 3 or len(command.title) > 200:
                raise ValidationFailed("Title must be 3-200 characters")

        if command.description is not None:
            if len(command.description) < 10:
                raise ValidationFailed("Description must be at least 10 characters")

        # Execute
        if command.title is not None:
            course.update_title(command.title)
        if command.description is not None:
            course.update_description(command.description)
        if command.settings is not None:
            course.update_settings(command.settings)

        await self._course_repo.save(course)

        event = CourseUpdated(
            course_id=course.id,
            updated_by=command.actor_id,
        )
        await self._event_publisher.publish(event)

        return UpdateCourseResult(updated_at=course.updated_at)
```

---

## Query Handlers

Query handlers retrieve and project data without side effects.

### Handler Pattern

```python
class GetUserHandler:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        auth_service: AuthorizationPort,
    ) -> None:
        self._user_repo = user_repo
        self._auth = auth_service

    async def handle(self, query: GetUserQuery) -> UserResponse:
        # Authorization
        if query.requester_id != query.user_id:
            if not await self._auth.is_admin(query.requester_id):
                raise AuthorizationDenied("Cannot view other users' profiles")

        user = await self._user_repo.find_by_id(query.user_id)
        if user is None:
            raise EntityNotFound("User", query.user_id)

        return UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            is_active=user.is_active,
            created_at=user.created_at,
        )
```

### Pagination in Query Handlers

```python
class ListCoursesHandler:
    async def handle(self, query: ListCoursesQuery) -> PaginatedCoursesResponse:
        courses, total = await self._course_repo.list_with_filters(
            status=query.status,
            instructor_id=query.instructor_id,
            search=query.search,
            page=query.page,
            page_size=query.page_size,
            sort_by=query.sort_by,
            sort_order=query.sort_order,
        )

        return PaginatedCoursesResponse(
            items=[CourseSummary.from_domain(c) for c in courses],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=ceil(total / query.page_size),
        )
```

---

## Command/Query Separation Rules

1. **Commands mutate, queries read.** Never perform writes in a query handler.
2. **Commands emit events.** Every state change produces a domain event.
3. **Queries are idempotent.** Running the same query twice yields the same result.
4. **Commands are not idempotent by default.** Use idempotency keys for safe retries.
5. **Queries may be cached.** Commands invalidate caches.
6. **Commands validate eagerly.** Fail fast before any mutation.
7. **Queries validate authorization.** Deny access before returning data.

## Event Publishing from Command Handlers

Events are published after successful state persistence but within the same
logical transaction:

```python
class EnrollStudentHandler:
    async def handle(self, command: EnrollStudentCommand) -> EnrollmentResult:
        # ... validation and execution ...

        await self._course_repo.save(course)
        await self._enrollment_repo.save(enrollment)

        # Events published after persistence succeeds
        await self._event_publisher.publish(StudentEnrolled(
            course_id=command.course_id,
            student_id=command.student_id,
            enrolled_at=enrollment.created_at,
        ))

        return EnrollmentResult(enrollment_id=enrollment.id)
```
