# Component Library — AuthShield Lab

> Comprehensive component specifications for the AuthShield Lab design system. Every component is accessible, keyboard-navigable, and theme-aware.

---

## Component Architecture

### Technology Stack

- **Framework**: React 18+ with TypeScript
- **Styling**: TailwindCSS with design tokens via CSS custom properties
- **State**: Zustand for component state, React context for theme/a11y
- **Testing**: React Testing Library + Playwright for a11y

### Component Principles

1. **Accessible by default** — every component ships with ARIA attributes, keyboard support, and screen reader labels
2. **Composable** — components combine to build complex interfaces
3. **Theme-aware** — all colors, spacing, and typography use design tokens
4. **Consistent API** — similar props across similar components (size, variant, disabled, loading)
5. **Self-contained** — components manage their own state and interactions

---

## Buttons

### Purpose

Trigger actions or events. Primary interactive element for user-initiated operations.

### Variants

| Variant | CSS Class | Background | Text | Border | Usage |
|---|---|---|---|---|---|
| Primary | `btn-primary` | blue-600 | white | none | Main actions (Submit, Save, Start) |
| Secondary | `btn-secondary` | white | blue-600 | blue-600 | Secondary actions (Cancel, Back) |
| Ghost | `btn-ghost` | transparent | text-secondary | none | Tertiary actions (Close, Dismiss) |
| Danger | `btn-danger` | red-600 | white | none | Destructive actions (Delete, Remove) |
| Danger Ghost | `btn-danger-ghost` | transparent | red-600 | red-600 | Secondary destructive (Cancel delete) |

### Sizes

| Size | Height | Padding H | Font Size | Icon Size | Usage |
|---|---|---|---|---|---|
| sm | 32px | 12px | 12px | 16px | Compact tables, inline actions |
| md | 40px | 16px | 14px | 20px | Default, most contexts |
| lg | 48px | 20px | 16px | 24px | Primary page actions |

### States

| State | Visual Treatment | Interaction |
|---|---|---|
| Default | Normal colors | Standard interaction |
| Hover | Slightly darker bg | Cursor pointer |
| Focus | 2px solid blue-500 ring, 2px offset | Keyboard focus |
| Active/Pressed | Darker than hover | Mouse down / Enter |
| Disabled | 50% opacity, gray cursor | No interaction |
| Loading | Spinner replaces text/icon | No interaction, aria-busy |

### A11y Requirements

- `role="button"` for non-native buttons
- `aria-label` when button contains only an icon
- `aria-busy="true"` when loading
- `aria-disabled="true"` when disabled (native disabled attribute also applied)
- Minimum touch target: 44x44px (WCAG 2.2 Target Size)
- Focus indicator: 2px solid blue-500 with 2px offset

### Keyboard Support

| Key | Action |
|---|---|
| Enter | Activates button |
| Space | Activates button |
| Tab | Moves focus to next focusable element |
| Shift+Tab | Moves focus to previous focusable element |

---

## Text Fields

### Purpose

Single-line text input for user data entry.

### Variants

| Variant | Purpose | Features |
|---|---|---|
| Standard | General text input | Label, helper text, validation |
| Password | Secret text input | Show/hide toggle, strength indicator |
| Search | Search queries | Clear button, search icon, debounced |
| Number | Numeric input | Increment/decrement buttons, min/max |
| Email | Email addresses | Validation, autocomplete |

### States

| State | Border | Background | Label | Helper |
|---|---|---|---|---|
| Default | gray-200 | white | gray-900 | gray-500 |
| Hover | gray-300 | white | gray-900 | gray-500 |
| Focus | blue-500 | white | gray-900 | gray-500 |
| Filled | gray-200 | white | gray-900 | gray-500 |
| Error | red-500 | red-50 | red-600 | red-500 |
| Success | green-500 | green-50 | green-600 | green-500 |
| Disabled | gray-200 | gray-50 | gray-400 | gray-400 |

### Anatomy

```
┌──────────────────────────────────┐
│ Label *                          │  (always visible, not placeholder)
├──────────────────────────────────┤
│ [icon] Input text...    [clear]  │  Input area
├──────────────────────────────────┤
│ Helper text or error message     │  (associated via aria-describedby)
└──────────────────────────────────┘
```

### A11y Requirements

- Visible `<label>` element associated via `htmlFor`/`id`
- Never use placeholder as label — placeholder disappears on focus
- `aria-invalid="true"` on error state
- `aria-describedby` points to helper/error text
- `aria-required="true"` for required fields
- Error messages announced via `aria-live="polite"` on change
- Autocomplete attributes for common fields (name, email, etc.)

---

## Dropdowns / Select

### Purpose

Choose one or more options from a list.

### Variants

| Variant | Purpose | Behavior |
|---|---|---|
| Select | Single selection | Click to open, select one |
| Multi-select | Multiple selections | Tags show selected, dropdown stays open |
| Searchable | Long option lists | Type to filter options |
| Cascading | Dependent options | Selecting parent filters children |

### A11y Requirements

- `role="combobox"` on trigger, `role="listbox"` on dropdown
- `aria-expanded` toggles on open/close
- `aria-activedescendant` tracks highlighted option
- Arrow keys navigate options, Enter selects, Escape closes
- Selected option has `aria-selected="true"`
- Group labels use `role="group"` with `aria-labelledby`
- Search input has `aria-label="Filter options"`

---

## Tables

### Purpose

Display tabular data with sorting, filtering, and bulk actions.

### Variants

| Variant | Purpose | Features |
|---|---|---|
| Basic | Simple data display | Static columns, no interaction |
| Sortable | Click-to-sort columns | Sort indicators, multi-sort |
| Filterable | Column filtering | Filter chips, filter builder |
| Paginated | Large datasets | Page size selector, pagination |
| Selectable | Row selection | Checkbox column, bulk actions |
| Compact | Dense data | Reduced row height |

### A11y Requirements

- `<table>` with `<thead>`, `<tbody>`, `<tfoot>` semantics
- `scope="col"` on column headers
- `scope="row"` on row headers (when applicable)
- `<caption>` or `aria-label` describing the table
- Sort buttons: `aria-sort="ascending"|"descending"|"none"`
- Sortable columns announce sort state change via `aria-live`
- Row selection: `aria-selected` on rows, `aria-label="Select row {name}"`
- Bulk actions toolbar announced when selection is active

### Keyboard Support

| Key | Action |
|---|---|
| Tab | Move between interactive table elements |
| Arrow keys | Navigate cells (when cell navigation enabled) |
| Enter | Activate cell action (link, button) |
| Space | Toggle row selection (when selectable) |
| Ctrl+A | Select all rows (when selectable) |
| Escape | Clear selection, close filters |

---

## Cards

### Purpose

Container for grouped content with optional actions.

### Variants

| Variant | Usage | Features |
|---|---|---|
| Content | Article, post, note | Title, body, metadata |
| Dashboard | Dashboard widgets | Header, content, footer |
| Course | Course listing | Thumbnail, title, progress, stats |
| Profile | User profile | Avatar, name, role, details |
| Stat | KPI display | Value, label, trend indicator |

### Anatomy

```
┌──────────────────────────────────┐
│ [Icon] Title              [Menu] │  Header (optional)
├──────────────────────────────────┤
│                                  │
│          Card Content            │  Body
│                                  │
├──────────────────────────────────┤
│ Footer / Actions                 │  Footer (optional)
└──────────────────────────────────┘
```

### A11y Requirements

- `role="article"` for content cards, `role="region"` for dashboard cards
- `aria-label` describing card purpose
- Interactive cards have `tabindex="0"` and keyboard activation
- Card headings use appropriate heading level (h3, h4, etc.)
- Progress indicators have `aria-valuenow`, `aria-valuemin`, `aria-valuemax`

---

## Lists

### Purpose

Display ordered or unordered collections of items.

### Variants

| Variant | Purpose | Features |
|---|---|---|
| Simple | Static list | Basic list rendering |
| Interactive | Clickable items | Hover, focus, selection states |
| Drag-sortable | Reorderable items | Drag handle, drop indicators |
| Navigation | Sidebar navigation | Active state, nested items |

### A11y Requirements

- Semantic `<ul>` or `<ol>` elements
- Interactive items have `role="button"` or are `<a>` elements
- Drag-sortable: `aria-grabbed`, `aria-dropeffect`, live announcements for reorder
- Active item: `aria-current="page"` for navigation lists

---

## Tabs

### Purpose

Switch between views within the same context.

### Variants

| Variant | Purpose | Orientation |
|---|---|---|
| Horizontal | Default tab interface | horizontal |
| Vertical | Sidebar tabs | vertical |
| Closable | Editor tabs | horizontal, with close buttons |

### Anatomy

```
┌──────┬──────┬──────┬──────┬────┐
│ Tab1 │ Tab2 │ Tab3 │ Tab4 │ [+]│  Tab bar
├──────┴──────┴──────┴──────┴────┤
│                                  │
│          Tab Panel              │  Content
│                                  │
└──────────────────────────────────┘
```

### A11y Requirements

- `role="tablist"` on tab bar, `role="tab"` on each tab, `role="tabpanel"` on panels
- `aria-selected="true"` on active tab
- `aria-controls` linking tab to its panel
- `aria-labelledby` linking panel to its tab
- Arrow keys navigate between tabs
- Home/End go to first/last tab
- Tab key moves focus into the panel content

---

## Dialogs

### Purpose

Modal overlay for focused tasks requiring user attention.

### Variants

| Variant | Purpose | Size | Close |
|---|---|---|---|
| Confirmation | Confirm destructive action | 400px | Cancel button, Escape |
| Form | Data entry | 480px | Cancel button, Escape |
| Full-screen | Immersive tasks | 100vw | Close button, Escape |
| Alert | System notification | 360px | OK button, Escape |

### A11y Requirements

- `role="dialog"` and `aria-modal="true"` on dialog container
- `aria-labelledby` pointing to dialog title
- `aria-describedby` pointing to dialog description (when present)
- Focus trapped within dialog (Tab wraps at boundaries)
- Focus moves to first focusable element on open
- Focus returns to trigger element on close
- Escape closes the dialog
- Clicking backdrop closes (unless action is in-progress)
- Screen reader announces dialog title on open

---

## Toasts / Notifications

### Purpose

Brief, non-blocking feedback about an operation.

### Variants

| Variant | Icon | Color | Usage |
|---|---|---|---|
| Success | Check | green | Operation completed |
| Error | X-circle | red | Operation failed |
| Warning | Alert triangle | amber | Potential issue |
| Info | Info | blue | Informational message |

### Anatomy

```
┌──────────────────────────────────┐
│ [icon] Message text    [action] [x] │
└──────────────────────────────────┘
```

### A11y Requirements

- `role="status"` for success/info, `role="alert"` for error/warning
- `aria-live="polite"` for non-urgent, `aria-live="assertive"` for errors
- Auto-dismiss after 5 seconds (except errors — manual dismiss only)
- Pause auto-dismiss on hover or keyboard focus
- Action button within toast is keyboard accessible
- Dismiss button has `aria-label="Dismiss notification"`
- Maximum 3 visible toasts, stacked from top-right

---

## Tooltips

### Purpose

Provide additional context on hover or focus.

### Variants

| Variant | Purpose | Content |
|---|---|---|
| Simple | Brief label | Plain text |
| Rich | Detailed info | Formatted text, links |
| Interactive | Actionable hint | Text with clickable action |

### A11y Requirements

- `role="tooltip"` on tooltip container
- `aria-describedby` on trigger pointing to tooltip id
- Tooltip appears on focus (not just hover)
- Escape dismisses tooltip
- Tooltip does not obscure the trigger element
- Delay: 300ms on hover, 0ms on focus

---

## Progress Indicators

### Purpose

Show completion status or loading state.

### Variants

| Variant | Usage | Display |
|---|---|---|
| Linear | Known progress | Bar from 0% to 100% |
| Circular | Compact progress | Ring filling |
| Steps | Multi-step process | Numbered circles with connectors |
| Indeterminate | Unknown progress | Animated bar/ring |

### A11y Requirements

- `role="progressbar"` on progress elements
- `aria-valuenow`, `aria-valuemin`, `aria-valuemax` for determinate
- `aria-label` describing what is progressing
- `aria-busy="true"` for indeterminate loading
- Animations respect `prefers-reduced-motion`

---

## Badges

### Purpose

Display status, count, or label information.

### Variants

| Variant | Purpose | Display |
|---|---|---|
| Status | Current state | Dot + text (e.g., "Online") |
| Count | Numeric count | Number in circle |
| Dot | Simple indicator | Small colored circle |
| Label | Categorical tag | Colored background + text |

### A11y Requirements

- `aria-label` for status badges describing the state
- Color is never the only indicator — always paired with text or icon
- Count badges: `aria-label="{count} items"` or contextual label

---

## Navigation Components

### Breadcrumbs

```
aria-label="Breadcrumb"
ol > li > a (current: aria-current="page")
```

### Pagination

```
role="navigation" aria-label="Pagination"
Previous / page numbers / Next
aria-current="page" on active page
```

### Steps

```
role="list" aria-label="Progress steps"
li[role="listitem"] with aria-current="step" for current
Completed: aria-label="Step {n}: {title} (completed)"
Current: aria-current="step"
Upcoming: aria-label="Step {n}: {title} (not started)"
```

---

## Feedback Components

### Empty States

- Centered illustration/icon
- Heading describing the empty state
- Description explaining why it's empty
- Primary action to resolve (e.g., "Create your first course")
- Secondary action (e.g., "Learn more")

### Loading States

- Skeleton screens for content areas (matches expected layout)
- Spinner for buttons and small operations
- Progress bar for known-duration operations
- `aria-busy="true"` on loading containers
- `aria-live="polite"` announcing "Loading..." for screen readers

### Error Boundaries

- Friendly error message (not stack trace)
- Illustration or icon
- "What happened" heading
- Brief explanation of the error
- "What to try" section with actionable steps
- "Try again" button (retries the failed operation)
- "Go to dashboard" link as fallback

---

## Component Accessibility Checklist

Every component must pass this checklist before inclusion in the library:

- [ ] Keyboard accessible — all interactions possible without mouse
- [ ] Focus visible — 2px solid ring with 2px offset on all focusable elements
- [ ] ARIA attributes — correct roles, states, and properties
- [ ] Screen reader tested — JAWS, NVDA, VoiceOver
- [ ] Color independence — meaning conveyed by more than color alone
- [ ] Contrast ratios — all text meets WCAG AA (4.5:1 normal, 3:1 large)
- [ ] Target size — minimum 44x44px for interactive elements
- [ ] Responsive — usable at all breakpoints and zoom levels
- [ ] Theme support — works in light, dark, and high-contrast themes
- [ ] Reduced motion — animations optional via prefers-reduced-motion
- [ ] Documentation — usage guidelines, examples, and a11y notes

---

*Every component is a contract with the user. It must deliver on accessibility, consistency, and usability without exception.*
