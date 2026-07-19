# Repository Architecture — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Overview

The Repository layer provides a clean abstraction over SQLAlchemy 2.0 async sessions,
implementing the Repository pattern with Specification support. Every bounded context
owns one or more repositories that encapsulate query logic, enforce consistency
boundaries, and handle pagination, filtering, sorting, and caching.

### 1.1 Design Principles

| Principle | Description |
|---|---|
| Single Responsibility | One repository per aggregate root |
| Interface Segregation | Read/Write separation via ReadOnlyRepository / WriteRepository |
| Specification Pattern | Complex queries composed from reusable specifications |
| Audit Integration | Every write operation creates audit entries |
| Optimistic Locking | Version checking on every update |
| Soft Delete by Default | Hard deletes require explicit repository methods |

---

## 2. Base Repository Interface

### 2.1 ReadOnlyRepository[T] — Generic Read Interface

```python
from typing import TypeVar, Generic, Sequence, Optional
from uuid import UUID

T = TypeVar("T")

class ReadOnlyRepository(Generic[T]):
    """Base interface for read-only repository operations."""

    async def get_by_id(self, id: UUID, include_deleted: bool = False) -> Optional[T]:
        """Retrieve a single entity by primary key.
        
        Args:
            id: Entity UUID
            include_deleted: If True, includes soft-deleted records
            
        Returns:
            Entity or None if not found
        """
        ...

    async def get_by_ids(self, ids: Sequence[UUID], include_deleted: bool = False) -> list[T]:
        """Retrieve multiple entities by primary keys.
        
        Args:
            ids: Sequence of entity UUIDs
            include_deleted: If True, includes soft-deleted records
            
        Returns:
            List of found entities (may be shorter than input if some not found)
        """
        ...

    async def list(
        self,
        filters: Optional[list[FilterSpecification]] = None,
        sort: Optional[list[SortSpecification]] = None,
        pagination: Optional[PaginationSpecification] = None,
        include_deleted: bool = False,
    ) -> PaginatedResult[T]:
        """List entities with filtering, sorting, and pagination.
        
        Args:
            filters: List of filter specifications (AND logic)
            sort: List of sort specifications (applied in order)
            pagination: Offset/cursor pagination
            include_deleted: If True, includes soft-deleted records
            
        Returns:
            PaginatedResult with items, total count, pagination metadata
        """
        ...

    async def search(
        self,
        query: str,
        fields: Optional[list[str]] = None,
        filters: Optional[list[FilterSpecification]] = None,
        pagination: Optional[PaginationSpecification] = None,
    ) -> PaginatedResult[T]:
        """Full-text search across specified fields.
        
        Args:
            query: Search query string
            fields: Fields to search (defaults to name, title, description)
            filters: Additional filter specifications
            pagination: Pagination specification
            
        Returns:
            PaginatedResult with search matches
        """
        ...

    async def count(
        self,
        filters: Optional[list[FilterSpecification]] = None,
        include_deleted: bool = False,
    ) -> int:
        """Count entities matching filters.
        
        Args:
            filters: Filter specifications
            include_deleted: Include soft-deleted records
            
        Returns:
            Count of matching entities
        """
        ...

    async def exists(
        self,
        filters: list[FilterSpecification],
        include_deleted: bool = False,
    ) -> bool:
        """Check if any entity matches the given filters.
        
        Args:
            filters: Filter specifications
            include_deleted: Include soft-deleted records
            
        Returns:
            True if at least one match exists
        """
        ...
```

### 2.2 WriteRepository[T] — Write Operations

```python
class WriteRepository(Generic[T]):
    """Base interface for write repository operations."""

    async def create(self, entity: T, actor_id: Optional[UUID] = None) -> T:
        """Create a new entity.
        
        Args:
            entity: Entity to create (id should be None or will be generated)
            actor_id: User performing the action (for audit)
            
        Returns:
            Created entity with generated ID and timestamps
        """
        ...

    async def update(
        self,
        entity: T,
        actor_id: Optional[UUID] = None,
        expected_version: Optional[int] = None,
    ) -> T:
        """Update an existing entity with optimistic locking.
        
        Args:
            entity: Entity with updated fields
            actor_id: User performing the action (for audit)
            expected_version: Expected current version (for optimistic lock)
            
        Returns:
            Updated entity with incremented version
            
        Raises:
            VersionConflictError: If current version != expected_version
            EntityNotFoundError: If entity doesn't exist
        """
        ...

    async def soft_delete(
        self,
        id: UUID,
        actor_id: Optional[UUID] = None,
        cascade: bool = True,
    ) -> bool:
        """Soft-delete an entity and optionally cascade to children.
        
        Args:
            id: Entity UUID to soft-delete
            actor_id: User performing the action
            cascade: If True, cascade soft-delete to child entities
            
        Returns:
            True if deleted, False if not found
        """
        ...

    async def hard_delete(
        self,
        id: UUID,
        actor_id: Optional[UUID] = None,
    ) -> bool:
        """Permanently remove an entity (GDPR erasure, archival).
        
        WARNING: This operation is irreversible.
        
        Args:
            id: Entity UUID to hard-delete
            actor_id: User performing the action
            
        Returns:
            True if deleted, False if not found
        """
        ...

    async def restore(
        self,
        id: UUID,
        actor_id: Optional[UUID] = None,
    ) -> bool:
        """Restore a soft-deleted entity.
        
        Args:
            id: Entity UUID to restore
            actor_id: User performing the action
            
        Returns:
            True if restored, False if not found or not deleted
        """
        ...

    async def bulk_create(
        self,
        entities: list[T],
        actor_id: Optional[UUID] = None,
    ) -> list[T]:
        """Create multiple entities in a single transaction.
        
        Args:
            entities: List of entities to create
            actor_id: User performing the action
            
        Returns:
            List of created entities with IDs
        """
        ...

    async def bulk_update(
        self,
        entities: list[T],
        actor_id: Optional[UUID] = None,
    ) -> list[T]:
        """Update multiple entities in a single transaction.
        
        Args:
            entities: List of entities to update
            actor_id: User performing the action
            
        Returns:
            List of updated entities
        """
        ...
```

### 2.3 Repository[T] — Combined Read/Write Interface

```python
class Repository(ReadOnlyRepository[T], WriteRepository[T]):
    """Full repository with read and write operations."""
    pass
```

---

## 3. Specification Pattern

### 3.1 Specification Base Classes

```python
from abc import ABC, abstractmethod
from sqlalchemy import Select, BinaryExpression

class Specification(ABC):
    """Base specification for composable query building."""

    @abstractmethod
    def to_clause(self) -> BinaryExpression:
        """Convert specification to SQLAlchemy WHERE clause."""
        ...

    def and_(self, other: "Specification") -> "AndSpecification":
        return AndSpecification(self, other)

    def or_(self, other: "Specification") -> "OrSpecification":
        return OrSpecification(self, other)

    def not_(self) -> "NotSpecification":
        return NotSpecification(self)


class FilterSpecification(Specification):
    """Field-level filter specification."""

    def __init__(self, field: str, operator: str, value: any):
        self.field = field
        self.operator = operator
        self.value = value


class SortSpecification:
    """Sort specification."""

    def __init__(self, field: str, direction: str = "asc"):
        self.field = field
        self.direction = direction  # "asc" or "desc"


class PaginationSpecification:
    """Pagination specification (offset-based or cursor-based)."""

    def __init__(
        self,
        offset: int = 0,
        limit: int = 50,
        cursor: Optional[str] = None,
    ):
        self.offset = offset
        self.limit = min(limit, 100)  # Max 100 per page
        self.cursor = cursor


class AndSpecification(Specification):
    """Combines two specifications with AND logic."""

    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def to_clause(self):
        return self.left.to_clause() & self.right.to_clause()


class OrSpecification(Specification):
    """Combines two specifications with OR logic."""

    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def to_clause(self):
        return self.left.to_clause() | self.right.to_clause()


class NotSpecification(Specification):
    """Negates a specification."""

    def __init__(self, spec: Specification):
        self.spec = spec

    def to_clause(self):
        return ~self.spec.to_clause()
```

### 3.2 Common Filter Specifications

```python
class IsDeletedFilter(FilterSpecification):
    """Filter by soft-delete status."""
    def __init__(self, include_deleted: bool = False):
        super().__init__("is_deleted", "eq", 0 if not include_deleted else None)

class StatusFilter(FilterSpecification):
    """Filter by status."""
    def __init__(self, status: str):
        super().__init__("status", "eq", status)

class UserIdFilter(FilterSpecification):
    """Filter by user ID."""
    def __init__(self, user_id: UUID):
        super().__init__("user_id", "eq", user_id)

class CreatedAfterFilter(FilterSpecification):
    """Filter by creation date."""
    def __init__(self, since: datetime):
        super().__init__("created_at", "gte", since)

class CreatedBeforeFilter(FilterSpecification):
    """Filter by creation date."""
    def __init__(self, before: datetime):
        super().__init__("created_at", "lte", before)

class TextSearchFilter(FilterSpecification):
    """Full-text search filter."""
    def __init__(self, field: str, query: str):
        super().__init__(field, "like", f"%{query}%")
```

### 3.3 Domain-Specific Specifications

```python
# Learning domain
class ActiveCourseFilter(StatusFilter):
    def __init__(self):
        super().__init__("active")

class EnrolledUserFilter(UserIdFilter):
    """Users enrolled in a specific course."""
    def __init__(self, course_id: UUID):
        super().__init__(course_id)
        self.field = "course_id"

class CompletedLessonsFilter(FilterSpecification):
    """Lessons with completion status."""
    def __init__(self):
        super().__init__("status", "eq", "completed")

class PassedAssessmentFilter(FilterSpecification):
    """Results with passing score."""
    def __init__(self, passing_score: float):
        super().__init__("score", "gte", passing_score)

class ActivePluginFilter(StatusFilter):
    def __init__(self):
        super().__init__("active")

class UnreadNotificationFilter(FilterSpecification):
    def __init__(self):
        super().__init__("is_read", "eq", 0)

# Assessment domain
class InProgressAttemptFilter(StatusFilter):
    def __init__(self):
        super().__init__("in_progress")

class GradedResultFilter(FilterSpecification):
    def __init__(self):
        super().__init__("is_graded", "eq", 1)
```

---

## 4. Pagination Strategies

### 4.1 Offset-Based Pagination

```python
class OffsetPagination(PaginationSpecification):
    """Traditional offset/limit pagination.
    
    Best for: Small datasets, admin dashboards, page-number navigation.
    Limitations: Inconsistent results when data changes between pages.
    """

    def __init__(self, page: int = 1, page_size: int = 50):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), 100)
        self.offset = (self.page - 1) * self.page_size
        self.limit = self.page_size


class PaginatedResult(Generic[T]):
    """Result container for paginated queries."""
    
    def __init__(
        self,
        items: list[T],
        total_count: int,
        page: int,
        page_size: int,
    ):
        self.items = items
        self.total_count = total_count
        self.page = page
        self.page_size = page_size
        self.total_pages = (total_count + page_size - 1) // page_size
        self.has_next = page < self.total_pages
        self.has_previous = page > 1

    @property
    def pagination_meta(self) -> dict:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total_count": self.total_count,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
        }
```

### 4.2 Cursor-Based Pagination

```python
class CursorPagination(PaginationSpecification):
    """Cursor-based pagination for large datasets.
    
    Best for: Infinite scroll, real-time feeds, large datasets.
    Advantages: Consistent results regardless of data changes.
    """

    def __init__(self, cursor: Optional[str] = None, limit: int = 50):
        self.cursor = cursor  # Encoded cursor (base64 of last item's sort key)
        self.limit = min(max(1, limit), 100)

    def decode_cursor(self) -> dict:
        """Decode cursor to extract sort key values."""
        if not self.cursor:
            return {}
        import base64, json
        return json.loads(base64.b64decode(self.cursor))

    @staticmethod
    def encode_cursor(sort_values: dict) -> str:
        """Encode sort values into a cursor string."""
        import base64, json
        return base64.b64encode(json.dumps(sort_values).encode()).decode()
```

---

## 5. Filtering System

### 5.1 Field-Level Filters

| Operator | Description | Example |
|---|---|---|
| `eq` | Equals | `FilterSpec("status", "eq", "active")` |
| `ne` | Not equals | `FilterSpec("status", "ne", "deleted")` |
| `gt` | Greater than | `FilterSpec("score", "gt", 80.0)` |
| `gte` | Greater than or equal | `FilterSpec("score", "gte", 70.0)` |
| `lt` | Less than | `FilterSpec("attempts", "lt", 3)` |
| `lte` | Less than or equal | `FilterSpec("days_old", "lte", 30)` |
| `in` | In list | `FilterSpec("status", "in", ["active", "pending"])` |
| `not_in` | Not in list | `FilterSpec("role", "not_in", ["banned"])` |
| `like` | Pattern match | `FilterSpec("name", "like", "%security%")` |
| `ilike` | Case-insensitive match | `FilterSpec("title", "ilike", "%python%")` |
| `is_null` | Is NULL | `FilterSpec("deleted_at", "is_null", True)` |
| `is_not_null` | Is not NULL | `FilterSpec("email_verified_at", "is_not_null", True)` |
| `between` | Range | `FilterSpec("score", "between", (60, 100))` |
| `contains` | JSON contains | `FilterSpec("tags", "contains", "python")` |

### 5.2 Composite Filters

```python
# Active courses with Python in the title
spec = (
    StatusFilter("active")
    .and_(TextSearchFilter("title", "python"))
    .and_(CreatedAfterFilter(datetime(2025, 1, 1)))
)

# Failed logins OR locked accounts
spec = (
    FilterSpecification("failed_login_attempts", "gte", 5)
    .or_(FilterSpecification("locked_until", "gt", datetime.now()))
)

# Exclude soft-deleted
spec = IsDeletedFilter(include_deleted=False)
```

---

## 6. Sorting System

### 6.1 Multi-Field Sorting

```python
# Sort by status (active first), then by title alphabetically
sort_specs = [
    SortSpecification("status", "asc"),
    SortSpecification("title", "asc"),
]

# Sort by most recent, then by score descending
sort_specs = [
    SortSpecification("created_at", "desc"),
    SortSpecification("score", "desc"),
]

# Sort by enrollment count (requires joined query)
sort_specs = [
    SortSpecification("enrollment_count", "desc"),
    SortSpecification("title", "asc"),
]
```

### 6.2 Dynamic Sorting

```python
# From API query parameters
ALLOWED_SORT_FIELDS = {
    "title": "courses.title",
    "created_at": "courses.created_at",
    "status": "courses.status",
    "difficulty": "courses.difficulty",
    "enrollment_count": "enrollment_count",  # Computed field
}

def parse_sort_params(sort_by: str, sort_order: str) -> list[SortSpecification]:
    """Parse API sort parameters into specifications."""
    fields = sort_by.split(",")
    return [
        SortSpecification(
            ALLOWED_SORT_FIELDS[f.strip()],
            sort_order if i == 0 else "asc"
        )
        for i, f in enumerate(fields)
        if f.strip() in ALLOWED_SORT_FIELDS
    ]
```

---

## 7. Caching Policy

### 7.1 Cache Strategy

| Operation | Cache Behavior | TTL |
|---|---|---|
| `get_by_id` | Cache on miss | 5 minutes |
| `list` | Cache on miss | 2 minutes |
| `search` | No caching (volatile) | — |
| `count` | Cache on miss | 1 minute |
| `create` | Invalidate related caches | — |
| `update` | Invalidate entity + related caches | — |
| `soft_delete` | Invalidate entity + related caches | — |

### 7.2 Cache Invalidation Rules

```python
class CachePolicy:
    """Cache invalidation policy for repositories."""

    @staticmethod
    def on_write(entity_type: str, entity_id: UUID):
        """Invalidate caches after a write operation."""
        cache.invalidate(f"{entity_type}:{entity_id}")
        cache.invalidate(f"{entity_type}:list:*")
        cache.invalidate(f"{entity_type}:count:*")

    @staticmethod
    def on_bulk_write(entity_type: str):
        """Invalidate all caches for a type after bulk operation."""
        cache.invalidate_pattern(f"{entity_type}:*")

    @staticmethod
    def dependencies() -> dict[str, list[str]]:
        """Cache dependency graph — when X changes, invalidate Y."""
        return {
            "users": ["roles", "sessions", "enrollments"],
            "courses": ["modules", "lessons", "enrollments", "assessments"],
            "roles": ["permissions", "user_roles"],
            "plugins": ["plugin_configs", "plugin_hooks"],
        }
```

### 7.3 Cache Implementation

```python
from functools import lru_cache
import time

class InMemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, expiry = self._store[key]
            if time.time() < expiry:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        self._store[key] = (value, time.time() + ttl_seconds)

    def invalidate(self, key: str):
        self._store.pop(key, None)

    def invalidate_pattern(self, pattern: str):
        import fnmatch
        keys_to_delete = [k for k in self._store if fnmatch.fnmatch(k, pattern)]
        for k in keys_to_delete:
            del self._store[k]
```

---

## 8. Concurrency Strategy

### 8.1 Optimistic Locking

Every entity carries a `version` integer column. On update, the repository checks
that the current version matches the expected version:

```python
async def update(self, entity: T, actor_id: UUID, expected_version: int) -> T:
    """Update with optimistic locking."""
    current = await self.get_by_id(entity.id)
    
    if current is None:
        raise EntityNotFoundError(entity.id)
    
    if current.version != expected_version:
        raise VersionConflictError(
            entity_id=entity.id,
            expected_version=expected_version,
            actual_version=current.version,
        )
    
    entity.version = expected_version + 1
    entity.updated_at = datetime.utcnow()
    entity.updated_by = actor_id
    
    # Execute update with WHERE version = expected_version
    result = await self.session.execute(
        update(self.model)
        .where(self.model.id == entity.id)
        .where(self.model.version == expected_version)
        .values(**entity.to_dict())
    )
    
    if result.rowcount == 0:
        raise VersionConflictError(entity.id, expected_version, expected_version + 1)
    
    return entity
```

### 8.2 VersionConflictError

```python
class VersionConflictError(Exception):
    """Raised when optimistic lock check fails."""
    
    def __init__(self, entity_id: UUID, expected_version: int, actual_version: int):
        self.entity_id = entity_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"Version conflict on {entity_id}: "
            f"expected v{expected_version}, found v{actual_version}"
        )
```

---

## 9. Per-Repository Specifications

### 9.1 UserRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get user by UUID |
| `get_by_email(email)` | Get user by email address |
| `search(query)` | Search by name, email |
| `list_active(pagination)` | List active users |
| `list_suspended(pagination)` | List suspended users |
| `list_locked(pagination)` | List locked accounts |
| `count_active()` | Count active users |
| `count_by_status(status)` | Count by status |
| `create(user, actor)` | Create user with password hashing |
| `update(user, actor, version)` | Update user profile |
| `update_password(user_id, hash, actor)` | Update password hash |
| `update_last_login(user_id, ip)` | Update last login timestamp |
| `lock_account(user_id, duration, actor)` | Lock user account |
| `unlock_account(user_id, actor)` | Unlock user account |
| `soft_delete(user_id, actor)` | Soft-delete user |
| `get_user_roles(user_id)` | Get user's roles |
| `assign_role(user_id, role_id, actor)` | Assign role to user |
| `remove_role(user_id, role_id, actor)` | Remove role from user |
| `get_permissions(user_id)` | Get effective permissions |

### 9.2 RoleRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get role by UUID |
| `get_by_name(name)` | Get role by name |
| `list_all(include_system)` | List all roles |
| `list_default()` | List default roles |
| `create(role, actor)` | Create role |
| `update(role, actor, version)` | Update role |
| `delete(role_id, actor)` | Soft-delete role (non-system only) |
| `get_permissions(role_id)` | Get role's permissions |
| `grant_permission(role_id, perm_id, actor)` | Grant permission |
| `revoke_permission(role_id, perm_id, actor)` | Revoke permission |
| `get_users_with_role(role_id)` | Get users assigned to role |

### 9.3 PermissionRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get permission by UUID |
| `get_by_name(name)` | Get permission by name (e.g., "course.create") |
| `list_all()` | List all permissions |
| `list_by_resource(resource_type)` | List permissions for a resource |
| `list_by_action(action)` | List permissions for an action |
| `list_for_user(user_id)` | Get effective permissions for user |
| `create(permission, actor)` | Create permission |
| `check_access(user_id, resource, action)` | Check if user has permission |

### 9.4 SessionRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get session by UUID |
| `get_by_token(token)` | Get session by token string |
| `get_active_for_user(user_id)` | Get active sessions for user |
| `list_all_active()` | List all active sessions |
| `create(session)` | Create session |
| `update_activity(session_id)` | Update last active timestamp |
| `expire(session_id)` | Mark session as expired |
| `revoke(session_id, actor)` | Revoke session |
| `revoke_all_for_user(user_id, actor)` | Revoke all user sessions |
| `cleanup_expired()` | Remove expired sessions |

### 9.5 AuditRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get audit entry by UUID |
| `list_by_user(user_id, pagination)` | List entries for a user |
| `list_by_entity(entity_type, entity_id)` | List entries for an entity |
| `list_by_action(action, pagination)` | List entries by action type |
| `list_by_time_range(start, end)` | List entries in time range |
| `search(query)` | Search audit entries |
| `get_hash_chain()` | Get full hash chain for verification |
| `verify_integrity()` | Verify hash chain integrity |
| `create(entry)` | Create audit entry (append-only) |
| `export(format, filters)` | Export audit data (JSON/CSV) |

### 9.6 CourseRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get course by UUID |
| `get_by_slug(slug)` | Get course by URL slug |
| `list_published(pagination)` | List published courses |
| `list_by_instructor(instructor_id)` | List courses by instructor |
| `list_by_organization(org_id)` | List courses for organization |
| `search(query)` | Full-text search courses |
| `create(course, actor)` | Create course (draft status) |
| `update(course, actor, version)` | Update course metadata |
| `publish(course_id, actor)` | Publish course (draft → active) |
| `archive(course_id, actor)` | Archive course |
| `get_enrollment_count(course_id)` | Get enrollment count |
| `get_completion_rate(course_id)` | Get completion rate |
| `get_modules(course_id)` | Get ordered modules |
| `soft_delete(course_id, actor)` | Soft-delete course |

### 9.7 LessonRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get lesson by UUID |
| `list_by_module(module_id)` | List lessons in module |
| `list_by_course(course_id)` | List all lessons in course |
| `create(lesson, actor)` | Create lesson |
| `update(lesson, actor, version)` | Update lesson content |
| `reorder(module_id, lesson_ids, actor)` | Reorder lessons |
| `get_progress(user_id, lesson_id)` | Get user progress for lesson |

### 9.8 AssessmentRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get assessment by UUID |
| `list_by_course(course_id)` | List assessments for course |
| `list_published(course_id)` | List published assessments |
| `create(assessment, actor)` | Create assessment |
| `update(assessment, actor, version)` | Update assessment |
| `publish(assessment_id, actor)` | Publish assessment |
| `get_questions(assessment_id)` | Get ordered questions |
| `get_results(assessment_id, pagination)` | Get results for assessment |
| `get_statistics(assessment_id)` | Get score statistics |

### 9.9 CertificateRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get certificate by UUID |
| `get_by_number(number)` | Get by certificate number |
| `list_for_user(user_id)` | List user's certificates |
| `list_for_course(course_id)` | List certificates for course |
| `issue(user_id, course_id, template_id, actor)` | Issue new certificate |
| `revoke(cert_id, reason, actor)` | Revoke certificate |
| `verify(cert_number, signature)` | Verify certificate authenticity |

### 9.10 PluginRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get plugin by UUID |
| `get_by_name(name)` | Get plugin by name |
| `list_active()` | List active plugins |
| `list_all(include_disabled)` | List all plugins |
| `install(plugin_data, actor)` | Install plugin |
| `update(plugin_id, version, actor)` | Update plugin version |
| `enable(plugin_id, actor)` | Enable plugin |
| `disable(plugin_id, actor)` | Disable plugin |
| `uninstall(plugin_id, actor)` | Uninstall plugin |
| `get_config(plugin_id)` | Get plugin configuration |
| `update_config(plugin_id, config, actor)` | Update plugin config |

### 9.11 ConfigurationRepository

| Method | Description |
|---|---|
| `get_by_key(key)` | Get configuration by key |
| `get_by_category(category)` | List configs by category |
| `list_all(include_sensitive)` | List all configurations |
| `set(key, value, type, actor)` | Set configuration value |
| `set_many(configs, actor)` | Set multiple configurations |
| `get_typed(key, target_type)` | Get config with type casting |
| `get_int(key, default)` | Get integer config |
| `get_bool(key, default)` | Get boolean config |
| `get_json(key, default)` | Get JSON config |
| `get_encrypted(key)` | Get encrypted config value |

### 9.12 BackupRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get backup record by UUID |
| `list_by_type(type)` | List backups by type |
| `list_recent(count)` | List recent backups |
| `create_record(record)` | Create backup record |
| `mark_completed(id, metadata)` | Mark backup as completed |
| `mark_failed(id, error)` | Mark backup as failed |
| `get_latest_full()` | Get latest full backup |
| `cleanup_expired()` | Remove expired backups |
| `get_restore_history()` | List restore operations |

### 9.13 ReportRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get report by UUID |
| `list_for_user(user_id)` | List user's reports |
| `list_by_type(report_type)` | List reports by type |
| `create(report, actor)` | Create report record |
| `update_result(id, data, actor)` | Store report results |
| `delete_expired()` | Remove expired reports |
| `get_scheduled()` | Get reports due for generation |

### 9.14 NotificationRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get notification by UUID |
| `list_for_user(user_id, unread_only)` | List user notifications |
| `list_unread(user_id)` | List unread notifications |
| `count_unread(user_id)` | Count unread notifications |
| `create(notification)` | Create and send notification |
| `mark_read(id)` | Mark notification as read |
| `mark_all_read(user_id)` | Mark all as read for user |
| `delete_old(days)` | Remove old notifications |
| `get_preferences(user_id)` | Get notification preferences |

### 9.15 OrganizationRepository

| Method | Description |
|---|---|
| `get_by_id(id)` | Get organization by UUID |
| `get_by_slug(slug)` | Get by URL slug |
| `list_all(pagination)` | List all organizations |
| `list_for_user(user_id)` | List user's organizations |
| `create(org, actor)` | Create organization |
| `update(org, actor, version)` | Update organization |
| `add_member(org_id, user_id, role, actor)` | Add member |
| `remove_member(org_id, user_id, actor)` | Remove member |
| `get_members(org_id)` | List organization members |
| `get_courses(org_id)` | List organization courses |

---

## 10. Repository Implementation Pattern

### 10.1 SQLAlchemy Async Implementation

```python
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy async implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = User
        self.cache = InMemoryCache()

    async def get_by_id(self, id: UUID, include_deleted: bool = False) -> Optional[User]:
        cache_key = f"user:{id}"
        cached = self.cache.get(cache_key)
        if cached and not include_deleted:
            return cached

        query = select(self.model).where(self.model.id == id)
        if not include_deleted:
            query = query.where(self.model.is_deleted == False)

        result = await self.session.execute(query)
        entity = result.scalar_one_or_none()

        if entity and not include_deleted:
            self.cache.set(cache_key, entity, ttl_seconds=300)

        return entity

    async def get_by_email(self, email: str) -> Optional[User]:
        cache_key = f"user:email:{email.lower()}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        query = (
            select(self.model)
            .where(self.model.email == email.lower())
            .where(self.model.is_deleted == False)
        )
        result = await self.session.execute(query)
        entity = result.scalar_one_or_none()

        if entity:
            self.cache.set(cache_key, entity, ttl_seconds=300)
            self.cache.set(f"user:{entity.id}", entity, ttl_seconds=300)

        return entity

    async def create(self, user: User, actor_id: Optional[UUID] = None) -> User:
        user.id = uuid.uuid4()
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        user.created_by = actor_id
        user.version = 1

        self.session.add(user)
        await self.session.flush()

        # Audit entry
        audit = AuditEntry(
            user_id=actor_id,
            action="user.create",
            entity_type="users",
            entity_id=user.id,
            new_value=user.to_audit_dict(),
        )
        self.session.add(audit)

        return user

    async def update(
        self, user: User, actor_id: UUID, expected_version: int
    ) -> User:
        current = await self.get_by_id(user.id)
        if current is None:
            raise EntityNotFoundError(user.id)
        if current.version != expected_version:
            raise VersionConflictError(user.id, expected_version, current.version)

        old_value = current.to_audit_dict()

        user.version = expected_version + 1
        user.updated_at = datetime.utcnow()
        user.updated_by = actor_id

        await self.session.execute(
            update(self.model)
            .where(self.model.id == user.id)
            .where(self.model.version == expected_version)
            .values(**user.to_update_dict())
        )

        # Audit entry
        audit = AuditEntry(
            user_id=actor_id,
            action="user.update",
            entity_type="users",
            entity_id=user.id,
            old_value=old_value,
            new_value=user.to_audit_dict(),
        )
        self.session.add(audit)

        # Invalidate cache
        CachePolicy.on_write("users", user.id)

        return user

    async def soft_delete(self, id: UUID, actor_id: UUID, cascade: bool = True) -> bool:
        entity = await self.get_by_id(id)
        if entity is None:
            return False

        old_value = entity.to_audit_dict()

        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(
                is_deleted=True,
                deleted_at=datetime.utcnow(),
                deleted_by=actor_id,
                version=entity.version + 1,
                updated_at=datetime.utcnow(),
                updated_by=actor_id,
            )
        )

        # Audit entry
        audit = AuditEntry(
            user_id=actor_id,
            action="user.delete",
            entity_type="users",
            entity_id=id,
            old_value=old_value,
        )
        self.session.add(audit)

        # Cascade to related entities
        if cascade:
            await self._cascade_soft_delete(id, actor_id)

        CachePolicy.on_write("users", id)
        return True

    async def _cascade_soft_delete(self, user_id: UUID, actor_id: UUID):
        """Soft-delete related entities."""
        # Sessions
        await self.session.execute(
            update(Session)
            .where(Session.user_id == user_id)
            .where(Session.is_deleted == False)
            .values(is_deleted=True, deleted_at=datetime.utcnow(), deleted_by=actor_id)
        )
        # Notifications
        await self.session.execute(
            update(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_deleted == False)
            .values(is_deleted=True, deleted_at=datetime.utcnow(), deleted_by=actor_id)
        )
```

---

## 11. Query Builder Integration

### 11.1 Specification to Query Translation

```python
class QueryBuilder:
    """Translates specifications into SQLAlchemy queries."""

    def __init__(self, model, session: AsyncSession):
        self.model = model
        self.session = session
        self._query = select(model)
        self._filters = []

    def filter(self, spec: Specification) -> "QueryBuilder":
        """Add a filter specification."""
        self._filters.append(spec.to_clause())
        return self

    def sort(self, *specs: SortSpecification) -> "QueryBuilder":
        """Add sort specifications."""
        for spec in specs:
            column = getattr(self.model, spec.field)
            if spec.direction == "desc":
                self._query = self._query.order_by(column.desc())
            else:
                self._query = self._query.order_by(column.asc())
        return self

    def paginate(self, spec: PaginationSpecification) -> "QueryBuilder":
        """Add pagination."""
        if hasattr(spec, "cursor") and spec.cursor:
            # Cursor-based: decode and apply
            cursor_data = spec.decode_cursor()
            # Apply cursor conditions...
        else:
            # Offset-based
            self._query = self._query.offset(spec.offset).limit(spec.limit)
        return self

    async def execute(self) -> Sequence:
        """Execute the built query."""
        for f in self._filters:
            self._query = self._query.where(f)
        result = await self.session.execute(self._query)
        return result.scalars().all()

    async def count(self) -> int:
        """Execute count query."""
        count_query = select(func.count()).select_from(self.model)
        for f in self._filters:
            count_query = count_query.where(f)
        result = await self.session.execute(count_query)
        return result.scalar()
```

---

## 12. Error Handling

### 12.1 Repository Exceptions

```python
class RepositoryError(Exception):
    """Base repository error."""
    pass

class EntityNotFoundError(RepositoryError):
    """Raised when requested entity doesn't exist."""
    def __init__(self, entity_id: UUID):
        self.entity_id = entity_id
        super().__init__(f"Entity not found: {entity_id}")

class VersionConflictError(RepositoryError):
    """Raised when optimistic lock check fails."""
    def __init__(self, entity_id: UUID, expected: int, actual: int):
        self.entity_id = entity_id
        self.expected_version = expected
        self.actual_version = actual
        super().__init__(
            f"Version conflict on {entity_id}: "
            f"expected v{expected}, found v{actual}"
        )

class DuplicateEntityError(RepositoryError):
    """Raised when unique constraint is violated."""
    def __init__(self, entity_type: str, field: str, value: str):
        super().__init__(
            f"Duplicate {entity_type}: {field}='{value}' already exists"
        )

class IntegrityError(RepositoryError):
    """Raised when referential integrity is violated."""
    def __init__(self, message: str):
        super().__init__(message)

class ConcurrencyError(RepositoryError):
    """Raised when concurrent modification is detected."""
    def __init__(self, entity_id: UUID):
        super().__init__(f"Concurrent modification detected for {entity_id}")
```

---

*This document defines the complete repository architecture for AuthShield Lab.*
