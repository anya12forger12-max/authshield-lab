# ADR-001: Electron + React over Flutter

## Status

Accepted

## Context

AuthShield Lab requires a cross-platform desktop application that can run on Windows, macOS, and Linux. The application needs a rich user interface with complex interactive components, real-time data visualization, and integration with a Python backend.

We evaluated two primary options:

1. **Electron + React + TypeScript**: Web technologies wrapped in a native shell
2. **Flutter**: Google's cross-platform UI framework using Dart

## Decision

We chose **Electron + React + TypeScript** for the frontend.

## Rationale

### Advantages of Electron + React

- **Team Expertise**: The team has extensive experience with React and TypeScript, reducing onboarding time
- **Ecosystem**: React has a massive ecosystem of libraries, components, and tools that directly apply to our needs (charts, tables, forms, accessibility)
- **Web Standards**: Using HTML, CSS, and JavaScript means we can leverage existing web knowledge and documentation
- **Python Integration**: Electron's Node.js layer provides seamless integration with our Python backend via IPC, child processes, or HTTP
- **Developer Experience**: Hot module replacement, excellent debugging tools (React DevTools, Chrome DevTools), and mature build tooling
- **Accessibility**: Web platform has built-in accessibility primitives (ARIA, semantic HTML, keyboard navigation) that React can leverage directly
- **CSS Flexibility**: Tailwind CSS and CSS custom properties provide powerful theming capabilities needed for our 5+ theme support
- **Testing**: Mature testing ecosystem with Vitest, Testing Library, and Playwright

### Disadvantages of Flutter

- **Dart Language**: Learning Dart adds overhead; fewer team members have Flutter experience
- **Desktop Maturity**: Flutter's desktop support, while improving, is less mature than Electron's
- **Python Integration**: Flutter requires additional bridging (method channels, FFI) to communicate with Python
- **Accessibility**: Flutter's desktop accessibility is less mature than web platform accessibility
- **Ecosystem**: Fewer pre-built components for complex enterprise UI patterns

### When Would We Reconsider

- If Electron's resource consumption becomes unacceptable for our users
- If Flutter's desktop and accessibility support significantly improves
- If we need mobile support as a primary requirement

## Consequences

### Positive

- Faster development with existing React expertise
- Rich component ecosystem for complex UI needs
- Native web accessibility features available immediately
- Seamless Python backend integration
- Excellent developer tooling

### Negative

- Larger application size due to Chromium bundling (~150MB)
- Higher memory usage compared to native applications
- Dependence on Electron's release cycle for security updates

### Mitigations

- Implement code splitting to reduce initial load
- Use lazy loading for heavy components
- Monitor memory usage and optimize rendering
- Stay current with Electron security updates
