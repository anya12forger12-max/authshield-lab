# AuthShield Lab — Accessibility UI Framework

> WCAG 2.2 AA compliance specification for the offline-first desktop cybersecurity education platform.

---

## 1. Overview

AuthShield Lab is committed to **accessibility-first design**. Every UI component must meet **WCAG 2.2 Level AA** conformance. This document defines the complete accessibility framework covering perceivability, operability, understandability, and robustness across all platform surfaces.

---

## 2. WCAG 2.2 AA Compliance Checklist

### 2.1 Perceivable

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| 1.1.1 Non-text Content | All non-text content has text alternatives | `alt` on images, `aria-label` on icons, `aria-label` on SVGs |
| 1.2.1 Audio-only/Video-only | Pre-recorded media alternatives | Text transcripts for audio, audio description for video |
| 1.2.2 Captions | Captions for pre-recorded audio | WebVTT captions for all video content |
| 1.2.3 Audio Description | Audio description for pre-recorded video | Described video track or text alternative |
| 1.2.5 Audio Description (Live) | Audio description for live video | Not applicable (no live video) |
| 1.3.1 Info and Relationships | Semantic structure conveys relationships | Proper heading hierarchy, `aria-labelledby`, `fieldset`/`legend` |
| 1.3.2 Meaningful Sequence | Reading order matches visual order | DOM order matches visual layout; no CSS reordering of content |
| 1.3.3 Sensory Characteristics | Instructions not solely sensory | "Click the red button" also says "Click the Delete button" |
| 1.3.4 Orientation | Content adapts to orientation | Not applicable (desktop app, landscape) |
| 1.3.5 Identify Input Purpose | Input fields identify purpose | `autocomplete` attributes, `aria-label` with purpose |
| 1.4.1 Use of Color | Color not sole means of conveying info | Error states use icon + text + color; status uses icon + color |
| 1.4.2 Audio Control | No auto-playing audio | Audio requires user interaction to start |
| 1.4.3 Contrast (Minimum) | 4.5:1 normal text, 3:1 large text | All text verified against backgrounds |
| 1.4.4 Resize Text | Text resizable to 200% | All text uses `rem`; 200% zoom supported |
| 1.4.5 Images of Text | No images of text | All text rendered as real text |
| 1.4.10 Reflow | No horizontal scroll at 320px / 400% zoom | Content reflows to single column at zoom |
| 1.4.11 Non-text Contrast | 3:1 contrast for UI components | All borders, icons, focus indicators meet 3:1 |
| 1.4.12 Text Spacing | Text spacing adjustable without loss | No fixed heights on text containers |
| 1.4.13 Content on Hover/Focus | Hover/focus content dismissible, hoverable, persistent | Tooltips: Esc closes, hoverable, persist until dismissed |

### 2.2 Operable

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| 2.1.1 Keyboard | All functionality keyboard accessible | Every interactive element reachable and operable via keyboard |
| 2.1.2 No Keyboard Trap | No keyboard trap | Tab cycles through; Esc exits modals |
| 2.1.4 Character Key Shortcuts | Single key shortcuts remappable/disablable | All shortcuts require modifier keys except when in focused widget |
| 2.2.1 Timing Adjustable | Time limits adjustable | No time limits imposed on user actions |
| 2.2.2 Pause, Stop, Hide | Auto-updating content pausable | Animations have pause button; auto-refresh can be stopped |
| 2.3.1 Three Flashes | No content flashes more than 3 times/second | All animations verified; no flashing content |
| 2.4.1 Bypass Blocks | Skip navigation link | "Skip to main content" link is first focusable element |
| 2.4.2 Page Titled | Descriptive page titles | Each view has a descriptive `<title>` or `aria-label` |
| 2.4.3 Focus Order | Focus order preserves meaning | Tab order matches visual reading order |
| 2.4.4 Link Purpose | Link purpose clear from text or context | Links have descriptive text; icon-only links have `aria-label` |
| 2.4.5 Multiple Ways | Multiple navigation methods | Search, tree view, breadcrumb, keyboard shortcuts |
| 2.4.6 Headings and Labels | Descriptive headings and labels | All headings describe section; all form fields labeled |
| 2.4.7 Focus Visible | Keyboard focus indicator visible | 2px solid blue-500 outline on all focusable elements |
| 2.4.11 Focus Not Obscured (Minimum) | Focused element not entirely obscured | Focus indicators positioned above other content |
| 2.4.12 Focus Not Obscured (Enhanced) | Focused element not obscured at all | Stacking order ensures focus ring always visible |
| 2.4.13 Focus Appearance | Focus indicator large enough, contrast sufficient | 2px outline, 3:1 contrast against adjacent colors |
| 2.5.1 Pointer Gestures | No complex gestures required | All actions achievable with single pointer (click) |
| 2.5.2 Pointer Cancellation | Actions on up-event | Click activates on `mouseup`, not `mousedown` |
| 2.5.3 Label in Name | Accessible name includes visible label | `aria-label` contains visible text label |
| 2.5.4 Motion Actuation | Motion-based input has alternatives | Device orientation actions also available via buttons |

### 2.3 Understandable

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| 3.1.1 Language of Page | Page language identified | `<html lang="en">` set, updates with locale |
| 3.1.2 Language of Parts | Language of content segments marked | Code blocks, foreign language text wrapped with `lang` attribute |
| 3.2.1 On Focus | No unexpected context change on focus | Focus does not trigger navigation or modal |
| 3.2.2 On Input | No unexpected context change on input | Select changes do not navigate; form submits require explicit button |
| 3.2.3 Consistent Navigation | Navigation consistent across views | Same nav structure, same position, same order |
| 3.2.4 Consistent Identification | Same functions identified consistently | Same icon + label for same action everywhere |
| 3.3.1 Error Identification | Errors clearly identified | Error message describes problem, points to field |
| 3.3.2 Labels or Instructions | Labels and instructions provided | Every input has visible label; help text via `aria-describedby` |
| 3.3.3 Error Suggestion | Error suggestions provided when known | "Email must include @" not just "Invalid format" |
| 3.3.4 Error Prevention | Important submissions reversible/confirmed | Destructive actions require confirmation dialog |
| 3.3.6 Error Prevention (All) | All user input validated | Client-side validation with clear feedback |

### 2.4 Robust

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| 4.1.2 Name, Role, Value | All components have accessible name and role | `role`, `aria-label`, `aria-valuenow` as appropriate |
| 4.1.3 Status Messages | Status messages announced to screen readers | `aria-live` regions for notifications, progress, errors |

---

## 3. Screen Reader Support

### 3.1 ARIA Landmarks

Every page/view must include these landmark regions:

```html
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>

  <header role="banner">
    <!-- Application header, toolbar -->
  </header>

  <nav role="navigation" aria-label="Main navigation">
    <!-- Navigation rail, sidebar navigation -->
  </nav>

  <nav role="navigation" aria-label="Breadcrumb">
    <!-- Breadcrumb trail -->
  </nav>

  <aside role="complementary" aria-label="Properties panel">
    <!-- Right panel / inspector -->
  </aside>

  <main id="main-content" role="main" aria-label="Lesson workspace">
    <!-- Primary workspace content -->
  </main>

  <footer role="contentinfo">
    <!-- Status bar -->
  </footer>
</body>
```

### 3.2 ARIA Labels

Every interactive element must have an accessible name:

| Element Type | Label Source | Example |
|-------------|-------------|---------|
| Icon button | `aria-label` | `<button aria-label="Close dialog">×</button>` |
| Image | `alt` text | `<img alt="Auth flow diagram" />` |
| SVG icon | `aria-label` or `role="img"` + `aria-label` | `<svg role="img" aria-label="Warning"><path/></svg>` |
| Text input | `<label>` + `for`/`id` | `<label for="email">Email</label><input id="email">` |
| Region | `aria-label` on landmark | `<aside aria-label="Properties panel">` |
| Custom widget | `aria-label` | `<div role="tree" aria-label="Lesson files">` |

### 3.3 ARIA Live Regions

Use live regions for dynamic content updates:

```html
<!-- Assertive: interrupts current screen reader output -->
<div role="alert" aria-live="assertive" aria-atomic="true">
  <!-- Error messages appear here -->
</div>

<!-- Polite: waits for screen reader idle -->
<div aria-live="polite" aria-atomic="true">
  <!-- Status updates, progress, search results count -->
</div>

<!-- Status role: implicitly polite -->
<div role="status">
  <!-- "3 results found", "Lesson saved" -->
</div>
```

| Live Region | Usage | Priority |
|------------|-------|----------|
| `role="alert"` | Errors, critical warnings | Assertive |
| `role="status"` | Status messages, result counts | Polite |
| `aria-live="polite"` | Progress updates, non-critical updates | Polite |
| `aria-live="assertive"` | Urgent messages requiring immediate attention | Assertive |
| `role="log"` | Terminal/console output | Polite |

### 3.4 ARIA Roles for Custom Widgets

| Widget | Role | Required ARIA Properties |
|--------|------|--------------------------|
| Tab list | `tablist` | `aria-label` |
| Tab | `tab` | `aria-selected`, `aria-controls`, `tabindex` |
| Tab panel | `tabpanel` | `aria-labelledby`, `tabindex="0"` |
| Tree view | `tree` | `aria-label`, `aria-multiselectable` |
| Tree item | `treeitem` | `aria-expanded`, `aria-selected`, `aria-level` |
| Menu | `menu` | `aria-label` |
| Menu item | `menuitem` | `aria-disabled` |
| Dialog | `dialog` | `aria-labelledby`, `aria-describedby` |
| Alert dialog | `alertdialog` | `aria-labelledby`, `aria-describedby` |
| Grid | `grid` | `aria-label`, `aria-rowcount`, `aria-colcount` |
| Grid cell | `gridcell` | `aria-rowindex`, `aria-colindex`, `aria-selected` |
| Toolbar | `toolbar` | `aria-label` |
| Progress bar | `progressbar` | `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, `aria-label` |
| Combobox | `combobox` | `aria-expanded`, `aria-controls`, `aria-activedescendant` |

### 3.5 Reading Order

- DOM order **always** matches visual order.
- CSS `order`, `grid-auto-flow`, and `float` are never used to reorder content semantically.
- Screen reader navigation follows DOM order.
- Visual presentation uses CSS that preserves DOM order.

### 3.6 Skip Navigation

```html
<!-- First focusable element in the document -->
<a href="#main-content" class="skip-link">
  Skip to main content
</a>

<style>
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #1e40af;
  color: white;
  padding: 8px 16px;
  z-index: 10000;
  transition: top 200ms;
}

.skip-link:focus {
  top: 0;
}
</style>
```

- The skip link appears only on keyboard focus (visually hidden by default).
- It is the **first** focusable element in the document.
- It moves focus directly to `#main-content`.
- After skip, Tab continues from main content.

---

## 4. Keyboard Navigation

### 4.1 Tab Order

- Tab moves forward through interactive elements in logical order.
- Shift+Tab moves backward.
- Tab order matches visual layout (left-to-right, top-to-bottom in LTR).
- Skip links are first, landmarks are keyboard-accessible.
- Inactive/disabled elements are **not** in the tab order (`tabindex="-1"`).

### 4.2 Focus Indicators

```css
:focus-visible {
  outline: 2px solid #3b82f6;  /* blue-500 */
  outline-offset: 2px;
}

:focus:not(:focus-visible) {
  outline: none;  /* Hide focus ring for mouse clicks */
}
```

| Property | Value |
|----------|-------|
| Style | Solid outline |
| Width | 2px |
| Color | `#3b82f6` (blue-500) |
| Offset | 2px |
| Contrast ratio | >3:1 against all backgrounds |
| High contrast mode | 3px black outline with white offset |

### 4.3 Focus Trapping

Focus is trapped in these contexts:

- **Modal dialogs**: Tab cycles through focusable elements within the dialog. First Tab goes to first focusable; last Tab wraps to first.
- **Dropdown menus**: Arrow keys navigate; Esc closes and returns focus.
- **Command palette (Ctrl+K)**: Tab cycles through results and input.
- **Context menus**: Arrow keys navigate; Esc closes and returns focus.

```typescript
function trapFocus(container: HTMLElement) {
  const focusable = container.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const first = focusable[0] as HTMLElement;
  const last = focusable[focusable.length - 1] as HTMLElement;

  container.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });
}
```

### 4.4 Focus Restoration

After a dialog or overlay closes, focus returns to the element that triggered it:

```typescript
function openDialog(trigger: HTMLElement) {
  const previousFocus = document.activeElement as HTMLElement;
  dialog.show();
  trapFocus(dialog);

  dialog.addEventListener('close', () => {
    previousFocus.focus();  // Restore focus
  }, { once: true });
}
```

| Context | Focus Returns To |
|---------|-----------------|
| Modal close | Trigger button/link |
| Dropdown close | Trigger button |
| Context menu close | Trigger element |
| Toast/notification dismiss | Last focused element before toast |
| Tab switch | Previous tab in tab list |

### 4.5 Roving Tabindex

Composite widgets use roving tabindex to manage focus within a group:

```typescript
// Example: Tab bar
function rovingTabindex(tabs: HTMLElement[]) {
  tabs.forEach((tab, i) => {
    tab.setAttribute('tabindex', i === 0 ? '0' : '-1');
  });

  tabs[0].addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') {
      const next = tabs[1];
      tabs[0].setAttribute('tabindex', '-1');
      next.setAttribute('tabindex', '0');
      next.focus();
    }
  });
  // ... similar for ArrowLeft, Home, End
}
```

Widgets using roving tabindex:
- Tab bars
- Toolbar button groups
- Tree view nodes
- Menu items
- Radio button groups
- Grid cells

---

## 5. Visual Accessibility

### 5.1 High Contrast Mode

When `prefers-contrast: more` or Windows High Contrast Mode is detected:

```css
@media (prefers-contrast: more) {
  :root {
    --border-color: CanvasText;
    --focus-ring-color: Highlight;
    --text-color: CanvasText;
    --bg-color: Canvas;
  }

  * {
    border-color: CanvasText !important;
  }

  :focus-visible {
    outline: 3px solid Highlight !important;
  }
}
```

- All borders become visible (no border-less elements).
- Color is supplemented with borders, patterns, or text.
- Focus ring uses system highlight color.
- Background images are removed; replaced with solid colors.

### 5.2 Reduced Motion

```css
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

- All animations are optional; the application is fully functional without them.
- Panel open/close transitions are instant.
- Loading spinners become static indicators.
- Auto-playing content does not auto-play.

### 5.3 Scalable Text

- All text uses `rem` units (base 14px).
- UI supports **200% zoom** without horizontal scrolling.
- At 200% zoom, all content remains visible and functional.
- No fixed-width containers for text content.
- Text containers use `min-height` not `height`.
- Overflow uses `text-overflow: ellipsis` with tooltip for truncated text.

### 5.4 Color Independence

Color is **never** the sole indicator of state or meaning:

| State | Visual Indicators |
|-------|-------------------|
| Error | Red text + error icon + border |
| Success | Green text + checkmark icon + border |
| Warning | Yellow text + warning icon + border |
| Info | Blue text + info icon + border |
| Active/Selected | Bold text + background highlight + checkmark |
| Disabled | Muted text + opacity reduction + label "(disabled)" |
| Required | Asterisk (*) + "(required)" text + `aria-required` |
| Online/Offline | Icon + text label + color dot |

### 5.5 Minimum Contrast Ratios

| Element | Minimum Ratio | Standard |
|---------|---------------|----------|
| Normal text (<18pt / <14pt bold) | 4.5:1 | WCAG AA |
| Large text (≥18pt / ≥14pt bold) | 3:1 | WCAG AA |
| UI components (borders, icons) | 3:1 | WCAG AA |
| Focus indicators | 3:1 | WCAG AA |
| Placeholder text | 4.5:1 | WCAG AA (treated as normal text) |

### 5.6 Contrast Verification Colors

Verified high-contrast combinations:

| Foreground | Background | Ratio | Pass |
|-----------|------------|-------|------|
| `#111827` (gray-900) | `#ffffff` (white) | 18.4:1 | AA |
| `#374151` (gray-700) | `#ffffff` (white) | 10.4:1 | AA |
| `#6b7280` (gray-500) | `#ffffff` (white) | 5.0:1 | AA |
| `#ffffff` (white) | `#1e40af` (blue-800) | 8.6:1 | AA |
| `#ffffff` (white) | `#111827` (gray-900) | 18.4:1 | AA |
| `#dc2626` (red-600) | `#ffffff` (white) | 4.6:1 | AA |
| `#16a34a` (green-600) | `#ffffff` (white) | 4.5:1 | AA |

---

## 6. Form Accessibility

### 6.1 Labels

Every form input must have a **visible** label (not just a placeholder):

```html
<!-- Correct -->
<label for="email">Email address</label>
<input
  id="email"
  type="email"
  aria-describedby="email-help"
  aria-required="true"
/>
<span id="email-help">We'll never share your email.</span>

<!-- Incorrect — placeholder only -->
<input type="email" placeholder="Email address" />
```

### 6.2 Help Text

Help text is associated via `aria-describedby`:

```html
<label for="password">Password</label>
<input id="password" type="password" aria-describedby="password-requirements" />
<div id="password-requirements">
  Must be at least 8 characters with one uppercase and one number.
</div>
```

### 6.3 Error Handling

```html
<label for="email">Email address</label>
<input
  id="email"
  type="email"
  aria-required="true"
  aria-invalid="true"
  aria-describedby="email-error"
/>
<div id="email-error" role="alert">
  Please enter a valid email address (e.g., user@example.com).
</div>
```

Error requirements:
- `aria-invalid="true"` on the invalid field.
- `aria-describedby` points to the error message.
- Error message is wrapped in `role="alert"` for live announcement.
- Error summary appears at the top of the form with links to each invalid field.
- Error message is **specific** and **actionable**.

### 6.4 Required Fields

```html
<label for="name">
  Full name <span aria-hidden="true">*</span>
</label>
<input
  id="name"
  type="text"
  aria-required="true"
  required
/>
```

- Visual indicator: asterisk `*` (hidden from screen readers via `aria-hidden`).
- Screen reader announces: "Full name, required, edit text."
- Required state communicated via `aria-required="true"` and `required` attribute.

### 6.5 Field Grouping

```html
<fieldset>
  <legend>Notification preferences</legend>
  <label>
    <input type="checkbox" name="email-notifications" /> Email notifications
  </label>
  <label>
    <input type="checkbox" name="desktop-notifications" /> Desktop notifications
  </label>
</fieldset>
```

- Related fields are grouped with `<fieldset>` and `<legend>`.
- Screen reader announces group name when first field receives focus.

---

## 7. Table Accessibility

### 7.1 Table Structure

```html
<table>
  <caption>Recent authentication attempts</caption>
  <thead>
    <tr>
      <th scope="col" aria-sort="descending">Timestamp</th>
      <th scope="col">User</th>
      <th scope="col">IP Address</th>
      <th scope="col">Result</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2026-07-19 10:32</td>
      <td>admin@example.com</td>
      <td>192.168.1.100</td>
      <td>
        <span role="img" aria-label="Success">✓</span> Success
      </td>
    </tr>
  </tbody>
</table>
```

### 7.2 Table Requirements

| Requirement | Implementation |
|------------|----------------|
| Caption | `<caption>` with descriptive text |
| Column headers | `<th scope="col">` for every column |
| Row headers | `<th scope="row">` where applicable |
| Sorting | `aria-sort="ascending"` or `aria-sort="descending"` on sorted column header |
| Selection | `aria-selected="true"` on selected rows |
| Pagination | `aria-label` on page controls ("Page 2 of 10", "Next page") |
| Row count | `aria-rowcount` on `<table>` if virtualized |
| Column count | `aria-colcount` on `<table>` if virtualized |

---

## 8. Dialog Accessibility

### 8.1 Modal Dialog

```html
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
>
  <h2 id="dialog-title">Confirm Lesson Delete</h2>
  <p id="dialog-description">
    Are you sure you want to delete "Introduction to SSH"? This action cannot be undone.
  </p>
  <div class="dialog-actions">
    <button type="button" data-dialog-close>Cancel</button>
    <button type="button" data-dialog-confirm>Delete</button>
  </div>
</div>
```

### 8.2 Dialog Requirements

| Property | Requirement |
|----------|------------|
| Role | `role="dialog"` or `role="alertdialog"` |
| Modal | `aria-modal="true"` for modal dialogs |
| Label | `aria-labelledby` points to dialog title |
| Description | `aria-describedby` points to descriptive text |
| Focus trap | Tab/Shift+Tab cycle within dialog only |
| Escape | Escape key closes the dialog |
| Return focus | Focus returns to triggering element on close |
| Background | Background content has `aria-hidden="true"` or `inert` |
| Initial focus | First focusable element or primary action receives focus |

### 8.3 Alert Dialog

```html
<div
  role="alertdialog"
  aria-modal="true"
  aria-labelledby="alert-title"
  aria-describedby="alert-description"
>
  <h2 id="alert-title">Unsaved Changes</h2>
  <p id="alert-description">
    You have unsaved changes. Do you want to save before closing?
  </p>
  <button>Save</button>
  <button>Discard</button>
  <button>Cancel</button>
</div>
```

- `role="alertdialog"` for important alerts requiring user response.
- `role="alert"` for simple notifications (no user response needed).

---

## 9. Chart and Data Visualization Accessibility

### 9.1 Requirements

| Requirement | Implementation |
|------------|----------------|
| Text alternative | Data table always available alongside chart |
| Summary description | `aria-label` with summary ("Authentication attempts over time: 150 in January, 200 in February...") |
| Keyboard navigation | Arrow keys navigate between data points |
| High contrast | Patterns/shapes used in addition to colors |
| Zoom | Charts are zoomable and scrollable |
| Data export | Data available in accessible formats (CSV, JSON) |

### 9.2 Chart Data Table

Every chart must have a toggle to view the underlying data as an accessible table:

```html
<button aria-pressed="false" aria-label="Show data table for authentication chart">
  View as Table
</button>
```

---

## 10. Testing Checklist

### 10.1 Automated Testing

| Tool | Frequency | Target |
|------|-----------|--------|
| axe-core | Every build | 0 violations |
| eslint-plugin-jsx-a11y | Every commit | 0 warnings |
| Lighthouse Accessibility | Every PR | Score >95 |
| Playwright a11y tests | Every PR | 0 failures |

### 10.2 Manual Testing

| Test | Frequency | Tool/Method |
|------|-----------|-------------|
| Keyboard-only navigation | Every sprint | Manual: Tab through all workflows |
| Screen reader (NVDA) | Every sprint | NVDA + Firefox on Windows |
| Screen reader (VoiceOver) | Every sprint | VoiceOver + Safari on macOS |
| Screen reader (JAWS) | Monthly | JAWS + Chrome on Windows |
| High contrast mode | Every sprint | Windows High Contrast theme |
| Zoom testing (200%) | Every sprint | Browser/app zoom to 200% |
| Color contrast verification | Every PR | axe-core + manual spot checks |
| Reduced motion | Every sprint | `prefers-reduced-motion: reduce` |
| Touch targets | Every sprint | Minimum 44×44px (24×24 for small UI) |

### 10.3 Automated Test Example

```typescript
// playwright accessibility test
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('main workspace has no axe violations', async ({ page }) => {
    await page.goto('/');
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze();
    expect(results.violations).toEqual([]);
  });

  test('all interactive elements have accessible names', async ({ page }) => {
    await page.goto('/');
    const results = await new AxeBuilder({ page })
      .include('[role="button"], button, a, input, select, textarea')
      .withRules(['aria-allowed-role', 'button-name', 'link-name'])
      .analyze();
    expect(results.violations).toEqual([]);
  });
});
```

---

*Document version: 1.0.0 — Last updated: 2026-07-19*
