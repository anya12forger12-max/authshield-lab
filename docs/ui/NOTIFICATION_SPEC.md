# AuthShield Lab — Notification Specifications

> Notification UI behavior, types, accessibility, and priority levels for AuthShield Lab.

---

## 1. Notification Types Overview

| Type               | Visibility       | Dismissal           | Priority Range |
|--------------------|------------------|---------------------|----------------|
| Toast              | Temporary        | Auto-dismiss        | Low–Medium     |
| Persistent Alert   | Until action     | Manual dismiss      | Medium–High    |
| Progress Indicator | During task      | On task complete    | Low            |
| Security Banner    | Until acknowledged| Requires action    | Critical       |
| Dialog             | Modal overlay    | Requires response   | Critical       |
| Notification Center| Permanent log    | Manual clear        | All            |

---

## 2. Toast Messages

### Behavior

- Slide in from top-right corner.
- Auto-dismiss after 5 seconds (errors: 8 seconds).
- Maximum 3 visible at a time; additional toasts queue.
- Stack vertically with 8px gap.
- Pause auto-dismiss on hover or focus.
- Dismiss on click (X button) or Escape key.

### Variants

| Variant  | Color   | Icon       | Example Use                    |
|----------|---------|------------|--------------------------------|
| Success  | Green   | ✓ checkmark| Save complete, export finished |
| Error    | Red     | ✕ cross    | Action failed, validation err  |
| Warning  | Amber   | ⚠ triangle | Low disk space, deprecation    |
| Info     | Blue    | ℹ circle   | Tip, non-urgent info           |

### Toast Wireframe

```
  Success:
  +-------------------------------------------+
  | ✓  Course saved successfully.       [X]   |
  +-------------------------------------------+

  Error:
  +-------------------------------------------+
  | ✕  Failed to export data.                  |
  |    Please try again.                 [X]  |
  +-------------------------------------------+

  Warning:
  +-------------------------------------------+
  | ⚠  Plugin "ScanTool" is deprecated.       |
  |    Update recommended.              [X]   |
  +-------------------------------------------+

  Info:
  +-------------------------------------------+
  | ℹ  New version available.                  |
  |    Click to update.                 [X]   |
  +-------------------------------------------+
```

### Toast with Action Button

```
+-------------------------------------------+
| ✕  Backup failed.                         |
|    Storage disk is full.                   |
|                            [Retry]  [X]   |
+-------------------------------------------+
```

### Toast with Expand

```
+-------------------------------------------+
| ⚠  3 warnings during scan.                |
|                            [Details ▼][X]  |
+-------------------------------------------+
| > Warning 1: Outdated signature database   |
| > Warning 2: Missing plugin dependency     |
| > Warning 3: Low memory during scan        |
+-------------------------------------------+
```

### Keyboard Focus

- First toast receives focus when it appears (if no other focus target is active).
- Tab cycles through toast action buttons and dismiss button.
- Escape dismisses the focused toast.
- Toasts do not steal focus from form fields or modals.

---

## 3. Persistent Alerts (Banners)

### Behavior

- Displayed as a full-width banner at the top of the content area.
- Stays visible until the user takes action or explicitly dismisses it.
- Can be dismissed with a close button unless it is a critical security alert.
- Supports an action button.

### Variants

| Variant  | Color   | Icon       | Use Case                        |
|----------|---------|------------|---------------------------------|
| Info     | Blue    | ℹ          | System maintenance scheduled    |
| Warning  | Amber   | ⚠          | Plugin needs attention          |
| Error    | Red     | ✕          | System error, service down      |
| Success  | Green   | ✓          | Backup complete, update applied |

### Banner Wireframe

```
  Info Banner:
  +-----------------------------------------------------------+
  | ℹ  System maintenance scheduled for Sunday 2:00 AM EST.   |
  |    Your data will be backed up automatically.      [X]    |
+-----------------------------------------------------------+

  Warning Banner:
  +-----------------------------------------------------------+
  | ⚠  The "Network Scanner" plugin requires an update.       |
  |    [Update Now]                                   [X]     |
+-----------------------------------------------------------+

  Error Banner:
  +-----------------------------------------------------------+
  | ✕  Unable to connect to the diagnostics server.           |
  |    Some features may be unavailable.             [X]     |
+-----------------------------------------------------------+

  Security Banner (cannot be dismissed):
  +-----------------------------------------------------------+
  | 🔴  Security Alert: Unusual login activity detected.      |
  |     Review your recent sessions immediately.              |
  |     [Review Sessions]                                     |
  +-----------------------------------------------------------+
```

---

## 4. Progress Indicators

### For Background Tasks

Display as a persistent toast or inline indicator depending on context.

### Determinate Progress

When the total duration or percentage is known.

```
+-------------------------------------------+
| ⏳  Backing up user data...                |
| [████████████░░░░░░░░] 65%                |
|                          [Cancel]   [X]   |
+-------------------------------------------+
```

### Indeterminate Progress

When duration is unknown.

```
+-------------------------------------------+
| ⏳  Scanning network for vulnerabilities...|
| [████░░░░░░░░░░░░░░░░]                    |
|                          [Cancel]   [X]   |
+-------------------------------------------+
```

### Progress in Notification Center

```
+-----------------------------------------------------------+
|  Running Tasks (2)                                         |
+-----------------------------------------------------------+
|  ⏳  Backup: User Data          [████████░░░░] 65% [Cancel]|
|  ⏳  Network Scan               [░░░░░░░░░░░░] 12% [Cancel]|
+-----------------------------------------------------------+
```

---

## 5. Background Tasks (Notification Center)

### Task Lifecycle

```
  Running → Completed
  Running → Failed
  Running → Cancelled
```

### Completed Task Notification

```
+-----------------------------------------------------------+
|  ✓  Backup: User Data — Completed                          |
|     Duration: 2m 34s | Size: 142 MB                       |
|     Completed at 3:45 PM                                    |
+-----------------------------------------------------------+
```

### Failed Task Notification

```
+-----------------------------------------------------------+
|  ✕  Backup: User Data — Failed                             |
|     Error: Disk full (ENOSPC)                              |
|     Failed at 3:42 PM                                      |
|                            [Retry]  [View Details]         |
+-----------------------------------------------------------+
```

---

## 6. Security Alerts

### Visual Treatment

- Prominent red or orange banner at the top of the application.
- Requires explicit acknowledgment (cannot be auto-dismissed).
- Appears as a modal dialog for critical security events.

### Security Alert Dialog

```
+-----------------------------------------------------------+
|  🔴 Security Alert                                         |
+-----------------------------------------------------------+
|                                                           |
|  Unusual login activity detected on your account.          |
|                                                           |
|  Time: July 19, 2026 at 2:30 AM EST                       |
|  Location: Unknown (VPN detected)                          |
|  IP Address: 198.51.100.42                                 |
|                                                           |
|  If this was you, no action is needed.                     |
|  If you don't recognize this activity, change your         |
|  password immediately.                                     |
|                                                           |
|  +-----------------------+  +---------------------------+  |
|  | Change Password Now   |  | This Was Me               |  |
|  +-----------------------+  +---------------------------+  |
+-----------------------------------------------------------+
```

### Security Alert Banner

```
+-----------------------------------------------------------+
| 🔴 SECURITY: 2 failed login attempts in the last 5 minutes.|
|    Account will be locked after 3 more failures.           |
|    [Review Activity]                                       |
+-----------------------------------------------------------+
```

---

## 7. Accessibility

### ARIA Live Regions

| Notification Type | aria-live Value | Role            |
|-------------------|-----------------|-----------------|
| Info toast        | `polite`        | `status`        |
| Success toast     | `polite`        | `status`        |
| Warning toast     | `assertive`     | `alert`         |
| Error toast       | `assertive`     | `alert`         |
| Security alert    | `assertive`     | `alertdialog`   |
| Progress update   | `polite`        | `status`        |

### Screen Reader Announcements

- Toast: Announce type + message content.
  - Example: "Success: Course saved successfully."
  - Example: "Error: Failed to export data. Please try again."
- Progress: Announce percentage milestones (25%, 50%, 75%, 100%).
- Security: Announce full alert content immediately.

### Focus Management

- New error toasts do NOT steal focus from current interaction.
- Security alert dialogs DO receive focus (modal).
- After dismissing a toast, focus returns to the previous element.
- Notification center dropdown: focus trap when open.

### Keyboard

| Key            | Behavior                                       |
|----------------|-------------------------------------------------|
| Escape         | Dismiss focused toast / close notification center|
| Tab            | Move between toast action buttons               |
| Enter/Space    | Activate toast action or dismiss button         |
| Arrow Up/Down  | Navigate notification center list               |

---

## 8. Backup Notifications

| Event                   | Type     | Priority | Message                                      |
|-------------------------|----------|----------|----------------------------------------------|
| Backup started          | Toast    | Low      | "Backup started: {scope}"                    |
| Backup progress         | Progress | Low      | "Backing up {scope}... {percent}%"           |
| Backup complete         | Toast    | Medium   | "Backup complete: {size} in {duration}"      |
| Backup failed           | Toast    | High     | "Backup failed: {error}. [Retry]"            |
| Restore started         | Toast    | Medium   | "Restore started. Do not close the app."     |
| Restore complete        | Toast    | High     | "Restore complete. App will restart."        |
| Restore failed          | Toast    | Critical | "Restore failed: {error}. Data may be corrupt."|
| Backup scheduled        | Info     | Low      | "Next backup: {date} at {time}"              |

---

## 9. Plugin Notifications

| Event                    | Type     | Priority | Message                                      |
|--------------------------|----------|----------|----------------------------------------------|
| Plugin installed         | Toast    | Medium   | "Plugin '{name}' v{version} installed."      |
| Plugin updated           | Toast    | Low      | "Plugin '{name}' updated to v{version}."     |
| Plugin error             | Toast    | High     | "Plugin '{name}' encountered an error."      |
| Plugin needs attention   | Banner   | Medium   | "Plugin '{name}' requires configuration."    |
| Plugin removed           | Toast    | Low      | "Plugin '{name}' removed."                   |
| Plugin dependency missing| Banner   | High     | "Plugin '{name}' requires '{dependency}'."   |

---

## 10. Diagnostics Notifications

| Event                    | Type     | Priority | Message                                      |
|--------------------------|----------|----------|----------------------------------------------|
| Health check complete    | Toast    | Low      | "Health check complete. {count} issues found."|
| All clear                | Toast    | Low      | "Health check complete. All systems nominal." |
| Issue found              | Banner   | Medium   | "Issue detected: {description}. [View Report]"|
| Critical issue           | Dialog   | Critical | "Critical issue: {description}. Immediate action required."|
| Diagnostic export ready  | Toast    | Low      | "Diagnostic report ready. [Download]"         |

---

## 11. Notification Center

### Trigger

Bell icon in the application header with unread count badge.

```
  Header:
  +-----------------------------------------------------------+
|  AuthShield Lab    [Search...]       🔔 3    [Avatar ▼]   |
+-----------------------------------------------------------+
```

### Badge

- Shows count of unread notifications.
- Maximum display: "99+" for counts above 99.
- Badge color: red for critical, default for others.

### Dropdown Panel

```
+-------------------------------------------+
|  Notifications              [Mark All Read]|
+-------------------------------------------+
|  [All] [Security] [Tasks] [System]        |
+-------------------------------------------+
|                                           |
|  🔴  Security: Unusual login detected     |
|      2 minutes ago              [Review]  |
|  ──────────────────────────────────────── |
|  ✓   Backup complete: 142 MB             |
|      15 minutes ago                       |
|  ──────────────────────────────────────── |
|  ⏳  Network scan: 65% complete           |
|      Running...                   [Cancel]|
|  ──────────────────────────────────────── |
|  ℹ   Update available: v3.2.0            |
|      1 hour ago                [Update]   |
|                                           |
+-------------------------------------------+
|  [View All Notifications]                 |
+-------------------------------------------+
```

### Tabs

| Tab        | Shows                                                        |
|------------|--------------------------------------------------------------|
| All        | All notifications                                            |
| Security   | Security alerts, login activity, permission changes          |
| Tasks      | Running/completed/failed background tasks                    |
| System     | Updates, maintenance, diagnostics, plugin events             |

### Actions

| Action              | Behavior                                            |
|---------------------|-----------------------------------------------------|
| Mark All Read       | Clears unread badge, marks all as read               |
| Clear All           | Removes all notifications from the list              |
| View All            | Opens full notification history page                 |
| Dismiss (per item)  | Removes individual notification                      |
| Action button       | Invokes the associated action (retry, update, etc.)  |

---

## 12. Priority Levels

| Priority  | Display                                  | Auto-Dismiss | Acknowledgment |
|-----------|------------------------------------------|--------------|----------------|
| Low       | Toast only                               | Yes (5s)     | No             |
| Medium    | Toast + Notification Center              | Yes (5s)     | No             |
| High      | Banner (persistent) + Notification Center| No           | Optional       |
| Critical  | Dialog (modal) + Banner + Notification Ctr| No          | Required       |

### Priority Routing

```
  Priority → Notification Channels:
  ┌──────────┬───────┬──────────┬────────┬────────┐
  │ Priority │ Toast │ Banner   │ Center │ Dialog │
  ├──────────┼───────┼──────────┼────────┼────────┤
  │ Low      │  ✓    │          │   ✓    │        │
  │ Medium   │  ✓    │          │   ✓    │        │
  │ High     │       │  ✓       │   ✓    │        │
  │ Critical │       │  ✓       │   ✓    │  ✓     │
  └──────────┴───────┴──────────┴────────┴────────┘
```

---

## 13. Notification Positioning & Stacking

### Toast Stack (Top-Right)

```
  +-- Screen -----------------------------------------+
  |                                        +----------+|
  |                                        | Toast 3  ||
  |                                        +----------+|
  |                                        +----------+|
  |                                        | Toast 2  ||
  |                                        +----------+|
  |                                        +----------+|
  |                                        | Toast 1  ||
  |                                        +----------+|
  |                                                    |
  +----------------------------------------------------+
```

- Newest toast appears at the top.
- Maximum 3 visible; others queued.
- When a toast dismisses, the next queued toast slides in.
- Gap between toasts: 8px.

### Banner Position

Banners appear below the header and above the main content area.

```
  +-----------------------------------------------------------+
  |  Header (AuthShield Lab, Search, Notifications)           |
+-----------------------------------------------------------+
|  Banner / Persistent Alert                                 |
+-----------------------------------------------------------+
|  Main Content                                              |
|                                                           |
|                                                           |
+-----------------------------------------------------------+
```

---

## 14. Notification State Management (Zustand)

```typescript
interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  timestamp: number;
  read: boolean;
  dismissed: boolean;
  action?: { label: string; onClick: () => void };
  progress?: number; // 0-100 for progress notifications
}

interface NotificationStore {
  notifications: Notification[];
  add(notification: Omit<Notification, 'id' | 'timestamp' | 'read' | 'dismissed'>): void;
  dismiss(id: string): void;
  markRead(id: string): void;
  markAllRead(): void;
  clearAll(): void;
  getUnreadCount(): number;
}
```

---

## 15. Auto-Dismiss Timing

| Notification Type             | Duration  | Pause on Hover |
|-------------------------------|-----------|----------------|
| Success toast                 | 5 seconds | Yes            |
| Info toast                    | 5 seconds | Yes            |
| Warning toast                 | 8 seconds | Yes            |
| Error toast                   | 8 seconds | Yes            |
| Security alert (banner)       | No auto   | N/A            |
| Progress toast                | No auto   | N/A            |
| Critical dialog               | No auto   | N/A            |

---

*Last updated: 2026-07-19 — AuthShield Lab UI Standards*
