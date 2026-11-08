# AuthShield Lab — Information Architecture

## 1. Overview

This document defines the complete information architecture for AuthShield Lab,
an offline-first desktop cybersecurity education platform. The IA governs how
content is organized, related, owned, and accessed across all modules and roles.

---

## 2. Application Hierarchy

```
AuthShield Lab (Application Root)
├── Bootstrap Layer
│   ├── Splash Screen
│   ├── First-Launch Wizard
│   │   ├── License Agreement
│   │   ├── Privacy Notice
│   │   ├── Welcome Screen
│   │   └── Profile Setup
│   └── Authentication Gate
│       ├── Login Screen
│       └── Session Manager
├── Workspace Root
│   ├── Primary Navigation (Left Rail)
│   ├── Content Area (Right Pane)
│   ├── Notification Center
│   ├── Command Palette
│   └── Global Search
└── Modules
    ├── Dashboard
    ├── Courses
    ├── Learning
    ├── Simulations
    ├── Assessments
    ├── Reports
    ├── Certificates
    ├── Analytics
    ├── Settings
    ├── Plugins
    ├── Accessibility
    ├── Localization
    ├── Administration
    ├── Diagnostics
    └── Help
```

---

## 3. Module Organization

### 3.1 Dashboard

| Content Item | Type | Description |
|---|---|---|
| Overview Widget | Panel | Summary of key metrics and activity |
| Recent Activity Feed | List | Chronological list of user actions |
| Quick Actions | Grid | Shortcut tiles for common tasks |
| Upcoming Deadlines | List | Assignments and assessment due dates |
| Progress Summary | Chart | Visual learning progress |
| Notifications Preview | List | Latest unread notifications |
| System Status | Indicator | Online/offline, sync status |

**Owner:** System (auto-generated, user-configurable layout)

### 3.2 Courses

| Content Item | Type | Description |
|---|---|---|
| Course Browser | Catalog | Filterable, searchable course listing |
| Course Detail | Page | Full course information and curriculum |
| Course Enrollment | Dialog | Enrollment confirmation and prerequisites |
| Course Progress | Page | Per-module progress tracking |
| Course Materials | List | Downloadable resources and references |
| Prerequisite Checker | System | Validates enrollment eligibility |

**Owner:** Instructor (creates/edits), Student (enrolls/views), Admin (publishes/approves)

### 3.3 Learning

| Content Item | Type | Description |
|---|---|---|
| Learning Workspace | Workspace | Primary lesson interaction area |
| Lesson View | Page | Individual lesson content renderer |
| Content Viewer | Panel | Text, video, interactive content display |
| Notebook | Panel | User notes per lesson |
| Bookmarks | List | Saved positions within lessons |
| Glossary | Reference | Cybersecurity terminology lookup |
| Flashcards | Tool | Spaced repetition study cards |

**Owner:** Student (interacts), Instructor (creates content)

### 3.4 Simulations

| Content Item | Type | Description |
|---|---|---|
| Simulation Browser | Catalog | Available simulation scenarios |
| Simulation Detail | Page | Scenario briefing and configuration |
| Simulation Workspace | Workspace | Live simulation execution environment |
| Terminal Emulator | Panel | Interactive command-line simulation |
| Network Viewer | Panel | Topology and traffic visualization |
| Timeline | Panel | Event log during simulation |
| Debrief | Page | Post-simulation analysis and score |

**Owner:** System (runs), Instructor (configures scenarios), Student (executes)

### 3.5 Assessments

| Content Item | Type | Description |
|---|---|---|
| Assessment Browser | Catalog | Available assessments listing |
| Assessment Detail | Page | Assessment overview, rules, time limit |
| Assessment Workspace | Workspace | Active assessment-taking environment |
| Question Renderer | Panel | Multiple choice, drag-drop, code entry |
| Timer Widget | Widget | Countdown and time management |
| Submission Review | Page | Post-submission answer review |
| Results | Page | Score, breakdown, explanations |

**Owner:** Instructor (creates), Student (takes), System (auto-grades)

### 3.6 Reports

| Content Item | Type | Description |
|---|---|---|
| Reports Dashboard | Dashboard | Overview of available report types |
| Report Builder | Wizard | Configure and generate custom reports |
| Report Detail | Page | Rendered report with charts and tables |
| Export Panel | Dialog | PDF, CSV, JSON export options |
| Scheduled Reports | List | Recurring report configurations |
| Comparative Reports | Page | Side-by-side metric comparisons |

**Owner:** Instructor (course reports), Admin (system reports), Student (own reports)

### 3.7 Certificates

| Content Item | Type | Description |
|---|---|---|
| Certificate Gallery | Grid | All earned certificates |
| Certificate Detail | Page | Full certificate view with metadata |
| Certificate Preview | Panel | Print-ready preview |
| Verification | System | Certificate authenticity check |
| Share Dialog | Dialog | Export and sharing options |

**Owner:** System (issues), Student (views/downloads), Admin (manages templates)

### 3.8 Analytics

| Content Item | Type | Description |
|---|---|---|
| Analytics Dashboard | Dashboard | Key learning metrics overview |
| Student Analytics | Page | Individual student performance |
| Course Analytics | Page | Per-course engagement and completion |
| Assessment Analytics | Page | Question-level performance breakdown |
| Cohort Analytics | Page | Group comparisons and trends |
| Export Analytics | Dialog | Data export for external analysis |

**Owner:** Instructor (course analytics), Admin (institution analytics)

### 3.9 Settings

| Content Item | Type | Description |
|---|---|---|
| General Settings | Form | App name, startup, default view |
| Appearance Settings | Form | Theme, colors, density |
| Accessibility Settings | Form | Screen reader, keyboard, visual aids |
| Localization Settings | Form | Language, region, formats |
| Security Settings | Form | Password, session, 2FA |
| Privacy Settings | Form | Data collection, analytics |
| Notification Settings | Form | Category toggles, sound |
| Storage Settings | Form | Cache, data location |
| Backup Settings | Form | Schedule, encryption |
| Learning Settings | Form | Difficulty, progress, reminders |
| Diagnostics Settings | Form | Logging, crash reporting |
| Advanced Settings | Form | Developer mode, experimental |
| Administration Settings | Form | Users, roles, institution |

**Owner:** User (personal settings), Admin (system settings)

### 3.10 Plugins

| Content Item | Type | Description |
|---|---|---|
| Plugin Manager | Dashboard | Installed, available, and update status |
| Plugin Browser | Catalog | Searchable plugin marketplace |
| Plugin Detail | Page | Description, permissions, changelog |
| Plugin Configuration | Form | Per-plugin settings |
| Plugin Permissions | List | Requested and granted capabilities |
| Plugin Logs | Page | Runtime logs and errors |

**Owner:** Admin (installs/manages), Plugin Developer (creates)

### 3.11 Accessibility

| Content Item | Type | Description |
|---|---|---|
| Accessibility Center | Dashboard | Centralized a11y preferences |
| Screen Reader Settings | Form | SR verbosity, announcements |
| Keyboard Settings | Form | Shortcuts, key repeat, tab order |
| Visual Settings | Form | Contrast, motion, text scaling |
| Motor Settings | Form | Timeout, sticky keys, alternatives |
| Preview Panel | Panel | Real-time a11y preference preview |

**Owner:** User (personal preferences), System (enforces WCAG 2.2 AA baseline)

### 3.12 Localization

| Content Item | Type | Description |
|---|---|---|
| Language Selector | List | Available UI languages |
| Region Settings | Form | Date, number, currency formats |
| Timezone Selector | List | UTC offset selection |
| RTL Preview | Panel | Right-to-left layout preview |
| Translation Status | Page | Community translation progress |

**Owner:** User (personal locale), System (bundled translations)

### 3.13 Administration

| Content Item | Type | Description |
|---|---|---|
| User Management | Table | Create, edit, deactivate users |
| Role Management | List | Define and assign roles |
| Organization Management | Tree | Institution and department hierarchy |
| Audit Log | Table | System-wide activity audit |
| Bulk Operations | Wizard | Mass user/role operations |
| Institution Settings | Form | Org-wide configuration |
| Policy Engine | Form | Access and content policies |

**Owner:** Administrator, Institution Manager

### 3.14 Diagnostics

| Content Item | Type | Description |
|---|---|---|
| System Health | Dashboard | Component status overview |
| Log Viewer | Table | Filterable application logs |
| Performance Monitor | Chart | CPU, memory, disk usage |
| Network Status | Panel | Online/offline, sync queue |
| Crash Reporter | Dialog | Error reporting and details |
| Database Integrity | Tool | Verify and repair local DB |

**Owner:** Administrator, System Operator

### 3.15 Help

| Content Item | Type | Description |
|---|---|---|
| Help Center | Dashboard | Searchable documentation hub |
| Interactive Tutorials | List | Guided step-by-step walkthroughs |
| Documentation Browser | Tree | Categorized help articles |
| Keyboard Shortcuts | Table | Searchable shortcut reference |
| Troubleshooting | List | Common issues and solutions |
| FAQ | List | Frequently asked questions |
| About | Page | Version, credits, licenses |

**Owner:** System (bundled), Admin (custom documentation)

---

## 4. Relationships Between Content Items

| Source | Relationship | Target |
|---|---|---|
| Dashboard | links_to | All module dashboards |
| Course Browser | contains | Course Detail |
| Course Detail | requires | Prerequisite Checker |
| Course Detail | starts | Learning Workspace |
| Course Detail | references | Assessment Browser |
| Learning Workspace | renders | Lesson View |
| Lesson View | triggers | Assessment (quiz) |
| Simulation Browser | opens | Simulation Detail |
| Simulation Detail | launches | Simulation Workspace |
| Simulation Workspace | generates | Timeline |
| Simulation Workspace | produces | Debrief |
| Assessment Browser | opens | Assessment Detail |
| Assessment Detail | launches | Assessment Workspace |
| Assessment Workspace | produces | Submission Review |
| Submission Review | generates | Results |
| Results | qualifies | Certificate Gallery |
| Certificate Gallery | displays | Certificate Detail |
| Reports Dashboard | opens | Report Builder |
| Report Builder | generates | Report Detail |
| Analytics Dashboard | drills_down | Student/Course/Assessment Analytics |
| Settings | configures | All modules |
| Plugins | extends | Any module |
| Help | contextual_to | Current screen |

---

## 5. Ownership Matrix

| Module | Student | Instructor | Admin | Inst. Manager | Plugin Dev | Operator |
|---|---|---|---|---|---|---|
| Dashboard | Read | Read | Read | Read | Read | Read |
| Courses | Enroll/View | Create/Edit | Publish | Cross-view | — | — |
| Learning | Interact | Create | View | View | — | — |
| Simulations | Execute | Configure | Manage | View | Extend | — |
| Assessments | Take | Create/Grade | Manage | View | — | — |
| Reports | Own | Course | System | Institution | — | — |
| Certificates | View/Download | View | Manage | View | — | — |
| Analytics | Own | Course | System | Institution | — | — |
| Settings | Personal | Personal | System | Institution | SDK | System |
| Plugins | — | Request | Install/Manage | Approve | Create/Test | — |
| Accessibility | Personal | Personal | Global | Institution | — | — |
| Localization | Personal | Personal | Global | Institution | — | — |
| Administration | — | Limited | Full | Full | — | — |
| Diagnostics | — | — | Full | Limited | Limited | Full |
| Help | Read | Read/Customize | Read/Customize | Read | SDK Docs | Read |

---

## 6. Navigation Rules

### 6.1 Module Entry Points

| Module | Entry From |
|---|---|
| Dashboard | App launch (default), primary nav |
| Courses | Primary nav, dashboard quick actions |
| Learning | Course detail "Start" button, resume widget |
| Simulations | Primary nav, course-linked simulations |
| Assessments | Primary nav, course-linked assessments |
| Reports | Primary nav, analytics drill-down |
| Certificates | Primary nav, results page link |
| Analytics | Primary nav, reports cross-link |
| Settings | Primary nav gear icon, keyboard shortcut |
| Plugins | Settings > Plugins, admin nav |
| Accessibility | Settings > Accessibility, keyboard shortcut |
| Localization | Settings > Localization |
| Administration | Primary nav (admin only) |
| Diagnostics | Help > Diagnostics, admin nav |
| Help | Primary nav help icon, keyboard shortcut |

### 6.2 Cross-Module Navigation

- **Dashboard → Courses**: Click "Browse Courses" tile
- **Dashboard → Resume**: Click "Continue Learning" widget
- **Courses → Assessments**: Assessment tab within course detail
- **Learning → Assessment**: End-of-lesson quiz trigger
- **Simulation → Reports**: "Generate Report" in debrief
- **Assessment → Certificate**: Pass threshold triggers certificate
- **Reports → Analytics**: "View in Analytics" action
- **Settings → Accessibility**: Direct link in settings sidebar
- **Any Module → Help**: Context help button opens relevant docs
- **Any Module → Search**: Ctrl+K opens command palette

---

## 7. Visibility Rules (Role-Based)

| Screen | Student | Instructor | Admin | Inst. Manager | Plugin Dev | Operator |
|---|---|---|---|---|---|---|
| Course Browser | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Course Management | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ |
| Assessment Creation | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ |
| Student Analytics | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ |
| User Management | ✗ | Limited | ✓ | ✓ | ✗ | ✗ |
| Role Management | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ |
| System Settings | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ |
| Plugin Manager | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ |
| Plugin SDK | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ |
| Audit Logs | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ |
| Diagnostics | ✗ | ✗ | ✓ | Limited | ✓ | ✓ |
| Backup/Restore | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ |
| Institution Settings | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ |
| Cross-Course Analytics | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ |

---

## 8. Permission Rules

### 8.1 Permission Format

```
module.action.permission_level
```

### 8.2 Permission Levels

- `none` — No access, screen hidden
- `read` — View only, no modifications
- `write` — Create and edit own content
- `manage` — Edit any content, moderate
- `admin` — Full control including delete and configure
- `system` — System-level operations (backup, diagnostics)

### 8.3 Permission Matrix

```
dashboard.view.*              = read (all roles)
dashboard.configure.layout    = write (all authenticated)

courses.browse                = read (all)
courses.enroll                = write (student, instructor)
courses.create                = write (instructor, admin)
courses.edit                  = manage (owner), manage (instructor), admin (admin)
courses.publish               = admin (admin, inst_manager)
courses.delete                = admin (admin)

learning.view                 = read (enrolled students, instructor, admin)
learning.progress             = write (student)
learning.notes                = write (student)
learning.content.create       = write (instructor, admin)

simulations.browse            = read (all)
simulations.execute           = write (student)
simulations.configure         = manage (instructor, admin)
simulations.delete            = admin (admin)

assessments.browse            = read (enrolled)
assessments.take              = write (student)
assessments.create            = write (instructor, admin)
assessments.grade             = manage (instructor, admin)
assessments.delete            = admin (admin)

reports.view.own              = read (student)
reports.view.course           = manage (instructor)
reports.view.system           = admin (admin, inst_manager)
reports.generate              = write (instructor, admin)
reports.export                = write (instructor, admin)
reports.delete                = admin (admin)

certificates.view.own         = read (student)
certificates.view.all         = manage (instructor, admin)
certificates.manage           = admin (admin)
certificates.templates        = admin (admin)

analytics.view.own            = read (student)
analytics.view.course         = manage (instructor)
analytics.view.system         = admin (admin, inst_manager)
analytics.export              = write (instructor, admin)

settings.personal             = write (all authenticated)
settings.system               = admin (admin)
settings.security             = admin (admin)
settings.backup               = admin (admin, operator)
settings.diagnostics          = admin (admin, operator)

plugins.browse                = read (instructor, admin, dev)
plugins.install               = admin (admin)
plugins.configure             = manage (admin)
plugins.develop               = write (dev)
plugins.test                  = write (dev)

admin.users.list              = admin (admin, inst_manager)
admin.users.create            = admin (admin)
admin.users.edit              = admin (admin, inst_manager)
admin.users.deactivate        = admin (admin)
admin.roles                   = admin (admin)
admin.institution             = admin (admin, inst_manager)
admin.audit                   = read (admin, inst_manager)

diagnostics.view              = admin (admin, operator)
diagnostics.run               = admin (admin, operator)
diagnostics.export            = admin (admin, operator)

help.read                     = read (all)
help.customize                = manage (instructor, admin)
help.tutorials.create         = write (instructor, admin)
```

---

## 9. Information Architecture Diagram (ASCII Tree)

```
AuthShield Lab
│
├── 🚀 Bootstrap
│   ├── Splash Screen
│   ├── First-Launch Wizard
│   │   ├── License Agreement
│   │   ├── Privacy Notice
│   │   ├── Welcome
│   │   └── Profile Setup
│   └── Authentication
│       ├── Login
│       └── Session Restore
│
├── 📊 Dashboard
│   ├── Overview Widgets
│   ├── Recent Activity
│   ├── Quick Actions
│   ├── Upcoming Deadlines
│   ├── Progress Summary
│   └── System Status
│
├── 📚 Courses
│   ├── Course Browser
│   │   ├── Filter Panel
│   │   ├── Search Results
│   │   └── Category Navigation
│   ├── Course Detail
│   │   ├── Overview Tab
│   │   ├── Curriculum Tab
│   │   ├── Assessments Tab
│   │   ├── Materials Tab
│   │   └── Discussion Tab
│   ├── Enrollment Dialog
│   └── Course Progress
│
├── 📖 Learning
│   ├── Learning Workspace
│   │   ├── Lesson View
│   │   │   ├── Content Renderer
│   │   │   ├── Interactive Elements
│   │   │   └── Code Playground
│   │   ├── Notebook Panel
│   │   ├── Glossary Panel
│   │   └── Flashcard Panel
│   ├── Bookmark Manager
│   └── Progress Tracker
│
├── 🎯 Simulations
│   ├── Simulation Browser
│   ├── Simulation Detail
│   │   ├── Scenario Brief
│   │   ├── Configuration Panel
│   │   └── Prerequisites
│   ├── Simulation Workspace
│   │   ├── Terminal Emulator
│   │   ├── Network Viewer
│   │   ├── Timeline
│   │   └── Command Reference
│   └── Debrief
│       ├── Score Breakdown
│       ├── Mistakes Review
│       └── Improvement Tips
│
├── ✅ Assessments
│   ├── Assessment Browser
│   ├── Assessment Detail
│   │   ├── Overview
│   │   ├── Rules & Time Limit
│   │   └── Prerequisites
│   ├── Assessment Workspace
│   │   ├── Question Renderer
│   │   ├── Timer Widget
│   │   ├── Navigation Panel
│   │   └── Flag & Review
│   ├── Submission Review
│   └── Results
│       ├── Score Summary
│       ├── Question Breakdown
│       └── Explanations
│
├── 📈 Reports
│   ├── Reports Dashboard
│   ├── Report Builder (Wizard)
│   │   ├── Type Selection
│   │   ├── Data Configuration
│   │   ├── Filter Setup
│   │   └── Format Options
│   ├── Report Detail
│   │   ├── Charts
│   │   ├── Tables
│   │   └── Narratives
│   ├── Export Dialog
│   └── Scheduled Reports
│
├── 🏆 Certificates
│   ├── Certificate Gallery
│   ├── Certificate Detail
│   │   ├── Certificate View
│   │   ├── Metadata
│   │   └── Verification
│   ├── Print Preview
│   └── Share Dialog
│
├── 📊 Analytics
│   ├── Analytics Dashboard
│   ├── Student Analytics
│   ├── Course Analytics
│   ├── Assessment Analytics
│   ├── Cohort Analytics
│   └── Export Dialog
│
├── ⚙️ Settings
│   ├── General
│   ├── Appearance
│   ├── Accessibility
│   ├── Localization
│   ├── Security
│   ├── Privacy
│   ├── Notifications
│   ├── Storage
│   ├── Backup
│   ├── Learning
│   ├── Diagnostics
│   ├── Advanced
│   └── Administration (admin-only)
│
├── 🔌 Plugins
│   ├── Plugin Manager
│   │   ├── Installed Tab
│   │   ├── Available Tab
│   │   └── Updates Tab
│   ├── Plugin Browser
│   ├── Plugin Detail
│   │   ├── Overview
│   │   ├── Permissions
│   │   ├── Changelog
│   │   └── Reviews
│   ├── Plugin Configuration
│   └── Plugin Logs
│
├── ♿ Accessibility
│   ├── Accessibility Center
│   ├── Screen Reader Settings
│   ├── Keyboard Settings
│   ├── Visual Settings
│   ├── Motor Settings
│   └── Preview Panel
│
├── 🌐 Localization
│   ├── Language Selector
│   ├── Region Settings
│   ├── Timezone Selector
│   └── RTL Preview
│
├── 👥 Administration
│   ├── User Management
│   │   ├── User List
│   │   ├── User Detail
│   │   ├── User Create/Edit
│   │   └── Bulk Operations
│   ├── Role Management
│   │   ├── Role List
│   │   ├── Role Editor
│   │   └── Permission Matrix
│   ├── Organization Management
│   │   ├── Org Tree
│   │   ├── Department Editor
│   │   └── Cross-Org Settings
│   ├── Audit Log
│   └── Institution Settings
│
├── 🔧 Diagnostics
│   ├── System Health
│   ├── Log Viewer
│   ├── Performance Monitor
│   ├── Network Status
│   ├── Crash Reporter
│   └── Database Integrity
│
└── ❓ Help
    ├── Help Center
    ├── Interactive Tutorials
    ├── Documentation Browser
    ├── Keyboard Shortcuts Reference
    ├── Troubleshooting
    ├── FAQ
    └── About
```

---

## 10. Data Flow Summary

```
User Action → Permission Check → Navigation Guard → Screen Render
     ↓                                                      ↓
  Local Store ←←←←←←←←←←← State Update ←←←←←←←←←←← UI Update
     ↓
  IndexedDB (offline) ──── Sync Queue ──── (when online) ──→ Cloud
```

---

## 11. Cross-References

- See `SCREEN_HIERARCHY.md` for detailed screen specifications
- See `GLOBAL_NAVIGATION.md` for navigation mechanics
- See `PERMISSION_NAVIGATION.md` for role-based access details
- See `SETTINGS_ARCHITECTURE.md` for settings dependency graph
- See `NOTIFICATION_FRAMEWORK.md` for notification routing
