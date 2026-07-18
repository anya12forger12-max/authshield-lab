# Coding Standards

This document defines the coding standards for AuthShield Lab.

## General Principles

1. **Readability First**: Code is read more often than written
2. **Consistency**: Follow established patterns in the codebase
3. **Simplicity**: Prefer simple, clear solutions over clever ones
4. **DRY**: Don't Repeat Yourself, but don't over-abstract
5. **YAGNI**: You Aren't Gonna Need It - avoid premature abstraction

## Python Standards

### Style

- Follow PEP 8 (enforced by Ruff)
- Maximum line length: 88 characters
- Use double quotes for strings
- Use trailing commas in multi-line structures

### Type Hints

All function signatures must include type hints:

```python
# Good
def create_user(
    db: Session,
    email: str,
    name: str,
    role: Role = Role.STUDENT
) -> User:
    ...

# Bad
def create_user(db, email, name, role=Role.STUDENT):
    ...
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Functions | snake_case | `get_user_by_id` |
| Variables | snake_case | `user_count` |
| Classes | PascalCase | `UserService` |
| Constants | UPPER_SNAKE_CASE | `MAX_LOGIN_ATTEMPTS` |
| Private | _leading_underscore | `_validate_token` |
| Type Variables | PascalCase | `ModelType` |

### Docstrings

Use Google-style docstrings:

```python
def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Authenticate a user with email and password.

    Args:
        db: Database session
        user_email: User's email address
        password: Plain text password

    Returns:
        Authenticated User object or None if authentication fails

    Raises:
        ValueError: If email format is invalid
    """
    ...
```

### Imports

Order imports by:

1. Standard library
2. Third-party packages
3. Local application

```python
# Standard library
import os
from datetime import datetime, timedelta

# Third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local
from app.config import settings
from app.database import get_db
from app.models import User
```

### Error Handling

```python
# Specific exceptions
class AuthenticationError(Exception):
    pass

class RateLimitExceeded(Exception):
    pass

# Proper exception handling
try:
    user = await authenticate_user(email, password)
except AuthenticationError:
    raise HTTPException(
        status_code=401,
        detail="Invalid credentials"
    )
```

## TypeScript/React Standards

### Style

- Follow ESLint configuration
- Use 2-space indentation
- Use single quotes for strings
- Use semicolons
- Use trailing commas

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Functions | camelCase | `getUserById` |
| Variables | camelCase | `userCount` |
| Components | PascalCase | `UserProfile` |
| Types | PascalCase | `UserType` |
| Interfaces | PascalCase | `UserData` |
| Constants | UPPER_SNAKE_CASE | `MAX_LOGIN_ATTEMPTS` |
| CSS Classes | kebab-case | `user-profile` |

### Component Structure

```tsx
// Functional components only
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

export const Button = ({
  label,
  onClick,
  variant = 'primary',
  disabled = false
}: ButtonProps) => {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
};
```

### Hooks

Custom hooks return structured data:

```tsx
// Good - returns object
const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<User | null>(null);
  // ...
  return { user, login, logout, isAuthenticated };
};

// Bad - returns array for multiple values
const useAuth = () => {
  // ...
  return [user, login, logout, isAuthenticated];
};
```

### State Management

```tsx
// Zustand store structure
interface UserStore {
  users: User[];
  selectedUser: User | null;
  loading: boolean;
  error: string | null;
  
  fetchUsers: () => Promise<void>;
  selectUser: (user: User) => void;
  clearSelection: () => void;
}

const useUserStore = create<UserStore>((set) => ({
  users: [],
  selectedUser: null,
  loading: false,
  error: null,
  
  fetchUsers: async () => {
    set({ loading: true, error: null });
    try {
      const users = await api.getUsers();
      set({ users, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  
  selectUser: (user) => set({ selectedUser: user }),
  clearSelection: () => set({ selectedUser: null }),
}));
```

### File Organization

```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   └── index.ts
├── hooks/
│   ├── useAuth.ts
│   └── index.ts
├── stores/
│   ├── useUserStore.ts
│   └── index.ts
├── pages/
│   ├── Dashboard/
│   │   ├── Dashboard.tsx
│   │   ├── Dashboard.test.tsx
│   │   └── index.ts
│   └── index.ts
└── utils/
    ├── formatters.ts
    └── index.ts
```

## Testing Standards

### Python Tests

```python
import pytest
from app.services.user import UserService

class TestUserService:
    def test_create_user(self, db_session):
        """Test user creation with valid data."""
        service = UserService(db_session)
        user = service.create_user(
            email="test@example.com",
            name="Test User"
        )
        assert user.email == "test@example.com"
        assert user.name == "Test User"
    
    def test_create_user_invalid_email(self, db_session):
        """Test user creation with invalid email raises error."""
        service = UserService(db_session)
        with pytest.raises(ValueError):
            service.create_user(email="not-an-email", name="Test")
    
    @pytest.mark.parametrize("email,expected", [
        ("valid@example.com", True),
        ("invalid", False),
        ("@example.com", False),
    ])
    def test_validate_email(self, email, expected):
        """Test email validation."""
        assert validate_email(email) == expected
```

### TypeScript Tests

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with label', () => {
    render(<Button label="Click me" onClick={() => {}} />);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button label="Click me" onClick={handleClick} />);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  it('is disabled when disabled prop is true', () => {
    render(<Button label="Click me" onClick={() => {}} disabled />);
    expect(screen.getByText('Click me')).toBeDisabled();
  });
});
```

### Coverage Requirements

| Language | Minimum Coverage |
|----------|-----------------|
| Python | 80% |
| TypeScript | 75% |

## Git Standards

### Commit Messages

Follow Conventional Commits:

```
feat(auth): add OAuth2 simulation flow
fix(sessions): prevent token reuse after expiration
docs(guides): update installation instructions
chore(deps): update FastAPI to 0.109.0
test(attacks): add brute force simulation tests
```

### Branch Naming

```
feature/session-hijack-sim
fix/login-rate-limiter
docs/update-install-guide
chore/update-dependencies
refactor/auth-middleware
test/add-attack-unit-tests
```

### Pull Requests

- Title follows Conventional Commits format
- Description explains what and why
- All tests pass
- Code coverage meets minimums
- Documentation updated if needed
- No console.log or print statements
- No hardcoded values

## Code Review Checklist

### General

- [ ] Code follows naming conventions
- [ ] No commented-out code
- [ ] No magic numbers
- [ ] Error handling is comprehensive
- [ ] No security vulnerabilities introduced

### Python Specific

- [ ] Type hints on all functions
- [ ] Docstrings on public functions
- [ ] No bare except clauses
- [ ] Context managers for resources
- [ ] No mutable default arguments

### TypeScript Specific

- [ ] Explicit return types on exported functions
- [ ] Props interfaces defined
- [ ] No `any` types
- [ ] Proper key props in lists
- [ ] Memoization where needed

### Testing

- [ ] Tests cover new functionality
- [ ] Edge cases tested
- [ ] Error cases tested
- [ ] No flaky tests

### Documentation

- [ ] Code comments explain why, not what
- [ ] API documentation updated
- [ ] README updated if needed
- [ ] CHANGELOG entry added

## Documentation Standards

### Code Comments

```python
# Bad - explains what
x = x + 1  # increment x

# Good - explains why
x = x + 1  # Account for zero-based indexing in API response
```

### API Documentation

All public endpoints must include:

- Description
- Request parameters
- Response format
- Error cases
- Example values

### README Updates

Update README when:

- Adding new features
- Changing setup process
- Modifying configuration
- Updating dependencies
