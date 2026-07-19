# AuthShield Lab — Quality Standards

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab enforces measurable quality standards across code quality, testing, documentation, accessibility, security, and performance. These standards are enforced via CI/CD gates and are non-negotiable for merge to main.

---

## 2. Static Analysis

### 2.1 Python: ruff

| Rule | Description | Enforcement |
|------|-------------|-------------|
| **E/W** | pycodestyle errors/warnings | Error |
| **F** | Pyflakes (unused imports, undefined names) | Error |
| **I** | isort (import sorting) | Error |
| **B** | flake8-bugbear (common bugs) | Error |
| **S** | flake8-bandit (security) | Error |
| **C4** | flake8-comprehensions | Error |
| **UP** | pyupgrade (Python version upgrades) | Warning |
| **RUF** | ruff-specific rules | Error |

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "S", "C4", "UP", "RUF"]
ignore = ["S101"]  # Allow assert in tests

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "S106"]
"**/migrations/**/*.py" = ["E501"]
```

### 2.2 TypeScript: eslint

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-floating-promises": "error",
    "no-console": "warn",
    "no-debugger": "error"
  }
}
```

---

## 3. Formatting

### 3.1 Python: ruff format

```toml
# pyproject.toml
[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"
docstring-code-format = true
```

### 3.2 TypeScript: prettier

```json
{
  "semi": true,
  "trailingComma": "all",
  "singleQuote": false,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

---

## 4. Type Checking

### 4.1 Python: mypy strict mode

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
```

### 4.2 TypeScript: strict tsconfig

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

---

## 5. Complexity Limits

### 5.1 Python

| Metric | Limit | Enforcement |
|--------|-------|-------------|
| **Cyclomatic complexity** | Max 15 | `ruff B015` + custom rules |
| **Function length** | Max 50 lines | CI check |
| **File length** | Max 500 lines | CI check (warning) |
| **Cognitive complexity** | Max 20 | Custom lint rule |
| **Nesting depth** | Max 4 | `ruff` rule |
| **Parameters per function** | Max 6 | CI check |

### 5.2 TypeScript

| Metric | Limit | Enforcement |
|--------|-------|-------------|
| **Cyclomatic complexity** | Max 15 | `eslint complexity` rule |
| **Function length** | Max 50 lines | CI check |
| **File length** | Max 500 lines | CI check (warning) |
| **Nesting depth** | Max 4 | ESLint rule |
| **Parameters per function** | Max 6 | CI check |

### 5.3 Complexity Calculation

```python
# Cyclomatic complexity = decision points + 1
# Decision points: if, elif, for, while, and, or, except, case

def process_assessment(assessment, user):  # +1
    if assessment.is_expired:             # +1
        raise ExpiredError()
    for question in assessment.questions:  # +1
        if question.type == "multiple":    # +1
            if question.required:          # +1
                validate_answer(question)
        elif question.type == "boolean":   # +1
            validate_boolean(question)
        else:
            validate_text(question)
    try:
        grade = calculate_grade(assessment)
    except GradeError:                     # +1
        grade = 0
    return grade

# Complexity: 8 (acceptable, limit is 15)
```

---

## 6. Documentation Coverage

### 6.1 Requirements

| Component | Requirement | Enforcement |
|-----------|-------------|-------------|
| **Public API** | 100% docstring coverage | `ruff D100-D107` + CI check |
| **Internal modules** | 80% docstring coverage | CI check (warning) |
| **React components** | JSDoc + accessibility docs | Code review |
| **Configuration** | Schema documentation | `pydantic` model descriptions |
| **Architecture decisions** | ADR format | Manual review |

### 6.2 Docstring Format (Google Style)

```python
def authenticate(
    username: str,
    password: str,
    ip_address: str,
    user_agent: str | None = None,
) -> AuthResult:
    """Authenticate a user with username and password.

    Validates credentials against the stored password hash using
    Argon2id. Implements rate limiting and account lockout policies.
    Logs all authentication attempts for security auditing.

    Args:
        username: Email address or username for authentication.
        password: Plain-text password to verify.
        ip_address: Client IP address for rate limiting and logging.
        user_agent: Optional client user agent string for logging.

    Returns:
        AuthResult containing session token and user information
        on success, or error details on failure.

    Raises:
        AuthRateLimitError: If too many failed attempts from this IP.
        AccountLockedError: If account is locked due to failed attempts.
        InvalidCredentialsError: If username/password combination is invalid.

    Example:
        >>> result = authenticate(
        ...     username="user@example.com",
        ...     password="secure_password",
        ...     ip_address="192.168.1.1",
        ... )
        >>> if result.success:
        ...     print(f"Welcome, {result.user.name}")
    """
```

### 6.3 React Component Documentation

```tsx
/**
 * AssessmentForm - Accessible form for submitting assessment answers.
 *
 * This component renders a multi-question assessment form with
 * keyboard navigation, screen reader support, and real-time validation.
 *
 * @accessibility
 * - All fields have associated labels
 * - Error messages are linked via aria-describedby
 * - Required fields marked with aria-required
 * - Form has error summary at top
 * - Tab order follows visual order
 *
 * @example
 * ```tsx
 * <AssessmentForm
 *   questions={questions}
 *   onSubmit={handleSubmit}
 *   onCancel={handleCancel}
 * />
 * ```
 */
function AssessmentForm({ questions, onSubmit, onCancel }) {
  // ...
}
```

---

## 7. Accessibility Coverage

### 7.1 Requirements

| Component | Requirement | Enforcement |
|-----------|-------------|-------------|
| **New UI components** | axe-core pass (0 violations) | CI gate |
| **New pages** | axe-core pass + manual keyboard test | CI gate |
| **New features** | A11y audit before merge | Code review |
| **Existing components** | Regression testing per release | Quarterly audit |

### 7.2 Accessibility Testing

```bash
# Automated accessibility tests
npm run test:a11y

# Manual keyboard navigation test
# 1. Tab through entire page
# 2. Verify all interactive elements are reachable
# 3. Verify focus indicators are visible
# 4. Verify modal focus trapping
# 5. Verify skip links work
# 6. Verify form error navigation

# Screen reader test
# 1. NVDA on Windows: navigate page, complete forms
# 2. VoiceOver on macOS: navigate page, complete forms
```

### 7.3 A11y Score Thresholds

| Score | Status | Action |
|-------|--------|--------|
| 100 | Perfect | No action |
| 95-99 | Excellent | Address minor issues |
| 90-94 | Good | Address serious issues |
| 80-89 | Needs work | Block merge |
| Below 80 | Poor | Block merge; remediate |

---

## 8. Test Coverage

### 8.1 Coverage Targets

| Category | Target | Enforcement |
|----------|--------|-------------|
| **Unit tests** | 95%+ line coverage | CI gate |
| **Integration tests** | 80%+ API endpoint coverage | CI gate |
| **E2E tests** | 100% critical user journeys | CI gate |
| **A11y tests** | 100% new components | CI gate |

### 8.2 Test Framework Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--cov=authshield",
    "--cov-report=html:htmlcov",
    "--cov-report=term-missing",
    "--cov-fail-under=95",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests",
]
```

### 8.3 Test Categories

```python
# Unit test
@pytest.mark.unit
def test_password_hashing():
    hasher = PasswordHasher(algorithm="argon2id")
    hashed = hasher.hash("password")
    assert hasher.verify("password", hashed) is True
    assert hasher.verify("wrong_password", hashed) is False

# Integration test
@pytest.mark.integration
async def test_assessment_submission(db_session):
    assessment = await create_assessment(db_session)
    result = await submit_assessment(db_session, assessment.id, answers)
    assert result.score >= 0
    assert result.status == "graded"

# E2E test
@pytest.mark.e2e
async def test_login_flow(page):
    await page.goto("http://localhost:3000/login")
    await page.fill('[name="email"]', "user@example.com")
    await page.fill('[name="password"]', "password")
    await page.click('button[type="submit"]')
    await page.wait_for_url("**/dashboard")
    assert await page.title() == "Dashboard - AuthShield Lab"
```

### 8.4 Coverage Reports

```bash
# Generate coverage report
pytest --cov=authshield --cov-report=html --cov-report=term-missing

# Upload to coverage service (optional)
coverage xml
bash <(curl -s https://codecov.io/bash)

# Fail CI if coverage below threshold
pytest --cov-fail-under=95
```

---

## 9. Security Gates

### 9.1 Required Gates

| Gate | Tool | Threshold | Blocking |
|------|------|-----------|----------|
| **No critical/high vulnerabilities** | pip-audit | 0 critical, 0 high | Yes |
| **No critical/high vulnerabilities** | npm audit | 0 critical, 0 high | Yes |
| **No hardcoded secrets** | detect-secrets | 0 new | Yes |
| **No unsafe code patterns** | bandit | 0 high severity | Yes |
| **SBOM generated** | cyclonedx | Required per release | Yes |
| **Code signed** | gpg | Required per release | Yes |

### 9.2 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: "v0.4.0"
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: "v1.10.0"
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]

  - repo: https://github.com/PyCQA/bandit
    rev: "1.7.8"
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]

  - repo: https://github.com/Yelp/detect-secrets
    rev: "v1.4.0"
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: "v9.0.0"
    hooks:
      - id: eslint
        files: \.(ts|tsx)$
        additional_dependencies:
          - eslint@9.0.0
          - "@typescript-eslint/eslint-plugin@8.0.0"
          - "@typescript-eslint/parser@8.0.0"

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: "v3.2.0"
    hooks:
      - id: prettier
        files: \.(ts|tsx|json|css|md)$
```

### 9.3 CI/CD Security Pipeline

```yaml
# .github/workflows/security.yml
name: Security Gates
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Python security
        run: |
          pip install pip-audit bandit detect-secrets
          pip-audit --require-hashes --strict
          bandit -r src/ -ll -f json -o bandit-report.json
          detect-secrets scan --all-files --update
      
      - name: Node security
        run: |
          npm ci
          npm audit --audit-level=critical
      
      - name: Type checking
        run: |
          pip install mypy
          mypy src/
          npm run typecheck
      
      - name: Linting
        run: |
          ruff check src/
          npm run lint
      
      - name: Formatting check
        run: |
          ruff format --check src/
          npm run format -- --check
```

---

## 10. Performance Targets

### 10.1 API Response Times

| Endpoint | Target | Measurement |
|----------|--------|-------------|
| **Authentication** | < 200ms | p95 latency |
| **Dashboard load** | < 500ms | p95 latency |
| **Assessment submission** | < 300ms | p95 latency |
| **Report generation** | < 2s (PDF) | p95 latency |
| **Search** | < 100ms | p95 latency |
| **Health check** | < 50ms | p99 latency |

### 10.2 Page Load Times

| Metric | Target | Measurement |
|--------|--------|-------------|
| **First Contentful Paint** | < 1s | Lighthouse |
| **Largest Contentful Paint** | < 2s | Lighthouse |
| **Time to Interactive** | < 3s | Lighthouse |
| **Cumulative Layout Shift** | < 0.1 | Lighthouse |
| **Total Blocking Time** | < 200ms | Lighthouse |

### 10.3 Application Startup

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Cold start (Electron)** | < 5s | Manual timing |
| **Hot reload (dev)** | < 1s | Vite HMR |
| **Database initialization** | < 500ms | Profiling |
| **Plugin loading** | < 2s total | Profiling |

### 10.4 Performance Testing

```python
# Performance test example
@pytest.mark.performance
async def test_assessment_submission_performance(db_session, benchmark):
    assessment = await create_assessment(db_session)
    
    result = await benchmark(
        submit_assessment,
        db_session,
        assessment.id,
        generate_answers(assessment),
    )
    
    assert result.elapsed_ms < 300  # p95 target
```

### 10.5 Performance Monitoring

```python
from authshield.logging import PerformanceLogger

perf = PerformanceLogger(logger)

@perf.measure("api.assessment.submit")
async def submit_assessment(assessment_id: str):
    # ... submission logic ...
    pass

# Logs: {"event": "api.assessment.submit", "duration_ms": 145}
```

---

## 11. Maintainability

### 11.1 Maintainability Index

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Maintainability Index** | > 80 | `radon mi src/` |
| **Technical Debt Ratio** | < 5% | SonarQube / custom |
| **Code Duplication** | < 3% | `jscpd` / `pylint` |
| **Comment Density** | 10-30% | Custom metric |

### 11.2 Code Quality Metrics

```bash
# Python maintainability index
pip install radon
radon mi src/ -a

# Complexity report
radon cc src/ -a -nc

# Duplication detection
pip install pylint
pylint --duplicate-code src/
```

### 11.3 Technical Debt Tracking

```python
# Mark technical debt items
# TODO: Refactor authentication flow to support OAuth
# FIXME: Race condition in session refresh
# HACK: Workaround for upstream bug #1234
# DEPRECATED: Remove in v2.0.0

# Track debt items
import re

def find_tech_debt(directory: Path) -> list[dict]:
    """Find all TODO/FIXME/HACK/DEPRECATED comments."""
    pattern = re.compile(r"#\s*(TODO|FIXME|HACK|DEPRECATED):\s*(.*)")
    items = []
    
    for file in directory.rglob("*.py"):
        for line_num, line in enumerate(file.read_text().splitlines(), 1):
            match = pattern.search(line)
            if match:
                items.append({
                    "file": str(file),
                    "line": line_num,
                    "type": match.group(1),
                    "description": match.group(2),
                })
    
    return items
```

---

## 12. Code Review Standards

### 12.1 Review Checklist

| Category | Items |
|----------|-------|
| **Correctness** | Logic correct, edge cases handled, error handling |
| **Security** | No secrets, input validation, SQL injection prevention |
| **Performance** | No N+1 queries, efficient algorithms, caching appropriate |
| **Accessibility** | ARIA labels, keyboard navigation, screen reader support |
| **Testing** | Tests cover new code, edge cases, error paths |
| **Documentation** | Docstrings, comments for complex logic, API docs |
| **Style** | Follows code style, consistent naming, no dead code |

### 12.2 Review Requirements

| Requirement | Description |
|-------------|-------------|
| **Minimum 1 approval** | At least 1 team member approval required |
| **CI passes** | All CI checks must pass |
| **No unresolved comments** | All review comments must be resolved |
| **Tests included** | New code must include tests |
| **Documentation updated** | Public API changes require doc updates |
| **A11y reviewed** | UI changes require accessibility review |

---

## 13. Release Quality Gates

### 13.1 Pre-release Checklist

| Gate | Requirement | Tool |
|------|-------------|------|
| **All tests pass** | 100% test suite green | pytest, vitest |
| **Coverage threshold** | 95%+ unit, 80%+ integration | pytest-cov |
| **No critical vulnerabilities** | 0 critical/high CVEs | pip-audit, npm audit |
| **SBOM generated** | SPDX + CycloneDX | cyclonedx |
| **Code signed** | Ed25519 signatures | gpg/cosign |
| **Documentation complete** | 100% public API | docstring coverage |
| **Accessibility audit** | axe-core pass | axe-core |
| **Performance benchmarks** | All targets met | benchmark suite |
| **Changelog updated** | All changes documented | Manual review |
| **Version bumped** | Semver compliant | Manual review |

### 13.2 Release Process

```bash
# 1. Run full test suite
pytest --cov --cov-fail-under=95
npm test

# 2. Run security audit
pip-audit --require-hashes --strict
npm audit --audit-level=critical

# 3. Run accessibility tests
npm run test:a11y

# 4. Run performance benchmarks
pytest -m performance

# 5. Generate SBOM
cyclonedx-py environment --output-file sbom-python.json
npx cyclonedx-npm --output-file sbom-node.json

# 6. Build release artifacts
python -m build
npm run electron:build

# 7. Sign release artifacts
gpg --armor --detach-sign dist/*.tar.gz

# 8. Generate checksums
sha256sum dist/* > SHA256SUMS

# 9. Tag release
git tag -s v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

---

*Document maintained by the AuthShield Lab Quality Team. Review quarterly.*
