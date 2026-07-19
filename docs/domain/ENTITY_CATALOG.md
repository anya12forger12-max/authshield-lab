# AuthShield Lab - Entity Catalog

## Overview

This document defines all entities in AuthShield Lab, specifying identity strategies, attributes, relationships, ownership, lifecycle, validation rules, persistence strategies, and audit requirements for each entity.

---

## Entity Catalog Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AuthShield Lab Entities                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Identity Entities                                │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │   User    │  │UserProfile│ │   Role   │  │Permission│         │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │   │
│  │  ┌──────────┐  ┌──────────┐                                      │   │
│  │  │  Group   │  │Organization│                                     │   │
│  │  └──────────┘  └──────────┘                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Education Entities                                │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │  Course  │  │  Module  │  │  Lesson  │  │Enrollment│         │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │ Progress │  │Competency│  │Assessment│  │ Question │         │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │   │
│  │  ┌──────────┐  ┌──────────┐                                      │   │
│  │  │  Answer  │  │Certificate│                                     │   │
│  │  └──────────┘  └──────────┘                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Platform Entities                                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │  Plugin  │  │PluginVer │  │Configuration│ │ Setting │         │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │   │
│  │  ┌──────────┐  ┌──────────┐                                      │   │
│  │  │  Backup  │  │AuditEntry│                                      │   │
│  │  └──────────┘  └──────────┘                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Identity Entities

### 1. User

**Identity Strategy:** UUID v4 generated at creation, immutable throughout lifecycle.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| userId | UUID | PK, not null, unique | Primary identifier |
| email | Email | unique, not null, max 254 chars | Login email |
| username | Username | unique, not null, 3-50 chars | Unique username |
| passwordHash | PasswordHash | not null, bcrypt format | Hashed password |
| status | UserStatus | not null, default 'pending' | Account status |
| mfaEnabled | boolean | default false | MFA activation flag |
| mfaSecret | string | nullable, encrypted | TOTP secret |
| lastLoginAt | DateTime | nullable | Last login timestamp |
| loginAttempts | int | default 0, min 0 | Failed login count |
| lockedUntil | DateTime | nullable | Account lock expiry |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |
| deletedAt | DateTime | nullable | Soft deletion timestamp |

**Relationships:**
- Has one `UserProfile` (1:1)
- Has many `Role` (M:N via UserRole)
- Has many `Session` (1:M)
- Belongs to one `Organization` (M:1)

**Ownership:**
- Owned by Identity Context
- Can be read by: Authorization, Session, Education, Analytics contexts
- Can be modified by: Identity Context only

**Lifecycle:**
```
Created (pending) → Email Verified → Active → Suspended → Deleted
                                ↓
                           Locked (temporary)
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-USER-001 | email | Valid RFC 5322 format | INVALID_EMAIL |
| VAL-USER-002 | email | Unique in system | EMAIL_EXISTS |
| VAL-USER-003 | username | 3-50 chars, alphanumeric_ | INVALID_USERNAME |
| VAL-USER-004 | username | Unique in system | USERNAME_EXISTS |
| VAL-USER-005 | passwordHash | Valid bcrypt hash | INVALID_PASSWORD_HASH |
| VAL-USER-006 | status | Valid UserStatus enum | INVALID_STATUS |

**Persistence Strategy:**
- Table: `users`
- Indexes: userId (PK), email (unique), username (unique), status
- Partitioning: By status for archival
- Archival: Deleted users moved to archive table after 90 days

**Audit Requirements:**
- Log all status changes
- Log all login attempts (success/failure)
- Log password changes
- Log profile modifications
- Retention: 7 years for compliance

---

### 2. UserProfile

**Identity Strategy:** UUID v4, references User entity.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| profileId | UUID | PK, not null | Primary identifier |
| userId | UUID | FK, unique, not null | Parent user |
| displayName | string | not null, 1-100 chars | Display name |
| avatarUrl | URL | nullable, max 500 chars | Profile picture |
| bio | string | nullable, max 1000 chars | User biography |
| firstName | string | nullable, max 50 chars | First name |
| lastName | string | nullable, max 50 chars | Last name |
| phone | PhoneNumber | nullable | Contact phone |
| timezone | string | default 'UTC' | Timezone |
| language | LanguageCode | default 'en-US' | Preferred language |
| theme | ThemeConfig | default 'system' | UI theme preference |
| accessibility | AccessibilityPreference | nullable | Accessibility settings |
| notifications | JSON | default '{}' | Notification preferences |
| socialLinks | JSON | default '{}' | Social media links |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |

**Relationships:**
- Belongs to one `User` (1:1)
- Independent lifecycle (deleted with User)

**Ownership:**
- Owned by Identity Context
- Can be read by: All contexts (public profile)
- Can be modified by: User (self), Admin

**Lifecycle:**
```
Created → Updated (multiple times) → Deleted (with User)
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-PROFILE-001 | displayName | 1-100 chars, not empty | INVALID_DISPLAY_NAME |
| VAL-PROFILE-002 | avatarUrl | Valid URL format | INVALID_AVATAR_URL |
| VAL-PROFILE-003 | bio | Max 1000 chars | BIO_TOO_LONG |
| VAL-PROFILE-004 | phone | Valid phone format | INVALID_PHONE |
| VAL-PROFILE-005 | timezone | Valid timezone string | INVALID_TIMEZONE |
| VAL-PROFILE-006 | language | Valid language code | INVALID_LANGUAGE |

**Persistence Strategy:**
- Table: `user_profiles`
- Indexes: profileId (PK), userId (unique)
- Lazy loading: Profile loaded on demand
- Versioning: Optimistic concurrency control

**Audit Requirements:**
- Log all profile changes
- Log avatar uploads
- Log accessibility setting changes
- Retention: 5 years

---

### 3. Role

**Identity Strategy:** UUID v4, with system-defined roles having fixed IDs.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| roleId | UUID | PK, not null | Primary identifier |
| name | string | unique, not null, 1-50 chars | Role name |
| description | string | not null, max 500 chars | Role description |
| hierarchy | int | not null, min 0 | Hierarchy level |
| isSystem | boolean | default false | System-defined flag |
| isActive | boolean | default true | Active status |
| parentId | UUID | nullable, FK | Parent role |
| permissions | Permission[] | not null | Assigned permissions |
| metadata | JSON | default '{}' | Additional data |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |

**Relationships:**
- Has many `Permission` (M:N via RolePermission)
- Has many `User` (M:N via UserRole)
- Has one parent `Role` (self-referential)
- Has many child `Role` (self-referential)

**Ownership:**
- Owned by Authorization Context
- Can be read by: All contexts
- Can be modified by: Authorization Context, Admin

**Lifecycle:**
```
Created (draft) → Active → Deprecated → Retired
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-ROLE-001 | name | Unique, 1-50 chars | INVALID_ROLE_NAME |
| VAL-ROLE-002 | hierarchy | Non-negative integer | INVALID_HIERARCHY |
| VAL-ROLE-003 | parentId | Valid role or null | INVALID_PARENT |
| VAL-ROLE-004 | permissions | Non-empty array | NO_PERMISSIONS |

**Persistence Strategy:**
- Table: `roles`
- Indexes: roleId (PK), name (unique), hierarchy
- Hierarchy stored as materialized path
- Cached aggressively (changes infrequently)

**Audit Requirements:**
- Log all role creation/modification
- Log permission assignments
- Log role assignments to users
- Retention: 7 years

---

### 4. Permission

**Identity Strategy:** UUID v4, with composite unique constraint on resource+action.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| permissionId | UUID | PK, not null | Primary identifier |
| resource | string | not null, max 100 chars | Resource type |
| action | string | not null, max 50 chars | Allowed action |
| description | string | not null, max 500 chars | Permission description |
| conditions | JSON | nullable | Conditional rules |
| isSystem | boolean | default false | System-defined flag |
| createdAt | DateTime | not null | Creation timestamp |

**Relationships:**
- Has many `Role` (M:N via RolePermission)
- Independent entity

**Ownership:**
- Owned by Authorization Context
- Can be read by: All contexts
- Can be modified by: Authorization Context only

**Lifecycle:**
```
Created → Active → Deprecated → Retired
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-PERM-001 | resource+action | Unique composite | PERMISSION_EXISTS |
| VAL-PERM-002 | resource | 1-100 chars | INVALID_RESOURCE |
| VAL-PERM-003 | action | 1-50 chars | INVALID_ACTION |
| VAL-PERM-004 | conditions | Valid JSON | INVALID_CONDITIONS |

**Persistence Strategy:**
- Table: `permissions`
- Indexes: permissionId (PK), resource+action (unique)
- Cached with role data
- Immutable after creation (deprecation only)

**Audit Requirements:**
- Log permission creation
- Log condition changes
- Retention: 7 years

---

### 5. Group

**Identity Strategy:** UUID v4, represents organizational or functional groupings.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| groupId | UUID | PK, not null | Primary identifier |
| name | string | unique, not null, 1-100 chars | Group name |
| description | string | nullable, max 500 chars | Group description |
| type | GroupType | not null | Group classification |
| organizationId | UUID | nullable, FK | Parent organization |
| ownerId | UUID | not null, FK | Group owner |
| members | User[] | not null | Group members |
| settings | JSON | default '{}' | Group settings |
| isPublic | boolean | default false | Public visibility |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |

**Relationships:**
- Has many `User` (M:N via GroupMember)
- Belongs to one `Organization` (M:1)
- Has one owner `User` (M:1)

**Ownership:**
- Owned by Identity Context
- Can be read by: Members, Organization admins
- Can be modified by: Group owner, Organization admins

**Lifecycle:**
```
Created → Active → Archived → Deleted
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-GROUP-001 | name | Unique within organization | GROUP_NAME_EXISTS |
| VAL-GROUP-002 | type | Valid GroupType | INVALID_GROUP_TYPE |
| VAL-GROUP-003 | ownerId | Active user | INVALID_OWNER |
| VAL-GROUP-004 | members | Max 1000 members | TOO_MANY_MEMBERS |

**Persistence Strategy:**
- Table: `groups`
- Indexes: groupId (PK), name+organizationId (unique), ownerId
- Member list cached for performance
- Soft deletion with member notification

**Audit Requirements:**
- Log group creation/deletion
- Log member additions/removals
- Log owner changes
- Retention: 5 years

---

### 6. Organization

**Identity Strategy:** UUID v4, represents tenant or business entity.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| organizationId | UUID | PK, not null | Primary identifier |
| name | string | unique, not null, 1-200 chars | Organization name |
| slug | string | unique, not null, 1-100 chars | URL-friendly identifier |
| domain | string | nullable, unique | Company domain |
| logoUrl | URL | nullable | Organization logo |
| settings | JSON | default '{}' | Org settings |
| plan | PlanType | not null, default 'free' | Subscription plan |
| owner | User | not null, FK | Organization owner |
| members | User[] | not null | Organization members |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |
| deletedAt | DateTime | nullable | Soft deletion timestamp |

**Relationships:**
- Has many `User` (M:N via OrganizationMember)
- Has many `Group` (1:M)
- Has one owner `User` (M:1)

**Ownership:**
- Owned by Identity Context
- Can be read by: Members, Platform admins
- Can be modified by: Owner, Organization admins

**Lifecycle:**
```
Created → Active → Suspended → Deleted
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-ORG-001 | name | Unique, 1-200 chars | INVALID_ORG_NAME |
| VAL-ORG-002 | slug | Unique, alphanumeric- | INVALID_SLUG |
| VAL-ORG-003 | domain | Valid domain format | INVALID_DOMAIN |
| VAL-ORG-004 | plan | Valid PlanType | INVALID_PLAN |

**Persistence Strategy:**
- Table: `organizations`
- Indexes: organizationId (PK), slug (unique), domain (unique)
- Tenant isolation via organizationId
- Soft deletion with member notification

**Audit Requirements:**
- Log organization creation/deletion
- Log plan changes
- Log owner transfers
- Log member management
- Retention: 7 years

---

## Education Entities

### 7. Course

**Identity Strategy:** UUID v4 with human-readable CourseCode.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| courseId | UUID | PK, not null | Primary identifier |
| title | string | not null, 1-200 chars | Course title |
| description | string | not null, max 5000 chars | Course description |
| courseCode | CourseCode | unique, not null | Human-readable code |
| status | CourseStatus | not null, default 'draft' | Publication status |
| creatorId | UUID | not null, FK | Course creator |
| modules | Module[] | not null | Course modules |
| prerequisites | UUID[] | nullable | Required courses |
| tags | string[] | nullable | Searchable tags |
| thumbnailUrl | URL | nullable | Course thumbnail |
| estimatedDuration | Duration | nullable | Total duration |
| maxEnrollments | int | nullable | Enrollment limit |
| isPublic | boolean | default true | Public visibility |
| publishedAt | DateTime | nullable | Publication timestamp |
| archivedAt | DateTime | nullable | Archive timestamp |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |

**Relationships:**
- Has many `Module` (1:M)
- Has many `Enrollment` (1:M)
- Belongs to one `User` (creator) (M:1)
- Has many prerequisite `Course` (M:N)

**Ownership:**
- Owned by Education Context
- Can be read by: All authenticated users (published)
- Can be modified by: Creator, Admin

**Lifecycle:**
```
Created (draft) → Review → Published → Archived → Deprecated
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-COURSE-001 | title | 1-200 chars | INVALID_TITLE |
| VAL-COURSE-002 | courseCode | Unique format [A-Z]{2,4}-[0-9]{3,4} | INVALID_CODE |
| VAL-COURSE-003 | description | Max 5000 chars | DESCRIPTION_TOO_LONG |
| VAL-COURSE-004 | modules | Min 3 for publication | INSUFFICIENT_MODULES |
| VAL-COURSE-005 | creatorId | Active user | INVALID_CREATOR |

**Persistence Strategy:**
- Table: `courses`
- Indexes: courseId (PK), courseCode (unique), creatorId, status
- Full-text search on title, description
- Version control for content changes

**Audit Requirements:**
- Log creation, publication, archival
- Log all content changes with versioning
- Log enrollment changes
- Retention: 7 years

---

### 8. Module

**Identity Strategy:** UUID v4, scoped within Course.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| moduleId | UUID | PK, not null | Primary identifier |
| courseId | UUID | FK, not null | Parent course |
| title | string | not null, 1-200 chars | Module title |
| description | string | nullable, max 2000 chars | Module description |
| order | int | not null, min 1 | Display order |
| lessons | Lesson[] | not null | Module lessons |
| duration | Duration | nullable | Estimated duration |
| isRequired | boolean | default true | Required for completion |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |

**Relationships:**
- Belongs to one `Course` (M:1)
- Has many `Lesson` (1:M)

**Ownership:**
- Owned by Education Context
- Can be read by: Course readers
- Can be modified by: Course creator, Admin

**Lifecycle:**
```
Created → Active → Reordered → Archived (with course)
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-MODULE-001 | title | 1-200 chars | INVALID_TITLE |
| VAL-MODULE-002 | order | Positive, unique in course | INVALID_ORDER |
| VAL-MODULE-003 | courseId | Valid course | INVALID_COURSE |

**Persistence Strategy:**
- Table: `modules`
- Indexes: moduleId (PK), courseId+order (unique)
- Ordered retrieval by order field
- Cascading operations with course

**Audit Requirements:**
- Log creation, reordering
- Log lesson additions/removals
- Retention: 5 years

---

### 9. Lesson

**Identity Strategy:** UUID v4, scoped within Module.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| lessonId | UUID | PK, not null | Primary identifier |
| moduleId | UUID | FK, not null | Parent module |
| title | string | not null, 1-200 chars | Lesson title |
| type | LessonType | not null | Content type |
| content | string | not null | Lesson content |
| order | int | not null, min 1 | Display order |
| duration | Duration | nullable | Estimated duration |
| isRequired | boolean | default true | Required for completion |
| resources | JSON | nullable | External resources |
| quiz | Assessment | nullable | Embedded assessment |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |

**Relationships:**
- Belongs to one `Module` (M:1)
- Has optional `Assessment` (1:1)

**Ownership:**
- Owned by Education Context
- Can be read by: Enrolled users
- Can be modified by: Course creator, Admin

**Lifecycle:**
```
Created → Draft → Review → Published → Updated → Archived
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-LESSON-001 | title | 1-200 chars | INVALID_TITLE |
| VAL-LESSON-002 | type | Valid LessonType | INVALID_TYPE |
| VAL-LESSON-003 | content | Non-empty | EMPTY_CONTENT |
| VAL-LESSON-004 | order | Positive, unique in module | INVALID_ORDER |

**Persistence Strategy:**
- Table: `lessons`
- Indexes: lessonId (PK), moduleId+order (unique)
- Content stored as markdown/HTML
- Version history maintained

**Audit Requirements:**
- Log creation, content changes
- Log access patterns
- Retention: 5 years

---

### 10. Enrollment

**Identity Strategy:** UUID v4, unique constraint on user+course.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| enrollmentId | UUID | PK, not null | Primary identifier |
| userId | UUID | FK, not null | Enrolled user |
| courseId | UUID | FK, not null | Enrolled course |
| status | EnrollmentStatus | not null | Enrollment status |
| progress | Progress | nullable | Completion progress |
| enrolledAt | DateTime | not null | Enrollment timestamp |
| expiresAt | DateTime | nullable | Access expiry |
| completedAt | DateTime | nullable | Completion timestamp |
| grade | GradePoint | nullable | Final grade |
| certificateId | UUID | nullable, FK | Earned certificate |

**Relationships:**
- Belongs to one `User` (M:1)
- Belongs to one `Course` (M:1)
- Has one `Progress` (1:1)
- Has optional `Certificate` (1:1)

**Ownership:**
- Owned by Learning Context
- Can be read by: User (self), Course creator, Admin
- Can be modified by: System (progress), User (withdrawal)

**Lifecycle:**
```
Created → Active → In Progress → Completed / Expired / Withdrawn
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-ENROLL-001 | userId+courseId | Unique pair | ALREADY_ENROLLED |
| VAL-ENROLL-002 | expiresAt | Future date | INVALID_EXPIRY |
| VAL-ENROLL-003 | status | Valid EnrollmentStatus | INVALID_STATUS |

**Persistence Strategy:**
- Table: `enrollments`
- Indexes: enrollmentId (PK), userId+courseId (unique), status
- Partitioned by enrollment date
- Historical enrollments archived

**Audit Requirements:**
- Log enrollment creation/completion
- Log status changes
- Log withdrawal reasons
- Retention: 7 years

---

### 11. Progress

**Identity Strategy:** UUID v4, linked to Enrollment.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| progressId | UUID | PK, not null | Primary identifier |
| enrollmentId | UUID | FK, not null | Parent enrollment |
| lessonId | UUID | FK, not null | Completed lesson |
| status | ProgressStatus | not null | Completion status |
| score | AssessmentScore | nullable | Lesson score |
| timeSpent | Duration | not null | Time invested |
| attempts | int | default 1 | Attempt count |
| completedAt | DateTime | nullable | Completion timestamp |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |

**Relationships:**
- Belongs to one `Enrollment` (M:1)
- References one `Lesson` (M:1)

**Ownership:**
- Owned by Learning Context
- Can be read by: User (self), Course creator, Admin
- Can be modified by: System only

**Lifecycle:**
```
Created (in_progress) → Updated → Completed
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-PROGRESS-001 | enrollmentId | Valid enrollment | INVALID_ENROLLMENT |
| VAL-PROGRESS-002 | lessonId | Valid lesson in course | INVALID_LESSON |
| VAL-PROGRESS-003 | timeSpent | Non-negative | INVALID_TIME |

**Persistence Strategy:**
- Table: `progress`
- Indexes: progressId (PK), enrollmentId+lessonId (unique)
- Aggregated for enrollment completion calculation
- Real-time updates via event sourcing

**Audit Requirements:**
- Log completion events
- Log score changes
- Retention: 5 years

---

### 12. Competency

**Identity Strategy:** UUID v4, represents skill or knowledge area.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| competencyId | UUID | PK, not null | Primary identifier |
| name | string | unique, not null, 1-100 chars | Competency name |
| description | string | not null, max 1000 chars | Description |
| category | CompetencyCategory | not null | Classification |
| level | CompetencyLevel | not null | Difficulty level |
| parentCompetencyId | UUID | nullable, FK | Parent competency |
| relatedCompetencies | UUID[] | nullable | Related skills |
| assessmentCriteria | JSON | not null | Evaluation criteria |
| createdAt | DateTime | not null | Creation timestamp |

**Relationships:**
- Self-referential hierarchy (parent/child)
- Has many `Assessment` (M:N)
- Has many `Certificate` (M:N)

**Ownership:**
- Owned by Assessment Context
- Can be read by: All contexts
- Can be modified by: Assessment admin

**Lifecycle:**
```
Defined → Active → Deprecated → Retired
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-COMP-001 | name | Unique, 1-100 chars | INVALID_NAME |
| VAL-COMP-002 | level | Valid CompetencyLevel | INVALID_LEVEL |
| VAL-COMP-003 | assessmentCriteria | Valid JSON | INVALID_CRITERIA |

**Persistence Strategy:**
- Table: `competencies`
- Indexes: competencyId (PK), name (unique), category
- Materialized path for hierarchy
- Cached with assessment mappings

**Audit Requirements:**
- Log creation, level changes
- Log assessment criteria updates
- Retention: 7 years

---

### 13. Assessment

**Identity Strategy:** UUID v4 with AssessmentType.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| assessmentId | UUID | PK, not null | Primary identifier |
| title | string | not null, 1-200 chars | Assessment title |
| type | AssessmentType | not null | Assessment type |
| courseId | UUID | nullable, FK | Associated course |
| competencyId | UUID | nullable, FK | Assessed competency |
| questions | Question[] | not null | Assessment questions |
| timeLimit | Duration | nullable | Time limit |
| passingScore | AssessmentScore | not null | Required score |
| maxAttempts | int | default 3 | Allowed attempts |
| isRandomized | boolean | default false | Question randomization |
| status | AssessmentStatus | not null | Current status |
| createdBy | UUID | not null, FK | Creator |
| publishedAt | DateTime | nullable | Publication timestamp |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |

**Relationships:**
- Has many `Question` (1:M)
- Belongs to optional `Course` (M:1)
- Belongs to optional `Competency` (M:1)

**Ownership:**
- Owned by Assessment Context
- Can be read by: Enrolled users, Creator, Admin
- Can be modified by: Creator, Admin

**Lifecycle:**
```
Created (draft) → Review → Active → Archived → Retired
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-ASSESS-001 | title | 1-200 chars | INVALID_TITLE |
| VAL-ASSESS-002 | passingScore | 0-100 or 0-maxPoints | INVALID_PASSING_SCORE |
| VAL-ASSESS-003 | questions | Min 1 question | NO_QUESTIONS |
| VAL-ASSESS-004 | maxAttempts | Min 1 | INVALID_MAX_ATTEMPTS |

**Persistence Strategy:**
- Table: `assessments`
- Indexes: assessmentId (PK), courseId, competencyId, status
- Question pool versioned separately
- Results stored in separate table

**Audit Requirements:**
- Log creation, publication
- Log all submission attempts
- Log score changes
- Retention: 7 years

---

### 14. Question

**Identity Strategy:** UUID v4, scoped within Assessment.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| questionId | UUID | PK, not null | Primary identifier |
| assessmentId | UUID | FK, not null | Parent assessment |
| type | QuestionType | not null | Question type |
| text | string | not null, max 5000 chars | Question text |
| options | Answer[] | nullable | Answer options |
| correctAnswer | UUID | nullable, FK | Correct answer |
| points | int | not null, min 1 | Point value |
| order | int | not null, min 1 | Display order |
| explanation | string | nullable, max 2000 chars | Answer explanation |
| metadata | JSON | nullable | Additional data |
| createdAt | DateTime | not null | Creation timestamp |

**Relationships:**
- Belongs to one `Assessment` (M:1)
- Has many `Answer` (1:M)
- References one `Answer` as correct (M:1)

**Ownership:**
- Owned by Assessment Context
- Can be read by: During assessment (limited), Creator, Admin
- Can be modified by: Creator, Admin

**Lifecycle:**
```
Created → Draft → Published → Archived
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-QUESTION-001 | text | 1-5000 chars | INVALID_TEXT |
| VAL-QUESTION-002 | points | Positive integer | INVALID_POINTS |
| VAL-QUESTION-003 | options | Min 2 for multiple choice | INSUFFICIENT_OPTIONS |
| VAL-QUESTION-004 | correctAnswer | Valid option reference | INVALID_ANSWER |

**Persistence Strategy:**
- Table: `questions`
- Indexes: questionId (PK), assessmentId+order (unique)
- Options stored as JSON array
- Versioned with assessment

**Audit Requirements:**
- Log creation, modifications
- Log correct answer changes
- Retention: 5 years

---

### 15. Answer

**Identity Strategy:** UUID v4, scoped within Question.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| answerId | UUID | PK, not null | Primary identifier |
| questionId | UUID | FK, not null | Parent question |
| text | string | not null, max 1000 chars | Answer text |
| isCorrect | boolean | not null | Correctness flag |
| feedback | string | nullable, max 1000 chars | Answer feedback |
| order | int | not null | Display order |
| metadata | JSON | nullable | Additional data |

**Relationships:**
- Belongs to one `Question` (M:1)

**Ownership:**
- Owned by Assessment Context
- Can be read by: Creator, Admin (correctness hidden during assessment)
- Can be modified by: Creator, Admin

**Lifecycle:**
```
Created → Active → Updated → Archived
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-ANSWER-001 | text | 1-1000 chars | INVALID_TEXT |
| VAL-ANSWER-002 | order | Unique in question | INVALID_ORDER |

**Persistence Strategy:**
- Table: `answers`
- Indexes: answerId (PK), questionId+order (unique)
- Correctness hidden in API responses during assessment
- Cached with question data

**Audit Requirements:**
- Log creation, modifications
- Log correctness changes
- Retention: 5 years

---

### 16. Certificate

**Identity Strategy:** UUID v4 with unique verification code.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| certificateId | UUID | PK, not null | Primary identifier |
| userId | UUID | FK, not null | Certificate holder |
| courseId | UUID | FK, not null | Certified course |
| templateId | UUID | FK, not null | Certificate template |
| verificationCode | VerificationCode | unique, not null | Verification code |
| status | CertificateStatus | not null | Current status |
| issuedAt | DateTime | not null | Issuance timestamp |
| expiresAt | DateTime | nullable | Expiry timestamp |
| revokedAt | DateTime | nullable | Revocation timestamp |
| revocationReason | string | nullable | Revocation reason |
| metadata | JSON | nullable | Additional data |

**Relationships:**
- Belongs to one `User` (M:1)
- Belongs to one `Course` (M:1)
- Belongs to one `Template` (M:1)

**Ownership:**
- Owned by Certification Context
- Can be read by: Holder, Course creator, Public (verification)
- Can be modified by: System only

**Lifecycle:**
```
Pending → Issued → Active → Expired / Revoked
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-CERT-001 | verificationCode | Unique 12-char alphanumeric | INVALID_CODE |
| VAL-CERT-002 | expiresAt | After issuedAt or null | INVALID_EXPIRY |
| VAL-CERT-003 | userId | Active user | INVALID_USER |
| VAL-CERT-004 | courseId | Completed course | INCOMPLETE_COURSE |

**Persistence Strategy:**
- Table: `certificates`
- Indexes: certificateId (PK), verificationCode (unique), userId, courseId
- Public verification API with rate limiting
- Revoked certificates retained for history

**Audit Requirements:**
- Log issuance, revocation
- Log verification attempts
- Log renewal attempts
- Retention: 10 years

---

## Platform Entities

### 17. Plugin

**Identity Strategy:** UUID v4 with unique name constraint.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| pluginId | UUID | PK, not null | Primary identifier |
| name | string | unique, not null, 1-100 chars | Plugin name |
| description | string | not null, max 2000 chars | Plugin description |
| authorId | UUID | not null, FK | Plugin author |
| versions | PluginVersion[] | not null | Available versions |
| capabilities | Capability[] | not null | Provided capabilities |
| status | PluginStatus | not null | Current status |
| manifest | JSON | not null | Plugin manifest |
| repositoryUrl | URL | nullable | Source repository |
| documentationUrl | URL | nullable | Documentation link |
| installedAt | DateTime | nullable | Installation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |

**Relationships:**
- Has many `PluginVersion` (1:M)
- Has many `Capability` (1:M)
- Belongs to one `User` (author) (M:1)

**Ownership:**
- Owned by Plugin Context
- Can be read by: All users (published), Author, Admin
- Can be modified by: Author, Admin

**Lifecycle:**
```
Development → Review → Published → Active → Deprecated → Retired
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-PLUGIN-001 | name | Unique, 1-100 chars | INVALID_NAME |
| VAL-PLUGIN-002 | manifest | Valid JSON schema | INVALID_MANIFEST |
| VAL-PLUGIN-003 | authorId | Active user | INVALID_AUTHOR |

**Persistence Strategy:**
- Table: `plugins`
- Indexes: pluginId (PK), name (unique), authorId, status
- Manifest stored as JSONB
- Capability index for fast lookup

**Audit Requirements:**
- Log installation, updates, removal
- Log capability changes
- Log security scan results
- Retention: 5 years

---

### 18. PluginVersion

**Identity Strategy:** UUID v4 with SemanticVersion.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| versionId | UUID | PK, not null | Primary identifier |
| pluginId | UUID | FK, not null | Parent plugin |
| version | SemanticVersion | unique, not null | Version number |
| changelog | string | not null, max 5000 chars | Change description |
| manifest | JSON | not null | Version manifest |
| dependencies | PluginDependency[] | nullable | Required plugins |
| platformVersion | string | not null | Required platform |
| downloadUrl | URL | not null | Download link |
| checksum | string | not null | File checksum |
| releasedAt | DateTime | not null | Release timestamp |

**Relationships:**
- Belongs to one `Plugin` (M:1)
- Has many `PluginDependency` (1:M)

**Ownership:**
- Owned by Plugin Context
- Can be read by: All users (published), Author, Admin
- Can be modified by: Author (only unreleased)

**Lifecycle:**
```
Draft → Released → Deprecated → Removed
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-VER-001 | version | Valid semantic version | INVALID_VERSION |
| VAL-VER-002 | version | Unique in plugin | VERSION_EXISTS |
| VAL-VER-003 | checksum | Valid hash | INVALID_CHECKSUM |

**Persistence Strategy:**
- Table: `plugin_versions`
- Indexes: versionId (PK), pluginId+version (unique)
- Immutable after release
- Download URLs signed with expiry

**Audit Requirements:**
- Log release, deprecation
- Log dependency changes
- Retention: 5 years

---

### 19. Configuration

**Identity Strategy:** UUID v4 with composite key (key+environment).

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| configId | UUID | PK, not null | Primary identifier |
| key | ConfigKey | unique, not null | Configuration key |
| value | ConfigValue | not null | Configuration value |
| type | ConfigType | not null | Value type |
| environment | Environment | not null | Target environment |
| isSecret | boolean | default false | Secret value flag |
| defaultValue | ConfigValue | nullable | Default value |
| description | string | nullable, max 500 chars | Setting description |
| category | string | nullable | Configuration category |
| lastModifiedBy | UUID | not null, FK | Last modifier |
| createdAt | DateTime | not null | Creation timestamp |
| updatedAt | DateTime | not null | Last update timestamp |

**Relationships:**
- Belongs to one `User` (modifier) (M:1)

**Ownership:**
- Owned by Configuration Context
- Can be read by: All contexts (non-secret), System (secret)
- Can be modified by: Admin, Operations

**Lifecycle:**
```
Created → Active → Updated → Deprecated → Removed
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-CONFIG-001 | key+environment | Unique pair | KEY_EXISTS |
| VAL-CONFIG-002 | value | Matches type | TYPE_MISMATCH |
| VAL-CONFIG-003 | type | Valid ConfigType | INVALID_TYPE |

**Persistence Strategy:**
- Table: `configurations`
- Indexes: configId (PK), key+environment (unique), category
- Cached with invalidation on update
- Secrets encrypted at rest

**Audit Requirements:**
- Log all changes with before/after values
- Log secret access
- Log rollback operations
- Retention: 7 years

---

### 20. Setting

**Identity Strategy:** UUID v4, child of Configuration.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| settingId | UUID | PK, not null | Primary identifier |
| configId | UUID | FK, not null | Parent configuration |
| key | string | not null, max 100 chars | Setting key |
| value | string | not null | Setting value |
| isEncrypted | boolean | default false | Encryption flag |
| lastModified | DateTime | not null | Last modification |

**Relationships:**
- Belongs to one `Configuration` (M:1)

**Ownership:**
- Owned by Configuration Context
- Can be read by: Parent configuration consumers
- Can be modified by: Configuration system

**Lifecycle:**
```
Created → Active → Updated → Removed
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-SETTING-001 | key | 1-100 chars | INVALID_KEY |
| VAL-SETTING-002 | value | Non-empty | EMPTY_VALUE |

**Persistence Strategy:**
- Table: `settings`
- Indexes: settingId (PK), configId+key (unique)
- Encrypted values decrypted on read
- Cached with configuration

**Audit Requirements:**
- Log all modifications
- Log encryption/decryption
- Retention: 5 years

---

### 21. Backup

**Identity Strategy:** UUID v4 with incremental identifier.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| backupId | UUID | PK, not null | Primary identifier |
| type | BackupType | not null | Backup type |
| status | BackupStatus | not null | Current status |
| size | long | not null | Backup size in bytes |
| checksum | string | not null | Integrity checksum |
| location | URL | not null | Storage location |
| startedAt | DateTime | not null | Start timestamp |
| completedAt | DateTime | nullable | Completion timestamp |
| expiresAt | DateTime | not null | Retention expiry |
| metadata | JSON | nullable | Backup metadata |
| initiatedBy | UUID | not null, FK | Initiator |

**Relationships:**
- Belongs to one `User` (initiator) (M:1)

**Ownership:**
- Owned by Backup Context
- Can be read by: Operations, Admin
- Can be modified by: System only

**Lifecycle:**
```
Scheduled → In Progress → Completed → Verified → Archived → Purged
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-BACKUP-001 | size | Positive integer | INVALID_SIZE |
| VAL-BACKUP-002 | checksum | Valid hash | INVALID_CHECKSUM |
| VAL-BACKUP-003 | expiresAt | After completedAt | INVALID_EXPIRY |

**Persistence Strategy:**
- Table: `backups`
- Indexes: backupId (PK), status, expiresAt
- Metadata stored in database
- Actual backup in object storage

**Audit Requirements:**
- Log creation, completion, verification
- Log restore operations
- Log deletion/purge
- Retention: 10 years

---

### 22. AuditEntry

**Identity Strategy:** UUID v4, append-only with cryptographic chaining.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| entryId | UUID | PK, not null | Primary identifier |
| eventType | EventType | not null | Event classification |
| actorId | UUID | nullable, FK | Performing user |
| actorType | ActorType | not null | User, system, plugin |
| resourceType | string | not null | Resource type |
| resourceId | UUID | nullable | Resource identifier |
| action | string | not null | Performed action |
| metadata | JSON | nullable | Additional data |
| ipAddress | IP | nullable | Client IP |
| userAgent | string | nullable | Client user agent |
| previousHash | string | not null | Chain link |
| currentHash | string | not null | Entry hash |
| timestamp | DateTime | not null | Event timestamp |

**Relationships:**
- References one `User` (actor) (M:1)

**Ownership:**
- Owned by Audit Context
- Can be read by: Security, Compliance, Admin
- Can be modified by: System only (immutable)

**Lifecycle:**
```
Created → Verified → Archived → Purged (after retention)
```

**Validation Rules:**
| Rule | Field | Condition | Error Code |
|------|-------|-----------|------------|
| VAL-AUDIT-001 | eventType | Valid EventType | INVALID_EVENT_TYPE |
| VAL-AUDIT-002 | currentHash | Valid hash matching content | INVALID_HASH |
| VAL-AUDIT-003 | previousHash | Matches previous entry or genesis | CHAIN_BROKEN |

**Persistence Strategy:**
- Table: `audit_entries`
- Indexes: entryId (PK), eventType, actorId, timestamp
- Append-only (no updates/deletes)
- Partitioned by month for performance
- Cryptographic chain for tamper evidence

**Audit Requirements:**
- Self-referential (audit entries are audited)
- Tamper-evident via hash chain
- Retention: 7 years minimum
- Compliance-ready export format

---

## Entity Relationship Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Entity Relationships                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User ──1:1──▶ UserProfile                                                 │
│    │                                                                       │
│    ├──M:N──▶ Role ──M:N──▶ Permission                                     │
│    │                                                                       │
│    ├──1:M──▶ Session                                                      │
│    │                                                                       │
│    ├──M:N──▶ Group                                                        │
│    │                                                                       │
│    ├──M:N──▶ Organization                                                 │
│    │                                                                       │
│    ├──1:M──▶ Enrollment ──1:1──▶ Progress                                 │
│    │              │                                                        │
│    │              └──M:1──▶ Course ──1:M──▶ Module ──1:M──▶ Lesson       │
│    │                                                                       │
│    ├──1:M──▶ Certificate                                                  │
│    │                                                                       │
│    └──1:M──▶ AuditEntry                                                   │
│                                                                             │
│  Course ──1:M──▶ Assessment ──1:M──▶ Question ──1:M──▶ Answer            │
│                                                                             │
│  Plugin ──1:M──▶ PluginVersion ──1:M──▶ PluginDependency                  │
│                                                                             │
│  Configuration ──1:M──▶ Setting                                            │
│                                                                             │
│  Backup ──M:1──▶ User (initiator)                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial entity catalog | AuthShield Team |
| 1.1 | 2024-02-20 | Added Platform entities | AuthShield Team |
| 1.2 | 2024-03-10 | Refined validation rules and persistence | AuthShield Team |
