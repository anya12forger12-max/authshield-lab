# Architectural Boundaries — AuthShield Lab

> Version: 1.0  
> Last Updated: 2026-07-19  
> Status: Current

---

## 1. Overview

Architectural boundaries enforce the separation of concerns that makes AuthShield Lab maintainable, testable, and extensible. Each boundary is a strict contract: what may cross, what is forbidden, and how violations are detected.

---

## 2. Application Boundary

### 2.1 What Crosses

| From | To | What Crosses |
|---|---|---|
| Presentation → Application | IPC messages, serialized commands/queries |
| Application → Domain | Entity instances, value objects, domain events |
| Application → Persistence | Repository interface calls (Dependency Inversion) |
| Application → Infrastructure | Config reads, log writes, event publishes |
| Application → Integration | Export/import requests (via interface) |

### 2.2 What is Forbidden

| Forbidden Crossing | Rationale |
|---|---|
| Presentation → Domain | Presentation must not know about domain entities |
| Presentation → Persistence | Presentation must not access database directly |
| Domain → Application | Domain must not depend on use case orchestration |
| Domain → Infrastructure | Domain must not know about config, logging, or event bus |
| Domain → Persistence | Domain must not know about SQL or ORM |
| Persistence → Application | Repository must not call use case handlers |
| Infrastructure → Domain | Infrastructure must not define business rules |

### 2.3 Enforcement Rules

- **Compile-time**: mypy strict mode enforces import restrictions
- **Architecture lint**: Custom ruff rules check import graph
- **PR review**: Architecture boundary violations require explicit justification
- **Runtime**: No enforcement (relying on compile-time and review)

---

## 3. Domain Boundary

### 3.1 What Crosses

| From | To | What Crosses |
|---|---|---|
| Domain → Shared Core | Base classes, common types, error definitions |

### 3.2 What is Forbidden

| Forbidden Crossing | Rationale |
|---|---|
| Domain → Application | Domain entities must not call use cases |
| Domain → Infrastructure | Domain must not use config, logging, or event bus |
| Domain → Persistence | Domain must not import ORM models or execute SQL |
| Domain → Integration | Domain must not do file I/O or IPC |
| Domain → Plugin | Domain must not know about plugins |
| Domain → SDK | Domain must not depend on plugin API |
| Domain → Presentation | Domain must not render or format for display |
| Domain → Testing | Domain must not import test utilities |
| Domain → Tooling | Domain must not depend on build scripts |
| Domain → Documentation | Domain must not depend on doc generation |

### 3.3 Domain Purity Rules

1. **No side effects in domain logic** — Domain methods return events; side effects happen in Application layer
2. **No external dependencies** — Domain uses only Python stdlib + shared core
3. **Immutable value objects** — Value objects are frozen dataclasses
4. **No ORM leaks** — Domain entities are not SQLAlchemy models
5. **No HTTP awareness** — Domain knows nothing about REST, JSON, or HTTP

### 3.4 Enforcement Rules

- **Import check**: `arch-check` tool scans for forbidden imports
- **CI gate**: Build fails on domain boundary violation
- **Test**: Domain tests must run without any infrastructure fixtures

---

## 4. Infrastructure Boundary

### 4.1 What Crosses

| From | To | What Crosses |
|---|---|---|
| Infrastructure → Domain | Event type definitions (read-only) |
| Infrastructure → Shared Core | Base classes, utility functions |

### 4.2 What is Forbidden

| Forbidden Crossing | Rationale |
|---|---|
| Infrastructure → Application | Infrastructure must not orchestrate use cases |
| Infrastructure → Persistence | Infrastructure must not execute queries |
| Infrastructure → Presentation | Infrastructure must not render UI |
| Infrastructure → Integration | Infrastructure must not do file I/O directly |
| Infrastructure → Plugin | Infrastructure must not manage plugin lifecycle |
| Infrastructure → SDK | Infrastructure must not depend on plugin API |

### 4.3 Infrastructure Service Contracts

| Service | Contract | Implementation |
|---|---|---|
| ConfigService | `get(key: str) → T` | `pydantic-settings` |
| LoggingService | `log(level, event, **kw)` | `structlog` |
| EventBus | `publish(event)` / `subscribe(topic, handler)` | In-memory async |
| AuthService | `generate_token(user_id) → Token` | `python-jose` |
| EncryptionService | `encrypt(data) → bytes` / `decrypt(bytes) → data` | `cryptography` |
| CacheService | `get(key)` / `set(key, value, ttl)` | LRU dict |
| SchedulerService | `schedule(task, interval)` / `cancel(task_id)` | `asyncio` |

### 4.4 Enforcement Rules

- **Interface segregation**: Each infrastructure service has a thin interface
- **Dependency injection**: Services injected via FastAPI DI, not imported directly
- **Configuration**: All infrastructure services configurable at startup

---

## 5. Plugin Boundary

### 5.1 What Crosses

| From | To | What Crosses |
|---|---|---|
| Plugin → SDK | Event publishing, data queries, config reads, logging |
| Core → Plugin | Event notifications, config change notifications, shutdown signals |

### 5.2 What is Forbidden

| Forbidden Crossing | Rationale |
|---|---|
| Plugin → Domain | Plugins must not import domain entities directly |
| Plugin → Persistence | Plugins must not access database |
| Plugin → Infrastructure | Plugins must not use internal infrastructure services |
| Plugin → Application | Plugins must not call use case handlers |
| Plugin → Integration | Plugins must not do file I/O outside sandbox |
| Plugin → Presentation | Plugins must not render UI directly |

### 5.3 Plugin Sandbox Rules

| Rule | Enforcement |
|---|---|
| No `os` module import | Import hook blocks restricted modules |
| No `socket` module import | Import hook blocks network access |
| No `subprocess` module import | Import hook blocks process spawning |
| No `ctypes` module import | Import hook blocks native code |
| No `importlib` import | Prevents plugin from loading plugins |
| Max 64MB memory | Resource monitor enforces limit |
| Max 100ms per handler | asyncio.wait_for timeout |
| Max 100 messages/sec | Token bucket rate limiter |
| Max 1MB message size | Pre-validation |
| File I/O restricted to plugin dir | Filesystem sandbox |

### 5.4 Enforcement Rules

- **Manifest validation**: Plugin manifest checked against JSON schema
- **Import hook**: Custom finder blocks restricted module imports
- **Resource monitoring**: Background task checks resource usage
- **Timeout enforcement**: All plugin calls wrapped in `asyncio.wait_for`
- **Logging**: All plugin API calls logged for audit trail

---

## 6. SDK Boundary

### 6.1 What Crosses

| From | To | What Crosses |
|---|---|---|
| SDK → Domain | Entity type definitions (read-only, frozen) |
| SDK → Shared Core | Base types, error definitions |
| Plugin → SDK | All plugin-to-core communication |

### 6.2 What is Forbidden

| Forbidden Crossing | Rationale |
|---|---|
| SDK → Application | SDK must not call use cases |
| SDK → Infrastructure | SDK must not use internal services |
| SDK → Persistence | SDK must not access database |
| SDK → Integration | SDK must not do file I/O |
| SDK → Presentation | SDK must not render UI |
| SDK → Plugin | SDK must not import plugin code |
| SDK → Testing | SDK must not import test utilities |

### 6.3 SDK Stability Rules

| Rule | Description |
|---|---|
| Semantic versioning | Major.Minor.Patch format |
| Deprecation window | 2 major versions minimum |
| No breaking changes | Without major version bump |
| API surface review | All public API changes require review |
| Backward compatibility | New versions must work with old plugins |
| Type stability | Public types must not change shape |

### 6.4 Enforcement Rules

- **API surface test**: Automated test ensures only public API is exposed
- **Compatibility test**: Old plugin code must work with new SDK
- **Breaking change detection**: Tool checks for removed/renamed APIs
- **Version check**: Plugin manifest declares SDK version, validated at load

---

## 7. Persistence Boundary

### 7.1 What Crosses

| From | To | What Crosses |
|---|---|---|
| Persistence → Domain | Repository interface implementations |
| Domain → Persistence | Repository interface definitions (Dependency Inversion) |

### 7.2 What is Forbidden

| Forbidden Crossing | Rationale |
|---|---|
| Persistence → Application | Repository must not call use cases |
| Persistence → Infrastructure | Repository must not use config or logging directly |
| Persistence → Presentation | Repository must not render or format |
| Persistence → Integration | Repository must not do file I/O |
| Persistence → Plugin | Repository must not manage plugins |

### 7.3 Persistence Rules

| Rule | Description |
|---|---|
| Repository pattern | All data access through repository interfaces |
| Unit of Work | Multi-table operations wrapped in UoW |
| Async only | All DB operations are async (aiosqlite) |
| No raw SQL in handlers | Use SQLAlchemy ORM or query builder |
| Transaction boundaries | Each request is one transaction |
| Soft delete | Never hard-delete audit-relevant data |
| Encryption | Sensitive fields encrypted before storage |

### 7.4 Repository Interface Contract

```python
class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: EntityID) -> User | None: ...
    
    @abstractmethod
    async def find_by_email(self, email: Email) -> User | None: ...
    
    @abstractmethod
    async def save(self, user: User) -> None: ...
    
    @abstractmethod
    async def delete(self, user_id: EntityID) -> None: ...
```

### 7.5 Enforcement Rules

- **Interface-only imports**: Application layer imports `UserRepository` (abstract), not `SQLAlchemyUserRepository` (concrete)
- **DI wiring**: FastAPI dependency injection binds concrete to abstract
- **Migration testing**: All migrations tested for forward/backward compatibility

---

## 8. Presentation Boundary

### 8.1 What Crosses

| From | To | What Crosses |
|---|---|---|
| Presentation → Application | Serialized commands/queries via IPC |
| Application → Presentation | Serialized responses via IPC |

### 8.2 What is Forbidden

| Forbidden Crossing | Rationale |
|---|---|
| Presentation → Domain | Presentation must not import domain entities |
| Presentation → Infrastructure | Presentation must not import config, logging, event bus |
| Presentation → Persistence | Presentation must not import repositories or models |
| Presentation → Integration | Presentation must not do file I/O directly |
| Presentation → Plugin | Presentation must not import plugin code |
| Presentation → SDK | Presentation must not import SDK |
| Backend → Presentation | Backend must not import React components |

### 8.3 Presentation Rules

| Rule | Description |
|---|---|
| IPC only | All backend communication via Electron IPC |
| Zustand stores | One store per module, no prop drilling |
| No business logic | Business logic lives in Application/Domain layers |
| Controlled forms | All forms use controlled components |
| Error boundaries | React error boundary catches render errors |
| Accessibility first | All components meet WCAG 2.2 AA |
| Keyboard navigation | All workflows keyboard-accessible |
| ARIA labels | All interactive elements labeled |

### 8.4 Enforcement Rules

- **Import check**: Frontend linter forbids backend imports
- **TypeScript strict**: Catches type errors at compile time
- **ESLint rules**: Custom rules enforce IPC-only communication
- **A11y tests**: axe-core runs on every component

---

## 9. Testing Boundary

### 9.1 What Crosses

| From | To | What Crosses |
|---|---|---|
| Testing → All Layers | Test code imports from all production layers |

### 9.2 What is Forbidden

| Forbidden Crossing | Rationale |
|---|---|
| Production → Testing | Production code must not import test utilities |
| Testing → Production behavior change | Tests must not modify production code behavior |

### 9.3 Testing Rules

| Rule | Description |
|---|---|
| Isolated test DB | Each test suite gets its own SQLite database |
| Factory pattern | Test data created via factories, not fixtures |
| No shared state | Tests must not depend on execution order |
| Mock external | Infrastructure mocked in unit tests |
| Real DB in integration | Integration tests use real SQLite |
| No test pollution | Tests clean up after themselves |

### 9.4 Test Category Boundaries

| Category | Scope | Speed | Dependencies |
|---|---|---|---|
| Unit | Single module/function | < 100ms | Mocks only |
| Integration | Cross-module | < 1s | Real SQLite |
| E2E | Full user journey | < 30s | Electron + DB |
| A11y | Component accessibility | < 5s | axe-core |
| Security | Penetration scenarios | < 10s | Real DB |
| Architecture | Import graph validation | < 1s | Static analysis |

---

## 10. Cross-Cutting Boundary Rules

### 10.1 Event Bus Boundary

| Rule | Description |
|---|---|
| Topic-based routing | Events routed by topic, not by type |
| Handler isolation | Handler failure does not affect other handlers |
| At-least-once delivery | Handlers must be idempotent |
| Event ordering | Ordered within aggregate, not across |
| Dead letter queue | Failed events stored for inspection |

### 10.2 Configuration Boundary

| Rule | Description |
|---|---|
| Read-only at runtime | Config loaded at startup, immutable |
| Layered resolution | Defaults → user → env → runtime |
| No secrets in config files | Sensitive values encrypted separately |
| Schema validation | All config validated against Pydantic schema |
| Change notification | Config changes published as events |

### 10.3 Logging Boundary

| Rule | Description |
|---|---|
| Never log secrets | Passwords, tokens, PII sanitized |
| Structured only | All logs are key-value structured |
| No sensitive data in metadata | Request bodies, headers sanitized |
| Log level enforcement | Production: INFO minimum |
| Audit trail integrity | Audit logs append-only, checksummed |

---

## 11. Boundary Violation Severity

| Severity | Definition | Example | Response |
|---|---|---|---|
| **Critical** | Security boundary breach | Plugin accessing database | Immediate fix, release blocker |
| **High** | Architecture rule violation | Domain importing infrastructure | Fix before merge |
| **Medium** | Boundary soft violation | Presentation importing shared core | Fix in next sprint |
| **Low** | Naming convention violation | Module using wrong naming pattern | Fix opportunistically |

---

## 12. Boundary Diagram Summary

```
                    ┌─────────────────────────────────┐
                    │       PRESENTATION BOUNDARY      │
                    │  ┌─────────────────────────────┐ │
                    │  │    APPLICATION BOUNDARY      │ │
                    │  │  ┌─────────────────────────┐ │ │
                    │  │  │    DOMAIN BOUNDARY       │ │ │
                    │  │  │  ┌─────────────────────┐ │ │ │
                    │  │  │  │  SHARED CORE         │ │ │ │
                    │  │  │  │  (no deps)           │ │ │ │
                    │  │  │  └─────────────────────┘ │ │ │
                    │  │  │                           │ │ │
                    │  │  │  Domain ↔ Core            │ │ │
                    │  │  └─────────────────────────┘ │ │
                    │  │                               │ │
                    │  │  App → Domain, Core           │ │
                    │  │  App → Persistence (inv)      │ │
                    │  └─────────────────────────────┘ │
                    │                                   │
                    │  Pres → App (IPC only)            │
                    │  Pres → Core (types only)         │
                    └─────────────────────────────────┘

     ┌──────────────────┐     ┌──────────────────┐
     │  PLUGIN BOUNDARY │     │  SDK BOUNDARY    │
     │  ┌──────────────┐│     │  ┌──────────────┐│
     │  │  Plugin Code  ││     │  │  SDK Surface  ││
     │  │  (sandboxed)  ││     │  │  (stable API) ││
     │  └──────┬───────┘│     │  └──────┬───────┘│
     │         │         │     │         │         │
     │    Plugin → SDK   │     │    SDK → Domain   │
     └──────────────────┘     └──────────────────┘

     ┌──────────────────┐     ┌──────────────────┐
     │  PERSISTENCE     │     │  INFRASTRUCTURE  │
     │  BOUNDARY        │     │  BOUNDARY        │
     │  ┌──────────────┐│     │  ┌──────────────┐│
     │  │  Repositories ││     │  │  Services     ││
     │  │  (async CRUD) ││     │  │  (config,log) ││
     │  └──────┬───────┘│     │  └──────┬───────┘│
     │         │         │     │         │         │
     │  Persistence →    │     │  Infra → Domain   │
     │  Domain (inv)     │     │  (read-only)      │
     └──────────────────┘     └──────────────────┘
```
