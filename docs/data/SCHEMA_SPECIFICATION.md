# Complete Schema Specification — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Conventions

### 1.1 Column Naming

| Convention | Example | Description |
|---|---|---|
| Snake case | `display_name` | All column names use snake_case |
| UUID primary key | `id` | Always `BLOB(16)`, stored as UUID4 binary |
| Foreign key | `user_id` | Always `<referenced_table_singular>_id` |
| Boolean flag | `is_deleted` | Prefixed with `is_` or `has_` |
| Timestamp | `created_at` | Suffixed with `_at` |
| Version | `version` | Integer, incremented on every update |

### 1.2 Audit Fields (Present on Every Table)

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `created_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Record creation time |
| `updated_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Last modification time |
| `created_by` | BLOB(16) | NULL | NULL | User ID of creator |
| `updated_by` | BLOB(16) | NULL | NULL | User ID of last modifier |
| `is_deleted` | BOOLEAN | NOT NULL | 0 | Soft delete flag |
| `deleted_at` | DATETIME | NULL | NULL | Soft delete timestamp |
| `deleted_by` | BLOB(16) | NULL | NULL | User who deleted the record |
| `version` | INTEGER | NOT NULL | 1 | Optimistic lock version |

### 1.3 Soft Delete Policy

- All tables support soft deletes via `is_deleted` and `deleted_at`
- Queries must always filter `WHERE is_deleted = 0` unless explicitly including deleted records
- Hard deletes are only permitted during data archival or GDPR erasure
- Cascade soft deletes propagate to child records where applicable
- Soft-deleted records are excluded from unique constraint checks

---

## 2. Table Specifications

### 2.1 `users` — Core Identity

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `email` | VARCHAR(255) | NOT NULL | — | Unique email address (login identifier) |
| `display_name` | VARCHAR(100) | NOT NULL | — | User's display name |
| `password_hash` | VARCHAR(255) | NOT NULL | — | Argon2id password hash |
| `status` | VARCHAR(50) | NOT NULL | 'active' | Account status enum |
| `avatar_url` | VARCHAR(500) | NULL | NULL | Profile image URL |
| `locale` | VARCHAR(10) | NOT NULL | 'en' | Preferred locale code |
| `timezone` | VARCHAR(50) | NOT NULL | 'UTC' | User timezone |
| `last_login_at` | DATETIME | NULL | NULL | Timestamp of last successful login |
| `last_login_ip` | VARCHAR(45) | NULL | NULL | IP address of last login |
| `failed_login_attempts` | INTEGER | NOT NULL | 0 | Consecutive failed login count |
| `locked_until` | DATETIME | NULL | NULL | Account lock expiry |
| `email_verified_at` | DATETIME | NULL | NULL | Email verification timestamp |
| `mfa_enabled` | BOOLEAN | NOT NULL | 0 | MFA enabled flag |
| `mfa_secret` | VARCHAR(255) | NULL | NULL | Encrypted TOTP secret |
| `metadata` | TEXT | NULL | NULL | JSON blob for extensible fields |

**Primary Key:** `id`

**Foreign Keys:** None (root aggregate)

**Unique Constraints:**
- `uq_users_email` on (`email`) WHERE `is_deleted = 0`

**Indexes:**
| Name | Columns | Type | Filter |
|---|---|---|---|
| `idx_users_email` | `email` | B-tree (unique) | `is_deleted = 0` |
| `idx_users_display_name` | `display_name` | B-tree | `is_deleted = 0` |
| `idx_users_status` | `status` | Partial | `is_deleted = 0` |
| `idx_users_last_login` | `last_login_at DESC` | B-tree | `is_deleted = 0` |

**Relationships:**
- Users → Roles (N:M via `user_roles`)
- Users → Sessions (1:N via `sessions`)
- Users → Enrollments (1:N via `enrollments`)
- Users → Certificates (1:N via `certificates`)
- Users → Notifications (1:N via `notifications`)
- Users → AuditEntries (1:N via `audit_entries`)

**Validation Rules:**
- `email` must be valid email format
- `email` must be unique among non-deleted users
- `password_hash` must be Argon2id format
- `status` must be one of: active, inactive, suspended, pending
- `display_name` must be 1-100 characters
- `version` must be positive integer

**Lifecycle:** DRAFT (pending verification) → ACTIVE → INACTIVE → SUSPENDED

---

### 2.2 `roles` — Authorization Roles

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `name` | VARCHAR(100) | NOT NULL | — | Role name (unique) |
| `display_name` | VARCHAR(200) | NOT NULL | — | Human-readable role name |
| `description` | TEXT | NULL | NULL | Role description |
| `is_system` | BOOLEAN | NOT NULL | 0 | System role (non-deletable) |
| `is_default` | BOOLEAN | NOT NULL | 0 | Auto-assigned to new users |
| `priority` | INTEGER | NOT NULL | 0 | Role priority for conflict resolution |
| `metadata` | TEXT | NULL | NULL | JSON blob for extensible fields |

**Primary Key:** `id`

**Unique Constraints:**
- `uq_roles_name` on (`name`) WHERE `is_deleted = 0`

**Indexes:**
| Name | Columns | Type |
|---|---|---|
| `idx_roles_name` | `name` | B-tree (unique) |
| `idx_roles_is_default` | `is_default` | Partial (`is_default = 1 AND is_deleted = 0`) |

**Relationships:**
- Roles → Permissions (N:M via `role_permissions`)
- Roles → Users (N:M via `user_roles`)

**Validation Rules:**
- `name` must be alphanumeric with underscores, 1-100 characters
- System roles cannot be deleted or renamed
- `priority` must be non-negative

**Lifecycle:** ACTIVE → DEPRECATED → RETIRED (soft-deleted)

---

### 2.3 `permissions` — Granular Permissions

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `name` | VARCHAR(200) | NOT NULL | — | Permission identifier (e.g., `course.create`) |
| `display_name` | VARCHAR(200) | NOT NULL | — | Human-readable name |
| `description` | TEXT | NULL | NULL | Permission description |
| `resource_type` | VARCHAR(100) | NOT NULL | — | Resource type this permission applies to |
| `action` | VARCHAR(50) | NOT NULL | — | Action: create, read, update, delete, manage |
| `is_system` | BOOLEAN | NOT NULL | 0 | System permission (non-deletable) |
| `metadata` | TEXT | NULL | NULL | JSON blob |

**Primary Key:** `id`

**Unique Constraints:**
- `uq_permissions_name` on (`name`) WHERE `is_deleted = 0`

**Relationships:**
- Permissions → Roles (N:M via `role_permissions`)

**Validation Rules:**
- `name` format: `<resource>.<action>` (e.g., `course.create`)
- `action` must be one of: create, read, update, delete, manage, execute

---

### 2.4 `user_roles` — User-Role Junction

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id |
| `role_id` | BLOB(16) | NOT NULL | — | FK → roles.id |
| `assigned_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Assignment timestamp |
| `assigned_by` | BLOB(16) | NULL | NULL | FK → users.id (admin who assigned) |
| `expires_at` | DATETIME | NULL | NULL | Temporary role expiry |
| `metadata` | TEXT | NULL | NULL | JSON blob |

**Unique Constraints:**
- `uq_user_roles_unique` on (`user_id`, `role_id`) WHERE `is_deleted = 0`

---

### 2.5 `role_permissions` — Role-Permission Junction

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `role_id` | BLOB(16) | NOT NULL | — | FK → roles.id |
| `permission_id` | BLOB(16) | NOT NULL | — | FK → permissions.id |
| `granted_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Grant timestamp |
| `granted_by` | BLOB(16) | NULL | NULL | FK → users.id |

**Unique Constraints:**
- `uq_role_permissions_unique` on (`role_id`, `permission_id`) WHERE `is_deleted = 0`

---

### 2.6 `sessions` — User Sessions

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id |
| `session_token` | VARCHAR(255) | NOT NULL | — | Secure session token |
| `ip_address` | VARCHAR(45) | NOT NULL | — | Client IP address |
| `user_agent` | VARCHAR(500) | NULL | NULL | Client user agent string |
| `started_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Session start |
| `last_active_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Last activity |
| `ended_at` | DATETIME | NULL | NULL | Session end |
| `status` | VARCHAR(50) | NOT NULL | 'active' | active, expired, revoked |
| `expires_at` | DATETIME | NOT NULL | — | Session expiry |

**Indexes:**
| Name | Columns | Type |
|---|---|---|
| `idx_sessions_user` | `user_id` | B-tree |
| `idx_sessions_token` | `session_token` | B-tree (unique) |
| `idx_sessions_active` | `status` | Partial (`status = 'active'`) |
| `idx_sessions_expires` | `expires_at` | B-tree |

---

### 2.7 `audit_entries` — Audit Trail

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `timestamp` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Event timestamp |
| `user_id` | BLOB(16) | NULL | NULL | FK → users.id (NULL for system events) |
| `action` | VARCHAR(100) | NOT NULL | — | Action performed |
| `entity_type` | VARCHAR(100) | NOT NULL | — | Entity type affected |
| `entity_id` | BLOB(16) | NULL | NULL | Entity ID affected |
| `old_value` | TEXT | NULL | NULL | Previous state (JSON) |
| `new_value` | TEXT | NULL | NULL | New state (JSON) |
| `ip_address` | VARCHAR(45) | NULL | NULL | Client IP |
| `user_agent` | VARCHAR(500) | NULL | NULL | Client user agent |
| `metadata` | TEXT | NULL | NULL | Additional context (JSON) |
| `previous_hash` | VARCHAR(64) | NULL | NULL | SHA-256 hash of previous entry |
| `entry_hash` | VARCHAR(64) | NOT NULL | — | SHA-256 hash of this entry |

**Indexes:**
| Name | Columns | Type |
|---|---|---|
| `idx_audit_timestamp` | `timestamp DESC` | B-tree |
| `idx_audit_user` | `user_id` | B-tree |
| `idx_audit_entity` | `entity_type, entity_id` | Composite |
| `idx_audit_action` | `action` | B-tree |
| `idx_audit_hash` | `entry_hash` | B-tree (unique) |

**Special Policy:** No soft deletes on audit entries. Append-only. Hash chain for tamper detection.

---

### 2.8 `courses` — Course Definitions

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `title` | VARCHAR(200) | NOT NULL | — | Course title |
| `description` | TEXT | NULL | NULL | Course description |
| `short_description` | VARCHAR(500) | NULL | NULL | Brief description |
| `slug` | VARCHAR(200) | NOT NULL | — | URL-friendly identifier |
| `status` | VARCHAR(50) | NOT NULL | 'draft' | draft, published, archived |
| `difficulty` | VARCHAR(50) | NOT NULL | 'beginner' | beginner, intermediate, advanced |
| `estimated_hours` | REAL | NULL | NULL | Estimated completion time |
| `thumbnail_url` | VARCHAR(500) | NULL | NULL | Course thumbnail |
| `tags` | TEXT | NULL | NULL | JSON array of tags |
| `language` | VARCHAR(10) | NOT NULL | 'en' | Course language |
| `organization_id` | BLOB(16) | NULL | NULL | FK → organizations.id |
| `instructor_id` | BLOB(16) | NULL | NULL | FK → users.id |
| `content_hash` | VARCHAR(64) | NULL | NULL | SHA-256 of published content |
| `published_at` | DATETIME | NULL | NULL | Publication timestamp |
| `metadata` | TEXT | NULL | NULL | JSON blob |

**Unique Constraints:**
- `uq_courses_slug` on (`slug`) WHERE `is_deleted = 0`

---

### 2.9 `course_modules` — Module Structure

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `course_id` | BLOB(16) | NOT NULL | — | FK → courses.id |
| `title` | VARCHAR(200) | NOT NULL | — | Module title |
| `description` | TEXT | NULL | NULL | Module description |
| `sort_order` | INTEGER | NOT NULL | 0 | Display order within course |
| `status` | VARCHAR(50) | NOT NULL | 'active' | active, draft, archived |
| `metadata` | TEXT | NULL | NULL | JSON blob |

**Indexes:**
| Name | Columns | Type |
|---|---|---|
| `idx_cm_course` | `course_id` | B-tree |
| `idx_cm_order` | `course_id, sort_order` | Composite |

---

### 2.10 `lessons` — Individual Lessons

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `module_id` | BLOB(16) | NOT NULL | — | FK → course_modules.id |
| `title` | VARCHAR(200) | NOT NULL | — | Lesson title |
| `content_type` | VARCHAR(50) | NOT NULL | 'text' | text, video, interactive, quiz |
| `content` | TEXT | NULL | NULL | Lesson content (Markdown/HTML) |
| `sort_order` | INTEGER | NOT NULL | 0 | Display order within module |
| `estimated_minutes` | INTEGER | NULL | NULL | Estimated completion time |
| `is_mandatory` | BOOLEAN | NOT NULL | 1 | Required for course completion |
| `content_hash` | VARCHAR(64) | NULL | NULL | SHA-256 of content |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.11 `enrollments` — Course Enrollments

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id |
| `course_id` | BLOB(16) | NOT NULL | — | FK → courses.id |
| `status` | VARCHAR(50) | NOT NULL | 'active' | active, completed, dropped, suspended |
| `enrolled_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Enrollment date |
| `completed_at` | DATETIME | NULL | NULL | Completion timestamp |
| `progress_percentage` | REAL | NOT NULL | 0.0 | Overall progress |
| `metadata` | TEXT | NULL | NULL | JSON blob |

**Unique Constraints:**
- `uq_enrollments` on (`user_id`, `course_id`) WHERE `is_deleted = 0`

---

### 2.12 `progress` — Lesson Progress

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id |
| `lesson_id` | BLOB(16) | NOT NULL | — | FK → lessons.id |
| `course_id` | BLOB(16) | NOT NULL | — | FK → courses.id |
| `status` | VARCHAR(50) | NOT NULL | 'not_started' | not_started, in_progress, completed |
| `percentage` | REAL | NOT NULL | 0.0 | Completion percentage |
| `started_at` | DATETIME | NULL | NULL | First access |
| `completed_at` | DATETIME | NULL | NULL | Completion timestamp |
| `time_spent_seconds` | INTEGER | NOT NULL | 0 | Total time spent |
| `last_position` | TEXT | NULL | NULL | Resume position (JSON) |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.13 `assessments` — Assessment Definitions

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `course_id` | BLOB(16) | NOT NULL | — | FK → courses.id |
| `title` | VARCHAR(200) | NOT NULL | — | Assessment title |
| `description` | TEXT | NULL | NULL | Assessment instructions |
| `assessment_type` | VARCHAR(50) | NOT NULL | 'quiz' | quiz, exam, practical, assignment |
| `max_score` | REAL | NOT NULL | 100.0 | Maximum possible score |
| `passing_score` | REAL | NOT NULL | 70.0 | Minimum passing score |
| `time_limit_minutes` | INTEGER | NULL | NULL | Time limit (NULL = unlimited) |
| `max_attempts` | INTEGER | NULL | NULL | Max attempts (NULL = unlimited) |
| `shuffle_questions` | BOOLEAN | NOT NULL | 0 | Randomize question order |
| `shuffle_options` | BOOLEAN | NOT NULL | 0 | Randomize option order |
| `show_answers` | VARCHAR(50) | NOT NULL | 'after_submission' | never, after_submission, after_due |
| `due_at` | DATETIME | NULL | NULL | Assessment deadline |
| `status` | VARCHAR(50) | NOT NULL | 'draft' | draft, published, archived |
| `content_hash` | VARCHAR(64) | NULL | NULL | SHA-256 of question content |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.14 `questions` — Question Bank

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `assessment_id` | BLOB(16) | NOT NULL | — | FK → assessments.id |
| `question_type` | VARCHAR(50) | NOT NULL | 'multiple_choice' | multiple_choice, true_false, short_answer, code, scenario |
| `content` | TEXT | NOT NULL | — | Question text (Markdown) |
| `explanation` | TEXT | NULL | NULL | Answer explanation |
| `points` | REAL | NOT NULL | 1.0 | Point value |
| `difficulty` | VARCHAR(50) | NOT NULL | 'medium' | easy, medium, hard |
| `sort_order` | INTEGER | NOT NULL | 0 | Display order |
| `hint` | TEXT | NULL | NULL | Optional hint |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.15 `question_options` — MCQ Options

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `question_id` | BLOB(16) | NOT NULL | — | FK → questions.id |
| `content` | TEXT | NOT NULL | — | Option text |
| `is_correct` | BOOLEAN | NOT NULL | 0 | Correct answer flag |
| `sort_order` | INTEGER | NOT NULL | 0 | Display order |
| `explanation` | TEXT | NULL | NULL | Why this option is correct/incorrect |

---

### 2.16 `attempts` — Student Attempts

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id |
| `assessment_id` | BLOB(16) | NOT NULL | — | FK → assessments.id |
| `attempt_number` | INTEGER | NOT NULL | 1 | Sequential attempt number |
| `status` | VARCHAR(50) | NOT NULL | 'in_progress' | in_progress, submitted, graded, voided |
| `started_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Attempt start |
| `submitted_at` | DATETIME | NULL | NULL | Submission timestamp |
| `time_spent_seconds` | INTEGER | NOT NULL | 0 | Total time in seconds |
| `ip_address` | VARCHAR(45) | NULL | NULL | Client IP during attempt |
| `checksum` | VARCHAR(64) | NULL | NULL | Integrity checksum |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.17 `answers` — Individual Answers

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `attempt_id` | BLOB(16) | NOT NULL | — | FK → attempts.id |
| `question_id` | BLOB(16) | NOT NULL | — | FK → questions.id |
| `selected_option_id` | BLOB(16) | NULL | NULL | FK → question_options.id (MCQ) |
| `answer_text` | TEXT | NULL | NULL | Free-text answer |
| `is_correct` | BOOLEAN | NULL | NULL | Grading result (NULL = ungraded) |
| `points_earned` | REAL | NULL | NULL | Points awarded (NULL = ungraded) |
| `time_spent_seconds` | INTEGER | NOT NULL | 0 | Time on this question |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.18 `results` — Graded Results

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `attempt_id` | BLOB(16) | NOT NULL | — | FK → attempts.id (unique) |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id |
| `assessment_id` | BLOB(16) | NOT NULL | — | FK → assessments.id |
| `score` | REAL | NOT NULL | — | Final score (0-100) |
| `points_earned` | REAL | NOT NULL | 0.0 | Points earned |
| `points_possible` | REAL | NOT NULL | 0.0 | Points possible |
| `passed` | BOOLEAN | NOT NULL | 0 | Whether assessment was passed |
| `graded_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Grading timestamp |
| `graded_by` | BLOB(16) | NULL | NULL | FK → users.id (manual grading) |
| `feedback` | TEXT | NULL | NULL | Instructor feedback |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.19 `competencies` — Skill Definitions

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `name` | VARCHAR(200) | NOT NULL | — | Competency name |
| `description` | TEXT | NULL | NULL | What this competency measures |
| `category` | VARCHAR(100) | NOT NULL | — | Skill category |
| `framework` | VARCHAR(100) | NULL | NULL | Competency framework reference |
| `is_active` | BOOLEAN | NOT NULL | 1 | Whether actively tracked |

---

### 2.20 `competency_levels` — Proficiency Levels

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `competency_id` | BLOB(16) | NOT NULL | — | FK → competencies.id |
| `label` | VARCHAR(100) | NOT NULL | — | Level label (e.g., "Beginner") |
| `description` | TEXT | NULL | NULL | Level description |
| `order_index` | INTEGER | NOT NULL | — | Level ordering (1 = lowest) |
| `criteria` | TEXT | NULL | NULL | Assessment criteria (JSON) |

---

### 2.21 `user_competencies` — User Skill Records

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id |
| `competency_id` | BLOB(16) | NOT NULL | — | FK → competencies.id |
| `level_id` | BLOB(16) | NOT NULL | — | FK → competency_levels.id |
| `achieved_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | When level was achieved |
| `verified_by` | BLOB(16) | NULL | NULL | FK → users.id (verifier) |
| `evidence` | TEXT | NULL | NULL | Evidence/justification (JSON) |
| `expires_at` | DATETIME | NULL | NULL | Optional expiry |

**Unique Constraints:**
- `uq_user_competencies` on (`user_id`, `competency_id`) WHERE `is_deleted = 0`

---

### 2.22 `certificates` — Issued Certificates

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id |
| `course_id` | BLOB(16) | NOT NULL | — | FK → courses.id |
| `certificate_number` | VARCHAR(100) | NOT NULL | — | Unique certificate ID |
| `issued_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Issue date |
| `expires_at` | DATETIME | NULL | NULL | Optional expiry |
| `status` | VARCHAR(50) | NOT NULL | 'active' | active, revoked, expired |
| `revoked_at` | DATETIME | NULL | NULL | Revocation timestamp |
| `revocation_reason` | TEXT | NULL | NULL | Why revoked |
| `template_id` | BLOB(16) | NULL | NULL | FK → certificate_templates.id |
| `signature` | VARCHAR(512) | NOT NULL | — | Cryptographic signature |
| `metadata` | TEXT | NULL | NULL | JSON blob |

**Unique Constraints:**
- `uq_cert_number` on (`certificate_number`)

---

### 2.23 `plugins` — Plugin Registry

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `name` | VARCHAR(200) | NOT NULL | — | Plugin identifier |
| `display_name` | VARCHAR(200) | NOT NULL | — | Human-readable name |
| `description` | TEXT | NULL | NULL | Plugin description |
| `author` | VARCHAR(200) | NULL | NULL | Plugin author |
| `status` | VARCHAR(50) | NOT NULL | 'active' | active, deprecated, disabled, error |
| `installed_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Installation date |
| `last_activated_at` | DATETIME | NULL | NULL | Last activation |
| `config_schema` | TEXT | NULL | NULL | JSON Schema for configuration |
| `permissions_required` | TEXT | NULL | NULL | JSON array of required permissions |
| `metadata` | TEXT | NULL | NULL | JSON blob |

**Unique Constraints:**
- `uq_plugins_name` on (`name`) WHERE `is_deleted = 0`

---

### 2.24 `plugin_versions` — Version History

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `plugin_id` | BLOB(16) | NOT NULL | — | FK → plugins.id |
| `version` | VARCHAR(50) | NOT NULL | — | Semantic version |
| `changelog` | TEXT | NULL | NULL | Version changelog |
| `download_url` | VARCHAR(500) | NULL | NULL | Package URL |
| `checksum_sha256` | VARCHAR(64) | NOT NULL | — | Package integrity hash |
| `min_platform_version` | VARCHAR(50) | NULL | NULL | Minimum required version |
| `released_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Release date |
| `is_installed` | BOOLEAN | NOT NULL | 0 | Currently installed version |

---

### 2.25 `configurations` — System Configuration

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `config_key` | VARCHAR(200) | NOT NULL | — | Configuration key |
| `config_value` | TEXT | NOT NULL | — | Configuration value (JSON) |
| `value_type` | VARCHAR(50) | NOT NULL | 'string' | string, integer, boolean, json, encrypted |
| `is_sensitive` | BOOLEAN | NOT NULL | 0 | Value is encrypted |
| `category` | VARCHAR(100) | NOT NULL | 'general' | Configuration category |
| `description` | TEXT | NULL | NULL | Configuration description |
| `default_value` | TEXT | NULL | NULL | Default value |
| `validation_schema` | TEXT | NULL | NULL | JSON Schema for validation |

**Unique Constraints:**
- `uq_configurations_key` on (`config_key`) WHERE `is_deleted = 0`

---

### 2.26 `settings` — User/System Settings

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NULL | NULL | FK → users.id (NULL = system setting) |
| `setting_key` | VARCHAR(200) | NOT NULL | — | Setting key |
| `setting_value` | TEXT | NOT NULL | — | Setting value (JSON) |
| `scope` | VARCHAR(50) | NOT NULL | 'user' | user, organization, global |
| `organization_id` | BLOB(16) | NULL | NULL | FK → organizations.id |

**Unique Constraints:**
- `uq_user_setting` on (`user_id`, `setting_key`) WHERE `is_deleted = 0`

---

### 2.27 `backups` — Backup Records

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `backup_type` | VARCHAR(50) | NOT NULL | — | full, incremental, config, export |
| `status` | VARCHAR(50) | NOT NULL | 'pending' | pending, in_progress, completed, failed |
| `file_path` | VARCHAR(500) | NOT NULL | — | Backup file location |
| `file_size_bytes` | INTEGER | NULL | NULL | File size |
| `checksum_sha256` | VARCHAR(64) | NOT NULL | — | Integrity hash |
| `parent_backup_id` | BLOB(16) | NULL | NULL | FK → backups.id (incremental parent) |
| `started_at` | DATETIME | NOT NULL | CURRENT_TIMESTAMP | Backup start |
| `completed_at` | DATETIME | NULL | NULL | Backup completion |
| `error_message` | TEXT | NULL | NULL | Error details |
| `schedule_id` | BLOB(16) | NULL | NULL | FK → backup_schedules.id |
| `retention_days` | INTEGER | NOT NULL | 365 | Days to retain |

---

### 2.28 `reports` — Generated Reports

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id (report owner) |
| `title` | VARCHAR(200) | NOT NULL | — | Report title |
| `report_type` | VARCHAR(100) | NOT NULL | — | Report type identifier |
| `status` | VARCHAR(50) | NOT NULL | 'pending' | pending, generating, completed, failed |
| `parameters` | TEXT | NULL | NULL | Report parameters (JSON) |
| `result_data` | TEXT | NULL | NULL | Report output (JSON) |
| `file_path` | VARCHAR(500) | NULL | NULL | Export file path |
| `generated_at` | DATETIME | NULL | NULL | Generation timestamp |
| `expires_at` | DATETIME | NULL | NULL | When report expires |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.29 `notifications` — Notification Records

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id |
| `template_id` | BLOB(16) | NULL | NULL | FK → notification_templates.id |
| `title` | VARCHAR(200) | NOT NULL | — | Notification title |
| `body` | TEXT | NOT NULL | — | Notification content |
| `notification_type` | VARCHAR(50) | NOT NULL | 'info' | info, warning, error, success |
| `category` | VARCHAR(100) | NOT NULL | 'general' | Notification category |
| `is_read` | BOOLEAN | NOT NULL | 0 | Read status |
| `read_at` | DATETIME | NULL | NULL | When marked as read |
| `action_url` | VARCHAR(500) | NULL | NULL | Deep link action |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.30 `organizations` — Organization Records

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `name` | VARCHAR(200) | NOT NULL | — | Organization name |
| `slug` | VARCHAR(200) | NOT NULL | — | URL-friendly identifier |
| `description` | TEXT | NULL | NULL | Organization description |
| `logo_url` | VARCHAR(500) | NULL | NULL | Logo image URL |
| `status` | VARCHAR(50) | NOT NULL | 'active' | active, inactive, dissolved |
| `settings` | TEXT | NULL | NULL | Organization settings (JSON) |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.31 `institutions` — Educational Institutions

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `organization_id` | BLOB(16) | NOT NULL | — | FK → organizations.id (unique) |
| `name` | VARCHAR(200) | NOT NULL | — | Institution name |
| `institution_type` | VARCHAR(50) | NOT NULL | — | university, school, training_center |
| `accreditation_number` | VARCHAR(100) | NULL | NULL | Accreditation ID |
| `contact_email` | VARCHAR(255) | NULL | NULL | Contact email |
| `contact_phone` | VARCHAR(50) | NULL | NULL | Contact phone |
| `address` | TEXT | NULL | NULL | Physical address |
| `website_url` | VARCHAR(500) | NULL | NULL | Institution website |
| `metadata` | TEXT | NULL | NULL | JSON blob |

---

### 2.32 `localization_keys` — i18n Key Definitions

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `key` | VARCHAR(500) | NOT NULL | — | Translation key (e.g., `nav.home`) |
| `context` | VARCHAR(100) | NULL | NULL | Usage context |
| `description` | TEXT | NULL | NULL | Key description for translators |
| `is_plural` | BOOLEAN | NOT NULL | 0 | Plural form flag |
| `metadata` | TEXT | NULL | NULL | JSON blob |

**Unique Constraints:**
- `uq_loc_key` on (`key`) WHERE `is_deleted = 0`

---

### 2.33 `accessibility_profiles` — A11y Preferences

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `user_id` | BLOB(16) | NOT NULL | — | FK → users.id (unique) |
| `profile_name` | VARCHAR(100) | NOT NULL | 'Default' | Profile name |
| `high_contrast` | BOOLEAN | NOT NULL | 0 | High contrast mode |
| `reduced_motion` | BOOLEAN | NOT NULL | 0 | Reduced animations |
| `font_size` | VARCHAR(20) | NOT NULL | 'medium' | small, medium, large, xlarge |
| `screen_reader_optimized` | BOOLEAN | NOT NULL | 0 | Screen reader mode |
| `keyboard_navigation` | BOOLEAN | NOT NULL | 1 | Enhanced keyboard nav |
| `color_blind_mode` | VARCHAR(50) | NOT NULL | 'none' | none, protanopia, deuteranopia, tritanopia |
| `dyslexia_font` | BOOLEAN | NOT NULL | 0 | OpenDyslexic font |
| `captions_enabled` | BOOLEAN | NOT NULL | 0 | Auto-enable captions |
| `settings` | TEXT | NULL | NULL | Additional settings (JSON) |

---

### 2.34 `assets` — File Storage Metadata

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BLOB(16) | NOT NULL | UUID4 | Primary key |
| `owner_id` | BLOB(16) | NOT NULL | — | FK → users.id |
| `filename` | VARCHAR(500) | NOT NULL | — | Original filename |
| `mime_type` | VARCHAR(200) | NOT NULL | — | MIME type |
| `file_size_bytes` | INTEGER | NOT NULL | — | File size |
| `storage_path` | VARCHAR(500) | NOT NULL | — | Local file path |
| `checksum_sha256` | VARCHAR(64) | NOT NULL | — | Integrity hash |
| `asset_type` | VARCHAR(50) | NOT NULL | 'file' | file, image, video, document, audio |
| `parent_type` | VARCHAR(100) | NULL | NULL | Parent entity type |
| `parent_id` | BLOB(16) | NULL | NULL | Parent entity ID |
| `metadata` | TEXT | NULL | NULL | JSON blob (dimensions, duration, etc.) |

---

## 3. Complete Relationship Matrix

| Parent Table | Child Table | FK Column | Cardinality | On Delete |
|---|---|---|---|---|
| users | sessions | user_id | 1:N | CASCADE |
| users | user_roles | user_id | N:M | CASCADE |
| users | enrollments | user_id | 1:N | RESTRICT |
| users | certificates | user_id | 1:N | RESTRICT |
| users | notifications | user_id | 1:N | CASCADE |
| users | audit_entries | user_id | 1:N | SET NULL |
| users | settings | user_id | 1:N | CASCADE |
| users | accessibility_profiles | user_id | 1:1 | CASCADE |
| users | user_competencies | user_id | N:M | CASCADE |
| users | assets | owner_id | 1:N | RESTRICT |
| users | reports | user_id | 1:N | RESTRICT |
| roles | role_permissions | role_id | N:M | CASCADE |
| roles | user_roles | role_id | N:M | RESTRICT |
| permissions | role_permissions | permission_id | N:M | RESTRICT |
| organizations | org_memberships | organization_id | 1:N | CASCADE |
| organizations | institutions | organization_id | 1:1 | RESTRICT |
| organizations | courses | organization_id | 1:N | SET NULL |
| courses | course_modules | course_id | 1:N | CASCADE |
| courses | enrollments | course_id | 1:N | RESTRICT |
| courses | assessments | course_id | 1:N | RESTRICT |
| courses | certificates | course_id | 1:N | RESTRICT |
| course_modules | lessons | module_id | 1:N | CASCADE |
| lessons | progress | lesson_id | 1:N | CASCADE |
| assessments | questions | assessment_id | 1:N | CASCADE |
| questions | question_options | question_id | 1:N | CASCADE |
| attempts | answers | attempt_id | 1:N | CASCADE |
| attempts | results | attempt_id | 1:1 | CASCADE |
| competencies | competency_levels | competency_id | 1:N | CASCADE |
| plugins | plugin_versions | plugin_id | 1:N | CASCADE |
| plugins | plugin_configs | plugin_id | 1:N | CASCADE |
| plugins | plugin_hooks | plugin_id | 1:N | CASCADE |
| configurations | settings | config_id | 1:N | SET NULL |
| localization_keys | translations | key_id | 1:N | CASCADE |
| backups | backups | parent_backup_id | 1:N | SET NULL |

---

## 4. Default Values Reference

| Table | Column | Default | Source |
|---|---|---|---|
| All tables | `id` | `uuid4()` | Application |
| All tables | `created_at` | `CURRENT_TIMESTAMP` | Database |
| All tables | `updated_at` | `CURRENT_TIMESTAMP` | Database |
| All tables | `is_deleted` | `0` (False) | Application |
| All tables | `version` | `1` | Application |
| users | `status` | `'active'` | Application |
| users | `locale` | `'en'` | Application |
| users | `timezone` | `'UTC'` | Application |
| users | `failed_login_attempts` | `0` | Application |
| users | `mfa_enabled` | `0` (False) | Application |
| roles | `is_system` | `0` (False) | Application |
| roles | `is_default` | `0` (False) | Application |
| roles | `priority` | `0` | Application |
| permissions | `is_system` | `0` (False) | Application |
| sessions | `status` | `'active'` | Application |
| courses | `status` | `'draft'` | Application |
| courses | `difficulty` | `'beginner'` | Application |
| courses | `language` | `'en'` | Application |
| assessments | `assessment_type` | `'quiz'` | Application |
| assessments | `max_score` | `100.0` | Application |
| assessments | `passing_score` | `70.0` | Application |
| assessments | `shuffle_questions` | `0` (False) | Application |
| assessments | `shuffle_options` | `0` (False) | Application |
| assessments | `show_answers` | `'after_submission'` | Application |
| assessments | `status` | `'draft'` | Application |
| questions | `question_type` | `'multiple_choice'` | Application |
| questions | `difficulty` | `'medium'` | Application |
| questions | `points` | `1.0` | Application |
| attempts | `attempt_number` | `1` | Application |
| attempts | `status` | `'in_progress'` | Application |
| progress | `status` | `'not_started'` | Application |
| progress | `percentage` | `0.0` | Application |
| progress | `time_spent_seconds` | `0` | Application |
| notifications | `notification_type` | `'info'` | Application |
| notifications | `category` | `'general'` | Application |
| notifications | `is_read` | `0` (False) | Application |
| configurations | `value_type` | `'string'` | Application |
| configurations | `is_sensitive` | `0` (False) | Application |
| configurations | `category` | `'general'` | Application |
| settings | `scope` | `'user'` | Application |
| backups | `status` | `'pending'` | Application |
| backups | `retention_days` | `365` | Application |
| certificates | `status` | `'active'` | Application |
| assets | `asset_type` | `'file'` | Application |
| accessibility_profiles | `profile_name` | `'Default'` | Application |
| accessibility_profiles | `high_contrast` | `0` (False) | Application |
| accessibility_profiles | `reduced_motion` | `0` (False) | Application |
| accessibility_profiles | `font_size` | `'medium'` | Application |
| accessibility_profiles | `keyboard_navigation` | `1` (True) | Application |

---

*This document is the authoritative schema specification for all tables in AuthShield Lab.*
