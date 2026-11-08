# Security Policy — AuthShield Lab

The AuthShield Lab team takes security seriously. This document outlines our security practices, how to report vulnerabilities, and our commitment to maintaining a secure platform.

---

## Supported Versions

| Version | Supported | End of Support |
|---------|-----------|---------------|
| 5.0.x | Yes | TBD (LTS) |
| 4.x | No | 2025-12-31 |
| < 4.0 | No | End of life |

We provide security updates for the current major version and the previous major version. Older versions receive no security patches.

---

## Reporting Vulnerabilities

### How to Report

If you discover a security vulnerability in AuthShield Lab, please report it responsibly through the following process:

1. **Do NOT** create a public GitHub Issue for security vulnerabilities
2. **Do NOT** discuss the vulnerability on public forums, social media, or in pull requests
3. **DO** send an email to **security@authshieldlab.dev**

### What to Include

Your report should include:

- **Description** — Clear description of the vulnerability
- **Impact** — Potential impact if exploited
- **Reproduction Steps** — Step-by-step instructions to reproduce the issue
- **Affected Component** — Which part of the platform is affected
- **Severity Assessment** — Your assessment using CVSS if possible
- **Environment** — OS, browser, Node.js version where you observed the issue
- **Proof of Concept** — Code, screenshots, or logs demonstrating the vulnerability (redact sensitive data)

### PGP Encryption

We strongly recommend encrypting your report. Our PGP public key is available at:

```
Key ID: [TBD]
Fingerprint: [TBD]
```

You can also request our PGP key by emailing security@authshieldlab.dev.

---

## Security Response Timeline

We are committed to the following response timeline:

| Phase | Timeline | Description |
|-------|----------|-------------|
| Acknowledgment | 24 hours | We confirm receipt of your report |
| Triage | 48 hours | We assess severity and validity |
| Initial Assessment | 5 business days | We determine impact and develop fix plan |
| Fix Development | 14 business days | We develop and test a fix |
| Disclosure | After fix release | We publish a security advisory |
| Credit | With disclosure | We credit the reporter (unless anonymity requested) |

### Severity Levels

| Level | Description | Response Time |
|-------|-------------|--------------|
| Critical | Remote code execution, authentication bypass, data exposure | Immediate (24h) |
| High | Privilege escalation, significant data exposure | 48 hours |
| Medium | Limited data exposure, denial of service | 5 business days |
| Low | Minor information disclosure, limited impact | 10 business days |

---

## Security Update Policy

### Patch Releases

- Security fixes are released as patch versions (e.g., 5.0.1 → 5.0.2)
- Security patches are backported to all supported versions
- Users are notified through GitHub Security Advisories
- Automated dependency updates are enabled where possible

### Emergency Patches

- Critical vulnerabilities may trigger an emergency release
- Emergency releases bypass the normal release process
- All emergency releases include a security changelog entry

### Notification Channels

- **GitHub Security Advisories** — Primary notification channel
- **GitHub Releases** — Patch notes for each security update
- **README Badge** — Version status badge is updated

---

## Dependency Security

### Dependency Management

- Dependencies are managed through `npm` with lockfiles committed
- **npm audit** is run as part of CI/CD pipeline
- **Dependabot** is configured to monitor dependencies
- All dependency updates are reviewed before merging

### Dependency Policies

| Policy | Requirement |
|--------|------------|
| New dependencies | Must be approved by a maintainer |
| Major version updates | Require review and testing |
| Security patches | Applied within 48 hours for critical/high |
| License audit | All dependencies must be MIT, Apache 2.0, or equivalent |
| Bundle size | No dependency should add >50KB gzipped without justification |

### Software Bill of Materials

A Software Bill of Materials (SBOM) is generated for each release and includes:
- All direct and transitive dependencies
- Version numbers and license information
- Known vulnerabilities at time of release

---

## Secret Management

### Hardcoded Secrets

Hardcoded secrets are strictly prohibited. The codebase is scanned using:
- **git-secrets** — Prevents committing secrets
- **gitleaks** — Detects secrets in git history
- **ESLint rules** — Custom rules to catch patterns like API keys in code

### Environment Variables

All sensitive configuration is managed through environment variables:

| Variable | Description | Required |
|----------|------------|---------|
| `AUTHSHIELD_SECRET_KEY` | Main application secret | Yes |
| `AUTHSHIELD_DB_ENCRYPTION_KEY` | Database encryption key | Yes |
| `AUTHSHIELD_JWT_SECRET` | JWT signing secret | Yes |
| `AUTHSHIELD_SESSION_SECRET` | Session encryption secret | Yes |

### Default Values

- No secret has a default value in production
- `.env.example` contains placeholder values only
- Development defaults are clearly marked as insecure

---

## Access Control

### Principle of Least Privilege

- All components operate with the minimum permissions required
- Database access uses read-only connections where writes are unnecessary
- File system access is restricted to designated directories
- Network access is restricted to required ports

### Authentication & Authorization

- Session tokens use secure, HttpOnly cookies
- Tokens have configurable expiration (default: 1 hour)
- Refresh tokens are rotated on use
- Failed login attempts are rate-limited
- Account lockout is configurable (default: 5 attempts)

### Role-Based Access Control (RBAC)

| Role | Description |
|------|------------|
| `admin` | Full platform access including configuration |
| `instructor` | Course management and student progress viewing |
| `learner` | Lab execution and progress tracking |
| `viewer` | Read-only access to public content |

---

## Audit Logging

### What Is Logged

| Event | Details |
|-------|---------|
| Authentication events | Login, logout, failed attempts, MFA events |
| Authorization events | Access denials, permission changes |
| Data access | Read/write operations on sensitive data |
| Configuration changes | All changes to system configuration |
| Lab execution | Lab start, completion, scores |
| API access | API calls with timestamps and response codes |

### Log Properties

- Logs are immutable once written
- Logs include timestamp, actor, action, resource, and result
- Sensitive data (passwords, tokens) are never logged
- Logs are stored in a separate, append-only database

### Log Retention

- Audit logs are retained for a minimum of 2 years
- Logs older than 2 years are archived and compressed
- Archived logs are available for compliance review

---

## Incident Response

### Response Process

1. **Detection** — Vulnerability or incident is identified
2. **Triage** — Assess severity and scope
3. **Containment** — Limit the impact of the incident
4. **Eradication** — Remove the vulnerability or threat
5. **Recovery** — Restore normal operations
6. **Post-Mortem** — Document the incident and improve processes

### Communication

- Users are notified of security incidents within 48 hours
- A detailed security advisory is published after the fix
- The incident post-mortem is published within 30 days
- Affected users receive specific guidance on any required actions

### Incident Classification

| Level | Description | Response |
|-------|-------------|---------|
| P1 | Active exploitation, data breach | Immediate, all hands |
| P2 | Critical vulnerability, no exploitation known | 24 hours |
| P3 | High vulnerability, limited impact | 48 hours |
| P4 | Low vulnerability, defense in depth | Standard process |

---

## Security Contacts

| Contact | Channel | Response Time |
|---------|---------|--------------|
| Security Team | security@authshieldlab.dev | 24 hours |
| Project Owner | Via GitHub @anya12forger12-max | 48 hours |
| General Issues | GitHub Issues | Standard timeline |

### Security Advisories

Published at: [https://github.com/anya12forger12-max/authshield-lab/security/advisories](https://github.com/anya12forger12-max/authshield-lab/security/advisories)

### Bug Bounty

We do not currently operate a bug bounty program. However, we deeply appreciate security researchers who report vulnerabilities responsibly and will acknowledge all valid reports in our security advisories.

---

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST SP 800-63B — Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

---

*This security policy is reviewed and updated quarterly. Last review: July 2026.*
