# AuthShield Lab — Defense-in-Depth Framework

## 1. Overview

Defense-in-depth is the cornerstone of AuthShield Lab's security architecture. No single
control protects the system. Instead, multiple overlapping layers ensure that the failure of
any one layer does not result in a complete compromise. Each layer assumes the layers above
it may have failed.

## 2. Defense-in-Depth Model

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 11: Administration Layer                               │
│  RBAC, Approval Workflows, Audit Logging, MFA for Admins    │
├─────────────────────────────────────────────────────────────┤
│ LAYER 10: Testing Layer                                      │
│  Security Tests, Pen Testing, Fuzzing, Regression Tests      │
├─────────────────────────────────────────────────────────────┤
│ LAYER 9: Documentation Layer                                 │
│  Security Guides, Threat Docs, Incident Procedures           │
├─────────────────────────────────────────────────────────────┤
│ LAYER 8: Deployment Layer                                    │
│  Code Signing, Integrity Verification, Secure Installation   │
├─────────────────────────────────────────────────────────────┤
│ LAYER 7: Build Pipeline Layer                                │
│  SAST, Dependency Scanning, Code Signing, Reproducible Builds│
├─────────────────────────────────────────────────────────────┤
│ LAYER 6: Logging Layer                                       │
│  Tamper-Resistant Logs, Integrity Chains, Secure Storage     │
├─────────────────────────────────────────────────────────────┤
│ LAYER 5: Plugin Layer                                        │
│  Sandboxing, Capability Enforcement, Resource Limits         │
├─────────────────────────────────────────────────────────────┤
│ LAYER 4: Configuration Layer                                 │
│  Secure Defaults, Integrity Checks, Change Validation        │
├─────────────────────────────────────────────────────────────┤
│ LAYER 3: Storage Layer                                       │
│  Encryption at Rest, Secure File Permissions, WAL Protection │
├─────────────────────────────────────────────────────────────┤
│ LAYER 2: Runtime Layer                                       │
│  Process Isolation, Memory Protection, ASLR, DEP/NX          │
├─────────────────────────────────────────────────────────────┤
│ LAYER 1: Application Layer                                   │
│  Input Validation, Output Encoding, CSRF, CSP                │
└─────────────────────────────────────────────────────────────┘
```

## 3. Layer Details

---

### Layer 1: Application Layer

The first line of defense. All external input passes through this layer before reaching
any other part of the system.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **Input Validation** | All inputs validated against schemas before processing | JSON Schema validation; Pydantic models; custom validators | Fuzz testing; unit tests for each endpoint |
| **Output Encoding** | All output encoded to prevent injection attacks | HTML entity encoding; JavaScript escaping; URL encoding | XSS test suite; automated scanning |
| **CSRF Protection** | Cross-site request forgery prevention | Synchronizer token pattern; SameSite cookies; origin validation | CSRF attack simulation tests |
| **Content Security Policy** | Restrict resource loading origins | Strict CSP headers; no inline scripts; no eval() | CSP violation monitoring |
| **Request Size Limits** | Prevent resource exhaustion through oversized requests | Configurable limits per endpoint; 10MB default | Load testing with oversized payloads |
| **Rate Limiting** | Prevent abuse through excessive requests | Per-user and global rate limits; progressive backoff | Rate limit bypass testing |
| **Content-Type Validation** | Ensure expected content types | Strict Content-Type checking; reject ambiguous types | Malformed content-type tests |
| **Parameterized Queries** | Prevent SQL injection | SQLAlchemy ORM; no raw SQL from user input | SQL injection test suite |

**Specific Implementation:**

```python
# Input validation middleware
class ApplicationSecurityLayer:
    def __init__(self):
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,
            burst_size=10
        )
        self.csrf_validator = CSRFValidator()
    
    async def process_request(self, request: Request):
        # 1. Rate limiting
        if self.rate_limiter.is_exceeded(request.client):
            raise HTTPException(429, "Too Many Requests")
        
        # 2. Request size validation
        if request.headers.get("content-length", 0) > self.max_request_size:
            raise HTTPException(413, "Request Too Large")
        
        # 3. Content-Type validation
        if not self.validate_content_type(request):
            raise HTTPException(415, "Unsupported Media Type")
        
        # 4. CSRF validation (for state-changing operations)
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            if not self.csrf_validator.validate(request):
                raise HTTPException(403, "CSRF Token Invalid")
        
        # 5. Input schema validation
        body = await request.json()
        validated = self.validate_schema(body, request.url.path)
        
        return validated
```

---

### Layer 2: Runtime Layer

Process-level isolation and memory protection mechanisms that prevent exploitation of
runtime vulnerabilities.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **Process Isolation** | Electron main and renderer processes isolated | Separate processes; no shared memory; IPC only | Process isolation tests |
| **Renderer Sandboxing** | Renderer process has restricted capabilities | Node.js integration disabled; contextIsolation enabled | Sandbox escape tests |
| **Memory Protection** | Operating system memory protections enabled | ASLR, DEP/NX, stack canaries (OS-level) | Memory corruption exploit tests |
| **Secure Memory Handling** | Sensitive data cleared after use | Token/password buffers zeroed after use; no swap exposure | Memory inspection tests |
| **IPC Validation** | Inter-process communication validated | Typed IPC messages; schema validation; no raw data transfer | IPC manipulation tests |
| **Resource Limits** | Process resource limits enforced | CPU, memory, file descriptor limits | Resource exhaustion tests |

**Electron Security Configuration:**

```javascript
// main.js security configuration
const mainConfig = {
    webPreferences: {
        nodeIntegration: false,        // Disable Node.js in renderer
        contextIsolation: true,        // Isolate renderer context
        sandbox: true,                 // Enable sandbox
        preload: path.join(__dirname, 'preload.js'),  // Secure preload
        webSecurity: true,             // Enable web security
        allowRunningInsecureContent: false,
        experimentalFeatures: false,
        enableRemoteModule: false,     // Disable remote module
    }
};
```

---

### Layer 3: Storage Layer

Protection of data at rest, including database encryption, file permissions, and WAL protection.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **Encryption at Rest** | All sensitive data encrypted | SQLCipher (AES-256) for database; AES-256-GCM for files | Encryption verification tests; key management audit |
| **Secure File Permissions** | Restrictive file permissions | Database: 0600; Config: 0600; Logs: 0640; Dirs: 0700 | Permission verification tests |
| **WAL Protection** | Write-Ahead Log secured | WAL file permissions; WAL checksummed; WAL backup included | WAL corruption recovery tests |
| **Atomic File Operations** | Prevent partial writes | Write to temp file, then atomic rename | Crash recovery tests |
| **Database Integrity** | Detect data corruption | SQLite integrity_check on startup; page checksums | Corruption injection tests |
| **Key Management** | Secure encryption key handling | Keys derived from passphrases (Argon2id); never stored in plaintext | Key management audit |
| **Data Classification** | Data protected based on sensitivity | Classification matrix applied to all data types | Classification compliance tests |
| **Backup Encryption** | Backups encrypted independently | User passphrase → Argon2id → AES-256-GCM key | Backup encryption verification |

**File Permission Matrix:**

| Path | Permission | Owner | Rationale |
|------|-----------|-------|-----------|
| `~/.config/authshield-lab/` | 0700 | User | Configuration directory |
| `~/.config/authshield-lab/config.json` | 0600 | User | Configuration file |
| `~/.config/authshield-lab/security_policy.json` | 0600 | User | Security policy |
| `~/.local/share/authshield-lab/` | 0700 | User | Data directory |
| `~/.local/share/authshield-lab/database.db` | 0600 | User | Database file |
| `~/.local/share/authshield-lab/database.db-wal` | 0600 | User | WAL file |
| `~/.local/share/authshield-lab/audit.log` | 0640 | User | Audit log |
| `~/.cache/authshield-lab/` | 0700 | User | Cache directory |

---

### Layer 4: Configuration Layer

Secure defaults, integrity verification, and change validation for all configuration data.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **Secure Defaults** | Most restrictive safe settings | Default deny; MFA for admins; short timeouts | Default configuration audit |
| **Integrity Checks** | Configuration files verified | HMAC-SHA256 signatures; validated before use | Tampered configuration detection tests |
| **Schema Validation** | Configuration structure validated | JSON Schema validation on every load | Malformed configuration tests |
| **Change Validation** | Modifications checked against policy | Admin auth required; policy compliance checked | Unauthorized change detection tests |
| **Rollback Capability** | Previous configurations preserved | Version history; rollback to last known-good | Rollback recovery tests |
| **Change Logging** | All modifications recorded | Old value, new value, actor, timestamp | Change audit verification |

**Secure Defaults Registry:**

| Setting | Default | Rationale |
|---------|---------|-----------|
| MFA required for admins | `true` | Admin accounts must use MFA |
| Session idle timeout | 30 minutes | Limit exposure window |
| Session absolute timeout | 8 hours | Prevent permanent sessions |
| Account lockout threshold | 5 attempts | Brute force protection |
| Lockout duration | 15 minutes | Deter brute force attacks |
| Audit logging | Enabled (non-disablable) | Maintain audit trail |
| Plugin permissions | All denied | Explicit grant required |
| Backup encryption | Enabled | Protect backup data |
| Debug logging | Disabled | Prevent sensitive data in logs |
| Plugin resource limits | CPU: 50%, Memory: 256MB | Prevent resource exhaustion |

---

### Layer 5: Plugin Layer

Isolation and enforcement mechanisms for the plugin ecosystem.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **Process Sandboxing** | Plugins in isolated processes | Separate process; restricted capabilities | Sandbox escape tests |
| **Capability Enforcement** | Explicit permission grants | Permission model; validated on every API call | Permission bypass tests |
| **Resource Limits** | Prevent resource exhaustion | CPU, memory, execution time limits | Resource exhaustion tests |
| **Storage Isolation** | Per-plugin storage | Separate directory; no cross-plugin access | Storage isolation tests |
| **API Gateway** | Mediated API access | All plugin calls through validated API layer | API bypass tests |
| **Signature Verification** | Plugin integrity checked | Ed25519 signatures; verified before loading | Signature bypass tests |
| **Integrity Monitoring** | Continuous integrity checks | Periodic re-verification; tamper detection | Tamper detection tests |
| **Revocation** | Immediate plugin disabling | Instant unload; storage retained | Revocation effectiveness tests |

**Resource Limits Configuration:**

```yaml
plugin_resource_limits:
  default:
    cpu_percent: 50
    memory_mb: 256
    execution_time_seconds: 30
    file_descriptors: 64
    open_files: 10
  
  strict:
    cpu_percent: 25
    memory_mb: 128
    execution_time_seconds: 15
    file_descriptors: 32
    open_files: 5
  
  per_api_call:
    timeout_seconds: 5
    max_response_size_mb: 10
```

---

### Layer 6: Logging Layer

Tamper-resistant logging with integrity chains and secure storage.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **Structured Logging** | Machine-readable log format | JSON schema; consistent fields | Log format validation |
| **Tamper Resistance** | Logs cannot be modified undetected | Append-only storage; HMAC verification | Tamper detection tests |
| **Integrity Chains** | Each entry linked to previous | SHA-256 hash chain; chain verification | Chain integrity tests |
| **Secure Storage** | Log files protected | File permissions 0640; separate directory | Permission verification |
| **Sensitive Data Filtering** | No secrets in logs | Password/token/key filtering; PII masking | Sensitive data scanning |
| **Log Rotation** | Prevent unbounded growth | Configurable rotation; old logs archived | Rotation functionality tests |
| **Retention Management** | Configurable log retention | Auto-cleanup of old logs; archive before deletion | Retention policy tests |

**Log Entry Schema:**

```json
{
  "timestamp": "ISO 8601",
  "level": "INFO|WARN|ERROR|CRITICAL",
  "category": "auth|authz|session|plugin|config|audit|system",
  "event": "event_name",
  "actor": "user_id|system|plugin_id",
  "action": "action_description",
  "resource": "resource_identifier",
  "outcome": "success|failure|denied",
  "details": {},
  "previous_hash": "SHA-256 of previous entry",
  "entry_hash": "SHA-256 of this entry"
}
```

---

### Layer 7: Build Pipeline Layer

Security integrated into the build and CI/CD pipeline.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **Static Application Security Testing (SAST)** | Automated code analysis | Bandit for Python; ESLint security plugin for JS/TS | SAST finding tracking |
| **Dependency Scanning** | Vulnerability detection in dependencies | Safety for Python; npm audit for Node.js | Dependency vulnerability tracking |
| **Secret Detection** | Prevent secrets in code | TruffleHog; git-secrets; pre-commit hooks | Secret detection tests |
| **License Compliance** | Ensure compatible licenses | License checker in CI; approved license list | License audit |
| **Code Signing** | Verify build integrity | Ed25519 signing of release artifacts | Signature verification tests |
| **Reproducible Builds** | Deterministic build output | Pinned dependencies; deterministic toolchain | Build reproducibility tests |
| **Container Scanning** | If containers used | Trivy; Grype for container images | Container vulnerability tracking |

**CI/CD Security Gates:**

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Code Push   │───►│  Lint & Test │───►│  SAST Scan   │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                                │
                    ┌──────────────┐    ┌──────▼───────┐
                    │  Build       │◄───│  Dep Scan    │
                    └──────┬───────┘    └──────────────┘
                           │
                    ┌──────▼───────┐    ┌──────────────┐
                    │  Sign        │───►│  Release     │
                    └──────────────┘    └──────────────┘
```

**SAST Configuration (Bandit):**

```ini
# .bandit
[bandit]
exclude = tests,migrations
skips = B101  # Disable assert warnings in production code
```

**Dependency Scanning:**

```yaml
# security-scanning.yml
dependencies:
  python:
    tool: safety
    command: safety check --full-report
    fail_on: any
  
  node:
    tool: npm-audit
    command: npm audit --audit-level=high
    fail_on: high
```

---

### Layer 8: Deployment Layer

Security controls applied during application deployment and installation.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **Code Signing** | Verify artifact authenticity | Ed25519 signatures on all release artifacts | Signature verification tests |
| **Integrity Verification** | Verify installation integrity | SHA-256 checksums for all installed files | Installation integrity tests |
| **Secure Installation** | Safe installation process | File permissions set during installation; secure defaults | Installation security tests |
| **Update Verification** | Verify updates before apply | Update signatures verified; integrity checked before application | Update security tests |
| **Rollback on Failure** | Recover from failed updates | Previous version preserved; automatic rollback | Rollback functionality tests |
| **Platform-Specific Security** | OS-specific protections | Windows: UAC; Linux: AppArmor/SELinux; macOS: Gatekeeper | Platform-specific security tests |

**Release Artifact Signing:**

```bash
# Sign release artifact
openssl dgst -sha256 -sign private_key.pem \
    -out authshield-lab-v1.0.0.tar.gz.sig \
    authshield-lab-v1.0.0.tar.gz

# Verify release artifact
openssl dgst -sha256 -verify public_key.pem \
    -signature authshield-lab-v1.0.0.tar.gz.sig \
    authshield-lab-v1.0.0.tar.gz
```

**Platform-Specific Installation Security:**

| Platform | Control | Implementation |
|----------|---------|----------------|
| Windows | UAC elevation | Installer requests elevation only when needed |
| Windows | Windows Defender | Exclusion configured for application directory |
| Linux | File permissions | Strict permissions set during installation |
| Linux | AppArmor profile | Optional profile for additional confinement |
| Linux | SELinux context | Optional context for additional confinement |
| macOS | Gatekeeper | Signed and notarized application |
| macOS | File quarantine | quarantine attribute set on downloaded files |
| macOS | Code signing | Hardened runtime with entitlements |

---

### Layer 9: Documentation Layer

Security documentation that guides users, developers, and administrators.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **Security Guides** | User-facing security documentation | Hardening guide; security best practices | Documentation review |
| **Threat Documentation** | Developer-facing threat information | Threat model; attack surface analysis | Threat model review |
| **Incident Procedures** | Response procedures | Incident response playbook; escalation paths | Procedure testing |
| **Security Policies** | Organizational security rules | Security policy; acceptable use; data handling | Policy compliance audit |
| **Architecture Documentation** | Security architecture details | Trust boundaries; security domains; controls | Architecture review |
| **API Security Documentation** | Plugin developer security guidance | SDK security guidelines; permission documentation | Documentation review |

**Required Documentation:**

| Document | Audience | Update Frequency |
|----------|----------|------------------|
| Security Architecture Overview | Developers, Auditors | Quarterly |
| Threat Model | Security Team, Developers | Quarterly |
| Hardening Guide | Administrators | Per release |
| Incident Response Playbook | Security Team | Quarterly |
| Plugin Security Guidelines | Plugin Developers | Per SDK release |
| Data Handling Policy | All stakeholders | Annually |
| Security Testing Guide | QA, Security Team | Per release |

---

### Layer 10: Testing Layer

Comprehensive security testing throughout the development lifecycle.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **Security Unit Tests** | Tests for individual security controls | Tests for each validation, authorization, encryption function | Test coverage tracking |
| **Integration Tests** | End-to-end security flow tests | Complete authentication, authorization, and session flows | Integration test results |
| **Fuzz Testing** | Automated input fuzzing | Fuzz all input handlers; boundary condition testing | Fuzz finding resolution |
| **Penetration Testing** | Manual security testing | Per-release penetration testing by security team | Pentest findings tracking |
| **Regression Tests** | Ensure fixes remain fixed | Automated tests for previously found vulnerabilities | Regression test results |
| **Architecture Tests** | Verify architectural constraints | Dependency rules; layer boundary enforcement | Architecture test results |
| **Load Testing** | Security under stress | Rate limiting; resource exhaustion; timeout behavior | Load test security results |

**Security Test Categories:**

| Category | Scope | Frequency | Owner |
|----------|-------|-----------|-------|
| Unit Security Tests | Individual functions | Every commit | Developers |
| Integration Security Tests | Module interactions | Every commit | Developers |
| Fuzz Tests | Input handlers | Weekly | Security Team |
| Penetration Tests | Full application | Per release | Security Team |
| Architecture Tests | Dependencies, layers | Every commit | CI/CD Pipeline |
| Regression Tests | Known vulnerabilities | Every commit | CI/CD Pipeline |
| Load Tests | Performance under attack | Per release | QA Team |

**Fuzz Testing Targets:**

| Target | Fuzz Strategy | Timeout |
|--------|--------------|---------|
| API endpoints | Schema-aware fuzzing | 30s per endpoint |
| Input fields | Boundary value analysis | 10s per field |
| File upload handlers | Malicious file fuzzing | 60s per handler |
| Configuration parsers | Malformed config fuzzing | 30s per parser |
| Import handlers | Corrupted import fuzzing | 60s per handler |

---

### Layer 11: Administration Layer

Administrative controls that oversee and enforce security policies.

| Control | Description | Implementation | Validation |
|---------|-------------|----------------|------------|
| **RBAC** | Role-based access control | Four roles: Learner, Educator, Admin, Super Admin | RBAC bypass tests |
| **Approval Workflows** | Multi-admin approval for critical changes | Critical operations require second admin approval | Approval bypass tests |
| **Audit Logging** | All admin actions logged | Immutable audit trail with hash chains | Audit completeness tests |
| **MFA for Admins** | Multi-factor authentication required | TOTP-based MFA for all admin accounts | MFA bypass tests |
| **Session Management** | Shorter admin sessions | 15-minute idle timeout; re-auth for sensitive ops | Session management tests |
| **Segregation of Duties** | No single admin has all power | Critical operations split across roles | SoD compliance tests |
| **Admin Monitoring** | Admin behavior monitoring | Login patterns; action frequency; anomaly detection | Monitoring effectiveness tests |

**Admin Action Matrix:**

| Action | Required Role | Re-auth | Approval | Audit |
|--------|--------------|---------|----------|-------|
| View users | Admin | No | No | Yes |
| Create user | Admin | No | No | Yes |
| Modify user | Admin | Yes | No | Yes |
| Delete user | Admin | Yes | Admin confirmation | Yes |
| Change user role | Super Admin | Yes | Super Admin approval | Yes |
| Install plugin | Admin | Yes | Permission review | Yes |
| Uninstall plugin | Admin | Yes | No | Yes |
| Modify config | Admin | Yes | No | Yes |
| Modify security policy | Super Admin | Yes | Super Admin approval | Yes |
| Create backup | Admin | No | No | Yes |
| Restore backup | Admin | Yes | Admin confirmation | Yes |
| View audit logs | Admin | Yes | No | Yes |
| Modify audit config | Super Admin | Yes | Super Admin approval | Yes |

## 4. Layer Interaction

Layers do not operate in isolation. They form an interconnected defense system:

```
Input → [L1: Validation] → [L2: Isolation] → [L4: Config Check]
  → [L5: Plugin Gate] → [L3: Storage Access] → [L6: Logging]
  → [L11: Admin Oversight]
```

Each layer provides defense against different threat categories:

| Layer | Primary Threats Addressed |
|-------|--------------------------|
| L1: Application | XSS, CSRF, injection, input manipulation |
| L2: Runtime | Process exploitation, memory corruption, sandbox escape |
| L3: Storage | Data theft, corruption, unauthorized access |
| L4: Configuration | Configuration tampering, insecure defaults |
| L5: Plugin | Malicious plugins, plugin abuse, resource exhaustion |
| L6: Logging | Log tampering, evidence destruction, repudiation |
| L7: Build | Vulnerable dependencies, code injection, supply chain |
| L8: Deployment | Tampered installations, unauthorized modifications |
| L9: Documentation | Security knowledge gaps, incident response failures |
| L10: Testing | Undetected vulnerabilities, regression of fixes |
| L11: Administration | Privilege abuse, unauthorized actions, insider threats |

## 5. Monitoring Across All Layers

Each layer contributes to a comprehensive monitoring picture:

| Layer | Monitoring Events |
|-------|-------------------|
| L1 | Input validation failures, rate limit triggers, CSRF violations |
| L2 | Process crashes, memory violations, IPC failures |
| L3 | File access violations, encryption failures, integrity check failures |
| L4 | Configuration changes, integrity check results, schema violations |
| L5 | Plugin API violations, resource limit breaches, sandbox violations |
| L6 | Log integrity failures, chain breaks, rotation events |
| L7 | SAST findings, dependency vulnerabilities, build failures |
| L8 | Installation integrity results, update verification results |
| L9 | Documentation gaps identified, procedure testing results |
| L10 | Test failures, fuzz findings, regression detections |
| L11 | Admin action anomalies, privilege escalation attempts |

## 6. Validation of Defense-in-Depth

| Validation Method | Description | Frequency |
|-------------------|-------------|-----------|
| Architecture Review | Verify all layers are implemented | Per release |
| Penetration Testing | Attempt to bypass each layer | Per release |
| Red Team Exercise | Simulate attacker trying all bypass paths | Annually |
| Compliance Audit | Verify controls match documentation | Quarterly |
| Automated Testing | Verify each layer's controls work | Every commit |
| Incident Post-Mortem | Review if layers failed during incidents | Per incident |
