# AuthShield Lab — Screen Specifications

> Version: 1.0.0
> Last Updated: 2026-07-19
> Status: Active

---

## Table of Contents

1. [Splash Screen](#1-splash-screen)
2. [Welcome Screen](#2-welcome-screen)
3. [License Agreement](#3-license-agreement)
4. [Privacy Notice](#4-privacy-notice)
5. [User Login](#5-user-login)
6. [Dashboard — Student](#6-dashboard--student)
7. [Dashboard — Instructor](#7-dashboard--instructor)
8. [Dashboard — Administrator](#8-dashboard--administrator)
9. [Course Catalog](#9-course-catalog)
10. [Course Detail](#10-course-detail)
11. [Learning Workspace](#11-learning-workspace)
12. [Lesson Viewer](#12-lesson-viewer)
13. [Simulation Workspace](#13-simulation-workspace)
14. [Assessment Workspace](#14-assessment-workspace)
15. [Assessment Results](#15-assessment-results)
16. [Report Viewer](#16-report-viewer)
17. [Certificate Gallery](#17-certificate-gallery)
18. [Certificate Detail](#18-certificate-detail)
19. [Analytics Dashboard](#19-analytics-dashboard)
20. [Plugin Manager](#20-plugin-manager)
21. [Accessibility Center](#21-accessibility-center)
22. [Localization Center](#22-localization-center)
23. [Backup & Restore](#23-backup--restore)
24. [Diagnostics](#24-diagnostics)
25. [Settings](#25-settings)
26. [Help Center](#26-help-center)
27. [About](#27-about)
28. [Keyboard Shortcut Reference](#28-keyboard-shortcut-reference)

---

## 1. Splash Screen

### Purpose
Display branding and loading progress while the application initializes offline data stores and checks system health.

### ASCII Wireframe

```
+---------------------------------------------------+
|                                                   |
|                                                   |
|                +-----------------+                |
|                |  AuthShield     |                |
|                |  Logo 120x120   |                |
|                +-----------------+                |
|                                                   |
|                  AuthShield Lab                   |
|                    v2.4.1                         |
|                                                   |
|        +-------------------------------+          |
|        | [|||||||||||||...........] 62%|          |
|        +-------------------------------+          |
|                                                   |
|        Initializing secure environment...         |
|                                                   |
+---------------------------------------------------+
```

### Layout Regions

| Region       | Position                  | Size              |
|--------------|---------------------------|-------------------|
| Logo         | Center, 200px from top    | 120 x 120px       |
| Title        | Center, 340px from top    | Auto width        |
| Version      | Center, 370px from top    | Auto width        |
| Progress bar | Center, 420px from top    | 300 x 8px         |
| Status text  | Center, 440px from top    | Auto width        |

### Components

- **Logo**: PNG/SVG branding, `role="img"`, `aria-label="AuthShield Lab logo"`
- **Version text**: `aria-label="Version 2.4.1"`
- **Progress bar**: `role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`
- **Status text**: `aria-live="polite"`, updates every 200ms during load

### Navigation
- **Entry**: Auto on application launch
- **Exit**: Auto-transition to Welcome Screen or Dashboard (after 1.5s minimum display)

### Keyboard Flow
1. No interactive elements — passive screen

### Focus Order
No focusable elements. Tab/Shift+Tab do nothing.

### Validation Rules
- Minimum display time: 1500ms
- Maximum display time: 8000ms (force transition)
- Progress must reach 100% before transition (or timeout)

### Accessibility Notes
- `aria-live="polite"` on status text for screen reader announcements
- Progress bar updates announced at 25%, 50%, 75%, 100%
- Sufficient contrast: white text on dark background (12:1 ratio)

### Localization Notes
- Status text: translatable ("Initializing secure environment...")
- Version format: `v{major}.{minor}.{patch}`

### Performance Expectations
- Total load: 1500-3000ms on SSD, 3000-5000ms on HDD
- Logo renders within 100ms

---

## 2. Welcome Screen

### Purpose
First-launch greeting with onboarding options for new users.

### ASCII Wireframe

```
+---------------------------------------------------+
|                                                   |
|                +-----------------+                |
|                | Welcome Artwork |                |
|                |   300 x 200     |                |
|                +-----------------+                |
|                                                   |
|             Welcome to AuthShield Lab             |
|                                                   |
|     Your offline-first cybersecurity education    |
|     platform. Practice safely in isolated         |
|     environments.                                 |
|                                                   |
|           +---------------------+                 |
|           |    Get Started ->   |  (primary)      |
|           +---------------------+                 |
|                                                   |
|           +---------------------+                 |
|           |  I have a license   |  (secondary)    |
|           +---------------------+                 |
|                                                   |
|           +---------------------+                 |
|           |  Explore as Guest   |  (tertiary)     |
|           +---------------------+                 |
|                                                   |
|          Already have an account? Sign In         |
|                                                   |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position                   | Size              |
|---------------|----------------------------|-------------------|
| Artwork       | Center, 80px from top      | 300 x 200px       |
| Heading       | Center, 300px from top     | Full width        |
| Description   | Center, 340px from top     | 480px max-width   |
| Primary CTA   | Center, 420px from top     | 240 x 44px        |
| Secondary CTA | Center, 476px from top     | 240 x 44px        |
| Guest CTA     | Center, 532px from top     | 240 x 44px        |
| Sign-in link  | Center, 590px from top     | Auto width        |

### Components

- **Artwork**: SVG illustration, decorative, `aria-hidden="true"`
- **Heading**: `<h1>`, "Welcome to AuthShield Lab"
- **Description**: `<p>`, platform summary
- **Get Started button**: Primary, opens License Agreement
- **License button**: Secondary, opens license entry dialog
- **Guest link**: Tertiary, enters guest mode with limited features
- **Sign-in link**: Text link to Login screen

### Navigation
- **Entry**: After Splash Screen (first launch only)
- **Exit**: License Agreement / User Login / Dashboard (guest)

### Keyboard Flow
1. Get Started -> (Enter) -> License Agreement
2. I have a license -> (Enter) -> License entry dialog
3. Explore as Guest -> (Enter) -> Dashboard (guest)
4. Sign In -> (Enter) -> Login screen

### Focus Order
1. "Get Started" button (auto-focus on screen load)
2. "I have a license" button
3. "Explore as Guest" button
4. "Sign In" link

### Validation Rules
- No validation needed (selection screen)

### Accessibility Notes
- Heading level: `<h1>`
- Artwork: `aria-hidden="true"`
- All buttons have visible focus indicators
- Guest mode: announce limitations on entry

### Localization Notes
- All text translatable
- RTL layout support for Arabic, Hebrew

### Performance Expectations
- Render: < 200ms (static content)
- Transitions: 200ms ease-out

---

## 3. License Agreement

### Purpose
Display end-user license agreement. User must accept to proceed.

### ASCII Wireframe

```
+---------------------------------------------------+
|  License Agreement                         [X]    |
+---------------------------------------------------+
|                                                   |
|  +---------------------------------------------+ |
|  | END-USER LICENSE AGREEMENT                   | |
|  |                                             | |
|  | IMPORTANT - READ CAREFULLY:                 | |
|  |                                             | |
|  | This End-User License Agreement (EULA) is   | |
|  | a legal agreement between you and           | |
|  | AuthShield Lab for the software product     | |
|  | identified above.                           | |
|  |                                             | |
|  | By installing, copying, or otherwise using  | |
|  | this software, you agree to be bound by the | |
|  | terms of this agreement.                    | |
|  |                                             | |
|  | 1. GRANT OF LICENSE                         | |
|  | ...                                         | |
|  |                                             | |
|  | [scrollbar on right]                        | |
|  +---------------------------------------------+ |
|                                                   |
|  [ ] I have read and agree to the License         |
|      Agreement                                    |
|                                                   |
|  +-------------------+  +-------------------+     |
|  | Decline           |  | Continue         |     |
|  +-------------------+  +-------------------+     |
|                                                   |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position                    | Size              |
|---------------|-----------------------------|-------------------|
| Title bar     | Top                         | Full width, 48px  |
| Scroll area   | Below title, above footer   | Full x 300px      |
| Checkbox      | Below scroll, 16px inset    | Auto height       |
| Action bar    | Bottom, 16px inset          | Full x 56px       |

### Components

- **Title**: "License Agreement", `<h2>`
- **Close button**: Top-right, closes dialog, returns to Welcome Screen
- **Scrollable text area**: EULA content, markdown rendered, scrollable
- **Agree checkbox**: Required before Continue is enabled
- **Decline button**: Closes app or returns to Welcome Screen
- **Continue button**: Disabled until checkbox checked, proceeds to Privacy Notice

### Navigation
- **Entry**: From Welcome Screen "Get Started" or License entry
- **Exit**: Privacy Notice (accept) or Welcome Screen (decline)

### Keyboard Flow
1. Scroll area (Tab to enter, arrow keys to scroll)
2. Checkbox (Tab)
3. Decline button (Tab)
4. Continue button (Tab)

### Focus Order
1. Close button (X)
2. Scroll area
3. Checkbox
4. Decline button
5. Continue button

### Validation Rules
- Continue disabled until checkbox is checked
- Decline shows confirmation: "Are you sure? You cannot use the application without accepting."

### Accessibility Notes
- Dialog: `role="dialog"`, `aria-modal="true"`, `aria-labelledby="license-title"`
- Focus trapped within dialog
- Scroll area: `aria-label="License agreement text"`
- Checkbox: `aria-describedby="license-required"` helper text

### Localization Notes
- EULA content: translatable per locale
- Date format in EULA: locale-appropriate
- RTL: full mirror layout

### Performance Expectations
- Render: < 100ms
- Scroll: 60fps

---

## 4. Privacy Notice

### Purpose
Inform user about data handling, emphasize local-only storage, and obtain consent.

### ASCII Wireframe

```
+---------------------------------------------------+
|  Privacy Notice                             [X]   |
+---------------------------------------------------+
|                                                   |
|  +---------------------------+                    |
|  |     [Shield Icon 48px]    |                    |
|  +---------------------------+                    |
|                                                   |
|  Your Privacy Matters                             |
|                                                   |
|  AuthShield Lab stores all data locally on your   |
|  device. No data is transmitted to external       |
|  servers. You are in full control.                |
|                                                   |
|  +---------------------------------------------+ |
|  | DATA HANDLING SUMMARY                        | |
|  |                                             | |
|  | [+] Course progress     -> Local storage    | |
|  | [+] Assessment results  -> Local storage    | |
|  | [+] User preferences    -> Local storage    | |
|  | [+] Simulations data    -> Local storage    | |
|  | [+] Backups             -> Local filesystem | |
|  |                                             | |
|  | [+] Analytics           -> NONE             | |
|  | [+] External telemetry  -> NONE             | |
|  | [+] Cloud sync          -> NONE             | |
|  +---------------------------------------------+ |
|                                                   |
|  [ ] I understand and consent to local storage    |
|                                                   |
|  +-------------------+  +-------------------+     |
|  | Decline           |  | Accept & Continue |     |
|  +-------------------+  +-------------------+     |
|                                                   |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position                    | Size              |
|---------------|-----------------------------|-------------------|
| Title bar     | Top                         | Full width, 48px  |
| Icon          | Center, 20px from top       | 48 x 48px         |
| Heading       | Center, 80px from top       | Full width        |
| Description   | Center, 120px from top      | 480px max         |
| Data summary  | Center, 180px from top      | 520px max         |
| Checkbox      | Below summary               | Auto              |
| Action bar    | Bottom                      | Full x 56px       |

### Components

- **Shield icon**: Decorative, `aria-hidden="true"`
- **Heading**: `<h2>`, "Your Privacy Matters"
- **Description**: `<p>`, privacy summary
- **Data handling table**: Expandable rows with category + storage location
- **Consent checkbox**: Required
- **Decline button**: Returns to Welcome Screen
- **Accept & Continue button**: Proceeds to Login or Dashboard

### Navigation
- **Entry**: After License Agreement acceptance
- **Exit**: Login screen or Dashboard

### Keyboard Flow
1. Scroll through data summary (arrow keys)
2. Checkbox (Tab)
3. Decline (Tab)
4. Accept (Tab)

### Focus Order
1. Close button
2. Data summary scroll area
3. Checkbox
4. Decline button
5. Accept button

### Validation Rules
- Accept disabled until checkbox checked
- Decline: confirmation dialog

### Accessibility Notes
- `role="dialog"`, `aria-modal="true"`
- Data table: proper `<table>` with `<th>` headers
- `aria-live="polite"` for checkbox state announcements

### Localization Notes
- All text translatable
- Data categories may vary by locale

### Performance Expectations
- Render: < 100ms (static)

---

## 5. User Login

### Purpose
Authenticate user with email and password for offline credential verification.

### ASCII Wireframe

```
+---------------------------------------------------+
|  [Logo]                                            |
|                                                   |
|                Sign In to AuthShield               |
|                                                   |
|  +---------------------------------------------+ |
|  | Email Address                                | |
|  | +-----------------------------------------+ | |
|  | | student@lab.edu                     [x] | | |
|  | +-----------------------------------------+ | |
|  +---------------------------------------------+ |
|                                                   |
|  +---------------------------------------------+ |
|  | Password                                     | |
|  | +-----------------------------+  +-------+  | |
|  | | *************               |  | Show 👁|  | |
|  | +-----------------------------+  +-------+  | |
|  +---------------------------------------------+ |
|                                                   |
|  +---------------------------------------------+ |
|  | [x] Remember me on this device               | |
|  +---------------------------------------------+ |
|                                                   |
|  +---------------------------------------------+ |
|  |              Sign In                         | |
|  +---------------------------------------------+ |
|                                                   |
|         Forgot your password?                     |
|                                                   |
|  ┌─────────────────────────────────────────────┐  |
|  | ⚠  Invalid email or password. Please try   |  |
|  |    again. (error state)                     |  |
|  └─────────────────────────────────────────────┘  |
|                                                   |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position                    | Size              |
|---------------|-----------------------------|-------------------|
| Logo          | Top-left, 24px inset        | 160 x 28px        |
| Heading       | Center, 120px from top      | Full width        |
| Email field   | Center, 180px from top      | 400 x 48px        |
| Password field| Center, 248px from top      | 400 x 48px        |
| Remember me   | Center, 316px from top      | Auto              |
| Sign In btn   | Center, 364px from top      | 400 x 48px        |
| Forgot link   | Center, 424px from top      | Auto              |
| Error banner  | Below forgot link           | 400 x auto        |

### Components

- **Email input**: `type="email"`, autocomplete="email", `aria-required="true"`
- **Password input**: `type="password"` toggle to text, `aria-required="true"`, show/hide button
- **Remember me checkbox**: persists session locally
- **Sign In button**: Primary, full-width, validates then authenticates
- **Forgot password link**: Opens password reset dialog
- **Error banner**: `role="alert"`, `aria-live="assertive"`, red background

### Navigation
- **Entry**: Privacy Notice acceptance or Welcome Screen sign-in link
- **Exit**: Dashboard (success) or error stays on screen

### Keyboard Flow
1. Email field (auto-focus)
2. Password field
3. Show/Hide password toggle
4. Remember me checkbox
5. Sign In button
6. Forgot password link

### Focus Order
1. Email input (auto-focus)
2. Password input
3. Show password toggle
4. Remember me checkbox
5. Sign In button
6. Forgot password link

### Validation Rules
- Email: required, valid format (RFC 5322 simplified)
- Password: required, minimum 8 characters
- Error state: inline below fields + banner
- Rate limiting: 5 attempts, then 30s cooldown

### Accessibility Notes
- `role="form"`, `aria-label="Sign in"`
- Error messages: `aria-describedby` linked to inputs
- Error banner: `role="alert"`, `aria-live="assertive"`
- Password visibility toggle: `aria-pressed` state

### Localization Notes
- All labels translatable
- Email validation pattern per locale
- Error messages translatable

### Performance Expectations
- Render: < 150ms
- Authentication: < 200ms (local credential check)
- Error display: < 50ms after failed attempt

---

## 6. Dashboard — Student

### Purpose
Home screen for students showing enrolled courses, progress, recent activity, and quick actions.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header: [Logo] [Search] [Avatar][Bell][Gear]  |
+------+--------------------------------------------+
| NAV  | Sidebar (240px)      |                     |
| RAIL | [Breadcrumbs]        | Welcome back, Alex! |
| 64px |                      |                     |
| [Home| Quick Actions:       | +--------+ +------+ |
| [Cour| [Continue Learning]  | | Course | |Course| |
| [Sim | [Take Assessment]    | | Card 1 | |Card 2| |
| [Asse| [Start Simulation]   | | 65%    | | 30%  | |
| [Repo|                      | +--------+ +------+ |
| [Set | Upcoming:            | +--------+ +------+ |
| [Help| [Assessment in 2h]   | | Course | |Course| |
|      | [Course deadline]    | | Card 3 | |Card 4| |
|      |                      | | 90%    | | 0%   | |
|      | Recent Activity:     | +--------+ +------+ |
|      | [Completed Lesson 1] |                     |
|      | [Scored 85% on Quiz] | Recent Activity:    |
|      |                      | +-----------------+ |
|      |                      | | Completed:      | |
|      |                      | | Lesson 3.2      | |
|      |                      | | 2 hours ago     | |
|      |                      | +-----------------+ |
|      |                      | | Assessment:     | |
|      |                      | | Quiz 2 - 85%    | |
|      |                      | | Yesterday       | |
|      |                      | +-----------------+ |
+------+--------------------------------------------+
| Status: [Online] [Student] [Saved] [1.2GB]        |
+---------------------------------------------------+
```

### Layout Regions

| Region         | Position                  | Size              |
|----------------|---------------------------|-------------------|
| App Header     | Top                       | Full x 48px       |
| Nav Rail       | Left                      | 64px x full       |
| Sidebar        | Left of workspace         | 240px x full      |
| Workspace      | Remaining space           | flex-grow         |
| Status Bar     | Bottom                    | Full x 24px       |

### Components

- **Welcome message**: `<h1>`, "Welcome back, {firstName}!"
- **Course cards grid**: 2-4 columns, responsive, each with thumbnail, title, progress bar, last accessed
- **Recent activity feed**: Timeline list, last 10 items
- **Quick actions sidebar**: Buttons for common actions
- **Upcoming items**: Due dates, deadlines
- **Progress summary**: Overall completion percentage

### Navigation
- **Entry**: After login (default screen for students)
- **Exit**: Course detail (click card), Reports, Settings

### Keyboard Flow
1. Course cards: arrow keys grid navigation
2. Recent activity: Tab through items
3. Quick actions: Tab through buttons

### Focus Order
1. Welcome heading
2. Course cards (grid: left-right, up-down)
3. Recent activity items
4. Sidebar quick actions
5. Sidebar upcoming items

### Validation Rules
- Empty state: "No courses yet — Browse the Course Catalog to get started"

### Accessibility Notes
- Course grid: `role="list"`, cards `role="listitem"`
- Progress bars: `role="progressbar"` with labels
- Activity feed: `aria-live="polite"` on updates
- Time elements: `<time datetime="...">` for machine-readable dates

### Localization Notes
- Time formats: locale-relative ("2 hours ago", "il y a 2 heures")
- Date formats: locale-appropriate
- Number formatting: locale-specific

### Performance Expectations
- Initial render: < 300ms
- Card click to detail: < 200ms
- Activity feed update: < 100ms

---

## 7. Dashboard — Instructor

### Purpose
Home screen for instructors showing managed courses, student statistics, and pending reviews.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar                 |                  |
| RAIL | [My Courses]           | Instructor Hub    |
| 64px | [Pending Reviews (3)]  |                   |
|      | [Student Issues]       | +------+ +------+ |
|      | [Analytics]            | |S stats| |S stats|
|      |                        | |Enrolled| |Avg   |
|      | Course List:           | | 45    | | 78%  |
|      | [Intro to Crypto]     | +------+ +------+ |
|      | [Network Security]    | +------+ +------+ |
|      | [Web App Security]    | |S stats| |S stats|
|      |                        | |Submiss| |Alerts|
|      | Recent Submissions:    | | 12    | | 2    |
|      | [Alice - Lab 3]      | +------+ +------+ |
|      | [Bob - Lab 2]        |                   |
|      | [Carol - Quiz 1]     | Pending Reviews:  |
|      |                        | +-----------------+|
|      | Alerts:                | | Alice - Lab 3  ||
|      | [Low completion rate] | | Due 2h ago      ||
|      | [3 overdue grades]    | +-----------------+|
|      |                        | | Bob - Lab 2    ||
|      |                        | | Due 1d ago      ||
|      |                        | +-----------------+|
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region         | Position                  | Size              |
|----------------|---------------------------|-------------------|
| Sidebar        | Left of workspace         | 240px             |
| Stats grid     | Top of workspace          | 4 columns         |
| Recent submissions | Below stats            | List              |
| Pending reviews | Right panel              | 300px             |

### Components

- **Stats cards**: Enrolled students, average score, submissions pending, alerts
- **Course list**: Managed courses with quick links
- **Recent submissions**: Student name, assignment, time ago
- **Pending reviews panel**: Sorted by urgency
- **Alerts section**: Warnings about low engagement, overdue grading

### Navigation
- **Entry**: Login (instructor role)
- **Exit**: Course management, student detail, analytics

### Keyboard Flow
1. Stats cards: arrow keys
2. Course list: arrow keys
3. Recent submissions: Tab
4. Pending reviews: Tab

### Focus Order
1. Stats cards (left-right)
2. Course list (up-down)
3. Recent submissions
4. Pending reviews
5. Alerts

### Validation Rules
- No data: "No courses created yet — Create your first course"

### Accessibility Notes
- Stats cards: `role="region"` with `aria-label` for each stat
- Time-sensitive items: `aria-live="polite"` for countdown updates
- Submissions list: `role="list"`

### Localization Notes
- All text translatable
- Number formats locale-specific
- Time: relative or absolute per preference

### Performance Expectations
- Render: < 300ms
- Real-time submission updates: < 500ms

---

## 8. Dashboard — Administrator

### Purpose
System overview for administrators: health, user counts, storage, audit log.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar                 |                  |
| RAIL | [System Health]        | Admin Dashboard   |
| 64px | [User Management]     |                   |
|      | [Storage]             | +------+ +------+ |
|      | [Audit Log]           | |Health| |Users |
|      | [Diagnostics]         | | 98%  | | 142  |
|      |                        | +------+ +------+ |
|      | System Overview:       | +------+ +------+ |
|      | [CPU: 23%]            | |Store | |Backup|
|      | [RAM: 412MB]          | |1.2GB | |Last  |
|      | [Disk: 67%]           | |      | |2d ago|
|      |                        | +------+ +------+ |
|      | Recent Audit Entries:  |                   |
|      | [2026-07-19 14:23]    | System Health:    |
|      |  User login: admin    | [===========] 98% |
|      | [2026-07-19 14:20]    |                   |
|      |  Backup completed     | Storage:          |
|      | [2026-07-19 14:15]    | [====....] 67%    |
|      |  Plugin installed     | 1.2 GB / 10 GB    |
|      |                        |                   |
|      | Quick Actions:        | Audit:            |
|      | [Create Backup]       | 47 entries today  |
|      | [Export Data]         | [View Full Log]   |
|      | [Run Diagnostics]     |                   |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region           | Position              | Size          |
|------------------|-----------------------|---------------|
| Sidebar          | Left of workspace     | 240px         |
| Stats grid       | Top of workspace      | 2x2 grid      |
| Health bars      | Below stats           | Full width    |
| Audit feed       | Below health          | Full width    |

### Components

- **Health score**: Circular progress, percentage
- **User count**: Total active users
- **Storage meter**: Used/total with bar
- **Backup status**: Last backup time
- **System metrics**: CPU, RAM, Disk usage bars
- **Audit log feed**: Timestamped entries with filter
- **Quick action buttons**: Backup, export, diagnostics

### Navigation
- **Entry**: Login (admin role)
- **Exit**: User management, audit log, diagnostics, settings

### Keyboard Flow
1. Stats grid: arrow keys
2. System metrics: Tab
3. Audit entries: Tab through list
4. Quick actions: Tab

### Focus Order
1. Health score
2. User count
3. Storage meter
4. Backup status
5. System metrics (CPU, RAM, Disk)
6. Audit entries
7. Quick action buttons

### Validation Rules
- Health < 50%: show warning banner
- Storage > 90%: show critical alert
- Audit log: pagination (50 per page)

### Accessibility Notes
- Health score: `role="progressbar"` with `aria-valuenow`
- System metrics: labeled bars with values
- Audit entries: `role="log"`, `aria-live="polite"`
- Alerts: `role="alert"` for critical states

### Localization Notes
- Timestamps: locale-formatted
- File sizes: locale-specific (GB vs Go)
- Number formatting: locale-specific

### Performance Expectations
- Render: < 400ms
- Audit log pagination: < 200ms
- System metrics refresh: every 5s

---

## 9. Course Catalog

### Purpose
Browse, search, and filter available courses for enrollment.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar (filters)     |                    |
| RAIL |                        | Course Catalog     |
| 64px | Search:               |                    |
|      | [Search courses...  ] | Sort: [Newest v]   |
|      |                        |                    |
|      | Category:             | +--------+ +------+ |
|      | [x] Networking       | | Course | |Course| |
|      | [x] Crypto           | | Card   | |Card  | |
|      | [x] Web Security     | | img    | |img   | |
|      | [x] Incident Resp.   | | Title  | |Title |
|      | [x] Malware          | | by Auth| |by    |
|      | [x] Forensics        | | 12 mod | |8 mod |
|      |                        | | [Enrol]| |[Enrol]|
|      | Level:                | +--------+ +------+ |
|      | ( ) Beginner          |                    |
|      | (x) All Levels        | +--------+ +------+ |
|      | ( ) Intermediate      | | Course | |Course| |
|      | ( ) Advanced          | | Card   | |Card  | |
|      |                        | |        | |      |
|      | Duration:             | +--------+ +------+ |
|      | [  0 ] to [ 40 ] hrs |                    |
|      |                        | Showing 1-12 of 47 |
|      | Rating:               | [< 1 2 3 4 >]     |
|      | [>= 3 stars]          |                    |
|      |                        |                    |
|      | [Clear Filters]       |                    |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Sidebar       | Left of workspace      | 240px, filters    |
| Header area   | Top of workspace       | Full x 48px       |
| Card grid     | Main area              | 2-3 columns       |
| Pagination    | Bottom of workspace    | Center            |

### Components

- **Search input**: Fuzzy search across title, description, author
- **Category checkboxes**: Multi-select filter
- **Level radio**: Single-select filter
- **Duration range**: Min/max input pair
- **Rating filter**: Star rating minimum
- **Clear filters button**: Resets all filters
- **Sort dropdown**: Newest, Oldest, Most Popular, Highest Rated, A-Z
- **Course cards**: Thumbnail, title, author, module count, enrollment status
- **Pagination**: Page numbers, prev/next

### Navigation
- **Entry**: Navigation Rail click or Ctrl+D -> Courses
- **Exit**: Course Detail (click card), back to Dashboard

### Keyboard Flow
1. Search input (auto-focus)
2. Category checkboxes
3. Level radios
4. Duration inputs
5. Rating filter
6. Clear filters button
7. Sort dropdown
8. Course card grid (arrow keys)
9. Pagination

### Focus Order
1. Search input
2. Filter sidebar (top to bottom)
3. Sort dropdown
4. Card grid (left-right, up-down)
5. Pagination controls

### Validation Rules
- Search: minimum 2 characters
- Duration: numeric, 0-200 range
- No results: "No courses match your filters. Try adjusting your criteria."

### Accessibility Notes
- Card grid: `role="list"`, cards `role="listitem"`
- Filters: `role="search"`, `aria-label="Course filters"`
- Active filters: `aria-live="polite"` count update
- Pagination: `role="navigation"`, `aria-label="Course pages"`

### Localization Notes
- Category names: translatable
- Duration: hours vs locale format
- Sorting labels: translatable

### Performance Expectations
- Filter response: < 100ms
- Card render (50 items): < 200ms
- Search debounced: 150ms

---

## 10. Course Detail

### Purpose
View course information, module list, and enroll or continue learning.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Breadcrumb: Home > Catalog > Course Name   |
| RAIL |                                             |
| 64px | +-----------------------------------------+|
|      | |  [Course Banner Image 800x200]          ||
|      | +-----------------------------------------+|
|      |                                             |
|      | Course Title                                |
|      | by Author Name                              |
|      |                                             |
|      | [Networking] [Intermediate] [12 Modules]    |
|      | [4.5 stars] [234 enrolled]                  |
|      |                                             |
|      | +-----------------------------------------+|
|      | | Description:                             ||
|      | | This course covers advanced network      ||
|      | | security concepts including...            ||
|      | +-----------------------------------------+|
|      |                                             |
|      | +-----------------------------------------+|
|      | | MODULE LIST                              ||
|      | | [1] Introduction to Networks        [30m]||
|      | | [2] TCP/IP Deep Dive                [45m]||
|      | | [3] Firewalls & IDS                 [60m]||
|      | | [4] VPN Configuration               [45m]||
|      | | [5] Network Scanning               [40m]||
|      | | ... (expandable)                        ||
|      | +-----------------------------------------+|
|      |                                             |
|      | +---------------------+                    |
|      | |   Enroll in Course  |  (or Continue)     |
|      | +---------------------+                    |
|      |                                             |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Breadcrumb    | Top of workspace       | Full x 40px       |
| Banner        | Below breadcrumb       | Full x 200px      |
| Info section  | Below banner           | Full, auto height |
| Module list   | Below info             | Full, scrollable  |
| CTA button    | Below modules          | 280 x 48px        |

### Components

- **Banner image**: `role="img"`, `aria-label="Course banner for {title}"`
- **Title**: `<h1>`
- **Author**: Link to author profile
- **Tags**: Category, level, module count badges
- **Rating**: Star display + count
- **Enrollment count**: Text display
- **Description**: Expandable/collapsible text
- **Module list**: Accordion or flat list with duration, completion status
- **Enroll/Continue button**: Primary CTA

### Navigation
- **Entry**: Course Catalog card click
- **Exit**: Learning Workspace (enrolled), Course Catalog (back)

### Keyboard Flow
1. Banner (skip)
2. Title
3. Tags
4. Description toggle
5. Module list items (arrow keys)
6. Enroll/Continue button

### Focus Order
1. Back link (breadcrumb)
2. Title
3. Author link
4. Tags
5. Description expand/collapse
6. Module list items (top to bottom)
7. Enroll/Continue button

### Validation Rules
- Already enrolled: Show "Continue" instead of "Enroll"
- All modules complete: Show "Review Course" option

### Accessibility Notes
- Module list: `role="list"`, items `role="listitem"`
- Completion status: `aria-label="Module 1: Introduction, completed"`
- Duration: displayed as human-readable ("30 min")

### Localization Notes
- Duration: locale-formatted
- Star rating: aria-label with numeric value

### Performance Expectations
- Render: < 300ms
- Banner lazy-load: < 500ms

---

## 11. Learning Workspace

### Purpose
Main workspace for progressing through course content with module navigation sidebar.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Module Tree   |                    |
| RAIL |                        | Learning Workspace |
| 64px | [Course Title]        |                    |
|      |                        | +----------------+ |
|      | [v] Module 1 (done)   | | Progress: 45% | |
|      |   [x] Lesson 1.1     | | [============..]| |
|      |   [x] Lesson 1.2     | +----------------+ |
|      |   [x] Quiz 1         |                    |
|      |                        | [Lesson Content   |
|      | [>] Module 2 (active) |  or Module View]  |
|      |   [ ] Lesson 2.1     |                    |
|      |   [ ] Lesson 2.2     | Lorem ipsum dolor  |
|      |   [ ] Quiz 2         | sit amet...        |
|      |                        |                    |
|      | [>] Module 3 (locked) |                    |
|      |   [ ] Lesson 3.1     |                    |
|      |   [ ] Lesson 3.2     |                    |
|      |                        |                    |
|      | [v] Module 4 (locked) |                    |
|      |                        |                    |
|      | +------------------+  | [<< Prev] [Next >>]|
|      | | Module Progress  |  |                    |
|      | | 3/12 complete    |  | [Mark Complete]    |
|      | +------------------+  |                    |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region         | Position               | Size              |
|----------------|------------------------|-------------------|
| Sidebar        | Left of workspace      | 240px, module tree|
| Progress bar   | Top of main content    | Full x 60px       |
| Content area   | Center of main         | flex-grow, scroll |
| Navigation bar | Bottom of main         | Full x 48px       |

### Components

- **Module tree**: Hierarchical list, expandable/collapsible
- **Lesson items**: Clickable, completion checkmark
- **Progress indicator**: Per-module and overall
- **Content area**: Renders lesson content (markdown, images, code)
- **Prev/Next buttons**: Navigate between lessons
- **Mark Complete button**: Toggle completion status

### Navigation
- **Entry**: Course Detail "Continue" or "Enroll"
- **Exit**: Dashboard, Course Detail (back)

### Keyboard Flow
1. Module tree (arrow keys for expand/collapse, Enter to select)
2. Content area (scroll)
3. Prev/Next buttons
4. Mark Complete button

### Focus Order
1. Module tree (hierarchical)
2. Content area
3. Prev button
4. Next button
5. Mark Complete

### Validation Rules
- Locked modules: Cannot access until prerequisites complete
- All lessons in module must be complete to unlock next module

### Accessibility Notes
- Module tree: `role="tree"`, items `role="treeitem"`
- Tree expand/collapse: `aria-expanded`
- Completion: `aria-checked` or visual checkmark + `aria-label`
- Content area: `role="article"`, `aria-live="polite"` on content change

### Localization Notes
- Module names: translatable
- Duration: locale-formatted

### Performance Expectations
- Module expand/collapse: < 50ms
- Content load: < 200ms
- Progress update: < 100ms

---

## 12. Lesson Viewer

### Purpose
Display lesson content with navigation, completion tracking, and notes.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Breadcrumb: Course > Module 2 > Lesson 2.1 |
| RAIL |                                             |
| 64px | Lesson 2.1: TCP/IP Fundamentals            |
|      |                                             |
|      | +-----------------------------------------+|
|      | |                                         ||
|      | |  [Lesson Content Area]                  ||
|      | |                                         ||
|      | |  # TCP/IP Fundamentals                  ||
|      | |                                         ||
|      | |  The TCP/IP model consists of four      ||
|      | |  layers:                                ||
|      | |                                         ||
|      | |  1. Network Access Layer                ||
|      | |  2. Internet Layer                      ||
|      | |  3. Transport Layer                     ||
|      | |  4. Application Layer                   ||
|      | |                                         ||
|      | |  [Code Block / Diagram if applicable]   ||
|      | |                                         ||
|      | |  ## Key Takeaways                       ||
|      | |  ...                                    ||
|      | |                                         ||
|      | +-----------------------------------------+|
|      |                                             |
|      | +-----------------------------------------+|
|      | | Notes Panel (collapsible)               ||
|      | | [Your notes about this lesson...]       ||
|      | +-----------------------------------------+|
|      |                                             |
|      | [<< Previous]  [Mark Complete]  [Next >>]  |
|      |                                             |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region          | Position               | Size              |
|-----------------|------------------------|-------------------|
| Breadcrumb      | Top of workspace       | Full x 40px       |
| Title           | Below breadcrumb       | Full, auto height |
| Content area    | Main                   | flex-grow, scroll |
| Notes panel     | Below content          | Full x 120px (collapsible) |
| Nav bar         | Bottom                 | Full x 48px       |

### Components

- **Breadcrumb**: Clickable path
- **Title**: `<h1>`
- **Content renderer**: Markdown with syntax highlighting, images, diagrams
- **Notes panel**: `<textarea>`, auto-saved, collapsible
- **Previous button**: Disabled if first lesson
- **Mark Complete button**: Toggles completion
- **Next button**: Disabled if last lesson

### Navigation
- **Entry**: Learning Workspace module tree click
- **Exit**: Learning Workspace (back), next lesson, assessment

### Keyboard Flow
1. Content area (scroll, read)
2. Notes textarea (Tab)
3. Previous button (Tab)
4. Mark Complete (Tab)
5. Next button (Tab)

### Focus Order
1. Content area (scroll only)
2. Notes panel expand/collapse
3. Notes textarea
4. Previous button
5. Mark Complete button
6. Next button

### Validation Rules
- Notes: max 10,000 characters
- Auto-save: debounce 1000ms
- Mark complete: requires viewing > 50% of content (scroll-based)

### Accessibility Notes
- Content: `role="article"`, proper heading hierarchy (h2-h4)
- Code blocks: `<pre><code>` with language label
- Notes: `aria-label="Your notes for this lesson"`
- Mark complete: `aria-pressed` toggle state

### Localization Notes
- Content: translatable (pre-localized)
- Notes: user language only

### Performance Expectations
- Content render: < 200ms
- Notes auto-save: 1000ms debounce
- Image lazy-load: on scroll into view

---

## 13. Simulation Workspace

### Purpose
Configure and run cybersecurity simulations in isolated environments.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Config Panel  |                    |
| RAIL |                        | Simulation:        |
| 64px | Scenario:             | SQL Injection Lab  |
|      | [SQL Injection v2  v] |                    |
|      |                        | +----------------+|
|      | Environment:           | |                ||
|      | [Web App + DB       v] | |  [Execution    ||
|      |                        | |   Area]        ||
|      | Difficulty:            | |                ||
|      | [*][*][*][ ][ ]      | |  [Target:      ||
|      |                        | |   localhost:   ||
|      | Time Limit:            | |   8080]        ||
|      | [30] minutes           | |                ||
|      |                        | |  [Terminal /   ||
|      | Options:               | |   Browser      ||
|      | [x] Show hints         | |   View]        ||
|      | [ ] Auto-save state    | |                ||
|      | [ ] Guided mode        | |                ||
|      |                        | |                ||
|      | +------------------+  | +----------------+|
|      | | [Start]          |  |                    |
|      | +------------------+  | +----------------+|
|      |                        | | Results Panel  ||
|      | Elapsed: 12:34        | | Score: 85/100  ||
|      | Attempts: 3           | | Steps: 7/10    ||
|      | [Pause] [Reset]       | +----------------+|
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region          | Position               | Size              |
|-----------------|------------------------|-------------------|
| Config panel    | Left sidebar           | 240px, scrollable |
| Execution area  | Top-right of workspace | flex-grow, 60%    |
| Results panel   | Bottom-right           | flex-grow, 40%    |

### Components

- **Scenario selector**: Dropdown of available scenarios
- **Environment selector**: Target environment configuration
- **Difficulty selector**: 1-5 star rating
- **Time limit input**: Minutes
- **Options checkboxes**: Hints, auto-save, guided mode
- **Start/Pause/Reset buttons**: Simulation control
- **Elapsed timer**: `aria-live="polite"` updates
- **Execution area**: Terminal emulator or browser view
- **Results panel**: Real-time scoring and feedback

### Navigation
- **Entry**: Navigation Rail Simulations or Course Module simulation activity
- **Exit**: Back to Learning Workspace, Assessment, Dashboard

### Keyboard Flow
1. Config panel (Tab through form controls)
2. Start button
3. Execution area (terminal input)
4. Pause/Reset
5. Results panel

### Focus Order
1. Scenario selector
2. Environment selector
3. Difficulty stars
4. Time limit input
5. Options checkboxes
6. Start button
7. Execution area (on start)
8. Pause button
9. Reset button
10. Results panel

### Validation Rules
- Cannot start without selecting scenario and environment
- Time limit: 5-120 minutes
- Reset: confirmation dialog ("All progress will be lost")

### Accessibility Notes
- Config panel: `role="form"`, labeled groups
- Execution area: `role="application"` for terminal interaction
- Timer: `aria-live="polite"`, `aria-atomic="true"`
- Results: `role="region"`, `aria-label="Simulation results"`

### Localization Notes
- Timer format: MM:SS
- Difficulty labels: translatable
- Results scoring: locale-specific formatting

### Performance Expectations
- Scenario load: < 500ms
- Terminal render: 60fps
- Timer accuracy: +/- 1 second per minute

---

## 14. Assessment Workspace

### Purpose
Take timed assessments with question navigation, answer selection, and submission.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | [Back to Course]        | Assessment:      |
| RAIL |                         | Quiz 2           |
| 64px | Time Remaining:         |                  |
|      | [23:45]                 | Question 3 of 10 |
|      |                         |                  |
|      | Question Navigation:    | +----------------+|
|      | [1][2][3*][4][5]       | |  What is the   ||
|      | [6][7][8][9][10]      | |  primary purpose||
|      |                         | |  of a firewall? ||
|      | Answered: 2/10         | |                ||
|      | Flagged: 1             | | (A) To speed up||
|      |                         | |     internet   ||
|      | [Show Flagged Only]    | |                ||
|      |                         | | (B) To filter  ||
|      |                         | |     network    ||
|      |                         | |     traffic    ||
|      |                         | |                ||
|      |                         | | (C) To encrypt ||
|      |                         | |     data       ||
|      |                         | |                ||
|      |                         | | (D) To store   ||
|      |                         | |     passwords  ||
|      |                         | +----------------+|
|      |                         |                  |
|      |                         | [<< Prev] [Next>>]|
|      |                         | [Flag Question]  |
|      |                         |                  |
|      |                         | [Submit Assessment]|
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region          | Position               | Size              |
|-----------------|------------------------|-------------------|
| Left panel      | Sidebar area           | 240px             |
| Timer           | Top of main            | 200 x 40px        |
| Question nav    | Left sidebar           | Full x auto       |
| Question area   | Center main            | flex-grow         |
| Action bar      | Bottom main            | Full x 48px       |

### Components

- **Timer**: Countdown, `aria-live="polite"` every 60s, red flash at 5min
- **Question navigator**: Numbered buttons, color-coded (answered, current, flagged)
- **Question display**: Number, text, answer options
- **Answer options**: Radio buttons (single choice) or checkboxes (multiple)
- **Prev/Next buttons**: Navigate questions
- **Flag button**: Toggle flag for review
- **Submit button**: Confirmation dialog, disabled until minimum questions answered

### Navigation
- **Entry**: From course assessment activity or assessment list
- **Exit**: Assessment Results (submit) or back to course (save progress)

### Keyboard Flow
1. Timer (read only)
2. Question navigator (arrow keys grid)
3. Question content (scroll)
4. Answer options (arrow keys for radio, space for checkbox)
5. Prev/Next buttons
6. Flag button
7. Submit button

### Focus Order
1. Timer
2. Question navigator (current question highlighted)
3. Question text
4. Answer option A
5. Answer option B
6. Answer option C
7. Answer option D
8. Previous button
9. Next button
10. Flag button
11. Submit button

### Validation Rules
- Cannot submit with 0 answers
- Warning at 5 minutes remaining (toast)
- Auto-submit at 0:00
- Each question: exactly 1 answer for MCQ, 1+ for multi-select
- Cannot navigate away without confirming save

### Accessibility Notes
- Timer: `role="timer"`, `aria-live="polite"`
- Question nav: `role="navigation"`, `aria-label="Question navigator"`
- Answers: `role="radiogroup"` or `role="group"`
- Flag state: `aria-pressed`, visual indicator

### Localization Notes
- Timer format: MM:SS
- Question numbering: locale-appropriate
- Answer labels: (A), (B) or locale equivalents

### Performance Expectations
- Question switch: < 50ms
- Timer update: every second, no frame drops
- Auto-submit: within 2 seconds of timeout

---

## 15. Assessment Results

### Purpose
Display assessment score, question-by-question review with explanations.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Breadcrumb: Course > Quiz 2 > Results      |
| RAIL |                                             |
| 64px | +-----------------------------------------+|
|      | |         ASSESSMENT RESULTS               ||
|      | |                                          ||
|      | |    +-----------+                          ||
|      | |    |   85/100  |                          ||
|      | |    |    85%    |                          ||
|      | |    |   PASS    |                          ||
|      | |    +-----------+                          ||
|      | |                                          ||
|      | |  Correct: 8  |  Incorrect: 2  | Time: 18m||
|      | +-----------------------------------------+|
|      |                                             |
|      | QUESTION REVIEW:                            |
|      |                                             |
|      | Q1. What is a firewall?          [Correct]  |
|      | Your answer: (B) To filter traffic          |
|      | Explanation: A firewall monitors...         |
|      |                                             |
|      | Q2. Which port does HTTPS use?   [Correct]  |
|      | Your answer: 443                             |
|      | Explanation: HTTPS uses port 443...          |
|      |                                             |
|      | Q3. What is SQL injection?       [Wrong]    |
|      | Your answer: (A) To speed up queries         |
|      | Correct answer: (C) To insert malicious SQL  |
|      | Explanation: SQL injection attacks...        |
|      |                                             |
|      | [<< Previous]  [Back to Course]  [Next >>]  |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region          | Position               | Size              |
|-----------------|------------------------|-------------------|
| Breadcrumb      | Top                    | Full x 40px       |
| Score card      | Below breadcrumb       | Center, 400px     |
| Stats row       | Below score            | Full, 3 columns   |
| Question review | Main area              | Full, scrollable  |
| Action bar      | Bottom                 | Full x 48px       |

### Components

- **Score card**: Large score display, pass/fail indicator
- **Stats row**: Correct count, incorrect count, time taken
- **Question review list**: Each question with answer, correct answer, explanation
- **Correct/Wrong badges**: Color-coded indicators
- **Explanation expandable**: Click to show/hide
- **Navigation**: Prev/Next through questions, Back to Course

### Navigation
- **Entry**: After Assessment submission or timeout
- **Exit**: Back to Course, retake assessment

### Keyboard Flow
1. Score card (read only)
2. Stats row (read only)
3. Question review items (Tab through each)
4. Explanation expand/collapse (Enter)
5. Navigation buttons

### Focus Order
1. Score display
2. Stats items (left to right)
3. Question 1 review
4. Question 2 review
5. ... (each question)
6. Previous button
7. Back to Course button
8. Next button

### Validation Rules
- Score must be non-negative
- Pass threshold: configurable (default 70%)

### Accessibility Notes
- Score: `role="status"`, `aria-live="polite"`
- Pass/Fail: `aria-label="Result: Pass"` or `aria-label="Result: Fail"`
- Explanations: `aria-expanded` toggle
- Correct/Wrong: text labels, not color alone

### Localization Notes
- Score: locale number format
- Time: locale format
- Pass/Fail labels: translatable

### Performance Expectations
- Render: < 200ms
- Explanation toggle: < 50ms

---

## 16. Report Viewer

### Purpose
Generate, view, and export reports on courses, assessments, and student progress.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Report Types  |                    |
| RAIL |                        | Report Viewer      |
| 64px | Report Type:          |                    |
|      | [Course Progress    v] | Parameters:       |
|      |                        |                    |
|      | Available Reports:     | Date Range:        |
|      | [>] Course Progress    | [2026-01-01] to    |
|      | [>] Assessment Scores  | [2026-07-19]       |
|      | [>] Student Activity   |                    |
|      | [>] Completion Rates   | Course: [All  v]   |
|      | [>] Engagement Metrics |                    |
|      |                        | Student: [All  v]  |
|      |                        |                    |
|      |                        | [Generate Report]  |
|      |                        |                    |
|      |                        | +----------------+|
|      |                        | | RESULTS TABLE  ||
|      |                        | | Name | Score   ||
|      |                        | | Alice| 92%     ||
|      |                        | | Bob  | 78%     ||
|      |                        | | Carol| 85%     ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | +----------------+|
|      |                        | | [Chart Area]   ||
|      |                        | | Bar/Line/Pie   ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | [Export PDF]       |
|      |                        | [Export CSV]       |
|      |                        | [Export JSON]      |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region          | Position               | Size              |
|-----------------|------------------------|-------------------|
| Sidebar         | Left                   | 240px, report list|
| Parameter form  | Top of main            | Full, auto height |
| Results table   | Below parameters       | Full, scrollable  |
| Chart area      | Below table            | Full x 300px      |
| Export buttons  | Bottom                 | Row               |

### Components

- **Report type selector**: Sidebar list
- **Parameter form**: Date range pickers, dropdowns
- **Generate button**: Triggers report generation
- **Results table**: Sortable columns, pagination
- **Chart**: Bar, line, or pie depending on report type
- **Export buttons**: PDF, CSV, JSON

### Navigation
- **Entry**: Navigation Rail Reports
- **Exit**: Dashboard, Course Detail, Student Detail

### Keyboard Flow
1. Report type sidebar (arrow keys)
2. Parameter form (Tab through fields)
3. Generate button
4. Results table (arrow keys for cell navigation)
5. Chart (read only)
6. Export buttons

### Focus Order
1. Report type list
2. Date range inputs
3. Course dropdown
4. Student dropdown
5. Generate button
6. Results table
7. Export buttons

### Validation Rules
- Date range: start < end, not in future beyond today
- At least one parameter must be set
- Report generation timeout: 30 seconds

### Accessibility Notes
- Table: `<table>` with `<th>`, sortable columns indicated
- Chart: `role="img"` with text alternative summary
- Export: `aria-label="Export as PDF"`

### Localization Notes
- Date formats: locale-appropriate
- Number formats: locale-specific
- Currency (if applicable): locale format

### Performance Expectations
- Report generation: < 5 seconds for up to 1000 records
- Chart render: < 500ms
- Export PDF: < 3 seconds

---

## 17. Certificate Gallery

### Purpose
Display all earned certificates in a filterable grid.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar (filter)       |                    |
| RAIL |                        | My Certificates    |
| 64px | Filter:               |                    |
|      |                        | Sort: [Newest v]   |
|      | Course: [All       v] |                    |
|      | Date: [All Time    v] | +--------+ +------+ |
|      |                        | |Cert    | |Cert  | |
|      | Search:               | |Card    | |Card  | |
|      | [Search certs...   ] | |[img]   | |[img] | |
|      |                        | |Course  | |Course|
|      |                        | |Date    | |Date  | |
|      |                        | |[View]  | |[View]| |
|      |                        | +--------+ +------+ |
|      |                        | +--------+ +------+ |
|      |                        | |Cert    | |Cert  | |
|      |                        | |Card    | |Card  | |
|      |                        | |        | |      | |
|      |                        | +--------+ +------+ |
|      |                        |                    |
|      |                        | 8 certificates     |
|      |                        | [Download All]     |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Sidebar       | Left                   | 240px, filters    |
| Header        | Top of main            | Full, title+sort  |
| Card grid     | Main area              | 3-4 columns       |
| Footer        | Bottom                 | Count + actions   |

### Components

- **Filter sidebar**: Course, date range, search
- **Sort dropdown**: Newest, Oldest, Course name A-Z
- **Certificate cards**: Thumbnail preview, course name, date, view button
- **Certificate count**: "8 certificates"
- **Download All button**: ZIP export

### Navigation
- **Entry**: User profile dropdown, Dashboard quick link
- **Exit**: Certificate Detail, Dashboard

### Keyboard Flow
1. Search input
2. Filter dropdowns
3. Certificate card grid (arrow keys)
4. Download All button

### Focus Order
1. Search input
2. Course filter
3. Date filter
4. Sort dropdown
5. Card grid (left-right, up-down)
6. Download All

### Validation Rules
- Empty: "No certificates yet. Complete courses to earn certificates."
- Search: minimum 2 characters, debounced

### Accessibility Notes
- Card grid: `role="list"`, cards `role="listitem"`
- Certificate thumbnail: `role="img"`, `aria-label="Certificate for {course}"`
- Date: `<time datetime="...">`

### Localization Notes
- Date: locale format
- Certificate text: pre-localized per course

### Performance Expectations
- Grid render (50 certs): < 300ms
- Thumbnail lazy-load: on scroll
- Search: < 150ms debounced

---

## 18. Certificate Detail

### Purpose
View, download, and print individual certificates.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Breadcrumb: Certificates > Course Name      |
| RAIL |                                             |
| 64px | +-----------------------------------------+|
|      | |                                         ||
|      | |     [Certificate Preview]               ||
|      | |     (rendered HTML, 600x425)            ||
|      | |                                         ||
|      | |     Certificate of Completion           ||
|      | |     AuthShield Lab                      ||
|      | |                                         ||
|      | |     This certifies that                 ||
|      | |     Alex Johnson has completed          ||
|      | |     Advanced Cryptography               ||
|      | |                                         ||
|      | |     Date: July 15, 2026                 ||
|      | |     Credential ID: ASL-2026-00142       ||
|      | |                                         ||
|      | +-----------------------------------------+|
|      |                                             |
|      | Certificate Details:                        |
|      | +-----------------------------------------+|
|      | | Course:     Advanced Cryptography       ||
|      | | Completed:  July 15, 2026              ||
|      | | Score:      92%                         ||
|      | | Duration:   40 hours                    ||
|      | | ID:         ASL-2026-00142              ||
|      | | Issuer:     AuthShield Lab              ||
|      | +-----------------------------------------+|
|      |                                             |
|      | [Download PDF]  [Print]  [Share]           |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region          | Position               | Size              |
|-----------------|------------------------|-------------------|
| Preview         | Center top             | 600 x 425px       |
| Details table   | Below preview          | 400px, centered   |
| Action buttons  | Bottom                 | Row, centered     |

### Components

- **Certificate preview**: Rendered HTML/CSS certificate
- **Details table**: Key-value pairs
- **Download PDF button**: Generates PDF from preview
- **Print button**: Opens print dialog
- **Share button**: Copy credential ID or generate shareable link

### Navigation
- **Entry**: Certificate Gallery card click
- **Exit**: Certificate Gallery (back)

### Keyboard Flow
1. Preview (read only)
2. Details table (Tab through cells)
3. Download button
4. Print button
5. Share button

### Focus Order
1. Certificate preview
2. Details table
3. Download PDF button
4. Print button
5. Share button

### Validation Rules
- Certificate must exist and be valid
- Download: generates PDF < 5 seconds
- Print: opens system print dialog

### Accessibility Notes
- Preview: `role="img"`, `aria-label="Certificate preview"`
- Details: `<dl>` definition list
- Download: `aria-label="Download certificate as PDF"`

### Localization Notes
- Certificate text: pre-rendered in certificate language
- Date on certificate: locale-formatted

### Performance Expectations
- Preview render: < 300ms
- PDF generation: < 3 seconds

---

## 19. Analytics Dashboard

### Purpose
Visualize learning analytics with charts, filters, and exportable data.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Dimensions    |                    |
| RAIL |                        | Analytics          |
| 64px | Dimensions:           |                    |
|      | [x] By Course         | Date Range:        |
|      | [x] By Student        | [Last 30 days  v]  |
|      | [ ] By Time           |                    |
|      |                        | [Apply Filters]    |
|      | Metrics:              |                    |
|      | [x] Completion Rate   | +----------------+|
|      | [x] Avg Score         | | [Line Chart]   ||
|      | [x] Time Spent        | | Completion     ||
|      | [ ] Drop-off Rate     | | over time      ||
|      |                        | +----------------+|
|      |                        |                    |
|      | +------------------+  | +----------------+|
|      | | Summary Stats    |  | | [Bar Chart]    ||
|      | | Avg Score: 82%   |  | | Scores by      ||
|      | | Completion: 67%  |  | | course         ||
|      | | Active: 142      |  | +----------------+|
|      | +------------------+  |                    |
|      |                        | +----------------+|
|      |                        | | [Pie Chart]    ||
|      |                        | | By category    ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | [Export PNG]       |
|      |                        | [Export CSV]       |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region          | Position               | Size              |
|-----------------|------------------------|-------------------|
| Sidebar         | Left                   | 240px, controls   |
| Summary stats   | Top-left of main       | 200px             |
| Date range      | Top-right of main      | Auto              |
| Charts          | Main area              | 2-column grid     |
| Export buttons  | Bottom                 | Row               |

### Components

- **Dimension checkboxes**: Multi-select data grouping
- **Metric checkboxes**: Multi-select what to measure
- **Date range selector**: Preset or custom
- **Apply Filters button**: Refreshes charts
- **Summary stats cards**: Key metrics at a glance
- **Line chart**: Time-series data
- **Bar chart**: Comparison data
- **Pie chart**: Distribution data
- **Export buttons**: PNG (charts), CSV (data)

### Navigation
- **Entry**: Navigation Rail Analytics or Reports section
- **Exit**: Dashboard, specific course/student detail

### Keyboard Flow
1. Dimension checkboxes
2. Metric checkboxes
3. Date range selector
4. Apply Filters button
5. Charts (read only, scroll)
6. Export buttons

### Focus Order
1. Dimensions group
2. Metrics group
3. Date range
4. Apply Filters
5. Summary stats
6. Charts (Tab through each)
7. Export buttons

### Validation Rules
- At least one dimension and one metric required
- Date range: start <= end
- Chart data: max 500 data points for performance

### Accessibility Notes
- Charts: `role="img"` with text alternative
- Summary stats: `role="status"`, `aria-live="polite"`
- Data table fallback for charts (toggle view)

### Localization Notes
- Number formats: locale-specific
- Date formats: locale-appropriate
- Chart labels: translatable

### Performance Expectations
- Chart render (1000 points): < 500ms
- Filter apply: < 300ms
- Export PNG: < 2 seconds

---

## 20. Plugin Manager

### Purpose
Install, update, and manage plugins that extend platform functionality.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Categories   |                    |
| RAIL |                        | Plugin Manager     |
| 64px | Categories:           |                    |
|      | [x] Security Tools    | [Installed] [Available]|
|      | [x] Content Packs     |                    |
|      | [x] Simulations       | +--------+ +------+ |
|      | [x] Assessment        | |Plugin  | |Plugin| |
|      | [x] Integrations      | |Card    | |Card  | |
|      |                        | |v2.1.0  | |v1.3.0| |
|      | Search:               | |[Update]| |[Inst]|
|      | [Search plugins... ] | |Desc... | |Desc..|
|      |                        | +--------+ +------+ |
|      |                        | +--------+ +------+ |
|      |                        | |Plugin  | |Plugin| |
|      |                        | |Card    | |Card  | |
|      |                        | |        | |      | |
|      |                        | +--------+ +------+ |
|      |                        |                    |
|      |                        | 12 plugins installed|
|      |                        | [Browse Store]     |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Sidebar       | Left                   | 240px, categories |
| Tab bar       | Top of main            | Full, 40px        |
| Plugin grid   | Main area              | 2-3 columns       |
| Footer        | Bottom                 | Count + actions   |

### Components

- **Category sidebar**: Multi-select filter
- **Tab bar**: Installed / Available toggle
- **Search input**: Search by name/description
- **Plugin cards**: Name, version, description, status badge, action button
- **Install/Update/Remove buttons**: Plugin management actions
- **Browse Store button**: Opens plugin marketplace (if online)

### Navigation
- **Entry**: Settings or Navigation Rail
- **Exit**: Settings, Dashboard

### Keyboard Flow
1. Category checkboxes
2. Tab bar (arrow keys)
3. Search input
4. Plugin cards (grid navigation)
5. Action buttons on cards

### Focus Order
1. Installed/Available tabs
2. Search input
3. Category filters
4. Plugin cards (left-right, up-down)
5. Action button on each card

### Validation Rules
- Remove: confirmation dialog
- Update: progress indicator
- Install: permission review dialog first

### Accessibility Notes
- Tab bar: `role="tablist"`, `role="tab"`, `role="tabpanel"`
- Plugin status: `aria-label="Plugin: {name}, version {ver}, installed"`
- Card grid: `role="list"`

### Localization Notes
- Plugin names: may be localized
- Descriptions: translatable

### Performance Expectations
- Grid render (50 plugins): < 200ms
- Install: < 10 seconds depending on size
- Search: < 150ms debounced

---

## 21. Accessibility Center

### Purpose
Centralized accessibility settings with live preview and testing tools.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Setting Groups|                    |
| RAIL |                        | Accessibility     |
| 64px | Groups:               | Center             |
|      | [>] Theme             |                    |
|      | [>] Typography        | Theme:             |
|      | [>] Motion            | (o) Light           |
|      | [>] Contrast          | ( ) Dark            |
|      | [>] Screen Reader     | ( ) High Contrast   |
|      | [>] Keyboard          |                    |
|      | [>] Focus Indicators  | Preview:           |
|      | [>] Color             | +----------------+|
|      |                        | |                ||
|      |                        | | [Live Preview  ||
|      |                        | |  of selected   ||
|      |                        | |  theme]        ||
|      |                        | |                ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | [Reset to Defaults]|
|      |                        | [Export Settings]  |
|      |                        | [Import Settings]  |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Sidebar       | Left                   | 240px, groups     |
| Setting area  | Top of main            | Form controls     |
| Preview area  | Below settings         | 300px height      |
| Action buttons| Bottom                 | Row               |

### Components

- **Setting groups**: Expandable sections
- **Theme selector**: Radio group with live preview
- **Typography controls**: Font size slider, font family selector
- **Motion controls**: Reduce motion toggle, animation speed
- **Contrast controls**: Minimum contrast ratio selector
- **Screen reader settings**: Announce updates, verbosity level
- **Keyboard settings**: Key repeat delay, sticky keys
- **Focus indicator settings**: Color, width, style
- **Color settings**: Color blind mode selector
- **Live preview**: Real-time preview of settings changes
- **Reset/Export/Import buttons**

### Navigation
- **Entry**: Settings > Accessibility or Navigation Rail
- **Exit**: Settings, Dashboard

### Keyboard Flow
1. Setting groups sidebar (arrow keys)
2. Form controls within group (Tab)
3. Live preview (scroll)
4. Action buttons

### Focus Order
1. Setting groups (top to bottom)
2. Current group's form controls
3. Live preview area
4. Reset button
5. Export button
6. Import button

### Validation Rules
- Font size: 12px - 24px range
- Contrast ratio: minimum 3:1 for UI, 4.5:1 for text
- Changes apply immediately (live preview)

### Accessibility Notes
- This screen must itself be fully accessible
- Live preview: `aria-live="polite"` announces changes
- Settings: proper labels, descriptions, and groupings

### Localization Notes
- All labels translatable
- Font families may vary by locale

### Performance Expectations
- Live preview update: < 50ms
- Theme switch: < 100ms

---

## 22. Localization Center

### Purpose
Manage language, regional formats, and locale-specific settings.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Regions      |                    |
| RAIL |                        | Localization       |
| 64px | Regions:              | Center             |
|      | [x] Americas          |                    |
|      | [x] Europe            | Language:          |
|      | [x] Asia-Pacific      | [English (US)   v] |
|      | [x] Africa            |                    |
|      |                        | Preview:           |
|      |                        | +----------------+|
|      |                        | | Date: 07/19/2026||
|      |                        | | Time: 2:30 PM  ||
|      |                        | | Number: 1,234.56||
|      |                        | | Currency: $100  ||
|      |                        | | Currency: EUR 100||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | Regional Settings: |
|      |                        | Date Format: [v]  |
|      |                        | Time Format: [v]  |
|      |                        | Number Format: [v] |
|      |                        | First Day: [v]    |
|      |                        |                    |
|      |                        | [Apply & Restart] |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Sidebar       | Left                   | 240px, regions    |
| Language      | Top of main            | Dropdown          |
| Preview       | Below language         | 300px box         |
| Regional form | Below preview          | Form controls     |
| Apply button  | Bottom                 | Button            |

### Components

- **Region filter sidebar**: Filter languages by region
- **Language selector**: Dropdown with search
- **Preview box**: Shows formatted date, time, number, currency
- **Regional settings form**: Date/time/number formats, first day of week
- **Apply & Restart button**: Applies changes, restarts app

### Navigation
- **Entry**: Settings > Localization or Navigation Rail
- **Exit**: Settings, Dashboard (after restart)

### Keyboard Flow
1. Region filter checkboxes
2. Language dropdown
3. Regional format dropdowns
4. Apply button

### Focus Order
1. Region filters
2. Language selector
3. Date format dropdown
4. Time format dropdown
5. Number format dropdown
6. First day of week
7. Apply & Restart button

### Validation Rules
- Language must be selected
- Apply: confirmation dialog ("Application will restart")

### Accessibility Notes
- Preview: `aria-live="polite"` updates on format change
- Language selector: `aria-label="Select language"`
- Restart warning: `role="alert"`

### Localization Notes
- Language names displayed in their own language
- Preview text updates per selected format

### Performance Expectations
- Preview update: < 50ms
- Restart: < 3 seconds

---

## 23. Backup & Restore

### Purpose
Create, manage, and restore application backups.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Operations   |                    |
| RAIL |                        | Backup & Restore   |
| 64px | Operations:           |                    |
|      | [>] Create Backup     | [Backups] [Schedule]|
|      | [>] Restore           |                    |
|      | [>] Schedule          | +--------+ +------+ |
|      |                        | |Backup  | |Backup| |
|      |                        | |Card    | |Card  | |
|      |                        | |Jul 19  | |Jul 12| |
|      |                        | |1.2 GB  | |1.1GB | |
|      |                        | |Full    | |Full  | |
|      |                        | |[Restore||[Resto]||
|      |                        | |[Delete]||[Delet]||
|      |                        | +--------+ +------+ |
|      |                        | +--------+ +------+ |
|      |                        | |Backup  | |Backup| |
|      |                        | |Jul 5   | |Jun 28| |
|      |                        | |1.0 GB  | |980MB | |
|      |                        | |Full    | |Diff  | |
|      |                        | |[Restore||[Resto]||
|      |                        | |[Delete]||[Delet]||
|      |                        | +--------+ +------+ |
|      |                        |                    |
|      |                        | Schedule:          |
|      |                        | [x] Daily at 2AM   |
|      |                        | [ ] Weekly          |
|      |                        | Retention: [30 days]|
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Sidebar       | Left                   | 240px, operations |
| Tab bar       | Top of main            | Full, 40px        |
| Backup grid   | Main area              | 2 columns         |
| Schedule form | Below grid             | Form controls     |

### Components

- **Operations sidebar**: Create, Restore, Schedule
- **Tab bar**: Backups list / Schedule settings
- **Backup cards**: Date, size, type, restore/delete buttons
- **Create backup button**: Triggers backup wizard dialog
- **Schedule form**: Frequency, time, retention policy

### Navigation
- **Entry**: Settings > Backup or Navigation Rail
- **Exit**: Settings, Dashboard

### Keyboard Flow
1. Operations sidebar
2. Tab bar
3. Backup cards grid (arrow keys)
4. Action buttons on cards
5. Schedule form controls

### Focus Order
1. Create Backup operation
2. Restore operation
3. Schedule operation
4. Backup cards (left-right, up-down)
5. Restore button per card
6. Delete button per card
7. Schedule form

### Validation Rules
- Delete: confirmation dialog
- Restore: confirmation + backup preview
- Schedule: at least one frequency selected
- Maximum 30 backups stored locally

### Accessibility Notes
- Backup cards: `role="article"`, `aria-label="Backup from {date}"`
- Delete: `aria-describedby` with confirmation warning
- Schedule: `role="form"` with proper labels

### Localization Notes
- Dates: locale-formatted
- File sizes: locale-specific (GB vs Go)
- Time: locale-formatted

### Performance Expectations
- Backup creation: < 30 seconds for 1GB
- Restore: < 60 seconds for 1GB
- Backup list render: < 200ms

---

## 24. Diagnostics

### Purpose
View system information, run health checks, and export diagnostic logs.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Categories   |                    |
| RAIL |                        | Diagnostics         |
| 64px | Categories:           |                    |
|      | [>] System Info       | System Info:       |
|      | [>] Health Checks     | +----------------+|
|      | [>] Log Viewer        | | OS: Linux 6.x  ||
|      | [>] Performance       | | RAM: 8GB       ||
|      |                        | | CPU: 4 cores   ||
|      |                        | | Disk: 256GB SSD||
|      |                        | | Electron: 28.x ||
|      |                        | | Node: 20.x     ||
|      |                        | | App: 2.4.1     ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | Health Checks:    |
|      |                        | +----------------+|
|      |                        | | [OK] Database   ||
|      |                        | | [OK] Storage    ||
|      |                        | | [WARN] Plugins  ||
|      |                        | | [OK] Network    ||
|      |                        | | [OK] Memory     ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | [Run All Checks]  |
|      |                        | [Export Diagnostics]|
|      |                        | [Clear Logs]       |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Sidebar       | Left                   | 240px, categories |
| Info panels   | Main area              | Stacked sections  |
| Action buttons| Bottom                 | Row               |

### Components

- **Category sidebar**: System Info, Health Checks, Log Viewer, Performance
- **System info table**: Key-value pairs of system information
- **Health check list**: Status indicators (OK, WARN, FAIL)
- **Log viewer**: Filterable, searchable log lines
- **Performance metrics**: CPU, memory, disk usage over time
- **Run All Checks button**: Re-runs health checks
- **Export button**: Generates diagnostic ZIP
- **Clear Logs button**: Confirmation required

### Navigation
- **Entry**: Settings > Diagnostics or Navigation Rail
- **Exit**: Settings, Dashboard

### Keyboard Flow
1. Category sidebar
2. System info table (Tab)
3. Health checks (Tab through each)
4. Log viewer (scroll, search)
5. Action buttons

### Focus Order
1. Categories
2. System info panel
3. Health check items
4. Log viewer search
5. Log lines
6. Run All Checks
7. Export Diagnostics
8. Clear Logs

### Validation Rules
- Health checks: timeout 10 seconds per check
- Log viewer: max 10,000 lines visible
- Clear logs: confirmation dialog

### Accessibility Notes
- Health status: `aria-label="Database check: OK"` (not just color)
- Log viewer: `role="log"`, `aria-live="polite"`
- System info: `<table>` with proper headers

### Localization Notes
- System info: English (technical terms)
- Health check names: translatable
- Log messages: English (technical)

### Performance Expectations
- Health checks: < 10 seconds total
- Log viewer: 60fps scrolling for 10,000 lines
- Export: < 10 seconds

---

## 25. Settings

### Purpose
Application-wide settings organized in tabbed categories.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Categories   |                    |
| RAIL |                        | Settings            |
| 64px | Categories:           |                    |
|      | [>] General           | [General][Account] |
|      | [>] Account           | [Appearance][A11y] |
|      | [>] Appearance        | [Advanced][Plugins]|
|      | [>] Accessibility     | [Backup][Diagnostics]
|      | [>] Keyboard          |                    |
|      | [>] Notifications     | General Settings:  |
|      | [>] Privacy           |                    |
|      | [>] Plugins           | Application:       |
|      | [>] Backup            | [x] Auto-save      |
|      | [>] Diagnostics       | [ ] Check updates  |
|      | [>] Advanced          | [x] Show tips      |
|      |                        |                    |
|      |                        | Startup:           |
|      |                        | (o) Show Dashboard |
|      |                        | ( ) Show last view |
|      |                        | ( ) Show Login     |
|      |                        |                    |
|      |                        | Language:          |
|      |                        | [English (US)   v] |
|      |                        |                    |
|      |                        | [Save Changes]     |
|      |                        | [Reset to Defaults]|
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Sidebar       | Left                   | 240px, categories |
| Tab bar       | Top of main            | Full, 40px        |
| Form area     | Main area              | flex-grow, scroll |
| Action buttons| Bottom                 | Row               |

### Components

- **Category sidebar**: Settings group list
- **Tab bar**: Duplicate of sidebar for compact mode
- **Form controls**: Checkboxes, radios, dropdowns, sliders, text inputs
- **Save Changes button**: Persists settings
- **Reset to Defaults button**: Confirmation required

### Navigation
- **Entry**: Navigation Rail Settings or Ctrl+,
- **Exit**: Previous screen, Dashboard

### Keyboard Flow
1. Category sidebar (arrow keys)
2. Form controls (Tab through each group)
3. Save button
4. Reset button

### Focus Order
1. Categories (top to bottom)
2. Form controls within category (top to bottom)
3. Save Changes button
4. Reset to Defaults button

### Validation Rules
- Each setting validated per type
- Save: only if changes made (dirty state tracking)
- Reset: confirmation dialog

### Accessibility Notes
- Form controls: proper labels, descriptions
- Groups: `<fieldset>` with `<legend>`
- Dirty state: `aria-live="polite"` "Unsaved changes"

### Localization Notes
- All labels translatable
- Setting values: locale-appropriate

### Performance Expectations
- Category switch: < 50ms
- Save: < 200ms
- Reset: < 100ms

---

## 26. Help Center

### Purpose
Searchable help documentation with categorized topics.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Topics       |                    |
| RAIL |                        | Help Center         |
| 64px | Topics:               |                    |
|      | [v] Getting Started   | [Search help...  ] |
|      |   [ ] First Steps    |                    |
|      |   [ ] Your Dashboard  | Popular Topics:    |
|      |   [ ] Taking Courses  | +----------------+|
|      | [>] Using Simulations| | Getting Started ||
|      | [>] Assessments       | | Quick guide     ||
|      | [>] Reports           | +----------------+|
|      | [>] Certificates      | +----------------+|
|      | [>] Plugins           | | Keyboard        ||
|      | [>] Settings          | | Shortcuts       ||
|      | [>] Troubleshooting   | +----------------+|
|      |                        | +----------------+|
|      |                        | | Offline Mode    ||
|      |                        | | How it works    ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | Article:           |
|      |                        | +----------------+|
|      |                        | | # Getting      ||
|      |                        | | Started        ||
|      |                        | |                ||
|      |                        | | Welcome to     ||
|      |                        | | AuthShield Lab!||
|      |                        | | This guide     ||
|      |                        | | will help you  ||
|      |                        | | get started... ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | [<< Prev] [Next>>]|
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Sidebar       | Left                   | 240px, topic tree |
| Search        | Top of main            | Full, 48px        |
| Popular       | Below search           | Card grid         |
| Article view  | Below popular          | flex-grow, scroll |
| Navigation    | Bottom                 | Prev/Next         |

### Components

- **Topic tree**: Hierarchical, expandable/collapsible
- **Search input**: Full-text search across articles
- **Popular topics**: Quick access cards
- **Article renderer**: Markdown with syntax highlighting
- **Prev/Next navigation**: Sequential article navigation

### Navigation
- **Entry**: Navigation Rail Help or F1
- **Exit**: Dashboard, any screen (help overlay)

### Keyboard Flow
1. Search input (auto-focus)
2. Topic tree (arrow keys)
3. Popular topic cards (Tab)
4. Article content (scroll)
5. Prev/Next buttons

### Focus Order
1. Search input
2. Topic tree
3. Popular topics
4. Article content
5. Previous article
6. Next article

### Validation Rules
- Search: minimum 2 characters
- No results: "No articles match your search. Try different keywords."

### Accessibility Notes
- Topic tree: `role="tree"`, `role="treeitem"`
- Article: `role="article"`, proper heading hierarchy
- Search results: `aria-live="polite"` count

### Localization Notes
- Article content: translatable
- Topic names: translatable

### Performance Expectations
- Article load: < 100ms (local files)
- Search: < 150ms debounced
- Tree expand/collapse: < 50ms

---

## 27. About

### Purpose
Display version information, credits, licenses, and links.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  |                        |                    |
| RAIL |                        | About              |
| 64px |                        |                    |
|      |                        | +----------------+|
|      |                        | | AuthShield Logo||
|      |                        | |    80x80       ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | AuthShield Lab    |
|      |                        | Version 2.4.1     |
|      |                        | Build 2026.07.19  |
|      |                        |                    |
|      |                        | +----------------+|
|      |                        | | Credits         ||
|      |                        | | Lead Developer  ||
|      |                        | | QA Team        ||
|      |                        | | Translators    ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | +----------------+|
|      |                        | | Licenses        ||
|      |                        | | Open source     ||
|      |                        | | libraries used  ||
|      |                        | | [View Details]  ||
|      |                        | +----------------+|
|      |                        |                    |
|      |                        | Links:            |
|      |                        | [Website]         |
|      |                        | [Documentation]   |
|      |                        | [Report Issue]    |
|      |                        | [License]         |
|      |                        |                    |
|      |                        | (c) 2026 AuthShield|
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Logo          | Center, top            | 80 x 80px         |
| Version info  | Below logo             | Centered          |
| Credits       | Below version          | 400px max         |
| Licenses      | Below credits          | 400px max         |
| Links         | Below licenses         | Vertical list     |
| Copyright     | Bottom                 | Centered          |

### Components

- **Logo**: Branding image
- **Version text**: Semantic version
- **Build text**: Build date
- **Credits list**: Contributors
- **Licenses list**: Open source licenses with expandable details
- **External links**: Website, docs, issue tracker, license
- **Copyright notice**: Year and entity

### Navigation
- **Entry**: Settings > About or Navigation Rail
- **Exit**: Settings, Dashboard

### Keyboard Flow
1. Logo (skip)
2. Credits section (Tab)
3. Licenses section (Tab)
4. Link buttons (Tab)

### Focus Order
1. Credits section
2. Licenses section
3. Website link
4. Documentation link
5. Report Issue link
6. License link

### Validation Rules
- Version must match package.json
- Links: open in external browser

### Accessibility Notes
- Version: `aria-label="Version 2.4.1, build 2026-07-19"`
- Links: `target="_blank"` with `rel="noopener noreferrer"`
- Credits: `<ul>` list

### Localization Notes
- Credits: original names preserved
- Licenses: English (legal)
- Copyright: year dynamic

### Performance Expectations
- Render: < 100ms (static)
- License expand: < 50ms

---

## 28. Keyboard Shortcut Reference

### Purpose
Searchable table of all keyboard shortcuts grouped by category.

### ASCII Wireframe

```
+---------------------------------------------------+
| App Header                                         |
+------+--------------------------------------------+
| NAV  | Sidebar: Categories   |                    |
| RAIL |                        | Keyboard Shortcuts |
| 64px | Categories:           |                    |
|      | [x] Global            | [Search shortcuts ]|
|      | [x] Navigation        |                    |
|      | [x] Course            | Category: [All v] |
|      | [x] Assessment        |                    |
|      | [x] Simulation        | +------+----------+|
|      | [x] Editor            | |Shortcut| Action  ||
|      | [x] Accessibility     | +------+----------+|
|      | [x] Dialog            | |Ctrl+K | Search   ||
|      |                        | |Ctrl+D |Dashboard||
|      |                        | |Ctrl+, |Settings ||
|      |                        | |Ctrl+. | FAB     ||
|      |                        | |F1     | Help    ||
|      |                        | |Esc    | Close   ||
|      |                        | +------+----------+|
|      |                        |                    |
|      |                        | Navigation:        |
|      |                        | +------+----------+|
|      |                        | |Alt+1 | Dashboard||
|      |                        | |Alt+2 | Courses  ||
|      |                        | |Alt+3 | Sim      ||
|      |                        | |Alt+4 | Assess   ||
|      |                        | |Alt+5 | Reports  ||
|      |                        | +------+----------+|
|      |                        |                    |
|      |                        | [Export Shortcuts] |
+------+--------------------------------------------+
| Status Bar                                         |
+---------------------------------------------------+
```

### Layout Regions

| Region        | Position               | Size              |
|---------------|------------------------|-------------------|
| Sidebar       | Left                   | 240px, categories |
| Search        | Top of main            | Full, 48px        |
| Category filter| Below search          | Dropdown          |
| Shortcut tables| Main area             | Stacked tables    |
| Export button | Bottom                 | Button            |

### Components

- **Category sidebar**: Filter by shortcut category
- **Search input**: Search shortcut actions
- **Category dropdown**: Additional filter
- **Shortcut tables**: Grouped by category, key + action columns
- **Export button**: Export shortcuts as PDF or text

### Navigation
- **Entry**: F1 -> Help -> Shortcuts, or Settings -> Keyboard
- **Exit**: Previous screen

### Keyboard Flow
1. Search input (auto-focus)
2. Category sidebar (arrow keys)
3. Shortcut tables (Tab through rows)
4. Export button

### Focus Order
1. Search input
2. Category filters
3. Shortcut tables (row by row)
4. Export button

### Validation Rules
- Search: minimum 1 character
- No results: "No shortcuts match your search."

### Accessibility Notes
- Tables: proper `<table>` with `<th>` headers
- Shortcut keys: `<kbd>` elements with `aria-label`
- Category headings: `<h3>`

### Localization Notes
- Shortcut keys: universal (not translated)
- Action descriptions: translatable
- Category names: translatable

### Performance Expectations
- Render: < 100ms
- Search: < 50ms
- Export: < 1 second

---

*End of Screen Specifications*
