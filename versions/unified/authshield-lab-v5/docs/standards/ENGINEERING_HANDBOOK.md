# AuthShield Lab — Enterprise Engineering Handbook

> Version 1.0 · Last Updated: 2026-07-19 · Owner: Engineering Leadership

---

## Table of Contents

1. [Engineering Principles](#1-engineering-principles)
2. [Code Review Standards](#2-code-review-standards)
3. [Technical Debt Management](#3-technical-debt-management)
4. [Incident Response Procedures](#4-incident-response-procedures)
5. [On-call Rotation Guidelines](#5-on-call-rotation-guidelines)
6. [Post-mortem Process](#6-post-mortem-process)
7. [Engineering Career Ladder](#7-engineering-career-ladder)
8. [Meeting Cadence](#8-meeting-cadence)
9. [Communication Standards](#9-communication-standards)
10. [Knowledge Transfer Protocols](#10-knowledge-transfer-protocols)

---

## 1. Engineering Principles

AuthShield Lab is a cybersecurity education platform running as an offline-only application with a Python 3.12+ FastAPI backend, Electron+React frontend, and SQLite database. Every architectural and coding decision must reflect these core principles.

### 1.1 SOLID Principles

| Principle | Application in AuthShield Lab |
|---|---|
| **Single Responsibility** | Each FastAPI router handles exactly one domain entity. Each React component renders one logical UI element. Each SQLAlchemy model maps to exactly one table. Each use-case class performs exactly one business operation. |
| **Open/Closed** | The plugin system must be extensible without modifying core authentication modules. Use `Protocol` classes for swappable implementations. New credential types (TOTP, HOTP, WebAuthn) are added by implementing the `AuthenticatorProtocol`, never by editing the base authentication flow. |
| **Liskov Substitution** | Any `Authenticator` subclass (TOTP, HOTP, WebAuthn) must be usable wherever `AuthenticatorProtocol` is referenced without behavioral surprises. All repository implementations must honor the same transaction guarantees. |
| **Interface Segregation** | React component props interfaces must be narrow — no god-props objects passed to leaf components. Python `Protocol` classes expose only the methods consumers need. Split large service interfaces into focused, role-specific protocols. |
| **Dependency Inversion** | Business logic depends on `Protocol` abstractions, not concrete SQLite or filesystem implementations. FastAPI dependencies inject abstractions, not concretions. The domain layer has zero imports from infrastructure. |

### 1.2 Domain-Driven Design (DDD)

AuthShield Lab organizes code around four bounded contexts:

- **Identity Context** — User registration, authentication, credential management, session handling, MFA enrollment.
- **Education Context** — Course modules, lesson content, progress tracking, assessment engine, scoring.
- **Security Context** — Threat simulations, vulnerability scanning, compliance checks, audit logging, incident tracking.
- **Platform Context** — Configuration, plugin management, offline synchronization, system health, diagnostics.

Each bounded context owns its own SQLAlchemy models, FastAPI routers, and React slice of the UI. Cross-context communication happens exclusively through domain events or explicit service interfaces — never through direct model imports across context boundaries.

**Aggregates:** Each context has a root aggregate (e.g., `User` aggregate in Identity, `Course` aggregate in Education). Only the aggregate root may be persisted or retrieved as a unit. Child entities are accessed through the root and cannot exist independently.

**Value Objects:** Immutable data structures for concepts like `EmailAddress`, `CredentialHash`, `CourseModuleId`, `RiskScore`. Implemented as frozen dataclasses (`@dataclass(frozen=True)`). Value objects implement `__eq__` and `__hash__` based on their attributes.

**Domain Events:** Published via an in-process event bus when state changes occur (e.g., `UserRegistered`, `LessonCompleted`, `ThreatDetected`). Events are stored in an outbox table for reliability. The outbox table is in the same SQLite transaction as the state change, guaranteeing atomicity.

### 1.3 Clean Architecture

```
+-------------------------------------------+
|           Presentation Layer              |  FastAPI routers, React components
+-------------------------------------------+
|           Application Layer               |  Use cases, orchestration, DTOs
+-------------------------------------------+
|            Domain Layer                   |  Entities, value objects, events, Protocol interfaces
+-------------------------------------------+
|         Infrastructure Layer              |  SQLAlchemy repos, SQLite adapters, filesystem
+-------------------------------------------+
```

**Dependency Rule:** Dependencies point inward. Domain imports nothing from infrastructure. Application imports only domain interfaces. Infrastructure implements domain interfaces. API layer imports application use cases.

**Layer Responsibilities in AuthShield Lab:**

- `domain/` — Pure Python: entities, value objects, repository Protocol classes, domain event definitions, value objects. No framework imports.
- `application/` — Use cases: `register_user.py`, `authenticate_user.py`, `complete_lesson.py`. Each use case is a single class with a `__call__` method and no framework dependencies.
- `infrastructure/` — SQLAlchemy repository implementations, SQLite connection management, file-based configuration, event bus implementation.
- `api/` — FastAPI routers, Pydantic request/response schemas, dependency injection wiring, middleware.
- `frontend/` — Electron+React presentation layer; communicates with backend exclusively via HTTP/REST.

### 1.4 Event-Driven Architecture

Even though AuthShield Lab is offline-only and single-process, we use an event-driven pattern for loose coupling:

- **Event Bus:** In-process `asyncio`-based pub/sub system defined in `domain/events/bus.py`. Supports synchronous and async handlers.
- **Event Store:** SQLite table `domain_events` for persistence and audit trail. Enables event replay and debugging.
- **Outbox Pattern:** Domain state changes write events to an outbox table within the same transaction. A background `asyncio` task polls the outbox and dispatches events to subscribers.

Events are never used for synchronous request-response flows. They serve cross-context notifications, audit logging, analytics, and triggering background work.

---

## 2. Code Review Standards

### 2.1 Purpose

Code reviews serve three goals:
1. **Correctness** — Catch logic errors, edge cases, and violations of invariants before they reach production.
2. **Knowledge Sharing** — Ensure at least two engineers understand every change that ships.
3. **Quality** — Enforce conventions, identify improvement opportunities, and prevent technical debt accumulation.

### 2.2 Reviewer Checklist

#### Correctness & Logic
- Does the code do what the PR description and linked issue claim?
- Are error conditions handled — not just the happy path?
- Are database transactions properly scoped (commit on success, rollback on failure)?
- Are async operations properly awaited — no unintentional fire-and-forget coroutines?
- Are race conditions possible with concurrent SQLite access?
- Are boundary conditions handled (empty lists, None values, zero-division, empty strings)?

#### Architecture & Design
- Does the change respect bounded context boundaries?
- Are dependencies pointing in the correct direction (inward per Clean Architecture)?
- Is new code behind a Protocol abstraction if it has multiple possible implementations?
- Are FastAPI routes returning the declared response model?
- Are new database queries covered by appropriate indexes?

#### Security
- Is user input validated and sanitized (SQL injection, XSS, path traversal)?
- Are secrets, API keys, and credential hashes never logged or exposed in error messages?
- Are authentication and authorization checks present where required?
- Is offline data encrypted at rest if it contains sensitive student information?
- Are rate-limiting considerations addressed for authentication endpoints?

#### Testing
- Does the change include tests?
- Do tests cover both happy path and error paths?
- Are async tests properly structured with `pytest-asyncio`?
- Do tests avoid coupling to implementation details?
- Do integration tests use realistic but isolated test data?

#### Performance
- Are N+1 queries avoided in SQLAlchemy?
- Are database indexes present for all new query patterns?
- Is there unnecessary memory allocation or large object creation?
- Are pagination patterns used for endpoints that return lists?

#### Readability & Maintainability
- Are type hints present on all function signatures and return types?
- Is naming clear and consistent with existing codebase conventions?
- Are there magic numbers or strings that should be named constants?
- Is the change small enough to review thoroughly (target: under 400 lines of diff)?

### 2.3 Approval Criteria

- **Minimum 2 approvals** required for merge to `main`.
- **1 approval** sufficient for merge to feature branches.
- All CI checks must pass (linting, type-checking, tests, security scan).
- No unresolved review comments marked as blocking.
- PR description must include: what changed, why it changed, how to test it, and any migration or configuration steps.
- PRs older than 5 business days without activity are flagged in weekly standup for resolution.

### 2.4 Review Turnaround

- **Target first review response:** Within 4 business hours of PR submission.
- **Critical/hotfix reviews:** Within 1 business hour.
- **Review completion:** All comments resolved within 2 business days.
- Reviewers who cannot complete a review within the target window must reassign or communicate delays.

### 2.5 Review Anti-Patterns to Avoid

- Rubber-stamping without reading the code.
- Nitpicking style issues that linters should catch.
- Withholding approval over architectural preferences not covered by existing standards.
- Reviewing only the diff without understanding the surrounding context.
- Approving PRs that lack tests for non-trivial logic changes.

---

## 3. Technical Debt Management

### 3.1 Identification

Technical debt is identified through multiple channels:

| Source | Example | Frequency |
|---|---|---|
| Code Reviews | Reviewer flags a workaround as TODO | Every PR |
| Development | Engineer tags code with `# DEBT:` or `# TECH_DEBT:` comments | Ad hoc |
| Retrospectives | Team identifies systemic friction | Bi-weekly |
| Architecture Reviews | Cross-cutting concerns reveal structural debt | Monthly |
| Incident Post-mortems | Root cause reveals underlying debt | Per incident |
| Linter/Tool Reports | Complexity warnings, deprecation notices | CI pipeline |

### 3.2 Debt Classification

**Severity Levels:**

- **Critical (P0):** Causes production incidents, security vulnerabilities, or data loss risk. Must be addressed within the current sprint.
- **High (P1):** Significantly slows development velocity or increases bug rate. Addressed within 2 sprints.
- **Medium (P2):** Creates friction but workarounds exist. Scheduled in the next quarterly planning.
- **Low (P3):** Code smell or minor inefficiency. Addressed opportunistically or during refactoring of adjacent code.

**Category Tags:**

- `DEBT-ARCH` — Architectural debt (wrong abstraction, missing layer boundary)
- `DEBT-TEST` — Missing or inadequate tests
- `DEBT-DOC` — Missing or outdated documentation
- `DEBT-SEC` — Security shortcuts or missing controls
- `DEBT-PERF` — Performance inefficiencies
- `DEBT-OPS` — Operational debt (missing monitoring, manual processes)
- `DEBT-DEP` — Outdated dependencies or pinned versions past EOL

### 3.3 Tracking

All technical debt is tracked as GitHub Issues with the `tech-debt` label and severity tag. The issue template includes:

```markdown
**Debt Type:** DEBT-ARCH | DEBT-TEST | DEBT-DOC | DEBT-SEC | DEBT-PERF | DEBT-OPS | DEBT-DEP
**Severity:** P0 | P1 | P2 | P3
**Area:** Backend | Frontend | Infrastructure | Database
**Estimated Effort:** S (< 4h) | M (4-16h) | L (16-40h) | XL (> 40h)
**Linked Issue:** (if discovered during another task)

**Description:** What is the debt and where does it live?

**Impact:** What happens if we do not address this?

**Proposed Solution:** How could this be resolved?

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
```

### 3.4 Remediation Policy

- **P0 debt** is treated like a production bug. The team stops current work and addresses it immediately.
- **P1 debt** receives dedicated sprint capacity — minimum 15% of each sprint is reserved for P1 debt.
- **P2 debt** is reviewed quarterly and promoted if it has grown in impact.
- **P3 debt** is batched into refactoring PRs when engineers are working in the affected area.
- **Debt Budget:** The team maintains a running debt budget. If total open P0+P1 issues exceeds 10, no new feature work begins until the count drops below 5.

### 3.5 Debt Prevention

- New code must pass all quality gates (see `QUALITY_GATES.md`).
- PRs that introduce new debt must include a corresponding debt-tracking issue.
- Quarterly architecture reviews proactively identify emerging structural debt.
- Automated tooling (linters, type checkers, complexity analyzers) catches common debt patterns before they ship.

---

## 4. Incident Response Procedures

### 4.1 Incident Severity Levels

| Level | Name | Description | Response Time | Example |
|---|---|---|---|---|
| SEV-1 | Critical | Application is unusable; data loss or security breach | Immediate (within 15 min) | Authentication system compromised; database corruption |
| SEV-2 | Major | Core feature is broken; significant user impact | Within 1 hour | Course completion not recording; quiz engine failing |
| SEV-3 | Minor | Non-core feature degraded; workaround available | Within 4 hours | Plugin marketplace search broken; export format issue |
| SEV-4 | Low | Cosmetic issue or minor inconvenience | Next business day | UI alignment issue; tooltip text wrong |

### 4.2 Incident Response Flow

```
1. DETECT    → Monitoring alert, user report, or engineer observation
2. TRIAGE    → Assess severity, assign severity level, notify appropriate responders
3. MITIGATE  → Stop the bleeding: rollback, disable feature, apply hotfix
4. RESOLVE   → Implement permanent fix, verify with tests
5. REVIEW    → Conduct post-mortem (see Section 6)
6. PREVENT   → Implement preventive measures, update runbooks
```

### 4.3 Incident Commander Role

The Incident Commander (IC) is the single point of coordination during an incident:

- **Who is IC:** Whoever detects the incident becomes IC unless they hand off. On-call engineer is default IC during business hours.
- **IC Responsibilities:**
  - Declares severity level and communicates it to the team.
  - Coordinates response activities — assigns tasks, removes blockers.
  - Maintains the incident timeline in the incident channel.
  - Decides when to escalate or involve additional responders.
  - Declares incident resolved and initiates post-mortem scheduling.
- **IC must NOT:** Be the sole person implementing the fix. The IC coordinates; others execute.

### 4.4 Communication During Incidents

- **Internal:** Dedicated incident channel (e.g., `#incidents` in team chat). Status updates every 30 minutes for SEV-1, every hour for SEV-2.
- **External (if applicable):** Status page updates. Student-facing communication via email for SEV-1 and SEV-2 incidents affecting data integrity.
- **Escalation Path:** IC → Engineering Lead → CTO → External stakeholders (only for SEV-1 with data breach implications).

### 4.5 Post-Incident Checklist

- [ ] Incident timeline documented
- [ ] Root cause identified
- [ ] Post-mortem meeting scheduled (within 48 hours)
- [ ] Preventive actions filed as issues
- [ ] Runbooks updated if procedures changed
- [ ] Monitoring gaps identified and addressed
- [ ] Stakeholders notified of resolution

---

## 5. On-call Rotation Guidelines

### 5.1 Context

AuthShield Lab is offline-only, so traditional 24/7 on-call is not necessary. However, on-call coverage is needed during active development sprints and for users running self-hosted instances.

### 5.2 On-call Structure

- **Primary on-call:** One engineer per week, rotating on Monday mornings.
- **Secondary on-call:** One engineer as backup, different person from primary.
- **Rotation order:** Defined in the `oncall-rotation.yaml` file, ensuring equal distribution across the team.
- **Swap policy:** Engineers may swap shifts with 48-hour notice. The swap must be recorded in the rotation schedule.

### 5.3 On-call Responsibilities

- Monitor issue tracker for incoming bug reports and support requests during business hours.
- Respond to SEV-1 and SEV-2 issues within the defined response times.
- Perform daily health checks of the CI/CD pipeline and build systems.
- Review and merge critical hotfix PRs when no other reviewer is available.
- Ensure the development environment is functional for the rest of the team.

### 5.4 On-call Expectations

- **Availability:** Primary on-call must be reachable within 15 minutes during business hours (9 AM - 6 PM local time).
- **Tools:** On-call engineer must have access to: issue tracker, CI dashboard, deployment logs, database diagnostics.
- **Handoff:** Outgoing on-call engineer writes a brief handoff note covering any open issues, ongoing investigations, and known concerns.
- **Compensation:** On-call duty outside standard hours is compensated with time-in-lieu or on-call stipend per company policy.

### 5.5 Escalation During On-call

```
Level 1 (0-15 min):    On-call engineer investigates independently
Level 2 (15-30 min):   Contact secondary on-call for assistance
Level 3 (30-60 min):   Escalate to Engineering Lead
Level 4 (60+ min):     Escalate to CTO; all-hands if SEV-1
```

---

## 6. Post-mortem Process

### 6.1 When to Conduct a Post-mortem

- All SEV-1 and SEV-2 incidents require a post-mortem.
- SEV-3 incidents require a post-mortem if they reveal systemic issues.
- Failed deployments that required rollback require a post-mortem.
- Near-misses (issues caught just before reaching users) are encouraged for post-mortems.

### 6.2 Post-mortem Meeting Structure

**Timing:** Within 48 hours of incident resolution. Duration: 60 minutes maximum.

**Attendees:** Incident Commander, responders, affected domain owner, engineering lead. Maximum 8 participants.

**Agenda:**

| Time | Activity | Owner |
|---|---|---|
| 0-5 min | Read the incident timeline silently | All |
| 5-20 min | Walk through timeline, confirm accuracy | IC |
| 20-35 min | Identify root cause(s) and contributing factors | All |
| 35-50 min | Brainstorm preventive actions | All |
| 50-55 min | Assign action items with owners and deadlines | Engineering Lead |
| 55-60 min | Schedule follow-up review | Engineering Lead |

### 6.3 Post-mortem Document Template

```markdown
# Post-mortem: [Incident Title]

**Date:** YYYY-MM-DD
**Duration:** [time from detection to resolution]
**Severity:** SEV-1 | SEV-2 | SEV-3
**Incident Commander:** [name]
**Author:** [name]

## Summary
[2-3 sentence summary of what happened and its impact]

## Timeline
| Time (UTC) | Event |
|---|---|
| HH:MM | [Event description] |

## Root Cause
[Detailed explanation of why the incident occurred]

## Contributing Factors
1. [Factor 1]
2. [Factor 2]

## Impact
- **Users affected:** [number or description]
- **Data impact:** [none / data corrected / data lost]
- **Duration of impact:** [time]

## What Went Well
1. [Thing 1]
2. [Thing 2]

## What Went Poorly
1. [Thing 1]
2. [Thing 2]

## Action Items
| # | Action | Owner | Deadline | Issue Link |
|---|---|---|---|---|
| 1 | [Action description] | [name] | YYYY-MM-DD | [#123] |

## Lessons Learned
[Key takeaways for the team]
```

### 6.4 Post-mortem Principles

- **Blameless:** The post-mortem focuses on systems and processes, not individuals. We examine why the system allowed the failure, not who caused it.
- **Actionable:** Every post-mortem must produce at least one concrete action item with an owner and deadline.
- **Follow-up:** A follow-up review occurs 30 days after the post-mortem to verify action items are completed.
- **Public:** Post-mortem documents are shared with the entire engineering team for learning purposes. Redact sensitive data as needed.

---

## 7. Engineering Career Ladder

### 7.1 Levels Overview

| Level | Title | Typical Experience | Scope |
|---|---|---|---|
| L1 | Junior Engineer | 0-2 years | Individual tasks, guided by senior engineers |
| L2 | Mid-level Engineer | 2-5 years | Independent features, small components |
| L3 | Senior Engineer | 5-8 years | Complex features, technical ownership of a domain |
| L4 | Staff Engineer | 8-12 years | Cross-domain technical leadership, architecture decisions |
| L5 | Principal Engineer | 12+ years | Organization-wide technical strategy, industry influence |

### 7.2 Role Expectations

#### L1 — Junior Engineer

- Completes well-defined tasks with guidance from senior team members.
- Writes code that meets coding conventions and passes quality gates.
- Participates actively in code reviews, learning from feedback.
- Asks questions proactively rather than struggling silently.
- Contributes to test writing for their features.
- Learning: Grows proficiency in Python, FastAPI, SQLAlchemy, React, and TypeScript.

#### L2 — Mid-level Engineer

- Independently owns and delivers features from requirements to deployment.
- Writes comprehensive tests including unit, integration, and edge cases.
- Provides thoughtful, constructive code reviews to peers.
- Identifies and addresses low-to-medium severity technical debt.
- Participates in on-call rotation and handles most incidents independently.
- Mentors junior engineers through pairing and review.

#### L3 — Senior Engineer

- Owns the technical direction of an entire bounded context (Identity, Education, Security, or Platform).
- Designs and implements complex features considering system-wide implications.
- Leads architecture decisions within their domain and documents them via ADRs.
- Drives technical debt remediation proactively.
- Conducts thorough post-mortems and drives systemic improvements.
- Mentors mid-level and junior engineers, providing regular career guidance.
- Contributes to the engineering handbook and coding conventions.

#### L4 — Staff Engineer

- Provides technical leadership across multiple bounded contexts.
- Designs cross-cutting concerns (authentication, event system, plugin architecture).
- Identifies and resolves architectural issues before they become systemic.
- Leads major refactoring efforts and technology evaluations.
- Sets technical standards and ensures team adherence.
- Collaborates with product and leadership on technical roadmap.
- Represents engineering in cross-functional planning.

#### L5 — Principal Engineer

- Defines the long-term technical vision for AuthShield Lab.
- Evaluates and adopts new technologies and frameworks.
- Solves the hardest technical problems that span the entire system.
- Contributes to the cybersecurity education industry through papers, talks, or open source.
- Shapes engineering culture and practices across the organization.
- Advises leadership on technical risk and investment priorities.

### 7.3 Promotion Criteria

Promotions are based on consistently operating at the next level for 6+ months, as demonstrated through:

- **Impact:** Measurable contributions that improved the platform, team velocity, or user experience.
- **Scope:** Ability to handle increasingly complex and ambiguous problems.
- **Leadership:** Influence on team practices, mentorship of others, and technical decision-making.
- **Communication:** Clear documentation, effective code reviews, and productive collaboration.
- **Reliability:** Consistent delivery, incident response, and follow-through on commitments.

### 7.4 Performance Review Cadence

- **Weekly:** 1:1 meetings with engineering lead (30 min).
- **Monthly:** Goal progress check-in (part of 1:1).
- **Quarterly:** Formal performance and growth review with written self-assessment.
- **Annually:** Comprehensive review with compensation and level assessment.

---

## 8. Meeting Cadence

### 8.1 Weekly Meetings

| Meeting | Frequency | Duration | Attendees | Purpose |
|---|---|---|---|---|
| Daily Standup | Daily | 15 min | Full engineering team | Sync on progress, blockers, and plans for the day |
| Sprint Planning | Bi-weekly (Monday) | 60 min | Full team + Product | Plan work for the upcoming sprint |
| Sprint Review/Demo | Bi-weekly (Friday) | 30 min | Full team + stakeholders | Demo completed work, gather feedback |
| Sprint Retrospective | Bi-weekly (Friday) | 45 min | Full engineering team | Reflect on process, identify improvements |
| Architecture Review | Monthly | 90 min | L3+ engineers | Review architectural decisions, ADRs, and system health |
| Tech Talk / Brown Bag | Bi-weekly | 30 min | Optional, all team | Share knowledge on topics of interest |

### 8.2 Daily Standup Format

Each engineer answers three questions (target: 2 minutes per person):

1. **What did I complete yesterday?** (Focus on outcomes, not activities)
2. **What will I work on today?** (Specific, actionable goals)
3. **Are there any blockers?** (Anything preventing progress)

**Rules:**
- Standup is synchronous for the core team; async updates via Slack for time-zone-distributed members.
- Detailed discussions are taken offline — the standup is for coordination, not problem-solving.
- If no one has blockers, the standup should end in under 15 minutes.

### 8.3 Architecture Review Agenda

| Time | Topic |
|---|---|
| 0-15 min | Review open ADRs and pending design proposals |
| 15-45 min | Deep-dive on the selected architecture topic of the month |
| 45-70 min | Review technical debt trends and prioritize remediation |
| 70-85 min | Discuss upcoming feature implications on architecture |
| 85-90 min | Action items and next meeting topic selection |

### 8.4 Retrospective Format

Rotating formats to keep retrospectives effective:

- **Start/Stop/Continue:** What should we start doing, stop doing, and continue doing?
- **4Ls:** What did we Love, Learn, Lack, and Long for?
- **Mad/Sad/Glad:** Categorize experiences by emotional response.
- **Sailboat:** Wind (what propelled us), Anchor (what held us back), Rocks (risks ahead), Island (our goal).
- **Timeline:** Walk through the sprint chronologically and mark highs and lows.

**Output:** Each retrospective produces a maximum of 3 action items with owners and deadlines. Action items are reviewed at the start of the next retrospective.

---

## 9. Communication Standards

### 9.1 Request for Comments (RFC) Process

RFCs are used for significant technical decisions that affect multiple teams or have long-lasting impact.

**When to write an RFC:**
- Introducing a new technology, framework, or major dependency.
- Changing the database schema strategy or migration approach.
- Modifying the plugin architecture or event system.
- Altering the authentication/authorization model.
- Any change affecting the offline-first architecture guarantees.

**RFC Process:**

```
1. Draft     → Author writes RFC document (template below)
2. Review    → 1-week review period; all L3+ engineers must provide feedback
3. Decide    → Author or Architecture Lead makes final decision, documenting rationale
4. Implement → RFC is implemented; the RFC document becomes a living reference
5. Archive   → Completed RFCs are archived in docs/standards/rfcs/
```

**RFC Template:**

```markdown
# RFC-[NNN]: [Title]

**Author:** [name]
**Status:** Draft | In Review | Accepted | Rejected | Superseded
**Created:** YYYY-MM-DD
**Updated:** YYYY-MM-DD

## Summary
[1-2 paragraph summary of the proposal]

## Motivation
[Why is this change needed? What problem does it solve?]

## Detailed Design
[Technical description of the proposed solution]

## Alternatives Considered
[What other approaches were evaluated? Why were they rejected?]

## Impact
- **Areas affected:** [list of bounded contexts, services, or components]
- **Migration required:** Yes/No — if yes, describe migration plan
- **Backward compatibility:** [impact on existing functionality]
- **Performance impact:** [expected impact on latency, memory, disk usage]

## Open Questions
[Remaining questions that need resolution before implementation]

## References
[Links to related RFCs, ADRs, documentation, or external resources]
```

### 9.2 Architecture Decision Records (ADRs)

ADRs document significant architectural decisions and their rationale. They are shorter than RFCs and focused on decisions already made.

**ADR Template:**

```markdown
# ADR-[NNN]: [Decision Title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-[NNN]
**Decision Makers:** [list of people involved]

## Context
[What is the situation that necessitated this decision?]

## Decision
[What is the decision that was made?]

## Rationale
[Why was this decision made? What factors were considered?]

## Consequences
- **Positive:** [benefits of this decision]
- **Negative:** [trade-offs and downsides]
- **Risks:** [potential issues this introduces]

## Alternatives Rejected
[What other options were considered and why they were not chosen]
```

**Storage:** ADRs live in `docs/standards/adr/` with sequential numbering.

### 9.3 Design Documents

For features requiring detailed upfront design (estimated at more than 3 sprint-days of work), a design document is written before implementation begins.

**Design Document Template:**

```markdown
# Design: [Feature Name]

**Author:** [name]
**Reviewers:** [list]
**Status:** Draft | In Review | Approved | Implemented
**Target Sprint:** [sprint identifier]

## Problem Statement
[What user or technical problem does this feature solve?]

## Goals and Non-Goals
### Goals
1. [Goal 1]
2. [Goal 2]

### Non-Goals
1. [Explicitly out of scope]

## Proposed Solution
### Architecture
[High-level architecture description with diagrams]

### Data Model
[New tables, columns, or schema changes]

### API Design
[New or changed endpoints with request/response schemas]

### UI Design
[Wireframes or descriptions of UI changes]

### Error Handling
[How errors are detected, reported, and recovered]

### Testing Strategy
[What types of tests will be written and why]

## Migration Plan
[Steps to deploy this feature without downtime or data loss]

## Rollback Plan
[How to revert if something goes wrong]

## Open Questions
[Unresolved design decisions]
```

### 9.4 Communication Channels

| Channel | Purpose | Response SLA |
|---|---|---|
| `#engineering` | General engineering discussion, announcements | 4 hours during business hours |
| `#incidents` | Active incident coordination | 15 minutes during incidents |
| `#code-reviews` | PR review requests and discussions | 4 hours for review assignment |
| `#architecture` | Technical design discussions, ADR reviews | 1 business day |
| `#standup` | Async daily standup updates (for distributed team) | End of business day |
| `#random` | Non-work social conversation | Best effort |

---

## 10. Knowledge Transfer Protocols

### 10.1 When Knowledge Transfer Is Required

- An engineer is leaving the team or going on extended leave (2+ weeks).
- A new bounded context or major subsystem is being introduced.
- A single engineer is the sole expert on a critical system (bus factor of 1).
- After a major incident, when institutional knowledge was generated.

### 10.2 Knowledge Transfer Methods

#### Pair Programming / Mob Programming
- **When:** For active knowledge transfer during normal development.
- **Duration:** 1-2 hours per session, 3-5 sessions over 2 weeks.
- **Format:** Knowledge holder drives while learner navigates, then roles reverse.
- **Best for:** Codebase navigation, debugging workflows, deployment procedures.

#### Documentation
- **When:** For persistent, reference-grade knowledge.
- **Format:** Markdown documents in the appropriate `docs/` directory.
- **Minimum required sections:** Purpose, setup, architecture, common tasks, troubleshooting.
- **Review:** Documentation must be reviewed by at least one other engineer for accuracy.

#### Recorded Walkthroughs
- **When:** For visual/auditory learners or complex system overviews.
- **Format:** Screen recordings with narration, stored in the team's knowledge base.
- **Duration:** 15-30 minutes per recording, focused on a specific topic.
- **Topics:** Architecture overview, deployment process, debugging common issues, database management.

#### Runbooks
- **When:** For operational procedures that must be followed step-by-step.
- **Format:** Numbered steps with expected outcomes at each stage.
- **Location:** `docs/runbooks/` directory.
- **Required runbooks:** Deployment, database migration, incident response, plugin installation.

### 10.3 Knowledge Transfer Checklist

When an engineer is transitioning off a project or leaving:

- [ ] All active PRs are completed or reassigned.
- [ ] Architecture Decision Records for systems they own are up to date.
- [ ] Critical-path documentation is current (runbooks, API docs, data model docs).
- [ ] At least 2 other engineers have been walked through their primary systems.
- [ ] Credentials, access tokens, and service accounts are transferred or revoked.
- [ ] On-call rotation is updated to remove the departing engineer.
- [ ] A recorded walkthrough of the top 3 most complex subsystems is completed.
- [ ] A "lessons learned" document is written covering pain points and improvement ideas.
- [ ] Handoff meeting is conducted with the replacement engineer(s).

### 10.4 Documentation Standards for Knowledge Articles

All knowledge transfer documentation must follow these standards:

- **Title:** Clear, descriptive title that can be found via search.
- **Audience:** State who the document is for (new engineer, ops, security, etc.).
- **Last Updated:** Date and author on every document.
- **Prerequisites:** What the reader should know before reading.
- **Step-by-step instructions:** Numbered steps, not paragraphs.
- **Code examples:** Working examples with expected output.
- **Troubleshooting:** Common failure modes and resolution steps.
- **Links:** Cross-references to related documents and ADRs.

### 10.5 Knowledge Base Organization

```
docs/
  standards/           ← Engineering standards and conventions (this handbook)
    adr/               ← Architecture Decision Records
    rfcs/              ← Request for Comments documents
  runbooks/            ← Operational procedures
  architecture/        ← System architecture documentation
    identity/          ← Identity bounded context docs
    education/         ← Education bounded context docs
    security/          ← Security bounded context docs
    platform/          ← Platform bounded context docs
  api/                 ← API documentation
  onboarding/          ← New engineer onboarding guides
  postmortems/         ← Incident post-mortem documents
```

### 10.6 Onboarding Knowledge Transfer

New engineers receive a structured onboarding experience:

**Week 1 — Foundation:**
- Read the Engineering Handbook, Coding Conventions, and Testing Standards.
- Set up the local development environment with assistance.
- Complete the "Your First PR" guided tutorial.
- Meet with each bounded context owner for a 30-minute overview.

**Week 2 — Deep Dive:**
- Pair with a senior engineer on a feature implementation.
- Review the architecture documentation and ADRs.
- Complete a small bug fix independently.
- Attend all team ceremonies and observe.

**Week 3 — Contributing:**
- Own a small feature or bug fix from requirements to deployment.
- Participate in code reviews (as reviewer and author).
- shadow on-call engineer for one day.

**Week 4 — Independent:**
- Take on a medium-complexity feature independently.
- Participate in on-call rotation.
- Provide feedback on the onboarding experience.

---

*This document is a living artifact. Propose changes via PR to the repository. All changes require approval from the Engineering Lead and at least one Staff Engineer.*
