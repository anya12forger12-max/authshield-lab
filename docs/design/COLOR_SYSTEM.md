# Color System — AuthShield Lab

> Semantic, accessible, themeable color system for all visual design decisions.

---

## Color System Architecture

The color system is built on three layers:

1. **Primitive palette** — raw color values organized by hue
2. **Semantic tokens** — purpose-driven aliases that reference primitives
3. **Component overrides** — component-specific color assignments

This architecture ensures that switching themes (light/dark/high-contrast) requires only changing semantic token values — primitive palettes remain constant.

---

## Primary Palette (Blue)

Blue is the primary interactive color. It signals action, selection, and focus throughout the application.

| Token | CSS Variable | Hex | RGB | HSL | Contrast on White | Usage |
|---|---|---|---|---|---|---|
| blue-50 | `--color-primary-50` | #eff6ff | 239,246,255 | 214,100%,97% | 1.07:1 | Lightest tint, backgrounds |
| blue-100 | `--color-primary-100` | #dbeafe | 219,234,254 | 214,86%,97% | 1.19:1 | Hover backgrounds |
| blue-200 | `--color-primary-200` | #bfdbfe | 191,219,254 | 213,86%,93% | 1.52:1 | Borders, dividers |
| blue-300 | `--color-primary-300` | #93c5fd | 147,197,253 | 213,86%,86% | 2.12:1 | Subtle indicators |
| blue-400 | `--color-primary-400` | #60a5fa | 96,165,250 | 213,86%,75% | 3.07:1 | Icons, secondary interactive |
| blue-500 | `--color-primary-500` | #3b82f6 | 59,130,246 | 217,91%,60% | 4.49:1 | Default interactive |
| blue-600 | `--color-primary-600` | #2563eb | 37,99,235 | 221,83%,53% | 5.87:1 | **Primary buttons, links** |
| blue-700 | `--color-primary-700` | #1d4ed8 | 29,78,216 | 224,76%,48% | 7.62:1 | Hover primary |
| blue-800 | `--color-primary-800` | #1e40af | 30,64,175 | 224,70%,40% | 9.44:1 | Active primary |
| blue-900 | `--color-primary-900` | #1e3a8a | 30,58,138 | 224,64%,33% | 11.22:1 | Darkest primary |

**Accessibility note**: blue-600 (#2563eb) on white passes WCAG AA for normal text (5.87:1). For large text and UI components, blue-500 (#3b82f6) also passes AA (4.49:1). On dark backgrounds, use blue-400 or lighter for equivalent contrast.

---

## Secondary Palette (Slate)

Slate provides neutral UI chrome — borders, secondary text, backgrounds, and supporting elements.

| Token | CSS Variable | Hex | RGB | HSL | Contrast on White | Usage |
|---|---|---|---|---|---|---|
| slate-50 | `--color-secondary-50` | #f8fafc | 248,250,252 | 210,20%,98% | 1.03:1 | Page background |
| slate-100 | `--color-secondary-100` | #f1f5f9 | 241,245,249 | 210,20%,96% | 1.07:1 | Alternate background |
| slate-200 | `--color-secondary-200` | #e2e8f0 | 226,232,240 | 214,22%,90% | 1.28:1 | Default borders |
| slate-300 | `--color-secondary-300` | #cbd5e1 | 203,213,225 | 213,20%,84% | 1.62:1 | Strong borders |
| slate-400 | `--color-secondary-400` | #94a3b8 | 148,163,184 | 211,16%,65% | 2.83:1 | Placeholder text |
| slate-500 | `--color-secondary-500` | #64748b | 100,116,139 | 211,13%,55% | 4.65:1 | Secondary text |
| slate-600 | `--color-secondary-600` | #475569 | 71,85,105 | 211,18%,35% | 7.32:1 | Strong secondary |
| slate-700 | `--color-secondary-700` | #334155 | 51,65,85 | 211,24%,27% | 10.44:1 | Emphasized |
| slate-800 | `--color-secondary-800` | #1e293b | 30,41,59 | 215,28%,18% | 14.55:1 | Dark surfaces |
| slate-900 | `--color-secondary-900` | #0f172a | 15,23,42 | 218,36%,11% | 18.06:1 | Near black |

---

## Accent Palette (Emerald)

Emerald signals success, completion, and positive outcomes. Used sparingly for emphasis.

| Token | CSS Variable | Hex | RGB | HSL | Contrast on White | Usage |
|---|---|---|---|---|---|---|
| emerald-50 | `--color-accent-50` | #ecfdf5 | 236,253,245 | 153,75%,96% | 1.04:1 | Lightest tint |
| emerald-100 | `--color-accent-100` | #d1fae5 | 209,250,229 | 153,76%,90% | 1.19:1 | Success background |
| emerald-200 | `--color-accent-200` | #a7f3d0 | 167,243,208 | 154,72%,80% | 1.60:1 | Success border |
| emerald-300 | `--color-accent-300` | #6ee7b7 | 110,231,183 | 154,66%,72% | 2.22:1 | Light success |
| emerald-400 | `--color-accent-400` | #34d399 | 52,211,153 | 154,59%,60% | 3.45:1 | Success interactive |
| emerald-500 | `--color-accent-500` | #10b981 | 16,185,129 | 156,68%,40% | 4.63:1 | **Default accent** |
| emerald-600 | `--color-accent-600` | #059669 | 5,150,105 | 156,94%,30% | 6.55:1 | Accent hover |
| emerald-700 | `--color-accent-700` | #047857 | 4,120,87 | 156,94%,24% | 8.58:1 | Accent active |
| emerald-800 | `--color-accent-800` | #065f46 | 6,95,70 | 157,88%,20% | 10.20:1 | Strong accent |
| emerald-900 | `--color-accent-900` | #064e3b | 6,78,59 | 157,86%,16% | 11.82:1 | Darkest accent |

---

## Background Colors

| Token | CSS Variable | Light Theme | Dark Theme | Usage |
|---|---|---|---|---|
| bg-primary | `--color-bg-primary` | #ffffff | #0f172a | Main application background |
| bg-secondary | `--color-bg-secondary` | #f8fafc | #1e293b | Alternate sections |
| bg-tertiary | `--color-bg-tertiary` | #f1f5f9 | #334155 | Subtle fills |
| bg-inverse | `--color-bg-inverse` | #0f172a | #ffffff | Inverted background |
| bg-primary-hover | `--color-bg-primary-hover` | #f8fafc | #1e293b | Primary hover state |
| bg-secondary-hover | `--color-bg-secondary-hover` | #f1f5f9 | #334155 | Secondary hover state |

---

## Surface Colors

| Token | CSS Variable | Light Theme | Dark Theme | Usage |
|---|---|---|---|---|
| surface-raised | `--color-surface-raised` | #ffffff | #1e293b | Cards, dialogs, popovers |
| surface-overlay | `--color-surface-overlay` | #ffffff | #334155 | Floating elements |
| surface-sunken | `--color-surface-sunken` | #f1f5f9 | #0f172a | Inset areas, wells |
| surface-disabled | `--color-surface-disabled` | #f8fafc | #1e293b | Disabled surfaces |
| surface-brand | `--color-surface-brand` | #eff6ff | #1e3a5f | Branded surfaces |
| surface-brand-hover | `--color-surface-brand-hover` | #dbeafe | #1e40af | Branded hover |

---

## Text Colors

| Token | CSS Variable | Light Theme | Dark Theme | Contrast (AA) | Usage |
|---|---|---|---|---|---|
| text-primary | `--color-text-primary` | #0f172a | #f8fafc | 18.06:1 | Headings, body text |
| text-secondary | `--color-text-secondary` | #475569 | #cbd5e1 | 7.32:1 | Descriptions, labels |
| text-tertiary | `--color-text-tertiary` | #64748b | #94a3b8 | 4.65:1 | Placeholders, hints |
| text-disabled | `--color-text-disabled` | #94a3b8 | #475569 | 2.83:1 | Disabled text |
| text-inverse | `--color-text-inverse` | #ffffff | #0f172a | — | Text on dark backgrounds |
| text-brand | `--color-text-brand` | #2563eb | #60a5fa | 5.87:1 | Brand-colored text |
| text-link | `--color-text-link` | #2563eb | #60a5fa | 5.87:1 | Clickable links |
| text-link-hover | `--color-text-link-hover` | #1d4ed8 | #93c5fd | 7.62:1 | Link hover |
| text-link-visited | `--color-text-link-visited` | #6d28d9 | #a78bfa | 4.55:1 | Visited links |
| text-code | `--color-text-code` | #7c2d12 | #fdba74 | 5.96:1 | Inline code text |

---

## Border Colors

| Token | CSS Variable | Light Theme | Dark Theme | Usage |
|---|---|---|---|---|
| border-default | `--color-border-default` | #e2e8f0 | #334155 | Default borders |
| border-strong | `--color-border-strong` | #cbd5e1 | #475569 | Emphasized borders |
| border-focus | `--color-border-focus` | #3b82f6 | #60a5fa | Focus indicators |
| border-error | `--color-border-error` | #ef4444 | #f87171 | Error state borders |
| border-warning | `--color-border-warning` | #f59e0b | #fbbf24 | Warning state borders |
| border-success | `--color-border-success` | #10b981 | #34d399 | Success state borders |
| border-info | `--color-border-info` | #3b82f6 | #60a5fa | Info state borders |
| border-interactive | `--color-border-interactive` | #94a3b8 | #64748b | Interactive element borders |

---

## Status Colors

### Error

| Token | CSS Variable | Light | Dark | Usage |
|---|---|---|---|---|
| error | `--color-error` | #ef4444 | #f87171 | Error icons, borders |
| error-bg | `--color-error-bg` | #fef2f2 | #450a0a | Error backgrounds |
| error-text | `--color-error-text` | #dc2626 | #fca5a5 | Error messages |
| error-border | `--color-error-border` | #fecaca | #7f1d1d | Error borders |
| error-hover | `--color-error-hover` | #b91c1c | #ef4444 | Error button hover |

### Warning

| Token | CSS Variable | Light | Dark | Usage |
|---|---|---|---|---|
| warning | `--color-warning` | #f59e0b | #fbbf24 | Warning icons, borders |
| warning-bg | `--color-warning-bg` | #fffbeb | #451a03 | Warning backgrounds |
| warning-text | `--color-warning-text` | #d97706 | #fcd34d | Warning messages |
| warning-border | `--color-warning-border` | #fde68a | #78350f | Warning borders |
| warning-hover | `--color-warning-hover` | #b45309 | #f59e0b | Warning button hover |

### Success

| Token | CSS Variable | Light | Dark | Usage |
|---|---|---|---|---|
| success | `--color-success` | #10b981 | #34d399 | Success icons, borders |
| success-bg | `--color-success-bg` | #ecfdf5 | #022c22 | Success backgrounds |
| success-text | `--color-success-text` | #059669 | #6ee7b7 | Success messages |
| success-border | `--color-success-border` | #a7f3d0 | #064e3b | Success borders |
| success-hover | `--color-success-hover` | #047857 | #10b981 | Success button hover |

### Info

| Token | CSS Variable | Light | Dark | Usage |
|---|---|---|---|---|
| info | `--color-info` | #3b82f6 | #60a5fa | Info icons, borders |
| info-bg | `--color-info-bg` | #eff6ff | #1e3a5f | Info backgrounds |
| info-text | `--color-info-text` | #2563eb | #93c5fd | Info messages |
| info-border | `--color-info-border` | #bfdbfe | #1e3a5f | Info borders |
| info-hover | `--color-info-hover` | #1d4ed8 | #3b82f6 | Info button hover |

---

## Color Independence

**Rule: Never use color as the sole indicator of information.**

Every use of color to convey meaning must be paired with at least one additional signal:

| Color Meaning | Required Pairing | Example |
|---|---|---|
| Error state | Icon + text + color | Red border + exclamation icon + "Error" text |
| Success state | Icon + text + color | Green checkmark + "Complete" label |
| Warning state | Icon + text + color | Amber triangle + "Warning" label |
| Required field | Asterisk + color | Red asterisk (*) + red label text |
| Active tab | Underline/indicator + color | Blue text + blue bottom border |
| Link | Underline + color | Blue text + underline |
| Status badge | Icon + text + color | Green dot + "Online" text |
| Chart series | Pattern + legend + color | Hatched bars + labeled legend |

---

## Contrast Ratios (WCAG 2.2 AA Compliance)

### Minimum Requirements

| Element Type | Minimum Ratio | WCAG Level | Our Implementation |
|---|---|---|---|
| Normal text (<18px) | 4.5:1 | AA | text-primary on bg-primary: 18.06:1 |
| Large text (≥18px bold or ≥24px) | 3:1 | AA | heading-1 on bg-primary: 18.06:1 |
| UI components & graphics | 3:1 | AA | borders, icons, focus rings |
| Non-text elements | 3:1 | AA | chart colors, status indicators |

### Contrast Pairings

| Foreground | Background | Ratio | Passes |
|---|---|---|---|
| text-primary (#0f172a) | bg-primary (#ffffff) | 18.06:1 | AAA ✓ |
| text-secondary (#475569) | bg-primary (#ffffff) | 7.32:1 | AAA ✓ |
| text-tertiary (#64748b) | bg-primary (#ffffff) | 4.65:1 | AA ✓ |
| text-disabled (#94a3b8) | bg-primary (#ffffff) | 2.83:1 | AA Large ✓ (decorative only) |
| primary (#2563eb) | bg-primary (#ffffff) | 5.87:1 | AAA ✓ |
| error (#ef4444) | bg-primary (#ffffff) | 4.53:1 | AA ✓ |
| warning (#f59e0b) | bg-primary (#ffffff) | 2.60:1 | AA Large ✓ (icons, not text) |
| success (#10b981) | bg-primary (#ffffff) | 2.35:1 | AA Large ✓ (icons, not text) |
| text-inverse (#ffffff) | text-primary-bg (#0f172a) | 18.06:1 | AAA ✓ |

### Dark Theme Contrast

| Foreground | Background | Ratio | Passes |
|---|---|---|---|
| text-primary (#f8fafc) | bg-primary-dark (#0f172a) | 18.06:1 | AAA ✓ |
| text-secondary (#cbd5e1) | bg-primary-dark (#0f172a) | 13.35:1 | AAA ✓ |
| text-tertiary (#94a3b8) | bg-primary-dark (#0f172a) | 8.14:1 | AAA ✓ |
| primary (#60a5fa) | bg-primary-dark (#0f172a) | 7.44:1 | AAA ✓ |
| error (#f87171) | bg-primary-dark (#0f172a) | 7.07:1 | AAA ✓ |
| warning (#fbbf24) | bg-primary-dark (#0f172a) | 11.16:1 | AAA ✓ |
| success (#34d399) | bg-primary-dark (#0f172a) | 9.04:1 | AAA ✓ |

---

## Chart Color Palette

8-color categorical palette for data visualization. Designed for colorblindness compatibility (tested with Deuteranopia, Protanopia, Tritanopia simulations).

| Index | CSS Variable | Hex | Color Name | Colorblind Safe |
|---|---|---|---|---|
| 1 | `--chart-1` | #2563eb | Blue | Yes |
| 2 | `--chart-2` | #dc2626 | Red | Yes |
| 3 | `--chart-3` | #059669 | Green | Yes |
| 4 | `--chart-4` | #d97706 | Amber | Yes |
| 5 | `--chart-5` | #7c3aed | Purple | Yes |
| 6 | `--chart-6` | #0891b2 | Cyan | Yes |
| 7 | `--chart-7` | #be185d | Pink | Yes |
| 8 | `--chart-8` | #65a30d | Lime | Yes |

### Chart Accessibility Rules

- Every chart must have a data table alternative
- Chart elements must have 3:1 contrast against adjacent colors
- Patterns/textures supplement color for 2+ series charts
- Tooltip on hover/focus shows data values
- Legend labels are always present and readable
- Color is never the only differentiator between series

---

## Theme Implementations

### Light Theme (Default)

The light theme uses white backgrounds with dark text. This is the default for all users.

```css
[data-theme="light"] {
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-bg-tertiary: #f1f5f9;
  --color-surface-raised: #ffffff;
  --color-text-primary: #0f172a;
  --color-text-secondary: #475569;
  --color-text-tertiary: #64748b;
  --color-border-default: #e2e8f0;
}
```

### Dark Theme

The dark theme inverts the palette with proper contrast ratios maintained. Recommended for extended use and low-light environments.

```css
[data-theme="dark"] {
  --color-bg-primary: #0f172a;
  --color-bg-secondary: #1e293b;
  --color-bg-tertiary: #334155;
  --color-surface-raised: #1e293b;
  --color-text-primary: #f8fafc;
  --color-text-secondary: #cbd5e1;
  --color-text-tertiary: #94a3b8;
  --color-border-default: #334155;
}
```

### High Contrast Theme

The high contrast theme provides maximum contrast for users with low vision. Uses pure black backgrounds, white text, and high-contrast accent colors. All contrast ratios exceed 7:1.

```css
[data-theme="high-contrast"] {
  --color-bg-primary: #000000;
  --color-bg-secondary: #0a0a0a;
  --color-bg-tertiary: #1a1a1a;
  --color-surface-raised: #1a1a1a;
  --color-text-primary: #ffffff;
  --color-text-secondary: #e0e0e0;
  --color-text-tertiary: #b0b0b0;
  --color-border-default: #ffffff;
  --color-primary: #60a5fa;
  --color-error: #ff6b6b;
  --color-warning: #ffd43b;
  --color-success: #51cf66;
  --color-info: #74c0fc;
}
```

### Print Theme

For printing educational materials, the print theme uses black and white with patterns for chart differentiation.

```css
@media print {
  :root {
    --color-bg-primary: #ffffff;
    --color-text-primary: #000000;
    --color-text-secondary: #333333;
    --color-border-default: #000000;
    --color-primary: #000000;
    --color-error: #000000;
    --color-success: #000000;
    /* Patterns replace colors in charts */
  }
}
```

---

## Color Token Usage Rules

1. **Never hardcode hex values in components** — always use semantic tokens
2. **Never use primitive colors directly** — use semantic aliases
3. **Always test both themes** — every color change must work in light, dark, and high-contrast
4. **Never rely on color alone** — always pair with icons, text, or patterns
5. **Maintain contrast ratios** — all text combinations must meet WCAG AA minimums
6. **Use consistent status colors** — red=error, amber=warning, green=success, blue=info, everywhere
7. **Chart colors must be colorblind-safe** — test with simulation tools before adding new series colors

---

*The color system exists to communicate information clearly and inclusively. Every color choice should be deliberate, accessible, and documented.*
