# AuthShield Lab — Table & Data Grid Standards

> Data table, grid, and list view standards for all tabular data in AuthShield Lab.

---

## 1. Table Structure

### Anatomy

```
+--+----------------+----------------+--------------+----------+----------+
|  | Column Header  | Column Header  | Col Header   | Col Hdr  | Col Hdr  |
|  | (sortable)     | (sortable)     | (sortable)   |          | (sortable|
+--+----------------+----------------+--------------+----------+----------+
| [x]| Row 1 Data   | Row 1 Data     | Row 1 Data   | Row 1    | Actions  |
+--+----------------+----------------+--------------+----------+----------+
| [ ]| Row 2 Data   | Row 2 Data     | Row 2 Data   | Row 2    | Actions  |
+--+----------------+----------------+--------------+----------+----------+
| [x]| Row 3 Data   | Row 3 Data     | Row 3 Data   | Row 3    | Actions  |
+--+----------------+----------------+--------------+----------+----------+
|    | Footer / Summary                                         |
+---------------------------------------------------------------+
```

### Table Elements

| Element        | HTML Element     | ARIA / Attributes                                    |
|----------------|------------------|------------------------------------------------------|
| Table          | `<table>`        | `role="grid"` for interactive grids                  |
| Caption        | `<caption>`      | Describes table purpose (e.g., "User management")    |
| Column Header  | `<th scope="col">` | `aria-sort` for sortable columns                  |
| Row Header     | `<th scope="row">` | For row labels in row-heavy tables                |
| Body           | `<tbody>`        |                                                      |
| Row            | `<tr>`           | `aria-selected` for selectable rows                  |
| Cell           | `<td>`           |                                                      |
| Footer         | `<tfoot>`        | Summary counts, totals                               |

---

## 2. Sorting

### Visual Indicators

```
Column Header (unsorted):     Name          ↑↓ (icon faint)
Column Header (ascending):    Name  ↑       (icon bold, up)
Column Header (descending):   Name  ↓       (icon bold, down)
```

### Behavior

| Interaction         | Result                                             |
|---------------------|----------------------------------------------------|
| Click header        | Toggle sort: none → asc → desc → none              |
| Shift+Click header  | Add secondary sort column                           |
| Screen reader       | Announce: "Name, sorted ascending" on sort change   |
| Keyboard: Enter     | Sort by focused column header                       |
| Keyboard: Space     | Same as Enter                                       |

### Multi-Sort Display

```
+--+------------------+-------------------+-------------------+
|  | Name       ↑ 1  | Score      ↓ 2    | Date        ↑    |
+--+------------------+-------------------+-------------------+
```

Numbers `1`, `2` indicate sort priority.

---

## 3. Filtering

### Filter Row (Inline)

Row below column headers with filter inputs per column.

```
+--+----------------+----------------+--------------+----------+
|  | Name      [v]  | Status    [v]  | Role     [v] | ...     |
+--+----------------+----------------+--------------+----------+
```

### Filter Chips

Active filters shown as removable chips above the table.

```
Status: Active  [x]  |  Role: Admin  [x]  |  Clear All
+-----------------------------------------------------------+
|  (filtered table below)                                   |
+-----------------------------------------------------------+
```

### Advanced Filter Dialog

Opened via "Advanced Filter" button. Allows complex boolean queries.

```
+-----------------------------------------------------------+
|  Advanced Filter                               [Close X]  |
+-----------------------------------------------------------+
|  Show rows where:                                          |
|                                                           |
|  [Status    v]  [contains    v]  [__________]  [Remove]  |
|                                                           |
|  [AND / OR]                                               |
|                                                           |
|  [Role      v]  [equals      v]  [Admin    v]  [Remove]  |
|                                                           |
|  [+ Add Filter]                                           |
|                                                           |
|  +----------+  +-----------+                              |
|  | Cancel   |  | Apply     |                              |
|  +----------+  +-----------+                              |
+-----------------------------------------------------------+
```

---

## 4. Grouping

### Collapsible Groups

```
▼ Group: Active Users (12)
+--+----------------+----------------+--------------+----------+
| [x]| Alice        | alice@...      | Admin        | ...     |
| [ ]| Bob          | bob@...        | Editor       | ...     |
+--+----------------+----------------+--------------+----------+
▶ Group: Inactive Users (3)
```

- Arrow keys expand/collapse groups.
- Group header shows count.
- `aria-expanded="true/false"` on group toggle button.

---

## 5. Pagination

### Page Controls

```
+-----------------------------------------------------------+
|  Show [10 v] per page                                     |
|  Showing 1-10 of 156 users                                |
|                                                           |
|  [< Prev]  [1] [2] [3] ... [16]  [Next >]                |
+-----------------------------------------------------------+
```

### Page Size Options

Default: 10, 25, 50, 100 per page.

### Keyboard

| Key            | Behavior                           |
|----------------|-------------------------------------|
| Arrow Left     | Previous page                       |
| Arrow Right    | Next page                           |
| Home           | First page                          |
| End            | Last page                           |

### Cursor-Based Pagination

For APIs with cursor-based pagination, display "Load More" instead of page numbers.

```
+-----------------------------------------------------------+
|  Showing 25 of 156 users                                  |
|  [Load More]                                              |
+-----------------------------------------------------------+
```

---

## 6. Column Features

### Column Reorder

Drag column header to reorder. Visual feedback: ghost column follows cursor.

### Column Resize

Drag right border of column header to resize. Minimum width: 60px. Show resize cursor.

### Column Show/Hide (Column Picker)

Gear icon or dropdown in table toolbar. Checkboxes to toggle column visibility.

```
+-------------------------------+
|  Columns                      |
|  [x] Name                     |
|  [x] Email                    |
|  [ ] Phone                    |
|  [x] Role                     |
|  [x] Status                   |
|  [ ] Created Date             |
|  [x] Actions                  |
+-------------------------------+
```

### Column Pin

Pin columns left or right. Pinned columns stay visible during horizontal scroll.

```
| Pinned Left       | Scrollable Columns      | Pinned Right |
| Name | Email      | Role | Status | Date   | Actions      |
```

---

## 7. Keyboard Navigation

| Key                | Behavior                                           |
|--------------------|----------------------------------------------------|
| Arrow keys         | Move between cells (left/right/up/down)            |
| Enter              | Activate cell (open edit, follow link)             |
| Space              | Toggle row selection                               |
| Ctrl+A             | Select all visible rows                            |
| Tab                | Move to next focusable section (toolbar, pagination)|
| Shift+Tab          | Move to previous section                           |
| Home               | First cell in row                                  |
| End                | Last cell in row                                   |
| Ctrl+Home           | First cell in table                                |
| Ctrl+End            | Last cell in table                                 |
| Escape             | Exit cell editing, close dropdown                  |
| F2                 | Enter cell editing mode                            |

---

## 8. Accessible Headers

```html
<table aria-label="User management">
  <caption>Active users in the system with roles and status</caption>
  <thead>
    <tr>
      <th scope="col">Name</th>
      <th scope="col">Email</th>
      <th scope="col">Role</th>
      <th scope="col">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Alice Johnson</th>
      <td>alice@example.com</td>
      <td>Admin</td>
      <td>Active</td>
    </tr>
  </tbody>
</table>
```

---

## 9. Bulk Selection

### Checkbox Column

```
+--+----------+----------------+----------------+----------+----------+
| [ ]| Select | Name           | Email          | Role     | Status   |
|    | All    |                |                |          |          |
+--+----------+----------------+----------------+----------+----------+
| [x]|        | Alice Johnson  | alice@...      | Admin    | Active   |
| [x]|        | Bob Smith      | bob@...        | Editor   | Active   |
| [ ]|        | Carol White    | carol@...      | Viewer   | Inactive |
+--+----------+----------------+----------------+----------+----------+
```

### Bulk Actions Toolbar

Appears when rows are selected. Replaces or overlays the table toolbar.

```
+-----------------------------------------------------------+
|  2 selected    [Delete] [Export] [Change Role]  [Clear]   |
+-----------------------------------------------------------+
```

- `aria-live="polite"` announces selection count change.
- `Escape` clears selection.

---

## 10. Export

Toolbar buttons for data export.

```
+-----------------------------------------------------------+
|  [+ Add User]  [Filter]  [Export v]  [Columns v]          |
+-----------------------------------------------------------+
```

Export dropdown:

```
+-------------------+
| Export            |
| Export as CSV     |
| Export as JSON    |
| Export as PDF     |
+-------------------+
```

- Export respects current filters and sort.
- Export respects column visibility.
- Large exports show progress indicator.

---

## 11. Responsive Behavior

### Standard (≥1024px)

Full table with all columns visible.

### Narrow (768-1023px)

Horizontal scroll. Pinned columns remain visible.

```
| Pinned | ← Scrollable →                    |
| Name   | Email | Role | Status | ...      |
+--------+-------+------+------+-----------+
| Alice  | alice | Admin| Active|           |
```

### Very Narrow (<768px)

Stacked card view. Each row becomes a card.

```
+-------------------------------------------+
|  Alice Johnson                     [x]    |
|  alice@example.com                        |
|  Role: Admin                              |
|  Status: Active                           |
|  [Edit]  [Delete]                         |
+-------------------------------------------+
|  Bob Smith                          [ ]    |
|  bob@example.com                          |
|  Role: Editor                             |
|  Status: Active                           |
|  [Edit]  [Delete]                         |
+-------------------------------------------+
```

---

## 12. Empty State

When no data matches current filters or the table is empty.

```
+-----------------------------------------------------------+
|                                                           |
|                     (icon/illustration)                   |
|                                                           |
|              No users found                               |
|   Try adjusting your filters or create a new user.        |
|                                                           |
|                  [+ Create User]                          |
|                                                           |
+-----------------------------------------------------------+
```

---

## 13. Loading State

Skeleton rows during data fetch.

```
+--+----------------+----------------+--------------+----------+
|  | Name           | Email          | Role         | Status   |
+--+----------------+----------------+--------------+----------+
|  | ████████████   | ██████████████ | ████████     | ████████ |
|  | ████████████   | ██████████████ | ████████     | ████████ |
|  | ████████████   | ██████████████ | ████████     | ████████ |
|  | ████████████   | ██████████████ | ████████     | ███████K |
+--+----------------+----------------+--------------+----------+
```

Skeleton rows animate with a shimmer effect. `aria-busy="true"` on the table.

---

## 14. Error State

When data fetch fails.

```
+-----------------------------------------------------------+
|                                                           |
|                     (error icon)                          |
|                                                           |
|              Unable to load users                         |
|   There was a problem fetching the data.                  |
|   Please check your connection and try again.             |
|                                                           |
|                   [Retry]                                 |
|                                                           |
+-----------------------------------------------------------+
```

---

## 15. Row Actions

### Context Menu (Right-Click)

```
+-------------------+
| View              |
| Edit              |
| Duplicate         |
| ---                |
| Change Role       |
| Reset Password    |
| ---                |
| Delete            |
+-------------------+
```

### Action Column (Dropdown)

```
+----------+----------------+----------------+--------------+------+--------+
| Name     | Email          | Role           | Status       |      | Actions|
+----------+----------------+----------------+--------------+------+--------+
| Alice    | alice@...      | Admin          | Active       |      | [...v] |
+----------+----------------+----------------+--------------+------+--------+
```

Dropdown:

```
+-------------------+
| View              |
| Edit              |
| ---                |
| Delete            |
+-------------------+
```

---

## 16. Complete Data Grid Wireframe

```
+-----------------------------------------------------------+
|  User Management                                           |
|  Manage all users in the system.                           |
+-----------------------------------------------------------+
|  [+ Add User]  [Filter]  [Export v]  [Columns v]          |
+-----------------------------------------------------------+
|  Status: Active  [x]  |  Role: Admin  [x]  |  Clear All   |
+-----------------------------------------------------------+
|                                                           |
|  +--+----------+----------------+----------------+-------+
|  |  | Name  ↑↓ | Email      ↑↓ | Role       ↑↓  | Stat  |
|  +--+----------+----------------+----------------+-------+
|  |Filter:       |Filter:         |Filter: [v]      |Fil[v] |
|  +--+----------+----------------+----------------+-------+
|  |[x]| Alice   | alice@...      | Admin           | Active|
|  +--+----------+----------------+----------------+-------+
|  |[ ]| Bob     | bob@...        | Editor          | Active|
|  +--+----------+----------------+----------------+-------+
|  |[x]| Carol   | carol@...      | Viewer          | Inact |
|  +--+----------+----------------+----------------+-------+
|                                                           |
|  +-------------------------------------------------------+
|  | 2 selected  [Delete] [Export] [Change Role]   [Clear] |
|  +-------------------------------------------------------+
|                                                           |
|  Showing 1-3 of 42 users        [< Prev] [1][2]..[5][Next]|
+-----------------------------------------------------------+
```

---

## 17. Data Grid Component API

| Prop             | Type       | Description                                  |
|------------------|------------|----------------------------------------------|
| `columns`        | Column[]   | Column definitions                           |
| `data`           | Row[]      | Row data                                     |
| `sortable`       | boolean    | Enable column sorting                        |
| `filterable`     | boolean    | Enable column filtering                      |
| `selectable`     | boolean    | Enable row selection                         |
| `pagination`     | Pagination | Pagination configuration                     |
| `groupBy`        | string     | Column key to group by                       |
| `onSort`         | function   | Sort change handler                          |
| `onFilter`       | function   | Filter change handler                        |
| `onSelect`       | function   | Selection change handler                     |
| `onRowClick`     | function   | Row click handler                            |
| `onExport`       | function   | Export handler                               |
| `loading`        | boolean    | Show loading skeleton                        |
| `emptyMessage`   | string     | Message when no data                         |
| `caption`        | string     | Accessible table caption                     |

---

*Last updated: 2026-07-19 — AuthShield Lab UI Standards*
