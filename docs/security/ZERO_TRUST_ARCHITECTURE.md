# AuthShield Lab — Zero Trust Architecture

## 1. Overview

AuthShield Lab implements Zero Trust principles throughout the application stack. The core
axiom: **trust nothing, verify everything — every request, every plugin, every configuration
change, every locally stored artifact.** Local-only operation does not grant implicit trust.
Every component must continuously prove its legitimacy.

## 2. Zero Trust Principles

1. **Never trust, always verify** — every access request is fully authenticated and authorized.
2. **Assume breach** — design as if an attacker already has partial access.
3. **Verify explicitly** — use all available signals (identity, device, context) to make access decisions.
4. **Least privilege access** — grant minimum permissions for minimum duration.
5. **Micro-segmentation** — isolate components so compromise of one does not propagate.
6. **Continuous monitoring** — validate trust continuously, not just at initial access.

## 3. Identity Verification

### 3.1 User Identity

Every user must authenticate before any access to application data or functionality.

```
┌─────────────────────────────────────────────────────┐
│                IDENTITY VERIFICATION                  │
│                                                       │
│  User → Login Request → Credential Validation         │
│                          │                            │
│                    ┌─────▼──────┐                     │
│                    │ Argon2id   │                     │
│                    │ Verification│                     │
│                    └─────┬──────┘                     │
│                          │                            │
│                    ┌─────▼──────┐     ┌────────────┐  │
│                    │ MFA Check  │────►│ TOTP / HOTP│  │
│                    └─────┬──────┘     └────────────┘  │
│                          │                            │
│                    ┌─────▼──────┐                     │
│                    │ Session    │                     │
│                    │ Token Issue│                     │
│                    └────────────┘                     │
└─────────────────────────────────────────────────────┘
```

**Controls:**
- Passwords hashed with Argon2id (memory-hard, resistant to GPU/ASIC attacks).
- Per-user random salt stored alongside hash.
- MFA via TOTP (RFC 6238) with time-window validation.
- Session tokens: 256-bit cryptographically random, stored server-side only.
- Failed login attempts tracked; account lockout after configurable threshold.

### 3.2 Identity Lifecycle

| Phase | Controls |
|-------|----------|
| **Creation** | Admin-only user creation; email uniqueness validation; default role assignment. |
| **Authentication** | Credential + MFA verification on every login. |
| **Authorization** | RBAC role check on every request; permissions evaluated per-operation. |
| **Session Management** | Token validated on every request; continuous session timeout. |
| **Modification** | Profile changes require current-password re-verification. |
| **Deactivation** | Soft-delete with data retention; all sessions invalidated immediately. |
| **Deletion** | Hard-delete with cryptographic erasure; audit log retained. |

## 4. Device Trust

### 4.1 Device Fingerprinting

The platform generates a local device fingerprint from hardware and software attributes
to detect environment changes.

**Signals collected:**
- Hostname
- Operating system version
- CPU architecture
- Machine ID (platform-specific)
- Application installation path
- Electron version hash

**Usage:**
- Stored with session metadata for anomaly detection.
- Changes in device fingerprint trigger session re-validation.
- Device trust is informational, not gating — it adds a detection layer.

### 4.2 Trusted Device Registration (Optional)

Users may register their device as "trusted." Trusted devices receive relaxed session
timeouts but still require full authentication on startup. Registration requires:

- Full authentication with MFA.
- Explicit user opt-in.
- Device fingerprint recorded.
- Ability to revoke trust per-device.

## 5. Session Trust

### 5.1 Token Properties

| Property | Value |
|----------|-------|
| Length | 256 bits (32 bytes) |
| Generation | `secrets.token_urlsafe(32)` |
| Lifetime | Configurable, default 30 minutes idle / 8 hours absolute |
| Storage | Server-side only (SQLite); never stored in client-side storage |
| Validation | Every API request; every IPC message |
| Invalidation | On logout, on password change, on role change, on security event |

### 5.2 Continuous Session Validation

Sessions are not validated only at the initial request. Every subsequent request re-validates:

1. Token exists in session store.
2. Token has not expired (idle or absolute).
3. Token belongs to an active, non-deactivated user.
4. Token's device fingerprint matches current device (informational).
5. No security events have invalidated the session since issuance.

### 5.3 Anomaly Detection

The session manager tracks per-session behavioral signals:

- Request frequency (abnormal spikes trigger review).
- Endpoints accessed (unusual patterns flagged).
- Timing patterns (access at unusual hours flagged).
- Device changes mid-session (flagged, may require re-auth).

Anomaly signals produce security warnings, not automatic lockout (availability vs. security
balance for an educational platform).

## 6. Application Trust

### 6.1 Application Integrity Verification

On startup, the application verifies its own integrity:

```
┌──────────────────────────────────────────────┐
│           STARTUP INTEGRITY CHECK             │
│                                               │
│  1. Verify application code hash              │
│  2. Verify Electron binary hash               │
│  3. Verify Node.js runtime hash               │
│  4. Verify Python runtime hash                │
│  5. Verify FastAPI module integrity            │
│  6. Verify configuration file signatures       │
│  7. Verify database schema version             │
│  8. Verify plugin manifests                    │
│                                               │
│  Any failure → warn user, log event,           │
│  optionally halt application                   │
└──────────────────────────────────────────────┘
```

### 6.2 Code Signing

Release artifacts are signed. Installation verifies signatures before deployment. The
signature verification chain:

1. Verify installer package signature.
2. Verify each extracted component against manifest checksums.
3. Verify runtime integrity at application startup.

### 6.3 Tamper Detection

- Application files monitored via periodic integrity checks.
- Unexpected modifications trigger security alerts.
- Configuration files carry HMAC signatures validated before each use.
- Database integrity verified through page checksums (SQLite PRAGMA integrity_check).

## 7. Plugin Trust

### 7.1 Trust Establishment

Plugins undergo a multi-stage trust establishment process:

```
┌─────────────────────────────────────────────────────┐
│              PLUGIN TRUST LIFECYCLE                    │
│                                                       │
│  Discovery → Verification → Permission Audit →        │
│  Sandboxing → Runtime Monitoring → Continuous Eval    │
│                                                       │
│  Stage 1: Signature Verification                      │
│    - Verify Ed25519 signature against known keys      │
│    - Reject unsigned plugins by default               │
│                                                       │
│  Stage 2: Permission Validation                       │
│    - Compare declared permissions against policy       │
│    - User must approve permission grants              │
│                                                       │
│  Stage 3: Sandboxing                                  │
│    - Isolated process or subprocess                   │
│    - No direct filesystem access outside sandbox      │
│    - No direct network access                         │
│    - Resource limits enforced                         │
│                                                       │
│  Stage 4: Runtime Monitoring                          │
│    - Resource usage tracked                           │
│    - API calls logged and validated                   │
│    - Anomalies trigger warnings                       │
└─────────────────────────────────────────────────────┘
```

### 7.2 Plugin Permission Model

Plugins declare required permissions at installation. Permissions are:

| Permission | Scope |
|------------|-------|
| `plugin:storage:read` | Read own plugin storage |
| `plugin:storage:write` | Write own plugin storage |
| `plugin:storage:delete` | Delete own plugin storage |
| `plugin:content:read` | Read learning module content |
| `plugin:ui:render` | Render custom UI components |
| `plugin:event:subscribe` | Subscribe to application events |
| `plugin:event:emit` | Emit events to application |
| `plugin:config:read` | Read plugin configuration |
| `plugin:config:write` | Write plugin configuration |

No plugin may request access to other plugins' storage, user credentials, session tokens,
or administrative functions.

### 7.3 Plugin Revocation

Plugins can be revoked at any time:

- Admin revokes via Plugin Management panel.
- Automatic revocation on integrity check failure.
- Automatic revocation on security policy violation.
- Revoked plugins are unloaded immediately; storage retained until user deletion.

## 8. Configuration Trust

### 8.1 Configuration Integrity

All configuration files are protected:

| File | Protection |
|------|------------|
| `config.json` | HMAC-SHA256 signature; validated at startup and before each use |
| `security_policy.json` | Signed; admin-only modification; change audit logged |
| `roles.json` | Signed; admin-only modification; rollback capability |
| `plugin_permissions.json` | Signed; per-plugin permission grants logged |
| `backup_policy.json` | Signed; admin-only modification |

### 8.2 Change Validation

Every configuration change passes through:

1. **Schema validation** — malformed configuration rejected.
2. **Policy validation** — changes checked against security policy.
3. **Integrity signing** — new HMAC computed and stored.
4. **Audit logging** — old value, new value, actor, timestamp recorded.
5. **Rollback availability** — previous configuration retained for recovery.

### 8.3 Secure Defaults

All configuration values ship in the most restrictive safe state:

- All plugin permissions denied by default.
- MFA required for admin accounts.
- Session timeout at 30 minutes idle.
- Audit logging enabled and non-disablable.
- Backup encryption enabled by default.

## 9. Data Trust

### 9.1 Encryption at Rest

| Data Type | Encryption |
|-----------|------------|
| User credentials | Argon2id hash (irreversible) |
| Session data | Server-side only; encrypted at rest via SQLite encryption |
| Plugin storage | Per-plugin encryption keys; AES-256-GCM |
| Backups | User-provided passphrase; AES-256-GCM |
| Audit logs | Append-only; HMAC integrity chain |
| Configuration | HMAC-signed; optionally encrypted |

### 9.2 Data Integrity

- SQLite WAL mode provides atomic writes.
- Database page checksums validated on startup.
- Audit logs use hash chains: each entry includes hash of previous entry.
- Backup archives include SHA-256 manifest of all included files.

### 9.3 Access Auditing

Every data access is logged:

| Event | Details |
|-------|---------|
| Read | Who, what data, when, from where |
| Write | Who, what data, when, old value, new value |
| Delete | Who, what data, when, soft or hard |
| Export | Who, what data, when, format |
| Backup | Who, when, what included, success/failure |

## 10. Administrative Trust

### 10.1 Admin Authentication

Administrative actions require:

1. **Current session** — admin must be logged in.
2. **Re-authentication** — admin must re-enter password for sensitive operations.
3. **MFA verification** — admin MFA token required for critical operations.
4. **Explicit confirmation** — destructive actions require typed confirmation.

### 10.2 Admin Action Approval

Critical administrative operations require approval:

| Operation | Approval Required |
|-----------|-------------------|
| User role change | Admin re-auth + audit log |
| Plugin installation | Admin re-auth + permission review |
| Configuration change | Admin re-auth + audit log |
| Data deletion | Admin re-auth + confirmation dialog |
| Security policy change | Admin re-auth + second admin approval |
| Backup deletion | Admin re-auth + confirmation |

### 10.3 Segregation of Duties

No single administrator can:

- Create admin accounts and assign roles (requires two separate admin actions).
- Install plugins and modify security policy (requires approval workflow).
- Modify audit configuration and access audit logs (separation prevents log tampering).

## 11. Local Trust Boundaries

### 11.1 Process Boundary

Electron Main process and Renderer process are isolated:

- IPC messages are type-validated and schema-checked.
- Renderer cannot access filesystem directly.
- Main process mediates all data access.
- Node.js integration disabled in Renderer.

### 11.2 File System Boundary

The application accesses only designated directories:

```
~/.config/authshield-lab/          (configuration)
~/.local/share/authshield-lab/     (data, database)
~/.cache/authshield-lab/           (temporary files)
```

All file access goes through a path validation layer that:

- Resolves symlinks and rejects path traversal.
- Validates paths against an allowlist of base directories.
- Checks file permissions before access.
- Logs all file access attempts.

### 11.3 Memory Boundary

- Sensitive data (tokens, passwords) is cleared from memory after use.
- Plugin processes have separate memory spaces.
- Encryption keys are never written to swap or temporary files.

## 12. Continuous Validation

Trust is not established once and forgotten. It is continuously re-evaluated:

| Validation | Frequency | Action on Failure |
|------------|-----------|-------------------|
| Session validity | Every request | Reject request; require re-authentication |
| Plugin integrity | Every plugin load + periodic | Disable plugin; alert user |
| Configuration integrity | Every config read | Use cached safe default; alert admin |
| Database integrity | Application startup | Warn user; offer recovery options |
| User role validity | Every request | Deny access; require re-authentication |
| Device fingerprint | Every session | Informational logging; flag anomaly |

## 13. Explicit Authorization

No implicit trust exists in the system. Every operation requires explicit authorization:

```python
# Conceptual authorization model
async def authorize(user, resource, action, context):
    """Every access goes through explicit authorization."""
    # 1. Verify user identity
    if not user.is_authenticated:
        raise UnauthorizedError()
    
    # 2. Check user is active (not deactivated)
    if user.is_deactivated:
        raise AccountDeactivatedError()
    
    # 3. Check role-based permissions
    if not await rbac.check_permission(user.role, resource, action):
        raise ForbiddenError()
    
    # 4. Check resource-level permissions (if applicable)
    if resource.requires_specific_permission:
        if not await resource.check_access(user, action):
            raise ForbiddenError()
    
    # 5. Check rate limits
    if await rate_limiter.is_exceeded(user, resource):
        raise RateLimitExceededError()
    
    # 6. Log authorization decision
    await audit_log.record(
        user=user.id, resource=resource.id,
        action=action, decision="granted",
        context=context
    )
    
    return AuthorizationGranted()
```

## 14. Least Privilege

### 14.1 Role Hierarchy

| Role | Permissions |
|------|-------------|
| **Learner** | Access enrolled modules; submit assessments; view own progress |
| **Educator** | Create/manage modules; view student progress; manage assessments |
| **Admin** | Full system access; user management; plugin management; configuration |
| **Super Admin** | Admin permissions + security policy modification + audit access |

### 14.2 Permission Granularity

Permissions are defined at the operation level:

```json
{
  "module:read": "View module content",
  "module:write": "Create or modify module content",
  "module:delete": "Delete module content",
  "assessment:submit": "Submit assessment answers",
  "assessment:grade": "Grade assessment submissions",
  "user:list": "List user accounts",
  "user:create": "Create user accounts",
  "user:modify": "Modify user accounts",
  "user:delete": "Delete user accounts",
  "plugin:install": "Install plugins",
  "plugin:configure": "Configure plugins",
  "config:read": "Read system configuration",
  "config:write": "Modify system configuration",
  "audit:read": "Read audit logs",
  "backup:create": "Create backups",
  "backup:restore": "Restore from backups"
}
```

### 14.3 Default Deny

All permissions default to **denied**. Permissions are granted only through:

1. Role assignment (predefined role permissions).
2. Explicit permission grant by an administrator.
3. Plugin permission approval by a user/administrator.

## 15. Trust Lifecycle

Trust follows a defined lifecycle for every entity in the system:

```
┌──────────┐    ┌──────────────┐    ┌────────────────┐    ┌────────────┐
│Establish │───►│  Maintain    │───►│ Re-evaluate    │───►│  Revoke    │
│          │    │              │    │                │    │            │
│• Verify  │    │• Continuous  │    │• Periodic      │    │• Immediate │
│  identity│    │  validation  │    │  integrity     │    │  unload    │
│• Grant   │    │• Anomaly     │    │  checks        │    │• Session   │
│  permis- │    │  detection   │    │• Role changes  │    │  invalid-  │
│  sions   │    │• Audit       │    │• Policy updates │    │  ation     │
│• Record  │    │  logging     │    │• Threat model  │    │• Audit log │
│          │    │              │    │  updates       │    │            │
└──────────┘    └──────────────┘    └────────────────┘    └────────────┘
```

### Establishment

- Identity verified through authentication.
- Permissions granted based on role and explicit grants.
- Trust metadata recorded (device, time, context).

### Maintenance

- Continuous validation on every request.
- Behavioral anomaly detection.
- Comprehensive audit logging.

### Re-evaluation

- Periodic integrity checks for all trusted entities.
- Role and permission changes trigger re-evaluation.
- Security policy updates propagate to all trust decisions.
- Threat model updates may require trust boundary adjustments.

### Revocation

- Immediate effect: sessions invalidated, plugins unloaded, access denied.
- Graceful degradation: user notified, data preserved for recovery.
- Audit trail retained for post-revocation analysis.
