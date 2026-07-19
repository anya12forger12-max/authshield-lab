# AuthShield Lab - Repository Interfaces

## Overview

This document defines all repository interfaces in AuthShield Lab, specifying methods, query specifications, pagination, filtering, versioning, and caching policies for each repository.

---

## Repository Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Repository Architecture                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Application Layer                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │   │
│  │  │  Use Case   │  │  Use Case   │  │  Use Case   │               │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │   │
│  └─────────┼────────────────┼────────────────┼───────────────────────┘   │
│            │                │                │                              │
│            ▼                ▼                ▼                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                 Repository Interfaces                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │   │
│  │  │   IUser     │  │  ICourse    │  │ IAssessment │               │   │
│  │  │ Repository  │  │ Repository  │  │ Repository  │               │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │   │
│  └─────────┼────────────────┼────────────────┼───────────────────────┘   │
│            │                │                │                              │
│            ▼                ▼                ▼                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                Repository Implementations                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │   │
│  │  │   Postgres  │  │   Redis     │  │  MongoDB    │               │   │
│  │  │  Repository │  │  Repository │  │ Repository  │               │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Common Repository Patterns

### Pagination
```python
class PaginationParams:
    page: int = 1
    pageSize: int = 20
    maxPageSize: int = 100
    sortBy: str = None
    sortOrder: SortOrder = SortOrder.ASC

class PaginatedResult:
    items: List[T]
    totalCount: int
    page: int
    pageSize: int
    totalPages: int
    hasNext: bool
    hasPrevious: bool
```

### Filtering
```python
class Filter:
    field: str
    operator: FilterOperator
    value: Any

class FilterOperator(Enum):
    EQ = "eq"           # Equals
    NEQ = "neq"         # Not equals
    GT = "gt"           # Greater than
    GTE = "gte"         # Greater than or equal
    LT = "lt"           # Less than
    LTE = "lte"         # Less than or equal
    IN = "in"           # In list
    NIN = "nin"         # Not in list
    LIKE = "like"       # Pattern match
    CONTAINS = "contains"  # Contains
    BETWEEN = "between"    # Range
```

### Query Specification Pattern
```python
class Specification:
    def to_query(self) -> Query:
        pass
    
    def and_(self, other: 'Specification') -> 'Specification':
        return AndSpecification(self, other)
    
    def or_(self, other: 'Specification') -> 'Specification':
        return OrSpecification(self, other)
    
    def not_(self) -> 'Specification':
        return NotSpecification(self)
```

---

## Identity Repositories

### 1. UserRepository

**Purpose:** Manages persistence and retrieval of User aggregates.

**Interface:**
```python
class IUserRepository:
    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve user by ID."""
        pass
    
    def find_by_email(self, email: Email) -> Optional[User]:
        """Retrieve user by email address."""
        pass
    
    def find_by_username(self, username: Username) -> Optional[User]:
        """Retrieve user by username."""
        pass
    
    def find_active_users(self, pagination: PaginationParams) -> PaginatedResult[User]:
        """Retrieve paginated list of active users."""
        pass
    
    def find_by_status(self, status: UserStatus, pagination: PaginationParams) -> PaginatedResult[User]:
        """Retrieve users by status."""
        pass
    
    def find_by_organization(self, org_id: UUID, pagination: PaginationParams) -> PaginatedResult[User]:
        """Retrieve users in an organization."""
        pass
    
    def search(self, query: str, filters: List[Filter], pagination: PaginationParams) -> PaginatedResult[User]:
        """Search users with filters."""
        pass
    
    def save(self, user: User) -> User:
        """Save or update user."""
        pass
    
    def delete(self, user_id: UUID) -> bool:
        """Soft delete user."""
        pass
    
    def exists_by_email(self, email: Email) -> bool:
        """Check if email exists."""
        pass
    
    def exists_by_username(self, username: Username) -> bool:
        """Check if username exists."""
        pass
    
    def count(self, filters: List[Filter] = None) -> int:
        """Count users matching filters."""
        pass
```

**Query Specifications:**
| Specification | Description |
|---------------|-------------|
| UserByIdSpec | Find user by ID |
| UserByEmailSpec | Find user by email |
| UserByUsernameSpec | Find user by username |
| ActiveUsersSpec | Find active users |
| SuspendedUsersSpec | Find suspended users |
| UsersByOrganizationSpec | Find users in organization |
| UsersByRoleSpec | Find users with role |
| UsersCreatedAfterSpec | Find users created after date |

**Caching Policy:**
- Cache by ID: TTL 5 minutes
- Cache by email: TTL 5 minutes
- Invalidate on save/delete

---

### 2. RoleRepository

**Purpose:** Manages persistence and retrieval of Role aggregates.

**Interface:**
```python
class IRoleRepository:
    def find_by_id(self, role_id: UUID) -> Optional[Role]:
        """Retrieve role by ID."""
        pass
    
    def find_by_name(self, name: str) -> Optional[Role]:
        """Retrieve role by name."""
        pass
    
    def find_all(self) -> List[Role]:
        """Retrieve all roles."""
        pass
    
    def find_system_roles(self) -> List[Role]:
        """Retrieve system-defined roles."""
        pass
    
    def find_by_hierarchy_level(self, level: int) -> List[Role]:
        """Retrieve roles at hierarchy level."""
        pass
    
    def find_child_roles(self, parent_id: UUID) -> List[Role]:
        """Retrieve child roles of parent."""
        pass
    
    def save(self, role: Role) -> Role:
        """Save or update role."""
        pass
    
    def delete(self, role_id: UUID) -> bool:
        """Delete role (if not system)."""
        pass
    
    def exists_by_name(self, name: str) -> bool:
        """Check if role name exists."""
        pass
```

**Query Specifications:**
| Specification | Description |
|---------------|-------------|
| RoleByIdSpec | Find role by ID |
| RoleByNameSpec | Find role by name |
| SystemRolesSpec | Find system roles |
| RolesByHierarchySpec | Find roles by hierarchy level |
| ChildRolesSpec | Find child roles |

**Caching Policy:**
- Cache all roles: TTL 15 minutes
- Cache by ID: TTL 15 minutes
- Invalidate on save/delete

---

### 3. PermissionRepository

**Purpose:** Manages persistence and retrieval of Permission aggregates.

**Interface:**
```python
class IPermissionRepository:
    def find_by_id(self, permission_id: UUID) -> Optional[Permission]:
        """Retrieve permission by ID."""
        pass
    
    def find_by_resource(self, resource: str) -> List[Permission]:
        """Retrieve permissions for resource."""
        pass
    
    def find_by_role(self, role_id: UUID) -> List[Permission]:
        """Retrieve permissions for role."""
        pass
    
    def find_by_user(self, user_id: UUID) -> List[Permission]:
        """Retrieve all permissions for user."""
        pass
    
    def find_all(self) -> List[Permission]:
        """Retrieve all permissions."""
        pass
    
    def save(self, permission: Permission) -> Permission:
        """Save or update permission."""
        pass
    
    def delete(self, permission_id: UUID) -> bool:
        """Delete permission."""
        pass
    
    def exists_by_resource_action(self, resource: str, action: str) -> bool:
        """Check if permission exists for resource+action."""
        pass
```

**Query Specifications:**
| Specification | Description |
|---------------|-------------|
| PermissionByIdSpec | Find permission by ID |
| PermissionByResourceSpec | Find permissions by resource |
| PermissionByRoleSpec | Find permissions by role |
| PermissionByUserSpec | Find permissions by user |
| AllPermissionsSpec | Find all permissions |

**Caching Policy:**
- Cache by ID: TTL 30 minutes
- Cache by role: TTL 15 minutes
- Cache by user: TTL 5 minutes

---

## Session Repositories

### 4. SessionRepository

**Purpose:** Manages persistence and retrieval of Session aggregates.

**Interface:**
```python
class ISessionRepository:
    def find_by_id(self, session_id: UUID) -> Optional[Session]:
        """Retrieve session by ID."""
        pass
    
    def find_by_user(self, user_id: UUID, pagination: PaginationParams = None) -> List[Session]:
        """Retrieve sessions for user."""
        pass
    
    def find_active_sessions(self, user_id: UUID) -> List[Session]:
        """Retrieve active sessions for user."""
        pass
    
    def find_by_token_hash(self, token_hash: str) -> Optional[Session]:
        """Retrieve session by token hash."""
        pass
    
    def count_active_sessions(self, user_id: UUID) -> int:
        """Count active sessions for user."""
        pass
    
    def save(self, session: Session) -> Session:
        """Save or update session."""
        pass
    
    def delete(self, session_id: UUID) -> bool:
        """Delete session."""
        pass
    
    def delete_expired(self) -> int:
        """Delete all expired sessions."""
        pass
    
    def revoke_all_user_sessions(self, user_id: UUID, except_session_id: UUID = None) -> int:
        """Revoke all sessions for user except one."""
        pass
```

**Query Specifications:**
| Specification | Description |
|---------------|-------------|
| SessionByIdSpec | Find session by ID |
| SessionByUserSpec | Find sessions by user |
| ActiveSessionSpec | Find active sessions |
| SessionByTokenSpec | Find session by token hash |
| ExpiredSessionSpec | Find expired sessions |

**Caching Policy:**
- Cache by ID: TTL 1 minute
- Cache by token: TTL 1 minute
- Redis-backed for performance

---

### 5. TokenRepository

**Purpose:** Manages persistence and retrieval of SessionToken aggregates.

**Interface:**
```python
class ITokenRepository:
    def find_by_hash(self, token_hash: str) -> Optional[SessionToken]:
        """Retrieve token by hash."""
        pass
    
    def find_by_session(self, session_id: UUID) -> List[SessionToken]:
        """Retrieve tokens for session."""
        pass
    
    def find_active_tokens(self, session_id: UUID) -> List[SessionToken]:
        """Retrieve active tokens for session."""
        pass
    
    def save(self, token: SessionToken) -> SessionToken:
        """Save or update token."""
        pass
    
    def revoke(self, token_id: UUID) -> bool:
        """Revoke token."""
        pass
    
    def revoke_all_session_tokens(self, session_id: UUID) -> int:
        """Revoke all tokens for session."""
        pass
    
    def delete_expired(self) -> int:
        """Delete all expired tokens."""
        pass
```

**Caching Policy:**
- Cache by hash: TTL 1 minute
- Redis-backed for performance

---

## Education Repositories

### 6. CourseRepository

**Purpose:** Manages persistence and retrieval of Course aggregates.

**Interface:**
```python
class ICourseRepository:
    def find_by_id(self, course_id: UUID) -> Optional[Course]:
        """Retrieve course by ID."""
        pass
    
    def find_by_code(self, course_code: CourseCode) -> Optional[Course]:
        """Retrieve course by course code."""
        pass
    
    def find_published(self, pagination: PaginationParams) -> PaginatedResult[Course]:
        """Retrieve published courses."""
        pass
    
    def find_by_creator(self, creator_id: UUID, pagination: PaginationParams) -> PaginatedResult[Course]:
        """Retrieve courses by creator."""
        pass
    
    def find_by_status(self, status: CourseStatus, pagination: PaginationParams) -> PaginatedResult[Course]:
        """Retrieve courses by status."""
        pass
    
    def find_by_tag(self, tag: str, pagination: PaginationParams) -> PaginatedResult[Course]:
        """Retrieve courses by tag."""
        pass
    
    def search(self, query: str, filters: List[Filter], pagination: PaginationParams) -> PaginatedResult[Course]:
        """Search courses with filters."""
        pass
    
    def save(self, course: Course) -> Course:
        """Save or update course."""
        pass
    
    def delete(self, course_id: UUID) -> bool:
        """Delete course."""
        pass
    
    def count_by_status(self, status: CourseStatus) -> int:
        """Count courses by status."""
        pass
```

**Query Specifications:**
| Specification | Description |
|---------------|-------------|
| CourseByIdSpec | Find course by ID |
| CourseByCodeSpec | Find course by code |
| PublishedCourseSpec | Find published courses |
| CourseByCreatorSpec | Find courses by creator |
| CourseByStatusSpec | Find courses by status |
| CourseByTagSpec | Find courses by tag |
| SearchableCourseSpec | Full-text search |

**Caching Policy:**
- Cache by ID: TTL 5 minutes
- Cache by code: TTL 5 minutes
- Cache published list: TTL 2 minutes
- Invalidate on save/delete

---

### 7. ModuleRepository

**Purpose:** Manages persistence and retrieval of Module aggregates.

**Interface:**
```python
class IModuleRepository:
    def find_by_id(self, module_id: UUID) -> Optional[Module]:
        """Retrieve module by ID."""
        pass
    
    def find_by_course(self, course_id: UUID) -> List[Module]:
        """Retrieve modules for course (ordered)."""
        pass
    
    def find_with_lessons(self, module_id: UUID) -> Optional[Module]:
        """Retrieve module with lessons loaded."""
        pass
    
    def save(self, module: Module) -> Module:
        """Save or update module."""
        pass
    
    def delete(self, module_id: UUID) -> bool:
        """Delete module."""
        pass
    
    def reorder(self, course_id: UUID, module_ids: List[UUID]) -> bool:
        """Reorder modules in course."""
        pass
    
    def count_by_course(self, course_id: UUID) -> int:
        """Count modules in course."""
        pass
```

**Caching Policy:**
- Cache by ID: TTL 5 minutes
- Cache by course: TTL 2 minutes

---

### 8. LessonRepository

**Purpose:** Manages persistence and retrieval of Lesson aggregates.

**Interface:**
```python
class ILessonRepository:
    def find_by_id(self, lesson_id: UUID) -> Optional[Lesson]:
        """Retrieve lesson by ID."""
        pass
    
    def find_by_module(self, module_id: UUID) -> List[Lesson]:
        """Retrieve lessons for module (ordered)."""
        pass
    
    def find_by_course(self, course_id: UUID) -> List[Lesson]:
        """Retrieve all lessons in course."""
        pass
    
    def save(self, lesson: Lesson) -> Lesson:
        """Save or update lesson."""
        pass
    
    def delete(self, lesson_id: UUID) -> bool:
        """Delete lesson."""
        pass
    
    def reorder(self, module_id: UUID, lesson_ids: List[UUID]) -> bool:
        """Reorder lessons in module."""
        pass
    
    def count_by_module(self, module_id: UUID) -> int:
        """Count lessons in module."""
        pass
```

**Caching Policy:**
- Cache by ID: TTL 5 minutes
- Cache by module: TTL 2 minutes

---

## Learning Repositories

### 9. EnrollmentRepository

**Purpose:** Manages persistence and retrieval of Enrollment aggregates.

**Interface:**
```python
class IEnrollmentRepository:
    def find_by_id(self, enrollment_id: UUID) -> Optional[Enrollment]:
        """Retrieve enrollment by ID."""
        pass
    
    def find_by_user_course(self, user_id: UUID, course_id: UUID) -> Optional[Enrollment]:
        """Retrieve enrollment for user+course."""
        pass
    
    def find_active_by_user(self, user_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[Enrollment]:
        """Retrieve active enrollments for user."""
        pass
    
    def find_by_course(self, course_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[Enrollment]:
        """Retrieve enrollments for course."""
        pass
    
    def find_by_status(self, status: EnrollmentStatus, pagination: PaginationParams) -> PaginatedResult[Enrollment]:
        """Retrieve enrollments by status."""
        pass
    
    def count_by_course(self, course_id: UUID) -> int:
        """Count enrollments in course."""
        pass
    
    def count_by_user(self, user_id: UUID) -> int:
        """Count enrollments for user."""
        pass
    
    def save(self, enrollment: Enrollment) -> Enrollment:
        """Save or update enrollment."""
        pass
    
    def delete(self, enrollment_id: UUID) -> bool:
        """Delete enrollment."""
        pass
    
    def find_expiring(self, within_days: int) -> List[Enrollment]:
        """Find enrollments expiring within days."""
        pass
```

**Caching Policy:**
- Cache by ID: TTL 1 minute
- Cache by user+course: TTL 1 minute

---

### 10. ProgressRepository

**Purpose:** Manages persistence and retrieval of Progress entities.

**Interface:**
```python
class IProgressRepository:
    def find_by_enrollment(self, enrollment_id: UUID) -> List[Progress]:
        """Retrieve progress for enrollment."""
        pass
    
    def find_by_enrollment_lesson(self, enrollment_id: UUID, lesson_id: UUID) -> Optional[Progress]:
        """Retrieve progress for specific lesson."""
        pass
    
    def get_completion_percentage(self, enrollment_id: UUID) -> float:
        """Calculate completion percentage."""
        pass
    
    def get_completed_lessons(self, enrollment_id: UUID) -> List[UUID]:
        """Retrieve completed lesson IDs."""
        pass
    
    def save(self, progress: Progress) -> Progress:
        """Save or update progress."""
        pass
    
    def delete(self, progress_id: UUID) -> bool:
        """Delete progress."""
        pass
    
    def get_time_spent(self, enrollment_id: UUID) -> int:
        """Get total time spent in seconds."""
        pass
```

---

## Assessment Repositories

### 11. AssessmentRepository

**Purpose:** Manages persistence and retrieval of Assessment aggregates.

**Interface:**
```python
class IAssessmentRepository:
    def find_by_id(self, assessment_id: UUID) -> Optional[Assessment]:
        """Retrieve assessment by ID."""
        pass
    
    def find_by_course(self, course_id: UUID) -> List[Assessment]:
        """Retrieve assessments for course."""
        pass
    
    def find_by_competency(self, competency_id: UUID) -> List[Assessment]:
        """Retrieve assessments for competency."""
        pass
    
    def find_active(self, pagination: PaginationParams) -> PaginatedResult[Assessment]:
        """Retrieve active assessments."""
        pass
    
    def find_by_creator(self, creator_id: UUID, pagination: PaginationParams) -> PaginatedResult[Assessment]:
        """Retrieve assessments by creator."""
        pass
    
    def save(self, assessment: Assessment) -> Assessment:
        """Save or update assessment."""
        pass
    
    def delete(self, assessment_id: UUID) -> bool:
        """Delete assessment."""
        pass
    
    def count_by_course(self, course_id: UUID) -> int:
        """Count assessments in course."""
        pass
```

**Caching Policy:**
- Cache by ID: TTL 5 minutes
- Cache by course: TTL 2 minutes

---

### 12. QuestionRepository

**Purpose:** Manages persistence and retrieval of Question aggregates.

**Interface:**
```python
class IQuestionRepository:
    def find_by_id(self, question_id: UUID) -> Optional[Question]:
        """Retrieve question by ID."""
        pass
    
    def find_by_assessment(self, assessment_id: UUID) -> List[Question]:
        """Retrieve questions for assessment."""
        pass
    
    def find_random_sample(self, assessment_id: UUID, count: int) -> List[Question]:
        """Retrieve random sample of questions."""
        pass
    
    def find_by_type(self, assessment_id: UUID, question_type: QuestionType) -> List[Question]:
        """Retrieve questions by type."""
        pass
    
    def save(self, question: Question) -> Question:
        """Save or update question."""
        pass
    
    def delete(self, question_id: UUID) -> bool:
        """Delete question."""
        pass
    
    def reorder(self, assessment_id: UUID, question_ids: List[UUID]) -> bool:
        """Reorder questions in assessment."""
        pass
    
    def count_by_assessment(self, assessment_id: UUID) -> int:
        """Count questions in assessment."""
        pass
```

**Caching Policy:**
- Cache by ID: TTL 5 minutes
- Cache by assessment: TTL 2 minutes
- Random samples not cached

---

### 13. ScoreRepository

**Purpose:** Manages persistence and retrieval of Score entities.

**Interface:**
```python
class IScoreRepository:
    def find_by_id(self, score_id: UUID) -> Optional[Score]:
        """Retrieve score by ID."""
        pass
    
    def find_by_user_assessment(self, user_id: UUID, assessment_id: UUID) -> List[Score]:
        """Retrieve scores for user+assessment."""
        pass
    
    def find_latest(self, user_id: UUID, assessment_id: UUID) -> Optional[Score]:
        """Retrieve latest score for user+assessment."""
        pass
    
    def find_best(self, user_id: UUID, assessment_id: UUID) -> Optional[Score]:
        """Retrieve best score for user+assessment."""
        pass
    
    def find_by_user(self, user_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[Score]:
        """Retrieve all scores for user."""
        pass
    
    def find_by_assessment(self, assessment_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[Score]:
        """Retrieve all scores for assessment."""
        pass
    
    def get_average_score(self, assessment_id: UUID) -> float:
        """Calculate average score for assessment."""
        pass
    
    def get_pass_rate(self, assessment_id: UUID) -> float:
        """Calculate pass rate for assessment."""
        pass
    
    def save(self, score: Score) -> Score:
        """Save score."""
        pass
    
    def count_attempts(self, user_id: UUID, assessment_id: UUID) -> int:
        """Count attempts for user+assessment."""
        pass
```

---

## Certification Repositories

### 14. CertificateRepository

**Purpose:** Manages persistence and retrieval of Certificate aggregates.

**Interface:**
```python
class ICertificateRepository:
    def find_by_id(self, certificate_id: UUID) -> Optional[Certificate]:
        """Retrieve certificate by ID."""
        pass
    
    def find_by_verification_code(self, code: str) -> Optional[Certificate]:
        """Retrieve certificate by verification code."""
        pass
    
    def find_by_user(self, user_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[Certificate]:
        """Retrieve certificates for user."""
        pass
    
    def find_by_course(self, course_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[Certificate]:
        """Retrieve certificates for course."""
        pass
    
    def find_active_by_user(self, user_id: UUID) -> List[Certificate]:
        """Retrieve active certificates for user."""
        pass
    
    def find_expired(self, pagination: PaginationParams = None) -> PaginatedResult[Certificate]:
        """Retrieve expired certificates."""
        pass
    
    def find_expiring_soon(self, within_days: int) -> List[Certificate]:
        """Retrieve certificates expiring within days."""
        pass
    
    def save(self, certificate: Certificate) -> Certificate:
        """Save or update certificate."""
        pass
    
    def revoke(self, certificate_id: UUID, reason: str) -> bool:
        """Revoke certificate."""
        pass
    
    def count_by_user(self, user_id: UUID) -> int:
        """Count certificates for user."""
        pass
    
    def count_active(self) -> int:
        """Count active certificates."""
        pass
```

**Caching Policy:**
- Cache by ID: TTL 5 minutes
- Cache by verification code: TTL 5 minutes
- Cache by user: TTL 1 minute

---

## Simulation Repositories

### 15. SimulationRepository

**Purpose:** Manages persistence and retrieval of Simulation aggregates.

**Interface:**
```python
class ISimulationRepository:
    def find_by_id(self, simulation_id: UUID) -> Optional[Simulation]:
        """Retrieve simulation by ID."""
        pass
    
    def find_published(self, pagination: PaginationParams = None) -> PaginatedResult[Simulation]:
        """Retrieve published simulations."""
        pass
    
    def find_by_creator(self, creator_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[Simulation]:
        """Retrieve simulations by creator."""
        pass
    
    def find_by_difficulty(self, difficulty: DifficultyLevel, pagination: PaginationParams = None) -> PaginatedResult[Simulation]:
        """Retrieve simulations by difficulty."""
        pass
    
    def find_by_skill(self, skill: str, pagination: PaginationParams = None) -> PaginatedResult[Simulation]:
        """Retrieve simulations by required skill."""
        pass
    
    def save(self, simulation: Simulation) -> Simulation:
        """Save or update simulation."""
        pass
    
    def delete(self, simulation_id: UUID) -> bool:
        """Delete simulation."""
        pass
    
    def count_published(self) -> int:
        """Count published simulations."""
        pass
```

---

### 16. ExecutionRepository

**Purpose:** Manages persistence and retrieval of Execution entities.

**Interface:**
```python
class IExecutionRepository:
    def find_by_id(self, execution_id: UUID) -> Optional[Execution]:
        """Retrieve execution by ID."""
        pass
    
    def find_by_user(self, user_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[Execution]:
        """Retrieve executions for user."""
        pass
    
    def find_by_simulation(self, simulation_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[Execution]:
        """Retrieve executions for simulation."""
        pass
    
    def find_by_user_simulation(self, user_id: UUID, simulation_id: UUID) -> List[Execution]:
        """Retrieve executions for user+simulation."""
        pass
    
    def find_active(self, user_id: UUID) -> Optional[Execution]:
        """Retrieve active execution for user."""
        pass
    
    def save(self, execution: Execution) -> Execution:
        """Save or update execution."""
        pass
    
    def get_leaderboard(self, simulation_id: UUID, limit: int = 10) -> List[Execution]:
        """Get top scores for simulation."""
        pass
    
    def get_user_stats(self, user_id: UUID) -> dict:
        """Get user execution statistics."""
        pass
```

---

## Platform Repositories

### 17. PluginRepository

**Purpose:** Manages persistence and retrieval of Plugin aggregates.

**Interface:**
```python
class IPluginRepository:
    def find_by_id(self, plugin_id: UUID) -> Optional[Plugin]:
        """Retrieve plugin by ID."""
        pass
    
    def find_by_name(self, name: str) -> Optional[Plugin]:
        """Retrieve plugin by name."""
        pass
    
    def find_installed(self, pagination: PaginationParams = None) -> PaginatedResult[Plugin]:
        """Retrieve installed plugins."""
        pass
    
    def find_by_author(self, author_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[Plugin]:
        """Retrieve plugins by author."""
        pass
    
    def find_by_status(self, status: PluginStatus, pagination: PaginationParams = None) -> PaginatedResult[Plugin]:
        """Retrieve plugins by status."""
        pass
    
    def find_by_capability(self, capability_type: CapabilityType) -> List[Plugin]:
        """Retrieve plugins by capability type."""
        pass
    
    def search(self, query: str, filters: List[Filter], pagination: PaginationParams) -> PaginatedResult[Plugin]:
        """Search plugins."""
        pass
    
    def save(self, plugin: Plugin) -> Plugin:
        """Save or update plugin."""
        pass
    
    def delete(self, plugin_id: UUID) -> bool:
        """Delete plugin."""
        pass
    
    def count_installed(self) -> int:
        """Count installed plugins."""
        pass
```

---

### 18. PluginVersionRepository

**Purpose:** Manages persistence and retrieval of PluginVersion entities.

**Interface:**
```python
class IPluginVersionRepository:
    def find_by_id(self, version_id: UUID) -> Optional[PluginVersion]:
        """Retrieve version by ID."""
        pass
    
    def find_by_plugin(self, plugin_id: UUID) -> List[PluginVersion]:
        """Retrieve versions for plugin."""
        pass
    
    def find_latest(self, plugin_id: UUID) -> Optional[PluginVersion]:
        """Retrieve latest version for plugin."""
        pass
    
    def find_by_version(self, plugin_id: UUID, version: SemanticVersion) -> Optional[PluginVersion]:
        """Retrieve specific version."""
        pass
    
    def find_compatible(self, platform_version: SemanticVersion) -> List[PluginVersion]:
        """Retrieve versions compatible with platform."""
        pass
    
    def save(self, version: PluginVersion) -> PluginVersion:
        """Save or update version."""
        pass
    
    def delete(self, version_id: UUID) -> bool:
        """Delete version."""
        pass
```

---

### 19. ConfigurationRepository

**Purpose:** Manages persistence and retrieval of Configuration aggregates.

**Interface:**
```python
class IConfigurationRepository:
    def find_by_key(self, key: ConfigKey, environment: Environment = None) -> Optional[Configuration]:
        """Retrieve configuration by key."""
        pass
    
    def find_by_category(self, category: str, environment: Environment = None) -> List[Configuration]:
        """Retrieve configurations by category."""
        pass
    
    def find_by_environment(self, environment: Environment) -> List[Configuration]:
        """Retrieve all configurations for environment."""
        pass
    
    def find_feature_flags(self, environment: Environment = None) -> List[Configuration]:
        """Retrieve feature flag configurations."""
        pass
    
    def find_secrets(self, environment: Environment = None) -> List[Configuration]:
        """Retrieve secret configurations."""
        pass
    
    def save(self, config: Configuration) -> Configuration:
        """Save or update configuration."""
        pass
    
    def delete(self, config_id: UUID) -> bool:
        """Delete configuration."""
        pass
    
    def get_value(self, key: ConfigKey, environment: Environment = None) -> Optional[ConfigValue]:
        """Get configuration value."""
        pass
    
    def get_value_or_default(self, key: ConfigKey, default: Any, environment: Environment = None) -> Any:
        """Get configuration value or default."""
        pass
```

**Caching Policy:**
- Cache all configs: TTL 5 minutes
- Invalidate on save/delete
- Event-driven invalidation

---

### 20. AuditRepository

**Purpose:** Manages persistence and retrieval of AuditEntry aggregates.

**Interface:**
```python
class IAuditRepository:
    def find_by_id(self, entry_id: UUID) -> Optional[AuditEntry]:
        """Retrieve audit entry by ID."""
        pass
    
    def find_by_event_type(self, event_type: EventType, pagination: PaginationParams = None) -> PaginatedResult[AuditEntry]:
        """Retrieve entries by event type."""
        pass
    
    def find_by_actor(self, actor_id: UUID, pagination: PaginationParams = None) -> PaginatedResult[AuditEntry]:
        """Retrieve entries by actor."""
        pass
    
    def find_by_resource(self, resource_type: str, resource_id: UUID) -> List[AuditEntry]:
        """Retrieve entries for resource."""
        pass
    
    def find_by_date_range(self, start: datetime, end: datetime, pagination: PaginationParams = None) -> PaginatedResult[AuditEntry]:
        """Retrieve entries within date range."""
        pass
    
    def search(self, query: AuditQuery, pagination: PaginationParams) -> PaginatedResult[AuditEntry]:
        """Search audit entries."""
        pass
    
    def save(self, entry: AuditEntry) -> AuditEntry:
        """Save audit entry (append only)."""
        pass
    
    def count_by_event_type(self, event_type: EventType, start: datetime = None, end: datetime = None) -> int:
        """Count entries by event type."""
        pass
    
    def get_latest_hash(self) -> str:
        """Get hash of latest entry for chain verification."""
        pass
    
    def verify_chain(self, start_id: UUID = None, end_id: UUID = None) -> bool:
        """Verify audit chain integrity."""
        pass
```

**Caching Policy:**
- No caching (append-only, immutable)
- Query results cached briefly (30 seconds)

---

## Backup Repositories

### 21. BackupRepository

**Purpose:** Manages persistence and retrieval of Backup aggregates.

**Interface:**
```python
class IBackupRepository:
    def find_by_id(self, backup_id: UUID) -> Optional[Backup]:
        """Retrieve backup by ID."""
        pass
    
    def find_latest(self, backup_type: BackupType = None) -> Optional[Backup]:
        """Retrieve latest backup."""
        pass
    
    def find_by_type(self, backup_type: BackupType, pagination: PaginationParams = None) -> PaginatedResult[Backup]:
        """Retrieve backups by type."""
        pass
    
    def find_by_status(self, status: BackupStatus, pagination: PaginationParams = None) -> PaginatedResult[Backup]:
        """Retrieve backups by status."""
        pass
    
    def find_expiring(self, within_days: int) -> List[Backup]:
        """Retrieve backups expiring within days."""
        pass
    
    def save(self, backup: Backup) -> Backup:
        """Save or update backup."""
        pass
    
    def delete(self, backup_id: UUID) -> bool:
        """Delete backup."""
        pass
    
    def count_by_type(self, backup_type: BackupType) -> int:
        """Count backups by type."""
        pass
    
    def get_total_size(self) -> int:
        """Get total backup size in bytes."""
        pass
```

---

## Repository Implementation Guidelines

### 1. Unit of Work Pattern
```python
class UnitOfWork:
    def __enter__(self):
        self.session = get_db_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.session.close()
    
    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()
```

### 2. Repository Factory
```python
class RepositoryFactory:
    def create_user_repository(self) -> IUserRepository:
        return PostgresUserRepository(get_db_session())
    
    def create_course_repository(self) -> ICourseRepository:
        return PostgresCourseRepository(get_db_session())
    
    def create_cache_user_repository(self) -> IUserRepository:
        return CachedUserRepository(
            PostgresUserRepository(get_db_session()),
            RedisCache(get_redis_client())
        )
```

### 3. Specification Pattern
```python
class ActiveUsersSpec(Specification):
    def to_query(self) -> Query:
        return Query().where(status=UserStatus.ACTIVE)

class UsersByOrganizationSpec(Specification):
    def __init__(self, org_id: UUID):
        self.org_id = org_id
    
    def to_query(self) -> Query:
        return Query().where(organization_id=self.org_id)

# Usage
spec = ActiveUsersSpec().and_(UsersByOrganizationSpec(org_id))
users = user_repo.find(spec, pagination)
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial repository interfaces | AuthShield Team |
| 1.1 | 2024-02-20 | Added simulation and plugin repositories | AuthShield Team |
| 1.2 | 2024-03-10 | Added caching and query specifications | AuthShield Team |
