# AuthShield Lab — Form Standards

> Form design, validation, layout, and interaction standards for all AuthShield Lab forms.

---

## 1. Form Layout

### Single-Column (Preferred)

Default layout for most forms. Optimizes vertical scanning and reduces cognitive load.

```
+--------------------------------------------------+
|  Form Title                                       |
|  Form description or helper text                  |
+--------------------------------------------------+
|  Label                                            |
|  +--------------------------------------------+  |
|  | input                                      |  |
|  +--------------------------------------------+  |
|  Help text here                                  |
|                                                  |
|  Label                                            |
|  +--------------------------------------------+  |
|  | input                                      |  |
|  +--------------------------------------------+  |
|  Help text here                                  |
|                                                  |
|  Label                                            |
|  +--------------------------------------------+  |
|  | input                                      |  |
|  +--------------------------------------------+  |
|                                                  |
|  +--------+  +-----------+                       |
|  | Cancel |  | Save Form |                       |
|  +--------+  +-----------+                       |
+--------------------------------------------------+
```

### Two-Column (Wide Screens ≥1024px)

Use for forms with many fields where horizontal space is available. Pair related fields.

```
+-----------------------------------------------------------+
|  Form Title                                                |
|  Form description                                          |
+-----------------------------------------------------------+
|  First Name           |  Last Name                         |
|  +-----------------+  |  +-----------------+               |
|  |                 |  |  |                 |               |
|  +-----------------+  |  +-----------------+               |
|                        |                                    |
|  Email Address                                    |
|  +----------------------------------------------+         |
|  |                                              |         |
|  +----------------------------------------------+         |
|                                                           |
|  +--------+  +-----------+                               |
|  | Cancel |  | Save Form |                               |
|  +--------+  +-----------+                               |
+-----------------------------------------------------------+
```

### Horizontal (Inline Forms)

Use for search bars, filter rows, or single-purpose inline actions. Label left of input.

```
+-----------------------------------------------------------+
|  Search: [________________________]  [Search]              |
+-----------------------------------------------------------+
```

### Stacked Sectioned Form

For long forms, group fields into named sections with dividers.

```
+-----------------------------------------------------------+
|  Form Title                                                |
|  +-------------------------------------------------------+|
|  |  Section: Basic Info                                   ||
|  |                                                        ||
|  |  Label            Label                                ||
|  |  [________]       [________]                           ||
|  |                                                        ||
|  |  Label                                            ||
|  |  [________________________________________]           ||
|  +-------------------------------------------------------+|
|  |  Section: Advanced Settings                            ||
|  |                                                        ||
|  |  Label            Label                                ||
|  |  [________]       [________]                           ||
|  +-------------------------------------------------------+|
|                                                          |
|  +--------+  +-----------+                               |
|  | Cancel |  | Save Form |                               |
|  +--------+  +-----------+                               |
+-----------------------------------------------------------+
```

---

## 2. Field Layout

### Label Above Input (Preferred)

Best for most forms. Clear visual hierarchy, mobile-friendly.

```
First Name *
+--------------------------------------------+
| John                                       |
+--------------------------------------------+
```

### Label Left of Input (Compact)

Use for dense forms, settings pages, or when vertical space is limited.

```
First Name *  [ John                            ]
```

### Floating Label

Label floats above on focus or when filled. Not recommended for accessibility-first design; use only when space is extremely constrained.

```
+--------------------------------------------+
| First Name                                 |
| John                                       |
+--------------------------------------------+
```

---

## 3. Required Fields

- Mark required fields with an asterisk `*` adjacent to the label text.
- Include a screen-reader-only (sr-only) text: `<span class="sr-only">(required)</span>`
- Do not rely on color alone to indicate required status.
- Place a note at the top of the form: "* Required fields"

```
+-----------------------------------------------------------+
|  * Required fields                                         |
|                                                           |
|  First Name *                                             |
|  +----------------------------------------------+        |
|  |                                              |        |
|  +----------------------------------------------+        |
|  Help text (optional)                                    |
+-----------------------------------------------------------+
```

---

## 4. Validation

### Timing

| Trigger             | Behavior                                           |
|---------------------|----------------------------------------------------|
| On blur             | Validate field, show inline error if invalid       |
| On submit           | Validate all fields, focus first error             |
| On change (debounced)| Optional: validate after 300ms idle for password strength |
| On mount            | Do NOT show errors on initial render               |

### Inline Error Display

```
Email Address *
+----------------------------------------------+
| invalid-email                                |
+----------------------------------------------+
! Please enter a valid email address           |
  (e.g., user@example.com)                     |
```

### Error Icon + Message

All error messages include an icon (⚠) for visual identification, plus text content.

```
Email Address *
+----------------------------------------------+
| invalid-email                                |
+----------------------------------------------+
! Please enter a valid email address           |
```

### Red Border on Invalid Fields

- Invalid fields: `border-color: var(--color-error)` (red)
- Valid fields on blur: `border-color: var(--color-success)` (green) — optional
- Focus ring: `box-shadow: 0 0 0 3px var(--color-focus-ring)`

---

## 5. Error Messages

### Guidelines

- Write in plain language, no jargon.
- Be specific about what is wrong and how to fix it.
- Never say "Invalid input" — say exactly what is invalid.
- Lead with the problem, not the field name.

### Examples

| Bad Message                     | Good Message                                           |
|---------------------------------|--------------------------------------------------------|
| Invalid input                   | Password must be at least 8 characters                 |
| Error                           | Please enter a valid email address                     |
| Required                        | This field is required                                 |
| Too short                       | Username must be between 3 and 30 characters           |
| Invalid format                  | Phone number must be in the format (555) 123-4567      |
| Passwords do not match          | Passwords must match                                   |
| File too large                  | File must be smaller than 10 MB                        |
| Invalid file type               | Please upload a .png, .jpg, or .webp file              |

### Error Summary (Top of Form)

For forms with multiple errors, show an error summary at the top on submit.

```
+-----------------------------------------------------------+
|  ! Please fix the following errors:                        |
|                                                           |
|  - First Name is required                                  |
|  - Email must be a valid email address                     |
|  - Password must be at least 8 characters                  |
+-----------------------------------------------------------+
```

Each item in the summary is a link that focuses the corresponding field.

---

## 6. Input Masks

Apply input masks for structured data entry. Use a library like `react-imask`.

| Field Type   | Mask Pattern         | Example              |
|--------------|----------------------|----------------------|
| Phone (US)   | (555) 123-4567      | (555) 123-4567       |
| Date         | MM/DD/YYYY           | 07/19/2026           |
| Time         | HH:MM                | 14:30                |
| SSN          | XXX-XX-XXXX         | 123-45-6789          |
| ZIP Code     | XXXXX or XXXXX-XXXX | 12345 or 12345-6789  |
| IP Address   | XXX.XXX.XXX.XXX     | 192.168.1.1          |

---

## 7. Autocomplete

Use the HTML `autocomplete` attribute on every relevant field to support password managers and browser autofill.

```html
<input autocomplete="name" />
<input autocomplete="email" />
<input autocomplete="tel" />
<input autocomplete="current-password" />
<input autocomplete="new-password" />
<input autocomplete="one-time-code" />
```

---

## 8. Keyboard Navigation

| Key              | Behavior                                      |
|------------------|-----------------------------------------------|
| Tab              | Move to next field                            |
| Shift+Tab        | Move to previous field                        |
| Enter            | Submit single-field form (search, inline)     |
| Arrow Down/Up    | Navigate options in dropdowns/comboboxes      |
| Escape           | Close dropdown, dismiss tooltip               |
| Space            | Toggle checkbox, open dropdown                |

---

## 9. Accessibility

Every input must have:

1. An associated `<label>` with matching `htmlFor`/`id`.
2. `aria-describedby` pointing to help text when present.
3. `aria-invalid="true"` when validation fails.
4. `aria-required="true"` for required fields.
5. `aria-errormessage` pointing to the error message element.

```html
<label for="email">Email Address <span class="sr-only">(required)</span></label>
<input
  id="email"
  type="email"
  autocomplete="email"
  aria-required="true"
  aria-describedby="email-help"
  aria-invalid="false"
/>
<span id="email-help">We'll never share your email.</span>
<span id="email-error" role="alert" aria-live="assertive"></span>
```

---

## 10. Form States

| State      | Visual Treatment                                  |
|------------|---------------------------------------------------|
| Pristine   | All fields at initial values, no validation shown |
| Dirty      | At least one field changed from initial value     |
| Submitting | Submit button shows spinner, all fields disabled  |
| Success    | Success message, form may reset or redirect       |
| Error      | Error summary at top, first error field focused   |
| Disabled   | All fields greyed out, `disabled` attribute set   |

```
Submitting State:
+-----------------------------------------------------------+
|  Form Title                                                |
|  +-------------------------------------------------------+|
|  |  [Saving...]                                          ||
|  +-------------------------------------------------------+|
|                                                           |
|  First Name                                               |
|  +----------------------------------------------+        |
|  | John (disabled)                              |        |
|  +----------------------------------------------+        |
|                                                           |
|  [ Cancel ]  [ Saving... ]  ← disabled, spinner          |
+-----------------------------------------------------------+
```

---

## 11. Button Placement

```
+-----------------------------------------------------------+
|                                                           |
|  [ Cancel ]              [ Reset ]            [ Save ]    |
|  secondary              secondary            primary      |
|  (left)                 (center, optional)   (right)      |
+-----------------------------------------------------------+
```

- **Primary action** (Save, Submit): rightmost, styled as primary button.
- **Secondary action** (Cancel): leftmost, styled as secondary/outline.
- **Danger action** (Delete): separate row or visually isolated (red style).
- **Reset**: optional, between cancel and save, secondary style.

---

## 12. Error Recovery

- Clear inline errors when the user re-focuses the field.
- Provide a "Reset form" link in the form footer.
- Support `Ctrl+Z` / `Cmd+Z` to undo the last field change.
- Show an undo toast after a successful save for 5 seconds.

---

## 13. Autosave

For long or critical forms (settings, profile):

- Save draft every 30 seconds or on field blur.
- Show status indicator: `Saving...` → `Saved at 2:30 PM`
- On conflict (e.g., another session edited the same data), show a conflict resolution dialog.

```
+-------------------------------------------+
| Profile                         Saved at 2:30 PM |
+-------------------------------------------+
```

---

## 14. Localization

- Use flexible container widths to accommodate translated label lengths.
- Date pickers must respect the user's locale (`Intl.DateTimeFormat`).
- Number inputs must respect locale-specific separators.
- Right-to-left (RTL) support: mirror layout for RTL locales.
- All user-visible strings must be translatable (use i18n keys, never hardcode).

---

## 15. Form Examples

### User Profile Form

```
+-----------------------------------------------------------+
|  User Profile                                              |
|  Manage your personal information and preferences.         |
+-----------------------------------------------------------+
|  * Required fields                                         |
|                                                           |
|  First Name *          Last Name *                         |
|  +-----------------+   +-----------------+                 |
|  |                 |   |                 |                 |
|  +-----------------+   +-----------------+                 |
|                                                           |
|  Email Address *                                          |
|  +----------------------------------------------+        |
|  |                                              |        |
|  +----------------------------------------------+        |
|  Used for notifications and login.                       |
|                                                           |
|  Phone Number                                             |
|  +----------------------------------------------+        |
|  | (555) 123-____                               |        |
|  +----------------------------------------------+        |
|  Optional. Used for two-factor authentication.            |
|                                                           |
|  Role                                                     |
|  +----------------------------------------------+  v     |
|  | Select a role...                             |        |
|  +----------------------------------------------+        |
|                                                           |
|  Preferences                                              |
|  [x] Receive email notifications                          |
|  [ ] Receive SMS notifications                            |
|  [x] Enable dark mode                                     |
|                                                           |
|  +--------+  +--------+  +-----------+                    |
|  | Cancel |  | Reset  |  | Save      |                    |
|  +--------+  +--------+  +-----------+                    |
+-----------------------------------------------------------+
```

### Course Creation Form

```
+-----------------------------------------------------------+
|  Create New Course                                         |
|  Build a cybersecurity training module.                    |
+-----------------------------------------------------------+
|                                                           |
|  Section: Content                                         |
|  +-------------------------------------------------------+|
|  |                                                        ||
|  |  Course Title *                                        ||
|  |  +----------------------------------------------+    ||
|  |  |                                              |    ||
|  |  +----------------------------------------------+    ||
|  |  3-100 characters                                  ||
|  |                                                        ||
|  |  Description *                                        ||
|  |  +----------------------------------------------+    ||
|  |  |                                              |    ||
|  |  |                                              |    ||
|  |  |                                              |    ||
|  |  +----------------------------------------------+    ||
|  |  Brief description of the course content.             ||
|  +-------------------------------------------------------+|
|                                                           |
|  Section: Modules                                         |
|  +-------------------------------------------------------+|
|  |  Module 1: [________________]  [Remove]               ||
|  |  Module 2: [________________]  [Remove]               ||
|  |  Module 3: [________________]  [Remove]               ||
|  |  [+ Add Module]                                       ||
|  +-------------------------------------------------------+|
|                                                           |
|  Section: Settings                                        |
|  +-------------------------------------------------------+|
|  |  Difficulty:  (o) Beginner  ( ) Intermediate  ( ) Adv||
|  |  Duration:    [____] hours                             ||
|  |  Max Students: [____]                                  ||
|  +-------------------------------------------------------+|
|                                                           |
|  Section: Publish                                         |
|  +-------------------------------------------------------+|
|  |  Status: (o) Draft  ( ) Published  ( ) Archived       ||
|  |  [x] Allow enrollment before start date                ||
|  +-------------------------------------------------------+|
|                                                           |
|  +--------+  +-----------+  +---------------+             |
|  | Cancel |  | Save Draft|  | Publish Course|             |
|  +--------+  +-----------+  +---------------+             |
+-----------------------------------------------------------+
```

### Assessment Creation Form

```
+-----------------------------------------------------------+
|  Create Assessment                                         |
|  Design a quiz or exam for your course.                    |
+-----------------------------------------------------------+
|                                                           |
|  Assessment Title *                                       |
|  +----------------------------------------------+        |
|  |                                              |        |
|  +----------------------------------------------+        |
|                                                           |
|  Time Limit *           Passing Score *                   |
|  +-----------------+    +-----------------+               |
|  | 30 min          |    | 70 %            |               |
|  +-----------------+    +-----------------+               |
|  Minutes (0 = no limit)   Percentage (0-100)              |
|                                                           |
|  Questions                                                |
|  +-------------------------------------------------------+|
|  |  Q1: [________________________________]  [x] Remove   ||
|  |  Type: [Multiple Choice v]  Points: [5]                ||
|  |  A) [________________]  [x]                            ||
|  |  B) [________________]  [x]                            ||
|  |  C) [________________]  [x]                            ||
|  |  D) [________________]  [x]  Correct: [ ]              ||
|  |  [+ Add Option]                                        ||
|  +-------------------------------------------------------+|
|  |  [+ Add Question]                                      ||
|  +-------------------------------------------------------+|
|                                                           |
|  +--------+  +-----------+                                |
|  | Cancel |  | Save      |                                |
|  +--------+  +-----------+                                |
+-----------------------------------------------------------+
```

### Plugin Installation Form

```
+-----------------------------------------------------------+
|  Install Plugin                                            |
|  Review and install a new plugin for AuthShield Lab.       |
+-----------------------------------------------------------+
|                                                           |
|  Plugin: AuthShield Security Scanner v2.1.0                |
|  Author: AuthShield Labs                                  |
|  Rating: ***** (124 reviews)                              |
|                                                           |
|  Description                                               |
|  +-------------------------------------------------------+|
|  |  Automated vulnerability scanning and reporting for    ||
|  |  network infrastructure. Supports CVE database lookups.||
|  +-------------------------------------------------------+|
|                                                           |
|  Permissions Required                                      |
|  +-------------------------------------------------------+|
|  |  [x] Read network configuration                        ||
|  |  [x] Execute diagnostic scans                           ||
|  |  [ ] Access external APIs                               ||
|  |  [ ] Write to system logs                               ||
|  +-------------------------------------------------------+|
|                                                           |
|  I understand the permissions this plugin requires.        |
|  [x] I have reviewed and accept these permissions.         |
|                                                           |
|  +--------+  +-------------------+                         |
|  | Cancel |  | Install Plugin    |                         |
|  +--------+  +-------------------+                         |
+-----------------------------------------------------------+
```

### Backup Configuration Form

```
+-----------------------------------------------------------+
|  Backup Configuration                                      |
|  Set up automatic backups for your data.                   |
+-----------------------------------------------------------+
|                                                           |
|  Backup Scope                                              |
|  [x] User data and profiles                               |
|  [x] Course content and assessments                        |
|  [ ] Plugin configurations                                 |
|  [x] Application settings                                  |
|                                                           |
|  Schedule                                                  |
|  Frequency: [Daily v]  Time: [02:00]                       |
|  Retention: [30] days                                      |
|                                                           |
|  Encryption                                                |
|  [x] Enable encryption                                     |
|  Encryption: [AES-256 v]                                   |
|                                                           |
|  Storage Location                                          |
|  (o) Local directory                                       |
|      Path: [/home/anya/backups________]                    |
|  ( ) Remote server                                         |
|      Host: [________________]  Port: [22]                  |
|                                                           |
|  +--------+  +-----------+                                 |
|  | Cancel |  | Save      |                                 |
|  +--------+  +-----------+                                 |
+-----------------------------------------------------------+
```

### Settings Forms

```
+-----------------------------------------------------------+
|  Settings                    [General] [Appearance] [A11y] |
|                          [Security] [Notifications] [Data] |
+-----------------------------------------------------------+
|                                                           |
|  General Settings                                          |
|  +-------------------------------------------------------+|
|  |  Application Language: [English (US) v]                 ||
|  |  Timezone:             [UTC-5 (Eastern) v]              ||
|  |  Date Format:          [MM/DD/YYYY v]                   ||
|  |  [x] Launch at startup                                  ||
|  |  [ ] Check for updates automatically                    ||
|  +-------------------------------------------------------+|
|                                                           |
|  Accessibility Settings                                    |
|  +-------------------------------------------------------+|
|  |  Font Size:   [Normal v]  (Small, Normal, Large, XL)   ||
|  |  Contrast:    [Normal v]  (Normal, High)                ||
|  |  Reduce Motion:  [x]                                    ||
|  |  Screen Reader Optimized: [x]                           ||
|  |  Keyboard Navigation Mode: [x]                          ||
|  +-------------------------------------------------------+|
|                                                           |
|  +--------+  +-----------+                                 |
|  | Reset  |  | Save      |                                 |
|  +--------+  +-----------+                                 |
+-----------------------------------------------------------+
```

---

## 16. Button Styles Reference

| Button Type  | Style                      | Usage                          |
|--------------|----------------------------|--------------------------------|
| Primary      | Filled, brand color       | Save, Submit, Confirm          |
| Secondary    | Outlined, neutral         | Cancel, Go Back                |
| Danger       | Filled, red               | Delete, Remove, Revoke         |
| Ghost        | No border, text only      | Inline actions, Less prominent |
| Icon         | Square, icon only         | Close, Expand, Collapse        |

---

*Last updated: 2026-07-19 — AuthShield Lab UI Standards*
