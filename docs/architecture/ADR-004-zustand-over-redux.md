# ADR-004: Zustand over Redux

## Status

Accepted

## Context

AuthShield Lab requires client-side state management for the React frontend. The application has complex state needs including:

- User authentication and session state
- Theme and accessibility preferences
- Module-specific state (attacks, defenses, sessions, etc.)
- UI state (sidebar, modals, notifications)
- Real-time data updates

We evaluated:

1. **Zustand**: Minimal, hook-based state management
2. **Redux Toolkit**: Industry-standard with Redux ecosystem

## Decision

We chose **Zustand** for state management.

## Rationale

### Advantages of Zustand

- **Simplicity**: Minimal API surface with no boilerplate (no actions, reducers, dispatch, providers)
- **Hook-Based**: Uses standard React hooks; no special providers or wrappers needed
- **Bundle Size**: ~1KB gzipped vs Redux Toolkit at ~11KB
- **Performance**: No re-renders from unrelated state changes by default
- **TypeScript**: First-class TypeScript support with excellent inference
- **DevTools**: Redux DevTools compatibility for debugging
- **Middleware**: Built-in middleware for persistence, devtools, immer, and subscriptions
- **Flexibility**: Works with or without React; can be used in any JavaScript environment
- **No Providers**: No Provider wrapping required at component tree root

### Why Redux Toolkit Wasn't Chosen

- **Boilerplate**: Redux requires actions, action creators, reducers, selectors, and dispatch
- **Provider Requirement**: Redux requires Provider wrapping at the app root
- **Learning Curve**: Redux's concepts (actions, reducers, middleware, thunks) add complexity
- **Bundle Size**: Redux Toolkit is significantly larger than Zustand
- **Overkill**: Redux's patterns are designed for very large applications; our needs are moderate
- **Re-render Concerns**: Redux can cause unnecessary re-renders without careful selector optimization

### When Would We Reconsider

- If state management complexity grows significantly (30+ stores)
- If we need time-travel debugging beyond what Zustand DevTools provides
- If we add features requiring Redux's middleware ecosystem (e.g., complex offline sync)

## Consequences

### Positive

- Simpler, more readable state management code
- Faster development with less boilerplate
- Smaller bundle size
- Better TypeScript experience
- Easier mental model for contributors

### Negative

- Smaller ecosystem compared to Redux
- Less community content and tutorials
- Fewer pre-built middleware solutions

### Mitigations

- Document state management patterns and conventions
- Use Zustand's DevTools middleware for debugging
- Create shared patterns for common state operations

## Implementation

```typescript
// Example store structure
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

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
      immer((set) => ({
        user: null,
        token: null,
        isAuthenticated: false,
        
        login: async (credentials) => {
          const { user, token } = await api.login(credentials);
          set((state) => {
            state.user = user;
            state.token = token;
            state.isAuthenticated = true;
          });
        },
        
        logout: () => {
          set((state) => {
            state.user = null;
            state.token = null;
            state.isAuthenticated = false;
          });
        },
      })),
      { name: 'auth-storage' }
    ),
    { name: 'Auth' }
  )
);
```
