# Contributing to AuthShield Lab

Thank you for your interest in contributing to AuthShield Lab! This guide will walk you through everything you need to get started.

---

## Welcome

AuthShield Lab is an open-source, offline-first authentication security testing platform. We value contributions of all kinds — code, documentation, bug reports, feature requests, accessibility improvements, and translations. Every contribution matters.

Before contributing, please read and understand our [Code of Conduct](CODE_OF_CONDUCT.md). All participants are expected to follow it.

---

## Getting Started

### 1. Fork the Repository

Navigate to [https://github.com/anya12forger12-max/authshield-lab](https://github.com/anya12forger12-max/authshield-lab) and click the **Fork** button in the top-right corner.

### 2. Clone Your Fork

```bash
git clone https://github.com/<your-username>/authshield-lab.git
cd authshield-lab
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/anya12forger12-max/authshield-lab.git
```

### 4. Keep Your Fork Updated

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

---

## Development Environment Setup

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | ≥ 20.0 | Runtime |
| npm | ≥ 10.0 | Package manager |
| Git | ≥ 2.40 | Version control |
| Docker | ≥ 24.0 (optional) | Containerized development |

### Installation

```bash
# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env

# Start the development server
npm run dev
```

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Build for production |
| `npm test` | Run the full test suite |
| `npm run test:watch` | Run tests in watch mode |
| `npm run test:coverage` | Run tests with coverage report |
| `npm run test:a11y` | Run accessibility tests |
| `npm run lint` | Run ESLint |
| `npm run lint:fix` | Auto-fix linting issues |
| `npm run format` | Format code with Prettier |
| `npm run typecheck` | Run TypeScript type checking |

---

## Branch Naming Conventions

Use the following prefixes and formats:

| Branch Type | Format | Example |
|-------------|--------|---------|
| Feature | `feature/<short-description>` | `feature/oauth2-support` |
| Bug Fix | `fix/<short-description>` | `fix/session-timeout-logic` |
| Hotfix | `hotfix/<short-description>` | `hotfix/token-validation-bypass` |
| Documentation | `docs/<short-description>` | `docs/api-reference-update` |
| Security | `security/<short-description>` | `security/xss-in-login-form` |
| Experimental | `experimental/<short-description>` | `experimental/webauthn-integration` |
| Release | `release/<version>` | `release/5.1.0` |

**Rules:**
- Use lowercase letters and hyphens only
- Keep names concise but descriptive
- No special characters or spaces
- Prefix must match one of the types above

---

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/) strictly. See our full [Commit Conventions](governance/policies/COMMIT_CONVENTIONS.md) guide.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring without behavior change |
| `perf` | Performance improvement |
| `docs` | Documentation changes |
| `style` | Formatting, semicolons, etc. (no logic change) |
| `test` | Adding or updating tests |
| `build` | Build system or dependency changes |
| `ci` | CI/CD configuration changes |
| `security` | Security-related changes |
| `accessibility` | Accessibility improvements |
| `localization` | Translation or i18n changes |

### Examples

```
feat(auth): add OAuth 2.0 authorization code flow support

Implements the full OAuth 2.0 authorization code flow including:
- Authorization endpoint
- Token exchange
- Refresh token rotation

Closes #142
```

```
fix(tokens): correct JWT expiration validation edge case

Tokens expiring at exactly the current time were incorrectly
considered valid. Added proper less-than comparison.

Fixes #287
```

### Rules

- Subject line must be lowercase (except proper nouns)
- Subject line must not end with a period
- Subject line must be 72 characters or fewer
- Body must wrap at 80 characters
- Use imperative mood in the subject ("add" not "added")
- Reference issues in the footer

---

## Pull Request Process

### Before Submitting

1. **Sync your branch** with `main`:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks**:
   ```bash
   npm run lint
   npm run typecheck
   npm test
   npm run test:a11y
   ```

3. **Review your changes** — verify there are no debug statements, console logs, or placeholder code.

### Submitting a Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-branch-name
   ```

2. Open a pull request against `main` on the upstream repository.

3. Fill out the PR template completely:
   - **Title** — Use the conventional commit format
   - **Description** — Explain what changed and why
   - **Type of Change** — Check all that apply
   - **Testing** — Describe how you tested your changes
   - **Checklist** — Complete all items

4. Link any related issues using `Closes #<number>` or `Relates to #<number>`.

### PR Requirements

- [ ] All CI checks pass (lint, typecheck, tests, accessibility)
- [ ] At least 1 approving review from a maintainer
- [ ] No unresolved review comments
- [ ] Branch is up to date with `main`
- [ ] PR description is complete and accurate
- [ ] Breaking changes are documented
- [ ] New/updated features include tests
- [ ] Documentation is updated if applicable
- [ ] Accessibility impact is considered

---

## Code Style Requirements

### General

- **TypeScript** is required for all new code
- **No `any` types** — use proper typing or `unknown` with type guards
- **Functional style** preferred over class-based patterns
- **Immutability** — prefer `const`, avoid reassignment

### Formatting

- **Prettier** handles all formatting (do not override)
- **2 spaces** for indentation
- **Single quotes** for strings
- **Trailing commas** in multiline structures
- **Semicolons** always

### Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Variables | camelCase | `authToken` |
| Functions | camelCase | `validateToken()` |
| Classes | PascalCase | `TokenValidator` |
| Interfaces | PascalCase (no `I` prefix) | `TokenPayload` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Files | kebab-case | `token-validator.ts` |
| Directories | kebab-case | `auth-middleware/` |

### Imports

```typescript
// External packages first
import express from 'express';

// Then internal packages
import { AuthService } from '@authshield/core';

// Then local modules
import { validateRequest } from './middleware';

// Types last
import type { Request, Response } from 'express';
```

---

## Testing Requirements

### Coverage Targets

| Category | Minimum Coverage |
|----------|-----------------|
| Statements | 90% |
| Branches | 85% |
| Functions | 90% |
| Lines | 90% |

### Test Types

1. **Unit Tests** — Test individual functions and modules in isolation
2. **Integration Tests** — Test module interactions and API endpoints
3. **Accessibility Tests** — Automated WCAG 2.2 AA compliance checks
4. **E2E Tests** — Full user workflow testing (Playwright)

### Test Guidelines

- One test file per source file (e.g., `token.ts` → `token.test.ts`)
- Use descriptive test names that explain the expected behavior
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies, never hit real network services
- Test both success and failure paths
- Include edge cases and boundary conditions
- Accessibility tests must pass for all new UI components

```typescript
describe('TokenValidator', () => {
  describe('validate', () => {
    it('should return valid for a correctly signed token', () => {
      // Arrange
      const token = createTestToken({ valid: true });
      const validator = new TokenValidator(testSecret);

      // Act
      const result = validator.validate(token);

      // Assert
      expect(result.valid).toBe(true);
      expect(result.payload).toBeDefined();
    });

    it('should return invalid for a tampered token', () => {
      // Arrange
      const token = createTestToken({ valid: true });
      token.payload = 'tampered';
      const validator = new TokenValidator(testSecret);

      // Act
      const result = validator.validate(token);

      // Assert
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Token signature mismatch');
    });
  });
});
```

---

## Accessibility Requirements

Accessibility is a first-class concern. All contributions must meet WCAG 2.2 AA standards.

### UI Components

- All interactive elements must have accessible names
- Use semantic HTML elements (`<button>`, `<nav>`, `<main>`, etc.)
- All images must have meaningful `alt` text (or `alt=""` for decorative images)
- Form inputs must have associated `<label>` elements
- Color must not be the sole means of conveying information
- Focus indicators must be visible and meet minimum contrast ratios
- All functionality must be operable via keyboard alone

### Keyboard Navigation

- Tab order must follow logical reading order
- All interactive elements must be focusable
- Custom keyboard shortcuts must not conflict with assistive technology shortcuts
- Focus must be managed correctly in modals and dynamic content

### ARIA Usage

- Use ARIA roles, states, and properties only when native semantics are insufficient
- Test all ARIA usage with screen readers
- Never add `aria-label` to elements that already have visible text

### Testing

- Run `npm run test:a11y` before submitting
- Manually test with at least one screen reader (NVDA, JAWS, or VoiceOver)
- Verify keyboard navigation for any UI changes
- Check color contrast with browser dev tools

See [ACCESSIBILITY.md](ACCESSIBILITY.md) for the full accessibility statement.

---

## Security Reporting

Security vulnerabilities must **not** be reported through public GitHub Issues. Instead:

1. Email the security team at **security@authshieldlab.dev**
2. Use PGP encryption if possible (key available at [SECURITY.md](SECURITY.md))
3. Include a detailed description, reproduction steps, and potential impact
4. Allow 48 hours for initial response
5. Follow responsible disclosure — do not publicly disclose until a fix is available

See [SECURITY.md](SECURITY.md) for the complete security policy.

---

## Documentation Requirements

- All public APIs must have JSDoc/TSDoc comments
- New features must include user-facing documentation
- Code changes that affect behavior must update relevant docs
- README updates are required for new modules or commands
- Use clear, concise language; avoid jargon without explanation

---

## Issue Reporting

### Bug Reports

When filing a bug report, include:

- **Environment** — OS, browser, Node.js version
- **Steps to reproduce** — numbered, clear, minimal
- **Expected behavior** — what should happen
- **Actual behavior** — what happens instead
- **Screenshots/Logs** — if applicable
- **Accessibility impact** — does this affect users of assistive technology?

### Feature Requests

- Describe the problem or use case, not just the solution
- Explain who benefits from this feature
- Note any accessibility considerations
- Link to related issues or discussions

### Labels

| Label | Description |
|-------|-------------|
| `bug` | Confirmed bug report |
| `enhancement` | New feature or improvement |
| `security` | Security-related issue |
| `accessibility` | Accessibility issue |
| `documentation` | Documentation issue |
| `good first issue` | Suitable for newcomers |
| `help wanted` | Extra attention needed |
| `breaking change` | Introduces breaking changes |

---

## Review Process

See [governance/processes/REVIEW_PROCESS.md](governance/processes/REVIEW_PROCESS.md) for the complete review process.

### Summary

1. All PRs require at least 1 approving review
2. Reviewers must check code quality, tests, accessibility, and documentation
3. Authors must respond to all review comments
4. Stale PRs (no activity for 14 days) will be marked inactive
5. Maintainers may close PRs that do not meet quality standards after notification

---

## Merge Policy

- Only maintainers can merge pull requests
- Merges use **squash and merge** for feature branches
- **Rebase and merge** is used for hotfixes
- All CI checks must pass before merging
- Branch protection rules apply to `main` and `release/*` branches
- See [governance/policies/BRANCH_STRATEGY.md](governance/policies/BRANCH_STRATEGY.md) for details

---

## Questions?

If you have questions about contributing:

- Check the [Developer Onboarding Guide](docs/development/ONBOARDING.md)
- Open a [GitHub Discussion](https://github.com/anya12forger12-max/authshield-lab/discussions)
- See the [Support](SUPPORT.md) page

Thank you for helping make AuthShield Lab better!
