# Accessibility Architecture — AuthShield Lab

> Version: 1.0  
> Last Updated: 2026-07-19  
> Status: Current

---

## 1. Overview

AuthShield Lab targets **WCAG 2.2 Level AA** compliance across all user-facing components. Accessibility is a first-class architectural concern, not an afterthought. The platform serves cybersecurity education users who may have diverse accessibility needs.

---

## 2. Accessibility Principles

| WCAG Principle | Implementation |
|---|---|
| **Perceivable** | Alt text, captions, high contrast, scalable text |
| **Operable** | Full keyboard navigation, no time traps, skip links |
| **Understandable** | Clear labels, consistent navigation, error identification |
| **Robust** | Valid HTML, ARIA usage, compatibility with assistive tech |

---

## 3. Keyboard Navigation

### 3.1 Navigation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    KEYBOARD NAVIGATION                           │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  Skip    │  │  Tab     │  │  Arrow   │  │  Shortcut    │  │
│  │  Links   │  │  Order   │  │  Keys    │  │  Keys        │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  Focus   │  │  Escape  │  │  Enter   │  │  Space       │  │
│  │  Trap    │  │  Close   │  │  Activate│  │  Toggle      │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Skip Links

Every page provides skip links as the first focusable elements:

```html
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <a href="#main-nav" class="skip-link">Skip to navigation</a>
  <a href="#search" class="skip-link">Skip to search</a>
  ...
</body>
```

**Skip Link Behavior:**
- Visible on focus (hidden when not focused)
- Moves focus to target element
- First element in tab order
- Styled with sufficient contrast

### 3.3 Tab Order Rules

| Rule | Implementation |
|---|---|
| Logical reading order | DOM order matches visual order |
| No positive tabindex | Use DOM order, not tabindex > 0 |
| Visible focus indicator | 2px solid outline, 3:1 contrast minimum |
| Focus management on navigation | Focus moves to page title on route change |
| Focus restoration | Return focus to trigger after modal close |
| No keyboard traps | Escape always available to exit |

### 3.4 Keyboard Shortcuts

| Shortcut | Action | Scope |
|---|---|---|
| `Tab` | Next focusable element | Global |
| `Shift+Tab` | Previous focusable element | Global |
| `Enter` | Activate button/link | Global |
| `Space` | Toggle checkbox/button | Global |
| `Escape` | Close modal/dropdown | Global |
| `Alt+1-9` | Navigate to module | Global |
| `Ctrl+/` | Open help | Global |
| `Ctrl+K` | Open search | Global |
| `Ctrl+Shift+P` | Command palette | Global |
| `Arrow keys` | Navigate within group | Contextual |
| `Home/End` | First/last in group | Contextual |

### 3.5 Component-Specific Keyboard Behavior

| Component | Keyboard Behavior |
|---|---|
| Modal dialog | Focus trapped, Escape closes, focus returns to trigger |
| Dropdown menu | Arrow keys navigate, Enter selects, Escape closes |
| Tab panel | Arrow keys switch tabs, Tab moves to panel content |
| Tree view | Arrow keys navigate nodes, Enter expands/collapses |
| Data table | Arrow keys navigate cells, Enter activates row |
| Form | Tab moves between fields, Enter submits |
| Toast notification | Focus moves to toast, Escape dismisses |

---

## 4. Screen Reader Support

### 4.1 ARIA Label Strategy

| Component | ARIA Pattern | Required Attributes |
|---|---|---|
| Button | — | `aria-label` if no visible text |
| Input | — | `aria-label` or associated `<label>` |
| Modal | `dialog` | `aria-modal`, `aria-labelledby`, `aria-describedby` |
| Navigation | `navigation` | `aria-label` (unique per nav) |
| Alert | `alert` | `role="alert"` |
| Status | `status` | `role="status"` |
| Progress | `progressbar` | `aria-valuenow`, `aria-valuemin`, `aria-valuemax` |
| Tab panel | `tablist` | `role="tablist"`, `role="tab"`, `role="tabpanel"` |
| Tree view | `tree` | `role="tree"`, `role="treeitem"`, `aria-expanded` |
| Data table | — | `<caption>`, `scope` attributes, `aria-sort` |
| Listbox | `listbox` | `role="listbox"`, `role="option"`, `aria-selected` |
| Menu | `menu` | `role="menu"`, `role="menuitem"` |
| Tooltip | `tooltip` | `role="tooltip"`, `aria-describedby` |

### 4.2 Live Regions

| Region | Usage | Politeness |
|---|---|---|
| Toast notifications | Success/error/info messages | `polite` |
| Form validation | Inline error messages | `assertive` |
| Loading states | Progress updates | `polite` |
| Search results | Result count changes | `polite` |
| Timer updates | Countdown timers | `off` (updated sparingly) |
| Modal title | New modal opened | `assertive` |

```html
<!-- Polite announcement (waits for user to finish) -->
<div role="status" aria-live="polite" id="status-announcer">
  Course saved successfully.
</div>

<!-- Assertive announcement (interrupts user) -->
<div role="alert" aria-live="assertive" id="error-announcer">
  Error: Invalid email address.
</div>
```

### 4.3 Screen Reader Testing

| Screen Reader | Platform | Testing Frequency |
|---|---|---|
| NVDA | Windows | Per release |
| JAWS | Windows | Per release |
| VoiceOver | macOS | Per release |
| TalkBack | Android | Quarterly |
| Narrator | Windows | Quarterly |

---

## 5. High Contrast Mode

### 5.1 High Contrast Theme

```css
/* High Contrast Mode Variables */
:root.high-contrast {
  --color-text-primary: #000000;
  --color-text-secondary: #1a1a1a;
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f0f0f0;
  --color-border: #000000;
  --color-focus: #0000ff;
  --color-error: #cc0000;
  --color-success: #006600;
  --color-warning: #cc6600;
  --color-link: #0000cc;
  --color-link-visited: #660099;
  --border-width-focus: 3px;
  --border-width-default: 2px;
}
```

### 5.2 High Contrast Requirements

| Requirement | Specification |
|---|---|
| Text contrast ratio | ≥ 7:1 (normal text) |
| Large text contrast ratio | ≥ 4.5:1 (≥ 18pt or 14pt bold) |
| UI component contrast | ≥ 3:1 (borders, icons) |
| Focus indicator contrast | ≥ 3:1 against adjacent colors |
| No color-only information | Icons, text, or patterns supplement color |
| Border visibility | All interactive elements have visible borders |

### 5.3 System-Level Detection

```css
@media (prefers-contrast: high) {
  :root {
    /* Apply high contrast theme automatically */
  }
}

@media (forced-colors: active) {
  /* Windows High Contrast Mode */
  :root {
    forced-color-adjust: none;
  }
}
```

---

## 6. Reduced Motion Support

### 6.1 Motion Policy

| Animation Type | Default | Reduced Motion |
|---|---|---|
| Page transitions | Fade + slide | Instant |
| Loading spinners | Animated | Static "Loading..." text |
| Progress bars | Animated fill | Static percentage |
| Toast notifications | Slide in | Instant appear |
| Modal open/close | Scale + fade | Instant |
| Hover effects | Transform | No transform |
| Parallax effects | Enabled | Disabled |
| Auto-scrolling | Enabled | Disabled |

### 6.2 System-Level Detection

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

### 6.3 User Override

Users can override system settings via Preferences:
```json
{
  "accessibility": {
    "reduced_motion": "system" | "enabled" | "disabled",
    "animations": "system" | "enabled" | "disabled"
  }
}
```

---

## 7. Accessible Reports

### 7.1 Table Structure

```html
<table aria-label="Assessment Results">
  <caption>Assessment Results for Course: Cybersecurity Fundamentals</caption>
  <thead>
    <tr>
      <th scope="col" aria-sort="ascending">Student Name</th>
      <th scope="col">Score</th>
      <th scope="col">Status</th>
      <th scope="col">Date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Alice Johnson</th>
      <td>92%</td>
      <td>Passed</td>
      <td>2026-07-15</td>
    </tr>
  </tbody>
</table>
```

### 7.2 Chart Accessibility

| Requirement | Implementation |
|---|---|
| Text alternative | Data table summary below chart |
| Color independence | Patterns, shapes, or labels supplement color |
| Screen reader summary | `aria-describedby` links to summary |
| Data table fallback | "View as table" option for every chart |
| Keyboard interaction | Tab to focus chart, arrow keys to explore data points |

### 7.3 Report Export Accessibility

| Format | Accessibility Features |
|---|---|
| PDF | Tagged PDF, reading order, alt text, bookmarks |
| HTML | Semantic HTML, ARIA, keyboard navigation |
| CSV | Screen reader friendly (plain text) |
| JSON | Machine-readable (for integration) |

---

## 8. Accessible Documentation

### 8.1 Semantic HTML

```html
<article>
  <header>
    <h1>Module Title</h1>
    <p class="subtitle">Module description</p>
  </header>
  
  <nav aria-label="Page sections">
    <ol>
      <li><a href="#section-1">Section 1</a></li>
      <li><a href="#section-2">Section 2</a></li>
    </ol>
  </nav>
  
  <section id="section-1">
    <h2>Section 1</h2>
    <p>Content...</p>
  </section>
  
  <section id="section-2">
    <h2>Section 2</h2>
    <p>Content...</p>
  </section>
  
  <footer>
    <p>Last updated: 2026-07-19</p>
  </footer>
</article>
```

### 8.2 Heading Hierarchy

| Level | Usage | Example |
|---|---|---|
| `h1` | Page title (one per page) | "Authentication Module" |
| `h2` | Major sections | "Configuration" |
| `h3` | Subsections | "Password Policy" |
| `h4` | Sub-subsections | "Complexity Requirements" |
| `h5-h6` | Rarely used | Avoid if possible |

### 8.3 Documentation Accessibility Requirements

| Requirement | Implementation |
|---|---|
| Heading hierarchy | Logical h1 → h2 → h3 nesting |
| Link text | Descriptive text (not "click here") |
| Image alt text | Descriptive alt for all images |
| Code blocks | `<pre><code>` with language annotation |
| Lists | Proper `<ul>`, `<ol>`, `<dl>` markup |
| Tables | `<caption>`, `<th scope>`, header associations |
| Abbreviations | `<abbr title="...">` for all abbreviations |
| Language | `lang` attribute on `<html>` and inline foreign text |

---

## 9. Accessible Plugin Interfaces

### 9.1 SDK Accessibility Requirements

Plugins that provide UI components must meet these requirements:

| Requirement | SDK Enforcement |
|---|---|
| ARIA labels on all controls | SDK validates plugin UI components |
| Keyboard navigation | Plugin UI must support Tab/Enter/Escape |
| Focus management | Plugin must manage focus correctly |
| Color contrast | SDK checks contrast ratios |
| Error identification | Plugin must announce errors to screen readers |
| Form labels | All form inputs must have labels |

### 9.2 Plugin UI Validation

```python
class PluginA11yValidator:
    def validate(self, plugin_ui: PluginUI) -> list[A11yViolation]:
        violations = []
        
        # Check all buttons have accessible names
        for button in plugin_ui.buttons:
            if not button.aria_label and not button.text:
                violations.append(A11yViolation(
                    severity="critical",
                    component=button,
                    rule="button-name",
                    message="Button must have accessible name"
                ))
        
        # Check all images have alt text
        for image in plugin_ui.images:
            if not image.alt_text:
                violations.append(A11yViolation(
                    severity="critical",
                    component=image,
                    rule="image-alt",
                    message="Image must have alt text"
                ))
        
        return violations
```

---

## 10. Accessible Configuration

### 10.1 Form Accessibility

| Requirement | Implementation |
|---|---|
| Visible labels | Every input has associated `<label>` |
| Error messages | Inline, linked via `aria-describedby` |
| Required fields | `aria-required="true"` + visual indicator |
| Help text | `aria-describedby` links to help text |
| Grouping | `<fieldset>` + `<legend>` for related inputs |
| Autocomplete | `autocomplete` attribute for common fields |

### 10.2 Validation UX

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Password Settings                                          │
│  ─────────────────                                          │
│                                                             │
│  New Password *                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ••••••••••••                                         │   │
│  └─────────────────────────────────────────────────────┘   │
│  <span id="pw-help" class="help-text">                     │
│    Must be at least 8 characters with uppercase,           │
│    lowercase, number, and special character.               │
│  </span>                                                   │
│  <span id="pw-error" class="error-text" role="alert">     │
│    Password must contain at least one uppercase letter.    │
│  </span>                                                   │
│                                                             │
│  Confirm Password *                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ••••••••••••                                         │   │
│  └─────────────────────────────────────────────────────┘   │
│  <span id="pw-match-error" class="error-text" role="alert">│
│    Passwords do not match.                                 │
│  </span>                                                   │
│                                                             │
│  [Save Changes]  [Cancel]                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Accessible Error Handling

### 11.1 Error Announcement Rules

| Error Type | Announcement | Focus Behavior |
|---|---|---|
| Form validation | Inline `role="alert"` | Focus to first error field |
| API error | Toast notification `role="alert"` | Focus to toast |
| Page not found | Page title + description | Focus to h1 |
| Permission denied | Explanation + suggested action | Focus to main content |
| Session expired | Login redirect with explanation | Focus to login form |
| Network error | Offline explanation | Focus to error message |

### 11.2 Error Message Requirements

| Requirement | Example |
|---|---|
| Identify the field | "Email address is required" |
| Explain the problem | "Email address is not valid" |
| Suggest a solution | "Please enter a valid email address (e.g., user@example.com)" |
| Be concise | One sentence per error |
| Be visible | Not hidden or collapsed |
| Be announced | `role="alert"` for screen readers |

### 11.3 Focus Management on Errors

```typescript
function handleFormError(errors: FieldError[]) {
  // Announce error summary
  announcer.announce(`${errors.length} errors found. Please correct them.`);
  
  // Focus first error field
  const firstErrorField = document.querySelector(`[name="${errors[0].field}"]`);
  firstErrorField?.focus();
  
  // Update ARIA attributes
  errors.forEach(error => {
    const field = document.querySelector(`[name="${error.field}"]`);
    field?.setAttribute('aria-invalid', 'true');
    field?.setAttribute('aria-describedby', `${error.field}-error`);
  });
}
```

---

## 12. WCAG 2.2 AA Checklist

### 12.1 Perceivable

| Criterion | Requirement | Status |
|---|---|---|
| 1.1.1 Non-text Content | Alt text for all images | ✅ |
| 1.2.1 Audio-only/Video-only | Captions for video content | ✅ |
| 1.2.2 Captions | Captions for pre-recorded audio | ✅ |
| 1.2.3 Audio Description | Descriptions for video | ✅ |
| 1.2.5 Audio Description (Live) | Live descriptions | N/A |
| 1.3.1 Info and Relationships | Semantic HTML structure | ✅ |
| 1.3.2 Meaningful Sequence | Logical reading order | ✅ |
| 1.3.3 Sensory Characteristics | Not relying on color/shape alone | ✅ |
| 1.3.4 Orientation | Support portrait + landscape | ✅ |
| 1.3.5 Identify Input Purpose | autocomplete attributes | ✅ |
| 1.4.1 Use of Color | Color not sole indicator | ✅ |
| 1.4.2 Audio Control | No auto-playing audio | ✅ |
| 1.4.3 Contrast (Minimum) | 4.5:1 text, 3:1 large text | ✅ |
| 1.4.4 Resize Text | Up to 200% without loss | ✅ |
| 1.4.5 Images of Text | No images of text | ✅ |
| 1.4.10 Reflow | No horizontal scroll at 320px | ✅ |
| 1.4.11 Non-text Contrast | 3:1 for UI components | ✅ |
| 1.4.12 Text Spacing | No loss with custom spacing | ✅ |
| 1.4.13 Content on Hover/Focus | Dismissible, hoverable, persistent | ✅ |

### 12.2 Operable

| Criterion | Requirement | Status |
|---|---|---|
| 2.1.1 Keyboard | All functionality keyboard accessible | ✅ |
| 2.1.2 No Keyboard Trap | Escape from all components | ✅ |
| 2.1.4 Character Key Shortcuts | Remappable or disableable | ✅ |
| 2.2.1 Timing Adjustable | No time limits (or adjustable) | ✅ |
| 2.2.2 Pause, Stop, Hide | User control over auto-updating | ✅ |
| 2.3.1 Three Flashes | No flashing content | ✅ |
| 2.4.1 Bypass Blocks | Skip links provided | ✅ |
| 2.4.2 Page Titled | Descriptive page titles | ✅ |
| 2.4.3 Focus Order | Logical tab order | ✅ |
| 2.4.4 Link Purpose | Descriptive link text | ✅ |
| 2.4.5 Multiple Ways | Navigation + search | ✅ |
| 2.4.6 Headings and Labels | Descriptive headings/labels | ✅ |
| 2.4.7 Focus Visible | Visible focus indicator | ✅ |
| 2.4.11 Focus Not Obscured (Minimum) | Focus indicator not hidden | ✅ |
| 2.4.13 Focus Appearance | Focus indicator ≥ 3:1 contrast | ✅ |
| 2.5.1 Pointer Gestures | No multipoint gestures required | ✅ |
| 2.5.2 Pointer Cancellation | Down-event doesn't activate | ✅ |
| 2.5.3 Label in Name | Visible label matches accessible name | ✅ |
| 2.5.4 Motion Actuation | No motion-triggered actions | ✅ |

### 12.3 Understandable

| Criterion | Requirement | Status |
|---|---|---|
| 3.1.1 Language of Page | `lang` attribute on `<html>` | ✅ |
| 3.1.2 Language of Parts | `lang` on foreign text | ✅ |
| 3.2.1 On Focus | No unexpected context change | ✅ |
| 3.2.2 On Input | Predictable input behavior | ✅ |
| 3.2.3 Consistent Navigation | Navigation consistent across pages | ✅ |
| 3.2.4 Consistent Identification | Same components same labels | ✅ |
| 3.2.6 Consistent Help | Help in consistent location | ✅ |
| 3.3.1 Error Identification | Errors clearly identified | ✅ |
| 3.3.2 Labels or Instructions | Labels and help text provided | ✅ |
| 3.3.3 Error Suggestion | Suggested corrections | ✅ |
| 3.3.4 Error Prevention | Confirmation for critical actions | ✅ |
| 3.3.7 Redundant Entry | No redundant input required | ✅ |
| 3.3.8 Accessible Authentication | No cognitive function tests | ✅ |

### 12.4 Robust

| Criterion | Requirement | Status |
|---|---|---|
| 4.1.2 Name, Role, Value | ARIA for all custom components | ✅ |
| 4.1.3 Status Messages | `role="status"` for updates | ✅ |

---

## 13. Testing Strategy

### 13.1 Automated Testing

| Tool | Purpose | Frequency |
|---|---|---|
| axe-core | Automated a11y scanning | Every component build |
| eslint-plugin-jsx-a11y | React a11y linting | Every commit |
| lighthouse | Overall a11y score | Per release |
| jest-axe | Unit test a11y checks | Every test run |

### 13.2 Manual Testing

| Test | Method | Frequency |
|---|---|---|
| Keyboard navigation | Manual tab-through | Per release |
| Screen reader testing | NVDA/VoiceOver | Per release |
| High contrast | Windows HC mode | Per release |
| Reduced motion | System preference | Per release |
| Zoom testing | 200% browser zoom | Per release |
| Color contrast | Manual check | Per release |

### 13.3 A11y Test Suite Structure

```
tests/a11y/
├── test_keyboard_navigation.py     # Keyboard-only walkthroughs
├── test_screen_reader.py           # Screen reader announcements
├── test_color_contrast.py          # Contrast ratio checks
├── test_heading_hierarchy.py       # Heading structure
├── test_form_accessibility.py      # Form labels, errors
├── test_table_accessibility.py     # Table structure
├── test_modal_accessibility.py     # Modal focus management
├── test_navigation_accessibility.py # Skip links, landmarks
├── test_plugin_a11y.py             # Plugin UI validation
└── test_report_a11y.py            # Report accessibility
```

### 13.4 CI/CD Integration

```yaml
# .github/workflows/a11y.yml
a11y-tests:
  runs-on: ubuntu-latest
  steps:
    - name: Run axe-core tests
      run: pytest tests/a11y/ -v --tb=short
    
    - name: Run ESLint a11y rules
      run: npm run lint:a11y
    
    - name: Check color contrast
      run: python tools/a11y/contrast_checker.py
    
    - name: Validate heading hierarchy
      run: python tools/a11y/heading_checker.py
```

---

## 14. Accessibility Metrics

| Metric | Target | Measurement |
|---|---|---|
| axe-core violations | 0 critical, 0 serious | Automated scan |
| Lighthouse a11y score | ≥ 95 | Automated scan |
| Keyboard navigation | 100% workflows | Manual test |
| Screen reader coverage | 100% interactive elements | Manual test |
| Color contrast | 100% compliance | Automated + manual |
| Focus indicator visibility | 100% elements | Automated scan |
| ARIA label coverage | 100% custom components | ESLint check |
| Heading hierarchy | Valid on all pages | Automated check |
