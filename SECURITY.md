# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x-alpha | Yes |
| < 1.0.0 | No |

## Reporting Vulnerabilities

If you discover a security vulnerability within AuthShield Lab, please report it responsibly.

**Do not** open a public GitHub issue for security vulnerabilities.

Instead, please email security@authshieldlab.dev with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if applicable)

You should receive an acknowledgment within 48 hours and a detailed response within 7 business days.

## Security Design Principles

AuthShield Lab is built on the following security principles:

### 1. Localhost-Only Restriction

All network communication is restricted to `127.0.0.1` / `localhost`. The application:

- Binds exclusively to loopback interfaces
- Rejects any configuration attempting external binding
- Monitors and logs all connection attempts
- Validates host headers on every request

This ensures no training data or simulated attack traffic ever leaves the local machine.

### 2. No External Connections

AuthShield Lab makes **zero** outbound network requests by design:

- No telemetry or analytics collection
- No external API calls
- No phone-home mechanisms
- No CDN dependencies at runtime
- All assets are bundled locally

The application functions entirely offline after installation.

### 3. Data Handling

All data generated within AuthShield Lab remains on the local filesystem:

- SQLite databases stored in the application data directory
- Logs written to local log files
- User uploads processed locally
- Configuration stored in local files
- No cloud synchronization
- No remote backups

### 4. Password Security

- Passwords are hashed using bcrypt with a minimum work factor of 12
- Salt is generated per-password using cryptographically secure random values
- Password complexity requirements enforced at account creation
- Password history prevents reuse of the last 12 passwords
- Account lockout after 5 consecutive failed attempts

### 5. Session Management

- JWT tokens expire after 15 minutes
- Refresh tokens expire after 7 days
- Tokens are bound to the device fingerprint
- Session invalidation on password change
- Single-session enforcement (optional)

### 6. Input Validation

- All inputs validated using Pydantic models on the backend
- SQL injection prevented through parameterized queries
- XSS prevention through React's automatic escaping and Content Security Policy
- CSRF protection via SameSite cookies and token validation
- File upload scanning and type restrictions

### 7. Data Encryption

- Sensitive configuration encrypted with AES-256 at rest
- Database encryption for credential storage
- Environment variables loaded from encrypted vaults in production
- Key rotation schedule for encryption keys

## Response Timeline

| Stage | Timeline |
|-------|----------|
| Acknowledgment | 48 hours |
| Initial assessment | 5 business days |
| Fix development | 14 business days |
| Disclosure coordination | 30 days |

## Security Updates

Security patches are released as soon as possible after a fix is ready. Updates will be published to the GitHub repository and documented in the CHANGELOG.

## Scope

This security policy applies to:

- The AuthShield Lab desktop application
- The backend API server
- The Electron renderer process
- Database storage
- Configuration files

This policy does not cover:

- Third-party dependencies (report upstream)
- The training content itself (simulated vulnerabilities)
- Social engineering attacks against maintainers

## Authentication & Authorization

- Role-based access control (RBAC) with four roles: Student, Instructor, Admin, Developer
- Principle of least privilege applied throughout
- API endpoints protected by JWT middleware
- Administrative functions require elevated permissions
- Audit logging for all privileged operations

## Network Security

- CORS configured to allow only localhost origins
- Rate limiting on authentication endpoints (5 requests/minute)
- Request size limits enforced (10MB default)
- Timeout on all HTTP connections (30 seconds)
- TLS not required for localhost communication but supported for testing
