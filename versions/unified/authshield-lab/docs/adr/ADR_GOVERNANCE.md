# ADR Governance Framework

> **Purpose**: Establish clear rules and processes for managing Architecture Decision Records (ADRs) in AuthShield Lab.

---

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Scope](#2-scope)
- [3. Ownership Model](#3-ownership-model)
- [4. Approval Workflow](#4-approval-workflow)
- [5. Review Cycle](#5-review-cycle)
- [6. Change Management](#6-change-management)
- [7. Retirement Process](#7-retirement-process)
- [8. Supersession Process](#8-supersession-process)
- [9. Archiving Policy](#9-archiving-policy)
- [10. Quality Criteria](#10-quality-criteria)

---

## 1. Purpose

### 1.1 Why ADRs Matter

Architecture Decision Records serve as the institutional memory of technical decisions in AuthShield Lab. They:

- **Capture context** that would otherwise be lost when team members leave
- **Prevent revisiting** decisions without new information
- **Provide rationale** for why specific technologies and patterns were chosen
- **Enable onboarding** by giving new team members decision context
- **Support accountability** by recording who approved what and when
- **Reduce technical debt** by making the cost of changes explicit

### 1.2 Scope of ADRs

ADRs are required for decisions that meet ALL of the following criteria:

| Criterion | Description |
|-----------|-------------|
| **Architectural significance** | Affects system structure, patterns, or principles |
| **Long-term impact** | Effects persist beyond a single sprint |
| **Reversibility cost** | Changing the decision later is expensive |
| **Cross-cutting concern** | Affects multiple modules or teams |
| **Technology selection** | Choosing frameworks, libraries, or infrastructure |

### 1.3 When ADRs Are NOT Required

- Implementation details within a single module
- Bug fixes or patches
- Refactoring that doesn't change architecture
- Configuration changes
- Documentation updates
- Temporary workarounds (use TODO comments instead)

---

## 2. Ownership Model

### 2.1 Roles and Responsibilities

| Role | Responsibilities | Who |
|------|-----------------|-----|
| **ADR Author** | Create, maintain, and update ADRs | Any team member |
| **ADR Reviewer** | Review ADRs for completeness and accuracy | Senior engineers, architects |
| **ADR Approver** | Formally approve ADRs for implementation | Tech leads, architecture board |
| **ADR Governor** | Enforce governance rules, manage lifecycle | Architecture lead |
| **ADR Archivist** | Manage archival and retention | DevOps, documentation lead |

### 2.2 ADR Author

**Who can create ADRs**: Any team member with write access to the repository.

**Responsibilities**:

- Create ADRs using the standard template (`docs/adr/ADR_TEMPLATE.md`)
- Fill in all required sections completely
- Respond to reviewer feedback promptly
- Update ADR status through the lifecycle
- Maintain the ADR after implementation

**Quality standards**:

- Must be written in clear, concise English
- Must include at least 3 considered options
- Must address all non-functional requirements
- Must include security and accessibility impact assessments

### 2.3 ADR Reviewer

**Who can review ADRs**: Senior engineers, architects, and domain experts.

**Responsibilities**:

- Review ADRs within 5 business days
- Check for completeness against quality criteria
- Verify technical accuracy
- Assess risk and mitigation strategies
- Provide constructive feedback
- Approve or request changes

**Review criteria**:

- Is the problem statement clear?
- Are all requirements documented?
- Are at least 3 options considered?
- Are trade-offs explicitly stated?
- Are security impacts assessed?
- Are accessibility impacts assessed?

### 2.4 ADR Approver

**Who can approve ADRs**: Tech leads and architecture board members.

**Responsibilities**:

- Make final approval decisions
- Ensure alignment with project vision
- Resolve disagreements between reviewers
- Sign off on ADR implementation plan
- Verify implementation matches ADR

**Approval authority**:

| ADR Category | Required Approvers |
|-------------|-------------------|
| Architecture | Tech Lead + 1 Architect |
| Security | Tech Lead + Security Lead |
| Technology | Tech Lead + Domain Expert |
| API Design | API Lead + Tech Lead |
| Database | DBA + Tech Lead |

### 2.5 ADR Governor

**Who**: Architecture lead (single point of responsibility).

**Responsibilities**:

- Enforce governance rules consistently
- Manage ADR lifecycle transitions
- Escalate stuck ADRs
- Maintain the ADR backlog
- Report on ADR health metrics
- Resolve governance conflicts

### 2.6 ADR Archivist

**Who**: DevOps or documentation lead.

**Responsibilities**:

- Move completed ADRs to archive
- Maintain archive integrity
- Generate reports on archived ADRs
- Ensure backup and recovery of ADRs
- Manage ADR search indices

---

## 3. Approval Workflow

### 3.1 Workflow Stages

```
┌─────────┐    ┌───────┐    ┌─────────────┐    ┌──────────┐    ┌───────────┐    ┌────────────┐
│ Proposal │ →  │ Draft │ →  │ Under Review│ →  │ Approved │ →  │ Accepted  │ →  │Implemented │
└─────────┘    └───────┘    └─────────────┘    └──────────┘    └───────────┘    └────────────┘
```

### 3.2 Stage Details

#### Stage 1: Proposal

**Trigger**: Team member identifies a significant architectural decision.

**Actions**:

1. Create issue in GitHub with label `adr-proposal`
2. Use the proposal template in the issue
3. Assign to ADR Governor for triage
4. Governor assigns ADR number if accepted

**Exit criteria**:

- Issue created and triaged
- ADR number assigned
- Author identified

#### Stage 2: Draft

**Trigger**: ADR number assigned.

**Actions**:

1. Create ADR file using template (`docs/adr/ADR_TEMPLATE.md`)
2. Fill in all required sections
3. Set status to `Draft`
4. Commit to feature branch
5. Request initial peer review

**Exit criteria**:

- All required sections completed
- At least 3 options documented
- Security impact assessed
- Accessibility impact assessed
- Peer review completed

#### Stage 3: Under Review

**Trigger**: Draft complete, ready for formal review.

**Actions**:

1. Update status to `Under Review`
2. Create PR with ADR changes
3. Assign reviewers based on ADR category
4. Address reviewer feedback
5. Iterate until all reviewers approve

**Exit criteria**:

- All reviewers approved
- All feedback addressed
- No blocking objections
- PR ready to merge

#### Stage 4: Approved

**Trigger**: All reviewers approved.

**Actions**:

1. Merge PR to main branch
2. Update status to `Approved`
3. Notify team of approval
4. Create implementation plan
5. Assign implementation tasks

**Exit criteria**:

- PR merged
- Team notified
- Implementation plan created
- Tasks assigned

#### Stage 5: Accepted

**Trigger**: Implementation plan approved.

**Actions**:

1. Update status to `Accepted`
2. Begin implementation
3. Track progress against plan
4. Update ADR as implementation progresses

**Exit criteria**:

- Implementation started
- Progress tracking active
- Regular updates to ADR

#### Stage 6: Implemented

**Trigger**: Implementation complete.

**Actions**:

1. Update status to `Implemented`
2. Create PR with implementation changes
3. Request code review
4. Verify tests pass
5. Deploy to staging

**Exit criteria**:

- Code complete
- All tests passing
- Code review approved
- Deployed to staging

#### Stage 7: Validated

**Trigger**: Implementation verified in staging.

**Actions**:

1. Run validation tests
2. Conduct accessibility audit
3. Perform security review
4. Update status to `Validated`
5. Deploy to production
6. Update ADR with final implementation details

**Exit criteria**:

- All validation tests pass
- Accessibility audit passed
- Security review approved
- Production deployment successful
- ADR fully documented

---

## 4. Review Cycle

### 4.1 Quarterly Review

**Frequency**: Every quarter (Q1, Q2, Q3, Q4).

**Scope**: All ADRs in `Approved`, `Accepted`, or `Implemented` status.

**Process**:

1. **Preparation** (Week 1):
   - Generate list of all active ADRs
   - Identify ADRs not reviewed in 6+ months
   - Prepare review agenda

2. **Review** (Week 2):
   - Review each ADR for relevance
   - Check if assumptions still hold
   - Verify implementation matches ADR
   - Identify superseded ADRs
   - Update status as needed

3. **Cleanup** (Week 3):
   - Archive completed ADRs
   - Deprecate obsolete ADRs
   - Update related ADRs
   - Generate review report

4. **Reporting** (Week 4):
   - Publish quarterly ADR report
   - Update ADR metrics dashboard
   - Share findings with team

### 4.2 Review Checklist

During quarterly review, verify each ADR:

- [ ] Is the problem statement still accurate?
- [ ] Are all assumptions still valid?
- [ ] Are all constraints still applicable?
- [ ] Does the implementation match the ADR?
- [ ] Are there new options that should be considered?
- [ ] Is the ADR still relevant to the project?
- [ ] Has the technology landscape changed?
- [ ] Are there new security concerns?
- [ ] Are there new accessibility requirements?
- [ ] Is the ADR still being followed?

### 4.3 Trigger-Based Review

ADRs may be reviewed outside the quarterly cycle when:

- A security vulnerability is discovered
- A technology dependency is deprecated
- A regulatory requirement changes
- A major incident occurs
- A new team lead or architect joins
- A significant refactor is planned

---

## 5. Change Management

### 5.1 Minor Changes

**Definition**: Corrections, clarifications, or formatting that don't change the decision.

**Process**:

1. Create PR with changes
2. Self-approve if author is a reviewer
3. Merge immediately if no objections within 24 hours
4. Update revision history

**Examples**:

- Fixing typos
- Clarifying ambiguous language
- Adding missing references
- Updating formatting

### 5.2 Moderate Changes

**Definition**: Changes that add context or expand on the decision without changing it.

**Process**:

1. Create PR with changes
2. Request review from original approvers
3. Address feedback
4. Merge after approval
5. Update revision history

**Examples**:

- Adding new considerations
- Expanding risk analysis
- Updating assumptions
- Adding related ADRs

### 5.3 Major Changes

**Definition**: Changes that alter the decision, requirements, or implementation strategy.

**Process**:

1. Create new ADR (don't modify existing)
2. Mark old ADR as `Superseded`
3. Follow full approval workflow for new ADR
4. Update all related ADRs
5. Notify team of decision change

**Examples**:

- Changing the chosen option
- Modifying requirements
- Altering the implementation approach
- Reversing the decision entirely

---

## 6. Retirement Process

### 6.1 Deprecation Criteria

An ADR should be deprecated when:

- The technology is no longer maintained
- The problem is no longer relevant
- A better solution exists
- The assumption was wrong
- The constraint no longer applies

### 6.2 Deprecation Process

1. **Propose deprecation**:
   - Create issue with label `adr-deprecation`
   - Explain why ADR should be deprecated
   - Link to superseding ADR if applicable

2. **Review deprecation**:
   - ADR Governor reviews proposal
   - Original approvers are notified
   - Team discusses deprecation

3. **Execute deprecation**:
   - Update ADR status to `Deprecated`
   - Add deprecation notice at top
   - Link to superseding ADR
   - Update ADR index

4. **Communicate deprecation**:
   - Announce in team channels
   - Update documentation
   - Train team on changes

### 6.3 Archive Criteria

An ADR should be archived when:

- It has been deprecated for 6+ months
- It is no longer referenced by any active code
- All related ADRs have been updated
- The team has acknowledged the change

### 6.4 Archive Process

1. Verify archive criteria met
2. Update status to `Archived`
3. Move to archive directory
4. Update ADR index
5. Generate archive report

---

## 7. Supersession Process

### 7.1 When to Supersede

An ADR should be superseded when:

- A better option exists that wasn't available before
- Requirements have changed significantly
- New information invalidates the original decision
- The original ADR was incorrect

### 7.2 Supersession Process

1. **Create new ADR**:
   - Use fresh template
   - Reference old ADR
   - Explain why supersession is needed

2. **Mark old ADR**:
   - Update status to `Superseded`
   - Add supersession notice
   - Link to new ADR
   - Preserve all historical content

3. **Migrate references**:
   - Update all ADRs referencing old ADR
   - Update documentation
   - Update code comments
   - Update implementation plans

4. **Validate transition**:
   - Verify no active code depends on old ADR
   - Verify new ADR is implemented
   - Verify team is trained

### 7.3 Supersession Notice Format

```markdown
> **SUPERSEDED BY**: ADR-XXX: [New ADR Title]
> **Superseded on**: YYYY-MM-DD
> **Reason**: [Brief reason for supersession]
```

---

## 8. Archiving Policy

### 8.1 Archive Storage

- Archived ADRs are stored in `docs/adr/archive/`
- Archive is version-controlled via git
- Archive is backed up to remote storage
- Archive is immutable (no modifications after archiving)

### 8.2 Retention Period

| ADR Status | Retention Period | Action After |
|-----------|-----------------|--------------|
| `Validated` | 3 years | Review for archive |
| `Implemented` | 2 years | Review for archive |
| `Accepted` | 1 year | Review for deprecation |
| `Approved` | 6 months | Review for status |
| `Deprecated` | 6 months | Review for archive |
| `Superseded` | 1 year | Review for archive |

### 8.3 Archive Integrity

- All archived ADRs are checksummed
- Checksums are stored in `docs/adr/archive/CHECKSUMS.md`
- Checksums are verified quarterly
- Any integrity violation triggers immediate review

### 8.4 Archive Access

- Archived ADRs are read-only
- Access is granted via repository permissions
- Archive changes require governance board approval
- All archive access is logged

---

## 9. Quality Criteria

### 9.1 Mandatory Quality Criteria

Every ADR must meet these criteria to be approved:

| Criterion | Requirement | Verification |
|-----------|------------|--------------|
| Completeness | All required sections filled | Checklist |
| Clarity | Problem statement is clear | Peer review |
| Options | At least 3 options documented | Count |
| Trade-offs | Explicitly stated | Peer review |
| Security | Security impact assessed | Security review |
| Accessibility | Accessibility impact assessed | A11y review |
| Risks | Risks with mitigations | Peer review |
| References | Related ADRs linked | Link check |

### 9.2 Quality Scoring

Each ADR is scored on a 1-5 scale for each criterion:

| Score | Description |
|-------|-------------|
| 5 | Excellent - exceeds expectations |
| 4 | Good - meets all expectations |
| 3 | Acceptable - meets minimum requirements |
| 2 | Needs improvement - requires changes |
| 1 | Unacceptable - must be rewritten |

**Minimum average score for approval**: 3.5

### 9.3 Quality Metrics

Tracked metrics per ADR:

- Time from proposal to approval
- Number of review cycles
- Number of changes after approval
- Number of supersessions
- Implementation completeness
- Team satisfaction score

### 9.4 Quality Gates

| Gate | Criteria | Owner |
|------|----------|-------|
| Gate 1 | Template compliance | ADR Author |
| Gate 2 | Technical accuracy | ADR Reviewer |
| Gate 3 | Security review | Security Lead |
| Gate 4 | Accessibility review | A11y Lead |
| Gate 5 | Final approval | ADR Approver |

---

## 10. Enforcement

### 10.1 Compliance Monitoring

- ADR Governor monitors compliance weekly
- Non-compliant ADRs are flagged in PR reviews
- Compliance metrics are reported monthly

### 10.2 Non-Compliance Consequences

| Violation | Consequence |
|-----------|-------------|
| Missing ADR for architectural decision | Decision blocked until ADR created |
| Incomplete ADR | PR rejected until complete |
| Skipping approval process | Decision invalidated |
| Unauthorized modification | Change reverted |

### 10.3 Exceptions

Exceptions to governance rules require:

1. Written justification
2. Approval from ADR Governor
3. Approval from Tech Lead
4. Documentation in the ADR
5. Review at next quarterly review

---

## Appendix A: ADR Quick Reference

| Action | Process | Time |
|--------|---------|------|
| Create ADR | Use template, fill in sections | 1-2 days |
| Review ADR | Peer review, provide feedback | 3-5 days |
| Approve ADR | Reviewer approval, merge PR | 1-2 days |
| Modify ADR | Create PR, follow change management | 1-3 days |
| Deprecate ADR | Create issue, review, update status | 1-2 weeks |
| Archive ADR | Verify criteria, move to archive | 1 day |

## Appendix B: Contacts

| Role | Name | GitHub |
|------|------|--------|
| ADR Governor | [Name] | [@username] |
| ADR Archivist | [Name] | [@username] |
| Security Lead | [Name] | [@username] |
| A11y Lead | [Name] | [@username] |

---

*Governance version: 1.0.0*
*Last updated: 2026-07-19*
*Next review: 2026-10-19*
