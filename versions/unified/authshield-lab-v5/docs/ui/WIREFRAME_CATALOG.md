# AuthShield Lab — Wireframe Catalog

> Version: 1.0.0
> Last Updated: 2026-07-19
> Status: Active

---

## 1. Wireframe Notation Legend

### Symbols

| Symbol | Meaning |
|--------|---------|
| `[...]` | Interactive element (button, input, link) |
| `( )` | Radio button (unselected) |
| `(o)` | Radio button (selected) |
| `[x]` | Checkbox (checked) |
| `[ ]` | Checkbox (unchecked) |
| `+---+` | Container border |
| `|` | Vertical separator |
| `---` | Horizontal separator |
| `[v]` | Dropdown trigger |
| `[*]` | Star rating (filled) |
| `[ ]` | Star rating (empty) |
| `<< >>` | Navigation arrows |
| `[> expandable]` | Collapsed section |
| `[v collapsible]` | Expanded section |

### Dimension Notation

```
+--- 240px ---+
|             |
|  Content    |  400px height
|             |
+-------------+
```

### Spacing Notation

- `16px` = default gap between elements
- `24px` = section spacing
- `8px` = tight spacing (within component groups)
- `32px` = large section spacing

### Grid System

- Base grid: 8px
- Column gutter: 16px
- Page padding: 24px (comfortable mode)
- Card padding: 16px

---

## 2. Splash Screen Wireframes

### Medium Desktop (1366x768)

```
+--[1366px]-------------------------------------------+
|                                                      |
|  [40px title bar - empty]                            |
|                                                      |
|                                                      |
|                                                      |
|                                                      |
|              +-------------------+                   |
|              |                   |                   |
|              |  AuthShield Logo  |                   |
|              |    120 x 120      |                   |
|              |                   |                   |
|              +-------------------+                   |
|                                                      |
|                    AuthShield Lab                    |
|                      v2.4.1                          |
|                                                      |
|          +---[300px]---[8px]---+                     |
|          |[|||||||||||....] 62%|                     |
|          +--------------------+                     |
|                                                      |
|          Initializing secure environment...          |
|                                                      |
|                                                      |
+------------------------------------------------------+
  Background: #0F172A (dark navy)
  Logo: centered horizontally, 200px from title bar bottom
  Progress bar: 8px height, rounded corners (4px radius)
  Text color: #F1F5F9, font-size: 14px
  Status text: #94A3B8, font-size: 13px
```

### Large Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|                                                      |
|  [40px title bar]                                    |
|                                                      |
|                                                      |
|                                                      |
|                                                      |
|              +-------------------+                   |
|              |                   |                   |
|              |  AuthShield Logo  |                   |
|              |    140 x 140      |                   |
|              |                   |                   |
|              +-------------------+                   |
|                                                      |
|                    AuthShield Lab                    |
|                      v2.4.1                          |
|                                                      |
|          +---[350px]---[8px]---+                     |
|          |[|||||||||||....] 62%|                     |
|          +--------------------+                     |
|                                                      |
|          Initializing secure environment...          |
|                                                      |
|                                                      |
+------------------------------------------------------+
  Logo scaled up to 140px
  Progress bar width: 350px
```

---

## 3. Welcome Screen Wireframes

### Medium Desktop (1366x768)

```
+--[1366px]-------------------------------------------+
|  [Logo 160x28]                        [⚙] [?]      |  48px header
+--[64px]--+--[240px]--+--[1062px]--------------------+
|          |           |                               |
|  NAV     |  SIDEBAR  |                               |
|  RAIL    |  (empty)  |           +-------+           |
|          |           |           | Welcome|           |
|  [🏠]   |           |           | Artwork|           |
|  [📚]   |           |           | 300x200|           |
|  [🔬]   |           |           +-------+           |
|  [📝]   |           |                               |
|  [📊]   |           |    Welcome to AuthShield Lab  |
|  [⚙]   |           |                               |
|          |           |  Your offline-first cyber-    |
|          |           |  security education platform. |
|          |           |                               |
|          |           |    +--[240px]--[44px]--+      |
|          |           |    |   Get Started ->  |      |
|          |           |    +-------------------+      |
|          |           |                               |
|          |           |    +--[240px]--[44px]--+      |
|          |           |    |  I have a license  |     |
|          |           |    +-------------------+      |
|          |           |                               |
|          |           |    +--[240px]--[44px]--+      |
|          |           |    |  Explore as Guest  |     |
|          |           |    +-------------------+      |
|          |           |                               |
|          |           |    Already have an account?   |
|          |           |         Sign In               |
|          |           |                               |
+----------+-----------+-------------------------------+
| [Online 🟢] [Student] [Saved 2m ago]   [1.2GB]      | 24px status
+------------------------------------------------------+
```

### Compact Desktop (1024x768)

```
+--[1024px]-------------------------------------------+
|  [Logo]                              [⚙] [?]        | 48px header
+--[0px]--+--[180px]--+--[844px]---------------------+
|         |           |                               |
| (rail   | SIDEBAR   |        +-------+              |
| hidden) | (compact) |        | Welcome|              |
|         |           |        | Artwork|              |
|         |           |        | 260x170|              |
|         |           |        +-------+              |
|         |           |                               |
|         |           |   Welcome to AuthShield Lab   |
|         |           |                               |
|         |           |   Your offline-first...       |
|         |           |                               |
|         |           |     +--[220px]--[40px]--+     |
|         |           |     |   Get Started ->  |     |
|         |           |     +-------------------+     |
|         |           |                               |
|         |           |     +--[220px]--[40px]--+     |
|         |           |     |  I have a license  |    |
|         |           |     +-------------------+     |
|         |           |                               |
|         |           |     +--[220px]--[40px]--+     |
|         |           |     |  Explore as Guest  |    |
|         |           |     +-------------------+     |
|         |           |                               |
|         |           |    Already have an account?   |
|         |           |         Sign In               |
+---------+-----------+-------------------------------+
| [Online 🟢] [Student] [Saved]            [1.2GB]    | 24px
+------------------------------------------------------+
  Rail collapsed, sidebar narrower, artwork smaller
```

---

## 4. License Agreement Wireframes

### Medium Dialog (600x560 centered)

```
+--[600px]-----------------------------------------+
| License Agreement                         [X]    | 48px title
+--------------------------------------------------+
|                                                  |
| +--[568px]--[300px]---------------------------+  |
| | END-USER LICENSE AGREEMENT                   |  |
| |                                             |  |
| | IMPORTANT - READ CAREFULLY:                 |  |
| |                                             |  |
| | This End-User License Agreement (EULA) is   |  |
| | a legal agreement between you and           |  |
| | AuthShield Lab for the software product     |  |
| | identified above.                           |  |
| |                                             |  |
| | 1. GRANT OF LICENSE                         |  |
| | Subject to the terms of this Agreement,     |  |
| | AuthShield Lab grants you a non-exclusive,  |  |
| | non-transferable license to use...          |  |
| |                                             |  |
| | 2. RESTRICTIONS                             |  |
| | You shall not:                              |  |
| | a) modify or reverse engineer...            |  |
| | b) rent, lease, or lend...                  |  |
| |                                             |  |
| | 3. TERMINATION                              |  |
| | This Agreement is effective until...        |  |
| |                                             |  |
| |                              [scrollbar >]   |  |
| +---------------------------------------------+  |
|                                                  |
| [x] I have read and agree to the License         |
|     Agreement                                    |
|                                                  |
| +--[180px]--+  +--[180px]--+                     |
| | Decline   |  | Continue  |                     |
| +-----------+  +-----------+                     |
|                                                  |
+--------------------------------------------------+
  Centered in viewport (not in shell)
  Background: semi-transparent overlay (#00000080)
  Dialog: white/dark background, 8px border-radius
  Shadow: 0 25px 50px -12px rgba(0,0,0,0.25)
```

---

## 5. User Login Wireframes

### Medium Desktop (1366x768)

```
+--[1366px]-------------------------------------------+
|  [Logo 160x28]                                      | 48px header
+------------------------------------------------------+
|                                                      |
|                                                      |
|                                                      |
|                  +--[400px]------------------------+  |
|                  |                                 |  |
|                  |      Sign In to AuthShield      |  |
|                  |                                 |  |
|                  |  Email Address                  |  |
|                  |  +--[368px]--[48px]-----------+  |  |
|                  |  | student@lab.edu          |  |  |
|                  |  +---------------------------+  |  |
|                  |                                 |  |
|                  |  Password                       |  |
|                  |  +--[290px]--[48px]--+ +[68px]+ |  |
|                  |  | *************     | | Show👁| |  |
|                  |  +-------------------+ +------+ |  |
|                  |                                 |  |
|                  |  [x] Remember me on this device |  |
|                  |                                 |  |
|                  |  +--[368px]--[48px]-----------+  |  |
|                  |  |        Sign In             |  |  |
|                  |  +---------------------------+  |  |
|                  |                                 |  |
|                  |    Forgot your password?        |  |
|                  |                                 |  |
|                  |  +--[368px]------------------+  |  |
|                  |  | ⚠ Invalid email or       |  |  |
|                  |  |   password.               |  |  |
|                  |  +---------------------------+  |  |
|                  |                                 |  |
|                  +---------------------------------+  |
|                                                      |
+------------------------------------------------------+
| [Online 🟢] [Student] [Saved]            [1.2GB]     |
+------------------------------------------------------+
  Centered layout, no sidebar/rail context needed
  Error banner: #FEF2F2 background, #DC2626 border-left
  Primary button: #3B82F6, hover: #2563EB
```

---

## 6. Dashboard — Student Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo 160x28]  [🔍 Search (Ctrl+K)  ───────] [👤][🔔][⚙]| 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Quick     |    Welcome back, Alex!       |
|  RAIL    | Actions   |    Here's your learning      |
|          |           |    overview for today.        |
|  [🏠]◄--| [Continue |                               |
|  [📚]   | Learning] |  +--[480px]--[220px]--+       |
|  [🔬]   |           |  |  📚 Course Card 1  |       |
|  [📝]   | [Take     |  |  Intro to Crypto  |       |
|  [📊]   | Assessment|  |  [===========] 65%|       |
|  [⚙]   |           |  |  Last: 2h ago     |       |
|          | [Start    |  +-------------------+       |
|          | Simulation|                               |
|          |           |  +--[480px]--[220px]--+       |
|          | Upcoming:  |  |  📚 Course Card 2  |       |
|          | ──────────|  |  Network Security  |       |
|          | ⏰ Quiz 2 |  |  [========....] 30%|      |
|          |  in 2h    |  |  Last: 1d ago      |      |
|          |           |  +-------------------+       |
|          | 📅 Lab 3  |                               |
|          |  due 7/21 |  +--[480px]--[220px]--+       |
|          |           |  |  📚 Course Card 3  |       |
|          | Recent:   |  |  Web App Security  |       |
|          | ──────────|  |  [==============] 90%|     |
|          | ✅ Lesson |  |  Last: 3d ago      |      |
|          |  3.2 done |  +-------------------+       |
|          |  2h ago   |                               |
|          |           |  +--[480px]--[220px]--+       |
|          | 📝 Quiz 1 |  |  📚 Course Card 4  |       |
|          |  85%      |  |  Forensics 101     |       |
|          |  yesterday|  |  [................] 0%|    |
|          |           |  |  Not started yet   |      |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  Recent Activity:             |
|          |           |  +--[760px]--[auto]--------+  |
|          |           |  | ✅ Completed Lesson 3.2 |  |
|          |           |  |    2 hours ago           |  |
|          |           |  +-------------------------+  |
|          |           |  | 📝 Scored 85% on Quiz 1 |  |
|          |           |  |    Yesterday             |  |
|          |           |  +-------------------------+  |
|          |           |  | 🔬 Started SQL Injection |  |
|          |           |  |    3 days ago            |  |
|          |           |  +-------------------------+  |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student: alex@lab.edu]  [💾 Saved 2s] | 24px
|                        [Storage: 1.2 GB / 10 GB]     |
+------------------------------------------------------+
```

### Compact Desktop (1024x768)

```
+--[1024px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[0px]--+--[180px]--+--[844px]---------------------+
|         |           |                               |
| (rail   | Quick     |    Welcome back, Alex!        |
| hidden) | Actions   |                               |
|         |           |  +--[396px]--[180px]--+       |
|         | [Continue]|  |  📚 Course 1  |   |       |
|         |           |  |  [======] 65% |   |       |
|         | [Take     |  +-------------------+       |
|         | Quiz]     |                               |
|         |           |  +--[396px]--[180px]--+       |
|         | ⏰ Quiz 2 |  |  📚 Course 2  |   |       |
|         |  in 2h    |  |  [====] 30%   |   |       |
|         |           |  +-------------------+       |
|         | Recent:   |                               |
|         | ✅ Done   |  +--[396px]--[180px]--+       |
|         | 📝 85%    |  |  📚 Course 3  |   |       |
|         |           |  |  [=======] 90% |   |       |
|         |           |  +-------------------+       |
|         |           |                               |
|         |           |  +--[396px]--[180px]--+       |
|         |           |  |  📚 Course 4  |   |       |
|         |           |  |  [.] 0%       |   |       |
|         |           |  +-------------------+       |
|         |           |                               |
|         |           |  Recent Activity:             |
|         |           |  +--[420px]----------------+  |
|         |           |  | ✅ Lesson 3.2 - 2h ago  |  |
|         |           |  | 📝 Quiz 1 - 85% - 1d   |  |
|         |           |  +-------------------------+  |
+---------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Two-column card layout, smaller cards
```

---

## 7. Course Catalog Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Search:   |  Course Catalog              |
|  RAIL    | [Search   |  Sort: [Newest ▼]            |
|          | courses]  |                               |
|  [🏠]   |           |  +--[480px]--[280px]--+       |
|  [📚]◄--| Category: |  |  [Banner Image]    |       |
|  [🔬]   | [x] Net   |  |  Intro to Crypto   |       |
|  [📝]   | [x] Crypto|  |  by Dr. Smith      |       |
|  [📊]   | [x] Web   |  |  [Networking]      |       |
|  [⚙]   | [x] IR    |  |  12 modules, 40h   |       |
|          | [x] Malw. |  |  [Enroll]          |       |
|          | [x] Foren.|  +-------------------+       |
|          |           |                               |
|          | Level:    |  +--[480px]--[280px]--+       |
|          | ( ) Begin |  |  [Banner Image]    |       |
|          | (o) All   |  |  Network Security  |       |
|          | ( ) Inter |  |  by Prof. Lee      |       |
|          | ( ) Adv   |  |  [Networking]      |       |
|          |           |  |  8 modules, 32h    |       |
|          | Duration: |  |  [Enroll]          |       |
|          | [0] to    |  +-------------------+       |
|          | [40] hrs  |                               |
|          |           |  +--[480px]--[280px]--+       |
|          | Rating:   |  |  [Banner Image]    |       |
|          | [>=3*]    |  |  Web App Security  |       |
|          |           |  |  by Jane Doe       |       |
|          | [Clear    |  |  [Web Security]    |       |
|          |  Filters] |  |  15 modules, 50h   |       |
|          |           |  |  [Enroll]          |       |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  Showing 1-12 of 47 courses   |
|          |           |  [< 1 2 3 4 >]                |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  3-column card grid in workspace area
  Each card: 480x280px (banner 480x140, info 140px below)
  Gutter: 24px between cards
```

---

## 8. Learning Workspace Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Course:   |  Lesson 2.1: TCP/IP Basics   |
|  RAIL    | Intro to  |                               |
|          | Crypto    |  +--[1240px]--[60px]--------+  |
|  [🏠]   |           |  |  Progress: 45%           |  |
|  [📚]◄--| Module 1  |  |  [===========...........] |  |
|  [🔬]   |  ✅ L1.1 |  +---------------------------+  |
|  [📝]   |  ✅ L1.2 |                               |
|  [📊]   |  ✅ Quiz 1|  +--[1240px]--[auto]-------+  |
|  [⚙]   |           |  |                          |  |
|          | Module 2 ◄|  |  # TCP/IP Basics         |  |
|          |  📌 L2.1 ◄|  |                          |  |
|          |  [ ] L2.2|  |  The TCP/IP model is     |  |
|          |  [ ] Quiz|  |  the foundation of...    |  |
|          |           |  |                          |  |
|          | Module 3  |  |  ## The Four Layers      |  |
|          |  🔒 L3.1 |  |                          |  |
|          |  🔒 L3.2 |  |  1. Network Access       |  |
|          |  🔒 Quiz |  |     The lowest layer...  |  |
|          |           |  |                          |  |
|          | Module 4  |  |  2. Internet Layer       |  |
|          |  🔒 L4.1 |  |     Handles addressing.. |  |
|          |  🔒 L4.2 |  |                          |  |
|          |  🔒 Quiz |  |  [Code Block / Diagram]  |  |
|          |           |  |                          |  |
|          |           |  +---------------------------+  |
|          |           |                               |
|          |           |  +--[1240px]--[120px]-------+  |
|          |           |  | Notes (collapsible)      |  |
|          |           |  | [Your notes here...]     |  |
|          |           |  +---------------------------+  |
|          |           |                               |
|          |           |  [<< Previous] [Mark Complete] [Next >>] |
|          |           |                               |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Module tree uses indentation for hierarchy
  Active lesson: highlighted with accent color left border
  Locked modules: padlock icon, reduced opacity (0.5)
```

---

## 9. Simulation Workspace Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Config    |  SQL Injection Lab            |
|  RAIL    | Panel     |                               |
|          |           |  +--[936px]--[450px]--------+  |
|  [🏠]   | Scenario: |  |                          |  |
|  [📚]   | [SQL Inj  |  |   [Terminal / Browser]   |  |
|  [🔬]◄--| v2     ]  |  |                          |  |
|  [📝]   |           |  |   $ curl -X POST          |  |
|  [📊]   | Env:      |  |     http://target:8080    |  |
|  [⚙]   | [Web+DB ] |  |     -d "id=1 OR 1=1"     |  |
|          |           |  |                          |  |
|          | Difficulty|  |   <html>                  |  |
|          | [*][*][*] |  |   <title>Dashboard</title>|  |
|          |           |  |   ...                     |  |
|          | Time:     |  |                          |  |
|          | [30] min  |  |   SQL Error detected!    |  |
|          |           |  |   > You found a vuln!    |  |
|          | Options:  |  |                          |  |
|          | [x] Hints |  +---------------------------+  |
|          | [ ] Auto  |                               |
|          | [ ] Guide |  +--[936px]--[200px]--------+  |
|          |           |  | Results Panel            |  |
|          | [Start]   |  | Score: 85/100            |  |
|          | [Pause]   |  | Steps: 7/10              |  |
|          | [Reset]   |  | Attempts: 3              |  |
|          |           |  | Time: 12:34              |  |
|          | Elapsed:  |  +---------------------------+  |
|          | 12:34     |                               |
|          | Attempts: |                               |
|          | 3         |                               |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Split view: 60% terminal / 40% results
  Terminal: monospace font, dark background (#1E1E1E)
```

---

## 10. Assessment Workspace Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Back to   |  Quiz 2: Network Security    |
|  RAIL    | Course    |                               |
|          |           |  Time Remaining: [23:45]      |
|  [🏠]   | ───────── |                               |
|  [📚]   |           |  Question 3 of 10             |
|  [🔬]   | [1] ✅    |                               |
|  [📝]◄--| [2] ✅    |  What is the primary purpose  |
|  [📊]   | [3] ◄●   |  of a firewall?               |
|  [⚙]   | [4] ⚑    |                               |
|          | [5] [ ]  |  (A) To speed up internet     |
|          | [6] [ ]  |      connection               |
|          | [7] [ ]  |                               |
|          | [8] [ ]  |  (B) To filter network traffic|  <-- selected
|          | [9] [ ]  |      and block unauthorized   |
|          | [10][ ]  |      access                   |
|          |           |                               |
|          | ───────── |  (C) To encrypt data in      |
|          | Answered: |      transit                 |
|          | 2/10      |                               |
|          | Flagged:  |  (D) To store passwords      |
|          | 1         |      securely                |
|          |           |                               |
|          | [Show     |  [<< Previous]  [Next >>]     |
|          |  Flagged] |  [⚑ Flag Question]            |
|          |           |                               |
|          |           |  [Submit Assessment]          |
|          |           |                               |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Question nav: color-coded (green=answered, blue=current, yellow=flagged)
  Answer options: large clickable areas, radio buttons
  Timer: bold, red flash at 5 minutes remaining
```

---

## 11. Assessment Results Wireframes

### Medium Dialog (800x700 centered)

```
+--[800px]-------------------------------------------+
| Assessment Results                           [X]   | 48px
+----------------------------------------------------+
|                                                    |
|            +--[160px]--[160px]--+                   |
|            |                    |                   |
|            |      85/100        |                   |
|            |        85%         |                   |
|            |       PASS         |                   |
|            |                    |                   |
|            +--------------------+                   |
|                                                    |
|  Correct: 8  |  Incorrect: 2  |  Time: 18:23     |
|                                                    |
|  ─────────────────────────────────────────────     |
|                                                    |
|  Q1. What is a firewall?              [Correct]    |
|  Your answer: (B) To filter network traffic        |
|  Explanation: A firewall monitors incoming...      |
|                                                    |
|  ─────────────────────────────────────────────     |
|                                                    |
|  Q2. Which port does HTTPS use?       [Correct]    |
|  Your answer: 443                                  |
|  Explanation: HTTPS uses port 443 for secure...    |
|                                                    |
|  ─────────────────────────────────────────────     |
|                                                    |
|  Q3. What is SQL injection?           [Incorrect]  |
|  Your answer: (A) To speed up queries              |
|  Correct answer: (C) To insert malicious SQL       |
|  Explanation: SQL injection is a code injection    |
|  technique that exploits vulnerabilities...        |
|                                                    |
|  ─────────────────────────────────────────────     |
|                                                    |
|  Q4. What does IDS stand for?         [Correct]    |
|  ...                                               |
|                                                    |
|  +--[240px]--+  +--[240px]--+  +--[240px]--+      |
|  |Previous Q|  | Back to   |  |  Next Q   |      |
|  |          |  |  Course   |  |           |      |
|  +----------+  +-----------+  +-----------+      |
|                                                    |
+----------------------------------------------------+
  Pass badge: green background, Fail: red background
  Correct: green left border, Incorrect: red left border
  Scrollable question list
```

---

## 12. Settings Wireframes

### Full-Screen Modal (fills workspace)

```
+--[1240px]------------------------------------------+
| Settings                                    [X]     | 48px
+----------------------------------------------------+
|                                                    |
|  [General][Account][Appearance][A11y][Keyboard]    | 40px tabs
|  [Notifications][Privacy][Plugins][Backup][Adv]    |
|                                                    |
|  General Settings                                  |
|  ─────────────────────────────────────────────     |
|                                                    |
|  Application                                       |
|  ─────────────────────────────────────────────     |
|  [x] Auto-save                     [toggle]        |
|  [ ] Check for updates on startup  [toggle]        |
|  [x] Show helpful tips             [toggle]        |
|  [ ] Send anonymous usage data     [toggle]        |
|                                                    |
|  Startup                                           |
|  ─────────────────────────────────────────────     |
|  On startup, show:                                 |
|  (o) Dashboard                                     |
|  ( ) Last viewed screen                            |
|  ( ) Login screen                                  |
|                                                    |
|  Language                                          |
|  ─────────────────────────────────────────────     |
|  [English (US)                             ▼]      |
|                                                    |
|  ─────────────────────────────────────────────     |
|                                                    |
|  +--[160px]--+  +--[160px]--+                      |
|  |Save Changes|  |Reset to   |                      |
|  |            |  |Defaults   |                      |
|  +------------+  +-----------+                      |
|                                                    |
+----------------------------------------------------+
  Full-screen modal overlay
  Tab bar: horizontal scrollable on compact screens
  Form controls: full-width with descriptions
  Save: only enabled when changes detected (dirty state)
```

---

## 13. Help Center Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Topics:   |  Help Center                 |
|  RAIL    | [🔍 Search|  [🔍 Search help articles...] |
|          |  help...] |                               |
|  [🏠]   |           |  Popular Topics:              |
|  [📚]   | [v] Get   |  +--[380px]--[120px]--------+  |
|  [🔬]   |  Started  |  | 🚀 Getting Started       |  |
|  [📝]   |  [ ] First|  | Quick guide for new users |  |
|  [📊]◄--|  [ ] Dash |  +-------------------------+  |
|  [⚙]   |  [ ] Learn |                               |
|  [❓]◄--|           |  +--[380px]--[120px]--------+  |
|          | [>] Simu- |  | ⌨️ Keyboard Shortcuts   |  |
|          |  lations  |  | Complete shortcut ref    |  |
|          |           |  +-------------------------+  |
|          | [>] Assess|                               |
|          |           |  +--[380px]--[120px]--------+  |
|          | [>] Reports| | 🌐 Offline Mode          |  |
|          |           |  | How it works             |  |
|          | [>] Certs |  +-------------------------+  |
|          |           |                               |
|          | [>] Plugins| ────────────────────────────|
|          |           |                               |
|          | [>] Settings| Article: Getting Started    |
|          |           |                               |
|          | [>] Troubleshoot| # Welcome to AuthShield |
|          |           |                               |
|          |           | Welcome to AuthShield Lab,    |
|          |           | your offline-first cyber-     |
|          |           | security education platform.  |
|          |           |                               |
|          |           | ## Getting Started            |
|          |           |                               |
|          |           | 1. **Create an account** or   |
|          |           |    sign in with your license  |
|          |           | 2. **Browse the catalog** to  |
|          |           |    find courses               |
|          |           | 3. **Enroll** and start       |
|          |           |    learning                   |
|          |           |                               |
|          |           | [<< Previous] [Next >>]       |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Topic tree: hierarchical, expandable
  Article: rendered markdown, scrollable
  Search: instant filter on article titles + content
```

---

## 14. Diagnostics Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Categories|  Diagnostics                  |
|  RAIL    |           |                               |
|          | [>] System|  System Information            |
|  [🏠]   |  Info ◄──|  +--[740px]--[auto]----------+ |
|  [📚]   |           |  | OS:          Linux 6.5.0  | |
|  [🔬]   | [>] Health|  | CPU:         4 cores @3.2GHz|
|  [📝]   |  Checks   |  | RAM:         8 GB (4.1 used)|
|  [📊]   |           |  | Disk:        256 GB SSD    | |
|  [⚙]   | [>] Log   |  | Electron:    v28.0.0       | |
|          |  Viewer   |  | Node.js:     v20.10.0      | |
|          |           |  | App Version: 2.4.1         | |
|          | [>] Perfor|  | Build:       2026.07.19    | |
|          |  mance    |  +---------------------------+ |
|          |           |                               |
|          |           |  Health Checks                 |
|          |           |  +--[740px]--[auto]----------+ |
|          |           |  | [OK]     Database          | |
|          |           |  |          SQLite connection  | |
|          |           |  |          healthy            | |
|          |           |  | [OK]     Storage            | |
|          |           |  |          1.2 GB used        | |
|          |           |  | [WARN]   Plugins            | |
|          |           |  |          1 plugin outdated  | |
|          |           |  | [OK]     Network            | |
|          |           |  |          Connectivity OK     | |
|          |           |  | [OK]     Memory             | |
|          |           |  |          4.1 GB / 8 GB       | |
|          |           |  +---------------------------+ |
|          |           |                               |
|          |           |  [Run All Checks]              |
|          |           |  [Export Diagnostics]           |
|          |           |  [Clear Logs]                   |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Health status: color-coded badges (green OK, yellow WARN, red FAIL)
  System info: key-value table with alternating row backgrounds
```

---

## 15. Certificate Gallery Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Filter:   |  My Certificates              |
|  RAIL    |           |  Sort: [Newest ▼]             |
|          | Course:   |                               |
|  [🏠]   | [All    ▼]|  +--[380px]--[260px]--+       |
|  [📚]   |           |  | +-[348px]-[180px]-+ |       |
|  [🔬]   | Date:     |  | |  [Certificate   | |       |
|  [📝]   | [All Time]|  | |   Preview]      | |       |
|  [📊]   |           |  | |   348x180       | |       |
|  [⚙]   | Search:   |  | +-----------------+ |       |
|          | [Search   |  |                     |       |
|          | certs...] |  | Advanced Crypto     |       |
|          |           |  | July 15, 2026      |       |
|          |           |  | [View Certificate] |       |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  +--[380px]--[260px]--+       |
|          |           |  | +-[348px]-[180px]-+ |       |
|          |           |  | |  [Certificate   | |       |
|          |           |  | |   Preview]      | |       |
|          |           |  | +-----------------+ |       |
|          |           |  |                     |       |
|          |           |  | Network Security    |       |
|          |           |  | June 28, 2026      |       |
|          |           |  | [View Certificate] |       |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  +--[380px]--[260px]--+       |
|          |           |  | +-[348px]-[180px]-+ |       |
|          |           |  | |  [Certificate   | |       |
|          |           |  | |   Preview]      | |       |
|          |           |  | +-----------------+ |       |
|          |           |  |                     |       |
|          |           |  | Web App Security    |       |
|          |           |  | June 10, 2026      |       |
|          |           |  | [View Certificate] |       |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  8 certificates               |
|          |           |  [Download All]                |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  3-column grid of certificate cards
  Card thumbnail: 348x180px ratio preview
  Hover: slight scale (1.02) + shadow increase
```

---

## 16. Backup & Restore Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Operations|  Backup & Restore             |
|  RAIL    |           |  [Backups] [Schedule]         |
|          | [>] Create|                               |
|  [🏠]   |  Backup ◄|  +--[480px]--[220px]--+       |
|  [📚]   |           |  |  📁 Backup 1       |       |
|  [🔬]   | [>] Restor|  |  Jul 19, 2026      |       |
|  [📝]   |  e        |  |  1.2 GB | Full     |       |
|  [📊]   |           |  |  [Restore] [Delete]|       |
|  [⚙]   | [>] Schedul|  +-------------------+       |
|          |  e        |                               |
|          |           |  +--[480px]--[220px]--+       |
|          |           |  |  📁 Backup 2       |       |
|          |           |  |  Jul 12, 2026      |       |
|          |           |  |  1.1 GB | Full     |       |
|          |           |  |  [Restore] [Delete]|       |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  +--[480px]--[220px]--+       |
|          |           |  |  📁 Backup 3       |       |
|          |           |  |  Jul 5, 2026       |       |
|          |           |  |  1.0 GB | Full     |       |
|          |           |  |  [Restore] [Delete]|       |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  ────────────────────────────|
|          |           |                               |
|          |           |  Schedule:                    |
|          |           |  [x] Daily at 2:00 AM         |
|          |           |  [ ] Weekly (Sunday)          |
|          |           |  [ ] Monthly (1st)            |
|          |           |  Retention: [30 days ▼]       |
|          |           |                               |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Backup cards: 2-column grid
  Schedule section: form controls below cards
```

---

## 17. Plugin Manager Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Categories|  Plugin Manager               |
|  RAIL    |           |  [Installed (5)] [Available]  |
|          | [x] Secur |                               |
|  [🏠]   | [x] Conten|  +--[480px]--[200px]--+       |
|  [📚]   | [x] Simul |  |  🔌 Plugin Name    |       |
|  [🔬]   | [x] Assess|  |  v2.1.0 | Installed |       |
|  [📝]   | [x] Integr|  |  Description text   |       |
|  [📊]   |           |  |  goes here...       |       |
|  [⚙]   | Search:   |  |  [Update] [Remove]  |       |
|          | [Search   |  +-------------------+       |
|          | plugins]  |                               |
|          |           |  +--[480px]--[200px]--+       |
|          |           |  |  🔌 Plugin Name 2  |       |
|          |           |  |  v1.3.0 | Installed |       |
|          |           |  |  Description text   |       |
|          |           |  |  goes here...       |       |
|          |           |  |  [Update] [Remove]  |       |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  +--[480px]--[200px]--+       |
|          |           |  |  🔌 Plugin Name 3  |       |
|          |           |  |  v3.0.0 | Installed |       |
|          |           |  |  Description text   |       |
|          |           |  |  goes here...       |       |
|          |           |  |  [Up to date]       |       |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  12 plugins installed          |
|          |           |  [Browse Store]                |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Tab bar: Installed | Available
  Plugin cards: 2-column, with status badge (Installed/Available/Update)
```

---

## 18. Analytics Dashboard Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Dimensions|  Analytics Dashboard          |
|  RAIL    |           |  Date Range: [Last 30 days ▼] |
|          | [x] Course|  [Apply Filters]              |
|  [🏠]   | [x] Studen|                               |
|  [📚]   | [ ] Time  |  +--[240px]--[100px]--+       |
|  [🔬]   |           |  |  📊 82%           |       |
|  [📝]   | Metrics:  |  |  Avg Score        |       |
|  [📊]◄--| [x] Compl |  +-------------------+       |
|  [⚙]   | [x] AvgSc |                               |
|          | [x] Time  |  +--[240px]--[100px]--+       |
|          | [ ] Dropof|  |  📈 67%           |       |
|          |           |  |  Completion Rate   |       |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  +--[240px]--[100px]--+       |
|          |           |  |  👥 142           |       |
|          |           |  |  Active Students   |       |
|          |           |  +-------------------+       |
|          |           |                               |
|          |           |  +--[740px]--[350px]--------+ |
|          |           |  | Line Chart             | |
|          |           |  | Completion over time   | |
|          |           |  |                        | |
|          |           |  |  100% |    *           | |
|          |           |  |   75% |  *   * *       | |
|          |           |  |   50% |*       * *     | |
|          |           |  |   25% |           *    | |
|          |           |  |     0 +--+--+--+--+--+ | |
|          |           |  |      W1 W2 W3 W4 W5 W6  | |
|          |           |  +------------------------+ |
|          |           |                               |
|          |           |  +--[740px]--[350px]--------+ |
|          |           |  | Bar Chart              | |
|          |           |  | Scores by course       | |
|          |           |  |                        | |
|          |           |  |  100|  ██              | |
|          |           |  |   75|  ██  ██  ██      | |
|          |           |  |   50|  ██  ██  ██  ██  | |
|          |           |  |   25|  ██  ██  ██  ██  | |
|          |           |  |     +--+--+--+--+--+   | |
|          |           |  |      Cr1 Cr2 Cr3 Cr4    | |
|          |           |  +------------------------+ |
|          |           |                               |
|          |           |  [Export PNG]  [Export CSV]    |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Summary stats: 3 cards in a row
  Charts: 2-column grid below stats
  Chart library: Recharts or Victory (accessible)
```

---

## 19. Accessibility Center Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Groups:   |  Accessibility Center         |
|  RAIL    |           |                               |
|          | [>] Theme |  Theme                        |
|  [🏠]   | [>] Typo  |  ─────────────────────────    |
|  [📚]   | [>] Motion|  (o) Light    [preview area]  |
|  [🔬]   | [>] Contr |  ( ) Dark                     |
|  [📝]   | [>] Screen|  ( ) High Contrast             |
|  [📊]   | [>] Keybo |                               |
|  [⚙]   | [>] Focus  |  ─────────────────────────    |
|          | [>] Color |                               |
|          |           |  Typography                   |
|          |           |  ─────────────────────────    |
|          |           |  Font Size: [===●----] 15px  |
|          |           |  Font Family: [System     ▼] |
|          |           |  Line Height: [===●----] 1.5 |
|          |           |                               |
|          |           |  ─────────────────────────    |
|          |           |                               |
|          |           |  Live Preview:                |
|          |           |  +--[740px]--[280px]--------+ |
|          |           |  | This is how text will    | |
|          |           |  | appear with your current | |
|          |           |  | accessibility settings.  | |
|          |           |  |                          | |
|          |           |  | [Button Preview]         | |
|          |           |  | [Input Preview]          | |
|          |           |  +-------------------------+ |
|          |           |                               |
|          |           |  [Reset to Defaults]          |
|          |           |  [Export Settings]            |
|          |           |  [Import Settings]            |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Settings change apply instantly to preview
  Preview area: real representation of theme + typography
  Slider controls: accessible with arrow keys
```

---

## 20. Localization Center Wireframes

### Comfortable Desktop (1920x1080)

```
+--[1920px]-------------------------------------------+
|  [Logo]  [🔍 Search ───────]        [👤][🔔][⚙]    | 48px
+--[64px]--+--[280px]--+--[1576px]--------------------+
|          |           |                               |
|  NAV     | Regions:  |  Localization Center          |
|  RAIL    |           |                               |
|          | [x] Ameri |  Language:                    |
|  [🏠]   | [x] Europe|  [English (US)             ▼] |
|  [📚]   | [x] Asia  |                               |
|  [🔬]   | [x] Africa|  ─────────────────────────    |
|  [📝]   |           |                               |
|  [📊]   |           |  Preview:                     |
|  [⚙]   |           |  +--[400px]--[180px]--------+  |
|          |           |  |  Date:    July 19, 2026  |  |
|          |           |  |  Time:    2:30 PM        |  |
|          |           |  |  Number:  1,234.56       |  |
|          |           |  |  Currency: $100.00       |  |
|          |           |  |  Currency: EUR 100.00    |  |
|          |           |  +-------------------------+  |
|          |           |                               |
|          |           |  ─────────────────────────    |
|          |           |                               |
|          |           |  Regional Settings:           |
|          |           |  Date Format: [MM/DD/YYYY ▼] |
|          |           |  Time Format: [12-hour    ▼] |
|          |           |  Number Format: [1,234.56 ▼] |
|          |           |  First Day of Week: [Sunday▼]|
|          |           |  Decimal Separator: [.    ▼]  |
|          |           |  Thousands Sep: [,      ▼]   |
|          |           |                               |
|          |           |  ─────────────────────────    |
|          |           |                               |
|          |           |  ⚠ Application will restart   |
|          |           |    to apply language changes.  |
|          |           |                               |
|          |           |  [Apply & Restart]             |
+----------+-----------+-------------------------------+
| [Online 🟢]  [Student]  [💾 Saved]       [1.2GB]    | 24px
+------------------------------------------------------+
  Preview: real-time updates as format selections change
  Warning: non-intrusive info banner, not blocking
```

---

## 21. Dialog Overlay Patterns

### Confirmation Dialog (360x200 centered)

```
+--[360px]------------------------------------+
|  ⚠ Confirm Action                     [X]  | 48px
+---------------------------------------------+
|                                             |
|  Are you sure you want to delete this       |
|  backup? This action cannot be undone.      |
|                                             |
|  +--[160px]--+  +--[160px]--+              |
|  |  Cancel   |  |  Delete   |              |
|  +-----------+  +-----------+              |
|                                             |
+---------------------------------------------+
  Background: semi-transparent overlay
  Focus trap: within dialog only
  Enter: confirm (Delete), Escape: cancel
  Delete button: red/danger variant
```

### Error Dialog (480x280 centered)

```
+--[480px]------------------------------------+
|  ✖ Error Occurred                    [X]   | 48px
+---------------------------------------------+
|                                             |
|  +--[36px]--+                               |
|  |  ✖       |  Failed to load course data. |
|  |  (red)   |  The file may be corrupted    |
|  +----------+  or missing.                  |
|                                             |
|  Error Details:                             |
|  ┌─────────────────────────────────────────┐|
|  │ Error: COURSE_NOT_FOUND                 │|
|  │ File: /data/courses/crypto-v2.json      │|
|  │ Time: 2026-07-19 14:30:00              │|
|  │ [Show Stack Trace ▼]                    │|
|  └─────────────────────────────────────────┘|
|                                             |
|  +--[140px]--+  +--[140px]--+  +--[140px]--+|
|  |  Retry    |  |  Go Home  |  |  Dismiss  | |
|  +-----------+  +-----------+  +-----------+ |
|                                             |
+---------------------------------------------+
  Error icon: red circle with X
  Stack trace: expandable <details> element
  Three action buttons: Retry (primary), Go Home, Dismiss
```

### Backup Wizard (600x500 centered)

```
+--[600px]------------------------------------+
|  Create Backup                          [X] | 48px
+---------------------------------------------+
|  Step 3 of 4: Confirm                       | 32px
|  ─────────────────────────────────────      |
|  [1] Select Scope  [2] Options  [3] Confirm|
|  [████████] [████████] [●●●●] [----]       |
|                                             |
|  ─────────────────────────────────────      |
|                                             |
|  Backup Summary:                            |
|  +--[568px]--[auto]-----------------------+ |
|  | Scope:        Full application data    | |
|  | Include:      Courses, Results, Config | |
|  | Compression:  Standard (gzip)          | |
|  | Estimated:    ~1.2 GB                  | |
|  | Destination:  /home/user/.authshield/  | |
|  +----------------------------------------+ |
|                                             |
|  ─────────────────────────────────────      |
|                                             |
|  +--[180px]--+  +--[180px]--+              |
|  |  Back     |  |  Create   |              |
|  +-----------+  +-----------+              |
|                                             |
+---------------------------------------------+
  Step indicator: numbered circles with connecting lines
  Current step: filled circle, future: outlined
  Back: returns to step 2, Create: starts backup
```

---

## 22. Toast Notification Patterns

### Success Toast (320x72)

```
+--[320px]---------------------------+
|  ✅ Course enrolled successfully  | 16px padding
|     Intro to Crypto               | 48px content
|                            [✕]    | 
+-----------------------------------+
  Background: #F0FDF4, border-left: #22C55E
  Auto-dismiss: 5 seconds
  Slide-in from right
```

### Warning Toast (320x72)

```
+--[320px]---------------------------+
|  ⚠ Assessment due in 2 hours     |
|     Quiz 2: Network Security      |
|                            [✕]    |
+-----------------------------------+
  Background: #FFFBEB, border-left: #F59E0B
  Auto-dismiss: 8 seconds (longer for warnings)
```

### Error Toast (320x88)

```
+--[320px]---------------------------+
|  ✖ Backup failed                  |
|     Insufficient disk space.      |
|     Need 2.1 GB, only 1.5 GB     |
|     available.              [✕]   |
|                            [Retry] |
+-----------------------------------+
  Background: #FEF2F2, border-left: #DC2626
  No auto-dismiss (requires action)
```

---

## 23. Status Bar Wireframe (Detail)

```
+--[1366px]-------------------------------------------+
| [🟢 Online] | Student: alex@lab.edu | 💾 Saved 2s ago | 1.2 GB / 10 GB |
+------------------------------------------------------+
 24px height
 |<- 16px ->|<- 16px ->|<-- flex -->|<- 16px ->|<- 16px ->|
 
 Connection: 16px dot + label, color-coded
 User: truncated at 200px, ellipsis
 Save: relative time, updates every second
 Storage: fraction with bar indicator
```

### Offline State

```
+--[1366px]-------------------------------------------+
| [🟡 Offline Mode] | Changes will sync when online  |
+------------------------------------------------------+
  Background: #FFFBEB (warning yellow tint)
  Full-width banner within status bar
```

---

## 24. Responsive Grid System

### Grid Specifications

| Screen | Columns | Gutter | Margin | Content Max |
|--------|---------|--------|--------|-------------|
| 1024px (compact) | 8 | 16px | 16px | 992px |
| 1366px (standard) | 12 | 16px | 24px | 1318px |
| 1920px (comfortable) | 12 | 24px | 32px | 1856px |
| 2560px (spacious) | 12 | 32px | 48px | 2464px |

### Column Width Calculation

```
Column Width = (Container Width - (Gutter * (Columns - 1)) - (Margin * 2)) / Columns

Example (1920px):
(1856 - (24 * 11) - (32 * 2)) / 12 = (1856 - 264 - 64) / 12 = 136px
```

### Breakpoint Transition Behaviour

```
< 1024px:     Not supported (show resize warning)
1024-1199px:  Compact density, rail collapsed, sidebar 180px
1200-1599px:  Standard density, rail auto, sidebar 240px
1600-2199px:  Comfortable density, rail expanded, sidebar 280px
2200px+:      Spacious density, rail expanded, sidebar 320px
```

---

*End of Wireframe Catalog*
