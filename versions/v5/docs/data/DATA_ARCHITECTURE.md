# Enterprise Data Architecture — AuthShield Lab

> Version 2.0 · Classification: INTERNAL · Last Updated: 2026-07-19

## 1. Overview

This document defines the complete enterprise data architecture for AuthShield Lab,
a cybersecurity education platform built on Python 3.12+ / FastAPI / SQLAlchemy 2.0
(async) / SQLite. The architecture governs how data is classified, stored, related,
retained, versioned, and secured across all 20+ functional domains.

### 1.1 Design Principles

| Principle | Description |
|---|---|
| Local-first | All data resides on the user's machine in SQLite. No cloud dependency. |
| Offline-capable | Full functionality without network. Sync queue for future multi-device. |
| UUID identity | Every aggregate root uses `uuid.UUID` primary keys. No sequential leaks. |
| Soft deletes | Records are never hard-deleted by default. `is_deleted` + `deleted_at`. |
| Audit everything | Every mutation produces an audit entry with actor, timestamp, diff. |
| Schema per context | Each bounded context owns its own SQLAlchemy model namespace. |
| Encrypted at rest | SQLCipher wraps sensitive databases. Argon2id for credentials. |

### 1.2 Technology Stack

| Layer | Technology |
|---|---|
| Database engine | SQLite 3.45+ (WAL mode, foreign keys enforced) |
| ORM | SQLAlchemy 2.0 async (asyncio + aiosqlite) |
| Migrations | Alembic (async revision chain) |
| Serialization | Pydantic v2 models, msgpack for offline queue |
| Backup | Custom backup manager (see BACKUP_RESTORE.md) |
| Encryption | SQLCipher 4.x / AES-256-CBC for backup files |

---

## 2. Data Domain Catalog

### 2.1 Identity Domain

| Attribute | Value |
|---|---|
| **Purpose** | Core user identity, authentication credentials, MFA state |
| **Ownership** | Identity bounded context (`authshield.identity`) |
| **Key Entities** | `users`, `credentials`, `mfa_factors`, `identity_providers` |
| **Relationships** | Users → Roles (N:M), Users → Sessions (1:N), Users → Audit (1:N) |
| **Retention** | Lifetime of account + 7 years post-deactivation |
| **Archival** | Compressed archive after 2 years of inactivity |
| **Versioning** | Full history via `audit_entries` with `old_value`/`new_value` |
| **Privacy** | PII — email, display name encrypted at rest |
| **Security** | CLASSIFICATION_SECRET — Argon2id password hashing, TOTP/HOTP MFA |

### 2.2 Roles & Permissions Domain

| Attribute | Value |
|---|---|
| **Purpose** | Authorization model: roles, permissions, RBAC enforcement |
| **Ownership** | Authorization bounded context (`authshield.authorization`) |
| **Key Entities** | `roles`, `permissions`, `user_roles`, `role_permissions` |
| **Relationships** | Roles → Permissions (N:M), Users → Roles (N:M) |
| **Retention** | Lifetime of platform. Inactive roles archived after 1 year. |
| **Archival** | Soft-deleted roles retained indefinitely for audit trace. |
| **Versioning** | Permission changes tracked via audit log with before/after diff. |
| **Privacy** | Internal — role names not PII but access patterns sensitive. |
| **Security** | CLASSIFICATION_CONFIDENTIAL — permission changes require admin auth. |

### 2.3 Organizations Domain

| Attribute | Value |
|---|---|
| **Purpose** | Institutional hierarchy: organizations, departments, teams |
| **Ownership** | Organization bounded context (`authshield.organization`) |
| **Key Entities** | `organizations`, `org_memberships`, `org_settings` |
| **Relationships** | Org → Users (1:N), Org → Courses (1:N), Org → Institutions (1:1) |
| **Retention** | Lifetime of organization + 5 years post-dissolution |
| **Archival** | Full org export to JSON before archival. Original soft-deleted. |
| **Versioning** | Org metadata versioned via audit. Settings snapshots. |
| **Privacy** | CLASSIFICATION_CONFIDENTIAL — org names, membership lists. |
| **Security** | Org-scoped data isolation. Cross-org access prohibited. |

### 2.4 Institutions Domain

| Attribute | Value |
|---|---|
| **Purpose** | Educational institutions: schools, universities, training centers |
| **Ownership** | Institution bounded context (`authshield.institution`) |
| **Key Entities** | `institutions`, `institution_members`, `institution_config` |
| **Relationships** | Institution → Org (1:1), Institution → Courses (1:N), Institution → Students (1:N) |
| **Retention** | 10 years post-student-record requirement (regulatory) |
| **Archival** | Annual archival of completed cohorts to compressed archive. |
| **Versioning** | Institutional config versioned. Student records immutable once certified. |
| **Privacy** | CLASSIFICATION_RESTRICTED — student PII, grades, completion records. |
| **Security** | FERPA-aware design. Minimum necessary access principle. |

### 2.5 Courses Domain

| Attribute | Value |
|---|---|
| **Purpose** | Course definitions, structure, metadata, enrollment rules |
| **Ownership** | Learning bounded context (`authshield.learning`) |
| **Key Entities** | `courses`, `course_modules`, `enrollments`, `course_prerequisites` |
| **Relationships** | Course → Modules (1:N), Course → Lessons (1:N), Course → Enrollments (1:N) |
| **Retention** | Active courses: indefinite. Archived courses: 5 years. |
| **Archival** | Course export (SCORM-compatible) before archival. |
| **Versioning** | Semantic versioning on course content. Draft/published lifecycle. |
| **Privacy** | CLASSIFICATION_INTERNAL — course content not PII. |
| **Security** | Enrollment-gated access. Content integrity checksums. |

### 2.6 Lessons Domain

| Attribute | Value |
|---|---|
| **Purpose** | Individual learning units within course modules |
| **Ownership** | Learning bounded context (`authshield.learning`) |
| **Key Entities** | `lessons`, `lesson_content`, `lesson_resources` |
| **Relationships** | Lesson → Module (N:1), Lesson → Content (1:N), Lesson → Progress (1:N) |
| **Retention** | Tied to course retention policy. |
| **Archival** | Bundled with course archive. |
| **Versioning** | Content versioned with minor/major bumps. Diffs tracked. |
| **Privacy** | CLASSIFICATION_INTERNAL. |
| **Security** | Content integrity SHA-256 checksums on publish. |

### 2.7 Modules Domain

| Attribute | Value |
|---|---|
| **Purpose** | Logical grouping of lessons within a course |
| **Ownership** | Learning bounded context (`authshield.learning`) |
| **Key Entities** | `modules`, `module_prerequisites`, `module_metadata` |
| **Relationships** | Module → Course (N:1), Module → Lessons (1:N) |
| **Retention** | Tied to parent course. |
| **Archival** | Bundled with course archive. |
| **Versioning** | Tied to course version. |
| **Privacy** | CLASSIFICATION_INTERNAL. |
| **Security** | Module ordering integrity enforced by constraints. |

### 2.8 Learning Sessions Domain

| Attribute | Value |
|---|---|
| **Purpose** | Tracks active learning sessions, time spent, progress checkpoints |
| **Ownership** | Learning bounded context (`authshield.learning`) |
| **Key Entities** | `learning_sessions`, `session_checkpoints`, `time_logs` |
| **Relationships** | Session → User (N:1), Session → Course (N:1), Session → Progress (1:N) |
| **Retention** | 2 years active, then archived. |
| **Archival** | Aggregated into analytics before archival. Raw data compressed. |
| **Versioning** | Append-only time log entries. |
| **Privacy** | CLASSIFICATION_CONFIDENTIAL — learning behavior patterns. |
| **Security** | Session data access limited to session owner + admin. |

### 2.9 Assessments Domain

| Attribute | Value |
|---|---|
| **Purpose** | Quizzes, exams, practical exercises, competency evaluations |
| **Ownership** | Assessment bounded context (`authshield.assessment`) |
| **Key Entities** | `assessments`, `assessment_configs`, `assessment_attempts` |
| **Relationships** | Assessment → Questions (1:N), Assessment → Course (N:1), Assessment → Results (1:N) |
| **Retention** | 5 years for completed assessments. Active: indefinite. |
| **Archival** | Results aggregated, raw attempts compressed after 2 years. |
| **Versioning** | Assessment versions for content changes. Attempt records immutable. |
| **Privacy** | CLASSIFICATION_RESTRICTED — scores, answers, timing data. |
| **Security** | Anti-cheating metadata. Attempt integrity checksums. |

### 2.10 Questions Domain

| Attribute | Value |
|---|---|
| **Purpose** | Question bank: MCQ, practical, code review, scenario-based |
| **Ownership** | Assessment bounded context (`authshield.assessment`) |
| **Key Entities** | `questions`, `question_options`, `question_metadata` |
| **Relationships** | Question → Assessment (N:1), Question → Answers (1:N) |
| **Retention** | Indefinite for question bank. Retired questions soft-deleted. |
| **Archival** | Question bank export before major version bumps. |
| **Versioning** | Question content versioned. Difficulty ratings updated. |
| **Privacy** | CLASSIFICATION_CONFIDENTIAL — question content is exam-sensitive. |
| **Security** | Question bank access restricted to assessment designers. |

### 2.11 Attempts & Results Domain

| Attribute | Value |
|---|---|
| **Purpose** | Student attempt records, scoring, grading, feedback |
| **Ownership** | Assessment bounded context (`authshield.assessment`) |
| **Key Entities** | `attempts`, `answers`, `results`, `feedback` |
| **Relationships** | Attempt → User (N:1), Attempt → Assessment (N:1), Result → Attempt (1:1) |
| **Retention** | 7 years (regulatory compliance for educational records). |
| **Archival** | Annual archival of completed attempt data. |
| **Versioning** | Attempts are immutable once submitted. Results may be amended (with audit). |
| **Privacy** | CLASSIFICATION_RESTRICTED — student performance data. |
| **Security** | Attempt data encrypted. Access limited to student + instructor + admin. |

### 2.12 Competencies Domain

| Attribute | Value |
|---|---|
| **Purpose** | Skill tracking, competency frameworks, proficiency levels |
| **Ownership** | Learning bounded context (`authshield.learning`) |
| **Key Entities** | `competencies`, `competency_levels`, `user_competencies` |
| **Relationships** | Competency → Levels (1:N), User → Competencies (N:M) |
| **Retention** | Indefinite for framework. User competency: lifetime + 5 years. |
| **Archival** | Competency snapshots for historical tracking. |
| **Versioning** | Framework versioned. User progress append-only. |
| **Privacy** | CLASSIFICATION_CONFIDENTIAL — skill proficiency is personal. |
| **Security** | Competency records tamper-evident (hash chain). |

### 2.13 Certificates Domain

| Attribute | Value |
|---|---|
| **Purpose** | Completion certificates, badges, credentials |
| **Ownership** | Learning bounded context (`authshield.learning`) |
| **Key Entities** | `certificates`, `certificate_templates`, `credential_wallet` |
| **Relationships** | Certificate → User (N:1), Certificate → Course (N:1), Certificate → Competencies (N:M) |
| **Retention** | Indefinite — certificates must not expire in records. |
| **Archival** | Never archived. Permanent retention. |
| **Versioning** | Certificate records immutable once issued. Revocation creates new record. |
| **Privacy** | CLASSIFICATION_PUBLIC (certificate itself) / RESTRICTED (verification data). |
| **Security** | Cryptographic signature on certificate data. Tamper-evident. |

### 2.14 Plugins Domain

| Attribute | Value |
|---|---|
| **Purpose** | Plugin registry, versions, configuration, lifecycle |
| **Ownership** | Extension bounded context (`authshield.extension`) |
| **Key Entities** | `plugins`, `plugin_versions`, `plugin_configs`, `plugin_hooks` |
| **Relationships** | Plugin → Versions (1:N), Plugin → Config (1:N), Plugin → Hooks (1:N) |
| **Retention** | Indefinite for registry. Deprecated plugins retained 2 years. |
| **Archival** | Plugin archive with code + metadata on deprecation. |
| **Versioning** | Semantic versioning. Full version history retained. |
| **Privacy** | CLASSIFICATION_INTERNAL. |
| **Security** | Plugin code integrity verification. Sandboxed execution. |

### 2.15 Configuration Domain

| Attribute | Value |
|---|---|
| **Purpose** | System settings, feature flags, environment configuration |
| **Ownership** | Platform bounded context (`authshield.platform`) |
| **Key Entities** | `configurations`, `settings`, `feature_flags`, `env_config` |
| **Relationships** | Config → Settings (1:N), Config → FeatureFlags (1:N) |
| **Retention** | Active: indefinite. Historical: 2 years of config change history. |
| **Archival** | Config snapshots exported before major changes. |
| **Versioning** | Every config change creates a new versioned entry. |
| **Privacy** | CLASSIFICATION_CONFIDENTIAL — may contain secrets/keys. |
| **Security** | Secret values encrypted at rest. Config changes audited. |

### 2.16 Themes Domain

| Attribute | Value |
|---|---|
| **Purpose** | UI themes, color schemes, branding customization |
| **Ownership** | Presentation bounded context (`authshield.presentation`) |
| **Key Entities** | `themes`, `theme_variables`, `theme_assets` |
| **Relationships** | Theme → Variables (1:N), Theme → Assets (1:N), Theme → Org (N:1) |
| **Retention** | Indefinite for active themes. Deleted themes: 1 year. |
| **Archival** | Theme export (JSON + assets) on deprecation. |
| **Versioning** | Theme versions with preview snapshots. |
| **Privacy** | CLASSIFICATION_INTERNAL. |
| **Security** | Theme assets scanned for malicious content. |

### 2.17 Localization Domain

| Attribute | Value |
|---|---|
| **Purpose** | Internationalization: language packs, translations, regional settings |
| **Ownership** | Platform bounded context (`authshield.platform`) |
| **Key Entities** | `localization_keys`, `translations`, `language_packs`, `regional_settings` |
| **Relationships** | LangPack → Translations (1:N), LangPack → RegionalSettings (1:1) |
| **Retention** | Indefinite for active packs. Deprecated: 2 years. |
| **Archival** | Full language pack export before deprecation. |
| **Versioning** | Translation versions with completion tracking. |
| **Privacy** | CLASSIFICATION_INTERNAL. |
| **Security** | Translation integrity checksums. |

### 2.18 Accessibility Profiles Domain

| Attribute | Value |
|---|---|
| **Purpose** | User accessibility preferences, assistive technology configs |
| **Ownership** | Presentation bounded context (`authshield.presentation`) |
| **Key Entities** | `accessibility_profiles`, `a11y_settings`, `a11y_presets` |
| **Relationships** | Profile → User (N:1), Profile → Settings (1:N) |
| **Retention** | Lifetime of user account. |
| **Archival** | Exported with user data package. |
| **Versioning** | Profile changes tracked via audit. |
| **Privacy** | CLASSIFICATION_CONFIDENTIAL — disability-related data is sensitive. |
| **Security** | Accessibility data never shared. Local-only processing. |

### 2.19 Notifications Domain

| Attribute | Value |
|---|---|
| **Purpose** | In-app notifications, alerts, system messages |
| **Ownership** | Platform bounded context (`authshield.platform`) |
| **Key Entities** | `notifications`, `notification_templates`, `notification_preferences` |
| **Relationships** | Notification → User (N:1), Notification → Template (N:1) |
| **Retention** | 90 days active. Archived after 1 year. Purged after 2 years. |
| **Archival** | Notification history compressed and archived. |
| **Versioning** | Notifications are immutable once sent. |
| **Privacy** | CLASSIFICATION_INTERNAL — notification content may contain PII. |
| **Security** | Notification delivery verified. No sensitive data in push notifications. |

### 2.20 Reports & Analytics Domain

| Attribute | Value |
|---|---|
| **Purpose** | Generated reports, analytics data, dashboards, aggregations |
| **Ownership** | Analytics bounded context (`authshield.analytics`) |
| **Key Entities** | `reports`, `report_templates`, `analytics_snapshots`, `dashboards` |
| **Relationships** | Report → User (N:1), Report → DataSources (N:M), Analytics → Course (N:1) |
| **Retention** | Generated reports: 1 year. Analytics snapshots: 3 years. |
| **Archival** | Reports compressed and archived after retention period. |
| **Versioning** | Report templates versioned. Report outputs immutable. |
| **Privacy** | CLASSIFICATION_CONFIDENTIAL — aggregated user performance data. |
| **Security** | Report generation access-controlled. PII anonymized in aggregates. |

### 2.21 Audit Logs Domain

| Attribute | Value |
|---|---|
| **Purpose** | Comprehensive audit trail for all system mutations |
| **Ownership** | Security bounded context (`authshield.security`) |
| **Key Entities** | `audit_entries`, `audit_chains`, `audit_archives` |
| **Relationships** | AuditEntry → User (N:1), AuditEntry → Entity (polymorphic) |
| **Retention** | 7 years default (configurable per entry type). |
| **Archival** | Annual archival to compressed, checksummed archive files. |
| **Versioning** | Append-only. Hash chain for tamper detection. |
| **Privacy** | CLASSIFICATION_SECRET — audit logs reveal access patterns. |
| **Security** | Hash chain integrity. Write-once storage semantics. No soft-delete. |

### 2.22 Security Events Domain

| Attribute | Value |
|---|---|
| **Purpose** | Security incident tracking, threat detection, intrusion logging |
| **Ownership** | Security bounded context (`authshield.security`) |
| **Key Entities** | `security_events`, `threat_indicators`, `incident_reports` |
| **Relationships** | SecurityEvent → User (N:1), Incident → Events (1:N) |
| **Retention** | 10 years for security events. Incidents: permanent. |
| **Archival** | Encrypted archive with integrity verification. |
| **Versioning** | Append-only. Event records immutable. |
| **Privacy** | CLASSIFICATION_SECRET — security events are highly sensitive. |
| **Security** | Encrypted at rest. Access limited to security admin. Hash chain. |

### 2.23 Backups Domain

| Attribute | Value |
|---|---|
| **Purpose** | Backup metadata, restore points, backup verification records |
| **Ownership** | Platform bounded context (`authshield.platform`) |
| **Key Entities** | `backup_records`, `backup_schedules`, `restore_logs` |
| **Relationships** | Backup → Schedule (N:1), Restore → Backup (N:1) |
| **Retention** | Backup metadata: lifetime. Backup files: per rotation policy (3-2-1). |
| **Archival** | Backup files are themselves the archival mechanism. |
| **Versioning** | Backup records immutable. Restore logs append-only. |
| **Privacy** | CLASSIFICATION_SECRET — backups contain full database. |
| **Security** | AES-256 encrypted. SHA-256 integrity verified. Secure deletion. |

### 2.24 Diagnostics Domain

| Attribute | Value |
|---|---|
| **Purpose** | System health, performance metrics, error logs, crash reports |
| **Ownership** | Platform bounded context (`authshield.platform`) |
| **Key Entities** | `diagnostic_logs`, `performance_metrics`, `error_reports`, `health_checks` |
| **Relationships** | DiagnosticLog → Session (N:1), Metric → Component (N:1) |
| **Retention** | 30 days active. 1 year archived. |
| **Archival** | Aggregated into performance reports before archival. |
| **Versioning** | Append-only log entries. |
| **Privacy** | CLASSIFICATION_INTERNAL — may contain stack traces, system info. |
| **Security** | Diagnostic data never leaves the local machine. |

### 2.25 Assets & Media Domain

| Attribute | Value |
|---|---|
| **Purpose** | File storage metadata, media references, binary asset management |
| **Ownership** | Content bounded context (`authshield.content`) |
| **Key Entities** | `assets`, `media_metadata`, `file_references`, `asset_versions` |
| **Relationships** | Asset → Course (N:1), Asset → Lesson (N:1), Asset → Versions (1:N) |
| **Retention** | Tied to parent content retention policy. |
| **Archival** | Bundled with parent content archive. |
| **Versioning** | Asset versions tracked. Previous versions retained. |
| **Privacy** | CLASSIFICATION varies by asset content. |
| **Security** | File integrity checksums. Malware scanning on upload. |

---

## 3. Data Domain Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AuthShield Lab Data Architecture                     │
└─────────────────────────────────────────────────────────────────────────────┘

 ┌──────────┐    N:M     ┌──────────┐    N:M     ┌──────────────┐
 │  USERS   │◄──────────►│  ROLES   │◄──────────►│ PERMISSIONS  │
 └────┬─────┘            └──────────┘            └──────────────┘
      │
      ├──── 1:N ────► ┌──────────┐
      │               │ SESSIONS │──── 1:N ────► ┌──────────┐
      │               └──────────┘               │ PROGRESS │
      │                                          └──────────┘
      ├──── 1:N ────► ┌──────────┐    1:N      ┌──────────┐
      │               │ ATTEMPTS │──────────────►│ RESULTS  │
      │               └──────────┘              └──────────┘
      │
      ├──── 1:N ────► ┌───────────────┐  N:M   ┌──────────────┐
      │               │ CERTIFICATES  │◄──────►│COMPETENCIES  │
      │               └───────────────┘        └──────────────┘
      │
      ├──── N:1 ────► ┌───────────────┐
      │               │ ORGANIZATIONS │──── 1:1 ───► ┌──────────────┐
      │               └───────────────┘              │ INSTITUTIONS │
      │                                              └──────────────┘
      ├──── 1:N ────► ┌───────────────┐
      │               │  COURSES      │
      │               └───────┬───────┘
      │                       │ 1:N
      │               ┌───────▼───────┐
      │               │    MODULES    │
      │               └───────┬───────┘
      │                       │ 1:N
      │               ┌───────▼───────┐
      │               │    LESSONS    │
      │               └───────────────┘
      │
      ├──── 1:N ────► ┌───────────────┐
      │               │  ENROLLMENTS  │
      │               └───────────────┘
      │
      └──── 1:N ────► ┌───────────────┐
                      │  NOTIFICATIONS│
                      └───────────────┘

 ┌──────────────┐    1:N    ┌──────────┐    1:N    ┌──────────────┐
 │ ASSESSMENTS  │──────────►│QUESTIONS │──────────►│   ANSWERS    │
 └──────────────┘           └──────────┘           └──────────────┘

 ┌──────────────┐    1:N    ┌──────────────────┐
 │   PLUGINS    │──────────►│ PLUGIN_VERSIONS  │
 └──────────────┘           └──────────────────┘

 ┌──────────────┐    1:N    ┌──────────────────┐
 │CONFIGURATIONS│──────────►│    SETTINGS      │
 └──────────────┘           └──────────────────┘

 ┌──────────────┐    1:N    ┌──────────────────┐
 │    THEMES    │──────────►│ THEME_VARIABLES  │
 └──────────────┘           └──────────────────┘

 ┌──────────────────┐  1:N  ┌──────────────┐
 │LOCALIZATION_KEYS │──────►│ TRANSLATIONS │
 └──────────────────┘       └──────────────┘

 ┌──────────────────┐  1:N  ┌──────────────────┐
 │  AUDIT_ENTRIES   │──────►│   AUDIT_CHAINS   │
 └──────────────────┘       └──────────────────┘

 ┌──────────────────┐  1:N  ┌──────────────────┐
 │ SECURITY_EVENTS  │──────►│ INCIDENT_REPORTS │
 └──────────────────┘       └──────────────────┘

 ┌──────────────────┐  1:N  ┌──────────────────┐
 │  BACKUP_RECORDS  │──────►│   RESTORE_LOGS   │
 └──────────────────┘       └──────────────────┘

 ┌──────────┐    1:N    ┌──────────────────┐
 │  ASSETS  │──────────►│ ASSET_VERSIONS   │
 └──────────┘           └──────────────────┘
```

---

## 4. Cross-Domain Data Flow

### 4.1 Authentication Flow

```
User Request → Session Creation → Audit Entry → Notification (optional)
     │              │                  │
     ▼              ▼                  ▼
 credentials   sessions         audit_entries
 mfa_factors   learning_sessions security_events (on failure)
```

### 4.2 Learning Flow

```
Enrollment → Course Access → Lesson Progress → Assessment → Results → Certificate
    │            │               │                 │           │          │
    ▼            ▼               ▼                 ▼           ▼          ▼
enrollments  progress      learning_sessions  attempts   results   certificates
                                             questions  answers   competencies
```

### 4.3 Administrative Flow

```
Config Change → Audit Entry → Notification → Backup (if critical)
     │              │              │
     ▼              ▼              ▼
configurations  audit_entries  notifications
settings                        backup_records
```

---

## 5. Data Classification Matrix

| Classification | Description | Domains | Encryption |
|---|---|---|---|
| **SECRET** | Highest sensitivity. Direct security impact. | Identity, Audit Logs, Security Events, Backups, Config (secrets) | SQLCipher + AES-256 |
| **RESTRICTED** | Sensitive data with regulatory requirements. | Institutions, Attempts/Results, Student Records | SQLCipher field-level |
| **CONFIDENTIAL** | Internal sensitive data. | Roles/Permissions, Organizations, Sessions, Competencies, Reports, Accessibility, Config | SQLCipher database |
| **INTERNAL** | Internal use only. Not for external sharing. | Courses, Lessons, Modules, Plugins, Themes, Localization, Notifications, Diagnostics | SQLite WAL encryption |
| **PUBLIC** | Non-sensitive. May be shared. | Certificate display data, Public course catalog | Standard SQLite |

---

## 6. Data Lifecycle States

Every entity progresses through a defined lifecycle:

```
                    ┌─────────┐
                    │  DRAFT   │
                    └────┬────┘
                         │ publish
                    ┌────▼────┐
              ┌────►│  ACTIVE  │◄────┐
              │     └────┬────┘     │
              │          │ archive  │ restore
              │     ┌────▼────┐     │
              │     │ARCHIVED │─────┘
              │     └────┬────┘
              │          │ expire
              │     ┌────▼────┐
              └─────│ RETIRED │
                    └────┬────┘
                         │ purge (after retention)
                    ┌────▼────┐
                    │ PURGED  │
                    └─────────┘
```

**Lifecycle per domain:**

| Domain | Draft → Active | Active → Archived | Archived → Retired | Retired → Purged |
|---|---|---|---|---|
| Courses | On publish | 1 year inactive | 5 years archived | Never (soft-delete) |
| Assessments | On publish | 2 years completed | 5 years archived | After retention |
| Certificates | On issue | Never | Never | Never |
| Audit Logs | On creation | 1 year | 7 years | Encrypted archive |
| Backups | On creation | Rotated per schedule | Expired per 3-2-1 | Secure delete |
| Notifications | On send | 90 days | 1 year | 2 years |
| Plugins | On install | On deprecation | 2 years deprecated | Soft-delete |

---

## 7. Schema Organization by Bounded Context

| Bounded Context | Schema Namespace | Tables |
|---|---|---|
| `authshield.identity` | identity | users, credentials, mfa_factors |
| `authshield.authorization` | authorization | roles, permissions, user_roles, role_permissions |
| `authshield.organization` | organization | organizations, org_memberships, org_settings |
| `authshield.institution` | institution | institutions, institution_members, institution_config |
| `authshield.learning` | learning | courses, course_modules, lessons, enrollments, progress, learning_sessions, competencies, competency_levels, user_competencies, certificates |
| `authshield.assessment` | assessment | assessments, questions, question_options, attempts, answers, results |
| `authshield.extension` | extension | plugins, plugin_versions, plugin_configs, plugin_hooks |
| `authshield.platform` | platform | configurations, settings, feature_flags, notifications, localization_keys, translations, backups |
| `authshield.presentation` | presentation | themes, theme_variables, accessibility_profiles, a11y_settings |
| `authshield.security` | security | audit_entries, audit_chains, security_events, incident_reports |
| `authshield.analytics` | analytics | reports, report_templates, analytics_snapshots, dashboards |
| `authshield.content` | content | assets, media_metadata, file_references |

---

## 8. Data Volume Estimates

| Domain | Estimated Records (Year 1) | Growth Rate | Storage Estimate |
|---|---|---|---|
| Users | 1,000 | 50%/year | 5 MB |
| Courses | 50 | 100%/year | 10 MB |
| Lessons | 500 | 100%/year | 20 MB |
| Assessments | 200 | 100%/year | 15 MB |
| Attempts | 50,000 | 200%/year | 100 MB |
| Audit Entries | 500,000 | 300%/year | 500 MB |
| Notifications | 100,000 | 150%/year | 50 MB |
| **Total Estimated** | **~1.16M rows** | | **~700 MB** |

---

## 9. Data Residency & Sovereignty

Since AuthShield Lab is localhost-only:

- **All data** resides on the user's local machine
- **No data** is transmitted to external servers by default
- **Backups** are stored locally (user-configurable external paths)
- **Future sync** (multi-device) will use end-to-end encrypted transport
- **Compliance**: GDPR, FERPA, COPPA awareness built into data model
- **Right to erasure**: Full account deletion workflow with audit trail
- **Data portability**: Export all user data in machine-readable JSON format

---

## 10. Version Control for Data

| Mechanism | Description |
|---|---|
| **UUID versioning** | Every entity has a `version` integer column, incremented on update |
| **Audit trail** | `audit_entries` stores `old_value`/`new_value` JSON diffs |
| **Hash chain** | Audit entries include `previous_hash` for tamper detection |
| **Content hashing** | Course/lesson content gets SHA-256 checksums on publish |
| **Certificate signing** | Certificates include cryptographic signature of all fields |
| **Backup checksums** | Every backup has SHA-256 integrity verification |
| **Schema versioning** | Alembic tracks schema revision chain |

---

## 11. Future Considerations

| Item | Status | Notes |
|---|---|---|
| Multi-device sync | Planned | Offline queue + CRDT merge for future |
| Cloud backup | Planned | Optional encrypted cloud backup |
| Federation | Researched | LTI integration for institutional systems |
| Blockchain certs | Researched | Immutable certificate verification |
| Real-time analytics | Planned | WebSocket-based live dashboards |
| AI-assisted learning | Researching | Adaptive assessment difficulty |

---

*This document is the authoritative reference for all data architecture decisions in AuthShield Lab.*
