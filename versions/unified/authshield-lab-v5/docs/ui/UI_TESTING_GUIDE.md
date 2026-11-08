# AuthShield Lab — UI Testing Guide

> Comprehensive testing specification for the offline-first desktop cybersecurity education platform.

---

## 1. Overview

This guide defines the complete UI testing strategy for AuthShield Lab, covering usability, accessibility, visual regression, interaction, performance, cross-platform, and localization testing. All UI code must pass these testing gates before release.

---

## 2. Usability Testing

### 2.1 Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Task completion rate | >90% | User testing sessions |
| Time on task | Per benchmark | Screen recording analysis |
| Error rate | <5% | Analytics + user testing |
| User satisfaction (SUS) | >80 | System Usability Scale survey |
| First-time user success | >85% | Unmoderated testing |

### 2.2 Task Benchmarks

| Workflow | Expected Time | Max Acceptable Time |
|----------|---------------|---------------------|
| Complete a lesson | 15–30 min | 45 min |
| Run a lab exercise | 10–20 min | 30 min |
| Navigate to a specific lesson | <5 seconds | <10 seconds |
| Find a setting and change it | <10 seconds | <20 seconds |
| Search and open a resource | <8 seconds | <15 seconds |
| Complete keyboard-only workflow | <1.5× mouse time | <2× mouse time |

### 2.3 Usability Testing Protocol

1. **Recruit**: 5–8 representative users per testing round.
2. **Scenarios**: Write task-based scenarios (not feature-based).
3. **Observe**: Record screen + audio + face (with consent).
4. **Measure**: Track time, errors, help requests, frustration signals.
5. **Debrief**: Post-task questionnaire (SUS + custom questions).
6. **Iterate**: Fix issues, retest in next round.

---

## 3. Accessibility Testing

### 3.1 Automated Testing

| Tool | Integration Point | Target |
|------|-------------------|--------|
| axe-core | Playwright tests (every PR) | 0 violations |
| eslint-plugin-jsx-a11y | ESLint (every commit) | 0 warnings |
| Lighthouse | CI pipeline (every PR) | Score >95 |
| Pa11y | HTML report (weekly) | 0 violations |

### 3.2 Automated Test Configuration

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  use: {
    baseURL: 'http://localhost:3000',
  },
  projects: [
    { name: 'chromium' },
    { name: 'firefox' },
    { name: 'webkit' },
  ],
});
```

### 3.3 Axe-core Integration

```typescript
// tests/accessibility/a11y.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const pages = [
  { name: 'Home', url: '/' },
  { name: 'Lessons', url: '/lessons' },
  { name: 'Lab Workspace', url: '/labs/demo' },
  { name: 'Settings', url: '/settings' },
  { name: 'Progress', url: '/progress' },
];

for (const page of pages) {
  test(`${page.name} has no accessibility violations`, async ({ browserPage }) => {
    await browserPage.goto(page.url);
    const results = await new AxeBuilder({ browserPage })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze();
    expect(results.violations).toEqual([]);
  });
}
```

### 3.4 Screen Reader Testing Matrix

| Screen Reader | Browser | OS | Frequency |
|--------------|---------|-----|-----------|
| NVDA | Firefox | Windows 10/11 | Every sprint |
| NVDA | Chrome | Windows 10/11 | Monthly |
| VoiceOver | Safari | macOS latest | Every sprint |
| JAWS | Chrome | Windows 10/11 | Monthly |

### 3.5 Screen Reader Test Scenarios

| Scenario | Expected Announcement |
|----------|----------------------|
| Page load | Page title, landmark regions, skip link |
| Navigate to sidebar | "Main navigation, list, 7 items" |
| Focus on lesson item | "Lesson 1: Introduction to SSH, link" |
| Open dialog | "Confirm dialog, title, description, Cancel button, Confirm button" |
| Form validation error | "Error: Please enter a valid email, alert" |
| Tab switch | "Tab panel, Lesson Content" |
| Progress update | "Progress: 3 of 5 lessons completed, status" |

### 3.6 Keyboard-Only Testing

All workflows must be completable using **only** a keyboard:

| Workflow | Required Keys | Acceptable Time |
|----------|---------------|-----------------|
| Navigate to Lessons section | Alt+2 | <2 seconds |
| Open a lesson | Tab to lesson, Enter | <5 seconds |
| Complete lesson exercise | Tab, Enter, Arrow keys, typing | Per task |
| Run a lab | Tab, Enter, typing | Per task |
| Change a setting | Ctrl+,, Tab, Arrow keys, Enter | <15 seconds |
| Search for a lesson | Ctrl+K, type, Arrow keys, Enter | <8 seconds |
| Close a dialog | Escape | <1 second |
| Switch between panels | Ctrl+B, Ctrl+J, Ctrl+Shift+I | <2 seconds |
| Open command palette | Ctrl+K, type, Enter | <5 seconds |

### 3.7 High Contrast Mode Testing

| Test | Expected Result |
|------|----------------|
| All borders visible | Every bordered element uses `CanvasText` color |
| Focus ring visible | 3px solid `Highlight` color |
| All icons visible | Icons use `CanvasText` color |
| Text readable | All text meets contrast on `Canvas` background |
| No background images | Decorative images hidden; solid colors used |
| Custom scrollbars | Scrollbar uses system high contrast colors |

### 3.8 Zoom Testing

| Zoom Level | Expected Result |
|-----------|----------------|
| 100% | Default layout, all elements visible |
| 125% | Slight increase, no layout breakage |
| 150% | Content reflows, no horizontal scroll |
| 200% | Full zoom, single column, no content loss |
| 400% | Maximum zoom, reflow to 320px equivalent |

At **200% zoom**:
- No horizontal scrolling on any page
- All text readable
- All interactive elements clickable/focusable
- No overlapping content
- All images scale proportionally

---

## 4. Visual Regression Testing

### 4.1 Screenshot Comparison

| Screen | Viewport | Theme | Frequency |
|--------|----------|-------|-----------|
| Home Dashboard | 1920×1080 | Light | Every PR |
| Home Dashboard | 1920×1080 | Dark | Every PR |
| Lesson Library | 1920×1080 | Light | Every PR |
| Lab Workspace | 1920×1080 | Light | Every PR |
| Settings | 1920×1080 | Light | Every PR |
| All screens | 1024×768 | Light | Weekly |
| All screens | 2560×1440 | Light | Weekly |
| Command Palette | 1920×1080 | Light | Every PR |
| Dialog: Confirm Delete | 1920×1080 | Light | Every PR |

### 4.2 Component Storybook Snapshots

Every UI component must have a Storybook story with visual snapshot:

| Component | Stories Required |
|-----------|-----------------|
| Button | Default, Hover, Focus, Disabled, Loading, Icon, Full-width |
| Input | Default, With Label, With Error, With Help Text, Disabled, RTL |
| Dialog | Default, With Form, Alert Dialog, Full-screen |
| Navigation Rail | Expanded, Collapsed, With Badge, RTL |
| Sidebar | Expanded, Collapsed, With Tree, Loading |
| Tab Bar | 1 Tab, Multiple Tabs, With Close, Overflow |
| Data Grid | Empty, 1 Row, 100 Rows, Sorted, Filtered, Selectable |
| Toast | Success, Error, Warning, Info, With Action |
| Tooltip | Top, Bottom, Left, Right, With Shortcut |
| Progress Bar | 0%, 50%, 100%, Indeterminate |

### 4.3 Responsive Breakpoint Screenshots

```typescript
// Visual regression test for breakpoints
const breakpoints = [
  { name: 'lg', width: 1024, height: 768 },
  { name: 'xl', width: 1280, height: 720 },
  { name: '2xl', width: 1366, height: 768 },
  { name: '3xl', width: 1920, height: 1080 },
  { name: '4xl', width: 2560, height: 1440 },
];

for (const bp of breakpoints) {
  test(`Home page at ${bp.name} (${bp.width}×${bp.height})`, async ({ page }) => {
    await page.setViewportSize({ width: bp.width, height: bp.height });
    await page.goto('/');
    await expect(page).toHaveScreenshot(`home-${bp.name}.png`);
  });
}
```

### 4.4 Theme Comparison

| Theme | Background | Text | Accent | Border |
|-------|-----------|------|--------|--------|
| Light | `#ffffff` | `#111827` | `#3b82f6` | `#e5e7eb` |
| Dark | `#111827` | `#f9fafb` | `#60a5fa` | `#374151` |
| High Contrast Light | `#ffffff` | `#000000` | `#0000ff` | `#000000` |
| High Contrast Dark | `#000000` | `#ffffff` | `#00ffff` | `#ffffff` |

---

## 5. Interaction Testing

### 5.1 Click/Tap Interactions

| Element | Test Cases |
|---------|-----------|
| Button | Click activates, disabled state prevents click, loading state prevents double-click |
| Link | Click navigates, Ctrl+Click opens in new tab (external links) |
| Checkbox | Click toggles, click on label toggles associated checkbox |
| Radio | Click selects, click on different radio deselects previous |
| Dropdown | Click opens, click option selects and closes, click outside closes |
| Icon button | Click activates, tooltip shows on hover |
| Tree node | Click expands/collapses, click selects |
| Tab | Click switches, click on active tab does nothing |

### 5.2 Keyboard Interactions

| Element | Key | Expected Behavior |
|---------|-----|-------------------|
| Button | Enter | Activates |
| Button | Space | Activates |
| Link | Enter | Follows link |
| Input | Typing | Enters text |
| Input | Backspace | Deletes character |
| Select | Arrow Down | Opens dropdown |
| Select | Arrow Up/Down | Navigates options |
| Modal | Escape | Closes modal |
| Tree | Arrow Right | Expands node |
| Tree | Arrow Left | Collapses node |
| Grid | Arrow keys | Moves between cells |
| Grid | Space | Selects/deselects row |
| Grid | Enter | Activates cell |

### 5.3 Drag and Drop

| Scenario | Test Case |
|----------|-----------|
| File reorder | Drag lesson to new position, verify order persists |
| Panel resize | Drag panel border, verify new size persists |
| Tab reorder | Drag tab to new position, verify order persists |
| Tree node move | Drag node to new parent, verify hierarchy updates |

### 5.4 Form Validation

| Input Type | Validation Rules | Error Display |
|-----------|-----------------|---------------|
| Email | Required, valid format | Inline below field, red border |
| Password | Required, min 8 chars | Inline below field, red border |
| Username | Required, alphanumeric, 3–32 chars | Inline below field, red border |
| Number | Required, within min/max range | Inline below field, red border |
| URL | Required, valid URL format | Inline below field, red border |
| File upload | Required, valid type, max size | Inline below field, red border |

### 5.5 Dialog Behavior

| Test | Expected |
|------|----------|
| Open modal | Focus moves to first focusable element in dialog |
| Close modal (Esc) | Dialog closes, focus returns to trigger |
| Close modal (X button) | Dialog closes, focus returns to trigger |
| Close modal (backdrop click) | Dialog closes, focus returns to trigger |
| Tab in modal | Focus cycles within dialog |
| Confirm action | Action executes, dialog closes |
| Cancel action | Action cancelled, dialog closes |

### 5.6 Notification Display

| Type | Display | Duration | Dismissible |
|------|---------|----------|-------------|
| Success | Green banner + checkmark icon | 3 seconds | Yes |
| Error | Red banner + error icon | Until dismissed | Yes |
| Warning | Yellow banner + warning icon | 5 seconds | Yes |
| Info | Blue banner + info icon | 3 seconds | Yes |
| Progress | Blue bar with percentage | Until complete | No |

---

## 6. Performance Testing

### 6.1 Key Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint (FCP) | <1.0s | Lighthouse |
| Largest Contentful Paint (LCP) | <1.5s | Lighthouse |
| Time to Interactive (TTI) | <2.0s | Lighthouse |
| First Input Delay (FID) | <50ms | Custom measurement |
| Cumulative Layout Shift (CLS) | <0.1 | Lighthouse |
| Bundle size (main) | <500KB gzipped | webpack-bundle-analyzer |
| Total bundle size | <2MB gzipped | webpack-bundle-analyzer |
| Memory usage (idle) | <150MB | Electron memory profiler |
| Memory usage (active) | <300MB | Electron memory profiler |

### 6.2 Performance Test Scenarios

| Scenario | Expected | Measurement |
|----------|----------|-------------|
| Cold start | <2s to interactive | Electron startup time |
| Hot start | <1s to interactive | Electron startup time |
| Lesson load | <500ms | Time from click to content visible |
| Lab initialization | <2s | Time from click to lab ready |
| Search results | <200ms | Time from keystroke to results |
| Theme switch | <100ms | Time from toggle to visual change |
| Panel resize | 60fps | Frame rate during resize animation |
| Scroll performance | 60fps | Frame rate during scroll |
| Large lesson render | <1s | Render time for 1000+ line lesson |

### 6.3 Memory Leak Detection

```typescript
// Memory leak test
test('no memory leaks during lesson navigation', async ({ page }) => {
  const initialMemory = await page.evaluate(() => {
    return (performance as any).memory.usedJSHeapSize;
  });

  // Navigate through 20 lessons
  for (let i = 0; i < 20; i++) {
    await page.click(`[data-lesson="${i}"]`);
    await page.waitForSelector('[data-content-loaded]');
  }

  const finalMemory = await page.evaluate(() => {
    return (performance as any).memory.usedJSHeapSize;
  });

  const memoryIncrease = finalMemory - initialMemory;
  expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024); // <50MB increase
});
```

### 6.4 Bundle Size Monitoring

```typescript
// CI check: fail if bundle exceeds threshold
const BUNDLE_THRESHOLDS = {
  'main.js': 300 * 1024,      // 300KB
  'vendor.js': 200 * 1024,    // 200KB
  'total.js': 500 * 1024,     // 500KB
  'total.css': 50 * 1024,     // 50KB
};
```

---

## 7. Cross-Platform Testing

### 7.1 Platform Matrix

| Platform | Versions | Priority |
|----------|----------|----------|
| Windows | 10 (21H2+), 11 | High |
| macOS | Ventura (13), Sonoma (14), Sequoia (15) | High |
| Linux | Ubuntu 22.04+, Fedora 38+, Debian 12+ | Medium |

### 7.2 Electron Version Compatibility

| Electron | Chromium | Node.js | Status |
|----------|----------|---------|--------|
| 28.x | 120 | 18.18 | Supported |
| 29.x | 122 | 20.11 | Supported |
| 30.x | 124 | 20.14 | Target |

### 7.3 Platform-Specific Tests

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Window chrome | Title bar overlay | Traffic lights | Custom title bar |
| System tray | Full support | Limited | Full support |
| Notifications | Windows Toast | macOS Notification Center | libnotify |
| File paths | Backslash | Forward slash | Forward slash |
| Menu bar | Window menu | Application menu | Window menu |
| Keyboard shortcuts | Ctrl-based | Cmd-based | Ctrl-based |
| DPI scaling | 100–200% | Retina | 100–200% |
| Auto-update | Electron Updater | Electron Updater | Electron Updater |

### 7.4 Cross-Platform Test Checklist

```
□ Application launches successfully
□ Window can be resized to minimum (1024×768)
□ Window can be maximized and restored
□ All keyboard shortcuts work
□ File dialogs open correctly
□ Notifications display correctly
□ System tray icon works (if applicable)
□ Menu bar works correctly
□ DPI scaling renders correctly
□ High contrast mode works
□ Reduced motion preference respected
□ Application quits cleanly
□ State persists across restarts
□ Updates can be checked
```

---

## 8. Localization Testing

### 8.1 Pseudo-Localization Testing

Enable pseudo-localization in development to catch:

- **Hardcoded strings**: Non-translated text appears in brackets `[!!!]`.
- **Text expansion**: Strings expanded to 200% to test container overflow.
- **Concatenation bugs**: Strings with variables show ordering issues.
- **Missing RTL support**: Layout breaks when pseudo-locale forces RTL.

```typescript
// Enable pseudo-locale
process.env.PSEUDO_LOCALE = 'en-X-pseudo';
```

### 8.2 RTL Layout Verification

| Check | Method | Expected |
|-------|--------|----------|
| Sidebar position | Visual inspection | Right side of screen |
| Nav rail position | Visual inspection | Right side of screen |
| Text alignment | Visual inspection | Right-aligned |
| Breadcrumbs | Visual inspection | Right-to-left order |
| Back/forward arrows | Visual inspection | Flipped direction |
| Progress bars | Visual inspection | Fill right-to-left |
| Form labels | Visual inspection | Right of input fields |
| Scrollbar | Visual inspection | Left side of content |
| Dialog position | Visual inspection | Centered correctly |

### 8.3 Date/Number Formatting

| Locale | Date Format | Number Format | Currency |
|--------|------------|---------------|----------|
| en-US | 7/19/2026 | 1,234,567.89 | $49.99 |
| de-DE | 19.7.2026 | 1.234.567,89 | 49,99 € |
| ja-JP | 2026/7/19 | 1,234,567.89 | ￥50 |
| ar-SA | ١٩‏/٧‏/٢٠٢٦ | ١٬٢٣٤٬٥٦٧٫٨٩ | ٤٩٫٩٩ ر.س. |
| ru-RU | 19.07.2026 | 1 234 567,89 | 49,99 ₽ |

### 8.4 Truncation Handling

| Language | "Settings" Translation | Container Test |
|----------|----------------------|----------------|
| English | Settings | Fits in standard container |
| German | Einstellungen | Fits with 200% expansion allowance |
| Japanese | 設定 | Fits (shorter) |
| Arabic | الإعدادات | Fits with RTL mirroring |

---

## 9. Testing Tools

### 9.1 Tool Stack

| Tool | Purpose | Integration |
|------|---------|-------------|
| Playwright | E2E testing, visual regression | CI pipeline |
| axe-core | Accessibility automated testing | Playwright + CI |
| React Testing Library | Component unit tests | Jest + CI |
| Storybook | Component development + snapshots | Chromatic |
| Chromatic | Visual regression hosting | CI + PR reviews |
| Lighthouse | Performance + accessibility audit | CI pipeline |
| webpack-bundle-analyzer | Bundle size analysis | Build step |
| Playwright a11y | Accessibility E2E tests | CI pipeline |

### 9.2 Playwright Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['junit', { outputFile: 'test-results.xml' }],
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'desktop-chrome',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'desktop-firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'desktop-webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### 9.3 React Testing Library

```typescript
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with label', () => {
    render(<Button>Save</Button>);
    expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Save</Button>);
    fireEvent.click(screen.getByRole('button', { name: 'Save' }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} disabled>Save</Button>);
    fireEvent.click(screen.getByRole('button', { name: 'Save' }));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('has accessible name', () => {
    render(<Button aria-label="Save document">💾</Button>);
    expect(screen.getByRole('button', { name: 'Save document' })).toBeInTheDocument();
  });
});
```

### 9.4 Storybook Configuration

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'ghost', 'danger'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Default: Story = {
  args: { children: 'Button' },
};

export const Primary: Story = {
  args: { variant: 'primary', children: 'Save' },
};

export const Disabled: Story = {
  args: { disabled: true, children: 'Disabled' },
};

export const Loading: Story = {
  args: { loading: true, children: 'Saving...' },
};

export const WithIcon: Story = {
  args: { children: 'Delete', icon: 'trash', variant: 'danger' },
};
```

---

## 10. Test Reporting

### 10.1 CI Integration

| Gate | Tool | Threshold | Blocks Merge |
|------|------|-----------|-------------|
| Unit tests | Jest | 100% pass | Yes |
| E2E tests | Playwright | 100% pass | Yes |
| Accessibility (axe) | axe-core | 0 violations | Yes |
| Lighthouse | Lighthouse | Score >95 | Yes (warning) |
| Visual regression | Chromatic | 0 unexpected changes | Yes (review required) |
| Bundle size | webpack | Under threshold | Yes |
| Type checking | TypeScript | 0 errors | Yes |
| Linting | ESLint | 0 errors | Yes |

### 10.2 HTML Report

Playwright generates an HTML report:

```bash
npx playwright show-report
```

Report includes:
- Test results per spec file
- Screenshots on failure
- Trace viewer for debugging
- Accessibility violations with selectors

### 10.3 Accessibility Violation Tracking

```typescript
// Track accessibility violations over time
interface A11yViolation {
  rule: string;
  impact: 'minor' | 'moderate' | 'serious' | 'critical';
  nodes: number;
  url: string;
  timestamp: string;
}

// Store violations in JSON for trend analysis
const results = await new AxeBuilder({ page })
  .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
  .analyze();

const violations: A11yViolation[] = results.violations.map(v => ({
  rule: v.id,
  impact: v.impact,
  nodes: v.nodes.length,
  url: page.url(),
  timestamp: new Date().toISOString(),
}));

// Compare with baseline
const baseline = JSON.parse(fs.readFileSync('a11y-baseline.json', 'utf-8'));
const newViolations = violations.filter(v =>
  !baseline.some(b => b.rule === v.rule && b.impact === v.impact)
);

if (newViolations.length > 0) {
  console.error('New accessibility violations detected:', newViolations);
  process.exit(1);
}
```

### 10.4 Weekly Report

```markdown
## UI Testing Report — Week of 2026-07-14

### Summary
- Unit tests: 247/247 passing (100%)
- E2E tests: 89/89 passing (100%)
- Accessibility: 0 violations (axe-core)
- Lighthouse: 97/100 accessibility score
- Visual regression: 0 unexpected changes
- Bundle size: 423KB gzipped (under 500KB threshold)

### Platforms Tested
- Windows 11: ✅ All tests passing
- macOS Sonoma: ✅ All tests passing
- Ubuntu 22.04: ✅ All tests passing

### Screen Reader Testing
- NVDA + Firefox: ✅ All scenarios passing
- VoiceOver + Safari: ✅ All scenarios passing

### Issues Found
- None

### Action Items
- Continue monitoring bundle size as new features are added
- Schedule JAWS testing for next sprint
```

---

*Document version: 1.0.0 — Last updated: 2026-07-19*
