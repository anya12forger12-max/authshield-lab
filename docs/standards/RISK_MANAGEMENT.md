# AuthShield Lab — Risk Management Framework

> Version 1.0 · Last Updated: 2026-07-19 · Owner: Engineering Leadership

---

## Table of Contents

1. [Overview](#1-overview)
2. [Risk Identification Process](#2-risk-identification-process)
3. [Risk Assessment Matrix](#3-risk-assessment-matrix)
4. [Risk Mitigation Strategies](#4-risk-mitigation-strategies)
5. [Risk Monitoring](#5-risk-monitoring)
6. [Technical Risk Categories](#6-technical-risk-categories)
7. [Security Risk Categories](#7-security-risk-categories)
8. [Operational Risk Categories](#8-operational-risk-categories)
9. [Risk Register Template](#9-risk-register-template)
10. [Risk Review Cadence](#10-risk-review-cadence)

---

## 1. Overview

### 1.1 Purpose

This framework provides a structured approach to identifying, assessing, mitigating, and monitoring risks across the AuthShield Lab project. Given that AuthShield Lab is a cybersecurity education platform operating in an offline-only mode, risks differ significantly from typical cloud-deployed SaaS applications. This framework is tailored to that reality.

### 1.2 Scope

This framework covers:
- **Technical risks** affecting system reliability, performance, and maintainability.
- **Security risks** affecting data confidentiality, integrity, and availability.
- **Operational risks** affecting team productivity, knowledge continuity, and delivery capability.
- **Strategic risks** affecting project viability, scope, and stakeholder alignment.

### 1.3 Roles and Responsibilities

| Role | Responsibility |
|---|---|
| **Engineering Lead** | Owns the risk register, leads risk review meetings, ensures mitigation actions are completed |
| **Security Champion** | Leads security risk identification and assessment, conducts threat modeling |
| **Senior Engineers** | Identify and document risks within their domain, implement mitigations |
| **All Engineers** | Report new risks as they are discovered, participate in risk assessments |
| **Product Owner** | Provides input on business impact and priority of risk mitigation |

### 1.4 Risk Management Principles

1. **Proactive over reactive.** Identify and mitigate risks before they become incidents.
2. **Proportionate.** Risk assessment effort is proportional to the risk severity.
3. **Transparent.** All risks are documented and visible to the team.
4. **Continuous.** Risk management is an ongoing process, not a one-time exercise.
5. **Blameless.** Reporting risks is encouraged and never punished, regardless of who identified them.

---

## 2. Risk Identification Process

### 2.1 Identification Methods

| Method | Description | Frequency | Participants |
|---|---|---|---|
| **Threat Modeling** | Structured analysis of threats using STRIDE or DREAD methodology | Per major feature | Security Champion + domain engineers |
| **Architecture Review** | Systematic review of architectural decisions for risk implications | Monthly | L3+ engineers |
| **Retrospective Analysis** | Identification of risks that materialized as incidents or near-misses | Bi-weekly | Full engineering team |
| **Code Review Risk Assessment** | Reviewers identify risks introduced by code changes | Every PR | Code reviewers |
| **Dependency Analysis** | Assessment of risks from third-party libraries and tools | Monthly | Security Champion + Engineering Lead |
| **Pre-mortem Analysis** | Imagining a future failure and working backward to identify causes | Before major features | Feature team |
| **External Threat Intelligence** | Monitoring CVE databases, security advisories, and industry reports | Weekly | Security Champion |

### 2.2 STRIDE Threat Model

For each major component, systematically evaluate:

| Threat | Description | AuthShield Lab Example |
|---|---|---|
| **S**poofing | Impersonating a user or system component | Forged authentication tokens, credential theft |
| **T**ampering | Modifying data without authorization | SQLite database manipulation, plugin tampering |
| **R**epudiation | Denying actions that were performed | Audit log gaps, missing authentication trails |
| **I**nformation Disclosure | Exposing data to unauthorized parties | Credential hashes in logs, debug endpoints in production |
| **D**enial of Service | Making the system unavailable | Database lock exhaustion, memory exhaustion via large uploads |
| **E**levation of Privilege | Gaining unauthorized access levels | Role escalation, plugin sandbox escape |

### 2.3 Risk Discovery Triggers

New risks may be identified at any time. The following events trigger mandatory risk assessment:

- Introduction of a new third-party dependency.
- Changes to the authentication or authorization system.
- Discovery of a CVE affecting a used dependency.
- A production incident or near-miss.
- Significant architectural changes.
- Changes to the SQLite schema strategy.
- New plugin or extension API introduction.
- Changes affecting offline data storage or encryption.
- Team member departure affecting bus factor.

---

## 3. Risk Assessment Matrix

### 3.1 Likelihood Scale

| Level | Score | Description | Frequency |
|---|---|---|---|
| **Almost Certain** | 5 | Expected to occur within the project lifecycle | > 10% probability per year |
| **Likely** | 4 | Will probably occur at some point | 5-10% probability per year |
| **Possible** | 3 | Could occur under certain conditions | 1-5% probability per year |
| **Unlikely** | 2 | Not expected but possible | < 1% probability per year |
| **Rare** | 1 | May occur only in exceptional circumstances | < 0.1% probability per year |

### 3.2 Impact Scale

| Level | Score | Technical Impact | Business Impact | Security Impact |
|---|---|---|---|---|
| **Catastrophic** | 5 | Complete system failure, data loss | Project failure, legal liability | Data breach, credential compromise |
| **Major** | 4 | Significant feature degradation, data corruption | Major scope delay, significant user impact | Unauthorized access to sensitive data |
| **Moderate** | 3 | Partial feature failure, performance degradation | Schedule impact, workaround required | Exposure of non-sensitive internal data |
| **Minor** | 2 | Cosmetic issues, minor performance impact | Minimal schedule impact | Limited exposure of public information |
| **Insignificant** | 1 | No functional impact | No measurable impact | No security impact |

### 3.3 Risk Score Matrix

The risk score is calculated as: **Risk Score = Likelihood × Impact**

|  | Insignificant (1) | Minor (2) | Moderate (3) | Major (4) | Catastrophic (5) |
|---|---|---|---|---|---|
| **Almost Certain (5)** | 5 (Medium) | 10 (High) | 15 (Critical) | 20 (Critical) | 25 (Critical) |
| **Likely (4)** | 4 (Low) | 8 (Medium) | 12 (High) | 16 (Critical) | 20 (Critical) |
| **Possible (3)** | 3 (Low) | 6 (Medium) | 9 (Medium) | 12 (High) | 15 (Critical) |
| **Unlikely (2)** | 2 (Low) | 4 (Low) | 6 (Medium) | 8 (Medium) | 10 (High) |
| **Rare (1)** | 1 (Low) | 2 (Low) | 3 (Low) | 4 (Low) | 5 (Medium) |

### 3.4 Risk Severity Levels

| Severity | Score Range | Response Required | Response Time |
|---|---|---|---|
| **Critical** | 15-25 | Immediate mitigation required. Escalate to Engineering Lead. | Within 24 hours |
| **High** | 10-14 | Mitigation plan required. Assign owner and deadline. | Within 1 week |
| **Medium** | 5-9 | Mitigation plan recommended. Monitor and review. | Within 1 sprint (2 weeks) |
| **Low** | 1-4 | Accept or monitor. No immediate action required. | Review at next risk review meeting |

---

## 4. Risk Mitigation Strategies

### 4.1 Mitigation Approaches

| Strategy | Description | When to Use |
|---|---|---|
| **Avoid** | Eliminate the risk by changing the approach or design | When the risk is unacceptable and an alternative exists |
| **Mitigate** | Reduce the likelihood or impact of the risk | When the risk is significant but the activity is necessary |
| **Transfer** | Shift the risk to another party or system | When another party can better manage the risk |
| **Accept** | Acknowledge the risk and proceed without action | When the risk is low and mitigation cost exceeds the benefit |
| **Monitor** | Track the risk for changes in likelihood or impact | When the risk may change over time but does not require immediate action |

### 4.2 Mitigation Strategy Selection

```
Is the risk acceptable as-is?
  → YES → Accept and Monitor
  → NO  → Can the risk be avoided entirely?
            → YES → Avoid
            → NO  → Can the risk be transferred?
                      → YES → Transfer
                      → NO  → Mitigate
```

### 4.3 Common Mitigation Patterns for AuthShield Lab

#### Technical Risk Mitigations

| Risk | Mitigation | Strategy |
|---|---|---|
| SQLite lock contention under load | Use WAL mode, connection pooling, retry logic with backoff | Mitigate |
| Data corruption from power loss | WAL journaling, backup system, integrity checks on startup | Mitigate |
| Performance degradation with data growth | Pagination, query optimization, data archiving strategy | Mitigate |
| Single point of failure (single SQLite file) | Regular backups, WAL mode, integrity verification | Mitigate + Monitor |
| Dependency vulnerabilities | Automated dependency scanning, pinning versions, regular updates | Mitigate |
| Breaking changes in dependencies | Version pinning, compatibility testing in CI, upgrade windows | Mitigate |
| Plugin system introducing instability | Sandboxing, capability-based permissions, comprehensive testing | Avoid + Mitigate |
| Migration failures | Forward + backward migration testing, staging environment | Mitigate |

#### Security Risk Mitigations

| Risk | Mitigation | Strategy |
|---|---|---|
| Credential theft | bcrypt/argon2 hashing, MFA, account lockout | Mitigate |
| SQL injection | Parameterized queries via SQLAlchemy ORM, input validation | Avoid |
| Cross-site scripting (XSS) | React's auto-escaping, CSP headers, output encoding | Avoid |
| Plugin-based privilege escalation | Plugin sandboxing, capability-based permissions, code review | Avoid + Mitigate |
| Offline data theft | Disk encryption, encrypted credential storage, secure deletion | Mitigate |
| Audit log tampering | Append-only log tables, cryptographic integrity checks | Mitigate |
| Man-in-the-middle on local API | localhost binding only, no network exposure by default | Avoid |

#### Operational Risk Mitigations

| Risk | Mitigation | Strategy |
|---|---|---|
| Bus factor (single expert) | Knowledge transfer protocols, documentation, cross-training | Mitigate |
| Key person unavailability | On-call rotation, runbooks, automated deployment | Mitigate |
| Loss of institutional knowledge | ADRs, RFCs, engineering handbook, recorded walkthroughs | Mitigate |
| Scope creep | RFC process, architecture reviews, sprint planning discipline | Avoid |
| Technical debt accumulation | Debt tracking, dedicated sprint capacity, quality gates | Mitigate |
| Deployment failures | Automated CI/CD, rollback procedures, staged releases | Mitigate |

---

## 5. Risk Monitoring

### 5.1 Monitoring Methods

| Method | Description | Frequency | Owner |
|---|---|---|---|
| **Risk Register Review** | Review all open risks for status changes and new entries | Bi-weekly (retrospective) | Engineering Lead |
| **Security Monitoring** | Monitor CVE databases, dependency advisories, and threat intelligence | Weekly | Security Champion |
| **Incident Tracking** | Track incidents and near-misses for risk implications | Per incident | Incident Commander |
| **Quality Gate Monitoring** | Track quality gate pass/fail rates as leading indicators | Weekly | Engineering Lead |
| **Dependency Health Dashboard** | Monitor dependency age, update frequency, and vulnerability status | Monthly | Security Champion |
| **Test Coverage Trends** | Track coverage changes over time as a quality indicator | Per sprint | Engineering Lead |

### 5.2 Risk Indicators

Leading indicators that a risk may be materializing:

| Indicator | What It Signals | Threshold |
|---|---|---|
| CI pipeline failure rate | Quality degradation | > 5% failure rate in a week |
| Open P0/P1 bugs increasing | Product stability declining | > 10 open P0/P1 bugs |
| Test coverage decreasing | Code quality risk growing | Drop of > 2% in a sprint |
| Dependency age increasing | Security/maintenance risk | Dependencies > 6 months without updates |
| PR review turnaround increasing | Knowledge bottleneck risk | > 24 hour average turnaround |
| Sprint velocity decreasing | Delivery risk increasing | > 20% velocity drop over 2 sprints |
| Flaky test count increasing | Test infrastructure degradation | > 5 flaky tests in CI |

### 5.3 Escalation Thresholds

| Condition | Escalation Path | Response |
|---|---|---|
| New Critical risk identified | Engineering Lead → CTO | Immediate assessment and mitigation plan |
| Risk materialized as incident | Follow Incident Response Procedures | Per `ENGINEERING_HANDBOOK.md` Section 4 |
| > 3 High risks open simultaneously | Engineering Lead → Team | Dedicated risk sprint or risk week |
| Risk mitigation overdue by > 2 weeks | Engineering Lead → Engineering Lead's manager | Status review and resource reallocation |

---

## 6. Technical Risk Categories

### 6.1 Architecture Risks

| Risk ID | Risk Description | Likelihood | Impact | Score | Severity | Mitigation |
|---|---|---|---|---|---|---|
| TECH-001 | SQLite becomes a bottleneck for concurrent users | 3 | 3 | 9 | Medium | WAL mode, connection pooling, benchmarking; plan migration path to PostgreSQL if needed |
| TECH-002 | Clean Architecture boundaries erode over time | 4 | 3 | 12 | High | Lint rules for import boundaries, architecture reviews, ADR documentation |
| TECH-003 | Plugin system introduces hard-to-debug failures | 3 | 4 | 12 | High | Plugin sandboxing, comprehensive integration tests, versioned plugin API |
| TECH-004 | Event bus becomes a single point of failure | 2 | 4 | 8 | Medium | Outbox pattern for reliability, event replay capability, monitoring |
| TECH-005 | Database schema migrations cause data loss | 2 | 5 | 10 | High | Migration testing, rollback procedures, backup before migration |
| TECH-006 | Electron frontend becomes unmaintainable | 3 | 3 | 9 | Medium | Component library, storybook, design system documentation |

### 6.2 Dependency Risks

| Risk ID | Risk Description | Likelihood | Impact | Score | Severity | Mitigation |
|---|---|---|---|---|---|---|
| TECH-007 | Critical dependency abandoned or compromised | 2 | 4 | 8 | Medium | Regular dependency audits, fallback alternatives documented |
| TECH-008 | Breaking changes in FastAPI/SQLAlchemy/Pydantic | 3 | 3 | 9 | Medium | Version pinning, upgrade testing in CI, phased upgrades |
| TECH-009 | Python version EOL forces forced upgrade | 2 | 3 | 6 | Medium | Track Python release schedule, test against upcoming versions |
| TECH-010 | Electron/React major version upgrade breaks build | 3 | 3 | 9 | Medium | Dependency updates in dedicated PRs, comprehensive frontend tests |

### 6.3 Performance Risks

| Risk ID | Risk Description | Likelihood | Impact | Score | Severity | Mitigation |
|---|---|---|---|---|---|---|
| TECH-011 | Application memory usage grows unbounded over time | 3 | 3 | 9 | Medium | Memory profiling in CI, resource limits, monitoring |
| TECH-012 | Startup time increases as data grows | 3 | 2 | 6 | Medium | Lazy loading, data archiving, startup benchmarks |
| TECH-013 | Large file uploads cause OOM | 2 | 3 | 6 | Medium | Upload size limits, streaming uploads, memory limits |

---

## 7. Security Risk Categories

### 7.1 Authentication & Authorization Risks

| Risk ID | Risk Description | Likelihood | Impact | Score | Severity | Mitigation |
|---|---|---|---|---|---|---|
| SEC-001 | Brute force attack on login endpoint | 4 | 3 | 12 | High | Rate limiting, account lockout, CAPTCHA after failures |
| SEC-002 | Credential stuffing attack | 3 | 4 | 12 | High | Account lockout, credential breach detection, MFA |
| SEC-003 | Session hijacking via token theft | 2 | 4 | 8 | Medium | Short-lived tokens, secure storage, token rotation |
| SEC-004 | Privilege escalation via role manipulation | 2 | 5 | 10 | High | Server-side role validation, RBAC enforcement, audit logging |
| SEC-005 | MFA bypass through enrollment skip | 2 | 4 | 8 | Medium | Enforce MFA before sensitive operations, enrollment validation |

### 7.2 Data Protection Risks

| Risk ID | Risk Description | Likelihood | Impact | Score | Severity | Mitigation |
|---|---|---|---|---|---|---|
| SEC-006 | Credential hashes exposed in logs | 3 | 4 | 12 | High | Log sanitization, structured logging, log review |
| SEC-007 | SQLite database file accessed by unauthorized users | 3 | 4 | 12 | High | OS-level file permissions, encrypted storage option |
| SEC-008 | Sensitive data in error responses | 3 | 3 | 9 | Medium | Error response sanitization, security testing |
| SEC-009 | PII stored without encryption at rest | 2 | 4 | 8 | Medium | Encryption at rest option, data classification |
| SEC-010 | Audit logs tampered with | 2 | 4 | 8 | Medium | Append-only tables, cryptographic integrity, log rotation |

### 7.3 Input Validation Risks

| Risk ID | Risk Description | Likelihood | Impact | Score | Severity | Mitigation |
|---|---|---|---|---|---|---|
| SEC-011 | SQL injection via search parameters | 2 | 5 | 10 | High | ORM usage, parameterized queries, input validation |
| SEC-012 | XSS via user-generated content | 3 | 3 | 9 | Medium | React auto-escaping, CSP headers, output encoding |
| SEC-013 | Path traversal in file operations | 2 | 4 | 8 | Medium | Path validation, sandboxed file system, allowlists |
| SEC-014 | Plugin code execution without sandboxing | 3 | 5 | 15 | Critical | Plugin sandboxing, capability-based permissions, code review |

### 7.4 Offline-Specific Security Risks

| Risk ID | Risk Description | Likelihood | Impact | Score | Severity | Mitigation |
|---|---|---|---|---|---|---|
| SEC-015 | Data theft from local device | 3 | 4 | 12 | High | Disk encryption, encrypted credential storage, secure deletion |
| SEC-016 | Malicious plugin installation via USB/sideload | 2 | 4 | 8 | Medium | Plugin signature verification, allowlisting, user confirmation |
| SEC-017 | Backup data exposure | 2 | 3 | 6 | Medium | Encrypted backups, backup access controls |

---

## 8. Operational Risk Categories

### 8.1 Team & Knowledge Risks

| Risk ID | Risk Description | Likelihood | Impact | Score | Severity | Mitigation |
|---|---|---|---|---|---|---|
| OPS-001 | Key engineer departure causes knowledge loss | 3 | 4 | 12 | High | Knowledge transfer protocols, documentation, cross-training |
| OPS-002 | Bus factor of 1 on critical subsystems | 3 | 4 | 12 | High | Mandatory knowledge sharing, pair programming, documentation |
| OPS-003 | Onboarding time too long for new engineers | 3 | 2 | 6 | Medium | Improved onboarding docs, mentorship program, setup automation |
| OPS-004 | Team burnout from on-call or crunch periods | 3 | 3 | 9 | Medium | Sustainable pace policy, on-call rotation, workload monitoring |

### 8.2 Process Risks

| Risk ID | Risk Description | Likelihood | Impact | Score | Severity | Mitigation |
|---|---|---|---|---|---|---|
| OPS-005 | Scope creep delays delivery | 4 | 3 | 12 | High | RFC process, sprint planning discipline, change management |
| OPS-006 | Technical debt blocks feature development | 4 | 3 | 12 | High | Dedicated debt capacity, quality gates, debt tracking |
| OPS-007 | Deployment failures in production | 2 | 4 | 8 | Medium | Automated CI/CD, rollback procedures, staged releases |
| OPS-008 | Release process errors (wrong version, missing migration) | 2 | 3 | 6 | Medium | Release checklist, automated versioning, migration testing |
| OPS-009 | Insufficient testing before release | 3 | 3 | 9 | Medium | Quality gates, coverage requirements, test automation |

### 8.3 Infrastructure Risks

| Risk ID | Risk Description | Likelihood | Impact | Score | Severity | Mitigation |
|---|---|---|---|---|---|---|
| OPS-010 | CI/CD pipeline outage prevents deployments | 3 | 3 | 9 | Medium | Pipeline redundancy, local build capability, backup deploy process |
| OPS-011 | Development environment inconsistencies | 4 | 2 | 8 | Medium | Docker dev environment, pinned tool versions, setup scripts |
| OPS-012 | Build tool compatibility issues | 2 | 3 | 6 | Medium | Version pinning, CI matrix testing, upgrade windows |
| OPS-013 | Data loss from user device failure | 3 | 3 | 9 | Medium | Backup recommendations, export/import capability, data recovery |

---

## 9. Risk Register Template

### 9.1 Risk Entry Format

```markdown
| Field | Description |
|---|---|
| **Risk ID** | Unique identifier: {CATEGORY}-{NNN} (e.g., TECH-001, SEC-003) |
| **Title** | Short descriptive title |
| **Description** | Detailed description of the risk, including triggers and conditions |
| **Category** | Technical | Security | Operational | Strategic |
| **Sub-category** | Architecture | Dependency | Performance | Auth | Data | Input | Team | Process | Infrastructure |
| **Likelihood** | 1-5 (see Risk Assessment Matrix) |
| **Impact** | 1-5 (see Risk Assessment Matrix) |
| **Score** | Likelihood × Impact |
| **Severity** | Critical | High | Medium | Low (derived from score) |
| **Owner** | Name of person responsible for monitoring and mitigation |
| **Mitigation Strategy** | Avoid | Mitigate | Transfer | Accept | Monitor |
| **Mitigation Actions** | Specific actions to reduce likelihood or impact |
| **Mitigation Deadline** | Date by which mitigation must be implemented |
| **Status** | Open | In Progress | Mitigated | Closed | Accepted |
| **Identified Date** | Date the risk was first identified |
| **Last Reviewed** | Date of most recent review |
| **Notes** | Additional context, related incidents, or references |
```

### 9.2 Risk Register File

The risk register is maintained as a structured YAML file in the repository:

```yaml
# docs/standards/risk-register.yaml

risks:
  - id: "SEC-014"
    title: "Plugin code execution without sandboxing"
    description: >
      The plugin system allows third-party code execution. Without proper
      sandboxing, a malicious or buggy plugin could access user credentials,
      modify system files, or escape to the host system.
    category: security
    sub_category: input
    likelihood: 3
    impact: 5
    score: 15
    severity: critical
    owner: "Security Champion"
    mitigation_strategy: "mitigate"
    mitigation_actions:
      - "Implement plugin capability-based permission system"
      - "Add plugin code signing and verification"
      - "Implement runtime sandboxing using process isolation"
      - "Add comprehensive security tests for plugin API"
      - "Conduct security audit of plugin system before release"
    mitigation_deadline: "2026-09-30"
    status: "in_progress"
    identified_date: "2026-06-15"
    last_reviewed: "2026-07-19"
    notes: >
      Depends on the plugin architecture design (see ADR-007).
      Critical for cybersecurity education platform credibility.
```

### 9.3 Risk Summary Dashboard

```yaml
# Risk summary for quick reference
summary:
  total_open: 18
  by_severity:
    critical: 2
    high: 6
    medium: 8
    low: 2
  by_status:
    open: 10
    in_progress: 6
    mitigated: 1
    accepted: 1
  by_category:
    technical: 13
    security: 12
    operational: 9
  overdue_mitigations: 1
  next_review_date: "2026-08-02"
```

---

## 10. Risk Review Cadence

### 10.1 Regular Review Schedule

| Review Type | Frequency | Duration | Participants | Output |
|---|---|---|---|---|
| **Quick Risk Check** | Daily standup (ad hoc) | 2 min | Standup participants | Risk flagged for investigation |
| **Sprint Risk Review** | Bi-weekly (during retrospective) | 15 min | Full engineering team | Updated risk statuses, new risks identified |
| **Monthly Risk Deep-Dive** | Monthly | 60 min | Engineering Lead, Security Champion, L3+ engineers | Risk register update, mitigation progress review |
| **Quarterly Risk Audit** | Quarterly | 90 min | Full team + stakeholders | Comprehensive risk assessment, risk register cleanup |
| **Incident-Triggered Review** | After every SEV-1/SEV-2 incident | 30-60 min | IC, responders, Engineering Lead | New risks identified, existing risks re-assessed |
| **Pre-Release Risk Assessment** | Before every major release | 30 min | Release team | Release-specific risk check, go/no-go decision |

### 10.2 Monthly Risk Deep-Dive Agenda

| Time | Activity | Owner |
|---|---|---|
| 0-5 min | Review risk summary dashboard | Engineering Lead |
| 5-20 min | Review all Critical and High risks for status updates | Risk owners |
| 20-35 min | Assess new risks identified since last review | Security Champion |
| 35-50 min | Review mitigation action progress and overdue items | Engineering Lead |
| 50-55 min | Re-assess risk scores based on new information | All |
| 55-60 min | Assign new action items and set next review date | Engineering Lead |

### 10.3 Quarterly Risk Audit

The quarterly audit is a comprehensive review:

1. **Full risk register review:** Every open risk is re-assessed for current likelihood and impact.
2. **Closed risk verification:** Verify that mitigated risks have not recurred.
3. **Trend analysis:** Compare risk counts and severity trends over the past quarter.
4. **Mitigation effectiveness:** Evaluate whether implemented mitigations are working as expected.
5. **New risk identification:** Conduct a fresh threat modeling exercise for areas that have changed.
6. **Risk appetite review:** Re-confirm the team's risk appetite and tolerance thresholds.
7. **Framework update:** Update this risk management framework if the team's context has changed.
8. **Reporting:** Produce a quarterly risk report for stakeholders.

### 10.4 Risk Review Meeting Rules

- Risk reviews are blameless. The goal is to identify and address risks, not assign blame.
- Every risk must have an owner. Unowned risks are escalated to the Engineering Lead.
- Mitigation deadlines are commitments. Overdue mitigations are reviewed in every subsequent meeting.
- Risk scores can change in either direction. Risks may be re-assessed upward or downward.
- Accepted risks must be explicitly documented with the rationale for acceptance.
- The risk register is the single source of truth. Verbal risk discussions must be followed by register updates.

---

## Appendix A: Risk Assessment Worksheet

Use this worksheet when assessing a new risk:

```
Risk Title: ________________________________
Risk ID: _______
Identified by: _____________________________
Date identified: ___________________________

Category: [ ] Technical  [ ] Security  [ ] Operational  [ ] Strategic
Sub-category: ______________________________

Description:
____________________________________________________________
____________________________________________________________

Triggers (what could cause this risk to materialize):
1. ______________________________
2. ______________________________
3. ______________________________

Impact if materialized:
____________________________________________________________

Affected components:
____________________________________________________________

Likelihood (1-5): _____
Justification for likelihood: _________________________________

Impact (1-5): _____
Justification for impact: _________________________________

Risk Score: _____ × _____ = _____
Severity: [ ] Critical  [ ] High  [ ] Medium  [ ] Low

Mitigation Strategy: [ ] Avoid  [ ] Mitigate  [ ] Transfer  [ ] Accept  [ ] Monitor

Mitigation Actions:
1. ______________________________
2. ______________________________
3. ______________________________

Mitigation Deadline: ______________________________
Owner: ______________________________
```

---

## Appendix B: Risk Severity Quick Reference

| Score | Severity | Action Required | Review Frequency |
|---|---|---|---|
| 15-25 | **Critical** | Immediate action. Escalate to leadership. | Daily until mitigated |
| 10-14 | **High** | Mitigation plan within 1 week. Assigned owner. | Weekly |
| 5-9 | **Medium** | Mitigation plan within 1 sprint. Monitored. | Bi-weekly |
| 1-4 | **Low** | Accepted or monitored. No immediate action. | Monthly |

---

## Appendix C: Risk Communication Templates

### New Risk Notification

```
NEW RISK IDENTIFIED: {Risk ID} - {Title}

Severity: {Critical/High/Medium/Low}
Category: {Technical/Security/Operational}
Owner: {Name}

Description: {Brief description}

Impact: {What could happen if this risk materializes}

Mitigation Plan: {Planned actions and timeline}

Tracked in: risk-register.yaml
```

### Mitigation Overdue Alert

```
RISK MITIGATION OVERDUE: {Risk ID} - {Title}

Severity: {Severity}
Owner: {Name}
Original Deadline: {Date}
Days Overdue: {Number}

Status: {Current status of mitigation}

Required Action: {What needs to happen to get back on track}

Please update the risk register with current status.
```

---

*This document is a living artifact. Propose changes via PR to the repository. All changes require approval from the Engineering Lead and Security Champion. Risk register updates may be made by any engineer and reviewed in the next risk review meeting.*
