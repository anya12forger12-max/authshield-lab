# Changelog

All notable changes to AuthShield Lab will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- SAML 2.0 authentication testing framework
- WebAuthn / FIDO2 passkey testing support
- Plugin architecture for custom attack modules
- Internationalization (i18n) framework with RTL language support
- Python SDK for programmatic access
- VS Code extension for in-editor lab execution
- Custom certificate authority for testing certificate-based authentication
- Compliance reporting for SOC 2, HIPAA, and PCI-DSS
- Real-time multi-user classroom mode
- Leaderboard system for training gamification
- Offline content package download support
- Webhook integration for event-driven notifications
- GraphQL API as alternative to REST
- Load testing framework for performance validation
- High availability clustering support

### Changed

- Migrated from Express 4 to Express 5
- Upgraded React from 18 to 19
- Replaced Jest with Vitest as the test runner
- Updated ESLint from v8 to v9 with flat config
- Upgraded TypeScript from v5.3 to v5.6
- Improved database query performance by 40%
- Refactored authentication engine for extensibility
- Enhanced error messages with actionable guidance

### Deprecated

- `@authshield/legacy-api` REST endpoints (scheduled for removal in v6.0.0)
- `--verbose` CLI flag in favor of `--log-level debug`
- Cookie-based session storage in favor of encrypted token storage

### Removed

- jQuery dependency (fully replaced with native browser APIs)
- Support for Node.js 18 (minimum is now v20)
- Legacy authentication protocol support (pre-OAuth 2.0)
- Flash-based lab components (replaced with HTML5 Canvas)

### Fixed

- JWT expiration validation edge case for tokens expiring at exact current time
- Session fixation vulnerability in multi-tab scenarios
- Race condition in concurrent lab execution
- Memory leak in long-running lab sessions
- Accessibility: focus trap not releasing in modal dialogs on Safari
- Accessibility: screen reader not announcing lab completion status
- Color contrast ratio below 4.5:1 on secondary button hover state
- Clipboard API not working in insecure contexts
- CSV export not handling Unicode characters correctly
- Database connection pool exhaustion under high concurrent load
- Token refresh not properly invalidating old tokens
- Lab progress not persisting after browser refresh in offline mode

### Security

- Upgraded all cryptographic operations to use AES-256-GCM
- Implemented Content Security Policy headers
- Added Subresource Integrity (SRI) for all external resources
- Strengthened session token entropy to 256 bits
- Added rate limiting to authentication endpoints
- Implemented CSRF protection with double-submit cookie pattern
- Updated dependency `jsonwebtoken` to patch CVE-2024-XXXXX
- Added automated dependency vulnerability scanning via Dependabot

---

## [5.0.0] — 2026-07-19

### Added

- **Core Authentication Testing Engine** — Full authentication protocol simulation and analysis
- **Attack Simulation Library** — Pre-built attack scenarios:
  - Brute force attacks with configurable wordlists
  - Credential stuffing with breach database simulation
  - Session hijacking and fixation
  - MFA bypass techniques
  - Token manipulation and replay attacks
- **JWT Security Testing** — Token signing, verification, algorithm confusion, expiration testing, key rotation
- **OAuth 2.0 Testing** — Authorization code flow, client credentials, PKCE, token introspection
- **Learning Management System** — Structured courses, progress tracking, grading
- **Interactive Lab Runner** — Sandboxed lab execution with real-time feedback
- **REST API** — Complete CRUD operations for all entities with OpenAPI documentation
- **CLI Toolkit** — Command-line interface for automation and CI/CD integration
- **React Web Interface** — Responsive UI with Tailwind CSS
- **SQLite Database** — Lightweight, embedded database with migration support
- **Docker Deployment** — Containerized deployment with Docker Compose
- **CI/CD Pipeline** — GitHub Actions with lint, typecheck, test, and accessibility gates
- **WCAG 2.2 AA Accessibility** — Full keyboard navigation, screen reader support, high contrast mode
- **Audit Logging** — Immutable audit trail for all security-relevant events
- **Role-Based Access Control** — Admin, instructor, learner, and viewer roles
- **Token Security Engine** — JWT, OAuth, and SAML token validation and attack simulation
- **Credential Analyzer** — Password strength analysis and breach database checking
- **Threat Modeling Dashboard** — Visual attack surface mapping
- **Incident Response Playbooks** — Step-by-step security incident response training
- **Capture-the-Flag Challenges** — Time-limited security exercises with scoring
- **Custom Scenario Builder** — Design and share custom attack/defense scenarios
- **Plugin Framework** (Beta) — Extensible module system for custom functionality
- **Analytics Dashboard** (Beta) — Learning and security metrics visualization
- **Comprehensive Test Suite** — >90% code coverage with unit, integration, and accessibility tests
- **Developer Onboarding Guide** — Complete setup and getting started documentation
- **Governance Documentation** — Contributing guide, code of conduct, security policy, roadmap
- **Branch Strategy** — Documented Git workflow with branch protection rules
- **Conventional Commits** — Enforced commit message format with commitlint

### Changed

- Initial stable release — no prior changes

### Deprecated

- None (initial release)

### Removed

- None (initial release)

### Fixed

- None (initial release)

### Security

- All authentication data encrypted at rest using AES-256-GCM
- Session tokens use secure, HttpOnly, SameSite cookies
- Input validation on all API endpoints
- Parameterized database queries prevent SQL injection
- Content Security Policy headers configured
- Rate limiting on authentication endpoints
- Dependency audit integrated into CI/CD pipeline
