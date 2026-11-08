# AuthShield Lab — Enterprise Search Architecture

## 1. Overview

This document defines the complete search system for AuthShield Lab. The search
architecture supports global search across all modules, module-specific search,
settings search, documentation search, and plugin search. All search features
are keyboard-first and fully accessible.

---

## 2. Search Types

### 2.1 Global Search

**Scope:** All modules and content across the application

**Triggers:**
- Ctrl+K or / (when not in text input)
- Click on search bar in header
- Command Palette (Ctrl+Shift+P)

**Indexed Content:**
| Content Type | Fields Indexed | Module |
|---|---|---|
| Courses | title, description, tags, instructor name | Courses |
| Lessons | title, content summary | Learning |
| Simulations | title, description, objectives | Simulations |
| Assessments | title, description, questions preview | Assessments |
| Reports | title, type, date generated | Reports |
| Certificates | title, course name, issue date | Certificates |
| Users | name, email, role | Administration |
| Settings | label, description, category | Settings |
| Help articles | title, content, tags | Help |
| Plugins | name, description, author | Plugins |
| Audit logs | action, user, timestamp | Administration |

**Search Behavior:**
- Fuzzy matching with tolerance for typos
- Minimum 2 characters to trigger search
- Results update in real-time as user types
- Maximum 50 results displayed
- Results grouped by module/category
- Most relevant results first (weighted by type and recency)

### 2.2 Module Search

**Scope:** Current active module only

**Triggers:**
- Ctrl+Shift+F (when in a module)
- Search icon within module secondary nav
- Magnifying glass on module-specific screens

**Examples:**
- In Courses: Search by course title, tag, or instructor
- In Simulations: Search by scenario name or difficulty
- In Assessments: Search by assessment title or type
- In Administration: Search by user name or email
- In Plugins: Search by plugin name or author

### 2.3 Settings Search

**Scope:** All settings categories and individual settings

**Triggers:**
- Search bar at top of Settings screen
- Ctrl+K while in Settings

**Searchable Fields:**
- Setting label
- Setting description
- Setting category name
- Setting keywords (synonyms)

**Examples:**
- "theme" → Appearance settings
- "password" → Security settings, Password policy
- "font size" → Appearance > Font size
- "backup" → Backup settings
- "screen reader" → Accessibility settings

### 2.4 Documentation Search

**Scope:** All help articles, tutorials, and guides

**Triggers:**
- Search bar in Help Center
- F1 then type in search

**Searchable Fields:**
- Article title
- Article content (full-text)
- Article tags
- Tutorial steps
- FAQ questions and answers

### 2.5 Plugin Search

**Scope:** Installed plugins and available plugins

**Triggers:**
- Search bar in Plugin Manager
- Ctrl+K with "plugin:" prefix

**Searchable Fields:**
- Plugin name
- Plugin description
- Plugin author
- Plugin tags
- Plugin changelog

---

## 3. Search Result Display

### 3.1 Result Item Format

```
┌─────────────────────────────────────────────────────┐
│  📄  Course: Network Security Fundamentals          │
│      Learn the basics of network security...         │
│      Courses > Network Security > Beginner           │
│                                          [Course] 🔵 │
└─────────────────────────────────────────────────────┘
```

### 3.2 Result Components

| Component | Description | Accessibility |
|---|---|---|
| Icon | Content type indicator | aria-hidden="true" |
| Title | Primary text, bold, highlighted match | Screen reader reads full title |
| Description | Secondary text, truncated | Screen reader reads truncated |
| Breadcrumb | Location path | Screen reader reads as path |
| Module Badge | Category indicator with color | Text label, not color-only |
| Relevance Score | Hidden, used for ordering | Not exposed to users |

### 3.3 Result Grouping

```
Screens (3 results)
  ├── Dashboard
  ├── Course Browser
  └── Settings

Actions (2 results)
  ├── Create New Course
  └── Generate Report

Help Articles (4 results)
  ├── Getting Started Guide
  ├── Keyboard Shortcuts
  ├── Course Enrollment
  └── Assessment Tips

Settings (2 results)
  ├── Appearance > Theme
  └── Accessibility > High Contrast
```

### 3.4 No Results State

```
┌─────────────────────────────────────────────┐
│                                              │
│  No results found for "xyznonexistent"       │
│                                              │
│  Suggestions:                                │
│  • Check your spelling                       │
│  • Try more general terms                    │
│  • Browse categories instead                 │
│                                              │
│  [Browse Courses] [Browse Simulations]       │
└─────────────────────────────────────────────┘
```

---

## 4. Search Filters

### 4.1 Filter Panel

```
┌─────────────────────────────────────────────┐
│  Search: "network security"                  │
│                                              │
│  Filters:                                    │
│  ┌─────────────────────────────────────┐    │
│  │ Type      [All ▼]                   │    │
│  │ Module    [All ▼]                   │    │
│  │ Date      [Any time ▼]             │    │
│  │ Status    [All ▼]                   │    │
│  │ [Apply Filters]    [Clear All]       │    │
│  └─────────────────────────────────────┘    │
│                                              │
│  Results (12):                               │
│  [Results list...]                           │
└─────────────────────────────────────────────┘
```

### 4.2 Filter Options

| Filter | Options | Description |
|---|---|---|
| Type | Course, Lesson, Simulation, Assessment, Report, Certificate, User, Setting, Help Article, Plugin | Content type |
| Module | Dashboard, Courses, Learning, Simulations, Assessments, Reports, Certificates, Analytics, Settings, Plugins, Help, Administration | Source module |
| Date | Any time, Today, This week, This month, This year, Custom range | Recency |
| Status | All, Active, Archived, Draft, Published | Content status |
| Owner | Me, Specific user, Any | Content owner |

### 4.3 Active Filter Display

```
┌─────────────────────────────────────────────┐
│  Active Filters:                             │
│  [Type: Course ✕] [Module: Courses ✕]       │
│  [Clear All]                                 │
└─────────────────────────────────────────────┘
```

### 4.4 Filter Keyboard Navigation

- Tab to reach filter panel
- Arrow keys to navigate filters
- Enter/Space to open dropdown
- Arrow keys within dropdown
- Enter to select option
- Escape to close dropdown
- Tab to "Apply" or "Clear"

---

## 5. Search Sorting

### 5.1 Sort Options

| Sort | Description | Default |
|---|---|---|
| Relevance | Weighted by match quality and type | ✓ (default) |
| Date (newest) | Most recent first | |
| Date (oldest) | Oldest first | |
| Name (A-Z) | Alphabetical ascending | |
| Name (Z-A) | Alphabetical descending | |
| Most accessed | Most frequently viewed | |

### 5.2 Sort Controls

```
┌─────────────────────────────────────────────┐
│  Results (12)    Sort: [Relevance ▼]         │
└─────────────────────────────────────────────┘
```

### 5.3 Keyboard

- Tab to sort dropdown
- Enter to open
- Arrow keys to navigate options
- Enter to select
- Escape to close

---

## 6. Recent Searches

### 6.1 Storage

- Last 10 search queries stored per user
- Stored in local database (IndexedDB)
- Persists across sessions

### 6.2 Display

```
┌─────────────────────────────────────────────┐
│  Recent Searches                             │
│  🕐 network security                        │
│  🕐 phishing simulation                     │
│  🕐 keyboard shortcuts                      │
│  🕐 backup settings                         │
│  🕐 certificate verify                      │
│                                              │
│  [Clear History]                             │
└─────────────────────────────────────────────┘
```

### 6.3 Behavior

- Show recent searches when search bar focused (before typing)
- Click recent search to execute it
- New searches added to top of list
- Duplicates moved to top
- Maximum 10 entries

---

## 7. Saved Searches

### 7.1 Create Saved Search

```
After executing a search:
  → Click "Save Search" button
  → Name dialog appears
  → User enters name: "Beginner Network Courses"
  → Search saved with query and filters
```

### 7.2 Access Saved Searches

```
┌─────────────────────────────────────────────┐
│  Saved Searches                              │
│  ⭐ Beginner Network Courses                 │
│  ⭐ Active Assessments Due                   │
│  ⭐ Recent Plugin Updates                    │
│  ⭐ Unread Notifications                     │
│                                              │
│  [Manage Saved Searches]                     │
└─────────────────────────────────────────────┘
```

### 7.3 Management

- Rename saved search
- Delete saved search
- Reorder via drag-and-drop
- Maximum 20 saved searches
- Share saved search link (for instructors)

---

## 8. Search Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+K or / | Open global search |
| Ctrl+Shift+F | Open module search |
| Ctrl+K then type "plugin:" | Search plugins |
| Ctrl+K then type "setting:" | Search settings |
| Ctrl+K then type "help:" | Search help docs |
| Arrow Up/Down | Navigate results |
| Enter | Select result |
| Escape | Close search |
| Tab | Move to filters |
| Ctrl+S (in search) | Save current search |

---

## 9. Search Accessibility

### 9.1 ARIA Attributes

```html
<div role="search" aria-label="Global search">
  <input
    type="search"
    aria-label="Search courses, simulations, assessments, and more"
    aria-autocomplete="list"
    aria-controls="search-results"
    aria-expanded="true"
    aria-activedescendant="result-3"
  />
  <ul id="search-results" role="listbox" aria-label="Search results">
    <li id="result-1" role="option" aria-selected="false">
      Course: Network Security Fundamentals
    </li>
    <li id="result-2" role="option" aria-selected="false">
      Simulation: Phishing Analysis
    </li>
    <li id="result-3" role="option" aria-selected="true">
      Assessment: Network Basics Quiz
    </li>
  </ul>
</div>
```

### 9.2 Live Announcements

| Event | Announcement |
|---|---|
| Results loaded | "X results found" |
| No results | "No results found" |
| Filter applied | "Showing X results" |
| Results cleared | "Search cleared" |
| Result selected | Read full result text |

### 9.3 Keyboard Focus Management

- Search input receives focus when opened
- Arrow keys move through results (aria-activedescendant)
- Tab moves to filter panel
- Enter selects highlighted result
- Escape closes search, returns focus to previous element

### 9.4 Visual Accessibility

- Search input has 4.5:1 contrast ratio minimum
- Focus ring visible on search input and results
- Results text meets WCAG AA contrast requirements
- Icons have text alternatives
- Filter labels always visible (not placeholder-only)
- High contrast mode supported

---

## 10. Search Performance

### 10.1 Indexing

- Content indexed on application start
- Re-indexed on content change (debounced 2 seconds)
- Incremental indexing for large datasets
- Index stored in memory for fast access
- Fallback to database query if index unavailable

### 10.2 Response Time

| Dataset Size | Target Response Time |
|---|---|
| < 100 items | < 50ms |
| 100 - 1,000 items | < 100ms |
| 1,000 - 10,000 items | < 200ms |
| > 10,000 items | < 500ms |

### 10.3 Offline Search

- All search works offline
- No network required
- Index rebuilt from local database
- Search quality equivalent to online

---

## 11. Search Integration Points

| Screen | Search Type | Keyboard |
|---|---|---|
| Any screen | Global search | Ctrl+K |
| Course Browser | Module search | / or Ctrl+Shift+F |
| Simulation Browser | Module search | / or Ctrl+Shift+F |
| Assessment Browser | Module search | / or Ctrl+Shift+F |
| Settings | Settings search | / or Ctrl+K |
| Help Center | Documentation search | / |
| Plugin Manager | Plugin search | / |
| Administration | User search | / or Ctrl+Shift+F |
| Report Builder | Data search | / |
| Command Palette | All actions | Ctrl+Shift+P |

---

## 12. Search Analytics

### 12.1 Tracked Metrics (Local Only)

| Metric | Purpose |
|---|---|
| Search queries | Identify common search terms |
| Result clicks | Measure search relevance |
| Zero-result queries | Identify content gaps |
| Filter usage | Understand search patterns |
| Time to first click | Measure search efficiency |

### 12.2 Analytics Privacy

- All analytics stored locally
- No data sent to external servers
- User can clear search analytics
- Analytics disabled in high-privacy mode
