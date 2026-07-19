# Typography System — AuthShield Lab

> Consistent, accessible, scalable typography for all interface and content text.

---

## Font Families

### Primary: Inter

**Usage**: All UI text — headings, body, labels, buttons, navigation, forms

- **Why Inter**: Designed specifically for computer screens. Excellent legibility at small sizes. Large x-height, open counters, clear letterforms. Free and open source.
- **Weights used**: Regular (400), Medium (500), Semibold (600), Bold (700)
- **Loading strategy**: Self-hosted via `@fontsource/inter`. Subset for Latin characters. Fallback to system fonts.

```
--font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

### Monospace: JetBrains Mono

**Usage**: Code blocks, terminal output, command references, inline code, cryptographic hashes

- **Why JetBrains Mono**: Designed for developers. Distinctive letterforms reduce ambiguity between similar characters (0/O, l/1/I). Ligature support. Free and open source.
- **Weights used**: Regular (400), Medium (500), Semibold (600)
- **Loading strategy**: Self-hosted via `@fontsource/jetbrains-mono`. Subset for Latin + common code characters. Fallback to system monospace.

```
--font-family-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
```

### Heading Family

Headings use the same Inter family as body text for consistency. Distinction is achieved through size, weight, and spacing — not font changes.

```
--font-family-heading: var(--font-family-sans);
```

---

## Type Scale

### Heading Scale

| Level | CSS Variable | Font Size | Line Height | Letter Spacing | Font Weight | Usage |
|---|---|---|---|---|---|---|
| Display | `--type-display` | 2.25rem (36px) | 2.75rem (44px) | -0.01em | 700 | Hero text, landing page titles |
| H1 | `--type-h1` | 1.875rem (30px) | 2.25rem (36px) | -0.01em | 700 | Page titles |
| H2 | `--type-h2` | 1.5rem (24px) | 2rem (32px) | -0.005em | 600 | Section headings |
| H3 | `--type-h3` | 1.25rem (20px) | 1.75rem (28px) | 0em | 600 | Subsection headings |
| H4 | `--type-h4` | 1.125rem (18px) | 1.625rem (26px) | 0em | 600 | Card titles, group headers |
| H5 | `--type-h5` | 1rem (16px) | 1.5rem (24px) | 0em | 500 | Small group headers |
| H6 | `--type-h6` | 0.875rem (14px) | 1.25rem (20px) | 0em | 500 | Compact headers |

### Body Scale

| Level | CSS Variable | Font Size | Line Height | Letter Spacing | Font Weight | Usage |
|---|---|---|---|---|---|---|
| Body Large | `--type-body-lg` | 1rem (16px) | 1.5rem (24px) | 0em | 400 | Extended reading, articles |
| Body | `--type-body` | 0.875rem (14px) | 1.375rem (22px) | 0em | 400 | Default UI text |
| Body Small | `--type-body-sm` | 0.8125rem (13px) | 1.25rem (20px) | 0em | 400 | Secondary body text |
| Caption | `--type-caption` | 0.75rem (12px) | 1rem (16px) | 0em | 400 | Captions, helper text |
| Overline | `--type-overline` | 0.75rem (12px) | 1rem (16px) | 0.1em | 500 | Section labels, categories |
| Micro | `--type-micro` | 0.6875rem (11px) | 0.875rem (14px) | 0.025em | 500 | Badges, metadata |

### Code Scale

| Level | CSS Variable | Font Size | Line Height | Letter Spacing | Font Weight | Usage |
|---|---|---|---|---|---|---|
| Code Large | `--type-code-lg` | 0.9375rem (15px) | 1.5rem (24px) | 0em | 400 | Featured code blocks |
| Code | `--type-code` | 0.8125rem (13px) | 1.25rem (20px) | 0em | 400 | Code blocks, terminal |
| Code Small | `--type-code-sm` | 0.75rem (12px) | 1rem (16px) | 0em | 400 | Inline code |

---

## Line Heights

| Token | CSS Variable | Value | Ratio | Usage |
|---|---|---|---|---|
| Leading None | `--line-height-none` | 1 | 1.0 | Display text (decorative only) |
| Leading Tight | `--line-height-tight` | 1.25 | 1.25 | Headings (H1-H3) |
| Leading Snug | `--line-height-snug` | 1.375 | 1.375 | Headings (H4-H6), body text |
| Leading Normal | `--line-height-normal` | 1.5 | 1.50 | Body text (default) |
| Leading Relaxed | `--line-height-relaxed` | 1.75 | 1.75 | Long-form reading content |

### Line Height Guidelines

- Headings use tighter line heights (1.25-1.375) because they are shorter and need visual cohesion
- Body text uses normal line height (1.5) for comfortable reading
- Long-form educational content uses relaxed line height (1.75) for extended reading sessions
- Never use line heights below 1.2 — text becomes cramped and illegible
- Line height is relative to font size, so larger text needs proportionally less line height

---

## Letter Spacing

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| Tracking Tight | `--letter-spacing-tight` | -0.01em | Display and H1 text |
| Tracking Snug | `--letter-spacing-snug` | -0.005em | H2-H3 text |
| Tracking Normal | `--letter-spacing-normal` | 0em | Body text, H4-H6 |
| Tracking Wide | `--letter-spacing-wide` | 0.025em | Small labels, overlines |
| Tracking Wider | `--letter-spacing-wider` | 0.1em | Overlines (uppercase) |

### Letter Spacing Guidelines

- Large text (>24px) benefits from slightly negative letter spacing for visual cohesion
- Small uppercase text benefits from positive letter spacing for legibility
- Never use letter spacing wider than 0.1em — text becomes disconnected
- Code text always uses normal (0) letter spacing — monospace fonts are designed for it

---

## Accessibility Scaling

The type system supports 4 zoom levels without layout breakage:

| Level | CSS Variable | Scale Factor | Body Equivalent | Usage |
|---|---|---|---|---|
| 100% (Default) | `--text-scale` | 1.0 | 14px | Standard display |
| 125% | `--text-scale` | 1.25 | 17.5px | Moderate enlargement |
| 150% | `--text-scale` | 1.5 | 21px | Significant enlargement |
| 200% | `--text-scale` | 2.0 | 28px | Maximum enlargement |

### Scaling Implementation

All type sizes are calculated relative to `--text-scale`:

```css
:root {
  --text-scale: 1;
}

[data-text-scale="125"] { --text-scale: 1.25; }
[data-text-scale="150"] { --text-scale: 1.5; }
[data-text-scale="200"] { --text-scale: 2; }

/* Example: body text scales proportionally */
.type-body {
  font-size: calc(0.875rem * var(--text-scale));
  line-height: calc(1.375rem * var(--text-scale));
}
```

### Scaling Rules

- All measurements scale, not just font size — line height, spacing, and layout adjust proportionally
- The application layout uses relative units (rem, %) to support zoom without horizontal scrolling
- Minimum font size for any text: 0.625rem (10px at 100%, 12.5px at 125%)
- Maximum text scale is 200% — beyond this, additional zoom should use OS-level magnification
- All text remains readable and no content is truncated at any scale level

---

## Reading Width

Body text should not exceed 70-80 characters per line for optimal readability:

| Context | Max Width | Character Approximation |
|---|---|---|
| Body text | 680px | ~70 characters |
| Narrow content (sidebar) | 320px | ~40 characters |
| Code blocks | 800px | ~80 characters (monospace) |
| Dialog text | 540px | ~60 characters |
| Tooltip text | 280px | ~40 characters |

### Reading Width Implementation

```css
.content-reading {
  max-width: 680px;
  margin-left: auto;
  margin-right: auto;
}

.content-narrow {
  max-width: 320px;
}

.code-block {
  max-width: 800px;
  overflow-x: auto;
}
```

---

## Localization Support

### Character Set Considerations

- **Latin**: Inter supports full Latin Extended characters for Western European languages
- **Cyrillic**: Inter includes Cyrillic character support
- **Arabic/Hebrew**: Fallback fonts provide RTL support
- **CJK**: System fonts provide fallback for Chinese, Japanese, Korean
- **Emoji**: System emoji fonts handle all Unicode emoji

### Variable-Width Handling

- All layout measurements use relative units (rem, %, max-width) — not fixed pixel widths
- Text containers use `overflow-wrap: break-word` to prevent overflow
- No assumptions about character width — layouts adapt to content
- Minimum container widths are enforced at each breakpoint

### Right-to-Left (RTL) Support

- Layout direction respects `dir="rtl"` attribute
- Margins, paddings, and transforms are mirrored
- Navigation flows right-to-left
- Icon directions are adjusted (arrows, chevrons)
- Bidirectional text (mixed Latin and Arabic) is handled correctly

### Text Truncation

When text must be truncated, the ellipsis is applied with proper semantics:

```css
.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* For multi-line truncation */
.text-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

- Truncated text always has a full-text alternative (title attribute or aria-label)
- Screen readers always receive the full text
- Truncation never occurs on headings or critical information

---

## Typography Component Classes

### Heading Components

```css
/* Usage: apply via class, not raw HTML h1-h6 for layout contexts */
.heading-display  { /* 36/44, 700, tracking-tight */ }
.heading-1        { /* 30/36, 700, tracking-tight */ }
.heading-2        { /* 24/32, 600, tracking-snug */ }
.heading-3        { /* 20/28, 600, tracking-normal */ }
.heading-4        { /* 18/26, 600, tracking-normal */ }
.heading-5        { /* 16/24, 500, tracking-normal */ }
.heading-6        { /* 14/20, 500, tracking-normal */ }
```

### Body Components

```css
.body-large  { /* 16/24, 400 */ }
.body        { /* 14/22, 400 */ }
.body-small  { /* 13/20, 400 */ }
.caption     { /* 12/16, 400 */ }
.overline    { /* 12/16, 500, uppercase, tracking-wider */ }
.micro       { /* 11/14, 500, tracking-wide */ }
```

### Code Components

```css
.code-block  { /* 13/20, JetBrains Mono, 400 */ }
.code-inline { /* 13/20, JetBrains Mono, 400, with background */ }
.code-large  { /* 15/24, JetBrains Mono, 400 */ }
```

---

## Typography Accessibility Checklist

- [ ] All text meets WCAG 2.2 AA contrast ratios (4.5:1 normal, 3:1 large)
- [ ] Text scales correctly at 125%, 150%, and 200%
- [ ] No text is rendered as images — all text is selectable and searchable
- [ ] Text spacing can be adjusted without breaking layout
- [ ] Line height is at least 1.5x for body text
- [ ] Paragraph spacing is at least 2x the line height
- [ ] Letter spacing can be expanded up to 0.12em without loss of content
- [ ] Word spacing can be expanded up to 0.16em without loss of content
- [ ] No horizontal scrolling at 200% zoom for body text
- [ ] Focus indicators are visible at all text sizes
- [ ] Semantic HTML elements are used for all headings (h1-h6)
- [ ] Heading hierarchy is logical and never skips levels

---

*Typography is the foundation of readability. Every design decision in this system prioritizes the user's ability to read, understand, and learn.*
