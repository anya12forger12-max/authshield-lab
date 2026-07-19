# AuthShield Lab — Security Validation Framework

## 1. Overview

Security validation ensures that the security architecture, controls, and policies of
AuthShield Lab are implemented correctly, remain effective over time, and comply with
defined standards. This framework covers automated validation, manual validation,
CI/CD integration, architecture drift detection, and compliance reporting.

## 2. Validation Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 SECURITY VALIDATION FRAMEWORK                 │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                AUTOMATED VALIDATION                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │  │
│  │  │ SAST     │  │ DAST     │  │ Dependency Scanning  │  │  │
│  │  │ (Bandit) │  │ (Tests)  │  │ (Safety + npm audit) │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────────┘  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │  │
│  │  │ Secret   │  │ License  │  │ Architecture Drift   │  │  │
│  │  │ Detection│  │ Compliance│  │ Detection            │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                MANUAL VALIDATION                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │  │
│  │  │ Security │  │ Pen Test │  │ Code Audit           │  │  │
│  │  │ Reviews  │  │          │  │                      │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                VALIDATION SCHEDULING                     │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │  │
│  │  │Per-Commit│  │Per-Release│  │ Quarterly / Annual   │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                REPORTING & TRACKING                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │  │
│  │  │Compliance│  │Vuln Mgmt │  │ Security Posture     │  │  │
│  │  │ Reports  │  │ Tracking │  │ Reports              │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 3. Automated Validation

### 3.1 Static Application Security Testing (SAST)

| Tool | Scope | Configuration | Fail Criteria |
|------|-------|---------------|---------------|
| **Bandit** | Python code | Exclude tests/migrations; skip B101 | Any HIGH or CRITICAL finding |
| **ESLint Security** | TypeScript/JavaScript | OWASP security rules | Any HIGH finding |
| **Semgrep** | All code | Custom security rules | Any finding above threshold |

**Bandit Configuration:**

```ini
# .bandit
[bandit]
exclude = tests,migrations,venv,.venv
skips = B101
```

**Bandit CI Integration:**

```yaml
# .github/workflows/security.yml
- name: Run Bandit SAST
  run: |
    bandit -r src/ -f json -o bandit-report.json \
      --severity-level high --confidence-level medium || true
    bandit -r src/ --severity-level high --confidence-level medium
```

### 3.2 Dependency Scanning

| Tool | Scope | Frequency | Fail Criteria |
|------|-------|-----------|---------------|
| **Safety** | Python dependencies | Every commit | Any known vulnerability |
| **npm audit** | Node.js dependencies | Every commit | HIGH or CRITICAL vulnerability |
| **Trivy** | Container images (if applicable) | Every build | Any HIGH or CRITICAL |

**Safety Configuration:**

```yaml
# security-scanning.yml
python_dependencies:
  tool: safety
  command: safety check --full-report --json
  fail_on: any_vulnerability
  ignore: []  # No exceptions without security sign-off
```

**npm Audit Configuration:**

```yaml
node_dependencies:
  tool: npm-audit
  command: npm audit --audit-level=high
  fail_on: high
```

### 3.3 Secret Detection

| Tool | Scope | Configuration | Fail Criteria |
|------|-------|---------------|---------------|
| **TruffleHog** | Git history | Full scan | Any detected secret |
| **git-secrets** | Pre-commit hook | AWS patterns + custom | Any match |
| **detect-secrets** | Pre-commit hook | All plugins | Any baseline change |

**TruffleHog Configuration:**

```yaml
# .trufflehog.yml
path: .
branch: main
entropy: true
```

**Pre-commit Hook:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/secretlint/secretlint
    rev: v5.0.0
    hooks:
      - id: secretlint
```

### 3.4 License Compliance

| Tool | Scope | Configuration | Fail Criteria |
|------|-------|---------------|---------------|
| **pip-licenses** | Python dependencies | Approved license list | Non-approved license |
| **license-checker** | Node.js dependencies | Approved license list | Non-approved license |

**Approved Licenses:**

```
MIT
Apache-2.0
BSD-2-Clause
BSD-3-Clause
ISC
Python-2.0
LGPL-2.1+
MPL-2.0
```

### 3.5 Architecture Drift Detection

Custom rules verify that the codebase maintains its intended architecture.

#### Dependency Rules

| Rule | Description | Implementation |
|------|-------------|----------------|
| **Layer Separation** | Domain layer must not import infrastructure | Import linting rules |
| **Plugin Isolation** | Plugin code must not import core modules | Import linting rules |
| **No Circular Dependencies** | No circular module dependencies | Dependency graph analysis |
| **Interface Contracts** | Infrastructure must implement domain interfaces | Type checking |

**Layer Dependency Matrix:**

| Layer | Can Import | Cannot Import |
|-------|-----------|---------------|
| Presentation | Application | Domain, Infrastructure, Persistence |
| Application | Domain | Infrastructure, Persistence |
| Domain | Nothing (leaf layer) | Presentation, Application, Infrastructure, Persistence |
| Infrastructure | Domain (interfaces) | Presentation, Application |
| Persistence | Domain (interfaces), Infrastructure | Presentation, Application |

**Architecture Test Implementation:**

```python
# tests/security/test_architecture.py
class TestArchitectureConstraints:
    """Verify architectural constraints are maintained."""
    
    def test_domain_layer_has_no_infrastructure_imports(self):
        """Domain layer must not import infrastructure."""
        domain_files = glob("src/domain/**/*.py")
        forbidden_imports = [
            "src.infrastructure",
            "src.persistence",
            "src.plugins",
        ]
        
        for file in domain_files:
            imports = extract_imports(file)
            for imp in imports:
                for forbidden in forbidden_imports:
                    assert not imp.startswith(forbidden), \
                        f"Domain layer imports infrastructure: {file} -> {imp}"
    
    def test_plugin_modules_cannot_import_core(self):
        """Plugin modules must not import core application modules."""
        plugin_files = glob("plugins/**/*.py")
        forbidden_imports = [
            "src.core",
            "src.auth",
            "src.models",
        ]
        
        for file in plugin_files:
            imports = extract_imports(file)
            for imp in imports:
                for forbidden in forbidden_imports:
                    assert not imp.startswith(forbidden), \
                        f"Plugin imports core: {file} -> {imp}"
```

#### Naming Convention Violations

| Rule | Description | Implementation |
|------|-------------|----------------|
| **Module Naming** | Snake_case for Python modules | Linter rule |
| **Test Naming** | test_ prefix for test files | Linter rule |
| **Security Test Naming** | test_security_ prefix for security tests | Custom lint |
| **Config Naming** | Specific naming for security configs | Custom lint |

### 3.6 Configuration Validation

| Check | Description | Implementation |
|-------|-------------|----------------|
| **Schema Compliance** | All config files match schema | JSON Schema validation |
| **Secure Defaults** | Verify default values are secure | Automated comparison |
| **HMAC Verification** | All config signatures valid | HMAC verification |
| **No Hardcoded Secrets** | No secrets in configuration files | Pattern scanning |

### 3.7 Policy Validation

| Check | Description | Implementation |
|-------|-------------|----------------|
| **RBAC Policy** | Role definitions are consistent | Policy parser validation |
| **Permission Policy** | All permissions are defined | Policy completeness check |
| **Retention Policy** | All retention periods are valid | Policy validator |
| **Plugin Policy** | Permission catalog is complete | Policy completeness check |

## 4. Manual Validation

### 4.1 Security Reviews

| Review Type | Scope | Frequency | Reviewer |
|-------------|-------|-----------|----------|
| **Architecture Review** | Architectural changes | Per change | Security Review Board |
| **Code Review** | All code changes | Per PR | Security Champion + 1 reviewer |
| **Design Review** | New features | Per feature | Security Review Board |
| **Configuration Review** | Configuration changes | Per change | Security Champion |
| **Plugin Review** | Plugin submissions | Per submission | Plugin Security Team |

### 4.2 Penetration Testing

| Scope | Methodology | Frequency | Tester |
|-------|-------------|-----------|--------|
| Authentication | OWASP Testing Guide | Per release | Security Team |
| Authorization | Privilege escalation testing | Per release | Security Team |
| Input Validation | Fuzzing + manual testing | Per release | Security Team |
| Plugin System | Sandbox escape testing | Per release | Security Team |
| Session Management | Session manipulation testing | Per release | Security Team |
| Data Storage | File access testing | Per release | Security Team |
| Configuration | Tampering resistance testing | Per release | Security Team |

**Penetration Testing Checklist:**

| # | Test Area | Test Description | Expected Result |
|---|-----------|-----------------|-----------------|
| 1 | Authentication | Brute force login attempts | Account lockout after threshold |
| 2 | Authentication | Session fixation | New session on login |
| 3 | Authentication | Credential stuffing | Uniform error messages |
| 4 | Authorization | Horizontal privilege escalation | Access denied |
| 5 | Authorization | Vertical privilege escalation | Access denied |
| 6 | Input Validation | SQL injection via input | Input rejected |
| 7 | Input Validation | XSS via input | Output encoded |
| 8 | Input Validation | Path traversal | Access denied |
| 9 | Session | Session hijacking | Session invalidated |
| 10 | Session | Token prediction | Cryptographically random tokens |
| 11 | Plugin | Sandbox escape | Escape prevented |
| 12 | Plugin | Unauthorized API access | Permission denied |
| 13 | Config | Configuration tampering | Integrity check failure |
| 14 | Storage | Database file access | Encryption prevents reading |
| 15 | Backup | Backup data exposure | Encryption prevents reading |

### 4.3 Code Audits

| Audit Type | Scope | Frequency | Auditor |
|------------|-------|-----------|---------|
| **Security Code Audit** | Security-critical code | Quarterly | Security Team |
| **Dependency Audit** | All dependencies | Monthly | Automated + Manual |
| **Cryptographic Audit** | Crypto implementations | Semi-annually | Security Team |
| **Access Control Audit** | Authorization logic | Quarterly | Security Team |

## 5. Security Testing

### 5.1 Unit Tests for Security Controls

| Control Area | Test Count (Target) | Coverage Target |
|--------------|-------------------|-----------------|
| Input Validation | 50+ tests | 100% of validators |
| Authentication | 30+ tests | 100% of auth flows |
| Authorization | 40+ tests | 100% of RBAC rules |
| Session Management | 20+ tests | 100% of session operations |
| Encryption | 15+ tests | 100% of crypto operations |
| Path Validation | 20+ tests | 100% of file access paths |
| Plugin Permissions | 25+ tests | 100% of permission checks |
| Configuration Integrity | 15+ tests | 100% of config operations |

**Security Unit Test Categories:**

```python
# Example security test categories
class TestInputValidation:
    """Test input validation at all boundaries."""
    
    def test_rejects_xss_in_text_fields(self):
        """Verify XSS payloads are rejected or encoded."""
        ...
    
    def test_rejects_sql_injection(self):
        """Verify SQL injection payloads are rejected."""
        ...
    
    def test_enforces_string_length_limits(self):
        """Verify strings are truncated or rejected at limits."""
        ...
    
    def test_validates_json_schema(self):
        """Verify inputs match expected JSON schema."""
        ...
    
    def test_rejects_path_traversal(self):
        """Verify path traversal payloads are rejected."""
        ...

class TestAuthentication:
    """Test authentication controls."""
    
    def test_password_hashing_uses_argon2id(self):
        """Verify Argon2id is used for password hashing."""
        ...
    
    def test_session_tokens_are_random(self):
        """Verify session tokens have sufficient entropy."""
        ...
    
    def test_lockout_after_failed_attempts(self):
        """Verify account lockout threshold."""
        ...

class TestAuthorization:
    """Test authorization controls."""
    
    def test_default_deny_all(self):
        """Verify unauthenticated access is denied."""
        ...
    
    def test_role_hierarchy_enforced(self):
        """Verify lower roles cannot access higher privileges."""
        ...
    
    def test_admin_requires_reauth(self):
        """Verify admin actions require re-authentication."""
        ...
```

### 5.2 Integration Tests for Security

| Test Area | Description | Frequency |
|-----------|-------------|-----------|
| **Authentication Flow** | Complete login/logout with MFA | Every commit |
| **Authorization Flow** | Complete RBAC enforcement across endpoints | Every commit |
| **Session Lifecycle** | Complete session creation/validation/invalidation | Every commit |
| **Plugin Loading** | Complete plugin verification/sandboxing/execution | Every commit |
| **Configuration Integrity** | Complete config load/validate/sign/verify flow | Every commit |
| **Backup Security** | Complete backup create/encrypt/restore/verify flow | Per release |

### 5.3 Fuzz Testing

| Target | Fuzz Strategy | Duration | Timeout |
|--------|--------------|----------|---------|
| API endpoints | Schema-aware fuzzing | 1 hour per endpoint | 30s per request |
| Input handlers | Boundary value + mutation | 2 hours per handler | 10s per input |
| File upload | Malicious file generation | 1 hour | 60s per file |
| Configuration parsers | Malformed config generation | 30 minutes per parser | 10s per config |
| Import handlers | Corrupted import generation | 1 hour per handler | 60s per import |
| JSON deserialization | Malformed JSON generation | 30 minutes | 5s per payload |

**Fuzz Testing Configuration:**

```yaml
fuzzing:
  targets:
    - name: api_endpoints
      strategy: schema_aware
      duration: 1h
      timeout: 30s
      
    - name: input_handlers
      strategy: mutation
      duration: 2h
      timeout: 10s
      
    - name: file_upload
      strategy: generation
      duration: 1h
      timeout: 60s
  
  coverage:
    min_line_coverage: 80%
    min_branch_coverage: 75%
  
  output:
    format: json
    directory: fuzz-results/
    retention: 30d
```

### 5.4 Regression Tests

Every found vulnerability generates a regression test:

```python
class TestVulnerabilityRegression:
    """Regression tests for found vulnerabilities."""
    
    def test_vuln_001_sql_injection_in_search(self):
        """Regression: SQL injection in module search endpoint."""
        # Previously found: SQL injection via search parameter
        # Fix: Parameterized queries
        payload = "'; DROP TABLE users; --"
        response = client.get(f"/api/modules/search?q={payload}")
        assert response.status_code == 400  # Input rejected
        assert "DROP" not in response.text
    
    def test_vuln_002_xss_in_plugin_name(self):
        """Regression: XSS in plugin name display."""
        # Previously found: Script tag in plugin name rendered
        # Fix: Output encoding
        payload = "<script>alert('xss')</script>"
        response = client.post("/api/plugins/install", 
                             json={"name": payload})
        assert response.status_code == 400  # Input rejected
```

## 6. CI/CD Integration

### 6.1 Pipeline Security Gates

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Code Push   │───►│  Lint & Test │───►│  Security    │
│              │    │              │    │  Tests       │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                    ┌──────────────┐    ┌──────▼───────┐
                    │  Build       │◄───│  SAST + Dep  │
                    │              │    │  Scanning    │
                    └──────┬───────┘    └──────────────┘
                           │
                    ┌──────▼───────┐    ┌──────────────┐
                    │  Fuzz Test   │───►│  Sign        │
                    │              │    │              │
                    └──────────────┘    └──────┬───────┘
                                               │
                    ┌──────────────┐    ┌──────▼───────┐
                    │  Archive     │◄───│  Verify      │
                    │              │    │              │
                    └──────────────┘    └──────────────┘
```

### 6.2 Pipeline Security Gates Detail

| Stage | Tool | Pass Criteria | Fail Action |
|-------|------|---------------|-------------|
| Lint | ESLint, Ruff | No errors | Block merge |
| Unit Tests | pytest, Jest | All pass | Block merge |
| Security Tests | pytest (security) | All pass | Block merge |
| SAST | Bandit, ESLint Security | No HIGH/CRITICAL | Block merge |
| Dependency Scan | Safety, npm audit | No known vulnerabilities | Block merge |
| Secret Detection | TruffleHog | No secrets found | Block merge |
| License Compliance | pip-licenses, license-checker | All approved | Block merge |
| Fuzz Testing | Custom fuzzers | No crashes in 10min | Block merge |
| Architecture Tests | Custom tests | All pass | Block merge |
| Build | npm/Python build | Successful | Block merge |
| Sign | Ed25519 signing | Successful | Block merge |
| Verify | Ed25519 verification | Successful | Block deploy |

### 6.3 CI/CD Configuration

```yaml
# .github/workflows/security-validation.yml
name: Security Validation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      
      - name: Run security unit tests
        run: pytest tests/security/ -v --tb=short
      
      - name: Run SAST (Bandit)
        run: bandit -r src/ -f json -o bandit-report.json
      
      - name: Run dependency scan (Safety)
        run: safety check --full-report
      
      - name: Run secret detection
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          
      - name: Run architecture tests
        run: pytest tests/architecture/ -v
      
      - name: Run license compliance
        run: pip-licenses --order=license --format=json
      
      - name: Upload security reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
```

## 7. Vulnerability Management

### 7.1 Vulnerability Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Detection│───►│ Triage   │───►│ Remediate│───►│ Verify   │
│          │    │          │    │          │    │          │
│• Scan    │    │• Classify│    │• Fix     │    │• Re-scan │
│• Report  │    │• Prioritize│  │• Patch   │    │• Test    │
│• Confirm │    │• Assign  │    │• Update  │    │• Close   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### 7.2 Vulnerability Classification

| Severity | CVSS Score | SLA (Detection to Fix) | Example |
|----------|-----------|----------------------|---------|
| Critical | 9.0-10.0 | 24 hours | Remote code execution, SQL injection |
| High | 7.0-8.9 | 7 days | Privilege escalation, XSS |
| Medium | 4.0-6.9 | 30 days | Information disclosure, CSRF |
| Low | 0.1-3.9 | 90 days | Minor information leakage |
| Informational | 0.0 | Next release | Code quality issues |

### 7.3 Vulnerability Tracking

| Field | Description |
|-------|-------------|
| ID | Unique identifier |
| Title | Brief description |
| Severity | Critical/High/Medium/Low/Informational |
| Source | SAST/DAST/Manual/Dependency Scan/External |
| Component | Affected module or dependency |
| Status | Open/Triaged/In Progress/Fixed/Verified/Closed |
| Assigned To | Responsible team member |
| Detection Date | When the vulnerability was found |
| Due Date | SLA-based remediation deadline |
| Fix Date | When the fix was implemented |
| Verification Date | When the fix was verified |
| CVSS Score | CVSS v3.1 score if applicable |
| References | CVE, CWE, or other references |

### 7.4 Vulnerability Metrics

| Metric | Target |
|--------|--------|
| Mean time to detect (MTTD) | < 24 hours for automated findings |
| Mean time to triage (MTTT) | < 4 hours for critical, < 24 hours for others |
| Mean time to remediate (MTTR) | Within SLA for each severity |
| Vulnerability recurrence rate | < 5% (same vulnerability type reappears) |
| False positive rate | < 10% |
| Security test coverage | > 90% |

## 8. Compliance Reporting

### 8.1 Automated Security Posture Reports

Reports generated automatically:

| Report | Frequency | Audience | Contents |
|--------|-----------|----------|----------|
| **Security Posture Dashboard** | Real-time | Security Team | Current posture score, active issues |
| **Vulnerability Status Report** | Weekly | Security Team | Open vulnerabilities, remediation progress |
| **Dependency Health Report** | Weekly | Development Team | Outdated dependencies, known CVEs |
| **Architecture Compliance Report** | Per commit | Development Team | Layer violations, naming issues |
| **Security Test Coverage Report** | Per commit | Development Team | Security test coverage metrics |
| **Release Security Report** | Per release | Security Steering Committee | All security checks, findings, sign-off |

### 8.2 Compliance Report Structure

```json
{
  "report_type": "security_posture",
  "generated_at": "ISO-8601",
  "period": "2024-01-01 to 2024-01-31",
  "summary": {
    "overall_score": 95,
    "grade": "A",
    "critical_findings": 0,
    "high_findings": 2,
    "medium_findings": 5,
    "low_findings": 12
  },
  "sections": {
    "sast": {
      "tool": "Bandit",
      "findings": 0,
      "suppressed": 2,
      "new_this_period": 0
    },
    "dependencies": {
      "total": 156,
      "outdated": 12,
      "vulnerable": 0,
      "license_issues": 0
    },
    "architecture": {
      "layer_violations": 0,
      "naming_violations": 2,
      "circular_dependencies": 0
    },
    "testing": {
      "security_test_count": 287,
      "coverage_percentage": 92,
      "pass_rate": 100
    },
    "vulnerabilities": {
      "open_critical": 0,
      "open_high": 2,
      "open_medium": 5,
      "open_low": 12,
      "mean_time_to_remediate_days": 4.5
    }
  }
}
```

### 8.3 Compliance Standards Mapping

| Standard | Controls | Status |
|----------|----------|--------|
| OWASP ASVS Level 2 | Authentication, session, access control, crypto, error handling, data protection, communication, code quality | Mapped |
| NIST CSF | Identify, Protect, Detect, Respond, Recover | Mapped |
| CIS Controls | Inventory, data protection, secure configuration, access control, audit, monitoring | Mapped |

## 9. Validation Schedule

| Validation | Frequency | Owner | Artifacts |
|------------|-----------|-------|-----------|
| SAST scan | Every commit | CI/CD | SAST report |
| Dependency scan | Every commit | CI/CD | Dependency report |
| Secret detection | Every commit | CI/CD | Secret scan report |
| License compliance | Every commit | CI/CD | License report |
| Security unit tests | Every commit | CI/CD | Test results |
| Architecture tests | Every commit | CI/CD | Architecture report |
| Fuzz testing | Weekly | Security Team | Fuzz report |
| Penetration testing | Per release | Security Team | Pentest report |
| Security code audit | Quarterly | Security Team | Audit report |
| Architecture review | Per change | Security Review Board | Review report |
| Threat model update | Quarterly | Security Team | Updated threat model |
| Compliance report | Monthly | Security Team | Compliance report |
| Full security assessment | Annually | External Auditor | Assessment report |
| Incident response drill | Semi-annually | Security Team | Drill report |

## 10. Validation Tooling

### 10.1 Tool Inventory

| Tool | Purpose | Configuration Location |
|------|---------|----------------------|
| Bandit | Python SAST | `.bandit` |
| ESLint Security | JavaScript/TypeScript SAST | `.eslintrc.js` |
| Safety | Python dependency scanning | `requirements.txt` |
| npm audit | Node.js dependency scanning | `package.json` |
| TruffleHog | Secret detection | `.trufflehog.yml` |
| pip-licenses | Python license compliance | Command-line flags |
| license-checker | Node.js license compliance | `package.json` |
| pytest | Security unit testing | `pytest.ini` |
| Custom fuzzers | Fuzz testing | `fuzz-config.yml` |
| Architecture tests | Architecture compliance | `tests/architecture/` |

### 10.2 Tool Maintenance

| Activity | Frequency |
|----------|-----------|
| Update tool versions | Monthly |
| Review tool configurations | Quarterly |
| Evaluate new tools | Semi-annually |
| Calibrate false positive rates | Monthly |
| Review suppressed findings | Monthly |

## 11. Findings Management

### 11.1 Finding Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Found   │───►│ Triaged  │───►│ Assigned │───►│ Fixing   │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                      │
                    ┌──────────┐    ┌──────────┐      │
                    │  Closed  │◄───│ Verified │◄─────┘
                    │          │    │          │
                    └──────────┘    └──────────┘
```

### 11.2 Finding Fields

| Field | Description |
|-------|-------------|
| ID | Unique identifier |
| Title | Brief description |
| Severity | Critical/High/Medium/Low/Informational |
| Category | SAST/DAST/Dependency/Architecture/Manual |
| Location | File and line number |
| Description | Detailed description |
| Recommendation | How to fix |
| Status | Open/Triaged/Assigned/Fixing/Verified/Closed |
| Assigned To | Team member responsible |
| Created Date | When finding was created |
| Updated Date | Last update |
| Resolution | How it was fixed |
| Regression Test | Test added to prevent recurrence |

### 11.3 Finding Suppression

Findings may be suppressed only with justification:

| Suppression Type | Approval Required | Duration |
|------------------|-------------------|----------|
| False positive | Security Champion | Until re-validated |
| Accepted risk | Security Review Board | 90 days (re-review) |
| Compensating control | Security Lead | 90 days (re-review) |
| Out of scope | Security Champion | Until scope changes |

All suppressions are logged and reviewed during quarterly security reviews.
