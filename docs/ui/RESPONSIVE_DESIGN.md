# AuthShield Lab — Responsive Design Guide

> Enterprise-grade responsive design specification for the offline-first desktop cybersecurity education platform.

---

## 1. Overview

AuthShield Lab runs as an Electron desktop application on Windows, Linux, and macOS. The minimum supported window size is **1024×768**. The UI must gracefully adapt across a wide range of resolutions—from compact laptop screens to 4K displays and ultra-wide monitors—while preserving full functionality and accessibility at every size.

This guide defines breakpoints, layout behavior, panel docking, typography scaling, spacing adaptation, grid system, and multi-monitor handling.

---

## 2. Breakpoints

| Token   | Min Width | Typical Use Case                     |
|---------|-----------|--------------------------------------|
| `sm`    | 640 px    | Not used (below minimum window)      |
| `md`    | 768 px    | Not used (below minimum window)      |
| `lg`    | 1024 px   | Minimum supported window             |
| `xl`    | 1280 px   | Small desktop / 720p external        |
| `2xl`   | 1536 px   | Standard laptop / 1080p              |
| `3xl`   | 1920 px   | Comfortable desktop / 1080p+         |
| `4xl`   | 2560 px   | Large monitor / QHD                  |
| `5xl`   | 3840 px   | 4K / Ultra-wide                      |

TailwindCSS configuration should map these tokens to the custom sizes below.

---

## 3. Layout Per Breakpoint

### 3.1 Minimum — 1024×768 (`lg`)

```
┌─────────────────────────────────────────────────┐
│  Compact Toolbar (48px)                        │
├────┬────────────────────────────────────────────┤
│ N  │                                            │
│ A  │                                            │
│ V  │           Full Workspace                   │
│    │                                            │
│ I  │                                            │
│ C  │                                            │
│ O  │                                            │
│ N  │                                            │
│ S  │                                            │
├────┴────────────────────────────────────────────┤
│  Status Bar                                    │
└─────────────────────────────────────────────────┘
```

- **Nav Rail**: Collapsed to **icons only** (48px wide). Labels hidden.
- **Sidebar**: Completely hidden. Toggle via Ctrl+B to reveal as overlay.
- **Toolbar**: Compact variant (48px height). Overflow menu for secondary actions.
- **Workspace**: Full remaining width. Single-column layout.
- **Right Panel**: Hidden.
- **Bottom Panel**: Hidden. Toggle via keyboard shortcut.

### 3.2 Small — 1280×720 (`xl`)

```
┌───────────────────────────────────────────────────────┐
│  Standard Toolbar (56px)                             │
├────┬────────────┬─────────────────────────────────────┤
│ N  │            │                                     │
│ A  │  Sidebar   │                                     │
│ V  │  200px     │        Full Workspace               │
│    │  (narrow)  │                                     │
│ I  │            │                                     │
│ C  │            │                                     │
│ O  │            │                                     │
│ N  │            │                                     │
│ S  │            │                                     │
├────┴────────────┴─────────────────────────────────────┤
│  Status Bar                                           │
└───────────────────────────────────────────────────────┘
```

- **Nav Rail**: Collapsed, icons only (48px).
- **Sidebar**: Narrow variant (200px), collapsible.
- **Toolbar**: Standard height (56px).
- **Workspace**: Fills remaining space. Two-column layout optional.
- **Right Panel**: Hidden.
- **Bottom Panel**: Hidden by default.

### 3.3 Standard — 1366×768 (`2xl`)

```
┌────────────────────────────────────────────────────────────┐
│  Standard Toolbar (56px)                                  │
├──────┬──────────────┬──────────────────────────────────────┤
│  N   │              │                                      │
│  A   │              │                                      │
│  V   │   Sidebar    │         Full Workspace               │
│      │   240px      │                                      │
│  R   │  (standard)  │                                      │
│  A   │              │                                      │
│  I   │              │                                      │
│  L   │              │                                      │
│ 64px │              │                                      │
├──────┴──────────────┴──────────────────────────────────────┤
│  Status Bar                                                │
└────────────────────────────────────────────────────────────┘
```

- **Nav Rail**: Full variant with labels (64px).
- **Sidebar**: Standard width (240px), resizable 200–360px.
- **Toolbar**: Standard height (56px).
- **Workspace**: Primary working area with optional two-column layout.
- **Right Panel**: Available but hidden by default. Appears as inspector/details.
- **Bottom Panel**: Available. Toggle for terminal, console, output.

### 3.4 Comfortable — 1920×1080 (`3xl`)

```
┌──────────────────────────────────────────────────────────────────────┐
│  Spacious Toolbar (56px)                                           │
├──────┬──────────────┬─────────────────────────────┬──────────────────┤
│  N   │              │                             │                  │
│  A   │              │                             │                  │
│  V   │   Sidebar    │      Spacious Workspace     │  Right Panel     │
│      │   240px      │                             │  300px           │
│  R   │              │                             │  (optional)      │
│  A   │              │                             │                  │
│  I   │              │                             │                  │
│  L   │              │                             │                  │
│ 64px │              │                             │                  │
├──────┴──────────────┴─────────────────────────────┴──────────────────┤
│  Status Bar                                                         │
└──────────────────────────────────────────────────────────────────────┘
```

- **Nav Rail**: Full variant (64px).
- **Sidebar**: Standard width (240px), resizable.
- **Toolbar**: Standard (56px) with extra spacing between groups.
- **Workspace**: Comfortable multi-column layout with breathing room.
- **Right Panel**: Inspector/details panel (300px), auto-docked.
- **Bottom Panel**: Available and easily toggled.

### 3.5 Large — 2560×1440 (`4xl`)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Spacious Toolbar (56px)                                                   │
├──────┬─────────────────┬──────────────────────────────────┬──────────────────┤
│  N   │                 │                                  │                  │
│  A   │                 │                                  │                  │
│  V   │   Sidebar       │       Spacious Workspace         │  Right Panel     │
│      │   300px         │                                  │  360px           │
│  R   │  (wide)         │                                  │                  │
│  A   │                 │                                  │                  │
│  I   │                 │                                  │                  │
│  L   │                 │                                  │                  │
│ 64px │                 │                                  │                  │
├──────┴─────────────────┴──────────────────────────────────┴──────────────────┤
│  Status Bar                                                                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Nav Rail**: Full (64px).
- **Sidebar**: Wide variant (300px), resizable up to 400px.
- **Toolbar**: Standard with generous spacing.
- **Workspace**: Multi-column with generous margins.
- **Right Panel**: Visible by default (360px).
- **Bottom Panel**: Available with comfortable height.

### 3.6 4K / Ultra-wide — 3840×2160+ (`5xl`)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                     Spacious Toolbar (56px)                                            │
├──────┬─────────────────┬──────────────────────────────────────────┬──────────────────────┤
│  N   │                 │                                          │                      │
│  A   │                 │              ┌──────────────────┐        │                      │
│  V   │   Sidebar       │              │                  │        │   Right Panel         │
│      │   300px         │              │  Max-width       │        │   360px              │
│  R   │                 │              │  Container       │        │                      │
│  A   │                 │              │  1440px centered │        │                      │
│  I   │                 │              │                  │        │                      │
│  L   │                 │              └──────────────────┘        │                      │
│ 64px │                 │                                          │                      │
├──────┴─────────────────┴──────────────────────────────────────────┴──────────────────────┤
│  Status Bar                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Nav Rail**: Full (64px).
- **Sidebar**: Wide (300px).
- **Toolbar**: Standard (56px).
- **Workspace**: Content capped at **1440px max-width**, centered. No stretched content.
- **Right Panel**: Visible (360px).
- **Extra space**: Used for padding or reserved for future features.

---

## 4. Window Resizing Behavior

### 4.1 Resize Rules

| Action                    | Behavior                                                                 |
|---------------------------|--------------------------------------------------------------------------|
| Window shrinks below 1280 | Sidebar auto-collapses to overlay mode                                  |
| Window shrinks below 1024 | Nav rail collapses to icons only; sidebar hides entirely                |
| Window grows above 1280   | Sidebar reappears if it was auto-hidden                                  |
| Window grows above 1366   | Nav rail shows labels                                                    |
| Window grows above 1920   | Right panel becomes available (auto-shows if previously docked)          |
| Drag to breakpoint        | Panels animate smoothly; 200ms transition                                |
| Resize while panels open  | Panels reflow proportionally; workspace adjusts last                    |

### 4.2 Panel Collapse Order

When the window shrinks, panels collapse in this order:

1. **Right panel** — collapses first, content merges into workspace
2. **Bottom panel** — collapses second
3. **Sidebar** — collapses to overlay (floating, not docked)
4. **Nav rail labels** — hidden, icons only
5. **Toolbar** — switches to compact variant (last resort)

When the window grows, panels restore in reverse order.

### 4.3 Minimum Content Widths

| Component        | Minimum Width |
|------------------|---------------|
| Nav Rail         | 48px (icons)  |
| Sidebar          | 0px (hidden)  |
| Workspace        | 400px         |
| Right Panel      | 240px         |
| Bottom Panel     | 100% width    |
| Dialog           | 320px         |
| Dialog (max)     | 640px         |

---

## 5. Panel Docking System

### 5.1 Dock Positions

```
┌────────────────────────────────────────────────┐
│  Left Sidebar  │         │  Right Panel        │
│  (240px)       │Workspace│  (Inspector)        │
│  Resizable:    │         │  (300px)            │
│  200–400px     │         │  Resizable:         │
│                │         │  240–480px          │
├────────────────┴─────────┴─────────────────────┤
│  Bottom Panel (Terminal/Console/Output)         │
│  Resizable: 100–400px height                   │
└────────────────────────────────────────────────┘
```

### 5.2 Panel Behavior

- **Left Sidebar**: Primary navigation, file tree, lesson list. Docked left, resizable.
- **Right Panel**: Inspector, properties, details. Docked right, resizable.
- **Bottom Panel**: Terminal, console, output logs. Docked bottom, resizable.
- **Floating Panels**: Detached panels become native Electron windows. Remember position.
- **Panel Stacking**: Multiple panels can share a dock zone via tabs.

### 5.3 Panel State Persistence

Panel widths, heights, dock positions, and open/closed state are persisted in `localStorage` and restored on application restart. Per-monitor positions are stored separately (see §8).

---

## 6. Typography Scaling

### 6.1 Base Configuration

| Property        | Value                                  |
|-----------------|----------------------------------------|
| Base font size  | 14px (1rem = 14px)                     |
| Font family     | System font stack (Segoe UI, SF Pro, etc.) |
| Line height     | 1.5 (1.625 for body text)              |
| Scale factor    | Follows system `text-scale-factor`     |

### 6.2 Type Scale

| Level    | rem    | px (@14px) | Usage                   |
|----------|--------|------------|--------------------------|
| `xs`     | 0.75   | 10.5       | Captions, metadata       |
| `sm`     | 0.875  | 12.25      | Secondary text           |
| `base`   | 1.0    | 14         | Body text, UI labels     |
| `lg`     | 1.125  | 15.75      | Emphasized body          |
| `xl`     | 1.25   | 17.5       | Section headings         |
| `2xl`    | 1.5    | 21         | Page headings            |
| `3xl`    | 1.875  | 26.25      | Hero text                |
| `4xl`    | 2.25   | 31.5       | Display headings         |

### 6.3 System Scale Integration

```css
:root {
  font-size: calc(14px * var(--system-text-scale, 1));
}
```

The application reads the OS text scale setting and applies it as a CSS custom property. All sizes use `rem`, so the entire UI scales proportionally.

### 6.4 Zoom Support

- The application supports up to **200% zoom** without horizontal scrolling.
- Zoom is implemented via CSS `transform: scale()` or `zoom` property.
- Zoom state persists across sessions.

---

## 7. Spacing Adaptation

### 7.1 Spacing Scale

| Token     | Small (<1280) | Medium (1280–1920) | Large (>1920) |
|-----------|---------------|---------------------|----------------|
| `gap-xs`  | 2px           | 4px                 | 4px            |
| `gap-sm`  | 4px           | 8px                 | 8px            |
| `gap-md`  | 8px           | 12px                | 16px           |
| `gap-lg`  | 12px          | 16px                | 24px           |
| `gap-xl`  | 16px          | 24px                | 32px           |
| `gap-2xl` | 24px          | 32px                | 48px           |
| `pad-sm`  | 8px           | 12px                | 16px           |
| `pad-md`  | 12px          | 16px                | 24px           |
| `pad-lg`  | 16px          | 24px                | 32px           |

### 7.2 Content Density Modes

| Mode     | When Used           | Description                                       |
|----------|----------------------|---------------------------------------------------|
| Compact  | <1280px width        | Tighter spacing, smaller touch targets, denser UI |
| Standard | 1280–1920px width    | Default spacing, balanced density                 |
| Spacious | >1920px width        | Generous spacing, larger targets, breathing room  |

---

## 8. Grid System

### 8.1 Grid Specification

| Property       | Value                                    |
|----------------|------------------------------------------|
| Columns        | 12                                       |
| Gutter         | 16px (standard), 12px (compact)          |
| Margin         | 16px (compact), 24px (standard), 32px (spacious) |
| Max width      | 1440px                                   |
| Column width   | Flexible (fluid grid)                    |

### 8.2 Grid Usage

```
|  col  |  col  |  col  |  col  |  col  |  col  |  col  |  col  |  col  |  col  |  col  |  col  |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| 8.33% | 8.33% | 8.33% | 8.33% | 8.33% | 8.33% | 8.33% | 8.33% | 8.33% | 8.33% | 8.33% | 8.33% |
```

- **12-column**: Divisible by 1, 2, 3, 4, 6, 12. Supports all common layouts.
- **Responsive columns**: Below 1024px, switch to 4-column grid. Below 768px (not supported), use single column.
- **Content areas**: Workspace uses full grid. Sidebar and panels occupy fixed track widths.

### 8.3 Content Max-Width

```css
.content-container {
  max-width: 1440px;
  margin-inline: auto;
  padding-inline: var(--content-padding);
}
```

On ultra-wide displays, content never stretches beyond 1440px. Extra space becomes padding.

---

## 9. Multi-Monitor Support

### 9.1 Window Position Persistence

- Window position (x, y, width, height) is saved on close.
- Position is stored per monitor configuration (by monitor EDID or resolution fingerprint).
- On launch, the app restores position if the monitor configuration matches; otherwise, centers on primary monitor.

### 9.2 Monitor Configuration Detection

```typescript
interface MonitorConfig {
  primary: { width: number; height: number; x: number; y: number };
  monitors: Array<{
    width: number;
    height: number;
    x: number;
    y: number;
    scaleFactor: number;
  }>;
}
```

### 9.3 Detached Panels

- Right panel and bottom panel can be **detached** into separate native windows.
- Detached panels remember their position per monitor.
- Detached panels support their own zoom level.
- Communication between main window and detached panels uses Electron IPC.

### 9.4 DPI / Scaling

| DPI Setting | Behavior                                    |
|-------------|---------------------------------------------|
| 100% (96dpi) | Native rendering                           |
| 125% (120dpi) | Electron `--force-device-scale-factor=1.25` |
| 150% (144dpi) | Scaled rendering, larger UI                |
| 200% (192dpi) | HiDPI, assets use @2x variants             |

The application uses Electron's `devicePixelRatio` awareness and loads appropriate asset scales.

---

## 10. Transition and Animation

### 10.1 Panel Resize Transitions

| Property          | Value                                      |
|-------------------|--------------------------------------------|
| Duration          | 200ms                                      |
| Easing            | `cubic-bezier(0.4, 0, 0.2, 1)`            |
| Trigger           | Window resize crossing a breakpoint        |
| Reduced motion    | Duration set to 0ms when `prefers-reduced-motion: reduce` |

### 10.2 Panel Show/Hide

| Property          | Value                                      |
|-------------------|--------------------------------------------|
| Sidebar show      | Slide in from left, 200ms                  |
| Sidebar hide      | Slide out to left, 150ms                   |
| Right panel show  | Slide in from right, 200ms                 |
| Right panel hide  | Slide out to right, 150ms                  |
| Bottom panel show | Slide up from bottom, 200ms                |
| Bottom panel hide | Slide down, 150ms                          |

### 10.3 Responsive Transitions

When the window crosses a breakpoint:
1. Panels animate to their new state over 200ms.
2. Content reflows immediately (no animation delay).
3. Layout changes (column count, grid width) happen instantly.
4. Only panel dimensions and visibility animate.

---

## 11. Platform-Specific Considerations

### 11.1 Windows

- Title bar height: 31px (standard), 48px (extended).
- Window chrome integrated via `titleBarOverlay`.
- Snap layouts respected (quarter screen = minimum viable).

### 11.2 macOS

- Title bar integrated (traffic lights embedded).
- Toolbar area accounts for traffic light inset (70px left padding).
- Full-screen mode: panels reflow to use full screen.

### 11.3 Linux

- GTK/Qt title bar varies by desktop environment.
- Use `frame: false` with custom title bar for consistency.
- Window decorations handled via Electron `BrowserWindow` options.

---

## 12. Responsive Design Testing Matrix

| Resolution     | Platform     | Panels Open        | Expected Layout        |
|----------------|--------------|--------------------|------------------------|
| 1024×768       | All          | Nav only           | Icons only, no sidebar |
| 1280×720       | All          | Nav + sidebar      | Narrow sidebar         |
| 1366×768       | All          | Nav + sidebar      | Standard sidebar       |
| 1920×1080      | All          | Nav + sidebar + RP | Full layout            |
| 2560×1440      | All          | Nav + sidebar + RP | Wide sidebar           |
| 3840×2160      | All          | All panels         | Max-width containers   |

---

## 13. Implementation Notes

### 13.1 TailwindCSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
      '3xl': '1920px',
      '4xl': '2560px',
      '5xl': '3840px',
    },
    extend: {
      spacing: {
        'nav-rail': '64px',
        'nav-rail-collapsed': '48px',
        'sidebar': '240px',
        'sidebar-narrow': '200px',
        'sidebar-wide': '300px',
        'right-panel': '300px',
        'right-panel-wide': '360px',
        'toolbar': '56px',
        'toolbar-compact': '48px',
        'status-bar': '24px',
      },
    },
  },
};
```

### 13.2 Zustand Store: Layout State

```typescript
interface LayoutState {
  navRailCollapsed: boolean;
  sidebarWidth: number;
  sidebarVisible: boolean;
  rightPanelWidth: number;
  rightPanelVisible: boolean;
  bottomPanelHeight: number;
  bottomPanelVisible: boolean;
  contentDensity: 'compact' | 'standard' | 'spacious';
}
```

### 13.3 CSS Custom Properties

```css
:root {
  --nav-rail-width: 64px;
  --sidebar-width: 240px;
  --right-panel-width: 300px;
  --bottom-panel-height: 200px;
  --toolbar-height: 56px;
  --status-bar-height: 24px;
  --content-padding: 16px;
  --gutter: 16px;
  --max-content-width: 1440px;
}

@media (max-width: 1279px) {
  :root {
    --nav-rail-width: 48px;
    --sidebar-width: 0px;
    --content-padding: 12px;
    --gutter: 12px;
  }
}
```

---

*Document version: 1.0.0 — Last updated: 2026-07-19*
