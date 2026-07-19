# Layout System — AuthShield Lab

> The structural foundation for all screen layouts, ensuring consistency, responsiveness, and accessibility.

---

## Application Shell

The application shell is the outermost container that wraps all content within the Electron window.

### Window Configuration

| Property | Value | Notes |
|---|---|---|
| Minimum size | 1024 x 768 | Below this, scroll and reflow |
| Default size | 1280 x 800 | Comfortable starting size |
| Maximum size | Unlimited | Content reflows at breakpoints |
| Resizable | Yes | Both horizontal and vertical |
| Fullscreen | Yes | F11 or double-click title bar |

### Shell Anatomy

```
┌──────────────────────────────────────────────────────┐
│ Title Bar (32px) — App name, window controls          │
├──────────────────────────────────────────────────────┤
│ Menu Bar (optional, 24px) — File, Edit, View, etc.   │
├────────┬─────────────────────────────────────────────┤
│        │ Toolbar (48px) — Breadcrumbs, actions        │
│ Nav    ├─────────────────────────────────────────────┤
│ Rail   │                                             │
│ (64px) │                                             │
│        │              Content Area                    │
│        │              (flex: 1)                       │
│        │                                             │
│        │                                             │
├────────┴─────────────────────────────────────────────┤
│ Status Bar (28px) — Status, sync, quick actions       │
└──────────────────────────────────────────────────────┘
```

### Shell Layout Tokens

| Token | CSS Variable | Value | Usage |
|---|---|---|---|
| shell-titlebar-height | `--shell-titlebar-height` | 32px | Electron title bar |
| shell-menubar-height | `--shell-menubar-height` | 24px | Application menu bar |
| shell-statusbar-height | `--shell-statusbar-height` | 28px | Bottom status bar |
| shell-toolbar-height | `--shell-toolbar-height` | 48px | Top toolbar with breadcrumbs |
| shell-navrail-width | `--shell-navrail-width` | 64px | Left navigation rail |
| shell-sidebar-width | `--shell-sidebar-width` | 240px | Left contextual sidebar |
| shell-sidebar-width-collapsed | `--shell-sidebar-width-collapsed` | 48px | Collapsed sidebar |
| shell-rightpanel-width | `--shell-rightpanel-width` | 320px | Right context panel |

---

## Navigation Rail

The primary navigation mechanism, always visible on the left edge of the application.

### Dimensions

| Property | Value | Notes |
|---|---|---|
| Width | 64px | Fixed, not resizable |
| Collapsed width | 48px | Icon only, no labels |
| Item height | 48px | Touch/click target minimum |
| Icon size | 24px | Centered in item |
| Label height | 12px | Below icon when expanded |
| Spacing between items | 4px | Vertical gap |

### Behavior

- Always visible — never hidden completely
- Collapsible to icon-only mode (48px) via toggle button
- Active section indicated by filled background + color change
- Hover shows tooltip with section name (when collapsed)
- Keyboard: Arrow Up/Down to navigate items, Enter to select
- Focus wraps from last to first item

### Navigation Items

| Order | Section | Icon | Keyboard Shortcut |
|---|---|---|---|
| 1 | Dashboard | Home | Ctrl+1 |
| 2 | Courses | Book | Ctrl+2 |
| 3 | Simulations | Shield | Ctrl+3 |
| 4 | Assessments | Clipboard | Ctrl+4 |
| 5 | Reports | BarChart | Ctrl+5 |
| 6 | (Separator) | — | — |
| 7 | Settings | Settings | Ctrl+, |

---

## Sidebar

Contextual content panel that provides secondary navigation or detail information within each section.

### Dimensions

| Property | Value | Notes |
|---|---|---|
| Default width | 240px | Standard sidebar |
| Minimum width | 180px | Cannot resize below this |
| Maximum width | 400px | Cannot resize above this |
| Collapsed width | 0px | Fully hidden |
| Toggle button | 32px wide | Right edge of sidebar |

### Layout Tokens

| Token | CSS Variable | Value |
|---|---|---|
| sidebar-width | `--sidebar-width` | 240px |
| sidebar-width-min | `--sidebar-width-min` | 180px |
| sidebar-width-max | `--sidebar-width-max` | 400px |
| sidebar-padding | `--sidebar-padding` | 12px |
| sidebar-gap | `--sidebar-gap` | 4px |

### Behavior

- Resizable via drag handle on right edge
- Collapsible via toggle button or keyboard shortcut (Ctrl+B)
- Remembers width preference across sessions
- Scrollable when content exceeds height
- Keyboard: Tab to enter, Arrow keys to navigate items, Escape to collapse
- Focus management: focus returns to main content when sidebar collapses

---

## Toolbar

Action bar at the top of the content area, providing context-specific actions and navigation context.

### Dimensions

| Property | Value | Notes |
|---|---|---|
| Height | 48px | Fixed |
| Padding horizontal | 16px | Consistent with content |
| Breadcrumb area | Flex: 1 | Left side |
| Actions area | Shrink: 0 | Right side |

### Anatomy

```
┌─────────────────────────────────────────────────────┐
│ [Section] / [Subsection] / [Current]    [Search] [+] │
└─────────────────────────────────────────────────────┘
```

### Toolbar Components

| Position | Component | Purpose |
|---|---|---|
| Left | Breadcrumbs | Navigation context |
| Center | Title (optional) | Current page title |
| Right | Search | Quick search within section |
| Right | Action buttons | Primary and secondary actions |
| Right | View toggle | Switch between list/card/table views |

---

## Content Area

The main workspace where primary content is displayed.

### Layout Behavior

- Uses `flex: 1` to fill available space between toolbar and status bar
- Content is scrollable when exceeding viewport height
- Horizontal scroll is avoided — content reflows at breakpoints
- Maximum reading width: 680px for body text content
- Full width for data-heavy content (tables, dashboards)

### Content Layouts

| Layout | Usage | Structure |
|---|---|---|
| Single column | Forms, reading content | Max-width 680px, centered |
| Two column | List + detail views | 1/3 + 2/3 or 1/4 + 3/4 |
| Three column | Dashboard, data views | Equal thirds or custom grid |
| Full width | Tables, wide data | Edge-to-edge with padding |
| Split view | Comparison, editor + preview | Resizable horizontal split |

---

## Right Panel

Context panel for inspector, properties, or detail views. Appears contextually.

### Dimensions

| Property | Value | Notes |
|---|---|---|
| Default width | 320px | Standard panel |
| Minimum width | 240px | Cannot resize below |
| Maximum width | 480px | Cannot resize above |
| Toggle button | 32px wide | Left edge of panel |

### Behavior

- Hidden by default — shown when context requires (e.g., selecting an item)
- Resizable via drag handle on left edge
- Keyboard: Ctrl+Shift+P to toggle
- Focus management: focus returns to triggering element when panel closes
- Stacks with sidebar if both are open (content area shrinks)

---

## Footer / Status Bar

Persistent bar at the bottom of the application providing status information and quick actions.

### Dimensions

| Property | Value | Notes |
|---|---|---|
| Height | 28px | Fixed |
| Padding | 0 12px | Horizontal padding |
| Font size | 11px (text-micro) | Compact information |

### Anatomy

```
┌──────────────────────────────────────────────────────┐
│ [Status]  [Sync] [Connection]          [Version] [?] │
└──────────────────────────────────────────────────────┘
```

### Status Bar Sections

| Position | Content | Purpose |
|---|---|---|
| Left | Status message | Current operation status |
| Left-center | Sync status | Last sync time, syncing indicator |
| Center | Connection indicator | Online/offline status with icon |
| Right | Keyboard shortcut help | Open shortcut reference |
| Right | Version | Application version |

---

## Dialogs

Modal overlays for focused interactions. Always centered in the viewport.

### Dimensions

| Dialog Type | Width | Height | Usage |
|---|---|---|---|
| Confirm | 400px | Auto | Simple confirmations |
| Form | 480px | Auto | Data entry forms |
| Large | 640px | Auto | Complex forms, details |
| Full-screen | 100vw | 100vh | Immersive tasks (lab environments) |
| Alert | 360px | Auto | System alerts, errors |

### Dialog Layout Tokens

| Token | CSS Variable | Value |
|---|---|---|
| dialog-padding | `--dialog-padding` | 24px |
| dialog-gap | `--dialog-gap` | 16px |
| dialog-header-height | `--dialog-header-height` | auto |
| dialog-footer-height | `--dialog-footer-height` | auto |
| dialog-backdrop-opacity | `--dialog-backdrop-opacity` | 0.6 |
| dialog-max-width | `--dialog-max-width` | 640px |
| dialog-border-radius | `--dialog-border-radius` | 12px |

### Dialog Structure

```
┌──────────────────────────────────────┐
│ [Title]                        [X]   │  Header (optional)
├──────────────────────────────────────┤
│                                      │
│           Dialog Body                │  Scrollable content
│                                      │
├──────────────────────────────────────┤
│  [Cancel]               [Action]     │  Footer (optional)
└──────────────────────────────────────┘
```

### Dialog Behavior

- Focus is trapped within the dialog when open
- Escape key closes the dialog (unless action is destructive and in-progress)
- Clicking backdrop closes the dialog (unless action is destructive)
- Focus returns to the triggering element when dialog closes
- Multiple dialogs stack (rare — avoid when possible)
- Full-screen dialogs have a close button in the top-right corner

---

## Split Views

Resizable panes for side-by-side content comparison or editing.

### Configuration

| Property | Value | Notes |
|---|---|---|
| Direction | Horizontal or Vertical | Configurable per instance |
| Min pane size | 200px | Cannot resize below |
| Default split | 50/50 | Equal split |
| Handle width | 4px | Draggable divider |
| Handle hover width | 8px | Expanded hit target |

### Split View Tokens

| Token | CSS Variable | Value |
|---|---|---|
| split-handle-width | `--split-handle-width` | 4px |
| split-handle-hover-width | `--split-handle-hover-width` | 8px |
| split-handle-color | `--split-handle-color` | var(--color-border-default) |
| split-handle-active-color | `--split-handle-active-color` | var(--color-primary) |
| split-min-pane | `--split-min-pane` | 200px |

---

## Tabbed Views

Tabs for switching between content views within a panel or section.

### Dimensions

| Property | Value | Notes |
|---|---|---|
| Tab height | 40px | Fixed |
| Tab min-width | 80px | Minimum tab width |
| Tab max-width | 200px | Maximum before truncation |
| Tab padding | 0 16px | Horizontal padding |
| Active indicator | 2px bottom border | Primary color |
| Gap between tabs | 0 | Tabs are adjacent |

### Tab Behavior

- Horizontal scroll when tabs exceed container width
- Closeable tabs show X icon on hover (or always for closable tabs)
- Keyboard: Ctrl+Tab to cycle forward, Ctrl+Shift+Tab to cycle backward
- Middle-click closes a tab (when tabs are closable)
- New tab button is always the last item

---

## Dashboard Cards

Grid-based card layouts for dashboard views.

### Card Grid

| Property | Value | Notes |
|---|---|---|
| Grid columns | Auto-fill | Responsive |
| Min column width | 280px | Minimum card width |
| Gap | 16px | Space between cards |
| Max columns | 4 | On ultra-wide displays |

### Card Types

| Card Type | Min Height | Usage |
|---|---|---|
| Stat card | 120px | Key metrics |
| Course card | 200px | Course listing |
| Activity card | 160px | Recent activity |
| Chart card | 280px | Data visualizations |
| Welcome card | 180px | Dashboard hero |

### Card Layout Tokens

| Token | CSS Variable | Value |
|---|---|---|
| card-padding | `--card-padding` | 16px |
| card-gap | `--card-gap` | 16px |
| card-radius | `--card-radius` | 8px |
| card-shadow | `--card-shadow` | var(--elevation-1) |
| card-hover-shadow | `--card-hover-shadow` | var(--elevation-2) |
| card-min-width | `--card-min-width` | 280px |

---

## Grid System

12-column grid for content layout within the content area.

### Grid Tokens

| Token | CSS Variable | Value |
|---|---|---|
| grid-columns | `--grid-columns` | 12 |
| grid-gutter | `--grid-gutter` | 16px |
| grid-margin | `--grid-margin` | 16px |
| grid-max-width | `--grid-max-width` | 1200px |

### Grid Breakpoints

| Breakpoint | Columns | Gutter | Margin | Target |
|---|---|---|---|---|
| < 640px | 4 | 16px | 16px | Small windows |
| 640-767px | 6 | 16px | 16px | Narrow desktop |
| 768-1023px | 8 | 16px | 24px | Standard desktop |
| 1024-1279px | 12 | 16px | 24px | Wide desktop |
| ≥ 1280px | 12 | 16px | 32px | Ultra-wide |

---

## Responsive Behavior

### Breakpoint Manifesto

AuthShield Lab is a desktop application, not a mobile app. Responsive behavior addresses window resizing within the desktop context — not phone screens.

| Breakpoint | Variable | Width | Behavior |
|---|---|---|---|
| Compact | `bp-compact` | < 1024px | Sidebar auto-collapses, content full-width |
| Standard | `bp-standard` | 1024-1279px | Sidebar + content (default) |
| Wide | `bp-wide` | 1280-1535px | Sidebar + content + right panel |
| Ultra | `bp-ultra` | ≥ 1536px | Full layout with expanded dashboard |

### Window Resize Behavior

- Below 1024px width: sidebar collapses automatically
- Below 1024px height: status bar remains, toolbar condenses
- Content reflows at each breakpoint
- No horizontal scrolling at any breakpoint for standard content
- Tables get horizontal scroll at narrow widths (acceptable for data-dense content)
- Dialogs maintain minimum width and scroll internally at small window sizes

---

## Layout Patterns

### List + Detail Pattern

```
┌────────┬──────────────────────────┐
│        │                          │
│ List   │      Detail View         │
│ 240px  │      (flex: 1)           │
│        │                          │
│        │                          │
└────────┴──────────────────────────┘
```

### Dashboard Pattern

```
┌──────────────────────────────────┐
│ [Stat] [Stat] [Stat] [Stat]      │  Stats row
├──────────────────┬───────────────┤
│                  │               │
│   Chart          │   Activity    │  Main content
│                  │               │
├──────────────────┴───────────────┤
│ [Course] [Course] [Course] [Cour]│  Course cards
└──────────────────────────────────┘
```

### Form Pattern

```
┌──────────────────────────────────┐
│ [Breadcrumbs]         [Actions]  │  Toolbar
├──────────────────────────────────┤
│                                  │
│  ┌──────────────────────────┐   │
│  │  Form Header / Title     │   │
│  ├──────────────────────────┤   │
│  │  Field Group 1           │   │
│  │  Field Group 2           │   │
│  │  ...                     │   │
│  ├──────────────────────────┤   │
│  │  [Cancel]     [Submit]   │   │  Footer
│  └──────────────────────────┘   │
│                                  │
└──────────────────────────────────┘
```

### Editor Pattern

```
┌──────────────────────────────────┐
│ [Breadcrumbs]  [Preview] [Save] │  Toolbar
├─────────────────────┬────────────┤
│                     │            │
│   Editor            │  Preview   │  Split view
│   (flex: 1)         │  (flex: 1) │
│                     │            │
└─────────────────────┴────────────┘
```

---

## Layout Accessibility

### Focus Management

- Tab order follows visual layout (top-to-bottom, left-to-right)
- Skipping hidden content (collapsed sidebar, closed dialog)
- Focus indicators are visible on all focusable elements
- Focus is trapped in modals and dialogs
- Focus returns to triggering element after modal closes

### Readability at Zoom

- Content reflows at all zoom levels up to 200%
- No horizontal scrolling for text content at 200% zoom
- Layout containers use relative units (rem, %)
- Sidebars can be collapsed to provide more content space
- Minimum content width: 320px (single column)

### Screen Reader Layout

- Semantic landmarks: `<main>`, `<nav>`, `<header>`, `<footer>`, `<aside>`
- Skip links: "Skip to main content", "Skip to navigation"
- ARIA labels on all regions: `aria-label="Primary navigation"`, `aria-label="Content area"`
- Heading hierarchy is logical and reflects visual layout

---

*Layout is the skeleton of the interface. Every layout decision must support consistency, responsiveness, and accessibility.*
