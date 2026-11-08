# Security Architecture — AuthShield Lab

> Version: 1.0  
> Last Updated: 2026-07-19  
> Status: Current

---

## 1. Overview

AuthShield Lab implements defense-in-depth security across all layers. As an educational cybersecurity platform, security is both a functional requirement and a learning objective. The system operates entirely on localhost with no external network connections.

---

## 2. Security Principles

| Principle | Implementation |
|---|---|
| **Least Privilege** | Each component has minimal required permissions |
| **Defense in Depth** | Multiple security layers, no single point of failure |
| **Zero Trust** | Every request authenticated and authorized |
| **Privacy by Design** | No telemetry, no external data transmission |
| **Secure by Default** | Most restrictive settings as default |
| **Fail Secure** | Errors default to deny, not allow |
| **Audit Everything** | Complete audit trail of security-relevant actions |

---

## 3. Authentication Boundaries

### 3.1 Authentication Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  CREDENTIALS │────▶│  PASSWORD    │────▶│  MFA         │────▶│  TOKEN       │
│  COLLECTED   │     │  VERIFIED    │     │  VERIFIED    │     │  ISSUED      │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                           │                     │                     │
                           ▼                     ▼                     ▼
                     ┌──────────┐         ┌──────────┐         ┌──────────┐
                     │  AUDIT   │         │  AUDIT   │         │  AUDIT   │
                     │  LOG     │         │  LOG     │         │  LOG     │
                     └──────────┘         └──────────┘         └──────────┘
```

### 3.2 Password Security

| Attribute | Value |
|---|---|
| Hashing algorithm | argon2id |
| Memory cost | 64 MB |
| Time cost | 3 iterations |
| Parallelism | 4 threads |
| Salt | Random 16-byte per password |
| Minimum length | 8 characters |
| Complexity | Upper, lower, digit, special required |
| History | Last 12 passwords remembered |
| Expiry | Configurable (default: 90 days) |

### 3.3 Token Security

| Attribute | Value |
|---|---|
| Algorithm | HS256 (symmetric) |
| Access token lifetime | 15 minutes |
| Refresh token lifetime | 7 days |
| Token rotation | On each refresh |
| Key rotation | Every 30 days |
| Key storage | Encrypted in database |
| Issuer validation | Strict issuer check |
| Audience validation | Strict audience check |

### 3.4 MFA (Multi-Factor Authentication)

| Attribute | Value |
|---|---|
| Algorithm | TOTP (RFC 6238) |
| Time step | 30 seconds |
| Digits | 6 |
| Clock skew tolerance | ±1 step (30s) |
| Backup codes | 10 single-use codes |
| Recovery | Manual admin reset only |

### 3.5 Account Protection

| Protection | Threshold | Duration |
|---|---|---|
| Failed login lockout | 5 failures | 15 minutes |
| Progressive delay | 3+ failures | 1s, 2s, 4s, 8s, 16s |
| CAPTCHA | After 3 failures | Until success |
| Account freeze | 10 failures | Until admin unlock |
| Session limit | 5 concurrent | Oldest terminated |

---

## 4. Authorization Boundaries

### 4.1 RBAC Model

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   USER   │────▶│   ROLE   │────▶│PERMISSION│────▶│RESOURCE  │
│          │     │          │     │          │     │          │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

### 4.2 Role Hierarchy

| Role | Permissions | Description |
|---|---|---|
| `super_admin` | All permissions | Full system access |
| `admin` | All except system config | Administrative access |
| `instructor` | Content, assessment, analytics | Teaching access |
| `student` | Learning, assessment (self) | Learning access |
| `viewer` | Read-only | Observation access |
| `plugin` | SDK API only | Plugin-restricted |

### 4.3 Permission Format

```
{module}:{action}
```

Examples:
- `users:create` — Create new users
- `courses:read` — View courses
- `assessments:grade` — Grade assessments
- `audit:export` — Export audit logs
- `plugins:install` — Install plugins
- `config:write` — Modify configuration

### 4.4 Authorization Check Points

| Check Point | Location | Enforcement |
|---|---|---|
| API endpoint | FastAPI middleware | Every request |
| Use case | Application handler | Business operations |
| UI element | React component | Conditional rendering |
| Plugin API | SDK boundary | Plugin calls |
| Data access | Repository | Query filtering |

---

## 5. Secure Storage

### 5.1 Encryption at Rest

| Data Type | Algorithm | Key Management |
|---|---|---|
| Passwords | argon2id (hash) | Per-password salt |
| Tokens | HS256 (signing) | Rotating master key |
| PII fields | AES-256-GCM | Master key + per-record IV |
| Configuration | AES-256-GCM | Master key |
| Backups | AES-256-GCM | Backup encryption key |
| Audit logs | HMAC-SHA256 (integrity) | Integrity key |

### 5.2 Key Management

```
┌─────────────────────────────────────────────────────────┐
│                   KEY HIERARCHY                          │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Master Key (encrypted, stored in config)        │   │
│  │  ├── Data Encryption Key (DEK)                   │   │
│  │  │   ├── PII field encryption                    │   │
│  │  │   └── Configuration encryption                │   │
│  │  ├── Token Signing Key (TSK)                     │   │
│  │  │   └── JWT token signing                       │   │
│  │  ├── Backup Encryption Key (BEK)                 │   │
│  │  │   └── Backup file encryption                  │   │
│  │  └── Integrity Key (IK)                          │   │
│  │      └── Audit log integrity                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 5.3 Key Rotation Policy

| Key | Rotation Interval | Grace Period |
|---|---|---|
| Token Signing Key | 30 days | 7 days (old + new valid) |
| Data Encryption Key | 90 days | 30 days (dual encryption) |
| Backup Encryption Key | 180 days | 30 days |
| Integrity Key | 365 days | 90 days |

---

## 6. Audit Logging Architecture

### 6.1 Audit Event Types

| Category | Events | Sensitivity |
|---|---|---|
| Authentication | Login, logout, MFA, password change | High |
| Authorization | Permission grant/deny, role change | High |
| Data Access | CRUD operations on sensitive data | Medium |
| Configuration | Settings changes, plugin install | Medium |
| Security | Threat detection, anomaly, defense alerts | Critical |
| System | Startup, shutdown, backup, migration | Low |

### 6.2 Audit Log Structure

```json
{
  "audit_id": "aud_01J2ABCDEF",
  "timestamp": "2026-07-19T10:30:00.000Z",
  "event_type": "authentication.login_success",
  "user_id": "usr_01J2...",
  "user_email": "admin@example.com",
  "source_ip": "127.0.0.1",
  "user_agent": "AuthShield/1.0.0",
  "resource": "auth:login",
  "action": "authenticate",
  "result": "success",
  "details": {
    "method": "password",
    "mfa_used": true,
    "session_id": "ses_01J2..."
  },
  "checksum": "sha256:a1b2c3d4..."
}
```

### 6.3 Audit Log Integrity

| Mechanism | Implementation |
|---|---|
| Chain of checksums | Each entry includes hash of previous entry |
| Append-only | No update or delete operations allowed |
| Tamper detection | Recompute chain on query, detect breaks |
| Local storage | No network transmission of audit data |
| Separate storage | Optional separate database for audit logs |

---

## 7. Integrity Verification

### 7.1 Checksum System

| Data | Algorithm | Frequency |
|---|---|---|
| Database files | SHA-256 | On backup, on integrity check |
| Backup files | SHA-256 | On creation |
| Plugin files | SHA-256 | On install, on load |
| Configuration | SHA-256 | On load |
| Application binary | SHA-256 | On startup |

### 7.2 Integrity Verification Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  LOAD    │────▶│  COMPUTE │────▶│  COMPARE │────▶│  RESULT  │
│  DATA    │     │  CURRENT │     │  STORED  │     │          │
└──────────┘     │  HASH    │     │  HASH    │     └────┬─────┘
                 └──────────┘     └──────────┘          │
                                                   ┌────▼─────┐
                                                   │  LOG     │
                                                   │  RESULT  │
                                                   └──────────┘
```

### 7.3 Tamper Detection

If integrity verification fails:
1. **Alert** raised to administrator
2. **Audit** log entry created with failure details
3. **Affected data** quarantined (marked as untrusted)
4. **Fallback** to last verified good state
5. **Recovery** options presented to administrator

---

## 8. Plugin Isolation Security

### 8.1 Sandbox Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PLUGIN SANDBOX                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Restricted Python Namespace                     │   │
│  │  ├── Allowed: json, datetime, typing, abc        │   │
│  │  ├── Blocked: os, socket, subprocess, ctypes     │   │
│  │  └── Blocked: importlib, sys.modules             │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Resource Limits                                  │   │
│  │  ├── Memory: 64MB max                            │   │
│  │  ├── CPU: 100ms per handler                      │   │
│  │  ├── Messages: 100/sec, 10 concurrent            │   │
│  │  └── File I/O: Plugin directory only             │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Communication Bridge                             │   │
│  │  ├── SDK API (validated, rate-limited)            │   │
│  │  ├── Event subscription (read-only)               │   │
│  │  ├── Data queries (read-only)                     │   │
│  │  └── Configuration (read-only)                    │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Plugin Security Rules

| Rule | Enforcement |
|---|---|
| No direct database access | Import hook blocks database modules |
| No network access | Import hook blocks socket, http, urllib |
| No process spawning | Import hook blocks subprocess, os.exec |
| No native code | Import hook blocks ctypes, cffi |
| No dynamic import | Import hook blocks importlib |
| File I/O restricted | Filesystem sandbox enforces directory |
| Memory limited | Resource monitor enforces 64MB |
| CPU limited | Timeout enforced per handler |
| No recursive messages | Message depth counter enforced |

### 8.3 Plugin Trust Levels

| Level | Capabilities | Use Case |
|---|---|---|
| Untrusted | Event subscription only | Newly installed, not reviewed |
| Basic | Event + query + config | Standard plugins |
| Extended | Basic + UI extensions | UI-integrated plugins |
| Trusted | Extended + write queries | Verified, security-reviewed |

---

## 9. Configuration Protection

### 9.1 Configuration Security

| Setting | Protection |
|---|---|
| Database path | Read-only after initialization |
| Encryption keys | Encrypted at rest, never logged |
| Admin credentials | Argon2id hashed, never stored plaintext |
| API tokens | Encrypted at rest, short-lived |
| Plugin manifests | Schema-validated, signature-checked |
| User preferences | User-scoped, not shared |

### 9.2 Configuration Change Control

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  CHANGE  │────▶│  VALIDATE│────▶│  APPROVE │────▶│  APPLY   │
│  REQUEST │     │  SCHEMA  │     │  (admin) │     │          │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
                                                        ▼
                                                  ┌──────────┐
                                                  │  AUDIT   │
                                                  │  LOG     │
                                                  └──────────┘
```

### 9.3 Sensitive Configuration

| Config Key | Sensitivity | Protection |
|---|---|---|
| `database.encryption_key` | Critical | Encrypted, access-controlled |
| `auth.jwt_secret` | Critical | Encrypted, rotated regularly |
| `auth.mfa.secret` | Critical | Encrypted, per-user |
| `plugin.api_key` | High | Encrypted, per-plugin |
| `backup.encryption_key` | High | Encrypted, access-controlled |

---

## 10. Certificate Validation (Offline CA)

### 10.1 Offline Certificate Authority

```
┌─────────────────────────────────────────────────────────┐
│                   OFFLINE CA SYSTEM                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Root Certificate (self-signed)                  │   │
│  │  ├── Validity: 10 years                          │   │
│  │  ├── Algorithm: RSA 4096 / ECDSA P-384           │   │
│  │  └── Storage: Encrypted, offline only             │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Intermediate Certificate                        │   │
│  │  ├── Validity: 2 years                           │   │
│  │  ├── Signed by: Root CA                          │   │
│  │  └── Used for: Plugin signing                    │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Leaf Certificates                               │   │
│  │  ├── Validity: 1 year                            │   │
│  │  ├── Signed by: Intermediate CA                  │   │
│  │  └── Used for: Code signing, TLS (if needed)     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 10.2 Certificate Validation Chain

```
Plugin Signature → Leaf Cert → Intermediate Cert → Root Cert → Trust Store
         │                    │                       │
         ▼                    ▼                       ▼
    Verify signature    Check expiry            Verify chain
    Check hash          Check revocation        Check trust
```

### 10.3 Certificate Policy

| Certificate | Validity | Purpose |
|---|---|---|
| Root CA | 10 years | Trust anchor |
| Intermediate | 2 years | Plugin signing |
| Code signing | 1 year | Application signing |
| TLS (optional) | 1 year | Localhost HTTPS (if enabled) |

---

## 11. Least Privilege Enforcement

### 11.1 Principle Implementation

| Context | Least Privilege Implementation |
|---|---|
| Database access | Repository pattern with query filtering |
| File system | Application writes to designated directories only |
| Plugin execution | Sandboxed with resource limits |
| User accounts | RBAC with minimal required permissions |
| API endpoints | Per-endpoint authorization checks |
| Background tasks | Task-specific resource allocation |

### 11.2 Privilege Escalation Prevention

| Vector | Prevention |
|---|---|
| SQL injection | Parameterized queries (SQLAlchemy ORM) |
| Path traversal | Sanitized file paths, directory restrictions |
| XSS | React auto-escaping, CSP headers |
| CSRF | Same-origin policy (localhost-only) |
| Plugin escape | Import hooks, resource monitoring |
| Token theft | Short-lived tokens, rotation |

---

## 12. Privacy Controls

### 12.1 Data Minimization

| Data Collected | Purpose | Retention |
|---|---|---|
| User credentials | Authentication | Until account deletion |
| Session data | Session management | Until session expiry |
| Audit logs | Compliance | Configurable (default: 1 year) |
| Analytics | Learning improvement | Anonymized after 90 days |
| Plugin usage | Ecosystem health | Aggregated, no PII |

### 12.2 Local Processing

| Processing | Location | External Data |
|---|---|---|
| Authentication | Local | None |
| Data storage | Local | None |
| Analytics | Local | None |
| Reporting | Local | None |
| Plugin execution | Local | None |
| All operations | Local | None |

### 12.3 Privacy Guarantees

1. **No network calls** at runtime (verified by architecture checks)
2. **No telemetry** — zero data transmitted externally
3. **No analytics services** — all analytics local
4. **No third-party SDKs** — all code is first-party
5. **No cloud sync** — all data local
6. **No external APIs** — fully offline

---

## 13. Security Event Flow

### 13.1 Detection → Logging → Alerting

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  SECURITY│────▶│  CLASSIFY│────▶│  LOG     │────▶│  RESPOND │
│  EVENT   │     │  (level) │     │  (audit) │     │          │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
                                              ┌─────────┼─────────┐
                                              │         │         │
                                              ▼         ▼         ▼
                                         ┌────────┐ ┌────────┐ ┌────────┐
                                         │  BLOCK │ │  ALERT │ │  RATE  │
                                         │  (IP)  │ │ (admin)│ │ LIMIT  │
                                         └────────┘ └────────┘ └────────┘
```

### 13.2 Security Event Categories

| Category | Detection | Response | Alert Level |
|---|---|---|---|
| Brute force | 5+ failed logins/min | Account lockout | High |
| Privilege escalation | Unauthorized permission check | Deny + log | Critical |
| Data exfiltration | Unusual export volume | Rate limit + alert | High |
| Plugin anomaly | Resource limit exceeded | Plugin unload | Medium |
| Integrity failure | Checksum mismatch | Quarantine + alert | Critical |
| Configuration tamper | Unauthorized config change | Revert + alert | High |

---

## 14. Threat Model Overview

### 14.1 Threat Categories

| Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Unauthorized access | Medium | High | MFA, RBAC, rate limiting |
| Data breach | Low | Critical | Encryption, access control |
| Plugin compromise | Medium | Medium | Sandboxing, resource limits |
| Configuration tamper | Low | High | Integrity checks, audit |
| Denial of service | Low | Medium | Rate limiting, resource limits |
| Data corruption | Low | High | Backups, integrity checks |
| Privilege escalation | Low | Critical | RBAC, audit, least privilege |
| Supply chain (plugin) | Medium | High | Signature verification, sandbox |

### 14.2 Attack Surface

```
┌─────────────────────────────────────────────────────────┐
│                    ATTACK SURFACE                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  User Input (forms, API)                         │   │
│  │  ├── Input validation                            │   │
│  │  ├── SQL injection prevention                    │   │
│  │  └── XSS prevention                              │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Plugin Interface                                │   │
│  │  ├── Import restrictions                         │   │
│  │  ├── Resource limits                             │   │
│  │  └── Message validation                          │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  File System                                     │   │
│  │  ├── Directory restrictions                      │   │
│  │  ├── Path sanitization                           │   │
│  │  └── Size limits                                 │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Configuration                                   │   │
│  │  ├── Schema validation                           │   │
│  │  ├── Change control                              │   │
│  │  └── Encryption                                  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 14.3 Security Testing

| Test Type | Frequency | Tool |
|---|---|---|
| Penetration testing | Per release | Manual + automated |
| Dependency scanning | Per build | Safety/pip-audit |
| SAST (static analysis) | Per commit | Bandit |
| Secret scanning | Per commit | TruffleHog |
| Fuzz testing | Monthly | Hypothesis |
| Access control testing | Per release | Custom test suite |
| Plugin sandbox testing | Per plugin | Custom test suite |
