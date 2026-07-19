# AuthShield Lab — Keyboard Navigation Guide

> Complete keyboard interaction specification for the offline-first desktop cybersecurity education platform.

---

## 1. Overview

AuthShield Lab is a **keyboard-first** application. Every workflow must be completable without a mouse. This document defines all keyboard shortcuts, navigation patterns, focus management, and composite widget behaviors.

---

## 2. Global Shortcuts

These shortcuts work from anywhere in the application.

### 2.1 Application Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+K` | Command Palette | Opens the fuzzy-search command palette |
| `Ctrl+/` | Keyboard Shortcuts Reference | Shows searchable shortcuts overlay |
| `Ctrl+,` | Settings | Opens the Settings dialog |
| `Ctrl+N` | New | Creates new item (context-dependent: lesson, lab, note) |
| `Ctrl+S` | Save | Saves the current document/workspace |
| `Ctrl+Z` | Undo | Undoes the last action |
| `Ctrl+Y` / `Ctrl+Shift+Z` | Redo | Redoes the last undone action |
| `Ctrl+F` | Find/Search | Opens the search panel in current context |
| `Ctrl+H` | Help | Opens the help documentation panel |
| `Escape` | Close/Cancel/Back | Closes current dialog, cancels action, or navigates back |
| `F1` | Context Help | Opens help specific to the current screen/focused element |
| `Ctrl+Shift+A` | Accessibility Settings | Opens the accessibility settings panel |
| `F5` | Refresh | Refreshes current view |
| `Ctrl+Q` | Quit | Closes the application (with save prompt if unsaved changes) |

### 2.2 Navigation Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Alt+1` | Home | Navigate to Home dashboard |
| `Alt+2` | Lessons | Navigate to Lessons library |
| `Alt+3` | Labs | Navigate to interactive Labs |
| `Alt+4` | Progress | Navigate to Progress tracker |
| `Alt+5` | Resources | Navigate to Resources center |
| `Alt+6` | Community | Navigate to Community (if enabled) |
| `Alt+7` | Settings | Navigate to Settings |
| `Alt+Left` | Back | Navigate to previous view in history |
| `Alt+Right` | Forward | Navigate to next view in history |
| `Ctrl+B` | Toggle Sidebar | Show/hide the left sidebar |
| `Ctrl+Shift+B` | Toggle Nav Rail | Show/hide the navigation rail |
| `Ctrl+J` | Toggle Bottom Panel | Show/hide the terminal/console panel |
| `Ctrl+Shift+I` | Toggle Inspector | Show/hide the right inspector panel |

### 2.3 Tab Management

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+T` | New Tab | Opens a new tab in the workspace |
| `Ctrl+W` | Close Tab | Closes the current tab |
| `Ctrl+Tab` | Next Tab | Switches to the next tab |
| `Ctrl+Shift+Tab` | Previous Tab | Switches to the previous tab |
| `Ctrl+1` through `Ctrl+9` | Tab by Position | Switches to tab at position 1–9 |
| `Ctrl+Shift+T` | Reopen Tab | Reopens the last closed tab |

### 2.4 Text Editing

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+A` | Select All | Selects all content in current context |
| `Ctrl+C` | Copy | Copies selected content |
| `Ctrl+X` | Cut | Cuts selected content |
| `Ctrl+V` | Paste | Pastes clipboard content |
| `Ctrl+D` | Duplicate | Duplicates current line or selection |
| `Ctrl+/` | Toggle Comment | Toggles line comment (in code editors) |
| `Ctrl+Shift+K` | Delete Line | Deletes current line |
| `Ctrl+Arrow` | Word Navigation | Moves cursor by word |
| `Ctrl+Backspace` | Delete Word Left | Deletes word before cursor |
| `Ctrl+Delete` | Delete Word Right | Deletes word after cursor |
| `Home` | Line Start | Moves cursor to line start |
| `End` | Line End | Moves cursor to line end |
| `Ctrl+Home` | Document Start | Moves cursor to document start |
| `Ctrl+End` | Document End | Moves cursor to document end |

---

## 3. Standard Widget Navigation

### 3.1 Button

| Key | Action |
|-----|--------|
| `Tab` | Move focus to button |
| `Shift+Tab` | Move focus away from button |
| `Enter` | Activate button |
| `Space` | Activate button |

### 3.2 Link

| Key | Action |
|-----|--------|
| `Tab` | Move focus to link |
| `Shift+Tab` | Move focus away from link |
| `Enter` | Follow link |

### 3.3 Checkbox

| Key | Action |
|-----|--------|
| `Tab` | Move focus to checkbox |
| `Space` | Toggle checkbox state |

### 3.4 Radio Button

| Key | Action |
|-----|--------|
| `Tab` | Move focus to radio group |
| `Arrow Down/Right` | Select next radio in group |
| `Arrow Up/Left` | Select previous radio in group |
| `Space` | Select focused radio |

### 3.5 Select / Dropdown

| Key | Action |
|-----|--------|
| `Tab` | Move focus to select |
| `Enter` / `Space` / `Arrow Down` | Open dropdown |
| `Arrow Up/Down` | Navigate options |
| `Enter` | Select option |
| `Escape` | Close dropdown (no selection) |
| `Type-ahead` | Jump to matching option |

### 3.6 Text Input

| Key | Action |
|-----|--------|
| `Tab` | Move focus to input |
| `Enter` | Submit form (if single input) or move to next field |
| `Escape` | Clear input / blur input |
| `Ctrl+A` | Select all text |
| `Ctrl+Z` | Undo text change |
| `Ctrl+Y` | Redo text change |

### 3.7 Slider

| Key | Action |
|-----|--------|
| `Tab` | Move focus to slider |
| `Arrow Right/Up` | Increase value |
| `Arrow Left/Down` | Decrease value |
| `Home` | Set to minimum |
| `End` | Set to maximum |
| `Page Up` | Increase by large step |
| `Page Down` | Decrease by large step |

---

## 4. Composite Widget Navigation

### 4.1 Tab List

```
┌──────┬──────┬──────┐
│ Tab1 │ Tab2 │ Tab3 │
│ ↑↓→  │  ←→  │  ←↓  │
└──────┴──────┴──────┘
```

| Key | Action |
|-----|--------|
| `Tab` | Move focus into tab list (focuses active tab) |
| `Shift+Tab` | Move focus out of tab list |
| `Arrow Right` | Focus next tab |
| `Arrow Left` | Focus previous tab |
| `Home` | Focus first tab |
| `End` | Focus last tab |
| `Enter` / `Space` | Activate focused tab |
| `Delete` | Close tab (if closable) |

Roving tabindex: Only the active/focused tab has `tabindex="0"`.

### 4.2 Tree View

```
├── Module 1       ← collapsed
│   ├── Lesson 1.1
│   ├── Lesson 1.2
│   └── Lesson 1.3
├── Module 2       ← expanded
│   ├── Lesson 2.1
│   └── Lesson 2.2
└── Module 3       ← collapsed
```

| Key | Action |
|-----|--------|
| `Arrow Down` | Focus next visible node |
| `Arrow Up` | Focus previous visible node |
| `Arrow Right` | Expand node / move to first child |
| `Arrow Left` | Collapse node / move to parent |
| `Enter` | Activate node (open lesson) |
| `Space` | Select node (multi-select with Ctrl) |
| `Home` | Focus first node |
| `End` | Focus last visible node |
| `*` (asterisk) | Expand all siblings |
| `Type-ahead` | Jump to matching node |

### 4.3 Menu / Context Menu

```
┌─────────────────┐
│ ▸ New Lesson    │ ← Arrow Down to move
│   Open          │ ← Enter to activate
│   Rename        │
│ ─────────────── │ ← Separator
│   Delete        │
└─────────────────┘
```

| Key | Action |
|-----|--------|
| `Enter` / `Space` / `Arrow Down` | Open menu |
| `Arrow Down` | Focus next menu item |
| `Arrow Up` | Focus previous menu item |
| `Arrow Right` | Open submenu |
| `Arrow Left` | Close submenu / return to parent |
| `Home` | Focus first item |
| `End` | Focus last item |
| `Enter` | Activate focused item |
| `Escape` | Close menu, return focus to trigger |
| `Tab` | Close menu, move focus to next element |
| `Type-ahead` | Jump to matching item |

### 4.4 Toolbar

```
┌─────┬─────┬─────┬─────┬─────┐
│ B   │ I   │ U   │  S  │ ... │
│ ←→  │ ←→  │ ←→  │ ←→  │     │
└─────┴─────┴─────┴─────┴─────┘
```

| Key | Action |
|-----|--------|
| `Tab` | Move focus into/out of toolbar (focuses first/active item) |
| `Arrow Right` | Focus next toolbar item |
| `Arrow Left` | Focus previous toolbar item |
| `Home` | Focus first item |
| `End` | Focus last item |
| `Enter` / `Space` | Activate focused button |

Roving tabindex: Only one item in toolbar has `tabindex="0"`.

### 4.5 Grid / Data Table

```
┌──────────┬──────────┬──────────┐
│ Name ↑↓  │ Status   │ Date     │
├──────────┼──────────┼──────────┤
│ Lesson 1 │ ● Active │ 07/19    │ ← Space to select
│ Lesson 2 │ ○ Draft  │ 07/18    │
│ Lesson 3 │ ● Active │ 07/17    │
└──────────┴──────────┴──────────┘
```

| Key | Action |
|-----|--------|
| `Tab` | Move focus into grid (focuses first cell) |
| `Shift+Tab` | Move focus out of grid |
| `Arrow Right/Left` | Move to next/previous cell in row |
| `Arrow Down/Up` | Move to same column in next/previous row |
| `Home` | Move to first cell in row |
| `End` | Move to last cell in row |
| `Ctrl+Home` | Move to first cell in grid |
| `Ctrl+End` | Move to last cell in grid |
| `Enter` | Activate cell (open item) |
| `Space` | Select/deselect current row |
| `Ctrl+Space` | Toggle row selection (additive) |
| `Ctrl+A` | Select all rows |
| `Page Down` | Move down by page |
| `Page Up` | Move up by page |
| `Shift+Arrow` | Extend selection |
| `Shift+Space` | Extend selection to current row |

### 4.6 Combobox / Autocomplete

| Key | Action |
|-----|--------|
| `Tab` | Move focus to input |
| `Arrow Down` | Open listbox / focus next option |
| `Arrow Up` | Focus previous option |
| `Enter` | Select focused option, close listbox |
| `Escape` | Close listbox, keep input value |
| `Type-ahead` | Filter options by typed text |

Uses `aria-activedescendant` to track active option without moving DOM focus.

---

## 5. Search Navigation

### 5.1 Quick Search (Ctrl+K)

```
┌────────────────────────────────────┐
│ 🔍 Search commands, lessons...     │
├────────────────────────────────────┤
│ > Introduction to SSH      Lesson │
│   SSH Key Generation       Lesson │
│   Open Settings           Action  │
│   New Lab                 Action  │
└────────────────────────────────────┘
```

| Key | Action |
|-----|--------|
| `Ctrl+K` | Open command palette |
| `/` | Open quick search (when not in input) |
| `Type` | Filter results |
| `Arrow Down` | Focus next result |
| `Arrow Up` | Focus previous result |
| `Enter` | Select result, close palette |
| `Escape` | Close palette |
| `Tab` | Cycle through result categories |

### 5.2 In-Content Search (Ctrl+F)

| Key | Action |
|-----|--------|
| `Ctrl+F` | Open find bar |
| `Type` | Search for text |
| `Enter` | Jump to next match |
| `Shift+Enter` | Jump to previous match |
| `Escape` | Close find bar, clear highlights |

---

## 6. Dialog Navigation

### 6.1 Modal Dialog Focus Management

```
Tab order within dialog:
┌─────────────────────────────────┐
│ Title                           │  ← Not focusable
│ Description text                │  ← Not focusable
│                                 │
│ [Input Field]                   │  ← 1st focusable
│ [Cancel Button]  [Confirm Btn]  │  ← 2nd, 3rd focusable
└─────────────────────────────────┘

Tab → cycles: Input → Cancel → Confirm → Input → ...
```

| Key | Action |
|-----|--------|
| `Tab` | Move to next focusable element within dialog |
| `Shift+Tab` | Move to previous focusable element within dialog |
| `Enter` | Activate focused button |
| `Escape` | Close dialog, return focus to trigger |
| `Arrow keys` | Navigate within composite widgets inside dialog |

### 6.2 Confirmation Dialogs

| Shortcut | Action |
|----------|--------|
| `Y` or `Enter` | Confirm (when confirm button is focused) |
| `N` or `Escape` | Cancel |

### 6.3 Alert Dialogs

| Key | Action |
|-----|--------|
| `Tab` | Cycle through action buttons |
| `Escape` | Dismiss alert (only if dismissible) |
| `Enter` | Activate focused button |

---

## 7. Command Palette (Ctrl+K)

### 7.1 Features

- Fuzzy text matching across commands, lessons, settings, and recent items.
- Categorized results with labels.
- Keyboard-driven navigation.
- Quick actions: type `>` prefix for commands, `#` for lessons, `@` for settings.

### 7.2 Key Bindings

| Key | Action |
|-----|--------|
| `Ctrl+K` | Open from anywhere |
| `Ctrl+K` (while open) | Close and reopen |
| `↑` / `↓` | Navigate results |
| `Enter` | Execute selected command / open selected item |
| `Escape` | Close palette |
| `Tab` | Cycle through result sections |
| `Backspace` on empty input | Close palette |

---

## 8. Terminal / Console Panel

### 8.1 Input Navigation

| Key | Action |
|-----|--------|
| `Ctrl+J` | Toggle terminal panel |
| `Enter` | Execute command |
| `↑` | Previous command in history |
| `↓` | Next command in history |
| `Tab` | Auto-complete |
| `Ctrl+C` | Cancel current input |
| `Ctrl+L` | Clear terminal |
| `Ctrl+A` | Move to line start |
| `Ctrl+E` | Move to line end |
| `Ctrl+U` | Clear line before cursor |
| `Ctrl+K` | Clear line after cursor |
| `Ctrl+W` | Delete word before cursor |

---

## 9. Accessibility Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+Shift+H` | Toggle High Contrast | Switches to high contrast theme |
| `Ctrl+Shift+M` | Toggle Reduced Motion | Disables all animations |
| `Ctrl++` | Increase Text Size | Increases UI text size by 10% |
| `Ctrl+-` | Decrease Text Size | Decreases UI text size by 10% |
| `Ctrl+0` | Reset Text Size | Resets to default size |
| `F6` | Cycle Landmarks | Cycles focus through ARIA landmarks |
| `Ctrl+Shift+U` | Screen Reader Mode | Enables enhanced screen reader output |

---

## 10. Focus Management

### 10.1 Focus Recovery Rules

| Context | Focus Returns To |
|---------|-----------------|
| Modal dialog closes | Element that triggered the dialog |
| Dropdown closes | Dropdown trigger button |
| Context menu closes | Element that triggered the context menu |
| Toast notification dismissed | Last focused element before toast |
| Page navigation | First focusable element on new page |
| Tab close | Nearest remaining tab (or first tab) |
| Panel toggle (show) | First focusable element in panel |
| Panel toggle (hide) | Panel toggle button |
| Search closes | Search input (or element that triggered search) |
| Error validation | First invalid field |

### 10.2 Focus Indicator Specification

```css
/* Default focus style */
:focus-visible {
  outline: 2px solid #3b82f6;  /* blue-500 */
  outline-offset: 2px;
}

/* High contrast focus style */
@media (prefers-contrast: more) {
  :focus-visible {
    outline: 3px solid Highlight;
    outline-offset: 3px;
  }
}

/* Dark background focus style */
.dark :focus-visible {
  outline-color: #60a5fa;  /* blue-400 */
}

/* Disabled elements: no focus */
[disabled] {
  pointer-events: none;
}
```

### 10.3 Focus Trapping Boundaries

The following contexts trap focus:

1. **Modal dialogs**: Tab/Shift+Tab cycle within dialog.
2. **Command palette**: Tab cycles through input and results.
3. **Dropdown menus**: Arrow keys navigate; Tab/Escape exits.
4. **Context menus**: Arrow keys navigate; Tab/Escape exits.
5. **Color pickers**: Tab cycles through controls.

Focus is **not** trapped in:
- Sidebar navigation
- Toolbar
- Tab bar
- Tree view
- Data grid

---

## 11. Keyboard Shortcut Reference Table

### 11.1 Complete Reference (Searchable)

| Category | Shortcut | Action |
|----------|----------|--------|
| **Application** | `Ctrl+K` | Command Palette |
| | `Ctrl+/` | Shortcuts Reference |
| | `Ctrl+,` | Settings |
| | `Ctrl+N` | New Item |
| | `Ctrl+S` | Save |
| | `Ctrl+Z` | Undo |
| | `Ctrl+Y` | Redo |
| | `Ctrl+F` | Find |
| | `Ctrl+H` | Help |
| | `Escape` | Close/Cancel/Back |
| | `F1` | Context Help |
| **Navigation** | `Alt+1-7` | Go to Section |
| | `Alt+Left` | Back |
| | `Alt+Right` | Forward |
| | `Ctrl+B` | Toggle Sidebar |
| | `Ctrl+Shift+B` | Toggle Nav Rail |
| | `Ctrl+J` | Toggle Bottom Panel |
| | `Ctrl+Shift+I` | Toggle Inspector |
| **Tabs** | `Ctrl+T` | New Tab |
| | `Ctrl+W` | Close Tab |
| | `Ctrl+Tab` | Next Tab |
| | `Ctrl+Shift+Tab` | Previous Tab |
| | `Ctrl+1-9` | Tab by Position |
| | `Ctrl+Shift+T` | Reopen Tab |
| **Editing** | `Ctrl+A` | Select All |
| | `Ctrl+C` | Copy |
| | `Ctrl+X` | Cut |
| | `Ctrl+V` | Paste |
| | `Ctrl+D` | Duplicate Line |
| | `Ctrl+/` | Toggle Comment |
| | `Ctrl+Shift+K` | Delete Line |
| **Accessibility** | `Ctrl+Shift+H` | High Contrast |
| | `Ctrl+Shift+M` | Reduced Motion |
| | `Ctrl++` | Increase Text Size |
| | `Ctrl+-` | Decrease Text Size |
| | `Ctrl+0` | Reset Text Size |
| | `F6` | Cycle Landmarks |
| **Terminal** | `Ctrl+C` | Cancel |
| | `Ctrl+L` | Clear |
| | `Ctrl+A` | Line Start |
| | `Ctrl+E` | Line End |
| | `Ctrl+U` | Clear Before |
| | `Ctrl+K` | Clear After |

---

## 12. Platform-Specific Differences

| Shortcut | Windows/Linux | macOS |
|----------|--------------|-------|
| Modifier | `Ctrl` | `⌘` (Cmd) |
| Close Tab | `Ctrl+W` | `⌘W` |
| Preferences | `Ctrl+,` | `⌘,` |
| Quit | `Ctrl+Q` | `⌘Q` |
| Find | `Ctrl+F` | `⌘F` |
| Save | `Ctrl+S` | `⌘S` |
| Undo | `Ctrl+Z` | `⌘Z` |

The application detects the platform and adjusts shortcut display and behavior automatically.

---

*Document version: 1.0.0 — Last updated: 2026-07-19*
