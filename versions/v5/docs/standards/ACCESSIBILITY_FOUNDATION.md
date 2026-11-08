# AuthShield Lab — Accessibility Foundation

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab targets WCAG 2.2 Level AA compliance across all user-facing components. This document defines the accessibility architecture, testing strategy, and implementation requirements. Accessibility is a first-class design constraint, not an afterthought.

---

## 2. WCAG 2.2 AA Compliance

### 2.1 Compliance Target

| WCAG Principle | Target | Coverage |
|---------------|--------|----------|
| **Perceivable** | 100% of criteria | All text, images, multimedia, UI components |
| **Operable** | 100% of criteria | Keyboard, timing, navigation, input modalities |
| **Understandable** | 100% of criteria | Language, predictable behavior, input assistance |
| **Robust** | 100% of criteria | Compatible with assistive technologies |

### 2.2 Key WCAG 2.2 Criteria

| Criterion | Level | Implementation |
|-----------|-------|---------------|
| 1.1.1 Non-text Content | A | Alt text for images; ARIA labels for icons |
| 1.3.1 Info and Relationships | A | Semantic HTML; proper heading hierarchy |
| 1.3.2 Meaningful Sequence | A | Logical DOM order; CSS logical properties |
| 1.3.3 Sensory Characteristics | A | Not relying solely on color/shape/position |
| 1.4.1 Use of Color | A | Color is not sole means of conveying info |
| 1.4.3 Contrast Minimum | AA | 4.5:1 for normal text; 3:1 for large text |
| 1.4.4 Resize Text | AA | Text resizable to 200% without loss |
| 1.4.5 Images of Text | AA | No images of text; use CSS for styling |
| 1.4.11 Non-text Contrast | AA | 3:1 for UI components and graphical objects |
| 2.1.1 Keyboard | A | All functionality via keyboard |
| 2.1.2 No Keyboard Trap | A | Focus can always be moved away |
| 2.4.1 Bypass Blocks | A | Skip links for repeated content |
| 2.4.2 Page Titled | A | Descriptive page titles |
| 2.4.3 Focus Order | A | Logical focus order |
| 2.4.6 Headings and Labels | AA | Descriptive headings and labels |
| 2.4.11 Focus Not Obscured | AA | Focused element not hidden by sticky content |
| 2.5.8 Target Size | AA | Minimum 24x24px touch targets |
| 3.1.1 Language of Page | A | `lang` attribute on `<html>` |
| 3.2.1 On Focus | A | No unexpected context changes on focus |
| 3.2.2 On Input | A | No unexpected context changes on input |
| 3.3.1 Error Identification | A | Errors identified and described |
| 3.3.3 Error Suggestion | AA | Suggestions for correcting errors |
| 3.3.4 Error Prevention | AA | Confirmation for important submissions |
| 4.1.2 Name, Role, Value | A | ARIA for custom components |

---

## 3. Screen Reader Support

### 3.1 ARIA Labels

```tsx
// Every interactive element must have an accessible name
<button aria-label="Close dialog">✕</button>
<button aria-label="Delete assessment">🗑️</button>

// Form inputs must have associated labels
<label htmlFor="email">Email address</label>
<input id="email" type="email" aria-required="true" />

// Complex components need descriptive ARIA
<div
  role="region"
  aria-label="Assessment results"
  aria-describedby="results-description"
>
  <p id="results-description">Your scores for completed assessments</p>
  {/* results content */}
</div>
```

### 3.2 Live Regions

```tsx
// Announce dynamic content changes
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  {statusMessage}
</div>

// Announce urgent messages
<div
  role="alert"
  aria-live="assertive"
>
  {errorMessage}
</div>

// Announce progress
<div
  role="progressbar"
  aria-valuenow={progress}
  aria-valuemin={0}
  aria-valuemax={100}
  aria-label={`Assessment progress: ${progress}%`}
/>
```

### 3.3 Landmark Roles

```tsx
// Use semantic HTML5 elements for landmarks
<header role="banner">
  <nav aria-label="Main navigation">
    {/* navigation items */}
  </nav>
</header>

<main role="main">
  <aside aria-label="Sidebar">
    {/* sidebar content */}
  </aside>
  <section aria-label="Content">
    {/* main content */}
  </section>
</main>

<footer role="contentinfo">
  {/* footer content */}
</footer>

// Skip links for keyboard users
<a href="#main-content" className="skip-link">
  Skip to main content
</a>
```

### 3.4 Screen Reader Testing Checklist

| Test | Screen Reader | Platform |
|------|--------------|----------|
| Page navigation | NVDA | Windows |
| Form completion | NVDA | Windows |
| Modal dialogs | NVDA | Windows |
| Live regions | NVDA | Windows |
| Keyboard navigation | VoiceOver | macOS |
| iOS navigation | VoiceOver | iOS |
| Android navigation | TalkBack | Android |

---

## 4. Keyboard Navigation

### 4.1 Focus Management

```tsx
// Focus trap for modal dialogs
function Modal({ isOpen, onClose, children }) {
  const modalRef = useRef(null);
  
  useEffect(() => {
    if (isOpen) {
      // Store previous focus
      const previousFocus = document.activeElement;
      
      // Focus modal
      modalRef.current?.focus();
      
      return () => {
        // Restore previous focus on close
        previousFocus?.focus();
      };
    }
  }, [isOpen]);

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      tabIndex={-1}
    >
      {children}
    </div>
  );
}
```

### 4.2 Skip Links

```tsx
// Skip navigation links
function SkipLinks() {
  return (
    <div className="skip-links">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <a href="#navigation" className="skip-link">
        Skip to navigation
      </a>
      <a href="#search" className="skip-link">
        Skip to search
      </a>
    </div>
  );
}
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary);
  color: var(--color-text-inverse);
  padding: 8px;
  z-index: 100;
  transition: top 0.2s;
}

.skip-link:focus {
  top: 0;
}
```

### 4.3 Tab Order

```tsx
// Ensure logical tab order
function AssessmentForm() {
  return (
    <form>
      {/* Tab order follows visual order */}
      <input type="text" tabIndex={0} aria-label="Question 1" />
      <input type="text" tabIndex={0} aria-label="Question 2" />
      <select tabIndex={0} aria-label="Select answer">
        <option>Option A</option>
        <option>Option B</option>
      </select>
      <button type="submit" tabIndex={0}>
        Submit
      </button>
    </form>
  );
}
```

### 4.4 Keyboard Shortcuts

| Key | Action | Context |
|-----|--------|---------|
| `Tab` | Move to next focusable element | Global |
| `Shift+Tab` | Move to previous focusable element | Global |
| `Enter` | Activate button/link | Global |
| `Space` | Activate button/toggle | Global |
| `Escape` | Close modal/dialog | Modal |
| `Arrow keys` | Navigate within list/menu | Menu |
| `Home` | Move to first item | List |
| `End` | Move to last item | List |
| `Ctrl+S` | Save (with confirmation) | Form |

---

## 5. High Contrast Support

### 5.1 CSS Custom Properties

```css
:root {
  /* Light theme tokens */
  --color-background: #ffffff;
  --color-surface: #f5f5f5;
  --color-text-primary: #1a1a1a;
  --color-text-secondary: #666666;
  --color-border: #cccccc;
  --color-focus: #0066cc;
  --color-error: #d32f2f;
  --color-success: #388e3c;
  --color-warning: #f57c00;
}

[data-theme="dark"] {
  --color-background: #121212;
  --color-surface: #1e1e1e;
  --color-text-primary: #ffffff;
  --color-text-secondary: #b0b0b0;
  --color-border: #333333;
  --color-focus: #4da6ff;
  --color-error: #ef5350;
  --color-success: #66bb6a;
  --color-warning: #ffa726;
}

@media (prefers-contrast: high) {
  :root {
    --color-background: #000000;
    --color-surface: #1a1a1a;
    --color-text-primary: #ffffff;
    --color-text-secondary: #ffffff;
    --color-border: #ffffff;
    --color-focus: #ffff00;
    --color-error: #ff6b6b;
    --color-success: #69db7c;
    --color-warning: #ffd43b;
  }
}
```

### 5.2 Focus Indicators

```css
/* Visible focus indicators for all interactive elements */
:focus-visible {
  outline: 3px solid var(--color-focus);
  outline-offset: 2px;
}

/* Remove default focus ring for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}

/* High contrast focus for high contrast mode */
@media (prefers-contrast: high) {
  :focus-visible {
    outline: 3px solid var(--color-focus);
    outline-offset: 3px;
    box-shadow: 0 0 0 6px rgba(0, 102, 204, 0.3);
  }
}
```

---

## 6. Reduced Motion Support

### 6.1 Media Query

```css
/* Disable animations for users who prefer reduced motion */
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

### 6.2 React Hook

```tsx
// Hook for motion preference
function useReducedMotion(): boolean {
  const [prefersReduced, setPrefersReduced] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReduced(mediaQuery.matches);
    
    const handler = (e: MediaQueryListEvent) => setPrefersReduced(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);
  
  return prefersReduced;
}

// Usage
function AnimatedComponent() {
  const prefersReduced = useReducedMotion();
  
  return (
    <div
      style={{
        transition: prefersReduced ? 'none' : 'transform 0.3s ease',
        transform: isHovered ? 'scale(1.05)' : 'scale(1)',
      }}
    >
      {/* Content */}
    </div>
  );
}
```

---

## 7. Font Scaling

### 7.1 Responsive Typography

```css
/* Use rem/em for font sizes (never px for text) */
:root {
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */
}

/* Line heights for readability */
:root {
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}

/* Text must be resizable to 200% without loss */
html {
  font-size: 100%; /* 16px base */
}

/* Ensure no horizontal overflow at 200% zoom */
@media screen and (min-width: 1px) {
  body {
    overflow-x: hidden;
  }
}
```

### 7.2 Text Overflow

```css
/* Handle long translations gracefully */
.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

/* Provide accessible alternative for truncated text */
.text-truncate[title]::after {
  content: " (";
}

.text-truncate[title]::before {
  content: "... )";
  clip-path: inset(0 100% 0 0);
  position: absolute;
}
```

---

## 8. Accessible Charts

### 8.1 Data Table Alternative

```tsx
// Every chart must have a data table alternative
function AccessibleChart({ data, chartType }) {
  const [showTable, setShowTable] = useState(false);
  
  return (
    <div>
      {/* Chart with ARIA description */}
      <div
        role="img"
        aria-label={`Chart showing ${chartType} data`}
        aria-describedby={`chart-desc-${data.id}`}
      >
        {/* Chart visualization */}
      </div>
      <p id={`chart-desc-${data.id}`} className="sr-only">
        {generateChartDescription(data)}
      </p>
      
      {/* Toggle for data table */}
      <button
        onClick={() => setShowTable(!showTable)}
        aria-expanded={showTable}
      >
        {showTable ? 'Hide data table' : 'Show data table'}
      </button>
      
      {showTable && (
        <table aria-label={`Data table for ${chartType}`}>
          <thead>
            <tr>
              <th scope="col">Category</th>
              <th scope="col">Value</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item) => (
              <tr key={item.id}>
                <td>{item.category}</td>
                <td>{item.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

### 8.2 Chart ARIA Descriptions

```tsx
// Generate human-readable chart descriptions
function generateChartDescription(data: ChartData): string {
  const max = Math.max(...data.items.map(i => i.value));
  const min = Math.min(...data.items.map(i => i.value));
  const maxItem = data.items.find(i => i.value === max);
  const minItem = data.items.find(i => i.value === min);
  
  return `This ${data.chartType} chart shows ${data.items.length} data points. ` +
    `The highest value is ${max} (${maxItem.category}). ` +
    `The lowest value is ${min} (${minItem.category}). ` +
    `The average is ${Math.round(data.items.reduce((a, b) => a + b.value, 0) / data.items.length)}.`;
}
```

---

## 9. Accessible Tables

### 9.1 Semantic Table Structure

```tsx
// Accessible data table
function AssessmentResultsTable({ results }) {
  return (
    <table aria-label="Assessment results">
      <caption>Results for all completed assessments</caption>
      <thead>
        <tr>
          <th scope="col">Assessment</th>
          <th scope="col">Score</th>
          <th scope="col">Date</th>
          <th scope="col">Status</th>
        </tr>
      </thead>
      <tbody>
        {results.map((result) => (
          <tr key={result.id}>
            <th scope="row">{result.name}</th>
            <td>{result.score}%</td>
            <td>{formatDate(result.date)}</td>
            <td>
              <StatusBadge status={result.status} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### 9.2 Table Accessibility Requirements

| Requirement | Implementation |
|------------|---------------|
| **Caption** | `<caption>` element describing table purpose |
| **Column headers** | `<th scope="col">` for all columns |
| **Row headers** | `<th scope="row">` for first column |
| **Sortable columns** | `aria-sort="ascending/descending/none"` |
| **Empty cells** | Explicitly marked with `aria-label="No data"` |
| **Responsive** | Scrollable container with `role="region"` and `aria-label` |
| **Loading state** | `aria-busy="true"` during data fetch |

---

## 10. Accessible Forms

### 10.1 Form Labels and Errors

```tsx
// Accessible form field
function FormField({ id, label, error, required, children }) {
  return (
    <div className="form-field">
      <label htmlFor={id}>
        {label}
        {required && <span aria-hidden="true">*</span>}
        {required && <span className="sr-only"> (required)</span>}
      </label>
      
      {children}
      
      {error && (
        <div
          id={`${id}-error`}
          role="alert"
          className="form-error"
        >
          {error}
        </div>
      )}
      
      <div id={`${id}-hint`} className="form-hint">
        {/* Help text */}
      </div>
    </div>
  );
}

// Usage
<FormField
  id="email"
  label="Email address"
  error={errors.email}
  required
>
  <input
    id="email"
    type="email"
    aria-required="true"
    aria-invalid={!!errors.email}
    aria-describedby={`${errors.email ? 'email-error' : ''} email-hint`}
  />
</FormField>
```

### 10.2 Error Summary

```tsx
// Accessible error summary at form top
function ErrorSummary({ errors }) {
  if (Object.keys(errors).length === 0) return null;
  
  return (
    <div
      role="alert"
      aria-labelledby="error-summary-title"
      className="error-summary"
    >
      <h2 id="error-summary-title">
        There are {Object.keys(errors).length} errors in this form
      </h2>
      <ul>
        {Object.entries(errors).map(([field, message]) => (
          <li key={field}>
            <a href={`#${field}`}>
              {message}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 11. Accessible Reports

### 11.1 Report Accessibility

```html
<!-- PDF report structure -->
<html lang="en">
<head>
  <title>Assessment Report - AuthShield Lab</title>
</head>
<body>
  <main role="main">
    <h1>Assessment Report</h1>
    
    <section aria-labelledby="summary-heading">
      <h2 id="summary-heading">Summary</h2>
      <dl>
        <dt>User</dt>
        <dd>Alice Johnson</dd>
        <dt>Assessment</dt>
        <dd>Phishing Awareness 101</dd>
        <dt>Score</dt>
        <dd>85%</dd>
      </dl>
    </section>
    
    <section aria-labelledby="results-heading">
      <h2 id="results-heading">Detailed Results</h2>
      <table>
        <caption>Question-by-question results</caption>
        <thead>
          <tr>
            <th scope="col">Question</th>
            <th scope="col">Your Answer</th>
            <th scope="col">Correct Answer</th>
            <th scope="col">Result</th>
          </tr>
        </thead>
        <tbody>
          <!-- rows -->
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
```

### 11.2 Reading Order

| Element | Reading Order |
|---------|--------------|
| **Headings** | Hierarchical (h1 → h2 → h3) |
| **Tables** | Row by row, cell by cell |
| **Lists** | Item by item |
| **Forms** | Label → input → error |
| **Modals** | Modal title → content → actions |
| **Charts** | Description → data table alternative |

---

## 12. Testing Strategy

### 12.1 Automated Testing (axe-core)

```typescript
// axe-core integration for CI/CD
import { AxePuppeteer } from '@axe-core/puppeteer';
import puppeteer from 'puppeteer';

async function testAccessibility(url: string): Promise<void> {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto(url);
  
  const results = await new AxePuppeteer(page).analyze();
  
  if (results.violations.length > 0) {
    console.error('Accessibility violations found:');
    results.violations.forEach(violation => {
      console.error(`  ${violation.impact}: ${violation.description}`);
      console.error(`    Help: ${violation.helpUrl}`);
      console.error(`    Elements: ${violation.nodes.length}`);
    });
    process.exit(1);
  }
  
  await browser.close();
}
```

### 12.2 Manual Testing Checklist

| Test | Method | Frequency |
|------|--------|-----------|
| **Keyboard navigation** | Tab through entire page | Every PR |
| **Screen reader** | NVDA/VoiceOver walkthrough | Every release |
| **Zoom to 200%** | Browser zoom test | Every PR |
| **High contrast** | Windows High Contrast mode | Every release |
| **Reduced motion** | OS preference + manual check | Every release |
| **Color contrast** | axe-core + manual spot check | Every PR |
| **Focus indicators** | Visual inspection | Every PR |
| **Error handling** | Submit invalid forms | Every PR |

### 12.3 CI/CD Integration

```yaml
# .github/workflows/accessibility.yml
name: Accessibility Testing
on: [push, pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run axe-core tests
        run: |
          npm ci
          npx playwright install
          npm run test:a11y
      - name: Check color contrast
        run: |
          npx pa11y-ci --config .pa11yci.json
      - name: Validate HTML
        run: |
          npx html-validate "dist/**/*.html"
```

### 12.4 axe-core Configuration

```json
{
  ".pa11yci.json": {
    "defaults": {
      "standard": "WCAG2AA",
      "timeout": 10000,
      "wait": 2000,
      "runners": ["axe"],
      "chromeLaunchConfig": {
        "args": ["--no-sandbox"]
      }
    },
    "urls": [
      "http://localhost:3000/",
      "http://localhost:3000/dashboard",
      "http://localhost:3000/assessments",
      "http://localhost:3000/settings"
    ]
  }
}
```

---

## 13. Accessibility Scoring

### 13.1 Component Score

```python
from authshield.a11y_engine import AccessibilityScorer

scorer = AccessibilityScorer()

# Score a React component
score = scorer.score_component(AssessmentForm)
# AccessibilityScore(
#     total=95,
#     critical=0,
#     serious=1,
#     moderate=3,
#     minor=5,
#     violations=[
#         {"rule": "color-contrast", "severity": "serious", "count": 1},
#         {"rule": "label", "severity": "moderate", "count": 2},
#         {"rule": "region", "severity": "moderate", "count": 1},
#     ],
# )
```

### 13.2 Page Score

```python
# Score an entire page
score = scorer.score_page("http://localhost:3000/dashboard")
# AccessibilityScore(
#     total=88,
#     critical=0,
#     serious=2,
#     moderate=5,
#     minor=10,
# )
```

### 13.3 Score Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| 95-100 | Excellent | No action required |
| 85-94 | Good | Address serious violations |
| 70-84 | Needs Work | Address all serious and moderate violations |
| Below 70 | Poor | Block merge; address all violations |

---

## 14. Accessibility Logging

### 14.1 Violation Logging

```python
from authshield.logging import A11yLogger

a11y_logger = A11yLogger()

# Log violation found during testing
a11y_logger.log_violation(
    rule="color-contrast",
    severity="serious",
    element="button.submit",
    page="/assessment/submit",
    wcag_criterion="1.4.3",
    description="Insufficient color contrast ratio (2.5:1, required 4.5:1)",
    remediation="Increase contrast ratio to at least 4.5:1",
)

# Log remediation
a11y_logger.log_remediation(
    rule="color-contrast",
    page="/assessment/submit",
    remediated=True,
    new_contrast_ratio=5.2,
)
```

### 14.2 A11y Metrics

```python
from authshield.a11y_engine import A11yMetrics

metrics = A11yMetrics(db=session)

# Get accessibility score trend
trend = metrics.get_score_trend(days=30)
# [
#     {"date": "2026-07-01", "score": 82},
#     {"date": "2026-07-08", "score": 85},
#     {"date": "2026-07-15", "score": 88},
# ]

# Get violation breakdown
breakdown = metrics.get_violation_breakdown()
# {
#     "color-contrast": {"count": 5, "severity": "serious"},
#     "label": {"count": 12, "severity": "moderate"},
#     "region": {"count": 3, "severity": "minor"},
# }
```

---

## 15. Accessibility Documentation

### 15.1 Component Documentation

Every UI component must include:

```tsx
/**
 * AssessmentForm - Accessible form for submitting assessment answers
 * 
 * Accessibility:
 * - All fields have associated labels
 * - Error messages are linked via aria-describedby
 * - Required fields marked with aria-required
 * - Form has error summary at top
 * - Submit button has loading state with aria-busy
 * - Keyboard: Tab order follows visual order
 * - Screen reader: Form announces total questions and current position
 */
function AssessmentForm({ questions, onSubmit }) {
  // ...
}
```

### 15.2 Accessibility Statement

```markdown
# Accessibility Statement

AuthShield Lab is committed to ensuring digital accessibility for people with disabilities. We are continually improving the user experience for everyone, and applying the relevant accessibility standards.

## Conformance Status
We are working toward achieving WCAG 2.2 Level AA conformance.

## Known Limitations
- Some older assessment content may not have alt text for images
- Complex charts have data table alternatives but may not be fully optimized

## Feedback
If you encounter accessibility barriers, please contact us at accessibility@authshield.dev
```

---

*Document maintained by the AuthShield Lab Architecture Team. Review quarterly.*
