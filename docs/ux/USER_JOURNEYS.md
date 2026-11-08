# AuthShield Lab — User Journey Mapping

## 1. Overview

This document defines complete user journeys for AuthShield Lab. Each journey
includes goals, numbered steps, decision points, alternative paths, error
recovery, and accessibility considerations. Journeys cover the full lifecycle
from first launch through daily use and advanced operations.

---

## 2. Journey: First Launch

### 2.1 Goals
- Accept license and privacy agreements
- Create initial profile
- Reach the dashboard ready to learn

### 2.2 Steps

1. User double-clicks application icon
2. Splash screen displays (1-3 seconds) with loading indicator
3. System detects no existing license acceptance
4. License Agreement screen appears
5. User scrolls through license text
6. User clicks "Accept" (or "Decline" to exit)
7. Privacy Notice screen appears
8. User reads privacy policy
9. User checks required consent checkboxes
10. User clicks "Continue"
11. Welcome screen appears with feature overview
12. User reads feature highlights
13. User clicks "Get Started" (or "Skip" to skip setup)
14. Profile Setup screen appears
15. User enters display name (required)
16. User selects role: Student, Instructor, or Administrator
17. User enters institution name (optional)
18. User selects timezone from dropdown
19. User optionally uploads avatar
20. User clicks "Complete Setup"
21. System creates local profile and initializes database
22. Dashboard loads with role-appropriate layout

### 2.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 6 | License acceptance | Accept / Decline |
| 9 | Privacy consent | Required checkboxes |
| 13 | Profile setup | Complete / Skip |
| 16 | Role selection | Student / Instructor / Admin |

### 2.4 Alternative Paths

- **Decline License**: Application closes gracefully with message
- **Skip Welcome**: Jumps directly to profile setup
- **Skip Profile**: Creates default profile, user can configure later in Settings
- **Offline Mode**: All steps work offline; no network required

### 2.5 Error Scenarios

| Error | Recovery |
|---|---|
| Database initialization fails | Retry button, then offer to reset data |
| Avatar upload fails | Skip avatar, continue setup |
| Profile save fails | Show error, allow retry |

### 2.6 Accessibility Considerations

- All screens keyboard navigable
- License text scrollable with keyboard
- Form fields have visible labels
- Error messages announced via aria-live
- Focus moves to new screen heading on transition
- Tab order follows logical reading order
- High contrast mode available throughout

---

## 3. Journey: First-Time User Onboarding

### 3.1 Goals
- Learn basic navigation
- Understand core features
- Complete first lesson

### 3.2 Steps

1. User arrives at Dashboard after first launch
2. Onboarding overlay appears highlighting primary navigation
3. Tooltip: "This is your navigation rail. Use Alt+1 to jump to Dashboard."
4. User presses Alt+2 or clicks "Courses"
5. Onboarding highlights course browser
6. Tooltip: "Browse courses here. Use / to search."
7. User searches for a beginner course
8. Onboarding highlights filter sidebar
9. User selects "Cybersecurity Fundamentals" course
10. Course Detail screen appears
11. Onboarding highlights "Enroll" button
12. User clicks "Enroll"
13. Confirmation dialog appears
14. User confirms enrollment
15. Onboarding highlights "Start Course" button
16. User clicks "Start Course"
17. Learning Workspace opens with Lesson 1
18. Onboarding highlights lesson content area
19. Tooltip: "Read through the content, then click Next to continue."
20. User completes Lesson 1
21. Onboarding highlights progress indicator
22. User proceeds to Lesson 2

### 3.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 6 | Search or browse | Search / Browse / Skip |
| 12 | Enrollment | Enroll / Cancel |
| 17 | Start now or later | Start / Dashboard |

### 3.4 Alternative Paths

- **Skip Onboarding**: Click "Skip Tour" at any time
- **Previous Experience**: Onboarding detects prior activity and adjusts
- **No Courses Found**: Suggest adjusting filters or browse categories

### 3.5 Error Scenarios

| Error | Recovery |
|---|---|
| Course unavailable offline | Show offline indicator, offer download |
| Enrollment limit reached | Show message, suggest alternatives |
| Lesson content fails to load | Retry button, report issue option |

### 3.6 Accessibility Considerations

- Onboarding overlays are focus-trapped
- Each step announced via aria-live
- Skip tour available via keyboard (Escape)
- Tooltips positioned to not obscure content
- High contrast borders on highlighted elements
- Screen reader receives step-by-step guidance

---

## 4. Journey: Returning User

### 4.1 Goals
- Resume where left off
- Check notifications
- Continue learning progress

### 4.2 Steps

1. User launches application
2. Splash screen displays
3. System detects existing session (within timeout)
4. Dashboard loads directly (skipping login)
5. "Resume Last Activity" widget shows recent lesson
6. User clicks "Continue" on resume widget
7. Learning Workspace opens at saved position
8. User completes lesson
9. User navigates to Dashboard
10. User checks notification center
11. User sees assessment due in 2 days
12. User clicks notification to view assessment

### 4.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 4 | Session valid? | Auto-login / Login screen |
| 5 | Resume or new activity | Continue / Dashboard |
| 11 | Act on notification | View / Dismiss / Snooze |

### 4.4 Alternative Paths

- **Session Expired**: Redirect to login screen
- **Multiple Activities**: Show list of recent activities to choose from
- **No Recent Activity**: Show getting started suggestions

### 4.5 Error Scenarios

| Error | Recovery |
|---|---|
| Session validation fails | Redirect to login |
| Saved progress corrupted | Show warning, offer to reload from last backup |

### 4.6 Accessibility Considerations

- Resume widget announced with progress percentage
- Notification center keyboard accessible
- Focus restored to previous position when possible

---

## 5. Journey: Authentication

### 5.1 Goals
- Authenticate and access the platform
- Support offline authentication

### 5.2 Steps

1. User reaches login screen
2. User enters username in first field
3. User presses Tab to password field
4. User enters password
5. User checks "Remember me" (optional)
6. User clicks "Sign In" or presses Enter
7. System validates credentials (locally or via network)
8. Authentication succeeds
9. Dashboard loads with role-appropriate view

### 5.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 5 | Remember session | Yes / No |
| 7 | Auth method | Local / Network |

### 5.4 Alternative Paths

- **Offline Auth**: Cached credentials validate locally
- **2FA Required**: TOTP code entry screen appears
- **Password Expired**: Force password change flow
- **First Login**: Redirect to profile setup

### 5.5 Error Scenarios

| Error | Recovery |
|---|---|
| Invalid credentials | Show error below password field, clear password |
| Account locked | Show lock message with unlock instructions |
| Network timeout (online mode) | Offer offline mode or retry |
| 2FA code invalid | Clear code, show retry message |

### 5.6 Accessibility Considerations

- Login form properly labeled
- Error messages associated with fields via aria-describedby
- Password visibility toggle keyboard accessible
- Focus returns to username field on failed login
- Screen reader announces authentication status

---

## 6. Journey: Course Enrollment

### 6.1 Goals
- Find a suitable course
- Enroll and begin learning

### 6.2 Steps

1. User navigates to Course Browser (Alt+2)
2. User types search query in search bar
3. Results filter in real-time
4. User applies "Beginner" difficulty filter
5. User applies "Network Security" category filter
6. User reviews filtered results
7. User clicks on "Network Security Fundamentals" card
8. Course Detail screen opens
9. User reviews Overview tab
10. User switches to Curriculum tab
11. User reviews module and lesson list
12. User checks Assessments tab
13. User reviews prerequisites
14. User clicks "Enroll in Course"
15. Enrollment confirmation dialog appears
16. User confirms enrollment
17. System adds course to enrolled list
18. "Start Course" button appears
19. User clicks "Start Course"
20. Learning Workspace opens at Lesson 1

### 6.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 14 | Enroll | Yes / Cancel |
| 19 | Start now | Start / Later |

### 6.4 Alternative Paths

- **Prerequisites Not Met**: Show requirement list, prevent enrollment
- **Already Enrolled**: Show "Resume" instead of "Enroll"
- **Course Full**: Show waitlist option (if applicable)
- **Offline**: Enrollment queued for sync

### 6.5 Error Scenarios

| Error | Recovery |
|---|---|
| Enrollment fails offline | Queue enrollment, show pending indicator |
| Course data corrupted | Reload from cache, offer re-download |

### 6.6 Accessibility Considerations

- Filter changes announced via aria-live
- Course cards keyboard navigable
- Enrollment dialog focus trapped
- Confirmation announced after enrollment

---

## 7. Journey: Lesson Completion

### 7.1 Goals
- Complete a lesson
- Track progress

### 7.2 Steps

1. User opens Learning Workspace from course
2. Lesson tree shows current position
3. User reads lesson content
4. User interacts with embedded exercise
5. User opens notebook panel (optional)
6. User takes notes
7. User closes notebook
8. User clicks "Complete & Continue"
9. End-of-lesson quiz appears (if configured)
10. User answers quiz questions
11. User submits quiz
12. Quiz results displayed
13. User clicks "Continue to Next Lesson"
14. Next lesson loads
15. Progress indicator updates
16. Dashboard progress widget reflects completion

### 7.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 5 | Open notebook | Yes / No |
| 8 | Complete | Complete / Save Draft |
| 13 | Continue | Next / Review / Dashboard |

### 7.4 Alternative Paths

- **No Quiz**: Skip to next lesson directly
- **Quiz Failed**: Show explanations, retry option
- **Last Lesson**: Show course completion screen

### 7.5 Error Scenarios

| Error | Recovery |
|---|---|
| Progress not saving | Auto-save retry, manual save option |
| Quiz submission fails | Retry, offline queue |

### 7.6 Accessibility Considerations

- Progress announced on completion
- Quiz questions keyboard navigable
- Timer (if present) announced periodically
- Focus management on lesson transition

---

## 8. Journey: Simulation Execution

### 8.1 Goals
- Run a cybersecurity simulation
- Analyze performance

### 8.2 Steps

1. User navigates to Simulations (Alt+3)
2. User browses scenarios by difficulty
3. User selects "Phishing Email Analysis" (Intermediate)
4. Simulation Detail shows scenario briefing
5. User reads objectives and constraints
6. User configures simulation parameters (optional)
7. User clicks "Start Simulation"
8. Simulation Workspace loads
9. Terminal emulator becomes active
10. User types commands to investigate
11. Network viewer shows traffic patterns
12. Timeline logs user actions
13. User identifies phishing indicators
14. User completes objectives
15. Simulation auto-completes or user clicks "Finish"
16. Debrief screen appears
17. User reviews score and mistakes
18. User reads improvement tips
19. User downloads report or returns to browser

### 8.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 6 | Configure | Yes / Defaults |
| 15 | Finish early | Finish / Cancel |
| 19 | Next action | New simulation / Dashboard / Report |

### 8.4 Alternative Paths

- **Simulation Failed**: Show debrief with failure analysis
- **Timeout**: Auto-complete with partial score
- **Connection Lost**: Pause simulation, auto-reconnect

### 8.5 Error Scenarios

| Error | Recovery |
|---|---|
| Terminal unresponsive | Reset terminal button |
| Simulation engine crash | Auto-save state, offer resume |
| Network viewer errors | Fallback to log-only view |

### 8.6 Accessibility Considerations

- Terminal output as aria-live region
- Network viewer has text alternative
- Timeline navigable by keyboard
- Score announced on debrief load
- Color-coded severity has text labels

---

## 9. Journey: Assessment Completion

### 9.1 Goals
- Complete an assessment
- Review results

### 9.2 Steps

1. User navigates to Assessments (Alt+4)
2. User selects available assessment
3. Assessment Detail shows rules and time limit
4. User clicks "Start Assessment"
5. Timer starts counting down
6. Question 1 appears
7. User selects answer
8. User flags question for review
9. User navigates to Question 3
10. User answers Question 3
11. User navigates to Question 2 (unanswered)
12. User answers Question 2
13. User navigates to flagged Question 1
14. User changes answer
15. User reviews question navigator (all answered)
16. User clicks "Submit Assessment"
17. Confirmation dialog: "Submit with X minutes remaining?"
18. User confirms submission
19. Results screen shows score
20. User reviews question breakdown
21. User reads explanations for incorrect answers

### 9.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 8 | Flag question | Flag / Unflag |
| 14 | Change answer | Change / Keep |
| 17 | Submit | Submit / Cancel / Continue |

### 9.4 Alternative Paths

- **Time Expired**: Auto-submit with warning at 5 minutes
- **Quit Mid-Assessment**: Confirmation, progress lost
- **Pass Threshold Met**: Certificate generated automatically

### 9.5 Error Scenarios

| Error | Recovery |
|---|---|
| Auto-save fails | Retry, show save indicator |
| Timer desync | Re-sync from server time |
| Submission fails | Retry with confirmation |

### 9.6 Accessibility Considerations

- Timer announced every 5 minutes and at 1 minute
- Question navigator shows answered/flagged state textually
- Focus management on question navigation
- Results screen: score announced first, then breakdown

---

## 10. Journey: Certificate Viewing

### 10.1 Goals
- View earned certificates
- Download or print certificate

### 10.2 Steps

1. User navigates to Certificates (primary nav or dashboard link)
2. Certificate Gallery shows earned certificates
3. User clicks on "Cybersecurity Fundamentals" certificate
4. Certificate Detail opens with full preview
5. User reviews certificate details
6. User checks verification code
7. User clicks "Download PDF"
8. System generates PDF and saves to downloads folder
9. User clicks "Print"
10. System print dialog appears
11. User confirms print settings
12. Certificate prints

### 10.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 7 | Download format | PDF / PNG / Both |
| 9 | Print | Print / Cancel |

### 10.4 Alternative Paths

- **No Certificates**: Empty state with "Complete courses to earn certificates"
- **Certificate Pending**: Show pending status with expected date

### 10.5 Error Scenarios

| Error | Recovery |
|---|---|
| PDF generation fails | Retry, offer alternative format |
| Printer not found | Save to file option |

### 10.6 Accessibility Considerations

- Certificate preview has alt text description
- Download button labeled with filename
- Print dialog keyboard accessible
- Certificate details as structured data

---

## 11. Journey: Plugin Installation

### 11.1 Goals
- Install a new plugin
- Configure and enable it

### 11.2 Steps

1. Admin navigates to Plugin Manager (Settings > Plugins)
2. Admin switches to "Available" tab
3. Admin searches for "Wireshark Integration"
4. Plugin card shows description and permissions
5. Admin clicks on plugin to view detail
6. Admin reviews permissions requested
7. Admin reviews changelog
8. Admin clicks "Install"
9. Installation confirmation dialog appears
10. Admin confirms installation
11. Plugin downloads and installs
12. Progress indicator shows installation status
13. Plugin appears in "Installed" tab
14. Admin clicks "Configure"
15. Plugin configuration form appears
16. Admin enters configuration values
17. Admin clicks "Save Configuration"
18. Admin toggles plugin "Enabled"
19. Plugin becomes active

### 11.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 8 | Install | Install / Cancel |
| 14 | Configure now | Configure / Later |
| 18 | Enable | Enable / Keep disabled |

### 11.4 Alternative Paths

- **Plugin Update Available**: Show update button instead of install
- **Already Installed**: Show "Update" and "Configure" buttons
- **Insufficient Permissions**: Show permission request to admin

### 11.5 Error Scenarios

| Error | Recovery |
|---|---|
| Download fails | Retry, check connectivity |
| Installation fails | Show error log, rollback |
| Plugin conflicts | Show conflict warning, offer resolution |

### 11.6 Accessibility Considerations

- Installation progress announced
- Permission list as structured content
- Configuration form properly labeled
- Plugin status changes announced

---

## 12. Journey: Accessibility Configuration

### 12.1 Goals
- Configure accessibility preferences
- Preview changes in real-time

### 12.2 Steps

1. User navigates to Settings (Ctrl+,)
2. User selects "Accessibility" category
3. Accessibility Center opens
4. User selects "Visual" tab
5. User enables "High Contrast" mode
6. Preview panel shows contrast change immediately
7. User adjusts "Text Scale" slider to 125%
8. UI text increases in preview
9. User selects "Screen Reader" tab
10. User enables "Verbose Announcements"
11. User enables "Descriptive Links"
12. User selects "Keyboard" tab
13. User enables "Sticky Keys" support
14. User adjusts "Key Repeat Delay" slider
15. User clicks "Save Preferences"
16. Preferences apply across application
17. User navigates to Dashboard to verify

### 12.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 5 | High contrast | On / Off |
| 7 | Text scale | 100% - 200% |
| 15 | Save | Save / Reset / Cancel |

### 12.4 Alternative Paths

- **Reset to Defaults**: Revert all accessibility settings
- **Per-Application**: Apply only to specific screens
- **Import Settings**: Load from backup file

### 12.5 Error Scenarios

| Error | Recovery |
|---|---|
| Preview fails to update | Apply setting, refresh preview |
| Setting conflicts with system | Show warning, suggest resolution |

### 12.6 Accessibility Considerations

- Self-referential: accessibility settings page fully accessible
- Preview panel keyboard navigable
- All settings have visible labels and descriptions
- Changes announced via aria-live
- Save confirmation announced

---

## 13. Journey: Localization

### 13.1 Goals
- Change application language
- Verify UI updates

### 13.2 Steps

1. User navigates to Settings > Localization
2. Language selector shows available languages
3. Current language highlighted
4. User scrolls through language list
5. Language names shown in native script
6. User selects "Español"
7. Confirmation dialog appears
8. User confirms language change
9. UI updates to Spanish
10. User verifies menu items, buttons, labels
11. User adjusts date format to DD/MM/YYYY
12. User adjusts number format (comma decimal)
13. User selects timezone
14. User clicks "Save"
15. All settings apply immediately

### 13.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 7 | Confirm language | Confirm / Cancel |
| 10 | Verify | Continue / Revert |

### 13.4 Alternative Paths

- **Partial Translation**: Show percentage complete, fallback to English
- **RTL Language**: UI mirrors for right-to-left layouts
- **Reset**: Revert to system default language

### 13.5 Error Scenarios

| Error | Recovery |
|---|---|
| Translation file missing | Fallback to English, report issue |
| Format incompatible | Show warning, suggest alternative |

### 13.6 Accessibility Considerations

- Language change announced via aria-live
- Native script names properly rendered
- RTL layout maintains keyboard navigation order
- Screen reader switches language profile

---

## 14. Journey: Backup Creation

### 14.1 Goals
- Create a data backup
- Verify backup integrity

### 14.2 Steps

1. Admin navigates to Settings > Backup
2. Backup settings page shows current configuration
3. Admin selects backup location
4. Admin enables encryption (optional)
5. Admin sets encryption passphrase
6. Admin clicks "Create Backup Now"
7. Progress indicator shows backup status
8. Backup completes successfully
9. System shows backup summary (size, date, contents)
10. Admin clicks "Verify Backup"
11. Verification completes
12. Green checkmark confirms integrity

### 14.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 4 | Encryption | Enable / Disable |
| 10 | Verify | Yes / Skip |

### 14.4 Alternative Paths

- **Scheduled Backup**: Configure automatic backup schedule
- **Cloud Backup**: Select cloud storage provider
- **Incremental**: Only backup changes since last backup

### 14.5 Error Scenarios

| Error | Recovery |
|---|---|
| Disk full | Show error, suggest alternate location |
| Encryption key forgotten | Show warning about irreversibility |
| Backup corrupted | Retry, report issue |

### 14.6 Accessibility Considerations

- Backup progress announced periodically
- Completion announced via aria-live
- Error messages associated with controls
- Keyboard-only operation throughout

---

## 15. Journey: Restore Process

### 15.1 Goals
- Restore from a backup
- Verify restored data

### 15.2 Steps

1. Admin navigates to Settings > Backup
2. Admin switches to "Restore" tab
3. Admin selects backup file from list
4. System shows backup details (date, size, contents)
5. Admin clicks "Restore"
6. Warning dialog: "This will overwrite current data"
7. Admin enters confirmation text: "RESTORE"
8. Admin clicks "Confirm Restore"
9. Restore progress indicator
10. Application restarts
11. Splash screen shows restore status
12. Dashboard loads with restored data
13. Admin verifies data integrity

### 15.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 5 | Restore | Restore / Cancel |
| 7 | Confirm | Confirm / Cancel |

### 15.4 Alternative Paths

- **Partial Restore**: Select specific data types to restore
- **Preview**: Show what will be overwritten before confirming
- **Backup Before Restore**: Auto-create backup before restoring

### 15.5 Error Scenarios

| Error | Recovery |
|---|---|
| Backup file corrupt | Show error, suggest another backup |
| Restore interrupted | Resume from checkpoint |
| Version mismatch | Show compatibility warning |

### 15.6 Accessibility Considerations

- Warning dialog focus trapped
- Confirmation input properly labeled
- Restart process announced
- Data verification results accessible

---

## 16. Journey: Report Generation

### 16.1 Goals
- Generate a custom report
- Export for external use

### 16.2 Steps

1. Instructor navigates to Reports (Alt+5)
2. Reports Dashboard shows recent reports
3. Instructor clicks "Create Report"
4. Report Builder wizard opens
5. Step 1: Select report type (Student Progress)
6. Instructor selects type and clicks Next
7. Step 2: Configure data sources
8. Instructor selects courses and date range
9. Instructor clicks Next
10. Step 3: Apply filters
11. Instructor filters by completion status
12. Instructor clicks Next
13. Step 4: Choose format and layout
14. Instructor selects "Charts + Tables"
15. Instructor clicks "Generate"
16. Report generates with progress indicator
17. Report Detail displays with charts and data
18. Instructor reviews report content
19. Instructor clicks "Export"
20. Export Dialog shows format options
21. Instructor selects PDF and clicks "Download"
22. PDF saves to downloads folder

### 16.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 5 | Report type | Student / Course / Assessment / Cohort |
| 21 | Export format | PDF / CSV / JSON |

### 16.4 Alternative Paths

- **Schedule Report**: Set up recurring generation
- **Use Template**: Start from saved template
- **Save as Template**: Save configuration for reuse

### 16.5 Error Scenarios

| Error | Recovery |
|---|---|
| No data matches filters | Show empty state, suggest filter changes |
| Export fails | Retry, offer alternative format |
| Report generation timeout | Show progress, offer background processing |

### 16.6 Accessibility Considerations

- Wizard steps announced with current/total
- Form validation errors linked to fields
- Charts have text alternatives
- Export progress announced
- PDF download link accessible

---

## 17. Journey: Administration — User Management

### 17.1 Goals
- Create new user account
- Assign role and permissions

### 17.2 Steps

1. Admin navigates to Administration (Alt+8)
2. Admin selects "Users" from secondary nav
3. User Management table displays
4. Admin clicks "Add User"
5. User Create form appears
6. Admin enters email (required)
7. Admin enters display name (required)
8. Admin selects role from dropdown
9. Admin assigns organization/department
10. Admin sets initial password
11. Admin clicks "Create User"
12. Confirmation dialog appears
13. Admin confirms creation
14. New user appears in table
15. Admin clicks on user to view detail
16. User Detail shows profile and activity

### 17.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 8 | Role assignment | Student / Instructor / Admin |
| 13 | Confirm | Create / Cancel |

### 17.4 Alternative Paths

- **Bulk Import**: Upload CSV of users
- **Invite via Email**: Send invitation link
- **Deactivate User**: Toggle user status

### 17.5 Error Scenarios

| Error | Recovery |
|---|---|
| Email already exists | Show error, suggest correction |
| Invalid email format | Show validation error |
| Role assignment fails | Show error, retry |

### 17.6 Accessibility Considerations

- Table keyboard navigable (arrow keys)
- Form fields properly labeled
- Confirmation dialog focus trapped
- User creation announced via aria-live

---

## 18. Journey: Diagnostics

### 18.1 Goals
- Diagnose system issues
- Export diagnostic data for support

### 18.2 Steps

1. Admin navigates to Help > Diagnostics
2. System Health dashboard displays
3. Admin sees yellow warning on "Database" component
4. Admin clicks "Database" to drill down
5. Database Integrity tool shows warning
6. Admin clicks "Run Integrity Check"
7. Check runs with progress indicator
8. Results show 2 minor issues found
9. Admin clicks "Auto-Repair"
10. Repair completes successfully
11. Admin clicks "Back to Health"
12. Database shows green status
13. Admin clicks "Export Diagnostics"
14. Export includes logs, health data, system info
15. File saves to downloads folder

### 18.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 9 | Repair | Auto-Repair / Manual / Skip |
| 14 | Export scope | Full / Selected |

### 18.4 Alternative Paths

- **No Issues**: Show all green, suggest export for baseline
- **Critical Issue**: Show red alert, prevent further operations
- **Repair Fails**: Show manual repair instructions

### 18.5 Error Scenarios

| Error | Recovery |
|---|---|
| Integrity check fails | Show error, suggest restart |
| Repair fails | Show error log, offer manual steps |
| Export fails | Retry, show file path error |

### 18.6 Accessibility Considerations

- Status colors have text labels
- Progress announced via aria-live
- Repair results as structured content
- Export completion announced

---

## 19. Journey: Help Search

### 19.1 Goals
- Find documentation for a feature
- Learn how to use a specific function

### 19.2 Steps

1. User presses F1 or clicks Help icon
2. Help Center opens
3. Search bar receives focus
4. User types "configure keyboard shortcuts"
5. Search results appear in real-time
6. Results show article title, snippet, and category
7. User navigates results with arrow keys
8. User selects "Keyboard Shortcuts Configuration"
9. Article displays with table of contents
10. User reads through content
11. User clicks "Was this helpful?" Yes
12. User closes help and returns to previous screen

### 19.3 Decision Points

| Step | Decision | Options |
|---|---|---|
| 8 | Select article | Open / More results |
| 11 | Feedback | Helpful / Not helpful |

### 19.4 Alternative Paths

- **No Results**: Suggest alternative searches, show related topics
- **Tutorial Available**: Link to interactive tutorial
- **Video Available**: Link to video walkthrough

### 19.5 Error Scenarios

| Error | Recovery |
|---|---|
| Search index not loaded | Show loading, retry |
| Article not found | Show 404, suggest similar articles |

### 19.6 Accessibility Considerations

- Search results announced with count
- Article headings properly structured
- Table of contents keyboard navigable
- Focus management on article load
- "Was this helpful?" accessible via keyboard
