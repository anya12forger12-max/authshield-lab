# AuthShield Lab — Application Shell Specification

> Version: 1.0.0
> Last Updated: 2026-07-19
> Status: Active

---

## 1. Overview

The AuthShield Lab Application Shell is the master container for the entire desktop
application. It manages layout, window chrome, navigation, focus, and responsive
behaviour across Windows, Linux, and macOS. All content renders inside this shell.

**Tech Stack:** Electron + React + TypeScript + Zustand + TailwindCSS
**Minimum Window:** 1024 × 768
**Accessibility Target:** WCAG 2.2 AA
**Navigation:** Keyboard-first

---

## 2. Shell Layout — ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│ TITLE BAR (macOS traffic lights / Win·Linux min·max·close) 40px   │
├─────────────────────────────────────────────────────────────────────┤
│ APP HEADER  48px                                                   │
│ [Logo]    [Global Search ─────── Ctrl+K]   [Avatar][🔔][⚙]       │
├────┬──────────────────────────────────────────────────────────────┤
│NAV │ SIDEBAR (contextual)           │ WORKSPACE AREA              │
│RAIL│ 240px default                  │ flex-grow                   │
│64px│                                │                             │
│    │ ┌──────────────────────────┐   │ ┌───────────────────────┐   │
│ [🏠]│ │ Breadcrumb: Home > ...  │   │ │ Toolbar (40px)        │   │
│ [📚]│ ├──────────────────────────┤   │ │ [Action] [Action]     │   │
│ [🔬]│ │                          │   │ ├───────────────────────┤   │
│ [📝]│ │ Contextual content       │   │ │                       │   │
│ [📊]│ │ for current section      │   │ │   Main Content        │   │
│ [⚙]│ │                          │   │ │   (scrollable)        │   │
│ [❓]│ │                          │   │ │                       │   │
│    │ │                          │   │ │                       │   │
│    │ │                          │   │ │                       │   │
│    │ ├──────────────────────────┤   │ ├───────────────────────┤   │
│    │ │ Sidebar footer actions   │   │ │                       │   │
│    │ └──────────────────────────┘   │ └───────────────────────┘   │
├────┴────────────────────────────────┴─────────────────────────────┤
│ STATUS BAR  24px   [Online 🟢]  [User: student@lab]  [💾 Saved]  │
│                 [Storage: 1.2 GB / 10 GB]                         │
└─────────────────────────────────────────────────────────────────────┘

OVERLAYS (not visible at rest):
┌──────────────────────────┐  ┌─────────────────────────────────────┐
│ TOAST CONTAINER          │  │ COMMAND PALETTE (Ctrl+Shift+P)      │
│ top-right, z-index:9999  │  │ [Search actions...         ]        │
│ ┌──────────────────┐     │  │  > Dashboard                        │
│ │ ✅ Saved         │     │  │  > Settings > Theme                  │
│ └──────────────────┘     │  │  > Run Simulation                   │
│ ┌──────────────────┐     │  └─────────────────────────────────────┘
│ │ ⚠️ Warning       │     │
│ └──────────────────┘     │  ┌─────────────────────────────────────┐
└──────────────────────────┘  │ FAB (bottom-right)                  │
                              │  [+] → contextual quick actions     │
                              └─────────────────────────────────────┘
```

---

## 3. Window Chrome

### 3.1 Title Bar

| Property | macOS | Windows / Linux |
|----------|-------|-----------------|
| Height | 40px (native traffic lights) | 40px custom |
| Traffic Lights | Left-aligned, 12px inset | N/A |
| Minimize / Maximize / Close | N/A | Right-aligned buttons (40×40 each) |
| Drag region | Full title bar minus controls | Full title bar minus controls |
| Background | Follows theme (`--color-titlebar`) | Same |
| Double-click | Toggle maximize | Toggle maximize |

### 3.2 Electron BrowserWindow Config

```json
{
  "minWidth": 1024,
  "minHeight": 768,
  "width": 1366,
  "height": 768,
  "frame": false,
  "titleBarStyle": "hiddenInset",
  "backgroundColor": "#0F172A",
  "resizable": true,
  "webPreferences": {
    "contextIsolation": true,
    "nodeIntegration": false,
    "sandbox": true
  }
}
```

---

## 4. Application Header

**Height:** 48px | **Position:** Fixed top (below title bar) | **z-index:** 100

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo 160×28]    [🔍 Search (Ctrl+K)  ──────────]   [👤][🔔][⚙]│
│  16px padding     flex: 1, max-width 480px              16px   │
└─────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Position | Size | Notes |
|-----------|----------|------|-------|
| Logo | Left, 16px padding | 160 × 28px | `alt="AuthShield Lab"`, clickable → Dashboard |
| Global Search Trigger | Center | 320 × 36px | Opens overlay on click or `Ctrl+K` |
| User Avatar | Right, 24px from edge | 32 × 32px | Circular, initials fallback, click → profile menu |
| Notification Bell | Right of avatar | 40 × 40px click area | Badge count, click → notification panel |
| Settings Gear | Right of bell | 40 × 40px click area | Shortcut: `Ctrl+,` |

### Header Interactions

- **Avatar click** → dropdown: Profile, My Certificates, Preferences, Sign Out
- **Bell click** → slide-out panel: list of notifications, mark all read, clear
- **Gear click** → Settings dialog (modal)

---

## 5. Navigation Rail

**Width:** 64px (expanded) | 0px (collapsed) | **Position:** Fixed left
**Background:** `--color-nav-rail` | **z-index:** 90

```
┌────┐
│ 🏠 │  Dashboard          ← active state: left accent bar
│ 📚 │  Courses
│ 🔬 │  Simulations
│ 📝 │  Assessments        ← notification dot if pending
│ 📊 │  Reports
│ ⚙  │  Settings
│    │                     ← spacer pushes Help to bottom
│ ❓ │  Help
│    │
│ ◀  │  Collapse toggle    ← only visible on hover / focus
└────┘
```

### Navigation Items

| Icon | Label | Route | Tooltip |
|------|-------|-------|---------|
| 🏠 | Dashboard | `/dashboard` | Dashboard (Ctrl+D) |
| 📚 | Courses | `/courses` | Courses |
| 🔬 | Simulations | `/simulations` | Simulations |
| 📝 | Assessments | `/assessments` | Assessments |
| 📊 | Reports | `/reports` | Reports |
| ⚙ | Settings | `/settings` | Settings (Ctrl+,) |
| ❓ | Help | `/help` | Help Center (F1) |

### Active State

- Left accent bar: 3px wide, 24px tall, `--color-accent`
- Icon color: `--color-accent`
- Background: `--color-nav-rail-active`

### Collapsible Behaviour

| Window Width | Rail State | Trigger |
|--------------|------------|---------|
| 1024–1199 | Collapsed (0px) | Auto-collapse |
| 1200–1599 | Collapsed by default, expand on hover | Auto + manual |
| 1600+ | Expanded (64px) | Manual collapse possible |

Transition: 200ms ease-out, `width` + `opacity`.

---

## 6. Sidebar

**Width:** 240px (default) | Min: 180px | Max: 400px | **Position:** Left of workspace
**Resizable:** Yes, via drag handle (8px invisible hit area)
**Background:** `--color-sidebar`

```
┌──────────────────────────────────┐
│ [Breadcrumbs]                    │ 40px toolbar area
├──────────────────────────────────┤
│ Section Header                   │
│                                  │
│ [Tree / List / Form Content]     │
│ Contextual to current section    │
│                                  │
│                                  │
│                                  │
│                                  │
│                                  │
├──────────────────────────────────┤
│ [Sidebar Footer Actions]         │ 48px
└──────────────────────────────────┘
```

### Contextual Content by Section

| Section | Sidebar Content |
|---------|----------------|
| Courses | Course module tree, progress per module |
| Simulations | Scenario list, difficulty filters |
| Assessments | Assessment list, upcoming due dates |
| Reports | Report type selector, date range |
| Settings | Category navigation list |
| Help | Topic tree, search |

### Resize Behaviour

- Drag handle on right edge of sidebar
- Snap to 180px, 240px, 320px, 400px
- Double-click handle → reset to 240px
- Collapse button at top-right of sidebar: collapses to 0px

---

## 7. Toolbar

**Height:** 40px | **Position:** Top of workspace area
**Background:** `--color-toolbar`

```
┌──────────────────────────────────────────────────────────────┐
│ [← Back] Home > Courses > Intro to Network Security   [⋯]   │
└──────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| Back button | Navigate to previous view (left arrow) |
| Breadcrumbs | Current location, clickable segments |
| Overflow menu | Additional actions (⋯) |

---

## 8. Workspace Area

**Position:** Fills remaining space after rail, sidebar, toolbar, status bar
**Overflow:** `auto` (scrollable)
**Padding:** 24px all sides (comfortable), scales with density

---

## 9. Status Bar

**Height:** 24px | **Position:** Fixed bottom | **z-index:** 80

```
┌─────────────────────────────────────────────────────────────────┐
│ [🟢 Online]  │  Student: alex@lab.edu  │  💾 Saved 2s ago  │  1.2 GB │
└─────────────────────────────────────────────────────────────────┘
```

| Slot | Content | Notes |
|------|---------|-------|
| Connection | 🟢 Online / 🟡 Offline Mode / 🔴 Disconnected | aria-live="polite" |
| User | Current user name / email | Truncated at 200px |
| Last Save | "Saved 2s ago" / "Saving…" / "Unsaved changes" | Debounced |
| Storage | Used / Total | e.g., "1.2 GB / 10 GB" |

---

## 10. Global Search Overlay

**Trigger:** `Ctrl+K` or click search input
**Display:** Centered modal overlay, 600px wide, 480px tall

```
┌─────────────────────────────────────────────────────┐
│ 🔍 Search courses, settings, help...        [Esc]  │
├─────────────────────────────────────────────────────┤
│ RECENT                                               │
│   📚 Intro to Network Security                      │
│   ⚙ Theme Settings                                  │
│                                                     │
│ COURSES (3 results)                                 │
│   📚 Advanced Cryptography                          │
│   📚 Web Application Security                       │
│   📚 Incident Response                              │
│                                                     │
│ SETTINGS (1 result)                                  │
│   ⚙ Accessibility Preferences                       │
│                                                     │
│ HELP (2 results)                                     │
│   ❓ Getting Started Guide                          │
│   ❓ Keyboard Shortcuts                             │
└─────────────────────────────────────────────────────┘
```

### Search Behaviour

- Fuzzy matching on titles, descriptions, settings labels
- Results categorized and ranked
- Arrow keys to navigate, Enter to select
- `Esc` to close, focus returns to trigger element
- Minimum 2 characters to search
- Debounce: 150ms
- `aria-live="polite"` announces result count

---

## 11. Command Palette

**Trigger:** `Ctrl+Shift+P`
**Display:** Same overlay as search, 600px wide, 480px tall

```
┌─────────────────────────────────────────────────────┐
│ ⚡ Run command...                          [Esc]    │
├─────────────────────────────────────────────────────┤
│ RECENT COMMANDS                                      │
│   ▶ Run Simulation: SQL Injection                   │
│   ▶ Export Report as PDF                            │
│                                                     │
│ NAVIGATION                                           │
│   → Go to Dashboard                                 │
│   → Go to Course Catalog                            │
│   → Go to Settings                                  │
│                                                     │
│ ACTIONS                                              │
│   ▶ Create New Course                               │
│   ▶ Start Assessment                                │
│   ▶ Create Backup                                   │
│   ▶ Toggle Theme                                    │
└─────────────────────────────────────────────────────┘
```

### Command Categories

| Prefix | Category | Examples |
|--------|----------|----------|
| `→` | Navigation | Go to Dashboard, Go to Courses |
| `▶` | Action | Run Simulation, Create Backup |
| `🔧` | Tool | Toggle Sidebar, Clear Cache |
| `?` | Help | Open Help Center, Keyboard Shortcuts |

---

## 12. Quick Actions (FAB)

**Position:** Bottom-right corner, 16px inset
**Size:** 56 × 56px (circle)

```
        ┌──────┐
        │  [+] │  ← FAB
        └──────┘
```

- On click: expands vertically into action list
- Contextual actions based on current screen
- Keyboard: `Ctrl+.` to focus FAB, Enter to open, arrow keys to select
- `aria-label="Quick actions"`

---

## 13. Notification Toast Container

**Position:** Top-right, 16px from top, 16px from right
**z-index:** 9999
**Max visible:** 3 stacked, auto-dismiss after 5s (manual dismiss also available)

```
┌──────────────────────────┐
│ ✅ Course enrolled       │  ← success
│    Intro to Crypto       │
│                     [✕]  │
├──────────────────────────┤
│ ⚠️ Assessment due soon   │  ← warning
│    In 2 hours             │
│                     [✕]  │
├──────────────────────────┤
│ ℹ️ Backup completed       │  ← info
│    1.2 GB saved           │
│                     [✕]  │
└──────────────────────────┘
```

---

## 14. Responsive Breakpoints

| Breakpoint | Width | Rail | Sidebar | Density |
|------------|-------|------|---------|---------|
| Compact | 1024–1199 | Collapsed (0px) | 180px | Compact (16px pad) |
| Standard | 1200–1599 | Auto (64px or 0px) | 240px | Standard (20px pad) |
| Comfortable | 1600–2199 | Expanded (64px) | 280px | Comfortable (24px pad) |
| Spacious | 2200+ | Expanded (64px) | 320px | Spacious (32px pad) |

### Density Modes

| Mode | Padding | Font Size | Line Height | Icon Size |
|------|---------|-----------|-------------|-----------|
| Compact | 16px | 13px | 18px | 16px |
| Standard | 20px | 14px | 20px | 18px |
| Comfortable | 24px | 15px | 22px | 20px |
| Spacious | 32px | 16px | 24px | 24px |

---

## 15. Focus Management

### Global Focus Order

1. Title bar controls (window chrome)
2. Application Header (logo → search → avatar → bell → gear)
3. Navigation Rail (top to bottom)
4. Sidebar (top to bottom)
5. Toolbar (back → breadcrumbs → overflow)
6. Workspace Area (content-defined)
7. Status Bar (left to right)
8. FAB

### Focus Indicators

- **Ring:** 2px solid `--color-focus-ring`, offset 2px
- **Style:** `outline: 2px solid var(--color-focus-ring); outline-offset: 2px;`
- **Color:** `#3B82F6` (light), `#60A5FA` (dark), `#FFFFFF` (high-contrast)
- **Keyboard trap:** Only in modals and overlays (search, command palette, dialogs)

### Skip Links

- `Ctrl+Shift+S` → Skip to main content
- `Ctrl+Shift+N` → Skip to navigation
- Visual on first Tab press in any session

---

## 16. Keyboard Shortcut Map

| Shortcut | Action | Scope |
|----------|--------|-------|
| `Ctrl+K` | Open search | Global |
| `Ctrl+Shift+P` | Open command palette | Global |
| `Ctrl+D` | Go to Dashboard | Global |
| `Ctrl+,` | Open Settings | Global |
| `Ctrl+.` | Focus FAB | Global |
| `Ctrl+Shift+S` | Skip to main content | Global |
| `F1` | Open Help Center | Global |
| `Esc` | Close overlay / go back | Global |
| `Ctrl+Shift+M` | Toggle sidebar | Global |
| `Ctrl+Shift+R` | Toggle rail collapse | Global |

---

## 17. Offline-First Behaviour

- Shell loads from local cache; no network required
- Status bar shows `🟡 Offline Mode` when disconnected
- All UI rendering is immediate (no loading spinners for shell)
- Network-dependent actions queue and sync on reconnect
- Toast: `Reconnected — syncing 3 pending changes` on reconnect

---

## 18. Performance Targets

| Metric | Target |
|--------|--------|
| Shell render (cold) | < 500ms |
| Navigation transition | < 100ms |
| Search overlay open | < 50ms |
| Status bar update | < 16ms (60fps) |
| Toast appearance | < 200ms |
| Memory usage | < 300MB idle |

---

## 19. Theming

Three themes supported: **Light**, **Dark**, **High-Contrast**

| Element | Light | Dark | High-Contrast |
|---------|-------|------|---------------|
| Background | `#FFFFFF` | `#0F172A` | `#000000` |
| Surface | `#F8FAFC` | `#1E293B` | `#1A1A1A` |
| Text | `#1E293B` | `#F1F5F9` | `#FFFFFF` |
| Accent | `#3B82F6` | `#60A5FA` | `#FFFF00` |
| Nav Rail BG | `#F1F5F9` | `#1E293B` | `#000000` |
| Sidebar BG | `#FFFFFF` | `#0F172A` | `#000000` |
| Focus Ring | `#3B82F6` | `#60A5FA` | `#FFFFFF` |
| Border | `#E2E8F0` | `#334155` | `#FFFFFF` |

---

## 20. Electron IPC Events

| Channel | Direction | Purpose |
|---------|-----------|---------|
| `shell:resize` | Renderer → Main | Sidebar/rail resize |
| `shell:theme` | Main → Renderer | Theme change from OS |
| `shell:minimize` | Renderer → Main | Minimize window |
| `shell:maximize` | Renderer → Main | Toggle maximize |
| `shell:close` | Renderer → Main | Close window |
| `shell:focus` | Main → Renderer | Bring window to front |
| `shell:fullscreen` | Renderer → Main | Toggle fullscreen |

---

## 21. Zustand Store — Shell Slice

```typescript
interface ShellState {
  railExpanded: boolean;
  sidebarWidth: number;
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'high-contrast';
  density: 'compact' | 'standard' | 'comfortable' | 'spacious';
  searchOpen: boolean;
  commandPaletteOpen: boolean;
  notificationPanelOpen: boolean;
  connectionStatus: 'online' | 'offline' | 'disconnected';
  lastSaved: Date | null;
  storageUsed: number;
  storageTotal: number;

  toggleRail: () => void;
  setSidebarWidth: (w: number) => void;
  toggleSidebar: () => void;
  setTheme: (t: Theme) => void;
  setDensity: (d: Density) => void;
  toggleSearch: () => void;
  toggleCommandPalette: () => void;
  toggleNotificationPanel: () => void;
}
```

---

## 22. ARIA Landmarks

```html
<div role="application" aria-label="AuthShield Lab">
  <header role="banner" aria-label="Application header">…</header>
  <nav role="navigation" aria-label="Main navigation">…</nav>
  <aside role="complementary" aria-label="Sidebar">…</aside>
  <main role="main" aria-label="Workspace">…</main>
  <footer role="contentinfo" aria-label="Status bar">…</footer>
  <div role="status" aria-live="polite">…</div>
  <div role="alert" aria-live="assertive">…</div>
</div>
```

---

## 23. Migration & Versioning

- Shell version stored in `package.json` → displayed in About screen
- Layout changes use feature flags in Zustand
- Previous layout preferences persisted in `localStorage`
- Migration script runs on version upgrade to reconcile preferences

---

*End of Application Shell Specification*
