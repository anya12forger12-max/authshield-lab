# Use Case Catalog

## Overview

This document catalogs every use case in AuthShield Lab. Each use case is a
single-responsibility workflow that orchestrates domain entities, enforces
business rules, and produces a well-defined output. Use cases are grouped
by module.

---

## Authentication Module

### UC-AUTH-001: AuthenticateUser

- **Purpose:** Verify a user's identity via email/password and optionally MFA.
- **Actor:** Unauthenticated user
- **Preconditions:** User account exists and is active. Identity provider is available.
- **Postconditions:** Session tokens issued. Audit event recorded. Failed attempts tracked.
- **Inputs:** `email: str`, `password: str`, `mfa_code: str | None`
- **Outputs:** `user_id: UUID`, `access_token: str`, `refresh_token: str`, `expires_in: int`
- **Business Rules:**
  - BR-AUTH-001: Account lockout after 5 consecutive failed attempts within 15 minutes
  - BR-AUTH-002: MFA code must be 6 digits and valid within 30-second window
  - BR-AUTH-003: Password verified against bcrypt hash (cost factor 12)
  - BR-AUTH-004: Refresh token rotation on each use
  - BR-AUTH-005: Deactivated accounts cannot authenticate
- **Exceptions:** `AuthenticationFailed`, `AccountLocked`, `MFARequired`, `AccountDeactivated`
- **Security Requirements:** Rate limiting (10 attempts/minute per IP), brute force protection, audit logging, no password in logs
- **Accessibility Requirements:** Error messages must be screen-reader friendly, no time-limited challenges without alternatives

### UC-AUTH-002: RefreshToken

- **Purpose:** Issue a new access token using a valid refresh token.
- **Actor:** Authenticated user (via token)
- **Preconditions:** Valid refresh token exists and has not been revoked.
- **Postconditions:** New access token issued. Old refresh token invalidated. Audit event recorded.
- **Inputs:** `refresh_token: str`
- **Outputs:** `access_token: str`, `refresh_token: str`, `expires_in: int`
- **Business Rules:**
  - BR-AUTH-006: Refresh token is single-use (rotation)
  - BR-AUTH-007: Refresh token expires after 7 days
  - BR-AUTH-008: Token family tracking detects reuse attacks
  - BR-AUTH-009: Revoked refresh tokens invalidate entire token family
- **Exceptions:** `TokenExpired`, `TokenRevoked`, `TokenReuseDetected`
- **Security Requirements:** Token rotation, family tracking, secure storage
- **Accessibility Requirements:** N/A (background process)

### UC-AUTH-003: RevokeSession

- **Purpose:** Invalidate a specific session or all sessions for a user.
- **Actor:** Authenticated user or administrator
- **Preconditions:** User has at least one active session.
- **Postconditions:** Session(s) invalidated. Refresh tokens revoked. Audit event recorded.
- **Inputs:** `user_id: UUID`, `session_id: UUID | None` (None = all sessions)
- **Outputs:** `revoked_count: int`
- **Business Rules:**
  - BR-AUTH-010: Users can revoke their own sessions without admin privileges
  - BR-AUTH-011: Admins can revoke any user's sessions
  - BR-AUTH-012: Revoking all sessions requires re-authentication
- **Exceptions:** `SessionNotFound`, `UnauthorizedRevocation`
- **Security Requirements:** Authorization check, audit trail
- **Accessibility Requirements:** Confirmation dialog with clear messaging

---

## Authorization Module

### UC-AUTHZ-001: AuthorizeRequest

- **Purpose:** Determine if an authenticated user may perform a requested action.
- **Actor:** System (middleware)
- **Preconditions:** User is authenticated. Permission definitions exist.
- **Postconditions:** Request allowed or denied. Denial logged.
- **Inputs:** `user_id: UUID`, `resource: str`, `action: str`, `context: dict`
- **Outputs:** `allowed: bool`, `reason: str | None`
- **Business Rules:**
  - BR-AUTHZ-001: Deny by default — access requires explicit permission
  - BR-AUTHZ-002: Role hierarchy: admin > instructor > student
  - BR-AUTHZ-003: Permissions can be granted at system, course, or resource level
  - BR-AUTHZ-004: Deny overrides allow when both exist
  - BR-AUTHZ-005: Context-aware permissions (e.g., owner of resource)
- **Exceptions:** `AuthorizationDenied`, `PermissionDefinitionMissing`
- **Security Requirements:** Always evaluated server-side, never trust client assertions
- **Accessibility Requirements:** Denial responses must include actionable guidance

### UC-AUTHZ-002: AssignRole

- **Purpose:** Assign a role to a user within a specific scope.
- **Actor:** Administrator
- **Preconditions:** User and role exist. Assigner has sufficient privileges.
- **Postconditions:** Role assignment recorded. Permissions effective immediately.
- **Inputs:** `user_id: UUID`, `role_name: str`, `scope: str | None`
- **Outputs:** `assignment_id: UUID`
- **Business Rules:**
  - BR-AUTHZ-006: Cannot assign roles higher than assigner's own role
  - BR-AUTHZ-007: Maximum 5 roles per user per scope
  - BR-AUTHZ-008: System roles cannot be modified or deleted
- **Exceptions:** `RoleNotFound`, `InsufficientPrivileges`, `RoleLimitExceeded`
- **Security Requirements:** Privilege escalation prevention, audit logging
- **Accessibility Requirements:** Confirmation with role details before assignment

### UC-AUTHZ-003: GrantPermission

- **Purpose:** Grant a specific permission to a user or role.
- **Actor:** Administrator
- **Preconditions:** User or role exists. Permission definition exists.
- **Postconditions:** Permission granted. Effective immediately.
- **Inputs:** `grantee_id: UUID`, `grantee_type: str`, `permission: str`, `scope: str | None`
- **Outputs:** `grant_id: UUID`
- **Business Rules:**
  - BR-AUTHZ-009: Wildcard permissions (resource:*) require admin approval
  - BR-AUTHZ-010: Temporary permissions require expiry date
  - BR-AUTHZ-011: Permissions inherit through scope hierarchy
- **Exceptions:** `PermissionNotFound`, `GranteeNotFound`, `ApprovalRequired`
- **Security Requirements:** Least-privilege principle enforcement, expiry tracking
- **Accessibility Requirements:** Permission details visible in user profile

---

## Course Management Module

### UC-COURSE-001: CreateCourse

- **Purpose:** Create a new course with metadata and initial structure.
- **Actor:** Instructor or administrator
- **Preconditions:** User has course creation permission.
- **Postconditions:** Course created in draft state. Creator enrolled as instructor.
- **Inputs:** `title: str`, `description: str`, `modules: list[ModuleInput]`, `settings: CourseSettings`
- **Outputs:** `course_id: UUID`
- **Business Rules:**
  - BR-COURSE-001: Title must be 3-200 characters
  - BR-COURSE-002: Maximum 50 modules per course
  - BR-COURSE-003: Maximum 200 lessons per module
  - BR-COURSE-004: Course creator automatically enrolled as instructor
  - BR-COURSE-005: Slug auto-generated from title, must be unique
- **Exceptions:** `ValidationFailed`, `DuplicateCourseSlug`, `PermissionDenied`
- **Security Requirements:** Input sanitization, XSS prevention in descriptions
- **Accessibility Requirements:** Course title and description must support Unicode

### UC-COURSE-002: PublishCourse

- **Purpose:** Move a course from draft to published state.
- **Actor:** Course instructor or administrator
- **Preconditions:** Course is in draft state. At least one module with one lesson exists.
- **Postconditions:** Course visible in course catalog. Students can enroll.
- **Inputs:** `course_id: UUID`
- **Outputs:** `published_at: datetime`
- **Business Rules:**
  - BR-COURSE-006: All modules must have at least one published lesson
  - BR-COURSE-007: Course must have a thumbnail image
  - BR-COURSE-008: Pricing must be set (including free)
  - BR-COURSE-009: Accessibility compliance check must pass
  - BR-COURSE-010: Terms and conditions acceptance required
- **Exceptions:** `CourseNotReady`, `AccessibilityCheckFailed`, `IncompleteModules`
- **Security Requirements:** Only course instructors can publish
- **Accessibility Requirements:** Automatic WCAG 2.1 AA check before publication

### UC-COURSE-003: ArchiveCourse

- **Purpose:** Archive a course making it read-only and hidden from catalog.
- **Actor:** Course instructor or administrator
- **Preconditions:** Course exists. Actor has archive permission.
- **Postconditions:** Course hidden from catalog. Enrolled students retain read access.
- **Inputs:** `course_id: UUID`, `reason: str | None`
- **Outputs:** `archived_at: datetime`
- **Business Rules:**
  - BR-COURSE-011: Active assessments in the course are finalized
  - BR-COURSE-012: Students are notified of archival
  - BR-COURSE-013: Course can be unarchived within 90 days
- **Exceptions:** `CourseNotFound`, `PermissionDenied`
- **Security Requirements:** Authorization check, notification to enrolled students
- **Accessibility Requirements:** Archive notification must be accessible

### UC-COURSE-004: EnrollStudent

- **Purpose:** Enroll a student in a course.
- **Actor:** Student (self-enrollment) or administrator
- **Preconditions:** Course is published. Student is not already enrolled. Capacity allows.
- **Postconditions:** Enrollment recorded. Welcome notification sent.
- **Inputs:** `course_id: UUID`, `student_id: UUID`
- **Outputs:** `enrollment_id: UUID`
- **Business Rules:**
  - BR-COURSE-014: Maximum 500 students per course
  - BR-COURSE-015: Prerequisites must be satisfied if defined
  - BR-COURSE-016: Free courses allow instant enrollment; paid courses require payment
  - BR-COURSE-017: Waitlist enabled when course is at capacity
- **Exceptions:** `AlreadyEnrolled`, `CourseFull`, `PrerequisitesNotMet`, `PaymentRequired`
- **Security Requirements:** Prevent enrollment in archived courses
- **Accessibility Requirements:** Enrollment confirmation in accessible format

---

## Lesson & Progress Module

### UC-LESSON-001: LaunchLesson

- **Purpose:** Start a lesson session for an enrolled student.
- **Actor:** Student
- **Preconditions:** Student is enrolled in the course. Lesson belongs to the course.
- **Postconditions:** Lesson session created. Progress tracking initialized.
- **Inputs:** `course_id: UUID`, `lesson_id: UUID`, `student_id: UUID`
- **Outputs:** `session_id: UUID`, `lesson_content: LessonContent`
- **Business Rules:**
  - BR-LESSON-001: Previous lesson must be completed or course has no sequential requirement
  - BR-LESSON-002: Maximum concurrent lesson sessions: 1 per student
  - BR-LESSON-003: Lesson content loaded based on student's accessibility preferences
- **Exceptions:** `LessonNotFound`, `NotEnrolled`, `PrerequisiteLessonIncomplete`
- **Security Requirements:** Verify enrollment, prevent unauthorized content access
- **Accessibility Requirements:** Load content adapted to user's accessibility settings

### UC-LESSON-002: CompleteLesson

- **Purpose:** Mark a lesson as completed and update student progress.
- **Actor:** Student (self) or system (auto-complete)
- **Preconditions:** Lesson session is active. Minimum time requirement met.
- **Postconditions:** Lesson marked complete. Progress updated. Next lesson unlocked if sequential.
- **Inputs:** `session_id: UUID`, `completion_data: dict`
- **Outputs:** `completed: bool`, `progress_percent: float`, `next_lesson_id: UUID | None`
- **Business Rules:**
  - BR-LESSON-004: Minimum 80% engagement time before completion
  - BR-LESSON-005: Interactive elements must be completed
  - BR-LESSON-006: Quiz within lesson must pass at 70% threshold
  - BR-LESSON-007: Completion timestamp recorded for audit
- **Exceptions:** `SessionExpired`, `MinimumTimeNotMet`, `InteractiveElementsIncomplete`
- **Security Requirements:** Prevent completion without genuine engagement
- **Accessibility Requirements:** Completion tracking respects accessibility accommodations

### UC-LESSON-003: TrackProgress

- **Purpose:** Calculate and return a student's progress through a course.
- **Actor:** Student or instructor
- **Preconditions:** Student is enrolled. At least one lesson attempted.
- **Outputs:** `progress: CourseProgress` (modules, lessons, percentage, time spent)
- **Business Rules:**
  - BR-LESSON-008: Progress calculated as weighted average of completed vs total content
  - BR-LESSON-009: Time spent includes active engagement only
  - BR-LESSON-010: Progress persisted for offline access
- **Inputs:** `course_id: UUID`, `student_id: UUID`
- **Exceptions:** `EnrollmentNotFound`
- **Security Requirements:** Students see only their own progress; instructors see all
- **Accessibility Requirements:** Progress visualization with screen reader support

---

## Assessment Module

### UC-ASSESS-001: StartAssessment

- **Purpose:** Begin an assessment session for a student.
- **Actor:** Student
- **Preconditions:** Student enrolled. Assessment available. No active attempt.
- **Postconditions:** Assessment session started. Timer begins.
- **Inputs:** `assessment_id: UUID`, `student_id: UUID`
- **Outputs:** `attempt_id: UUID`, `questions: list[Question]`, `time_limit_minutes: int`
- **Business Rules:**
  - BR-ASSESS-001: Maximum 3 attempts per assessment
  - BR-ASSESS-002: Questions randomized per student
  - BR-ASSESS-003: Time limit enforced server-side
  - BR-ASSESS-004: Browser lockdown mode optional
- **Exceptions:** `MaxAttemptsReached`, `AssessmentNotAvailable`, `ActiveAttemptExists`
- **Security Requirements:** Anti-cheating measures, question pool randomization
- **Accessibility Requirements:** Extended time accommodations honored

### UC-ASSESS-002: SubmitAssessment

- **Purpose:** Submit answers for an assessment attempt.
- **Actor:** Student
- **Preconditions:** Active assessment attempt exists.
- **Postconditions:** Answers recorded. Auto-graded where applicable. Results pending review.
- **Inputs:** `attempt_id: UUID`, `answers: list[Answer]`
- **Outputs:** `submission_id: UUID`, `auto_score: float | None`, `pending_review: bool`
- **Business Rules:**
  - BR-ASSESS-005: Partial submissions allowed up to time limit
  - BR-ASSESS-006: Auto-grading for objective questions
  - BR-ASSESS-007: Subjective questions queued for instructor review
  - BR-ASSESS-008: Late submissions penalized per course policy
- **Exceptions:** `AttemptExpired`, `AttemptAlreadySubmitted`, `InvalidAnswerFormat`
- **Security Requirements:** Answer encryption at rest, submission integrity verification
- **Accessibility Requirements:** Alternative input methods supported for answers

### UC-ASSESS-003: GradeAssessment

- **Purpose:** Grade a submitted assessment (manual or auto).
- **Actor:** Instructor or system
- **Preconditions:** Assessment submitted. Grading rubric defined.
- **Postconditions:** Grade recorded. Student notified. Certificate eligibility checked.
- **Inputs:** `attempt_id: UUID`, `grades: list[QuestionGrade] | None`, `feedback: str | None`
- **Outputs:** `final_score: float`, `passed: bool`, `certificate_eligible: bool`
- **Business Rules:**
  - BR-ASSESS-009: Pass threshold configurable per assessment (default 70%)
  - BR-ASSESS-010: Instructor feedback required for failed attempts
  - BR-ASSESS-011: Grade appeals within 14 days of grading
  - BR-ASSESS-012: Grade history immutable after finalization
- **Exceptions:** `AlreadyGraded`, `GradingRubricMissing`, `AppealWindowOpen`
- **Security Requirements:** Grade tamper detection, audit trail
- **Accessibility Requirements:** Grade reports available in accessible formats

---

## Certificate Module

### UC-CERT-001: IssueCertificate

- **Purpose:** Issue a digital certificate upon course completion.
- **Actor:** System (automatic) or administrator
- **Preconditions:** Student completed all requirements. Grade meets threshold.
- **Postconditions:** Certificate issued with unique ID. Student notified. Certificate downloadable.
- **Inputs:** `student_id: UUID`, `course_id: UUID`
- **Outputs:** `certificate_id: UUID`, `certificate_url: str`, `issued_at: datetime`
- **Business Rules:**
  - BR-CERT-001: All course modules must be completed
  - BR-CERT-002: Final assessment score must meet pass threshold
  - BR-CERT-003: Certificate includes student name, course name, date, unique verification code
  - BR-CERT-004: Certificates are digitally signed
  - BR-CERT-005: One certificate per student per course
- **Exceptions:** `RequirementsNotMet`, `CertificateAlreadyIssued`, `CourseArchived`
- **Security Requirements:** Tamper-proof certificate generation, digital signature
- **Accessibility Requirements:** Certificate PDF must be accessible (tagged PDF)

### UC-CERT-002: VerifyCertificate

- **Purpose:** Verify the authenticity of a certificate.
- **Actor:** External verifier or system
- **Preconditions:** Certificate ID provided.
- **Postconditions:** Verification result returned.
- **Inputs:** `certificate_id: str`
- **Outputs:** `valid: bool`, `student_name: str`, `course_name: str`, `issued_at: datetime`
- **Business Rules:**
  - BR-CERT-006: Verification works via public URL without authentication
  - BR-CERT-007: Revoked certificates return invalid with reason
  - BR-CERT-008: Verification rate limited to 100 requests/minute
- **Exceptions:** `CertificateNotFound`, `CertificateRevoked`
- **Security Requirements:** Rate limiting, no sensitive data exposed
- **Accessibility Requirements:** Verification page must be WCAG compliant

### UC-CERT-003: RevokeCertificate

- **Purpose:** Revoke a previously issued certificate.
- **Actor:** Administrator
- **Preconditions:** Certificate exists and is valid.
- **Postconditions:** Certificate marked as revoked. Verification returns invalid.
- **Inputs:** `certificate_id: UUID`, `reason: str`
- **Outputs:** `revoked_at: datetime`
- **Business Rules:**
  - BR-CERT-009: Revocation requires administrator approval
  - BR-CERT-010: Student notified with revocation reason
  - BR-CERT-011: Revoked certificates cannot be re-issued; new attempt required
- **Exceptions:** `CertificateNotFound`, `AlreadyRevoked`, `InsufficientPrivileges`
- **Security Requirements:** Audit logging, administrator confirmation
- **Accessibility Requirements:** Revocation notification accessible

---

## Simulation Module

### UC-SIM-001: StartSimulation

- **Purpose:** Launch a security attack/defense simulation lab.
- **Actor:** Student or instructor
- **Preconditions:** Simulation scenario is available. Student has required prerequisites.
- **Postconditions:** Simulation environment provisioned. Timer started.
- **Inputs:** `scenario_id: UUID`, `student_id: UUID`
- **Outputs:** `simulation_id: UUID`, `environment_config: EnvironmentConfig`, `time_limit_minutes: int`
- **Business Rules:**
  - BR-SIM-001: Maximum 1 concurrent simulation per student
  - BR-SIM-002: Sandbox environment isolated from production
  - BR-SIM-003: Resource limits enforced (CPU, memory, network)
  - BR-SIM-004: Automatic cleanup after timeout
- **Exceptions:** `ScenarioNotFound`, `ActiveSimulationExists`, `ResourceLimitExceeded`
- **Security Requirements:** Network isolation, no data exfiltration, audit logging
- **Accessibility Requirements:** Simulation UI supports keyboard navigation

### UC-SIM-002: ExecuteScenario

- **Purpose:** Execute attack or defense actions within the simulation.
- **Actor:** Student
- **Preconditions:** Simulation is active. Action is valid for the scenario.
- **Postconditions:** Action executed. Result recorded. Progress updated.
- **Inputs:** `simulation_id: UUID`, `action: SimulationAction`
- **Outputs:** `result: ActionResult`, `score_delta: float`, `hints_remaining: int`
- **Business Rules:**
  - BR-SIM-005: Actions validated against scenario ruleset
  - BR-SIM-006: Hints reduce maximum score by 10% each
  - BR-SIM-007: Dangerous actions blocked in sandbox mode
  - BR-SIM-008: Action history available for review
- **Exceptions:** `SimulationExpired`, `InvalidAction`, `BlockedAction`
- **Security Requirements:** Action sandboxing, dangerous command filtering
- **Accessibility Requirements:** Action results announced to screen readers

### UC-SIM-003: RecordResults

- **Purpose:** Record and finalize simulation results.
- **Actor:** System (automatic on completion) or student
- **Preconditions:** Simulation active or just completed.
- **Postconditions:** Results recorded. Grade calculated. Course progress updated.
- **Inputs:** `simulation_id: UUID`
- **Outputs:** `results: SimulationResults`, `grade: float`, `completion_time: timedelta`
- **Business Rules:**
  - BR-SIM-009: Score based on objectives completed, time taken, hints used
  - BR-SIM-010: Results available for instructor review
  - BR-SIM-011: Retake policy defined per course
- **Exceptions:** `SimulationNotFound`, `ResultsAlreadyRecorded`
- **Security Requirements:** Result integrity verification
- **Accessibility Requirements:** Results displayed in accessible format

---

## Analytics & Reporting Module

### UC-RPT-001: GenerateReport

- **Purpose:** Generate an analytics report for courses, students, or platform.
- **Actor:** Administrator or instructor
- **Preconditions:** Sufficient data exists. Actor has reporting permission.
- **Postconditions:** Report generated and available for download/viewing.
- **Inputs:** `report_type: str`, `filters: ReportFilters`, `format: str`
- **Outputs:** `report_id: UUID`, `report_data: ReportData`
- **Business Rules:**
  - BR-RPT-001: Reports generated from cached data (max 1 hour old)
  - BR-RPT-002: Student PII anonymized in aggregate reports
  - BR-RPT-003: Export formats: JSON, CSV, PDF
  - BR-RPT-004: Maximum report range: 12 months
- **Exceptions:** `InsufficientData`, `ReportGenerationFailed`, `PermissionDenied`
- **Security Requirements:** Data anonymization, access control on reports
- **Accessibility Requirements:** Reports available in accessible formats

### UC-RPT-002: ExportData

- **Purpose:** Export data in various formats for external use.
- **Actor:** Administrator
- **Preconditions:** Export permission granted. Data exists.
- **Postconditions:** Export file generated. Download link provided.
- **Inputs:** `data_type: str`, `filters: ExportFilters`, `format: str`
- **Outputs:** `export_id: UUID`, `download_url: str`, `expires_at: datetime`
- **Business Rules:**
  - BR-RPT-005: Exports include data lineage metadata
  - BR-RPT-006: Large exports paginated (max 10,000 records per page)
  - BR-RPT-007: Export links expire after 24 hours
  - BR-RPT-008: Export activity logged for compliance
- **Exceptions:** `ExportTooLarge`, `UnsupportedFormat`, `ExportFailed`
- **Security Requirements:** Encryption of exported data, access logging
- **Accessibility Requirements:** Export options accessible via keyboard

### UC-RPT-003: ImportData

- **Purpose:** Import data from external sources into the system.
- **Actor:** Administrator
- **Preconditions:** Import permission. Valid data format. Schema mapping defined.
- **Postconditions:** Data validated, transformed, and imported. Conflicts resolved.
- **Inputs:** `data_type: str`, `file: bytes`, `mapping: dict`, `conflict_strategy: str`
- **Outputs:** `import_id: UUID`, `imported_count: int`, `conflicts: list[Conflict]`
- **Business Rules:**
  - BR-RPT-009: All imports validated before commit
  - BR-RPT-010: Rollback on critical validation failures
  - BR-RPT-011: Duplicate detection by unique identifier
  - BR-RPT-012: Import preview before final commit
- **Exceptions:** `ImportValidationFailed`, `SchemaMismatch`, `DuplicateData`
- **Security Requirements:** File type validation, size limits, virus scanning
- **Accessibility Requirements:** Import progress announced to assistive technology

---

## Plugin Module

### UC-PLUGIN-001: InstallPlugin

- **Purpose:** Install a plugin to extend system functionality.
- **Actor:** Administrator
- **Preconditions:** Plugin package available. System requirements met.
- **Postconditions:** Plugin installed. Configuration available. System restarted if needed.
- **Inputs:** `plugin_id: str`, `version: str | None`
- **Outputs:** `installation_id: UUID`, `config_schema: dict`
- **Business Rules:**
  - BR-PLUGIN-001: Plugins must be cryptographically signed
  - BR-PLUGIN-002: Plugin sandbox permissions must be approved
  - BR-PLUGIN-003: Maximum 20 plugins installed simultaneously
  - BR-PLUGIN-004: Plugin compatibility verified against system version
  - BR-PLUGIN-005: Plugin manifests validated before installation
- **Exceptions:** `PluginNotFound`, `IncompatiblePlugin`, `SignatureInvalid`, `PluginLimitExceeded`
- **Security Requirements:** Signature verification, sandbox enforcement, permission audit
- **Accessibility Requirements:** Plugin configuration UI must be accessible

### UC-PLUGIN-002: UpdatePlugin

- **Purpose:** Update an installed plugin to a newer version.
- **Actor:** Administrator
- **Preconditions:** Plugin is installed. Newer version available.
- **Postconditions:** Plugin updated. Configuration preserved. System notified.
- **Inputs:** `plugin_id: str`, `target_version: str | None`
- **Outputs:** `previous_version: str`, `new_version: str`, `updated_at: datetime`
- **Business Rules:**
  - BR-PLUGIN-006: Automatic backup of configuration before update
  - BR-PLUGIN-007: Rollback capability within 24 hours
  - BR-PLUGIN-008: Breaking changes require manual configuration review
- **Exceptions:** `PluginNotFound`, `AlreadyUpToDate`, `UpdateFailed`, `ConfigMigrationRequired`
- **Security Requirements:** Signature verification for updates
- **Accessibility Requirements:** Update notification in accessible format

### UC-PLUGIN-003: RemovePlugin

- **Purpose:** Remove an installed plugin from the system.
- **Actor:** Administrator
- **Preconditions:** Plugin is installed. No active dependencies from other plugins.
- **Postconditions:** Plugin removed. Configuration archived. System notified.
- **Inputs:** `plugin_id: str`
- **Outputs:** `removed_at: datetime`
- **Business Rules:**
  - BR-PLUGIN-009: Plugin data archived before removal
  - BR-PLUGIN-010: Dependent plugins must be removed first
  - BR-PLUGIN-011: System restart required after removal
- **Exceptions:** `PluginNotFound`, `PluginHasDependents`, `RemovalFailed`
- **Security Requirements:** Cleanup of plugin-specific data
- **Accessibility Requirements:** Removal confirmation accessible

---

## Configuration Module

### UC-CFG-001: ConfigureSystem

- **Purpose:** Update system-wide configuration settings.
- **Actor:** Administrator
- **Preconditions:** Admin access. Configuration key exists.
- **Postconditions:** Configuration updated. Affected services notified.
- **Inputs:** `settings: dict[str, Any]`
- **Outputs:** `updated_keys: list[str]`, `restart_required: bool`
- **Business Rules:**
  - BR-CFG-001: Configuration changes logged with before/after values
  - BR-CFG-002: Sensitive settings encrypted at rest
  - BR-CFG-003: Some changes require system restart
  - BR-CFG-004: Configuration validated against schema before apply
- **Exceptions:** `InvalidConfiguration`, `ReadOnlySetting`, `RestartRequired`
- **Security Requirements:** Encrypted storage for secrets, change audit
- **Accessibility Requirements:** Configuration UI keyboard navigable

### UC-CFG-002: UpdateSetting

- **Purpose:** Update a single configuration setting.
- **Actor:** Administrator or user (for personal settings)
- **Preconditions:** Setting key exists. Actor has permission.
- **Postconditions:** Setting updated. Change propagated.
- **Inputs:** `key: str`, `value: Any`
- **Outputs:** `previous_value: Any`, `updated_at: datetime`
- **Business Rules:**
  - BR-CFG-005: User settings scoped to user
  - BR-CFG-006: System settings require admin access
  - BR-CFG-007: Settings validated against type schema
- **Exceptions:** `SettingNotFound`, `InvalidValue`, `PermissionDenied`
- **Security Requirements:** Permission-based access control per setting
- **Accessibility Requirements:** Setting descriptions available to screen readers

---

## Backup Module

### UC-BAK-001: CreateBackup

- **Purpose:** Create a full system backup.
- **Actor:** Administrator or scheduled task
- **Preconditions:** Backup storage available. Sufficient disk space.
- **Postconditions:** Backup file created. Metadata recorded. Integrity verified.
- **Inputs:** `backup_type: str` (full, incremental), `include_plugins: bool`
- **Outputs:** `backup_id: UUID`, `size_bytes: int`, `checksum: str`
- **Business Rules:**
  - BR-BAK-001: Backups include database, files, and configuration
  - BR-BAK-002: Backups encrypted with AES-256
  - BR-BAK-003: Maximum 30 backups retained (oldest auto-deleted)
  - BR-BAK-004: Backup integrity verified immediately after creation
  - BR-BAK-005: Backup metadata includes system version and timestamp
- **Exceptions:** `InsufficientStorage`, `BackupFailed`, `IntegrityCheckFailed`
- **Security Requirements:** Encryption, access control, secure storage
- **Accessibility Requirements:** Backup status notifications accessible

### UC-BAK-002: RestoreBackup

- **Purpose:** Restore system state from a backup.
- **Actor:** Administrator
- **Preconditions:** Valid backup exists. Current state backed up as safety net.
- **Postconditions:** System restored to backup state. Pre-restore backup created.
- **Inputs:** `backup_id: UUID`, `confirm: bool`
- **Outputs:** `restored_at: datetime`, `pre_restore_backup_id: UUID`
- **Business Rules:**
  - BR-BAK-006: Pre-restore backup mandatory
  - BR-BAK-007: Restore validates backup integrity before applying
  - BR-BAK-008: System enters maintenance mode during restore
  - BR-BAK-009: All active sessions terminated after restore
- **Exceptions:** `BackupNotFound`, `BackupCorrupted`, `RestoreFailed`
- **Security Requirements:** Encrypted restore, admin-only access, audit logging
- **Accessibility Requirements:** Maintenance mode notification accessible

### UC-BAK-003: VerifyBackup

- **Purpose:** Verify the integrity and restorability of a backup.
- **Actor:** Administrator or scheduled task
- **Preconditions:** Backup exists.
- **Postconditions:** Verification result recorded.
- **Inputs:** `backup_id: UUID`
- **Outputs:** `valid: bool`, `details: dict`
- **Business Rules:**
  - BR-BAK-010: Weekly automatic verification
  - BR-BAK-011: Failed backups flagged for manual review
- **Exceptions:** `BackupNotFound`, `VerificationFailed`
- **Security Requirements:** Read-only access to backup during verification
- **Accessibility Requirements:** Verification status in dashboard

### UC-BAK-004: ListBackups

- **Purpose:** List available backups with metadata.
- **Actor:** Administrator
- **Preconditions:** None
- **Postconditions:** Backup list returned.
- **Inputs:** `filters: BackupFilters | None`
- **Outputs:** `backups: list[BackupMetadata]`
- **Business Rules:**
  - BR-BAK-012: Backups sorted by creation date descending
  - BR-BAK-013: Storage usage displayed
- **Exceptions:** None
- **Security Requirements:** Admin-only access
- **Accessibility Requirements:** Backup list accessible with screen readers

---

## Audit Module

### UC-AUDIT-001: ViewAuditLogs

- **Purpose:** Query and view audit log entries.
- **Actor:** Administrator or compliance officer
- **Preconditions:** Audit log permission. Logs exist.
- **Postconditions:** Log entries returned with filtering and pagination.
- **Inputs:** `filters: AuditFilters`, `page: int`, `page_size: int`
- **Outputs:** `entries: list[AuditEntry]`, `total: int`, `page: int`
- **Business Rules:**
  - BR-AUDIT-001: Logs immutable once written
  - BR-AUDIT-002: Retention period: 2 years minimum
  - BR-AUDIT-003: Log entries include timestamp, actor, action, resource, outcome
  - BR-AUDIT-004: PII redacted based on viewer role
- **Exceptions:** `InsufficientPermissions`, `LogsNotFound`
- **Security Requirements:** Read-only access, PII protection, tamper detection
- **Accessibility Requirements:** Log table must be accessible, filterable via keyboard

---

## Diagnostics Module

### UC-DIAG-001: RunDiagnostics

- **Purpose:** Run system health checks and diagnostics.
- **Actor:** Administrator or automated monitoring
- **Preconditions:** None
- **Postconditions:** Diagnostic results recorded.
- **Inputs:** `checks: list[str] | None` (None = all checks)
- **Outputs:** `results: DiagnosticResults`, `healthy: bool`
- **Business Rules:**
  - BR-DIAG-001: Checks include database, filesystem, plugins, memory, CPU
  - BR-DIAG-002: Critical failures trigger alerts
  - BR-DIAG-003: Diagnostic history retained for 30 days
  - BR-DIAG-004: Diagnostics run in read-only mode (no mutations)
- **Exceptions:** `DiagnosticFailed`, `PartialDiagnostics`
- **Security Requirements:** Diagnostics must not expose sensitive data
- **Accessibility Requirements:** Health status dashboard must be accessible

### UC-DIAG-002: ViewSystemInfo

- **Purpose:** Display system information and version details.
- **Actor:** Administrator
- **Preconditions:** None
- **Postconditions:** System information returned.
- **Inputs:** None
- **Outputs:** `system_info: SystemInfo` (version, uptime, resource usage, plugin versions)
- **Business Rules:**
  - BR-DIAG-005: Version information always accessible
  - BR-DIAG-006: Resource usage includes memory, disk, CPU
- **Exceptions:** None
- **Security Requirements:** No secrets or keys in system info
- **Accessibility Requirements:** System info readable by screen readers

---

## Accessibility Module

### UC-A11Y-001: ManageAccessibilityPreferences

- **Purpose:** Update user accessibility preferences.
- **Actor:** User
- **Preconditions:** User is authenticated.
- **Postconditions:** Preferences saved. UI adapts immediately.
- **Inputs:** `preferences: AccessibilityPreferences` (theme, font_size, contrast, reduced_motion, screen_reader)
- **Outputs:** `saved_at: datetime`
- **Business Rules:**
  - BR-A11Y-001: Preferences stored per user
  - BR-A11Y-002: System-wide defaults available
  - BR-A11Y-003: Preferences sync across devices
  - BR-A11Y-004: All UI components must respect preferences
- **Exceptions:** `InvalidPreference`, `SaveFailed`
- **Security Requirements:** Preferences not exposed to other users
- **Accessibility Requirements:** Preference UI itself must be accessible

---

## Localization Module

### UC-L10N-001: ManageLocalization

- **Purpose:** Set language and regional formatting preferences.
- **Actor:** User or administrator
- **Preconditions:** Supported locale available.
- **Postconditions:** Locale applied. All content re-rendered.
- **Inputs:** `locale: str` (e.g., "en-US", "fr-FR", "ja-JP")
- **Outputs:** `applied_locale: str`, `fallback_used: bool`
- **Business Rules:**
  - BR-L10N-001: 12 languages supported at launch
  - BR-L10N-002: Date/time/number formatting per locale
  - BR-L10N-003: RTL layout support for Arabic, Hebrew
  - BR-L10N-004: Untranslated content falls back to English
- **Exceptions:** `LocaleNotSupported`, `TranslationIncomplete`
- **Security Requirements:** Locale setting not exploitable for XSS
- **Accessibility Requirements:** Language attribute set on HTML for screen readers
