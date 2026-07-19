# AuthShield Lab — Plugin Accessibility Requirements

> **Version:** 1.0.0
> **Status:** Authoritative
> **See also:** [Plugin SDK](PLUGIN_SDK.md) · [Plugin Manifest](PLUGIN_MANIFEST_SPECIFICATION.md)

---

## 1. Overview

Accessibility is **mandatory** for all AuthShield Lab plugins. The platform serves
cybersecurity education to a diverse audience, and every plugin must be usable by people
with disabilities. Accessibility is not optional — plugins that fail accessibility checks
cannot be published.

---

## 2. Mandatory Requirements

### 2.1 Keyboard Navigation

**Every** interactive element must be accessible via keyboard alone.

**Requirements:**
- All buttons, links, inputs, and controls must be focusable.
- Focus order must be logical and follow visual layout.
- Focus must be visible (focus ring or highlight).
- Keyboard shortcuts must not conflict with platform or OS shortcuts.
- Escape key must close modals and dropdowns.
- Tab and Shift+Tab must navigate between interactive elements.
- Arrow keys must navigate within composite widgets (menus, toolbars, lists).
- Enter and Space must activate buttons and links.

**Implementation:**

```typescript
// React component example
const ThreatPanel: React.FC = () => {
  return (
    <div role="region" aria-label="Threat Dashboard">
      <button
        tabIndex={0}
        onClick={handleScan}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleScan();
          }
        }}
      >
        Run Scan
      </button>
    </div>
  );
};
```

### 2.2 Screen Reader Support

All content must be accessible to screen readers (JAWS, NVDA, VoiceOver, TalkBack).

**Requirements:**
- All images must have `alt` text (decorative images: `alt=""`).
- All form inputs must have associated `<label>` elements.
- Dynamic content updates must use ARIA live regions.
- Complex widgets must use appropriate ARIA roles and properties.
- Tables must have headers and captions.
- Landmarks must be used for page structure.

**ARIA Implementation:**

```typescript
// Live region for dynamic updates
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  {threatCount > 0
    ? `${threatCount} threats detected`
    : 'No threats detected'}
</div>

// Complex widget with ARIA
<div
  role="tree"
  aria-label="Threat Category Tree"
  aria-expanded={isExpanded}
>
  <div
    role="treeitem"
    aria-selected={isSelected}
    tabIndex={isSelected ? 0 : -1}
  >
    Network Threats
  </div>
</div>
```

### 2.3 High Contrast Compatibility

Plugins must work in high contrast modes (Windows High Contrast, macOS Increase Contrast).

**Requirements:**
- Use CSS custom properties for colors (not hardcoded hex values).
- Use `currentColor` for borders and icons.
- Ensure text is visible against both light and dark backgrounds.
- Use `forced-colors` media query for Windows High Contrast.
- Provide sufficient contrast ratios (WCAG AA: 4.5:1 for normal text, 3:1 for large text).

**Implementation:**

```css
.threat-card {
  border: 2px solid var(--border-color, currentColor);
  background: var(--card-background, transparent);
  color: var(--text-color, inherit);
}

@media (forced-colors: active) {
  .threat-card {
    border: 2px solid ButtonText;
    background: Canvas;
    color: CanvasText;
  }

  .threat-icon {
    forced-color-adjust: none;
  }
}
```

### 2.4 Font Scaling Support

Plugins must remain usable when the user scales fonts up to 200%.

**Requirements:**
- Use relative units (`rem`, `em`, `%`) for font sizes, not `px`.
- Layout must not break at 200% zoom.
- Text must not be clipped or overlap.
- Scrollable regions must be keyboard-accessible.
- Tooltips must be dismissible and not rely on hover-only.

**Implementation:**

```css
/* Good: relative units */
.threat-title {
  font-size: 1.25rem;
  line-height: 1.5;
}

.threat-description {
  font-size: 0.875rem;
  margin-bottom: 1em;
}

/* Bad: absolute units */
.threat-title {
  font-size: 20px; /* DO NOT USE */
  line-height: 24px; /* DO NOT USE */
}
```

### 2.5 Reduced Motion Respect

Plugins must respect the `prefers-reduced-motion` media query.

**Requirements:**
- All animations must be disabled when `prefers-reduced-motion: reduce` is active.
- Transitions should be instant or very short (max 100ms).
- Auto-playing animations must have a pause/stop control.
- Parallax effects must be disabled.

**Implementation:**

```css
.threat-pulse {
  animation: pulse 2s infinite;
}

@media (prefers-reduced-motion: reduce) {
  .threat-pulse {
    animation: none;
  }

  .transition-all {
    transition: none !important;
  }
}
```

### 2.6 Accessible Documentation

All plugin documentation must be accessible:

- Written at a reading level appropriate for the target audience.
- Use clear, concise language.
- Provide alt text for all images.
- Use proper heading hierarchy (H1 → H2 → H3).
- Use lists for list content.
- Provide text alternatives for diagrams.
- Ensure PDF documents are tagged for accessibility.

### 2.7 Localization Support

Plugins must support localization for accessibility:

- All user-visible text must use the Localization API (not hardcoded strings).
- Date and number formats must respect locale.
- Text direction (LTR/RTL) must be handled.
- String expansion must not break layouts.

### 2.8 Accessible Error Messages

Error messages must be accessible:

- Announced to screen readers via live regions.
- Visually associated with the affected input field.
- Provide clear, actionable guidance.
- Use `aria-describedby` to link errors to inputs.
- Use `aria-invalid` to mark invalid fields.

**Implementation:**

```typescript
<div>
  <label htmlFor="port-input">Port Number</label>
  <input
    id="port-input"
    type="number"
    aria-invalid={hasError}
    aria-describedby={hasError ? 'port-error' : undefined}
  />
  {hasError && (
    <div id="port-error" role="alert" aria-live="assertive">
      Port must be between 1 and 65535.
    </div>
  )}
</div>
```

### 2.9 Accessible Reports

Reports generated by plugins must be accessible:

- Tables must have proper `<th>`, `<caption>`, and `scope` attributes.
- Charts must have text alternatives.
- PDF exports must be tagged for accessibility.
- Data visualizations must have a text summary.

---

## 3. WCAG 2.2 AA Checklist for Plugins

| # | Criterion | Requirement | Status |
|---|---|---|---|
| 1.1.1 | Non-text Content | All images have alt text | Mandatory |
| 1.2.1 | Audio-only/Video-only | Alternatives for media | Mandatory |
| 1.3.1 | Info and Relationships | Semantic HTML structure | Mandatory |
| 1.3.2 | Meaningful Sequence | Logical reading order | Mandatory |
| 1.3.3 | Sensory Characteristics | Don't rely on color/shape alone | Mandatory |
| 1.3.4 | Orientation | Support portrait and landscape | Mandatory |
| 1.3.5 | Identify Input Purpose | Autocomplete attributes | Mandatory |
| 1.4.1 | Use of Color | Color is not the only indicator | Mandatory |
| 1.4.3 | Contrast Minimum | 4.5:1 ratio (normal text) | Mandatory |
| 1.4.4 | Resize Text | Up to 200% without loss | Mandatory |
| 1.4.5 | Images of Text | Use real text, not images | Mandatory |
| 1.4.10 | Reflow | No horizontal scrolling at 400% | Mandatory |
| 1.4.11 | Non-text Contrast | 3:1 for UI components | Mandatory |
| 1.4.12 | Text Spacing | No loss with increased spacing | Mandatory |
| 1.4.13 | Content on Hover/Focus | Dismissible, hoverable, persistent | Mandatory |
| 2.1.1 | Keyboard | All functionality via keyboard | Mandatory |
| 2.1.2 | No Keyboard Trap | Escape from any component | Mandatory |
| 2.1.4 | Character Key Shortcuts | Remappable or disableable | Mandatory |
| 2.4.1 | Bypass Blocks | Skip navigation links | Mandatory |
| 2.4.2 | Page Titled | Descriptive page titles | Mandatory |
| 2.4.3 | Focus Order | Logical focus order | Mandatory |
| 2.4.5 | Multiple Ways | Search or sitemap | Recommended |
| 2.4.6 | Headings and Labels | Descriptive headings | Mandatory |
| 2.4.7 | Focus Visible | Visible focus indicator | Mandatory |
| 2.4.11 | Focus Not Obscured | Focus indicator not hidden | Mandatory |
| 2.4.13 | Focus Appearance | Focus indicator meets size/contrast | Mandatory |
| 2.5.1 | Pointer Gestures | Multipoint or path alternatives | Mandatory |
| 2.5.2 | Pointer Cancellation | Up-event activation | Mandatory |
| 2.5.3 | Label in Name | Visible label matches accessible name | Mandatory |
| 2.5.4 | Motion Actuation | Alternatives for motion triggers | Mandatory |
| 3.1.1 | Language of Page | `lang` attribute set | Mandatory |
| 3.1.2 | Language of Parts | `lang` for language changes | Mandatory |
| 3.2.1 | On Focus | No unexpected context changes | Mandatory |
| 3.2.2 | On Input | No unexpected context changes | Mandatory |
| 3.2.3 | Consistent Navigation | Same navigation across pages | Mandatory |
| 3.2.4 | Consistent Identification | Same components have same names | Mandatory |
| 3.3.1 | Error Identification | Errors clearly identified | Mandatory |
| 3.3.2 | Labels or Instructions | Input labels provided | Mandatory |
| 3.3.3 | Error Suggestion | Suggest corrections | Recommended |
| 3.3.4 | Error Prevention | Confirm before submission | Recommended |
| 3.3.7 | Redundant Entry | Don't ask for same info twice | Mandatory |
| 3.3.8 | Accessible Authentication | No cognitive test authentication | Mandatory |
| 4.1.2 | Name, Role, Value | ARIA for custom components | Mandatory |
| 4.1.3 | Status Messages | `role="status"` for updates | Mandatory |

---

## 4. Automated Accessibility Testing Requirements

### 4.1 Required Tools

| Tool | Purpose | Integration |
|---|---|---|
| **axe-core** | Automated WCAG checks | CI/CD pipeline |
| **eslint-plugin-jsx-a11y** | React JSX accessibility linting | Editor + CI |
| **jest-axe** | Unit test accessibility assertions | Unit tests |
| **pa11y** | Page-level accessibility testing | Integration tests |
| **Lighthouse** | Performance + accessibility audit | CI/CD pipeline |

### 4.2 Automated Test Example

```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ThreatPanel } from './ThreatPanel';

expect.extend(toHaveNoViolations);

describe('ThreatPanel Accessibility', () => {
  it('should have no axe violations', async () => {
    const { container } = render(<ThreatPanel />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### 4.3 CI/CD Integration

```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests
on: [push, pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run axe-core tests
        run: npm run test:a11y
      - name: Run pa11y
        run: npx pa11y http://localhost:3000
      - name: Run Lighthouse
        run: npx lighthouse http://localhost:3000 --only-categories=accessibility --output=json
```

---

## 5. Manual Accessibility Testing Requirements

### 5.1 Keyboard-Only Testing

For each plugin, manually verify:

1. Tab through all interactive elements.
2. Activate each element with Enter or Space.
3. Navigate menus and dropdowns with arrow keys.
4. Close modals with Escape.
5. Verify focus order matches visual order.
6. Verify focus is always visible.

### 5.2 Screen Reader Testing

Test with at least two screen readers:

| Screen Reader | Browser | Platform |
|---|---|---|
| NVDA | Firefox | Windows |
| JAWS | Chrome | Windows |
| VoiceOver | Safari | macOS |
| TalkBack | Chrome | Android |

Verify:
- All content is read in logical order.
- All interactive elements are announced with role and state.
- Dynamic updates are announced via live regions.
- Images and icons have appropriate alt text.

### 5.3 Visual Testing

1. **Zoom to 200%** — verify no content is clipped or overlaps.
2. **High contrast mode** — verify all text and controls are visible.
3. **Color blindness simulation** — verify information is not conveyed by color alone.
4. **Reduced motion** — verify animations are disabled.
5. **Custom font sizes** — verify layout remains intact.

---

## 6. Accessibility Certification Process

### 6.1 Self-Certification

Plugin developers must complete an accessibility self-certification form:

```json
{
  "plugin_id": "threat-dashboard",
  "wcag_level": "AA",
  "self_certification": {
    "keyboard_navigation": true,
    "screen_reader_tested": true,
    "high_contrast_compatible": true,
    "font_scaling_supported": true,
    "reduced_motion_respected": true,
    "automated_tests_passing": true,
    "manual_tests_completed": true,
    "screen_readers_tested": ["NVDA", "VoiceOver"],
    "test_date": "2026-07-15"
  }
}
```

### 6.2 Automated Gate

The CI/CD pipeline enforces:

- Zero axe-core violations (critical and serious).
- Zero eslint-plugin-jsx-a11y errors.
- Lighthouse accessibility score ≥ 90.

### 6.3 Manual Review

For plugins claiming WCAG AA or AAA compliance:

1. Manual keyboard testing report.
2. Screen reader testing report.
3. Visual testing report.
4. All reports included in the plugin package under `docs/accessibility/`.

### 6.4 Certification Badge

Plugins that pass all checks receive an accessibility certification badge:

```
♿ WCAG 2.2 AA Certified
   Last audited: 2026-07-15
   Audit report: docs/accessibility/audit-report.pdf
```

---

## 7. Accessibility Metadata in Manifest

```json
{
  "accessibility_metadata": {
    "wcag_level": "AA",
    "keyboard_only": true,
    "screen_reader_tested": true,
    "high_contrast": true,
    "reduced_motion": true,
    "font_scaling": true,
    "notes": "All charts have text alternatives. Color is not the sole indicator of threat severity."
  }
}
```

---

## 8. Common Accessibility Mistakes

| Mistake | Fix |
|---|---|
| Missing alt text on images | Add descriptive alt text to all images |
| No focus indicator | Add visible focus styles |
| Color-only indicators | Add text/icon alternatives |
| Missing form labels | Use `<label>` or `aria-label` |
| No keyboard access | Add `tabIndex` and keyboard handlers |
| Hardcoded pixel sizes | Use relative units (rem, em) |
| No ARIA roles on custom widgets | Add appropriate ARIA roles |
| Missing skip navigation | Add skip-to-content link |
| No live regions for updates | Add `role="status"` or `aria-live` |
| Hover-only tooltips | Make tooltips focusable and dismissible |

---

## 9. References

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apd/)
- [Plugin SDK](PLUGIN_SDK.md)
- [Plugin Manifest](PLUGIN_MANIFEST_SPECIFICATION.md)

---

*End of document.*
