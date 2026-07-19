# AuthShield Lab — Security Engineering Standards

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab is a cybersecurity education platform that must itself be secure. This document defines the security engineering standards covering dependency verification, supply chain security, code signing, cryptographic standards, secret management, and integrity verification. Security is not a feature; it is a property of the entire system.

---

## 2. Dependency Verification

### 2.1 Hash Checking

All dependencies are verified against cryptographic hashes at install time.

```bash
# Python: generate and verify hashes
pip-compile --generate-hashes --output-file=requirements.lock pyproject.toml
pip install --require-hashes -r requirements.lock

# Verify hash consistency
pip install --dry-run --require-hashes -r requirements.lock
```

### 2.2 Sigstore Verification (optional)

```bash
# Verify package signatures via Sigstore
pip install --require-hashes --verify-sigstore -r requirements.lock

# Or verify individual package
sigstore verify identity \
  --certificate identity-cert.pem \
  --certificate-oidc-issuer "https://accounts.google.com" \
  --certificate-identity "user@example.com" \
  package.whl
```

### 2.3 Lock File Integrity

| Component | Integrity Check | Frequency |
|-----------|----------------|-----------|
| Python packages | SHA-256 hashes in `requirements.lock` | Every install |
| Node packages | Integrity hashes in `package-lock.json` | Every `npm ci` |
| Rust crates | Checksums in `Cargo.lock` | Every build |
| Vendored deps | SHA-256 manifest | Every build |

---

## 3. Supply Chain Security

### 3.1 SBOM Generation

Software Bill of Materials (SBOM) is generated for every release in SPDX and CycloneDX format.

```bash
# Python SBOM (CycloneDX)
pip install cyclonedx-bom
cyclonedx-py environment --output-file sbom-python.json
cyclonedx-py environment --format spdx --output-file sbom-python.spdx.json

# Node SBOM (CycloneDX)
npx cyclonedx-npm --output-file sbom-node.json

# Rust SBOM (CycloneDX)
cargo install cargo-cyclonedx
cargo cyclonedx --output-file sbom-rust.json
```

### 3.2 SBOM Schema

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "version": 1,
  "metadata": {
    "tools": [
      {"vendor": "CycloneDX", "name": "cyclonedx-bom", "version": "2.0.0"}
    ],
    "timestamp": "2026-07-19T12:00:00Z",
    "component": {
      "name": "authshield-lab",
      "version": "1.0.0",
      "type": "application"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "fastapi",
      "version": "0.111.0",
      "purl": "pkg:pypi/fastapi@0.111.0",
      "hashes": [
        {"alg": "SHA-256", "value": "abc123..."}
      ],
      "licenses": [{"license": {"id": "MIT"}}]
    }
  ],
  "dependencies": [
    {
      "ref": "authshield-lab",
      "dependsOn": ["fastapi", "sqlalchemy", "pydantic"]
    }
  ]
}
```

### 3.3 Dependency Scanning

| Tool | Scope | Integration | Threshold |
|------|-------|-------------|-----------|
| **pip-audit** | Python dependencies | CI/CD, pre-commit | 0 critical/high |
| **npm audit** | Node dependencies | CI/CD, pre-commit | 0 critical/high |
| **cargo-audit** | Rust dependencies | CI/CD, pre-commit | 0 critical/high |
| **Snyk** (optional) | All ecosystems | CI/CD, scheduled | 0 critical |

### 3.4 CI/CD Integration

```yaml
# .github/workflows/supply-chain.yml
name: Supply Chain Security
on: [push, pull_request, schedule]

jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate Python SBOM
        run: |
          pip install cyclonedx-bom
          cyclonedx-py environment --output-file sbom-python.json
      - name: Generate Node SBOM
        run: |
          npm ci
          npx cyclonedx-npm --output-file sbom-node.json
      - name: Upload SBOMs
        uses: actions/upload-artifact@v4
        with:
          name: sboms
          path: sbom-*.json

  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Audit Python
        run: |
          pip install pip-audit
          pip-audit --require-hashes --strict
      - name: Audit Node
        run: |
          npm ci
          npm audit --audit-level=critical
```

---

## 4. Code Signing

### 4.1 Release Signing (Ed25519)

```python
from authshield.crypto import DigitalSignature

signer = DigitalSignature(algorithm="ed25519")

# Generate signing keypair (one-time, stored securely)
key_pair = signer.generate_keypair()
# Private key stored in secure location (HSM, key vault, or encrypted file)
# Public key distributed with application

# Sign release artifact
signature = signer.sign_file(
    file_path=Path("authshield-lab-1.0.0.tar.gz"),
    private_key=key_pair.private_key,
)

# Verify release artifact
valid = signer.verify_file(
    file_path=Path("authshield-lab-1.0.0.tar.gz"),
    signature=signature,
    public_key=key_pair.public_key,
)
```

### 4.2 Git Commit Signing (GPG/SSH)

```bash
# Configure Git for signing
git config --global gpg.format ssh
git config --global user.signingkey "ssh-ed25519 AAAA..."

# Sign commits
git commit -S -m "feat: add new feature"

# Sign tags
git tag -s v1.0.0 -m "Release 1.0.0"

# Verify signatures
git log --show-signature
git verify-tag v1.0.0
```

### 4.3 Signing Key Management

| Key Type | Algorithm | Storage | Rotation |
|----------|-----------|---------|----------|
| **Release signing** | Ed25519 | Encrypted file / HSM | Annual |
| **Commit signing** | Ed25519 (SSH) | SSH agent / hardware token | As needed |
| **Plugin signing** | Ed25519 | Developer keychain | Per-developer |
| **Code review** | Ed25519 (SSH) | SSH agent | As needed |

---

## 5. Package Verification

### 5.1 Checksum Manifests

```bash
# Generate checksums for release artifacts
sha256sum authshield-lab-1.0.0.tar.gz > SHA256SUMS
sha256sum authshield-lab-1.0.0-linux-x64.tar.gz >> SHA256SUMS
sha256sum authshield-lab-1.0.0-macos-arm64.dmg >> SHA256SUMS
sha256sum authshield-lab-1.0.0-windows-x64.exe >> SHA256SUMS

# Sign the checksum file
gpg --armor --detach-sign SHA256SUMS

# User verification
sha256sum -c SHA256SUMS
gpg --verify SHA256SUMS.asc SHA256SUMS
```

### 5.2 Signature Validation

```python
from authshield.crypto import PackageVerifier

verifier = PackageVerifier(
    trusted_keys_dir=Path("keys/release/"),
)

# Verify release package
result = verifier.verify_package(
    package_path=Path("authshield-lab-1.0.0.tar.gz"),
    signature_path=Path("authshield-lab-1.0.0.tar.gz.sig"),
    checksum_path=Path("SHA256SUMS"),
)

if not result.valid:
    raise SecurityError(f"Package verification failed: {result.reason}")
```

---

## 6. Secure Defaults

### 6.1 Default Configuration

| Setting | Default | Rationale |
|---------|---------|-----------|
| **Server bind** | `127.0.0.1` | Localhost only; no network exposure |
| **CSRF protection** | Enabled | Prevent cross-site request forgery |
| **CSP headers** | Enabled | Prevent XSS attacks |
| **Session timeout** | 1 hour | Limit session exposure |
| **Password minimum** | 12 characters | Resist brute-force attacks |
| **Max login attempts** | 5 | Prevent brute-force attacks |
| **Lockout duration** | 15 minutes | Slow down brute-force attacks |
| **Database encryption** | Enabled | Protect data at rest |
| **Plugin sandbox** | Level 1 | Import restrictions for plugins |
| **Network access** | Disabled (offline-first) | No unintended network calls |
| **Auto-update** | Disabled | User opt-in required |

### 6.2 Security Headers

```python
# FastAPI middleware for security headers
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), "
        "payment=(), usb=(), magnetometer=(), gyroscope=()"
    )
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response
```

---

## 7. Cryptographic Standards

### 7.1 Algorithm Selection

| Purpose | Algorithm | Parameters | Standard |
|---------|-----------|------------|----------|
| **Password hashing** | Argon2id | memory=64MB, iterations=3, parallelism=4 | RFC 9106 |
| **Password hashing (fallback)** | bcrypt | rounds=12 | — |
| **Password hashing (legacy)** | PBKDF2-SHA256 | iterations=600,000 | NIST SP 800-132 |
| **Digital signatures** | Ed25519 | — | RFC 8032 |
| **Digital signatures (fallback)** | RSA-PSS | 2048-bit minimum | NIST SP 800-56B |
| **Symmetric encryption** | AES-256-GCM | 256-bit key | NIST SP 800-38D |
| **Key derivation** | HKDF-SHA256 | — | RFC 5869 |
| **Integrity hashing** | SHA-256 | — | FIPS 180-4 |
| **JWT signing** | Ed25519 | — | RFC 8037 |
| **TLS** | TLS 1.3 | — | RFC 8446 |

### 7.2 Argon2id Parameters

```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__type="id",  # Argon2id variant
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,  # 3 iterations
    argon2__parallelism=4,  # 4 threads
    argon2__hash_len=32,  # 32-byte hash
    argon2__salt_len=16,  # 16-byte salt
    argon2__desired_keylen=32,  # 32-byte derived key
)

# Hash a password
hashed = pwd_context.hash("user_password")

# Verify a password
valid = pwd_context.verify("user_password", hashed)

# Check if rehashing is needed
needs_rehash = pwd_context.needs_update(hashed)
```

### 7.3 Ed25519 Signature Parameters

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization

# Generate keypair
private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Serialize public key
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
)

# Sign data
signature = private_key.sign(b"data to sign")

# Verify signature
try:
    public_key.verify(signature, b"data to sign")
    valid = True
except Exception:
    valid = False
```

---

## 8. Secret Management

### 8.1 Environment Variables

```bash
# Required secrets (must be set before running)
export AUTHSHIELD_SECURITY_SECRET_KEY="your-secret-key-here"

# Optional secrets
export AUTHSHIELD_DB_PASSWORD="database-password"
export AUTHSHIELD_SMTP_PASSWORD="email-password"

# Never commit .env files
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
echo "secrets/" >> .gitignore
```

### 8.2 Secret Generation

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Or using OpenSSL
openssl rand -base64 64

# Or using uuid4
python -c "import uuid; print(uuid.uuid4().hex)"
```

### 8.3 Secret Handling Rules

| Rule | Implementation |
|------|---------------|
| **No hardcoded secrets** | ruff rule `S105`/`S106` catches hardcoded passwords |
| **No secrets in logs** | Redaction filter masks `password`, `secret`, `token`, `api_key` |
| **No secrets in config files** | Use `SecretStr` type; environment variables preferred |
| **No secrets in git** | `.gitignore` excludes `.env`, `secrets/`, `*.key` |
| **No secrets in error messages** | Exception handlers sanitize error output |
| **Secret rotation** | Support for key rotation without downtime |
| **Minimum secret length** | 32 characters for cryptographic secrets |

### 8.4 Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: "1.7.8"
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        additional_dependencies: ["bandit[toml]"]

  - repo: https://github.com/Yelp/detect-secrets
    rev: "v1.4.0"
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
```

---

## 9. Certificate Management

### 9.1 Development Certificates

```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey ed25519 -nodes \
  -keyout dev-key.pem \
  -out dev-cert.pem \
  -days 365 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

# Trust the certificate (macOS)
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain dev-cert.pem

# Trust the certificate (Linux)
sudo cp dev-cert.pem /usr/local/share/ca-certificates/authshield-dev.crt
sudo update-ca-certificates
```

### 9.2 Local CA for Development

```python
from authshield.crypto import CertificateManager

cm = CertificateManager()

# Create local CA
ca = cm.create_ca(
    subject="AuthShield Lab Dev CA",
    valid_years=10,
    key_algorithm="ed25519",
)

# Issue development certificate
dev_cert = cm.issue_certificate(
    ca=ca,
    subject="localhost",
    valid_days=365,
    san=["DNS:localhost", "IP:127.0.0.1", "DNS:*.local"],
)
```

### 9.3 Certificate Verification

```python
from authshield.crypto import CertificateVerifier

verifier = CertificateVerifier(
    trusted_cas=Path("certs/trusted/"),
)

# Verify a certificate chain
result = verifier.verify(
    certificate=Path("server-cert.pem"),
    chain=[Path("ca-cert.pem")],
)

if not result.valid:
    raise SecurityError(f"Certificate verification failed: {result.reason}")
```

---

## 10. Integrity Verification

### 10.1 File Checksums

```python
from authshield.crypto import IntegrityHasher

hasher = IntegrityHasher()

# Generate checksum
checksum = hasher.hash_file(Path("authshield-lab-1.0.0.tar.gz"))
# "sha256:abc123def456..."

# Verify checksum
valid = hasher.verify_file(
    file_path=Path("authshield-lab-1.0.0.tar.gz"),
    expected="sha256:abc123def456...",
)

# Generate checksums for directory
manifest = hasher.hash_directory(
    directory=Path("dist/"),
    output=Path("SHA256SUMS"),
)
```

### 10.2 Database Integrity

```python
from sqlalchemy import text

async def verify_database_integrity(db_session):
    # SQLite integrity check
    result = await db_session.execute(text("PRAGMA integrity_check"))
    integrity = result.scalar()
    
    if integrity != "ok":
        logger.critical("database.integrity.failed", result=integrity)
        raise DatabaseIntegrityError(f"Database integrity check failed: {integrity}")
    
    # Verify checksums of critical tables
    tables = ["users", "sessions", "assessments", "audit_log"]
    for table in tables:
        result = await db_session.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        )
        count = result.scalar()
        logger.info(f"database.table.{table}.count", count=count)
```

### 10.3 Application Integrity

```python
from authshield.crypto import IntegrityVerifier

verifier = IntegrityVerifier(
    manifest_path=Path("integrity-manifest.json"),
)

# Verify application files on startup
result = verifier.verify_all()
if not result.valid:
    for violation in result.violations:
        logger.critical(
            "integrity.violation",
            file=violation.file,
            expected=violation.expected,
            actual=violation.actual,
        )
    raise IntegrityError("Application integrity verification failed")
```

---

## 11. Security Audit Trail

### 11.1 Events Logged

| Event | Channel | Level | Data Captured |
|-------|---------|-------|---------------|
| User login (success) | Audit | INFO | user_id, ip, timestamp |
| User login (failure) | Security | WARNING | username, ip, attempt_count |
| Account lockout | Security | WARNING | user_id, ip, lockout_duration |
| Password change | Audit | INFO | user_id, ip, timestamp |
| Session created | Audit | INFO | user_id, session_id, ip |
| Session revoked | Audit | INFO | user_id, session_id, reason |
| Permission denied | Security | WARNING | user_id, resource, permission |
| Plugin loaded | Audit | INFO | plugin_id, version, permissions |
| Plugin error | Security | WARNING | plugin_id, error, context |
| Database modification | Audit | INFO | table, operation, user_id |
| Configuration change | Audit | INFO | setting, old_value, new_value |
| Export/download | Audit | INFO | user_id, file_type, file_name |
| Integrity violation | Security | CRITICAL | file, expected, actual |

### 11.2 Audit Log Integrity

```python
from authshield.logging import AuditLog

audit = AuditLog(
    log_dir=Path("~/.local/share/authshield-lab/logs"),
    integrity_check=True,
)

# Write audit entry with integrity hash
audit.write({
    "event": "user.login",
    "actor": {"user_id": "user_123"},
    "action": "login",
    "result": "success",
})

# Verify audit log integrity (hash chain)
is_valid = audit.verify_integrity()
# Raises AuditLogTamperedError if integrity check fails
```

---

## 12. Incident Response

### 12.1 Security Incident Classification

| Severity | Description | Response Time | Escalation |
|----------|-------------|---------------|------------|
| **Critical** | Active exploitation, data breach | Immediate | CISO, CTO |
| **High** | Vulnerability with exploit available | 4 hours | Security team |
| **Medium** | Vulnerability without known exploit | 24 hours | Development lead |
| **Low** | Minor security improvement | 1 week | Development team |

### 12.2 Incident Response Process

```
1. Detection
   ├── Automated: Security scanning, integrity checks
   ├── Manual: User reports, security audits
   └── External: CVE notifications, security research

2. Triage
   ├── Classify severity
   ├── Identify affected components
   ├── Determine scope of impact
   └── Assign response team

3. Containment
   ├── Isolate affected systems
   ├── Block attack vectors
   ├── Preserve evidence
   └── Notify affected users (if required)

4. Eradication
   ├── Remove vulnerability
   ├── Patch affected code
   ├── Rotate compromised secrets
   └── Verify patches

5. Recovery
   ├── Restore from clean backups
   ├── Verify system integrity
   ├── Resume normal operations
   └── Monitor for recurrence

6. Post-incident
   ├── Incident report
   ├── Lessons learned
   ├── Process improvements
   └── Security control updates
```

---

## 13. Security Testing

### 13.1 Static Analysis

| Tool | Scope | Integration |
|------|-------|-------------|
| **ruff** | Python linting (includes security rules) | Pre-commit, CI/CD |
| **bandit** | Python security analysis | CI/CD |
| **eslint** | TypeScript security rules | Pre-commit, CI/CD |
| **detect-secrets** | Secret detection | Pre-commit |

### 13.2 Dynamic Analysis

| Tool | Scope | Frequency |
|------|-------|-----------|
| **OWASP ZAP** (optional) | Web application security | Quarterly |
| **Manual penetration testing** | Full application | Annual |
| **Fuzz testing** | API endpoints | CI/CD |

### 13.3 Security Gates

```yaml
# CI/CD security gates
security-gates:
  - name: "No critical vulnerabilities"
    command: "pip-audit --strict --require-hashes"
    threshold: 0

  - name: "No hardcoded secrets"
    command: "detect-secrets scan --all-files"
    threshold: 0

  - name: "No unsafe code patterns"
    command: "bandit -r src/ -ll"
    threshold: 0

  - name: "SBOM generated"
    command: "cyclonedx-py environment --output-file sbom.json"
    required: true

  - name: "Code signed"
    command: "gpg --verify release.tar.gz.sig release.tar.gz"
    required: true
```

---

## 14. Compliance

### 14.1 Standards Alignment

| Standard | Applicability | Implementation |
|----------|--------------|----------------|
| **OWASP Top 10** | Web application security | Input validation, output encoding, authentication |
| **CWE/SANS Top 25** | Common weakness enumeration | Addressed via code review and static analysis |
| **NIST SP 800-53** | Security controls | Access control, audit, configuration management |
| **ISO 27001** | Information security management | Documented policies, risk assessment |

### 14.2 Security Documentation

| Document | Purpose | Review Cycle |
|----------|---------|-------------|
| SECURITY.md | Vulnerability reporting policy | Annual |
| Threat Model | Threat identification and mitigation | Annual |
| Risk Register | Security risk tracking | Quarterly |
| Incident Response Plan | Response procedures | Annual |
| Security Audit Report | Third-party assessment | Annual |

---

*Document maintained by the AuthShield Lab Security Team. Review quarterly.*
