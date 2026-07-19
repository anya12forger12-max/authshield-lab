# AuthShield Lab — Workspace Architecture

> Version: 1.0.0 | Last Updated: 2026-07-19
> Status: Living Document | Owner: Architecture Team

---

## 1. Overview

AuthShield Lab is organized as a **monorepo** with strict directory-level separation of concerns. Every directory has an explicit purpose, governance model, and build boundary. No directory may violate the responsibilities assigned to another.

This document defines the workspace layout, the role of each top-level directory, cross-cutting concern mapping, dependency flow, build isolation principles, shared code governance, and configuration management hierarchy.

---

## 2. Monorepo Root Structure

```
AuthShieldLab/
├── apps/                    # Deployable application packages
├── packages/                # Shared internal packages (buildable, publishable)
├── libraries/               # Vendored or upstream-adjacent library forks
├── services/                # Background / long-running service processes
├── sdk/                     # Public SDKs (Python, JS/TS)
├── plugins/                 # Plugin packages and plugin API definitions
├── docs/                    # All documentation (guides, ADRs, standards)
├── architecture/            # Architecture decision records & diagrams
├── assets/                  # Static assets (images, fonts, icons, media)
├── scripts/                 # Developer utility scripts (scaffolding, migration)
├── tools/                   # Internal developer tooling (linters, formatters)
├── configs/                 # Shared configuration files and schemas
├── infrastructure/          # IaC, Docker, Terraform, CI/CD pipeline definitions
├── tests/                   # Cross-cutting integration and E2E test suites
├── benchmarks/              # Performance benchmarks and profiling scripts
├── examples/                # Example configurations and usage patterns
├── templates/               # Code generation templates (scaffolding, CRUD)
├── localization/            # i18n translation files and tooling
├── accessibility/           # WCAG audit reports and accessibility tooling
├── licenses/                # Third-party license files and SBOM manifests
├── governance/              # Contribution rules, approval matrices, RFC templates
├── security/                # Threat models, pen-test reports, security tooling
├── ci/                      # CI/CD pipeline definitions (GitHub Actions, etc.)
├── release/                 # Release playbooks, changelogs, versioning rules
├── backups/                 # Database snapshots, config backups (gitignored)
├── backend/                 # Python backend application (FastAPI)
├── frontend/                # React/Electron frontend application
└── installer/               # Offline installer and distribution packaging
```

---

## 3. Directory Definitions

### 3.1 `apps/` — Deployable Applications

**Purpose:** Contains self-contained, independently deployable application packages.

| Entry | Description |
|---|---|
| `apps/web/` | Next.js / React web dashboard (production UI) |
| `apps/desktop/` | Electron desktop application shell |
| `apps/admin/` | Admin control panel (restricted access) |

**Conventions:**
- Each app must declare its own `package.json` or `pyproject.toml`.
- Apps may import from `packages/` but never from other `apps/`.
- Each app owns its own routing, layout, and view layer.
- Apps are the only directory permitted to produce distributable artifacts.

**Build isolation:** Each app is built independently. The CI pipeline builds each app in its own container or job. No app may read another app's build output at compile time.

---

### 3.2 `packages/` — Shared Internal Packages

**Purpose:** Reusable, independently versioned packages shared across apps and services.

| Entry | Description |
|---|---|
| `packages/ui/` | Shared React component library |
| `packages/auth-core/` | Core authentication logic (shared Python) |
| `packages/config/` | Configuration loader and schema definitions |
| `packages/event-bus/` | Cross-module event bus implementation |
| `packages/validation/` | Input validation schemas (Pydantic, Zod) |
| `packages/errors/` | Error types and error formatting |
| `packages/logging/` | Structured logging setup and formatters |

**Conventions:**
- Every package must be publishable (internal npm registry or PyPI-compatible).
- Packages must not import from `apps/`, `services/`, `plugins/`, or `backend/`.
- Packages may depend on other packages within `packages/` (explicit, documented).
- Every package exports a public API surface via `index.ts` or `__init__.py` `__all__`.
- Private internals live in `_private/` or files prefixed with `_`.

**Build isolation:** Packages are built in dependency order via a topological sort. Each package compiles in isolation and outputs to a `dist/` directory. No package reads another package's source at build time—only its published output.

---

### 3.3 `libraries/` — Vendored & Upstream Libraries

**Purpose:** Forked or vendored upstream libraries that AuthShield Lab patches or extends.

| Entry | Description |
|---|---|
| `libraries/fastapi-extensions/` | Custom FastAPI middleware and route helpers |
| `libraries/electron-plugins/` | Electron IPC and plugin loader extensions |
| `libraries/sqlite-wal/` | SQLite WAL mode helpers |

**Conventions:**
- Each library fork documents the upstream version it tracks and patches applied.
- A `PATCHES.md` file in each library directory lists all modifications.
- Libraries may not import from `packages/`, `apps/`, `backend/`, or `services/`.
- Upgrades are reviewed quarterly or on critical security patches.

---

### 3.4 `services/` — Background & Long-Running Services

**Purpose:** Processes that run independently of the main application request cycle.

| Entry | Description |
|---|---|
| `services/worker/` | Async task worker (Celery/RQ equivalent) |
| `services/scheduler/` | Cron-like job scheduler |
| `services/webhook-relay/` | Outbound webhook delivery service |
| `services/metrics-collector/` | Metrics aggregation daemon |

**Conventions:**
- Each service has its own `Dockerfile` and entrypoint script.
- Services communicate via the event bus—never by direct function calls.
- Services own their database tables and migrations (no shared schemas).
- Each service declares resource limits (CPU, memory) in its Docker Compose entry.

**Build isolation:** Services are containerized independently. A change in one service does not trigger a rebuild of another unless the shared `packages/` they depend on also changed.

---

### 3.5 `sdk/` — Public SDKs

**Purpose:** Official client SDKs for external consumers.

| Entry | Description |
|---|---|
| `sdk/python/` | Python SDK (`authshield`) |
| `sdk/javascript/` | JavaScript/TypeScript SDK (`@authshield/sdk`) |

**Conventions:**
- SDKs mirror the public REST API surface exactly.
- SDKs may depend on `packages/validation` for shared schemas (copied, not imported).
- SDKs are versioned independently from the platform.
- Breaking changes in the platform API require a new major SDK version.
- SDKs ship with auto-generated API reference docs.

---

### 3.6 `plugins/` — Plugin Packages

**Purpose:** Plugin API definitions and first-party plugin implementations.

| Entry | Description |
|---|---|
| `plugins/api/` | Plugin API contracts and types |
| `plugins/saml-provider/` | SAML SSO provider plugin |
| `plugins/ldap-sync/` | LDAP directory synchronization plugin |
| `plugins/custom-attacks/` | User-contributed attack scenario plugin |

**Conventions:**
- Plugins implement interfaces defined in `plugins/api/`.
- Plugins may depend on `packages/` but never on `apps/`, `backend/`, or `services/`.
- Third-party plugins are sandboxed and may not access the file system or network directly.
- Each plugin declares its permissions in a `plugin.json` manifest.

---

### 3.7 `docs/` — Documentation

**Purpose:** All documentation, organized by audience and topic.

```
docs/
├── architecture/       # Architecture docs (this document lives here)
├── guides/             # User guides, admin guides, developer guides
├── standards/          # Coding standards, security engineering, logging
├── security/           # Security-specific documentation
├── accessibility/      # WCAG compliance guides
├── development/        # Onboarding, local development
└── api/                # REST API reference (auto-generated from OpenAPI)
```

**Conventions:**
- All docs use Markdown. Diagrams use Mermaid or are stored as SVG in `assets/`.
- Every doc file has a status badge (Draft / Living / Archived).
- Docs are versioned via git tags—no separate doc versioning system.
- Auto-generated docs (API reference) are excluded from linting.

---

### 3.8 `architecture/` — Architecture Decision Records

**Purpose:** ADRs (Architecture Decision Records) and high-level architecture diagrams.

```
architecture/
├── ADR-001-*.md
├── ADR-002-*.md
├── ...
├── DECISIONS.md
├── diagrams/
│   ├── system-context.mmd
│   ├── container.mmd
│   └── component.mmd
```

**Conventions:**
- Every significant architectural decision has an ADR.
- ADRs are immutable once accepted. Reversals get new ADRs.
- The `DECISIONS.md` file is an index of all ADRs with status.

---

### 3.9 `assets/` — Static Assets

**Purpose:** Images, fonts, icons, media files, and other non-code resources.

```
assets/
├── icons/
├── images/
├── fonts/
├── media/
└── brand/
```

**Conventions:**
- All images are optimized (WebP preferred, PNG fallback).
- Fonts are self-hosted (no external CDN loading).
- Asset paths in code use the config module's `assetUrl()` helper.

---

### 3.10 `scripts/` — Developer Utility Scripts

**Purpose:** Automation scripts for development workflows.

| Entry | Description |
|---|---|
| `scripts/scaffold/` | Module/component scaffolding generators |
| `scripts/migrate/` | Database migration helpers |
| `scripts/seed/` | Test data seeding scripts |
| `scripts/release/` | Release automation scripts |
| `scripts/health/` | Health check and diagnostics scripts |

**Conventions:**
- Scripts are written in Bash or Python.
- Scripts must not modify production data without explicit `--production` flag.
- Scripts log to stdout in structured JSON format.

---

### 3.11 `tools/` — Internal Developer Tooling

**Purpose:** Custom linters, formatters, and code analysis tools.

| Entry | Description |
|---|---|
| `tools/linters/` | Custom lint rules (architecture boundary enforcement) |
| `tools/analyzers/` | Dependency graph analysis tools |
| `tools/validators/` | Schema validators for configs and manifests |

**Conventions:**
- Tools are invoked via `make` targets or npm scripts.
- Tools must not modify source files (read-only analysis only).

---

### 3.12 `configs/` — Shared Configuration

**Purpose:** Configuration files and schemas shared across the workspace.

```
configs/
├── pyproject.toml.base
├── tsconfig.base.json
├── .eslintrc.base.js
├── .prettierrc.json
├── schemas/
│   ├── plugin-manifest.schema.json
│   ├── config.schema.json
│   └── event-contract.schema.json
```

**Conventions:**
- App-level configs extend base configs in this directory.
- Schemas are validated during CI—invalid configs block the build.
- Secrets are never stored in this directory.

---

### 3.13 `infrastructure/` — Infrastructure as Code

**Purpose:** Docker, Terraform, Kubernetes manifests, and deployment configs.

```
infrastructure/
├── docker/
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── Dockerfile.backend
├── kubernetes/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
└── terraform/
    └── modules/
```

**Conventions:**
- All infrastructure code is versioned and reviewed via PR.
- Secrets are injected via environment variables, never committed.
- Infrastructure changes require approval from the security team.

---

### 3.14 `tests/` — Cross-Cutting Tests

**Purpose:** Integration tests, E2E tests, and tests that span multiple modules.

```
tests/
├── integration/       # Cross-module integration tests
├── e2e/               # End-to-end user flow tests
├── contract/          # API contract tests
├── performance/       # Load and performance tests
└── conftest.py        # Shared test fixtures
```

**Conventions:**
- Unit tests live inside their module (e.g., `backend/app/auth/tests/`).
- Cross-cutting tests live here and are excluded from module-level test runs.
- Test data is seeded via `scripts/seed/` and cleaned up after each run.

---

### 3.15 `benchmarks/` — Performance Benchmarks

**Purpose:** Benchmarks, profiling scripts, and performance regression tests.

```
benchmarks/
├── auth-throughput/
├── event-bus-latency/
├── api-response-times/
└── baselines/
```

**Conventions:**
- Benchmarks run on a dedicated CI job (not mixed with unit tests).
- Baseline results are committed to `baselines/` and compared against new runs.
- Performance regressions beyond 10% fail the CI pipeline.

---

### 3.16 `examples/` — Example Configurations

**Purpose:** Runnable examples demonstrating platform features.

```
examples/
├── quickstart/
├── plugin-development/
├── api-usage/
└── custom-scenarios/
```

**Conventions:**
- Every example must be runnable with a single command.
- Examples are tested in CI to prevent bit-rot.

---

### 3.17 `templates/` — Code Generation Templates

**Purpose:** Scaffolding templates for new modules, plugins, and components.

```
templates/
├── new-module/
├── new-plugin/
├── new-api-route/
├── new-entity/
└── new-test/
```

**Conventions:**
- Templates use a simple variable substitution syntax (`{{name}}`).
- Templates are tested by generating output and verifying it compiles.

---

### 3.18 `localization/` — i18n Resources

**Purpose:** Translation files, locale definitions, and i18n tooling.

```
localization/
├── locales/
│   ├── en.json
│   ├── es.json
│   └── ...
├── schemas/
│   └── locale.schema.json
└── tools/
    └── extract-translations.py
```

**Conventions:**
- English (`en.json`) is the source of truth.
- All user-facing strings must be externalized.
- Missing translations fall back to English at runtime.

---

### 3.19 `accessibility/` — Accessibility Resources

**Purpose:** WCAG audit reports, axe configs, and accessibility testing tooling.

```
accessibility/
├── axe-config.json
├── audits/
│   ├── 2026-07-wcag-audit.md
│   └── ...
└── tools/
    └── a11y-check.py
```

**Conventions:**
- WCAG 2.2 AA compliance is required for all UI components.
- Audit reports are generated monthly and committed here.
- Accessibility regressions are treated as P1 bugs.

---

### 3.20 `licenses/` — Third-Party Licenses

**Purpose:** License compliance manifests and SBOM files.

```
licenses/
├── THIRD_PARTY_LICENSES.md
├── SBOM.json
└── NOTICE
```

**Conventions:**
- SBOM is regenerated on every release.
- License compatibility is checked during CI (GPL-incompatible dependencies are blocked).

---

### 3.21 `governance/` — Contribution & Approval Rules

**Purpose:** Contribution guidelines, approval matrices, and RFC templates.

```
governance/
├── APPROVAL_MATRIX.md
├── RFC_TEMPLATE.md
├── CONTRIBUTION_GUIDELINES.md
└── REVIEW_PROCESS.md
```

**Conventions:**
- All governance documents are reviewed quarterly.
- Changes to governance require team-wide consensus.

---

### 3.22 `security/` — Security Resources

**Purpose:** Threat models, penetration test reports, security tooling, and vulnerability tracking.

```
security/
├── threat-models/
│   ├── data-flow-diagrams/
│   └── STRIDE-analysis.md
├── pentest-reports/
│   └── 2026-Q2-pentest.md
├── vulnerability-tracker/
│   └── open-findings.md
└── tools/
    └── secret-scanner.py
```

**Conventions:**
- All security reports are access-controlled (not committed if containing remediation details for active CVEs).
- Security scans run on every PR and nightly.

---

### 3.23 `ci/` — CI/CD Pipeline Definitions

**Purpose:** GitHub Actions workflows, reusable actions, and CI configuration.

```
ci/
├── workflows/
│   ├── ci.yml
│   ├── release.yml
│   ├── security-scan.yml
│   └── deploy.yml
├── actions/
│   └── setup-python/
└── scripts/
    └── ci-helpers.sh
```

**Conventions:**
- CI workflows are the single source of truth for build/test/deploy.
- All CI scripts must handle failures gracefully (exit codes, retries).
- Secrets are injected via GitHub Secrets—never hardcoded.

---

### 3.24 `release/` — Release Management

**Purpose:** Release playbooks, changelogs, and versioning rules.

```
release/
├── PLAYBOOK.md
├── VERSIONING.md
├── CHANGELOG.md       # symlinked to root
└── scripts/
    └── bump-version.py
```

**Conventions:**
- Semantic versioning (MAJOR.MINOR.PATCH) is mandatory.
- Changelogs are auto-generated from conventional commits.
- Releases are tagged in git and published to the internal artifact store.

---

### 3.25 `backups/` — Data Backups

**Purpose:** Database snapshots, config backups, and disaster recovery artifacts.

**Conventions:**
- This directory is `.gitignore`d except for the README.
- Backups are encrypted at rest and stored in the offline distribution.
- Backup rotation policy: daily (7 days), weekly (4 weeks), monthly (12 months).

---

## 4. Cross-Cutting Concerns Mapping

| Concern | Primary Owner | Applies To | Implementation |
|---|---|---|---|
| Authentication | `packages/auth-core/` | All apps, services | Middleware, decorators |
| Authorization | `packages/auth-core/` | All apps, services | RBAC policy engine |
| Logging | `packages/logging/` | All modules | structlog integration |
| Error Handling | `packages/errors/` | All modules | Global exception handler |
| Validation | `packages/validation/` | All modules | Pydantic / Zod schemas |
| Event Bus | `packages/event-bus/` | All modules | In-process pub/sub |
| Configuration | `packages/config/` | All modules | Hierarchical settings |
| Localization | `localization/` | UI modules only | i18n translation loader |
| Accessibility | `accessibility/` | UI modules only | axe-core integration |
| Security Scanning | `security/` | All code | Pre-commit, CI gates |
| Performance | `benchmarks/` | Performance-critical paths | Benchmark suite |
| Documentation | `docs/` | All modules | Markdown + Mermaid |

---

## 5. Dependency Flow Between Directories

```
┌─────────────────────────────────────────────────────────────┐
│                        apps/                                 │
│              (web, desktop, admin)                           │
└───────────┬─────────────┬─────────────┬────────────────────┘
            │             │             │
            ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                     packages/                                │
│  (ui, auth-core, config, event-bus, validation, errors)     │
└───────────┬─────────────────────────────┬──────────────────┘
            │                             │
            ▼                             ▼
┌──────────────────────┐    ┌────────────────────────────────┐
│     libraries/       │    │          plugins/               │
│ (vendored forks)     │    │   (plugin implementations)     │
└──────────────────────┘    └────────────────────────────────┘
            │                             │
            ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     services/                                │
│          (worker, scheduler, webhook-relay)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              backend/  (FastAPI application)                 │
└─────────────────────────────────────────────────────────────┘
```

**Arrow direction = "may depend on."** Dependencies flow downward only. A package in a lower layer must never import from an upper layer.

### 5.1 Allowed Dependency Directions

| From | To | Allowed? |
|---|---|---|
| `apps/` → `packages/` | Yes |
| `apps/` → `backend/` | Yes (HTTP client only) |
| `apps/` → `plugins/` | No |
| `packages/` → `packages/` | Yes (explicit only) |
| `packages/` → `apps/` | **No** |
| `services/` → `packages/` | Yes |
| `services/` → `backend/` | Yes (event bus only) |
| `plugins/` → `packages/` | Yes |
| `plugins/` → `apps/` | **No** |
| `libraries/` → `packages/` | **No** |
| `backend/` → `packages/` | Yes |
| `backend/` → `services/` | **No** (event bus only) |

---

## 6. Build Isolation Principles

### 6.1 Principle: No Implicit Dependencies

Every import must be declared explicitly in the package manifest. Auto-discovery of modules is forbidden.

### 6.2 Principle: Build-Time Boundary Enforcement

The `tools/analyzers/` directory contains a dependency graph validator that runs in CI. It parses all `package.json`, `pyproject.toml`, and `__init__.py` files and validates that no forbidden imports exist.

### 6.3 Principle: Incremental Builds

Only changed packages and their downstream dependents are rebuilt. The build system maintains a dependency graph (`configs/dependency-graph.json`) that is updated on every commit.

### 6.4 Principle: Reproducible Builds

All builds run in containerized environments with pinned tool versions. No build may depend on the host machine's state.

### 6.5 Principle: Output Isolation

Each buildable unit outputs to its own `dist/` or `build/` directory. No unit reads another unit's build output directory.

---

## 7. Shared Code Governance

### 7.1 Package Ownership

Every package in `packages/` has a designated **owner** (team or individual) recorded in the package's `CODEOWNERS`-equivalent file (`MAINTAINERS.md`).

### 7.2 Change Approval

| Package Tier | Change Type | Required Reviewers |
|---|---|---|
| Tier 1 (auth-core, event-bus) | API change | 2 senior engineers + 1 security review |
| Tier 1 | Bug fix | 1 senior engineer |
| Tier 2 (ui, validation, errors) | API change | 2 engineers |
| Tier 2 | Bug fix | 1 engineer |
| Tier 3 (config, logging) | Any change | 1 engineer |

### 7.3 Deprecation Process

1. Mark the API with `@deprecated` or `# deprecated`.
2. Add a migration guide to `docs/guides/`.
3. Maintain backward compatibility for at least 2 minor versions.
4. Remove after the deprecation window expires.

### 7.4 Breaking Change Policy

Breaking changes to Tier 1 or Tier 2 packages require:
- A RFC in `governance/RFC_TEMPLATE.md`
- Approval from at least 2 code owners
- A migration guide published before merge
- A changelog entry with migration instructions

---

## 8. Configuration Management Hierarchy

Configuration is loaded in a strict priority order. Higher-priority sources override lower-priority ones.

```
┌─────────────────────────────────────────────┐
│  1. Environment Variables (highest)          │
│     AUTHSHIELD_<MODULE>_<KEY>                │
├─────────────────────────────────────────────┤
│  2. Local Config File                        │
│     ./authshield.local.json                  │
├─────────────────────────────────────────────┤
│  3. User Config File                         │
│     ~/.config/authshield/config.json         │
├─────────────────────────────────────────────┤
│  4. Application Config                       │
│     apps/<app>/config/<env>.json             │
├─────────────────────────────────────────────┤
│  5. Shared Config                            │
│     configs/shared.json                      │
├─────────────────────────────────────────────┤
│  6. Package Defaults (lowest)                │
│     packages/config/defaults.json            │
└─────────────────────────────────────────────┘
```

### 8.1 Configuration Namespacing

Every configuration key is namespaced by module:

```json
{
  "auth": { "session_ttl": 3600, "max_attempts": 5 },
  "users": { "default_role": "viewer" },
  "audit": { "retention_days": 365 },
  "defense": { "rate_limit_enabled": true }
}
```

### 8.2 Secrets Management

- Secrets are **never** stored in configuration files.
- Secrets are injected via environment variables or a secrets manager.
- The `packages/config/` module validates that no secret values are logged or serialized.

### 8.3 Configuration Validation

All configuration is validated against JSON schemas in `configs/schemas/` at application startup. Invalid configuration causes an immediate, descriptive error—no silent fallbacks.

---

## 9. Workspace Tooling

| Tool | Location | Purpose |
|---|---|---|
| Boundary Enforcer | `tools/linters/boundary-check.py` | Validates import boundaries |
| Dep Graph Builder | `tools/analyzers/build-graph.py` | Generates `dependency-graph.json` |
| Schema Validator | `tools/validators/validate-schemas.py` | Validates config and manifest schemas |
| Template Generator | `scripts/scaffold/` | Scaffolds new modules and components |
| License Scanner | `security/tools/license-check.py` | Scans for license incompatibilities |
| Secret Scanner | `security/tools/secret-scanner.py` | Detects committed secrets |
| i18n Extractor | `localization/tools/extract-translations.py` | Extracts strings for translation |

---

## 10. References

- [MODULE_BOUNDARIES.md](./MODULE_BOUNDARIES.md) — Module-level boundary definitions
- [CROSS_CUTTING_CONCERNS.md](./CROSS_CUTTING_CONCERNS.md) — Cross-cutting concern implementations
- [SERVICE_COMMUNICATION.md](./SERVICE_COMMUNICATION.md) — Inter-service communication patterns
- [DATA_FLOW.md](./DATA_FLOW.md) — Request and event lifecycle
- [DEPENDENCY_GRAPH.json](./DEPENDENCY_GRAPH.json) — Machine-readable dependency graph
- [DECISIONS.md](../architecture/DECISIONS.md) — Architecture decision records index
- [SHARED_LIBRARIES.md](../standards/SHARED_LIBRARIES.md) — Shared library conventions
- [CONFIGURATION_MANAGEMENT.md](../standards/CONFIGURATION_MANAGEMENT.md) — Configuration standards
