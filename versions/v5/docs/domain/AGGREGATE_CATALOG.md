# AuthShield Lab - Aggregate Catalog

## Overview

This document defines all aggregates in AuthShield Lab, specifying aggregate roots, entities, value objects, business invariants, commands, queries, events, repositories, factories, and validation rules for each aggregate.

---

## Aggregate Catalog Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AuthShield Lab Aggregates                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │    User          │  │    Session      │  │    Course       │            │
│  │    Aggregate     │  │    Aggregate    │  │    Aggregate    │            │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤            │
│  │ Root: User      │  │ Root: Session   │  │ Root: Course    │            │
│  │ Entities:       │  │ Entities:       │  │ Entities:       │            │
│  │  - UserProfile  │  │  - SessionToken │  │  - Module       │            │
│  │  - Role         │  │  - DeviceInfo   │  │  - Lesson       │            │
│  │  - Permission   │  │ Value Objects:  │  │  - Enrollment   │            │
│  │ Value Objects:  │  │  - SessionId    │  │ Value Objects:  │            │
│  │  - Email        │  │  - ExpiryTime   │  │  - CourseCode   │            │
│  │  - Username     │  │  - RefreshToken │  │  - LessonId     │            │
│  │  - Password     │  │                 │  │  - ModuleId     │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │  Assessment      │  │  Certificate    │  │  Simulation     │            │
│  │  Aggregate       │  │  Aggregate      │  │  Aggregate      │            │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤            │
│  │ Root: Assessment│  │ Root: Certificate│ │ Root: Simulation│            │
│  │ Entities:       │  │ Entities:       │  │ Entities:       │            │
│  │  - Question     │  │  - Issuance     │  │  - Scenario     │            │
│  │  - Answer       │  │ Value Objects:  │  │  - Execution    │            │
│  │  - Score        │  │  - CertificateId│  │ Value Objects:  │            │
│  │ Value Objects:  │  │  - IssuanceDate │  │  - SimulationId │            │
│  │  - AssessmentId │  │  - ValidityPeriod│ │  - ScenarioConfig│            │
│  │  - QuestionId   │  │                 │  │  - ExecutionLog │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │    Plugin        │  │  Configuration  │  │    Audit        │            │
│  │    Aggregate     │  │  Aggregate      │  │    Aggregate    │            │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤            │
│  │ Root: Plugin    │  │ Root: Config    │  │ Root: AuditLog  │            │
│  │ Entities:       │  │ Entities:       │  │ Entities:       │            │
│  │  - PluginVersion│  │  - Setting      │  │  - AuditEntry   │            │
│  │  - Capability   │  │  - Category     │  │  - AuditQuery   │            │
│  │ Value Objects:  │  │ Value Objects:  │  │ Value Objects:  │            │
│  │  - PluginId     │  │  - ConfigKey    │  │  - AuditEntryId │            │
│  │  - SemanticVer  │  │  - ConfigValue  │  │  - Timestamp    │            │
│  │  - CapabilityId │  │  - ConfigType   │  │  - EventType    │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. User Aggregate

### Aggregate Root: User

**Bounded Context:** Identity Context

### Entities

#### User (Root)
| Attribute | Type | Description |
|-----------|------|-------------|
| userId | UUID | Unique identifier |
| email | Email | User's email address |
| username | Username | Unique username |
| passwordHash | PasswordHash | Hashed password |
| status | UserStatus | Account status |
| createdAt | DateTime | Creation timestamp |
| updatedAt | DateTime | Last update timestamp |
| lastLoginAt | DateTime | Last login timestamp |

#### UserProfile
| Attribute | Type | Description |
|-----------|------|-------------|
| profileId | UUID | Profile identifier |
| userId | UUID | Parent user reference |
| displayName | string | Display name |
| avatarUrl | URL | Profile picture URL |
| bio | string | User biography |
| timezone | string | User timezone |
| language | LanguageCode | Preferred language |

#### Role
| Attribute | Type | Description |
|-----------|------|-------------|
| roleId | UUID | Role identifier |
| name | string | Role name |
| description | string | Role description |
| hierarchy | int | Role hierarchy level |
| permissions | Permission[] | Assigned permissions |
| isSystem | boolean | System-defined role |

#### Permission
| Attribute | Type | Description |
|-----------|------|-------------|
| permissionId | UUID | Permission identifier |
| resource | string | Resource type |
| action | string | Allowed action |
| conditions | JSON | Conditional rules |

### Value Objects

| Value Object | Attributes | Validation Rules |
|--------------|------------|------------------|
| Email | address | RFC 5322 format, max 254 chars, unique |
| Username | value | 3-50 chars, alphanumeric + underscore, unique |
| PasswordHash | hash, algorithm, salt | bcrypt/argon2, min 60 chars |
| UserStatus | status | Enum: active, suspended, pending, deleted |

### Business Invariants
- INV-USER-001: User must have unique email address
- INV-USER-002: Username must be unique across platform
- INV-USER-003: Password must meet complexity requirements
- INV-USER-004: Suspended users cannot authenticate
- INV-USER-005: Deleted users cannot be reactivated with same email for 90 days
- INV-USER-006: User must have at least one active role
- INV-USER-007: Profile display name cannot be empty

### Commands
| Command | Description | Validation |
|---------|-------------|------------|
| CreateUser | Register new user | Email unique, password valid |
| UpdateProfile | Modify user profile | Display name required |
| ChangePassword | Update password | Current password valid, new password complex |
| SuspendUser | Temporarily disable account | Reason required, admin auth |
| DeleteUser | Remove user account | Soft delete, 90-day grace period |
| AssignRole | Add role to user | Role exists, user active |
| RemoveRole | Remove role from user | Cannot remove last role |

### Queries
| Query | Description | Access Control |
|-------|-------------|----------------|
| GetUserById | Fetch user by ID | Self or admin |
| GetUserByEmail | Find user by email | Admin only |
| GetUserProfile | Get user profile | Self or public |
| GetUserRoles | List user roles | Self or admin |
| ListUsers | Paginated user list | Admin only |
| SearchUsers | User search | Admin only |

### Events
| Event | Publisher | Subscribers |
|-------|-----------|-------------|
| UserCreated | User Aggregate | Education, Analytics, Notification |
| UserUpdated | User Aggregate | Analytics, Notification |
| UserDeleted | User Aggregate | Education, Analytics, Audit |
| PasswordChanged | User Aggregate | Audit, Security |
| RoleAssigned | User Aggregate | Authorization, Analytics |
| RoleRemoved | User Aggregate | Authorization, Analytics |

### Repositories
| Repository | Methods | Query Specs |
|------------|---------|-------------|
| UserRepository | findById, findByEmail, findByUsername, save, delete | UserByIdSpec, UserByEmailSpec, ActiveUsersSpec |
| RoleRepository | findById, findByName, save, delete | RoleByIdSpec, SystemRolesSpec |
| PermissionRepository | findByResource, findByRole, save | PermissionByResourceSpec |

### Factories
| Factory | Creates | Validation |
|---------|---------|------------|
| UserFactory.create(email, username, password) | User | Email unique, username unique, password valid |
| UserFactory.createFromOAuth(provider, data) | User | Provider data valid, email verified |
| UserProfileFactory.create(userId, data) | UserProfile | Display name provided |

### Validation Rules
| Rule | Field | Condition | Error |
|------|-------|-----------|-------|
| VAL-USER-001 | email | RFC 5322 format | Invalid email format |
| VAL-USER-002 | username | 3-50 chars, alphanumeric_ | Invalid username |
| VAL-USER-003 | password | Min 8 chars, complexity | Weak password |
| VAL-USER-004 | displayName | Non-empty, max 100 chars | Invalid display name |
| VAL-USER-005 | timezone | Valid timezone string | Invalid timezone |

---

## 2. Session Aggregate

### Aggregate Root: Session

**Bounded Context:** Session Context

### Entities

#### Session (Root)
| Attribute | Type | Description |
|-----------|------|-------------|
| sessionId | UUID | Unique identifier |
| userId | UUID | Associated user |
| status | SessionStatus | Current status |
| createdAt | DateTime | Creation time |
| expiresAt | DateTime | Expiration time |
| lastActivityAt | DateTime | Last activity |
| ipAddress | IP | Client IP address |
| userAgent | string | Client user agent |

#### SessionToken
| Attribute | Type | Description |
|-----------|------|-------------|
| tokenId | UUID | Token identifier |
| sessionId | UUID | Parent session |
| tokenHash | string | Hashed token value |
| type | TokenType | Access or refresh |
| expiresAt | DateTime | Token expiration |
| isRevoked | boolean | Revocation status |

#### DeviceInfo
| Attribute | Type | Description |
|-----------|------|-------------|
| deviceId | string | Device fingerprint |
| deviceType | DeviceType | Browser, mobile, etc. |
| os | string | Operating system |
| browser | string | Browser name |
| isTrusted | boolean | Trusted device flag |

### Value Objects

| Value Object | Attributes | Validation Rules |
|--------------|------------|------------------|
| SessionId | value | UUID v4, unique |
| ExpiryTime | datetime | Future datetime, max 30 days |
| RefreshToken | token, expiresAt | Min 32 chars, future expiry |
| SessionStatus | status | Enum: active, expired, revoked |
| TokenType | type | Enum: access, refresh |

### Business Invariants
- INV-SESS-001: Session must have valid user reference
- INV-SESS-002: Session expires after 24 hours of inactivity
- INV-SESS-003: Maximum 5 concurrent sessions per user
- INV-SESS-004: Refresh tokens rotate every 4 hours
- INV-SESS-005: Revoked sessions cannot be reactivated
- INV-SESS-006: Suspicious activity triggers automatic revocation
- INV-SESS-007: Token hash must be bcrypt-hashed

### Commands
| Command | Description | Validation |
|---------|-------------|------------|
| CreateSession | Start new session | User active, limit not exceeded |
| ValidateSession | Check session validity | Token exists, not expired, not revoked |
| RefreshSession | Rotate tokens | Valid refresh token, session active |
| RevokeSession | Terminate session | Session exists, user authorized |
| RevokeAllSessions | Terminate all user sessions | User authenticated |
| ExtendSession | Extend session expiry | Session active, within limits |

### Queries
| Query | Description | Access Control |
|-------|-------------|----------------|
| GetSessionById | Fetch session details | Self or admin |
| GetUserSessions | List user's active sessions | Self only |
| GetActiveSessions | Count active sessions | System only |
| FindSessionByToken | Lookup session by token | System only |
| GetSessionHistory | Historical session data | Self or admin |

### Events
| Event | Publisher | Subscribers |
|-------|-----------|-------------|
| SessionCreated | Session Aggregate | Analytics, Security |
| SessionExpired | Session Aggregate | Analytics, Audit |
| SessionRevoked | Session Aggregate | Analytics, Security |
| SessionRefreshed | Session Aggregate | Analytics |
| SuspiciousActivity | Session Aggregate | Security, Alerting |

### Repositories
| Repository | Methods | Query Specs |
|------------|---------|-------------|
| SessionRepository | findById, findByUserId, save, delete | ActiveSessionSpec, UserSessionsSpec |
| TokenRepository | findByHash, save, revoke | ValidTokenSpec, ExpiredTokenSpec |
| DeviceRepository | findByDeviceId, save | TrustedDeviceSpec |

### Factories
| Factory | Creates | Validation |
|---------|---------|------------|
| SessionFactory.create(userId, deviceInfo) | Session | User active, device valid |
| SessionTokenFactory.create(sessionId, type) | SessionToken | Session active, type valid |

### Validation Rules
| Rule | Field | Condition | Error |
|------|-------|-----------|-------|
| VAL-SESS-001 | ipAddress | Valid IP format | Invalid IP |
| VAL-SESS-002 | userAgent | Non-empty string | Invalid user agent |
| VAL-SESS-003 | expiresAt | Future datetime | Invalid expiry |
| VAL-SESS-004 | deviceId | Non-empty, consistent | Invalid device |

---

## 3. Course Aggregate

### Aggregate Root: Course

**Bounded Context:** Education Context

### Entities

#### Course (Root)
| Attribute | Type | Description |
|-----------|------|-------------|
| courseId | UUID | Unique identifier |
| title | string | Course title |
| description | string | Course description |
| courseCode | CourseCode | Unique course code |
| status | CourseStatus | Publication status |
| creatorId | UUID | Creator reference |
| modules | Module[] | Course modules |
| prerequisites | UUID[] | Required courses |
| createdAt | DateTime | Creation time |
| publishedAt | DateTime | Publication time |

#### Module
| Attribute | Type | Description |
|-----------|------|-------------|
| moduleId | UUID | Module identifier |
| courseId | UUID | Parent course |
| title | string | Module title |
| description | string | Module description |
| order | int | Display order |
| lessons | Lesson[] | Module lessons |
| duration | Duration | Estimated duration |

#### Lesson
| Attribute | Type | Description |
|-----------|------|-------------|
| lessonId | UUID | Lesson identifier |
| moduleId | UUID | Parent module |
| title | string | Lesson title |
| type | LessonType | Video, text, interactive |
| content | string | Lesson content |
| duration | Duration | Estimated duration |
| order | int | Display order |
| isRequired | boolean | Required for completion |

#### Enrollment
| Attribute | Type | Description |
|-----------|------|-------------|
| enrollmentId | UUID | Enrollment identifier |
| courseId | UUID | Enrolled course |
| userId | UUID | Enrolled user |
| status | EnrollmentStatus | Enrollment status |
| enrolledAt | DateTime | Enrollment time |
| expiresAt | DateTime | Access expiry |
| completedAt | DateTime | Completion time |

### Value Objects

| Value Object | Attributes | Validation Rules |
|--------------|------------|------------------|
| CourseCode | value | Format: [A-Z]{2,4}-[0-9]{3,4}, unique |
| LessonId | value | UUID v4, unique within course |
| ModuleId | value | UUID v4, unique within course |
| CourseStatus | status | Enum: draft, review, published, archived |
| EnrollmentStatus | status | Enum: active, completed, expired, withdrawn |
| Duration | minutes | Positive integer, max 480 minutes |

### Business Invariants
- INV-COURSE-001: Course must have at least 3 modules to publish
- INV-COURSE-002: Each module must have at least 1 lesson
- INV-COURSE-003: Course code must be unique across platform
- INV-COURSE-004: Prerequisites must exist and be published
- INV-COURSE-005: Lessons must have unique order within module
- INV-COURSE-006: Enrollment expiry must be future date
- INV-COURSE-007: Course title max 200 characters
- INV-COURSE-008: At least 30% of lessons must be required

### Commands
| Command | Description | Validation |
|---------|-------------|------------|
| CreateCourse | Create new course | Title provided, creator valid |
| UpdateCourse | Modify course details | Course in draft/review status |
| PublishCourse | Make course public | Meets publication requirements |
| ArchiveCourse | Retire course | No active enrollments or transfer |
| AddModule | Add module to course | Course in draft status |
| ReorderModules | Change module order | Valid sequence provided |
| AddLesson | Add lesson to module | Module exists, content provided |
| EnrollUser | Register user in course | User active, prerequisites met |
| WithdrawUser | Remove user enrollment | Enrollment active, within window |

### Queries
| Query | Description | Access Control |
|-------|-------------|----------------|
| GetCourseById | Fetch course details | Published: all, Draft: creator/admin |
| GetCourseByCode | Find by course code | Published: all, Draft: creator/admin |
| ListCourses | Paginated course list | Published: all, All: admin |
| GetUserEnrollments | User's enrolled courses | Self only |
| GetCourseModules | List course modules | Enrolled or admin |
| GetModuleLessons | List module lessons | Enrolled or admin |
| SearchCourses | Course search | Published: all, All: admin |

### Events
| Event | Publisher | Subscribers |
|-------|-----------|-------------|
| CourseCreated | Course Aggregate | Analytics, Notification |
| CoursePublished | Course Aggregate | Learning, Analytics, Notification |
| CourseArchived | Course Aggregate | Learning, Analytics |
| ModuleAdded | Course Aggregate | Learning, Analytics |
| LessonAdded | Course Aggregate | Learning |
| EnrollmentCreated | Course Aggregate | Learning, Analytics, Notification |
| EnrollmentWithdrawn | Course Aggregate | Analytics, Notification |

### Repositories
| Repository | Methods | Query Specs |
|------------|---------|-------------|
| CourseRepository | findById, findByCode, save, delete | PublishedCourseSpec, CourseByCreatorSpec |
| ModuleRepository | findById, findByCourse, save | ModuleByCourseSpec |
| LessonRepository | findById, findByModule, save | LessonByModuleSpec |
| EnrollmentRepository | findById, findByUser, findByCourse, save | ActiveEnrollmentSpec |

### Factories
| Factory | Creates | Validation |
|---------|---------|------------|
| CourseFactory.create(creatorId, title, code) | Course | Code unique, creator valid |
| ModuleFactory.create(courseId, title, order) | Module | Course exists, order valid |
| LessonFactory.create(moduleId, title, type) | Lesson | Module exists, type valid |
| EnrollmentFactory.create(userId, courseId) | Enrollment | User active, course published, prerequisites met |

### Validation Rules
| Rule | Field | Condition | Error |
|------|-------|-----------|-------|
| VAL-COURSE-001 | title | 1-200 chars | Invalid title |
| VAL-COURSE-002 | courseCode | Format [A-Z]{2,4}-[0-9]{3,4} | Invalid code format |
| VAL-COURSE-003 | description | Max 5000 chars | Description too long |
| VAL-COURSE-004 | order | Positive integer | Invalid order |
| VAL-COURSE-005 | duration | 1-480 minutes | Invalid duration |

---

## 4. Assessment Aggregate

### Aggregate Root: Assessment

**Bounded Context:** Assessment Context

### Entities

#### Assessment (Root)
| Attribute | Type | Description |
|-----------|------|-------------|
| assessmentId | UUID | Unique identifier |
| title | string | Assessment title |
| type | AssessmentType | Quiz, exam, practical |
| courseId | UUID | Associated course |
| questions | Question[] | Assessment questions |
| timeLimit | Duration | Time limit |
| passingScore | AssessmentScore | Required score |
| maxAttempts | int | Allowed attempts |
| isRandomized | boolean | Question randomization |
| status | AssessmentStatus | Current status |

#### Question
| Attribute | Type | Description |
|-----------|------|-------------|
| questionId | UUID | Question identifier |
| assessmentId | UUID | Parent assessment |
| type | QuestionType | Multiple choice, essay, etc. |
| text | string | Question text |
| options | Answer[] | Answer options |
| correctAnswer | UUID | Correct answer reference |
| points | int | Point value |
| order | int | Display order |
| explanation | string | Answer explanation |

#### Answer
| Attribute | Type | Description |
|-----------|------|-------------|
| answerId | UUID | Answer identifier |
| questionId | UUID | Parent question |
| text | string | Answer text |
| isCorrect | boolean | Correctness flag |
| feedback | string | Answer feedback |

#### Score
| Attribute | Type | Description |
|-----------|------|-------------|
| scoreId | UUID | Score identifier |
| assessmentId | UUID | Assessed assessment |
| userId | UUID | Assessed user |
| value | AssessmentScore | Score value |
| maxScore | AssessmentScore | Maximum possible |
| gradedAt | DateTime | Grading time |
| attempt | int | Attempt number |

### Value Objects

| Value Object | Attributes | Validation Rules |
|--------------|------------|------------------|
| AssessmentId | value | UUID v4, unique |
| QuestionId | value | UUID v4, unique within assessment |
| AssessmentScore | value | 0-100 or 0-maxPoints |
| AssessmentType | type | Enum: quiz, exam, practical, competency |
| QuestionType | type | Enum: multiple_choice, true_false, essay, code |
| AssessmentStatus | status | Enum: draft, active, archived |

### Business Invariants
- INV-ASSESS-001: Assessment must have at least 1 question
- INV-ASSESS-002: Questions must have unique order within assessment
- INV-ASSESS-003: Correct answer must reference valid option
- INV-ASSESS-004: Points must be positive integer
- INV-ASSESS-005: Time limit must be positive if specified
- INV-ASSESS-006: Passing score must be between 0 and max score
- INV-ASSESS-007: Max attempts must be at least 1
- INV-ASSESS-008: Question pool must have minimum 20 questions for randomization

### Commands
| Command | Description | Validation |
|---------|-------------|------------|
| CreateAssessment | Create new assessment | Title provided, course exists |
| AddQuestion | Add question to assessment | Assessment in draft |
| UpdateQuestion | Modify question | Assessment in draft |
| RemoveQuestion | Delete question | Assessment in draft, min questions maintained |
| PublishAssessment | Activate assessment | Meets requirements |
| StartAssessment | Begin assessment attempt | User enrolled, attempts remaining |
| SubmitAssessment | Submit responses | Within time limit, all required answered |
| GradeAssessment | Score assessment | Submission exists, auto or manual grading |

### Queries
| Query | Description | Access Control |
|-------|-------------|----------------|
| GetAssessmentById | Fetch assessment details | Creator, enrolled, admin |
| GetAssessmentByCourse | Assessments for course | Enrolled or admin |
| GetQuestionById | Fetch question | During assessment: randomize, After: creator |
| GetUserScores | User's assessment scores | Self or admin |
| GetAssessmentResults | Aggregate results | Creator or admin |
| GetQuestionPool | Random question subset | System only |

### Events
| Event | Publisher | Subscribers |
|-------|-----------|-------------|
| AssessmentCreated | Assessment Aggregate | Analytics |
| AssessmentPublished | Assessment Aggregate | Learning, Notification |
| AssessmentStarted | Assessment Aggregate | Analytics, Security |
| AssessmentSubmitted | Assessment Aggregate | Learning, Analytics |
| AssessmentGraded | Assessment Aggregate | Learning, Certificate, Analytics |
| CompetencyAchieved | Assessment Aggregate | Certificate, Analytics |

### Repositories
| Repository | Methods | Query Specs |
|------------|---------|-------------|
| AssessmentRepository | findById, findByCourse, save | ActiveAssessmentSpec, CourseAssessmentsSpec |
| QuestionRepository | findById, findByAssessment, save | QuestionByAssessmentSpec, RandomQuestionSpec |
| AnswerRepository | findById, findByQuestion, save | CorrectAnswerSpec |
| ScoreRepository | findByUser, findByAssessment, save | UserScoreSpec, AssessmentScoresSpec |

### Factories
| Factory | Creates | Validation |
|---------|---------|------------|
| AssessmentFactory.create(courseId, title, type) | Assessment | Course exists, type valid |
| QuestionFactory.create(assessmentId, type, text) | Question | Assessment exists, text valid |
| AnswerFactory.create(questionId, text, isCorrect) | Answer | Question exists, text valid |

### Validation Rules
| Rule | Field | Condition | Error |
|------|-------|-----------|-------|
| VAL-ASSESS-001 | title | 1-200 chars | Invalid title |
| VAL-ASSESS-002 | text | Non-empty, max 5000 chars | Invalid question text |
| VAL-ASSESS-003 | points | Positive integer | Invalid points |
| VAL-ASSESS-004 | timeLimit | Positive or null | Invalid time limit |
| VAL-ASSESS-005 | passingScore | 0-100 or 0-maxPoints | Invalid passing score |

---

## 5. Certificate Aggregate

### Aggregate Root: Certificate

**Bounded Context:** Certification Context

### Entities

#### Certificate (Root)
| Attribute | Type | Description |
|-----------|------|-------------|
| certificateId | UUID | Unique identifier |
| userId | UUID | Certificate holder |
| courseId | UUID | Certified course |
| templateId | UUID | Certificate template |
| status | CertificateStatus | Current status |
| issuedAt | DateTime | Issuance time |
| expiresAt | DateTime | Expiry time |
| verificationCode | string | Unique verification code |
| metadata | JSON | Additional data |

#### Issuance
| Attribute | Type | Description |
|-----------|------|-------------|
| issuanceId | UUID | Issuance identifier |
| certificateId | UUID | Parent certificate |
| issuedBy | UUID | Issuer reference |
| reason | string | Issuance reason |
| criteria | JSON | Achievement criteria met |
| issuedAt | DateTime | Issuance timestamp |

#### Revocation
| Attribute | Type | Description |
|-----------|------|-------------|
| revocationId | UUID | Revocation identifier |
| certificateId | UUID | Revoked certificate |
| revokedBy | UUID | Revoker reference |
| reason | string | Revocation reason |
| revokedAt | DateTime | Revocation timestamp |

### Value Objects

| Value Object | Attributes | Validation Rules |
|--------------|------------|------------------|
| CertificateId | value | UUID v4, unique |
| IssuanceDate | date | Valid date, not future |
| ValidityPeriod | startDate, endDate | Start before end, max 5 years |
| CertificateStatus | status | Enum: pending, active, expired, revoked |
| VerificationCode | value | 12-char alphanumeric, unique |

### Business Invariants
- INV-CERT-001: Certificate requires course completion
- INV-CERT-002: Certificate requires minimum score (80% default)
- INV-CERT-003: Verification code must be unique
- INV-CERT-004: Expiry must be after issuance date
- INV-CERT-005: Revoked certificates cannot be reinstated
- INV-CERT-006: Certificate must reference valid template
- INV-CERT-007: Max validity period is 5 years
- INV-CERT-008: Renewal must occur within 30 days of expiry

### Commands
| Command | Description | Validation |
|---------|-------------|------------|
| IssueCertificate | Create certificate | Requirements met, template exists |
| RevokeCertificate | Revoke certificate | Active certificate, reason provided |
| RenewCertificate | Extend certificate | Within renewal window, requirements met |
| VerifyCertificate | Check validity | Certificate exists |
| UpdateMetadata | Modify certificate data | Certificate exists, valid changes |

### Queries
| Query | Description | Access Control |
|-------|-------------|----------------|
| GetCertificateById | Fetch certificate | Holder, issuer, admin |
| GetCertificateByCode | Verify by code | Public (limited data) |
| GetUserCertificates | User's certificates | Self or admin |
| GetCourseCertificates | Certificates for course | Creator or admin |
| VerifyCertificate | Validate certificate | Public API |
| GetExpiredCertificates | Find expired certs | System only |

### Events
| Event | Publisher | Subscribers |
|-------|-----------|-------------|
| CertificateIssued | Certificate Aggregate | Notification, Analytics |
| CertificateRevoked | Certificate Aggregate | Notification, Analytics |
| CertificateExpired | Certificate Aggregate | Notification, Analytics |
| CertificateRenewed | Certificate Aggregate | Notification, Analytics |

### Repositories
| Repository | Methods | Query Specs |
|------------|---------|-------------|
| CertificateRepository | findById, findByCode, findByUser, save | ActiveCertSpec, UserCertsSpec |
| IssuanceRepository | findById, findByCertificate, save | IssuanceByCertSpec |
| RevocationRepository | findById, findByCertificate, save | RevocationByCertSpec |

### Factories
| Factory | Creates | Validation |
|---------|---------|------------|
| CertificateFactory.create(userId, courseId, templateId) | Certificate | User completed course, template exists |
| IssuanceFactory.create(certificateId, issuedBy, reason) | Issuance | Certificate pending, issuer authorized |

### Validation Rules
| Rule | Field | Condition | Error |
|------|-------|-----------|-------|
| VAL-CERT-001 | verificationCode | 12-char alphanumeric | Invalid verification code |
| VAL-CERT-002 | expiresAt | After issuedAt, max 5 years | Invalid expiry |
| VAL-CERT-003 | reason | Non-empty for revocation | Reason required |
| VAL-CERT-004 | templateId | Valid template exists | Invalid template |

---

## 6. Simulation Aggregate

### Aggregate Root: Simulation

**Bounded Context:** Simulation Context

### Entities

#### Simulation (Root)
| Attribute | Type | Description |
|-----------|------|-------------|
| simulationId | UUID | Unique identifier |
| title | string | Simulation title |
| description | string | Description |
| difficulty | DifficultyLevel | Easy, medium, hard |
| scenarios | Scenario[] | Available scenarios |
| requiredSkills | string[] | Prerequisites |
| estimatedDuration | Duration | Time estimate |
| status | SimulationStatus | Current status |

#### Scenario
| Attribute | Type | Description |
|-----------|------|-------------|
| scenarioId | UUID | Scenario identifier |
| simulationId | UUID | Parent simulation |
| title | string | Scenario title |
| config | ScenarioConfig | Configuration |
| steps | ScenarioStep[] | Execution steps |
| successCriteria | JSON | Completion requirements |
| hints | string[] | Available hints |

#### Execution
| Attribute | Type | Description |
|-----------|------|-------------|
| executionId | UUID | Execution identifier |
| simulationId | UUID | Executed simulation |
| scenarioId | UUID | Executed scenario |
| userId | UUID | Executor |
| status | ExecutionStatus | Current status |
| startedAt | DateTime | Start time |
| completedAt | DateTime | End time |
| results | JSON | Execution results |
| score | number | Performance score |

#### ScenarioStep
| Attribute | Type | Description |
|-----------|------|-------------|
| stepId | UUID | Step identifier |
| scenarioId | UUID | Parent scenario |
| order | int | Step order |
| action | string | Required action |
| expectedOutcome | string | Expected result |
| points | int | Step value |

### Value Objects

| Value Object | Attributes | Validation Rules |
|--------------|------------|------------------|
| SimulationId | value | UUID v4, unique |
| ScenarioConfig | env, resources, constraints | Valid environment, resource limits |
| DifficultyLevel | level | Enum: beginner, intermediate, advanced, expert |
| ExecutionStatus | status | Enum: pending, running, completed, failed, timeout |
| Duration | minutes | Positive integer, max 480 |

### Business Invariants
- INV-SIM-001: Simulation must have at least 1 scenario
- INV-SIM-002: Scenarios must have unique order
- INV-SIM-003: Execution requires valid user and simulation
- INV-SIM-004: Completed executions cannot be restarted
- INV-SIM-005: Score must be between 0 and total points
- INV-SIM-006: Execution timeout at 4 hours
- INV-SIM-007: Success criteria must reference valid steps
- INV-SIM-008: Hints reduce maximum possible score by 10% each

### Commands
| Command | Description | Validation |
|---------|-------------|------------|
| CreateSimulation | Create simulation | Title, scenarios provided |
| AddScenario | Add scenario | Simulation in draft |
| UpdateScenario | Modify scenario | Simulation in draft |
| StartExecution | Begin execution | User eligible, simulation active |
| RecordStep | Log step completion | Execution active, step valid |
| CompleteExecution | Finish execution | All required steps done |
| FailExecution | Mark as failed | Execution active, reason provided |

### Queries
| Query | Description | Access Control |
|-------|-------------|----------------|
| GetSimulationById | Fetch simulation | Published: all, Draft: creator |
| GetUserExecutions | User's executions | Self only |
| GetExecutionResults | Execution details | Self or creator |
| GetLeaderboard | Simulation rankings | Published simulations only |
| GetScenarioConfig | Scenario configuration | During execution only |
| GetSimulationStats | Aggregate statistics | Creator or admin |

### Events
| Event | Publisher | Subscribers |
|-------|-----------|-------------|
| SimulationCreated | Simulation Aggregate | Analytics |
| SimulationPublished | Simulation Aggregate | Learning, Analytics |
| ExecutionStarted | Simulation Aggregate | Analytics, Security |
| ExecutionCompleted | Simulation Aggregate | Learning, Analytics, Certificate |
| ExecutionFailed | Simulation Aggregate | Analytics |
| SkillAchieved | Simulation Aggregate | Certificate, Analytics |

### Repositories
| Repository | Methods | Query Specs |
|------------|---------|-------------|
| SimulationRepository | findById, save, delete | PublishedSimSpec, CreatorSimSpec |
| ScenarioRepository | findById, findBySimulation, save | ScenarioBySimSpec |
| ExecutionRepository | findById, findByUser, findBySimulation, save | ActiveExecSpec, UserExecSpec |

### Factories
| Factory | Creates | Validation |
|---------|---------|------------|
| SimulationFactory.create(title, difficulty) | Simulation | Title valid, difficulty valid |
| ScenarioFactory.create(simulationId, title, config) | Scenario | Simulation exists, config valid |
| ExecutionFactory.create(userId, simulationId, scenarioId) | Execution | User eligible, simulation active |

### Validation Rules
| Rule | Field | Condition | Error |
|------|-------|-----------|-------|
| VAL-SIM-001 | title | 1-200 chars | Invalid title |
| VAL-SIM-002 | description | Max 5000 chars | Description too long |
| VAL-SIM-003 | difficulty | Valid level | Invalid difficulty |
| VAL-SIM-004 | estimatedDuration | 1-480 minutes | Invalid duration |
| VAL-SIM-005 | points | Positive integer | Invalid points |

---

## 7. Plugin Aggregate

### Aggregate Root: Plugin

**Bounded Context:** Plugin Context

### Entities

#### Plugin (Root)
| Attribute | Type | Description |
|-----------|------|-------------|
| pluginId | UUID | Unique identifier |
| name | string | Plugin name |
| description | string | Plugin description |
| authorId | UUID | Plugin author |
| versions | PluginVersion[] | Available versions |
| capabilities | Capability[] | Provided capabilities |
| status | PluginStatus | Current status |
| manifest | JSON | Plugin manifest |
| installedAt | DateTime | Installation time |
| updatedAt | DateTime | Last update time |

#### PluginVersion
| Attribute | Type | Description |
|-----------|------|-------------|
| versionId | UUID | Version identifier |
| pluginId | UUID | Parent plugin |
| version | SemanticVersion | Version number |
| changelog | string | Change description |
| manifest | JSON | Version-specific manifest |
| dependencies | PluginDependency[] | Required plugins |
| platformVersion | string | Required platform version |
| releasedAt | DateTime | Release time |

#### Capability
| Attribute | Type | Description |
|-----------|------|-------------|
| capabilityId | UUID | Capability identifier |
| pluginId | UUID | Providing plugin |
| type | CapabilityType | Type of capability |
| name | string | Capability name |
| description | string | Capability description |
| config | JSON | Configuration schema |
| hooks | string[] | Available hooks |

#### PluginDependency
| Attribute | Type | Description |
|-----------|------|-------------|
| dependencyId | UUID | Dependency identifier |
| pluginId | UUID | Dependent plugin |
| requiredPluginId | UUID | Required plugin |
| versionRange | string | Version constraint |

### Value Objects

| Value Object | Attributes | Validation Rules |
|--------------|------------|------------------|
| PluginId | value | UUID v4, unique |
| SemanticVersion | major, minor, patch | Follows semver 2.0 |
| CapabilityId | value | UUID v4, unique within plugin |
| PluginStatus | status | Enum: draft, published, active, deprecated, retired |
| CapabilityType | type | Enum: ui, api, hook, transformer, validator |

### Business Invariants
- INV-PLUGIN-001: Plugin must have at least one version
- INV-PLUGIN-002: Version numbers must follow semantic versioning
- INV-PLUGIN-003: Dependencies must be satisfiable
- INV-PLUGIN-004: Capabilities must have unique names within plugin
- INV-PLUGIN-005: Deprecated plugins cannot be dependencies for new plugins
- INV-PLUGIN-006: Plugin manifest must declare all capabilities
- INV-PLUGIN-007: Platform version must be compatible
- INV-PLUGIN-008: Plugin sandbox isolation must be maintained

### Commands
| Command | Description | Validation |
|---------|-------------|------------|
| CreatePlugin | Register new plugin | Name unique, manifest valid |
| AddVersion | Release new version | Semantic version increment |
| DeprecatePlugin | Mark as deprecated | No dependent active plugins |
| RetirePlugin | Remove from marketplace | No active installations |
| InstallPlugin | Add to platform | Compatible, dependencies met |
| UpdatePlugin | Upgrade version | Version increment, compatible |
| RemovePlugin | Uninstall | No critical dependencies |
| RegisterCapability | Add capability | Plugin active, name unique |

### Queries
| Query | Description | Access Control |
|-------|-------------|----------------|
| GetPluginById | Fetch plugin details | Published: all, Draft: author |
| GetPluginByName | Find by name | Published: all, Draft: author |
| GetInstalledPlugins | List installed | Admin only |
| GetPluginCapabilities | List capabilities | Admin, consuming plugins |
| GetPluginVersions | Version history | Author or admin |
| CheckCompatibility | Version compatibility | System only |
| SearchPlugins | Plugin search | Published: all, All: admin |

### Events
| Event | Publisher | Subscribers |
|-------|-----------|-------------|
| PluginCreated | Plugin Aggregate | Analytics, Developer |
| PluginPublished | Plugin Aggregate | Marketplace, Analytics |
| PluginInstalled | Plugin Aggregate | Platform, Analytics |
| PluginUpdated | Plugin Aggregate | Platform, Analytics |
| PluginDeprecated | Plugin Aggregate | Marketplace, Analytics |
| PluginRemoved | Plugin Aggregate | Platform, Analytics |
| CapabilityRegistered | Plugin Aggregate | Platform, consuming plugins |

### Repositories
| Repository | Methods | Query Specs |
|------------|---------|-------------|
| PluginRepository | findById, findByName, save, delete | InstalledPluginSpec, PublishedPluginSpec |
| PluginVersionRepository | findById, findByPlugin, findLatest, save | LatestVersionSpec, CompatibleVersionSpec |
| CapabilityRepository | findById, findByPlugin, findByType, save | CapabilityByTypeSpec |

### Factories
| Factory | Creates | Validation |
|---------|---------|------------|
| PluginFactory.create(name, authorId, manifest) | Plugin | Name unique, manifest valid |
| PluginVersionFactory.create(pluginId, version, manifest) | PluginVersion | Version valid, manifest valid |
| CapabilityFactory.create(pluginId, type, name) | Capability | Plugin exists, name unique |

### Validation Rules
| Rule | Field | Condition | Error |
|------|-------|-----------|-------|
| VAL-PLUGIN-001 | name | 1-100 chars, alphanumeric_- | Invalid name |
| VAL-PLUGIN-002 | version | Semver 2.0 format | Invalid version |
| VAL-PLUGIN-003 | description | Max 2000 chars | Description too long |
| VAL-PLUGIN-004 | manifest | Valid JSON schema | Invalid manifest |
| VAL-PLUGIN-005 | platformVersion | Semver range | Invalid version range |

---

## 8. Configuration Aggregate

### Aggregate Root: Configuration

**Bounded Context:** Platform Context

### Entities

#### Configuration (Root)
| Attribute | Type | Description |
|-----------|------|-------------|
| configId | UUID | Unique identifier |
| key | ConfigKey | Configuration key |
| value | ConfigValue | Configuration value |
| type | ConfigType | Value type |
| category | Category | Configuration category |
| environment | Environment | Target environment |
| isSecret | boolean | Secret value flag |
| defaultValue | ConfigValue | Default value |
| description | string | Setting description |
| createdAt | DateTime | Creation time |
| updatedAt | DateTime | Last update time |
| updatedBy | UUID | Last updater |

#### Setting
| Attribute | Type | Description |
|-----------|------|-------------|
| settingId | UUID | Setting identifier |
| configId | UUID | Parent configuration |
| key | string | Setting key |
| value | string | Setting value |
| isEncrypted | boolean | Encryption flag |
| lastModified | DateTime | Last modification |

#### Category
| Attribute | Type | Description |
|-----------|------|-------------|
| categoryId | UUID | Category identifier |
| name | string | Category name |
| description | string | Category description |
| parentId | UUID | Parent category |
| settings | Setting[] | Category settings |

### Value Objects

| Value Object | Attributes | Validation Rules |
|--------------|------------|------------------|
| ConfigKey | value | Dot notation, alphanumeric_ |
| ConfigValue | value, type | Type matches ConfigType |
| ConfigType | type | Enum: string, number, boolean, json, secret |
| Environment | name | Enum: development, staging, production |

### Business Invariants
- INV-CONFIG-001: Configuration key must be unique per environment
- INV-CONFIG-002: Secret values must be encrypted at rest
- INV-CONFIG-003: Type must match value format
- INV-CONFIG-004: Default value must be valid for type
- INV-CONFIG-005: Production changes require approval
- INV-CONFIG-006: Configuration changes are audited
- INV-CONFIG-007: Category hierarchy max depth is 3
- INV-CONFIG-008: Feature flags must have rollout percentage

### Commands
| Command | Description | Validation |
|---------|-------------|------------|
| CreateConfiguration | Add new config | Key unique in environment |
| UpdateConfiguration | Modify config | Key exists, valid value |
| DeleteConfiguration | Remove config | No dependent configs |
| CreateCategory | Add category | Name unique, depth valid |
| UpdateCategory | Modify category | Category exists |
| DeleteCategory | Remove category | No settings in category |
| SetFeatureFlag | Toggle feature flag | Valid flag name, percentage |
| RollbackConfiguration | Revert to previous | Previous version exists |

### Queries
| Query | Description | Access Control |
|-------|-------------|----------------|
| GetConfigByKey | Fetch config value | System or admin |
| GetConfigsByCategory | List category configs | Admin |
| GetConfigsByEnvironment | Environment configs | Admin |
| GetFeatureFlags | List feature flags | Admin |
| GetConfigHistory | Change history | Admin |
| GetConfigDefaults | Default values | System |

### Events
| Event | Publisher | Subscribers |
|-------|-----------|-------------|
| ConfigurationCreated | Configuration Aggregate | All contexts (if subscribed) |
| ConfigurationUpdated | Configuration Aggregate | All contexts (if subscribed) |
| ConfigurationDeleted | Configuration Aggregate | All contexts (if subscribed) |
| FeatureFlagToggled | Configuration Aggregate | All contexts (if subscribed) |
| ConfigurationRolledBack | Configuration Aggregate | All contexts (if subscribed) |

### Repositories
| Repository | Methods | Query Specs |
|------------|---------|-------------|
| ConfigurationRepository | findByKey, findByCategory, save, delete | ConfigByKeySpec, ConfigByCategorySpec |
| SettingRepository | findByConfig, save, delete | SettingByConfigSpec |
| CategoryRepository | findById, findByName, save, delete | CategoryByNameSpec, RootCategoriesSpec |

### Factories
| Factory | Creates | Validation |
|---------|---------|------------|
| ConfigurationFactory.create(key, value, type) | Configuration | Key unique, value matches type |
| CategoryFactory.create(name, parentId) | Category | Name unique, depth valid |
| SettingFactory.create(configId, key, value) | Setting | Config exists, value valid |

### Validation Rules
| Rule | Field | Condition | Error |
|------|-------|-----------|-------|
| VAL-CONFIG-001 | key | Dot notation format | Invalid key format |
| VAL-CONFIG-002 | value | Matches type | Type mismatch |
| VAL-CONFIG-003 | defaultValue | Matches type | Invalid default |
| VAL-CONFIG-004 | description | Max 500 chars | Description too long |
| VAL-CONFIG-005 | category | Valid category exists | Invalid category |

---

## Aggregate Relationship Rules

### 1. Reference Rules
- Aggregates reference each other by ID, not by object reference
- Cross-aggregate references are weak references (no referential integrity)
- Deleted aggregate references are handled via eventual consistency

### 2. Consistency Rules
- Each aggregate is consistency boundary
- Invariants within aggregate are enforced synchronously
- Cross-aggregate invariants are enforced eventually consistent

### 3. Lifecycle Rules
- Aggregate roots control entity lifecycle
- Entities cannot exist without aggregate root
- Value objects are recreated, not updated

### 4. Event Rules
- Aggregates publish events after state changes
- Events contain minimal required data
- Events are idempotent where possible

### 5. Repository Rules
- One repository per aggregate root
- Repositories return complete aggregates
- Aggregate loading is lazy (children loaded on demand)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial aggregate catalog | AuthShield Team |
| 1.1 | 2024-02-20 | Added Plugin and Configuration aggregates | AuthShield Team |
| 1.2 | 2024-03-10 | Refined invariants and validation rules | AuthShield Team |
