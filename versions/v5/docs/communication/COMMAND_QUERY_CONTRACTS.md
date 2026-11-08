# Command & Query Contracts (CQRS)

## Document Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Status | Authoritative |
| Last Updated | 2026-07-19 |
| Owner | Architecture Team |
| Classification | Internal |

---

## 1. Overview

AuthShield Lab follows Command Query Responsibility Segregation (CQRS) principles to separate read and write operations. Commands mutate state and return confirmation; queries read state and return data. Every command and query is a typed contract with explicit input/output schemas, validation rules, authorization requirements, and error codes.

### 1.1 Design Principles

| Principle | Description |
|-----------|-------------|
| Explicit Contracts | Every command/query has a defined input and output schema |
| Idempotent Commands | Commands use unique IDs for idempotent replay |
| Read-Optimized Queries | Queries may use cached or denormalized data |
| Authorization Required | Every operation requires specific role/permission |
| Validation at Boundary | Input validation occurs before business logic |
| Accessibility by Design | All operations consider accessibility requirements |

---

## 2. Command Contracts

### 2.1 Authentication Commands

#### AuthenticateUser

| Attribute | Detail |
|-----------|--------|
| Purpose | Verify user credentials and establish a session |
| Service | Authentication Service |
| Authorization | Public (pre-authentication) |

**Input Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AuthenticateUserCommand",
  "type": "object",
  "required": ["username", "password"],
  "properties": {
    "command_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique command ID for idempotent replay"
    },
    "username": {
      "type": "string",
      "minLength": 3,
      "maxLength": 64,
      "pattern": "^[a-zA-Z0-9_.@-]+$"
    },
    "password": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "remember_me": {
      "type": "boolean",
      "default": false
    }
  }
}
```

**Output Schema:**

```json
{
  "title": "AuthenticateUserResult",
  "type": "object",
  "required": ["success", "session_token", "refresh_token", "expires_at"],
  "properties": {
    "success": { "type": "boolean" },
    "session_token": { "type": "string" },
    "refresh_token": { "type": "string" },
    "expires_at": { "type": "string", "format": "date-time" },
    "user": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "username": { "type": "string" },
        "roles": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

**Validation Rules:**
- Username must be non-empty, max 64 characters
- Password must be non-empty, max 128 characters
- Rate limited: max 5 attempts per 15 minutes per username

**Accessibility Considerations:**
- Error messages must be compatible with screen readers
- No CAPTCHA required (offline-first platform)

**Error Codes:**

| Code | Description |
|------|-------------|
| `AUTH-VAL-001` | Invalid username format |
| `AUTH-VAL-002` | Missing password |
| `AUTH-AUTH-001` | Invalid credentials |
| `AUTH-AUTH-002` | Account locked due to failed attempts |
| `AUTH-AUTH-003` | Account disabled |
| `AUTH-TMO-001` | Authentication timeout |
| `AUTH-SEC-001` | Rate limit exceeded |

---

#### RefreshToken

| Attribute | Detail |
|-----------|--------|
| Purpose | Exchange a refresh token for a new access/refresh token pair |
| Service | Authentication Service |
| Authorization | Valid refresh token required |

**Input Schema:**

```json
{
  "title": "RefreshTokenCommand",
  "type": "object",
  "required": ["refresh_token"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "refresh_token": { "type": "string", "minLength": 1 }
  }
}
```

**Output Schema:**

```json
{
  "title": "RefreshTokenResult",
  "type": "object",
  "required": ["session_token", "refresh_token", "expires_at"],
  "properties": {
    "session_token": { "type": "string" },
    "refresh_token": { "type": "string" },
    "expires_at": { "type": "string", "format": "date-time" }
  }
}
```

**Error Codes:**

| Code | Description |
|------|-------------|
| `AUTH-AUTH-004` | Refresh token expired |
| `AUTH-AUTH-005` | Refresh token revoked |
| `AUTH-AUTH-006` | Refresh token invalid |

---

#### RevokeSession

| Attribute | Detail |
|-----------|--------|
| Purpose | Invalidate a specific session or all sessions for a user |
| Service | Authentication Service |
| Authorization | Own session or admin role |

**Input Schema:**

```json
{
  "title": "RevokeSessionCommand",
  "type": "object",
  "required": ["session_id"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "session_id": { "type": "string", "format": "uuid" },
    "revoke_all": {
      "type": "boolean",
      "default": false,
      "description": "If true, revoke all sessions for the user"
    }
  }
}
```

**Output Schema:**

```json
{
  "title": "RevokeSessionResult",
  "type": "object",
  "required": ["revoked_count"],
  "properties": {
    "revoked_count": { "type": "integer", "minimum": 0 }
  }
}
```

---

### 2.2 Authorization Commands

#### AssignRole

| Attribute | Detail |
|-----------|--------|
| Purpose | Grant a role to a user |
| Service | Authorization Service |
| Authorization | Admin role required |

**Input Schema:**

```json
{
  "title": "AssignRoleCommand",
  "type": "object",
  "required": ["user_id", "role"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "user_id": { "type": "string", "format": "uuid" },
    "role": {
      "type": "string",
      "enum": ["admin", "instructor", "student", "viewer"]
    },
    "expires_at": {
      "type": "string",
      "format": "date-time",
      "description": "Optional expiration for temporary roles"
    }
  }
}
```

**Output Schema:**

```json
{
  "title": "AssignRoleResult",
  "type": "object",
  "required": ["assigned"],
  "properties": {
    "assigned": { "type": "boolean" },
    "user_roles": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

**Error Codes:**

| Code | Description |
|------|-------------|
| `AUTHZ-AUTH-001` | Insufficient permissions to assign role |
| `AUTHZ-VAL-001` | Invalid role name |
| `AUTHZ-VAL-002` | Cannot assign admin role to self |
| `AUTHZ-VAL-003` | User not found |

---

### 2.3 Course Management Commands

#### CreateCourse

| Attribute | Detail |
|-----------|--------|
| Purpose | Create a new course with initial structure |
| Service | Course Management Service |
| Authorization | Instructor or admin role |

**Input Schema:**

```json
{
  "title": "CreateCourseCommand",
  "type": "object",
  "required": ["title"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "description": {
      "type": "string",
      "maxLength": 5000
    },
    "category": { "type": "string" },
    "difficulty_level": {
      "type": "string",
      "enum": ["beginner", "intermediate", "advanced", "expert"]
    },
    "estimated_duration_minutes": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10000
    },
    "tags": {
      "type": "array",
      "items": { "type": "string", "maxLength": 50 },
      "maxItems": 20
    },
    "prerequisites": {
      "type": "array",
      "items": { "type": "string", "format": "uuid" },
      "description": "Course IDs that must be completed first"
    }
  }
}
```

**Output Schema:**

```json
{
  "title": "CreateCourseResult",
  "type": "object",
  "required": ["course_id", "created_at"],
  "properties": {
    "course_id": { "type": "string", "format": "uuid" },
    "created_at": { "type": "string", "format": "date-time" },
    "status": {
      "type": "string",
      "enum": ["draft"]
    }
  }
}
```

**Validation Rules:**
- Title must be 1-200 characters
- Description max 5000 characters
- Tags array max 20 items, each max 50 characters
- Prerequisites must reference existing published courses

**Error Codes:**

| Code | Description |
|------|-------------|
| `COURSE-VAL-001` | Title is required |
| `COURSE-VAL-002` | Title exceeds maximum length |
| `COURSE-VAL-003` | Invalid difficulty level |
| `COURSE-VAL-004` | Invalid prerequisite course ID |
| `COURSE-AUTH-001` | Insufficient permissions to create course |

---

#### PublishCourse

| Attribute | Detail |
|-----------|--------|
| Purpose | Transition a course from draft to published state |
| Service | Course Management Service |
| Authorization | Instructor (own courses) or admin |

**Input Schema:**

```json
{
  "title": "PublishCourseCommand",
  "type": "object",
  "required": ["course_id"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "course_id": { "type": "string", "format": "uuid" },
    "publish_immediately": {
      "type": "boolean",
      "default": true
    }
  }
}
```

**Validation Rules:**
- Course must have at least one lesson
- All lessons must pass content validation
- Course must be in draft or review state
- All prerequisite courses must be published

**Error Codes:**

| Code | Description |
|------|-------------|
| `COURSE-VAL-005` | Course has no lessons |
| `COURSE-VAL-006` | One or more lessons fail validation |
| `COURSE-VAL-007` | Course not in publishable state |
| `COURSE-VAL-008` | Prerequisite course not published |

---

#### ArchiveCourse

| Attribute | Detail |
|-----------|--------|
| Purpose | Archive a course, making it read-only and hidden from new enrollments |
| Service | Course Management Service |
| Authorization | Instructor (own courses) or admin |

**Input Schema:**

```json
{
  "title": "ArchiveCourseCommand",
  "type": "object",
  "required": ["course_id"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "course_id": { "type": "string", "format": "uuid" },
    "reason": {
      "type": "string",
      "maxLength": 500,
      "description": "Reason for archival"
    }
  }
}
```

---

### 2.4 Learning Engine Commands

#### EnrollStudent

| Attribute | Detail |
|-----------|--------|
| Purpose | Enroll a student in a course |
| Service | Learning Engine Service |
| Authorization | Student (self) or admin |

**Input Schema:**

```json
{
  "title": "EnrollStudentCommand",
  "type": "object",
  "required": ["student_id", "course_id"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "student_id": { "type": "string", "format": "uuid" },
    "course_id": { "type": "string", "format": "uuid" }
  }
}
```

**Validation Rules:**
- Student must exist and be active
- Course must be published
- Student must not already be enrolled
- Prerequisites must be met (if any)

**Error Codes:**

| Code | Description |
|------|-------------|
| `LEARN-VAL-001` | Student not found |
| `LEARN-VAL-002` | Course not published |
| `LEARN-VAL-003` | Already enrolled |
| `LEARN-VAL-004` | Prerequisites not met |
| `LEARN-AUTH-001` | Cannot enroll others (non-admin) |

---

#### StartLesson

| Attribute | Detail |
|-----------|--------|
| Purpose | Mark a lesson as started by a student |
| Service | Learning Engine Service |
| Authorization | Enrolled student |

**Input Schema:**

```json
{
  "title": "StartLessonCommand",
  "type": "object",
  "required": ["student_id", "course_id", "lesson_id"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "student_id": { "type": "string", "format": "uuid" },
    "course_id": { "type": "string", "format": "uuid" },
    "lesson_id": { "type": "string", "format": "uuid" }
  }
}
```

**Validation Rules:**
- Student must be enrolled in the course
- Lesson must exist and belong to the course
- Previous lessons must be completed (or course allows non-sequential)

---

#### CompleteLesson

| Attribute | Detail |
|-----------|--------|
| Purpose | Mark a lesson as completed by a student |
| Service | Learning Engine Service |
| Authorization | Enrolled student |

**Input Schema:**

```json
{
  "title": "CompleteLessonCommand",
  "type": "object",
  "required": ["student_id", "course_id", "lesson_id"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "student_id": { "type": "string", "format": "uuid" },
    "course_id": { "type": "string", "format": "uuid" },
    "lesson_id": { "type": "string", "format": "uuid" },
    "time_spent_seconds": {
      "type": "integer",
      "minimum": 0
    },
    "notes": {
      "type": "string",
      "maxLength": 2000,
      "description": "Optional student notes"
    }
  }
}
```

**Output Schema:**

```json
{
  "title": "CompleteLessonResult",
  "type": "object",
  "required": ["completed", "course_progress_percent"],
  "properties": {
    "completed": { "type": "boolean" },
    "course_progress_percent": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "next_lesson_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the next lesson, or null if course complete"
    },
    "course_completed": { "type": "boolean" }
  }
}
```

---

### 2.5 Assessment Engine Commands

#### StartAssessment

| Attribute | Detail |
|-----------|--------|
| Purpose | Begin an assessment attempt for a student |
| Service | Assessment Engine Service |
| Authorization | Enrolled student |

**Input Schema:**

```json
{
  "title": "StartAssessmentCommand",
  "type": "object",
  "required": ["student_id", "assessment_id"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "student_id": { "type": "string", "format": "uuid" },
    "assessment_id": { "type": "string", "format": "uuid" }
  }
}
```

**Output Schema:**

```json
{
  "title": "StartAssessmentResult",
  "type": "object",
  "required": ["attempt_id", "questions", "time_limit_seconds"],
  "properties": {
    "attempt_id": { "type": "string", "format": "uuid" },
    "questions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "question_id": { "type": "string", "format": "uuid" },
          "question_text": { "type": "string" },
          "question_type": {
            "type": "string",
            "enum": ["multiple_choice", "true_false", "short_answer", "practical"]
          },
          "options": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "option_id": { "type": "string" },
                "option_text": { "type": "string" }
              }
            }
          }
        }
      }
    },
    "time_limit_seconds": { "type": "integer" },
    "max_attempts": { "type": "integer" }
  }
}
```

---

#### SubmitAssessment

| Attribute | Detail |
|-----------|--------|
| Purpose | Submit answers for an assessment attempt |
| Service | Assessment Engine Service |
| Authorization | Student with active attempt |

**Input Schema:**

```json
{
  "title": "SubmitAssessmentCommand",
  "type": "object",
  "required": ["student_id", "attempt_id", "answers"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "student_id": { "type": "string", "format": "uuid" },
    "attempt_id": { "type": "string", "format": "uuid" },
    "answers": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["question_id", "answer"],
        "properties": {
          "question_id": { "type": "string", "format": "uuid" },
          "answer": {
            "oneOf": [
              { "type": "string" },
              { "type": "boolean" },
              { "type": "array", "items": { "type": "string" } }
            ]
          }
        }
      }
    },
    "time_taken_seconds": {
      "type": "integer",
      "minimum": 0
    }
  }
}
```

**Output Schema:**

```json
{
  "title": "SubmitAssessmentResult",
  "type": "object",
  "required": ["score", "passed", "results"],
  "properties": {
    "score": {
      "type": "number",
      "minimum": 0,
      "maximum": 100
    },
    "passed": { "type": "boolean" },
    "passing_score": { "type": "number" },
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "question_id": { "type": "string" },
          "correct": { "type": "boolean" },
          "points_earned": { "type": "number" },
          "points_possible": { "type": "number" },
          "explanation": { "type": "string" }
        }
      }
    },
    "attempt_number": { "type": "integer" },
    "attempts_remaining": { "type": "integer" }
  }
}
```

---

#### IssueCertificate

| Attribute | Detail |
|-----------|--------|
| Purpose | Issue a certificate of completion for a course |
| Service | Certificate Service |
| Authorization | System (auto-issued on completion) |

**Input Schema:**

```json
{
  "title": "IssueCertificateCommand",
  "type": "object",
  "required": ["student_id", "course_id"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "student_id": { "type": "string", "format": "uuid" },
    "course_id": { "type": "string", "format": "uuid" }
  }
}
```

**Output Schema:**

```json
{
  "title": "IssueCertificateResult",
  "type": "object",
  "required": ["certificate_id", "issued_at", "certificate_url"],
  "properties": {
    "certificate_id": { "type": "string", "format": "uuid" },
    "issued_at": { "type": "string", "format": "date-time" },
    "certificate_url": { "type": "string" },
    "verification_code": { "type": "string" }
  }
}
```

---

### 2.6 Plugin Management Commands

#### InstallPlugin

| Attribute | Detail |
|-----------|--------|
| Purpose | Install a plugin from a package file |
| Service | Plugin Runtime Service |
| Authorization | Admin role |

**Input Schema:**

```json
{
  "title": "InstallPluginCommand",
  "type": "object",
  "required": ["plugin_package_path"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "plugin_package_path": { "type": "string" },
    "force": {
      "type": "boolean",
      "default": false,
      "description": "Force install even if incompatible"
    }
  }
}
```

**Validation Rules:**
- Package must pass integrity verification (checksum)
- Package signature must be valid
- SDK version compatibility must be verified
- Plugin manifest must be well-formed

**Error Codes:**

| Code | Description |
|------|-------------|
| `PLUGIN-VAL-001` | Invalid plugin package |
| `PLUGIN-VAL-002` | Plugin manifest malformed |
| `PLUGIN-SEC-001` | Plugin signature verification failed |
| `PLUGIN-SEC-002` | Plugin contains prohibited capabilities |
| `PLUGIN-VER-001` | SDK version incompatible |

---

#### EnablePlugin / DisablePlugin

| Attribute | Detail |
|-----------|--------|
| Purpose | Activate or deactivate an installed plugin |
| Service | Plugin Runtime Service |
| Authorization | Admin role |

**Input Schema:**

```json
{
  "title": "EnablePluginCommand",
  "type": "object",
  "required": ["plugin_id"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "plugin_id": { "type": "string", "format": "uuid" }
  }
}
```

---

### 2.7 Platform Management Commands

#### BackupPlatform

| Attribute | Detail |
|-----------|--------|
| Purpose | Create a complete platform backup |
| Service | Backup Service |
| Authorization | Admin role |

**Input Schema:**

```json
{
  "title": "BackupPlatformCommand",
  "type": "object",
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "backup_name": {
      "type": "string",
      "maxLength": 100,
      "description": "Optional human-readable name"
    },
    "include_plugins": {
      "type": "boolean",
      "default": true
    },
    "include_user_data": {
      "type": "boolean",
      "default": true
    },
    "encryption_key": {
      "type": "string",
      "description": "Optional encryption key for the backup"
    }
  }
}
```

**Output Schema:**

```json
{
  "title": "BackupPlatformResult",
  "type": "object",
  "required": ["backup_id", "created_at", "size_bytes"],
  "properties": {
    "backup_id": { "type": "string", "format": "uuid" },
    "created_at": { "type": "string", "format": "date-time" },
    "size_bytes": { "type": "integer" },
    "checksum": { "type": "string" },
    "path": { "type": "string" }
  }
}
```

---

#### RunDiagnostics

| Attribute | Detail |
|-----------|--------|
| Purpose | Execute comprehensive system diagnostics |
| Service | Diagnostics Service |
| Authorization | Admin role |

**Input Schema:**

```json
{
  "title": "RunDiagnosticsCommand",
  "type": "object",
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "checks": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["database", "filesystem", "plugins", "performance", "security", "integrity"]
      },
      "description": "Specific checks to run; defaults to all"
    }
  }
}
```

---

#### UpdateConfiguration

| Attribute | Detail |
|-----------|--------|
| Purpose | Update platform configuration settings |
| Service | Configuration Service |
| Authorization | Admin role |

**Input Schema:**

```json
{
  "title": "UpdateConfigurationCommand",
  "type": "object",
  "required": ["settings"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "settings": {
      "type": "object",
      "description": "Key-value pairs of settings to update"
    },
    "validate_only": {
      "type": "boolean",
      "default": false,
      "description": "Validate settings without applying"
    }
  }
}
```

---

#### ImportData

| Attribute | Detail |
|-----------|--------|
| Purpose | Import data from a backup or external format |
| Service | Backup Service |
| Authorization | Admin role |

**Input Schema:**

```json
{
  "title": "ImportDataCommand",
  "type": "object",
  "required": ["source_path"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "source_path": { "type": "string" },
    "import_type": {
      "type": "string",
      "enum": ["backup", "courses", "users", "configuration"]
    },
    "decryption_key": { "type": "string" },
    "overwrite_existing": {
      "type": "boolean",
      "default": false
    }
  }
}
```

---

#### ExportData

| Attribute | Detail |
|-----------|--------|
| Purpose | Export platform data in a portable format |
| Service | Backup Service |
| Authorization | Admin role |

**Input Schema:**

```json
{
  "title": "ExportDataCommand",
  "type": "object",
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "export_type": {
      "type": "string",
      "enum": ["full", "courses", "users", "reports", "audit_log"]
    },
    "format": {
      "type": "string",
      "enum": ["json", "csv"],
      "default": "json"
    },
    "encryption_key": { "type": "string" }
  }
}
```

---

### 2.8 Accessibility Commands

#### ManageAccessibilityProfile

| Attribute | Detail |
|-----------|--------|
| Purpose | Create or update user accessibility preferences |
| Service | Accessibility Service |
| Authorization | Own profile or admin |

**Input Schema:**

```json
{
  "title": "ManageAccessibilityProfileCommand",
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "user_id": { "type": "string", "format": "uuid" },
    "screen_reader_enabled": { "type": "boolean" },
    "high_contrast_mode": { "type": "boolean" },
    "reduced_motion": { "type": "boolean" },
    "font_size": {
      "type": "string",
      "enum": ["small", "medium", "large", "extra_large"]
    },
    "keyboard_navigation_enhanced": { "type": "boolean" },
    "color_blind_mode": {
      "type": "string",
      "enum": ["none", "protanopia", "deuteranopia", "tritanopia"]
    },
    "audio_descriptions": { "type": "boolean" },
    "captions_enabled": { "type": "boolean" }
  }
}
```

---

### 2.9 Localization Commands

#### UpdateLocalization

| Attribute | Detail |
|-----------|--------|
| Purpose | Update locale settings or add custom translations |
| Service | Localization Service |
| Authorization | Admin role (system locale) or own profile (user locale) |

**Input Schema:**

```json
{
  "title": "UpdateLocalizationCommand",
  "type": "object",
  "properties": {
    "command_id": { "type": "string", "format": "uuid" },
    "locale": {
      "type": "string",
      "pattern": "^[a-z]{2}(-[A-Z]{2})?$",
      "description": "Target locale (e.g., 'en', 'en-US', 'es')"
    },
    "translations": {
      "type": "object",
      "description": "Key-value translation pairs"
    },
    "set_as_default": {
      "type": "boolean",
      "default": false
    }
  }
}
```

---

## 3. Query Contracts

### 3.1 Standard Query Parameters

All list queries support standard parameters:

```json
{
  "type": "object",
  "properties": {
    "page": {
      "type": "integer",
      "minimum": 1,
      "default": 1
    },
    "page_size": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 20
    },
    "sort": {
      "type": "string",
      "description": "Field name with optional '-' prefix for descending"
    },
    "filter": {
      "type": "object",
      "description": "Field-value filter pairs"
    },
    "search": {
      "type": "string",
      "description": "Full-text search query"
    }
  }
}
```

### 3.2 Standard Pagination Response

```json
{
  "type": "object",
  "required": ["items", "total", "page", "page_size", "has_more"],
  "properties": {
    "items": { "type": "array" },
    "total": { "type": "integer" },
    "page": { "type": "integer" },
    "page_size": { "type": "integer" },
    "has_more": { "type": "boolean" },
    "next_cursor": {
      "type": "string",
      "description": "Cursor for next page (alternative to page number)"
    }
  }
}
```

### 3.3 Query Definitions

#### GetUser

| Attribute | Detail |
|-----------|--------|
| Purpose | Retrieve a specific user's profile |
| Authorization | Own profile or admin |
| Caching | 5-minute TTL |

**Input:** `user_id: UUID`
**Output:** `UserProfile`

---

#### ListUsers

| Attribute | Detail |
|-----------|--------|
| Purpose | List all users with filtering and pagination |
| Authorization | Admin role |
| Caching | 1-minute TTL |

**Filtering:** username, role, status, created_at range
**Sorting:** username, created_at, last_login
**Output:** `PaginatedList[UserSummary]`

---

#### GetCourse

| Attribute | Detail |
|-----------|--------|
| Purpose | Retrieve course details with lessons |
| Authorization | Published courses: any role; drafts: instructor (own) or admin |
| Caching | 5-minute TTL |

**Input:** `course_id: UUID`
**Output:** `CourseDetail` (includes lessons, prerequisites, metadata)

---

#### ListCourses

| Attribute | Detail |
|-----------|--------|
| Purpose | List courses with filtering |
| Authorization | Any authenticated user |
| Caching | 2-minute TTL |

**Filtering:** status, category, difficulty_level, author, tags
**Sorting:** title, created_at, published_at, enrollment_count
**Output:** `PaginatedList[CourseSummary]`

---

#### GetAssessments

| Attribute | Detail |
|-----------|--------|
| Purpose | List assessments for a course or student |
| Authorization | Enrolled students, instructors, admin |
| Caching | 2-minute TTL |

**Filtering:** course_id, student_id, status, date range
**Sorting:** created_at, score, submission_date
**Output:** `PaginatedList[AssessmentResult]`

---

#### GetCertificates

| Attribute | Detail |
|-----------|--------|
| Purpose | Retrieve certificates for a student |
| Authorization | Own certificates or admin |
| Caching | 10-minute TTL |

**Filtering:** student_id, course_id, issued_at range
**Sorting:** issued_at, course_title
**Output:** `PaginatedList[Certificate]`

---

#### GetPlugins

| Attribute | Detail |
|-----------|--------|
| Purpose | List installed plugins with status |
| Authorization | Admin role |
| Caching | 1-minute TTL |

**Filtering:** status (enabled/disabled/error), name, author
**Sorting:** name, installed_at, version
**Output:** `PaginatedList[PluginInfo]`

---

#### GetConfiguration

| Attribute | Detail |
|-----------|--------|
| Purpose | Retrieve current platform configuration |
| Authorization | Admin role |
| Caching | No caching (always fresh) |

**Input:** Optional `category` filter
**Output:** `ConfigurationMap`

---

#### GetAuditLogs

| Attribute | Detail |
|-----------|--------|
| Purpose | Query the audit log for compliance and investigation |
| Authorization | Admin role |
| Caching | No caching |

**Filtering:** event_type, user_id, date range, severity
**Sorting:** timestamp (newest first default)
**Output:** `PaginatedList[AuditEntry]`

---

#### GetReports

| Attribute | Detail |
|-----------|--------|
| Purpose | Retrieve generated reports |
| Authorization | Reports scoped to user permission |
| Caching | 5-minute TTL |

**Filtering:** report_type, date_range, status
**Sorting:** generated_at
**Output:** `PaginatedList[Report]`

---

#### GetAnalytics

| Attribute | Detail |
|-----------|--------|
| Purpose | Retrieve analytics data and dashboards |
| Authorization | Admin or instructor (own courses) |
| Caching | 5-minute TTL |

**Filtering:** metric_type, date_range, course_id, user_id
**Sorting:** date, value
**Output:** `AnalyticsDashboard`

---

#### GetNotifications

| Attribute | Detail |
|-----------|--------|
| Purpose | List user notifications |
| Authorization | Own notifications |
| Caching | No caching |

**Filtering:** read/unread, type, date range
**Sorting:** created_at (newest first)
**Output:** `PaginatedList[Notification]`

---

#### GetDiagnostics

| Attribute | Detail |
|-----------|--------|
| Purpose | Retrieve system diagnostic information |
| Authorization | Admin role |
| Caching | 30-second TTL |

**Input:** Optional `check_type` filter
**Output:** `DiagnosticsReport` (health status, system info, metrics)

---

#### GetBackups

| Attribute | Detail |
|-----------|--------|
| Purpose | List available backups |
| Authorization | Admin role |
| Caching | 1-minute TTL |

**Filtering:** date range, size range, status
**Sorting:** created_at (newest first)
**Output:** `PaginatedList[BackupInfo]`

---

## 4. Command Processing Pipeline

```
1. Receive Command
   ├── Validate command_id format
   ├── Check for duplicate command_id (idempotency)
   └── Parse command payload

2. Validate Input
   ├── Schema validation (JSON Schema)
   ├── Business rule validation
   ├── Authorization check
   └── Rate limit check

3. Execute Business Logic
   ├── Acquire necessary locks
   ├── Perform state mutations
   ├── Generate side effects (events)
   └── Record audit entry

4. Return Result
   ├── Format output per schema
   ├── Include correlation_id
   └── Log completion
```

## 5. Query Processing Pipeline

```
1. Receive Query
   ├── Validate query parameters
   └── Check authorization

2. Check Cache
   ├── Cache hit → Return cached result
   └── Cache miss → Continue

3. Execute Query
   ├── Apply filters
   ├── Apply sorting
   ├── Apply pagination
   └── Format results

4. Cache Result
   ├── Store in cache with TTL
   └── Return to caller
```
