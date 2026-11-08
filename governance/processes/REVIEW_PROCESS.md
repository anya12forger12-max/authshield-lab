# Code Review Process — AuthShield Lab

This document describes the code review process for the AuthShield Lab repository.

---

## Overview

Code review is a critical part of our development process. Every pull request must be reviewed by at least one maintainer before merging. Reviews ensure code quality, security, accessibility, and alignment with project standards.

---

## Author Responsibilities

Before submitting a pull request, the author must:

### Self-Review

1. **Review your own diff** — Read every line as if you were the reviewer
2. **Run all checks locally** before pushing:
   ```bash
   npm run lint
   npm run typecheck
   npm test
   npm run test:a11y
   ```
3. **Verify the PR description** is complete and accurate
4. **Check for debug artifacts** — Remove console.log, debugger statements, TODO comments, and test data

### PR Preparation

1. **Write a clear title** using conventional commit format
2. **Fill out the PR template** completely:
   - Description of changes and motivation
   - Type of change (bug fix, feature, breaking change, etc.)
   - Testing approach
   - Checklist completion
3. **Link related issues** using `Closes #<number>` or `Relates to #<number>`
4. **Keep the PR focused** — One logical change per PR
5. **Keep the PR small** — Aim for under 400 lines of diff when possible
6. **Ensure CI passes** — Do not submit a PR with failing checks

### During Review

1. **Respond to all comments** — Even if just to acknowledge
2. **Explain decisions** — If you disagree, provide rationale
3. **Make requested changes** promptly (within 3 business days)
4. **Re-request review** after addressing feedback
5. **Do not merge your own PR** — Wait for approval

---

## Reviewer Responsibilities

### Before Reviewing

1. **Check your expertise** — Only review areas where you have knowledge
2. **Set aside focused time** — Reviews require attention to detail
3. **Understand the context** — Read the linked issues and PR description

### During Review

1. **Read the full diff** — Do not skip files or sections
2. **Understand the intent** — What is this change trying to accomplish?
3. **Evaluate correctness** — Does the code do what it claims?
4. **Check for edge cases** — What happens in unusual scenarios?
5. **Verify tests** — Are there adequate tests for the change?
6. **Check accessibility** — Are there any a11y implications?
7. **Review security** — Does this introduce any security concerns?
8. **Check documentation** — Is the change documented where needed?

### Providing Feedback

1. **Be constructive** — Focus on the code, not the person
2. **Be specific** — Reference exact lines and explain the issue
3. **Categorize comments**:
   - **Must fix** — Blocking issues that must be addressed
   - **Should fix** — Strong recommendations but not blocking
   - **Nit** — Minor style or preference issues (non-blocking)
   - **Question** — Seeking clarification, not necessarily a change request
   - **Praise** — Recognize good work when you see it
4. **Suggest solutions** — When possible, propose how to fix the issue
5. **Link resources** — Reference documentation, standards, or examples

### Example Review Comments

```
// Must fix
src/auth/validator.ts:42 — This comparison should be `>` not `>=`.
Tokens expiring at exactly the current time should be considered invalid.

// Should fix
src/ui/LabRunner.tsx:115 — Consider adding a loading state here.
Users may see a blank screen during the API call.

// Nit
src/utils/token.ts:8 — Could use optional chaining here:
`payload?.sub?.toString()`.

// Question
Is there a reason we're not using the existing `validateClaims` utility
here? See src/core/claims.ts:23.

// Praise
Nice use of the builder pattern here. Clean and readable.
```

---

## Review Checklist

Every review must verify the following:

### Code Quality

- [ ] Code follows the project's style guide
- [ ] No unnecessary complexity
- [ ] Functions are appropriately sized (< 50 lines preferred)
- [ ] No code duplication (DRY principle)
- [ ] Error handling is comprehensive
- [ ] No `any` types in TypeScript
- [ ] Variable and function names are descriptive
- [ ] No dead code or commented-out code

### Testing

- [ ] Tests cover the changed code
- [ ] Tests cover success and failure paths
- [ ] Tests cover edge cases
- [ ] Test names are descriptive
- [ ] No flaky tests introduced
- [ ] Coverage thresholds are met

### Security

- [ ] Input is validated and sanitized
- [ ] No hardcoded secrets or credentials
- [ ] SQL queries use parameterization
- [ ] Authentication/authorization is checked
- [ ] No information leakage in error messages
- [ ] Cryptographic operations use standard libraries

### Accessibility

- [ ] Interactive elements have accessible names
- [ ] Focus management is correct
- [ ] Color contrast meets AA requirements
- [ ] ARIA attributes are used correctly
- [ ] Keyboard navigation works as expected
- [ ] Screen reader announcements are correct

### Documentation

- [ ] Public APIs have JSDoc/TSDoc comments
- [ ] Complex logic is explained with comments
- [ ] README is updated if applicable
- [ ] CHANGELOG entry is included (for user-facing changes)

---

## Approval Criteria

A pull request is approved when:

1. **All review comments are resolved** — No outstanding "must fix" items
2. **At least 1 approval** from a maintainer
3. **All CI checks pass** — Lint, typecheck, tests, accessibility
4. **No unresolved conversations** — All discussions are closed
5. **PR description is complete** — All template items addressed

### Approval Levels

| Level | Meaning |
|-------|---------|
| **Approved** | Code meets all quality standards and is ready to merge |
| **Approved with suggestions** | Code is acceptable but has non-blocking recommendations |
| **Changes requested** | Must address feedback before merge |
| **Comment** | Reviewer has questions or concerns but hasn't finished review |

### Auto-Approval

Auto-approval is not used for any pull request. Every PR requires at least one human review.

---

## Merge Criteria

Before a PR can be merged, all of the following must be true:

| Criterion | Requirement |
|-----------|-------------|
| Approvals | ≥ 1 approving review |
| CI Status | All checks passing |
| Branch | Up to date with target branch |
| Conversations | All resolved |
| Signed commits | Required for main, develop, release/* |
| Conflicts | No merge conflicts |
| PR Description | Complete and accurate |

### Merge Method

| Source Branch | Target Branch | Method |
|---------------|---------------|--------|
| `feature/*` | `develop` | Squash and merge |
| `fix/*` | `develop` | Squash and merge |
| `release/*` | `main` | Squash and merge |
| `release/*` | `develop` | Merge commit |
| `hotfix/*` | `main` | Squash and merge |
| `hotfix/*` | `develop` | Merge commit |
| `security/*` | `develop` | Squash and merge |

---

## Review Turnaround Expectations

| PR Type | Expected First Review | Expected Final Approval |
|---------|----------------------|------------------------|
| Bug fix | 3 business days | 5 business days |
| Feature | 5 business days | 10 business days |
| Security | 24 hours | 48 hours |
| Hotfix | 24 hours | 24 hours |
| Documentation | 3 business days | 5 business days |
| Accessibility fix | 3 business days | 5 business days |

### Stale PRs

- PRs with no activity for **7 days** receive a stale warning
- PRs with no activity for **14 days** are marked inactive
- PRs with no activity for **30 days** are closed with a comment
- Authors may request re-opening at any time

---

## Conflict Resolution

### During Review

If the author and reviewer disagree:

1. **Discuss** — The author and reviewer discuss the concern in the PR comments
2. **Reference standards** — Both parties reference project standards, documentation, or best practices
3. **Third opinion** — If unresolved, another maintainer is consulted
4. **Escalation** — If still unresolved, the issue is escalated to the Technical Steering Committee
5. **Decision** — The TSC makes a binding decision

### Merge Conflicts

When a PR has merge conflicts with the target branch:

1. The author is responsible for resolving conflicts
2. Rebase on the target branch (preferred) or merge the target branch into the PR
3. Resolve conflicts carefully, preserving the intent of both changes
4. Re-run tests after resolution
5. Re-request review if the conflict resolution involved significant changes

### Rejection

PRs may be rejected if:

- The change does not align with project goals
- The change introduces unacceptable risk
- The author is unwilling to address review feedback
- A better approach is identified during review

Rejected PRs receive a clear explanation and are closed respectfully. Authors are encouraged to discuss alternatives before reopening.

---

## Special Review Types

### Security Reviews

Security-related changes require review from a security team member:

- Authentication changes
- Token handling changes
- Encryption changes
- Access control changes
- Input validation changes

### Accessibility Reviews

UI changes require accessibility review:

- New components
- Changes to existing components
- Layout changes
- Color or visual changes

### Documentation Reviews

Documentation changes require technical accuracy review:

- API documentation
- Architecture documentation
- Security documentation
- Contribution guidelines

---

## Tools

| Tool | Purpose |
|------|---------|
| GitHub Pull Requests | Primary review interface |
| Code Owners | Automatic reviewer assignment |
| Reviewer Suggestions | ML-based reviewer recommendations |
| Merge Queue | Automated merge queue for CI gating |

---

*This process is reviewed quarterly. Last update: July 2026.*
