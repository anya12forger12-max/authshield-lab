# AuthShield Lab - Domain Events

## Overview

This document defines all domain events in AuthShield Lab, specifying publishers, subscribers, payload schemas, ordering, reliability requirements, and audit considerations for each event.

---

## Domain Events Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Domain Events Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Event Producers                                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │ Identity │  │Education │  │Assessment│  │ Platform │         │   │
│  │  │ Context  │  │ Context  │  │ Context  │  │ Context  │         │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │   │
│  └───────┼──────────────┼──────────────┼──────────────┼───────────────┘   │
│          │              │              │              │                     │
│          ▼              ▼              ▼              ▼                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Event Bus                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Message Broker                            │   │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │   │   │
│  │  │  │ Identity│  │Education│  │Assessment│  │ Platform│      │   │   │
│  │  │  │ Topic   │  │ Topic   │  │ Topic   │  │ Topic   │      │   │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └────────────────────────────┬────────────────────────────────────────┘   │
│                               │                                             │
│          ┌────────────────────┼────────────────────┐                       │
│          ▼                    ▼                    ▼                        │
│  ┌──────────┐          ┌──────────┐          ┌──────────┐                 │
│  │Analytics │          │  Audit   │          │  Notif   │                 │
│  │ Consumer │          │ Consumer │          │ Consumer │                 │
│  └──────────┘          └──────────┘          └──────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Event Categories

| Category | Description | Priority | Retention |
|----------|-------------|----------|-----------|
| Identity Events | User lifecycle events | High | 7 years |
| Session Events | Session management events | Medium | 1 year |
| Education Events | Course and content events | High | 5 years |
| Assessment Events | Evaluation events | High | 7 years |
| Certificate Events | Credential events | Critical | 10 years |
| Platform Events | System events | Medium | 1 year |
| Operational Events | Infrastructure events | Low | 90 days |

---

## 1. Identity Events

### 1.1 UserCreated

**Purpose:** Indicates a new user has been registered in the platform.

**Publisher:** Identity Context → User Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Education Context | Enable enrollment | Sync user data |
| Analytics Context | User metrics | Increment counters |
| Notification Context | Welcome email | Send onboarding |
| Audit Context | Compliance | Log creation |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "UserCreated",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "userId": "UUID",
    "email": "string",
    "username": "string",
    "displayName": "string",
    "status": "pending",
    "createdAt": "ISO8601",
    "createdBy": "UUID|system",
    "metadata": {
      "registrationSource": "web|api|oauth",
      "invitedBy": "UUID|null",
      "organizationId": "UUID|null"
    }
  }
}
```

**Ordering:** Per-user ordering guaranteed. Cross-user ordering best-effort.

**Reliability:** At-least-once delivery. Idempotent processing required.

**Audit Requirements:**
- Log event publication
- Log subscriber processing
- Log any failures

---

### 1.2 UserUpdated

**Purpose:** Indicates user profile or attributes have been modified.

**Publisher:** Identity Context → User Aggregate, UserProfile Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Education Context | Update enrollments | Sync display name |
| Analytics Context | User metrics | Track changes |
| Notification Context | Profile changes | Notify if sensitive |
| Audit Context | Compliance | Log changes |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "UserUpdated",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "userId": "UUID",
    "changes": [
      {
        "field": "string",
        "oldValue": "any",
        "newValue": "any",
        "changedAt": "ISO8601"
      }
    ],
    "updatedBy": "UUID",
    "updatedAt": "ISO8601"
  }
}
```

**Ordering:** Per-user ordering guaranteed.

**Reliability:** At-least-once delivery. Idempotent processing required.

**Audit Requirements:**
- Log all profile changes
- Log who made changes
- Log before/after values

---

### 1.3 UserDeleted

**Purpose:** Indicates user account has been soft-deleted.

**Publisher:** Identity Context → User Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Education Context | Handle enrollments | Archive enrollments |
| Analytics Context | User metrics | Decrement counters |
| Session Context | Terminate sessions | Revoke all sessions |
| Audit Context | Compliance | Log deletion |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "UserDeleted",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "userId": "UUID",
    "reason": "user_request|admin_action|policy_violation",
    "deletedBy": "UUID",
    "deletedAt": "ISO8601",
    "gracePeriodEnd": "ISO8601",
    "metadata": {
      "dataRetentionDays": 90,
      "anonymizeAfter": "ISO8601"
    }
  }
}
```

**Ordering:** Per-user ordering guaranteed.

**Reliability:** Exactly-once delivery. Critical event.

**Audit Requirements:**
- Log deletion with reason
- Log who initiated deletion
- Log data handling plan

---

### 1.4 PasswordChanged

**Purpose:** Indicates user password has been changed.

**Publisher:** Identity Context → User Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Session Context | Invalidate sessions | Revoke other sessions |
| Security Context | Security alert | Notify user |
| Audit Context | Compliance | Log change |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "PasswordChanged",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "userId": "UUID",
    "changedBy": "UUID",
    "changedAt": "ISO8601",
    "reason": "user_initiated|admin_reset|expired",
    "metadata": {
      "ipAddress": "string",
      "userAgent": "string",
      "invalidateOtherSessions": "boolean"
    }
  }
}
```

**Ordering:** Per-user ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log password change event
- Log initiator
- Log IP and user agent

---

### 1.5 RoleAssigned

**Purpose:** Indicates a role has been assigned to a user.

**Publisher:** Authorization Context → Role Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Education Context | Update permissions | Recalculate access |
| Analytics Context | User metrics | Track role changes |
| Audit Context | Compliance | Log assignment |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "RoleAssigned",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "userId": "UUID",
    "roleId": "UUID",
    "roleName": "string",
    "assignedBy": "UUID",
    "assignedAt": "ISO8601",
    "expiresAt": "ISO8601|null",
    "metadata": {
      "context": "global|organization|course",
      "contextId": "UUID|null"
    }
  }
}
```

**Ordering:** Per-user ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log role assignment
- Log who assigned role
- Log expiration if temporary

---

### 1.6 PermissionGranted

**Purpose:** Indicates a specific permission has been granted to a user.

**Publisher:** Authorization Context → Permission Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Education Context | Update access | Apply permission |
| Analytics Context | Metrics | Track grants |
| Audit Context | Compliance | Log grant |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "PermissionGranted",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "userId": "UUID",
    "permissionId": "UUID",
    "resource": "string",
    "action": "string",
    "grantedBy": "UUID",
    "grantedAt": "ISO8601",
    "expiresAt": "ISO8601|null",
    "conditions": "JSON|null"
  }
}
```

**Ordering:** Per-user ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log permission grant
- Log conditions
- Log expiration

---

## 2. Session Events

### 2.1 SessionCreated

**Purpose:** Indicates a new user session has been established.

**Publisher:** Session Context → Session Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Analytics Context | Session metrics | Track active sessions |
| Security Context | Anomaly detection | Check for suspicious activity |
| Audit Context | Compliance | Log session start |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "SessionCreated",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "sessionId": "UUID",
    "userId": "UUID",
    "deviceInfo": {
      "deviceId": "string",
      "userAgent": "string",
      "ipAddress": "string",
      "deviceType": "browser|mobile|api"
    },
    "createdAt": "ISO8601",
    "expiresAt": "ISO8601",
    "metadata": {
      "authMethod": "password|mfa|oauth",
      "isRememberMe": "boolean"
    }
  }
}
```

**Ordering:** Per-user ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log session creation
- Log device information
- Log authentication method

---

### 2.2 SessionExpired

**Purpose:** Indicates a user session has expired.

**Publisher:** Session Context → Session Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Analytics Context | Session metrics | Update session stats |
| Security Context | Cleanup | Handle expiry |
| Audit Context | Compliance | Log expiry |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "SessionExpired",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "sessionId": "UUID",
    "userId": "UUID",
    "reason": "timeout|token_expired|max_age",
    "expiredAt": "ISO8601",
    "duration": "number (seconds)",
    "metadata": {
      "lastActivityAt": "ISO8601",
      "activityCount": "number"
    }
  }
}
```

**Ordering:** Per-user ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log session expiry
- Log reason for expiry
- Log session duration

---

### 2.3 SessionRevoked

**Purpose:** Indicates a user session has been forcibly terminated.

**Publisher:** Session Context → Session Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Security Context | Security alert | Notify user |
| Analytics Context | Security metrics | Track revocations |
| Notification Context | Alert user | Send notification |
| Audit Context | Compliance | Log revocation |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "SessionRevoked",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "sessionId": "UUID",
    "userId": "UUID",
    "revokedBy": "UUID|system",
    "reason": "user_request|security_concern|admin_action|concurrent_limit",
    "revokedAt": "ISO8601",
    "metadata": {
      "ipAddress": "string",
      "userAgent": "string"
    }
  }
}
```

**Ordering:** Per-user ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log revocation event
- Log who initiated revocation
- Log reason for revocation

---

## 3. Education Events

### 3.1 CourseCreated

**Purpose:** Indicates a new course has been created.

**Publisher:** Education Context → Course Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Analytics Context | Course metrics | Track creation |
| Notification Context | Creator alert | Confirm creation |
| Audit Context | Compliance | Log creation |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "CourseCreated",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "courseId": "UUID",
    "title": "string",
    "courseCode": "string",
    "creatorId": "UUID",
    "createdAt": "ISO8601",
    "metadata": {
      "template": "string|null",
      "copiedFrom": "UUID|null"
    }
  }
}
```

**Ordering:** Per-course ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log course creation
- Log creator
- Log template if used

---

### 3.2 CoursePublished

**Purpose:** Indicates a course has been published and is now live.

**Publisher:** Education Context → Course Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Learning Context | Enable enrollment | Update course status |
| Analytics Context | Course metrics | Track publication |
| Notification Context | Announce course | Notify followers |
| Search Context | Index course | Update search index |
| Audit Context | Compliance | Log publication |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "CoursePublished",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "courseId": "UUID",
    "title": "string",
    "courseCode": "string",
    "publishedBy": "UUID",
    "publishedAt": "ISO8601",
    "version": "string",
    "metadata": {
      "moduleCount": "number",
      "lessonCount": "number",
      "estimatedDuration": "number (minutes)",
      "tags": ["string"]
    }
  }
}
```

**Ordering:** Per-course ordering guaranteed.

**Reliability:** Exactly-once delivery. Critical event.

**Audit Requirements:**
- Log publication
- Log publisher
- Log course version

---

### 3.3 CourseArchived

**Purpose:** Indicates a course has been archived and is no longer available for new enrollments.

**Publisher:** Education Context → Course Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Learning Context | Update enrollments | Notify enrolled users |
| Analytics Context | Course metrics | Track archival |
| Search Context | Update index | Remove from search |
| Audit Context | Compliance | Log archival |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "CourseArchived",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "courseId": "UUID",
    "archivedBy": "UUID",
    "archivedAt": "ISO8601",
    "reason": "string",
    "metadata": {
      "activeEnrollments": "number",
      "completionDeadline": "ISO8601|null"
    }
  }
}
```

**Ordering:** Per-course ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log archival
- Log reason
- Log active enrollment count

---

### 3.4 LessonCompleted

**Purpose:** Indicates a learner has completed a lesson.

**Publisher:** Learning Context → Progress Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Education Context | Update statistics | Track completion |
| Analytics Context | Learning metrics | Update progress |
| Assessment Context | Check prerequisites | Unlock assessments |
| Certificate Context | Check eligibility | Update progress |
| Notification Context | Progress update | Notify learner |
| Audit Context | Compliance | Log completion |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "LessonCompleted",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "userId": "UUID",
    "courseId": "UUID",
    "moduleId": "UUID",
    "lessonId": "UUID",
    "completedAt": "ISO8601",
    "score": "number|null",
    "timeSpent": "number (seconds)",
    "metadata": {
      "attemptNumber": "number",
      "passedAssessment": "boolean|null"
    }
  }
}
```

**Ordering:** Per-user-course ordering guaranteed.

**Reliability:** At-least-once delivery. Idempotent processing required.

**Audit Requirements:**
- Log lesson completion
- Log score if applicable
- Log time spent

---

### 3.5 EnrollmentCreated

**Purpose:** Indicates a learner has enrolled in a course.

**Publisher:** Learning Context → Enrollment Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Education Context | Update statistics | Track enrollment |
| Analytics Context | Enrollment metrics | Increment counter |
| Certificate Context | Track eligibility | Initialize tracking |
| Notification Context | Welcome | Send enrollment confirmation |
| Audit Context | Compliance | Log enrollment |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "EnrollmentCreated",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "enrollmentId": "UUID",
    "userId": "UUID",
    "courseId": "UUID",
    "enrolledAt": "ISO8601",
    "expiresAt": "ISO8601|null",
    "metadata": {
      "enrollmentSource": "self|admin|api",
      "promoCode": "string|null"
    }
  }
}
```

**Ordering:** Per-user-course ordering guaranteed.

**Reliability:** Exactly-once delivery.

**Audit Requirements:**
- Log enrollment creation
- Log enrollment source
- Log expiry if applicable

---

### 3.6 ProgressUpdated

**Purpose:** Indicates learner progress has been updated.

**Publisher:** Learning Context → Progress Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Education Context | Course statistics | Update metrics |
| Analytics Context | Learning analytics | Track progress |
| Certificate Context | Completion check | Evaluate eligibility |
| Notification Context | Milestone alerts | Notify on milestones |
| Audit Context | Compliance | Log progress |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "ProgressUpdated",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "userId": "UUID",
    "courseId": "UUID",
    "moduleId": "UUID",
    "lessonId": "UUID",
    "previousStatus": "not_started|in_progress|completed",
    "newStatus": "in_progress|completed",
    "score": "number|null",
    "updatedAt": "ISO8601",
    "metadata": {
      "overallProgress": "number (percentage)",
      "isCourseComplete": "boolean"
    }
  }
}
```

**Ordering:** Per-user-course ordering guaranteed.

**Reliability:** At-least-once delivery. Idempotent processing required.

**Audit Requirements:**
- Log status change
- Log score if applicable
- Log overall progress

---

## 4. Assessment Events

### 4.1 AssessmentStarted

**Purpose:** Indicates a learner has started an assessment attempt.

**Publisher:** Assessment Context → Assessment Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Analytics Context | Attempt metrics | Track starts |
| Security Context | Monitoring | Monitor session |
| Audit Context | Compliance | Log attempt start |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "AssessmentStarted",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "assessmentId": "UUID",
    "userId": "UUID",
    "attemptNumber": "number",
    "startedAt": "ISO8601",
    "timeLimit": "number (minutes)|null",
    "metadata": {
      "questionCount": "number",
      "shuffleQuestions": "boolean",
      "proctored": "boolean"
    }
  }
}
```

**Ordering:** Per-user-assessment ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log attempt start
- Log attempt number
- Log time limit

---

### 4.2 AssessmentSubmitted

**Purpose:** Indicates a learner has submitted an assessment for grading.

**Publisher:** Assessment Context → Assessment Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Learning Context | Update progress | Record attempt |
| Analytics Context | Submission metrics | Track submissions |
| Notification Context | Confirmation | Notify submission |
| Audit Context | Compliance | Log submission |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "AssessmentSubmitted",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "assessmentId": "UUID",
    "userId": "UUID",
    "submissionId": "UUID",
    "attemptNumber": "number",
    "submittedAt": "ISO8601",
    "responseCount": "number",
    "metadata": {
      "timeSpent": "number (seconds)",
      "proctored": "boolean",
      "submissionType": "auto|manual"
    }
  }
}
```

**Ordering:** Per-user-assessment ordering guaranteed.

**Reliability:** Exactly-once delivery.

**Audit Requirements:**
- Log submission
- Log time spent
- Log submission type

---

### 4.3 AssessmentGraded

**Purpose:** Indicates an assessment has been graded and results are available.

**Publisher:** Assessment Context → Score Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Learning Context | Update grade | Record score |
| Certificate Context | Eligibility check | Evaluate requirements |
| Analytics Context | Performance metrics | Track scores |
| Notification Context | Results | Send results to learner |
| Competency Context | Skill update | Update competency levels |
| Audit Context | Compliance | Log grade |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "AssessmentGraded",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "assessmentId": "UUID",
    "userId": "UUID",
    "submissionId": "UUID",
    "score": {
      "value": "number",
      "maxScore": "number",
      "percentage": "number",
      "passed": "boolean"
    },
    "gradedAt": "ISO8601",
    "gradedBy": "UUID|system",
    "metadata": {
      "gradingMethod": "auto|manual|hybrid",
      "feedbackAvailable": "boolean",
      "comparedToAverage": "number"
    }
  }
}
```

**Ordering:** Per-user-assessment ordering guaranteed.

**Reliability:** Exactly-once delivery. Critical event.

**Audit Requirements:**
- Log grading event
- Log score details
- Log grading method

---

### 4.4 CompetencyAchieved

**Purpose:** Indicates a learner has achieved a competency level.

**Publisher:** Assessment Context → Competency Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Certificate Context | Eligibility check | Evaluate requirements |
| Learning Context | Progress update | Record achievement |
| Analytics Context | Competency metrics | Track achievements |
| Notification Context | Achievement | Celebrate achievement |
| Audit Context | Compliance | Log achievement |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "CompetencyAchieved",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "userId": "UUID",
    "competencyId": "UUID",
    "competencyName": "string",
    "level": "novice|beginner|intermediate|advanced|expert",
    "score": {
      "value": "number",
      "maxScore": "number",
      "percentage": "number"
    },
    "achievedAt": "ISO8601",
    "previousLevel": "string|null",
    "metadata": {
      "evidenceCount": "number",
      "assessmentIds": ["UUID"]
    }
  }
}
```

**Ordering:** Per-user-competency ordering guaranteed.

**Reliability:** Exactly-once delivery.

**Audit Requirements:**
- Log competency achievement
- Log level change
- Log evidence sources

---

## 5. Certificate Events

### 5.1 CertificateIssued

**Purpose:** Indicates a certificate has been issued to a learner.

**Publisher:** Certification Context → Certificate Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Learning Context | Update record | Record achievement |
| Analytics Context | Certification metrics | Track issuances |
| Notification Context | Delivery | Send certificate |
| Blockchain Context | Anchoring | Create anchor record |
| Audit Context | Compliance | Log issuance |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "CertificateIssued",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "certificateId": "UUID",
    "userId": "UUID",
    "courseId": "UUID",
    "courseTitle": "string",
    "verificationCode": "string",
    "issuedAt": "ISO8601",
    "expiresAt": "ISO8601|null",
    "issuedBy": "UUID|system",
    "metadata": {
      "templateId": "UUID",
      "finalGrade": "number",
      "completionDate": "ISO8601"
    }
  }
}
```

**Ordering:** Per-user ordering guaranteed.

**Reliability:** Exactly-once delivery. Critical event.

**Audit Requirements:**
- Log issuance
- Log verification code
- Log issuer
- Log expiry

---

### 5.2 CertificateRevoked

**Purpose:** Indicates a certificate has been revoked.

**Publisher:** Certification Context → Certificate Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Learning Context | Update record | Mark as revoked |
| Analytics Context | Certification metrics | Track revocations |
| Notification Context | Alert | Notify certificate holder |
| Verification Context | Update status | Mark as invalid |
| Audit Context | Compliance | Log revocation |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "CertificateRevoked",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "certificateId": "UUID",
    "userId": "UUID",
    "courseId": "UUID",
    "verificationCode": "string",
    "revokedBy": "UUID",
    "revokedAt": "ISO8601",
    "reason": "academic_integrity|policy_violation|request|error",
    "metadata": {
      "evidence": "string|null",
      "appealDeadline": "ISO8601|null"
    }
  }
}
```

**Ordering:** Per-certificate ordering guaranteed.

**Reliability:** Exactly-once delivery. Critical event.

**Audit Requirements:**
- Log revocation
- Log reason
- Log who revoked
- Log appeal process if applicable

---

### 5.3 CertificateExpired

**Purpose:** Indicates a certificate has reached its expiration date.

**Publisher:** Certification Context → Certificate Aggregate (scheduled)

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Learning Context | Update record | Mark as expired |
| Analytics Context | Certification metrics | Track expirations |
| Notification Context | Alert | Notify renewal option |
| Verification Context | Update status | Mark as expired |
| Audit Context | Compliance | Log expiration |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "CertificateExpired",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "certificateId": "UUID",
    "userId": "UUID",
    "courseId": "UUID",
    "verificationCode": "string",
    "expiredAt": "ISO8601",
    "issuedAt": "ISO8601",
    "metadata": {
      "renewalWindowDays": "number",
      "renewalDeadline": "ISO8601"
    }
  }
}
```

**Ordering:** Per-certificate ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log expiration
- Log renewal window

---

## 6. Platform Events

### 6.1 PluginInstalled

**Purpose:** Indicates a plugin has been installed on the platform.

**Publisher:** Plugin Context → Plugin Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Platform Context | Enable capabilities | Register capabilities |
| Analytics Context | Plugin metrics | Track installations |
| Notification Context | Admin alert | Notify installation |
| Audit Context | Compliance | Log installation |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "PluginInstalled",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "pluginId": "UUID",
    "pluginName": "string",
    "version": "string",
    "installedBy": "UUID",
    "installedAt": "ISO8601",
    "capabilities": [
      {
        "capabilityId": "UUID",
        "type": "string",
        "name": "string"
      }
    ],
    "metadata": {
      "configurationRequired": "boolean",
      "dependencies": ["string"]
    }
  }
}
```

**Ordering:** Per-plugin ordering guaranteed.

**Reliability:** Exactly-once delivery.

**Audit Requirements:**
- Log installation
- Log version
- Log installer
- Log capabilities

---

### 6.2 PluginUpdated

**Purpose:** Indicates a plugin has been updated to a new version.

**Publisher:** Plugin Context → Plugin Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Platform Context | Update capabilities | Apply changes |
| Analytics Context | Plugin metrics | Track updates |
| Notification Context | Admin alert | Notify update |
| Audit Context | Compliance | Log update |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "PluginUpdated",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "pluginId": "UUID",
    "pluginName": "string",
    "fromVersion": "string",
    "toVersion": "string",
    "updatedBy": "UUID",
    "updatedAt": "ISO8601",
    "breakingChanges": "boolean",
    "metadata": {
      "changelog": "string",
      "requiresRestart": "boolean"
    }
  }
}
```

**Ordering:** Per-plugin ordering guaranteed.

**Reliability:** Exactly-once delivery.

**Audit Requirements:**
- Log update
- Log version change
- Log breaking changes

---

### 6.3 PluginRemoved

**Purpose:** Indicates a plugin has been removed from the platform.

**Publisher:** Plugin Context → Plugin Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Platform Context | Disable capabilities | Unregister capabilities |
| Analytics Context | Plugin metrics | Track removals |
| Notification Context | Admin alert | Notify removal |
| Audit Context | Compliance | Log removal |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "PluginRemoved",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "pluginId": "UUID",
    "pluginName": "string",
    "removedBy": "UUID",
    "removedAt": "ISO8601",
    "reason": "string",
    "metadata": {
      "dataRetention": "string",
      "migrationRequired": "boolean"
    }
  }
}
```

**Ordering:** Per-plugin ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log removal
- Log reason
- Log data handling

---

### 6.4 ConfigurationUpdated

**Purpose:** Indicates a configuration setting has been changed.

**Publisher:** Configuration Context → Configuration Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| All Contexts | Apply config | Update runtime config |
| Analytics Context | Config metrics | Track changes |
| Audit Context | Compliance | Log change |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "ConfigurationUpdated",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "configKey": "string",
    "environment": "development|staging|production",
    "oldValue": "any",
    "newValue": "any",
    "updatedBy": "UUID",
    "updatedAt": "ISO8601",
    "metadata": {
      "requiresRestart": "boolean",
      "affectedServices": ["string"]
    }
  }
}
```

**Ordering:** Per-key ordering guaranteed.

**Reliability:** Exactly-once delivery.

**Audit Requirements:**
- Log change with before/after values
- Log who made change
- Log affected services

---

## 7. Operational Events

### 7.1 BackupCompleted

**Purpose:** Indicates a backup operation has completed successfully.

**Publisher:** Backup Context → Backup Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Operations Context | Monitoring | Update backup status |
| Analytics Context | Metrics | Track backup stats |
| Audit Context | Compliance | Log backup |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "BackupCompleted",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "backupId": "UUID",
    "type": "full|incremental|differential",
    "status": "success|partial|failed",
    "size": "number (bytes)",
    "duration": "number (seconds)",
    "checksum": "string",
    "startedAt": "ISO8601",
    "completedAt": "ISO8601",
    "metadata": {
      "storageLocation": "string",
      "compressionRatio": "number",
      "encrypted": "boolean"
    }
  }
}
```

**Ordering:** Per-backup ordering guaranteed.

**Reliability:** At-least-once delivery.

**Audit Requirements:**
- Log backup completion
- Log size and duration
- Log storage location

---

### 7.2 AuditEntryCreated

**Purpose:** Indicates a new audit entry has been created.

**Publisher:** Audit Context → AuditEntry Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| Security Context | Monitoring | Real-time analysis |
| Compliance Context | Reporting | Compliance tracking |
| Analytics Context | Metrics | Audit analytics |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "AuditEntryCreated",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "entryId": "UUID",
    "eventType": "string",
    "actorId": "UUID",
    "actorType": "user|system|plugin",
    "resourceType": "string",
    "resourceId": "UUID",
    "action": "string",
    "timestamp": "ISO8601",
    "metadata": {
      "ipAddress": "string",
      "userAgent": "string",
      "previousHash": "string",
      "currentHash": "string"
    }
  }
}
```

**Ordering:** Global ordering guaranteed (hash chain).

**Reliability:** Exactly-once delivery. Critical event.

**Audit Requirements:**
- Self-referential (audit events are audited)
- Tamper-evident via hash chain

---

### 7.3 SecurityPolicyUpdated

**Purpose:** Indicates a security policy has been updated.

**Publisher:** Authorization Context → Policy Aggregate

**Subscribers:**
| Subscriber | Purpose | Processing |
|------------|---------|------------|
| All Contexts | Apply policy | Update enforcement |
| Analytics Context | Security metrics | Track policy changes |
| Notification Context | Admin alert | Notify policy change |
| Audit Context | Compliance | Log policy update |

**Payload Schema:**
```json
{
  "eventId": "UUID",
  "eventType": "SecurityPolicyUpdated",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {
    "policyId": "UUID",
    "policyName": "string",
    "action": "created|updated|deleted|activated|deactivated",
    "updatedBy": "UUID",
    "updatedAt": "ISO8601",
    "metadata": {
      "policyType": "string",
      "effectiveDate": "ISO8601",
      "requiresNotification": "boolean"
    }
  }
}
```

**Ordering:** Per-policy ordering guaranteed.

**Reliability:** Exactly-once delivery.

**Audit Requirements:**
- Log policy change
- Log effective date
- Log notification requirement

---

## Event Processing Patterns

### 1. Idempotent Processing
All event handlers must be idempotent. Use event ID for deduplication.

```python
def handle_event(event):
    if event_already_processed(event.eventId):
        return
    
    process_event(event)
    mark_event_processed(event.eventId)
```

### 2. Event Sourcing
Critical aggregates can use event sourcing for state reconstruction.

```python
def rebuild_state(aggregateId):
    events = event_store.get_events(aggregateId)
    state = InitialState()
    
    for event in events:
        state = apply_event(state, event)
    
    return state
```

### 3. Saga Pattern
Long-running processes use sagas for coordination.

```python
class CourseCompletionSaga:
    def __init__(self, userId, courseId):
        self.userId = userId
        self.courseId = courseId
        self.steps = [
            self.check_progress,
            self.check_assessments,
            self.issue_certificate,
            self.send_notification
        ]
    
    def execute(self):
        for step in self.steps:
            try:
                step()
            except Exception as e:
                self.compensate()
                raise
```

### 4. Event Replay
Support event replay for debugging and recovery.

```python
def replay_events(fromDate, toDate, handler):
    events = event_store.get_events(fromDate, toDate)
    
    for event in events:
        handler.process(event)
```

---

## Event Schema Evolution

### Versioning Strategy
- Major version: Breaking changes
- Minor version: New optional fields
- Patch version: Documentation only

### Backward Compatibility
- New fields must be optional
- Existing fields cannot be removed
- Field types cannot change
- Renamed fields require new field + deprecation

### Migration Process
1. Add new optional fields
2. Publish migration event
3. Update all consumers
4. Deprecate old fields
5. Remove old fields after 6 months

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial domain events | AuthShield Team |
| 1.1 | 2024-02-20 | Added certificate and plugin events | AuthShield Team |
| 1.2 | 2024-03-10 | Added operational events | AuthShield Team |
