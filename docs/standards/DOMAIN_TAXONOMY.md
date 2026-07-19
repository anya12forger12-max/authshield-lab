# Domain Taxonomy

> Domain model definitions for AuthShield Lab. This document defines bounded contexts,
> their entities, value objects, aggregate roots, domain events, services, and repositories.

---

## Table of Contents

1. [Bounded Contexts Overview](#bounded-contexts-overview)
2. [Identity Context](#identity-context)
3. [Authorization Context](#authorization-context)
4. [Education Context](#education-context)
5. [Simulation Context](#simulation-context)
6. [Analytics Context](#analytics-context)
7. [Operations Context](#operations-context)
8. [Context Map](#context-map)
9. [Ubiquitous Language Glossary](#ubiquitous-language-glossary)

---

## Bounded Contexts Overview

AuthShield Lab is divided into six primary bounded contexts, each owning its own data model, business rules, and ubiquitous language:

| Context | Purpose | Core Modules |
|---|---|---|
| **Identity** | User lifecycle, authentication, credentials | auth, users, sessions |
| **Authorization** | Access control, roles, permissions, policies | authorization, policies, rules |
| **Education** | Learning content, courses, assessments, competency | lms, content, content_studio |
| **Simulation** | Attack simulations, defense exercises, scenarios | simulation, defense |
| **Analytics** | Metrics, reporting, learning analytics, dashboards | analytics, certification |
| **Operations** | Audit, compliance, production, ecosystem | audit, production, ecosystem, optimization |

---

## Identity Context

### Domain Entities

| Entity | Description | Key Attributes |
|---|---|---|
| `User` | A registered person in the system | id, email, display_name, is_active, created_at |
| `Credential` | Authentication material for a user | id, user_id, type, value, is_active, created_at |
| `Session` | An active authenticated connection | id, user_id, token, ip_address, expires_at, is_revoked |
| `MfaChallenge` | An outstanding MFA verification request | id, user_id, method, code_hash, expires_at, attempts |

### Value Objects

| Value Object | Description | Attributes |
|---|---|---|
| `Email` | Validated email address | value (validated format) |
| `PasswordHash` | Hashed password with algorithm metadata | hash, algorithm, salt |
| `SessionToken` | Opaque authentication token | value, expires_at |
| `TotpCode` | Time-based one-time password | value, window |
| `IpAddress` | Client IP address | address, version (v4/v6) |
| `UserAgent` | Client user agent string | raw, parsed components |

### Aggregate Roots

| Aggregate | Root Entity | Invariants |
|---|---|---|
| `UserAccount` | `User` | Must have at least one credential; email must be unique; deactivation cascades to sessions |
| `SessionPool` | `Session` (collection) | Max concurrent sessions per user enforced; expired sessions cleaned up |
| `MfaEnrollment` | `MfaChallenge` | Max 3 verification attempts; code expires after T seconds |

### Domain Events

| Event | Trigger | Payload |
|---|---|---|
| `UserRegistered` | New user account created | user_id, email, registration_method |
| `UserActivated` | Admin activates account | user_id, activated_by |
| `UserDeactivated` | Admin deactivates account | user_id, deactivated_by, reason |
| `PasswordChanged` | User changes password | user_id, changed_by, password_age_days |
| `PasswordResetRequested` | User requests reset | user_id, reset_token, expires_at |
| `PasswordResetCompleted` | Reset flow completed | user_id, reset_by |
| `SessionCreated` | Successful login | user_id, session_id, ip_address, mfa_used |
| `SessionExpired` | Token TTL reached | user_id, session_id, duration_seconds |
| `SessionRevoked` | Explicit logout | user_id, session_id, revoked_by |
| `MfaChallengeIssued` | MFA prompt sent | user_id, challenge_id, method |
| `MfaChallengeVerified` | Correct MFA code submitted | user_id, challenge_id, method |
| `MfaChallengeFailed` | Incorrect MFA code submitted | user_id, challenge_id, attempt_number |

### Domain Services

| Service | Responsibility |
|---|---|
| `AuthenticationService` | Orchestrates credential validation, MFA flow, session creation |
| `PasswordService` | Hash generation, complexity validation, rotation enforcement |
| `SessionService` | Token generation, validation, renewal, revocation |
| `MfaService` | Challenge generation, code verification, TOTP enrollment |
| `TokenService` | JWT creation, parsing, refresh, blacklisting |

### Repositories

| Repository | Aggregate | Operations |
|---|---|---|
| `UserRepository` | UserAccount | find_by_id, find_by_email, save, deactivate |
| `CredentialRepository` | UserAccount | find_by_user_id, save, revoke_all |
| `SessionRepository` | SessionPool | find_by_token, find_active_by_user, revoke, purge_expired |
| `MfaChallengeRepository` | MfaEnrollment | create, find_pending, mark_verified, mark_failed |

---

## Authorization Context

### Domain Entities

| Entity | Description | Key Attributes |
|---|---|---|
| `Role` | A named set of permissions | id, name, description, is_system, created_at |
| `Permission` | A specific allowed action | id, resource, action, description |
| `Policy` | A rule evaluating conditions for access | id, name, conditions, effect, priority |
| `AccessDecision` | The result of an authorization check | allowed, reason, evaluated_policies |

### Value Objects

| Value Object | Description | Attributes |
|---|---|---|
| `ResourceAction` | A resource-action pair | resource (string), action (string) |
| `PolicyCondition` | A boolean expression for policy evaluation | field, operator, value |
| `AccessScope` | The boundary of an access grant | resource_type, resource_id, constraints |

### Aggregate Roots

| Aggregate | Root Entity | Invariants |
|---|---|---|
| `RoleDefinition` | `Role` | System roles cannot be deleted; each role has unique name |
| `PolicySet` | `Policy` | Policies evaluated by priority; no circular references in conditions |

### Domain Events

| Event | Trigger | Payload |
|---|---|---|
| `RoleCreated` | New role defined | role_id, name, created_by |
| `RoleAssigned` | Role granted to user | user_id, role_id, assigned_by, expires_at |
| `RoleRevoked` | Role removed from user | user_id, role_id, revoked_by |
| `PermissionGranted` | Permission added to role | permission_id, role_id |
| `PermissionRevoked` | Permission removed from role | permission_id, role_id |
| `PolicyCreated` | New policy defined | policy_id, name, effect |
| `PolicyUpdated` | Policy modified | policy_id, changed_fields |
| `PolicyDeactivated` | Policy disabled | policy_id, deactivated_by |
| `AccessDenied` | Authorization check failed | user_id, resource, action, reason |
| `PrivilegeEscalationAttempt` | Suspicious permission grant detected | user_id, target_role, detected_by |

### Domain Services

| Service | Responsibility |
|---|---|
| `AuthorizationService` | Evaluates permissions against policies for a user-context pair |
| `PolicyEngine` | Interprets and evaluates policy conditions against request context |
| `RoleManagementService` | CRUD for roles, role assignment, expiration management |

### Repositories

| Repository | Aggregate | Operations |
|---|---|---|
| `RoleRepository` | RoleDefinition | find_by_id, find_by_name, find_all, save |
| `PermissionRepository` | RoleDefinition | find_by_role, find_by_resource_action, save |
| `PolicyRepository` | PolicySet | find_active, find_by_resource, save, deactivate |
| `AccessDecisionRepository` | PolicySet | log_decision, find_recent_by_user |

---

## Education Context

### Domain Entities

| Entity | Description | Key Attributes |
|---|---|---|
| `Course` | A structured learning path | id, title, description, difficulty, is_published, author_id |
| `Module` | A course subdivision with focused topic | id, course_id, title, order, description |
| `Lesson` | Individual instructional unit | id, module_id, title, content_type, content, duration_minutes |
| `Assessment` | An evaluation of learner knowledge | id, module_id, title, passing_score, time_limit_minutes, max_attempts |
| `Question` | A single assessment question | id, assessment_id, type, prompt, options, correct_answer |
| `Enrollment` | A user's registration in a course | id, user_id, course_id, status, enrolled_at, completed_at |
| `LearnerProgress` | Tracking of lesson/module completion | id, user_id, lesson_id, status, score, completed_at |
| `Certificate` | Completion credential | id, user_id, course_id, issued_at, certificate_number |

### Value Objects

| Value Object | Description | Attributes |
|---|---|---|
| `CourseSlug` | URL-safe course identifier | value (lowercase, hyphenated) |
| `DifficultyLevel` | Course difficulty | beginner, intermediate, advanced, expert |
| `ContentType` | Lesson content format | video, text, interactive, lab, quiz |
| `Score` | Assessment result | percentage, passed (boolean) |
| `TimeLimit` | Duration constraint | minutes, is_strict |
| `CompletionStatus` | Progress state | not_started, in_progress, completed, failed |

### Aggregate Roots

| Aggregate | Root Entity | Invariants |
|---|---|---|
| `CourseDefinition` | `Course` | Must have at least one module; title unique; slug unique |
| `AssessmentDefinition` | `Assessment` | Must have at least one question; passing_score 0-100; max_attempts >= 1 |
| `EnrollmentRecord` | `Enrollment` | One enrollment per user per course; cannot enroll in unpublished course |
| `CertificateIssuance` | `Certificate` | Unique certificate_number; issued only after course completion |

### Domain Events

| Event | Trigger | Payload |
|---|---|---|
| `CourseCreated` | New course authored | course_id, title, author_id |
| `CoursePublished` | Course made available | course_id, published_by |
| `CourseUnpublished` | Course hidden from catalog | course_id, unpublished_by |
| `CourseUpdated` | Course metadata changed | course_id, changed_fields |
| `LessonCreated` | New lesson added to module | lesson_id, module_id, title |
| `LessonCompleted` | Learner finishes lesson | lesson_id, user_id, score |
| `AssessmentSubmitted` | Learner submits answers | assessment_id, user_id, submission_id |
| `AssessmentGraded` | Auto or manual grading | assessment_id, user_id, score, passed |
| `ModuleCompleted` | All lessons and assessments done | module_id, user_id |
| `CourseCompleted` | All modules done | course_id, user_id |
| `EnrollmentCreated` | User enrolls in course | enrollment_id, user_id, course_id |
| `EnrollmentCancelled` | User withdraws from course | enrollment_id, user_id, reason |
| `CertificateIssued` | Certificate generated | certificate_id, user_id, course_id, certificate_number |

### Domain Services

| Service | Responsibility |
|---|---|
| `CourseManagementService` | CRUD for courses, modules, lessons; publishing workflow |
| `AssessmentService` | Question management, submission handling, grading logic |
| `EnrollmentService` | Enrollment creation, cancellation, prerequisite checks |
| `ProgressTrackingService` | Records and retrieves learner progress; determines completion |
| `CertificateService` | Issues certificates, validates certificate authenticity |

### Repositories

| Repository | Aggregate | Operations |
|---|---|---|
| `CourseRepository` | CourseDefinition | find_by_id, find_by_slug, find_published, save |
| `ModuleRepository` | CourseDefinition | find_by_course, find_by_id, save |
| `LessonRepository` | CourseDefinition | find_by_module, find_by_id, save |
| `AssessmentRepository` | AssessmentDefinition | find_by_module, find_by_id, save |
| `EnrollmentRepository` | EnrollmentRecord | find_by_user, find_by_course, find_active, save |
| `ProgressRepository` | EnrollmentRecord | find_by_user_course, find_by_lesson, save |
| `CertificateRepository` | CertificateIssuance | find_by_user, find_by_number, save |

---

## Simulation Context

### Domain Entities

| Entity | Description | Key Attributes |
|---|---|---|
| `Simulation` | An attack or defense exercise | id, name, type, difficulty, scenario, is_active |
| `AttackScenario` | A specific attack pattern to simulate | id, simulation_id, attack_type, steps, expected_outcomes |
| `DefenseScenario` | A specific defense exercise | id, simulation_id, defense_type, steps, success_criteria |
| `SimulationSession` | A learner's attempt at a simulation | id, simulation_id, user_id, status, started_at, completed_at |
| `SimulationResult` | Outcome of a simulation attempt | id, session_id, score, metrics, feedback |
| `Vulnerability` | A simulated security weakness | id, simulation_id, name, severity, description |

### Value Objects

| Value Object | Description | Attributes |
|---|---|---|
| `SimulationType` | Category of simulation | attack, defense, hybrid |
| `DifficultyLevel` | Simulation difficulty | beginner, intermediate, advanced, expert |
| `AttackType` | Specific attack category | brute_force, sql_injection, xss, phishing, credential_stuffing |
| `DefenseType` | Specific defense category | firewall_config, log_analysis, incident_response, forensics |
| `SeverityLevel` | Vulnerability severity | low, medium, high, critical |
| `SimulationMetrics` | Performance measurements | time_to_detect, time_to_respond, accuracy, coverage |

### Aggregate Roots

| Aggregate | Root Entity | Invariants |
|---|---|---|
| `SimulationDefinition` | `Simulation` | Must have at least one scenario; difficulty valid |
| `SimulationAttempt` | `SimulationSession` | Cannot start completed simulation; max concurrent attempts |

### Domain Events

| Event | Trigger | Payload |
|---|---|---|
| `SimulationCreated` | New simulation defined | simulation_id, name, type, created_by |
| `SimulationActivated` | Simulation made available | simulation_id |
| `SimulationStarted` | Learner begins attempt | session_id, simulation_id, user_id |
| `SimulationStepCompleted` | Learner completes a step | session_id, step_id, result |
| `SimulationCompleted` | Learner finishes attempt | session_id, score, duration_seconds |
| `SimulationTimedOut` | Time limit exceeded | session_id, partial_score |
| `VulnerabilityDiscovered` | Learner identifies simulated vuln | session_id, vulnerability_id, time_to_discover |
| `DefenseSuccessCriteriaMet` | Defense exercise passed | session_id, criteria_met |

### Domain Services

| Service | Responsibility |
|---|---|
| `SimulationOrchestrator` | Manages simulation lifecycle, step sequencing, timeout enforcement |
| `AttackSimulator` | Executes attack scenario logic, generates simulated responses |
| `DefenseSimulator` | Runs defense exercises, evaluates defensive actions |
| `ResultEvaluator` | Scores simulation performance, generates feedback |

### Repositories

| Repository | Aggregate | Operations |
|---|---|---|
| `SimulationRepository` | SimulationDefinition | find_by_id, find_by_type, find_active, save |
| `AttackScenarioRepository` | SimulationDefinition | find_by_simulation, save |
| `DefenseScenarioRepository` | SimulationDefinition | find_by_simulation, save |
| `SimulationSessionRepository` | SimulationAttempt | find_by_user, find_by_simulation, find_active, save |
| `SimulationResultRepository` | SimulationAttempt | find_by_session, find_best_by_user, save |

---

## Analytics Context

### Domain Entities

| Entity | Description | Key Attributes |
|---|---|---|
| `LearningAnalytics` | Aggregated learning metrics per user | id, user_id, period, courses_completed, hours_spent, avg_score |
| `PerformanceReport` | Detailed report for a user or cohort | id, report_type, generated_at, data, filters |
| `CompetencyRecord` | Demonstrated skill or knowledge area | id, user_id, competency, level, assessed_at |
| `EngagementMetric` | User engagement data points | id, user_id, event_type, timestamp, metadata |

### Value Objects

| Value Object | Description | Attributes |
|---|---|---|
| `TimePeriod` | Reporting period | start_date, end_date, granularity |
| `CompetencyLevel` | Skill proficiency | novice, beginner, proficient, expert, master |
| `MetricValue` | A measured value with context | value, unit, trend (up/down/flat) |
| `CohortFilter` | Grouping criteria for reports | filter_type, values |

### Aggregate Roots

| Aggregate | Root Entity | Invariants |
|---|---|---|
| `AnalyticsDashboard` | `LearningAnalytics` | One analytics record per user per period |
| `CompetencyProfile` | `CompetencyRecord` | One record per user per competency; level monotonically increases |

### Domain Events

| Event | Trigger | Payload |
|---|---|---|
| `AnalyticsRecorded` | New metric captured | user_id, event_type, value |
| `ReportGenerated` | Report completed | report_id, report_type, requested_by |
| `CompetencyAchieved` | User demonstrates new skill level | user_id, competency, level |
| `EngagementThresholdMet` | User hits engagement milestone | user_id, milestone_type, value |
| `LearningStreakRecorded` | Consecutive day activity | user_id, streak_length |

### Domain Services

| Service | Responsibility |
|---|---|
| `AnalyticsAggregator` | Collects raw events into period summaries |
| `ReportGenerator` | Produces formatted reports from analytics data |
| `CompetencyTracker` | Evaluates and updates competency records |
| `EngagementAnalyzer` | Computes engagement metrics and trends |

### Repositories

| Repository | Aggregate | Operations |
|---|---|---|
| `LearningAnalyticsRepository` | AnalyticsDashboard | find_by_user_period, save, aggregate |
| `PerformanceReportRepository` | AnalyticsDashboard | find_by_id, find_by_type, save |
| `CompetencyRecordRepository` | CompetencyProfile | find_by_user, find_by_competency, save |
| `EngagementMetricRepository` | AnalyticsDashboard | find_by_user, find_by_event_type, save |

---

## Operations Context

### Domain Entities

| Entity | Description | Key Attributes |
|---|---|---|
| `AuditLog` | Immutable record of system activity | id, actor_id, action, resource_type, resource_id, timestamp, metadata |
| `ComplianceReport` | Regulatory compliance assessment | id, report_type, generated_at, status, findings |
| `SecurityAlert` | Detected security anomaly or incident | id, severity, type, description, status, detected_at |
| `DeploymentRecord` | Record of a production deployment | id, version, deployed_by, deployed_at, status |
| `SystemHealth` | Health status of system components | id, component, status, last_checked, metrics |

### Value Objects

| Value Object | Description | Attributes |
|---|---|---|
| `AuditAction` | Type of audited action | create, read, update, delete, login, logout, export |
| `ResourceType` | Type of audited resource | user, session, course, assessment, certificate |
| `AlertSeverity` | Security alert level | info, warning, critical, emergency |
| `AlertStatus` | Alert lifecycle state | open, investigating, resolved, dismissed |
| `DeploymentStatus` | Deployment state | pending, in_progress, success, failed, rolled_back |

### Aggregate Roots

| Aggregate | Root Entity | Invariants |
|---|---|---|
| `AuditTrail` | `AuditLog` | Append-only; immutable once written; retention policy enforced |
| `IncidentResponse` | `SecurityAlert` | Critical alerts must be acknowledged within SLA |

### Domain Events

| Event | Trigger | Payload |
|---|---|---|
| `AuditLogCreated` | System activity recorded | audit_id, actor_id, action, resource |
| `ComplianceReportGenerated` | Compliance check completed | report_id, status, findings_count |
| `SecurityAlertTriggered` | Anomaly detected | alert_id, severity, type |
| `SecurityAlertAcknowledged` | Analyst begins investigation | alert_id, acknowledged_by |
| `SecurityAlertResolved` | Incident closed | alert_id, resolved_by, resolution_notes |
| `DeploymentStarted` | New deployment begins | deployment_id, version, target_environment |
| `DeploymentCompleted` | Deployment finished | deployment_id, status, duration_seconds |
| `DeploymentRolledBack` | Deployment reversed | deployment_id, reason |
| `HealthCheckFailed` | Component unhealthy | component, status, last_error |

### Domain Services

| Service | Responsibility |
|---|---|
| `AuditService` | Records, queries, and exports audit logs |
| `ComplianceService` | Runs compliance checks, generates reports |
| `AlertService` | Monitors, triggers, escalates, and resolves security alerts |
| `DeploymentService` | Manages deployment lifecycle and rollback |
| `HealthMonitor` | Periodic health checks, status aggregation |

### Repositories

| Repository | Aggregate | Operations |
|---|---|---|
| `AuditLogRepository` | AuditTrail | append, find_by_actor, find_by_resource, find_by_date_range |
| `ComplianceReportRepository` | AuditTrail | find_by_type, find_latest, save |
| `SecurityAlertRepository` | IncidentResponse | find_open, find_by_severity, save |
| `DeploymentRecordRepository` | AuditTrail | find_latest, find_by_version, save |
| `SystemHealthRepository` | AuditTrail | find_by_component, find_all_status, save |

---

## Context Map

### Relationships Between Bounded Contexts

```
┌──────────────┐       ┌──────────────────┐
│   Identity   │──────▶│  Authorization   │
│              │       │                  │
│  User, Auth  │       │  Roles, Policies │
└──────┬───────┘       └────────┬─────────┘
       │                        │
       │    ┌───────────────────┘
       │    │
       ▼    ▼
┌──────────────┐       ┌──────────────────┐
│   Education  │◀─────▶│   Simulation     │
│              │       │                  │
│  Courses,    │       │  Attacks,        │
│  Assessments │       │  Defenses        │
└──────┬───────┘       └────────┬─────────┘
       │                        │
       │    ┌───────────────────┘
       │    │
       ▼    ▼
┌──────────────┐       ┌──────────────────┐
│  Analytics   │◀─────▶│   Operations     │
│              │       │                  │
│  Reports,    │       │  Audit, Alerts,  │
│  Metrics     │       │  Compliance      │
└──────────────┘       └──────────────────┘
```

### Relationship Types

| Relationship | From | To | Type | Description |
|---|---|---|---|---|
| Identity → Authorization | User | Role/Permission | Upstream-Downstream | Identity provides user context; Authorization consumes it |
| Identity → Education | User | Enrollment | Partnership | User enrolls; Education consumes identity |
| Education → Simulation | Course | Simulation | Conformist | Simulations referenced within courses |
| Education → Analytics | Progress | Metrics | Data Feed | Education generates data consumed by Analytics |
| Simulation → Analytics | Results | Metrics | Data Feed | Simulation results feed into analytics |
| Operations → All | AuditLog | Events | Customer-Supplier | Operations consumes events from all contexts |
| Analytics → Operations | Reports | Compliance | Partnership | Analytics data used for compliance reporting |

### ACL Boundaries (Anti-Corruption Layers)

| Boundary | Protecting | From | Translation |
|---|---|---|---|
| Identity ACL | Identity context | External IdPs (OAuth, LDAP) | External tokens → internal User/Credential |
| Education ACL | Education context | External content providers | External content formats → internal Lesson content |
| Simulation ACL | Simulation context | Security tool APIs | Tool responses → SimulationResult |
| Operations ACL | Operations context | SIEM / Monitoring | Events → AuditLog format |

---

## Ubiquitous Language Glossary

### Identity Context

| Term | Definition |
|---|---|
| **User** | A registered person with a unique identity in the system |
| **Credential** | Authentication material (password hash, OAuth token, SSH key) |
| **Session** | An authenticated connection with a finite lifetime |
| **Login** | The act of authenticating and receiving a session |
| **Logout** | Explicitly terminating an active session |
| **Token** | An opaque string used to represent an authenticated session |
| **MFA** | Multi-Factor Authentication; requires multiple verification steps |
| **TOTP** | Time-based One-Time Password algorithm for MFA |
| **Lockout** | Temporary account restriction after failed attempts |
| **Password Rotation** | Periodic requirement to change passwords |
| **Account Activation** | Enabling a user account after registration or admin action |
| **Account Deactivation** | Disabling a user account while preserving data |

### Authorization Context

| Term | Definition |
|---|---|
| **Role** | A named collection of permissions assigned to users |
| **Permission** | An authorization to perform a specific action on a resource |
| **Policy** | A rule that evaluates context to grant or deny access |
| **RBAC** | Role-Based Access Control; authorization via role assignments |
| **ABAC** | Attribute-Based Access Control; authorization via attribute evaluation |
| **Access Decision** | The outcome (allow/deny) of an authorization check |
| **Privilege** | The ability to perform protected operations |
| **Scope** | The boundary of a permission grant (e.g., own data only) |

### Education Context

| Term | Definition |
|---|---|
| **Course** | A structured sequence of learning content on a topic |
| **Module** | A focused section within a course covering one subtopic |
| **Lesson** | An individual instructional unit (video, text, interactive, lab) |
| **Assessment** | An evaluation testing learner knowledge at module or course level |
| **Question** | A single item within an assessment (multiple choice, fill-in, code) |
| **Enrollment** | A user's registration and participation in a course |
| **Progress** | Tracking of which lessons and modules a learner has completed |
| **Score** | A numerical result on an assessment or exercise |
| **Certificate** | A document proving completion of a course |
| **Competency** | A demonstrable skill or knowledge area |
| **Prerequisite** | A requirement (course, skill, score) before enrollment or access |

### Simulation Context

| Term | Definition |
|---|---|
| **Simulation** | A controlled cybersecurity exercise (attack or defense) |
| **Attack Scenario** | A simulated offensive technique with steps and outcomes |
| **Defense Scenario** | A simulated defensive exercise with actions and success criteria |
| **Vulnerability** | A simulated weakness identified during an attack exercise |
| **Severity** | The risk level of a vulnerability (low, medium, high, critical) |
| **Time to Detect** | How quickly a learner identifies a simulated threat |
| **Time to Respond** | How quickly a learner takes effective action |

### Analytics Context

| Term | Definition |
|---|---|
| **Learning Analytics** | Aggregated data about learner behavior and outcomes |
| **Engagement** | Measures of learner activity frequency and depth |
| **Performance Report** | A formatted summary of learning outcomes for a user or cohort |
| **Competency Record** | A demonstrated skill level at a point in time |
| **Cohort** | A group of learners sharing common characteristics |
| **Learning Streak** | Consecutive days of learner activity |

### Operations Context

| Term | Definition |
|---|---|
| **Audit Log** | An immutable, chronological record of system events |
| **Compliance** | Adherence to regulatory and organizational policies |
| **Security Alert** | A detected anomaly or potential security incident |
| **Deployment** | The process of releasing a new version to production |
| **Rollback** | Reverting a deployment to a previous version |
| **Health Check** | A periodic test of a component's operational status |
| **SLA** | Service Level Agreement; time commitment for response |
| **Incident** | A confirmed security event requiring response |

---

*Last updated: 2025-01-15*
*Owner: AuthShield Lab Engineering*
