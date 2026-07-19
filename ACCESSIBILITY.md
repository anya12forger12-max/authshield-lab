# Accessibility Statement — AuthShield Lab

## Our Commitment

AuthShield Lab is committed to ensuring digital accessibility for all users. We believe that security education should be available to everyone, regardless of ability or technology. We continuously work toward full compliance with the **Web Content Accessibility Guidelines (WCAG) 2.2 Level AA**.

This statement applies to the AuthShield Lab web application, documentation site, and all user-facing interfaces.

---

## Current Compliance Status

| Criterion | Level | Status |
|-----------|-------|--------|
| WCAG 2.2 Level A | A | Fully compliant |
| WCAG 2.2 Level AA | AA | Substantially compliant (see known limitations) |
| WCAG 2.2 Level AAA | AAA | Partially compliant (not a target) |
| Section 508 | — | Compliant |
| EN 301 549 | — | Partially compliant |

### Last Audit

- **Date**: July 2026
- **Method**: Automated scanning (axe-core) + manual testing
- **Scope**: All user-facing pages and components
- **Result**: 0 critical issues, 2 minor issues identified (tracked below)

---

## Supported Assistive Technologies

We test and support the following assistive technologies:

### Screen Readers

| Screen Reader | Browser | Platform | Status |
|--------------|---------|----------|--------|
| NVDA | Firefox | Windows | Fully supported |
| NVDA | Chrome | Windows | Fully supported |
| JAWS | Chrome | Windows | Fully supported |
| JAWS | Edge | Windows | Fully supported |
| VoiceOver | Safari | macOS | Fully supported |
| VoiceOver | Safari | iOS | Fully supported |
| TalkBack | Chrome | Android | Fully supported |

### Browser Support

| Browser | Minimum Version | Keyboard Support | Screen Reader |
|---------|----------------|------------------|---------------|
| Chrome | 100+ | Full | Full |
| Firefox | 100+ | Full | Full |
| Safari | 16+ | Full | Full |
| Edge | 100+ | Full | Full |

### Additional Assistive Technologies

- **Switch navigation** — Full support
- **Voice control** (Dragon NaturallySpeaking, Voice Control) — Supported
- **Screen magnification** (ZoomText, built-in OS magnifiers) — Supported
- **Alternative keyboards** — Supported
- **Refreshable Braille displays** — Supported

---

## Accessibility Features

### Keyboard Navigation

- All interactive elements are focusable and operable via keyboard
- Focus order follows logical reading order
- Visible focus indicators are provided on all interactive elements
- Skip navigation links are available on every page
- Modal dialogs trap focus appropriately
- Keyboard shortcuts are discoverable and documented

### Visual Design

- Color contrast ratios meet WCAG 2.2 AA requirements:
  - Normal text: minimum 4.5:1
  - Large text: minimum 3:1
  - UI components: minimum 3:1
- Color is never the sole means of conveying information
- High contrast mode is available
- Reduced motion is supported (`prefers-reduced-motion`)
- Text can be resized up to 200% without loss of functionality

### Content Structure

- All pages use proper heading hierarchy (h1 → h2 → h3)
- Landmark regions are defined (`<main>`, `<nav>`, `<header>`, `<footer>`)
- Lists are marked up as lists (`<ul>`, `<ol>`, `<dl>`)
- Tables include proper headers and captions
- Language is set in the HTML (`lang` attribute)
- Page titles are descriptive and unique

### Forms

- All form fields have visible, associated labels
- Required fields are indicated both visually and programmatically
- Error messages are descriptive and associated with the relevant field
- Error messages are announced to screen readers via `aria-live`
- Form validation occurs on submit, not on blur
- Instructions are provided before the form, not only in placeholder text

### Images and Media

- All informative images have descriptive `alt` text
- Decorative images use `alt=""`
- Complex images include long descriptions
- Animations respect `prefers-reduced-motion`
- No content flashes more than 3 times per second

### Dynamic Content

- Live regions (`aria-live`) are used for dynamic updates
- Loading states are announced to screen readers
- State changes (expanded, selected, checked) use appropriate ARIA attributes
- Toast notifications are announced and dismissible

### Lab Interface

- Attack simulations provide audio descriptions of visual effects
- Terminal-like interfaces are accessible via screen readers
- All lab controls are keyboard accessible
- Progress indicators are accessible
- Timer countdowns can be paused or extended

---

## Known Limitations

We are transparent about current accessibility limitations:

| Issue | Description | Severity | Status | Target Fix |
|-------|-------------|----------|--------|------------|
| #A11Y-001 | Some lab visualization charts lack text alternatives | Medium | In progress | v5.1.0 |
| #A11Y-002 | Drag-and-drop scenario builder has limited keyboard support | Low | Planned | v5.2.0 |

### Workarounds

- **Charts**: Text-based data tables are provided alongside all charts
- **Drag-and-drop**: An alternative form-based interface is available for all scenario building tasks

We are actively working to resolve these limitations and welcome feedback on any additional barriers.

---

## Testing Methodology

### Automated Testing

- **axe-core** is integrated into our CI/CD pipeline and runs on every pull request
- **pa11y** is used for page-level accessibility audits
- **Lighthouse** accessibility scoring is tracked for all pages
- **eslint-plugin-jsx-a11y** catches common accessibility issues during development

### Manual Testing

- Keyboard-only navigation testing for all new features
- Screen reader testing (NVDA + Firefox, VoiceOver + Safari) for each release
- Manual color contrast verification using browser dev tools
- High contrast mode testing
- Zoom/magnification testing at 200% and 400%
- Voice control testing for major workflows

### User Testing

- We conduct periodic accessibility testing sessions with users of assistive technologies
- Feedback is collected and prioritized in our backlog
- We welcome volunteers for accessibility testing — contact us at accessibility@authshieldlab.dev

### Testing Checklist for Contributors

Before submitting a pull request, verify:

- [ ] All new interactive elements are keyboard accessible
- [ ] New components have proper ARIA attributes
- [ ] Color contrast meets AA requirements
- [ ] Automated tests pass (`npm run test:a11y`)
- [ ] Screen reader announcement works as expected
- [ ] Focus management is correct for dynamic content
- [ ] No content relies solely on color to convey meaning
- [ ] Images have appropriate `alt` text
- [ ] Form fields have associated labels

---

## Feedback Process

We welcome feedback on the accessibility of AuthShield Lab. If you encounter a barrier or have suggestions for improvement:

### How to Provide Feedback

1. **GitHub Issues** — Open an issue with the `accessibility` label
2. **Email** — Send feedback to accessibility@authshieldlab.dev
3. **GitHub Discussions** — Start a discussion in the Accessibility category
4. **Direct Contribution** — Submit a pull request with the fix

### What to Include

- Description of the accessibility barrier
- The page or component where you encountered it
- The assistive technology and browser you were using
- Suggested improvement (if any)

### Response Commitment

- All accessibility feedback is acknowledged within 48 hours
- Critical accessibility barriers are prioritized for immediate resolution
- Non-critical feedback is triaged and added to the roadmap
- We will follow up on issues you report with status updates

---

## Accessibility Roadmap

### Short-Term (Next Release — v5.1.0)

- [ ] Complete text alternatives for all data visualizations
- [ ] Improve lab scenario builder keyboard support
- [ ] Add high contrast theme option
- [ ] Enhance screen reader announcements for lab progress

### Medium-Term (v5.2.0)

- [ ] Full WCAG 2.2 AA compliance audit by third party
- [ ] Keyboard-accessible scenario builder
- [ ] Improved mobile accessibility
- [ ] Accessibility documentation for contributors

### Long-Term (v6.0.0)

- [ ] WCAG 2.2 AAA compliance for critical user journeys
- [ ] Advanced voice control integration
- [ ] Real-time accessibility feedback in the lab environment
- [ ] Automated accessibility regression testing for all visual components

---

## Training and Awareness

- All contributors receive accessibility training as part of onboarding
- Accessibility is a standing item in sprint retrospectives
- Quarterly accessibility reviews are conducted
- The team tracks accessibility metrics and trends

---

## Accessibility Contact

| Contact | Channel |
|---------|---------|
| Accessibility Team | accessibility@authshieldlab.dev |
| GitHub Issues | [Accessibility Label](https://github.com/anya12forger12-max/authshield-lab/issues?q=label%3Aaccessibility) |
| GitHub Discussions | [Accessibility Category](https://github.com/anya12forger12-max/authshield-lab/discussions) |

---

## Legal Reference

This accessibility statement is provided in accordance with:
- [Section 508 of the Rehabilitation Act](https://www.section508.gov/)
- [EN 301 549](https://www.etsi.org/deliver/etsi_en/301500_301599/301549/03.02.01_60/en_301549v030201p.pdf)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)

---

*Last updated: July 2026*
