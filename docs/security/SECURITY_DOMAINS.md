# AuthShield Lab — Security Domain Catalog

## 1. Overview

This document defines the security domain catalog for AuthShield Lab. Each domain is a logical
grouping of security responsibilities with clear ownership, controls, audit requirements, and
dependencies. Domains do not map 1:1 to code modules — they map to security concerns that
span multiple modules.

## 2. Domain Inventory

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY DOMAIN MAP                        │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   IDENTITY & ACCESS                      │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │ Identity │  │Authentication│  │  Authorization   │  │  │
│  │  └──────────┘  └──────────────┘  └──────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   DATA PROTECTION                        │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │ Storage  │  │    Backup    │  │  Configuration   │  │  │
│  │  └──────────┘  └──────────────┘  └──────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   PLATFORM INTEGRITY                     │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │ Plugins  │  │     SDK      │  │     Logging      │  │  │
│  │  └──────────┘  └──────────────┘  └──────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   GOVERNANCE & OPERATIONS                 │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │  Audit   │  │Administration│  │  Diagnostics     │  │  │
│  │  └──────────┘  └──────────────┘  └──────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   APPLICATION FEATURES                   │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │ Learning │  │  Assessment  │  │   Reporting      │  │  │
│  │  │ Modules  │  │   System     │  │     Engine       │  │  │
│  │  └──────────┘  └──────────────┘  └──────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   CROSS-CUTTING                          │  │
│  │  ┌──────────────┐  ┌──────────────────────────────┐    │  │
│  │  │Accessibility │  │      Localization             │    │  │
│  │  └──────────────┘  └──────────────────────────────┘    │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 3. Domain Specifications

---

### 3.1 Identity Domain

**Responsibilities:** User lifecycle management, credential storage, profile management, account states.

| Attribute | Details |
|-----------|---------|
| **Owner** | Security Team |
| **Modules** | `auth/identity.py`, `models/user.py`, `services/user_service.py` |
| **Data Classification** | Confidential (credentials), Internal (profiles) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Password hashing | Preventive | Argon2id with memory-hard parameters (64MB minimum, 3 iterations) |
| Salt generation | Preventive | Cryptographically random 16-byte per-user salt |
| Credential storage | Preventive | Hashed passwords only; never plaintext; never reversible |
| Account lifecycle | Preventive | States: Active, Locked, Deactivated, Deleted; state transitions logged |
| Profile protection | Preventive | Profile changes require current-password verification |
| Username uniqueness | Preventive | Case-insensitive uniqueness constraint |
| Password policy | Preventive | Minimum 8 characters; complexity requirements configurable |
| Password history | Preventive | Last N passwords remembered; reuse prevented |

**Audit Requirements:**
- User creation (admin who created, new user, timestamp).
- User modification (who changed, what changed, old/new values).
- User deactivation/deletion (who, when, reason).
- Password changes (user, timestamp, method).
- Account lockouts (user, reason, lockout duration).

**Dependencies:**
- Authentication Domain (credential verification).
- Authorization Domain (role assignment on creation).
- Logging Domain (audit trail).
- Storage Domain (data persistence).

---

### 3.2 Authentication Domain

**Responsibilities:** Login/logout, MFA, credential verification, session creation, brute force protection.

| Attribute | Details |
|-----------|---------|
| **Owner** | Security Team |
| **Modules** | `auth/authentication.py`, `auth/mfa.py`, `auth/session.py` |
| **Data Classification** | Confidential (session tokens), Internal (MFA secrets) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| MFA (TOTP) | Preventive | RFC 6238 compliant; 30-second window; ±1 step tolerance |
| Account lockout | Preventive | Configurable threshold (default 5 failures); 15-minute lockout |
| Progressive delay | Preventive | 1s → 2s → 4s → 8s → 16s between attempts |
| Session token security | Preventive | 256-bit tokens; server-side only; validated on every request |
| Session timeout | Preventive | 30-minute idle; 8-hour absolute; configurable |
| Session regeneration | Preventive | Regenerated on privilege change, MFA setup |
| Constant-time comparison | Preventive | Hash comparison uses constant-time algorithm |
| Login rate limiting | Preventive | Per-user and global rate limits on login endpoint |

**Audit Requirements:**
- Login success (user, timestamp, device fingerprint).
- Login failure (user, timestamp, reason, source IP).
- MFA setup/change (user, timestamp, method).
- Session creation/invalidation (user, token ID, reason).
- Account lockout events (user, trigger, duration).
- Brute force detection alerts.

**Dependencies:**
- Identity Domain (user verification).
- Session Management (token lifecycle).
- Logging Domain (audit trail).
- Security Observability (alerting).

---

### 3.3 Authorization Domain

**Responsibilities:** RBAC, permission management, role assignments, access control decisions.

| Attribute | Details |
|-----------|---------|
| **Owner** | Security Team |
| **Modules** | `auth/authorization.py`, `auth/rbac.py`, `models/role.py` |
| **Data Classification** | Internal (roles, permissions) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| RBAC enforcement | Preventive | Middleware on every API endpoint; default deny |
| Permission granularity | Preventive | Operation-level permissions (resource:action format) |
| Role hierarchy | Preventive | Learner < Educator < Admin < Super Admin |
| Default deny | Preventive | All permissions denied unless explicitly granted |
| Permission cache | Performance | TTL-based cache (5 min); invalidated on role change |
| Admin re-auth | Preventive | Sensitive operations require password + MFA verification |
| Separation of duties | Preventive | Critical operations require multiple admin approvals |
| Permission audit | Detective | All permission changes logged with before/after values |

**Audit Requirements:**
- Permission grants/revocations (granter, grantee, permission, timestamp).
- Role assignments/changes (assigner, assignee, old role, new role).
- Authorization failures (user, resource, action, reason).
- Admin action authorization (admin, action, outcome).
- Separation of duties violations.

**Dependencies:**
- Identity Domain (user identification).
- Authentication Domain (session validity).
- Logging Domain (audit trail).
- Configuration Domain (role definitions).

---

### 3.4 Configuration Domain

**Responsibilities:** System configuration integrity, secure defaults, change control, rollback capability.

| Attribute | Details |
|-----------|---------|
| **Owner** | Platform Team |
| **Modules** | `config/configuration.py`, `config/schema.py`, `config/validator.py` |
| **Data Classification** | Internal (system settings), Confidential (security policy) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| HMAC signatures | Preventive | SHA-256 HMAC on all config files; verified before use |
| Schema validation | Preventive | JSON Schema validation on every config load |
| Admin-only modification | Preventive | Configuration changes require admin authentication |
| Change audit logging | Detective | Old value, new value, actor, timestamp logged |
| Rollback capability | Recovery | Previous configuration preserved; rollback available |
| Secure defaults | Preventive | Most restrictive safe settings as defaults |
| Integrity checks | Detective | Configuration integrity verified at startup and before use |
| Version tracking | Detective | Configuration version incremented on every change |

**Audit Requirements:**
- Configuration modifications (who, what, old/new, when).
- Configuration integrity check results.
- Rollback events (who triggered, to what version).
- Schema validation failures.
- Default configuration usage (unmodified defaults).

**Dependencies:**
- Logging Domain (audit trail).
- Storage Domain (config file persistence).
- Security Observability (integrity monitoring).

---

### 3.5 Storage Domain

**Responsibilities:** Database encryption, key management, data classification, file protection, WAL management.

| Attribute | Details |
|-----------|---------|
| **Owner** | Platform Team |
| **Modules** | `storage/database.py`, `storage/encryption.py`, `storage/file_manager.py` |
| **Data Classification** | Varies per data type (see data classification matrix) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Encryption at rest | Preventive | SQLCipher (AES-256) for database; AES-256-GCM for files |
| WAL protection | Preventive | Separate file permissions; checksummed; protected during writes |
| File permissions | Preventive | Sensitive files: 0600; logs: 0640; directories: 0700 |
| Path validation | Preventive | All file access validated against allowlist of base directories |
| Symlink protection | Preventive | Symlinks resolved and validated before access |
| Atomic operations | Integrity | File writes use atomic rename pattern |
| Integrity checks | Detective | Database integrity check on startup; periodic verification |
| Key management | Preventive | Encryption keys derived from user passphrases (Argon2id); never stored in plaintext |

**Data Classification Matrix:**

| Data Type | Classification | Encryption | Access Control |
|-----------|---------------|------------|----------------|
| User passwords | Critical | Argon2id hash (irreversible) | Authentication system only |
| Session tokens | Confidential | Server-side storage | Session manager only |
| User profiles | Internal | At-rest encryption | User + Admin |
| Learning content | Internal | At-rest encryption | Enrolled users |
| Assessment data | Confidential | At-rest encryption | Enrolled users + Educators |
| Audit logs | Internal | Integrity chain | Admin + Audit system |
| Configuration | Internal | HMAC-signed | Admin only |
| Backups | Critical | AES-256-GCM encrypted | Admin with passphrase |
| Plugin data | Internal | Per-plugin encryption | Plugin + Admin |

**Audit Requirements:**
- Database access patterns (unusual query detection).
- File access logging (all file operations on sensitive files).
- Key management operations (creation, rotation, derivation).
- Integrity check results (startup, periodic).
- Encryption/decryption operations (success/failure).

**Dependencies:**
- Configuration Domain (encryption settings).
- Logging Domain (access logging).
- Backup Domain (data preservation).

---

### 3.6 Plugin Domain

**Responsibilities:** Plugin lifecycle, signature verification, sandboxing, capability enforcement, resource limits.

| Attribute | Details |
|-----------|---------|
| **Owner** | Plugin Security Team |
| **Modules** | `plugins/loader.py`, `plugins/sandbox.py`, `plugins/permissions.py` |
| **Data Classification** | Internal (plugin metadata), Confidential (plugin storage) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Signature verification | Preventive | Ed25519 signatures required; verified before loading |
| Process sandboxing | Preventive | Plugins run in isolated processes with restricted capabilities |
| Permission enforcement | Preventive | Explicit capability grants; validated on every API call |
| Resource limits | Preventive | CPU, memory, execution time limits per plugin |
| Storage isolation | Preventive | Each plugin has isolated storage directory |
| API gateway | Preventive | All plugin calls go through validated API layer |
| Revocation capability | Recovery | Plugins can be disabled instantly |
| Integrity monitoring | Detective | Plugin integrity verified on every load and periodically |
| Behavior profiling | Detective | Plugin API usage patterns tracked for anomalies |

**Plugin Permission Catalog:**

| Permission | Scope | Risk Level | Requires Approval |
|------------|-------|------------|-------------------|
| `plugin:storage:read` | Own storage only | Low | No |
| `plugin:storage:write` | Own storage only | Low | No |
| `plugin:storage:delete` | Own storage only | Low | No |
| `plugin:content:read` | Learning modules | Medium | Yes (first install) |
| `plugin:ui:render` | Custom UI components | Medium | Yes (first install) |
| `plugin:event:subscribe` | Application events | Low | No |
| `plugin:event:emit` | Application events | Medium | Yes (first install) |
| `plugin:config:read` | Plugin config only | Low | No |
| `plugin:config:write` | Plugin config only | Low | No |

**Audit Requirements:**
- Plugin installation/removal (admin, plugin, version, timestamp).
- Plugin permission changes (who, what permission, granted/denied).
- Plugin integrity check results (pass/fail, details).
- Plugin API call patterns (unusual behavior detection).
- Plugin resource usage (CPU, memory, time).
- Plugin security violations (type, severity, action taken).

**Dependencies:**
- Storage Domain (plugin data persistence).
- Configuration Domain (plugin settings).
- Logging Domain (audit trail).
- Security Observability (behavior monitoring).

---

### 3.7 SDK Domain

**Responsibilities:** API security, version validation, deprecation management, compatibility enforcement.

| Attribute | Details |
|-----------|---------|
| **Owner** | Plugin Security Team |
| **Modules** | `sdk/api.py`, `sdk/validator.py`, `sdk/versioning.py` |
| **Data Classification** | Internal (API contracts) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Semantic versioning | Preventive | Strict version compatibility checking |
| API schema validation | Preventive | All API calls validated against current schema |
| Deprecation warnings | Detective | Deprecated API usage logged and warned |
| Breaking change detection | Preventive | Breaking changes require major version bump |
| API documentation | Preventive | Security implications documented for each API |
| Rate limiting | Preventive | SDK call rate limits per plugin |

**Audit Requirements:**
- API version mismatches (plugin, requested version, current version).
- Deprecated API usage (plugin, API, deprecation date).
- Breaking change introductions (version, change, impact).
- SDK compatibility test results.

**Dependencies:**
- Plugin Domain (plugin lifecycle).
- Configuration Domain (version settings).
- Logging Domain (usage logging).

---

### 3.8 Logging Domain

**Responsibilities:** Structured log generation, log integrity, tamper-resistant storage, log rotation.

| Attribute | Details |
|-----------|---------|
| **Owner** | Platform Team |
| **Modules** | `logging/logger.py`, `logging/rotation.py`, `logging/integrity.py` |
| **Data Classification** | Internal (operational logs), Confidential (security logs) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Structured logging | Preventive | JSON-formatted logs with consistent schema |
| Log integrity chains | Detective | Each log entry includes hash of previous entry |
| Tamper resistance | Detective | Log file HMAC verification; append-only enforcement |
| Log rotation | Preventive | Configurable rotation policy; old logs archived securely |
| Log access control | Preventive | Log files have restricted permissions (0640) |
| Sensitive data filtering | Preventive | Passwords, tokens, keys never logged |
| Log level controls | Preventive | Debug logging disabled in production; admin-controlled |
| Log retention | Preventive | Configurable retention with automatic cleanup |

**Audit Requirements:**
- Log integrity verification results (periodic).
- Log access attempts (who accessed log files).
- Log tampering detection (integrity chain breaks).
- Log rotation events.
- Sensitive data exposure in logs (scanning results).

**Dependencies:**
- Storage Domain (log file persistence).
- Configuration Domain (log settings).
- Security Observability (log analysis).

---

### 3.9 Audit Domain

**Responsibilities:** Immutable audit trail, chain verification, retention management, audit reporting.

| Attribute | Details |
|-----------|---------|
| **Owner** | Security Team |
| **Modules** | `audit/trail.py`, `audit/verifier.py`, `audit/reporter.py` |
| **Data Classification** | Internal (audit records) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Immutable audit trail | Preventive | Append-only storage; no delete/update operations |
| Hash chain integrity | Detective | Each entry includes SHA-256 hash of previous entry |
| Chain verification | Detective | Periodic verification of entire audit chain |
| Tamper detection | Detective | Broken chain immediately detected and alerted |
| Retention management | Preventive | Configurable retention; old entries archived |
| Access control | Preventive | Audit logs readable by admin only; not modifiable |
| Structured format | Preventive | Machine-readable format for automated analysis |
| Export capability | Recovery | Admin can export audit trail for external review |

**Audit Requirements:**
- The audit system itself is audited by the Security Observability system.
- Chain verification runs on application startup and periodically.
- Any integrity failure triggers immediate security alert.
- Audit log access is logged in the Security Observability system.

**Dependencies:**
- Logging Domain (log infrastructure).
- Storage Domain (audit data persistence).
- Configuration Domain (retention settings).

---

### 3.10 Backup Domain

**Responsibilities:** Backup creation, encryption, integrity verification, restoration, retention.

| Attribute | Details |
|-----------|---------|
| **Owner** | Platform Team |
| **Modules** | `backup/creator.py`, `backup/encryptor.py`, `backup/restorer.py` |
| **Data Classification** | Critical (backup data) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Backup encryption | Preventive | AES-256-GCM; key derived from user passphrase via Argon2id |
| Integrity manifests | Preventive | SHA-256 checksums for all backup components |
| Access control | Preventive | Admin authentication required for backup operations |
| Retention policies | Preventive | Configurable retention; automatic cleanup of old backups |
| Integrity verification | Detective | Backup integrity verified before every restore |
| Size limits | Preventive | Maximum backup size enforced |
| Frequency limits | Preventive | Minimum interval between backups enforced |
| Secure deletion | Recovery | Backup files securely deleted when removed |

**Audit Requirements:**
- Backup creation (who, when, size, components, success/failure).
- Backup restoration (who, when, source version, success/failure).
- Backup deletion (who, when, reason).
- Backup integrity verification results.
- Backup encryption/decryption operations.
- Backup storage usage.

**Dependencies:**
- Storage Domain (data being backed up).
- Configuration Domain (backup settings).
- Logging Domain (backup audit trail).

---

### 3.11 Reporting Domain

**Responsibilities:** Report generation, data access control, output sanitization, data masking.

| Attribute | Details |
|-----------|---------|
| **Owner** | Platform Team |
| **Modules** | `reporting/engine.py`, `reporting/masking.py`, `reporting/templates.py` |
| **Data Classification** | Internal (reports), varies by content |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Role-based access | Preventive | Reports filtered by user permissions |
| Data masking | Preventive | Sensitive fields masked based on classification |
| Output sanitization | Preventive | Report output validated and sanitized |
| Template validation | Preventive | Report templates validated against schema |
| Temporary file cleanup | Preventive | Generated reports securely deleted after use |
| Audit logging | Detective | Report generation and access logged |

**Audit Requirements:**
- Report generation (who, what report, what data accessed).
- Report access (who viewed what report, when).
- Data masking application (what was masked, why).
- Temporary file cleanup (files created and deleted).

**Dependencies:**
- Storage Domain (report data).
- Authorization Domain (access control).
- Logging Domain (audit trail).

---

### 3.12 Learning Modules Domain

**Responsibilities:** Content integrity, progress protection, module access control, content versioning.

| Attribute | Details |
|-----------|---------|
| **Owner** | Education Team |
| **Modules** | `learning/modules.py`, `learning/progress.py`, `learning/content.py` |
| **Data Classification** | Internal (content), Confidential (progress data) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Content integrity | Preventive | Manifest checksums; version tracking |
| Content sanitization | Preventive | HTML purging; script removal on import |
| Progress protection | Preventive | Server-side storage; integrity validation |
| Access control | Preventive | Enrollment-based access; role-based content management |
| Change audit logging | Detective | Content modifications logged with diffs |
| Rollback capability | Recovery | Previous content versions preserved |

**Audit Requirements:**
- Content creation/modification (who, what, when, diff).
- Content access patterns (unusual bulk access detection).
- Progress data modifications (who changed, what changed).
- Content integrity verification results.

**Dependencies:**
- Storage Domain (content persistence).
- Authorization Domain (access control).
- Logging Domain (audit trail).

---

### 3.13 Assessment Domain

**Responsibilities:** Assessment creation, submission, grading, integrity, anti-cheating measures.

| Attribute | Details |
|-----------|---------|
| **Owner** | Education Team |
| **Modules** | `assessment/engine.py`, `assessment/submission.py`, `assessment/grading.py` |
| **Data Classification** | Confidential (assessment data, grades) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Server-side validation | Preventive | Answers validated server-side; client-side is cosmetic |
| Submission integrity | Preventive | Submission logged with timestamp and checksum |
| Grade protection | Preventive | Grade calculation server-side; modification requires admin |
| Attempt limits | Preventive | Configurable maximum attempts per assessment |
| Timing enforcement | Preventive | Submissions validated against time windows |
| Answer encryption | Preventive | Assessment answers encrypted at rest |
| Anti-tampering | Detective | Submission patterns analyzed for anomalies |

**Audit Requirements:**
- Assessment creation (who, what, when).
- Assessment submissions (who, when, answers, score).
- Grade modifications (who changed, old/new grade, reason).
- Timing violations (submission outside allowed window).
- Pattern anomalies (unusual submission behavior).

**Dependencies:**
- Learning Modules Domain (content association).
- Authorization Domain (access control).
- Storage Domain (data persistence).
- Logging Domain (audit trail).

---

### 3.14 Administration Domain

**Responsibilities:** Admin authentication, privileged access, approval workflows, segregation of duties.

| Attribute | Details |
|-----------|---------|
| **Owner** | Security Team |
| **Modules** | `admin/management.py`, `admin/approval.py`, `admin/audit.py` |
| **Data Classification** | Confidential (admin actions), Internal (admin configurations) |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Admin MFA | Preventive | MFA required for all admin accounts |
| Re-authentication | Preventive | Password + MFA for sensitive operations |
| Approval workflows | Preventive | Critical changes require second admin approval |
| Segregation of duties | Preventive | No single admin can perform all critical operations |
| Shorter session timeout | Preventive | 15-minute idle timeout for admin sessions |
| Admin action logging | Detective | All admin actions immutably logged |
| Privilege change approval | Preventive | Role changes require higher-level approval |
| Admin account monitoring | Detective | Admin login patterns and actions monitored |

**Admin Operations Classification:**

| Operation | Sensitivity | Requirements |
|-----------|-------------|--------------|
| View user list | Low | Admin auth |
| Create user | Medium | Admin auth + audit |
| Modify user role | High | Admin re-auth + higher-level approval |
| Delete user | Critical | Admin re-auth + confirmation + audit |
| Install plugin | High | Admin re-auth + permission review |
| Modify security policy | Critical | Super Admin re-auth + second Super Admin approval |
| Modify audit configuration | Critical | Super Admin re-auth + second Super Admin approval |
| Create backup | Medium | Admin auth + audit |
| Restore backup | High | Admin re-auth + confirmation + audit |
| View audit logs | Medium | Admin auth + audit |

**Audit Requirements:**
- All admin actions logged (admin, action, target, timestamp, outcome).
- Admin login patterns (unusual access times, locations).
- Approval workflow events (request, approve/reject, reason).
- Segregation of duties compliance.
- Privilege escalation attempts.

**Dependencies:**
- Authentication Domain (admin authentication).
- Authorization Domain (admin permissions).
- Logging Domain (audit trail).
- Security Observability (admin monitoring).

---

### 3.15 Diagnostics Domain

**Responsibilities:** Data masking in diagnostics, permission checks, privacy protection, troubleshooting support.

| Attribute | Details |
|-----------|---------|
| **Owner** | Platform Team |
| **Modules** | `diagnostics/collector.py`, `diagnostics/masker.py`, `diagnostics/reporter.py` |
| **Data Classification** | Internal (diagnostic data), varies by content |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Data masking | Preventive | Sensitive fields masked in all diagnostic output |
| Permission checks | Preventive | Admin access required for diagnostic tools |
| Output sanitization | Preventive | Diagnostic output validated before display |
| No data modification | Preventive | Diagnostic tools are read-only |
| Access logging | Detective | Diagnostic tool usage logged |
| Retention limits | Preventive | Diagnostic data retained for limited time |

**Diagnostic Data Masking Rules:**

| Data Type | Masking Rule |
|-----------|-------------|
| Passwords | Fully masked (never displayed) |
| Session tokens | Fully masked (never displayed) |
| Encryption keys | Fully masked (never displayed) |
| User emails | Partially masked (e.g., `u***@example.com`) |
| IP addresses | Partially masked for external (localhost shown) |
| Plugin storage | Masked unless owner is viewing |
| Database contents | Masked unless admin is viewing |

**Audit Requirements:**
- Diagnostic tool access (who, what tool, when).
- Diagnostic output generated (what data was included).
- Data masking application (what was masked).

**Dependencies:**
- Storage Domain (data access).
- Authorization Domain (permission checks).
- Logging Domain (access logging).

---

### 3.16 Accessibility Domain

**Responsibilities:** Secure accessibility features, prevent accessibility-based attacks, accessible security controls.

| Attribute | Details |
|-----------|---------|
| **Owner** | UX Team + Security Team |
| **Modules** | `accessibility/` directory |
| **Data Classification** | Internal |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Accessible authentication | Preventive | Authentication forms are screen-reader compatible; no CAPTCHAs that exclude users |
| Secure ARIA labels | Preventive | Security-sensitive elements have appropriate ARIA labels |
| Keyboard navigation security | Preventive | All security actions accessible via keyboard; no keyboard-only bypasses |
| Accessibility announcements | Preventive | Security events announced to screen readers |
| Focus management | Preventive | Focus trapped in security dialogs; prevents clickjacking |

**Audit Requirements:**
- Accessibility compliance testing (WCAG 2.1 AA).
- Security control accessibility verification.
- Accessibility-based attack surface review.

**Dependencies:**
- Authentication Domain (accessible login).
- Authorization Domain (accessible permission displays).
- Presentation Layer (accessible UI components).

---

### 3.17 Localization Domain

**Responsibilities:** Locale validation, injection prevention in localized content, secure translation handling.

| Attribute | Details |
|-----------|---------|
| **Owner** | Platform Team |
| **Modules** | `localization/` directory |
| **Data Classification** | Internal |

**Security Controls:**

| Control | Type | Implementation |
|---------|------|----------------|
| Locale validation | Preventive | Locale codes validated against supported list |
| Translation injection prevention | Preventive | Translation strings sanitized; no code execution |
| Unicode safety | Preventive | Unicode normalization; homoglyph detection |
| RTL support security | Preventive | Bidirectional text handled safely |
| Format string protection | Preventive | User-controlled strings never used in format operations |

**Audit Requirements:**
- Locale validation results.
- Translation file integrity.
- Unicode security testing.

**Dependencies:**
- Configuration Domain (locale settings).
- Storage Domain (translation file storage).
- Logging Domain (validation logging).

## 4. Domain Interaction Matrix

| Domain | Depends On | Is Depended On By |
|--------|-----------|-------------------|
| Identity | Storage, Logging | Authentication, Authorization, Administration |
| Authentication | Identity, Storage, Logging | Authorization, Administration, Session Management |
| Authorization | Identity, Authentication, Configuration | All feature domains |
| Configuration | Storage, Logging | All domains |
| Storage | — | All domains |
| Plugin | Storage, Configuration, Logging, SDK | — |
| SDK | Plugin, Configuration | Plugin |
| Logging | Storage | All domains, Audit |
| Audit | Logging, Storage | Security Observability |
| Backup | Storage, Configuration, Logging | — |
| Reporting | Storage, Authorization, Logging | — |
| Learning Modules | Storage, Authorization, Logging | Assessment |
| Assessment | Learning Modules, Storage, Authorization, Logging | — |
| Administration | Authentication, Authorization, Logging | All domains (admin operations) |
| Diagnostics | Storage, Authorization, Logging | — |
| Accessibility | Authentication, Authorization | — |
| Localization | Configuration, Storage | — |
