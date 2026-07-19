# AuthShield Lab - Value Object Catalog

## Overview

This document defines all value objects in AuthShield Lab, specifying validation rules, equality semantics, immutability guarantees, and serialization formats for each value object.

---

## Value Object Principles

1. **Immutability:** Value objects cannot be modified after creation
2. **Equality by Value:** Two value objects are equal if all attributes match
3. **No Identity:** Value objects have no surrogate identity
4. **Self-Validating:** Validation occurs at construction time
5. **Replaceable:** Updated value objects are replaced, not modified

---

## Value Object Categories

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Value Object Categories                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │
│  │    Identity      │  │   Education     │  │   Assessment    │           │
│  │    Value Objects │  │   Value Objects │  │   Value Objects │           │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤           │
│  │  - Email        │  │  - CourseCode   │  │  - AssessmentId │           │
│  │  - Username     │  │  - LessonId     │  │  - QuestionId   │           │
│  │  - PasswordHash │  │  - ModuleId     │  │  - AnswerId     │           │
│  │  - PhoneNumber  │  │  - Duration     │  │  - AssessmentScore│         │
│  │  - UserStatus   │  │  - CourseStatus │  │  - GradePoint   │           │
│  └─────────────────┘  └─────────────────┘  │  - CompetencyLevel│          │
│                                             └─────────────────┘           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │
│  │   Session       │  │   Platform      │  │   Security      │           │
│  │   Value Objects │  │   Value Objects │  │   Value Objects │           │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤           │
│  │  - SessionId    │  │  - PluginId     │  │  - SecurityLevel│           │
│  │  - TokenExpiry  │  │  - SemanticVer  │  │  - PermissionLevel│         │
│  │  - RefreshToken │  │  - ConfigKey    │  │  - AccessLevel  │           │
│  │  - DeviceId     │  │  - ConfigValue  │  │  - AuditEntryId │           │
│  │  - SessionStatus│  │  - ConfigType   │  │  - EventType    │           │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘           │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │
│  │    Temporal     │  │  Localization   │  │  Accessibility  │           │
│  │  Value Objects  │  │  Value Objects  │  │  Value Objects  │           │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤           │
│  │  - DateRange    │  │  - LanguageCode │  │  - Accessibility│           │
│  │  - TimeRange    │  │  - Locale       │  │    Preference   │           │
│  │  - DateTime     │  │  - LocalizationKey│ │  - ThemeConfig  │           │
│  │  - Duration     │  │  - TimeZone     │  │  - FontSize     │           │
│  │  - Timestamp    │  │  - Currency     │  │  - ContrastLevel│           │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Identity Value Objects

### 1. Email

**Purpose:** Represents a validated email address with format normalization.

| Attribute | Type | Description |
|-----------|------|-------------|
| address | string | Normalized email address |
| localPart | string | Local part (before @) |
| domain | string | Domain part (after @) |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-EMAIL-001 | Must match RFC 5322 format | INVALID_EMAIL_FORMAT |
| VAL-EMAIL-002 | Max 254 characters | EMAIL_TOO_LONG |
| VAL-EMAIL-003 | Local part max 64 characters | LOCAL_PART_TOO_LONG |
| VAL-EMAIL-004 | Domain must be valid hostname | INVALID_DOMAIN |
| VAL-EMAIL-005 | No consecutive dots | INVALID_FORMAT |
| VAL-EMAIL-006 | Cannot start or end with dot | INVALID_FORMAT |

**Equality Semantics:**
- Case-insensitive comparison
- Leading/trailing whitespace stripped
- Dot-stripping for Gmail addresses (optional)

**Immutability Guarantees:**
- Created via factory method only
- No setter methods
- Hash computed at creation
- Thread-safe for concurrent access

**Serialization Format:**
```json
{
  "type": "Email",
  "address": "user@example.com",
  "localPart": "user",
  "domain": "example.com",
  "normalized": "user@example.com"
}
```

---

### 2. Username

**Purpose:** Represents a unique platform username with format validation.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | string | Normalized username |
| normalized | string | Lowercase version for lookup |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-USER-001 | 3-50 characters | INVALID_USERNAME_LENGTH |
| VAL-USER-002 | Alphanumeric and underscores only | INVALID_USERNAME_CHARS |
| VAL-USER-003 | Cannot start with number | INVALID_USERNAME_START |
| VAL-USER-004 | No consecutive underscores | INVALID_USERNAME_FORMAT |
| VAL-USER-005 | Cannot end with underscore | INVALID_USERNAME_END |
| VAL-USER-006 | Reserved names blocked | RESERVED_USERNAME |

**Equality Semantics:**
- Case-insensitive comparison
- Normalized form (lowercase) used for equality

**Immutability Guarantees:**
- Created via factory method only
- No setter methods
- Normalized form computed at creation

**Serialization Format:**
```json
{
  "type": "Username",
  "value": "john_doe",
  "normalized": "john_doe"
}
```

---

### 3. PasswordHash

**Purpose:** Securely stores hashed password with algorithm metadata.

| Attribute | Type | Description |
|-----------|------|-------------|
| hash | string | Hashed password value |
| algorithm | HashAlgorithm | Hashing algorithm |
| salt | string | Random salt used |
| iterations | int | Work factor |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-PASS-001 | Hash must be non-empty | EMPTY_HASH |
| VAL-PASS-002 | Algorithm must be supported | UNSUPPORTED_ALGORITHM |
| VAL-PASS-003 | Salt must be 16+ bytes | INVALID_SALT |
| VAL-PASS-004 | Iterations must be 10000+ | WEAK_WORK_FACTOR |

**Equality Semantics:**
- Never compared directly (security)
- Verify method for password checking
- Timing-safe comparison

**Immutability Guarantees:**
- Created via hash method only
- Original password never stored
- Hash cannot be reversed

**Serialization Format:**
```json
{
  "type": "PasswordHash",
  "algorithm": "argon2id",
  "hash": "$argon2id$v=19$m=65536,t=3,p=4$salt$hash",
  "iterations": 3,
  "memoryCost": 65536,
  "parallelism": 4
}
```

---

### 4. PhoneNumber

**Purpose:** Represents a validated international phone number.

| Attribute | Type | Description |
|-----------|------|-------------|
| number | string | Full international number |
| countryCode | string | Country calling code |
| nationalNumber | string | National destination number |
| format | PhoneFormat | E.164, national, etc. |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-PHONE-001 | Valid E.164 format | INVALID_PHONE_FORMAT |
| VAL-PHONE-002 | Valid country code | INVALID_COUNTRY_CODE |
| VAL-PHONE-003 | Appropriate length for country | INVALID_PHONE_LENGTH |
| VAL-PHONE-004 | No special characters except + | INVALID_PHONE_CHARS |

**Equality Semantics:**
- E.164 format used for comparison
- Whitespace and formatting stripped

**Immutability Guarantees:**
- Created via factory method only
- Parsed at creation time
- Cannot be modified after creation

**Serialization Format:**
```json
{
  "type": "PhoneNumber",
  "number": "+12025551234",
  "countryCode": "+1",
  "nationalNumber": "2025551234",
  "format": "e164"
}
```

---

### 5. UserStatus

**Purpose:** Represents the lifecycle state of a user account.

| Value | Description |
|-------|-------------|
| pending | Awaiting email verification |
| active | Fully active account |
| suspended | Temporarily disabled |
| locked | Too many failed attempts |
| deleted | Soft-deleted account |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-STATUS-001 | Must be valid enum value | INVALID_STATUS |
| VAL-STATUS-002 | Cannot transition from deleted | INVALID_TRANSITION |

**State Transitions:**
```
pending → active (email verified)
pending → deleted (verification timeout)
active → suspended (admin action)
active → locked (failed attempts)
active → deleted (user request)
suspended → active (admin reinstatement)
suspended → deleted (admin action)
locked → active (admin unlock or timeout)
```

**Serialization Format:**
```json
{
  "type": "UserStatus",
  "value": "active",
  "changedAt": "2024-01-15T10:30:00Z",
  "reason": "Email verified"
}
```

---

## Education Value Objects

### 6. CourseCode

**Purpose:** Human-readable unique course identifier.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | string | Course code (e.g., "SEC-101") |
| prefix | string | Subject prefix |
| number | int | Course number |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-CODE-001 | Format: [A-Z]{2,4}-[0-9]{3,4} | INVALID_CODE_FORMAT |
| VAL-CODE-002 | Prefix must be 2-4 uppercase letters | INVALID_PREFIX |
| VAL-CODE-003 | Number must be 100-9999 | INVALID_NUMBER |

**Equality Semantics:**
- Case-sensitive (uppercase expected)
- Whitespace stripped

**Immutability Guarantees:**
- Created via factory method only
- Parsed at creation time
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "CourseCode",
  "value": "SEC-101",
  "prefix": "SEC",
  "number": 101
}
```

---

### 7. LessonId

**Purpose:** Unique identifier for a lesson within a module.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | UUID | Lesson identifier |
| moduleId | UUID | Parent module reference |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-LID-001 | Valid UUID v4 | INVALID_UUID |
| VAL-LID-002 | moduleId must be valid | INVALID_MODULE |

**Equality Semantics:**
- UUID value equality
- Module context included in comparison

**Immutability Guarantees:**
- Generated at creation time
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "LessonId",
  "value": "550e8400-e29b-41d4-a716-446655440000",
  "moduleId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
}
```

---

### 8. ModuleId

**Purpose:** Unique identifier for a module within a course.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | UUID | Module identifier |
| courseId | UUID | Parent course reference |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-MID-001 | Valid UUID v4 | INVALID_UUID |
| VAL-MID-002 | courseId must be valid | INVALID_COURSE |

**Equality Semantics:**
- UUID value equality
- Course context included in comparison

**Immutability Guarantees:**
- Generated at creation time
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "ModuleId",
  "value": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "courseId": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

---

### 9. Duration

**Purpose:** Represents a time duration with validation.

| Attribute | Type | Description |
|-----------|------|-------------|
| minutes | int | Total minutes |
| hours | int | Hours component |
| display | string | Human-readable format |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-DUR-001 | Must be positive integer | INVALID_DURATION |
| VAL-DUR-002 | Max 480 minutes (8 hours) | DURATION_TOO_LONG |

**Equality Semantics:**
- Based on total minutes
- Normalized to minutes for comparison

**Immutability Guarantees:**
- Created via factory method only
- Computed at creation time
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "Duration",
  "minutes": 90,
  "hours": 1.5,
  "display": "1h 30m"
}
```

---

### 10. CourseStatus

**Purpose:** Represents the publication state of a course.

| Value | Description |
|-------|-------------|
| draft | Not yet published |
| review | Under content review |
| published | Live and accessible |
| archived | No longer maintained |
| deprecated | Scheduled for removal |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-CS-001 | Must be valid enum value | INVALID_STATUS |
| VAL-CS-002 | Published requires min 3 modules | INSUFFICIENT_MODULES |

**State Transitions:**
```
draft → review (submitted for review)
review → draft (returned for revision)
review → published (approved)
published → archived (manual action)
archived → deprecated (automatic or manual)
```

**Serialization Format:**
```json
{
  "type": "CourseStatus",
  "value": "published",
  "changedAt": "2024-01-15T10:30:00Z",
  "changedBy": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Assessment Value Objects

### 11. AssessmentId

**Purpose:** Unique identifier for an assessment.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | UUID | Assessment identifier |
| courseId | UUID | Associated course (optional) |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-AID-001 | Valid UUID v4 | INVALID_UUID |

**Equality Semantics:**
- UUID value equality

**Immutability Guarantees:**
- Generated at creation time
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "AssessmentId",
  "value": "550e8400-e29b-41d4-a716-446655440000",
  "courseId": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

---

### 12. QuestionId

**Purpose:** Unique identifier for a question within an assessment.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | UUID | Question identifier |
| assessmentId | UUID | Parent assessment reference |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-QID-001 | Valid UUID v4 | INVALID_UUID |
| VAL-QID-002 | assessmentId must be valid | INVALID_ASSESSMENT |

**Equality Semantics:**
- UUID value equality

**Immutability Guarantees:**
- Generated at creation time
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "QuestionId",
  "value": "550e8400-e29b-41d4-a716-446655440000",
  "assessmentId": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

---

### 13. AssessmentScore

**Purpose:** Represents a score within an assessment with validation.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | decimal | Score value |
| maxScore | decimal | Maximum possible score |
| percentage | decimal | Calculated percentage |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-SCORE-001 | Value >= 0 | NEGATIVE_SCORE |
| VAL-SCORE-002 | Value <= maxScore | SCORE_EXCEEDS_MAX |
| VAL-SCORE-003 | MaxScore > 0 | INVALID_MAX_SCORE |

**Equality Semantics:**
- Based on value and maxScore
- Percentage used for comparison across assessments

**Immutability Guarantees:**
- Created via factory method only
- Percentage computed at creation
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "AssessmentScore",
  "value": 85,
  "maxScore": 100,
  "percentage": 85.0
}
```

---

### 14. GradePoint

**Purpose:** Represents a grade point for academic records.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | decimal | Grade point (0.0-4.0) |
| letter | LetterGrade | Corresponding letter grade |
| gpa | decimal | GPA equivalent |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-GRADE-001 | Value between 0.0 and 4.0 | INVALID_GRADE_POINT |
| VAL-GRADE-002 | Letter must correspond to value | INVALID_LETTER_GRADE |

**Grade Scale:**
| Point | Letter | Description |
|-------|--------|-------------|
| 4.0 | A | Excellent |
| 3.7 | A- | Very Good |
| 3.3 | B+ | Good Plus |
| 3.0 | B | Good |
| 2.7 | B- | Above Average |
| 2.3 | C+ | Average Plus |
| 2.0 | C | Average |
| 1.7 | C- | Below Average |
| 1.3 | D+ | Poor Plus |
| 1.0 | D | Poor |
| 0.0 | F | Failing |

**Equality Semantics:**
- Based on numeric value
- Letter grade derived

**Immutability Guarantees:**
- Created via factory method only
- Letter grade computed at creation
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "GradePoint",
  "value": 3.7,
  "letter": "A-",
  "gpa": 3.7
}
```

---

### 15. CompetencyLevel

**Purpose:** Represents a level of competency achievement.

| Attribute | Type | Description |
|-----------|------|-------------|
| level | CompetencyLevelEnum | Level classification |
| score | AssessmentScore | Achieved score |
| achievedAt | DateTime | Achievement timestamp |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-COMP-001 | Valid level enum | INVALID_LEVEL |
| VAL-COMP-002 | Score meets level requirements | INSUFFICIENT_SCORE |

**Level Definitions:**
| Level | Score Range | Description |
|-------|-------------|-------------|
| novice | 0-40% | Beginning understanding |
| beginner | 41-60% | Basic competency |
| intermediate | 61-80% | Working knowledge |
| advanced | 81-90% | Proficient application |
| expert | 91-100% | Mastery demonstrated |

**Equality Semantics:**
- Based on level and score
- Achievement timestamp for ordering

**Immutability Guarantees:**
- Created upon achievement
- Cannot be downgraded
- Timestamp fixed at achievement

**Serialization Format:**
```json
{
  "type": "CompetencyLevel",
  "level": "advanced",
  "score": {
    "value": 85,
    "maxScore": 100,
    "percentage": 85.0
  },
  "achievedAt": "2024-01-15T10:30:00Z"
}
```

---

## Session Value Objects

### 16. SessionId

**Purpose:** Unique identifier for a user session.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | UUID | Session identifier |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-SID-001 | Valid UUID v4 | INVALID_UUID |

**Equality Semantics:**
- UUID value equality

**Immutability Guarantees:**
- Generated at session creation
- Cannot be modified
- Cryptographically random

**Serialization Format:**
```json
{
  "type": "SessionId",
  "value": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 17. TokenExpiry

**Purpose:** Represents token expiration time with validation.

| Attribute | Type | Description |
|-----------|------|-------------|
| expiresAt | DateTime | Expiration timestamp |
| issuedAt | DateTime | Issuance timestamp |
| isExpired | boolean | Current expiry status |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-EXP-001 | ExpiresAt must be after issuedAt | INVALID_EXPIRY |
| VAL-EXP-002 | Max lifetime: 30 days | EXCESSIVE_LIFETIME |

**Equality Semantics:**
- Based on expiresAt timestamp
- Current time affects isExpired

**Immutability Guarantees:**
- Set at token creation
- Cannot be extended (new token required)
- isExpired computed dynamically

**Serialization Format:**
```json
{
  "type": "TokenExpiry",
  "expiresAt": "2024-01-16T10:30:00Z",
  "issuedAt": "2024-01-15T10:30:00Z",
  "isExpired": false,
  "remainingSeconds": 86400
}
```

---

### 18. RefreshToken

**Purpose:** Represents a refresh token with metadata.

| Attribute | Type | Description |
|-----------|------|-------------|
| token | string | Token value (hashed) |
| sessionId | UUID | Associated session |
| expiry | TokenExpiry | Expiration information |
| family | string | Token family for rotation |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-RT-001 | Token must be non-empty | EMPTY_TOKEN |
| VAL-RT-002 | SessionId must be valid | INVALID_SESSION |
| VAL-RT-003 | Family must be consistent | TOKEN_FAMILY_MISMATCH |

**Equality Semantics:**
- Based on token hash
- Session context included

**Immutability Guarantees:**
- Generated at creation
- Hash stored, not original
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "RefreshToken",
  "tokenHash": "$2b$10$...",
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "expiry": {
    "expiresAt": "2024-02-15T10:30:00Z"
  },
  "family": "family_abc123"
}
```

---

### 19. DeviceId

**Purpose:** Unique identifier for a client device.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | string | Device fingerprint |
| hash | string | Hashed device ID |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-DID-001 | Value must be non-empty | EMPTY_DEVICE_ID |
| VAL-DID-002 | Max 256 characters | DEVICE_ID_TOO_LONG |

**Equality Semantics:**
- Hash-based comparison
- Fingerprint normalized before hashing

**Immutability Guarantees:**
- Generated from device characteristics
- Hash computed at creation
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "DeviceId",
  "hash": "$2b$10$..."
}
```

---

## Platform Value Objects

### 20. PluginId

**Purpose:** Unique identifier for a plugin.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | UUID | Plugin identifier |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-PID-001 | Valid UUID v4 | INVALID_UUID |

**Equality Semantics:**
- UUID value equality

**Immutability Guarantees:**
- Generated at plugin registration
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "PluginId",
  "value": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 21. SemanticVersion

**Purpose:** Represents a semantic version number.

| Attribute | Type | Description |
|-----------|------|-------------|
| major | int | Major version |
| minor | int | Minor version |
| patch | int | Patch version |
| preRelease | string | Pre-release identifier |
| build | string | Build metadata |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-SEM-001 | Major, minor, patch >= 0 | INVALID_VERSION |
| VAL-SEM-002 | Pre-release follows semver spec | INVALID_PRERELEASE |

**Comparison Rules:**
1. Compare major versions first
2. Then minor versions
3. Then patch versions
4. Pre-release < release
5. Build metadata ignored for precedence

**Equality Semantics:**
- Based on major.minor.patch
- Pre-release considered for equality

**Immutability Guarantees:**
- Parsed at creation time
- Components cannot be modified
- String representation cached

**Serialization Format:**
```json
{
  "type": "SemanticVersion",
  "major": 2,
  "minor": 1,
  "patch": 0,
  "preRelease": "beta.1",
  "build": "build.123",
  "string": "2.1.0-beta.1+build.123"
}
```

---

### 22. ConfigKey

**Purpose:** Represents a configuration key with dot notation.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | string | Configuration key |
| parts | string[] | Parsed key components |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-CK-001 | Dot notation format | INVALID_KEY_FORMAT |
| VAL-CK-002 | Parts alphanumeric and underscore | INVALID_KEY_CHARS |
| VAL-CK-003 | Max 10 parts | KEY_TOO_NESTED |
| VAL-CK-004 | Each part 1-50 characters | INVALID_PART_LENGTH |

**Equality Semantics:**
- Case-sensitive
- Normalized dot notation

**Immutability Guarantees:**
- Parsed at creation time
- Parts array computed
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "ConfigKey",
  "value": "auth.session.timeout",
  "parts": ["auth", "session", "timeout"]
}
```

---

### 23. ConfigValue

**Purpose:** Represents a typed configuration value.

| Attribute | Type | Description |
|-----------|------|-------------|
| value | any | Configuration value |
| type | ConfigType | Value type |
| encrypted | boolean | Encryption flag |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-CV-001 | Value must match type | TYPE_MISMATCH |
| VAL-CV-002 | Secret values must be encrypted | UNENCRYPTED_SECRET |

**Type Mapping:**
| ConfigType | Expected Value Type |
|------------|---------------------|
| string | string |
| number | number (int or float) |
| boolean | boolean |
| json | object or array |
| secret | string (encrypted) |

**Equality Semantics:**
- Type-aware comparison
- Encrypted values compared by ciphertext

**Immutability Guarantees:**
- Created via factory method
- Encryption applied at creation
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "ConfigValue",
  "value": "3600",
  "configType": "number",
  "encrypted": false,
  "parsed": 3600
}
```

---

## Security Value Objects

### 24. SecurityLevel

**Purpose:** Represents security classification level.

| Attribute | Type | Description |
|-----------|------|-------------|
| level | SecurityLevelEnum | Classification level |
| clearance | int | Required clearance |

**Level Definitions:**
| Level | Clearance | Description |
|-------|-----------|-------------|
| public | 0 | Publicly accessible |
| internal | 1 | Internal use only |
| confidential | 2 | Confidential information |
| secret | 3 | Secret classification |
| top_secret | 4 | Top secret classification |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-SEC-001 | Valid level enum | INVALID_LEVEL |
| VAL-SEC-002 | Clearance matches level | CLEARANCE_MISMATCH |

**Equality Semantics:**
- Based on level and clearance
- Used for access control decisions

**Immutability Guarantees:**
- Assigned at creation
- Cannot be downgraded
- Requires authorization to upgrade

**Serialization Format:**
```json
{
  "type": "SecurityLevel",
  "level": "confidential",
  "clearance": 2
}
```

---

### 25. PermissionLevel

**Purpose:** Represents permission level for authorization.

| Attribute | Type | Description |
|-----------|------|-------------|
| level | PermissionLevelEnum | Permission classification |
| scope | string | Permission scope |

**Level Definitions:**
| Level | Description |
|-------|-------------|
| none | No access |
| read | Read-only access |
| write | Read and write access |
| admin | Administrative access |
| superadmin | Super administrator |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-PERM-001 | Valid level enum | INVALID_LEVEL |
| VAL-PERM-002 | Scope must be defined | MISSING_SCOPE |

**Equality Semantics:**
- Based on level and scope
- Hierarchical comparison

**Immutability Guarantees:**
- Assigned via role/permission system
- Requires authorization to change
- Audit logged on change

**Serialization Format:**
```json
{
  "type": "PermissionLevel",
  "level": "write",
  "scope": "courses"
}
```

---

## Temporal Value Objects

### 26. DateRange

**Purpose:** Represents a date range with validation.

| Attribute | Type | Description |
|-----------|------|-------------|
| start | Date | Start date |
| end | Date | End date |
| duration | int | Days in range |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-DR-001 | Start must be before end | INVALID_DATE_RANGE |
| VAL-DR-002 | Duration must be positive | INVALID_DURATION |

**Equality Semantics:**
- Based on start and end dates

**Immutability Guarantees:**
- Created via factory method
- Duration computed at creation
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "DateRange",
  "start": "2024-01-01",
  "end": "2024-01-31",
  "duration": 30
}
```

---

### 27. TimeRange

**Purpose:** Represents a time range within a day.

| Attribute | Type | Description |
|-----------|------|-------------|
| start | Time | Start time |
| end | Time | End time |
| durationMinutes | int | Duration in minutes |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-TR-001 | Start must be before end | INVALID_TIME_RANGE |

**Equality Semantics:**
- Based on start and end times

**Immutability Guarantees:**
- Created via factory method
- Duration computed at creation
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "TimeRange",
  "start": "09:00:00",
  "end": "17:00:00",
  "durationMinutes": 480
}
```

---

### 28. DateTimeRange

**Purpose:** Represents a datetime range for scheduling.

| Attribute | Type | Description |
|-----------|------|-------------|
| start | DateTime | Start timestamp |
| end | DateTime | End timestamp |
| durationMinutes | int | Duration in minutes |
| timezone | string | Timezone reference |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-DTR-001 | Start must be before end | INVALID_DATETIME_RANGE |
| VAL-DTR-002 | Valid timezone | INVALID_TIMEZONE |

**Equality Semantics:**
- Based on start and end timestamps
- Timezone considered for comparison

**Immutability Guarantees:**
- Created via factory method
- Duration computed at creation
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "DateTimeRange",
  "start": "2024-01-15T09:00:00Z",
  "end": "2024-01-15T17:00:00Z",
  "durationMinutes": 480,
  "timezone": "UTC"
}
```

---

## Localization Value Objects

### 29. LanguageCode

**Purpose:** Represents a language code per ISO 639.

| Attribute | Type | Description |
|-----------|------|-------------|
| code | string | ISO 639-1 code |
| region | string | Optional region code |
| full | string | Full BCP 47 tag |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-LANG-001 | Valid ISO 639-1 code | INVALID_LANGUAGE |
| VAL-LANG-002 | Region must be valid ISO 3166 | INVALID_REGION |

**Common Codes:**
| Code | Language |
|------|----------|
| en | English |
| es | Spanish |
| fr | French |
| de | German |
| ja | Japanese |
| zh | Chinese |

**Equality Semantics:**
- Case-insensitive
- Region optional for comparison

**Immutability Guarantees:**
- Parsed at creation time
- Cannot be modified

**Serialization Format:**
```json
{
  "type": "LanguageCode",
  "code": "en",
  "region": "US",
  "full": "en-US"
}
```

---

### 30. LocalePreference

**Purpose:** Represents complete locale settings.

| Attribute | Type | Description |
|-----------|------|-------------|
| language | LanguageCode | Language preference |
| timezone | string | Timezone |
| dateFormat | string | Date format pattern |
| timeFormat | string | Time format (12/24h) |
| numberFormat | NumberFormat | Number formatting |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-LOC-001 | Valid language code | INVALID_LANGUAGE |
| VAL-LOC-002 | Valid timezone | INVALID_TIMEZONE |

**Equality Semantics:**
- Based on all attributes
- Used for personalization

**Immutability Guarantees:**
- Created via user preferences
- Updated via replacement only
- Default provided if not set

**Serialization Format:**
```json
{
  "type": "LocalePreference",
  "language": {"code": "en", "region": "US"},
  "timezone": "America/New_York",
  "dateFormat": "MM/DD/YYYY",
  "timeFormat": "12h",
  "numberFormat": {
    "decimal": ".",
    "thousands": ","
  }
}
```

---

## Accessibility Value Objects

### 31. AccessibilityPreference

**Purpose:** Represents user accessibility settings.

| Attribute | Type | Description |
|-----------|------|-------------|
| screenReader | boolean | Screen reader optimization |
| highContrast | boolean | High contrast mode |
| reducedMotion | boolean | Reduce animations |
| fontSize | FontSize | Text size preference |
| keyboardNav | boolean | Enhanced keyboard navigation |
| captions | boolean | Auto-enable captions |
| altText | boolean | Force alt text display |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-ACC-001 | Valid FontSize enum | INVALID_FONT_SIZE |

**Font Size Options:**
| Size | Scale Factor |
|------|--------------|
| small | 0.875 |
| medium | 1.0 (default) |
| large | 1.125 |
| x-large | 1.25 |

**Equality Semantics:**
- Based on all boolean flags and font size
- Used for UI customization

**Immutability Guarantees:**
- Set via user preferences
- Updated via replacement only
- Defaults provided if not set

**Serialization Format:**
```json
{
  "type": "AccessibilityPreference",
  "screenReader": false,
  "highContrast": false,
  "reducedMotion": true,
  "fontSize": "large",
  "keyboardNav": true,
  "captions": true,
  "altText": false
}
```

---

### 32. ThemeConfig

**Purpose:** Represents UI theme configuration.

| Attribute | Type | Description |
|-----------|------|-------------|
| mode | ThemeMode | Light, dark, system |
| primaryColor | Color | Primary accent color |
| fontFamily | string | Preferred font family |
| borderRadius | int | Border radius in pixels |

**Validation Rules:**
| Rule | Condition | Error |
|------|-----------|-------|
| VAL-THEME-001 | Valid ThemeMode | INVALID_THEME_MODE |
| VAL-THEME-002 | Valid color format | INVALID_COLOR |

**Theme Modes:**
| Mode | Description |
|------|-------------|
| light | Light theme |
| dark | Dark theme |
| system | Follow OS preference |

**Equality Semantics:**
- Based on all theme attributes
- Used for UI personalization

**Immutability Guarantees:**
- Set via user preferences
- Updated via replacement only
- System default provided

**Serialization Format:**
```json
{
  "type": "ThemeConfig",
  "mode": "dark",
  "primaryColor": "#3B82F6",
  "fontFamily": "Inter, sans-serif",
  "borderRadius": 8
}
```

---

## Value Object Factory Methods

Each value object provides static factory methods for creation:

```python
# Identity
Email.create("user@example.com")
Username.create("john_doe")
PasswordHash.hash("password123", algorithm="argon2id")
PhoneNumber.create("+12025551234")

# Education
CourseCode.create("SEC-101")
Duration.create(minutes=90)
CourseStatus.create("published")

# Assessment
AssessmentScore.create(value=85, maxScore=100)
GradePoint.create(3.7)
CompetencyLevel.create("advanced", score)

# Session
SessionId.create()
TokenExpiry.create(hours=24)
RefreshToken.create(sessionId)

# Platform
PluginId.create()
SemanticVersion.create("2.1.0")
ConfigKey.create("auth.session.timeout")
ConfigValue.create(value=3600, type="number")
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2024-01-15 | Initial value object catalog | AuthShield Team |
| 1.1 | 2024-02-20 | Added accessibility and localization | AuthShield Team |
| 1.2 | 2024-03-10 | Refined validation rules | AuthShield Team |
