# AuthShield Lab — Global Navigation System

## 1. Overview

This document defines the complete navigation model for AuthShield Lab. The
navigation system is designed for keyboard-first operation, screen reader
compatibility, and efficient multi-tasking across all supported platforms.

---

## 2. Primary Navigation (Left Rail)

The left rail is the persistent primary navigation element. It is always visible
unless the user collapses it.

### 2.1 Layout

```
┌──────────────────────────────┐
│  [Logo / App Name]           │
│                              │
│  📊 Dashboard                │
│  📚 Courses                  │
│  🎯 Simulations              │
│  ✅ Assessments               │
│  📈 Reports                  │
│  ⚙️ Settings                 │
│  ❓ Help                     │
│                              │
│  ─────────────────           │
│  ★ Favorites                 │
│  🕐 Recent                   │
│                              │
│  ─────────────────           │
│  [User Avatar]               │
│  [User Name]                 │
│  [Role Badge]                │
└──────────────────────────────┘
```

### 2.2 Navigation Items

| Position | Label | Icon | Shortcut | Route |
|---|---|---|---|---|
| 1 | Dashboard | grid | Alt+1 | `/dashboard` |
| 2 | Courses | book | Alt+2 | `/courses` |
| 3 | Simulations | target | Alt+3 | `/simulations` |
| 4 | Assessments | check-circle | Alt+4 | `/assessments` |
| 5 | Reports | bar-chart | Alt+5 | `/reports` |
| 6 | Settings | gear | Alt+6 | `/settings` |
| 7 | Help | help-circle | Alt+7 | `/help` |
| separator | — | — | — | — |
| 8 | Favorites | star | Alt+F | `/favorites` |
| 9 | Recent | clock | Alt+R | `/recent` |
| separator | — | — | — | — |
| — | User Menu | avatar | Alt+U | dropdown |

### 2.3 Behavior

- **Active state**: Highlighted background, bold text, accent color indicator bar
- **Hover state**: Light background highlight
- **Focus state**: Visible focus ring (2px solid accent color, 2px offset)
- **Badge indicators**: Unread notification count on relevant items
- **Collapse**: Double-click separator or click collapse button; becomes icon-only rail
- **Expand**: Click expand button or hover collapsed rail (configurable)
- **Keyboard**: Arrow Up/Down to navigate items, Enter/Space to activate, Home/End for first/last

### 2.4 Role-Based Visibility

| Item | Student | Instructor | Admin | Inst. Manager | Plugin Dev | Operator |
|---|---|---|---|---|---|---|
| Dashboard | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Courses | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Simulations | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Assessments | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Reports | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Settings | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Help | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Favorites | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Recent | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Note:** Items above are visible to all authenticated users. The content within
each item varies by role. Admin-only items appear as additional primary nav
entries when the user has the Administrator role.

### 2.5 Admin-Only Primary Nav Items

| Position | Label | Icon | Shortcut | Route |
|---|---|---|---|---|
| 8 | Administration | users | Alt+8 | `/admin` |
| 9 | Plugins | puzzle | Alt+9 | `/plugins` |
| 10 | Diagnostics | activity | Alt+0 | `/diagnostics` |

These items are inserted between Reports and Settings when the user has the
Administrator or Institution Manager role.

---

## 3. Secondary Navigation (Contextual Sidebar)

Each primary section has a secondary navigation sidebar that provides sub-section
navigation. The secondary nav appears to the right of the primary rail.

### 3.1 Dashboard Secondary Nav

| Item | Route | Description |
|---|---|---|
| Overview | `/dashboard/overview` | Default widget layout |
| Activity | `/dashboard/activity` | Activity feed |
| Quick Actions | `/dashboard/actions` | Shortcut tiles |
| Progress | `/dashboard/progress` | Learning progress |
| System Status | `/dashboard/status` | Online/offline, sync |

### 3.2 Courses Secondary Nav

| Item | Route | Description |
|---|---|---|
| Browse | `/courses/browse` | Course catalog |
| Enrolled | `/courses/enrolled` | My enrolled courses |
| Completed | `/courses/completed` | Finished courses |
| Bookmarks | `/courses/bookmarks` | Saved courses |
| Categories | `/courses/categories` | Browse by category |
| Instructors | `/courses/instructors` | Browse by instructor |

### 3.3 Simulations Secondary Nav

| Item | Route | Description |
|---|---|---|
| Browse | `/simulations/browse` | All scenarios |
| My History | `/simulations/history` | Past attempts |
| Bookmarks | `/simulations/bookmarks` | Saved scenarios |
| Difficulty | `/simulations/difficulty` | Filter by difficulty |
| Categories | `/simulations/categories` | Filter by category |

### 3.4 Assessments Secondary Nav

| Item | Route | Description |
|---|---|---|
| Browse | `/assessments/browse` | All assessments |
| Available | `/assessments/available` | Upcoming/active |
| Completed | `/assessments/completed` | Past submissions |
| Results | `/assessments/results` | Score history |
| Bookmarks | `/assessments/bookmarks` | Saved assessments |

### 3.5 Reports Secondary Nav

| Item | Route | Description |
|---|---|---|
| Dashboard | `/reports/dashboard` | Report overview |
| Create | `/reports/create` | Report builder |
| My Reports | `/reports/mine` | User's reports |
| Scheduled | `/reports/scheduled` | Recurring reports |
| Templates | `/reports/templates` | Report templates |
| Export History | `/reports/exports` | Export log |

### 3.6 Settings Secondary Nav

| Item | Route | Description |
|---|---|---|
| General | `/settings/general` | App behavior |
| Appearance | `/settings/appearance` | Theme and visuals |
| Accessibility | `/settings/accessibility` | A11y preferences |
| Localization | `/settings/localization` | Language and region |
| Security | `/settings/security` | Auth and sessions |
| Privacy | `/settings/privacy` | Data handling |
| Notifications | `/settings/notifications` | Alert preferences |
| Storage | `/settings/storage` | Cache and data |
| Backup | `/settings/backup` | Backup configuration |
| Learning | `/settings/learning` | Learning prefs |
| Diagnostics | `/settings/diagnostics` | Logging and reporting |
| Advanced | `/settings/advanced` | Developer options |

### 3.7 Help Secondary Nav

| Item | Route | Description |
|---|---|---|
| Help Center | `/help/center` | Documentation hub |
| Tutorials | `/help/tutorials` | Interactive guides |
| Shortcuts | `/help/shortcuts` | Keyboard reference |
| Troubleshooting | `/help/troubleshooting` | Common issues |
| FAQ | `/help/faq` | Frequently asked |
| About | `/help/about` | Version and credits |

### 3.8 Administration Secondary Nav (Admin Only)

| Item | Route | Description |
|---|---|---|
| Overview | `/admin/overview` | Admin dashboard |
| Users | `/admin/users` | User management |
| Roles | `/admin/roles` | Role management |
| Organizations | `/admin/organizations` | Org hierarchy |
| Audit Log | `/admin/audit` | Activity audit |
| Institution | `/admin/institution` | Institution settings |
| Policies | `/admin/policies` | Access policies |

### 3.9 Plugins Secondary Nav (Admin/Developer)

| Item | Route | Description |
|---|---|---|
| Installed | `/plugins/installed` | Installed plugins |
| Browse | `/plugins/browse` | Available plugins |
| Updates | `/plugins/updates` | Available updates |
| Developer | `/plugins/developer` | SDK and tools |
| Logs | `/plugins/logs` | Plugin logs |
| Settings | `/plugins/settings` | Plugin config |

### 3.10 Diagnostics Secondary Nav (Admin/Operator)

| Item | Route | Description |
|---|---|---|
| System Health | `/diagnostics/health` | Component status |
| Logs | `/diagnostics/logs` | Application logs |
| Performance | `/diagnostics/performance` | Resource usage |
| Network | `/diagnostics/network` | Connectivity status |
| Database | `/diagnostics/database` | DB integrity |
| Crash Reports | `/diagnostics/crashes` | Error reports |

---

## 4. Breadcrumbs

### 4.1 Format

```
Home > Module > Section > Page
```

### 4.2 Rules

- Maximum 4 levels displayed
- All segments are clickable links
- Current page is non-clickable, bold text
- Separator: `>` with `aria-hidden="true"`
- Overflow: truncate leftmost items with `...` ellipsis
- Keyboard: Tab to enter breadcrumb, Arrow Left/Right to navigate segments

### 4.3 Examples

```
Home > Courses > Network Security 101 > Lesson 3
Home > Assessments > Midterm Exam > Results
Home > Settings > Accessibility > Keyboard
Home > Administration > Users > john.doe@example.com
```

### 4.4 Screen Reader Announcement

```html
<nav aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a> <span aria-hidden="true">></span></li>
    <li><a href="/courses">Courses</a> <span aria-hidden="true">></span></li>
    <li><span aria-current="page">Network Security 101</span></li>
  </ol>
</nav>
```

---

## 5. Workspace Tabs

Multi-document workspace tabs allow users to have multiple screens open simultaneously.

### 5.1 Tab Bar

```
┌─────────────────────────────────────────────────────┐
│ [Dashboard] [Course: NetSec 101] [Assessment] [+]   │
└─────────────────────────────────────────────────────┘
```

### 5.2 Rules

- Maximum 10 tabs open simultaneously
- New tab opens via Ctrl+T or middle-click on link
- Close tab via Ctrl+W or click X button
- Tab overflow: scrollable with arrows
- Active tab: bold label, accent color bottom border
- Modified indicator: dot before label if unsaved changes
- Keyboard: Ctrl+Tab next, Ctrl+Shift+Tab previous, Ctrl+1-9 jump to tab

### 5.3 Tab Context Menu

- Close Tab
- Close Other Tabs
- Close Tabs to the Right
- Close All Tabs
- Duplicate Tab
- Move Tab to New Window

---

## 6. Quick Actions

### 6.1 Floating Action Button (FAB)

- Position: Bottom-right corner
- Default action: Context-dependent (e.g., "New Course" in Courses)
- Expand: Click to reveal additional quick actions
- Keyboard: Alt+Q to focus, Enter to expand, Arrow keys to select
- Accessibility: aria-label="Quick actions", expanded state announced

### 6.2 Toolbar Actions

- Position: Top of content area, below breadcrumbs
- Actions: Context-dependent per screen
- Layout: Icon buttons with labels (on hover or always if configured)
- Overflow: `...` menu for additional actions
- Keyboard: Tab to reach toolbar, Arrow keys between buttons

---

## 7. Favorites System

### 7.1 Favoriting

- Star icon on any content item (course, simulation, assessment, report, settings page)
- Click star to toggle favorite
- Keyboard: Alt+S to toggle favorite on focused item
- Visual: Filled star = favorited, outline = not favorited

### 7.2 Favorites Panel

- Accessible via primary nav "Favorites" or Alt+F
- Groups favorites by module
- Sortable: by date added, name, module
- Drag to reorder within groups
- Quick remove: star icon on each item
- Keyboard: Arrow keys to navigate, Enter to open, Delete to remove

### 7.3 Persistence

- Favorites stored in local database
- Synced across devices (when online)
- Maximum 100 favorites

---

## 8. Recent Items

### 8.1 Tracking

- Last 10 unique screens visited
- Excludes: splash, login, settings pages
- Updated on screen mount (not on every render)
- Stored with timestamp and screen metadata

### 8.2 Recent Panel

- Accessible via primary nav "Recent" or Alt+R
- Chronological list with timestamps
- Click to navigate back
- Clear all option
- Keyboard: Arrow keys, Enter to open, Delete to remove

### 8.3 Dashboard Widget

- "Recent Activity" widget on dashboard shows last 5 items
- Compact view with icons and titles

---

## 9. History Navigation

### 9.1 Back/Forward

- Browser-like history stack
- Back: Alt+Left or mouse back button
- Forward: Alt+Right or mouse forward button
- History: Alt+H for history panel

### 9.2 History Panel

- Full navigation history with timestamps
- Searchable
- Filterable by module
- Grouped by date
- Click to revisit any point

---

## 10. Workspace Switcher

### 10.1 Purpose

Allows users with multiple roles to switch between role-specific views.

### 10.2 Implementation

- Located in user menu dropdown
- Available roles based on user's assigned roles
- Switching reconfigures primary nav, dashboard, and available features
- Current view indicated in role badge

### 10.3 Views

| View | Default Landing | Nav Configuration |
|---|---|---|
| Student View | Student Dashboard | Student nav items |
| Instructor View | Instructor Dashboard | Instructor + admin-lite nav items |
| Admin View | Admin Dashboard | Full admin nav items |
| Developer View | Plugin Manager | Developer-focused nav items |

### 10.4 Keyboard

- Alt+V to open workspace switcher
- Arrow keys to select view
- Enter to switch
- Escape to close

---

## 11. Notification Center

### 11.1 Access

- Bell icon in top-right header
- Badge counter for unread notifications
- Keyboard: Alt+N to open

### 11.2 Panel Layout

```
┌─────────────────────────────┐
│  Notifications    [Mark All] │
│  ─────────────────────────  │
│  🔵 New course published    │
│  🟡 Assessment due tomorrow │
│  🟢 Backup complete         │
│  🔴 Login attempt blocked   │
│  ─────────────────────────  │
│  [View All] [Settings]      │
└─────────────────────────────┘
```

### 11.3 Behavior

- Panel slides in from right
- Maximum 20 items displayed
- Scroll for more
- Click notification to navigate to relevant screen
- Dismiss individual notifications
- Mark all as read
- Keyboard: Arrow keys to navigate, Enter to open, Delete to dismiss

---

## 12. Global Search & Command Palette

### 12.1 Search Bar

- Position: Top header, center
- Placeholder: "Search... (Ctrl+K)"
- Keyboard: Ctrl+K or / to focus
- Opens dropdown with recent searches and suggestions
- Results update as user types

### 12.2 Command Palette

- Triggered by Ctrl+K (when search bar not focused) or Ctrl+Shift+P
- Full-screen modal overlay
- Single input field with fuzzy search
- Results grouped by category (Screens, Actions, Settings, Help)
- Arrow keys to navigate results
- Enter to execute selected action
- Escape to close

### 12.3 Search Result Format

```
[Icon] Title                    Module Badge
      Description text (truncated)
      Breadcrumb path
```

### 12.4 Keyboard Shortcuts Reference

| Action | Shortcut |
|---|---|
| Open search | Ctrl+K or / |
| Open command palette | Ctrl+Shift+P |
| Navigate results | Arrow Up/Down |
| Select result | Enter |
| Close | Escape |
| Search in module | Ctrl+Shift+F |

---

## 13. Context Menus

### 13.1 Trigger

- Right-click on any item
- Application key (Windows) or Shift+F10
- Long-press on touch (configurable)

### 13.2 Context Menu Items (Vary by Element)

**On Course Card:**
- Open
- Enroll / Start
- Add to Favorites
- Share
- View Analytics (Instructor)
- Delete (Admin)

**On Assessment Card:**
- Open
- Take Assessment
- View Results
- Add to Favorites
- Delete (Admin)

**On User Row:**
- View Profile
- Edit
- Change Role
- Deactivate
- View Audit History

**On Empty Area:**
- Refresh
- Select All
- Paste (if applicable)
- View Settings

### 13.3 Context Menu Behavior

- Maximum 8 items visible
- Sub-menus with arrow indicator
- Separators between groups
- Destructive items at bottom, red text
- Keyboard: Arrow Up/Down to navigate, Right for sub-menu, Enter to activate
- Escape or click outside to close

---

## 14. Navigation Drawer (Compact Mode)

### 14.1 Trigger

- Window width below 768px
- Manual toggle button
- Configurable auto-collapse threshold

### 14.2 Behavior

- Primary nav collapses to icon-only rail
- Secondary nav becomes slide-out drawer
- Content area expands to fill space
- Drawer opens on hamburger click or swipe gesture
- Drawer closes on item select, outside click, or Escape

---

## 15. Global Keyboard Shortcuts

### 15.1 Navigation Shortcuts

| Shortcut | Action |
|---|---|
| Alt+1-7 | Jump to primary nav items |
| Alt+8-0 | Jump to admin nav items |
| Alt+F | Favorites panel |
| Alt+R | Recent items panel |
| Alt+N | Notification center |
| Alt+V | Workspace switcher |
| Alt+Q | Quick actions |
| Alt+S | Toggle favorite |
| Alt+Left | Navigate back |
| Alt+Right | Navigate forward |
| Alt+H | History panel |
| Ctrl+K | Command palette / Search |
| Ctrl+Shift+P | Command palette |
| Ctrl+T | New tab |
| Ctrl+W | Close current tab |
| Ctrl+Tab | Next tab |
| Ctrl+Shift+Tab | Previous tab |
| Ctrl+1-9 | Jump to tab by position |
| Ctrl+/ | Keyboard shortcuts reference |
| F1 | Help center |
| Ctrl+, | Settings |
| Escape | Close overlay / go back |
| ? | Show keyboard shortcuts (when not in input) |

### 15.2 Tab Focus Order

1. Skip link (hidden until focus)
2. Primary navigation rail
3. Secondary navigation sidebar
4. Breadcrumbs
5. Content area
6. Toolbar actions
7. Footer actions

---

## 16. Navigation State Management (Zustand)

### 16.1 Navigation Store

```typescript
interface NavigationState {
  currentScreen: string;
  previousScreen: string | null;
  history: string[];
  historyIndex: number;
  openTabs: Tab[];
  activeTabId: string;
  favorites: FavoriteItem[];
  recentItems: RecentItem[];
  secondaryNavOpen: boolean;
  commandPaletteOpen: boolean;
  searchQuery: string;
  searchResults: SearchResult[];
}
```

### 16.2 Actions

- `navigateTo(screen, params?)` — Push to history, update active screen
- `goBack()` — Navigate to previous screen in history
- `goForward()` — Navigate to next screen in history
- `openTab(screen, title)` — Create or focus tab
- `closeTab(tabId)` — Close tab, focus adjacent
- `toggleFavorite(item)` — Add/remove from favorites
- `addToRecent(item)` — Add to recent items list
- `openCommandPalette()` — Show command palette overlay
- `search(query)` — Execute global search
- `switchWorkspace(role)` — Switch role-based view
