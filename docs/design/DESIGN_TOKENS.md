# Design Tokens — AuthShield Lab

> The single source of truth for all visual design values. Every component consumes these tokens — never hardcode values.

---

## Token Architecture

Tokens are organized in three layers:

1. **Primitive tokens** — raw values (colors, sizes, fonts)
2. **Semantic tokens** — purpose-driven aliases (e.g., `--color-text-primary`)
3. **Component tokens** — component-specific overrides (e.g., `--button-bg-primary`)

All components use semantic tokens. Semantic tokens reference primitive tokens. This ensures theme changes propagate automatically.

---

## Color Tokens

### Primary

| Token | CSS Variable | Light Value | Dark Value | Usage |
|---|---|---|---|---|
| blue-50 | `--color-primary-50` | #eff6ff | #1e3a5f | Lightest primary |
| blue-100 | `--color-primary-100` | #dbeafe | #1e40af | Hover backgrounds |
| blue-200 | `--color-primary-200` | #bfdbfe | #2563eb | Borders, subtle indicators |
| blue-300 | `--color-primary-300` | #93c5fd | #3b82f6 | Light interactive states |
| blue-400 | `--color-primary-400` | #60a5fa | #60a5fa | Default interactive |
| blue-500 | `--color-primary-500` | #3b82f6 | #60a5fa | Primary buttons, links |
| blue-600 | `--color-primary-600` | #2563eb | #3b82f6 | **Default primary** |
| blue-700 | `--color-primary-700` | #1d4ed8 | #2563eb | Hover primary |
| blue-800 | `--color-primary-800` | #1e40af | #1d4ed8 | Active primary |
| blue-900 | `--color-primary-900` | #1e3a8a | #1e3a8a | Darkest primary |

### Secondary (Slate)

| Token | CSS Variable | Light Value | Dark Value | Usage |
|---|---|---|---|---|
| slate-50 | `--color-secondary-50` | #f8fafc | #1e293b | Lightest secondary |
| slate-100 | `--color-secondary-100` | #f1f5f9 | #334155 | Secondary hover bg |
| slate-200 | `--color-secondary-200` | #e2e8f0 | #475569 | Borders |
| slate-300 | `--color-secondary-300` | #cbd5e1 | #64748b | Subtle borders |
| slate-400 | `--color-secondary-400` | #94a3b8 | #94a3b8 | Placeholder text |
| slate-500 | `--color-secondary-500` | #64748b | #94a3b8 | Secondary text |
| slate-600 | `--color-secondary-600` | #475569 | #cbd5e1 | **Default secondary** |
| slate-700 | `--color-secondary-700` | #334155 | #e2e8f0 | Strong secondary |
| slate-800 | `--color-secondary-800` | #1e293b | #f1f5f9 | Emphasized secondary |
| slate-900 | `--color-secondary-900` | #0f172a | #f8fafc | Darkest secondary |

### Accent (Emerald)

| Token | CSS Variable | Light Value | Dark Value | Usage |
|---|---|---|---|---|
| emerald-50 | `--color-accent-50` | #ecfdf5 | #064e3b | Lightest accent |
| emerald-100 | `--color-accent-100` | #d1fae5 | #065f46 | Success bg tints |
| emerald-200 | `--color-accent-200` | #a7f3d0 | #047857 | Success borders |
| emerald-300 | `--color-accent-300` | #6ee7b7 | #10b981 | Light success |
| emerald-400 | `--color-accent-400` | #34d399 | #34d399 | Success interactive |
| emerald-500 | `--color-accent-500` | #10b981 | #34d399 | **Default accent** |
| emerald-600 | `--color-accent-600` | #059669 | #10b981 | Accent hover |
| emerald-700 | `--color-accent-700` | #047857 | #059669 | Accent active |
| emerald-800 | `--color-accent-800` | #065f46 | #047857 | Strong accent |
| emerald-900 | `--color-accent-900` | #064e3b | #064e3b | Darkest accent |

### Background

| Token | CSS Variable | Light Value | Dark Value | Usage |
|---|---|---|---|---|
| bg-primary | `--color-bg-primary` | #ffffff | #0f172a | Main background |
| bg-secondary | `--color-bg-secondary` | #f8fafc | #1e293b | Alternate background |
| bg-tertiary | `--color-bg-tertiary` | #f1f5f9 | #334155 | Subtle background |

### Surface

| Token | CSS Variable | Light Value | Dark Value | Usage |
|---|---|---|---|---|
| surface-raised | `--color-surface-raised` | #ffffff | #1e293b | Cards, dialogs |
| surface-overlay | `--color-surface-overlay` | #ffffff | #334155 | Popovers, dropdowns |
| surface-sunken | `--color-surface-sunken` | #f1f5f9 | #0f172a | Inset areas |

### Text

| Token | CSS Variable | Light Value | Dark Value | Usage |
|---|---|---|---|---|
| text-primary | `--color-text-primary` | #0f172a | #f8fafc | Headings, body |
| text-secondary | `--color-text-secondary` | #475569 | #cbd5e1 | Descriptions, labels |
| text-tertiary | `--color-text-tertiary` | #64748b | #94a3b8 | Placeholders |
| text-disabled | `--color-text-disabled` | #94a3b8 | #475569 | Disabled text |
| text-inverse | `--color-text-inverse` | #ffffff | #0f172a | Text on dark bg |
| text-link | `--color-text-link` | #2563eb | #60a5fa | Links |
| text-link-hover | `--color-text-link-hover` | #1d4ed8 | #93c5fd | Link hover |

### Borders

| Token | CSS Variable | Light Value | Dark Value | Usage |
|---|---|---|---|---|
| border-default | `--color-border-default` | #e2e8f0 | #334155 | Default borders |
| border-strong | `--color-border-strong` | #cbd5e1 | #475569 | Emphasized borders |
| border-focus | `--color-border-focus` | #3b82f6 | #60a5fa | Focus indicators |
| border-error | `--color-border-error` | #ef4444 | #f87171 | Error borders |
| border-success | `--color-border-success` | #10b981 | #34d399 | Success borders |

---

## Semantic Status Tokens

| Token | CSS Variable | Light Value | Dark Value | Usage |
|---|---|---|---|---|
| error | `--color-error` | #ef4444 | #f87171 | Errors, destructive |
| error-light | `--color-error-light` | #fef2f2 | #450a0a | Error backgrounds |
| error-text | `--color-error-text` | #dc2626 | #fca5a5 | Error text |
| warning | `--color-warning` | #f59e0b | #fbbf24 | Warnings, caution |
| warning-light | `--color-warning-light` | #fffbeb | #451a03 | Warning backgrounds |
| warning-text | `--color-warning-text` | #d97706 | #fcd34d | Warning text |
| success | `--color-success` | #10b981 | #34d399 | Success, complete |
| success-light | `--color-success-light` | #ecfdf5 | #022c22 | Success backgrounds |
| success-text | `--color-success-text` | #059669 | #6ee7b7 | Success text |
| info | `--color-info` | #3b82f6 | #60a5fa | Information |
| info-light | `--color-info-light` | #eff6ff | #1e3a5f | Info backgrounds |
| info-text | `--color-info-text` | #2563eb | #93c5fd | Info text |

---

## Neutral Scale

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| gray-50 | `--color-gray-50` | #f9fafb | Lightest neutral |
| gray-100 | `--color-gray-100` | #f3f4f6 | Alternate bg |
| gray-200 | `--color-gray-200` | #e5e7eb | Borders |
| gray-300 | `--color-gray-300` | #d1d5db | Strong borders |
| gray-400 | `--color-gray-400` | #9ca3af | Placeholder, disabled |
| gray-500 | `--color-gray-500` | #6b7280 | Secondary text |
| gray-600 | `--color-gray-600` | #4b5563 | Strong secondary |
| gray-700 | `--color-gray-700` | #374151 | Emphasized |
| gray-800 | `--color-gray-800` | #1f2937 | Dark surfaces |
| gray-900 | `--color-gray-900` | #111827 | Darkest |
| gray-950 | `--color-gray-950` | #030712 | Near black |

---

## Typography Tokens

### Font Families

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| font-sans | `--font-family-sans` | 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif | UI text |
| font-mono | `--font-family-mono` | 'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace | Code, commands |
| font-heading | `--font-family-heading` | 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif | Headings |

### Font Sizes

| Token | CSS Variable | Value | Pixel Equivalent |
|---|---|---|---|
| text-xs | `--font-size-xs` | 0.75rem | 12px |
| text-sm | `--font-size-sm` | 0.875rem | 14px |
| text-base | `--font-size-base` | 1rem | 16px |
| text-lg | `--font-size-lg` | 1.125rem | 18px |
| text-xl | `--font-size-xl` | 1.25rem | 20px |
| text-2xl | `--font-size-2xl` | 1.5rem | 24px |
| text-3xl | `--font-size-3xl` | 1.875rem | 30px |
| text-4xl | `--font-size-4xl` | 2.25rem | 36px |

### Font Weights

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| weight-regular | `--font-weight-regular` | 400 | Body text |
| weight-medium | `--font-weight-medium` | 500 | Labels, emphasis |
| weight-semibold | `--font-weight-semibold` | 600 | Headings, buttons |
| weight-bold | `--font-weight-bold` | 700 | Strong emphasis |

### Line Heights

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| leading-none | `--line-height-none` | 1 | Headings (display) |
| leading-tight | `--line-height-tight` | 1.25 | Headings |
| leading-normal | `--line-height-normal` | 1.5 | Body text |
| leading-relaxed | `--line-height-relaxed` | 1.75 | Long-form reading |

### Letter Spacing

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| tracking-tight | `--letter-spacing-tight` | -0.01em | Large headings |
| tracking-normal | `--letter-spacing-normal` | 0em | Body text |
| tracking-wide | `--letter-spacing-wide` | 0.025em | Overlines, labels |
| tracking-wider | `--letter-spacing-wider` | 0.05em | All caps labels |

---

## Spacing Tokens

All spacing values are based on a 4px grid. Use only these tokens — never arbitrary values.

| Token | CSS Variable | Value | Common Usage |
|---|---|---|---|
| space-0 | `--spacing-0` | 0px | Reset |
| space-0.5 | `--spacing-0-5` | 2px | Micro gaps |
| space-1 | `--spacing-1` | 4px | Tight spacing |
| space-1.5 | `--spacing-1-5` | 6px | Compact spacing |
| space-2 | `--spacing-2` | 8px | Default small gap |
| space-3 | `--spacing-3` | 12px | Default medium gap |
| space-4 | `--spacing-4` | 16px | Default large gap, gutters |
| space-5 | `--spacing-5` | 20px | Section spacing |
| space-6 | `--spacing-6` | 24px | Card padding |
| space-8 | `--spacing-8` | 32px | Section padding |
| space-10 | `--spacing-10` | 40px | Large section padding |
| space-12 | `--spacing-12` | 48px | Page margins |
| space-16 | `--spacing-16` | 64px | Major section breaks |
| space-20 | `--spacing-20` | 80px | Page-level spacing |
| space-24 | `--spacing-24` | 96px | Maximum spacing |

---

## Border Radius Tokens

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| radius-none | `--radius-none` | 0px | Flat edges |
| radius-sm | `--radius-sm` | 4px | Small elements (badges) |
| radius-md | `--radius-md` | 6px | Buttons, inputs |
| radius-lg | `--radius-lg` | 8px | Cards, dialogs |
| radius-xl | `--radius-xl` | 12px | Large cards, panels |
| radius-2xl | `--radius-2xl` | 16px | Feature cards |
| radius-full | `--radius-full` | 9999px | Circles, pills |

---

## Elevation Tokens (Box Shadows)

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| elevation-0 | `--elevation-0` | none | Flat |
| elevation-1 | `--elevation-1` | 0 1px 2px 0 rgba(0,0,0,0.05) | Cards, subtle lift |
| elevation-2 | `--elevation-2` | 0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1) | Dropdowns, popovers |
| elevation-3 | `--elevation-3` | 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1) | Dialogs |
| elevation-4 | `--elevation-4` | 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1) | Modals |
| elevation-5 | `--elevation-5` | 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1) | Tooltips, notifications |

---

## Opacity Tokens

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| opacity-disabled | `--opacity-disabled` | 0.5 | Disabled elements |
| opacity-hover | `--opacity-hover` | 0.8 | Hover states |
| opacity-overlay | `--opacity-overlay` | 0.6 | Modal backdrops |
| opacity-subtle | `--opacity-subtle` | 0.05 | Subtle tints |
| opacity-muted | `--opacity-muted` | 0.3 | Watermarks, decorations |

---

## Animation Tokens

### Duration

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| duration-fast | `--duration-fast` | 100ms | Micro-interactions (hover, focus) |
| duration-normal | `--duration-normal` | 200ms | Standard transitions |
| duration-slow | `--duration-slow` | 300ms | Page transitions, panel expansion |
| duration-slower | `--duration-slower` | 500ms | Complex animations |

### Easing

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| easing-default | `--easing-default` | cubic-bezier(0.4, 0, 0.2, 1) | General transitions |
| easing-enter | `--easing-enter` | cubic-bezier(0, 0, 0.2, 1) | Elements entering view |
| easing-exit | `--easing-exit` | cubic-bezier(0.4, 0, 1, 1) | Elements leaving view |
| easing-spring | `--easing-spring` | cubic-bezier(0.34, 1.56, 0.64, 1) | Bouncy, playful |

---

## Focus Tokens

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| focus-ring-width | `--focus-ring-width` | 2px | Focus ring thickness |
| focus-ring-color | `--focus-ring-color` | #3b82f6 | Focus ring color |
| focus-ring-offset | `--focus-ring-offset` | 2px | Gap between element and ring |
| focus-ring-style | `--focus-ring-style` | solid | Focus ring style |
| focus-visible | `--focus-visible` | 2px solid #3b82f6 offset 2px | Complete focus style |

---

## Breakpoint Tokens

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| bp-sm | `--breakpoint-sm` | 640px | Small screens |
| bp-md | `--breakpoint-md` | 768px | Medium screens |
| bp-lg | `--breakpoint-lg` | 1024px | Large screens (default desktop) |
| bp-xl | `--breakpoint-xl` | 1280px | Extra large screens |
| bp-2xl | `--breakpoint-2xl` | 1536px | Ultra wide displays |

---

## Theme Tokens

### Light Theme (Default)

```css
:root, [data-theme="light"] {
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-surface-raised: #ffffff;
  --color-text-primary: #0f172a;
  --color-text-secondary: #475569;
  --color-border-default: #e2e8f0;
  --color-primary: #2563eb;
  --color-error: #ef4444;
  --color-warning: #f59e0b;
  --color-success: #10b981;
  --color-info: #3b82f6;
}
```

### Dark Theme

```css
[data-theme="dark"] {
  --color-bg-primary: #0f172a;
  --color-bg-secondary: #1e293b;
  --color-surface-raised: #1e293b;
  --color-text-primary: #f8fafc;
  --color-text-secondary: #cbd5e1;
  --color-border-default: #334155;
  --color-primary: #3b82f6;
  --color-error: #f87171;
  --color-warning: #fbbf24;
  --color-success: #34d399;
  --color-info: #60a5fa;
}
```

### High Contrast Theme

```css
[data-theme="high-contrast"] {
  --color-bg-primary: #000000;
  --color-bg-secondary: #0a0a0a;
  --color-surface-raised: #1a1a1a;
  --color-text-primary: #ffffff;
  --color-text-secondary: #e0e0e0;
  --color-border-default: #ffffff;
  --color-primary: #60a5fa;
  --color-error: #ff6b6b;
  --color-warning: #ffd43b;
  --color-success: #51cf66;
  --color-info: #74c0fc;
  --focus-ring-color: #ffff00;
  --focus-ring-width: 3px;
}
```

---

## Token Naming Convention

```
--{category}-{property}-{variant}-{modifier}

Examples:
--color-text-primary           (category: color, property: text, variant: primary)
--font-size-heading-1          (category: font, property: size, variant: heading-1)
--spacing-card-padding         (category: spacing, property: card-padding)
--elevation-dialog             (category: elevation, property: dialog)
--duration-transition-normal   (category: duration, property: transition, variant: normal)
```

---

*All components must reference tokens. Hardcoded values are a bug. When in doubt, check if a token exists before creating a new one.*
