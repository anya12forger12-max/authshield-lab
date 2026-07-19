# Governance — AuthShield Lab

This document describes the governance model for AuthShield Lab, including decision-making processes, code ownership, and community guidelines.

---

## Vision Statement

AuthShield Lab exists to make authentication security education accessible, practical, and thorough. We believe that understanding security threats is the first step toward building resilient systems. Our platform is designed to be:

- **Offline-first** — fully functional without internet access
- **Defensive** — teaching secure practices through hands-on experience
- **Educational** — serving learners from beginners to seasoned professionals
- **Accessible** — meeting WCAG 2.2 AA standards for all users
- **Secure** — following best practices in our own codebase
- **Maintainable** — built for long-term sustainability

---

## Core Principles

### 1. Offline-First

All core functionality must work without an internet connection. No external API calls, CDNs, or cloud services are required for the platform to operate. This is a non-negotiable architectural constraint.

### 2. Defensive Security

The platform teaches defensive security. All attack simulations are conducted in controlled, sandboxed environments. We do not provide tools or instructions that could be used for unauthorized access. The goal is education and defense.

### 3. Educational

Every feature should serve a learning objective. If a feature does not clearly contribute to education, security awareness, or skill development, it should not be included.

### 4. Accessible

Accessibility is not an afterthought. All user-facing features must meet WCAG 2.2 AA standards. We actively seek feedback from users of assistive technologies and prioritize accessibility fixes.

### 5. Secure

We practice what we preach. The codebase follows security best practices including input validation, output encoding, parameterized queries, and principle of least privilege. All code changes undergo security review.

### 6. Maintainable

Code should be readable, well-tested, and documented. We prioritize clarity over cleverness. Dependencies are audited regularly. Technical debt is tracked and addressed systematically.

---

## Decision-Making Process

### Day-to-Day Decisions

Day-to-day development decisions (implementation details, code style, minor feature choices) are made by individual contributors and the author of a pull request. These decisions are reviewed as part of the standard code review process.

### Significant Decisions

Significant decisions that affect the project's architecture, scope, or direction require discussion and consensus among maintainers. Significant decisions include:

- Adding or removing major features
- Changing the tech stack
- Modifying the API contract
- Introducing new dependencies
- Changing the governance model
- Modifying the release process

### Decision Process

1. **Proposal** — Open a GitHub Issue or Discussion with a clear description and rationale
2. **Discussion** — Community and maintainers discuss for a minimum of 7 days
3. **Consensus** — Maintainers reach consensus (see Conflict Resolution below)
4. **Documentation** — Decision is recorded in the relevant governance or documentation file
5. **Implementation** — Changes are implemented through the standard PR process

### Voting

When consensus cannot be reached, maintainers vote. Each maintainer gets one vote. A simple majority is required. The project owner holds the tie-breaking vote.

---

## Code Ownership

### CODEOWNERS

The `CODEOWNERS` file defines ownership for different areas of the codebase:

| Area | Owner | Reviewers |
|------|-------|-----------|
| `/` (root) | Project Owner | All maintainers |
| `packages/core/` | Core Team | @authshield/core-team |
| `packages/attacks/` | Core Team | @authshield/core-team |
| `packages/tokens/` | Core Team | @authshield/core-team |
| `packages/lms/` | LMS Team | @authshield/lms-team |
| `packages/ui/` | Frontend Team | @authshield/frontend-team |
| `packages/api/` | Backend Team | @authshield/backend-team |
| `packages/cli/` | CLI Team | @authshield/cli-team |
| `packages/sdk/` | SDK Team | @authshield/sdk-team |
| `docs/` | Documentation Team | @authshield/docs-team |
| `.github/` | DevOps | @authshield/devops |
| `governance/` | Project Owner | All maintainers |
| `SECURITY.md` | Security Team | @authshield/security-team |

### Ownership Responsibilities

- **Review** all changes to owned areas
- **Maintain** quality and consistency within their domain
- **Respond** to issues and questions in their area within 5 business days
- **Ensure** changes meet accessibility and security requirements

---

## Review Requirements

### Minimum Review Threshold

| Change Type | Minimum Approvals | Additional Requirements |
|-------------|-------------------|------------------------|
| Bug fix | 1 | CI must pass |
| New feature | 1 | Tests + docs required |
| Security change | 2 | Security team review required |
| Governance change | 2 | 7-day discussion period |
| Dependency change | 1 | Security audit required |
| Accessibility fix | 1 | Manual a11y testing required |
| Documentation | 1 | Technical review |

### Reviewer Qualifications

- Must be a maintainer or designated reviewer for the affected area
- Must have reviewed the full diff, not just a portion
- Must check for tests, documentation, and accessibility compliance
- Should understand the security implications of the change

---

## Branch Protection Rules

### `main` Branch

- Pull requests required (no direct pushes)
- At least 1 approving review required
- All CI checks must pass (lint, typecheck, test, a11y)
- Branch must be up to date with `main`
- Signed commits required
- No force pushes
- No deletion

### `release/*` Branches

- Pull requests required
- At least 1 approving review required
- All CI checks must pass
- Only bug fixes allowed after feature freeze
- Maintainers only for final merge to `main`

### `develop` Branch

- Pull requests required
- At least 1 approving review required
- CI checks must pass
- Feature branches merge here first

### `hotfix/*` Branches

- Pull requests required
- At least 1 approving review required
- Expedited review process (24-hour turnaround)
- Merge to both `main` and `develop`

---

## Release Process

See [governance/processes/RELEASE_PROCESS.md](governance/processes/RELEASE_PROCESS.md) for the complete release process.

### Summary

1. **Release Planning** — Features are planned for each release cycle
2. **Feature Freeze** — `release/*` branch is created from `develop`
3. **Testing Phase** — Full test suite, security audit, accessibility audit
4. **Release Candidate** — RC is published for testing
5. **Final Release** — Stable version is released after validation
6. **Post-Release** — Monitoring, hotfix readiness

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** — Breaking changes
- **MINOR** — New features (backward-compatible)
- **PATCH** — Bug fixes (backward-compatible)

### LTS Policy

Major versions receive long-term support (LTS) for 24 months. During LTS:
- Critical security patches are applied
- High-severity bugs are fixed
- No new features are added

---

## Conflict Resolution

### Informal Resolution

Most disagreements are resolved through discussion in pull requests or issues. Contributors are encouraged to seek compromise and focus on the best outcome for the project.

### Mediation

If informal resolution fails, any maintainer may request mediation. The project owner or a designated mediator will facilitate a resolution.

### Escalation

If mediation fails, the issue is escalated to a maintainer vote:
1. The issue is documented with all perspectives
2. Each maintainer votes (approve/reject/abstain)
3. Simple majority decides
4. The project owner holds the tie-breaking vote
5. The decision is final and binding

### Revisiting Decisions

Decisions can be revisited if:
- New information becomes available
- The decision was made with incomplete context
- A significant amount of time has passed (minimum 6 months)

---

## Technical Steering

### Technical Steering Committee

The Technical Steering Committee (TSC) consists of all maintainers and is responsible for:

- Setting the technical direction of the project
- Approving architectural changes
- Managing the release schedule
- Resolving technical disputes
- Ensuring code quality and security standards

### Meeting Schedule

- The TSC meets monthly via video call or asynchronous discussion
- Meeting notes are published in the `governance/meetings/` directory
- All project members may attend meetings as observers
- Decisions are recorded and linked from the relevant issues

### Standing Agenda

1. Review open issues and PRs needing attention
2. Discuss architectural proposals and significant changes
3. Review security reports and status
4. Discuss roadmap progress and adjustments
5. Review any governance changes

---

## Roadmap Management

### Roadmap Principles

- The roadmap is public and maintained in [ROADMAP.md](ROADMAP.md)
- Roadmap items are tracked as GitHub Issues with the `roadmap` label
- Priorities are reviewed quarterly
- Community input is actively sought through Discussions
- The roadmap is a living document, updated as priorities shift

### Proposing Roadmap Items

1. Open a GitHub Discussion with the `roadmap` tag
2. Describe the feature, its use case, and its alignment with core principles
3. Gather community feedback
4. The TSC reviews and decides on inclusion during the next quarterly review

### Quarterly Review

Every quarter, the TSC:
1. Reviews all open roadmap proposals
2. Assesses progress on current roadmap items
3. Re-prioritizes based on community feedback and project needs
4. Updates the public roadmap

---

## Amendments

This governance document may be amended through the following process:

1. A pull request is opened with proposed changes
2. The PR is discussed for a minimum of 14 days
3. All maintainers must approve the change
4. The change takes effect immediately upon merge

---

## Contact

For governance-related questions or concerns:

- **GitHub Discussions** — [github.com/anya12forger12-max/authshield-lab/discussions](https://github.com/anya12forger12-max/authshield-lab/discussions)
- **Security concerns** — See [SECURITY.md](SECURITY.md)
- **Code of Conduct issues** — See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
