# AuthShield Lab — Plugin Security

> **Version:** 1.0.0
> **Status:** Authoritative
> **See also:** [Plugin Sandbox](PLUGIN_SANDBOX.md) · [Plugin Package Format](PLUGIN_PACKAGE_FORMAT.md)

---

## 1. Overview

Security is a core concern of the AuthShield Lab plugin system. Since the platform is a
cybersecurity education tool, plugins must be trustworthy and verifiable. The security model
covers:

1. **Digital signature verification** — ensure plugins are from trusted publishers.
2. **Integrity checking** — ensure plugins have not been tampered with.
3. **Permission enforcement** — ensure plugins only use declared capabilities.
4. **Capability validation** — ensure declared capabilities match actual usage.
5. **Audit logging** — ensure all security-relevant actions are traceable.

---

## 2. Digital Signature Verification

### 2.1 Supported Algorithms

| Algorithm | File Format | Use Case |
|---|---|---|
| **X.509 (CMS/PKCS#7)** | `.p7s` | Primary signing method. Uses a certificate chain. |
| **GPG (OpenPGP)** | `.sig` | Alternative signing method. Uses GPG keyring. |

### 2.2 X.509 Signing Process

1. Publisher generates an X.509 certificate (self-signed or CA-signed).
2. Publisher signs the `integrity.json` file with their private key.
3. The signature is stored in `signature.p7s` (PKCS#7 detached format).
4. The public certificate is distributed to the platform's `trust_anchors/` directory.

### 2.3 Verification Process

```
1. Read signature.p7s.
2. Read integrity.json.
3. Extract the certificate chain from the signature.
4. Verify the certificate chain against trust anchors.
5. Verify the signature over integrity.json.
6. Verify integrity.json checksums against all package files.
7. If all checks pass → plugin is trusted.
8. If any check fails → plugin is untrusted.
```

### 2.4 Trust Anchors

Trust anchor certificates are stored in:

```
~/.authshieldlab/trust_anchors/
├── authshield-lab-prod.crt       # Platform publisher certificate
├── authshield-lab-dev.crt        # Development certificate
└── custom/
    └── university-oxford.crt     # Institution-specific certificate
```

**Rules:**
- Only certificates in this directory are trusted.
- The kernel loads all `.crt` and `.pem` files at startup.
- Certificates can be revoked by removing them from the directory.

---

## 3. Integrity Checking

### 3.1 Checksum Algorithm

The default algorithm is **SHA-256**. SHA-512 is also supported.

### 3.2 integrity.json Format

```json
{
  "algorithm": "sha256",
  "generated_at": "2026-07-19T12:00:00Z",
  "files": {
    "manifest.json": "a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
    "src/__init__.py": "f6e5d4c3b2a109876543210fedcba9876543210fedcba9876543210fedcba987",
    "src/plugin.py": "1a2b3c4d5e6f7890123456789012345678901234567890123456789012345678"
  }
}
```

### 3.3 Verification

The kernel verifies checksums during the Signature Verification lifecycle stage:

```python
def verify_integrity(self, package_path: Path, integrity_file: Path) -> bool:
    """Verify all file checksums match the integrity manifest."""
    integrity = json.loads(integrity_file.read_text())
    algorithm = integrity["algorithm"]

    for relative_path, expected_hash in integrity["files"].items():
        file_path = package_path / relative_path
        actual_hash = hashlib.new(algorithm, file_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            self.audit.log(
                "integrity.mismatch",
                file=relative_path,
                expected=expected_hash,
                actual=actual_hash,
            )
            return False

    return True
```

---

## 4. Permission Enforcement

### 4.1 Static Analysis

During the Validation lifecycle stage, the kernel performs static analysis:

1. Parse the plugin's Python AST.
2. Detect imports of restricted modules.
3. Detect calls to restricted builtins.
4. Detect network access patterns.
5. Compare detected usage against declared capabilities.

**Results:**
- All detected usage must be covered by declared capabilities.
- Undetected usage in production mode → plugin is rejected.
- Undetected usage in development mode → warning logged.

### 4.2 Runtime Enforcement

Every SDK API call checks permissions at runtime:

```python
class PermissionEnforcer:
    def check(self, plugin_id: str, permission: str) -> bool:
        manifest = self._get_manifest(plugin_id)
        declared = {p["permission"] for p in manifest.get("permissions", [])}
        return permission in declared

    def enforce(self, plugin_id: str, permission: str) -> None:
        if not self.check(plugin_id, permission):
            raise PermissionDenied(
                f"Plugin '{plugin_id}' does not have permission '{permission}'. "
                f"Declare it in manifest.json → permissions."
            )
```

### 4.3 Permission Categories

| Permission | Scope | Risk Level |
|---|---|---|
| `storage:read` | Read plugin's own storage | Low |
| `storage:rw` | Read/write plugin's own storage | Medium |
| `ui:panel` | Register UI panels | Low |
| `ui:toolbar` | Register toolbar buttons | Low |
| `event:subscribe` | Subscribe to events | Low |
| `event:publish` | Publish events | Medium |
| `commands:register` | Register commands | Medium |
| `config:read` | Read plugin's config | Low |
| `config:write` | Write plugin's config | Medium |
| `report:register` | Register report types | Low |
| `report:generate` | Generate reports | Low |
| `localization:register` | Register translations | Low |
| `accessibility:register` | Register accessibility features | Low |
| `kernel:override` | Override kernel services | High (restricted) |

---

## 5. Capability Validation

### 5.1 Manifest vs Actual Usage

The kernel compares declared capabilities against actual API usage:

```
Declared: ["ui:panel", "event:subscribe", "storage:rw"]

Actual usage detected:
  ✓ ctx.ui.register_panel(...)        → ui:panel ✓
  ✓ ctx.events.subscribe_event(...)   → event:subscribe ✓
  ✓ ctx.storage.set_store(...)        → storage:rw ✓
  ✓ ctx.logging.log_info(...)         → (always allowed) ✓

Result: All capabilities covered.
```

### 5.2 Undeclared Capability Detection

If a plugin uses an API without declaring the corresponding capability:

```
Declared: ["ui:panel"]

Actual usage detected:
  ✓ ctx.ui.register_panel(...)        → ui:panel ✓
  ✗ ctx.storage.set_store(...)        → storage:rw ✗ NOT DECLARED

Result: Capability mismatch. Plugin will be rejected in production mode.
```

---

## 6. Least Privilege

### 6.1 Minimal Permissions by Default

New plugins start with **zero permissions**. The developer must explicitly declare each
permission in the manifest with a justification.

### 6.2 Permission Request Review

The platform displays requested permissions during plugin installation:

```
Plugin: threat-dashboard v1.2.0
Author: AuthShield Lab Team

Requested permissions:
  ✓ storage:rw  — "Store dashboard layout preferences and cached threat data."
  ✓ ui:panel    — "Display the main threat visualization panel."

Do you want to install this plugin? [Yes/No/Review Details]
```

### 6.3 Runtime Permission Revocation

Users can revoke permissions after installation:

```bash
authshield-cli plugin permissions revoke threat-dashboard storage:rw
```

If a revoked permission is used at runtime, the SDK raises `PermissionDenied`.

---

## 7. Secure Defaults

All sensitive operations require explicit permission:

| Operation | Default | Required Permission |
|---|---|---|
| Network access | Blocked | Not available (offline-first) |
| Filesystem access | Blocked | Not available (use Storage API) |
| Storage read/write | Blocked | `storage:rw` |
| Event publishing | Blocked | `event:publish` |
| Command registration | Blocked | `commands:register` |
| Kernel service override | Blocked | `kernel:override` (restricted) |
| System notifications | Blocked | User consent required |

---

## 8. Audit Logging

### 8.1 What Is Logged

Every security-relevant operation is logged:

| Event | Description |
|---|---|
| `plugin.discovered` | Plugin directory found during scan. |
| `plugin.validated` | Manifest validation result. |
| `plugin.signature_verified` | Signature verification result. |
| `plugin.loaded` | Python module imported. |
| `plugin.activated` | Plugin activated successfully. |
| `plugin.permission_granted` | Permission granted to plugin. |
| `plugin.permission_denied` | Permission check failed. |
| `plugin.capability_violated` | Undeclared capability used. |
| `plugin.faulted` | Plugin crashed or was terminated. |
| `plugin.deactivated` | Plugin deactivated. |
| `plugin.removed` | Plugin removed from system. |
| `security.integrity_mismatch` | File checksum mismatch. |
| `security.signature_invalid` | Signature verification failed. |
| `security.untrusted_plugin` | Plugin from untrusted publisher. |

### 8.2 Audit Log Format

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-07-19T12:00:00Z",
  "event_type": "plugin.signature_invalid",
  "plugin_id": "unknown-plugin",
  "severity": "warning",
  "details": {
    "signature_file": "signature.p7s",
    "error": "Certificate not found in trust anchors",
    "certificate_subject": "CN=Unknown Publisher"
  },
  "previous_hash": "sha256:abc123...",
  "hash": "sha256:def456..."
}
```

### 8.3 Tamper-Evident Chain

Each audit log entry includes a hash of the previous entry, creating a tamper-evident chain:

```
Entry 1: hash = SHA256(data_1)
Entry 2: previous_hash = hash_1, hash = SHA256(previous_hash + data_2)
Entry 3: previous_hash = hash_2, hash = SHA256(previous_hash + data_3)
```

If any entry is modified, the chain breaks and tampering is detected.

---

## 9. Package Verification (Before Installation)

### 9.1 Pre-Installation Checks

Before installing a plugin package, the platform performs:

1. **File existence** — all required files present.
2. **Manifest validation** — JSON schema conformance.
3. **Integrity check** — all checksums match.
4. **Signature verification** — signature is valid and from a trusted publisher.
5. **Permission review** — permissions are reasonable for the plugin type.
6. **Static analysis** — no restricted module usage detected.
7. **Size check** — package within size limits.

### 9.2 Installation Decision

| Check | Pass | Fail |
|---|---|---|
| All checks pass | Install (with user confirmation) | — |
| Signature invalid | — | Block installation |
| Integrity mismatch | — | Block installation |
| Untrusted publisher | Warning | User may override in dev mode |
| Permission risk high | Warning | User must explicitly approve |
| Static analysis warning | Warning | User must review |

---

## 10. Tamper Detection

### 10.1 Checksum Validation

The kernel validates checksums at multiple points:

1. **At installation** — full package integrity check.
2. **At startup** — re-validate critical files (manifest.json, entry point).
3. **At runtime** — periodic random checks (configurable).

### 10.2 Tamper Response

If tampering is detected:

1. Log a `security.tamper_detected` audit event with severity `critical`.
2. Disable the plugin immediately.
3. Notify the user through the UI.
4. Preserve the tampered files for forensic analysis.
5. Do not delete the plugin (may be needed for investigation).

---

## 11. Trusted Publisher Policies

### 11.1 Publisher Trust Levels

| Level | Description | Capabilities |
|---|---|---|
| **Platform Publisher** | AuthShield Lab official key | All capabilities including `kernel:override` |
| **Verified Publisher** | Institution-verified key | All standard capabilities |
| **Community Publisher** | Self-signed or unverified | Standard capabilities, warning shown |
| **Unknown** | No signature | Blocked in production |

### 11.2 Trust Configuration

```json
{
  "plugins": {
    "security": {
      "trust_policy": {
        "require_signature": true,
        "require_integrity": true,
        "allow_self_signed": false,
        "allowed_publishers": [
          "authshield-lab-prod-key-2026",
          "university-oxford-key-2026"
        ],
        "blocked_publishers": [],
        "enforce_in_development": false
      }
    }
  }
}
```

---

## 12. Security Scanning Checklist

Before publishing a plugin, the developer should verify:

- [ ] No hardcoded secrets, API keys, or passwords.
- [ ] No network access patterns (offline-first).
- [ ] No filesystem access outside Storage API.
- [ ] No subprocess or system command execution.
- [ ] No dynamic code execution (exec, eval).
- [ ] All user inputs are validated.
- [ ] All outputs are properly escaped.
- [ ] Error messages do not leak sensitive information.
- [ ] Logging does not contain PII.
- [ ] Storage data is encrypted at rest (if sensitive).
- [ ] No known vulnerable dependencies.
- [ ] Permission requests are justified and minimal.
- [ ] All interactive elements are accessible.
- [ ] All text is translatable (no hardcoded strings in UI).

---

## 13. Vulnerability Reporting

### 13.1 Reporting Process

If a security vulnerability is discovered in a plugin:

1. **Do not** disclose publicly.
2. Email `security@authshieldlab.dev` with:
   - Plugin ID and version.
   - Description of the vulnerability.
   - Steps to reproduce.
   - Potential impact.
3. The security team will acknowledge within 48 hours.
4. A fix will be developed and a patched version released.
5. The vulnerability will be disclosed after the fix is available.

### 13.2 Vulnerability Severity

| Severity | Response Time | Description |
|---|---|---|
| Critical | 24 hours | Remote code execution, data exfiltration. |
| High | 72 hours | Privilege escalation, sandbox escape. |
| Medium | 1 week | Information disclosure, denial of service. |
| Low | 2 weeks | Minor issues, best practice violations. |

---

## 14. Security Best Practices for Plugin Developers

1. **Declare minimum permissions** — only request what you need.
2. **Validate all inputs** — never trust data from events or configuration.
3. **Use the SDK APIs** — never bypass the sandbox.
4. **Log security events** — use the Logging API for audit trails.
5. **Handle errors gracefully** — never expose internals in error messages.
6. **Keep dependencies updated** — use the latest compatible versions.
7. **Test security** — use the plugin test harness to verify sandbox compliance.
8. **Sign your plugins** — use a trusted publisher key for distribution.

---

## 15. References

- [Plugin Sandbox](PLUGIN_SANDBOX.md)
- [Plugin Package Format](PLUGIN_PACKAGE_FORMAT.md)
- [Plugin Manifest Specification](PLUGIN_MANIFEST_SPECIFICATION.md)
- [Plugin Lifecycle](PLUGIN_LIFECYCLE.md)

---

*End of document.*
