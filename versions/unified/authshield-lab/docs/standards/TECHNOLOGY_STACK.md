# AuthShield Lab — Technology Stack

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab is an offline-first, enterprise-grade, cross-platform cybersecurity education platform. The technology stack is chosen for long-term maintainability, offline capability, security, and cross-platform support. Every component below is evaluated against four criteria: (1) suitability for offline-first operation, (2) security posture, (3) community longevity, and (4) developer productivity.

---

## 2. Backend

### 2.1 Python 3.12+

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 3.12 (target 3.12 LTS track) |
| **Role** | Primary backend language for all server-side logic, services, SDK, testing |
| **Justification** | Mature ecosystem, strong typing via `typing` and PEP 695 (Type Parameter Syntax), `asyncio` native support, extensive security/crypto libraries, dominant in cybersecurity tooling. |
| **Advantages** | Readable syntax reduces defect density; `match` statements for complex branching; `tomllib` in stdlib (3.11+); `TaskGroup` for structured concurrency; GIL removal in 3.13+ previews improves async throughput. |
| **Trade-offs** | Single-threaded CPU-bound performance (mitigated by async I/O and optional Rust extensions); runtime overhead vs. compiled languages (acceptable for web service workloads). |
| **Long-term maintenance** | Python has guaranteed 5-year security support per release; PEP 703 (free-threaded CPython) ensures relevance through 2030+. |

### 2.2 FastAPI

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 0.111 |
| **Role** | Async HTTP framework for REST API and WebSocket endpoints |
| **Justification** | Native async/await, automatic OpenAPI schema generation, Pydantic v2 integration, dependency injection system, high performance (on par with Node.js/Go in benchmarks). |
| **Advantages** | Type-safe request/response validation; interactive API docs at `/docs`; WebSocket support for real-time lab feedback; `BackgroundTasks` for async work; middleware stack for auth/CORS/logging. |
| **Trade-offs** | Smaller ecosystem than Django/Flask (mitigated by Starlette foundation); less opinionated (requires discipline in project structure). |
| **Long-term maintenance** | Active development, Starlette stability, strong community; API-first design enables future alternative frontends. |

### 2.3 SQLAlchemy 2.0 (async)

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 2.0 |
| **Role** | ORM and database abstraction layer |
| **Justification** | Mature, battle-tested ORM with full async support via `AsyncSession`, Pythonic query DSL (2.0 style with `select()`), schema migration support via Alembic. |
| **Advantages** | Database-agnostic (SQLite, PostgreSQL, MySQL); relationship mapping; connection pooling; event hooks; `mapped_column` for declarative models; `AsyncSession` integrates with `asyncio`. |
| **Trade-offs** | Learning curve for 2.0 migration style; async SQLite support via `aiosqlite` driver adds a dependency. |
| **Long-term maintenance** | SQLAlchemy has 18+ years of continuous development; 2.0 release is a stable long-term API. |

### 2.4 Pydantic v2

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 2.7 |
| **Role** | Data validation, serialization, settings management |
| **Justification** | Rust-based core for 5-50x performance improvement over v1; `BaseSettings` for configuration; `model_validator` for cross-field validation; JSON Schema generation. |
| **Advantages** | Type-safe API contracts; `model_dump()` for serialization; `TypeAdapter` for runtime validation; strict/lax modes; custom types via `Annotated`. |
| **Trade-offs** | Migration from v1 required; some v1 patterns deprecated (e.g., `validator` → `model_validator`). |
| **Long-term maintenance** | Pydantic v2 is the long-term supported version; Vercel backing ensures continued development. |

---

## 3. Frontend

### 3.1 Electron 28+

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 28 (Chromium 130+, Node.js 20.x) |
| **Role** | Cross-platform desktop application shell |
| **Justification** | Single codebase for Windows, macOS, Linux; native OS integration (tray, notifications, file system access); offline-first via bundled assets; auto-update via `electron-updater`. |
| **Advantages** | Chromium DevTools for debugging; `ipcRenderer`/`ipcMain` for secure process communication; `contextBridge` for sandboxed preload scripts; native menu/tray integration; file system access via `fs` module. |
| **Trade-offs** | Large binary size (~150MB); higher memory usage vs. native; security surface area of Chromium (mitigated by process isolation, CSP, `contextBridge`). |
| **Long-term maintenance** | Electron follows Chromium LTS cycle; `electron-builder` maintained; `electron-updater` supports differential updates. |

### 3.2 React 18

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 18.3 |
| **Role** | UI component framework |
| **Justification** | Declarative UI model; concurrent features (automatic batching, Suspense for data loading); massive ecosystem; TypeScript-first community; `react-dom` for DOM rendering, potential for `react-native` future. |
| **Advantages** | Component composition; hooks for state/effect management; `useTransition` for non-blocking updates; `useDeferredValue` for responsive UI; error boundaries for fault isolation. |
| **Trade-offs** | Re-renders can be expensive (mitigated by `React.memo`, `useMemo`, `useCallback`); state management complexity (mitigated by Zustand or Jotai for minimal global state). |
| **Long-term maintenance** | React 18 is the current stable; React 19 in development with continued backwards compatibility. |

### 3.3 TypeScript 5.3+

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 5.3 |
| **Role** | Static type system for JavaScript |
| **Justification** | Compile-time error detection; IDE autocomplete/refactoring; type-safe API contracts shared with backend Pydantic models; `satisfies` operator for type narrowing. |
| **Advantages** | `import type` for zero-runtime type imports; `const` type parameters; decorators (stage 3); `using` declarations (TC39); `--verbatimModuleSyntax` for ESM correctness. |
| **Trade-offs** | Compilation step adds to build time (mitigated by SWC/esbuild); learning curve for complex types (mitigated by pragmatic typing discipline). |
| **Long-term maintenance** | TypeScript is developed by Microsoft with regular releases; ECMAScript alignment ensures future-proofing. |

---

## 4. Database

### 4.1 SQLite (primary, async)

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 3.45 (bundled via `aiosqlite` 0.20+) |
| **Role** | Primary embedded database |
| **Justification** | Zero-configuration; single-file database; serverless; ACID compliant; WAL mode for concurrent reads; FTS5 for full-text search (assessment content); `json1` extension for JSON operations. |
| **Advantages** | No server process; portable (single file backup/restore); excellent read performance; `PRAGMA integrity_check` for data verification; `UNIQUE` + `CHECK` constraints for data integrity. |
| **Trade-offs** | Single-writer at a time (acceptable for offline-first); no network access (by design); limited concurrent write throughput (mitigated by WAL mode and batched writes). |
| **Long-term maintenance** | SQLite is the most widely deployed database engine; public domain license; backward-compatible file format since 2004. |

### 4.2 PostgreSQL (optional, for networked deployments)

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 15 |
| **Role** | Alternative database for institutional/multi-user deployments |
| **Justification** | Enterprise-grade for server deployments; full ACID with MVCC; row-level security; JSONB for flexible schemas; extensions (pg_trgm, uuid-ossp). |
| **Advantages** | Concurrent read/write; network access; replication support; rich query optimizer; `pg_stat_statements` for performance analysis. |
| **Trade-offs** | Requires server setup and maintenance; network dependency contradicts offline-first (deployed as optional upgrade path). |
| **Long-term maintenance** | PostgreSQL has 30+ years of development; strong governance via PostgreSQL Global Development Group. |

---

## 5. Shared Libraries

| Library | Purpose | Justification |
|---------|---------|---------------|
| **httpx** | Async HTTP client | `httpx` is the modern successor to `requests` with native `asyncio` support; HTTP/2 support; connection pooling; timeout management. |
| **structlog** | Structured logging | Processor-based pipeline; context binding; `structlog.stdlib` integration; JSON output by default; lazy evaluation of log messages. |
| **python-jose** | JWT handling | JOSE standards (JWS, JWE, JWK); Ed25519/EC/RSA algorithm support; JWK set handling for key rotation. |
| **passlib** | Password hashing | Unified API for Argon2, bcrypt, PBKDF2; configurable rounds/memory; time-constant comparison. |
| **argon2-cffi** | Argon2 password hashing | Winner of Password Hashing Competition; memory-hard (ASIC/GPU resistant); configurable time/memory/parallelism. |
| **cryptography** | Cryptographic primitives | Ed25519/RSA signatures; X.509 certificates; Fernet symmetric encryption; TLS certificate generation; maintained by pyca (Python Cryptographic Authority). |

---

## 6. Plugin System

### 6.1 importlib.metadata + stevedore pattern

| Attribute | Detail |
|-----------|--------|
| **Version** | stdlib (Python 3.12+) |
| **Role** | Plugin discovery, registration, and lifecycle management |
| **Justification** | Standard library (no external dependency); PEP 685 entry point compatibility; `entry_points()` API for plugin discovery; stevedore-inspired pattern for grouped entry points. |
| **Advantages** | No runtime dependency; plugins installed as Python packages; `group` parameter for organizing entry points (`authshield.plugins`, `authshield.routes`, `authshield.themes`); lazy loading via `load()` call. |
| **Trade-offs** | No built-in dependency resolution (custom resolver required); no sandboxing (mitigated by permission model and optional subprocess isolation). |
| **Long-term maintenance** | Part of Python stdlib; `importlib.metadata` is actively maintained; PEP 517/518 package metadata is standardized. |

### 6.2 Plugin Manifest Format

```yaml
# plugin.yaml (per-plugin)
name: "authshield-plugin-example"
version: "1.2.0"
min_platform: ">=1.0.0"
max_platform: "<2.0.0"
description: "Example plugin for demonstration"
author: "AuthShield Team"
license: "MIT"
required_permissions:
  - "filesystem:read"
  - "database:read"
provides:
  - "route:/api/v1/example"
  - "menu:Tools > Example"
  - "dashboard:widget:example_widget"
depends_on: []
platforms:
  - linux
  - macos
  - windows
```

---

## 7. Offline Storage

### 7.1 SQLite (primary offline store)

- Application state, user progress, lab results, configuration stored in SQLite
- WAL mode enabled for read performance
- `PRAGMA foreign_keys = ON` for referential integrity
- `PRAGMA journal_mode = WAL` for crash recovery

### 7.2 JSON Files (secondary offline store)

- Plugin manifests, theme definitions, translation files stored as JSON
- Atomic writes via `aiofiles` (write to temp file, then rename)
- UTF-8 with BOM detection for cross-platform compatibility

### 7.3 MessagePack (optional, for compact serialization)

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 1.8 |
| **Role** | Compact binary serialization for large datasets (lab results, assessment data) |
| **Justification** | 30-50% smaller than JSON; faster parsing; zero-dependency decoding; schema evolution support. |
| **Advantages** | Reduced storage footprint for offline data; faster network transfer when syncing; backwards-compatible schema changes. |
| **Trade-offs** | Not human-readable (JSON fallback always available); optional dependency (degrades gracefully). |
| **Long-term maintenance** | msgpack specification is stable; msgpack-python is actively maintained. |

---

## 8. Reporting

### 8.1 Jinja2 Templates

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 3.1 |
| **Role** | HTML/PDF report templating |
| **Justification** | Mature, secure (sandboxed environment); template inheritance; filters for data formatting; i18n support via `jinja2.ext.i18n`. |
| **Advantages** | Declarative templates; block inheritance for layout composition; custom filters for date/currency formatting; macro system for reusable components. |
| **Trade-offs** | HTML generation only (PDF via WeasyPrint); requires template authoring discipline. |
| **Long-term maintenance** | Jinja2 is the standard Python template engine; minimal changes needed for stability. |

### 8.2 WeasyPrint (PDF generation)

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 62 |
| **Role** | HTML-to-PDF conversion for assessment reports |
| **Justification** | CSS Paged Media support; Unicode/CJK rendering; no external dependencies (bundles Cairo/Pango); offline-capable. |
| **Advantages** | HTML+CSS → PDF (single template system); font embedding; page breaks, headers/footers; A4/Letter page sizes. |
| **Trade-offs** | Large dependency (Cairo/Pango); slower than wkhtmltopdf (acceptable for batch report generation). |
| **Long-term maintenance** | WeasyPrint 62+ is actively maintained; Cairo/Pango are stable system libraries. |

### 8.3 CSV/JSON Export

- Python `csv` module for CSV export (stdlib, zero-dependency)
- `orjson` for fast JSON export (Rust-based, 2-10x faster than `json`)
- Streaming export for large datasets (generator-based, memory-efficient)

---

## 9. Localization

### 9.1 gettext

| Attribute | Detail |
|-----------|--------|
| **Role** | PO/MO file format for compiled translations |
| **Justification** | Industry standard for Unix/Linux localization; compiled `.mo` files are binary-optimized for lookup; `babel` extracts strings from Python source. |
| **Advantages** | Plural forms support; context (`msgctxt`) for disambiguation; `ngettext` for plural-aware translation. |
| **Trade-offs** | PO files are less readable than JSON (mitigated by JSON translation files as source format). |

### 9.2 Babel

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 2.15 |
| **Role** | Localization utilities (date/time, number, currency formatting) |
| **Justification** | CLDR data for locale-specific formatting; `format_date()`, `format_currency()`, `format_number()`; locale negotiation. |
| **Advantages** | Locale-aware date/time formatting; currency formatting with symbol placement; number grouping (1,000 vs 1.000); timezone support. |
| **Trade-offs** | CLDR data is large (~50MB for all locales); only selected locales bundled. |
| **Long-term maintenance** | Babel follows CLDR releases; widely used in Python ecosystem. |

### 9.3 Custom JSON Translation Files

- Flat key structure: `"module.feature.element": "Translated text"`
- RTL-aware (Arabic, Hebrew) via CSS logical properties
- Fallback chain: locale → regional → English (default)
- Completeness scoring: percentage of keys translated per locale

---

## 10. Accessibility

### 10.1 axe-core (testing)

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 4.9 |
| **Role** | Automated WCAG 2.2 AA accessibility testing |
| **Justification** | Industry standard for web accessibility testing; 70+ rules covering WCAG 2.0/2.1/2.2; Selenium/Playwright integration; rule customization. |
| **Advantages** | Automated detection of common issues (missing labels, color contrast, ARIA misuse); CI/CD integration; report generation for audit trails. |
| **Trade-offs** | Cannot detect all accessibility issues (requires manual testing for cognitive/UX accessibility); ~30% of WCAG criteria require human judgment. |
| **Long-term maintenance** | axe-core is maintained by Deque Systems; follows WCAG specification updates. |

### 10.2 Custom WCAG Validation

- Semantic HTML validation (heading hierarchy, landmark regions)
- Keyboard navigation testing (Tab/Enter/Escape/Arrow key flows)
- Screen reader compatibility checks (ARIA labels, live regions)
- High contrast mode validation (CSS custom properties)
- Reduced motion support (`prefers-reduced-motion` media query)

---

## 11. Configuration

### 11.1 Pydantic Settings

| Attribute | Detail |
|-----------|--------|
| **Role** | Type-safe configuration management |
| **Justification** | `BaseSettings` class with environment variable binding; nested settings models; `.env` file support; validation on load; JSON Schema generation. |
| **Advantages** | Type validation at startup (fail-fast); environment variable override; secret handling via `SecretStr`; custom sources (TOML, YAML). |
| **Trade-offs** | Requires Pydantic dependency (already used for API validation). |

### 11.2 TOML Configuration

| Attribute | Detail |
|-----------|--------|
| **Role** | Primary configuration file format |
| **Justification** | Python 3.11+ `tomllib` in stdlib; human-readable; nested structures; comments supported; used by `pyproject.toml` (Python ecosystem standard). |
| **Advantages** | No external dependency for reading; clear syntax; widely supported by tooling (Rust, Go, Node.js). |
| **Trade-offs** | Less flexible than YAML for complex structures (acceptable for configuration). |

### 11.3 YAML Configuration (optional)

| Attribute | Detail |
|-----------|--------|
| **Version** | PyYAML ≥ 6.0 or ruamel.yaml ≥ 0.18 |
| **Role** | Alternative configuration format (plugin manifests, CI/CD) |
| **Justification** | Human-readable; comments preserved (ruamel.yaml); supports anchors/aliases; widely used in DevOps tooling. |
| **Advantages** | Compact representation; multi-line strings; anchor reuse; flow/block styles. |
| **Trade-offs** | YAML parsing is slower than TOML; potential for injection via YAML anchors (mitigated by safe loading). |
| **Long-term maintenance** | PyYAML is widely maintained; ruamel.yaml preserves round-trip fidelity. |

---

## 12. Logging

### 12.1 structlog

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 24.1 |
| **Role** | Structured logging framework |
| **Justification** | Processor-based pipeline; context binding for request-scoped data; `structlog.stdlib` integration for stdlib logger compatibility; lazy evaluation. |
| **Advantages** | JSON output by default; context propagation via `bind()`/`unbind()`; `tqdm` integration; thread-safe; `wrap_logger()` for stdlib migration. |
| **Trade-offs** | Different API from stdlib logging (mitigated by `structlog.stdlib` bridge). |
| **Long-term maintenance** | structlog is actively maintained; follows Python release cycle. |

### 12.2 python-json-logger

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 3.2 |
| **Role** | JSON log formatter for stdlib logging |
| **Justification** | Fallback for stdlib logging integration; structured JSON output; custom field formatting. |
| **Advantages** | Drop-in replacement for `logging.Formatter`; configurable field names; `rename_fields` for custom output. |
| **Trade-offs** | Not needed if structlog is used exclusively (included as fallback). |
| **Long-term maintenance** | python-json-logger is actively maintained; widely used. |

---

## 13. Dependency Injection

### 13.1 FastAPI Depends (primary)

| Attribute | Detail |
|-----------|--------|
| **Role** | Request-scoped dependency injection |
| **Justification** | Native FastAPI feature; `Depends()` callable; dependency caching per request; `yield` dependencies for setup/teardown; `use_class_attributes_for_kwargs` for class-based dependencies. |
| **Advantages** | Zero additional dependency; type-safe; composable (`Depends(get_db)` chained); override in tests (`app.dependency_overrides`); WebSocket dependencies. |
| **Trade-offs** | FastAPI-specific (not portable to other frameworks; acceptable for single-framework architecture). |

### 13.2 dependency-injector (optional, for complex DI)

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 4.41 |
| **Role** | Inversion of Control container for complex dependency graphs |
| **Justification** | `Factory`, `Singleton`, `Configuration` providers; wire/unwire for test overrides; `@inject` decorator; FastAPI integration module. |
| **Advantages** | Explicit dependency graph; easy test overrides; singleton management; configuration-driven wiring. |
| **Trade-offs** | Additional dependency; more boilerplate than `Depends()` (used only for complex service layers). |
| **Long-term maintenance** | dependency-injector is actively maintained; widely used in enterprise Python. |

---

## 14. Validation

### 14.1 Pydantic v2 (primary)

- All API request/response bodies validated via Pydantic models
- `Field()` constraints: `min_length`, `max_length`, `ge`, `le`, `pattern`
- `model_validator(mode='before')` for cross-field validation
- Custom types via `Annotated[int, Field(ge=0)]`

### 14.2 Custom Validators

- Domain-specific validators (password strength, email format, IP address)
- `@validator` decorators for reusable validation logic
- Business rule validation in service layer (Pydantic validates structure, services validate semantics)

---

## 15. Serialization

| Format | Library | Use Case |
|--------|---------|----------|
| **JSON** | `orjson` | API responses, log output, configuration files |
| **JSON** | `json` (stdlib) | Fallback when `orjson` unavailable |
| **MessagePack** | `msgpack` | Compact offline storage, sync payloads |
| **Pydantic** | `model_dump()` | Model serialization with type coercion |
| **Pydantic** | `model_dump_json()` | Fast JSON serialization (Rust core) |

---

## 16. Scheduling

### 16.1 APScheduler (optional)

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 3.10 |
| **Role** | Scheduled task execution (backup, cleanup, report generation) |
| **Justification** | `BackgroundScheduler`/`AsyncIOScheduler` for in-process scheduling; cron/date/interval triggers; `JobStore` for persistence (SQLite-backed). |
| **Advantages** | No external process required; cron expressions for complex schedules; `max_instances` prevents overlapping; `CoalescingJobStore` for deduplication. |
| **Trade-offs** | Not distributed (single-instance only; acceptable for desktop app); in-memory job store lost on restart (mitigated by SQLite job store). |
| **Long-term maintenance** | APScheduler 3.x is stable; APScheduler 4.x in development with async-first design. |

---

## 17. Background Tasks

### 17.1 asyncio (primary)

- `asyncio.create_task()` for concurrent async operations
- `asyncio.gather()` for parallel execution
- `asyncio.Semaphore` for rate limiting
- `asyncio.Queue` for producer/consumer patterns
- `asyncio.TaskGroup` (Python 3.11+) for structured concurrency

### 17.2 FastAPI BackgroundTasks

- `BackgroundTasks.add_task()` for post-response work
- Dependency injection integration
- Automatic task lifecycle management

---

## 18. File Management

### 18.1 aiofiles

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 24.1 |
| **Role** | Async file I/O |
| **Justification** | Non-blocking file operations; thread pool execution; `aiofiles.tempfile` for atomic writes; `aiofiles.os` for async OS operations. |
| **Advantages** | Async-compatible file reads/writes; atomic file operations (write-to-temp + rename); temporary file management. |
| **Trade-offs** | Thread pool overhead (acceptable for file I/O workloads). |
| **Long-term maintenance** | aiofiles is actively maintained; thin wrapper over stdlib `asyncio`. |

### 18.2 pathlib (stdlib)

- `Path` objects for cross-platform path manipulation
- `Path.mkdir(parents=True, exist_ok=True)` for directory creation
- `Path.write_text()` / `Path.read_text()` for synchronous operations
- `Path.resolve()` for canonical path resolution
- `Path.suffix` / `Path.stem` for filename manipulation

---

## 19. Native OS Integration

### 19.1 Cross-platform

| Operation | Implementation |
|-----------|---------------|
| **Process management** | `subprocess.run()` with timeout; `asyncio.create_subprocess_exec()` for async |
| **File system** | `pathlib.Path` (cross-platform); `shutil` for copy/move/tree |
| **Environment** | `os.environ` / `os.getenv()`; `platform.system()` for OS detection |
| **Clipboard** | `pyperclip` (cross-platform clipboard access) |
| **Notifications** | `plyer` (cross-platform desktop notifications) |
| **System info** | `platform` module (OS, architecture, Python version) |

### 19.2 Windows-specific

| Operation | Implementation |
|-----------|---------------|
| **Registry** | `winreg` (stdlib) for Windows registry access |
| **Service** | `pywin32` (`win32serviceutil`) for Windows service management |
| **COM** | `comtypes` for COM automation (optional) |
| **Scheduled Tasks** | `subprocess.run(['schtasks', ...])` for Windows Task Scheduler |

### 19.3 macOS-specific

| Operation | Implementation |
|-----------|---------------|
| **LaunchAgent** | `launchd` plist generation via `subprocess` |
| **Keychain** | `subprocess.run(['security', ...])` for Keychain access |
| **Notifications** | `osascript` for AppleScript notifications |

### 19.4 Linux-specific

| Operation | Implementation |
|-----------|---------------|
| **Systemd** | Unit file generation; `systemctl` integration |
| **D-Bus** | `dbus-next` for D-Bus IPC (optional) |
| **Package managers** | `apt`/`dnf`/`pacman` detection via `shutil.which()` |

---

## 20. Digital Signature

### 20.1 cryptography library

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 42 |
| **Role** | Cryptographic operations (signatures, hashing, encryption, certificates) |
| **Justification** | PyCA-maintained; OpenSSL-backed; Ed25519/RSA/EC support; Fernet symmetric encryption; X.509 certificate generation; TLS primitives. |
| **Advantages** | `Ed25519PrivateKey` for fast signatures; `rsa.generate_private_key()` for RSA; `hashlib` wrapper for SHA-256; `Fernet` for symmetric encryption; `x509` for certificate generation. |
| **Trade-offs** | Large dependency (OpenSSL); C extension compilation required (mitigated by pre-built wheels). |
| **Long-term maintenance** | PyCA is the Python security standard; annual releases with security patches. |

---

## 21. Packaging & Distribution

### 21.1 Python Packaging

| Tool | Purpose |
|------|---------|
| **PyInstaller** | Single-file executable bundling; `--onefile` mode; hidden imports detection; `spec` files for customization |
| **Nuitka** | Ahead-of-time compilation; C extension generation; smaller binaries than PyInstaller (alternative) |
| **cx_Freeze** | Cross-platform executable freezing (alternative) |

### 21.2 Electron Packaging

| Tool | Purpose |
|------|---------|
| **electron-builder** | Cross-platform packaging; NSIS (Windows), DMG (macOS), AppImage/deb/rpm (Linux); code signing; auto-update support |
| **electron-forge** | Alternative packaging with Webpack/Vite integration |

### 21.3 Platform-specific Installers

| Platform | Installer | Notes |
|----------|-----------|-------|
| **Windows** | NSIS (default) or WiX | NSIS for lightweight; WiX for MSI enterprise deployment; UAC manifest; Add/Remove Programs integration |
| **macOS** | DMG | Notarization required (Apple Developer ID); `codesign` for signing; `pkgutil` for verification |
| **Linux** | AppImage + deb + rpm | AppImage for universal; deb for Debian/Ubuntu; rpm for Fedora/RHEL; `.desktop` file for menu integration |

---

## 22. Auto-Update

### 22.1 electron-updater

| Attribute | Detail |
|-----------|--------|
| **Version** | ≥ 6.1 |
| **Role** | Automatic application updates (disabled by default) |
| **Justification** | Differential updates (smaller download sizes); code signing verification; staged rollouts; manual check option; offline-safe (skips if no network). |
| **Advantages** | `autoDownload: false` for opt-in updates; `autoInstallOnAppQuit` for silent install; `update-downloaded` event for notification; `feedURL` for custom update server. |
| **Trade-offs** | Network dependency (contradicts offline-first; disabled by default); update server hosting required for distribution. |
| **Long-term maintenance** | electron-updater is maintained by electron-builder team; follows Electron release cycle. |

---

## 23. Additional Libraries

### 23.1 Development Tools

| Tool | Version | Purpose |
|------|---------|---------|
| **pytest** | ≥ 8.0 | Test framework; `pytest-asyncio` for async tests; `pytest-cov` for coverage |
| **ruff** | ≥ 0.4 | Python linter+formatter (replaces flake8, isort, black) |
| **mypy** | ≥ 1.10 | Static type checker for Python |
| **eslint** | ≥ 9.0 | TypeScript linter; flat config; React plugin |
| **prettier** | ≥ 3.2 | Code formatter for TypeScript/JSON/CSS/Markdown |
| **vitest** | ≥ 2.0 | Test framework for TypeScript (Vite-native) |
| **playwright** | ≥ 1.44 | E2E testing for Electron renderer; cross-browser support |

### 23.2 Build Tools

| Tool | Version | Purpose |
|------|---------|---------|
| **Vite** | ≥ 5.4 | Frontend bundler; HMR; TypeScript support; library mode |
| **SWC** | ≥ 1.6 | Rust-based TypeScript compiler (replaces tsc for speed) |
| **esbuild** | ≥ 0.23 | Fast JavaScript bundler (used by Vite internally) |

### 23.3 Data & Serialization

| Library | Version | Purpose |
|---------|---------|---------|
| **orjson** | ≥ 3.10 | Fast JSON serialization (Rust-based) |
| **msgpack** | ≥ 1.8 | Binary serialization (optional) |
| **csv** | stdlib | CSV export (no external dependency) |
| **tomllib** | stdlib (3.11+) | TOML reading (no external dependency) |

### 23.4 Security

| Library | Version | Purpose |
|---------|---------|---------|
| **cryptography** | ≥ 42 | Cryptographic primitives |
| **argon2-cffi** | ≥ 23.1 | Argon2id password hashing |
| **passlib** | ≥ 1.7.4 | Password hashing abstraction |
| **python-jose** | ≥ 3.3 | JWT/JWK/JWE handling |
| **certifi** | ≥ 2024.2 | CA certificate bundle (for httpx) |

---

## 24. Dependency Summary

```
Python Backend:
├── Python 3.12+
├── FastAPI 0.111+
├── SQLAlchemy 2.0+
├── Pydantic v2.7+
├── aiosqlite 0.20+
├── httpx 0.27+
├── structlog 24.1+
├── python-jose 3.3+
├── passlib 1.7.4+
├── argon2-cffi 23.1+
├── cryptography 42+
├── Jinja2 3.1+
├── WeasyPrint 62+
├── orjson 3.10+
├── aiofiles 24.1+
├── Babel 2.15+
├── APScheduler 3.10+ (optional)
├── dependency-injector 4.41+ (optional)
├── msgpack 1.8+ (optional)
└── pywin32 (Windows only)

Electron Frontend:
├── Electron 28+
├── React 18.3+
├── TypeScript 5.3+
├── Vite 5.4+
├── electron-builder (dev)
└── electron-updater 6.1+ (optional)

Testing:
├── pytest 8.0+
├── pytest-asyncio
├── pytest-cov
├── ruff 0.4+
├── mypy 1.10+
├── eslint 9.0+
├── prettier 3.2+
├── vitest 2.0+
├── playwright 1.44+
└── axe-core 4.9+ (browser)
```

---

## 25. Version Policy

| Category | Policy |
|----------|--------|
| **Python** | Target 3.12; minimum 3.11; drop support 2 years after EOL |
| **Electron** | Target latest stable; support N-1; security patches within 48h |
| **React** | Target 18.x; evaluate 19.x migration after stable release |
| **Dependencies** | Monthly security patches; quarterly feature updates; annual major upgrades |
| **Lock files** | Regenerate monthly; CI verification of lock file consistency |

---

*Document maintained by the AuthShield Lab Architecture Team. Review quarterly.*
