# Interaction Model — AuthShield Lab

> Principles and specifications for all user interactions: keyboard, mouse, touchpad, and assistive technology.

---

## Interaction Philosophy

AuthShield Lab is designed for **keyboard-first, mouse-secondary** interaction. Every action is accessible via keyboard. Mouse and touchpad interactions are shortcuts, not requirements.

### Core Interaction Principles

1. **Keyboard parity** — every mouse action has a keyboard equivalent
2. **Predictable focus** — focus always moves to the logical next element
3. **Immediate feedback** — every interaction produces visible feedback within 100ms
4. **Forgiving** — mistakes can be undone, destructive actions confirmed
5. **Efficient** — shortcuts for power users, discoverable for new users

---

## Keyboard Navigation

### Tab Order

Tab follows the visual reading order: top-to-bottom, left-to-right (RTL: top-to-bottom, right-to-left).

**Tab stop hierarchy:**

1. Navigation rail items
2. Sidebar items (when visible and expanded)
3. Toolbar actions (left to right)
4. Main content area (top to bottom, left to right)
5. Right panel items (when visible)
6. Status bar items

### Focus Management Rules

| Scenario | Focus Behavior |
|---|---|
| Tab into section | First focusable element in the section |
| Tab out of section | Last focusable element, then next section |
| Open modal/dialog | First focusable element in modal |
| Close modal/dialog | Return to trigger element |
| Collapse sidebar | Return to main content |
| Navigate to new page | First focusable element in new content area |
| Delete item in list | Next item in list, or previous if last |
| Add item to list | The newly added item |

### Keyboard Shortcuts

#### Global Shortcuts

| Shortcut | Action | Scope |
|---|---|---|
| Ctrl+K | Open command palette | Global |
| Ctrl+/ | Open keyboard shortcuts reference | Global |
| Ctrl+S | Save current form/document | When applicable |
| Ctrl+Z | Undo | Global |
| Ctrl+Y / Ctrl+Shift+Z | Redo | Global |
| Ctrl+F | Find/search in current view | Global |
| Ctrl+N | Create new item | Context-dependent |
| Ctrl+P | Print current view | Global |
| Ctrl+, | Open settings | Global |
| Escape | Close current overlay/modal, clear search, deselect | Global |
| F1 | Open help for current context | Global |

#### Navigation Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+1-6 | Navigate to rail sections (1=Dashboard, 6=Settings) |
| Ctrl+B | Toggle sidebar |
| Ctrl+Shift+P | Toggle right panel |
| Alt+Left | Go back in navigation history |
| Alt+Right | Go forward in navigation history |
| Alt+Home | Go to dashboard |

#### Selection Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+A | Select all items in current list |
| Space | Toggle selection of focused item |
| Shift+Click | Range select (from last selected to clicked) |
| Ctrl+Click | Add/remove item from selection |
| Escape | Clear all selections |

#### Edit Shortcuts

| Shortcut | Action |
|---|---|
| Enter | Activate/confirm focused item |
| Delete/Backspace | Delete selected item(s) (with confirmation) |
| F2 | Rename focused item |
| Ctrl+C | Copy selected item(s) |
| Ctrl+V | Paste copied item(s) |
| Ctrl+X | Cut selected item(s) |
| Ctrl+D | Duplicate selected item(s) |

#### Table Shortcuts (when table has focus)

| Shortcut | Action |
|---|---|
| Arrow keys | Navigate cells |
| Enter | Activate cell action |
| Space | Toggle row selection |
| Ctrl+Space | Select row without deselecting others |
| Shift+Space | Range select rows |
| Home | Go to first cell in row |
| End | Go to last cell in row |
| Ctrl+Home | Go to first cell in table |
| Ctrl+End | Go to last cell in table |

### Focus Trapping

Focus is trapped within these containers when active:

- Modal dialogs
- Command palette
- Context menus
- Dropdown menus
- Popovers with interactive content

**Trapping behavior:**
- Tab from last focusable element → wraps to first
- Shift+Tab from first focusable element → wraps to last
- Focus never escapes to content behind the overlay
- Screen reader users are aware of the container boundaries via `role="dialog"` and `aria-modal="true"`

### Roving Tabindex

For composite widgets (tab bars, menus, toolbars), only one item is in the tab order at a time. Arrow keys move between items:

| Widget | Arrow Key Behavior |
|---|---|
| Tab bar | Left/Right (or Up/Down for vertical) moves active tab |
| Toolbar | Left/Right moves between toolbar items |
| Menu | Up/Down moves between menu items |
| Radio group | Arrow keys move selection |
| Listbox | Up/Down moves active option |

---

## Mouse Interactions

### Click Behavior

| Action | Behavior |
|---|---|
| Left click | Activate (button, link), select (list item), focus (form field) |
| Double-click | Edit in-place (when supported), open detail view |
| Right-click | Open context menu (if applicable) |
| Middle-click | Open in new tab (links), close tab (tab bar) |
| Ctrl+click | Add to selection (lists, tables) |
| Shift+click | Range select (lists, tables) |

### Context Menus

Right-click context menus appear on:

| Target | Menu Items |
|---|---|
| Table row | View, Edit, Duplicate, Delete, Copy, Export |
| List item | View, Edit, Delete, Move, Copy |
| Tree node | Expand/Collapse, Add child, Rename, Delete |
| Empty space | Paste, Select all, View options |
| Text | Copy, Select all (when in edit mode) |
| Image | Copy, Save as, Open in new tab |

**Context menu A11y:**
- `role="menu"` on container
- `role="menuitem"` on each item
- Arrow keys navigate, Enter activates, Escape closes
- Focus returns to trigger element on close

### Drag and Drop

| Operation | Source | Target | Feedback |
|---|---|---|---|
| Reorder | List item, table row | Same list/table | Drop indicator line |
| Move to group | Item | Group/container | Target highlight |
| File import | External file | Drop zone | Drop zone highlight |
| Sort | Column header | — | Visual sort indicator |

**Drag and drop A11y:**
- Keyboard alternative always available (Cut/Paste, Move menu items)
- `aria-grabbed="true"` on dragged item
- `aria-dropeffect="move"` on valid drop targets
- Live region announces: "Item grabbed", "Item dropped at position {n}", "Item dropped in {group}"

---

## Touchpad Interactions

| Gesture | Action | Notes |
|---|---|---|
| Two-finger scroll | Scroll content vertically | Standard |
| Two-finger scroll horizontal | Scroll tables, code blocks horizontally | When content overflows |
| Pinch zoom | Not supported (use Ctrl+/- for zoom) | Application zoom only |
| Two-finger swipe | Navigate back/forward | When applicable |
| Smart zoom | Not supported | — |

---

## Context Menus

### Context Menu Structure

```
┌─────────────────────────────┐
│ [icon] Action 1        Ctrl+1│
│ [icon] Action 2        Ctrl+2│
├─────────────────────────────┤
│ [icon] Action 3             │
│ [icon] Action 4        Del  │
└─────────────────────────────┘
```

### Context Menu Rules

- Maximum 8 items visible without scroll
- Destructive actions at the bottom, separated by a divider
- Keyboard shortcuts displayed on the right side
- Icons on the left for visual scanning
- Disabled items are grayed out with reason tooltip
- Maximum nesting depth: 1 level (one submenu)
- Context menus are dismissed by Escape, clicking outside, or scrolling

---

## Selection Model

### Single Selection

- Click selects one item, deselects all others
- Arrow keys in list/table move selection
- Selected item has blue-50 background and blue-500 border

### Multi-Selection

| Method | Behavior |
|---|---|
| Ctrl+Click | Toggle individual item in selection |
| Shift+Click | Select range from last clicked to current |
| Ctrl+A | Select all visible items |
| Space | Toggle selection on focused item |
| Escape | Clear all selections |

### Selection State Communication

- Selected count shown in toolbar: "3 items selected"
- Bulk action toolbar appears when items are selected
- "Select all X items" link when selection is partial
- "Clear selection" link to deselect all

---

## Copy and Paste

### Standard Keyboard Shortcuts

| Operation | Windows/Linux | macOS |
|---|---|---|
| Copy | Ctrl+C | Cmd+C |
| Cut | Ctrl+X | Cmd+X |
| Paste | Ctrl+V | Cmd+V |
| Select all | Ctrl+A | Cmd+A |

### Supported Copy/Paste Content

| Content Type | Copy | Paste | Notes |
|---|---|---|---|
| Text | Yes | Yes | Plain text, rich text |
| Table rows | Yes | Yes | As TSV or formatted table |
| Course items | Yes | Yes | Within same instance |
| Images | Yes | Yes | From clipboard |
| Code blocks | Yes | Yes | Preserves formatting |
| Files | No | Yes | File import via paste |

---

## Undo and Redo

### Undo Stack

- Maximum undo depth: 50 operations
- Undo operations are grouped logically (e.g., typing characters → one undo)
- Destructive operations (delete) cannot be undone after confirmation
- Auto-save does not create undo entries

### Undo/Redo Communication

- Toast notification on undo: "Action undone" with brief description
- Toast notification on redo: "Action redone" with brief description
- Undo/Redo buttons in toolbar show availability (grayed when stack is empty)
- Keyboard: Ctrl+Z (undo), Ctrl+Y or Ctrl+Shift+Z (redo)

---

## Search

### Global Search (Ctrl+K / Command Palette)

| Feature | Behavior |
|---|---|
| Trigger | Ctrl+K or clicking search bar |
| Scope | All actions, navigation, content, settings |
| Matching | Fuzzy — tolerates typos and abbreviations |
| Results | Categorized (Actions, Navigation, Content, Settings) |
| Keyboard | Type to filter, Up/Down to navigate, Enter to activate |
| Recent | Last 5 searches shown before typing |
| Screen reader | Live region announces result count on each keystroke |

### In-View Search (Ctrl+F)

| Feature | Behavior |
|---|---|
| Trigger | Ctrl+F |
| Scope | Current view content only |
| Matching | Exact and partial, with regex option |
| Results | Highlighted matches, match count shown |
| Navigation | Enter/Shift+Enter for next/previous match |
| Replace | Ctrl+H opens replace field |

---

## Filtering

### Filter Chips

- Applied filters shown as removable chips above the content
- Each chip shows filter name and value
- X button on each chip removes that filter
- "Clear all" removes all filters
- Screen reader announces filter changes via `aria-live`

### Advanced Filter Builder

- Column-based filter conditions
- Operators: equals, contains, starts with, greater than, etc.
- AND/OR logic for combining conditions
- Keyboard navigable with Tab and Arrow keys
- Results update live as filters change

---

## Sorting

### Column Header Sorting

| Click | Behavior |
|---|---|
| First click | Sort ascending (A→Z, 0→9) |
| Second click | Sort descending (Z→A, 9→0) |
| Third click | Remove sort |

### Multi-Sort

- Hold Shift and click additional column headers
- Sort priority shown as numbered badges on column headers
- Maximum 3 sort levels
- "Clear sort" button to reset all sorting

---

## Bulk Actions

### Triggering Bulk Mode

- Select one or more items via Ctrl+Click, Shift+Click, or Space
- Bulk action toolbar appears above the content area
- Shows count of selected items
- Actions available: Delete, Export, Move, Change status, Assign

### Bulk Action Confirmation

- Bulk delete: "Delete {n} items? This action cannot be undone."
- Bulk move: "Move {n} items to {destination}?"
- Bulk status change: "Change status of {n} items to {new status}?"
- Each confirmation shows affected item count and provides Cancel option

---

## Progress Feedback

### Immediate Feedback (< 100ms)

- Button press → visual state change (active color)
- Click → element focus ring visible
- Hover → cursor change, background tint

### Short Operations (100ms - 1s)

- Spinner in button (for button-specific loading)
- Inline loading indicator
- Skeleton screen for content areas

### Long Operations (1s - 30s)

- Progress bar with percentage
- Estimated time remaining
- Operation description ("Saving course...")

### Very Long Operations (> 30s)

- Progress bar with percentage and ETA
- Background operation indicator in status bar
- Ability to cancel operation
- Notification on completion (even if app is not focused)

---

## Interaction Accessibility Requirements

### Motor Accessibility

- All interactive elements have minimum 44x44px touch/click targets
- No time-limited interactions (unless configurable in settings)
- Drag-and-drop always has keyboard alternative
- Double-click always has single-click alternative
- No hover-only interactions — hover augments, not gates functionality

### Cognitive Accessibility

- Consistent interaction patterns across the application
- Clear labels on all interactive elements
- Predictable results from interactions
- Confirmation for destructive actions
- Ability to undo most actions

### Screen Reader Interaction

- All interactive elements are announced with name, role, and state
- Dynamic content changes are announced via aria-live regions
- Landmark regions allow quick navigation
- Heading structure allows jumping between sections
- Form errors are announced when they appear

---

*Every interaction should feel natural, predictable, and accessible. When in doubt, default to the most standard, expected behavior.*
