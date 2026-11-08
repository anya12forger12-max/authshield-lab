# Contributing to AuthShield Lab

Thank you for your interest in contributing to AuthShield Lab! This guide will help you get started with the development workflow.

## Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/authshield-lab.git
cd authshield-lab
```

2. **Set up the backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

3. **Set up the frontend**

```bash
cd ../frontend
npm install
cp .env.example .env
```

4. **Run validation**

```bash
cd ..
./scripts/utilities/validate.sh
```

## Branch Naming

Use the following prefix convention for branches:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New functionality | `feature/session-hijack-sim` |
| `fix/` | Bug fixes | `fix/login-rate-limiter` |
| `docs/` | Documentation changes | `docs/update-install-guide` |
| `chore/` | Maintenance tasks | `chore/update-dependencies` |
| `refactor/` | Code restructuring | `refactor/auth-middleware` |
| `test/` | Adding or updating tests | `test/add-attack-unit-tests` |

Use kebab-case for branch names and include the issue number when applicable:

```bash
git checkout -b feature/123-mfa-enrollment
```

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only changes |
| `style` | Formatting, no code change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `chore` | Build process or auxiliary tool changes |
| `ci` | CI configuration changes |

### Scopes

| Scope | Description |
|-------|-------------|
| `auth` | Authentication module |
| `users` | User management |
| `sessions` | Session handling |
| `attacks` | Attack simulations |
| `defenses` | Defense mechanisms |
| `analytics` | Analytics module |
| `reports` | Report generation |
| `learning` | Learning center |
| `audit` | Audit logging |
| `ui` | Frontend components |
| `api` | Backend API |
| `db` | Database changes |
| `config` | Configuration |
| `deps` | Dependencies |

### Examples

```bash
git commit -m "feat(auth): add OAuth2 simulation flow"
git commit -m "fix(sessions): prevent token reuse after expiration"
git commit -m "docs(guides): update installation instructions for macOS"
git commit -m "chore(deps): update FastAPI to 0.109.0"
git commit -m "test(attacks): add brute force simulation tests"
```

## Pull Request Process

1. **Create your branch** from `main`
2. **Make your changes** following the coding standards
3. **Write or update tests** for any new functionality
4. **Update documentation** if your change affects user-facing behavior
5. **Run the full validation suite**:
   ```bash
   ./scripts/utilities/validate.sh
   ```
6. **Push your branch** and create a pull request
7. **Fill out the PR template** completely
8. **Request review** from at least one maintainer
9. **Address review feedback** promptly
10. **Squash and merge** after approval

### PR Title

Use the same Conventional Commits format for PR titles:

```
feat(auth): implement SAML SSO simulation
```

### PR Description

The PR template will guide you through providing:

- Summary of changes
- Related issue(s)
- Type of change
- Testing performed
- Checklist verification

## Code Review Checklist

All pull requests must pass the following review criteria:

### Code Quality
- [ ] Code follows the project coding standards
- [ ] No commented-out code left in the diff
- [ ] No `console.log` or `print` debug statements
- [ ] Error handling is comprehensive
- [ ] No magic numbers or hardcoded values

### Testing
- [ ] Unit tests cover new functionality
- [ ] All existing tests pass
- [ ] Edge cases are tested
- [ ] No flaky tests introduced

### Documentation
- [ ] Code has appropriate docstrings/comments
- [ ] API changes are documented
- [ ] README updated if needed
- [ ] CHANGELOG entry added

### Security
- [ ] No secrets or credentials in code
- [ ] Input validation is present
- [ ] No SQL injection vectors
- [ ] XSS prevention applied
- [ ] Localhost-only restriction maintained

### Performance
- [ ] No N+1 query problems
- [ ] No unnecessary re-renders
- [ ] Memory leaks addressed
- [ ] Database queries optimized

## Testing Requirements

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html
```

- Minimum 80% code coverage for new code
- Use `pytest` fixtures for test setup
- Mock external dependencies
- Test both success and failure paths

### Frontend Tests

```bash
cd frontend
npm run test -- --coverage
```

- Component tests for new React components
- Integration tests for user flows
- Minimum 75% code coverage for new code

### Validation

```bash
./scripts/utilities/validate.sh
```

This runs all linting, type checking, and tests in sequence.

## Documentation Requirements

- All public API endpoints must have docstrings
- New features require a guide entry in `docs/guides/`
- Architecture changes require an ADR in `docs/architecture/DECISIONS.md`
- Breaking changes must be documented in `CHANGELOG.md`
- Code examples must be tested and working

## Code Style

### Python

- Follow PEP 8 (enforced by Ruff)
- Type hints required for all function signatures
- Maximum line length: 88 characters (Black default)
- Use `snake_case` for functions and variables
- Use `PascalCase` for classes

### TypeScript/JavaScript

- Follow the ESLint configuration
- Use `camelCase` for functions and variables
- Use `PascalCase` for components and types
- Prefer `const` over `let`
- Use explicit return types for functions

## Getting Help

- Check existing documentation in `docs/`
- Search existing issues before creating new ones
- Join discussions in GitHub Discussions
- Review the architecture docs for context

## Recognition

Contributors will be recognized in:

- The project README
- Release notes
- The CONTRIBUTORS file

Thank you for helping make AuthShield Lab better!
