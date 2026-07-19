# ADR Traceability Framework

> **Purpose**: Establish bidirectional traceability between Architecture Decision Records and all related artifacts, ensuring decisions can be traced from conception to implementation.

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. Traceability Links](#2-traceability-links)
- [3. Link Standards](#3-link-standards)
- [4. Traceability Matrix](#4-traceability-matrix)
- [5. Validation Tools](#5-validation-tools)
- [6. Automated Link Checking](#6-automated-link-checking)

---

## 1. Overview

### 1.1 Purpose

Traceability ensures that every architectural decision can be traced to:

- **Upstream**: Business requirements, user stories, design documents
- **Downstream**: Code, tests, documentation, deployments
- **Lateral**: Related decisions, security reviews, accessibility reviews

### 1.2 Benefits

- **Accountability**: Know who decided what and why
- **Impact Analysis**: Understand what's affected by a decision change
- **Compliance**: Demonstrate decisions align with requirements
- **Onboarding**: Help new team members understand decision context
- **Quality**: Ensure decisions are properly implemented

### 1.3 Traceability Principles

| Principle | Description |
|-----------|-------------|
| **Bidirectional** | Links work in both directions |
| **Comprehensive** | All relevant artifacts are linked |
| **Current** | Links are kept up-to-date |
| **Automated** | Link validation is automated |
| **Auditable** | Link history is recorded |

---

## 2. Traceability Links

### 2.1 Upstream Links

Links to artifacts that motivated or influenced the decision.

| Artifact Type | Link Format | Example |
|--------------|------------|---------|
| GitHub Issue | `ISSUE-{number}` | `ISSUE-123` |
| User Story | `US-{number}` | `US-456` |
| Design Doc | `DESIGN-{name}` | `DESIGN-auth-flow` |
| Requirements Doc | `REQ-{number}` | `REQ-789` |
| Meeting Minutes | `MEETING-{date}` | `MEETING-2026-07-15` |

### 2.2 Downstream Links

Links to artifacts produced by or influenced by the decision.

| Artifact Type | Link Format | Example |
|--------------|------------|---------|
| GitHub PR | `PR-{number}` | `PR-1234` |
| Commit | `COMMIT-{hash}` | `COMMIT-abc1234` |
| Release | `RELEASE-{version}` | `RELEASE-1.0.0` |
| Test Suite | `TEST-{suite}` | `TEST-integration` |
| Benchmark | `BENCH-{name}` | `BENCH-api-perf` |

### 2.3 Lateral Links

Links to related artifacts in other domains.

| Artifact Type | Link Format | Example |
|--------------|------------|---------|
| Security Review | `SEC-{number}` | `SEC-001` |
| Accessibility Audit | `A11Y-{number}` | `A11Y-002` |
| Privacy Assessment | `PRIV-{number}` | `PRIV-003` |
| Performance Review | `PERF-{number}` | `PERF-004` |
| Compliance Review | `COMP-{number}` | `COMP-005` |

### 2.4 Related ADR Links

Links to other Architecture Decision Records.

| Relationship | Link Format | Example |
|-------------|------------|---------|
| Depends on | `ADR-XXX depends on ADR-YYY` | `ADR-002 depends on ADR-001` |
| Supersedes | `ADR-XXX supersedes ADR-YYY` | `ADR-004 supersedes ADR-002` |
| Relates to | `ADR-XXX relates to ADR-YYY` | `ADR-005 relates to ADR-001` |
| Conflicts with | `ADR-XXX conflicts with ADR-YYY` | `ADR-006 conflicts with ADR-003` |

---

## 3. Link Standards

### 3.1 Link Format

All links follow a consistent format:

```
[LinkType]-[Identifier]
```

**Examples**:

- `ISSUE-123` (GitHub Issue #123)
- `PR-456` (GitHub Pull Request #456)
- `COMMIT-abc1234` (Git commit hash)
- `RELEASE-1.0.0` (Release version)
- `SEC-001` (Security Review #001)
- `A11Y-002` (Accessibility Audit #002)

### 3.2 Link Placement

Links are placed in the ADR in these sections:

| Section | Link Types |
|---------|-----------|
| **Related ADRs** | Other ADRs |
| **References** | External documents, URLs |
| **Implementation** | PRs, Commits, Releases |
| **Testing** | Test suites, benchmarks |
| **Reviews** | Security, accessibility reviews |

### 3.3 Link Documentation

Each link must include:

1. **Link identifier**: The formatted link
2. **Link type**: Category of the link
3. **Description**: Brief description of the linked artifact
4. **Status**: Current status of the linked artifact
5. **Date**: When the link was created or last verified

### 3.4 Link Metadata

```yaml
links:
  - id: "ISSUE-123"
    type: "upstream"
    description: "Original feature request"
    status: "closed"
    created: "2026-01-15"
    verified: "2026-07-19"
  - id: "PR-456"
    type: "downstream"
    description: "Implementation PR"
    status: "merged"
    created: "2026-02-01"
    verified: "2026-07-19"
```

---

## 4. Traceability Matrix

### 4.1 ADR-to-Issue Matrix

| ADR | Issues | Status |
|-----|--------|--------|
| ADR-001 | ISSUE-101, ISSUE-102 | Closed |
| ADR-002 | ISSUE-103 | Closed |
| ADR-003 | ISSUE-104, ISSUE-105 | Closed |
| ADR-004 | ISSUE-106 | Closed |
| ADR-005 | ISSUE-107, ISSUE-108 | Closed |
| ADR-006 | ISSUE-109, ISSUE-110 | Closed |

### 4.2 ADR-to-PR Matrix

| ADR | PRs | Status |
|-----|-----|--------|
| ADR-001 | PR-201, PR-202 | Merged |
| ADR-002 | PR-203 | Merged |
| ADR-003 | PR-204 | Merged |
| ADR-004 | PR-205, PR-206 | Merged |
| ADR-005 | PR-207 | Merged |
| ADR-006 | PR-208, PR-209, PR-210 | Merged |

### 4.3 ADR-to-Test Matrix

| ADR | Test Suites | Coverage |
|-----|-------------|----------|
| ADR-001 | TEST-frontend, TEST-e2e | 85% |
| ADR-002 | TEST-api, TEST-integration | 90% |
| ADR-003 | TEST-database, TEST-unit | 88% |
| ADR-004 | TEST-state, TEST-unit | 92% |
| ADR-005 | TEST-styles, TEST-visual | 80% |
| ADR-006 | TEST-security, TEST-network | 95% |

### 4.4 ADR-to-Review Matrix

| ADR | Security Reviews | Accessibility Reviews |
|-----|-----------------|----------------------|
| ADR-001 | SEC-001 | A11Y-001 |
| ADR-002 | SEC-002 | A11Y-002 |
| ADR-003 | SEC-003 | A11Y-003 |
| ADR-004 | SEC-004 | A11Y-004 |
| ADR-005 | SEC-005 | A11Y-005 |
| ADR-006 | SEC-006 | A11Y-006 |

### 4.5 ADR-to-Release Matrix

| ADR | First Release | Current Release | Status |
|-----|---------------|-----------------|--------|
| ADR-001 | RELEASE-0.1.0 | RELEASE-1.0.0 | Active |
| ADR-002 | RELEASE-0.1.0 | RELEASE-1.0.0 | Active |
| ADR-003 | RELEASE-0.1.0 | RELEASE-1.0.0 | Active |
| ADR-004 | RELEASE-0.2.0 | RELEASE-1.0.0 | Active |
| ADR-005 | RELEASE-0.2.0 | RELEASE-1.0.0 | Active |
| ADR-006 | RELEASE-0.1.0 | RELEASE-1.0.0 | Active |

---

## 5. Validation Tools

### 5.1 Link Checker

The link checker validates that all links in ADRs are valid.

**Usage**:

```bash
# Check all ADRs
python scripts/adr_checker.py --check-links

# Check specific ADR
python scripts/adr_checker.py --check-links --adr ADR-001

# Generate report
python scripts/adr_checker.py --check-links --report
```

**Checks performed**:

- All GitHub issues exist
- All GitHub PRs exist
- All commits exist
- All releases exist
- All related ADRs exist
- All external URLs are accessible
- All internal file paths exist

### 5.2 Status Validator

The status validator ensures ADR statuses are consistent with their implementation.

**Usage**:

```bash
# Validate all statuses
python scripts/adr_checker.py --validate-status

# Validate specific ADR
python scripts/adr_checker.py --validate-status --adr ADR-001
```

**Checks performed**:

- Status matches implementation state
- Status transitions follow lifecycle rules
- Required reviews are completed
- Required approvals are recorded

### 5.3 Metadata Validator

The metadata validator ensures ADR metadata is complete and correct.

**Usage**:

```bash
# Validate all metadata
python scripts/adr_checker.py --validate-metadata

# Validate specific ADR
python scripts/adr_checker.py --validate-metadata --adr ADR-001
```

**Checks performed**:

- All required fields are present
- Date formats are correct
- Authors are valid team members
- Reviewers are valid team members
- Approvers are valid approvers

### 5.4 Completeness Checker

The completeness checker ensures ADRs have all required sections.

**Usage**:

```bash
# Check all ADRs
python scripts/adr_checker.py --check-completeness

# Check specific ADR
python scripts/adr_checker.py --check-completeness --adr ADR-001
```

**Checks performed**:

- All required sections exist
- All required sections have content
- At least 3 options are documented
- Security impact is assessed
- Accessibility impact is assessed

### 5.5 Report Generator

The report generator creates traceability reports.

**Usage**:

```bash
# Generate full report
python scripts/adr_checker.py --report

# Generate specific report
python scripts/adr_checker.py --report --type traceability

# Generate CSV export
python scripts/adr_checker.py --report --format csv
```

**Report types**:

- **Traceability report**: All links and their status
- **Completeness report**: ADR completeness metrics
- **Status report**: ADR status distribution
- **Audit report**: Compliance with governance rules

---

## 6. Automated Link Checking

### 6.1 CI/CD Integration

Link checking is integrated into the CI/CD pipeline.

**Pipeline steps**:

1. **Pre-commit hook**: Basic link validation
2. **PR check**: Full link validation
3. **Merge check**: Comprehensive validation
4. **Scheduled check**: Weekly full validation

### 6.2 Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: adr-link-check
        name: ADR Link Check
        entry: python scripts/adr_checker.py --check-links --changed-only
        language: system
        files: 'docs/adr/.*\.md$'
```

### 6.3 PR Check

```yaml
# .github/workflows/adr-check.yml
name: ADR Check
on:
  pull_request:
    paths:
      - 'docs/adr/**'

jobs:
  adr-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check ADR links
        run: python scripts/adr_checker.py --check-links --pr ${{ github.event.pull_request.number }}
      - name: Validate ADR status
        run: python scripts/adr_checker.py --validate-status --pr ${{ github.event.pull_request.number }}
      - name: Check ADR metadata
        run: python scripts/adr_checker.py --validate-metadata --pr ${{ github.event.pull_request.number }}
```

### 6.4 Merge Check

```yaml
# .github/workflows/adr-merge.yml
name: ADR Merge Check
on:
  push:
    branches:
      - main
    paths:
      - 'docs/adr/**'

jobs:
  adr-merge-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Full ADR validation
        run: python scripts/adr_checker.py --all
      - name: Generate report
        run: python scripts/adr_checker.py --report
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: adr-report
          path: adr-report.md
```

### 6.5 Scheduled Check

```yaml
# .github/workflows/adr-weekly.yml
name: ADR Weekly Check
on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight

jobs:
  adr-weekly-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Full ADR validation
        run: python scripts/adr_checker.py --all --report
      - name: Check external links
        run: python scripts/adr_checker.py --check-external-links
      - name: Generate audit report
        run: python scripts/adr_checker.py --report --format audit
      - name: Send report
        uses: actions/github-script@v6
        with:
          script: |
            // Send report to team channel
```

### 6.6 Link Validation Rules

| Rule | Description | Severity |
|------|-------------|----------|
| **Existence** | Link target exists | Error |
| **Access** | Link target is accessible | Warning |
| **Freshness** | Link target is up-to-date | Info |
| **Consistency** | Link format is consistent | Error |
| **Completeness** | All required links are present | Error |

### 6.7 Link Validation Report

```markdown
# ADR Link Validation Report

**Date**: 2026-07-19
**Scope**: All ADRs in docs/adr/

## Summary

- Total ADRs: 6
- Total links: 42
- Valid links: 40
- Invalid links: 1
- Warnings: 1

## Invalid Links

| ADR | Link | Issue |
|-----|------|-------|
| ADR-003 | ISSUE-104 | Issue not found |

## Warnings

| ADR | Link | Issue |
|-----|------|-------|
| ADR-005 | URL-001 | External link may be outdated |

## Recommendations

1. Fix invalid link in ADR-003
2. Verify external link in ADR-005
3. Add missing test link in ADR-006
```

---

## Appendix A: Link Format Reference

| Format | Example | Description |
|--------|---------|-------------|
| `ISSUE-{n}` | `ISSUE-123` | GitHub Issue |
| `PR-{n}` | `PR-456` | GitHub Pull Request |
| `COMMIT-{hash}` | `COMMIT-abc1234` | Git Commit |
| `RELEASE-{v}` | `RELEASE-1.0.0` | Release |
| `SEC-{n}` | `SEC-001` | Security Review |
| `A11Y-{n}` | `A11Y-002` | Accessibility Audit |
| `PRIV-{n}` | `PRIV-003` | Privacy Assessment |
| `PERF-{n}` | `PERF-004` | Performance Review |
| `COMP-{n}` | `COMP-005` | Compliance Review |
| `ADR-{n}` | `ADR-001` | Architecture Decision Record |
| `TEST-{suite}` | `TEST-integration` | Test Suite |
| `BENCH-{name}` | `BENCH-api-perf` | Benchmark |
| `DESIGN-{name}` | `DESIGN-auth-flow` | Design Document |
| `REQ-{n}` | `REQ-789` | Requirements Document |
| `US-{n}` | `US-456` | User Story |
| `MEETING-{date}` | `MEETING-2026-07-15` | Meeting Minutes |

---

*Traceability version: 1.0.0*
*Last updated: 2026-07-19*
*Next review: 2026-10-19*
