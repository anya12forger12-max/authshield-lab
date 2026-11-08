# AuthShield Lab — Workflow Engineering

## 1. Overview

This document defines the complete workflow system for AuthShield Lab. It covers
task flows from simple single-step actions to complex multi-step wizards, including
undo/redo, autosave, offline recovery, and background task management.

---

## 2. Simple Tasks

Single-step actions that complete immediately with feedback.

### 2.1 Save Settings

```
User changes setting → Setting auto-saves (debounced 500ms)
  → Visual indicator: "Saved" toast (auto-dismiss 3s)
  → If save fails: Error toast with "Retry" action
```

| Property | Value |
|---|---|
| Trigger | Value change in settings form |
| Feedback | "Saved" toast |
| Duration | < 100ms |
| Reversible | Yes (change setting back) |

### 2.2 Delete Item

```
User clicks delete → Confirmation dialog
  → User confirms → Item removed → Undo toast (5s, reversible)
  → User cancels → Dialog closes
```

| Property | Value |
|---|---|
| Trigger | Delete button on item |
| Feedback | Confirmation dialog, then undo toast |
| Duration | < 200ms |
| Reversible | Yes (via undo for 5 seconds) |

### 2.3 Toggle Switch

```
User toggles switch → Value updates immediately → Visual feedback
  → If requires save: "Save" button appears
  → If auto-saves: "Saved" toast
```

| Property | Value |
|---|---|
| Trigger | Toggle switch interaction |
| Feedback | Visual state change, optional toast |
| Duration | Instant |
| Reversible | Yes (toggle back) |

### 2.4 Star/Favorite

```
User clicks star → Star fills → "Added to Favorites" toast
  → User clicks again → Star empties → "Removed from Favorites" toast
```

| Property | Value |
|---|---|
| Trigger | Star icon click or Alt+S |
| Feedback | Visual state change, toast |
| Duration | Instant |
| Reversible | Yes (toggle) |

### 2.5 Mark as Read (Notification)

```
User clicks notification → Notification marked read → Badge count decrements
  → If in notification panel: Item dims
  → If on bell icon: Badge updates
```

| Property | Value |
|---|---|
| Trigger | Click or keyboard shortcut |
| Feedback | Visual state change, badge update |
| Duration | Instant |
| Reversible | Yes (mark as unread) |

---

## 3. Advanced Tasks (Multi-Step Wizards)

### 3.1 Create Course Wizard

**Total Steps:** 5
**Estimated Time:** 10-20 minutes

```
Step 1: Basic Information
  → Course title (required)
  → Description (required, rich text)
  → Category (dropdown, required)
  → Difficulty level (radio, required)
  → Tags (multi-select, optional)
  → Thumbnail upload (optional)
  → Validation: Title min 5 chars, description min 20 chars

Step 2: Modules & Structure
  → Add modules (reorderable list)
  → Module title (required)
  → Module description (optional)
  → Drag to reorder
  → Minimum 1 module required
  → Validation: Each module needs title

Step 3: Lessons
  → Add lessons to each module
  → Lesson title (required)
  → Lesson type: Text / Video / Interactive / Quiz
  → Content editor (per type)
  → Drag to reorder within module
  → Validation: Each lesson needs title and content

Step 4: Assessments
  → Add end-of-module assessments (optional)
  → Add final assessment (optional)
  → Question editor
  → Passing score configuration
  → Time limit configuration
  → Validation: Assessments need questions

Step 5: Review & Publish
  → Course summary display
  → Preview button (opens preview mode)
  → Publish status: Draft / Published / Scheduled
  → Schedule date/time (if scheduled)
  → Estimated completion time (auto-calculated)
  → Prerequisites (optional, link to other courses)
  → "Save as Draft" / "Publish Now" / "Schedule"
```

#### Wizard UI Pattern

```
┌─────────────────────────────────────────────────┐
│  Create Course                                   │
│                                                  │
│  ● Step 1  ○ Step 2  ○ Step 3  ○ Step 4  ○ Step 5 │
│  ───────────────────────────────────────────────│
│                                                  │
│  [Form Content Area]                             │
│                                                  │
│  ───────────────────────────────────────────────│
│  [Back]                          [Next] [Save Draft] │
└─────────────────────────────────────────────────┘
```

#### Step Indicator Rules

- Current step: Filled circle, bold label
- Completed steps: Checkmark icon, clickable to go back
- Upcoming steps: Empty circle, gray label
- Click any completed step to jump back
- Cannot skip to future steps (unless saving draft)
- Progress percentage shown (e.g., "Step 2 of 5 — 40%")

### 3.2 Create Assessment Wizard

**Total Steps:** 4
**Estimated Time:** 15-30 minutes

```
Step 1: Assessment Setup
  → Title (required)
  → Description (required)
  → Type: Quiz / Exam / Practical / Mixed
  → Time limit (minutes, optional)
  → Maximum attempts (number, optional)
  → Passing score (percentage, required)
  → Linked course (optional dropdown)

Step 2: Questions
  → Add questions (one at a time or bulk)
  → Question types:
    - Multiple Choice (2-6 options)
    - True/False
    - Multiple Select (checkboxes)
    - Short Answer
    - Code Entry
    - Drag and Drop
  → Each question:
    - Question text (required)
    - Answer options (required)
    - Correct answer (required)
    - Explanation (optional, shown in review)
    - Points value (default 1)
  → Reorder questions via drag-and-drop
  → Import questions from CSV (optional)

Step 3: Configuration
  → Shuffle question order (toggle)
  → Shuffle answer order (toggle)
  → Show feedback after each question (toggle)
  → Show correct answers in review (toggle)
  → Allow flagging questions (toggle)
  → Proctoring settings (if available)
  → Accessibility accommodations

Step 4: Review & Publish
  → Question count and total points
  → Time estimate
  → Preview mode
  → Publish status
  → "Save as Draft" / "Publish" / "Schedule"
```

### 3.3 Bulk Operations Wizard

**Total Steps:** 3

```
Step 1: Select Items
  → Display items in table with checkboxes
  → Select All / Deselect All buttons
  → Selected count display
  → Filters to narrow selection

Step 2: Choose Action
  → Available actions based on item type:
    - Users: Assign role, deactivate, move to org, export
    - Courses: Publish, unpublish, archive, delete
    - Assessments: Enable, disable, duplicate, delete
  → Action-specific options form
  → Preview of affected items

Step 3: Confirm & Execute
  → Summary of action and affected items
  → "Confirm" button
  → Progress indicator during execution
  → Results summary (successes and failures)
  → "Export Results" option
```

---

## 4. Progressive Disclosure

Show essential information first; reveal details on demand.

### 4.1 Pattern: Expandable Sections

```
┌──────────────────────────────────────┐
│  Course Settings              [▼]    │
│  ─────────────────────────────────── │
│  Title: [Cybersecurity Fundamentals] │
│  Category: [Network Security    ▼]  │
│                                       │
│  ▶ Advanced Settings                  │
│  ─────────────────────────────────── │
│  (collapsed — click to expand)       │
└──────────────────────────────────────┘
```

### 4.2 Pattern: Inline Expand

```
┌──────────────────────────────────────┐
│  User: john.doe@example.com          │
│  Role: Student                       │
│  Status: Active                      │
│                                       │
│  ▶ Show more details                  │
│  ─────────────────────────────────── │
│  (clicks to expand)                  │
│  Organization: Cyber Academy         │
│  Last login: 2026-07-18              │
│  Courses enrolled: 5                 │
│  Completion rate: 78%                │
└──────────────────────────────────────┘
```

### 4.3 Pattern: Progressive Form Fields

```
Initial view: Essential fields only
  → User fills required fields
  → "Show Advanced Options" link appears

Expanded view: Advanced fields revealed
  → Additional configuration options
  → Tooltips on each field
  → "Hide Advanced Options" link
```

### 4.4 Rules

- Always show essential information without expansion
- Expansion state persists per session (not per page load)
- Keyboard: Enter or Space to toggle expansion
- Screen reader: expanded/collapsed state announced
- Animation: Smooth height transition (200ms, respects prefers-reduced-motion)
- Maximum expansion depth: 2 levels

---

## 5. Undo/Redo System

### 5.1 Undo Stack

```
Action Stack (LIFO):
  [1] Create Course "NetSec 101"
  [2] Add Module "Introduction"
  [3] Add Lesson "What is Networking?"
  [4] Delete Lesson "What is Networking?"    ← Current
  [5] Add Lesson "OSI Model"
```

### 5.2 Undo Toast

```
┌─────────────────────────────────────────────────┐
│  Lesson deleted.                    [Undo] [✕]  │
└─────────────────────────────────────────────────┘
```

| Property | Value |
|---|---|
| Duration | 5 seconds (auto-dismiss) |
| Action | Click "Undo" to reverse |
| Keyboard | Ctrl+Z to undo, Escape to dismiss toast |
| Position | Bottom-center of screen |
| Stacking | Latest toast replaces previous |

### 5.3 Undo Rules

- **Reversible actions**: Create, delete, move, toggle, text edit
- **Irreversible actions**: Submit assessment, publish course, send notification
- **Batch undo**: Bulk operations undo as single action
- **Maximum stack**: 50 actions
- **Session scope**: Stack clears on application restart
- **Cross-module**: Undo works across modules within session

### 5.4 Confirmation for Irreversible Actions

```
┌─────────────────────────────────────────────┐
│  ⚠️ Confirm Irreversible Action              │
│                                              │
│  You are about to publish this course.       │
│  This will make it visible to all students.  │
│                                              │
│  This action cannot be undone.               │
│                                              │
│         [Cancel]              [Publish]      │
└─────────────────────────────────────────────┘
```

### 5.5 Redo

- Ctrl+Shift+Z or Ctrl+Y to redo
- Redo stack maintained until new action clears it
- Redo toast: "Redo: [action description]" with Redo button

---

## 6. Autosave System

### 6.1 Trigger Conditions

| Trigger | Delay | Description |
|---|---|---|
| Content change | 30 seconds | Periodic autosave after changes |
| Field blur | Immediate | Save when leaving a field |
| Tab switch | Immediate | Save before switching tabs |
| Navigation | Immediate | Save before navigating away |
| Window blur | Immediate | Save when window loses focus |
| Before unload | Immediate | Final save attempt |

### 6.2 Autosave Indicator

```
┌─────────────────────────────────────────────┐
│  Assessment Workspace                        │
│                                              │
│  [Content Area]                              │
│                                              │
│  ───────────────────────────────────────────│
│  ● Auto-saved at 14:32:05          [Save Now]│
└─────────────────────────────────────────────┘
```

| State | Indicator | Color |
|---|---|---|
| Saved | ● Auto-saved at [time] | Green |
| Saving | ● Saving... | Amber (animated) |
| Unsaved changes | ● Unsaved changes | Red |
| Save failed | ● Save failed [Retry] | Red |

### 6.3 Conflict Detection

```
Scenario: User A and User B edit same item

User A saves → Success
User B saves → Conflict detected

┌─────────────────────────────────────────────┐
│  ⚠️ Save Conflict                            │
│                                              │
│  This item was modified by another user      │
│  since you started editing.                  │
│                                              │
│  Their changes: [View diff]                  │
│  Your changes:  [View diff]                  │
│                                              │
│  [Keep Mine] [Keep Theirs] [Merge]           │
└─────────────────────────────────────────────┘
```

### 6.4 Autosave Scope

| Content | Autosave | Notes |
|---|---|---|
| Assessment answers | Every 30s | Critical, high frequency |
| Notes | Every 30s | Per-lesson notes |
| Form inputs | On blur | Settings forms |
| Course draft | Every 30s | Draft courses |
| Simulation state | On checkpoint | Simulation progress |

---

## 7. Offline Recovery System

### 7.1 Operation Queue

```
When offline:
  User action → Operation queued → "Queued" indicator
  → Connection restored → Queue processes → Success toast
  → If conflict: Conflict dialog
```

### 7.2 Queue Display

```
┌─────────────────────────────────────────────┐
│  📡 Offline Mode — 3 operations queued       │
│  ───────────────────────────────────────────│
│  1. Save assessment answers      [Pending]   │
│  2. Enroll in "NetSec 101"      [Pending]   │
│  3. Upload avatar                [Pending]   │
│  ───────────────────────────────────────────│
│  [View Queue]                    [Retry All] │
└─────────────────────────────────────────────┘
```

### 7.3 Sync Indicator

| State | Indicator | Position |
|---|---|---|
| Online, synced | ● Online | Header, green |
| Online, syncing | ● Syncing... | Header, amber |
| Offline | ● Offline | Header, red |
| Offline, queued | ● Offline (N queued) | Header, red with count |

### 7.4 Retry Logic

- **Automatic retry**: 3 attempts with exponential backoff (1s, 4s, 16s)
- **Manual retry**: "Retry All" button in queue panel
- **Failed operations**: Moved to "Failed" tab with error details
- **Maximum queue**: 100 operations
- **Queue persistence**: Stored in IndexedDB, survives app restart

---

## 8. Background Tasks System

### 8.1 Task Types

| Task | Duration | Cancellable | Priority |
|---|---|---|---|
| Report generation | 5-30s | Yes | Normal |
| Export to PDF | 3-15s | Yes | Normal |
| Database backup | 10-60s | Yes | High |
| Plugin installation | 5-30s | Yes | Normal |
| Bulk operations | Variable | Yes | Normal |
| Search indexing | 2-10s | No | Low |
| Course import | 10-60s | Yes | Normal |

### 8.2 Progress Indicator

```
┌─────────────────────────────────────────────┐
│  Background Tasks (2 active)                 │
│  ───────────────────────────────────────────│
│  📊 Generating report...                     │
│  ████████████░░░░░░░░  60%  [Cancel]        │
│                                              │
│  📥 Exporting to PDF...                      │
│  ████░░░░░░░░░░░░░░░░  20%  [Cancel]        │
└─────────────────────────────────────────────┘
```

### 8.3 Task States

| State | Description | User Action |
|---|---|---|
| Queued | Waiting to start | Cancel, reorder |
| Running | In progress | Cancel, view details |
| Paused | Temporarily stopped | Resume, cancel |
| Completed | Finished successfully | View result, dismiss |
| Failed | Error occurred | Retry, view error, dismiss |
| Cancelled | User cancelled | Dismiss |

### 8.4 Notification on Completion

```
Toast (auto-dismiss 5s):
  ✅ Report "Q3 Analysis" generated successfully.  [View]

Toast (auto-dismiss, persists for errors):
  ❌ PDF export failed.  [Retry] [View Error]
```

---

## 9. Task Queue Panel

### 9.1 Access

- Click task indicator in header
- Keyboard: Alt+T to open
- Automatically opens when tasks are active

### 9.2 Panel Layout

```
┌─────────────────────────────────────────────┐
│  Task Queue                    [Clear Done]  │
│  ───────────────────────────────────────────│
│  Active (2)                                  │
│  ├── 📊 Report: Q3 Analysis     60% [Cancel]│
│  └── 📥 PDF Export               20% [Cancel]│
│                                              │
│  Completed (3)              [▼ Expand]       │
│  ├── ✅ Backup completed        14:28        │
│  ├── ✅ User import             14:15        │
│  └── ✅ Course publish          13:52        │
│                                              │
│  Failed (1)                  [▼ Expand]       │
│  └── ❌ Plugin update           13:45 [Retry]│
└─────────────────────────────────────────────┘
```

### 9.3 Keyboard Navigation

- Arrow Up/Down: Navigate tasks
- Enter: View task details
- Delete: Cancel/remove task
- Ctrl+A: Select all completed
- Escape: Close panel

---

## 10. Long-Running Operations

### 10.1 Full-Screen Progress

For operations that block the UI:

```
┌─────────────────────────────────────────────┐
│                                              │
│              📊 Generating Report            │
│                                              │
│         ████████████████████░░░░  80%        │
│                                              │
│         Analyzing student data...            │
│         Estimated time remaining: 12 seconds │
│                                              │
│         [Cancel]              [Background]   │
│                                              │
└─────────────────────────────────────────────┘
```

### 10.2 Background Option

- "Background" button moves operation to task queue
- UI becomes interactive again
- Progress continues in background
- Notification on completion

### 10.3 Estimated Time

- Based on historical data for similar operations
- Updated every 2 seconds during execution
- Shown as "About X seconds" or "About X minutes"
- Hidden if < 3 seconds remaining

---

## 11. Cancellation System

### 11.1 Cancel Button

- Available on all cancellable operations
- Click triggers confirmation dialog
- Keyboard: Escape key triggers cancel for in-progress operations

### 11.2 Cancel Confirmation

```
┌─────────────────────────────────────────────┐
│  ⚠️ Cancel Operation?                        │
│                                              │
│  The report is 60% complete.                 │
│  Cancelling will discard partial results.    │
│                                              │
│         [Continue]            [Cancel Task]  │
└─────────────────────────────────────────────┘
```

### 11.3 Cleanup

- Partial results discarded
- Resources released (file handles, memory)
- Progress indicator removed
- "Task cancelled" toast shown
- Queue updated to remove cancelled task

### 11.4 Non-Cancellable Operations

Some operations cannot be cancelled once started:
- Database writes (atomic)
- Application restart
- Backup finalization
- Restore execution

For these, the cancel button is disabled with tooltip explaining why.

---

## 12. Workflow State Persistence

### 12.1 What Persists

| State | Duration | Storage |
|---|---|---|
| Wizard progress | Until completion | IndexedDB |
| Form drafts | 24 hours | IndexedDB |
| Undo stack | Session | Memory |
| Open tabs | Session | Memory |
| Task queue | Until completion | IndexedDB |
| Autosave content | Until saved permanently | IndexedDB |

### 12.2 Recovery on Crash

```
Application crash → Restart → Recovery dialog:

┌─────────────────────────────────────────────┐
│  💾 Unsaved Work Recovered                   │
│                                              │
│  The following work was saved before the     │
│  application closed unexpectedly:            │
│                                              │
│  • Assessment: 15 answers saved              │
│  • Course draft: "NetSec 101" (3 modules)   │
│  • Notes: 3 lessons with notes               │
│                                              │
│  [Restore All]  [Review Individually]        │
└─────────────────────────────────────────────┘
```
