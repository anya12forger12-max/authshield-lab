# AuthShield Lab — Loading and Empty States

> Version: 1.0.0
> Last Updated: 2026-07-19
> Status: Active

---

## Table of Contents

1. [Loading Indicators](#1-loading-indicators)
2. [Skeleton Screen Patterns](#2-skeleton-screen-patterns)
3. [Empty States](#3-empty-states)
4. [Error States](#4-error-states)
5. [Offline Messages](#5-offline-messages)
6. [Plugin Errors](#6-plugin-errors)
7. [Missing Resources](#7-missing-resources)
8. [Recovery Actions](#8-recovery-actions)

---

## 1. Loading Indicators

### 1.1 Spinner (Small Tasks)

**Use for:** Operations under 2 seconds (button clicks, form submissions, toggles).

```
        +-----+
        |     |
        |  ◌  |   24x24px spinner
        |     |
        +-----+
        
  Inline variant:
  [Save] [◌ Saving...]
```

**Behavior:**
- Appears immediately (no delay for < 200ms operations)
- For operations 200ms-2s: show spinner + label text
- For operations > 2s: transition to progress bar
- Color: matches current theme accent

**Component:**

```tsx
<Spinner size="sm" />          // 16x16px - inline
<Spinner size="md" />          // 24x24px - default
<Spinner size="lg" />          // 40x40px - standalone
<Spinner label="Saving..." />  // with text
```

**Accessibility:**
- `role="status"`, `aria-label="Loading"`
- `aria-live="polite"` for status text
- Hidden from screen readers by default (decorative)

---

### 1.2 Progress Bar (Known Duration)

**Use for:** Operations with known or estimable duration (file operations, imports, backups).

```
Standard:
+--[300px]--[8px]--+
| [|||||||||||....] |  65%
+------------------+

With label:
Loading courses...
+--[300px]--[8px]--+
| [|||||||||||....] |  65% (78 of 120 courses)
+------------------+

Indeterminate (unknown duration):
+--[300px]--[8px]--+
| [|||||||||||||||] |  ← animated sliding fill
+------------------+
```

**Behavior:**
- Shows immediately for determinate progress
- Indeterminate: sliding animation for unknown duration
- Percentage updates at minimum every 5% or 500ms (whichever is more frequent)
- At 100%: brief pause (300ms) before transition

**Component:**

```tsx
<ProgressBar value={65} max={100} label="Loading courses..." />
<ProgressBar value={null} /> // indeterminate
```

**Accessibility:**
- `role="progressbar"`, `aria-valuenow="65"`, `aria-valuemin="0"`, `aria-valuemax="100"`
- `aria-label="Loading courses: 65%"`
- `aria-live="polite"` for value updates (debounced to every 10% or 1 second)
- Indeterminate: `aria-valuetext="Loading"`

---

### 1.3 Skeleton Screens (Content Loading)

**Use for:** Content areas loading from local storage (course lists, dashboards, profiles).

```
Course Card Skeleton:
+--[480px]--[280px]--+
| [████████████████] |  140px - shimmer
| [████████████████] |
|                    |
| [████████]         |  title line
| [██████]           |  subtitle line
|                    |
| [============....] |  progress bar
+--------------------+
  Shimmer animation: left-to-right gradient sweep
  1.5s duration, infinite loop
  Background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)
```

**Behavior:**
- Shows immediately when content is loading
- Matches the layout of actual content (1:1 shape)
- Shimmer animation provides visual feedback
- Replaced by real content as it loads (crossfade 200ms)

---

### 1.4 Indeterminate (Unknown Duration)

**Use for:** Operations with no known endpoint (searching, connecting, syncing).

```
Dots variant:
[● ○ ○] Searching...

Bar variant:
+--[200px]--[4px]--+
| [━━━━━━━━━━━━━]  |  ← animated bar
+------------------+

Ring variant:
    ╭───╮
   ╱  ●  ╲   40x40px rotating ring
   ╲     ╱
    ╰───╯
```

**Accessibility:**
- `role="status"`, `aria-label="Searching"`
- `aria-live="polite"` for associated text

---

## 2. Skeleton Screen Patterns

### 2.1 List Skeleton (Course List, Activity Feed)

```
+--[100%]--[auto]---+
| [████] [████████] |  16px height lines
| [████] [████████] |  varied widths (60-80%)
| [████] [████████] |
|                    |  16px gap between items
| [████] [████████] |
| [████] [████████] |
| [████] [████████] |
+--------------------+
  6-8 items shown (matches visible area)
  Shimmer offset per row for natural appearance
  Heights: 16px (title), 12px (subtitle), 24px (avatar)
```

### 2.2 Grid Skeleton (Course Cards, Certificate Gallery)

```
+--[480px]--+ +--[480px]--+ +--[480px]--+
| [████████] | | [████████] | | [████████] |  140px image
| [████████] | | [████████] | | [████████] |
|            | |            | |            |
| [████████] | | [████████] | | [████████] |  16px title
| [██████]   | | [██████]   | | [██████]   |  12px subtitle
|            | |            | |            |
| [========] | | [========] | | [========] |  8px progress
+------------+ +------------+ +------------+
  24px gap between cards
  Shimmer: each card starts at different phase
  Cards: 480x280px (matches real cards)
```

### 2.3 Detail Skeleton (Course Detail, Lesson Viewer)

```
+--[100%]--[auto]---+
| [████████████████] |  200px banner
| [████████████████] |
|                    |
| [████████████]     |  24px title
| [████████]         |  16px subtitle
|                    |
| [████] [████] [████] |  32x32px tags
|                    |
| [████████████████] |  16px text line
| [████████████████] |  16px text line
| [████████]         |  16px text line (short)
| [████████████████] |  16px text line
| [████████████]     |  16px text line
|                    |
| +--[module-list]--+ |
| | [████] [████]   | |  40px module rows
| | [████] [████]   | |
| | [████] [████]   | |
| +-----------------+ |
+--------------------+
```

### 2.4 Form Skeleton (Settings, Profile)

```
+--[100%]--[auto]---+
| [████████]         |  20px section title
|                    |
| [████████████]     |  14px label
| [████████████████] |  40px input field
|                    |
| [████████████]     |  14px label
| [████████████████] |  40px input field
|                    |
| [████████]         |  14px label
| ( ) [████] ( ) [██] |  radio group
|                    |
| +--button-skeleton] |
| | [██████] [██████] |  40px buttons
| +------------------+ |
+--------------------+
```

### 2.5 Table Skeleton (Reports, Analytics)

```
+--[100%]--[auto]---+
| [████] | [████████] | [████] | [████████] |  header
|--------|------------|--------|------------|
| [███]  | [████████] | [███]  | [████████] |  row 1
| [███]  | [████████] | [███]  | [████████] |  row 2
| [███]  | [████████] | [███]  | [████████] |  row 3
| [███]  | [████████] | [███]  | [████████] |  row 4
| [███]  | [████████] | [███]  | [████████] |  row 5
| [███]  | [████████] | [███]  | [████████] |  row 6
| [███]  | [████████] | [███]  | [████████] |  row 7
| [███]  | [████████] | [███]  | [████████] |  row 8
+--------------------+
  8 rows visible (matches typical viewport)
  Column widths match actual table layout
```

---

## 3. Empty States

### 3.1 Empty Table

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [icon]    |   |  64x64px illustration
|    |  (gray)   |   |
|    +-----------+   |
|                    |
|  No data available |
|                    |
|  There are no items|  14px body text
|  to display in     |
|  this table yet.   |
|                    |
|  [Action Button]   |  primary CTA
|                    |
+--------------------+
```

**Text Content:**
- Title: "No data available"
- Description: "There are no items to display in this table yet."
- Action: Context-dependent ("Import Data", "Create First Item", etc.)

**Accessibility:**
- Container: `role="status"`, `aria-label="No data available"`
- Icon: `aria-hidden="true"`
- Action button: standard focus management

---

### 3.2 No Search Results

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [🔍]      |   |  64x64px search icon
|    +-----------+   |
|                    |
| No results found   |  18px heading
|                    |
| No courses match   |  14px body
| "xyz123".          |
|                    |
| Suggestions:       |
| * Check your       |
|   spelling         |
| * Try more general |
|   keywords         |
| * Clear filters    |
|                    |
| [Clear Filters]    |  secondary button
| [Browse All]       |  primary button
|                    |
+--------------------+
```

**Text Content:**
- Title: "No results found"
- Description: "No courses match \"{query}\"."
- Suggestions: bulleted list of helpful actions
- Actions: "Clear Filters" + "Browse All"

**Accessibility:**
- `role="status"`, `aria-label="No search results for {query}"`
- Suggestions: `<ul>` list
- Both buttons accessible

---

### 3.3 No Courses Enrolled

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [📚]      |   |  80x80px book illustration
|    | (illustr) |   |
|    +-----------+   |
|                    |
| Start Learning!    |  20px heading
|                    |
| You haven't        |  14px body
| enrolled in any    |
| courses yet.       |
| Browse our catalog |
| to find courses    |
| that interest you. |
|                    |
| +--[240px]--[44px]+|
| | Browse Catalog   |  primary CTA
| +-----------------+|
|                    |
| [Take a Tour]      |  tertiary link
|                    |
+--------------------+
```

**Text Content:**
- Title: "Start Learning!"
- Description: Multi-line invitation to browse catalog
- CTA: "Browse Catalog" → Course Catalog
- Secondary: "Take a Tour" → guided tour

**Accessibility:**
- `role="region"`, `aria-label="No enrolled courses"`
- Illustration: `aria-hidden="true"`
- CTA auto-focused when screen loads

---

### 3.4 No Plugins Installed

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [🔌]      |   |  80x80px plug illustration
|    +-----------+   |
|                    |
| Enhance Your       |  20px heading
| Experience         |
|                    |
| No plugins are     |  14px body
| installed yet.     |
| Plugins add new    |
| simulation types,  |
| assessment tools,  |
| and integrations.  |
|                    |
| +--[200px]--[44px]+|
| | Browse Plugins   |  primary CTA
| +-----------------+|
|                    |
| [Learn About       |  tertiary link
|  Plugins]          |
|                    |
+--------------------+
```

---

### 3.5 No Backups

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [💾]      |   |  80x80px floppy illustration
|    +-----------+   |
|                    |
| Protect Your Data  |  20px heading
|                    |
| You haven't created|  14px body
| any backups yet.   |
| Backups protect    |
| your course data,  |
| settings, and      |
| progress.          |
|                    |
| +--[200px]--[44px]+|
| | Create Backup    |  primary CTA
| +-----------------+|
|                    |
| [Schedule Auto-    |  tertiary link
|  Backup]           |
|                    |
+--------------------+
```

---

### 3.6 No Reports Generated

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [📊]      |   |  80x80px chart illustration
|    +-----------+   |
|                    |
| Generate Reports   |  20px heading
|                    |
| No reports have    |  14px body
| been generated yet.|
| Reports help you   |
| track progress and |
| measure learning   |
| outcomes.          |
|                    |
| +--[200px]--[44px]+|
| | Generate Report  |  primary CTA
| +-----------------+|
|                    |
+--------------------+
```

---

### 3.7 No Activity

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [📋]      |   |  64x64px clipboard illustration
|    +-----------+   |
|                    |
| All Caught Up!     |  18px heading
|                    |
| No recent activity |  14px body
| to display.        |
| Start a course or  |
| take an assessment |
| to see your        |
| activity here.     |
|                    |
+--------------------+
```

**No CTA** — informational only.

---

### 3.8 No Certificates

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [🏆]      |   |  80x80px trophy illustration
|    +-----------+   |
|                    |
| Earn Certificates! |  20px heading
|                    |
| Complete courses to|  14px body
| earn certificates  |
| of completion.     |
| They're stored     |
| here for easy      |
| access.            |
|                    |
| +--[200px]--[44px]+|
| | Browse Courses   |  primary CTA
| +-----------------+|
|                    |
+--------------------+
```

---

## 4. Error States

### 4.1 Connection Error

```
+--[100%]--[auto]---+
|                    |
|  ⚠ Connection Issue|  18px heading, amber
|                    |
|  Unable to verify  |  14px body
|  your license.     |
|  The application   |
|  will continue in  |
|  offline mode with |
|  limited features. |
|                    |
|  Status: Offline   |
|  Last checked:     |
|  2 minutes ago     |
|                    |
|  +--[160px]--[44px]+|
|  | Retry Connection|  primary CTA
|  +-----------------+|
|  | Continue Offline |  secondary
|  +-----------------+|
|                    |
+--------------------+
```

**Text Content:**
- Title: "Connection Issue"
- Description: Explains offline mode and limitations
- Status details: last check time
- Actions: "Retry Connection" + "Continue Offline"

**Accessibility:**
- `role="alert"`, `aria-live="assertive"`
- Error icon: `aria-hidden="true"`
- Focus moves to "Retry Connection"

---

### 4.2 Data Load Error

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [⚠]       |   |  64x64px error icon (red)
|    +-----------+   |
|                    |
|  Failed to Load    |  18px heading
|  Course Data       |
|                    |
|  An error occurred |  14px body
|  while loading the |
|  course content.   |
|  This may be due to|
|  corrupted data or |
|  a missing file.   |
|                    |
|  Error:            |
|  +--[auto]---------+|
|  | COURSE_NOT_FOUND |  monospace, 12px
|  | File: /data/     |  scrollable if long
|  | courses/v2.json  |
|  +-----------------+|
|                    |
|  +--[140px]--[44px]+|
|  | Retry            |  primary
|  +-----------------+|
|  | Go to Dashboard  |  secondary
|  +-----------------+|
|  | Report Issue     |  tertiary
|  +-----------------+|
|                    |
+--------------------+
```

**Accessibility:**
- `role="alert"`, `aria-live="assertive"`
- Error details: collapsible `<details>` for stack trace
- Focus moves to "Retry"

---

### 4.3 Permission Error

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [🔒]       |   |  64x64px lock icon
|    +-----------+   |
|                    |
|  Access Denied     |  18px heading
|                    |
|  You don't have    |  14px body
|  permission to     |
|  access this       |
|  content. This     |
|  feature requires  |
|  an Instructor or  |
|  Administrator     |
|  account.          |
|                    |
|  Current role:     |
|  Student           |
|                    |
|  +--[160px]--[44px]+|
|  | Go Back          |  primary
|  +-----------------+|
|  | Contact Support  |  tertiary
|  +-----------------+|
|                    |
+--------------------+
```

**Accessibility:**
- `role="alert"`, `aria-live="assertive"`
- Role information for context
- Focus moves to "Go Back"

---

### 4.4 Not Found (404)

```
+--[100%]--[auto]---+
|                    |
|         404        |  48px, light gray
|                    |
|    Page Not Found  |  18px heading
|                    |
|  The page you're   |  14px body
|  looking for       |
|  doesn't exist or  |
|  has been moved.   |
|                    |
|  +--[160px]--[44px]+|
|  | Go to Dashboard  |  primary
|  +-----------------+|
|  | Go Back          |  secondary
|  +-----------------+|
|                    |
|  +--[auto]---------+|
|  | [🔍 Search]     |  search input
|  +-----------------+|
|                    |
+--------------------+
```

**Accessibility:**
- `role="status"`, `aria-label="Page not found"`
- "404" as decorative text (aria-hidden)
- Focus moves to "Go to Dashboard"

---

## 5. Offline Messages

### 5.1 Offline Indicator Banner

```
+--[100%]--[48px]---+
| 🟡 Offline Mode   |  16px text, centered
| Changes will sync |  12px subtext
| when reconnected  |
+--------------------+
  Background: #FFFBEB (amber tint)
  Border-bottom: 1px solid #FCD34D
  Height: 48px
  Dismissible: [X] button on right
  Position: below header, above content
  z-index: 95 (below modals, above content)
```

**Behavior:**
- Appears immediately when connection lost
- Persists until reconnected
- Shows sync status: "3 changes pending sync"
- Dismissible (X button) but reappears if still offline

**Accessibility:**
- `role="status"`, `aria-live="polite"`
- Dismiss button: `aria-label="Dismiss offline notification"`
- Reconnection: "Reconnected. Syncing 3 pending changes."

---

### 5.2 Offline Capability Explanation

```
+--[100%]--[auto]---+
|                    |
|  🟡 You're Offline |  18px heading
|                    |
|  AuthShield Lab    |  14px body
|  works offline.    |
|  Here's what you   |
|  can still do:     |
|                    |
|  ✓ View enrolled   |
|    courses         |
|  ✓ Take lessons    |
|  ✓ Run simulations |  (pre-downloaded)
|  ✓ Take assessments|  (pre-downloaded)
|  ✓ View progress   |
|  ✓ View reports    |
|                    |
|  ✗ Browse new      |
|    courses         |
|  ✗ Download new    |
|    content         |
|  ✗ Sync to cloud   |
|  ✓ Check for       |
|    updates (later) |
|                    |
|  +--[160px]--[44px]+|
|  | Continue Offline |  primary
|  +-----------------+|
|                    |
+--------------------+
```

**Accessibility:**
- `role="region"`, `aria-label="Offline capabilities"`
- Check/cross items: `<ul>` with `<li>` containing visual + text
- Focus moves to "Continue Offline"

---

## 6. Plugin Errors

### 6.1 Plugin Failed to Load

```
+--[100%]--[auto]---+
|                    |
|  +--[auto]---------+|
|  | ⚠ Plugin Error  |  amber header
|  +-----------------+|
|                    |
|  The plugin        |  14px body
|  "Network Scanner" |
|  failed to load.   |
|                    |
|  Error: Plugin     |
|  initialization    |
|  timed out after   |
|  5 seconds.        |
|                    |
|  +--[140px]--[44px]+|
|  | Disable Plugin   |  primary
|  +-----------------+|
|  | Retry            |  secondary
|  +-----------------+|
|  | View Details     |  tertiary
|  +-----------------+|
|                    |
+--------------------+
  Inline within Plugin Manager
  Non-blocking: other plugins still functional
```

**Accessibility:**
- `role="alert"`, `aria-live="assertive"`
- Plugin name and error details included
- Focus moves to "Disable Plugin"

---

### 6.2 Plugin Incompatible

```
+--[100%]--[auto]---+
|                    |
|  +--[auto]---------+|
|  | ✖ Incompatible  |  red header
|  +-----------------+|
|                    |
|  The plugin        |  14px body
|  "Old Scanner v1.0"|
|  is not compatible |
|  with this version |
|  of AuthShield Lab.|
|                    |
|  Required: >= 2.3  |
|  Installed: 2.4.1  |
|                    |
|  +--[160px]--[44px]+|
|  | Remove Plugin    |  primary
|  +-----------------+|
|  | Check for Update |  secondary
|  +-----------------+|
|                    |
+--------------------+
```

**Accessibility:**
- `role="alert"`, `aria-live="assertive"`
- Version information clearly displayed
- Focus moves to "Remove Plugin"

---

### 6.3 Plugin Permission Denied

```
+--[100%]--[auto]---+
|                    |
|  +--[auto]---------+|
|  | 🔒 Permission    |  amber header
|  |    Denied        |
|  +-----------------+|
|                    |
|  The plugin        |  14px body
|  "External API"    |
|  requires network  |
|  access permission |
|  which is currently|
|  denied.           |
|                    |
|  You can grant     |
|  this permission   |
|  in the plugin     |
|  settings.         |
|                    |
|  +--[160px]--[44px]+|
|  | Grant Permission |  primary
|  +-----------------+|
|  | Disable Plugin   |  secondary
|  +-----------------+|
|  | Deny             |  tertiary
|  +-----------------+|
|                    |
+--------------------+
```

---

## 7. Missing Resources

### 7.1 File Not Found

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [📄]      |   |  48x48px file icon with X
|    +-----------+   |
|                    |
|  File Not Found    |  18px heading
|                    |
|  The file you're   |  14px body
|  trying to open    |
|  could not be      |
|  found:            |
|                    |
|  +--[auto]---------+|
|  | /home/user/      |  monospace, 12px
|  | documents/       |  scrollable
|  | report.pdf       |
|  +-----------------+|
|                    |
|  The file may have |
|  been moved or     |
|  deleted.          |
|                    |
|  +--[160px]--[44px]+|
|  | Browse for File  |  primary
|  +-----------------+|
|  | Go Back          |  secondary
|  +-----------------+|
|                    |
+--------------------+
```

---

### 7.2 Corrupted Data

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [⚠]       |   |  64x64px warning icon
|    +-----------+   |
|                    |
|  Corrupted Data    |  18px heading
|                    |
|  The data file     |  14px body
|  appears to be     |
|  corrupted or in an|
|  unrecognized      |
|  format.           |
|                    |
|  Affected file:    |
|  settings.json     |  monospace
|                    |
|  You may be able to|
|  fix this by:      |
|                    |
|  1. Restoring from |
|     a backup       |
|  2. Re-downloading |
|     the data       |
|  3. Reinstalling   |
|     the application|
|                    |
|  +--[160px]--[44px]+|
|  | Restore Backup   |  primary
|  +-----------------+|
|  | Reset to Default |  secondary
|  +-----------------+|
|  | Contact Support  |  tertiary
|  +-----------------+|
|                    |
+--------------------+
```

**Accessibility:**
- `role="alert"`, `aria-live="assertive"`
- Affected file: monospace, `aria-label="Affected file: settings.json"`
- Recovery steps: ordered `<ol>` list

---

### 7.3 Expired Session

```
+--[100%]--[auto]---+
|                    |
|    +-----------+   |
|    | [⏰]       |   |  64x64px clock icon
|    +-----------+   |
|                    |
|  Session Expired   |  18px heading
|                    |
|  Your session has  |  14px body
|  expired. Please   |
|  sign in again to  |
|  continue.         |
|                    |
|  Your progress has |
|  been auto-saved.  |
|                    |
|  +--[160px]--[44px]+|
|  | Sign In Again    |  primary
|  +-----------------+|
|                    |
+--------------------+
```

**Accessibility:**
- `role="alert"`, `aria-live="assertive"`
- Reassurance about auto-save included
- Focus moves to "Sign In Again"

---

## 8. Recovery Actions

### 8.1 Retry Button

```
Component:
+--[120px]--[40px]--+
|    ↻ Retry        |
+-------------------+
```

**Behavior:**
- Re-attempts the failed operation
- Shows spinner during retry: "↻ Retrying..."
- Maximum 3 automatic retries before showing error
- Manual retry unlimited
- `aria-label="Retry loading course data"`

---

### 8.2 Go Home Button

```
Component:
+--[140px]--[40px]--+
|    Go to Dashboard |
+-------------------+
```

**Behavior:**
- Navigates to Dashboard
- Clears error state
- `aria-label="Go to Dashboard"`

---

### 8.3 Contact Support Button

```
Component:
+--[160px]--[40px]--+
|  Contact Support   |
+-------------------+
```

**Behavior:**
- Opens Help Center with pre-filled search for error
- Or opens support email in default mail client
- Includes error details in clipboard
- `aria-label="Contact support about this error"`

---

### 8.4 Restore from Backup Button

```
Component:
+--[180px]--[40px]--+
| Restore from Backup |
+--------------------+
```

**Behavior:**
- Opens Backup & Restore screen
- Pre-selects most recent backup
- Shows confirmation dialog before restoring
- `aria-label="Restore application data from backup"`

---

### 8.5 Common Recovery Patterns

| Scenario | Primary Action | Secondary Action | Tertiary Action |
|----------|---------------|------------------|-----------------|
| Network error | Retry Connection | Continue Offline | — |
| Data load error | Retry | Go to Dashboard | Report Issue |
| Permission error | Go Back | Contact Support | — |
| File not found | Browse for File | Go Back | — |
| Corrupted data | Restore Backup | Reset to Default | Contact Support |
| Expired session | Sign In Again | — | — |
| Plugin error | Disable Plugin | Retry | View Details |
| Backup failed | Retry | Choose Different Location | — |
| Import failed | Retry | Choose Different File | — |
| Export failed | Choose Different Location | Retry | — |

---

## 9. Transition Animations

### Content Loading Transition

```
Skeleton -> Content:
1. Skeleton displayed (shimmer active)
2. Content loads
3. Skeleton fades out (200ms ease-out)
4. Content fades in (200ms ease-in, 100ms delay)
5. Total transition: ~300ms
```

### Error to Recovery

```
Error -> Retry:
1. Error state displayed
2. User clicks Retry
3. Error fades out (150ms)
4. Spinner appears (immediate)
5. On success: Spinner -> Content (200ms)
6. On failure: Spinner -> Error (150ms)
```

### Empty to Content

```
Empty -> Content:
1. Empty state displayed
2. Data arrives (e.g., first item created)
3. Empty state fades out (200ms)
4. Content fades in (200ms)
```

---

## 10. Accessibility Summary

### All Loading/Empty/Error States Must:

1. **Announce state changes** via `aria-live` regions:
   - `aria-live="polite"` for loading, progress updates
   - `aria-live="assertive"` for errors, critical states

2. **Provide text alternatives** for all visual indicators:
   - Spinners: `aria-label="Loading"`
   - Progress bars: `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
   - Illustrations: `aria-hidden="true"` (decorative)

3. **Maintain focus management**:
   - Errors: focus moves to primary action button
   - Loading: focus stays on trigger element
   - Empty: focus moves to primary CTA

4. **Use semantic roles**:
   - `role="status"` for loading states
   - `role="alert"` for error states
   - `role="progressbar"` for progress indicators
   - `role="region"` with labels for empty states

5. **Support keyboard navigation**:
   - All action buttons focusable
   - Skip links where appropriate
   - Escape to dismiss banners

6. **Maintain contrast ratios**:
   - All text: 4.5:1 minimum (WCAG AA)
   - Error text: 7:1 recommended (WCAG AAA)
   - Skeleton shimmer: subtle, not distracting

---

*End of Loading and Empty States*
