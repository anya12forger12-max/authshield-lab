# React / TypeScript Standards — AuthShield Lab

This document defines the coding standards for all React and TypeScript code in
the Electron + React frontend of the AuthShield Lab project.

---

## 1. Project Structure

```
src/
├── components/              # Shared/reusable UI components
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   └── index.ts             # Barrel export
├── hooks/                   # Custom hooks
│   ├── useAuth.ts
│   ├── useAuditLogs.ts
│   └── index.ts
├── pages/                   # Route-level page components
│   ├── Login/
│   │   ├── LoginPage.tsx
│   │   └── LoginPage.test.tsx
│   └── Dashboard/
│       ├── DashboardPage.tsx
│       └── DashboardPage.test.tsx
├── stores/                  # Zustand stores
│   ├── authStore.ts
│   └── uiStore.ts
├── services/                # API client functions
│   ├── api.ts
│   ├── auth.ts
│   └── users.ts
├── types/                   # Shared TypeScript types
│   ├── api.ts
│   └── models.ts
├── utils/                   # Pure utility functions
│   ├── formatDate.ts
│   └── validators.ts
├── styles/                  # Global styles, theme
│   └── theme.ts
└── App.tsx
```

### Rules

- One component per file. Component name matches file name.
- Use index.ts barrel files to simplify imports.
- Co-locate test files with their components.
- Pages handle routing and data fetching; components are presentation-focused.

---

## 2. Component Patterns

### 2.1 Functional components only

No class components. All components use function declarations with explicit
return types.

```tsx
interface UserCardProps {
  user: User;
  onSelect: (userId: string) => void;
}

export function UserCard({ user, onSelect }: UserCardProps): JSX.Element {
  return (
    <div className="user-card" onClick={() => onSelect(user.id)}>
      <h3>{user.username}</h3>
      <p>{user.email}</p>
    </div>
  );
}
```

### 2.2 Props interface naming

- Interface name: `{ComponentName}Props`
- Always define props as an interface (not a type alias) directly above the
  component definition.
- Destructure props in the function signature.

```tsx
interface LoginFormProps {
  onSubmit: (credentials: LoginCredentials) => void;
  isLoading: boolean;
  error?: string;
}

export function LoginForm({ onSubmit, isLoading, error }: LoginFormProps): JSX.Element {
  // ...
}
```

### 2.3 Export convention

- Named exports for components (not default exports).
- Default exports only for page components (used by route definitions).

```tsx
// components/Button/Button.tsx — named export
export function Button({ ... }: ButtonProps): JSX.Element { ... }

// pages/Login/LoginPage.tsx — default export
export default function LoginPage(): JSX.Element { ... }
```

---

## 3. State Management (Zustand)

### 3.1 Store definition

```ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        token: null,
        isAuthenticated: false,

        login: async (credentials: LoginCredentials) => {
          const response = await authApi.login(credentials);
          set({
            user: response.user,
            token: response.token,
            isAuthenticated: true,
          });
        },

        logout: () => {
          set({ user: null, token: null, isAuthenticated: false });
        },
      }),
      { name: 'auth-storage' },
    ),
    { name: 'AuthStore' },
  ),
);
```

### 3.2 Rules

- Use `devtools` middleware in all stores for Redux DevTools compatibility.
- Use `persist` middleware for state that must survive page reloads (auth tokens,
  user preferences).
- Keep stores small and focused. One store per domain.
- Never store derived data in a store; compute it with selectors.

### 3.3 Selectors

```tsx
// Bad — causes unnecessary re-renders
const { user, isAuthenticated } = useAuthStore();

// Good — granular subscription
const user = useAuthStore((state) => state.user);
const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
```

---

## 4. Custom Hooks

### 4.1 Naming

- Hook files: `use{Thing}.ts`
- Hook functions: `use{Thing}`

### 4.2 Data-fetching hook pattern

```ts
import { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '../stores/authStore';

interface UseUsersResult {
  users: User[];
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useUsers(): UseUsersResult {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const token = useAuthStore((state) => state.token);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await usersApi.list(token);
      setUsers(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return { users, isLoading, error, refetch: fetchUsers };
}
```

### 4.3 Rules

- Prefix all custom hooks with `use`.
- Return a consistent shape: `{ data, isLoading, error, refetch }`.
- Never call hooks conditionally.
- Keep hooks focused on a single concern.

---

## 5. Event Handler Naming

| Pattern        | Convention               | Example                    |
| -------------- | ------------------------ | -------------------------- |
| Click handler  | `handle{Event}`         | `handleClick`, `handleClose` |
| Submit handler | `on{Action}`            | `onSubmit`, `onLogin`      |
| Change handler | `handle{Field}Change`   | `handleEmailChange`        |
| Prop callback  | `on{Action}`            | `onSelect`, `onDelete`     |

```tsx
export function LoginForm({ onSubmit, isLoading }: LoginFormProps): JSX.Element {
  const [email, setEmail] = useState('');

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ email });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={email} onChange={handleEmailChange} />
      <button type="submit" disabled={isLoading}>
        Log In
      </button>
    </form>
  );
}
```

---

## 6. Accessibility Requirements

### 6.1 ARIA attributes

- All interactive elements must be reachable via keyboard.
- Use `aria-label` or `aria-labelledby` for icon-only buttons.
- Use `aria-describedby` for helper text linked to form inputs.
- Use `role` only when semantic HTML is insufficient.

```tsx
<button
  onClick={handleClose}
  aria-label="Close dialog"
  className="icon-button"
>
  <CloseIcon />
</button>
```

### 6.2 Keyboard navigation

- All buttons and links must be focusable.
- Implement `onKeyDown` for custom interactive widgets.
- Use `tabIndex={0}` for non-interactive elements that must be focusable.
- Trap focus inside modals and dialogs.

```tsx
function Modal({ onClose, children }: ModalProps): JSX.Element {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    modalRef.current?.focus();
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
  };

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
      onKeyDown={handleKeyDown}
    >
      {children}
    </div>
  );
}
```

### 6.3 Focus management

- After an action (e.g., deleting an item), move focus to the next logical
  element.
- Restore focus when closing overlays.
- Use `useRef` + `.focus()` for programmatic focus management.

### 6.4 Color contrast

- All text must meet WCAG 2.1 AA contrast ratio (4.5:1 for normal text,
  3:1 for large text).
- Never convey information through color alone.

---

## 7. Performance Patterns

### 7.1 React.memo

Wrap components that receive the same props frequently but depend on reference
stability.

```tsx
interface AuditLogRowProps {
  log: AuditLog;
  onClick: (id: string) => void;
}

export const AuditLogRow = React.memo(function AuditLogRow({
  log,
  onClick,
}: AuditLogRowProps): JSX.Element {
  return (
    <tr onClick={() => onClick(log.id)}>
      <td>{log.action}</td>
      <td>{formatDate(log.createdAt)}</td>
    </tr>
  );
});
```

### 7.2 useMemo

Use for expensive computations derived from props or state.

```tsx
export function AuditLogTable({ logs, filter }: AuditLogTableProps): JSX.Element {
  const filteredLogs = useMemo(() => {
    if (!filter) return logs;
    return logs.filter((log) => log.action.includes(filter));
  }, [logs, filter]);

  return (
    <table>
      {filteredLogs.map((log) => (
        <AuditLogRow key={log.id} log={log} onClick={handleClick} />
      ))}
    </table>
  );
}
```

### 7.3 useCallback

Use to maintain referential stability for functions passed to memoized
children or used in `useEffect` dependencies.

```tsx
export function AuditLogPage(): JSX.Element {
  const [page, setPage] = useState(1);

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  return <Pagination page={page} onChange={handlePageChange} />;
}
```

### 7.4 Rules

- Do not wrap every component in `React.memo`. Only use when profiling
  shows a re-render bottleneck.
- Prefer stable references from Zustand selectors over `useCallback` + props.
- Lazy-load page components with `React.lazy()`.

---

## 8. Error Boundaries

```tsx
import React, { Component, type ErrorInfo, type ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('ErrorBoundary caught:', error, info.componentStack);
    // Report to error tracking service
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div role="alert">
            <h2>Something went wrong</h2>
            <p>{this.state.error?.message}</p>
            <button onClick={() => this.setState({ hasError: false, error: null })}>
              Try again
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
```

### Rules

- Wrap each route-level component in an `ErrorBoundary`.
- Provide a meaningful fallback UI, not just a blank screen.
- Log errors to an external service in `componentDidCatch`.

---

## 9. Suspense Patterns

```tsx
import { Suspense, lazy } from 'react';

const DashboardPage = lazy(() => import('./pages/Dashboard/DashboardPage'));

export function App(): JSX.Element {
  return (
    <ErrorBoundary>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
}
```

### Rules

- Use `Suspense` boundaries around lazy-loaded components.
- Always provide a fallback component (never `null`).
- Combine with `ErrorBoundary` for resilient loading.

---

## 10. Testing Components

### 10.1 React Testing Library patterns

```tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('calls onSubmit with credentials', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();

    render(<LoginForm onSubmit={onSubmit} isLoading={false} />);

    await user.type(screen.getByLabelText(/email/i), 'alice@example.com');
    await user.type(screen.getByLabelText(/password/i), 'secret123');
    await user.click(screen.getByRole('button', { name: /log in/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'alice@example.com',
      password: 'secret123',
    });
  });

  it('displays error message', () => {
    render(<LoginForm onSubmit={vi.fn()} isLoading={false} error="Invalid credentials" />);
    expect(screen.getByRole('alert')).toHaveTextContent('Invalid credentials');
  });

  it('disables submit while loading', () => {
    render(<LoginForm onSubmit={vi.fn()} isLoading={true} />);
    expect(screen.getByRole('button', { name: /log in/i })).toBeDisabled();
  });
});
```

### 10.2 Testing rules

- Query by accessible roles, labels, and text — not test IDs.
- Use `userEvent` over `fireEvent` for realistic interactions.
- Wrap async assertions in `waitFor`.
- Mock API calls at the service layer, not inside components.
- Test one behavior per `it` block.
- Aim for behavior-focused tests, not implementation-focused tests.
