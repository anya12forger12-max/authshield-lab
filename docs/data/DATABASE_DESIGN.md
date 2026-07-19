# Complete Database Design — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. SQLite Configuration

### 1.1 Core Pragmas

AuthShield Lab configures SQLite at connection time using the following pragmas,
applied via SQLAlchemy event listeners on every new connection:

```sql
-- Write-Ahead Logging for concurrent read/write
PRAGMA journal_mode = WAL;

-- Foreign key enforcement (SQLite disables by default)
PRAGMA foreign_keys = ON;

-- Busy timeout: 5000ms before returning SQLITE_BUSY
PRAGMA busy_timeout = 5000;

-- Page size: 4096 bytes (optimal for modern filesystems)
PRAGMA page_size = 4096;

-- Cache size: -64000 = 64MB
PRAGMA cache_size = -64000;

-- Memory-mapped I/O: 256MB
PRAGMA mmap_size = 268435456;

-- Synchronous mode: NORMAL (safe with WAL)
PRAGMA synchronous = NORMAL;

-- Temp store in memory
PRAGMA temp_store = MEMORY;

-- WAL auto-checkpoint at 1000 pages
PRAGMA wal_autocheckpoint = 1000;

-- Secure delete for sensitive data
PRAGMA secure_delete = OFF;  -- Toggled ON for sensitive tables

-- Integrity check on startup
PRAGMA integrity_check;

-- Secure deletion for audit/security tables
-- PRAGMA secure_delete = ON;  -- Applied per-connection for sensitive contexts
```

### 1.2 Connection Pool Configuration

```python
SQLALCHEMY_ENGINE_CONFIG = {
    "url": "sqlite+aiosqlite:///./data/authshield.db",
    "echo": False,
    "pool_pre_ping": True,
    "pool_size": 5,
    "max_overflow": 10,
    "connect_args": {
        "timeout": 30,
        "isolation_level": None,  # Autocommit for explicit transaction control
    },
}
```

### 1.3 Database Files

| Database | Purpose | Encryption |
|---|---|---|
| `authshield.db` | Main application database | SQLCipher |
| `authshield_audit.db` | Audit log (separate for security) | SQLCipher (stricter) |
| `authshield_cache.db` | Query cache, session cache | Standard SQLite |
| `authshield_fts.db` | Full-text search indexes | Standard SQLite |

---

## 2. Logical Database Model

### 2.1 Entity Relationship Overview

```
┌───────────────────────────────────────────────────────────────┐
│                    Logical Model Overview                     │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────┐  user_roles  ┌────────┐  role_permissions       │
│  │  users  │◄────────────►│  roles │◄────────────►           │
│  └────┬────┘              └────────┘  ┌────────────┐         │
│       │                               │permissions │         │
│       │                               └────────────┘         │
│       │ 1:N                                                   │
│  ┌────▼────────┐                                              │
│  │  sessions   │                                              │
│  └─────────────┘                                              │
│                                                               │
│  ┌───────────────┐  N:M  ┌───────────────┐                   │
│  │organizations  │◄─────►│  institutions │                   │
│  └───────┬───────┘       └───────────────┘                   │
│          │ 1:N                                                │
│  ┌───────▼───────┐                                            │
│  │    courses    │                                            │
│  └──┬─────┬──┬───┘                                            │
│     │     │  │                                                │
│     │     │  └── 1:N ──► ┌────────────┐                      │
│     │     │               │enrollments │                      │
│     │     │               └────────────┘                      │
│     │     │ 1:N                                               │
│     │  ┌──▼──────────┐                                        │
│     │  │   modules   │                                        │
│     │  └──────┬──────┘                                        │
│     │         │ 1:N                                           │
│     │  ┌──────▼──────┐                                        │
│     │  │   lessons   │                                        │
│     │  └─────────────┘                                        │
│     │                                                         │
│     └── 1:N ──► ┌──────────────┐                              │
│                  │ assessments  │                              │
│                  └──────┬───────┘                              │
│                         │ 1:N                                 │
│                  ┌──────▼──────┐                               │
│                  │  questions  │                               │
│                  └──────┬──────┘                               │
│                         │ 1:N                                 │
│                  ┌──────▼──────┐                               │
│                  │   answers   │                               │
│                  └─────────────┘                               │
│                                                               │
│  ┌──────────────┐  1:N  ┌──────────────────┐                 │
│  │    plugins   │──────►│ plugin_versions  │                 │
│  └──────────────┘       └──────────────────┘                 │
│                                                               │
│  ┌──────────────────┐  1:N  ┌──────────────┐                 │
│  │ audit_entries     │──────►│ audit_chains │                 │
│  └──────────────────┘       └──────────────┘                 │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 2.2 Aggregate Roots

Each bounded context defines aggregate roots that serve as consistency boundaries:

| Bounded Context | Aggregate Root | Identity Type |
|---|---|---|
| Identity | User | UUID |
| Authorization | Role | UUID |
| Authorization | Permission | UUID |
| Organization | Organization | UUID |
| Institution | Institution | UUID |
| Learning | Course | UUID |
| Learning | Certificate | UUID |
| Assessment | Assessment | UUID |
| Assessment | Attempt | UUID |
| Extension | Plugin | UUID |
| Platform | Configuration | UUID |
| Platform | Notification | UUID |
| Security | AuditEntry | UUID |
| Security | SecurityEvent | UUID |
| Analytics | Report | UUID |

---

## 3. Physical Database Model

### 3.1 Index-Organized Storage

SQLite uses B-tree storage for all tables. Primary keys (UUIDs) are stored as
16-byte BLOBs for space efficiency:

```sql
-- UUID primary key storage optimization
CREATE TABLE users (
    id BLOB(16) PRIMARY KEY,  -- UUID stored as binary
    -- ...
) WITHOUT ROWID;  -- Clustered index on primary key
```

**Note**: `WITHOUT ROWID` is used on tables with small, fixed-length primary keys
for optimal space usage. Tables with large text/blob columns or variable-length
keys use the default ROWID-based storage.

### 3.2 Page Allocation Strategy

| Table Category | Expected Pages | Growth Pattern |
|---|---|---|
| Small lookup (< 1K rows) | 1-5 pages | Rarely grows |
| Medium (1K-100K rows) | 5-1000 pages | Steady growth |
| Large (100K+ rows) | 1000+ pages | High growth |
| Audit/Log (append-only) | 10K+ pages | Continuous growth |

---

## 4. Schema Organization by Bounded Context

### 4.1 Schema Namespace Mapping

Each bounded context maps to a SQLAlchemy declarative base and Alembic migration
sequence. In SQLite, schemas are emulated via table name prefixes or separate
database files:

```
authshield_main.db:
  ├── identity.*       (users, credentials, mfa_factors)
  ├── authorization.*   (roles, permissions, user_roles, role_permissions)
  ├── organization.*   (organizations, org_memberships, org_settings)
  ├── institution.*    (institutions, institution_members, institution_config)
  ├── learning.*       (courses, course_modules, lessons, enrollments, progress,
  │                     learning_sessions, competencies, competency_levels,
  │                     user_competencies, certificates)
  ├── assessment.*     (assessments, questions, question_options, attempts,
  │                     answers, results)
  ├── extension.*      (plugins, plugin_versions, plugin_configs, plugin_hooks)
  ├── platform.*       (configurations, settings, feature_flags, notifications,
  │                     localization_keys, translations, backups)
  ├── presentation.*   (themes, theme_variables, accessibility_profiles,
  │                     a11y_settings)
  ├── analytics.*      (reports, report_templates, analytics_snapshots, dashboards)
  └── content.*        (assets, media_metadata, file_references, asset_versions)

authshield_audit.db:
  ├── security.audit_entries
  ├── security.audit_chains
  ├── security.audit_archives
  ├── security.security_events
  ├── security.threat_indicators
  └── security.incident_reports

authshield_cache.db:
  ├── cache.query_results
  ├── cache.session_data
  └── cache.computed_values

authshield_fts.db:
  ├── fts.courses_fts
  ├── fts.lessons_fts
  ├── fts.questions_fts
  └── fts.notifications_fts
```

---

## 5. Table Organization Per Module

### 5.1 Identity Module

| Table | Rows (est.) | Description |
|---|---|---|
| `users` | 1,000 | Core user records |
| `credentials` | 1,500 | Password hashes, API keys |
| `mfa_factors` | 500 | TOTP/HOTP configurations |

### 5.2 Authorization Module

| Table | Rows (est.) | Description |
|---|---|---|
| `roles` | 20 | System and custom roles |
| `permissions` | 200 | Granular permission definitions |
| `user_roles` | 2,000 | User-role assignments |
| `role_permissions` | 500 | Role-permission mappings |

### 5.3 Learning Module

| Table | Rows (est.) | Description |
|---|---|---|
| `courses` | 50 | Course definitions |
| `course_modules` | 200 | Module definitions per course |
| `lessons` | 500 | Individual lessons |
| `enrollments` | 5,000 | User course enrollments |
| `progress` | 50,000 | Lesson completion records |
| `learning_sessions` | 10,000 | Active/completed sessions |
| `competencies` | 100 | Skill definitions |
| `competency_levels` | 500 | Proficiency level definitions |
| `user_competencies` | 10,000 | User skill records |
| `certificates` | 3,000 | Issued certificates |

### 5.4 Assessment Module

| Table | Rows (est.) | Description |
|---|---|---|
| `assessments` | 200 | Assessment definitions |
| `questions` | 2,000 | Question bank |
| `question_options` | 8,000 | MCQ answer options |
| `attempts` | 50,000 | Student attempt records |
| `answers` | 500,000 | Individual answer records |
| `results` | 50,000 | Graded results |

### 5.5 Extension Module

| Table | Rows (est.) | Description |
|---|---|---|
| `plugins` | 50 | Installed plugins |
| `plugin_versions` | 200 | Version history |
| `plugin_configs` | 100 | Plugin configurations |
| `plugin_hooks` | 300 | Registered hook points |

### 5.6 Platform Module

| Table | Rows (est.) | Description |
|---|---|---|
| `configurations` | 100 | System configuration entries |
| `settings` | 500 | User/system settings |
| `feature_flags` | 30 | Feature toggle definitions |
| `notifications` | 100,000 | Notification records |
| `localization_keys` | 5,000 | i18n key definitions |
| `translations` | 100,000 | Translated strings |
| `backups` | 500 | Backup records |

---

## 6. Index Strategy

### 6.1 Index Types

| Index Type | Use Case | Example |
|---|---|---|
| **B-tree** | Default. Range queries, equality, sorting | `CREATE INDEX idx_users_email ON users(email)` |
| **Partial** | Queries with constant filter conditions | `CREATE INDEX idx_active_users ON users(email) WHERE is_deleted = 0` |
| **Composite** | Multi-column queries | `CREATE INDEX idx_enrollment_user_course ON enrollments(user_id, course_id)` |
| **Covering** | Index-only scans | `CREATE INDEX idx_user_lookup ON users(email, display_name) INCLUDE (id)` |
| **Expression** | Computed column indexes | `CREATE INDEX idx_users_lower_email ON users(LOWER(email))` |

### 6.2 Index Definitions

```sql
-- ============================================================
-- IDENTITY MODULE
-- ============================================================

-- User lookup by email (most common auth query)
CREATE UNIQUE INDEX idx_users_email
    ON users(email)
    WHERE is_deleted = 0;

-- User display name search
CREATE INDEX idx_users_display_name
    ON users(display_name COLLATE NOCASE)
    WHERE is_deleted = 0;

-- Users by last login (activity tracking)
CREATE INDEX idx_users_last_login
    ON users(last_login_at DESC)
    WHERE is_deleted = 0;

-- Users by status
CREATE INDEX idx_users_status
    ON users(status)
    WHERE is_deleted = 0;

-- Credentials by user ID
CREATE INDEX idx_credentials_user_id
    ON credentials(user_id)
    WHERE is_deleted = 0;

-- MFA factors by user
CREATE INDEX idx_mfa_user_id
    ON mfa_factors(user_id)
    WHERE is_deleted = 0;

-- ============================================================
-- AUTHORIZATION MODULE
-- ============================================================

-- User roles lookup
CREATE INDEX idx_user_roles_user
    ON user_roles(user_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_user_roles_role
    ON user_roles(role_id)
    WHERE is_deleted = 0;

-- Unique user-role assignment
CREATE UNIQUE INDEX idx_user_roles_unique
    ON user_roles(user_id, role_id)
    WHERE is_deleted = 0;

-- Role permissions lookup
CREATE INDEX idx_role_permissions_role
    ON role_permissions(role_id)
    WHERE is_deleted = 0;

CREATE UNIQUE INDEX idx_role_permissions_unique
    ON role_permissions(role_id, permission_id)
    WHERE is_deleted = 0;

-- Permission lookup by name
CREATE UNIQUE INDEX idx_permissions_name
    ON permissions(name)
    WHERE is_deleted = 0;

-- ============================================================
-- ORGANIZATION MODULE
-- ============================================================

-- Org membership lookup
CREATE INDEX idx_org_members_org
    ON org_memberships(organization_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_org_members_user
    ON org_memberships(user_id)
    WHERE is_deleted = 0;

CREATE UNIQUE INDEX idx_org_members_unique
    ON org_memberships(organization_id, user_id)
    WHERE is_deleted = 0;

-- ============================================================
-- LEARNING MODULE
-- ============================================================

-- Course lookup by status
CREATE INDEX idx_courses_status
    ON courses(status)
    WHERE is_deleted = 0;

-- Course modules ordering
CREATE INDEX idx_course_modules_order
    ON course_modules(course_id, sort_order)
    WHERE is_deleted = 0;

-- Lessons by module
CREATE INDEX idx_lessons_module
    ON lessons(module_id, sort_order)
    WHERE is_deleted = 0;

-- Enrollments composite
CREATE UNIQUE INDEX idx_enrollments_unique
    ON enrollments(user_id, course_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_enrollments_course
    ON enrollments(course_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_enrollments_status
    ON enrollments(status)
    WHERE is_deleted = 0;

-- Progress tracking
CREATE INDEX idx_progress_user_lesson
    ON progress(user_id, lesson_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_progress_user_course
    ON progress(user_id, course_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_progress_status
    ON progress(status)
    WHERE is_deleted = 0;

-- Learning sessions
CREATE INDEX idx_sessions_user
    ON learning_sessions(user_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_sessions_active
    ON learning_sessions(status)
    WHERE status = 'active' AND is_deleted = 0;

-- User competencies
CREATE INDEX idx_user_competencies_user
    ON user_competencies(user_id)
    WHERE is_deleted = 0;

CREATE UNIQUE INDEX idx_user_competencies_unique
    ON user_competencies(user_id, competency_id)
    WHERE is_deleted = 0;

-- Certificates
CREATE INDEX idx_certificates_user
    ON certificates(user_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_certificates_course
    ON certificates(course_id)
    WHERE is_deleted = 0;

CREATE UNIQUE INDEX idx_certificates_number
    ON certificates(certificate_number)
    WHERE is_deleted = 0;

-- ============================================================
-- ASSESSMENT MODULE
-- ============================================================

-- Assessments by course
CREATE INDEX idx_assessments_course
    ON assessments(course_id)
    WHERE is_deleted = 0;

-- Questions by assessment
CREATE INDEX idx_questions_assessment
    ON questions(assessment_id, sort_order)
    WHERE is_deleted = 0;

-- Question options
CREATE INDEX idx_question_options_question
    ON question_options(question_id, sort_order)
    WHERE is_deleted = 0;

-- Attempts composite
CREATE INDEX idx_attempts_user_assessment
    ON attempts(user_id, assessment_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_attempts_status
    ON attempts(status)
    WHERE is_deleted = 0;

CREATE INDEX idx_attempts_submitted
    ON attempts(submitted_at DESC)
    WHERE is_deleted = 0;

-- Answers by attempt
CREATE INDEX idx_answers_attempt
    ON answers(attempt_id)
    WHERE is_deleted = 0;

-- Results by user
CREATE INDEX idx_results_user
    ON results(user_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_results_assessment
    ON results(assessment_id)
    WHERE is_deleted = 0;

-- ============================================================
-- EXTENSION MODULE
-- ============================================================

-- Plugin lookup by name
CREATE UNIQUE INDEX idx_plugins_name
    ON plugins(name)
    WHERE is_deleted = 0;

CREATE INDEX idx_plugins_status
    ON plugins(status)
    WHERE is_deleted = 0;

-- Plugin versions
CREATE INDEX idx_plugin_versions_plugin
    ON plugin_versions(plugin_id, version DESC)
    WHERE is_deleted = 0;

-- ============================================================
-- PLATFORM MODULE
-- ============================================================

-- Config lookup
CREATE UNIQUE INDEX idx_configurations_key
    ON configurations(config_key)
    WHERE is_deleted = 0;

-- Settings by user
CREATE INDEX idx_settings_user
    ON settings(user_id)
    WHERE is_deleted = 0;

CREATE UNIQUE INDEX idx_settings_user_key
    ON settings(user_id, setting_key)
    WHERE is_deleted = 0;

-- Feature flags
CREATE UNIQUE INDEX idx_feature_flags_name
    ON feature_flags(flag_name)
    WHERE is_deleted = 0;

-- Notifications
CREATE INDEX idx_notifications_user
    ON notifications(user_id, created_at DESC)
    WHERE is_deleted = 0;

CREATE INDEX idx_notifications_unread
    ON notifications(user_id)
    WHERE is_read = 0 AND is_deleted = 0;

-- Localization
CREATE UNIQUE INDEX idx_localization_keys_key
    ON localization_keys(key)
    WHERE is_deleted = 0;

CREATE INDEX idx_translations_lang
    ON translations(language_code, key_id)
    WHERE is_deleted = 0;

-- ============================================================
-- CONTENT MODULE
-- ============================================================

-- Assets by owner
CREATE INDEX idx_assets_owner
    ON assets(owner_id)
    WHERE is_deleted = 0;

CREATE INDEX idx_assets_type
    ON assets(asset_type)
    WHERE is_deleted = 0;

CREATE INDEX idx_assets_checksum
    ON assets(checksum_sha256);
```

---

## 7. Constraints

### 7.1 CHECK Constraints

```sql
-- Status enums
ALTER TABLE users ADD CONSTRAINT chk_users_status
    CHECK (status IN ('active', 'inactive', 'suspended', 'pending'));

ALTER TABLE enrollments ADD CONSTRAINT chk_enrollments_status
    CHECK (status IN ('active', 'completed', 'dropped', 'suspended'));

ALTER TABLE attempts ADD CONSTRAINT chk_attempts_status
    CHECK (status IN ('in_progress', 'submitted', 'graded', 'voided'));

ALTER TABLE plugins ADD CONSTRAINT chk_plugins_status
    CHECK (status IN ('active', 'deprecated', 'disabled', 'error'));

-- Score ranges
ALTER TABLE results ADD CONSTRAINT chk_results_score
    CHECK (score >= 0 AND score <= 100);

ALTER TABLE progress ADD CONSTRAINT chk_progress_percentage
    CHECK (percentage >= 0 AND percentage <= 100);

-- Non-negative values
ALTER TABLE questions ADD CONSTRAINT chk_questions_points
    CHECK (points > 0);

ALTER TABLE assessments ADD CONSTRAINT chk_assessments_max_score
    CHECK (max_score > 0);

-- Date logic
ALTER TABLE sessions ADD CONSTRAINT chk_sessions_dates
    CHECK (ended_at IS NULL OR ended_at >= started_at);

ALTER TABLE learning_sessions ADD CONSTRAINT chk_ls_dates
    CHECK (ended_at IS NULL OR ended_at >= started_at);

-- Version positive
ALTER TABLE users ADD CONSTRAINT chk_users_version
    CHECK (version > 0);

-- Sort order non-negative
ALTER TABLE course_modules ADD CONSTRAINT chk_cm_order
    CHECK (sort_order >= 0);

ALTER TABLE lessons ADD CONSTRAINT chk_lessons_order
    CHECK (sort_order >= 0);
```

### 7.2 UNIQUE Constraints

```sql
-- Natural keys
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
ALTER TABLE roles ADD CONSTRAINT uq_roles_name UNIQUE (name);
ALTER TABLE permissions ADD CONSTRAINT uq_permissions_name UNIQUE (name);
ALTER TABLE configurations ADD CONSTRAINT uq_config_key UNIQUE (config_key);
ALTER TABLE feature_flags ADD CONSTRAINT uq_feature_flag_name UNIQUE (flag_name);
ALTER TABLE localization_keys ADD CONSTRAINT uq_loc_key UNIQUE (key);
ALTER TABLE plugins ADD CONSTRAINT uq_plugin_name UNIQUE (name);
ALTER TABLE certificates ADD CONSTRAINT uq_cert_number UNIQUE (certificate_number);

-- Composite unique
ALTER TABLE user_roles ADD CONSTRAINT uq_user_role UNIQUE (user_id, role_id);
ALTER TABLE role_permissions ADD CONSTRAINT uq_role_permission UNIQUE (role_id, permission_id);
ALTER TABLE org_memberships ADD CONSTRAINT uq_org_member UNIQUE (organization_id, user_id);
ALTER TABLE enrollments ADD CONSTRAINT uq_enrollment UNIQUE (user_id, course_id);
ALTER TABLE user_competencies ADD CONSTRAINT uq_user_competency UNIQUE (user_id, competency_id);
ALTER TABLE settings ADD CONSTRAINT uq_user_setting UNIQUE (user_id, setting_key);
```

### 7.3 NOT NULL Constraints

Every table enforces NOT NULL on:
- Primary key (`id`)
- `created_at` (always set on insert)
- `version` (always starts at 1)
- `is_deleted` (defaults to false)
- Domain-specific required fields (see SCHEMA_SPECIFICATION.md)

### 7.4 DEFAULT Values

```sql
-- Common defaults
id              BLOB(16)      -- Generated by application (UUID4)
created_at      DATETIME      DEFAULT CURRENT_TIMESTAMP
updated_at      DATETIME      DEFAULT CURRENT_TIMESTAMP
is_deleted      BOOLEAN       DEFAULT 0
deleted_at      DATETIME      DEFAULT NULL
version         INTEGER       DEFAULT 1
created_by      BLOB(16)      DEFAULT NULL
updated_by      BLOB(16)      DEFAULT NULL

-- Domain defaults
status          VARCHAR(50)   DEFAULT 'active'
sort_order      INTEGER       DEFAULT 0
score           REAL          DEFAULT 0.0
percentage      REAL          DEFAULT 0.0
is_read         BOOLEAN       DEFAULT 0
is_enabled      BOOLEAN       DEFAULT 1
```

---

## 8. Relationships

### 8.1 One-to-One (1:1)

| Parent | Child | FK Column | Constraint |
|---|---|---|---|
| User | Accessibility Profile | `user_id` | UNIQUE |
| User | Credential | `user_id` | UNIQUE |
| Organization | Institution | `organization_id` | UNIQUE |
| Attempt | Result | `attempt_id` | UNIQUE |
| AuditEntry | AuditChain | `entry_id` | UNIQUE |

### 8.2 One-to-Many (1:N)

| Parent | Child | FK Column | On Delete |
|---|---|---|---|
| User | Sessions | `user_id` | CASCADE |
| User | Enrollments | `user_id` | RESTRICT |
| User | Certificates | `user_id` | RESTRICT |
| User | Notifications | `user_id` | CASCADE |
| User | AuditEntries | `user_id` | SET NULL |
| Course | Modules | `course_id` | CASCADE |
| Course | Enrollments | `course_id` | RESTRICT |
| Course | Assessments | `course_id` | RESTRICT |
| Module | Lessons | `module_id` | CASCADE |
| Assessment | Questions | `assessment_id` | CASCADE |
| Question | Options | `question_id` | CASCADE |
| Attempt | Answers | `attempt_id` | CASCADE |
| Plugin | Versions | `plugin_id` | CASCADE |
| Plugin | Configs | `plugin_id` | CASCADE |
| Organization | Members | `organization_id` | CASCADE |
| LocalizationKey | Translations | `key_id` | CASCADE |

### 8.3 Many-to-Many (N:M)

| Entity A | Entity B | Junction Table | Extra Columns |
|---|---|---|---|
| Users | Roles | `user_roles` | `assigned_at`, `assigned_by` |
| Roles | Permissions | `role_permissions` | `granted_at`, `granted_by` |
| Users | Competencies | `user_competencies` | `level_id`, `achieved_at`, `verified_by` |
| Certificates | Competencies | `certificate_competencies` | `required_level` |
| Courses | Prerequisites | `course_prerequisites` | `required_course_id`, `minimum_grade` |
| Modules | Prerequisites | `module_prerequisites` | `required_module_id` |
| Reports | DataSources | `report_data_sources` | `source_type`, `source_config` |

---

## 9. Views for Common Queries

```sql
-- Active users with role count
CREATE VIEW v_active_users AS
SELECT
    u.id,
    u.email,
    u.display_name,
    u.status,
    u.last_login_at,
    COUNT(ur.role_id) AS role_count,
    u.created_at
FROM users u
LEFT JOIN user_roles ur ON u.id = ur.user_id AND ur.is_deleted = 0
WHERE u.is_deleted = 0 AND u.status = 'active'
GROUP BY u.id;

-- Course enrollment summary
CREATE VIEW v_course_enrollment_summary AS
SELECT
    c.id AS course_id,
    c.title AS course_title,
    c.status AS course_status,
    COUNT(e.id) AS total_enrollments,
    SUM(CASE WHEN e.status = 'active' THEN 1 ELSE 0 END) AS active_enrollments,
    SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) AS completed_enrollments,
    ROUND(
        100.0 * SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(e.id), 0), 1
    ) AS completion_rate
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id AND e.is_deleted = 0
WHERE c.is_deleted = 0
GROUP BY c.id;

-- User learning progress
CREATE VIEW v_user_learning_progress AS
SELECT
    u.id AS user_id,
    u.display_name,
    c.id AS course_id,
    c.title AS course_title,
    COUNT(DISTINCT l.id) AS total_lessons,
    COUNT(DISTINCT p.lesson_id) AS completed_lessons,
    ROUND(
        100.0 * COUNT(DISTINCT p.lesson_id) / 
        NULLIF(COUNT(DISTINCT l.id), 0), 1
    ) AS progress_percentage
FROM users u
JOIN enrollments e ON u.id = e.user_id AND e.is_deleted = 0
JOIN courses c ON e.course_id = c.id AND c.is_deleted = 0
JOIN course_modules cm ON c.id = cm.course_id AND cm.is_deleted = 0
JOIN lessons l ON cm.id = l.module_id AND l.is_deleted = 0
LEFT JOIN progress p ON u.id = p.user_id AND l.id = p.lesson_id AND p.is_deleted = 0
WHERE u.is_deleted = 0 AND u.status = 'active'
GROUP BY u.id, c.id;

-- Assessment results summary
CREATE VIEW v_assessment_results AS
SELECT
    a.id AS assessment_id,
    a.title AS assessment_title,
    c.title AS course_title,
    COUNT(atm.id) AS total_attempts,
    ROUND(AVG(r.score), 1) AS average_score,
    MIN(r.score) AS min_score,
    MAX(r.score) AS max_score,
    SUM(CASE WHEN r.score >= a.passing_score THEN 1 ELSE 0 END) AS passed_count,
    ROUND(
        100.0 * SUM(CASE WHEN r.score >= a.passing_score THEN 1 ELSE 0 END) / 
        NULLIF(COUNT(atm.id), 0), 1
    ) AS pass_rate
FROM assessments a
JOIN courses c ON a.course_id = c.id AND c.is_deleted = 0
LEFT JOIN attempts atm ON a.id = atm.assessment_id AND atm.is_deleted = 0 AND atm.status = 'graded'
LEFT JOIN results r ON atm.id = r.attempt_id AND r.is_deleted = 0
WHERE a.is_deleted = 0
GROUP BY a.id;

-- Plugin health dashboard
CREATE VIEW v_plugin_dashboard AS
SELECT
    p.id AS plugin_id,
    p.name AS plugin_name,
    p.status,
    pv.version AS latest_version,
    p.installed_at,
    p.last_activated_at,
    COUNT(ph.id) AS hook_count,
    COUNT(pc.id) AS config_count
FROM plugins p
LEFT JOIN plugin_versions pv ON p.id = pv.plugin_id AND pv.is_deleted = 0
LEFT JOIN plugin_hooks ph ON p.id = ph.plugin_id AND ph.is_deleted = 0
LEFT JOIN plugin_configs pc ON p.id = pc.plugin_id AND pc.is_deleted = 0
WHERE p.is_deleted = 0
GROUP BY p.id;

-- Recent audit activity
CREATE VIEW v_recent_audit AS
SELECT
    ae.id,
    ae.timestamp,
    u.display_name AS actor_name,
    ae.action,
    ae.entity_type,
    ae.entity_id,
    ae.ip_address,
    ae.metadata
FROM audit_entries ae
LEFT JOIN users u ON ae.user_id = u.id
WHERE ae.is_deleted = 0
ORDER BY ae.timestamp DESC
LIMIT 1000;

-- Notification delivery stats
CREATE VIEW v_notification_stats AS
SELECT
    n.user_id,
    u.display_name,
    COUNT(*) AS total_notifications,
    SUM(CASE WHEN n.is_read = 0 THEN 1 ELSE 0 END) AS unread_count,
    MAX(n.created_at) AS latest_notification
FROM notifications n
JOIN users u ON n.user_id = u.id AND u.is_deleted = 0
WHERE n.is_deleted = 0
GROUP BY n.user_id;

-- Competency leaderboard
CREATE VIEW v_competency_leaderboard AS
SELECT
    u.id AS user_id,
    u.display_name,
    comp.name AS competency_name,
    cl.label AS level_label,
    cl.order_index AS level_order,
    uc.achieved_at
FROM user_competencies uc
JOIN users u ON uc.user_id = u.id AND u.is_deleted = 0
JOIN competencies comp ON uc.competency_id = comp.id AND comp.is_deleted = 0
JOIN competency_levels cl ON uc.level_id = cl.id AND cl.is_deleted = 0
WHERE uc.is_deleted = 0
ORDER BY comp.name, cl.order_index DESC, uc.achieved_at ASC;

-- Backup status overview
CREATE VIEW v_backup_status AS
SELECT
    br.id,
    br.backup_type,
    br.status,
    br.file_size_bytes,
    br.checksum_sha256,
    br.created_at,
    br.completed_at,
    br.error_message,
    bs.schedule_name
FROM backup_records br
LEFT JOIN backup_schedules bs ON br.schedule_id = bs.id
WHERE br.is_deleted = 0
ORDER BY br.created_at DESC
LIMIT 100;
```

---

## 10. Migration Strategy

### 10.1 Alembic Async Configuration

```python
# alembic.ini
[alembic]
script_location = migrations
sqlalchemy.url = sqlite+aiosqlite:///./data/authshield.db
```

```python
# migrations/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 10.2 Migration Naming Convention

```
migrations/
  ├── alembic.ini
  ├── env.py
  ├── script.py.mako
  └── versions/
      ├── 001_initial_schema.py
      ├── 002_add_mfa_factors.py
      ├── 003_add_competencies.py
      ├── 004_add_plugins.py
      ├── 005_add_localization.py
      ├── 006_add_accessibility.py
      ├── 007_add_analytics.py
      ├── 008_add_backup_system.py
      ├── 009_enhance_audit_chain.py
      └── ...
```

### 10.3 Migration Validation

Every migration includes:

```python
def upgrade() -> None:
    # Forward migration
    op.create_table(...)
    
    # Post-migration validation
    connection = op.get_bind()
    result = connection.execute(text("SELECT COUNT(*) FROM new_table"))
    assert result.scalar() >= 0, "Validation failed: new_table empty or error"

def downgrade() -> None:
    # Reverse migration
    op.drop_table(...)
```

---

## 11. Performance Pragmas & Optimization

### 11.1 Query Performance Guidelines

| Guideline | Rationale |
|---|---|
| Use partial indexes | Smaller indexes for filtered queries |
| Composite index column order | Most selective/filtered columns first |
| Avoid SELECT * | Only select needed columns |
| Use covering indexes | For frequently accessed column combinations |
| Batch inserts | Use executemany for bulk operations |
| Connection pooling | Reuse connections via SQLAlchemy pool |

### 11.2 SQLite-Specific Optimizations

```sql
-- Analyze tables after significant data changes
ANALYZE;

-- Optimize database file (reclaim space)
VACUUM;

-- Incremental vacuum (keep last N pages)
PRAGMA incremental_vacuum(1000);

-- Reindex all indexes
REINDEX;
```

### 11.3 Monitoring Queries

```sql
-- Table sizes
SELECT name, 
       (page_count * page_size) / 1024.0 AS size_kb
FROM pragma_page_count(), pragma_page_size(), sqlite_master
WHERE type = 'table';

-- Index usage statistics
SELECT name, 
       (SELECT COUNT(*) FROM sqlite_stat1 WHERE idx = sqlite_master.name) AS usage_count
FROM sqlite_master
WHERE type = 'index';

-- Slow query identification (requires application-level logging)
-- Track via audit_entries with action = 'query_slow'
```

---

## 12. Version Compatibility

| SQLite Version | AuthShield Lab Version | Notes |
|---|---|---|
| 3.35.0+ | v1.0+ | Minimum supported version |
| 3.40.0+ | v2.0+ | Required for enhanced JSON support |
| 3.45.0+ | v2.5+ | Recommended for performance improvements |

### 12.1 Schema Version Tracking

```sql
-- Alembic version table (auto-managed)
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Application version table (manual management)
CREATE TABLE schema_metadata (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_metadata (key, value) VALUES
    ('schema_version', '2.0.0'),
    ('min_sqlite_version', '3.35.0'),
    ('created_at', CURRENT_TIMESTAMP);
```

---

## 13. Data Integrity Guarantees

### 13.1 Application-Level Integrity

- UUID generation via `uuid.uuid4()` — collision-resistant
- Soft deletes prevent orphaned foreign key references
- Optimistic locking via `version` column prevents lost updates
- Audit chain hash verification prevents tampering

### 13.2 Database-Level Integrity

- Foreign key constraints enforced (PRAGMA foreign_keys = ON)
- CHECK constraints validate domain invariants
- UNIQUE constraints prevent duplicate natural keys
- NOT NULL constraints enforce required fields
- WAL mode ensures crash recovery without data loss

### 13.3 Backup Integrity

- SHA-256 checksums on every backup file
- Pre-backup VACUUM for consistency
- Post-restore integrity_check PRAGMA
- Backup chain verification (incremental builds on parent checksum)

---

*This document defines the complete physical and logical database design for AuthShield Lab.*
