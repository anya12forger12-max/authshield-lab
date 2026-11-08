# Commit Conventions — AuthShield Lab

This document defines the commit message format and conventions used in the AuthShield Lab repository. We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

---

## Commit Message Format

Each commit message consists of a **header**, an optional **body**, and an optional **footer**:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Rules

1. The header is **mandatory**
2. The header must be lowercase (except proper nouns)
3. The header must not end with a period
4. The header must be 72 characters or fewer
5. The body must wrap at 80 characters
6. The body must explain **what** and **why**, not **how**
7. Use imperative mood in the subject ("add" not "added")
8. Reference issues in the footer

---

## Types

| Type | Description | When to Use |
|------|-------------|-------------|
| `feat` | A new feature | Adding new functionality |
| `fix` | A bug fix | Correcting existing behavior |
| `refactor` | Code restructuring | No behavior change, improves code structure |
| `perf` | Performance improvement | Makes code run faster or use fewer resources |
| `docs` | Documentation | README, comments, docs site, JSDoc |
| `style` | Formatting | Whitespace, semicolons, quotes (no logic change) |
| `test` | Tests | Adding or updating tests |
| `build` | Build system | Webpack, Vite, esbuild, npm scripts |
| `ci` | CI/CD | GitHub Actions, pipelines, deployment config |
| `security` | Security | Vulnerability fixes, security improvements |
| `accessibility` | Accessibility | WCAG compliance, a11y improvements |
| `localization` | Localization | Translations, i18n, RTL support |
| `deps` | Dependencies | Dependency updates or additions |
| `chore` | Maintenance | Configuration, tooling, non-production changes |

---

## Examples

### `feat`

```
feat(auth): add OAuth 2.0 authorization code flow

Implements the complete OAuth 2.0 authorization code flow including:
- Authorization endpoint with PKCE support
- Token exchange endpoint
- Refresh token rotation
- Token revocation

Closes #142
```

```
feat(lms): add course completion certificates

Learners now receive a downloadable PDF certificate upon completing
a course with a passing score.
```

### `fix`

```
fix(tokens): correct JWT expiration validation edge case

Tokens expiring at exactly the current time were incorrectly considered
valid. Changed the comparison from >= to > to properly reject expired
tokens.

Fixes #287
```

```
fix(ui): resolve focus trap not releasing in Safari modals

Added explicit focus restoration when closing modal dialogs in Safari.
Previously, keyboard focus was trapped after modal dismissal.
```

### `refactor`

```
refactor(attacks): extract common attack base class

Moved shared attack simulation logic into a base class to reduce
duplication across brute-force, credential-stuffing, and session-hijack
modules.
```

### `perf`

```
perf(core): optimize token validation with caching

Added LRU cache for validated tokens to reduce redundant cryptographic
operations. Cache hit rate averages 85% in typical usage patterns.
```

### `docs`

```
docs: update API reference for token endpoints

Added missing documentation for the /api/tokens/validate endpoint
including request/response schemas and error codes.
```

```
docs(readme): add Docker deployment instructions

Added step-by-step guide for deploying AuthShield Lab using Docker
Compose, including environment configuration.
```

### `style`

```
style(api): apply consistent formatting to route handlers

Reformatted route handlers to follow the project's Prettier
configuration. No logic changes.
```

### `test`

```
test(tokens): add edge case tests for JWT validation

Added tests for:
- Tokens with expired 'nbf' claims
- Tokens with missing 'iss' claim
- Tokens with invalid signature algorithms
- Tokens with oversized payloads
```

### `build`

```
build: upgrade Vite from v5 to v6

Updated build configuration for Vite 6 compatibility.
Switched from deprecated `build.rollupOptions` to new API.
```

### `ci`

```
ci: add accessibility test step to GitHub Actions

Added `npm run test:a11y` as a required check in the CI pipeline.
Runs axe-core and pa11y on all user-facing pages.
```

### `security`

```
security(auth): implement rate limiting on login endpoint

Added configurable rate limiting to prevent brute-force attacks:
- 5 attempts per minute per IP
- 15 minute lockout after 5 failed attempts
- Configurable via environment variables
```

### `accessibility`

```
accessibility(ui): add aria-live regions for lab progress updates

Lab completion status and score announcements are now properly
announced to screen readers via aria-live="polite" regions.
```

### `localization`

```
localization(i18n): add Spanish translations for LMS modules

Added complete Spanish translations for course pages, lab instructions,
and notification messages. RTL layout support remains for future
languages.
```

### `deps`

```
deps: update jsonwebtoken from 9.0.0 to 9.0.2

Patches CVE-2024-XXXXX (algorithm confusion vulnerability).
No breaking changes.
```

```
deps(auth): add jose library for JWT operations

Added jose as a more modern alternative to jsonwebtoken for
EdDSA and OKP key type support. jsonwebtoken remains for RSA/EC.
```

### `chore`

```
chore: update .gitignore to exclude new build artifacts

Added dist/ and .turbo/ directories to .gitignore.
```

---

## Breaking Changes

Breaking changes must be clearly indicated in the commit footer and are only allowed in major version releases.

### Format

```
feat(api)!: change authentication endpoint response format

BREAKING CHANGE: The /api/auth/login endpoint now returns a structured
response object instead of a plain token string. Clients must update
their parsing logic.

Migration guide: docs/migration/v5-to-v6.md
Closes #450
```

### Rules

- Use `!` after the type/scope to indicate a breaking change
- Include `BREAKING CHANGE:` in the footer with a description
- Provide a migration guide when possible
- Breaking changes are only merged into `main` during major version releases

---

## Scope Conventions

The scope is optional but encouraged. It should be the name of the module or area affected:

| Scope | Area |
|-------|------|
| `core` | Core authentication engine |
| `auth` | Authentication and authorization |
| `tokens` | JWT, OAuth, SAML token handling |
| `attacks` | Attack simulation library |
| `lms` | Learning management system |
| `labs` | Interactive lab runner |
| `api` | REST API server |
| `cli` | Command-line interface |
| `sdk` | JavaScript/TypeScript SDK |
| `ui` | React web interface |
| `analytics` | Analytics and reporting |
| `plugins` | Plugin framework |
| `i18n` | Internationalization |
| `db` | Database and migrations |
| `docs` | Documentation |
| `ci` | CI/CD pipeline |
| `deps` | Dependencies |

Use the module name from the repository structure. If the change spans multiple modules, use the most significant one. If no scope fits, omit the scope.

---

## Validation Rules

Commits are validated using [commitlint](https://commitlint.js.org/) with the following configuration:

### `.commitlintrc` Configuration

```json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "refactor",
        "perf",
        "docs",
        "style",
        "test",
        "build",
        "ci",
        "security",
        "accessibility",
        "localization",
        "deps",
        "chore"
      ]
    ],
    "type-case": [2, "always", "lower-case"],
    "type-empty": [2, "never"],
    "subject-empty": [2, "never"],
    "subject-full-stop": [2, "never", "."],
    "subject-case": [2, "never", ["sentence-case", "start-case", "pascal-case", "upper-case"]],
    "header-max-length": [2, "always", 72],
    "body-max-line-length": [2, "always", 80],
    "body-leading-blank": [2, "always"],
    "footer-leading-blank": [2, "always"],
    "scope-case": [2, "always", "lower-case"]
  }
}
```

### Pre-commit Hook

Commitlint is enforced via a Git pre-commit hook using [husky](https://typicode.github.io/husky/):

```bash
# Install husky
npx husky install

# Add commit-msg hook
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit $1'
```

### CI Validation

Commits are also validated in CI to catch any bypassed hooks:

```yaml
# .github/workflows/commitlint.yml
name: Commitlint
on: [pull_request]
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: wagoid/commitlint-github-action@v5
```

---

## Squash and Merge

When a pull request is merged using squash and merge, GitHub combines all commits into a single commit. The PR title is used as the commit message.

### PR Title Format

PR titles must follow the same conventional commit format:

```
feat(auth): add OAuth 2.0 PKCE flow support
```

### Rules

- PR title must follow commit message format
- Maintain a clean, descriptive PR title throughout review
- The squashed commit will use the PR title as the message
- Individual commit messages are preserved in the PR description

---

## Quick Reference

| Scenario | Type | Example |
|----------|------|---------|
| New feature | `feat` | `feat(auth): add MFA support` |
| Bug fix | `fix` | `fix(tokens): handle expired refresh tokens` |
| Code cleanup | `refactor` | `refactor(core): simplify token parser` |
| Speed improvement | `perf` | `perf(db): add index for user lookups` |
| Documentation | `docs` | `docs: update API reference` |
| Formatting only | `style` | `style(ui): fix indentation in modal` |
| New tests | `test` | `test(auth): add login failure tests` |
| Build changes | `build` | `build: upgrade TypeScript to 5.6` |
| CI changes | `ci` | `ci: add coverage reporting` |
| Security fix | `security` | `security: patch XSS in search input` |
| A11y fix | `accessibility` | `accessibility: add alt text to lab images` |
| Translation | `localization` | `localization: add French translations` |
| Dep update | `deps` | `deps: upgrade express to 5.1.0` |
| Maintenance | `chore` | `chore: update CI node version` |
