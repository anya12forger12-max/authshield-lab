# AuthShield Lab — Trust Boundary Model

## 1. Overview

Trust boundaries are the lines between components with different trust levels. Every boundary
is a potential attack surface. AuthShield Lab defines, documents, and enforces validation at
every trust boundary in the system. This document specifies what each boundary protects, what
threats exist at each boundary, what controls are deployed, and what monitoring is in place.

## 2. Trust Boundary Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │  React   │  │ Electron │  │ Tailwind │  │  Renderer Process│    │
│  │ Components│ │  Shell   │  │  Styles  │  │  (Isolated)      │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘    │
│       │              │              │                 │              │
├───────┼──────────────┼──────────────┼─────────────────┼──────────────┤
│       │         TB-1: Presentation ↔ Application      │              │
│       │         (Input Validation, XSS Prevention)     │              │
├───────┼──────────────┼──────────────┼─────────────────┼──────────────┤
│       │              │              │                 │              │
│       ▼              ▼              ▼                 ▼              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  APPLICATION LAYER                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐     │   │
│  │  │   FastAPI   │  │   Router   │  │   Middleware Stack  │     │   │
│  │  │   App       │  │            │  │                     │     │   │
│  │  └──────┬─────┘  └──────┬─────┘  └──────────┬─────────┘     │   │
│  │         │               │                    │               │   │
├──┼─────────┼───────────────┼────────────────────┼───────────────┼───┤
│  │    TB-2: Application ↔ Domain Layer                        │   │
│  │    (Business Rule Enforcement, Authorization)              │   │
├──┼─────────┼───────────────┼────────────────────┼───────────────┼───┤
│  │         ▼               ▼                    ▼               │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │                  DOMAIN LAYER                         │   │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │   │
│  │  │  │ Services │  │ Entities │  │ Business Rules    │   │   │   │
│  │  │  └────┬─────┘  └──────────┘  └──────────────────┘   │   │   │
│  │  └───────┼──────────────────────────────────────────────┘   │   │
│  │          │                                                   │   │
├──┼──────────┼──────────────────────────────────────────────────┼───┤
│  │     TB-3: Domain ↔ Infrastructure Layer                     │   │
│  │     (Dependency Inversion, Interface Contracts)             │   │
├──┼──────────┼──────────────────────────────────────────────────┼───┤
│  │          ▼                                                   │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │              INFRASTRUCTURE LAYER                     │   │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │   │
│  │  │  │Database  │  │  File    │  │  External         │   │   │   │
│  │  │  │ Access   │  │  I/O     │  │  Services         │   │   │   │
│  │  │  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │   │   │
│  │  └───────┼──────────────┼────────────────┼──────────────┘   │   │
│  └──────────┼──────────────┼────────────────┼──────────────────┘   │
│             │              │                │                       │
├─────────────┼──────────────┼────────────────┼───────────────────────┤
│        TB-4: Infrastructure ↔ Persistence Layer                    │
│        (SQL Injection Prevention, Data Integrity)                  │
├─────────────┼──────────────┼────────────────┼───────────────────────┤
│             ▼              ▼                ▼                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   PERSISTENCE LAYER                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │  │
│  │  │ SQLite   │  │  Config  │  │   Logs   │  │  Backups   │  │  │
│  │  │ Database │  │  Files   │  │          │  │            │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────────────────┐
        │              PLUGIN RUNTIME                    │
        │  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
        │  │ Plugin A │  │ Plugin B │  │ Plugin C   │  │
        │  │(Sandboxed)│ │(Sandboxed)│ │(Sandboxed) │  │
        │  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
        │       │              │               │         │
        │  ┌────▼──────────────▼───────────────▼──────┐  │
        │  │         Plugin Host (Sandbox)            │  │
        │  └──────────────────┬───────────────────────┘  │
        └─────────────────────┼──────────────────────────┘
                              │
                    TB-5: Application ↔ Plugin Runtime
                    (Sandboxing, Permission Enforcement)
```

## 3. Trust Boundary Definitions

Each boundary is defined with: assets protected, threats at the boundary, controls deployed,
validation rules, and monitoring requirements.

---

### TB-1: Presentation ↔ Application Layer

**Location:** Between the React/Electron renderer process and the FastAPI application layer.

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | Application logic, business rules, data models, backend state. |
| **Threats** | XSS injection, CSRF attacks, malformed input, parameter tampering, mass assignment, client-side code injection, prototype pollution. |
| **Controls** | Input validation on all API endpoints; output encoding on all responses; CSRF tokens; Content Security Policy headers; strict Content-Type validation; request size limits; parameter type enforcement. |
| **Validation Rules** | All inputs validated against JSON schemas; HTML stripped from text fields; URLs validated against allowlist; numeric ranges enforced; string lengths bounded; enum values enforced; nested object depth limited. |
| **Monitoring** | Log all rejected inputs; track input validation failure rates; alert on unusual patterns (e.g., spike in XSS attempts); audit all API requests. |

**Implementation:**

```python
# Input validation middleware
class InputValidationMiddleware:
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_NESTING_DEPTH = 10
    MAX_STRING_LENGTH = 10000
    
    async def validate_input(self, request: Request):
        body = await request.body()
        if len(body) > self.MAX_REQUEST_SIZE:
            raise HTTPException(413, "Request too large")
        
        data = json.loads(body)
        if self._get_nesting_depth(data) > self.MAX_NESTING_DEPTH:
            raise HTTPException(400, "Request too deeply nested")
        
        sanitized = self._sanitize(data)
        return sanitized
```

---

### TB-2: Application ↔ Domain Layer

**Location:** Between the FastAPI route handlers and the domain/business logic layer.

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | Business rules, domain entities, service logic, authorization decisions. |
| **Threats** | Business logic bypass, authorization circumvention, privilege escalation through business rule exploitation, incomplete validation. |
| **Controls** | Authorization decorators on all routes; business rule validation in services; domain entity invariants enforced; input sanitization at application layer before domain access; separation of concerns. |
| **Validation Rules** | Every route must have authorization; domain services validate business invariants; entities enforce integrity constraints; service boundaries respect permission boundaries. |
| **Monitoring** | Log all authorization decisions; track business rule violations; audit domain entity modifications; monitor service call patterns. |

**Implementation:**

```python
# Authorization decorator
def require_permission(permission: str):
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = request.state.user
            if not await rbac_service.check_permission(user, permission):
                await audit_log.record(
                    event="authorization.denied",
                    user=user.id,
                    permission=permission,
                    resource=func.__name__
                )
                raise HTTPException(403, "Forbidden")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

### TB-3: Domain ↔ Infrastructure Layer

**Location:** Between domain services and infrastructure implementations (database, file I/O, external services).

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | Domain logic from infrastructure concerns; infrastructure from domain misuse. |
| **Threats** | Infrastructure leakage into domain; domain logic coupled to specific storage; dependency inversion violations; interface contract breaches. |
| **Controls** | Dependency inversion principle; interface contracts between layers; repository pattern for data access; unit of work for transaction management; adapter pattern for external services. |
| **Validation Rules** | Domain layer never imports infrastructure directly; infrastructure implements domain-defined interfaces; interface contracts are tested; repository methods have defined pre/post conditions. |
| **Monitoring** | Track layer violations in static analysis; monitor interface contract compliance; audit infrastructure access patterns. |

---

### TB-4: Infrastructure ↔ Persistence Layer

**Location:** Between infrastructure code and persistent storage (SQLite, config files, logs, backups).

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | Data integrity, data confidentiality, database structure, stored data. |
| **Threats** | SQL injection, path traversal to database files, data corruption, unauthorized data modification, backup tampering, log injection, configuration file manipulation. |
| **Controls** | Parameterized queries only (SQLAlchemy ORM); path validation for all file access; WAL mode for atomicity; HMAC signatures on configuration; encrypted backups; append-only audit logs; integrity checksums on data files. |
| **Validation Rules** | All database queries use parameterized statements; file paths validated against allowlist; configuration files validated against schema before use; backup integrity verified before restore; database integrity check on startup. |
| **Monitoring** | Database integrity checks; file access logging; configuration change detection; backup integrity verification; unusual query pattern detection. |

**Implementation:**

```python
# Path traversal prevention
class PathValidator:
    ALLOWED_BASES = [
        Path("~/.config/authshield-lab").expanduser(),
        Path("~/.local/share/authshield-lab").expanduser(),
        Path("~/.cache/authshield-lab").expanduser(),
    ]
    
    def validate(self, requested_path: Path) -> Path:
        resolved = requested_path.resolve()
        for base in self.ALLOWED_BASES:
            try:
                resolved.relative_to(base)
                return resolved
            except ValueError:
                continue
        raise SecurityError(f"Path traversal detected: {requested_path}")
```

---

### TB-5: Application ↔ Plugin Runtime

**Location:** Between the core application and the plugin execution environment.

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | Core application state, other plugins' data, user data, system resources. |
| **Threats** | Plugin escaping sandbox, plugin accessing unauthorized data, plugin consuming excessive resources, plugin making unauthorized API calls, plugin modifying other plugins' state, plugin accessing host filesystem. |
| **Controls** | Process-level sandboxing; capability-based permission system; resource limits (CPU, memory, time); API gateway pattern (all plugin calls go through validated API); permission validation on every plugin API call; plugin storage isolation. |
| **Validation Rules** | Plugin signature verified before loading; permissions validated against policy; API calls logged and validated; resource usage monitored; sandbox integrity verified; plugin cannot access core database directly. |
| **Monitoring** | Plugin resource usage tracking; API call logging; sandbox escape detection; permission violation alerts; plugin behavior profiling. |

---

### TB-6: Application ↔ SDK

**Location:** Between the application and the Plugin SDK (APIs exposed to plugin developers).

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | SDK API contracts, plugin compatibility, application stability. |
| **Threats** | API breaking changes, version incompatibility, deprecated API usage, unexpected data types, resource exhaustion through API abuse. |
| **Controls** | Semantic versioning for SDK; API compatibility testing; deprecation warnings; input validation on all SDK methods; rate limiting on SDK calls; API documentation with security implications. |
| **Validation Rules** | SDK version validated at plugin load; API calls validated against current schema; deprecated APIs emit warnings; incompatible versions rejected; SDK changes require security review. |
| **Monitoring** | SDK usage statistics; deprecation warnings tracked; version mismatch detection; API error rates. |

---

### TB-7: Application ↔ Configuration System

**Location:** Between the application runtime and configuration files.

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | System configuration integrity, security policies, user preferences. |
| **Threats** | Configuration file tampering, unauthorized setting changes, downgrade attacks via old configuration, configuration injection, insecure defaults. |
| **Controls** | HMAC signatures on configuration files; schema validation on load; admin-only modification; change audit logging; rollback capability; secure defaults; integrity checks on startup and before each use. |
| **Validation Rules** | Configuration files validated against JSON schema; HMAC verified before loading; changes logged with before/after values; rollback preserves previous valid state; default values enforced for missing keys. |
| **Monitoring** | Configuration integrity checks; change frequency monitoring; unauthorized modification attempts; configuration drift detection. |

---

### TB-8: Application ↔ Backup System

**Location:** Between the application and backup creation/restoration.

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | Backup data confidentiality, backup integrity, restore reliability. |
| **Threats** | Backup data exposure, backup tampering, unauthorized restore, backup deletion, restore of corrupted backups, backup as exfiltration vector. |
| **Controls** | Backup encryption (AES-256-GCM); integrity manifests (SHA-256); access-controlled backup storage; restore validation; backup integrity verification before restore; admin-only backup operations; backup retention policies. |
| **Validation Rules** | Backup encryption verified before storage; integrity manifest validated; restore checks backup version compatibility; backup size limits enforced; backup frequency limits enforced. |
| **Monitoring** | Backup success/failure tracking; backup integrity verification; restore operation logging; backup storage usage monitoring. |

---

### TB-9: Application ↔ Reporting Engine

**Location:** Between the application and report generation.

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | Data privacy in reports, report accuracy, report access control. |
| **Threats** | Data leakage through reports, report tampering, unauthorized report access, excessive data exposure in reports. |
| **Controls** | Role-based report access; data masking in reports; report generation audit logging; report output validation; temporary report file cleanup; no raw data export without authorization. |
| **Validation Rules** | Report data filtered by user permissions; sensitive fields masked; report templates validated; generated reports validated against schema; temporary files securely deleted. |
| **Monitoring** | Report generation logging; report access tracking; data sensitivity classification enforcement; report output validation. |

---

### TB-10: Application ↔ Administration Tools

**Location:** Between the application and administrative interfaces.

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | System administration capabilities, admin accounts, system configuration. |
| **Threats** | Privilege escalation, unauthorized admin access, admin action abuse, admin account compromise, configuration manipulation through admin interface. |
| **Controls** | Admin re-authentication for sensitive operations; approval workflows for critical changes; comprehensive admin action audit logging; session management for admin actions; IP binding (where applicable); admin action rate limiting. |
| **Validation Rules** | Admin identity verified before every sensitive action; admin permissions validated per-operation; admin actions logged immutably; critical changes require confirmation; admin session has shorter timeout than regular sessions. |
| **Monitoring** | All admin actions logged; admin login patterns; admin action frequency; unusual admin behavior flagged. |

---

### TB-11: Application ↔ Diagnostic Tools

**Location:** Between the application and diagnostic/troubleshooting features.

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | User privacy, data confidentiality during diagnostics, diagnostic output safety. |
| **Threats** | Sensitive data exposure through diagnostics, diagnostic output used for information gathering, diagnostic tools used to bypass security controls. |
| **Controls** | Data masking in diagnostic output; permission checks before diagnostic access; diagnostic output sanitized; no raw data dumps; diagnostic tools require admin access; diagnostic sessions logged. |
| **Validation Rules** | Diagnostic output validated before display; sensitive fields masked; diagnostic access logged; diagnostic data retention limited; diagnostic tools cannot modify data. |
| **Monitoring** | Diagnostic tool usage logging; diagnostic output content review; unusual diagnostic access patterns flagged. |

---

### TB-12: Application ↔ External Import Packages

**Location:** Between the application and imported data (backup restores, content imports).

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | Application integrity, data integrity, import package isolation. |
| **Threats** | Malicious import packages, data injection through imports, import of corrupted data, import packages containing executable code, oversized imports causing resource exhaustion. |
| **Controls** | Import package validation (schema, integrity); sandboxed import processing; import size limits; import content sanitization; import approval workflow; import audit logging; rollback on import failure. |
| **Validation Rules** | Import package integrity verified; content validated against expected schema; executable content rejected; import size within limits; import version compatibility checked; import processed in isolated context. |
| **Monitoring** | Import attempt logging; import success/failure tracking; import content scanning; import size monitoring. |

---

### TB-13: Application ↔ Local File System

**Location:** Between the application and the host file system.

| Attribute | Details |
|-----------|---------|
| **Assets Protected** | Application files, user data files, system files, file system integrity. |
| **Threats** | Path traversal, symlink attacks, file permission escalation, file system race conditions, temporary file exposure, disk space exhaustion. |
| **Controls** | Path validation against allowlist; symlink resolution and validation; secure file permissions (0600 for sensitive files); atomic file operations; temporary file cleanup; disk usage monitoring; file locking for concurrent access. |
| **Validation Rules** | All file paths validated before access; resolved paths checked against allowlist; file permissions verified; temporary files created with secure permissions; file operations logged; file system calls validated. |
| **Monitoring** | File access logging; permission change detection; disk usage monitoring; unusual file access patterns flagged. |

## 4. Boundary Validation Matrix

| Boundary | Input Validation | Authorization | Integrity | Encryption | Monitoring |
|----------|-----------------|---------------|-----------|------------|------------|
| TB-1: Presentation ↔ App | Schema validation | Session + RBAC | Request signing | HTTPS (localhost) | Request logging |
| TB-2: App ↔ Domain | Parameter validation | Permission check | Entity invariants | N/A | Auth decision logging |
| TB-3: Domain ↔ Infra | Interface contracts | Layer isolation | Interface compliance | N/A | Layer violation detection |
| TB-4: Infra ↔ Persistence | Parameterized queries | Access control | Checksums | Encryption at rest | DB integrity checks |
| TB-5: App ↔ Plugin | API validation | Capability check | Signature verification | Plugin isolation | Behavior monitoring |
| TB-6: App ↔ SDK | Schema validation | Version check | API contract | N/A | Usage tracking |
| TB-7: App ↔ Config | Schema validation | Admin auth | HMAC signatures | Optional encryption | Change logging |
| TB-8: App ↔ Backup | Package validation | Admin auth | SHA-256 manifests | AES-256-GCM | Integrity verification |
| TB-9: App ↔ Report | Template validation | Role check | Output validation | N/A | Report logging |
| TB-10: App ↔ Admin | Input validation | Re-authentication | Action logging | N/A | Admin audit trail |
| TB-11: App ↔ Diagnostics | Output validation | Admin auth | Sanitization | N/A | Diagnostic logging |
| TB-12: App ↔ Import | Package validation | Approval workflow | Integrity check | Import isolation | Import logging |
| TB-13: App ↔ Filesystem | Path validation | Permission check | Atomic operations | File encryption | Access logging |

## 5. Boundary Enforcement Principles

1. **No boundary is optional.** Every boundary listed here is enforced in code and tested.
2. **Fail closed.** When a boundary check fails, access is denied, not granted.
3. **Defense at boundary.** Multiple controls at each boundary ensure redundancy.
4. **Audit everything.** Every boundary crossing is logged with sufficient detail for forensics.
5. **Validate early.** Input validation occurs at the outermost boundary possible.
6. **Trust nothing from the other side.** Even if data comes from a "trusted" component, validate it.

## 6. Boundary Testing

Each trust boundary is tested through:

| Test Type | Description | Frequency |
|-----------|-------------|-----------|
| **Unit Tests** | Test boundary validation logic in isolation | Every commit |
| **Integration Tests** | Test complete boundary crossing flows | Every commit |
| **Fuzz Tests** | Fuzz inputs at each boundary | Weekly |
| **Penetration Tests** | Attempt to cross boundaries maliciously | Per release |
| **Architecture Tests** | Verify layer dependencies are correct | Every commit |
| **Regression Tests** | Verify previously found boundary bypasses remain fixed | Every commit |
