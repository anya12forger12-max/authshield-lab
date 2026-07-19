# FastAPI Standards — AuthShield Lab

This document defines the standards for building FastAPI endpoints, routers,
dependencies, and middleware in the AuthShield Lab project.

---

## 1. Project Structure

```
authshield/
├── api/
│   ├── __init__.py
│   ├── deps.py              # Shared dependencies
│   ├── middleware.py         # Middleware definitions
│   ├── app.py               # FastAPI app factory
│   └── v1/
│       ├── __init__.py
│       ├── router.py        # v1 aggregate router
│       ├── auth.py
│       ├── users.py
│       ├── audit.py
│       └── schemas/
│           ├── __init__.py
│           ├── auth.py
│           ├── users.py
│           └── audit.py
```

---

## 2. App Factory Pattern

Create the application through a factory function to enable testing and
multiple configurations.

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    yield
    # Shutdown — close pools, flush buffers, etc.


def create_app() -> FastAPI:
    app = FastAPI(
        title="AuthShield Lab API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Middleware — order matters (last added = first executed)
    app.add_middleware(SomeMiddleware)

    # Routers
    from authshield.api.v1.router import api_router

    app.include_router(api_router, prefix="/api/v1")

    # Exception handlers
    register_exception_handlers(app)

    return app
```

### Rules

- Always use the `lifespan` parameter instead of deprecated `on_startup` /
  `on_shutdown` event hooks.
- Instantiate routers inside the factory or via lazy imports to avoid circular
  import issues.

---

## 3. Router Organization

Each resource domain gets its own router module. A top-level `router.py`
aggregates them under a shared prefix.

### Individual router module

```python
from fastapi import APIRouter, Depends

from authshield.api.deps import get_current_user
from authshield.api.v1.schemas.users import UserCreateRequest, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> User:
    ...
```

### Aggregate router

```python
from fastapi import APIRouter

from authshield.api.v1 import auth, users, audit

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(audit.router)
```

### Conventions

- Set `prefix` on the individual router, not on the aggregate.
- Set `tags` on each router for OpenAPI grouping.
- Use `dependencies` at the router level when all endpoints require the same
  guards (e.g., authentication).
- Route paths use kebab-case: `/audit-logs/`, `/api-keys/`.

---

## 4. Dependency Injection Patterns

### 4.1 Yield dependencies (resource management)

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 4.2 Class-based dependencies

```python
from fastapi import Depends, Request


class RateLimiter:
    def __init__(self, times: int, seconds: int) -> None:
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request) -> None:
        # Check rate limit using request.client.host and path
        ...


# Usage
@router.get(
    "/",
    dependencies=[Depends(RateLimiter(times=100, seconds=60))],
)
async def list_users() -> list[UserResponse]:
    ...
```

### 4.3 Dependency overrides for testing

```python
def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
```

---

## 5. Request/Response Models

### 5.1 Request models

- Name request models as `{Resource}CreateRequest`, `{Resource}UpdateRequest`, etc.
- Use `Field(...)` for required fields with validation constraints.
- Use `Field(default=...)` for optional fields.

```python
class AuditLogCreateRequest(BaseModel):
    action: str = Field(..., max_length=128, examples=["user.login"])
    actor_id: UUID
    resource_type: str = Field(..., max_length=64)
    resource_id: UUID | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
```

### 5.2 Response models

- Name response models as `{Resource}Response`, `{Resource}ListResponse`.
- Use `from_attributes = True` on the model config to enable ORM mode.
- Always specify `response_model` on the route decorator.

```python
@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(...) -> User:
    ...
```

### 5.3 `response_model_exclude_unset`

Use `response_model_exclude_unset=True` on PATCH endpoints to omit fields the
client did not send.

```python
@router.patch("/{user_id}", response_model=UserResponse, response_model_exclude_unset=True)
async def update_user(...) -> User:
    ...
```

### 5.4 List responses with pagination

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool


class UserListResponse(PaginatedResponse[UserResponse]):
    pass
```

---

## 6. Error Handling

### 6.1 HTTPException patterns

Use `HTTPException` only for simple cases. Prefer custom exception handlers
for structured error responses.

```python
from fastapi import HTTPException


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, session: AsyncSession = Depends(get_session)) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "USER_NOT_FOUND",
                "message": f"User '{user_id}' does not exist.",
            },
        )
    return user
```

### 6.2 Exception handlers

Register a global handler for `AuthShieldException` in the app factory.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AuthShieldException)
    async def authshield_exception_handler(
        request: Request, exc: AuthShieldException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "about:blank",
                "title": exc.code,
                "status": exc.status_code,
                "detail": str(exc),
                "instance": str(request.url),
            },
        )
```

---

## 7. Middleware Ordering

Middleware executes in **reverse** registration order. The recommended stack
(top-to-bottom in `add_middleware` calls, which means bottom-to-top execution):

```python
app.add_middleware(CORSMiddleware, ...)          # Executes 5th
app.add_middleware(GZipMiddleware, ...)           # Executes 4th
app.add_middleware(TrustedHostMiddleware, ...)    # Executes 3rd
app.add_middleware(RequestIdMiddleware)           # Executes 2nd
app.add_middleware(StructuredLoggingMiddleware)   # Executes 1st (outermost)
```

Order rationale:
1. **Structured logging** must wrap everything to capture all request data.
2. **Request ID** injection must happen before any handler reads it.
3. **Trusted host** validation rejects bad hosts early.
4. **GZip** compression is applied after response body is built.
5. **CORS** headers are added last to ensure they are always present.

---

## 8. Background Tasks vs. Event-Driven

### 8.1 FastAPI BackgroundTasks

Use for short, fire-and-forget work that must complete before the response is
sent (or shortly after).

```python
from fastapi import BackgroundTasks


async def send_welcome_email(user_email: str) -> None:
    ...


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreateRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> User:
    user = User(**payload.model_dump())
    session.add(user)
    await session.flush()
    background_tasks.add_task(send_welcome_email, user.email)
    return user
```

### 8.2 Long-running work

For jobs that take longer than a few seconds, publish to a task queue (e.g.,
Celery, ARQ, or a custom SQLite-backed queue) instead of using BackgroundTasks.

```python
@router.post("/reports/generate", status_code=202)
async def generate_report(
    payload: ReportRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    job_id = uuid4()
    await enqueue_job("generate_report", job_id=job_id, **payload.model_dump())
    return {"job_id": str(job_id), "status": "queued"}
```

---

## 9. OpenAPI Schema Customization

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="AuthShield Lab API",
        version="1.0.0",
        openapi_tags=[
            {"name": "auth", "description": "Authentication & authorization"},
            {"name": "users", "description": "User management"},
            {"name": "audit", "description": "Audit log queries"},
        ],
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )
    return app
```

Use the `response_model_include` and `response_model_exclude` parameters
sparingly; prefer dedicated response models instead.

---

## 10. Rate Limiting

Implement rate limiting via a dependency that inspects a token bucket or
fixed-window counter stored in Redis (or a local dict for development).

```python
class RateLimiter:
    def __init__(
        self,
        times: int,
        seconds: int,
        key_func: Callable[[Request], str] | None = None,
    ) -> None:
        self.times = times
        self.seconds = seconds
        self.key_func = key_func or self._default_key

    async def __call__(self, request: Request) -> None:
        key = self.key_func(request)
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, self.seconds)
        if current > self.times:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later.",
                headers={"Retry-After": str(self.seconds)},
            )

    @staticmethod
    def _default_key(request: Request) -> str:
        return f"rate_limit:{request.client.host}:{request.url.path}"


# Usage at router or endpoint level
@router.post(
    "/login",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def login(...) -> TokenResponse:
    ...
```

---

## 11. Pagination Patterns

### 11.1 Offset-based (default)

```python
from fastapi import Query


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    offset = (page - 1) * page_size
    stmt = select(User).offset(offset).limit(page_size)
    result = await session.execute(stmt)
    items = result.scalars().all()
    total = await session.scalar(select(func.count(User.id)))
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": offset + page_size < total,
    }
```

### 11.2 Cursor-based

For large datasets or real-time streams, use cursor-based pagination.

```python
@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    cursor: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    stmt = select(AuditLog).order_by(AuditLog.id)
    if cursor:
        stmt = stmt.where(AuditLog.id > cursor)
    stmt = stmt.limit(limit + 1)
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    has_next = len(rows) > limit
    return {
        "items": rows[:limit],
        "next_cursor": str(rows[limit].id) if has_next else None,
    }
```

---

## 12. Filtering and Sorting

```python
from enum import StrEnum


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


@router.get("/", response_model=UserListResponse)
async def list_users(
    search: str | None = Query(None, description="Search by username or email"),
    role: str | None = Query(None),
    sort_by: str = Query("created_at", pattern=r"^(created_at|username|email)$"),
    sort_order: SortOrder = SortOrder.DESC,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    stmt = select(User)

    if search:
        stmt = stmt.where(
            User.username.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
        )
    if role:
        stmt = stmt.where(User.role == role)

    order_col = getattr(User, sort_by)
    stmt = stmt.order_by(order_col.desc() if sort_order == SortOrder.DESC else order_col.asc())

    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    result = await session.execute(stmt)
    items = result.scalars().all()
    total = await session.scalar(select(func.count()).select_from(stmt.subquery()))
    return {"items": items, "total": total, "page": page, "page_size": page_size, "has_next": offset + page_size < total}
```

---

## 13. Versioning Strategy

All API endpoints live under a versioned URL prefix: `/api/v1/`.

- When introducing breaking changes, create a new version directory
  (`v2/`) and a new aggregate router.
- Non-breaking additions (new endpoints, new optional fields) go into the
  current version.
- Deprecate old versions by adding `Sunset` and `Deprecation` headers and
  updating the OpenAPI docs.

```python
# In app.py
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
```

---

## 14. Health Checks

Expose a health check endpoint outside the versioned API.

```python
@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

For readiness checks, verify database connectivity and downstream dependencies.

```python
@router.get("/ready")
async def readiness_check(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    await session.execute(select(1))
    return {"status": "ready"}
```
