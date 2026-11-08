# AuthShield Lab — Dialog Specifications

> Version: 1.0.0
> Last Updated: 2026-07-19
> Status: Active

---

## Table of Contents

1. [Confirmation Dialog](#1-confirmation-dialog)
2. [Warning Dialog](#2-warning-dialog)
3. [Error Dialog](#3-error-dialog)
4. [Success Dialog](#4-success-dialog)
5. [Information Dialog](#5-information-dialog)
6. [File Picker](#6-file-picker)
7. [Folder Picker](#7-folder-picker)
8. [Plugin Installer](#8-plugin-installer)
9. [Backup Wizard](#9-backup-wizard)
10. [Restore Wizard](#10-restore-wizard)
11. [Import Wizard](#11-import-wizard)
12. [Export Wizard](#12-export-wizard)
13. [Settings Dialog](#13-settings-dialog)
14. [Accessibility Preferences](#14-accessibility-preferences)
15. [Theme Selector](#15-theme-selector)
16. [Language Selector](#16-language-selector)

---

## 1. Confirmation Dialog

### Purpose
Ask user to confirm a potentially destructive or irreversible action.

### ASCII Wireframe

```
+--[360px]--------------------------------------+
|  Confirm Action                          [X]  | 48px title bar
+-----------------------------------------------+
|  16px padding                                 |
|                                               |
|  +--[36px]--+                                 |
|  |    ⚠     |  Are you sure you want to      |
|  |  (icon)  |  delete this backup?            |
|  +----------+                                 |
|                                               |
|  This action cannot be undone. The backup     |
|  and all its data will be permanently         |
|  removed from your device.                    |
|                                               |
|  +--[160px]----+  +--[160px]----+             |
|  |   Cancel    |  |   Delete    |             |
|  +-------------+  +-------------+             |
|  (secondary)       (danger)                    |
|  16px padding                                 |
+-----------------------------------------------+
  Overlay: #00000080, backdrop-filter: blur(4px)
  Dialog: bg --color-surface, border-radius 12px
  Shadow: 0 25px 50px -12px rgba(0,0,0,0.25)
  z-index: 10000
```

### Structure

| Element | Role | Content |
|---------|------|---------|
| Title bar | Header | Dialog title + close button |
| Icon | Decorative | Warning icon (⚠), 36x36px |
| Message | Body | Clear description of consequences |
| Cancel button | Action (secondary) | "Cancel" — closes dialog |
| Confirm button | Action (danger) | Action verb — "Delete", "Remove", etc. |

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to Cancel button (safe default) |
| Tab | Cancel -> Confirm -> Close (X) -> Cancel (trapped) |
| Shift+Tab | Reverse order |
| Focus trap | Tab cannot leave dialog |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Activates focused button |
| Escape | Closes dialog, equivalent to Cancel |
| Tab | Cycles through focusable elements |
| Shift+Tab | Reverse cycle |

### Screen Reader Behavior

```html
<div role="dialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-desc">
  <h2 id="confirm-title">Confirm Action</h2>
  <p id="confirm-desc">Are you sure you want to delete this backup?...</p>
  <button>Cancel</button>
  <button aria-describedby="confirm-desc">Delete</button>
</div>
```

- `role="dialog"` announced on open
- Title and description linked via `aria-labelledby` and `aria-describedby`
- `aria-modal="true"` prevents background interaction
- Live region announces: "Confirm dialog: Confirm Action"

### Error Recovery

- Close (X): Equivalent to Cancel
- Click outside: Does NOT close (prevents accidental dismissal of destructive actions)
- Escape: Equivalent to Cancel

### Accessibility Annotations

- Minimum touch target: 44x44px for buttons
- Contrast: all text meets 4.5:1 ratio
- Focus indicator: 2px solid --color-focus-ring
- Icon: `aria-hidden="true"` (text provides context)

---

## 2. Warning Dialog

### Purpose
Alert user to a non-destructive but important condition requiring attention.

### ASCII Wireframe

```
+--[400px]--------------------------------------+
|  Warning                                [X]   | 48px
+-----------------------------------------------+
|                                               |
|  +--[48px]--+                                 |
|  |    ⚠     |                                 |
|  |  (amber) |                                 |
|  +----------+                                 |
|                                               |
|  Unsaved Changes                              |
|                                               |
|  You have unsaved changes in your assessment. |
|  If you leave now, your progress since the    |
|  last auto-save will be lost.                 |
|                                               |
|  +--[160px]----+  +--[160px]----+             |
|  |  Discard    |  |  Save & Exit|             |
|  +-------------+  +-------------+             |
|  (danger)        (primary)                     |
|                                               |
+-----------------------------------------------+
```

### Structure

| Element | Role | Content |
|---------|------|---------|
| Title bar | Header | "Warning" + close button |
| Icon | Decorative | Amber warning icon, 48x48px |
| Title | Heading | Short description of warning |
| Message | Body | Detailed explanation |
| Discard button | Action (danger) | Proceeds without saving |
| Save & Exit button | Action (primary) | Saves first, then proceeds |

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to "Save & Exit" (safest action) |
| Tab | Save & Exit -> Discard -> Close (X) -> Save & Exit (trapped) |
| Shift+Tab | Reverse order |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Activates focused button |
| Escape | Closes dialog (equivalent to Cancel/dismiss) |
| Tab | Cycles through focusable elements |

### Screen Reader Behavior

```html
<div role="alertdialog" aria-modal="true" aria-labelledby="warn-title" aria-describedby="warn-desc">
  <h2 id="warn-title">Unsaved Changes</h2>
  <p id="warn-desc">You have unsaved changes...</p>
  <button>Discard</button>
  <button>Save & Exit</button>
</div>
```

- Uses `role="alertdialog"` (not `dialog`) for important warnings
- Live region announces: "Warning: Unsaved Changes"

### Error Recovery

- Close (X): Dismisses warning, stays on current screen
- Escape: Same as close
- Click outside: Does NOT close

### Accessibility Annotations

- Icon: `aria-hidden="true"`
- Amber color: #F59E0B, contrast ratio 4.5:1 against white
- Buttons have distinct visual styles (danger vs primary)

---

## 3. Error Dialog

### Purpose
Display error details with recovery options.

### ASCII Wireframe

```
+--[480px]--------------------------------------+
|  Error Occurred                         [X]   | 48px
+-----------------------------------------------+
|                                               |
|  +--[40px]--+                                 |
|  |    ✖     |  Failed to load course data.    |
|  |  (red)   |                                 |
|  +----------+                                 |
|                                               |
|  The course file may be corrupted or missing. |
|  Please try again or contact support.         |
|                                               |
|  +--[448px]--[120px]------------------------+ |
|  | Error Details:                            | |
|  | Code:    COURSE_NOT_FOUND                 | |
|  | File:    /data/courses/crypto-v2.json     | |
|  | Time:    2026-07-19 14:30:00 UTC          | |
|  |                                           | |
|  | [Show Stack Trace ▼]                      | |
|  | +--[448px]--[auto]---------------------+ | |
|  | | at loadCourse (courseService.ts:42)  | | |
|  | | at async loadCourseData (app.ts:128)| | |
|  | | at async initialize (app.ts:45)     | | |
|  | +-------------------------------------+ | |
|  +-----------------------------------------+ |
|                                               |
|  +--[130px]--+ +--[130px]--+ +--[130px]--+   |
|  |  Retry    | |  Go Home  | |  Dismiss  |   |
|  +-----------+ +-----------+ +-----------+   |
|  (primary)     (secondary)    (tertiary)     |
|                                               |
+-----------------------------------------------+
```

### Structure

| Element | Role | Content |
|---------|------|---------|
| Title bar | Header | "Error Occurred" + close |
| Error icon | Decorative | Red circle with X, 40x40px |
| Error title | Heading | Short error summary |
| Error message | Body | Detailed explanation |
| Details panel | Collapsible | Error code, file, timestamp |
| Stack trace | Expandable | Technical details (collapsed by default) |
| Retry button | Action (primary) | Re-attempts the failed operation |
| Go Home button | Action (secondary) | Navigates to Dashboard |
| Dismiss button | Action (tertiary) | Closes dialog only |

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to "Retry" button |
| Tab | Retry -> Go Home -> Dismiss -> Close (X) -> Details toggle -> Retry (trapped) |
| Enter on "Show Stack Trace" | Expands stack trace, focus stays on toggle |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Activates focused button |
| Escape | Closes dialog (equivalent to Dismiss) |
| Tab | Cycles through focusable elements |

### Screen Reader Behavior

```html
<div role="alertdialog" aria-modal="true" aria-labelledby="err-title" aria-describedby="err-desc">
  <h2 id="err-title">Error Occurred</h2>
  <p id="err-desc">Failed to load course data...</p>
  <div role="region" aria-label="Error details">
    <dl>...</dl>
  </div>
  <details>
    <summary>Show Stack Trace</summary>
    <pre>...</pre>
  </details>
  <button>Retry</button>
  <button>Go Home</button>
  <button>Dismiss</button>
</div>
```

- Uses `role="alertdialog"` for immediate attention
- Error details: `<dl>` definition list for key-value pairs
- Stack trace: `<details>/<summary>` for progressive disclosure
- Live region announces: "Error: Failed to load course data"

### Error Recovery

- Retry: Re-attempts operation, closes dialog on success
- Go Home: Navigates to Dashboard, closes dialog
- Dismiss: Closes dialog, stays on current (potentially broken) screen
- Close (X): Same as Dismiss

### Accessibility Annotations

- Error icon: `aria-hidden="true"`, red (#DC2626)
- Stack trace: monospace font, scrollable container
- All error text meets 4.5:1 contrast ratio
- Retry button has `aria-label="Retry loading course data"`

---

## 4. Success Dialog

### Purpose
Confirm successful completion of an action.

### ASCII Wireframe

```
+--[400px]--------------------------------------+
|  Success                                [X]   | 48px
+-----------------------------------------------+
|                                               |
|  +--[48px]--+                                 |
|  |    ✅    |                                 |
|  |  (green) |                                 |
|  +----------+                                 |
|                                               |
|  Backup Created Successfully                  |
|                                               |
|  Your backup has been created and saved to:   |
|  /home/user/.authshield/backups/2026-07-19   |
|                                               |
|  Size: 1.2 GB                                |
|  Duration: 23 seconds                        |
|                                               |
|  +--[180px]----+                              |
|  |    Done     |                              |
|  +-------------+                              |
|  (primary)                                    |
|                                               |
+-----------------------------------------------+
```

### Structure

| Element | Role | Content |
|---------|------|---------|
| Title bar | Header | "Success" + close |
| Success icon | Decorative | Green checkmark, 48x48px |
| Title | Heading | Confirmation message |
| Details | Body | Relevant completion details |
| Done button | Action (primary) | Closes dialog |

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to "Done" button |
| Tab | Done -> Close (X) -> Done (trapped) |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Activates "Done" |
| Escape | Closes dialog |
| Tab | Cycles Done <-> Close |

### Screen Reader Behavior

```html
<div role="dialog" aria-modal="true" aria-labelledby="success-title" aria-describedby="success-desc">
  <h2 id="success-title">Backup Created Successfully</h2>
  <p id="success-desc">Your backup has been created...</p>
  <button>Done</button>
</div>
```

- Uses `role="dialog"` (not alert — not urgent)
- Live region announces: "Success: Backup Created Successfully"

### Error Recovery

- Done: Closes dialog
- Close (X): Same as Done
- Escape: Same as Done

### Accessibility Annotations

- Success icon: `aria-hidden="true"`, green (#22C55E)
- Single action makes focus management simple
- Auto-dismiss after 10 seconds (with warning: "This dialog will close in 5 seconds")

---

## 5. Information Dialog

### Purpose
Display informational content without requiring action.

### ASCII Wireframe

```
+--[440px]--------------------------------------+
|  Information                            [X]   | 48px
+-----------------------------------------------+
|                                               |
|  +--[48px]--+                                 |
|  |    ℹ️    |                                 |
|  |  (blue)  |                                 |
|  +----------+                                 |
|                                               |
|  About Offline Mode                           |
|                                               |
|  AuthShield Lab works entirely offline. All   |
|  your data is stored locally on your device.  |
|  No internet connection is required to use    |
|  the application.                             |
|                                               |
|  When you do connect to the internet, the     |
|  application can check for updates and sync   |
|  optional cloud backups (if configured).      |
|                                               |
|  +--[180px]----+                              |
|  |    Close    |                              |
|  +-------------+                              |
|  (primary)                                    |
|                                               |
+-----------------------------------------------+
```

### Structure

| Element | Role | Content |
|---------|------|---------|
| Title bar | Header | "Information" + close |
| Info icon | Decorative | Blue info icon, 48x48px |
| Title | Heading | Topic |
| Content | Body | Informational text |
| Close button | Action (primary) | Closes dialog |

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to "Close" button |
| Tab | Close -> Close (X) -> Close (trapped) |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Closes dialog |
| Escape | Closes dialog |

### Screen Reader Behavior

- `role="dialog"`, `aria-modal="true"`
- Content may contain headings, lists, links
- Links within content are focusable and functional

### Error Recovery

- Close, Close (X), Escape: All close the dialog

### Accessibility Annotations

- Icon: `aria-hidden="true"`, blue (#3B82F6)
- Content supports rich formatting (headings, lists, links)

---

## 6. File Picker

### Purpose
Browse and select files from the local filesystem.

### ASCII Wireframe

```
+--[640px]--------------------------------------+
|  Select File                             [X]  | 48px
+-----------------------------------------------+
|  Breadcrumb: Home > Documents > Lab Files     | 40px
+-----------------------------------------------+
|  +--[200px]--------+ +--[424px]-------------+ |
|  | FAVORITES        | |  Name          Size  | |
|  | [⭐] Recent      | |  [Folder 📁]  --    | |
|  | [📁] Documents   | |  [Folder 📁]  --    | |
|  | [📁] Downloads   | |  report.pdf   2.4MB | |
|  |                  | |  data.csv     156KB | |
|  | FOLDERS          | |  notes.txt    12KB  | |
|  | [📁] Projects    | |                    | |
|  | [📁] Backups     | |                    | |
|  | [📁] Lab Data    | |                    | |
|  |                  | |                    | |
|  |                  | |                    | |
|  +------------------+ +--------------------+ |
|                                               |
|  File type: [All Files (*.*)           ▼]     |
|  File name: [report.pdf                 ]     |
|                                               |
|  +--[160px]----+  +--[160px]----+             |
|  |   Cancel    |  |   Open      |             |
|  +-------------+  +-------------+             |
|                                               |
+-----------------------------------------------+
```

### Structure

| Element | Role | Content |
|---------|------|---------|
| Title bar | Header | "Select File" + close |
| Breadcrumb | Navigation | Current path segments |
| Sidebar | Favorites | Quick-access locations |
| File list | Main area | Sortable columns (name, size, date) |
| File type filter | Dropdown | File extension filter |
| File name input | Text field | Selected filename or type to filter |
| Cancel button | Action | Closes dialog |
| Open button | Action | Selects file and closes |

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to file list (first item) |
| Tab | Sidebar -> File list -> File type -> File name -> Cancel -> Open -> Sidebar (trapped) |
| Arrow keys in file list | Navigate files |
| Enter on folder | Opens folder, updates breadcrumb |
| Enter on file | Selects file, populates file name field |
| Backspace | Navigate up one directory |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Open folder / Select file |
| Escape | Cancel dialog |
| Backspace | Go up one directory |
| Arrow keys | Navigate file list |
| Home | First file in list |
| End | Last file in list |
| Ctrl+L | Focus breadcrumb for manual path entry |

### Screen Reader Behavior

```html
<div role="dialog" aria-modal="true" aria-labelledby="fp-title">
  <h2 id="fp-title">Select File</h2>
  <nav aria-label="File path breadcrumb">...</nav>
  <nav aria-label="Quick access locations">...</nav>
  <div role="grid" aria-label="Files" aria-rowcount="12">
    <div role="row" aria-rowindex="1">...</div>
  </div>
  <label for="fp-type">File type</label>
  <label for="fp-name">File name</label>
</div>
```

- File list: `role="grid"` for efficient keyboard navigation
- Folder navigation announced: "Entered folder: Lab Files"
- File count announced: "12 items, 2 folders, 10 files"

### Error Recovery

- Cancel: Closes dialog, no selection
- Navigate to different folder if current is empty

### Accessibility Annotations

- File icons: `aria-hidden="true"` (text label provides name)
- Folder: `role="row"` with `aria-label="Folder: {name}"`
- Selected file: `aria-selected="true"`
- File type dropdown: `aria-label="Filter by file type"`

---

## 7. Folder Picker

### Purpose
Browse and select folders from the local filesystem.

### ASCII Wireframe

```
+--[600px]--------------------------------------+
|  Select Folder                           [X]  | 48px
+-----------------------------------------------+
|  Breadcrumb: Home > Documents                 | 40px
+-----------------------------------------------+
|  +--[180px]--------+ +--[404px]-------------+ |
|  | FAVORITES        | |  Name                | |
|  | [⭐] Recent      | |  [📁] Projects       | |
|  | [📁] Documents   | |  [📁] Backups        | |
|  | [📁] Downloads   | |  [📁] Lab Data       | |
|  |                  | |  [📁] Simulations    | |
|  | SYSTEM           | |  [📁] Course Files   | |
|  | [📁] Home        | |                    | |
|  | [📁] Desktop     | |                    | |
|  |                  | |                    | |
|  +------------------+ +--------------------+ |
|                                               |
|  Selected: /home/user/Documents/Lab Data      |
|                                               |
|  [Create New Folder ✏️]                       |
|                                               |
|  +--[160px]----+  +--[160px]----+             |
|  |   Cancel    |  |   Select    |             |
|  +-------------+  +-------------+             |
|                                               |
+-----------------------------------------------+
```

### Structure

Same as File Picker but:
- No file type filter
- No file name input
- Shows "Selected: {path}" instead
- "Create New Folder" button: inline form for new folder name
- Select button: "Select" instead of "Open"

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to folder list (first item) |
| Tab | Sidebar -> Folder list -> Create New Folder -> Cancel -> Select -> Sidebar (trapped) |
| Enter on folder | Selects folder, updates "Selected" display |
| Enter again or Enter on Select | Confirms selection |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Select folder (single click) or Open folder (double Enter) |
| Escape | Cancel |
| Backspace | Go up one directory |
| Arrow keys | Navigate folder list |
| Ctrl+N | Focus "Create New Folder" |

### Screen Reader Behavior

- Folder list: `role="tree"`, folders `role="treeitem"`
- Selection announced: "Selected: /home/user/Documents/Lab Data"
- New folder creation: form with `aria-label="New folder name"`

### Error Recovery

- Cancel: Closes dialog
- New folder: Creates folder, auto-selects it

### Accessibility Annotations

- Folder icons: `aria-hidden="true"`
- Selected state: `aria-selected="true"` + visual highlight
- Create New Folder: `role="form"` with text input and confirm button

---

## 8. Plugin Installer

### Purpose
Review plugin details, permissions, and install.

### ASCII Wireframe

```
+--[480px]--------------------------------------+
|  Install Plugin                          [X]  | 48px
+-----------------------------------------------+
|                                               |
|  +--[48px]--+  Plugin Name                   |
|  |  [icon]  |  v2.1.0 | by Author Name       |
|  +----------+                                |
|                                               |
|  Description of what this plugin does and     |
|  why you might want to install it.            |
|                                               |
|  +--[448px]--[auto]------------------------+ |
|  | Permissions Required:                    | |
|  |                                         | |
|  | [✓] Access course data                  | |
|  |     Read and modify course content      | |
|  |                                         | |
|  | [✓] Run simulations                     | |
|  |     Execute simulation environments     | |
|  |                                         | |
|  | [!] Network access                      | |
|  |     Connect to external APIs            | |
|  +-----------------------------------------+ |
|                                               |
|  Rating: ★★★★☆ (4.2/5) | Downloads: 1,234   |
|                                               |
|  [ ] I understand the permissions requested   |
|                                               |
|  +--[160px]----+  +--[160px]----+             |
|  |   Cancel    |  |   Install   |             |
|  +-------------+  +-------------+             |
|  (disabled until checkbox checked)            |
|                                               |
+-----------------------------------------------+
```

### Structure

| Element | Role | Content |
|---------|------|---------|
| Title bar | Header | "Install Plugin" + close |
| Plugin icon | Visual | 48x48px plugin icon |
| Plugin name | Heading | Name + version + author |
| Description | Body | What the plugin does |
| Permissions list | List | Required permissions with descriptions |
| Rating/stats | Info | User rating and download count |
| Consent checkbox | Required | Permission acknowledgment |
| Cancel button | Action | Closes dialog |
| Install button | Action | Installs plugin (disabled until consent) |

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to scroll area (plugin details) |
| Tab | Scroll area -> Consent checkbox -> Cancel -> Install -> Close -> Scroll area (trapped) |
| Checkbox checked | Install button becomes enabled |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Activates focused button |
| Escape | Closes dialog |
| Space | Toggles checkbox |
| Tab | Cycles through elements |

### Screen Reader Behavior

```html
<div role="dialog" aria-modal="true" aria-labelledby="pi-title">
  <h2 id="pi-title">Install Plugin: Network Scanner</h2>
  <div role="region" aria-label="Plugin details">...</div>
  <div role="region" aria-label="Required permissions">
    <ul>
      <li><strong>Access course data:</strong> Read and modify course content</li>
    </ul>
  </div>
  <input type="checkbox" id="pi-consent" aria-describedby="pi-consent-desc" />
  <label for="pi-consent">I understand the permissions</label>
</div>
```

- Permissions list: `<ul>` with `<strong>` for permission name
- Install button: `aria-disabled="true"` until consent given
- Consent checkbox: linked to install button via describedby

### Error Recovery

- Cancel: Closes dialog
- Install fails: Shows error dialog with retry option

### Accessibility Annotations

- Permission indicators: not color alone — text labels ("✓ Required", "! Network")
- Consent checkbox: required for screen reader announcement
- Install button: disabled state clearly indicated (opacity + aria-disabled)

---

## 9. Backup Wizard

### Purpose
Step-by-step wizard to create application backups.

### ASCII Wireframe (4 steps)

```
+--[560px]--------------------------------------+
|  Create Backup                           [X]  | 48px
+-----------------------------------------------+
|  Step 1 of 4: Select Scope                    | 32px
|  ─────────────────────────────────────────    |
|  [1] Scope    [2] Options    [3] Confirm     |
|  [██████]     [--------]     [--------]       |
|  [4] Progress [--------]     [--------]       |
|  [--------]                                  |
|                                               |
|  What would you like to back up?              |
|                                               |
|  (o) Full Application Data                    |
|      Courses, assessments, results, settings  |
|                                               |
|  ( ) Courses Only                             |
|      Course content and enrollment data       |
|                                               |
|  ( ) Settings Only                            |
|      Preferences, themes, keyboard shortcuts  |
|                                               |
|  ( ) Custom Selection                         |
|      Choose specific data categories          |
|                                               |
|  ─────────────────────────────────────────    |
|                                               |
|  +--[160px]----+          +--[160px]----+     |
|  |   Cancel    |          |   Next →    |     |
|  +-------------+          +-------------+     |
|                                               |
+-----------------------------------------------+
```

### Step 2: Options

```
+--[560px]--------------------------------------+
|  Create Backup                           [X]  | 48px
+-----------------------------------------------+
|  Step 2 of 4: Options                         |
|  ─────────────────────────────────────────    |
|  [1] Scope    [2] Options    [3] Confirm     |
|  [██████]     [██████]       [--------]       |
|  [4] Progress [--------]     [--------]       |
|  [--------]                                  |
|                                               |
|  Backup Options:                              |
|                                               |
|  Compression:                                 |
|  (o) Standard (gzip) — Good balance           |
|  ( ) Maximum (bzip2) — Smaller, slower        |
|  ( ) None — Fastest, largest                  |
|                                               |
|  Include:                                     |
|  [x] Course content and progress              |
|  [x] Assessment results and certificates      |
|  [x] User settings and preferences            |
|  [ ] Plugin data                              |
|  [x] Simulation state                         |
|                                               |
|  Estimated size: ~1.2 GB                      |
|                                               |
|  ─────────────────────────────────────────    |
|                                               |
|  +--[160px]----+          +--[160px]----+     |
|  |  ← Back     |          |   Next →    |     |
|  +-------------+          +-------------+     |
|                                               |
+-----------------------------------------------+
```

### Step 3: Confirm

```
+--[560px]--------------------------------------+
|  Create Backup                           [X]  | 48px
+-----------------------------------------------+
|  Step 3 of 4: Confirm                         |
|  ─────────────────────────────────────────    |
|  [1] Scope    [2] Options    [3] Confirm     |
|  [██████]     [██████]       [██████]         |
|  [4] Progress [--------]     [--------]       |
|  [--------]                                  |
|                                               |
|  Backup Summary:                              |
|  +--[528px]--[auto]------------------------+ |
|  | Scope:        Full application data      | |
|  | Compression:  Standard (gzip)            | |
|  | Includes:     Courses, Assessments,      | |
|  |               Settings, Simulations      | |
|  | Estimated:    ~1.2 GB                    | |
|  | Destination:  ~/.authshield/backups/     | |
|  | Available:    45.2 GB free               | |
|  +-----------------------------------------+ |
|                                               |
|  ─────────────────────────────────────────    |
|                                               |
|  +--[160px]----+          +--[160px]----+     |
|  |  ← Back     |          |  Create     |     |
|  +-------------+          +-------------+     |
|                                               |
+-----------------------------------------------+
```

### Step 4: Progress

```
+--[560px]--------------------------------------+
|  Create Backup                           [X]  | 48px
+-----------------------------------------------+
|  Step 4 of 4: Creating Backup                 |
|  ─────────────────────────────────────────    |
|  [1] Scope    [2] Options    [3] Confirm     |
|  [██████]     [██████]       [██████]         |
|  [4] Progress [██████]       [██████]         |
|  [██████]                                   |
|                                               |
|  Creating backup...                           |
|  +--[528px]--[8px]--------------------------+ |
|  | [||||||||||||||||||||||............] 65% | |
|  +-----------------------------------------+ |
|                                               |
|  Current: Compressing assessment results...   |
|  Elapsed: 0:15                                |
|                                               |
|  ─────────────────────────────────────────    |
|                                               |
|  +--[160px]----+  (Cancel disabled during)    |
|  |   Cancel    |                              |
|  +-------------+                              |
|                                               |
+-----------------------------------------------+
```

### Focus Management

| Step | Initial Focus |
|------|---------------|
| 1 (Scope) | First radio button |
| 2 (Options) | First radio (compression) |
| 3 (Confirm) | "Create" button |
| 4 (Progress) | Progress bar (read-only) |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Next / Create |
| Escape | Cancel (with confirmation if in progress) |
| Arrow keys | Navigate radio buttons |
| Space | Toggle checkboxes |
| Tab | Move between sections |

### Screen Reader Behavior

- Step indicator: "Step 1 of 4: Select Scope"
- Progress: `role="progressbar"`, `aria-valuenow="65"`, `aria-label="Backup progress: 65%"`
- `aria-live="polite"` on progress updates (every 5%)
- Completion: "Backup created successfully"

### Error Recovery

- Cancel during creation: confirmation dialog
- Error during creation: error dialog with retry option
- Back button: returns to previous step without losing selections

### Accessibility Annotations

- Step indicator: visually clear numbered steps
- Radio buttons: proper `role="radiogroup"` with labels
- Progress bar: accessible with percentage and current operation text

---

## 10. Restore Wizard

### Purpose
Step-by-step wizard to restore from a backup.

### ASCII Wireframes (4 steps)

### Step 1: Select Backup

```
+--[560px]--------------------------------------+
|  Restore from Backup                     [X]  | 48px
+-----------------------------------------------+
|  Step 1 of 4: Select Backup                   |
|  ─────────────────────────────────────────    |
|  [1] Select   [2] Preview    [3] Confirm     |
|  [██████]     [--------]     [--------]       |
|  [4] Progress [--------]     [--------]       |
|  [--------]                                  |
|                                               |
|  Select a backup to restore:                  |
|                                               |
|  +--[528px]--[80px]------------------------+ |
|  | [Radio] Backup: Jul 19, 2026           | |
|  |          1.2 GB | Full | Last modified: | |
|  |          2 hours ago                    | |
|  +-----------------------------------------+ |
|  +--[528px]--[80px]------------------------+ |
|  | [Radio] Backup: Jul 12, 2026           | |
|  |          1.1 GB | Full | Last modified: | |
|  |          7 days ago                     | |
|  +-----------------------------------------+ |
|  +--[528px]--[80px]------------------------+ |
|  | [Radio] Backup: Jul 5, 2026            | |
|  |          1.0 GB | Full | Last modified: | |
|  |          14 days ago                    | |
|  +-----------------------------------------+ |
|                                               |
|  ─────────────────────────────────────────    |
|  +--[160px]----+          +--[160px]----+     |
|  |   Cancel    |          |   Next →    |     |
|  +-------------+          +-------------+     |
+-----------------------------------------------+
```

### Step 2-4: Similar structure to Backup Wizard

Step 2 (Preview): Shows what data will be restored, conflicts
Step 3 (Confirm): Summary with warning about overwriting current data
Step 4 (Progress): Progress bar with current operation

### Focus Management

| Step | Initial Focus |
|------|---------------|
| 1 (Select) | First backup radio button |
| 2 (Preview) | Scroll area with preview data |
| 3 (Confirm) | "Restore" button |
| 4 (Progress) | Progress bar |

### Keyboard Shortcuts

Same as Backup Wizard.

### Screen Reader Behavior

- Backup list: `role="radiogroup"`, each backup `role="radio"`
- Selected backup announced with full details
- Step 2 preview: `aria-live="polite"` for data summary
- Progress: `role="progressbar"` with detailed status

### Error Recovery

- Cancel at any step: confirmation if selections made
- Invalid backup: error message inline, try different backup
- Restore failure: error dialog with option to try another backup

---

## 11. Import Wizard

### Purpose
Import external data (courses, assessments, plugins) into the application.

### ASCII Wireframes (5 steps)

### Step 1: Select File

```
+--[560px]--------------------------------------+
|  Import Data                             [X]  | 48px
+-----------------------------------------------+
|  Step 1 of 5: Select File                     |
|  ─────────────────────────────────────────    |
|  [1] File     [2] Preview     [3] Mapping    |
|  [██████]     [--------]      [--------]      |
|  [4] Confirm  [5] Progress   [--------]       |
|  [--------]  [--------]                       |
|                                               |
|  Select a file to import:                     |
|                                               |
|  +--[528px]--[120px]-----------------------+ |
|  |                                         | |
|  |  +--[120px]--+                          | |
|  |  |           |  Drag and drop a file    | |
|  |  |  [icon]   |  here, or                | |
|  |  |           |                          | |
|  |  +----------+  [Browse Files]           | |
|  |                                         | |
|  +-----------------------------------------+ |
|                                               |
|  Supported formats: .json, .csv, .xml, .yaml  |
|  Maximum file size: 500 MB                    |
|                                               |
|  ─────────────────────────────────────────    |
|  +--[160px]----+          +--[160px]----+     |
|  |   Cancel    |          |   Next →    |     |
|  +-------------+          +-------------+     |
+-----------------------------------------------+
```

### Step 2: Preview

Shows data preview: first 20 rows for tables, structure for JSON
Validates data format and shows warnings for issues

### Step 3: Mapping

Column/field mapping for structured data:
- Source field -> Target field dropdowns
- Skip field option
- Preview of mapped data

### Step 4: Confirm

Summary of import: data type, record count, estimated time
Warnings for conflicts (duplicate data)

### Step 5: Progress

Import progress bar with current operation and ETA

### Focus Management

| Step | Initial Focus |
|------|---------------|
| 1 (File) | Browse Files button |
| 2 (Preview) | Data preview scroll area |
| 3 (Mapping) | First mapping dropdown |
| 4 (Confirm) | "Import" button |
| 5 (Progress) | Progress bar |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+O | Open file browser (step 1) |
| Enter | Next / Import |
| Escape | Cancel |
| Tab | Navigate between mapping fields |

### Screen Reader Behavior

- File drop zone: `role="button"`, `aria-label="Browse for file to import"`
- Preview table: proper `<table>` with `<th>`
- Mapping: each pair announced as "Source field X maps to Target field Y"
- Progress: `role="progressbar"`, `aria-valuenow`, `aria-label="Import progress"`

### Error Recovery

- Invalid file format: inline error, "Please select a supported format"
- Corrupted file: error dialog with suggestion to try different file
- Import partial failure: summary of what succeeded/failed

---

## 12. Export Wizard

### Purpose
Export application data to external files.

### ASCII Wireframes (5 steps)

### Step 1: Select Data

```
+--[560px]--------------------------------------+
|  Export Data                             [X]  | 48px
+-----------------------------------------------+
|  Step 1 of 5: Select Data                     |
|  ─────────────────────────────────────────    |
|  What would you like to export?               |
|                                               |
|  [x] Course Progress (12 courses, 4.2 MB)     |
|  [x] Assessment Results (47 results, 1.8 MB)  |
|  [x] Certificates (8 certificates, 0.3 MB)    |
|  [ ] Simulation Data (15 sessions, 2.1 MB)    |
|  [x] User Settings (0.1 MB)                   |
|  [ ] Plugins (3 plugins, 15.2 MB)             |
|                                               |
|  Selected: 4 items (~6.4 MB)                  |
|                                               |
|  ─────────────────────────────────────────    |
|  +--[160px]----+          +--[160px]----+     |
|  |   Cancel    |          |   Next →    |     |
|  +-------------+          +-------------+     |
+-----------------------------------------------+
```

### Step 2: Format Options

Format selection (JSON, CSV, XML, PDF for reports)
Format-specific options (delimiter for CSV, pretty-print for JSON)

### Step 3: Confirm

Export summary: data items, format, estimated size

### Step 4: Progress

Export progress with current operation

### Step 5: Save

File save dialog (native or custom): choose destination, filename
Confirmation with file path and size

### Focus Management

| Step | Initial Focus |
|------|---------------|
| 1 (Data) | First checkbox |
| 2 (Format) | Format radio group |
| 3 (Confirm) | "Export" button |
| 4 (Progress) | Progress bar |
| 5 (Save) | File name input |

### Screen Reader Behavior

- Data selection: checkboxes with data counts and sizes
- Format selection: radio group with descriptions
- Save: file path announced, "Export complete. File saved to {path}"

### Error Recovery

- Cancel at any step: confirmation if selections made
- Disk full: error with option to choose different location
- Export failure: retry or save partial export

---

## 13. Settings Dialog

### Purpose
Full-screen modal for all application settings.

### ASCII Wireframe

```
+--[100% of workspace]-------------------------------+
|  Settings                                    [X]  | 48px
+---------------------------------------------------+
|                                                   |
|  [General][Account][Appearance][A11y][Keyboard]   | 40px tab bar
|  [Notifications][Privacy][Plugins][Backup][Adv]   |
|                                                   |
|  +--[240px]--+ +--[calc-100%-256px]-------------+ |
|  | Categories| |                                | |
|  |           | |  General Settings              | |
|  | [>]General| |                                | |
|  | [>]Account| |  Application                   | |
|  | [>]Appear | |  ──────────────────────────── | |
|  | [>]A11y   | |  [x] Auto-save    [toggle]    | |
|  | [>]Keybrd | |  [ ] Check updates [toggle]   | |
|  | [>]Notif  | |  [x] Show tips    [toggle]    | |
|  | [>]Privacy| |                                | |
|  | [>]Plugin | |  Startup                      | |
|  | [>]Backup | |  ──────────────────────────── | |
|  | [>]Diagnos| |  (o) Show Dashboard           | |
|  | [>]Advanc | |  ( ) Show last view           | |
|  |           | |  ( ) Show Login               | |
|  |           | |                                | |
|  |           | |  Language                      | |
|  |           | |  ──────────────────────────── | |
|  |           | |  [English (US)            ▼]  | |
|  |           | |                                | |
|  +-----------+ +--------------------------------+ |
|                                                   |
|  ────────────────────────────────────────────     |
|                                                   |
|  [Save Changes]  [Reset to Defaults]              |
|                                                   |
+---------------------------------------------------+
  Full-screen modal (not small dialog)
  Sidebar + main content layout within modal
  Tabs duplicate sidebar on narrow screens
```

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to first category in sidebar |
| Tab | Sidebar -> Content area form controls -> Save -> Reset -> Close -> Sidebar (trapped) |
| Arrow keys in sidebar | Navigate categories |
| Enter on category | Loads category content, focus moves to first form control |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Confirm / Save |
| Escape | Close (with unsaved changes warning) |
| Arrow keys | Navigate sidebar categories |
| Tab | Navigate form controls |
| Ctrl+S | Save changes |

### Screen Reader Behavior

```html
<div role="dialog" aria-modal="true" aria-labelledby="settings-title">
  <h1 id="settings-title">Settings</h1>
  <nav aria-label="Settings categories">
    <ul role="tablist">
      <li role="tab" aria-selected="true">General</li>
    </ul>
  </nav>
  <div role="tabpanel" aria-label="General settings">
    <fieldset>
      <legend>Application</legend>
      ...
    </fieldset>
  </div>
</div>
```

### Error Recovery

- Unsaved changes: warning dialog before closing
- Invalid setting value: inline validation message
- Reset: confirmation dialog with "This will reset all settings to defaults"

---

## 14. Accessibility Preferences

### Purpose
Quick access to accessibility settings without full settings dialog.

### ASCII Wireframe

```
+--[440px]--------------------------------------+
|  Accessibility Preferences               [X]  | 48px
+-----------------------------------------------+
|                                               |
|  Theme:                                       |
|  (o) Light    ( ) Dark    ( ) High Contrast   |
|                                               |
|  Text Size:                                   |
|  [A-] [====●==========] [A+]  15px           |
|                                               |
|  Contrast:                                    |
|  [Normal] [==========●==] [High]              |
|                                               |
|  Reduce Motion:                               |
|  [Toggle: OFF ──── ON]                        |
|                                               |
|  Screen Reader Optimizations:                 |
|  [Toggle: OFF ──── ON]                        |
|                                               |
|  +--[160px]----+  +--[160px]----+             |
|  |   Cancel    |  |   Apply     |             |
|  +-------------+  +-------------+             |
|                                               |
+-----------------------------------------------+
  Compact dialog, all settings visible at once
  Changes apply immediately on toggle/slider
  Apply button only needed for destructive changes
```

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to first setting (Theme radio group) |
| Tab | Theme -> Text Size slider -> Contrast slider -> Reduce Motion toggle -> Screen Reader toggle -> Cancel -> Apply -> Theme (trapped) |

### Screen Reader Behavior

- Sliders: `role="slider"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
- Toggles: `role="switch"`, `aria-checked`
- Live region: announces preview changes immediately

---

## 15. Theme Selector

### Purpose
Select and preview application theme.

### ASCII Wireframe

```
+--[480px]--------------------------------------+
|  Select Theme                            [X]  | 48px
+-----------------------------------------------+
|                                               |
|  +--[140px]--+  +--[140px]--+ +--[140px]--+  |
|  |           |  |           | |           |  |
|  |  [Light   |  |  [Dark    | | [High     |  |
|  |   Theme   |  |   Theme   | |  Contrast |  |
|  |   Preview]|  |   Preview]| |  Preview] |  |
|  |           |  |           | |           |  |
|  |  ○ Light  |  |  ○ Dark   | | ○ High    |  |
|  +-----------+  +-----------+ |  Contrast |  |
|  (selected)                    +-----------+  |
|                                (selected)     |
|                                               |
|  Live Preview:                                |
|  +--[448px]--[200px]-----------------------+  |
|  |  +--[sample-card]--+                    |  |
|  |  |  Heading        |                    |  |
|  |  |  Body text      |                    |  |
|  |  |  [Button]       |                    |  |
|  |  +-----------------+                    |  |
|  +-----------------------------------------+  |
|                                               |
|  +--[160px]----+  +--[160px]----+             |
|  |   Cancel    |  |   Apply     |             |
|  +-------------+  +-------------+             |
|                                               |
+-----------------------------------------------+
  3-column theme preview cards
  Live preview shows real UI elements in selected theme
  Click card or radio to select
```

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to currently selected theme card |
| Arrow keys | Navigate between theme cards |
| Enter | Selects focused theme, updates preview |
| Tab | Theme cards -> Cancel -> Apply -> Theme cards (trapped) |

### Screen Reader Behavior

- Theme cards: `role="radio"`, `role="radiogroup"` for group
- Preview: `aria-live="polite"` announces theme change
- Selected state: `aria-checked="true"`

---

## 16. Language Selector

### Purpose
Select application language with preview.

### ASCII Wireframe

```
+--[480px]--------------------------------------+
|  Select Language                         [X]  | 48px
+-----------------------------------------------+
|                                               |
|  Search: [Search languages...             ]   |
|                                               |
|  +--[448px]--[auto]------------------------+  |
|  |  English (US)                    [en-US]|  |
|  |  English (UK)                    [en-GB]|  |
|  |  English (AU)                    [en-AU]|  |
|  |  ------------------------------------  |  |
|  |  Francais (FR)                   [fr-FR]|  |
|  |  Deutsch (DE)                    [de-DE]|  |
|  |  Espanol (ES)                    [es-ES]|  |
|  |  ------------------------------------  |  |
|  |  Portugues (PT-BR)              [pt-BR]|  |
|  |  Italiano (IT)                   [it-IT]|  |
|  |  ------------------------------------  |  |
|  |  Arabic (ar)                     [ar]  |  |
|  |  Japanese (ja)                   [ja]  |  |
|  |  [Selected: English (US) ✓]            |  |
|  +-----------------------------------------+  |
|                                               |
|  Preview:                                     |
|  +--[448px]--[80px]-------------------------+ |
|  |  Date: July 19, 2026                     | |
|  |  Time: 2:30 PM                           | |
|  |  Number: 1,234.56                        | |
|  |  Currency: $100.00                       | |
|  +-----------------------------------------+  |
|                                               |
|  ─────────────────────────────────────────    |
|  ⚠ Language change requires application       |
|    restart to take full effect.                |
|                                               |
|  +--[160px]----+  +--[160px]----+             |
|  |   Cancel    |  |  Apply &    |             |
|  |             |  |  Restart    |             |
|  +-------------+  +-------------+             |
|                                               |
+-----------------------------------------------+
  Scrollable language list grouped by region
  Preview updates on language selection
  Restart warning is non-blocking info
```

### Focus Management

| Event | Behavior |
|-------|----------|
| Dialog opens | Focus moves to search input |
| Tab | Search -> Language list -> Preview -> Cancel -> Apply -> Search (trapped) |
| Arrow keys in list | Navigate languages |
| Enter on language | Selects language, updates preview |

### Screen Reader Behavior

- Language list: `role="listbox"`, each language `role="option"`
- Selected: `aria-selected="true"`
- Preview: `aria-live="polite"` announces formatted values
- Restart warning: `role="note"`

### Error Recovery

- Cancel: Closes dialog, no language change
- Invalid locale: Falls back to English (US)

---

*End of Dialog Specifications*
