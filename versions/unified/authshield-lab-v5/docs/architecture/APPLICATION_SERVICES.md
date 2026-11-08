# Application Services

## Overview

Application services sit at the center of the architecture, orchestrating use cases,
coordinating domain objects, and managing transactions. Each service is a cohesive
unit of functionality with clear responsibilities, explicit dependencies, and
consistent patterns for validation, events, logging, security, and accessibility.

---

## AuthService

### Responsibilities
- User authentication (password-based, OAuth, SAML)
- Multi-factor authentication (TOTP, SMS, email)
- Token generation, validation, rotation, and revocation
- Session management and lifecycle
- Brute force protection and account lockout
- Password reset flows

### Dependencies (Ports)
- `UserRepositoryPort` — user lookup and lockout tracking
- `AuthenticationPort` — password hashing, token operations
- `EventPublishingPort` — authentication event dispatch
- `LoggingPort` — audit trail
- `ConfigurationPort` — security policy settings
- `NotificationPort` — MFA codes, password reset emails

### Transactions
- Authentication attempt recorded atomically (success or failure + lockout update)
- Token creation and old token invalidation in single transaction
- MFA verification and session creation atomic

### Validation
- Email format validation against `Email` value object
- Password strength validation via `PasswordPolicy` domain service
- MFA code format and time-window validation
- Token format and signature verification

### Events
- `UserAuthenticated` — successful login
- `AuthenticationFailed` — failed attempt
- `SessionCreated` — new session active
- `SessionRevoked` — session terminated
- `MFAEnabled` — MFA setup completed
- `PasswordResetRequested` — reset flow initiated
- `AccountLocked` — lockout threshold reached

### Logging
- All authentication attempts logged with timestamp, IP, user agent
- Successful logins logged at INFO level
- Failed logins logged at WARNING level
- Account lockouts logged at ERROR level
- MFA challenges logged for security audit

### Security
- Passwords never logged or stored in plaintext (bcrypt cost 12)
- Tokens transmitted only over HTTPS
- Refresh tokens stored in httpOnly secure cookies
- Rate limiting: 10 login attempts per minute per IP
- Account lockout after 5 failures in 15 minutes
- Session binding to IP and user agent

### Accessibility
- Login form supports all input methods (keyboard, voice, switch)
- Error messages are descriptive and screen-reader friendly
- MFA alternatives available (TOTP for users who cannot receive SMS)
- Time-limited challenges provide extended time option

---

## UserService

### Responsibilities
- User CRUD operations
- Profile management (display name, avatar, bio)
- User preferences (theme, notifications, language)
- Account deactivation and reactivation
- User search and listing

### Dependencies (Ports)
- `UserRepositoryPort` — user persistence
- `NotificationPort` — account notifications
- `EventPublishingPort` — user lifecycle events
- `LoggingPort` — audit trail
- `ConfigurationPort` — default preferences

### Transactions
- User creation: create user + assign default role + create profile atomically
- Profile update: validate + persist + emit event atomically
- Account deactivation: deactivate + revoke sessions + notify atomically

### Validation
- Email uniqueness enforcement
- Display name: 2-100 characters, no HTML
- Bio: max 500 characters
- Avatar: valid image format, max 5MB

### Events
- `UserCreated` — new user registered
- `UserUpdated` — profile modified
- `UserDeactivated` — account disabled
- `UserReactivated` — account re-enabled
- `PreferencesUpdated` — settings changed

### Logging
- User CRUD operations logged with actor identity
- Profile changes logged with before/after values
- Account status changes logged at INFO level

### Security
- Users can only modify their own profile (admins can modify any)
- Email changes require verification
- Account deactivation requires password confirmation
- Avatar uploads scanned for malware

### Accessibility
- Profile page fully keyboard navigable
- Avatar alt text provided
- Preferences UI follows WCAG 2.1 AA

---

## CourseService

### Responsibilities
- Course creation, update, publication, archival
- Module and lesson management within courses
- Student enrollment and unenrollment
- Course catalog and search
- Course statistics and analytics

### Dependencies (Ports)
- `CourseRepositoryPort` — course persistence
- `UserRepositoryPort` — instructor/student lookup
- `NotificationPort` — enrollment notifications
- `EventPublishingPort` — course lifecycle events
- `LoggingPort` — audit trail
- `AnalyticsInputPort` — course analytics tracking

### Transactions
- Course creation: create course + create first module + assign instructor atomically
- Enrollment: check capacity + create enrollment + update count + notify atomically
- Publication: validate completeness + change status + index for search atomically

### Validation
- Title: 3-200 characters
- Description: 10-5000 characters, sanitized HTML
- Module count: 1-50
- Lesson count per module: 1-200
- Capacity: 1-500 students

### Events
- `CourseCreated` — new course drafted
- `CoursePublished` — course live in catalog
- `CourseArchived` — course hidden
- `StudentEnrolled` — enrollment created
- `StudentUnenrolled` — enrollment removed
- `CourseUpdated` — metadata changed

### Logging
- All course mutations logged with actor, timestamp, changes
- Enrollment changes logged for compliance
- Publication decisions logged with checklist results

### Security
- Only instructors assigned to a course can modify it
- Students can only see published courses
- Enrollment requires authentication
- Archived courses are read-only

### Accessibility
- Course content must pass WCAG 2.1 AA before publication
- Course catalog supports screen reader navigation
- Progress indicators are accessible

---

## AssessmentService

### Responsibilities
- Assessment creation with questions and rubrics
- Assessment session management (start, timeout, submit)
- Auto-grading for objective questions
- Manual grading workflow for subjective questions
- Grade calculation and pass/fail determination
- Attempt tracking and limits

### Dependencies (Ports)
- `AssessmentRepositoryPort` — assessment and attempt persistence
- `CourseRepositoryPort` — course context
- `UserRepositoryPort` — student lookup
- `NotificationPort` — grade notifications
- `EventPublishingPort` — assessment events
- `LoggingPort` — audit trail

### Transactions
- Start assessment: validate + create attempt + record start time atomically
- Submit assessment: validate + record answers + auto-grade + update status atomically
- Grade assessment: apply grades + calculate final + check certificate eligibility atomically

### Validation
- Question format validation per type (MCQ, short answer, essay, code)
- Answer format validation per question type
- Time limit enforcement
- Attempt count enforcement
- Rubric completeness for subjective questions

### Events
- `AssessmentStarted` — attempt initiated
- `AssessmentSubmitted` — answers received
- `AssessmentGraded` — grading complete
- `AssessmentPassed` — score meets threshold
- `AssessmentFailed` — score below threshold

### Logging
- Assessment start/end times logged
- Auto-grading decisions logged with question/answer details
- Manual grading logged with grader identity
- Grade changes logged immutably

### Security
- Questions randomized per student
- Answer encryption at rest
- Anti-cheating measures (time validation, submission integrity)
- Grade tamper detection via checksums

### Accessibility
- Extended time accommodations honored
- Alternative question formats available
- Grade reports in accessible formats
- Screen reader support for assessment interface

---

## CertificateService

### Responsibilities
- Certificate generation and issuance
- Certificate verification (public API)
- Certificate revocation
- Certificate template management
- Certificate download in multiple formats

### Dependencies (Ports)
- `CertificateRepositoryPort` — certificate persistence
- `CourseRepositoryPort` — course details
- `UserRepositoryPort` — recipient details
- `EventPublishingPort` — certificate events
- `LoggingPort` — audit trail
- `NotificationPort` — issuance notifications

### Transactions
- Issuance: verify eligibility + create certificate + sign + notify atomically
- Revocation: validate + mark revoked + notify + update verification atomically

### Validation
- Prerequisites met (all modules completed, assessment passed)
- No duplicate certificate for same course/student
- Certificate data integrity (name, course, date, hash)

### Events
- `CertificateIssued` — new certificate created
- `CertificateVerified` — public verification accessed
- `CertificateRevoked` — certificate invalidated

### Logging
- Issuance logged with full certificate details
- Verification attempts logged (for abuse detection)
- Revocation logged with reason and administrator identity

### Security
- Certificates digitally signed (RSA-2048)
- Verification API rate limited
- Revocation requires admin confirmation
- No sensitive data in verification response

### Accessibility
- Certificate PDF must be tagged (accessible)
- Verification page WCAG 2.1 AA compliant
- Download options accessible

---

## SimulationService

### Responsibilities
- Simulation environment provisioning
- Scenario execution and action validation
- Sandbox management and isolation
- Score calculation and result recording
- Hint system management

### Dependencies (Ports)
- `SimulationRepositoryPort` — simulation state persistence
- `CourseRepositoryPort` — course context
- `UserRepositoryPort` — student lookup
- `EventPublishingPort` — simulation events
- `LoggingPort` — action audit trail
- `ConfigurationPort` — sandbox resource limits

### Transactions
- Start simulation: provision + create session + record start atomically
- Execute action: validate + execute + record + update score atomically
- Record results: finalize + calculate grade + update progress atomically

### Validation
- Action validation against scenario ruleset
- Resource limit enforcement (CPU, memory, network)
- Time limit enforcement
- Maximum concurrent simulation check

### Events
- `SimulationStarted` — environment provisioned
- `ActionExecuted` — action completed
- `SimulationCompleted` — scenario finished
- `SimulationTimedOut` — time limit reached

### Logging
- Every action logged with timestamp, input, output, score delta
- Resource usage logged periodically
- Sandbox violations logged at ERROR level

### Security
- Full network isolation for sandboxes
- Dangerous command filtering
- No data exfiltration paths
- Action audit trail immutable

### Accessibility
- Simulation UI keyboard navigable
- Action results announced to screen readers
- Color-blind friendly score indicators

---

## AnalyticsService

### Responsibilities
- Event collection from all modules
- Real-time metric computation
- Historical data aggregation
- Report generation (course, student, platform)
- Data anonymization for compliance

### Dependencies (Ports)
- `AnalyticsRepositoryPort` — analytics data persistence
- `EventPublishingPort` — event subscription
- `ConfigurationPort` — retention policies
- `LoggingPort` — analytics audit

### Transactions
- Event batch ingestion: validate + persist + aggregate atomically
- Report generation: query + aggregate + cache atomically

### Validation
- Event schema validation
- Date range validation (max 12 months)
- Aggregation window validation

### Events
- `ReportGenerated` — report available
- `DataExported` — export completed
- `AnomalyDetected` — unusual pattern found

### Logging
- Aggregation jobs logged with duration and record count
- Data access logged for compliance

### Security
- PII anonymized in aggregate reports
- Access control on analytics endpoints
- Data retention policies enforced

### Accessibility
- Reports available in screen-reader-friendly formats
- Charts include text alternatives
- Dashboard keyboard navigable

---

## PluginService

### Responsibilities
- Plugin discovery and manifest parsing
- Plugin installation, update, removal
- Plugin configuration management
- Plugin lifecycle (enable, disable)
- Plugin security validation

### Dependencies (Ports)
- `PluginStoragePort` — plugin file storage
- `ConfigurationPort` — plugin settings
- `EventPublishingPort` — plugin events
- `LoggingPort` — plugin audit
- `NotificationPort` — plugin notifications

### Transactions
- Installation: download + validate signature + extract + configure atomically
- Update: backup config + download + migrate + apply atomically
- Removal: archive data + delete files + remove config atomically

### Validation
- Manifest schema validation
- Signature verification (RSA-2048)
- Version compatibility check
- Dependency resolution
- Sandboxed permission validation

### Events
- `PluginInstalled` — installation complete
- `PluginUpdated` — version changed
- `PluginRemoved` — uninstalled
- `PluginEnabled` — activated
- `PluginDisabled` — deactivated
- `PluginError` — runtime error

### Logging
- All plugin lifecycle events logged
- Plugin errors logged with full stack trace
- Plugin hook executions logged for debugging

### Security
- Plugins run in sandboxed environment
- Signature verification mandatory
- Permission audit on every install
- Maximum 20 plugins enforced

### Accessibility
- Plugin configuration UI must be accessible
- Plugin descriptions support localization

---

## BackupService

### Responsibilities
- Full and incremental backup creation
- Backup restoration with safety pre-backup
- Backup integrity verification
- Backup listing and metadata management
- Automatic cleanup of old backups

### Dependencies (Ports)
- `BackupStoragePort` — backup file storage
- `UserRepositoryPort` — user data for backup
- `CourseRepositoryPort` — course data for backup
- `ConfigurationPort` — backup configuration
- `EventPublishingPort` — backup events
- `LoggingPort` — backup audit

### Transactions
- Backup creation: snapshot + compress + encrypt + verify atomically
- Restoration: pre-backup + verify + restore + post-verify atomically

### Validation
- Storage space verification before backup
- Backup integrity after creation
- Restoration compatibility check
- Minimum 1 backup always retained

### Events
- `BackupCreated` — backup complete
- `BackupRestored` — restoration complete
- `BackupVerified` — integrity confirmed
- `BackupFailed` — operation failed
- `BackupDeleted` — cleanup performed

### Logging
- Backup size, duration, checksum logged
- Restoration steps logged with timestamps
- Verification results logged

### Security
- Backups encrypted with AES-256
- Backup access restricted to admins
- Encryption keys stored securely (not with backup data)

### Accessibility
- Backup status notifications accessible
- Backup dashboard keyboard navigable

---

## ConfigurationService

### Responsibilities
- System configuration CRUD
- User preference management
- Configuration validation against schemas
- Configuration export/import
- Default value management

### Dependencies (Ports)
- `ConfigurationPort` — configuration persistence
- `UserRepositoryPort` — user-specific settings
- `EventPublishingPort` — configuration change events
- `LoggingPort` — change audit

### Transactions
- Batch update: validate all + apply all + notify atomically
- Reset: backup current + apply defaults + notify atomically

### Validation
- Type validation against schema
- Range validation for numeric settings
- Enum validation for categorical settings
- Sensitive value masking in exports

### Events
- `ConfigurationChanged` — setting modified
- `ConfigurationReset` — defaults restored
- `ConfigurationExported` — export completed
- `ConfigurationImported` — import completed

### Logging
- Every change logged with before/after values
- Admin identity logged for system settings
- Bulk changes logged with count

### Security
- Sensitive settings encrypted at rest
- System settings require admin access
- User settings scoped to authenticated user
- Configuration audit trail

### Accessibility
- Configuration UI fully accessible
- Setting descriptions available to assistive technology
- Changes confirmed with accessible notifications

---

## AuditService

### Responsibilities
- Audit log ingestion and storage
- Audit log querying with filters and pagination
- Audit log export for compliance
- Audit log analysis and anomaly detection
- Tamper detection for audit integrity

### Dependencies (Ports)
- `AuditRepositoryPort` — audit log persistence
- `LoggingPort` — logging infrastructure
- `EventPublishingPort` — audit events

### Transactions
- Log ingestion: validate + persist + index atomically
- Export: query + format + deliver atomically

### Validation
- Log entry schema validation
- Date range validation
- Filter parameter validation

### Events
- `AuditLogCreated` — new entry
- `AuditLogExported` — export completed
- `AuditAnomalyDetected` — suspicious pattern

### Logging
- Audit service itself logs to separate audit trail
- Query patterns logged for abuse detection

### Security
- Logs immutable once written
- Access restricted to admins and compliance officers
- PII redacted based on viewer role
- Tamper detection via hash chains

### Accessibility
- Log viewer keyboard navigable
- Filter controls accessible
- Export options accessible

---

## DiagnosticsService

### Responsibilities
- System health checks (database, filesystem, memory, CPU)
- Plugin health verification
- Configuration validation
- System information reporting
- Diagnostic history management

### Dependencies (Ports)
- `ConfigurationPort` — system config
- `PluginStoragePort` — plugin status
- `LoggingPort` — diagnostic logging

### Transactions
- Diagnostic run: execute checks + record results atomically

### Validation
- Check result validation
- Threshold comparison for alerts
- History retention enforcement

### Events
- `DiagnosticsCompleted` — run finished
- `HealthCheckFailed` — critical issue
- `HealthCheckRecovered` — issue resolved

### Logging
- Diagnostic results logged with full details
- Performance metrics logged for trend analysis

### Security
- Diagnostics must not expose sensitive data
- Read-only operations only (no mutations)
- Access restricted to admins

### Accessibility
- Health status dashboard accessible
- Diagnostic results in screen-reader-friendly format
- Alert notifications accessible
