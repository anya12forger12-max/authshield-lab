# Data Flow Detailed — AuthShield Lab

> Version: 1.0  
> Last Updated: 2026-07-19  
> Status: Current

---

## 1. Overview

This document traces every major data flow through AuthShield Lab from user action to persistence and back. Each flow includes an ASCII diagram and textual description.

---

## 2. User Action → Presentation → Application → Domain → Persistence → Response

This is the canonical request-response flow for any user-initiated operation.

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│              │    │              │    │              │    │              │    │              │
│   RENDERER   │───▶│ IPC BRIDGE   │───▶│  FASTAPI     │───▶│   DOMAIN     │───▶│  PERSISTENCE │
│   (React)    │    │ (Preload)    │    │  (Router)    │    │   SERVICE    │    │  (SQLAlchemy) │
│              │    │              │    │              │    │              │    │              │
└──────┬───────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
       │                                                                                │
       │  1. User clicks button                                                         │
       │  2. React calls IPC invoke                                                     │
       │  3. Preload serializes + sends                                                 │
       │  4. FastAPI receives request                                                   │
       │  5. Auth middleware validates token                                            │
       │  6. Command/Query dispatched                                                   │
       │  7. Handler executes business logic                                            │
       │  8. Repository persists changes                                                │
       │  9. Domain events published                                                    │
       │  10. Response serialized                                                       │
       │                                                                                │
       ◀───────────────────── Response flows back through same path ─────────────────────┘
```

**Step-by-step:**
1. **Renderer**: User interacts with React component (button click, form submit)
2. **Zustand Store**: Store action dispatched, local state updated optimistically
3. **IPC Call**: `window.api.invoke('module.action', payload)` serializes request
4. **Preload Bridge**: ContextBridge validates channel name, forwards to main process
5. **FastAPI Router**: Route matched, request validated (Pydantic), auth middleware checks token
6. **Application Layer**: Command/Query handler instantiated via dependency injection
7. **Domain Layer**: Business logic executed, invariants validated, events collected
8. **Persistence Layer**: Repository methods called, SQLAlchemy async session executes queries
9. **Response**: `Result<T, E>` converted to HTTP response, serialized to JSON
10. **IPC Return**: Response sent back through preload bridge
11. **Renderer**: Zustand store updated, React re-renders affected components

---

## 3. Authentication Flow (Login)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  LOGIN   │────▶│  IPC     │────▶│  AUTH    │────▶│  USER    │────▶│  TOKEN   │────▶│  DB      │
│  FORM    │     │  BRIDGE  │     │  SERVICE │     │  REPO    │     │  SERVICE │     │  WRITE   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                                              │                  │                  │
     │ 1. Email + password submitted                │                  │                  │
     │                                              │                  │                  │
     │              ┌──────────┐     ┌──────────┐   │                  │                  │
     │              │  AUDIT   │◀────│  EVENT   │◀──┼──────────────────┼──────────────────┘
     │              │  LOG     │     │  BUS     │   │
     │              └──────────┘     └──────────┘   │
     │                    │                         │
     │                    ▼                         │
     │              ┌──────────┐     ┌──────────┐   │
     │              │ SESSION  │◀────│SESSION   │◀──┘
     │              │ CREATED  │     │ SERVICE  │
     │              └──────────┘     └──────────┘
     │                    │
     ▼                    ▼
┌──────────┐     ┌──────────┐
│  UI      │     │  TOKEN   │
│  UPDATE  │     │  STORED  │
│  (Home)  │     │  (Cookie)│
└──────────┘     └──────────┘
```

**Detailed Steps:**
1. **User** enters email and password in login form
2. **Renderer** validates input client-side (format, length)
3. **IPC** sends `AuthCommand.Login` with credentials
4. **Auth Service** receives command, calls credential store
5. **User Repository** queries user by email (encrypted column)
6. **Password Service** verifies using argon2id hash comparison
7. **If MFA required**: Returns MFA challenge, user submits TOTP code
8. **Token Service** generates JWT access + refresh tokens
9. **Session Service** creates session record with IP, user agent, timestamp
10. **Event Bus** publishes `UserLoggedIn` event
11. **Audit Module** logs successful authentication
12. **Analytics Module** records login metric
13. **Response** sent to renderer with tokens + user info
14. **Renderer** stores tokens securely, updates Zustand auth store
15. **Navigation** redirected to dashboard

**Security Events:**
- `AuthenticationFailed` — logged after 3 failures
- `AccountLocked` — after 5 consecutive failures (15-min lockout)
- `MFACreated` — when user enables MFA

---

## 4. Authorization Flow (Permission Check)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ REQUEST  │────▶│  AUTH    │────▶│  RBAC    │────▶│  POLICY  │
│ (any)    │     │  MIDDLE- │     │  ENGINE  │     │  ENGINE  │
└──────────┘     │  WARE    │     └──────────┘     └──────────┘
                 └────┬─────┘          │                  │
                      │                │                  │
                      │         ┌──────▼──────┐   ┌──────▼──────┐
                      │         │  ROLE       │   │  POLICY     │
                      │         │  REPOSITORY │   │  REPOSITORY │
                      │         └─────────────┘   └─────────────┘
                      │
                      ▼
                 ┌──────────┐     ┌──────────┐
                 │  DENY    │     │  ALLOW   │
                 │  (403)   │     │  (next)  │
                 └──────────┘     └──────────┘
```

**Detailed Steps:**
1. **FastAPI Middleware** extracts JWT token from request header
2. **Token Service** validates token signature and expiry
3. **User ID** extracted from token claims
4. **RBAC Engine** loads user's roles from database
5. **Role Repository** returns role → permission mappings
6. **Permission Set** computed: union of all role permissions
7. **Policy Engine** evaluates resource-specific policies
8. **Policy Evaluation**: Context (user, resource, action) → Allow/Deny
9. **If Allow**: Request proceeds to handler
10. **If Deny**: 403 Forbidden response with error details

**Permission Model:**
```
User → has many → Roles
Role → has many → Permissions
Permission → format: "{module}:{action}"
Example: "users:create", "courses:delete", "audit:read"
```

---

## 5. Course Loading Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ NAVIGATE │────▶│  IPC     │────▶│  QUERY   │────▶│  COURSE  │
│ TO COURSE│     │  CALL    │     │  HANDLER │     │  REPO    │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
                                                        ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  REACT   │◀────│  DTO     │◀────│  DOMAIN  │◀────│  SQLITE  │
│  RENDER  │     │  MAP     │     │  BUILD   │     │  QUERY  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

**Detailed Steps:**
1. **User** navigates to course detail page
2. **React Component** mounts, triggers `useCourse(courseId)` hook
3. **Zustand Store** dispatches fetch action
4. **IPC** sends `Query.GetCourse` with course ID
5. **Query Handler** receives request, calls course repository
6. **Repository** executes SQL: `SELECT * FROM courses WHERE id = ?`
7. **Domain Build**: Raw data mapped to `CourseAggregate` entity
8. **Aggregate** loads child entities (modules, lessons) via repository
9. **DTO Mapping**: Domain entities converted to `CourseDTO`
10. **Response** sent via IPC to renderer
11. **Zustand Store** updated with course data
12. **React** re-renders course detail view

---

## 6. Assessment Execution Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  START   │────▶│  CREATE  │────▶│  LOAD    │────▶│  RENDER  │
│  ASSESS  │     │ ATTEMPT  │     │ QUESTIONS│     │ QUESTION │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
     ┌──────────┐     ┌──────────┐     ┌──────────┐     │
     │  RESULT  │◀────│  GRADE   │◀────│  SUBMIT  │◀────┘
     │  DISPLAY │     │  ENGINE  │     │  ANSWERS │
     └────┬─────┘     └──────────┘     └──────────┘
          │
          ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  EVENT   │────▶│  PROGRESS│────▶│  ANALYTICS│───▶│  AUDIT   │
│  BUS     │     │  UPDATE  │     │  RECORD  │     │  LOG     │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

**Detailed Steps:**
1. **User** clicks "Start Assessment"
2. **Application** creates `AssessmentAttempt` entity
3. **Repository** persists attempt record (status: in_progress)
4. **Content** module loads questions for this assessment
5. **Renderer** displays first question
6. **User** answers each question, answers stored locally
7. **User** clicks "Submit"
8. **IPC** sends `Command.SubmitAssessment` with answers
9. **Grading Engine** evaluates answers against correct answers
10. **Score** computed (percentage, pass/fail, per-question breakdown)
11. **Attempt** record updated with score
12. **Event** `AssessmentCompleted` published
13. **LMS Module** updates course progress
14. **Analytics Module** records assessment metrics
15. **Audit Module** logs assessment completion
16. **Results** returned to renderer
17. **Renderer** displays results with detailed feedback

---

## 7. Analytics Generation Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  TIMER   │────▶│  AGGREG- │────▶│  QUERY   │────▶│  COMPUTE │
│  TRIGGER │     │  ATION   │     │  RAW DATA│     │  METRICS │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
┌──────────┐     ┌──────────┐     ┌──────────┐         │
│  DASH-   │◀────│  CACHE   │◀────│  STORE   │◀────────┘
│  BOARD   │     │  UPDATE  │     │  RESULT  │
└──────────┘     └──────────┘     └──────────┘
```

**Detailed Steps:**
1. **Scheduler** triggers analytics aggregation every 5 minutes
2. **Analytics Worker** queries raw event data from audit logs
3. **Aggregation** computes: login counts, session durations, assessment scores
4. **Trend Analysis** compares current period to previous periods
5. **Anomaly Detection** flags unusual patterns
6. **Results** stored in `analytics_cache` table
7. **Dashboard** component polls for fresh data via query
8. **Cache** serves pre-computed results for fast rendering
9. **Charts** rendered with trend lines and anomaly highlights

**Computed Metrics:**
| Metric | Calculation | Period |
|---|---|---|
| Daily Active Users | COUNT(DISTINCT user_id) | 24h |
| Average Session Duration | AVG(session_end - session_start) | 7d |
| Assessment Pass Rate | COUNT(passed) / COUNT(total) | 30d |
| Content Engagement | SUM(time_spent) / COUNT(views) | 7d |
| Security Incident Rate | COUNT(security_events) / COUNT(sessions) | 24h |

---

## 8. Reporting Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  REQUEST │────▶│  SELECT  │────▶│  QUERY   │────▶│  AGGREGATE│
│  REPORT  │     │  TYPE    │     │  DATA    │     │  RESULTS │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
                                                        ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  FILE    │◀────│  FORMAT  │◀────│  BUILD   │◀────│  ENRICH  │
│  OUTPUT  │     │  SELECT  │     │  REPORT  │     │  DATA    │
└────┬─────┘     └──────────┘     └──────────┘     └──────────┘
     │
     ▼
┌──────────┐
│  NOTIFY  │
│  USER    │
└──────────┘
```

**Detailed Steps:**
1. **User** requests report (type, date range, filters)
2. **Application** validates report parameters
3. **Domain** determines data requirements for report type
4. **Persistence** executes optimized queries for report data
5. **Aggregation** computes summary statistics
6. **Enrichment** adds context (user names, course titles)
7. **Report Builder** assembles report structure
8. **Formatter** converts to requested format (PDF/CSV/JSON/HTML)
9. **File System** writes output file to exports directory
10. **IPC** notifies user with file path
11. **Renderer** shows download notification

---

## 9. Plugin Communication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  PLUGIN  │────▶│  SDK     │────▶│  MESSAGE │────▶│  VALIDATOR│
│  CODE    │     │  INTERFACE│    │  QUEUE   │     │  (Sandbox)│
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
     ┌──────────┐     ┌──────────┐     ┌──────────┐     │
     │  PLUGIN  │◀────│  SDK     │◀────│  CORE    │◀────┘
     │  RECEIVES│     │  RESPONSE│     │  HANDLER │
     │  RESPONSE│     │  SERIAL  │     │          │
     └──────────┘     └──────────┘     └──────────┘
```

**Detailed Steps:**
1. **Plugin** calls SDK method (e.g., `sdk.events.publish("my.event", data)`)
2. **SDK Interface** creates `PluginMessage` with plugin ID and timestamp
3. **Message Queue** buffers message (max 10 concurrent per plugin)
4. **Validator** checks message size, rate limits, permissions
5. **Sandbox Boundary** crossed — message enters core system
6. **Core Handler** processes message (event published, data returned, etc.)
7. **Response** serialized back through SDK interface
8. **Plugin** receives response (or error if timeout/restriction)

**Plugin Message Limits:**
| Limit | Value | Enforcement |
|---|---|---|
| Max message size | 1 MB | Pre-validation |
| Messages per second | 100 | Token bucket |
| Concurrent messages | 10 | Semaphore |
| Message timeout | 100ms | asyncio.wait_for |
| Max recursion depth | 3 | Counter tracking |

---

## 10. Logging Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  ANY     │────▶│  STRUCT- │────▶│  LOG     │────▶│  SINK    │
│  MODULE  │     │  LOG     │     │  BUFFER  │     │  ROUTER  │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
                            ┌────────────────────────────┼────────────────────────┐
                            │                            │                        │
                            ▼                            ▼                        ▼
                    ┌──────────┐               ┌──────────┐              ┌──────────┐
                    │  FILE    │               │  CONSOLE │              │  AUDIT   │
                    │  SINK    │               │  SINK    │              │  SINK    │
                    │  (JSON)  │               │  (Human) │              │  (DB)    │
                    └──────────┘               └──────────┘              └──────────┘
```

**Detailed Steps:**
1. **Module** calls `logger.info("event_name", key=value, ...)` via structlog
2. **Structlog** adds context (timestamp, level, module, request_id)
3. **Processor pipeline** enriches event (add user_id, sanitize PII)
4. **Log Buffer** holds events in memory (flush every 1s or 100 events)
5. **Sink Router** routes to configured sinks based on level and type
6. **File Sink** writes JSON line to daily rotating log file
7. **Console Sink** writes human-readable format (development only)
8. **Audit Sink** writes security-relevant events to database
9. **Log Rotation** compresses yesterday's log files

**Log Levels:**
| Level | Usage | Output |
|---|---|---|
| `DEBUG` | Detailed diagnostic info | Console only |
| `INFO` | Normal operations | File + Console |
| `WARNING` | Unexpected but handled | File + Console |
| `ERROR` | Operation failed | File + Console + Audit |
| `CRITICAL` | System-level failure | File + Console + Audit + Alert |

---

## 11. Backup Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  TRIGGER │────▶│  PRE-    │────▶│  SQLITE  │────▶│  VERIFY  │
│  (Timer/ │     │  BACKUP  │     │  BACKUP  │     │  CHECK-  │
│  Manual) │     │  CHECK   │     │  API     │     │  SUM     │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
┌──────────┐     ┌──────────┐     ┌──────────┐         │
│  CLEANUP │◀────│  ROTATE  │◀────│  STORE   │◀────────┘
│  OLD     │     │  OLD     │     │  METADATA│
│  BACKUPS │     │  BACKUPS │     │          │
└──────────┘     └──────────┘     └──────────┘
```

**Detailed Steps:**
1. **Scheduler** triggers backup at configured time (default: 02:00 daily)
2. **Pre-backup check** verifies disk space, database integrity
3. **SQLite Backup API** performs online backup (non-blocking)
4. **WAL checkpoint** performed before backup for consistency
5. **Checksum** (SHA-256) computed for backup file
6. **Metadata** stored in database: size, checksum, timestamp, schema version
7. **Rotation** removes old backups beyond retention count
8. **Cleanup** compresses old backups, removes expired archives
9. **Event** `BackupCompleted` published to event bus
10. **Audit** log entry created for backup event

**Backup Metadata:**
```json
{
  "backup_id": "bak_01J2ABCDEF",
  "timestamp": "2026-07-19T02:00:00Z",
  "type": "automated",
  "schema_version": 42,
  "size_bytes": 52428800,
  "checksum_sha256": "a1b2c3d4...",
  "encrypted": false,
  "duration_ms": 3200,
  "tables": {
    "users": 15,
    "courses": 8,
    "sessions": 142,
    "audit_logs": 12847
  }
}
```

---

## 12. Export/Import Flow

### 12.1 Export Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  SELECT  │────▶│  QUERY   │────▶│  MAP TO  │────▶│  FORMAT  │
│  EXPORT  │     │  DATA    │     │  OUTPUT  │     │  (JSON/  │
│  SCOPE   │     │          │     │  SCHEMA  │     │  CSV/PDF)│
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
                                                        ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  NOTIFY  │◀────│  VERIFY  │◀────│  ENCRYPT │◀────│  WRITE   │
│  USER    │     │  FILE    │     │  (opt.)  │     │  FILE    │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

**Export Formats:**
| Format | Use Case | Includes |
|---|---|---|
| JSON | Full data export | All entities, relationships |
| CSV | Spreadsheet analysis | Flat tables, one entity type |
| PDF | Printable reports | Formatted report with charts |
| HTML | Web viewable | Interactive report |

### 12.2 Import Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  SELECT  │────▶│  READ    │────▶│  VALIDATE│────▶│  DRY RUN │
│  IMPORT  │     │  FILE    │     │  SCHEMA  │     │  (check) │
│  FILE    │     │          │     │          │     │          │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                        │
     ┌──────────┐     ┌──────────┐     ┌──────────┐     │
     │  CONFIRM │◀────│  IMPORT  │◀────│  MERGE   │◀────┘
     │  RESULT  │     │  WRITE   │     │  STRATEGY│
     └──────────┘     └──────────┘     └──────────┘
```

**Import Strategies:**
| Strategy | Behavior | Use Case |
|---|---|---|
| `Replace` | Overwrite existing data | Fresh restore from backup |
| `Merge` | Update existing, create new | Data consolidation |
| `Skip` | Skip duplicates | Safe import, no overwrites |
| `Ask` | Prompt for each conflict | Interactive import |

---

## 13. Cross-Module Event Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     EVENT FLOW EXAMPLES                          │
│                                                                 │
│  UserLoggedIn:                                                 │
│    auth → event_bus → [sessions.create, audit.log, analytics.record]
│                                                                 │
│  CourseCompleted:                                              │
│    lms → event_bus → [analytics.record, certification.check,    │
│                       learning.update, audit.log]               │
│                                                                 │
│  PolicyViolation:                                              │
│    policies → event_bus → [defense.alert, audit.log,            │
│                            analytics.record, notification.send] │
│                                                                 │
│  PluginInstalled:                                              │
│    ecosystem → event_bus → [sdk.notify, audit.log,              │
│                             testing.run_compat]                 │
└─────────────────────────────────────────────────────────────────┘
```

**Event Chain Example — User Login:**
```
1. auth module: LoginCommand handled successfully
2. auth module: publishes UserLoggedIn event
3. event_bus: routes to all subscribers of "auth.user.logged_in"
4. sessions module: creates new Session record
5. audit module: creates AuditEntry with login details
6. analytics module: increments daily active user count
7. defense module: checks rate limit, records successful auth
8. learning module: updates user's last active timestamp
9. All handlers complete (some may fail independently)
10. Response returned to user with auth token
```
