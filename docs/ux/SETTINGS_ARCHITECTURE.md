# AuthShield Lab — Settings Architecture

## 1. Overview

This document defines the complete settings organization for AuthShield Lab.
Settings are organized into categories with clear ownership, visibility rules,
dependencies, and import/export capabilities.

---

## 2. Settings Categories

### 2.1 General

**Route:** `/settings/general`
**Owner:** User (personal), Admin (app-wide defaults)

| Setting | Type | Default | Description |
|---|---|---|---|
| Application Name | Text | "AuthShield Lab" | Display name in title bar |
| Startup Behavior | Dropdown | "Show Dashboard" | Screen shown on launch |
| Default View | Dropdown | "Student View" | Default workspace view |
| Auto-check Updates | Toggle | On | Check for updates on startup |
| Confirm on Exit | Toggle | On | Prompt before closing |
| Open Last Session | Toggle | On | Restore tabs on restart |
| Tab Behavior | Dropdown | "Smart" | New tab vs current tab behavior |

### 2.2 Appearance

**Route:** `/settings/appearance`
**Owner:** User (personal)

| Setting | Type | Default | Description |
|---|---|---|---|
| Theme | Dropdown | "System" | Light / Dark / High Contrast / System |
| Accent Color | Color Picker | Blue (#3B82F6) | Primary accent color |
| Font Size | Slider | 16px | Base font size (12px - 24px) |
| Font Family | Dropdown | "System" | Application font |
| Density | Dropdown | "Default" | Compact / Default / Comfortable |
| Sidebar Position | Dropdown | "Left" | Left / Right |
| Show Icons in Menus | Toggle | On | Display icons alongside text |
| Animation Speed | Dropdown | "Normal" | Reduced / Normal / Fast |
| Border Radius | Dropdown | "Default" | None / Default / Rounded |

### 2.3 Accessibility

**Route:** `/settings/accessibility`
**Owner:** User (personal)

**Screen Reader Tab:**
| Setting | Type | Default | Description |
|---|---|---|---|
| Verbose Announcements | Toggle | Off | Announce more UI changes |
| Announce Navigation | Toggle | On | Announce page transitions |
| Announce Updates | Toggle | On | Announce dynamic content changes |
| Descriptive Links | Toggle | Off | More detailed link descriptions |
| Describe Images | Toggle | On | Read image descriptions |

**Keyboard Tab:**
| Setting | Type | Default | Description |
|---|---|---|---|
| Sticky Keys | Toggle | Off | Sequential modifier keys |
| Key Repeat Delay | Slider | 500ms | Delay before key repeats (100ms - 2000ms) |
| Key Repeat Rate | Slider | 30/s | Keys per second when held (5 - 50) |
| Bounce Keys | Toggle | Off | Ignore rapid repeated presses |
| Keyboard Shortcuts | Toggle | On | Enable keyboard shortcuts |
| Shortcut Delay | Dropdown | "None" | Delay before shortcut activates |

**Visual Tab:**
| Setting | Type | Default | Description |
|---|---|---|---|
| High Contrast | Toggle | Off | Increase contrast ratios |
| Focus Indicator Style | Dropdown | "Default" | Default / Bold / High Visibility |
| Focus Indicator Color | Color Picker | System | Custom focus ring color |
| Reduce Motion | Toggle | System | Disable animations |
| Reduce Transparency | Toggle | Off | Remove transparent effects |
| Text Spacing | Dropdown | "Default" | Default / Wide / Extra Wide |
| Line Height | Dropdown | "Default" | Default / Relaxed / Loose |
| Cursor Size | Dropdown | "Default" | Default / Large / Extra Large |

**Motor Tab:**
| Setting | Type | Default | Description |
|---|---|---|---|
| Click Delay | Slider | 0ms | Delay before click registers |
| Dwell Click | Toggle | Off | Click by hovering |
| Large Click Targets | Toggle | Off | Increase button/link sizes |
| Timeout Extension | Dropdown | "Default" | Extend session timeouts |
| Auto-save Frequency | Dropdown | "30 seconds" | More frequent autosave |

### 2.4 Localization

**Route:** `/settings/localization`
**Owner:** User (personal)

| Setting | Type | Default | Description |
|---|---|---|---|
| Language | Dropdown | "English" | UI language |
| Region | Dropdown | "United States" | Regional conventions |
| Date Format | Dropdown | "MM/DD/YYYY" | Date display format |
| Time Format | Dropdown | "12-hour" | 12-hour / 24-hour |
| Number Format | Dropdown | "1,234.56" | Number display format |
| Currency Format | Dropdown | "USD ($)" | Currency display |
| Timezone | Dropdown | "System" | UTC offset |
| First Day of Week | Dropdown | "Sunday" | Calendar first day |
| Measurement System | Dropdown | "Imperial" | Imperial / Metric |

**Available Languages:**
| Language | Code | Translation Status |
|---|---|---|
| English | en | 100% |
| Spanish | es | 95% |
| French | fr | 90% |
| German | de | 88% |
| Japanese | ja | 85% |
| Portuguese (BR) | pt-BR | 82% |
| Chinese (Simplified) | zh-CN | 80% |
| Arabic | ar | 75% |
| Russian | ru | 70% |

### 2.5 Security

**Route:** `/settings/security`
**Owner:** Admin (system-wide), User (personal 2FA)

| Setting | Type | Default | Description |
|---|---|---|---|
| Password Minimum Length | Number | 8 | Minimum password characters |
| Password Complexity | Dropdown | "Medium" | Low / Medium / High |
| Session Timeout | Dropdown | "30 minutes" | Auto-logout after inactivity |
| Remember Me Duration | Dropdown | "30 days" | How long to remember login |
| Two-Factor Authentication | Toggle | Off | Enable 2FA (user-level) |
| 2FA Method | Dropdown | "TOTP" | TOTP / Backup Codes |
| Max Login Attempts | Number | 5 | Attempts before lockout |
| Lockout Duration | Dropdown | "15 minutes" | Account lockout period |
| Require Password Change | Dropdown | "Never" | Force password rotation |
| Session Per Device | Toggle | On | One active session per device |

### 2.6 Privacy

**Route:** `/settings/privacy`
**Owner:** Admin (system), User (personal)

| Setting | Type | Default | Description |
|---|---|---|---|
| Analytics Collection | Toggle | On | Anonymous usage analytics |
| Error Reporting | Toggle | On | Send crash reports |
| Activity Tracking | Toggle | On | Track learning activity |
| Audit Log Retention | Dropdown | "90 days" | How long to keep audit logs |
| Data Retention | Dropdown | "1 year" | How long to keep user data |
| Export on Request | Toggle | On | Allow data export requests |
| Anonymize on Delete | Toggle | On | Anonymize data on account deletion |

### 2.7 Notifications

**Route:** `/settings/notifications`
**Owner:** User (personal)

See NOTIFICATION_FRAMEWORK.md Section 5 for complete notification preferences.

### 2.8 Storage

**Route:** `/settings/storage`
**Owner:** User (personal view), Admin (management)

| Setting | Type | Default | Description |
|---|---|---|---|
| Data Location | Path | System default | Local data storage path |
| Cache Size Limit | Dropdown | "500 MB" | Maximum cache size |
| Clear Cache | Button | — | Manually clear cached data |
| Storage Usage | Display | — | Shows current usage breakdown |
| Auto-cleanup | Toggle | On | Remove old cache automatically |
| Cleanup Age | Dropdown | "30 days" | Remove cache older than |

**Storage Usage Display:**
```
┌─────────────────────────────────────────┐
│  Storage Usage                           │
│  ───────────────────────────────────────│
│  Database:     45 MB  ████████████░░░░  │
│  Cache:        120 MB ████████████████░  │
│  Plugins:      35 MB  █████░░░░░░░░░░░  │
│  Media:        80 MB  ██████████░░░░░░  │
│  Backups:      200 MB ██████████████████ │
│  ───────────────────────────────────────│
│  Total:        480 MB / 2 GB             │
│  [Clear Cache]  [Manage Backups]         │
└─────────────────────────────────────────┘
```

### 2.9 Backup

**Route:** `/settings/backup`
**Owner:** Admin

| Setting | Type | Default | Description |
|---|---|---|---|
| Auto Backup | Toggle | On | Enable automatic backups |
| Backup Schedule | Dropdown | "Weekly" | Daily / Weekly / Monthly |
| Backup Time | Time Picker | "02:00" | When to run backups |
| Backup Location | Path | System default | Where to store backups |
| Encryption | Toggle | On | Encrypt backup files |
| Encryption Passphrase | Password | — | Encryption key (hidden) |
| Retention Count | Number | 5 | Number of backups to keep |
| Backup Content | Checkboxes | All | What to include in backup |
| Compress | Toggle | On | Compress backup files |

### 2.10 Learning

**Route:** `/settings/learning`
**Owner:** User (personal)

| Setting | Type | Default | Description |
|---|---|---|---|
| Default Difficulty | Dropdown | "Beginner" | Preferred difficulty level |
| Auto-play Videos | Toggle | On | Start videos automatically |
| Video Playback Speed | Dropdown | "1x" | Default playback speed |
| Show Hints | Toggle | On | Display learning hints |
| Flashcard Review Interval | Dropdown | "Daily" | Spaced repetition schedule |
| Study Reminder | Toggle | Off | Daily study reminder |
| Reminder Time | Time Picker | "18:00" | When to send reminder |
| Progress Tracking | Toggle | On | Track learning progress |
| Show Completion % | Toggle | On | Display progress percentage |

### 2.11 Diagnostics

**Route:** `/settings/diagnostics`
**Owner:** Admin, Operator

| Setting | Type | Default | Description |
|---|---|---|---|
| Logging Level | Dropdown | "Warning" | Error / Warning / Info / Debug |
| Log Retention | Dropdown | "30 days" | How long to keep logs |
| Crash Reporting | Toggle | On | Send crash reports |
| Performance Monitoring | Toggle | On | Track performance metrics |
| Show Debug Info | Toggle | Off | Display debug information |
| Log Location | Path | System default | Where to store logs |
| Export Logs | Button | — | Export all logs to file |

### 2.12 Advanced

**Route:** `/settings/advanced`
**Owner:** Admin

| Setting | Type | Default | Description |
|---|---|---|---|
| Developer Mode | Toggle | Off | Enable developer tools |
| Experimental Features | Toggle | Off | Enable beta features |
| Force Offline Mode | Toggle | Off | Always work offline |
| Sync Interval | Dropdown | "5 minutes" | How often to sync |
| Database Optimization | Button | — | Optimize local database |
| Reset Application | Button | — | Reset all settings to defaults |
| Reset User Data | Button | — | Clear all user data |

### 2.13 Administration

**Route:** `/settings/administration`
**Owner:** Admin, Institution Manager

| Setting | Type | Default | Description |
|---|---|---|---|
| Institution Name | Text | — | Organization name |
| Institution Logo | Upload | — | Organization logo |
| Default Role | Dropdown | "Student" | Default role for new users |
| Self Registration | Toggle | Off | Allow self-registration |
| Email Domain Restrictions | Text | — | Allowed email domains |
| User Quota | Number | 1000 | Maximum users |
| Course Quota | Number | 100 | Maximum courses |
| Plugin Approval | Toggle | On | Require admin approval for plugins |
| API Access | Toggle | Off | Enable API access |
| API Key | Text (readonly) | — | API access key |

---

## 3. Settings Dependencies

### 3.1 Dependency Graph

```
Theme (Appearance)
  └── affects → Focus Indicator Color (Accessibility)
  └── affects → High Contrast (Accessibility)
  └── affects → Font Size (Accessibility)

Language (Localization)
  └── affects → Date Format (Localization)
  └── affects → Number Format (Localization)
  └── affects → Time Format (Localization)

Session Timeout (Security)
  └── affects → Timeout Extension (Accessibility)
  └── affects → Remember Me Duration (Security)

Developer Mode (Advanced)
  └── enables → Debug Info (Diagnostics)
  └── enables → Experimental Features (Advanced)
  └── enables → Additional settings in other categories

Auto Backup (Backup)
  └── requires → Backup Location
  └── enables → Backup Schedule, Backup Time, Retention

Encryption (Backup)
  └── requires → Encryption Passphrase

Self Registration (Administration)
  └── enables → Email Domain Restrictions
  └── enables → Default Role

Analytics Collection (Privacy)
  └── enables → Activity Tracking
```

### 3.2 Cascading Effects

| Setting Changed | Affected Settings | Effect |
|---|---|---|
| Theme → Dark | Focus Indicator Color | Auto-adjusts for contrast |
| Theme → High Contrast | High Contrast (A11y) | Enables automatically |
| Language → Arabic | UI Layout | Mirrors for RTL |
| Developer Mode → On | Debug Info | Enables automatically |
| Auto Backup → Off | Backup Schedule, Time | Disables and grays out |
| Encryption → Off | Encryption Passphrase | Hides passphrase field |

---

## 4. Settings Visibility Rules

### 4.1 Role-Based Visibility

| Setting Category | Student | Instructor | Admin | Inst. Manager | Operator |
|---|---|---|---|---|---|
| General | ✓ | ✓ | ✓ | ✓ | ✓ |
| Appearance | ✓ | ✓ | ✓ | ✓ | ✓ |
| Accessibility | ✓ | ✓ | ✓ | ✓ | ✓ |
| Localization | ✓ | ✓ | ✓ | ✓ | ✓ |
| Security (personal) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Security (system) | ✗ | ✗ | ✓ | ✓ | ✗ |
| Privacy (personal) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Privacy (system) | ✗ | ✗ | ✓ | ✓ | ✗ |
| Notifications | ✓ | ✓ | ✓ | ✓ | ✓ |
| Storage | ✓ | ✓ | ✓ | ✓ | ✓ |
| Backup | ✗ | ✗ | ✓ | ✓ | ✓ |
| Learning | ✓ | ✓ | ✓ | ✓ | ✓ |
| Diagnostics | ✗ | ✗ | ✓ | ✓ | ✓ |
| Advanced | ✗ | ✗ | ✓ | ✗ | ✗ |
| Administration | ✗ | ✗ | ✓ | ✓ | ✗ |

### 4.2 Individual Setting Visibility

Some settings within categories are conditionally visible:

- **Session Timeout**: Visible when Developer Mode is off
- **Debug Info**: Visible only when Developer Mode is on
- **Experimental Features**: Visible only when Developer Mode is on
- **Encryption Passphrase**: Visible only when Encryption is on
- **Backup Schedule**: Visible only when Auto Backup is on
- **Email Domain Restrictions**: Visible only when Self Registration is on
- **API Key**: Visible only when API Access is on

---

## 5. Settings Import/Export

### 5.1 Export Settings

```
┌─────────────────────────────────────────────┐
│  Export Settings                              │
│  ───────────────────────────────────────────│
│  Select settings to export:                   │
│  [✓] General                                  │
│  [✓] Appearance                               │
│  [✓] Accessibility                            │
│  [✓] Localization                             │
│  [ ] Security (requires confirmation)         │
│  [ ] Privacy (requires confirmation)          │
│  [✓] Notifications                            │
│  [✓] Learning                                 │
│  [ ] Administration (admin only)              │
│                                              │
│  Format: [JSON ▼]  [Encrypt: ☐]              │
│                                              │
│  [Cancel]                   [Export Settings] │
└─────────────────────────────────────────────┘
```

### 5.2 Import Settings

```
┌─────────────────────────────────────────────┐
│  Import Settings                              │
│  ───────────────────────────────────────────│
│                                              │
│  Select a settings file to import:            │
│  [Choose File...]                             │
│                                              │
│  Preview:                                     │
│  General: 3 settings will be updated          │
│  Appearance: 5 settings will be updated       │
│  Accessibility: 2 settings will be updated    │
│                                              │
│  ⚠️ Importing will overwrite current values.  │
│  A backup will be created automatically.      │
│                                              │
│  [Cancel]            [Import Settings]        │
└─────────────────────────────────────────────┘
```

### 5.3 Export Format

```json
{
  "version": "1.0",
  "exportDate": "2026-07-19T12:00:00Z",
  "application": "AuthShield Lab",
  "settings": {
    "general": {
      "applicationName": "AuthShield Lab",
      "startupBehavior": "showDashboard"
    },
    "appearance": {
      "theme": "dark",
      "accentColor": "#3B82F6",
      "fontSize": 16
    },
    "accessibility": {
      "screenReader": {
        "verboseAnnouncements": false
      },
      "visual": {
        "highContrast": true,
        "reduceMotion": true
      }
    }
  }
}
```

### 5.4 Import Behavior

- Validates import file format
- Shows preview of changes before applying
- Creates automatic backup before import
- Skips security/privacy settings unless explicitly selected
- Confirms destructive overwrites
- Reports success/failure per category
- Offers to restart application if needed

---

## 6. Settings State Management

### 6.1 Settings Store (Zustand)

```typescript
interface SettingsState {
  general: GeneralSettings;
  appearance: AppearanceSettings;
  accessibility: AccessibilitySettings;
  localization: LocalizationSettings;
  security: SecuritySettings;
  privacy: PrivacySettings;
  notifications: NotificationSettings;
  storage: StorageSettings;
  backup: BackupSettings;
  learning: LearningSettings;
  diagnostics: DiagnosticsSettings;
  advanced: AdvancedSettings;
  administration: AdministrationSettings;

  updateSetting: (category: string, key: string, value: any) => void;
  resetCategory: (category: string) => void;
  resetAll: () => void;
  exportSettings: (categories: string[], encrypt: boolean) => string;
  importSettings: (data: string) => void;
  getDefaults: (category: string) => Settings;
  isModified: (category: string) => boolean;
}
```

### 6.2 Settings Persistence

- Settings stored in IndexedDB
- Changed immediately on user action
- Debounced for rapid changes (500ms)
- Synced across windows via broadcast channel
- Exported/imported as JSON files
- Backup included in full backups

---

## 7. Settings UI Patterns

### 7.1 Settings Form Layout

```
┌─────────────────────────────────────────────────────┐
│  ⚙ Settings                                         │
│  ───────────────────────────────────────────────────│
│  General        │  Application Name: [AuthShield Lab]│
│  Appearance     │  Startup Behavior: [Dashboard  ▼]  │
│  Accessibility  │  Default View:      [Student   ▼]  │
│  Localization   │  Auto-check Updates: [✓]           │
│  Security       │  Confirm on Exit:    [✓]           │
│  Privacy        │  Open Last Session:  [✓]           │
│  Notifications  │  Tab Behavior:       [Smart    ▼]  │
│  Storage        │                                    │
│  Backup         │                                    │
│  Learning       │                                    │
│  Diagnostics    │                                    │
│  Advanced       │                                    │
│  Admin          │                                    │
│                 │  ───────────────────────────────────│
│                 │  [Reset Category]  [Save]           │
└─────────────────────────────────────────────────────┘
```

### 7.2 Settings Change Behavior

- Changes apply immediately (no save button required for most settings)
- "Reset Category" button reverts to defaults
- Visual indicator for modified settings (bold label)
- Confirmation for destructive changes
- Toast notification on save
- Undo available for 5 seconds after change

### 7.3 Settings Search

- Search bar at top of settings
- Searches setting labels, descriptions, and keywords
- Highlights matching settings
- Narrows sidebar to show only matching categories
- Keyboard: Ctrl+K or / to focus search
