# ADR Template

> **Usage**: Copy this template when creating a new Architecture Decision Record.
> Replace all placeholders with actual content. Delete optional sections if not applicable.
> Reference: `docs/adr/ADR_GOVERNANCE.md` for governance rules.

---

## ADR Number

**ADR-XXX**

> Sequential number assigned by the ADR automation tool or governance lead.
> Numbers are monotonically increasing and never reused.

---

## Title

**Short, Descriptive Title**

> Format: `[Action] [Subject] over [Alternative]` or `[Topic] Decision`
> Examples: "FastAPI over Django", "SQLite over PostgreSQL", "Localhost-Only Security Model"

---

## Status

**Proposed**

> Valid states and their definitions:

| State | Definition |
|-------|-----------|
| `Proposed` | Idea submitted, not yet a formal draft |
| `Draft` | Actively being written, incomplete |
| `Under Review` | Complete draft awaiting review |
| `Approved` | Approved by designated reviewers |
| `Accepted` | Accepted by team, ready for implementation |
| `Implemented` | Code changes completed |
| `Validated` | Implementation verified via tests/review |
| `Superseded` | Replaced by a newer ADR |
| `Deprecated` | No longer applicable but kept for reference |
| `Archived` | Final resting state, read-only |

> **State transitions**: See `docs/adr/ADR_LIFECYCLE.md` for allowed transitions.

---

## Date

**YYYY-MM-DD**

> ISO 8601 format. Date when this ADR was first proposed.

---

## Authors

| Name | Role | GitHub |
|------|------|--------|
| `@username` | `Role` | `github.com/username` |

> List all primary authors who contributed to this ADR.

---

## Reviewers

| Name | Role | GitHub | Review Date |
|------|------|--------|-------------|
| `@username` | `Role` | `github.com/username` | `YYYY-MM-DD` |

> List all reviewers who examined this ADR.

---

## Approvers

| Name | Role | GitHub | Approval Date | Method |
|------|------|--------|---------------|--------|
| `@username` | `Role` | `github.com/username` | `YYYY-MM-DD` | `PR Review / GPG Sign` |

> List all approvers. Approval method must be recorded.

---

## Decision Summary

> **1-2 sentence summary of the decision.**

In 1-2 sentences, state what was decided and why. This should be comprehensible without reading the full ADR.

Example: "We will use FastAPI for the backend API because it provides automatic OpenAPI documentation, native async support, and Pydantic validation, which align with our requirements for type safety and performance."

---

## Context

> **Background and situation that led to this decision.**

Describe the situation, problem, or opportunity that necessitated this decision. Include:

- Current state of the system
- Business drivers and goals
- Technical landscape
- Relevant constraints
- Timeline pressures

> **Write 3-8 paragraphs.** Be thorough but focused. Include only information relevant to this decision.

---

## Problem Statement

> **The specific problem being addressed.**

Define the problem in clear, unambiguous terms. Use the format:

```
[Actor] needs [Capability] so that [Benefit] despite [Constraint].
```

Example: "The development team needs a backend framework that provides automatic API documentation so that frontend integration is accelerated despite the constraint of maintaining a small engineering team."

---

## Requirements

### Functional Requirements

- [ ] `REQ-001`: Description of functional requirement 1
- [ ] `REQ-002`: Description of functional requirement 2
- [ ] `REQ-003`: Description of functional requirement 3

> List all functional requirements that influenced this decision.

### Non-Functional Requirements

| ID | Category | Requirement | Priority |
|----|----------|-------------|----------|
| `NFR-001` | Performance | Response time < 100ms | Must |
| `NFR-002` | Security | No external network calls | Must |
| `NFR-003` | Accessibility | WCAG 2.1 AA compliance | Must |
| `NFR-004` | Usability | Intuitive UI for security practitioners | Should |
| `NFR-005` | Maintainability | Low cognitive overhead | Should |

> Non-functional requirements are critical for evaluating trade-offs.

---

## Assumptions

> **Assumptions made during this decision process.**

1. The team has sufficient expertise in the chosen technologies
2. The existing infrastructure can support the chosen approach
3. The timeline allows for the implementation of the chosen option
4. Dependencies will remain available and maintained

> Document all assumptions. Invalid assumptions may invalidate the decision.

---

## Constraints

### Technical Constraints

- Must run on Windows, macOS, and Linux
- Must integrate with existing Python backend
- Must support offline operation

### Business Constraints

- Must be released within Q2 2026
- Must maintain backward compatibility with v1.x

### Regulatory Constraints

- Must comply with GDPR data handling requirements
- Must meet WCAG 2.1 AA accessibility standards

> List all constraints that influenced the decision.

---

## Considered Options

> **Minimum 3 options per ADR.** Document all serious alternatives.

### Option 1: [Name]

**Description**: Detailed description of this option.

| Criterion | Assessment |
|-----------|------------|
| Pros | List of advantages |
| Cons | List of disadvantages |
| Cost | Estimated cost/effort |
| Risk | Risk level and description |

### Option 2: [Name]

**Description**: Detailed description of this option.

| Criterion | Assessment |
|-----------|------------|
| Pros | List of advantages |
| Cons | List of disadvantages |
| Cost | Estimated cost/effort |
| Risk | Risk level and description |

### Option 3: [Name]

**Description**: Detailed description of this option.

| Criterion | Assessment |
|-----------|------------|
| Pros | List of advantages |
| Cons | List of disadvantages |
| Cost | Estimated cost/effort |
| Risk | Risk level and description |

> Include options that were seriously considered, even if not selected.
> Document why options were rejected.

---

## Decision

> **The actual decision made.**

State clearly what was decided. Use bold for the chosen option.

Example: **We chose Option 2: FastAPI** for the backend API framework.

---

## Rationale

> **Why this option was chosen over alternatives.**

Explain the reasoning behind the decision. Address:

- How each requirement is satisfied
- Why the chosen option's pros outweigh its cons
- Why rejected options were insufficient
- How the decision aligns with project goals

---

## Expected Benefits

- **Benefit 1**: Description of expected positive outcome
- **Benefit 2**: Description of expected positive outcome
- **Benefit 3**: Description of expected positive outcome

> List the benefits that motivated this decision.

---

## Trade-offs

| What We Gain | What We Lose |
|-------------|-------------|
| Benefit A | Trade-off A |
| Benefit B | Trade-off B |
| Benefit C | Trade-off C |

> Be explicit about what we're giving up to gain something else.

---

## Risks

| Risk ID | Description | Probability | Impact | Severity |
|---------|-------------|-------------|--------|----------|
| `RISK-001` | Description of risk | Low/Med/High | Low/Med/High | Low/Med/High |
| `RISK-002` | Description of risk | Low/Med/High | Low/Med/High | Low/Med/High |
| `RISK-003` | Description of risk | Low/Med/High | Low/Med/High | Low/Med/High |

---

## Mitigations

| Risk ID | Mitigation Strategy | Owner | Status |
|---------|-------------------|-------|--------|
| `RISK-001` | Description of mitigation | `@owner` | `Pending/In Progress/Done` |
| `RISK-002` | Description of mitigation | `@owner` | `Pending/In Progress/Done` |
| `RISK-003` | Description of mitigation | `@owner` | `Pending/In Progress/Done` |

---

## Security Impact

> **How this decision affects the security posture.**

- **Positive security impacts**: [List]
- **Negative security impacts**: [List]
- **Security controls required**: [List]
- **Threat model changes**: [List]

---

## Accessibility Impact

> **How this decision affects accessibility.**

- **WCAG compliance**: [Impact assessment]
- **Screen reader support**: [Impact assessment]
- **Keyboard navigation**: [Impact assessment]
- **Color contrast**: [Impact assessment]
- **Required accommodations**: [List]

---

## Performance Impact

> **How this decision affects performance.**

- **Response time**: [Impact assessment]
- **Memory usage**: [Impact assessment]
- **CPU usage**: [Impact assessment]
- **Network usage**: [Impact assessment]
- **Storage**: [Impact assessment]

---

## Maintainability Impact

> **How this decision affects long-term maintenance.**

- **Code complexity**: [Impact assessment]
- **Team knowledge**: [Impact assessment]
- **Upgrade path**: [Impact assessment]
- **Documentation needs**: [Impact assessment]

---

## Testing Strategy

> **How this decision will be tested.**

- **Unit tests**: [Description]
- **Integration tests**: [Description]
- **E2E tests**: [Description]
- **Performance tests**: [Description]
- **Security tests**: [Description]
- **Accessibility tests**: [Description]

---

## Documentation Impact

> **Documentation that needs to be created or updated.**

- [ ] New documentation to create
- [ ] Existing documentation to update
- [ ] API documentation updates
- [ ] Architecture diagram updates
- [ ] User guide updates

---

## Migration Strategy

> **How to migrate from the current state to the decided state.**

1. Phase 1: [Description]
2. Phase 2: [Description]
3. Phase 3: [Description]

> If no migration needed, state "No migration required."

---

## Rollback Strategy

> **How to undo this decision if needed.**

- **Rollback trigger**: [Conditions that would trigger rollback]
- **Rollback process**: [Steps to execute rollback]
- **Rollback impact**: [What would be lost]
- **Data recovery**: [How to recover data]

---

## Dependencies

| Dependency | Type | Version | Impact if Unavailable |
|-----------|------|---------|----------------------|
| `dependency-1` | Internal/External | `v1.0.0` | Description of impact |
| `dependency-2` | Internal/External | `v1.0.0` | Description of impact |

---

## Related ADRs

| ADR | Relationship | Notes |
|-----|-------------|-------|
| `ADR-XXX` | Depends on / Supersedes / Relates to | Brief description |

---

## References

- [Reference 1](URL)
- [Reference 2](URL)
- [Internal Document](path/to/document)

---

## Revision History

| Date | Author | Change | Status |
|------|--------|--------|--------|
| `YYYY-MM-DD` | `@author` | Initial draft | `Proposed` |
| `YYYY-MM-DD` | `@author` | Updated after review | `Draft` |
| `YYYY-MM-DD` | `@approver` | Approved | `Approved` |

---

## Appendix

> **Optional additional information.**

Include any supplementary material that supports the decision but doesn't fit in the main sections.

---

## Checklist

Before submitting this ADR for review, verify:

- [ ] All required sections are complete
- [ ] At least 3 options are documented
- [ ] All non-functional requirements are addressed
- [ ] Security impact is assessed
- [ ] Accessibility impact is assessed
- [ ] Risks are documented with mitigations
- [ ] Related ADRs are linked
- [ ] Revision history is updated
- [ ] Status is set correctly
- [ ] ADR has been spell-checked
- [ ] ADR has been reviewed by at least one peer

---

*Template version: 1.0.0*
*Last updated: 2026-07-19*
*Reference: `docs/adr/ADR_GOVERNANCE.md`*
