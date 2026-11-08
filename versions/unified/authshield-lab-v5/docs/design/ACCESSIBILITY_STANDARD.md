# Accessibility Standard — AuthShield Lab

> Comprehensive accessibility requirements ensuring WCAG 2.2 AA compliance and inclusive design for all users.

---

## Accessibility Commitment

AuthShield Lab is committed to providing an accessible experience for all users, regardless of ability, assistive technology, or interaction method. Accessibility is not a feature — it is a fundamental quality attribute of every component and screen.

**Target standard**: WCAG 2.2 Level AA, with selected Level AAA criteria where feasible.

---

## Keyboard-Only Operation

### Requirement

Every feature, action, and interaction in AuthShield Lab must be fully operable using only a keyboard. No functionality may require a mouse, touchpad, or other pointing device.

### Tab Order

- Tab follows visual reading order: top-to-bottom, left-to-right
- Tab order matches the DOM order (no `tabindex` values > 0)
- Skip links allow jumping past repetitive navigation
- Focus wraps within contained regions (modals, dialogs)

### Focus Indicators

| Property | Value |
|---|---|
| Style | 2px solid blue-500 |
| Offset | 2px |
| Radius | Matches element border-radius |
| Visibility | Always visible on keyboard focus |
| Never removed | `outline: none` is forbidden unless replaced with custom focus style |

### Keyboard Shortcuts

Every frequently used action has a keyboard shortcut. Full shortcut reference available via Ctrl+/.

### Focus Trapping

- Modal dialogs trap focus within the dialog
- Command palette traps focus within the palette
- Context menus trap focus within the menu
- Escape always closes the trapping container

### No Keyboard Traps

- Focus must never get stuck in a component
- All keyboard traps are bugs and must be fixed immediately
- Testing: Tab through every screen — focus must always be able to reach every interactive element and return to a logical position

---

## Screen Reader Support

### ARIA Landmarks

Every page uses semantic landmarks:

```html
<header role="banner">        <!-- Application header -->
<nav role="navigation">        <!-- Primary navigation -->
<aside role="complementary">  <!-- Sidebar -->
<main role="main">            <!-- Primary content -->
<footer role="contentinfo">   <!-- Status bar -->
```

### ARIA Labels

Every interactive element must have a accessible name:

| Element | Label Pattern | Example |
|---|---|---|
| Icon button | `aria-label="{action}"` | `aria-label="Close dialog"` |
| Form field | `<label for="id">` | `<label for="email">Email</label>` |
| Region | `aria-label="{description}"` | `aria-label="Course list"` |
| Navigation | `aria-label="{context}"` | `aria-label="Breadcrumb"` |
| Table | `<caption>` or `aria-label` | `<caption>Student grades</caption>` |
| Landmark | `aria-label` (when duplicate) | `aria-label="Course navigation"` |

### ARIA Live Regions

Dynamic content changes must be announced to screen readers:

| Content Change | ARIA Pattern | Timing |
|---|---|---|
| Toast notification | `role="status"` + `aria-live="polite"` | On appearance |
| Error message | `role="alert"` + `aria-live="assertive"` | On appearance |
| Search results count | `aria-live="polite"` | On result change |
| Loading state | `aria-busy="true"` on container | On start/end |
| Form validation | `aria-live="polite"` on error container | On validation |
| Sort change | `aria-live="polite"` on table region | On sort change |
| Filter change | `aria-live="polite"` on results region | On filter apply |
| Selection change | `aria-live="polite"` on count display | On selection change |

### ARIA States and Properties

| Component | Required ARIA |
|---|---|
| Button | `aria-label` (icon only), `aria-pressed` (toggle), `aria-busy` (loading) |
| Dialog | `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, `aria-describedby` |
| Tab panel | `role="tab/tablist/tabpanel"`, `aria-selected`, `aria-controls`, `aria-labelledby` |
| Dropdown | `role="combobox"`, `aria-expanded`, `aria-activedescendant`, `aria-controls` |
| Menu | `role="menu"`, `role="menuitem"`, `aria-disabled` |
| Progress | `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax` |
| Tooltip | `role="tooltip"`, `aria-describedby` on trigger |
| Alert | `role="alert"`, `aria-live="assertive"` |

### Screen Reader Testing

Test with the following screen readers:

| Platform | Screen Reader | Browser |
|---|---|---|
| Windows | NVDA | Chrome, Firefox |
| Windows | JAWS | Chrome |
| macOS | VoiceOver | Safari |
| Linux | Orca | Firefox |

### Testing Checklist

- [ ] All content is read in logical order
- [ ] All interactive elements are announced with name, role, and state
- [ ] Dynamic content changes are announced via live regions
- [ ] Form errors are announced when they appear
- [ ] Navigation landmarks are accessible via screen reader shortcuts
- [ ] Heading structure is logical (h1 → h2 → h3, no skipped levels)
- [ ] Tables are read with headers and row context
- [ ] Modal dialogs are announced and focus is trapped

---

## High Contrast Mode

### Enhanced Contrast Theme

The high contrast theme provides:

- **Minimum 7:1 contrast ratio** for all text (exceeding WCAG AAA)
- **Pure black background** (#000000) with **pure white text** (#ffffff)
- **Yellow focus indicators** (#ffff00) for maximum visibility
- **Thick borders** (2px minimum) for all interactive elements
- **No subtle colors** — all colors are fully saturated

### High Contrast CSS

```css
[data-theme="high-contrast"] {
  --color-bg-primary: #000000;
  --color-text-primary: #ffffff;
  --color-text-secondary: #e0e0e0;
  --color-border-default: #ffffff;
  --color-primary: #60a5fa;
  --color-error: #ff6b6b;
  --color-warning: #ffd43b;
  --color-success: #51cf66;
  --focus-ring-color: #ffff00;
  --focus-ring-width: 3px;
}
```

### Windows High Contrast Mode

AuthShield Lab respects Windows High Contrast Mode:

- System colors are used for borders and text when high contrast mode is active
- Images are replaced with high-contrast alternatives
- Background colors are transparent to allow system theme
- Focus indicators use system highlight color

### Testing

- Test with Windows High Contrast Mode (Settings > Accessibility > High contrast)
- Test with macOS Increase Contrast (System Settings > Accessibility > Display)
- Test with the application's built-in high contrast theme

---

## Reduced Motion

### Respect for Motion Preferences

All animations must respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Manual Override

Settings > Accessibility > "Reduce motion" toggle applies `[data-reduced-motion="true"]` to the root element.

### What Changes

- Page transitions: instant (no fade/slide)
- Component transitions: instant (no fade/scale)
- Loading spinners: static or pulsing opacity only
- Progress bars: instant fill (no animation)
- Celebrations: static badges (no confetti)
- Focus indicators: unchanged (always instant)

---

## Scalable Text

### Zoom Support

The application supports text scaling up to 200% without loss of content or functionality:

| Scale | Body Size | Usage |
|---|---|---|
| 100% | 14px | Default |
| 125% | 17.5px | Moderate enlargement |
| 150% | 21px | Significant enlargement |
| 200% | 28px | Maximum enlargement |

### Zoom Requirements

- No horizontal scrolling for text content at 200% zoom
- All content remains visible and readable
- UI controls remain usable (minimum 44x44px targets)
- Layout reflows to single column if necessary
- Images scale proportionally or have text alternatives
- No content is truncated or hidden at any zoom level

### Text Spacing Override

Users can override text spacing per WCAG 1.4.12:

```css
/* Allow user overrides */
.text-override {
  line-height: 1.5; /* minimum 1.5x font size */
  /* User can override to any value */
}
```

WCAG 1.4.12 allows users to override:
- Line height to 1.5x font size
- Paragraph spacing to 2x font size
- Letter spacing to 0.12x font size
- Word spacing to 0.16x font size

---

## Color Independence

### Rule

Color is never the sole means of conveying information. Every use of color must be paired with at least one additional visual indicator.

### Required Pairings

| Information | Color Only | Accessible Alternative |
|---|---|---|
| Error state | Red border | Red border + error icon + error text |
| Success state | Green check | Green check + "Complete" label |
| Required field | Red asterisk | Red asterisk * + "(required)" text |
| Active tab | Blue underline | Blue underline + bold text |
| Link | Blue text | Blue text + underline |
| Status badge | Green dot | Green dot + "Active" text |
| Chart series | Color only | Color + pattern + legend label |
| Sort direction | Arrow color | Arrow direction + aria-sort |
| Disabled state | Gray color | Gray + opacity + aria-disabled |

### Icon Pairings

| Status | Icon | Text | Color |
|---|---|---|---|
| Error | ⚠ or ✕ | "Error" or description | red-500 |
| Warning | ▲ | "Warning" or description | amber-500 |
| Success | ✓ | "Success" or description | green-500 |
| Info | ℹ | "Info" or description | blue-500 |
| Loading | ⟳ | "Loading..." | current text color |
| Required | * | "(required)" | red-500 |

---

## Accessible Forms

### Form Structure

```html
<form aria-label="Course creation form">
  <fieldset>
    <legend>Course Details</legend>
    <div class="form-field">
      <label for="course-name">
        Course name <span aria-hidden="true" class="required">*</span>
        <span class="sr-only">(required)</span>
      </label>
      <input
        id="course-name"
        type="text"
        required
        aria-required="true"
        aria-describedby="course-name-help"
        aria-invalid="false"
      />
      <span id="course-name-help" class="helper">
        Enter the course title
      </span>
    </div>
  </fieldset>
</form>
```

### Form Rules

1. Every input has a visible `<label>` (not placeholder-only)
2. Required fields marked with `*` and `aria-required="true"`
3. Helper text associated via `aria-describedby`
4. Error messages associated via `aria-describedby` (replaces helper text)
5. Error state: `aria-invalid="true"` on the input
6. Error summary at top of form with links to each invalid field
7. Form errors announced via `aria-live="polite"`
8. Form submission does not clear errors until resolved

### Validation Timing

| Validation | Timing | Pattern |
|---|---|---|
| Required | On blur (first) | Immediate feedback after leaving field |
| Format | On blur | Email, URL, phone format |
| Length | On blur | Min/max characters |
| Match | On blur | Password confirmation |
| Custom | On blur or debounced (500ms) | Business rules |
| Submit | On submit | All validations run |

---

## Logical Focus Order

### Requirements

1. Focus order matches the visual layout (top-to-bottom, left-to-right)
2. No `tabindex` values greater than 0
3. No focus on hidden elements
4. Focus is managed programmatically for dynamic content changes

### Focus Management Patterns

| Scenario | Focus Target |
|---|---|
| Page load | Skip link, then first focusable element |
| Open dialog | First focusable element in dialog |
| Close dialog | Element that triggered the dialog |
| Delete item | Next item in list, or previous if last |
| Tab change | First focusable element in new tab panel |
| Sidebar collapse | Main content area |
| Search results | First result, or input if no results |
| Form submission | Error summary, or success message |

---

## Accessible Dialogs

### Requirements

1. `role="dialog"` and `aria-modal="true"` on dialog container
2. `aria-labelledby` pointing to dialog title
3. `aria-describedby` pointing to dialog description (when present)
4. Focus trapped within dialog (Tab wraps at boundaries)
5. Focus moves to first focusable element on open
6. Focus returns to trigger element on close
7. Escape closes the dialog
8. Screen reader announces dialog title on open
9. Background content has `aria-hidden="true"` and `inert` when dialog is open

### Focus Trap Implementation

```javascript
function trapFocus(dialogElement) {
  const focusableElements = dialogElement.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  // Tab from last → wrap to first
  // Shift+Tab from first → wrap to last
}
```

---

## Accessible Tables

### Requirements

1. Use semantic `<table>`, `<thead>`, `<tbody>`, `<tfoot>` elements
2. `<caption>` or `aria-label` describing the table purpose
3. `scope="col"` on column headers
4. `scope="row"` on row headers (when applicable)
5. Sort state indicated by `aria-sort` on sortable headers
6. Sort state changes announced via `aria-live`
7. Row selection indicated by `aria-selected` on rows
8. Bulk action count announced via `aria-live`
9. Tables with horizontal scroll have accessible scroll instructions

### Complex Tables

For tables with:
- Sortable columns: `aria-sort="ascending"|"descending"|"none"` + sort button
- Selectable rows: Checkbox column with `aria-label="Select row {name}"`
- Expandable rows: `aria-expanded` on trigger, `role="row"` on children
- Editable cells: `contenteditable` with `role="textbox"` and `aria-label`

---

## Accessible Charts

### Requirements

1. Every chart has a data table alternative (toggle between chart and table view)
2. Chart elements have minimum 3:1 contrast against adjacent colors
3. Patterns or textures supplement color for multi-series charts
4. Tooltips show data values on hover/focus
5. Legend labels are always present and readable
6. Chart title and description provided via `aria-label` and `aria-describedby`
7. Data table alternative is keyboard accessible
8. Chart data is downloadable as CSV/TSV

### Screen Reader Alternative

Charts are supplemented with:

```html
<div role="img" aria-label="Course completion rates by month" aria-describedby="chart-desc">
  <canvas aria-hidden="true"><!-- chart rendered here --></canvas>
</div>
<p id="chart-desc" class="sr-only">
  Course completion rates: January 45%, February 52%, March 61%, April 58%, May 72%, June 78%.
</p>
<button aria-label="Show chart as data table">View as table</button>
```

---

## Accessible Documentation

### Requirements

1. Semantic HTML throughout (headings, lists, tables, code blocks)
2. Heading hierarchy is logical and never skips levels
3. Links have descriptive text (no "click here")
4. Images have meaningful alt text or are marked decorative
5. Code blocks have language identification
6. Abbreviations have `<abbr>` with `title` attribute
7. Content is readable at 200% zoom
8. Reading width is limited to 70-80 characters

### Heading Hierarchy

```html
<h1>Page Title</h1>
  <h2>Section</h2>
    <h3>Subsection</h3>
    <h3>Subsection</h3>
  <h2>Section</h2>
    <h3>Subsection</h3>
```

---

## Testing Checklist

### Automated Testing

- [ ] axe-core integrated in CI/CD pipeline
- [ ] Zero critical violations on every build
- [ ] Lighthouse accessibility score ≥ 95
- [ ] No color contrast violations
- [ ] No missing form labels
- [ ] No missing alt text
- [ ] No ARIA misuse

### Manual Testing

- [ ] Full keyboard navigation through every screen
- [ ] Screen reader testing (NVDA, JAWS, VoiceOver)
- [ ] High contrast mode testing (Windows, macOS, app theme)
- [ ] Reduced motion testing (OS setting and app setting)
- [ ] 200% zoom testing
- [ ] Text spacing override testing
- [ ] Focus visible testing on every interactive element
- [ ] Dialog focus trap testing
- [ ] Dynamic content announcement testing
- [ ] Form validation testing with screen reader

### User Testing

- [ ] Test with keyboard-only users
- [ ] Test with screen reader users
- [ ] Test with low vision users
- [ ] Test with cognitive disability users
- [ ] Document and resolve all accessibility barriers

---

*Accessibility is not a checkbox — it is a continuous commitment to inclusive design. Every user deserves a complete, functional, and dignified experience.*
