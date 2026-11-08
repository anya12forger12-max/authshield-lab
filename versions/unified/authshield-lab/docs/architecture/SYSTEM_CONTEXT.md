# System Context — AuthShield Lab

> Version: 1.0  
> Last Updated: 2026-07-19  
> Status: Current

---

## 1. System Context Overview

AuthShield Lab operates as a **self-contained desktop application** running entirely on localhost. There are no external service dependencies, no cloud connections, and no remote APIs. All data, logic, and state persist locally on the user's machine.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LOCALHOST BOUNDARY                               │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                     DESKTOP APPLICATION                           │  │
│  │                  Electron + FastAPI + SQLite                      │  │
│  │                                                                   │  │
│  │  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │ Renderer │  │  Main   │  │ Backend  │  │  Database Engine  │  │  │
│  │  │ (React)  │◄►│ Process │◄►│(FastAPI) │◄►│  (SQLite async)  │  │  │
│  │  └─────────┘  └─────────┘  └──────────┘  └──────────────────┘  │  │
│  │       │            │             │                │               │  │
│  │       ▼            ▼             ▼                ▼               │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │                    LOCAL FILE SYSTEM                         │ │  │
│  │  │  ├── app.db          (SQLite database)                      │ │  │
│  │  │  ├── backups/        (automated backups)                     │ │  │
│  │  │  ├── logs/           (structured logs)                      │ │  │
│  │  │  ├── plugins/        (installed plugins)                    │ │  │
│  │  │  ├── config/         (configuration files)                  │ │  │
│  │  │  └── exports/        (user exports)                         │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ╔═══════════════════════════════════════════════════════════════════╗  │
│  ║              EXTERNAL SYSTEM BOUNDARY (NONE)                      ║  │
│  ║   All communication is local. No network sockets. No HTTP         ║  │
│  ║   clients. No WebSocket connections. No external APIs.            ║  │
│  ╚═══════════════════════════════════════════════════════════════════╝  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Inventory

### 2.1 Desktop Application

| Attribute | Detail |
|---|---|
| **Type** | Electron shell (Chromium + Node.js) |
| **Processes** | Main process, Renderer process, Preload script |
| **Location** | `src/renderer/`, `src/main/`, `src/preload/` |
| **Lifecycle** | User launches app → Electron starts → FastAPI backend boots → UI renders |

**Responsibilities:**
- Host the React-based user interface in a Chromium webview
- Manage application lifecycle (startup, suspend, shutdown)
- Provide native OS integration (menus, tray, notifications)
- Bridge renderer ↔ main process via IPC (contextBridge)
- Enforce single-instance lock (prevent multiple app instances)
- Handle application updates (offline manifest comparison)

**Internal Components:**
- `ElectronMain` — process manager, window lifecycle
- `ElectronRenderer` — React application host
- `PreloadBridge` — contextBridge API exposure
- `NativeMenu` — application menu definitions
- `TrayManager` — system tray icon and menu

---

### 2.2 Local Database

| Attribute | Detail |
|---|---|
| **Type** | SQLite 3 (WAL mode, async via aiosqlite) |
| **Location** | `{app_data}/app.db` |
| **Size Limit** | Recommended ≤ 2GB; soft limit enforced |
| **Backup** | Automated daily + on-demand |

**Responsibilities:**
- Store all application data persistently (users, courses, sessions, audit logs)
- Enforce referential integrity via foreign keys
- Support concurrent reads (WAL mode allows this)
- Handle migrations via Alembic
- Provide atomic transactions for multi-step operations
- Encrypt sensitive columns (passwords, tokens, personal data)

**Schema Domains:**
| Domain | Tables | Description |
|---|---|---|
| Auth | `users`, `credentials`, `tokens` | Authentication and identity |
| Sessions | `sessions`, `session_events` | User session tracking |
| Audit | `audit_logs`, `security_events` | Audit trail |
| Courses | `courses`, `modules`, `lessons` | Educational content |
| Assessments | `assessments`, `attempts`, `scores` | Learning evaluation |
| Policies | `policies`, `rules`, `exceptions` | Security policies |
| Analytics | `metrics`, `aggregates` | Usage analytics |
| Plugins | `installed_plugins`, `plugin_configs` | Plugin registry |
| Config | `settings`, `user_preferences` | Configuration state |

---

### 2.3 Plugin Engine

| Attribute | Detail |
|---|---|
| **Type** | Python importlib-based sandboxed loader |
| **Location** | `src/backend/app/plugins/` |
| **Sandbox** | Restricted imports, resource limits, timeout enforcement |
| **API Surface** | SDK v1 (stable, versioned) |

**Responsibilities:**
- Load plugins from `plugins/` directory at startup
- Validate plugin manifests against JSON schema
- Enforce sandbox restrictions (no network, no filesystem outside sandbox)
- Manage plugin lifecycle (load → enable → disable → unload)
- Route events between plugins and core system
- Track plugin resource usage (CPU time, memory)
- Handle plugin errors without crashing the host

**Trust Model:**
- Plugins run in a restricted Python namespace
- No access to `os`, `socket`, `subprocess`, `ctypes` modules
- File I/O restricted to plugin's own directory
- CPU time limited to 100ms per event handler
- Memory limited to 64MB per plugin instance

---

### 2.4 SDK

| Attribute | Detail |
|---|---|
| **Type** | Python package with stable public API |
| **Location** | `src/backend/app/sdk/` |
| **Current Version** | 1.0.0 |
| **Deprecation Policy** | 2-release support window |

**Responsibilities:**
- Provide stable API surface for plugin developers
- Define event types plugins can subscribe to
- Provide safe query builders for data access
- Expose logging, configuration, and UI extension points
- Version management and compatibility checking
- API documentation generation

**Public API Surface:**
| Module | Description |
|---|---|
| `authshield_sdk.events` | Event subscription and publishing |
| `authshield_sdk.queries` | Read-only data access |
| `authshield_sdk.config` | Plugin configuration access |
| `authshield_sdk.logging` | Plugin-scoped logging |
| `authshield_sdk.ui` | UI extension point registration |
| `authshield_sdk.types` | Shared type definitions |

---

### 2.5 Configuration System

| Attribute | Detail |
|---|---|
| **Type** | Layered config (defaults → user → environment → runtime) |
| **Location** | `config/settings.json`, `config/user_preferences.json` |
| **Format** | JSON with Pydantic validation |
| **Encryption** | Sensitive values encrypted at rest |

**Responsibilities:**
- Load and validate application settings at startup
- Support user preferences (theme, font size, language, notifications)
- Environment-specific overrides (development, testing, production)
- Runtime configuration changes without restart (where possible)
- Configuration export/import
- Secure storage of sensitive settings (encryption keys, credentials)
- Schema validation on load and save
- Default value fallback chain

**Configuration Layers:**
```
┌─────────────────────────┐
│    Runtime Overrides     │  ← Highest priority
├─────────────────────────┤
│   Environment Variables  │
├─────────────────────────┤
│  User Preferences        │
├─────────────────────────┤
│  Application Settings    │
├─────────────────────────┤
│    Built-in Defaults     │  ← Lowest priority
└─────────────────────────┘
```

---

### 2.6 Logging System

| Attribute | Detail |
|---|---|
| **Type** | Structured logging (structlog) |
| **Output** | Local JSON files, rotating, compressed |
| **Location** | `logs/` directory |
| **Retention** | 30 days default, configurable |

**Responsibilities:**
- Capture structured log events from all layers
- Include context (request ID, user ID, module, timestamp)
- Support multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Rotate logs daily, compress archives
- Sanitize sensitive data (passwords, tokens, PII)
- Provide log query capability (by date, level, module)
- Export logs for diagnostic purposes
- Performance logging (request timing, query duration)

**Log Structure:**
```json
{
  "timestamp": "2026-07-19T10:30:00.000Z",
  "level": "info",
  "module": "authentication",
  "event": "login_success",
  "user_id": "01J2...",
  "request_id": "req_abc",
  "duration_ms": 145,
  "context": {"method": "password", "mfa": false}
}
```

---

### 2.7 Reporting Engine

| Attribute | Detail |
|---|---|
| **Type** | Data aggregation and export |
| **Location** | `src/backend/app/application/reporting/` |
| **Formats** | PDF, CSV, JSON, HTML |

**Responsibilities:**
- Generate learning progress reports
- Create security assessment summaries
- Build audit trail exports
- Produce analytics dashboards data
- Support date range filtering
- Support module-specific filtering
- Export in multiple formats
- Include accessibility-compliant table structures
- Cache generated reports for performance

**Report Types:**
| Report | Description | Format |
|---|---|---|
| User Progress | Course completion, scores, time spent | PDF, HTML |
| Security Audit | Authentication attempts, policy violations | CSV, JSON |
| Assessment Results | Pass/fail rates, score distributions | PDF, CSV |
| Plugin Activity | Plugin usage, errors, resource consumption | JSON, CSV |
| System Health | Performance metrics, error rates | HTML, JSON |

---

### 2.8 Backup System

| Attribute | Detail |
|---|---|
| **Type** | SQLite backup API + file copy |
| **Location** | `backups/` directory |
| **Strategy** | Daily automated + on-demand + pre-migration |

**Responsibilities:**
- Automated daily backups at configurable time
- Pre-migration automatic backup (before schema changes)
- On-demand manual backup trigger
- Backup integrity verification (checksum)
- Backup rotation (keep last N backups, configurable)
- Export/import backup for data portability
- Backup size monitoring
- Restore capability (full restore from backup)
- Backup encryption (optional, using app encryption key)

**Backup Metadata:**
```json
{
  "backup_id": "bak_01J2...",
  "timestamp": "2026-07-19T02:00:00Z",
  "size_bytes": 52428800,
  "checksum_sha256": "abc123...",
  "schema_version": 42,
  "type": "automated",
  "encrypted": true,
  "contents": {
    "tables": ["users", "courses", "audit_logs", ...],
    "row_counts": {"users": 15, "courses": 8, ...}
  }
}
```

---

### 2.9 Package Manager

| Attribute | Detail |
|---|---|
| **Type** | Plugin installation and dependency resolution |
| **Location** | `src/backend/app/plugins/package_manager.py` |
| **Storage** | `plugins/` directory, `installed_plugins` DB table |

**Responsibilities:**
- Install plugins from local `.asplugin` packages
- Resolve plugin dependencies
- Version compatibility checking
- Plugin updates (offline manifest comparison)
- Plugin uninstallation (cleanup files and DB records)
- Plugin search (local catalog)
- Dependency conflict detection
- Rollback on failed installation

---

### 2.10 Documentation System

| Attribute | Detail |
|---|---|
| **Type** | Markdown-based, searchable, offline |
| **Location** | `docs/` directory, rendered in-app |
| **Format** | Markdown, Mermaid diagrams |

**Responsibilities:**
- In-app documentation viewer (renderer component)
- Full-text search across all documentation
- Architecture documentation (this document tree)
- API reference (auto-generated from FastAPI/OpenAPI)
- User guides and tutorials
- Developer onboarding guides
- Contextual help (per-module help panels)
- Documentation versioning (matches app version)
- Print-friendly formatting

---

### 2.11 Testing Framework

| Attribute | Detail |
|---|---|
| **Type** | pytest + Playwright + axe-core |
| **Tests** | 877 total (unit, integration, E2E, a11y, security) |
| **Coverage** | ≥ 85% unit, ≥ 70% integration |

**Responsibilities:**
- Unit testing for all domain entities and services
- Integration testing for cross-module workflows
- E2E testing for complete user journeys
- Accessibility testing (automated axe-core + manual)
- Security testing (penetration scenarios, injection)
- Performance benchmarking
- Architecture compliance testing
- Test data management
- CI/CD integration

---

### 2.12 CI/CD Tooling

| Attribute | Detail |
|---|---|
| **Type** | Local build automation (no external CI service) |
| **Location** | `scripts/`, `tools/`, `.github/workflows/` (optional) |
| **Triggers** | Manual, pre-commit hooks, release scripts |

**Responsibilities:**
- Automated test execution
- Code quality checks (linting, type checking)
- Architecture compliance validation
- Build artifact creation
- Release packaging (Electron + Python)
- Documentation generation
- Security scanning (dependency audit)
- Version bumping and changelog generation

---

### 2.13 Release Tools

| Attribute | Detail |
|---|---|
| **Type** | Release automation |
| **Location** | `scripts/release/` |

**Responsibilities:**
- Semantic version management
- Changelog generation from commit history
- Git tag creation
- Build artifact generation (Electron installer, Python package)
- Release notes drafting
- Offline update manifest generation
- Release verification (smoke tests)
- Rollback documentation

---

### 2.14 Administration Tools

| Attribute | Detail |
|---|---|
| **Type** | Admin CLI + UI panels |
| **Location** | `src/backend/app/admin/`, renderer admin views |

**Responsibilities:**
- User management (create, deactivate, reset)
- System configuration (admin-only settings)
- Database maintenance (vacuum, integrity check)
- Plugin management (install, enable, disable, remove)
- Backup management (trigger, restore, list)
- Audit log review and export
- System health monitoring
- License and version management
- User role assignment (RBAC)

---

## 3. Trust Boundaries

### 3.1 Trust Boundary Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ TRUST BOUNDARY 1: Operating System                              │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ TRUST BOUNDARY 2: Electron Application                      │ │
│ │                                                             │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ TRUST BOUNDARY 3: Backend Process                       │ │ │
│ │ │                                                         │ │ │
│ │ │ ┌─────────────────────────────────────────────────────┐ │ │ │
│ │ │ │ TRUST BOUNDARY 4: Database                          │ │ │ │
│ │ │ │  - SQLite file with encryption                      │ │ │ │
│ │ │ │  - Access only via repository layer                 │ │ │ │
│ │ │ └─────────────────────────────────────────────────────┘ │ │ │
│ │ │                                                         │ │ │
│ │ │ ┌─────────────────────────────────────────────────────┐ │ │ │
│ │ │ │ TRUST BOUNDARY 5: Plugin Sandbox                    │ │ │ │
│ │ │ │  - Restricted Python namespace                      │ │ │ │
│ │ │ │  - No direct DB access                              │ │ │ │
│ │ │ │  - Resource limits enforced                         │ │ │ │
│ │ │ └─────────────────────────────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ │                                                             │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ TRUST BOUNDARY 6: Renderer Process                     │ │ │
│ │ │  - Isolated Chromium process                           │ │ │
│ │ │  - No direct filesystem access                         │ │ │
│ │ │  - No Node.js APIs (via contextIsolation)              │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Boundary Rules

| Boundary | Crossing Mechanism | Enforcement |
|---|---|---|
| OS → Electron | Process creation | Electron sandboxing |
| Electron → Backend | IPC (contextBridge) | Typed API surface only |
| Backend → Database | SQLAlchemy async | Repository pattern |
| Backend → Plugin | SDK interface | Sandboxed importlib |
| Renderer → Backend | IPC messages | Preload bridge validation |
| Plugin → Backend | SDK events/queries | Resource limits, time limits |

### 3.3 Trust Levels

| Trust Level | Components | Permissions |
|---|---|---|
| **High** | Domain Layer, Core | Full read/write to all business data |
| **Medium** | Application Layer, Infrastructure | Execute business logic, access config |
| **Low** | Plugin Layer | Read-only data access, event subscription |
| **Minimal** | Renderer | Display data, capture input, no direct data access |
| **Untrusted** | User Input | Sanitized before processing |

---

## 4. Data Flow Between Components

### 4.1 Login Flow

```
User Input → Renderer → IPC Bridge → Application → Domain → Infrastructure → Persistence
    │                              │                              │
    │                              │                              ▼
    │                              │                        SQLite (encrypted)
    │                              │
    │                              ▼
    │                        Response DTO
    │
    ▼
  UI Update (session stored, redirect)
```

### 4.2 Course Content Load

```
Navigation → Renderer → IPC → Application → Domain (CourseService)
                                            │
                                            ▼
                                      Persistence (query)
                                            │
                                            ▼
                                      Domain (instantiate CourseAggregate)
                                            │
                                            ▼
                                      Application (format DTO)
                                            │
                                            ▼
                                      IPC Response → Renderer (render)
```

### 4.3 Plugin Event Flow

```
Plugin publishes event → Plugin Layer → SDK EventBridge → Infrastructure (EventBus)
    │
    ▼
Event Bus routes to subscribers:
    ├── Domain handlers (business logic)
    ├── Application handlers (use case triggers)
    ├── Infrastructure handlers (logging, metrics)
    └── Other plugins (cross-plugin communication)
```

### 4.4 Backup Flow

```
Scheduled/Manual → Infrastructure (SchedulerService)
    │
    ▼
Persistence Layer (SQLite backup API)
    │
    ▼
Integration Layer (file copy to backups/)
    │
    ▼
Infrastructure (checksum generation, metadata)
    │
    ▼
Persistence (backup metadata storage)
    │
    ▼
Logging (backup event logged)
```

### 4.5 Export Flow

```
User Request → Renderer → IPC → Application (ExportUseCase)
    │
    ▼
Domain (data assembly, formatting rules)
    │
    ▼
Persistence (data retrieval)
    │
    ▼
Application (format transformation: PDF/CSV/JSON)
    │
    ▼
Integration Layer (file system write)
    │
    ▼
Renderer (download notification, file path)
```

---

## 5. Component Interaction Matrix

| Component | Desktop App | Database | Plugin Engine | SDK | Config | Logging | Reporting | Backup | Package Mgr | Docs | Testing | CI/CD | Release | Admin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Desktop App** | — | R/W | R | R | R | W | R | R/W | R | R | R | R | R | R |
| **Database** | — | — | — | — | — | — | — | — | R | — | R | — | — | — |
| **Plugin Engine** | — | — | — | R | R | W | — | — | R | — | — | — | — | — |
| **SDK** | — | — | — | — | R | W | — | — | — | — | — | — | — | — |
| **Config** | R | R | — | — | — | R | — | — | — | — | — | — | — | R |
| **Logging** | — | W | — | — | R | — | — | — | — | — | — | — | — | — |
| **Reporting** | — | R | — | — | R | R | — | — | — | — | — | — | — | — |
| **Backup** | — | R/W | — | — | — | W | — | — | — | — | — | — | — | — |
| **Package Mgr** | — | R | R/W | R | — | W | — | R | — | — | — | — | — | — |
| **Docs** | R | — | R | R | R | — | — | — | — | — | — | — | — | — |
| **Testing** | R | R/W | R | R | R | R | R | R | R | R | — | R | R | R |
| **CI/CD** | R | R | R | R | R | R | R | R | R | R | R | — | R | R |
| **Release** | R | — | R | R | — | — | R | R | R | R | R | R | — | — |
| **Admin** | R | R/W | R/W | — | R/W | R | R | R/W | R/W | R | — | — | — | — |

**Legend:** R = Read, W = Write, R/W = Read/Write, — = No interaction

---

## 6. External System Boundary

### 6.1 No External Dependencies

AuthShield Lab deliberately has **zero external system dependencies**:

| Concern | Approach |
|---|---|
| Authentication | Local credential store, no OAuth/SSO |
| Data Storage | SQLite file, no cloud database |
| Updates | Offline manifest comparison, manual download |
| Telemetry | None — zero data transmission |
| Analytics | Local aggregation only, no external reporting |
| Content | All content bundled or user-imported |
| Certificate Validation | Offline CA, local trust store |
| Package Resolution | Local plugin catalog, no remote registry |

### 6.2 Air-Gap Compliance

The application is designed to function in **air-gapped environments** (no internet connectivity). All dependencies are bundled in the application package. Plugin installation uses local `.asplugin` files. Documentation is bundled. No runtime network access is required or permitted.

### 6.3 Data Portability

All data is stored in standard SQLite format, making it portable across:
- Operating systems (Windows, macOS, Linux)
- Application versions (via migration scripts)
- Machines (copy the data directory)
- Backup/restore workflows

---

## 7. System Lifecycle

### 7.1 Startup Sequence

```
1. Electron main process initializes
2. SQLite database opened (WAL mode enabled)
3. Alembic migrations run (if pending)
4. Config system loads (defaults → user → env)
5. Logging system initializes (sinks configured)
6. Event bus created and wired
7. Domain services instantiated
8. Application use cases registered
9. Plugin engine loads and validates plugins
10. FastAPI backend starts (localhost only)
11. Electron renderer window created
12. React application mounts
13. Zustand stores hydrated
14. Initial data loaded (dashboard)
15. UI fully interactive
```

### 7.2 Shutdown Sequence

```
1.  User triggers shutdown
2.  In-progress requests completed (timeout: 5s)
3.  Background tasks cancelled gracefully
4.  Plugins notified of shutdown (unload hooks)
5.  Event bus flushed (pending events processed)
6.  FastAPI backend stops accepting requests
7.  Database connections closed
8.  SQLite WAL checkpoint performed
9.  Log files flushed and closed
10. Configuration persisted if changed
11. Electron window closed
12. Main process exits
```

### 7.3 Error Recovery

| Failure | Recovery Strategy |
|---|---|
| Database corruption | Auto-backup detection, restore from last good backup |
| Plugin crash | Plugin isolated, logged, continues without plugin |
| Config corruption | Fall back to defaults, log warning |
| Log file full | Rotate immediately, create new log file |
| Migration failure | Rollback to pre-migration backup |
| Memory pressure | Plugin resource limits enforced, cache eviction |
