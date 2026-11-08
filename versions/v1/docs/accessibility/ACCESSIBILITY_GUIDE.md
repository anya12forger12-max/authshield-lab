# Accessibility Guide

This document describes the accessibility features and compliance approach for AuthShield Lab, targeting WCAG 2.2 AA compliance.

## Overview

AuthShield Lab is committed to being accessible to all users, including those with visual, auditory, motor, and cognitive disabilities. The platform follows WCAG 2.2 Level AA guidelines and implements the following accessibility features.

## Perceivable

### Text Alternatives

All non-text content includes text alternatives:

```tsx
// Images
<img src="chart.png" alt="Bar chart showing login attempts over the last 7 days" />

// Icons
<button aria-label="Close dialog">
  <CloseIcon />
</button>

// Decorative images
<img src="decoration.png" alt="" role="presentation" />
```

### Color and Contrast

**Color Contrast Requirements**:

| Element | Minimum Ratio |
|---------|--------------|
| Normal text | 4.5:1 |
| Large text (18px+) | 3:1 |
| UI components | 3:1 |
| Focus indicators | 3:1 |

**Theme Contrast Ratios**:

| Theme | Primary Text | Background | Ratio |
|-------|-------------|------------|-------|
| Light | #1a1a2e | #ffffff | 15.4:1 |
| Dark | #e0e0e0 | #1a1a2e | 12.8:1 |
| High Contrast | #000000 | #ffffff | 21:1 |

**Color-Blind Safe Palettes**:

```typescript
// Color-blind safe palette options
const colorBlindPalettes = {
  default: ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9'],
  deuteranopia: ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9'],
  protanopia: ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#56B4E9'],
  tritanopia: ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9'],
};
```

### Content Reflow

Content reflows without horizontal scrolling at 400% zoom:

```css
/* Responsive container */
.container {
  max-width: 100%;
  padding: 1rem;
}

/* Flexible grid */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

/* Text scaling support */
.text-base { font-size: 1rem; }
.text-sm { font-size: 0.875rem; }
.text-lg { font-size: 1.125rem; }
.text-xl { font-size: 1.25rem; }
.text-2xl { font-size: 1.5rem; }
```

### Images of Text

No images of text are used. All text is rendered as actual text elements.

## Operable

### Keyboard Navigation

All functionality is available via keyboard:

```tsx
// Focusable elements must be reachable via Tab
<button tabIndex={0} onClick={handleClick}>
  Click Me
</button>

// Custom keyboard handling
const handleKeyDown = (e: KeyboardEvent) => {
  switch (e.key) {
    case 'Enter':
    case ' ':
      e.preventDefault();
      activateElement();
      break;
    case 'ArrowDown':
      e.preventDefault();
      focusNext();
      break;
    case 'ArrowUp':
      e.preventDefault();
      focusPrevious();
      break;
    case 'Escape':
      e.preventDefault();
      closeDialog();
      break;
  }
};
```

**Keyboard Shortcuts**:

| Shortcut | Action |
|----------|--------|
| `Tab` | Move to next element |
| `Shift+Tab` | Move to previous element |
| `Enter` | Activate button/link |
| `Space` | Toggle checkbox/button |
| `Escape` | Close dialog/modal |
| `Arrow keys` | Navigate within groups |
| `Ctrl+K` | Open search |
| `Ctrl+/` | Toggle sidebar |
| `?` | Show shortcuts help |

### Skip Navigation

```tsx
// Skip to main content link
const SkipNavigation = () => (
  <a
    href="#main-content"
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:p-4 focus:bg-white focus:border focus:border-black"
  >
    Skip to main content
  </a>
);
```

### Focus Management

```css
/* Visible focus indicators */
:focus-visible {
  outline: 3px solid #0072B2;
  outline-offset: 2px;
}

/* Focus trap for modals */
.modal-content:focus {
  outline: none;
}

/* Remove default outline, replace with custom */
*:focus {
  outline: none;
}

*:focus-visible {
  outline: 3px solid #0072B2;
  outline-offset: 2px;
  border-radius: 2px;
}
```

### Timing

Users can adjust timing:

- Session timeout warnings with extend option
- No time limits on content consumption
- Animations can be paused or disabled
- Auto-playing content has controls

### Motion

```css
/* Respect user preference for reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Configurable in Settings:

```typescript
const useAccessibilityStore = create((set) => ({
  reducedMotion: false,
  setReducedMotion: (value: boolean) => set({ reducedMotion: value }),
}));
```

## Understandable

### Readable

Content is readable and understandable:

- Language attribute set on HTML element
- Consistent navigation patterns
- Clear heading hierarchy (h1 → h2 → h3)
- Plain language for UI text
- Abbreviations expanded on first use

```html
<html lang="en">
```

```tsx
// Heading hierarchy
<main>
  <h1>Dashboard</h1>
  <section>
    <h2>Recent Activity</h2>
    <h3>Today</h3>
    <h3>Yesterday</h3>
  </section>
  <section>
    <h2>System Status</h2>
  </section>
</main>
```

### Predictable

Interface behavior is predictable:

- Consistent navigation across pages
- Consistent identification of components
- No unexpected context changes on focus
- Form labels properly associated with inputs

```tsx
// Properly labeled inputs
<label htmlFor="email">Email Address</label>
<input id="email" type="email" name="email" aria-required="true" />

// Or using aria-label
<input
  type="email"
  aria-label="Email address"
  aria-required="true"
  aria-invalid={hasError}
  aria-describedby={hasError ? "email-error" : undefined}
/>
{hasError && (
  <span id="email-error" role="alert">
    Please enter a valid email address
  </span>
)}
```

### Input Assistance

Form validation provides clear feedback:

```tsx
const FormField = ({ label, error, required, children }) => (
  <div className="form-field">
    <label htmlFor={id}>
      {label}
      {required && <span aria-hidden="true" className="text-red-500">*</span>}
    </label>
    {children}
    {error && (
      <span id={`${id}-error`} className="error" role="alert">
        {error}
      </span>
    )}
  </div>
);
```

## Robust

### Compatible

Content is compatible with current and future user agents:

- Semantic HTML elements
- ARIA roles and properties where needed
- Valid HTML structure
- Progressive enhancement

```tsx
// Semantic elements
<nav aria-label="Main navigation">...</nav>
<main id="main-content">...</main>
<aside aria-label="Sidebar">...</aside>
<footer>...</footer>

// ARIA roles for custom components
<div role="tablist" aria-label="Module tabs">
  <button role="tab" aria-selected="true" aria-controls="panel-1">
    Dashboard
  </button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">
    Attacks
  </button>
</div>
<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
  {/* Dashboard content */}
</div>
```

### Status Messages

```tsx
// Live region for status updates
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

// Alert for important notifications
<div role="alert">
  Session will expire in 5 minutes.
</div>

// Log for dynamic content updates
<div role="log" aria-live="polite">
  {events.map(event => (
    <div key={event.id}>{event.message}</div>
  ))}
</div>
```

## Screen Reader Support

### ARIA Labels

```tsx
// Navigation landmark labels
<nav aria-label="Main navigation">
<nav aria-label="Breadcrumb navigation">

// Button labels
<button aria-label="Close dialog">×</button>
<button aria-label="Delete user: John Doe">Delete</button>

// Region labels
<section aria-label="Attack configuration">
<section aria-label="Results">
```

### Descriptions

```tsx
<input
  type="password"
  aria-describedby="password-requirements"
/>
<p id="password-requirements" className="text-sm text-gray-500">
  Password must be at least 8 characters with uppercase, lowercase, number, 
  and special character.
</p>
```

### Announcements

```tsx
// Custom hook for screen reader announcements
const useAnnounce = () => {
  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const el = document.createElement('div');
    el.setAttribute('aria-live', priority);
    el.setAttribute('aria-atomic', 'true');
    el.className = 'sr-only';
    document.body.appendChild(el);
    el.textContent = message;
    setTimeout(() => el.remove(), 1000);
  };
  return announce;
};

// Usage
const announce = useAnnounce();
announce('Attack simulation completed. 23 failed attempts detected.');
```

## Font Size Support

Users can adjust font size from 12px to 24px:

```typescript
// Theme configuration
const fontSizes = {
  sm: { base: '12px', scale: 0.875 },
  md: { base: '16px', scale: 1 },
  lg: { base: '18px', scale: 1.125 },
  xl: { base: '20px', scale: 1.25 },
  '2xl': { base: '24px', scale: 1.5 },
};

// CSS custom properties
:root {
  --font-size-base: 16px;
  --font-size-scale: 1;
}

.font-size-sm { --font-size-base: 12px; --font-size-scale: 0.875; }
.font-size-md { --font-size-base: 16px; --font-size-scale: 1; }
.font-size-lg { --font-size-base: 18px; --font-size-scale: 1.125; }
.font-size-xl { --font-size-base: 20px; --font-size-scale: 1.25; }
.font-size-2xl { --font-size-base: 24px; --font-size-scale: 1.5; }
```

## High Contrast Mode

```css
@media (forced-colors: active) {
  .button {
    border: 1px solid ButtonText;
  }
  
  .input {
    border: 1px solid ButtonText;
  }
  
  .card {
    border: 1px solid CanvasText;
  }
  
  :focus-visible {
    outline: 2px solid Highlight;
  }
}
```

## Testing Checklist

### Automated Testing

- [ ] axe-core integration in CI pipeline
- [ ] Lighthouse accessibility audit
- [ ] Color contrast validation in theme definitions

### Manual Testing

- [ ] Complete keyboard-only navigation through all modules
- [ ] Screen reader testing (NVDA, VoiceOver, JAWS)
- [ ] 200% zoom without horizontal scroll
- [ ] 400% zoom usability
- [ ] Reduced motion preference respected
- [ ] High contrast mode functional
- [ ] Form error messages announced
- [ ] Dynamic content updates announced
- [ ] Focus management in modals/dialogs
- [ ] Skip navigation links work

### Browser Testing

- Chrome: Keyboard + screen reader (ChromeVox)
- Firefox: Keyboard + screen reader (NVDA)
- Safari: Keyboard + screen reader (VoiceOver)
- Edge: Keyboard + screen reader (Narrator)

## Accessibility Statement

AuthShield Lab aims to meet WCAG 2.2 Level AA standards. We are committed to:

- Regular accessibility audits
- User testing with assistive technology users
- Continuous improvement of accessibility features
- Training for contributors on accessibility best practices

For accessibility issues or suggestions, please open a GitHub issue with the `accessibility` label.
