# Roadmap — AuthShield Lab

This document outlines the current and planned development roadmap for AuthShield Lab. It is a living document, updated quarterly based on community feedback and project priorities.

---

## Vision

To become the leading open-source platform for authentication security education, providing comprehensive, accessible, and offline-first tools for learning, testing, and teaching authentication security.

---

## Phase 1: Enterprise Foundation (Current)

**Timeline**: Q3 2026 — Q4 2026
**Status**: In Progress

Phase 1 establishes the core platform, essential modules, and developer experience.

### Completed Milestones

| Milestone | Status | Description |
|-----------|--------|-------------|
| Core Authentication Engine | Complete | Token validation, session management, credential analysis |
| Attack Simulation Library | Complete | Brute force, credential stuffing, session hijacking, MFA bypass |
| JWT Security Testing | Complete | Token signing, verification, algorithm confusion, expiration testing |
| OAuth 2.0 Testing | Complete | Authorization code, client credentials, PKCE flows |
| LMS Framework | Complete | Course structure, progress tracking, grading |
| Lab Runner | Complete | Sandboxed lab execution with real-time feedback |
| REST API | Complete | Full CRUD operations for all entities |
| CLI Toolkit | Complete | Command-line interface for automation |
| React UI | Complete | Responsive web interface with full keyboard support |
| WCAG 2.2 AA | Substantially Complete | Accessibility audit with 2 minor issues remaining |
| Docker Deployment | Complete | Containerized deployment with Docker Compose |
| CI/CD Pipeline | Complete | GitHub Actions with lint, typecheck, test, a11y gates |

### In Progress

| Feature | Target | Description |
|---------|--------|-------------|
| Data Visualization Charts | v5.1.0 | Text alternatives for all charts |
| Scenario Builder Keyboard Support | v5.1.0 | Full keyboard navigation for drag-and-drop |
| Session Management Testing | v5.1.0 | Session fixation, hijacking, and timeout testing |

---

## Phase 2: Advanced Features

**Timeline**: Q1 2027 — Q2 2027
**Status**: Planned

Phase 2 expands the platform with advanced security testing, plugin system, and enhanced LMS features.

### Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| SAML 2.0 Testing | High | SAML assertion validation and attack simulation |
| WebAuthn / FIDO2 | High | Passkey and hardware token testing |
| SAML SP Testing | High | Service provider configuration and attack testing |
| Plugin Architecture | High | Extensible module system for custom attacks |
| Plugin Marketplace | Medium | Community-contributed plugins and scenarios |
| Multi-Language Support (i18n) | High | Framework for localization with RTL support |
| API Rate Limiting | Medium | Configurable rate limiting for API endpoints |
| Advanced Analytics Dashboard | Medium | Detailed learning analytics and reporting |
| LDAP Authentication Testing | Medium | Directory service authentication simulation |
| RBAC for Labs | Medium | Role-based access control for lab environments |
| Lab Sharing | Medium | Export and import lab scenarios |
| Instructor Dashboard v2 | Medium | Enhanced classroom management tools |
| Automated Grading | High | AI-assisted lab evaluation and feedback |

### Technical Improvements

| Improvement | Priority | Description |
|-------------|----------|-------------|
| Performance Optimization | High | Lab execution speed improvements |
| Database Migration System | High | Versioned, reversible migrations |
| End-to-End Test Suite | High | Playwright-based E2E tests |
| Third-Party Accessibility Audit | High | Professional WCAG 2.2 AA audit |
| Bundle Size Reduction | Medium | Tree-shaking and code splitting |
| TypeScript Strict Mode | Medium | Enable strict TypeScript checks |

---

## Phase 3: Ecosystem Expansion

**Timeline**: Q3 2027 — Q4 2027
**Status**: Planned

Phase 3 focuses on community growth, enterprise features, and ecosystem integration.

### Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| Python SDK | High | Native Python client library |
| VS Code Extension | Medium | IDE integration for lab execution |
| Custom Certificate Authority | High | Internal CA for testing certificate-based auth |
| Compliance Reporting | Medium | SOC 2, HIPAA, PCI-DSS compliance checklists |
| Classroom Mode | High | Real-time multi-user lab sessions |
| Leaderboards | Medium | Gamification for training programs |
| Offline Content Packages | Medium | Downloadable course bundles |
| Webhook Integration | Medium | Event-driven notifications |
| Custom Branding | Low | White-label support for enterprises |
| GraphQL API | Low | Alternative API interface |

---

## Phase 4: Production Hardening

**Timeline**: 2028
**Status**: Future

| Feature | Description |
|---------|-------------|
| Enterprise Authentication | SAML SSO, OIDC integration for platform access |
| Audit Compliance | Enhanced audit logging for regulatory requirements |
| High Availability | Clustering and failover support |
| Load Testing Framework | Built-in load generation and performance testing |
| Disaster Recovery | Backup and restore procedures |

---

## How to Contribute to the Roadmap

### Proposing a Feature

1. **Search existing discussions** — Check if your idea has already been proposed
2. **Open a GitHub Discussion** — Use the `Ideas` category with the `roadmap` tag
3. **Describe the use case** — Explain the problem, not just the solution
4. **Gather feedback** — Engage with the community discussion
5. **Wait for review** — The TSC reviews proposals quarterly

### Contributing Implementation

1. Check the roadmap for items marked `help wanted` or `good first issue`
2. Comment on the issue to indicate you are working on it
3. Follow the [Contributing Guide](CONTRIBUTING.md) for implementation details
4. Submit a pull request for review

### Prioritization Criteria

Features are prioritized based on:

1. **Alignment with core principles** — Offline-first, defensive, educational, accessible, secure, maintainable
2. **Community demand** — Number of requests and engagement
3. **Security impact** — Does it improve security testing capabilities?
4. **Accessibility impact** — Does it improve or maintain accessibility?
5. **Implementation complexity** — Effort required vs. benefit
6. **Maintenance burden** — Long-term cost of adding and maintaining the feature

---

## Quarterly Review

The roadmap is reviewed quarterly by the Technical Steering Committee:

| Quarter | Review Date | Notes |
|---------|-------------|-------|
| Q1 2026 | January 2026 | Initial roadmap created |
| Q2 2026 | April 2026 | Phase 1 milestones confirmed |
| Q3 2026 | July 2026 | Phase 1 progress review (current) |
| Q4 2026 | October 2026 | Phase 1 completion, Phase 2 planning |

---

## Milestone Tracking

All roadmap items are tracked as GitHub Issues with the `roadmap` label:
[View roadmap issues](https://github.com/anya12forger12-max/authshield-lab/issues?q=label%3Aroadmap)

---

*This roadmap is a living document. Last updated: July 2026.*
