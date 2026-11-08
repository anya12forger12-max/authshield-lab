# Navigation System — AuthShield Lab

> Global, contextual, and utility navigation patterns that keep users oriented and efficient.

---

## Navigation Architecture

AuthShield Lab uses a three-tier navigation architecture:

1. **Primary Navigation** — always visible, section-level (Navigation Rail)
2. **Secondary Navigation** — contextual within each section (Sidebar)
3. **Utility Navigation** — on-demand, for rapid access (Command Palette, Search, Breadcrumbs)

---

## Primary Navigation — Navigation Rail

### Structure

The navigation rail is a 64px-wide vertical bar on the left edge of the application. It is always visible and provides access to the application's top-level sections.

### Sections

| Order | Section | Icon | Route | Shortcut | Description |
|---|---|---|---|---|---|
| 1 | Dashboard | Home | /dashboard | Ctrl+1 | Overview, recent activity, stats |
| 2 | Courses | BookOpen | /courses | Ctrl+2 | Course catalog and management |
| 3 | Simulations | Shield | /simulations | Ctrl+3 | Lab environments and exercises |
| 4 | Assessments | ClipboardCheck | /assessments | Ctrl+4 | Quizzes, tests, evaluations |
| 5 | Reports | BarChart3 | /reports | Ctrl+5 | Analytics, progress, exports |
| — | Divider | — | — | — | Visual separator |
| 6 | Settings | Settings | /settings | Ctrl+, | Application configuration |

### Rail Behavior

- **Always visible** — never fully hidden, even on narrow windows
- **Collapsible** to 48px (icon-only mode) via toggle button at the bottom
- **Active state**: Filled background (primary-50 light / primary-900 dark) + primary-600 icon color
- **Hover state**: Subtle background tint (primary-50/50 light / primary-800/50 dark)
- **Focus state**: 2px solid blue-500 ring around the icon

### Rail A11y

- `role="navigation"` with `aria-label="Primary navigation"`
- Each item: `role="link"` (or `role="button"` for non-route items)
- Active item: `aria-current="page"`
- Collapsed mode: tooltip on hover/focus shows section name
- Screen reader: "Primary navigation, Dashboard (current), Courses, Simulations..."

---

## Secondary Navigation — Section Sidebar

### Purpose

Provides navigation within each primary section. The sidebar content changes based on the active section.

### Section-Specific Sidebars

#### Dashboard Sidebar

| Item | Description |
|---|---|
| Overview | Main dashboard view |
| Recent Activity | Timeline of recent actions |
| My Progress | Personal learning progress |
| Quick Actions | Frequently used actions |
| Announcements | System and course announcements |

#### Courses Sidebar

| Item | Description |
|---|---|
| All Courses | Complete course catalog |
| My Courses | Enrolled courses |
| In Progress | Currently active courses |
| Completed | Finished courses |
| Bookmarks | Bookmarked courses |

#### Simulations Sidebar

| Item | Description |
|---|---|
| Available Labs | List of available lab environments |
| My Labs | Saved lab sessions |
| Lab History | Previously completed labs |
| Custom Labs | User-created lab configurations |

#### Assessments Sidebar

| Item | Description |
|---|---|
| Pending | Upcoming assessments |
| In Progress | Currently taking |
| Completed | Past assessments with results |
| Practice | Practice quizzes and drills |

#### Reports Sidebar

| Item | Description |
|---|---|
| My Progress | Personal analytics |
| Course Reports | Per-course analytics |
| Skill Map | Competency visualization |
| Export Center | Data export tools |

#### Settings Sidebar

| Item | Description |
|---|---|
| General | Application preferences |
| Appearance | Theme, font size, layout |
| Accessibility | A11y settings, screen reader |
| Privacy | Data handling, local storage |
| Keyboard | Custom shortcuts |
| About | Version, licenses, updates |

### Sidebar Behavior

- **Resizable** via drag handle (180px-400px range)
- **Collapsible** via Ctrl+B or toggle button
- **Active item** indicated by primary-50 background and primary-600 text
- **Nested items** expand/collapse with chevron icon
- **Keyboard**: Tab to enter, Arrow Up/Down to navigate, Enter to select, Escape to collapse
- **Width preference** saved per-section across sessions

---

## Breadcrumbs

### Purpose

Show the user's current location within the navigation hierarchy. Allow quick navigation to any ancestor.

### Format

```
Dashboard / Courses / Introduction to Network Security / Module 3 / Lab Exercise 2
```

### Breadcrumb Rules

- Maximum 5 levels before truncation (show "... / parent / current")
- All segments except the current page are clickable links
- Current page is bold and non-clickable
- Separator: `/` with spacing
- Overflow: leftmost items collapse into "..." with dropdown menu

### Breadcrumb A11y

- `nav` element with `aria-label="Breadcrumb"`
- `ol` list for breadcrumb items
- Current page: `aria-current="page"`
- Truncated items accessible via dropdown menu

---

## Command Palette (Ctrl+K)

### Purpose

Universal search and action execution. The fastest way to navigate or perform any action.

### Trigger

- Keyboard: Ctrl+K (Windows/Linux), Cmd+K (macOS)
- Click: Search bar in the toolbar

### Structure

```
┌─────────────────────────────────────────────┐
│ 🔍 Type a command or search...              │
├─────────────────────────────────────────────┤
│ Recent                                      │
│   Dashboard                                 │
│   Course: Intro to Network Security         │
│                                             │
│ Actions                                     │
│   Create new course                         │
│   Import users                              │
│   Generate report                           │
│                                             │
│ Navigation                                  │
│   Go to Settings                            │
│   Go to Simulations                         │
│                                             │
│ Content                                     │
│   Course: Advanced Penetration Testing      │
│   Lab: SQL Injection Basics                 │
└─────────────────────────────────────────────┘
```

### Behavior

- Opens centered at top of viewport with overlay
- Auto-focuses search input
- Fuzzy matching: "net sec" matches "Network Security"
- Results update as user types (debounced 100ms)
- Categories: Recent, Actions, Navigation, Content, Settings
- Maximum 10 results per category, 50 total

### Keyboard Support

| Key | Action |
|---|---|
| Type | Filter results |
| Up/Down | Navigate results |
| Enter | Execute selected action |
| Escape | Close command palette |
| Tab | Cycle between categories |
| Ctrl+K | Re-open (when already open — refocus input) |

### Command Palette A11y

- `role="dialog"` and `aria-modal="true"`
- `aria-label="Command palette"`
- Search input: `role="combobox"`, `aria-expanded`, `aria-controls`
- Results list: `role="listbox"`, each result `role="option"`
- `aria-activedescendant` tracks highlighted result
- Live region announces result count: "12 results found"
- Category headings use `role="separator"` or `aria-hidden` with visual presentation

---

## Quick Actions

### Toolbar Quick Actions

Displayed in the toolbar for each section, providing one-click access to common operations.

| Section | Quick Actions |
|---|---|
| Dashboard | Refresh, Filter date range |
| Courses | New course, Import, Filter by status |
| Simulations | New lab, Import lab, Filter by difficulty |
| Assessments | New assessment, Import, Filter by type |
| Reports | Export, Date range, Filter by course |

### Quick Action Buttons

- Primary action: Filled button (blue-600 background)
- Secondary actions: Ghost buttons (transparent, text-secondary)
- Icon-only buttons include `aria-label`
- Grouped actions separated by 1px divider

---

## Favorites

### Purpose

User-bookmarked items for quick access.

### Favorites Mechanism

- **Toggle**: Ctrl+B on any item (course, lab, assessment, page)
- **Indicator**: Filled star icon (amber-500) on favorited items
- **Display**: Favorites section in sidebar, favorites filter in lists
- **Maximum**: 20 favorites (with graceful degradation if exceeded)
- **Persistence**: Saved locally, synced if online account exists

### Favorites A11y

- Star icon has `aria-label="Remove from favorites"` or `aria-label="Add to favorites"`
- Toggle announces state change: "Added to favorites" / "Removed from favorites"
- Favorites section in sidebar: `aria-label="Favorites"`

---

## Recent Items

### Purpose

Show the last 10 screens/items the user visited.

### Implementation

- Stored in local state (not persisted — resets on app restart)
- Available in the Dashboard sidebar under "Recent"
- Maximum 10 items
- Each item shows: icon, title, section, timestamp ("2 minutes ago")
- Click navigates to the item
- "Clear recent" button to reset the list

### Recent Items A11y

- `aria-label="Recent items"` on the list
- Each item: descriptive label with section context
- "Clear recent" has `aria-label="Clear recent items"`

---

## Navigation History

### Back/Forward

- Maintained per navigation stack
- Alt+Left: Go back
- Alt+Right: Go forward
- History is section-scoped (switching sections does not pollute history)
- Maximum history depth: 50 entries

### History A11y

- Back/Forward buttons: `aria-label="Go back"` / `aria-label="Go forward"`
- Disabled state when history is empty: `aria-disabled="true"`
- Screen reader announces page change on navigation

---

## Workspace Switching

### Purpose

Toggle between different application modes for different user roles.

### Workspaces

| Workspace | Audience | Features |
|---|---|---|
| Learning | Students | Courses, labs, assessments, progress |
| Teaching | Instructors | Content authoring, grading, student management |
| Administration | Admins | User management, system config, reporting |
| Training | Corporate trainers | Enterprise features, compliance, bulk operations |

### Workspace Switcher

- Dropdown in the toolbar (right side)
- Only shows workspaces the user has permission to access
- Switching workspaces changes the sidebar and available actions
- Current workspace shown in status bar

### Workspace A11y

- `role="listbox"` with `aria-label="Workspace selector"`
- Current workspace: `aria-selected="true"`
- Workspace change announces: "Switched to {workspace} workspace"

---

## Notification Center

### Purpose

Display system notifications, alerts, and activity updates.

### Trigger

- Bell icon in the toolbar (right side)
- Badge shows unread count

### Notification Types

| Type | Priority | Auto-dismiss | Sound |
|---|---|---|---|
| System alert | High | No | Yes |
| Assessment due | High | No | No |
| Grade posted | Medium | After reading | No |
| Course update | Low | After 30s | No |
| Sync complete | Low | After 10s | No |

### Notification Panel

```
┌─────────────────────────────┐
│ Notifications        [Mark all read] │
├─────────────────────────────┤
│ 🔴 System maintenance at 2am  │
│ 📋 New grade posted           │
│ 📚 Course updated             │
│ ✅ Sync complete              │
└─────────────────────────────┘
```

### Notification A11y

- Bell icon: `aria-label="Notifications, 3 unread"`
- Panel: `role="region"` with `aria-label="Notifications"`
- Unread notifications have `aria-label` with "unread" prefix
- "Mark all read" button: `aria-label="Mark all notifications as read"`
- New notifications announced via `aria-live="polite"`

---

## Global Search Bar

### Purpose

Persistent search in the toolbar for finding content, users, and settings.

### Search Scopes

| Scope | Shortcut | Searches |
|---|---|---|
| All | Ctrl+K | Everything |
| Content | Ctrl+Shift+F | Courses, labs, assessments |
| Users | — | User directory (admin only) |
| Settings | — | Application settings |

### Search Results

- Grouped by type (Courses, Labs, Assessments, Users, Settings)
- Each result shows: icon, title, description, section
- Keyboard navigable: Up/Down arrows, Enter to select
- Results highlighted with matching text bolded
- "No results found" empty state with suggestions

---

## Navigation Rules

### Authentication Required

| Screen | Auth Required | Redirect |
|---|---|---|
| Login | No | — |
| Onboarding | No (first run only) | — |
| Dashboard | Yes | Login |
| Courses | Yes | Login |
| Simulations | Yes | Login |
| Assessments | Yes | Login |
| Reports | Yes | Login |
| Settings | Yes | Login |

### Role Restrictions

| Screen | Roles |
|---|---|
| User Management | Administrator, Institution Manager |
| System Settings | Administrator |
| Content Authoring | Instructor, Administrator |
| Student Management | Instructor, Administrator |
| Bulk Operations | Instructor, Administrator, Security Trainer |
| All Learning Features | All roles |

### Deep Linking

- All screens have stable URLs (e.g., `/courses/123/modules/456`)
- Application handles deep links from OS (file associations, shortcuts)
- Unrecognized routes redirect to Dashboard with "Page not found" message

---

## Navigation Accessibility Summary

| Feature | Keyboard | Screen Reader | Motor |
|---|---|---|---|
| Rail navigation | Ctrl+1-6, Tab | Labeled landmarks | Standard click |
| Sidebar | Ctrl+B, Arrow keys | Section labels | Resize handle, collapse |
| Breadcrumbs | Tab | Semantic nav+ol | Click |
| Command palette | Ctrl+K, Arrow keys | Dialog, combobox | Click results |
| Search | Ctrl+F, Ctrl+K | Live region results | Click results |
| History | Alt+Left/Right | Page announcements | Back/Forward buttons |
| Notifications | Click bell, Tab | Unread count, live region | Click |

---

*Navigation should be invisible when done well — users should always know where they are, where they can go, and how to get back.*
