# AuthShield Lab — Notification Framework

## 1. Overview

This document defines the complete notification system for AuthShield Lab. The
framework handles notifications from system events, learning progress, security
events, plugin activity, and background tasks. All notifications are fully
accessible and keyboard-operable.

---

## 2. Notification Types

### 2.1 Type Definitions

| Type | Icon | Color | Default Sound | Auto-Dismiss |
|---|---|---|---|---|
| Information | ℹ | Blue (#3B82F6) | Soft chime | 5 seconds |
| Warning | ⚠ | Amber (#F59E0B) | Alert tone | 8 seconds |
| Error | ✕ | Red (#EF4444) | Error beep | Manual dismiss only |
| Success | ✓ | Green (#22C55E) | Success tone | 4 seconds |

### 2.2 Type Usage Rules

**Information:**
- Course published by instructor
- New content available
- Backup completed
- Plugin installed
- Report generated
- Sync completed

**Warning:**
- Assessment due soon (24h, 1h, 15min)
- Storage running low
- Session expiring soon
- Sync conflict detected
- Deprecated plugin feature

**Error:**
- Login attempt blocked
- Permission denied
- Backup failed
- Plugin error
- Network connection lost
- Database integrity issue
- Export failed

**Success:**
- Settings saved
- Course enrolled
- Assessment submitted
- Backup verified
- Plugin installed
- Certificate earned
- Restore completed

---

## 3. Notification Sources

### 3.1 System Notifications

| Event | Type | Message Template | Action |
|---|---|---|---|
| Backup complete | Success | "Backup completed successfully. Size: {size}" | View details |
| Update available | Information | "Version {version} is available" | View changelog |
| Session expiring | Warning | "Your session expires in {time}" | Extend session |
| Storage low | Warning | "Storage is {percent}% full. {remaining} available" | Manage storage |
| Sync complete | Success | "All changes synced successfully" | View sync log |
| Network lost | Error | "Network connection lost. Working offline." | View queue |
| Network restored | Success | "Network connection restored. Syncing {count} items." | View progress |

### 3.2 Learning Notifications

| Event | Type | Message Template | Action |
|---|---|---|---|
| Course published | Information | "New course available: {title}" | View course |
| Course updated | Information | "{title} has been updated" | View changes |
| Assessment graded | Success | "Assessment graded: {score}%" | View results |
| Assessment due | Warning | "Assessment due in {time}: {title}" | Start assessment |
| Certificate earned | Success | "You earned: {certificate_name}" | View certificate |
| Lesson available | Information | "New lesson available: {title}" | Start lesson |
| Progress milestone | Success | "You've completed {percent}% of {course}" | View progress |

### 3.3 Security Notifications

| Event | Type | Message Template | Action |
|---|---|---|---|
| Login attempt blocked | Error | "Failed login attempt from {source}" | View audit log |
| Permission denied | Warning | "Access denied to {resource}" | Request access |
| Password expiring | Warning | "Password expires in {days} days" | Change password |
| 2FA code requested | Information | "Verification code sent" | Enter code |
| Session started | Information | "New session on {device}" | Manage sessions |

### 3.4 Plugin Notifications

| Event | Type | Message Template | Action |
|---|---|---|---|
| Plugin installed | Success | "Plugin installed: {name}" | Configure |
| Plugin updated | Information | "Plugin updated: {name} v{version}" | View changelog |
| Plugin error | Error | "Plugin error: {name} - {error}" | View logs |
| Plugin permission | Warning | "Plugin requests: {permission}" | Manage |
| Plugin deprecated | Warning | "Plugin {name} will be removed" | Find alternative |

### 3.5 Background Task Notifications

| Event | Type | Message Template | Action |
|---|---|---|---|
| Task complete | Success | "{task_name} completed" | View result |
| Task failed | Error | "{task_name} failed: {reason}" | Retry |
| Task cancelled | Information | "{task_name} was cancelled" | View details |
| Long task complete | Success | "{task_name} finished after {time}" | View result |

---

## 4. Notification Delivery Methods

### 4.1 Toast Notifications

**Position:** Bottom-center of screen
**Duration:** Per type (see 2.1)
**Stacking:** Maximum 3 visible, newest at bottom

```
┌─────────────────────────────────────────────────┐
│  ✅ Backup completed successfully               │
│     Size: 2.4 MB                    [View] [✕]  │
└─────────────────────────────────────────────────┘
```

**Behavior:**
- Slide in from bottom
- Auto-dismiss after duration
- Manual dismiss via X button or Escape
- Click action button to navigate
- Maximum 3 visible at once
- Older toasts queue and show after current dismisses
- Pause auto-dismiss on hover (not on focus for accessibility)

**Keyboard:**
- Tab to toast action buttons
- Enter to activate
- Escape to dismiss

### 4.2 Banner Notifications

**Position:** Top of content area, below header
**Duration:** Persistent until dismissed
**Stacking:** Maximum 1 visible

```
┌─────────────────────────────────────────────────┐
│  ⚠️ Your session expires in 5 minutes.          │
│     [Extend Session]              [Dismiss]      │
└─────────────────────────────────────────────────┘
```

**Behavior:**
- Slides down from top
- Stays visible until action or dismiss
- Maximum 1 banner at a time
- Priority: Error > Warning > Information
- Dismissed banners do not reappear (stored as read)
- Keyboard: Tab to actions, Enter to activate, Escape to dismiss

### 4.3 Badge Notifications

**Position:** Bell icon in header
**Format:** Counter number (99+ for large counts)

```
  🔔 3
```

**Behavior:**
- Counter updates in real-time
- Maximum display: "99+"
- Clears when notification center is opened and all read
- Persists until all notifications are read
- Screen reader: "3 unread notifications"

### 4.4 Notification Center Panel

**Position:** Slides in from right side
**Trigger:** Click bell icon or Alt+N

```
┌─────────────────────────────────────────────┐
│  Notifications                 [Mark All Read]│
│  ───────────────────────────────────────────│
│  Today                                        │
│  ├── ✅ Backup completed            14:32    │
│  ├── ⚠️ Assessment due tomorrow     12:15    │
│  └── ℹ️ Course updated              10:00    │
│                                              │
│  Yesterday                                   │
│  ├── ✅ Certificate earned          16:45    │
│  ├── ❌ Login attempt blocked       09:12    │
│  └── ✅ Settings saved              08:30    │
│                                              │
│  ───────────────────────────────────────────│
│  [View All]  [Settings]  [Clear All]         │
└─────────────────────────────────────────────┘
```

**Behavior:**
- Grouped by date (Today, Yesterday, This Week, Earlier)
- Scrollable for long lists
- Click notification to navigate to relevant screen
- Right-click for context menu (mark read, dismiss, snooze)
- Keyboard: Arrow keys to navigate, Enter to open, Delete to dismiss

---

## 5. Notification Preferences

### 5.1 Preference Categories

```
Settings > Notifications
├── System
│   ├── Backup complete          [✓ Enabled]
│   ├── Update available         [✓ Enabled]
│   ├── Session expiring         [✓ Enabled]
│   └── Storage low              [✓ Enabled]
├── Learning
│   ├── Course published         [✓ Enabled]
│   ├── Assessment graded        [✓ Enabled]
│   ├── Assessment due           [✓ Enabled]
│   └── Certificate earned       [✓ Enabled]
├── Security
│   ├── Login blocked            [✓ Enabled]
│   ├── Permission denied        [✓ Enabled]
│   └── Password expiring        [✓ Enabled]
├── Plugins
│   ├── Installed                [✓ Enabled]
│   ├── Updated                  [✓ Enabled]
│   └── Errors                   [✓ Enabled]
├── Background Tasks
│   ├── Task complete            [✓ Enabled]
│   └── Task failed              [✓ Enabled]
└── Global
    ├── Sound                    [✓ Enabled]
    ├── Desktop notifications    [✓ Enabled]
    ├── Toast notifications      [✓ Enabled]
    └── Badge notifications      [✓ Enabled]
```

### 5.2 Preference Behavior

- Each category can be individually enabled/disabled
- Per-type toggles override category toggles
- Global toggles override all per-type settings
- Changes apply immediately
- Critical security notifications cannot be fully disabled (warning shown)
- Desktop notifications require OS permission

### 5.3 Desktop Notifications

- Use Electron Notification API
- Show OS-native notification
- Include title, body, and icon
- Click to focus application and navigate
- Respect OS Do Not Disturb mode
- Fallback to in-app toast if permission denied

---

## 6. Notification History

### 6.1 Storage

- All notifications stored in IndexedDB
- Maximum 500 notifications retained
- Oldest notifications pruned automatically
- User can manually clear history

### 6.2 History Panel

Access via Settings > Notifications > View History

```
┌─────────────────────────────────────────────┐
│  Notification History          [Search 🔍]   │
│  ───────────────────────────────────────────│
│  Filter: [All Types ▼]  [All Sources ▼]      │
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │ ✅ Backup completed    14:32 Read   │    │
│  │ ⚠️ Assessment due      12:15 Unread │    │
│  │ ℹ️ Course updated      10:00 Read   │    │
│  │ ...                                   │    │
│  └─────────────────────────────────────┘    │
│                                              │
│  [Mark Selected Read]  [Delete Selected]     │
└─────────────────────────────────────────────┘
```

### 6.3 History Actions

- Mark as read/unread
- Delete individual notifications
- Bulk select and actions
- Search notification content
- Filter by type, source, date, read status
- Export notification history

---

## 7. Notification Accessibility

### 7.1 ARIA Live Regions

```html
<!-- Toast notifications -->
<div aria-live="polite" aria-atomic="true" class="toast-container">
  <div role="status">
    Backup completed successfully. Size: 2.4 MB.
  </div>
</div>

<!-- Error notifications -->
<div aria-live="assertive" aria-atomic="true" class="error-toast">
  <div role="alert">
    Login attempt blocked. View audit log for details.
  </div>
</div>

<!-- Badge counter -->
<span aria-label="3 unread notifications" role="status">3</span>
```

### 7.2 Screen Reader Behavior

| Event | Announcement |
|---|---|
| Toast appears | Full notification text read aloud |
| Error toast appears | Read immediately (assertive) |
| Badge updates | "X unread notifications" |
| Notification center opens | "Notification center, X notifications" |
| Notification read | "Marked as read" |
| Notification dismissed | "Notification dismissed" |

### 7.3 Keyboard Accessibility

| Action | Shortcut |
|---|---|
| Open notification center | Alt+N |
| Navigate notifications | Arrow Up/Down |
| Open notification | Enter |
| Dismiss notification | Delete |
| Mark as read | R |
| Mark all as read | Ctrl+R |
| Close notification center | Escape |
| Dismiss toast | Escape |
| Snooze toast | S (when focused) |

### 7.4 Visual Accessibility

- All type indicators use icon + text (not color alone)
- Toast borders have sufficient contrast (3:1 minimum)
- Notification text meets WCAG AA contrast (4.5:1)
- Focus indicators visible on all interactive elements
- Animations respect prefers-reduced-motion
- High contrast mode uses borders instead of colors

---

## 8. Notification Actions

### 8.1 Action Types

| Action | Description | Availability |
|---|---|---|
| View | Navigate to related screen | All notifications |
| Dismiss | Remove notification | All notifications |
| Snooze | Delay notification display | Toasts, non-critical |
| Configure | Open relevant settings | All notifications |
| Retry | Re-attempt failed operation | Failed operations |
| Export | Download notification data | History panel |

### 8.2 Action Implementation

```typescript
interface NotificationAction {
  type: 'view' | 'dismiss' | 'snooze' | 'configure' | 'retry' | 'export';
  label: string;
  target?: string; // route or setting path
  handler: () => void;
  accessibility: {
    ariaLabel: string;
    keyboardShortcut?: string;
  };
}
```

### 8.3 View Action

- Navigates to the screen relevant to the notification
- Marks notification as read
- Closes notification center (if open)
- Focus moves to relevant content on target screen

### 8.4 Dismiss Action

- Removes notification from panel
- Does not navigate
- Toast: removes immediately
- Panel item: fade-out animation
- Undo available for 3 seconds via undo toast

### 8.5 Snooze Action

- Hides notification temporarily
- Reappears after snooze period
- Snooze options: 15 minutes, 1 hour, 4 hours, tomorrow
- Maximum snooze: 24 hours
- Snoozed notifications in separate "Snoozed" section

---

## 9. Notification Priority

### 9.1 Priority Levels

| Level | Types | Behavior |
|---|---|---|
| Critical (P0) | Security errors, system failures | Banner + toast + sound + desktop |
| High (P1) | Errors, assessment deadlines | Toast + sound + badge |
| Medium (P2) | Warnings, task completions | Toast + badge |
| Low (P3) | Informational updates | Badge only (optional toast) |

### 9.2 Priority Rules

- Critical notifications always show regardless of preferences
- Maximum 3 toasts visible; overflow queued by priority
- Higher priority notifications push lower priority ones out
- Banner notifications reserved for P0 and P1 only
- Desktop notifications configurable per priority level

---

## 10. Notification Sound

### 10.1 Sound Library

| Sound | Usage | Duration |
|---|---|---|
| Soft chime | Information | 0.5s |
| Alert tone | Warning | 0.8s |
| Error beep | Error | 0.3s |
| Success tone | Success | 0.5s |
| Critical alarm | Critical | 1.0s (repeats) |

### 10.2 Sound Behavior

- Sounds disabled by default (opt-in via settings)
- Respects system volume
- Respects Do Not Disturb mode
- Can be previewed in notification settings
- Per-type enable/disable
- Volume slider in settings
- Master mute toggle
