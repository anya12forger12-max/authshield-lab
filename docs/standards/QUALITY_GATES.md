# AuthShield Lab — Quality Gates Framework

> Version 1.0 · Last Updated: 2026-07-19 · Owner: Engineering Team

---

## Table of Contents

1. [Overview](#1-overview)
2. [Pre-commit Checks](#2-pre-commit-checks)
3. [Pre-push Checks](#3-pre-push-checks)
4. [CI/CD Quality Gates](#4-cicd-quality-gates)
5. [Code Review Quality Gates](#5-code-review-quality-gates)
6. [Release Quality Gates](#6-release-quality-gates)
7. [Documentation Quality Gates](#7-documentation-quality-gates)
8. [Security Quality Gates](#8-security-quality-gates)
9. [Accessibility Quality Gates](#9-accessibility-quality-gates)
10. [Performance Quality Gates](#10-performance-quality-gates)
11. [Gate Failure Policy](#11-gate-failure-policy)

---

## 1. Overview

Quality gates are automated and manual checkpoints that code must pass before advancing to the next stage of the development pipeline. They exist to prevent defects from reaching production and to maintain consistent quality standards across the team.

### Pipeline Flow

```
Developer Workstation
    ↓ [Pre-commit Checks]
    ↓ [Pre-push Checks]
Pull Request
    ↓ [CI/CD Quality Gates]
    ↓ [Code Review Quality Gates]
    ↓ [Security Quality Gates]
    ↓ [Documentation Quality Gates]
    ↓ [Accessibility Quality Gates]
    ↓ [Performance Quality Gates]
Merge to main
    ↓ [Release Quality Gates]
Production Deployment
```

### Gate Ownership

| Gate Category | Owner | Enforcement |
|---|---|---|
| Pre-commit | Individual developer | Automated (git hooks) |
| Pre-push | Individual developer | Automated (git hooks) |
| CI/CD | Engineering team | Automated (CI pipeline) |
| Code Review | Reviewers | Manual + automated |
| Security | Security champion + automated | Automated + manual review |
| Documentation | Author + reviewers | Manual review |
| Accessibility | Frontend team | Automated (Lighthouse) + manual |
| Performance | Engineering team | Automated benchmarks |
| Release | Release manager | Manual checklist |

---

## 2. Pre-commit Checks

Pre-commit checks run locally before a commit is created. They are enforced via pre-commit hooks (`.pre-commit-config.yaml`).

### 2.1 Python Backend Pre-commit Gates

#### Linting with Ruff

| Criteria | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| No linting errors | `ruff check` | 0 errors | PASS if 0 errors, FAIL otherwise |
| No unused imports | `ruff check --select F401` | 0 violations | PASS if 0, FAIL otherwise |
| No undefined names | `ruff check --select F821` | 0 violations | PASS if 0, FAIL otherwise |
| No bare except clauses | `ruff check --select E722` | 0 violations | PASS if 0, FAIL otherwise |

#### Formatting with Ruff

| Criteria | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| Code formatted correctly | `ruff format --check` | 0 files needing reformatting | PASS if 0, FAIL otherwise |
| Consistent line length | Ruff config | 100 characters max | PASS if all lines ≤ 100, FAIL otherwise |

#### Type Checking with mypy

| Criteria | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| No type errors | `mypy src/` | 0 errors | PASS if 0, FAIL otherwise |
| No missing return type annotations | `mypy --disallow-untyped-defs` | 0 violations | PASS if 0, FAIL otherwise |
| Strict mode compliance | `mypy --strict` | Per-module overrides only | PASS if no new strict violations, FAIL otherwise |

#### Trailing Whitespace and File Endings

| Criteria | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| No trailing whitespace | `pre-commit-hooks trailing-whitespace` | 0 files | PASS if 0, FAIL otherwise |
| Files end with newline | `pre-commit-hooks end-of-file-fixer` | 0 files | PASS if 0, FAIL otherwise |
| No large files committed | `pre-commit-hooks check-added-large-files` | < 500 KB per file | PASS if all files < 500 KB, FAIL otherwise |
| No merge conflict markers | `pre-commit-hooks check-merge-conflict` | 0 markers | PASS if 0, FAIL otherwise |

### 2.2 Frontend Pre-commit Gates

#### TypeScript Compilation

| Criteria | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| TypeScript compiles | `tsc --noEmit` | 0 errors | PASS if 0, FAIL otherwise |
| No `any` types introduced | ESLint `@typescript-eslint/no-explicit-any` | 0 new violations | PASS if 0, FAIL otherwise |

#### Frontend Linting

| Criteria | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| ESLint passes | `eslint src/` | 0 errors | PASS if 0 errors, FAIL on errors (warnings allowed) |
| No unused variables | `eslint --no-unused-vars` | 0 violations | PASS if 0, FAIL otherwise |
| Consistent formatting | `prettier --check` | 0 files needing formatting | PASS if 0, FAIL otherwise |

### 2.3 Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, sqlalchemy, fastapi]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-yaml
      - id: check-toml
```

---

## 3. Pre-push Checks

Pre-push checks run before code is pushed to the remote repository. These are more expensive checks that should not block every commit but must run before sharing code.

### 3.1 Backend Pre-push Gates

| Criteria | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| Unit tests pass | `pytest tests/unit/ -x -q` | 100% pass rate | PASS if all pass, FAIL if any fail |
| Test collection succeeds | `pytest --collect-only` | 0 collection errors | PASS if 0, FAIL otherwise |
| No import cycles | `pylint --disable=all --enable=E0401` or `import-linter` | 0 circular imports | PASS if 0, FAIL otherwise |
| Code coverage meets minimum | `pytest --cov=src --cov-fail-under=75` | ≥ 75% overall | PASS if ≥ 75%, FAIL otherwise |

### 3.2 Frontend Pre-push Gates

| Criteria | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| Frontend tests pass | `npm test -- --watchAll=false` | 100% pass rate | PASS if all pass, FAIL if any fail |
| TypeScript compiles cleanly | `tsc --noEmit` | 0 errors | PASS if 0, FAIL otherwise |

### 3.3 Pre-push Hook Configuration

```bash
#!/bin/bash
# .git/hooks/pre-push

echo "Running pre-push checks..."

# Backend checks
cd backend
echo "Running unit tests..."
pytest tests/unit/ -x -q || { echo "Unit tests failed"; exit 1; }

echo "Checking code coverage..."
pytest --cov=src --cov-fail-under=75 --cov-report=term-missing -q || { echo "Coverage below threshold"; exit 1; }

# Frontend checks
cd ../frontend
echo "Running TypeScript compilation..."
npx tsc --noEmit || { echo "TypeScript compilation failed"; exit 1; }

echo "Running frontend tests..."
npm test -- --watchAll=false || { echo "Frontend tests failed"; exit 1; }

echo "All pre-push checks passed."
```

---

## 4. CI/CD Quality Gates

CI/CD gates run on every push and every pull request. They are the primary automated quality enforcement mechanism.

### 4.1 Backend CI Pipeline

#### Stage 1: Code Quality

| Gate | Tool | Threshold | Pass/Fail | Blocks |
|---|---|---|---|---|
| Lint | `ruff check` | 0 errors | FAIL on any error | Merge |
| Format | `ruff format --check` | 0 files need formatting | FAIL on any file | Merge |
| Type check | `mypy --strict` | 0 new errors | FAIL on any new error | Merge |
| Import order | `ruff --select I` | 0 violations | FAIL on any violation | Merge |

#### Stage 2: Testing

| Gate | Tool | Threshold | Pass/Fail | Blocks |
|---|---|---|---|---|
| Unit tests | `pytest tests/unit/` | 100% pass, ≥ 80% coverage | FAIL if any test fails or coverage < 80% | Merge |
| Integration tests | `pytest tests/integration/` | 100% pass, ≥ 60% coverage | FAIL if any test fails or coverage < 60% | Merge |
| Test duration | `pytest --timeout=30` | No test exceeds 30 seconds | FAIL if any test times out | Merge |
| Test collection | `pytest --collect-only` | 0 errors | FAIL on collection error | Merge |

#### Stage 3: Security

| Gate | Tool | Threshold | Pass/Fail | Blocks |
|---|---|---|---|---|
| Dependency audit | `pip-audit` | 0 high/critical vulnerabilities | FAIL on high/critical | Merge |
| Secret scanning | `detect-secrets scan` | 0 new secrets detected | FAIL on any detection | Merge |
| Bandit security scan | `bandit -r src/` | 0 high-severity issues | FAIL on high severity | Merge |
| SAST | `semgrep --config=auto` | 0 high-confidence findings | FAIL on high findings | Merge |

### 4.2 Frontend CI Pipeline

#### Stage 1: Code Quality

| Gate | Tool | Threshold | Pass/Fail | Blocks |
|---|---|---|---|---|
| TypeScript | `tsc --noEmit` | 0 errors | FAIL on any error | Merge |
| ESLint | `eslint src/` | 0 errors (warnings OK) | FAIL on any error | Merge |
| Prettier | `prettier --check` | 0 files need formatting | FAIL on any file | Merge |

#### Stage 2: Testing

| Gate | Tool | Threshold | Pass/Fail | Blocks |
|---|---|---|---|---|
| Unit tests | `npm test` | 100% pass | FAIL if any test fails | Merge |
| Test coverage | `jest --coverage` | ≥ 70% line coverage | FAIL if < 70% | Merge |

#### Stage 3: Build

| Gate | Tool | Threshold | Pass/Fail | Blocks |
|---|---|---|---|---|
| Build succeeds | `npm run build` | Exit code 0 | FAIL on non-zero exit | Merge |
| Bundle size | `webpack-bundle-analyzer` | < 2 MB total bundle | FAIL if > 2 MB | Warning (non-blocking) |
| No console.log in production | Custom grep | 0 occurrences in build output | FAIL if found | Merge |

### 4.3 CI Pipeline Configuration

```yaml
# .github/workflows/ci.yml (or equivalent)
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e ".[dev]"
      - run: ruff check src/ tests/
      - run: ruff format --check src/ tests/
      - run: mypy --strict src/
      - run: bandit -r src/ -ll
      - run: pip-audit

  backend-tests:
    runs-on: ubuntu-latest
    needs: backend-quality
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit/ --cov=src --cov-fail-under=80 -v
      - run: pytest tests/integration/ --cov=src --cov-fail-under=60 -v

  frontend-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npx eslint src/
      - run: npx prettier --check src/

  frontend-tests:
    runs-on: ubuntu-latest
    needs: frontend-quality
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test -- --coverage --watchAll=false
      - run: npm run build
```

---

## 5. Code Review Quality Gates

Code review gates combine automated checks with human judgment before a PR can be merged.

### 5.1 Automated Checks (Must Pass Before Review)

| Gate | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| All CI checks green | CI pipeline | 0 failures | PASS if all pass, FAIL if any fail |
| PR linked to issue | GitHub | Issue number in PR description | PASS if linked, FAIL otherwise |
| PR description complete | Template check | All required sections filled | PASS if complete, FAIL otherwise |
| PR size within limits | `git diff --stat` | < 400 lines changed | PASS if < 400, WARNING if 400-800, FAIL if > 800 |

### 5.2 Human Review Checks (Reviewer Must Verify)

| Gate | Criteria | Pass/Fail |
|---|---|---|
| Correctness | Code implements the described functionality without bugs | PASS / REQUEST_CHANGES |
| Test coverage | Tests cover happy path, error path, and edge cases | PASS / REQUEST_CHANGES |
| Security | No injection vulnerabilities, secrets exposed, or missing auth checks | PASS / REQUEST_CHANGES |
| Architecture | Change respects Clean Architecture boundaries and bounded contexts | PASS / REQUEST_CHANGES |
| Naming | Variables, functions, and classes are descriptively named | PASS / REQUEST_CHANGES |
| Documentation | Public APIs, complex logic, and non-obvious decisions are documented | PASS / REQUEST_CHANGES |
| Performance | No N+1 queries, unnecessary allocations, or blocking operations | PASS / REQUEST_CHANGES |

### 5.3 Approval Requirements

| Branch Target | Required Approvals | Additional Requirements |
|---|---|---|
| Feature branch | 1 approval | CI passes |
| `main` branch | 2 approvals | CI passes + security scan passes |
| Hotfix to `main` | 2 approvals (1 can be expedited) | CI passes + security scan passes |
| Release branch | 2 approvals including Engineering Lead | All gates pass + release checklist |

### 5.4 Review SLA

| Condition | Expected Response |
|---|---|
| Normal PR | First review within 4 business hours |
| Hotfix PR | First review within 1 business hour |
| All comments resolved | Final approval within 2 business days |
| Stale PR (> 5 days) | Flagged in daily standup |

---

## 6. Release Quality Gates

Release gates must all pass before a version is tagged and deployed.

### 6.1 Pre-release Checklist

| Gate | Tool/Method | Threshold | Pass/Fail |
|---|---|---|---|
| All CI checks pass on `main` | CI dashboard | 0 failures in last 24 hours | PASS if clean, FAIL otherwise |
| All unit tests pass | `pytest tests/unit/` | 100% pass rate | PASS if 100%, FAIL otherwise |
| All integration tests pass | `pytest tests/integration/` | 100% pass rate | PASS if 100%, FAIL otherwise |
| Unit test coverage ≥ 80% | `pytest --cov` | ≥ 80% line coverage | PASS if ≥ 80%, FAIL otherwise |
| Integration test coverage ≥ 60% | `pytest --cov` | ≥ 60% line coverage | PASS if ≥ 60%, FAIL otherwise |
| No P0/P1 bugs open | Issue tracker | 0 open P0/P1 bugs tagged for release | PASS if 0, FAIL otherwise |
| Security scan clean | `bandit` + `pip-audit` | 0 high/critical findings | PASS if 0, FAIL otherwise |
| Changelog updated | Manual check | CHANGELOG.md reflects all changes since last release | PASS if complete, FAIL otherwise |
| Database migrations tested | Migration test suite | All migrations run forward and backward | PASS if all pass, FAIL otherwise |
| API backward compatibility | `schemathesis` or manual | No breaking changes without version bump | PASS if compatible, FAIL otherwise |

### 6.2 Release Tagging

| Criteria | Requirement |
|---|---|
| Version format | Semantic versioning: `MAJOR.MINOR.PATCH` |
| Tag message | Include changelog summary |
| Git signed tags | All release tags must be GPG-signed |
| Branch protection | Release branch protected from force-push |

### 6.3 Post-release Verification

| Gate | Tool/Method | Threshold | Pass/Fail |
|---|---|---|---|
| Smoke tests pass | Automated smoke test suite | 100% pass | PASS if 100%, FAIL otherwise |
| Application starts cleanly | Health check endpoint | HTTP 200 within 30 seconds | PASS if 200, FAIL otherwise |
| No spike in error rate | Log monitoring | Error rate < 1% within 1 hour | PASS if < 1%, FAIL otherwise |
| Rollback plan documented | Release notes | Rollback steps included | PASS if documented, FAIL otherwise |

---

## 7. Documentation Quality Gates

Documentation gates ensure that all code changes are accompanied by appropriate documentation updates.

### 7.1 Documentation Requirements by Change Type

| Change Type | Required Documentation |
|---|---|
| New API endpoint | API documentation (OpenAPI schema), request/response examples |
| New feature | Feature documentation in `docs/features/`, user-facing help text |
| Breaking API change | Migration guide, API changelog, version bump |
| New architecture decision | ADR document in `docs/standards/adr/` |
| Bug fix | Regression test added, root cause documented in PR description |
| Configuration change | Updated configuration documentation, deployment guide |
| Database migration | Migration notes, rollback procedure documented |
| New dependency | Justification in PR description, license compatibility check |

### 7.2 Documentation Review Gates

| Gate | Criteria | Pass/Fail |
|---|---|---|
| OpenAPI schema updated | Auto-generated from FastAPI route definitions | PASS if schema reflects changes, FAIL if outdated |
| README.md current | Project README reflects current setup instructions | PASS if accurate, FAIL if outdated |
| CHANGELOG.md updated | New entry for user-facing changes | PASS if entry present, FAIL if missing |
| ADR created | For architectural decisions, ADR exists in `docs/standards/adr/` | PASS if ADR exists, N/A if no architecture change |
| Inline comments | Complex algorithms and non-obvious logic are explained | PASS if present where needed, FAIL if critical logic is undocumented |

### 7.3 Documentation Quality Standards

- **Accuracy:** Documentation matches the actual behavior of the code.
- **Currency:** Documentation is updated as part of the same PR that changes behavior.
- **Clarity:** Documentation is understandable by a new team member without additional context.
- **Completeness:** All public APIs, configuration options, and deployment steps are documented.
- **Searchability:** Documents have clear titles, headers, and are placed in the correct directory.

---

## 8. Security Quality Gates

Security gates are enforced at multiple stages to prevent vulnerabilities from reaching production.

### 8.1 Dependency Security

| Gate | Tool | Threshold | Pass/Fail | Frequency |
|---|---|---|---|---|
| No known high/critical CVEs | `pip-audit` (Python) | 0 high/critical | FAIL on any high/critical | Every CI run |
| No known high/critical CVEs | `npm audit` (JavaScript) | 0 high/critical | FAIL on any high/critical | Every CI run |
| Licenses compatible | `pip-licenses` / `license-checker` | No GPL in proprietary builds | FAIL if incompatible license found | Weekly scan |
| Dependencies up to date | `dependabot` or `renovate` | No dependency > 6 months stale | WARNING (not blocking) | Weekly scan |

### 8.2 Static Application Security Testing (SAST)

| Gate | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| Python SAST | `bandit -r src/ -ii -ll` | 0 high-severity issues | FAIL on high severity |
| Python SAST | `semgrep --config=p/python` | 0 high-confidence findings | FAIL on high findings |
| JavaScript SAST | `eslint-plugin-security` | 0 high-severity issues | FAIL on high severity |
| Secret detection | `detect-secrets scan` | 0 new secrets in diff | FAIL on any detection |

### 8.3 Authentication & Authorization Gates

| Gate | Criteria | Pass/Fail |
|---|---|---|
| All protected endpoints require auth | Manual review + automated test | PASS if all auth checks present |
| Role-based access control | Each endpoint declares required roles | PASS if roles defined |
| Password hashing | bcrypt/argon2 with minimum work factor | PASS if compliant algorithm used |
| Session management | Tokens have expiry, refresh rotation implemented | PASS if properly implemented |
| MFA bypass prevention | MFA enrollment cannot be skipped when enforced | PASS if enforcement tested |

### 8.4 Input Validation Gates

| Gate | Criteria | Pass/Fail |
|---|---|---|
| SQL injection prevention | All queries use parameterized statements | PASS if no string interpolation in SQL |
| XSS prevention | All user output is escaped | PASS if template engine or library handles escaping |
| Path traversal prevention | File operations validate paths against allowed directories | PASS if path validation present |
| Request size limits | API endpoints have request body size limits | PASS if limits configured |
| Rate limiting | Authentication endpoints have rate limiting | PASS if rate limits active |

### 8.5 Security Review Checklist

For PRs touching authentication, authorization, cryptography, or sensitive data:

- [ ] No hardcoded secrets or credentials
- [ ] Cryptographic operations use vetted libraries (not custom implementations)
- [ ] Sensitive data is not logged (passwords, tokens, PII)
- [ ] Error messages do not leak internal state
- [ ] CORS is properly configured
- [ ] Content Security Policy headers are set (for frontend)
- [ ] Cookies have `Secure`, `HttpOnly`, and `SameSite` attributes
- [ ] API keys and tokens are rotated periodically

---

## 9. Accessibility Quality Gates

All frontend changes must meet WCAG 2.1 AA accessibility standards.

### 9.1 Automated Accessibility Checks

| Gate | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| Lighthouse accessibility score | Google Lighthouse | ≥ 90/100 | PASS if ≥ 90, FAIL if < 90 |
| axe-core automated tests | `@axe-core/react` | 0 violations | PASS if 0, FAIL on any violation |
| Color contrast ratio | axe-core / manual | ≥ 4.5:1 for normal text, ≥ 3:1 for large text | PASS if compliant, FAIL otherwise |
| HTML validity | `html-validate` | 0 errors | PASS if 0, FAIL otherwise |

### 9.2 Manual Accessibility Checks

| Gate | Criteria | Pass/Fail |
|---|---|---|
| Keyboard navigation | All interactive elements reachable and operable via keyboard only | PASS if fully navigable |
| Focus indicators | Visible focus ring on all interactive elements | PASS if visible |
| Screen reader compatibility | All content announced correctly by screen reader | PASS if compatible |
| Form labels | All form inputs have associated labels | PASS if all labeled |
| Alt text | All meaningful images have descriptive alt text | PASS if all images have alt text |
| Error identification | Form errors identified by text, not color alone | PASS if text-based error messages |
| Motion preferences | Animations respect `prefers-reduced-motion` | PASS if reduced motion supported |

### 9.3 Accessibility Regression Prevention

- Automated axe-core tests run in CI on every PR that modifies frontend code.
- Lighthouse CI runs on the built application in the CI pipeline.
- Accessibility issues are tagged as `a11y` in the issue tracker.
- P1/P2 accessibility issues block merge. P3 issues are tracked for the next sprint.

---

## 10. Performance Quality Gates

Performance gates ensure that changes do not degrade application performance beyond acceptable thresholds.

### 10.1 Backend Performance Gates

| Gate | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| API response time | `pytest-benchmark` / load test | p95 < 200ms for standard endpoints | PASS if p95 < 200ms, FAIL otherwise |
| Database query count | SQLAlchemy query logging | ≤ 5 queries per API request (typical) | WARNING if > 5, FAIL if > 20 |
| N+1 query detection | `nplusone` library | 0 N+1 queries detected | FAIL on any N+1 |
| Memory usage | `tracemalloc` in tests | No unbounded memory growth | PASS if stable, FAIL on growth |
| Test suite duration | CI timing | Full suite < 10 minutes | WARNING if > 10 min, FAIL if > 20 min |

### 10.2 Frontend Performance Gates

| Gate | Tool | Threshold | Pass/Fail |
|---|---|---|---|
| Lighthouse performance score | Google Lighthouse | ≥ 80/100 | PASS if ≥ 80, FAIL if < 80 |
| First Contentful Paint | Lighthouse | < 2 seconds | PASS if < 2s, FAIL otherwise |
| Largest Contentful Paint | Lighthouse | < 3 seconds | PASS if < 3s, FAIL otherwise |
| Total bundle size | webpack-bundle-analyzer | < 2 MB | WARNING if > 2 MB, FAIL if > 5 MB |
| JavaScript execution time | Performance API | < 3 seconds on simulated mid-range device | PASS if < 3s, FAIL otherwise |
| Image optimization | Lighthouse | All images use modern formats (WebP/AVIF) | PASS if optimized, FAIL if raw formats used |

### 10.3 Performance Testing Cadence

| Type | Frequency | Duration | Scope |
|---|---|---|---|
| Benchmark tests | Every PR | Per-test < 30s | Individual function/query benchmarks |
| Load tests | Weekly / pre-release | 5-10 minutes | Full application under simulated load |
| Stress tests | Monthly | 15-30 minutes | Application under 2x expected peak load |
| Endurance tests | Quarterly | 1 hour | Application under normal load for extended period |

### 10.4 Performance Regression Policy

- **Within threshold:** PR proceeds normally.
- **10-25% regression:** Warning posted in PR. Must be investigated and resolved before merge if the regression is in a critical path.
- **> 25% regression:** PR is blocked. Performance fix required before merge. Engineering Lead must approve the exception if the regression is intentional and documented.

---

## 11. Gate Failure Policy

### 11.1 Blocking vs. Warning Gates

| Gate Type | Behavior on Failure | Example |
|---|---|---|
| **Blocking** | PR cannot be merged. Must be fixed. | Failing tests, security vulnerabilities, type errors |
| **Warning** | PR can be merged with explicit approval. Issue tracked. | Coverage slightly below threshold, bundle size warning |

### 11.2 Exception Process

When a gate failure is known and accepted:

1. Engineer documents the exception in the PR description.
2. An issue is created to address the gate failure.
3. Engineering Lead approves the exception with a deadline.
4. The exception is tracked in the technical debt register.
5. Exceptions expire after 30 days and must be re-evaluated.

### 11.3 Gate Maintenance

- Quality gates are reviewed quarterly by the engineering team.
- Thresholds are adjusted based on team velocity and quality metrics.
- New gates are proposed via RFC process.
- Deprecated gates are removed with the same RFC process.
- Gate configuration is version-controlled and changes are tracked in git.

### 11.4 Metrics and Reporting

The following metrics are tracked to measure gate effectiveness:

| Metric | Target | Measurement |
|---|---|---|
| Gate pass rate | ≥ 95% of CI runs pass all gates | CI dashboard |
| Mean time to fix gate failures | < 2 hours for blocking gates | Issue tracker |
| Gate false positive rate | < 5% | Manual tracking |
| Defect escape rate | < 1% of releases require hotfix | Release tracker |
| Security vulnerability escape rate | 0 critical/high in production | Security audit |

---

*This document is a living artifact. Propose changes via PR to the repository. All changes require approval from the Engineering Lead and Security Champion.*
