# AuthShield Lab — Threat Model

## 1. Methodology

AuthShield Lab uses the **STRIDE** threat modeling framework, applied systematically to each
subsystem. STRIDE covers:

| Category | Description | Security Property |
|----------|-------------|-------------------|
| **S**poofing | Impersonating a user or component | Authentication |
| **T**ampering | Modifying data or code | Integrity |
| **R**epudiation | Denying an action occurred | Non-repudiation |
| **I**nformation Disclosure | Exposing data to unauthorized parties | Confidentiality |
| **D**enial of Service | Making the system unavailable | Availability |
| **E**levation of Privilege | Gaining unauthorized access levels | Authorization |

## 2. Threat Actor Profiles

### 2.1 Local User (Insider)

- **Motivation:** Curiosity, academic exploration, accidental misuse.
- **Capabilities:** Physical access to the machine; can run arbitrary software; can modify files with appropriate permissions; social engineering awareness.
- **Access Level:** Full local access; standard user account within the application.
- **Risk Level:** Medium — likely to trigger accidental issues rather than deliberate attacks, but must be defended against.

### 2.2 Malicious Plugin Author

- **Motivation:** Data exfiltration, privilege escalation, supply chain attack.
- **Capabilities:** Can craft malicious plugin packages; can attempt sandbox escape; can social-engineer plugin approval.
- **Access Level:** Plugin sandbox access; may attempt to escalate beyond sandbox.
- **Risk Level:** High — plugins are a primary attack surface.

### 2.3 Physical Attacker

- **Motivation:** Data theft, system compromise, disruption.
- **Capabilities:** Physical access to the device; can access storage directly; can modify boot process; can extract data from disk.
- **Access Level:** Full physical access; no application authentication.
- **Risk Level:** High — physical access significantly expands attack surface.

### 2.4 Supply Chain Attacker

- **Motivation:** Compromise the application through its dependencies.
- **Capabilities:** Can modify dependencies; can compromise build tools; can inject code during distribution.
- **Access Level:** Indirect — affects the application before it reaches the user.
- **Risk Level:** Medium-High — difficult to detect; requires proactive defenses.

## 3. Subsystem Threat Analysis

### 3.1 Authentication System

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Brute force password attack | Elevation of Privilege | High | Medium | Account lockout after N failures; progressive delays; CAPTCHA after threshold | Low | Login failure rate monitoring; alert on abnormal failure rates |
| Credential stuffing | Spoofing | High | Low | Unique per-user salts; Argon2id hashing; no credential reuse encouragement | Low | Login pattern analysis; anomalous login detection |
| Session token theft (memory) | Spoofing | High | Low | Short-lived tokens; token rotation; secure memory handling; process isolation | Low | Session anomaly detection; device fingerprint monitoring |
| Password hash extraction | Information Disclosure | Critical | Low | Argon2id (memory-hard); file permissions on database; encryption at rest | Low | Database integrity monitoring; file permission checks |
| MFA bypass via TOTP replay | Spoofing | High | Low | Time-window validation; one-time use enforcement; replay detection | Low | MFA attempt logging; replay detection |
| Password reset abuse | Elevation of Privilege | Medium | Low | Reset requires current password; rate-limited reset attempts; audit logging | Low | Reset attempt monitoring; admin notification |
| Timing attacks on authentication | Information Disclosure | Medium | Low | Constant-time comparison for hash verification; uniform error messages | Very Low | Unusual authentication timing patterns |

#### Controls

- Argon2id password hashing with configurable memory cost (minimum 64MB, time cost 3).
- Per-user random 16-byte salt stored alongside hash.
- MFA via TOTP with 30-second window, ±1 step tolerance.
- Account lockout after 5 failed attempts (configurable), 15-minute lockout duration.
- Progressive delay: 1s, 2s, 4s, 8s, 16s between attempts.
- Session tokens: 256-bit, validated on every request, 30-minute idle timeout.
- All authentication events logged with IP, timestamp, device fingerprint, outcome.

---

### 3.2 Authorization System

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Horizontal privilege escalation | Elevation of Privilege | High | Medium | RBAC enforcement on every request; resource-level access checks | Low | Authorization decision logging; cross-user access detection |
| Vertical privilege escalation | Elevation of Privilege | Critical | Low | Admin actions require re-authentication; permission check on every endpoint | Low | Admin action logging; unusual permission patterns |
| Role manipulation | Tampering | Critical | Low | Role changes require admin auth; role file signed; audit logged | Low | Role change monitoring; integrity verification |
| Permission bypass through API | Elevation of Privilege | High | Low | Middleware authorization; no endpoint bypasses RBAC; automated testing | Low | API access pattern monitoring; permission check coverage |
| Session role mismatch | Spoofing | Medium | Low | Role validated from session, not client; re-validated on every request | Low | Role change detection; session integrity checks |

#### Controls

- RBAC middleware on every API endpoint; default deny for undefined permissions.
- Role hierarchy: Learner < Educator < Admin < Super Admin.
- Permission granularity at operation level (resource:action).
- Admin actions require re-authentication (current password + MFA).
- Role changes logged immutably with before/after values.
- Automated tests verify authorization on every endpoint.
- Permission cache with TTL (5 minutes) and invalidation on role change.

---

### 3.3 Session Management

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Session fixation | Spoofing | High | Low | New session token on every authentication; token regeneration | Low | Session creation logging; fixation detection |
| Session hijacking | Spoofing | Critical | Low | Short-lived tokens; device fingerprint binding; continuous validation | Low | Session anomaly detection; device change detection |
| Session replay | Spoofing | Medium | Low | One-time use tokens for sensitive operations; timestamp validation | Low | Duplicate token detection; timing analysis |
| Session persistence after logout | Information Disclosure | Medium | Medium | Server-side session invalidation on logout; token wiped from client | Low | Session state logging; orphan session detection |
| Concurrent session abuse | Information Disclosure | Medium | Low | Configurable session limit; active session listing; remote session invalidation | Low | Concurrent session monitoring |

#### Controls

- Session tokens stored server-side only (SQLite); never in client-side storage.
- Token format: `secrets.token_urlsafe(32)` — 256 bits of entropy.
- Idle timeout: 30 minutes (configurable). Absolute timeout: 8 hours.
- Session regeneration on privilege change (role assignment, MFA setup).
- Active session listing available to user and admin.
- Remote session invalidation (admin can force-logout users).
- Session data encrypted at rest in SQLite.

---

### 3.4 Data Storage

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Database file extraction | Information Disclosure | Critical | Low | File permissions (0600); encryption at rest; database locked while running | Medium | File permission monitoring; access logging |
| SQL injection | Tampering | Critical | Low | SQLAlchemy ORM (parameterized queries); no raw SQL from user input | Very Low | Query pattern monitoring; SQL injection detection |
| Data corruption | Tampering | High | Medium | WAL mode; integrity checks; backup system; transaction isolation | Low | Database integrity monitoring; checksum validation |
| Unauthorized data export | Information Disclosure | High | Low | Export requires authorization; export audit logging; data classification | Low | Export monitoring; data access logging |
| Backup data exposure | Information Disclosure | Critical | Low | Backup encryption; access-controlled storage; passphrase protection | Low | Backup access logging; integrity verification |
| Configuration file tampering | Tampering | High | Low | HMAC signatures; admin-only modification; change audit logging | Low | Configuration integrity checks; change detection |

#### Controls

- SQLite with WAL mode for atomicity and crash recovery.
- Database encryption via SQLCipher (AES-256).
- File permissions: database 0600, config 0600, logs 0640.
- WAL file protection: separate file permissions, checksummed.
- Database integrity check on startup: `PRAGMA integrity_check`.
- All data modifications wrapped in transactions.
- Automated backup with configurable frequency and retention.
- Backup encryption with user-provided passphrase (Argon2id key derivation).

---

### 3.5 Plugin System

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Plugin sandbox escape | Elevation of Privilege | Critical | Low | Process-level isolation; capability enforcement; resource limits | Low | Sandbox monitoring; resource usage tracking |
| Malicious plugin data exfiltration | Information Disclosure | Critical | Medium | No direct filesystem access; API gateway pattern; permission enforcement | Medium | Plugin API call logging; data access monitoring |
| Plugin signature bypass | Tampering | Critical | Low | Ed25519 signature verification; signature required for loading | Low | Signature verification logging; integrity checks |
| Plugin resource exhaustion | Denial of Service | Medium | Medium | CPU limits; memory limits; execution time limits; plugin restart capability | Low | Resource usage monitoring; limit enforcement |
| Plugin-to-plugin interference | Tampering | High | Low | Storage isolation; no direct inter-plugin communication; mediated events | Low | Plugin behavior monitoring; interference detection |
| Malicious plugin update | Tampering | Critical | Low | Update requires re-verification; update audit logging; user approval | Low | Update monitoring; version tracking |

#### Controls

- Plugins run in isolated processes with restricted capabilities.
- Permission model: explicit grant required for each capability.
- Resource limits: configurable CPU, memory, and execution time limits.
- Plugin storage isolated: each plugin has its own storage directory.
- API gateway: all plugin calls go through validated API layer.
- Signature verification: Ed25519 signatures required for plugin installation.
- Plugin integrity verification on every load.
- Revocation capability: plugins can be disabled instantly.
- Comprehensive plugin API call logging.

---

### 3.6 Configuration System

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Configuration downgrade | Tampering | High | Low | Version tracking; rollback protection; integrity checksums | Low | Configuration version monitoring; downgrade detection |
| Insecure configuration injection | Tampering | Critical | Low | Schema validation; HMAC signatures; admin-only modification | Low | Configuration change monitoring; validation logging |
| Configuration file deletion | Denial of Service | Medium | Low | Automatic backup; recovery from defaults; graceful degradation | Low | Configuration file monitoring; deletion detection |
| Default configuration weakness | Tampering | Medium | Low | Secure defaults documented; hardening guide; configuration auditing | Low | Default value monitoring; hardening compliance |

#### Controls

- Configuration files HMAC-SHA256 signed; verified before each use.
- Schema validation on every configuration load.
- Admin authentication required for all configuration modifications.
- Configuration changes logged with before/after values.
- Rollback capability: previous configuration preserved.
- Secure defaults for all settings.
- Configuration integrity check on application startup.

---

### 3.7 Backup System

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Backup data theft | Information Disclosure | Critical | Low | AES-256-GCM encryption; user-provided passphrase; secure storage | Low | Backup access logging; storage monitoring |
| Backup tampering | Tampering | Critical | Low | SHA-256 integrity manifests; signature verification before restore | Low | Backup integrity monitoring; restore validation |
| Backup deletion | Denial of Service | High | Low | Multiple backup copies; retention policy; backup monitoring | Low | Backup count monitoring; deletion alerting |
| Restore of malicious backup | Tampering | Critical | Low | Backup validation before restore; sandboxed restore process | Low | Restore logging; backup integrity verification |
| Backup as exfiltration vector | Information Disclosure | High | Low | Backup requires authorization; backup audit logging; export limits | Low | Backup creation monitoring; data volume tracking |

#### Controls

- Backup encryption: AES-256-GCM with Argon2id-derived key.
- Integrity manifest: SHA-256 checksums for all backup components.
- Backup stored in user-designated directory with file permissions 0600.
- Admin authorization required for backup creation and restore.
- Backup retention policies with automatic cleanup.
- Backup integrity verified before every restore operation.
- Backup audit logging with creation time, size, components, and actor.

---

### 3.8 Import/Export System

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Malicious import package | Tampering | Critical | Low | Package validation; content sanitization; sandboxed processing | Low | Import monitoring; content scanning |
| Data exfiltration through export | Information Disclosure | High | Low | Export authorization; audit logging; data classification | Low | Export monitoring; data volume tracking |
| Import data injection | Tampering | High | Low | Schema validation; content sanitization; import sandboxing | Low | Import validation logging |
| Oversized import denial of service | Denial of Service | Medium | Low | Import size limits; resource monitoring; timeout enforcement | Low | Import size monitoring; resource tracking |

#### Controls

- Import packages validated against expected schema.
- Import content sanitized: HTML stripped, script tags removed, URLs validated.
- Import processed in isolated context with resource limits.
- Export requires authorization and is audit-logged.
- Export data classified by sensitivity; sensitive fields masked.
- Import/export size limits enforced.
- Import/export operations logged with full details.

---

### 3.9 Learning Content

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Content tampering | Tampering | High | Low | Content integrity checksums; manifest verification; version control | Low | Content integrity monitoring |
| Content injection (XSS in learning materials) | Tampering | High | Low | Content sanitization; CSP enforcement; output encoding | Low | Content validation logging |
| Unauthorized content modification | Tampering | High | Low | Role-based content access; edit authorization; change audit logging | Low | Content change monitoring |
| Progress data manipulation | Tampering | Medium | Low | Progress stored server-side; integrity validation; audit logging | Low | Progress modification monitoring |

#### Controls

- Learning content integrity verified via manifest checksums.
- Content stored with version information for rollback.
- Content modifications require Educator or Admin role.
- All content changes logged with user, timestamp, and diff.
- Content sanitization on import (HTML purging, script removal).
- Progress data stored in database with integrity constraints.
- Content access controlled by enrollment and role.

---

### 3.10 Assessment System

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Answer manipulation | Tampering | High | Low | Server-side answer validation; submission integrity checks | Low | Assessment submission monitoring |
| Assessment bypass | Elevation of Privilege | High | Low | Role-based access; assessment completion requirements; audit logging | Low | Assessment access monitoring |
| Grade tampering | Tampering | Critical | Low | Grade calculation server-side; grade change audit logging; admin-only modification | Low | Grade modification monitoring |
| Cheating detection evasion | Repudiation | Medium | Low | Timestamp validation; submission pattern analysis; attempt tracking | Low | Submission pattern monitoring |

#### Controls

- Assessment answers validated server-side; client-side validation is cosmetic only.
- Assessment submissions logged with timestamp, answers, and user.
- Grade calculation performed server-side.
- Grade changes require admin authorization and are audit-logged.
- Assessment attempt limits enforced.
- Assessment timing validated (no submissions before start or after deadline).
- Assessment data encrypted at rest.

---

### 3.11 Administration

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Admin account compromise | Elevation of Privilege | Critical | Low | MFA required; session management; re-authentication for sensitive ops | Low | Admin login monitoring; unusual admin activity |
| Admin action abuse | Elevation of Privilege | High | Low | Comprehensive audit logging; segregation of duties; approval workflows | Low | Admin action monitoring; anomaly detection |
| Unauthorized admin creation | Elevation of Privilege | Critical | Low | Admin creation requires existing admin auth; approval workflow | Low | Admin account creation monitoring |
| Admin privilege escalation | Elevation of Privilege | Critical | Low | Role hierarchy enforced; privilege changes require higher-level approval | Low | Role change monitoring; privilege escalation detection |

#### Controls

- Admin accounts require MFA.
- Admin actions require re-authentication for sensitive operations.
- Critical operations require second admin approval.
- All admin actions logged immutably.
- Segregation of duties: no single admin can perform all operations.
- Admin session timeout: 15 minutes idle (shorter than regular users).
- Admin account creation logged and notified to other admins.
- Privilege escalation requires higher-level approval.

---

### 3.12 Local Network

#### STRIDE Analysis

| Threat | Type | Impact | Likelihood | Mitigation | Residual Risk | Monitoring |
|--------|------|--------|------------|------------|---------------|------------|
| Unauthorized network listener | Information Disclosure | High | Low | Localhost binding only; no external network access; network monitoring | Low | Network binding verification; connection monitoring |
| Man-in-the-middle (localhost) | Spoofing | Medium | Very Low | Localhost-only; no network authentication tokens transmitted | Very Low | Connection monitoring |
| Port scanning / service discovery | Information Disclosure | Low | Low | Bind to 127.0.0.1 only; no mDNS/UPnP; minimal service exposure | Very Low | Network binding verification |

#### Controls

- All network services bound to `127.0.0.1` (localhost only).
- No external network connections; no cloud services; no telemetry.
- Network interface validation on startup.
- Connection logging for all network activity.
- Firewall rules documented for environments that require additional isolation.
- No multicast or broadcast traffic.

## 4. Attack Surface Analysis

| Module | Attack Surface | Controls | Priority |
|--------|---------------|----------|----------|
| Authentication | Login endpoint, password change, MFA setup | Rate limiting, lockout, MFA | Critical |
| Authorization | Every API endpoint, role management | RBAC middleware, permission checks | Critical |
| Session Management | Token validation, session lifecycle | Server-side tokens, short TTL | High |
| Data Storage | Database files, WAL, backups | Encryption, permissions, integrity | Critical |
| Plugin System | Plugin loading, API gateway, sandbox | Sandboxing, signatures, permissions | Critical |
| Configuration | Config files, admin settings | HMAC, schema validation, audit | High |
| Import/Export | File upload/download, data processing | Validation, sanitization, limits | High |
| Learning Content | Content rendering, progress tracking | Sanitization, integrity checks | Medium |
| Assessment | Submission, grading, results | Server-side validation, audit | Medium |
| Administration | Admin actions, user management | Re-auth, approval, audit logging | Critical |
| Local Network | Service binding, connections | Localhost-only, binding validation | Medium |

## 5. Risk Matrix

| Threat | Likelihood | Impact | Risk Level | Priority |
|--------|-----------|--------|------------|----------|
| Plugin sandbox escape | Low | Critical | High | P1 |
| Admin account compromise | Low | Critical | High | P1 |
| Database file extraction | Low | Critical | High | P1 |
| SQL injection | Low | Critical | High | P1 |
| Malicious plugin data exfiltration | Medium | Critical | High | P1 |
| Backup data theft | Low | Critical | High | P1 |
| Session hijacking | Low | Critical | Medium | P2 |
| Configuration downgrade | Low | High | Medium | P2 |
| Unauthorized admin creation | Low | Critical | High | P1 |
| Content tampering | Low | High | Medium | P2 |
| Import data injection | Low | High | Medium | P2 |
| Brute force attack | Medium | High | Medium | P2 |
| Grade tampering | Low | Critical | Medium | P2 |
| Physical data access | Low | Critical | Medium | P2 |
| Supply chain compromise | Low | Critical | High | P1 |

## 6. Mitigation Priority List

### P1 — Immediate (implement before any release)

1. Database encryption at rest (SQLCipher).
2. Plugin sandboxing with capability enforcement.
3. RBAC middleware on every endpoint.
4. Admin action re-authentication and audit logging.
5. Session token server-side storage and validation.
6. Configuration HMAC signatures.
7. Backup encryption.
8. SQL injection prevention (parameterized queries only).
9. Input validation on all API endpoints.
10. File path traversal prevention.

### P2 — High Priority (implement within first 2 releases)

1. Account lockout and progressive delay.
2. Device fingerprinting for anomaly detection.
3. Content sanitization for learning materials.
4. Import package validation and sandboxing.
5. Export authorization and audit logging.
6. Configuration rollback capability.
7. Database integrity monitoring.
8. Admin segregation of duties.
9. Assessment server-side validation.
10. Network binding validation.

### P3 — Medium Priority (implement within 6 months)

1. Behavioral anomaly detection for sessions.
2. Plugin behavior profiling.
3. Advanced reporting data masking.
4. Diagnostic tool data sanitization.
5. Comprehensive fuzz testing.
6. Penetration testing program.
7. Security champion model.
8. Incident response procedures.

## 7. Residual Risk Acceptance

After all mitigations are applied, the following residual risks are accepted with documented
justification:

| Residual Risk | Justification | Review Frequency |
|---------------|---------------|------------------|
| Physical disk access by attacker with machine access | Mitigated by OS-level encryption (BitLocker, FileVault, LUKS) which is outside application scope | Quarterly |
| Highly sophisticated sandbox escape | Mitigated by defense-in-depth; no single point of failure; monitor for anomalies | Quarterly |
| Supply chain compromise of dependencies | Mitigated by automated scanning, manual review, but cannot guarantee 100% | Monthly |

## 8. Threat Model Maintenance

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Full threat model review | Quarterly | Security Team |
| New feature threat assessment | Per feature | Feature Owner + Security Champion |
| Dependency threat update | Monthly | Automated + Manual Review |
| Incident-triggered threat review | Per incident | Security Team |
| Plugin ecosystem threat review | Quarterly | Plugin Security Reviewer |
| Third-party security audit | Annually | External Auditor |
