# AuthShield Lab — Visualization Standards

> Chart types, report visuals, and data visualization standards for AuthShield Lab.

---

## 1. Chart Types Overview

| Chart Type     | Use Case                                | Max Categories |
|----------------|-----------------------------------------|----------------|
| Bar (vertical) | Comparing discrete values               | 12             |
| Bar (horizontal)| Long category labels                   | 12             |
| Stacked Bar    | Part-to-whole across categories         | 6 segments     |
| Grouped Bar    | Comparing sub-categories                | 4 per group    |
| Line           | Trends over time                        | 6 lines        |
| Pie            | Part-to-whole (single snapshot)         | 8 slices       |
| Heat Map       | Density / intensity across 2 dimensions | 20x20 cells    |
| Progress Bar   | Completion percentage                   | N/A            |
| Ring/Donut     | Single or few completion values         | 1              |
| Gauge          | Single metric vs target                 | N/A            |
| Traffic Light  | Status indicator (RAG)                  | N/A            |

---

## 2. Bar Charts

### Vertical Bar (Default)

Best for comparing values across discrete categories.

```
  Users per Role
  30 |
     |     [##]
  25 |     [##]
     |     [##]    [##]
  20 |     [##]    [##]
     | [##] [##]    [##]
  15 | [##] [##]    [##]
     | [##] [##]    [##]    [##]
  10 | [##] [##]    [##]    [##]
     | [##] [##]    [##]    [##]
   5 | [##] [##]    [##]    [##]
     | [##] [##]    [##]    [##]
   0 +---------------------------+
      Admin  Editor  Viewer  Guest
```

**When to use:** Comparing quantities across 2-12 categories.
**Data:** One categorical axis, one numeric axis.

### Horizontal Bar

Use when category labels are long or when there are many categories.

```
  Course Completions
  Phishing 101   [##############] 287
  Network Sec    [#############]  245
  Incident Resp  [############]   212
  Malware Det    [##########]     178
  Crypto Basics  [########]       142
  Forensics      [######]          98
  +--+--+--+--+--+--+--+--+--+--+
  0     50    100   150   200   250  300
```

### Stacked Bar

Show composition of each category.

```
  Course Enrollment by Status
  100% |  [###]  [###]  [###]
       |  [###]  [###]  [###]
   75% |  [###]  [###]  [###]
       |  [###]  [###]  [###]
   50% |  [###]  [###]  [###]
       |  [###]  [###]  [###]
   25% |  [###]  [###]  [###]
       |  [###]  [###]  [###]
    0% +------------------------+
         Q1      Q2      Q3

  Legend: [Completed] [In Progress] [Not Started]
```

### Grouped Bar

Compare sub-categories side by side.

```
  Assessment Scores by Department
  90 |  [##] [##]    [##] [##]
     |  [##] [##]    [##] [##]
  80 |  [##] [##]    [##] [##]
     |  [##] [##]    [##] [##]
  70 |  [##] [##]    [##] [##]
     |  [##] [##]    [##] [##]
  60 |  [##] [##]    [##] [##]
     +---------------------------+
       Eng    QA      Ops   HR

  Legend: [Avg Score] [Pass Rate]
```

---

## 3. Line Charts

### Single Line

Show trend over time.

```
  Login Attempts (7 days)
  500 |          *
      |        *   *
  400 |      *       *
      |    *           *
  300 |  *               *
      | *                   *
  200 |*                     *
      +--+--+--+--+--+--+--+--+
       Mon Tue Wed Thu Fri Sat Sun
```

### Multi-Line

Compare multiple series over the same time period.

```
  User Activity (30 days)
  200 |*                           *
      | *                        *
  150 |  *  *                   *
      |    * *                *
  100 |      * *           *
      |        * *      *
   50 |          * * *
      +--+--+--+--+--+--+--+--+--+
       W1  W2  W3  W4  W5  W6  W7  W8

  Legend: [Active Users] [New Signups] [Logins]
  Line styles: solid, dashed, dotted
```

### Area Fill

Optional: fill area under line for emphasis. Use low opacity (0.1-0.2).

---

## 4. Pie / Donut Charts

### Guidelines

- Maximum 8 slices. Group remaining into "Other".
- Start largest slice at 12 o'clock, proceed clockwise.
- Always include a legend.
- Show percentage labels on slices >5%.
- Prefer donut over pie for modern aesthetic.

```
       +-----------+
      /  Admin 12%  \
     |  +---------+  |
     |  | Editor  |  |
     |  |   28%   |  |
     |  +---------+  |
     | Viewer 45%    |
      \  Other 15%  /
       +-----------+

  Legend:
  [■] Admin (12%)   [■] Editor (28%)
  [■] Viewer (45%)  [■] Other (15%)
```

---

## 5. Heat Maps

Use for density/intensity data across two dimensions (e.g., login attempts by hour/day).

```
  Login Attempts by Hour and Day

          Mon  Tue  Wed  Thu  Fri  Sat  Sun
  00:00   ░░   ░░   ░░   ░░   ░░   ░░   ░░
  04:00   ░░   ░░   ░░   ░░   ░░   ░░   ░░
  08:00   ▒▒   ▒▒   ▓▓   ▒▒   ▒▒   ░░   ░░
  12:00   ▒▒   ▓▓   ▓▓   ▓▓   ▒▒   ░░   ░░
  16:00   ▓▓   ▓▓   ██   ▓▓   ▒▒   ░░   ░░
  20:00   ▒▒   ▒▒   ▒▒   ▒▒   ░░   ░░   ░░

  Legend: ░ Low  ▒ Medium  ▓ High  █ Critical
```

### Color Scale

- Use a sequential color scale (light → dark).
- Colorblind-safe palette: use blues or viridis scale.
- Always include a legend with labeled thresholds.

---

## 6. Trend Graphs

### Time Series with Trend Line

```
  Vulnerability Discoveries (12 months)
  30 |        *
     |      *   *    _-----_ trend
  25 |    *       *-/        \
     |  *                       *
  20 |*                          *
     |                             *
  15 |                              *
     |                                *
  10 |                                 *
     +--+--+--+--+--+--+--+--+--+--+--+
      J  F  M  A  M  J  J  A  S  O  N  D
```

### Annotations

Mark significant events on the chart with vertical lines or callouts.

```
  25 |     *    |     *
     |   *   *  |   *   *
  20 | *       *|*       *        ← Policy change
     |          |                  (annotation)
  15 |          |
     +--+--+--+--+--+--+--+--+
      J  F  M  A  M  J  J  A
              ^
              Breach detected
```

---

## 7. Progress Charts

### Progress Bar

```
  Course Completion: 72%
  [#############============] 72%
```

### Ring Chart

```
       +--------+
      /  +----+  \
     |  |      |  |
     |  | 72%  |  |
     |  |      |  |
      \  +----+  /
       +--------+
```

### Completion Indicator (Multiple)

```
  Module Progress
  [x] Introduction to Security     ✓ Complete
  [x] Network Fundamentals         ✓ Complete
  [ ] Cryptography Basics          In Progress (45%)
  [ ] Incident Response            Not Started
  [ ] Forensics Fundamentals       Not Started
```

---

## 8. Risk Indicators

### Traffic Light (RAG)

```
  Status          Indicator
  Low Risk        [GREEN]   (safe, passed, nominal)
  Medium Risk     [AMBER]   (warning, attention needed)
  High Risk       [RED]     (critical, failure, danger)
```

Never use color alone. Always include text label or icon.

```
  [●] Low       (green circle)
  [●] Medium    (amber circle)
  [●] High      (red circle)
```

### Gauge Chart

```
      +-------------------+
     /    Medium Risk     \
    /         ↓            \
   |    [needle]            |
   |     ◄──●               |
   |  Low  | Med  | High    |
    \                     /
     +-------------------+
      0%    50%    100%
```

---

## 9. Learning Analytics

### Completion Rates

```
  Course Completion Rates
  Phishing Awareness     [#############============] 72%
  Network Security       [#########================] 48%
  Incident Response      [##########################] 95%
  Cryptography           [==========================]  0%
  +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
  0%       25%       50%       75%      100%
```

### Score Distribution

```
  Assessment Score Distribution
  30 |  [##]
     |  [##]
  25 |  [##] [##]
     |  [##] [##]
  20 |  [##] [##]
     |  [##] [##] [##]
  15 |  [##] [##] [##]
     |  [##] [##] [##] [##]
  10 |  [##] [##] [##] [##]
     |  [##] [##] [##] [##] [##]
   5 |  [##] [##] [##] [##] [##]
     |  [##] [##] [##] [##] [##]
   0 +--+--+--+--+--+--+--+--+--+
     0-20 21-40 41-60 61-80 81-100
          Score Range
```

### Time Spent

```
  Average Time per Module (minutes)
  Intro          ████████               12m
  Networking     ████████████████       24m
  Crypto         ████████████████████   32m
  Incident Resp  ██████████████████     28m
  Forensics      ████████████████████   30m
```

---

## 10. Accessibility Requirements (ALL Charts)

### 10.1 Data Table Alternative

**Every chart must have a "View as Table" toggle or link.**

```
+-----------------------------------------------------------+
|  Course Completion Rates              [Chart] [Table]      |
+-----------------------------------------------------------+
|  (chart display here)                                      |
|                                                           |
|  [View data as table]                                     |
+-----------------------------------------------------------+
```

Table alternative:

```
+-----------------------------------------------------------+
|  Course Completion Rates                                  |
|  +--------------------------------------------+----+-----+|
|  | Course              | Enrolled | Completed | %   |     ||
|  +--------------------------------------------+----+-----+|
|  | Phishing Awareness  | 100      | 72        | 72% |     ||
|  | Network Security    | 80       | 38        | 48% |     ||
|  | Incident Response   | 60       | 57        | 95% |     ||
|  | Cryptography        | 45       | 0         | 0%  |     ||
|  +--------------------------------------------+----+-----+|
+-----------------------------------------------------------+
```

### 10.2 ARIA Labels

```html
<div role="img" aria-label="Bar chart showing course completion rates: Phishing Awareness 72%, Network Security 48%, Incident Response 95%, Cryptography 0%">
  <svg>...</svg>
</div>
```

### 10.3 Keyboard Navigation

| Key            | Behavior                                       |
|----------------|-------------------------------------------------|
| Tab            | Focus the chart container                       |
| Arrow keys     | Move between data points                        |
| Enter          | Show tooltip/details for focused point          |
| Escape         | Hide tooltip, return focus to chart              |
| Home           | First data point                                |
| End            | Last data point                                 |

Data points must be focusable: `tabindex="0"` on each point element.

### 10.4 High Contrast Mode

- Use patterns in addition to colors (stripes, dots, crosshatch).
- Ensure sufficient contrast ratio (4.5:1 for text, 3:1 for graphical elements).
- Provide pattern swatches in legend.

```
  Legend:
  [////] Series A (striped)
  [::::] Series B (dotted)
  [XXXX] Series C (crosshatch)
  [    ] Series D (solid)
```

### 10.5 Color-Independent Indicators

Always pair color with at least one other visual cue:

- Shape (circles, squares, triangles)
- Pattern (solid, striped, dotted)
- Label (text on or near the element)
- Icon (checkmark, warning triangle)

### 10.6 Screen Reader Description

Provide a concise summary of chart data via `aria-describedby` or a visually hidden description.

```html
<div class="sr-only" id="chart-desc">
  Bar chart: Course completion rates.
  Phishing Awareness: 72 of 100 enrolled completed.
  Network Security: 38 of 80 enrolled completed.
  Incident Response: 57 of 60 enrolled completed.
  Cryptography: 0 of 45 enrolled completed.
  Average completion rate: 53.75%.
</div>
```

---

## 11. Chart Color Palette

### Primary Palette (Colorblind-Safe)

| Color       | Hex       | Usage                    |
|-------------|-----------|--------------------------|
| Blue        | #3B82F6   | Primary data series      |
| Amber       | #F59E0B   | Secondary data series    |
| Teal        | #14B8A6   | Tertiary data series     |
| Purple      | #8B5CF6   | Quaternary data series   |
| Slate       | #64748B   | Reference / baseline     |

### Status Colors

| Status  | Hex       | Pattern         |
|---------|-----------|-----------------|
| Success | #22C55E   | Solid           |
| Warning | #F59E0B   | Diagonal stripes|
| Error   | #EF4444   | Crosshatch      |
| Info    | #3B82F6   | Dots            |

### High Contrast Override

| Role       | Light Mode | Dark Mode |
|------------|------------|-----------|
| Text       | #1E293B    | #F1F5F9   |
| Grid lines | #E2E8F0    | #334155   |
| Background | #FFFFFF    | #0F172A   |

---

## 12. Tooltips

### Behavior

- **Hover:** Show tooltip with data value, category, and series name.
- **Focus (keyboard):** Show tooltip for focused data point.
- **Position:** Follow cursor, flip if near edge of viewport.
- **Dismiss:** Escape key or move focus away.
- **Content format:** `Category: Value (Percentage)`

### Tooltip Wireframe

```
  +-----------------------------+
  |  Phishing Awareness         |
  |  72 of 100 enrolled (72%)   |
  +-----------------------------+
              |
              ▼
            [##]
```

### Accessibility

- Tooltip content must be associated via `aria-describedby`.
- Keyboard users must be able to trigger tooltip via focus.

---

## 13. Export

All charts support export in three formats:

| Format | Use Case                    | Button Label      |
|--------|-----------------------------|-------------------|
| PNG    | Presentations, documents    | "Download PNG"    |
| SVG    | Print, scaling              | "Download SVG"    |
| CSV    | Raw data for analysis       | "Export Data"     |

Export button appears in chart toolbar (top-right corner of chart container).

---

## 14. Responsive Behavior

| Breakpoint   | Behavior                                        |
|--------------|--------------------------------------------------|
| ≥1024px      | Full chart, legend on right                      |
| 768-1023px   | Chart scales to container, legend below          |
| 480-767px    | Simplified chart (fewer labels), legend below    |
| <480px       | Data table only, chart hidden                    |

---

## 15. Chart Component API

| Prop             | Type       | Description                                  |
|------------------|------------|----------------------------------------------|
| `type`           | string     | 'bar' \| 'line' \| 'pie' \| 'heat' \| ...   |
| `data`           | object     | Chart data (labels + datasets)               |
| `title`          | string     | Chart title                                  |
| `description`    | string     | Accessible description                       |
| `height`         | number     | Chart height in px (default: 300)            |
| `colors`         | string[]   | Override color palette                        |
| `showLegend`     | boolean    | Show/hide legend (default: true)              |
| `showGrid`       | boolean    | Show/hide grid lines                          |
| `interactive`    | boolean    | Enable hover/focus tooltips                   |
| `exportable`     | boolean    | Show export buttons                           |
| `tableAlternative`| boolean  | Show "View as Table" toggle                   |
| `loading`        | boolean    | Show loading state                            |
| `error`          | string     | Error message to display                      |

---

*Last updated: 2026-07-19 — AuthShield Lab UI Standards*
