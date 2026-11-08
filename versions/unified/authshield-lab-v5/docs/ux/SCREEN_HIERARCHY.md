# AuthShield Lab — Screen Hierarchy & Master Screen Map

## 1. Overview

This document defines every screen in AuthShield Lab, including purpose, users,
entry points, exit points, and dependencies. It provides the complete screen
dependency graph for routing and navigation implementation.

---

## 2. Screen Specifications

### 2.1 Splash Screen

| Property | Value |
|---|---|
| **Purpose** | Display branding while application initializes |
| **Primary Users** | All users |
| **Entry Points** | Application launch |
| **Exit Points** | First-launch wizard (new), Authentication gate (returning), Dashboard (session cached) |
| **Dependencies** | Local database initialization, config load, session check |
| **Layout** | Centered logo, loading indicator, version text |
| **Keyboard** | None (non-interactive) |
| **Duration** | 1-3 seconds typical |

### 2.2 First-Launch Wizard — License Agreement

| Property | Value |
|---|---|
| **Purpose** | Present and accept End User License Agreement |
| **Primary Users** | First-time users |
| **Entry Points** | Splash screen (no license accepted) |
| **Exit Points** | Privacy Notice (accept), close app (decline) |
| **Dependencies** | None |
| **Layout** | Scrollable text area, Accept/Decline buttons |
| **Keyboard** | Tab between controls, Enter to activate, Space to scroll |
| **Accessibility** | Focus trapped in dialog, heading announced |

### 2.3 First-Launch Wizard — Privacy Notice

| Property | Value |
|---|---|
| **Purpose** | Inform user of data handling practices and obtain consent |
| **Primary Users** | First-time users |
| **Entry Points** | License Agreement (accepted) |
| **Exit Points** | Welcome Screen (accept), close app (decline) |
| **Dependencies** | License Agreement accepted |
| **Layout** | Scrollable privacy text, consent checkboxes, Continue button |
| **Keyboard** | Tab between controls, Enter to continue |
| **Accessibility** | Focus trapped, all checkboxes labeled |

### 2.4 First-Launch Wizard — Welcome Screen

| Property | Value |
|---|---|
| **Purpose** | Welcome user, explain platform capabilities |
| **Primary Users** | First-time users |
| **Entry Points** | Privacy Notice (accepted) |
| **Exit Points** | Profile Setup (continue), Dashboard (skip) |
| **Dependencies** | License and privacy accepted |
| **Layout** | Hero graphic, feature highlights, Continue/Skip buttons |
| **Keyboard** | Tab navigation, Enter to continue, Escape to skip |
| **Accessibility** | Landmark regions, skip link announced |

### 2.5 First-Launch Wizard — Profile Setup

| Property | Value |
|---|---|
| **Purpose** | Collect initial user profile information |
| **Primary Users** | First-time users |
| **Entry Points** | Welcome Screen, Settings > Profile |
| **Exit Points** | Dashboard (complete), Welcome Screen (back) |
| **Dependencies** | Welcome completed |
| **Layout** | Form fields: name, role selection, institution, timezone, avatar |
| **Keyboard** | Tab between fields, Enter to submit, Escape to skip |
| **Accessibility** | All fields labeled, error messages linked to fields |

### 2.6 Authentication — Login Screen

| Property | Value |
|---|---|
| **Purpose** | Authenticate user credentials |
| **Primary Users** | All returning users |
| **Entry Points** | Splash screen (no session), session expiry |
| **Exit Points** | Dashboard (success), first-launch (no account) |
| **Dependencies** | Local credential store or network auth |
| **Layout** | Username field, password field, remember checkbox, login button, offline indicator |
| **Keyboard** | Tab between fields, Enter to submit |
| **Accessibility** | Error messages announced, field labels visible |
| **Note** | Supports offline mode with cached credentials |

### 2.7 Dashboard — Student View

| Property | Value |
|---|---|
| **Purpose** | Overview of learning progress and activities |
| **Primary Users** | Student |
| **Entry Points** | Login, navigation, app launch |
| **Exit Points** | All modules via quick actions, widget clicks |
| **Dependencies** | User profile, enrolled courses, progress data |
| **Layout** | Widget grid: progress summary, upcoming deadlines, recent activity, quick actions, notifications |
| **Keyboard** | Tab through widgets, Enter to activate, Arrow keys within widgets |
| **Accessibility** | Landmark regions per widget, headings hierarchy |

### 2.8 Dashboard — Instructor View

| Property | Value |
|---|---|
| **Purpose** | Overview of teaching activities and student management |
| **Primary Users** | Instructor |
| **Entry Points** | Login, navigation, app launch |
| **Exit Points** | Course management, analytics, reports, student lists |
| **Dependencies** | Managed courses, student enrollment data |
| **Layout** | Widget grid: course summaries, pending reviews, student activity alerts, creation shortcuts |
| **Keyboard** | Tab through widgets, Enter to activate |
| **Accessibility** | Same as Student Dashboard |

### 2.9 Dashboard — Administrator View

| Property | Value |
|---|---|
| **Purpose** | System health overview and administrative actions |
| **Primary Users** | Administrator, Institution Manager |
| **Entry Points** | Login, navigation, app launch |
| **Exit Points** | Admin modules, diagnostics, user management |
| **Dependencies** | System metrics, user counts, audit data |
| **Layout** | Widget grid: system health, user stats, recent audit entries, plugin status, storage usage |
| **Keyboard** | Tab through widgets, Enter to activate |
| **Accessibility** | Same as Student Dashboard |

### 2.10 Course Browser

| Property | Value |
|---|---|
| **Purpose** | Browse, search, and filter available courses |
| **Primary Users** | Student, Instructor, Admin |
| **Entry Points** | Dashboard, primary nav "Courses" |
| **Exit Points** | Course Detail (select), Dashboard (back) |
| **Dependencies** | Course catalog data |
| **Layout** | Search bar, filter sidebar, course card grid, sort controls, pagination |
| **Keyboard** | / to focus search, Arrow keys through grid, Enter to open, Tab to filters |
| **Accessibility** | Results count announced, filters labeled, grid navigation |

### 2.11 Course Detail

| Property | Value |
|---|---|
| **Purpose** | Display full course information and actions |
| **Primary Users** | Student, Instructor, Admin |
| **Entry Points** | Course Browser, search results, dashboard links |
| **Exit Points** | Learning Workspace (start/resume), Course Browser (back), Enrollment Dialog |
| **Dependencies** | Course data, enrollment status, prerequisites |
| **Layout** | Header with title/metadata, tab bar (Overview/Curriculum/Assessments/Materials), action buttons |
| **Keyboard** | Tab through tabs and content, Enter to activate |
| **Accessibility** | Tabs keyboard accessible, content updates announced |

### 2.12 Learning Workspace

| Property | Value |
|---|---|
| **Purpose** | Primary lesson interaction and learning environment |
| **Primary Users** | Student |
| **Entry Points** | Course Detail (Start/Resume), Dashboard (Continue), bookmarks |
| **Exit Points** | Lesson View (within), Course Detail (back), Dashboard (home) |
| **Dependencies** | Course content, user progress, notes |
| **Layout** | Sidebar (lesson tree), main content area, toolbar (bookmarks, notes, glossary) |
| **Keyboard** | Arrow keys for lesson tree, Tab for content, shortcuts for panels |
| **Accessibility** | Tree navigation, content landmarks, panel focus management |

### 2.13 Lesson View

| Property | Value |
|---|---|
| **Purpose** | Render individual lesson content |
| **Primary Users** | Student |
| **Entry Points** | Learning Workspace (lesson selection) |
| **Exit Points** | Next/Previous lesson, Assessment (end-of-lesson quiz), Learning Workspace |
| **Dependencies** | Lesson content (text, video, interactive) |
| **Layout** | Content area (scrollable), progress indicator, navigation footer, side panels |
| **Keyboard** | Space to scroll, Page Up/Down, Alt+N/P for next/previous |
| **Accessibility** | Semantic HTML content, video captions, interactive element labels |

### 2.14 Simulation Browser

| Property | Value |
|---|---|
| **Purpose** | Browse available simulation scenarios |
| **Primary Users** | Student, Instructor |
| **Entry Points** | Primary nav "Simulations", Dashboard quick action |
| **Exit Points** | Simulation Detail (select), Dashboard (back) |
| **Dependencies** | Simulation catalog data |
| **Layout** | Filter sidebar, scenario card grid with difficulty badges |
| **Keyboard** | Arrow keys through grid, Enter to open, Tab to filters |
| **Accessibility** | Difficulty indicated textually, not color-only |

### 2.15 Simulation Detail

| Property | Value |
|---|---|
| **Purpose** | Display scenario briefing and configuration |
| **Primary Users** | Student, Instructor |
| **Entry Points** | Simulation Browser, search results |
| **Exit Points** | Simulation Workspace (start), Simulation Browser (back) |
| **Dependencies** | Scenario data, prerequisites, user history |
| **Layout** | Briefing text, objectives list, configuration panel, start button |
| **Keyboard** | Tab through controls, Enter to start |
| **Accessibility** | Objectives as list, configuration fields labeled |

### 2.16 Simulation Workspace

| Property | Value |
|---|---|
| **Purpose** | Live simulation execution environment |
| **Primary Users** | Student |
| **Entry Points** | Simulation Detail (Start), Assessment-linked simulation |
| **Exit Points** | Debrief (complete/abort), Simulation Detail (back), Dashboard (home) |
| **Dependencies** | Simulation engine, terminal emulator, network viewer |
| **Layout** | Split view: terminal + network viewer, toolbar, timeline panel, command reference |
| **Keyboard** | Full terminal keyboard access, Tab between panels, shortcuts for tools |
| **Accessibility** | Terminal output as live region, panel labels, keyboard-only operation |

### 2.17 Debrief Screen

| Property | Value |
|---|---|
| **Purpose** | Post-simulation analysis and scoring |
| **Primary Users** | Student, Instructor (reviewing student work) |
| **Entry Points** | Simulation Workspace (complete/abort) |
| **Exit Points** | Simulation Browser (new), Learning Workspace (course-linked), Dashboard (home) |
| **Dependencies** | Simulation results, scoring data |
| **Layout** | Score summary, objectives checklist, mistakes list, improvement tips, replay option |
| **Keyboard** | Tab through sections, Enter to replay or navigate |
| **Accessibility** | Score announced, sections headed, list semantics |

### 2.18 Assessment Browser

| Property | Value |
|---|---|
| **Purpose** | Browse available assessments |
| **Primary Users** | Student, Instructor |
| **Entry Points** | Primary nav "Assessments", Course Detail (Assessments tab) |
| **Exit Points** | Assessment Detail (select), Dashboard (back) |
| **Dependencies** | Assessment catalog, enrollment data |
| **Layout** | Filter sidebar, assessment card grid with status badges |
| **Keyboard** | Arrow keys through grid, Enter to open |
| **Accessibility** | Status badges have text alternatives |

### 2.19 Assessment Detail

| Property | Value |
|---|---|
| **Purpose** | Assessment overview, rules, and start |
| **Primary Users** | Student, Instructor |
| **Entry Points** | Assessment Browser, Course Detail |
| **Exit Points** | Assessment Workspace (start), Assessment Browser (back) |
| **Dependencies** | Assessment data, attempt history |
| **Layout** | Title, description, rules, time limit, attempt info, start button |
| **Keyboard** | Tab through info, Enter to start |
| **Accessibility** | Rules as structured list, time limit announced |

### 2.20 Assessment Workspace

| Property | Value |
|---|---|
| **Purpose** | Active assessment-taking environment |
| **Primary Users** | Student |
| **Entry Points** | Assessment Detail (Start) |
| **Exit Points** | Results (submit), Assessment Detail (abort), Dashboard (abort with confirmation) |
| **Dependencies** | Question data, timer, auto-save |
| **Layout** | Question navigator sidebar, question area, timer, flag button, submit button |
| **Keyboard** | Number keys for question jump, Tab through answers, Enter to submit |
| **Accessibility** | Question count announced, timer as aria-live, focus management on question change |

### 2.21 Results Screen

| Property | Value |
|---|---|
| **Purpose** | Display assessment results and explanations |
| **Primary Users** | Student, Instructor (reviewing) |
| **Entry Points** | Assessment Workspace (submit), Assessment Browser (view past) |
| **Exit Points** | Assessment Browser (new), Learning Workspace (course-linked), Certificate Gallery (if passed) |
| **Dependencies** | Submission data, grading results |
| **Layout** | Score display, question-by-question breakdown, explanations, retry button |
| **Keyboard** | Tab through questions, Enter to expand explanations |
| **Accessibility** | Score announced first, correct/incorrect indicated by text not color alone |

### 2.22 Reports Dashboard

| Property | Value |
|---|---|
| **Purpose** | Overview of report types and recent reports |
| **Primary Users** | Instructor, Admin, Student (own) |
| **Entry Points** | Primary nav "Reports", Analytics drill-down |
| **Exit Points** | Report Builder, Report Detail, Export Dialog |
| **Dependencies** | Report templates, generated reports |
| **Layout** | Report type cards, recent reports list, schedule overview |
| **Keyboard** | Tab through cards and list, Enter to open |
| **Accessibility** | Report types described, recent reports as list |

### 2.23 Report Builder (Wizard)

| Property | Value |
|---|---|
| **Purpose** | Configure and generate custom reports |
| **Primary Users** | Instructor, Admin |
| **Entry Points** | Reports Dashboard (Create), analytics export |
| **Exit Points** | Report Detail (generate), Reports Dashboard (cancel) |
| **Dependencies** | Data sources, report templates |
| **Layout** | Step indicator, form per step, next/back/finish buttons |
| **Keyboard** | Tab through form, Enter for next, Escape to cancel |
| **Accessibility** | Step indicator announced, validation errors linked |

### 2.24 Report Detail

| Property | Value |
|---|---|
| **Purpose** | Display rendered report |
| **Primary Users** | Instructor, Admin, Student |
| **Entry Points** | Report Builder, Reports Dashboard, search results |
| **Exit Points** | Reports Dashboard (back), Export Dialog (export) |
| **Dependencies** | Report data, charts, tables |
| **Layout** | Report header, charts area, data tables, narrative sections, export button |
| **Keyboard** | Tab through sections, Arrow keys in charts/tables |
| **Accessibility** | Charts have text alternatives, tables properly headed |

### 2.25 Certificate Gallery

| Property | Value |
|---|---|
| **Purpose** | Display all earned certificates |
| **Primary Users** | Student, Instructor (viewing), Admin |
| **Entry Points** | Primary nav "Certificates", Results (if passed), Dashboard |
| **Exit Points** | Certificate Detail (select), Dashboard (back) |
| **Dependencies** | User certificates data |
| **Layout** | Grid of certificate thumbnails with earned date |
| **Keyboard** | Arrow keys through grid, Enter to open |
| **Accessibility** | Certificate names and dates announced |

### 2.26 Certificate Detail

| Property | Value |
|---|---|
| **Purpose** | Full certificate view with print and share options |
| **Primary Users** | Student, Admin |
| **Entry Points** | Certificate Gallery, Results (link) |
| **Exit Points** | Certificate Gallery (back), Print, Download, Share |
| **Dependencies** | Certificate data, verification code |
| **Layout** | Certificate preview, metadata, verification code, action buttons |
| **Keyboard** | Tab through actions, Enter to activate |
| **Accessibility** | Certificate details as structured content |

### 2.27 Analytics Dashboard

| Property | Value |
|---|---|
| **Purpose** | Key learning metrics overview with drill-down |
| **Primary Users** | Instructor, Admin, Student (own) |
| **Entry Points** | Primary nav "Analytics", Dashboard widget |
| **Exit Points** | Student Analytics, Course Analytics, Assessment Analytics, Cohort Analytics |
| **Dependencies** | Aggregated metrics data |
| **Layout** | KPI cards, trend charts, drill-down links |
| **Keyboard** | Tab through KPIs and charts, Enter to drill down |
| **Accessibility** | KPIs as text, charts with data tables alternative |

### 2.28 Settings Screen

| Property | Value |
|---|---|
| **Purpose** | Application configuration |
| **Primary Users** | All authenticated users |
| **Entry Points** | Primary nav gear icon, keyboard shortcut (Ctrl+,) |
| **Exit Points** | Previous screen (back), any module affected by settings |
| **Dependencies** | User preferences, system config |
| **Layout** | Settings sidebar (categories), settings content area, save/reset buttons |
| **Keyboard** | Tab through sidebar, Enter to select category, Tab through settings |
| **Accessibility** | Categories as navigation, settings grouped with headings, live preview |
| **Sub-screens** | General, Appearance, Accessibility, Localization, Security, Privacy, Notifications, Storage, Backup, Learning, Diagnostics, Advanced, Administration |

### 2.29 Plugin Manager

| Property | Value |
|---|---|
| **Purpose** | Manage installed plugins and browse available ones |
| **Primary Users** | Admin, Plugin Developer |
| **Entry Points** | Settings > Plugins, Admin nav |
| **Exit Points** | Plugin Detail, Plugin Configuration, Plugin Logs |
| **Dependencies** | Plugin registry, installed plugins, update feed |
| **Layout** | Tabs (Installed/Available/Updates), plugin list, search, install/update buttons |
| **Keyboard** | Tab through tabs and list, Enter to open, keyboard shortcuts for install |
| **Accessibility** | Plugin status announced, action buttons labeled |

### 2.30 Plugin Detail

| Property | Value |
|---|---|
| **Purpose** | Display plugin information and actions |
| **Primary Users** | Admin, Plugin Developer |
| **Entry Points** | Plugin Manager, search results |
| **Exit Points** | Plugin Manager (back), Plugin Configuration, Plugin Logs |
| **Dependencies** | Plugin metadata, permissions, changelog |
| **Layout** | Overview, permissions list, changelog, reviews, install/configure button |
| **Keyboard** | Tab through sections, Enter to install/configure |
| **Accessibility** | Permissions as structured list, status announced |

### 2.31 Accessibility Center

| Property | Value |
|---|---|
| **Purpose** | Centralized accessibility preferences |
| **Primary Users** | All users |
| **Entry Points** | Settings > Accessibility, keyboard shortcut (Alt+A) |
| **Exit Points** | Settings (back), affected screens (live preview) |
| **Dependencies** | User a11y preferences |
| **Layout** | Category tabs (Screen Reader/Keyboard/Visual/Motor), settings, preview panel |
| **Keyboard** | Tab through tabs and settings, preview keyboard accessible |
| **Accessibility** | Self-referential: must be fully accessible, live preview announced |

### 2.32 Localization Settings

| Property | Value |
|---|---|
| **Purpose** | Language and region configuration |
| **Primary Users** | All users |
| **Entry Points** | Settings > Localization |
| **Exit Points** | Settings (back), affected screens (language update) |
| **Dependencies** | Available translations, timezone data |
| **Layout** | Language list, region dropdown, format previews, timezone selector |
| **Keyboard** | Arrow keys through languages, Enter to select |
| **Accessibility** | Language names in native script, current selection announced |

### 2.33 Administration — User Management

| Property | Value |
|---|---|
| **Purpose** | Create, edit, and manage user accounts |
| **Primary Users** | Administrator, Institution Manager |
| **Entry Points** | Primary nav "Admin", Admin dashboard widget |
| **Exit Points** | User Detail, User Create/Edit dialog, bulk operations wizard |
| **Dependencies** | User database, role assignments |
| **Layout** | User table with search/filter, action buttons, bulk select checkboxes |
| **Keyboard** | Arrow keys through table, Enter to open, Space to select, Delete to deactivate |
| **Accessibility** | Table headers, row counts, selection state announced |

### 2.34 Administration — Role Management

| Property | Value |
|---|---|
| **Purpose** | Define and assign user roles |
| **Primary Users** | Administrator |
| **Entry Points** | Admin nav, User Management (link) |
| **Exit Points** | Role Editor, Permission Matrix |
| **Dependencies** | Role definitions, permission registry |
| **Layout** | Role list, role detail, permission matrix grid |
| **Keyboard** | Arrow keys through matrix, Enter to toggle |
| **Accessibility** | Matrix cells have role and permission labels |

### 2.35 Diagnostics — System Health

| Property | Value |
|---|---|
| **Purpose** | Display system component status |
| **Primary Users** | Administrator, System Operator |
| **Entry Points** | Help > Diagnostics, Admin nav, dashboard widget |
| **Exit Points** | Log Viewer, Performance Monitor, Crash Reporter |
| **Dependencies** | System health checks |
| **Layout** | Status cards per component, overall health indicator, action buttons |
| **Keyboard** | Tab through cards, Enter to drill down |
| **Accessibility** | Status indicated by text and icon, not color alone |

### 2.36 Help Center

| Property | Value |
|---|---|
| **Purpose** | Searchable documentation and tutorials |
| **Primary Users** | All users |
| **Entry Points** | Primary nav help icon, keyboard shortcut (F1), context help buttons |
| **Exit Points** | Documentation pages, tutorials, keyboard shortcuts reference |
| **Dependencies** | Bundled documentation, search index |
| **Layout** | Search bar, category grid, popular articles, recent views |
| **Keyboard** | Tab through categories, / to focus search, Enter to open |
| **Accessibility** | Search results announced, article headings structured |

### 2.37 About Screen

| Property | Value |
|---|---|
| **Purpose** | Display version, credits, and license information |
| **Primary Users** | All users |
| **Entry Points** | Help > About, Settings > General (version link) |
| **Exit Points** | Help Center (back) |
| **Dependencies** | App version, credits data, third-party licenses |
| **Layout** | App logo, version, credits list, license text, open-source attributions |
| **Keyboard** | Tab through links, Enter to activate |
| **Accessibility** | Version announced, links labeled |

### 2.38 Keyboard Shortcuts Reference

| Property | Value |
|---|---|
| **Purpose** | Searchable keyboard shortcut reference |
| **Primary Users** | All users |
| **Entry Points** | Help > Shortcuts, keyboard shortcut (Ctrl+/) |
| **Exit Points** | Help Center (back) |
| **Dependencies** | Shortcut registry |
| **Layout** | Search/filter bar, shortcut categories, shortcut table |
| **Keyboard** | / to focus search, Arrow keys through table |
| **Accessibility** | Shortcuts as text, categories headed |

### 2.39 Backup & Restore

| Property | Value |
|---|---|
| **Purpose** | Create and restore data backups |
| **Primary Users** | Administrator, System Operator |
| **Entry Points** | Settings > Backup |
| **Exit Points** | Settings (back), Diagnostics (backup status) |
| **Dependencies** | Backup engine, file system access |
| **Layout** | Backup creation form, restore selection, backup history, storage info |
| **Keyboard** | Tab through form, Enter to create/restore |
| **Accessibility** | Backup progress announced, confirmation dialogs labeled |

### 2.40 Command Palette

| Property | Value |
|---|---|
| **Purpose** | Quick access to all actions and screens |
| **Primary Users** | All users |
| **Entry Points** | Ctrl+K, / key (when not in input) |
| **Exit Points** | Any screen or action, Escape to close |
| **Dependencies** | Action registry, screen registry |
| **Layout** | Modal overlay, search input, results list with icons |
| **Keyboard** | Type to filter, Arrow keys to navigate, Enter to execute, Escape to close |
| **Accessibility** | Modal focus trap, results count, selected result announced |

---

## 3. Screen Dependency Graph

```
Splash Screen
  ├──→ First-Launch Wizard
  │     ├──→ License Agreement
  │     │     └──→ Privacy Notice
  │     │           └──→ Welcome Screen
  │     │                 └──→ Profile Setup
  │     │                       └──→ Dashboard
  │     └──→ Dashboard (skip)
  └──→ Login Screen
        └──→ Dashboard

Dashboard (Student) ──→ Courses, Simulations, Assessments, Reports, Certificates, Settings, Help
Dashboard (Instructor) ──→ All Student + Course Mgmt, Analytics, Administration
Dashboard (Admin) ──→ All Instructor + User Mgmt, Plugin Mgmt, Diagnostics

Courses ──→ Course Browser ──→ Course Detail
  Course Detail ──→ Learning Workspace ──→ Lesson View
  Course Detail ──→ Assessment Browser ──→ Assessment Detail
  Course Detail ──→ Enrollment Dialog

Simulations ──→ Simulation Browser ──→ Simulation Detail ──→ Simulation Workspace ──→ Debrief

Assessments ──→ Assessment Browser ──→ Assessment Detail ──→ Assessment Workspace ──→ Results
  Results ──→ Certificate Gallery (if passed)

Reports ──→ Reports Dashboard ──→ Report Builder ──→ Report Detail
  Report Detail ──→ Export Dialog

Certificates ──→ Certificate Gallery ──→ Certificate Detail

Analytics ──→ Analytics Dashboard ──→ Student/Course/Assessment/Cohort Analytics

Settings ──→ [All Settings Categories]
  Settings ──→ Accessibility Center
  Settings ──→ Localization Settings
  Settings ──→ Backup & Restore

Plugins ──→ Plugin Manager ──→ Plugin Detail ──→ Plugin Configuration
  Plugin Manager ──→ Plugin Logs

Administration ──→ User Management ──→ User Detail
  Administration ──→ Role Management ──→ Permission Matrix
  Administration ──→ Organization Management
  Administration ──→ Audit Log
  Administration ──→ Institution Settings

Diagnostics ──→ System Health ──→ Log Viewer
  Diagnostics ──→ Performance Monitor
  Diagnostics ──→ Crash Reporter

Help ──→ Help Center ──→ Documentation Pages
  Help ──→ Interactive Tutorials
  Help ──→ Keyboard Shortcuts Reference
  Help ──→ About

Command Palette ──→ Any Screen
Global Search ──→ Any Screen
```

---

## 4. Screen Count Summary

| Category | Count |
|---|---|
| Bootstrap screens | 5 |
| Authentication screens | 1 |
| Dashboard variants | 3 |
| Course-related screens | 3 |
| Learning screens | 2 |
| Simulation screens | 4 |
| Assessment screens | 4 |
| Report screens | 3 |
| Certificate screens | 2 |
| Analytics screens | 2 |
| Settings screens | 14 |
| Plugin screens | 3 |
| Administration screens | 4 |
| Diagnostics screens | 1 |
| Help screens | 4 |
| Overlay screens | 1 |
| **Total unique screens** | **56** |
