# ADR Lifecycle Management

> **Purpose**: Define the complete lifecycle of Architecture Decision Records, including all states, transitions, and escalation procedures.

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. State Definitions](#2-state-definitions)
- [3. State Transitions](#3-state-transitions)
- [4. Time Limits](#4-time-limits)
- [5. Escalation Procedures](#5-escalation-procedures)
- [6. Emergency ADR Process](#6-emergency-adr-process)
- [7. Status Tracking](#7-status-tracking)

---

## 1. Overview

### 1.1 Purpose

The ADR lifecycle defines how Architecture Decision Records move from initial proposal to final archival. It ensures:

- **Consistency**: All ADRs follow the same process
- **Quality**: ADRs are reviewed and validated before implementation
- **Traceability**: Every state change is recorded
- **Accountability**: Clear ownership at each stage
- **Timeliness**: ADRs don't get stuck in any state

### 1.2 Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ADR LIFECYCLE                                      │
│                                                                             │
│  ┌──────────┐    ┌───────┐    ┌─────────────┐    ┌──────────┐              │
│  │ Proposed │ →  │ Draft │ →  │ Under Review│ →  │ Approved │              │
│  └──────────┘    └───────┘    └─────────────┘    └──────────┘              │
│       │              │              │                   │                   │
│       │              │              │                   ↓                   │
│       │              │              │            ┌───────────┐              │
│       │              │              │            │ Accepted  │              │
│       │              │              │            └───────────┘              │
│       │              │              │                   │                   │
│       │              │              │                   ↓                   │
│       │              │              │            ┌────────────┐             │
│       │              │              │            │ Implemented│             │
│       │              │              │            └────────────┘             │
│       │              │              │                   │                   │
│       │              │              │                   ↓                   │
│       │              │              │            ┌────────────┐             │
│       │              │              │            │ Validated  │             │
│       │              │              │            └────────────┘             │
│       │              │              │                   │                   │
│       │              │              │                   ↓                   │
│       │              │              │            ┌────────────┐             │
│       │              │              │            │ Archived   │             │
│       │              │              │            └────────────┘             │
│       │              │              │                                       │
│       ↓              ↓              ↓                                       │
│  ┌────────────┐ ┌───────────┐ ┌─────────────┐                              │
│  │ Deprecated │ │Deprecated │ │ Superseded  │                              │
│  └────────────┘ └───────────┘ └─────────────┘                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 State Summary

| State | Description | Duration | Next States |
|-------|-------------|----------|-------------|
| `Proposed` | Idea submitted | 0-7 days | `Draft`, `Deprecated` |
| `Draft` | Actively written | 1-14 days | `Under Review`, `Deprecated` |
| `Under Review` | Awaiting review | 1-10 days | `Approved`, `Draft`, `Deprecated` |
| `Approved` | Approved for implementation | 1-30 days | `Accepted`, `Superseded` |
| `Accepted` | Ready for implementation | 1-60 days | `Implemented`, `Superseded` |
| `Implemented` | Code complete | 1-14 days | `Validated`, `Superseded` |
| `Validated` | Verified in staging | 1-30 days | `Archived`, `Superseded` |
| `Superseded` | Replaced by newer ADR | N/A | `Archived` |
| `Deprecated` | No longer applicable | N/A | `Archived` |
| `Archived` | Final resting state | Permanent | None |

---

## 2. State Definitions

### 2.1 Proposed

**Definition**: An ADR idea has been submitted but not yet formalized.

**Characteristics**:

- Issue created in GitHub with label `adr-proposal`
- ADR number may or may not be assigned
- Author identified
- High-level problem description available
- No formal template used yet

**Entry criteria**:

- Team member identifies significant architectural decision
- Decision meets ADR criteria (see `ADR_GOVERNANCE.md`)
- Issue is created and triaged

**Exit criteria**:

- ADR number assigned
- Author committed to writing draft
- Initial problem statement drafted

**Owner**: ADR Author

**Typical duration**: 0-7 days

**Allowed transitions**:

- → `Draft`: Author begins writing
- → `Deprecated`: Idea rejected after triage

---

### 2.2 Draft

**Definition**: ADR is being actively written using the standard template.

**Characteristics**:

- ADR file created with template
- Required sections being filled in
- At least 1 option documented
- Peer feedback being incorporated
- Work in progress

**Entry criteria**:

- ADR number assigned
- Author committed to writing
- Template copied and ready

**Exit criteria**:

- All required sections completed
- At least 3 options documented
- Security impact assessed
- Accessibility impact assessed
- Author believes it's ready for review

**Owner**: ADR Author

**Typical duration**: 1-14 days

**Allowed transitions**:

- → `Under Review`: Author submits for review
- → `Deprecated`: Author abandons or idea becomes obsolete

---

### 2.3 Under Review

**Definition**: ADR is complete and awaiting formal review by designated reviewers.

**Characteristics**:

- All sections filled in
- Reviewers assigned
- PR created for review
- Feedback being collected
- Iterating on feedback

**Entry criteria**:

- Draft complete
- All required sections filled
- PR created
- Reviewers assigned

**Exit criteria**:

- All reviewers approved
- All feedback addressed
- No blocking objections
- PR ready to merge

**Owner**: ADR Reviewer

**Typical duration**: 1-10 days

**Allowed transitions**:

- → `Approved`: All reviewers approved
- → `Draft`: Significant changes needed
- → `Deprecated`: Idea rejected during review

---

### 2.4 Approved

**Definition**: ADR has been formally approved by designated approvers.

**Characteristics**:

- All approvers signed off
- PR merged to main branch
- Team notified of approval
- Implementation plan being created
- Tasks being assigned

**Entry criteria**:

- All reviewers approved
- PR merged
- Team notified

**Exit criteria**:

- Implementation plan created
- Tasks assigned
- Team ready to begin implementation

**Owner**: ADR Approver

**Typical duration**: 1-30 days

**Allowed transitions**:

- → `Accepted`: Implementation plan approved
- → `Superseded`: Replaced by newer ADR

---

### 2.5 Accepted

**Definition**: ADR is accepted and ready for implementation.

**Characteristics**:

- Implementation plan approved
- Tasks assigned to team members
- Implementation about to begin
- Team aligned on approach

**Entry criteria**:

- Implementation plan approved
- Tasks assigned
- Team ready

**Exit criteria**:

- Implementation started
- First code changes committed

**Owner**: ADR Author

**Typical duration**: 1-60 days

**Allowed transitions**:

- → `Implemented`: Implementation complete
- → `Superseded`: Replaced by newer ADR

---

### 2.6 Implemented

**Definition**: Implementation is complete and code has been merged.

**Characteristics**:

- All code changes committed
- All tests passing
- Code review approved
- Deployed to staging
- Documentation updated

**Entry criteria**:

- All code changes complete
- All tests passing
- Code review approved

**Exit criteria**:

- Deployed to staging
- Validation tests running
- Team confident in implementation

**Owner**: ADR Author

**Typical duration**: 1-14 days

**Allowed transitions**:

- → `Validated`: Validation tests pass
- → `Superseded`: Replaced by newer ADR
- → `Draft`: Implementation issues discovered

---

### 2.7 Validated

**Definition**: Implementation has been verified and validated in staging.

**Characteristics**:

- All validation tests pass
- Accessibility audit passed
- Security review approved
- Performance benchmarks met
- Ready for production

**Entry criteria**:

- Deployed to staging
- Validation tests running
- Audit requests submitted

**Exit criteria**:

- All validation tests pass
- All audits passed
- Production deployment approved

**Owner**: ADR Governor

**Typical duration**: 1-30 days

**Allowed transitions**:

- → `Archived`: Production deployment successful
- → `Superseded`: Replaced by newer ADR
- → `Implemented`: Validation issues discovered

---

### 2.8 Superseded

**Definition**: ADR has been replaced by a newer ADR.

**Characteristics**:

- New ADR created and approved
- Old ADR marked as superseded
- References updated
- Team trained on changes

**Entry criteria**:

- New ADR approved
- Supersession notice added
- References migrated

**Exit criteria**:

- All references updated
- Team trained
- 6 months elapsed

**Owner**: ADR Governor

**Typical duration**: 6 months minimum

**Allowed transitions**:

- → `Archived`: After retention period

---

### 2.9 Deprecated

**Definition**: ADR is no longer applicable but kept for reference.

**Characteristics**:

- Decision no longer relevant
- Technology deprecated
- Problem no longer exists
- Better solution found

**Entry criteria**:

- Deprecation approved
- Deprecation notice added
- Impact assessed

**Exit criteria**:

- 6 months elapsed
- All references removed
- Archive criteria met

**Owner**: ADR Governor

**Typical duration**: 6 months minimum

**Allowed transitions**:

- → `Archived`: After retention period

---

### 2.10 Archived

**Definition**: ADR is in its final resting state, read-only.

**Characteristics**:

- Immutable record
- Checksummed for integrity
- Backed up to remote storage
- Read-only access
- Permanent retention

**Entry criteria**:

- All retention requirements met
- Archive criteria verified
- Checksum generated
- Backup completed

**Exit criteria**: None (permanent state)

**Owner**: ADR Archivist

**Typical duration**: Permanent

**Allowed transitions**: None

---

## 3. State Transitions

### 3.1 Allowed Transitions

| From | To | Trigger | Approver |
|------|----|---------|----------|
| `Proposed` | `Draft` | Author begins writing | ADR Author |
| `Proposed` | `Deprecated` | Idea rejected | ADR Governor |
| `Draft` | `Under Review` | Author submits for review | ADR Author |
| `Draft` | `Deprecated` | Author abandons | ADR Governor |
| `Under Review` | `Approved` | All reviewers approve | ADR Approver |
| `Under Review` | `Draft` | Significant changes needed | ADR Reviewer |
| `Under Review` | `Deprecated` | Idea rejected during review | ADR Governor |
| `Approved` | `Accepted` | Implementation plan approved | ADR Approver |
| `Approved` | `Superseded` | Replaced by newer ADR | ADR Governor |
| `Accepted` | `Implemented` | Implementation complete | ADR Author |
| `Accepted` | `Superseded` | Replaced by newer ADR | ADR Governor |
| `Implemented` | `Validated` | Validation tests pass | ADR Governor |
| `Implemented` | `Superseded` | Replaced by newer ADR | ADR Governor |
| `Implemented` | `Draft` | Implementation issues discovered | ADR Author |
| `Validated` | `Archived` | Production deployment successful | ADR Archivist |
| `Validated` | `Superseded` | Replaced by newer ADR | ADR Governor |
| `Validated` | `Implemented` | Validation issues discovered | ADR Author |
| `Superseded` | `Archived` | Retention period elapsed | ADR Archivist |
| `Deprecated` | `Archived` | Retention period elapsed | ADR Archivist |

### 3.2 Blocked Transitions

The following transitions are NOT allowed:

| From | To | Reason |
|------|----|--------|
| `Proposed` | `Approved` | Must go through review |
| `Proposed` | `Implemented` | Must go through full lifecycle |
| `Draft` | `Approved` | Must go through review |
| `Draft` | `Implemented` | Must go through full lifecycle |
| `Under Review` | `Implemented` | Must go through approval |
| `Approved` | `Implemented` | Must go through acceptance |
| `Approved` | `Validated` | Must go through implementation |
| `Accepted` | `Validated` | Must go through implementation |
| `Accepted` | `Archived` | Must go through implementation |
| `Implemented` | `Archived` | Must go through validation |
| `Superseded` | `Proposed` | Cannot reuse superseded ADR |
| `Deprecated` | `Proposed` | Cannot reuse deprecated ADR |
| `Archived` | Any | Archived is permanent |

### 3.3 Transition Rules

1. **Forward-only by default**: ADRs move forward through the lifecycle
2. **Backward with approval**: Moving backward requires ADR Governor approval
3. **No skipping**: Cannot skip states (except emergency process)
4. **No reuse**: Superseded/Deprecated ADRs cannot be reused
5. **Immutable archive**: Archived ADRs cannot be modified

---

## 4. Time Limits

### 4.1 Maximum Duration per State

| State | Maximum Duration | Escalation |
|-------|-----------------|------------|
| `Proposed` | 7 days | Auto-assign author |
| `Draft` | 14 days | Check-in with author |
| `Under Review` | 10 days | Escalate to ADR Governor |
| `Approved` | 30 days | Check-in with team |
| `Accepted` | 60 days | Review for relevance |
| `Implemented` | 14 days | Verify validation setup |
| `Validated` | 30 days | Escalate to production |
| `Superseded` | 6 months | Review for archive |
| `Deprecated` | 6 months | Review for archive |

### 4.2 Minimum Duration per State

| State | Minimum Duration | Reason |
|-------|-----------------|--------|
| `Proposed` | 0 days | Can move immediately |
| `Draft` | 1 day | Ensure quality |
| `Under Review` | 1 day | Ensure thorough review |
| `Approved` | 1 day | Allow team notification |
| `Accepted` | 1 day | Ensure readiness |
| `Implemented` | 1 day | Ensure implementation is stable |
| `Validated` | 1 day | Ensure validation is complete |
| `Superseded` | 6 months | Retention for reference |
| `Deprecated` | 6 months | Retention for reference |
| `Archived` | Permanent | Never deleted |

### 4.3 Time Tracking

Time is tracked from:

- **Entry**: When status changes to the state
- **Exit**: When status changes from the state
- **Duration**: Exit time minus entry time

All time tracking is recorded in the ADR revision history.

---

## 5. Escalation Procedures

### 5.1 Escalation Triggers

| Trigger | Condition | Action |
|---------|-----------|--------|
| **Stale ADR** | ADR exceeds maximum duration | Notify ADR Governor |
| **Blocked ADR** | ADR waiting on external dependency | Escalate to Tech Lead |
| **Conflicting ADRs** | Two ADRs make conflicting decisions | Escalate to Architecture Board |
| **Rejection** | ADR rejected by reviewer | ADR Governor mediates |
| **Abandoned ADR** | Author unresponsive for 7+ days | ADR Governor reassigns |

### 5.2 Escalation Levels

| Level | Trigger | Escalated To | Response Time |
|-------|---------|--------------|---------------|
| Level 1 | 1-3 days overdue | ADR Author | 24 hours |
| Level 2 | 3-7 days overdue | ADR Reviewer | 48 hours |
| Level 3 | 7-14 days overdue | ADR Governor | 48 hours |
| Level 4 | 14+ days overdue | Tech Lead | 24 hours |
| Level 5 | Critical conflict | Architecture Board | 24 hours |

### 5.3 Escalation Process

1. **Detect**: Automated or manual detection of escalation trigger
2. **Notify**: Notify appropriate parties
3. **Respond**: Escalated party responds within time limit
4. **Resolve**: Issue resolved or further escalated
5. **Document**: Resolution documented in ADR

### 5.4 Escalation Communication

Escalation notifications include:

- ADR number and title
- Current status and duration
- Escalation reason
- Expected action
- Deadline for response

---

## 6. Emergency ADR Process

### 6.1 When to Use Emergency Process

The emergency ADR process is for:

- **Critical security vulnerabilities** requiring immediate architecture changes
- **Production incidents** requiring architectural decisions
- **Regulatory deadlines** requiring immediate compliance
- **External vendor failures** requiring immediate alternative

### 6.2 Emergency Process Steps

1. **Identify emergency**:
   - Author identifies emergency
   - Creates issue with label `adr-emergency`
   - Documents emergency justification

2. **Fast-track approval**:
   - Tech Lead approves emergency process
   - ADR Governor assigns expedited reviewers
   - Reviewers respond within 4 hours

3. **Rapid ADR creation**:
   - Author creates ADR using abbreviated template
   - Focus on critical sections only
   - Skip non-essential sections

4. **Expedited review**:
   - Single reviewer approval required
   - Review completed within 8 hours
   - Approval documented in issue

5. **Immediate implementation**:
   - Implementation begins immediately
   - ADR completed post-implementation
   - Full review completed within 5 business days

### 6.3 Emergency Template

Emergency ADRs use abbreviated template:

```markdown
# ADR-XXX: [Title]

## Status
Emergency

## Problem Statement
[Critical problem requiring immediate decision]

## Decision
[Decision made]

## Rationale
[Why this decision]

## Next Steps
[Immediate actions required]

## Post-Emergency Review
[Full ADR to be completed within 5 business days]
```

### 6.4 Post-Emergency Review

Within 5 business days of emergency resolution:

1. Complete full ADR using standard template
2. Document emergency decision in full context
3. Update revision history with emergency timeline
4. Conduct lessons learned review
5. Update emergency process if needed

---

## 7. Status Tracking

### 7.1 Tracking Mechanisms

| Mechanism | Purpose | Location |
|-----------|---------|----------|
| **ADR Files** | Primary record | `docs/adr/` |
| **GitHub Issues** | Proposal tracking | GitHub Issues |
| **GitHub PRs** | Review tracking | GitHub PRs |
| **ADR Index** | Status overview | `docs/architecture/DECISIONS.md` |
| **Dashboard** | Real-time status | ADR Dashboard |

### 7.2 Status Updates

Status is updated when:

- **State changes**: Update ADR file status field
- **Transitions**: Update revision history
- **Reviews**: Record reviewer actions
- **Approvals**: Record approver decisions
- **Implementation**: Record implementation progress

### 7.3 Status Reporting

Weekly status report includes:

- Total ADRs by status
- New ADRs this week
- ADRs stuck in any state
- Upcoming reviews
- Escalated ADRs

### 7.4 Status Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Cycle time** | Time from proposal to archive | < 90 days |
| **Review time** | Time in Under Review state | < 5 days |
| **Approval rate** | Percentage approved on first review | > 80% |
| **Stale rate** | Percentage exceeding time limits | < 10% |
| **Escalation rate** | Percentage requiring escalation | < 5% |

### 7.5 Status Dashboard

The ADR dashboard displays:

```
┌─────────────────────────────────────────────────────────────┐
│                    ADR STATUS DASHBOARD                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Proposed:    ████████░░░░░░░░░░░░  2                      │
│  Draft:       ████████████░░░░░░░░  3                      │
│  Under Review: ██████░░░░░░░░░░░░░░  1                      │
│  Approved:    ████████░░░░░░░░░░░░  2                      │
│  Accepted:    ████████████░░░░░░░░  3                      │
│  Implemented: ████████████████████  5                      │
│  Validated:   ██████████████████░░  4                      │
│  Superseded:  ████░░░░░░░░░░░░░░░░  1                      │
│  Deprecated:  ██░░░░░░░░░░░░░░░░░░  0                      │
│  Archived:    ████████████████░░░░  3                      │
│                                                             │
│  Total ADRs: 24                                             │
│  Active: 16  |  Inactive: 8                                 │
│                                                             │
│  Stale: 1 (overdue)  |  Escalated: 0                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Appendix A: State Transition Checklist

Before transitioning an ADR, verify:

- [ ] All exit criteria for current state are met
- [ ] All entry criteria for next state are met
- [ ] Transition is allowed per transition rules
- [ ] Approvers have authorized the transition
- [ ] ADR file is updated with new status
- [ ] Revision history is updated
- [ ] All references are updated
- [ ] Team is notified of transition

## Appendix B: Status Field Values

Use these exact values in the ADR status field:

```
Proposed
Draft
Under Review
Approved
Accepted
Implemented
Validated
Superseded
Deprecated
Archived
Emergency
```

---

*Lifecycle version: 1.0.0*
*Last updated: 2026-07-19*
*Next review: 2026-10-19*
