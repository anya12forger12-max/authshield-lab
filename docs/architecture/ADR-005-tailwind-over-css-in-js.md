# ADR-005: Tailwind CSS over CSS-in-JS

## Status

Accepted

## Context

AuthShield Lab requires a styling solution for the React frontend. The application needs:

- Consistent design system across 20+ modules
- Theme support (5 themes: light, dark, high-contrast, dyslexia, solarized)
- Responsive design
- Accessibility features (focus indicators, reduced motion)
- Rapid UI development

We evaluated:

1. **Tailwind CSS**: Utility-first CSS framework
2. **CSS-in-JS** (Styled Components / Emotion): Component-level styling

## Decision

We chose **Tailwind CSS** for styling.

## Rationale

### Advantages of Tailwind CSS

- **Performance**: No runtime CSS-in-JS overhead; CSS is purged and minified at build time
- **Theme Support**: CSS custom properties integrate naturally with Tailwind's config for our 5+ themes
- **Bundle Size**: Purged CSS is typically smaller than CSS-in-JS runtime + generated styles
- **Design System**: Tailwind's configuration provides centralized design tokens (colors, spacing, typography)
- **Accessibility**: CSS custom properties for themes; easy focus-visible and prefers-reduced-motion support
- **Developer Experience**: IDE autocomplete for class names; visual feedback in editor
- **No Runtime Cost**: Styles are static CSS; no JavaScript execution for styling
- **Flexibility**: Works with any CSS approach; easy to add custom CSS when needed
- **Maintainability**: Changes to design tokens propagate automatically via configuration

### Why CSS-in-JS Wasn't Chosen

- **Runtime Overhead**: CSS-in-JS generates styles at runtime, adding to bundle size and execution time
- **SSR Complexity**: While not critical for Electron, SSR setup adds complexity
- **Theme Switching**: CSS-in-JS theme switching requires JavaScript execution; CSS custom properties are instant
- **Bundle Size**: Styled Components adds ~12KB gzipped; Emotion adds ~8KB
- **Learning Curve**: Tailwind's utility classes are more discoverable than custom CSS-in-JS patterns
- **Debugging**: Browser DevTools show utility classes; CSS-in-JS generates dynamic class names

### When Would We Reconsider

- If we need very dynamic styling based on runtime data
- If Tailwind's utility classes become too complex for our use cases
- If we add SSR requirements

## Consequences

### Positive

- Better performance with no runtime CSS generation
- Smaller production bundle size
- Excellent theme support via CSS custom properties
- Faster development with utility classes
- Easier debugging in browser DevTools
- Design tokens centralized in Tailwind config

### Negative

- HTML can become verbose with many utility classes
- Requires learning Tailwind's class naming conventions
- Less co-located than CSS-in-JS (styles are in className, not in component)

### Mitigations

- Use `@apply` for frequently repeated patterns
- Create component abstractions for complex patterns
- Use Tailwind plugins for custom utilities
- Maintain clear naming conventions in tailwind.config.js

## Implementation

```javascript
// tailwind.config.js
export default {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'var(--color-primary-50)',
          500: 'var(--color-primary-500)',
          900: 'var(--color-primary-900)',
        },
        // ... more theme-aware colors
      },
      fontSize: {
        base: 'var(--font-size-base)',
        scale: 'var(--font-size-scale)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

```tsx
// Component usage
const Button = ({ variant = 'primary', children }) => (
  <button
    className={`
      px-4 py-2 rounded-md font-medium
      transition-colors duration-200
      focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500
      ${variant === 'primary'
        ? 'bg-primary-500 text-white hover:bg-primary-600'
        : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
      }
    `}
  >
    {children}
  </button>
);
```
