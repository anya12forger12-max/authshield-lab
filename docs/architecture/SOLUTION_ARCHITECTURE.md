# Solution Architecture — AuthShield Lab

> Version: 1.0  
> Last Updated: 2026-07-19  
> Status: Current

---

## 1. Architectural Overview

AuthShield Lab follows a **layered Clean Architecture** with explicit dependency direction flowing inward toward the Domain core. Every layer is independently testable, and no layer may reference an outer layer directly. The system is split into **12 architectural layers**, each with strict ownership, allowed dependencies, and lifecycle management.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│              Electron + React + TypeScript UI                   │
├─────────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                            │
│           Use Cases, Command/Query Handlers, DTOs               │
├─────────────────────────────────────────────────────────────────┤
│                      DOMAIN LAYER                               │
│          Entities, Value Objects, Aggregates, Events            │
├──────────────────────┬──────────────────────────────────────────┤
│  INFRASTRUCTURE      │          PERSISTENCE LAYER               │
│  Config, Logging,    │       SQLAlchemy 2.0, SQLite,            │
│  Event Bus, Plugins  │       Migrations, Repositories          │
├──────────────────────┴──────────────────────────────────────────┤
│                    INTEGRATION LAYER                            │
│           External Adapters, IPC Bridge, File I/O               │
├─────────────────────────────────────────────────────────────────┤
│                      PLUGIN LAYER                               │
│           Plugin Loader, Sandboxed Execution, Registry          │
├─────────────────────────────────────────────────────────────────┤
│                       SDK LAYER                                 │
│           Public API Surface, Versioning, Documentation         │
├─────────────────────────────────────────────────────────────────┤
│                    SHARED CORE LAYER                            │
│        Common Types, Utilities, Constants, Error Types          │
├──────────────────────┬──────────────────────────────────────────┤
│   TESTING LAYER      │           TOOLING LAYER                  │
│   Unit, Integration, │      Build Scripts, Linters,             │
│   E2E, Accessibility │      Code Generation, Migration Tools    │
├──────────────────────┴──────────────────────────────────────────┤
│                 DOCUMENTATION LAYER                             │
│          Architecture Docs, API Specs, User Guides              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer Definitions

### 2.1 Presentation Layer

| Attribute | Value |
|---|---|
| **Purpose** | Render UI, capture user input, display data, manage navigation |
| **Ownership** | Frontend team — `src/renderer/`, `src/preload/` |
| **Technologies** | Electron 28+, React 18+, TypeScript 5.3+, Zustand, TailwindCSS |
| **Lifecycle** | Tied to Electron renderer process; mounted/unmounted per route |

**Responsibilities:**
- Render all 20+ module views (auth, users, sessions, audit, policies, etc.)
- Form validation, input sanitization before sending to Application layer
- Manage local UI state via Zustand stores (one per module)
- Handle keyboard navigation, ARIA labels, screen reader announcements
- High contrast mode, reduced motion, font scaling
- Route management and navigation guards
- Toast notifications, modals, dialogs
- Responsive layout adaptation

**Allowed Dependencies:**
- Application Layer (use cases, DTOs)
- Shared Core (types, constants, utility functions)

**Forbidden Dependencies:**
- Domain Layer (never import entities directly)
- Infrastructure Layer (never import database, config, or logging)
- Persistence Layer (never import repositories or models)
- Plugin Layer (indirect only, via SDK)

**Public Interfaces:**
- `React.ComponentType<ModuleProps>` — view components per module
- `ZustandStore<T>` — one store per module
- `ElectronIPC` — preload bridge to invoke backend commands

**Internal Interfaces:**
- `useModuleStore()` — per-module Zustand hooks
- `<AuthProvider>` — context wrapper for auth state
- `<A11yProvider>` — accessibility context

---

### 2.2 Application Layer

| Attribute | Value |
|---|---|
| **Purpose** | Orchestrate business workflows, enforce use-case rules, transform DTOs |
| **Ownership** | Backend team — `src/backend/app/application/` |
| **Technologies** | Python 3.12+, FastAPI dependency injection, Pydantic v2 |
| **Lifecycle** | Per-request; created by FastAPI dependency injection, garbage collected |

**Responsibilities:**
- Define and execute use cases (LoginUser, CreateCourse, GenerateReport, etc.)
- Validate input DTOs via Pydantic models
- Coordinate between Domain services and Infrastructure adapters
- Publish application-level events (user-visible outcomes)
- Enforce transaction boundaries for multi-step operations
- Implement CQRS-lite command and query separation
- Rate limiting, input size validation
- Request/response serialization

**Allowed Dependencies:**
- Domain Layer (entities, value objects, domain services, domain events)
- Shared Core (types, constants, error definitions)
- Persistence Layer (repositories — via interface only, Dependency Inversion)

**Forbidden Dependencies:**
- Presentation Layer (never render or format for display)
- Infrastructure Layer (never import config, logging implementations)
- Plugin Layer (never execute plugin code directly)
- Integration Layer (never import file I/O, IPC)

**Public Interfaces:**
- `UseCaseHandler<CMD, RES>` — command handlers
- `QueryHandler<QRY, RES>` — query handlers
- `ApplicationEventBus` — publish domain events
- Pydantic DTO schemas per module

**Internal Interfaces:**
- `UnitOfWork` — transaction management
- `DomainEventDispatcher` — routes events to subscribers

---

### 2.3 Domain Layer

| Attribute | Value |
|---|---|
| **Purpose** | Core business logic, entity lifecycle, invariants, domain events |
| **Ownership** | Backend team — `src/backend/app/domain/` |
| **Technologies** | Pure Python 3.12+, dataclasses, abc |
| **Lifecycle** | Per aggregate root; managed by Unit of Work pattern |

**Responsibilities:**
- Define entities: User, Session, Course, Assessment, Policy, Rule, etc.
- Define value objects: Email, Password, Token, Permission, etc.
- Define aggregates: UserAggregate, CourseAggregate, PolicyAggregate
- Define domain events: UserCreated, CoursePublished, AssessmentCompleted
- Enforce business invariants (password complexity, permission hierarchies)
- Domain services: TokenGeneration, PasswordHashing, PermissionEvaluation
- Factory methods for complex entity construction
- Specification pattern for complex queries

**Allowed Dependencies:**
- Shared Core (common types, base classes, error definitions)

**Forbidden Dependencies:**
- Presentation Layer
- Application Layer
- Infrastructure Layer
- Persistence Layer
- Integration Layer
- Plugin Layer
- SDK Layer
- Testing Layer
- Tooling Layer
- Documentation Layer

**Public Interfaces:**
- `Entity<T>` — base entity with ID and lifecycle
- `ValueObject<T>` — immutable value type
- `AggregateRoot<T>` — entity with domain event collection
- `DomainEvent` — base event class
- `DomainService` — stateless business logic
- `Repository<T>` — abstract repository interface (Persistence implements)

**Internal Interfaces:**
- `InvariantGuard` — assertion helper for business rules
- `Specification<T>` — composable query predicates

---

### 2.4 Infrastructure Layer

| Attribute | Value |
|---|---|
| **Purpose** | Technical concerns: configuration, logging, event bus, cross-cutting |
| **Ownership** | Backend team — `src/backend/app/infrastructure/` |
| **Technologies** | structlog, pydantic-settings, asyncio event bus |
| **Lifecycle** | Singleton services initialized at startup, destroyed at shutdown |

**Responsibilities:**
- Configuration management (settings, user preferences, environment)
- Structured logging (structlog, JSON output, local file sinks)
- Event bus implementation (async pub/sub within backend)
- Password hashing (bcrypt/argon2 via cryptography layer)
- JWT token generation and validation
- Encryption/decryption for sensitive stored data
- Plugin loading and sandboxed execution environment
- Background task management (asyncio tasks)
- Task scheduling (cron-like for periodic jobs)
- Localization (i18n message catalogs)
- File system abstraction (cross-platform paths)
- Cache management (in-memory, LRU)

**Allowed Dependencies:**
- Domain Layer (only for event types and entity interfaces)
- Shared Core (types, constants, utility functions)

**Forbidden Dependencies:**
- Presentation Layer
- Application Layer
- Persistence Layer
- Integration Layer
- Plugin Layer
- SDK Layer

**Public Interfaces:**
- `ConfigService` — typed configuration access
- `LoggingService` — structured log writer
- `EventBus` — publish/subscribe messaging
- `AuthService` — authentication and token management
- `EncryptionService` — encrypt/decrypt operations
- `PluginManager` — plugin lifecycle management
- `SchedulerService` — task scheduling
- `CacheService` — in-memory caching

**Internal Interfaces:**
- `EventDispatcher` — internal routing
- `TaskRunner` — background execution
- `MiddlewarePipeline` — request/response processing

---

### 2.5 Persistence Layer

| Attribute | Value |
|---|---|
| **Purpose** | Data storage, retrieval, migration, integrity |
| **Ownership** | Backend team — `src/backend/app/persistence/` |
| **Technologies** | SQLAlchemy 2.0 (async), aiosqlite, Alembic |
| **Lifecycle** | Connection pool managed at startup; sessions per-request |

**Responsibilities:**
- SQLAlchemy ORM models mapping to SQLite tables
- Async repository implementations for all Domain repository interfaces
- Database migration scripts (Alembic)
- Schema versioning and rollback support
- Query optimization and indexing
- Data seeding for demo/educational content
- Backup/restore database operations
- Referential integrity enforcement
- Soft delete support for audit trail preservation

**Allowed Dependencies:**
- Domain Layer (entity interfaces, repository interfaces)
- Shared Core (types, utility functions)

**Forbidden Dependencies:**
- Presentation Layer
- Application Layer
- Infrastructure Layer
- Integration Layer
- Plugin Layer
- SDK Layer

**Public Interfaces:**
- `AsyncSession` — SQLAlchemy async session factory
- `BaseRepository<T>` — generic CRUD repository
- `MigrationRunner` — Alembic migration execution
- `DatabaseManager` — connection lifecycle management

**Internal Interfaces:**
- `ModelMapper<T>` — domain entity ↔ ORM model mapping
- `QueryBuilder<T>` — composable query construction

---

### 2.6 Integration Layer

| Attribute | Value |
|---|---|
| **Purpose** | Bridge between backend and Electron, file system, IPC, external formats |
| **Ownership** | Full-stack team — `src/backend/app/integration/`, `src/preload/` |
| **Technologies** | Electron IPC, Node.js fs, JSON, CSV, PDF generation |
| **Lifecycle** | Per IPC session; alive while Electron window is open |

**Responsibilities:**
- Electron IPC bridge (main ↔ renderer communication)
- File system operations (read/write logs, backups, exports)
- Export/import formats (JSON, CSV, PDF)
- Clipboard operations
- System tray integration
- Auto-update checking (offline manifest comparison)
- OS-level notifications
- Path resolution for cross-platform compatibility
- File locking for concurrent access prevention

**Allowed Dependencies:**
- Infrastructure Layer (config, logging)
- Shared Core (types, constants)

**Forbidden Dependencies:**
- Domain Layer
- Application Layer
- Persistence Layer
- Plugin Layer
- SDK Layer
- Presentation Layer

**Public Interfaces:**
- `IPCChannel<T>` — typed IPC message handler
- `FileSystemAdapter` — cross-platform file operations
- `ExportService` — data export in multiple formats
- `ImportService` — data import with validation

**Internal Interfaces:**
- `IPCBridge` — low-level IPC serialization
- `FilePathResolver` — OS-aware path management

---

### 2.7 Plugin Layer

| Attribute | Value |
|---|---|
| **Purpose** | Load, validate, sandbox, and execute third-party plugins |
| **Ownership** | Backend team — `src/backend/app/plugins/` |
| **Technologies** | Python importlib, restricted execution, plugin manifest |
| **Lifecycle** | Per-plugin; loaded at startup, unloaded on demand |

**Responsibilities:**
- Plugin manifest validation (JSON schema)
- Plugin sandboxing (restricted imports, resource limits)
- Plugin lifecycle management (load, enable, disable, unload)
- Plugin API surface exposure via SDK
- Plugin event subscription and publishing
- Plugin configuration management
- Plugin dependency resolution
- Plugin version compatibility checking
- Plugin health monitoring

**Allowed Dependencies:**
- Infrastructure Layer (event bus, config, logging)
- Shared Core (types, constants, error definitions)
- Domain Layer (event types only — read-only)

**Forbidden Dependencies:**
- Application Layer
- Persistence Layer (plugins never access DB directly)
- Presentation Layer
- Integration Layer
- SDK Layer (plugins consume SDK, not vice versa)

**Public Interfaces:**
- `PluginManifest` — plugin metadata schema
- `PluginContext` — sandboxed execution environment
- `PluginRegistry` — installed plugin catalog
- `PluginSDK` — safe API surface for plugins

**Internal Interfaces:**
- `SandboxExecutor` — restricted code execution
- `ManifestValidator` — schema validation
- `DependencyResolver` — plugin dependency graph

---

### 2.8 SDK Layer

| Attribute | Value |
|---|---|
| **Purpose** | Public API surface for plugin authors, stable contract, versioning |
| **Ownership** | Backend team — `src/backend/app/sdk/` |
| **Technologies** | Python, Pydantic schemas, semantic versioning |
| **Lifecycle** | Versioned; each SDK version supported for minimum 2 major releases |

**Responsibilities:**
- Define stable public API for plugin developers
- Version management (semver)
- API deprecation policy and migration guides
- Type-safe SDK interfaces
- SDK documentation generation
- API compatibility testing
- Breaking change detection

**Allowed Dependencies:**
- Domain Layer (entity interfaces, event types — read-only)
- Shared Core (types, constants)

**Forbidden Dependencies:**
- Application Layer
- Infrastructure Layer
- Persistence Layer
- Integration Layer
- Plugin Layer
- Presentation Layer

**Public Interfaces:**
- `SDKv1` — current stable SDK version
- `PluginAPI` — event subscription, command registration
- `QueryBuilder` — safe query construction for plugins
- `Logger` — plugin-scoped logging

**Internal Interfaces:**
- `APIVersionManager` — version routing
- `DeprecationTracker` — tracks deprecated APIs

---

### 2.9 Shared Core Layer

| Attribute | Value |
|---|---|
| **Purpose** | Common types, base classes, utility functions, constants |
| **Ownership** | Cross-cutting — `src/backend/app/core/` |
| **Technologies** | Pure Python 3.12+ |
| **Lifecycle** | Immutable; changes require cross-team review |

**Responsibilities:**
- Base entity classes and ID types
- Common error types and error codes
- Utility functions (string, date, crypto helpers)
- Constants and enumerations
- Result/Either monad for error handling
- Common validation helpers
- Unique ID generation (ULID)
- Time zone handling
- JSON serialization helpers

**Allowed Dependencies:**
- None (leaf layer — zero dependencies on other layers)

**Forbidden Dependencies:**
- Everything except Python standard library

**Public Interfaces:**
- `EntityID` — ULID-based unique identifier
- `Result<T, E>` — success/failure monad
- `ErrorCode` — enumeration of all error codes
- `BaseError` — application error base class
- `Timestamp` — timezone-aware datetime wrapper
- `Slug` — URL-safe identifier value object

**Internal Interfaces:**
- `_internal_helpers` — private utility modules

---

### 2.10 Testing Layer

| Attribute | Value |
|---|---|
| **Purpose** | Test infrastructure, fixtures, factories, test utilities |
| **Ownership** | QA team + feature teams — `tests/` |
| **Technologies** | pytest, pytest-asyncio, httpx, factory_boy, hypothesis |
| **Lifecycle** | Per test session; fixtures scoped appropriately |

**Responsibilities:**
- Unit test suites for all 20+ modules (877 total tests)
- Integration tests for cross-module workflows
- End-to-end tests (Electron + Playwright)
- Accessibility tests (axe-core, manual checklists)
- Security tests (penetration scenarios, fuzzing)
- Performance benchmarks
- Test factories for domain entities
- Mock/fixture management
- Test data seeding
- Code coverage tracking

**Allowed Dependencies:**
- All application layers (for testing purposes only)
- Testing frameworks (pytest, playwright, axe-core)

**Forbidden Dependencies:**
- Must not modify production code behavior

**Public Interfaces:**
- `TestFactory<T>` — entity factory per domain type
- `TestClient` — HTTP test client for FastAPI
- `MockEventBus` — test double for event bus
- `TestDatabase` — isolated SQLite test database

**Internal Interfaces:**
- `FixtureManager` — pytest fixture registration
- `CoverageTracker` — coverage collection

---

### 2.11 Tooling Layer

| Attribute | Value |
|---|---|
| **Purpose** | Build scripts, code generation, linting, migration utilities |
| **Ownership** | DevOps/Platform team — `tools/`, `scripts/` |
| **Technologies** | Python scripts, ruff, mypy, Alembic CLI |
| **Lifecycle** | Versioned with the project; updated per release |

**Responsibilities:**
- Build automation (backend packaging, frontend bundling)
- Code generation (API stubs, type definitions)
- Linting and formatting (ruff, black)
- Type checking (mypy strict mode)
- Architecture validation (custom lint rules)
- Migration script generation and validation
- Release packaging (PyPI-style, Electron builder)
- Dependency auditing
- License compliance checking
- Documentation generation (API docs, architecture diagrams)

**Allowed Dependencies:**
- All application layers (for analysis purposes)
- Build tools (Node.js, Python, Electron builder)

**Forbidden Dependencies:**
- Must not alter runtime behavior of the application

**Public Interfaces:**
- `arch-check` — architecture validation CLI
- `migrate` — database migration runner
- `generate-api` — API stub generator
- `build-release` — release packaging script

**Internal Interfaces:**
- `ASTAnalyzer` — static analysis helpers
- `ConfigLoader` — tool configuration loading

---

### 2.12 Documentation Layer

| Attribute | Value |
|---|---|
| **Purpose** | Architecture docs, API specs, user guides, developer onboarding |
| **Ownership** | Tech writing + engineering — `docs/` |
| **Technologies** | Markdown, Mermaid, OpenAPI 3.1 |
| **Lifecycle** | Updated with every feature; reviewed in PRs |

**Responsibilities:**
- Architecture Decision Records (ADRs)
- API documentation (auto-generated from FastAPI)
- Module documentation per feature
- User guides and tutorials
- Developer onboarding guides
- Deployment guides per topology
- Security guidelines
- Accessibility guidelines
- Changelog and release notes
- Code comments (JSDoc/docstrings for public APIs only)

**Allowed Dependencies:**
- All application layers (for documentation purposes)

**Forbidden Dependencies:**
- Must not affect runtime behavior

**Public Interfaces:**
- `docs/architecture/` — this document tree
- `docs/api/` — OpenAPI specifications
- `docs/guides/` — user and developer guides

**Internal Interfaces:**
- `doc-template` — documentation templates

---

## 3. Layer Interaction Rules

### 3.1 Dependency Direction

Dependencies flow **inward only**. Outer layers may depend on inner layers, but never the reverse.

```
PRESENTATION ──→ APPLICATION ──→ DOMAIN ←── PERSISTENCE
                                    ↑            ↑
                                    │            │
                              INFRASTRUCTURE     │
                                    ↑            │
                                    │            │
                              INTEGRATION ───────┘
                                    ↑
                                    │
                              PLUGIN ──→ SDK ──→ DOMAIN
```

### 3.2 Interaction Patterns

| Pattern | Layers Involved | Description |
|---|---|---|
| Use Case Call | Presentation → Application | Frontend invokes a use case via IPC |
| Dependency Injection | Application → Domain | Application constructs domain objects via interfaces |
| Repository Call | Application → Persistence | Application calls repository through interface (DI) |
| Event Publish | Any → Infrastructure | Domain/application events published to event bus |
| Event Subscribe | Any → Infrastructure | Any layer subscribes to events it cares about |
| Config Read | Any → Infrastructure | Configuration accessed via ConfigService |
| Log Write | Any → Infrastructure | Logging via structured logging service |
| Plugin Call | Plugin → SDK → Domain | Plugins use SDK to interact with domain (read-only) |
| IPC Bridge | Presentation ↔ Integration ↔ Application | Electron IPC bridges renderer and main process |

### 3.3 Communication Protocols

| Protocol | Direction | Use Case |
|---|---|---|
| Synchronous Call | Presentation → Application | User action requiring immediate response |
| Async Event | Domain → Infrastructure → Any | Cross-module notifications |
| IPC Message | Presentation ↔ Application | Electron renderer ↔ main process |
| Database Query | Application → Persistence | Data retrieval and mutation |
| Plugin Event | Plugin → Infrastructure → Domain | Plugin-triggered side effects |

---

## 4. Cross-Cutting Concerns Integration Points

### 4.1 Logging

| Layer | Integration Point | Behavior |
|---|---|---|
| Presentation | IPC call logging | Log user actions at renderer boundary |
| Application | Use case entry/exit | Log use case execution with timing |
| Domain | Domain event emission | Log business events |
| Infrastructure | Log sink management | Write structured logs to local files |
| Persistence | Query logging | Log slow queries (>100ms) |
| Plugin | Plugin activity | Log plugin API calls |
| Integration | IPC bridge | Log IPC messages |

### 4.2 Security

| Layer | Integration Point | Behavior |
|---|---|---|
| Presentation | Input validation | Client-side form validation |
| Application | Authorization check | Permission verification per use case |
| Domain | Invariant enforcement | Password complexity, permission hierarchies |
| Infrastructure | Encryption, hashing | AES-256-GCM at rest, argon2 for passwords |
| Persistence | Data encryption | Sensitive field encryption before storage |
| Plugin | Sandboxing | Resource limits, import restrictions |

### 4.3 Accessibility

| Layer | Integration Point | Behavior |
|---|---|---|
| Presentation | ARIA attributes | All interactive elements labeled |
| Presentation | Keyboard navigation | Tab order, shortcuts, focus management |
| Application | Accessible responses | Structured data for screen readers |
| Documentation | Semantic HTML | Proper heading hierarchy, alt text |

### 4.4 Error Handling

| Layer | Integration Point | Behavior |
|---|---|---|
| Presentation | Error display | Toast notifications, error boundaries |
| Application | Result monad | `Result<T, E>` for all use case returns |
| Domain | Invariant violations | Domain-specific error types |
| Infrastructure | Error logging | Structured error context capture |
| Persistence | Database errors | Transient vs. permanent classification |

---

## 5. Architecture Principles and Constraints

### 5.1 Core Principles

1. **Offline-First**: All functionality works without network. No external API calls at runtime.
2. **Localhost-Only**: All communication is via IPC or localhost. No remote connections.
3. **Educational Focus**: Every feature serves a cybersecurity learning objective.
4. **Clean Architecture**: Strict layering with dependency inversion at boundaries.
5. **Domain-Driven Design**: Business logic in Domain layer; infrastructure is pluggable.
6. **Event-Driven**: Cross-module communication via domain events, not direct calls.
7. **SOLID Compliance**: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion.
8. **Privacy by Design**: No telemetry, no external data transmission, no analytics collection.
9. **Accessibility First**: WCAG 2.2 AA compliance for all user-facing features.
10. **Testability**: Every layer independently testable with 877+ tests.

### 5.2 Technical Constraints

| Constraint | Rationale | Enforcement |
|---|---|---|
| Python 3.12+ | Modern type hints, performance | `pyproject.toml` minimum version |
| SQLAlchemy 2.0 async | Consistent async I/O | Import validation in tooling |
| TypeScript strict mode | Type safety in renderer | `tsconfig.json` strict: true |
| SQLite only | No external database server | No PostgreSQL/MySQL drivers allowed |
| No external network calls | Offline-first requirement | Architecture validation script |
| No secrets in code | Security requirement | Pre-commit hook + secret scanning |
| Max 3-second cold start | User experience | Performance benchmarks in CI |
| A11y tests pass | WCAG 2.2 AA compliance | CI pipeline gate |

### 5.3 Code Organization Constraints

```
src/
├── backend/
│   ├── app/
│   │   ├── core/           # Shared Core Layer
│   │   ├── domain/         # Domain Layer
│   │   ├── application/    # Application Layer
│   │   ├── infrastructure/ # Infrastructure Layer
│   │   ├── persistence/    # Persistence Layer
│   │   ├── integration/    # Integration Layer
│   │   ├── plugins/        # Plugin Layer
│   │   └── sdk/            # SDK Layer
│   └── main.py             # Entry point
├── renderer/               # Presentation Layer
│   ├── components/
│   ├── stores/
│   ├── hooks/
│   └── styles/
├── preload/                # Integration Layer (Electron preload)
└── shared/                 # Shared types between main and renderer
tests/
├── unit/
├── integration/
├── e2e/
├── a11y/
└── security/
tools/                      # Tooling Layer
docs/                       # Documentation Layer
scripts/                    # Build & deploy scripts
```

---

## 6. Versioning Strategy

| Component | Versioning | Breaking Change Policy |
|---|---|---|
| SDK | Semver (1.0.0) | 2-release deprecation window |
| Database Schema | Sequential migration | Backward-compatible migrations only |
| IPC Protocol | Internal version | Updated with Electron version |
| Plugin Manifest | Semver | Strict version matching |
| Architecture Docs | Date-stamped | Reviewed per release |

---

## 7. Quality Gates

| Gate | Threshold | Enforcement |
|---|---|---|
| Unit test coverage | ≥ 85% | CI pipeline |
| Integration test coverage | ≥ 70% | CI pipeline |
| Architecture violations | 0 critical | `arch-check` tool |
| Type errors (mypy) | 0 | CI pipeline |
| Lint errors (ruff) | 0 | CI pipeline |
| A11y violations | 0 critical | axe-core + manual |
| Performance (cold start) | ≤ 3s | Benchmark suite |
| Bundle size | ≤ 50MB | Build check |
