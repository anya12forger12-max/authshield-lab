# Architectural Vocabulary

> Canonical definitions for architectural terms used in AuthShield Lab. This document
> covers Clean Architecture, Domain-Driven Design, Event-Driven Architecture, design
> patterns, and infrastructure terminology.

---

## Table of Contents

1. [Clean Architecture Layers](#clean-architecture-layers)
2. [Domain-Driven Design (DDD) Terms](#domain-driven-design-ddd-terms)
3. [Event-Driven Architecture Terms](#event-driven-architecture-terms)
4. [Design Pattern Terminology](#design-pattern-terminology)
5. [Infrastructure Terminology](#infrastructure-terminology)

---

## Clean Architecture Layers

AuthShield Lab follows Clean Architecture (also known as Hexagonal or Onion Architecture) to isolate core business logic from external concerns.

### Layer Diagram

```
┌─────────────────────────────────────────────────┐
│               Frameworks & Drivers              │
│   (Web framework, Database driver, Cache, etc.) │
├─────────────────────────────────────────────────┤
│             Interface Adapters                   │
│   (Controllers, Repositories, Gateways, Mappers)│
├─────────────────────────────────────────────────┤
│                 Use Cases                        │
│   (Application services, DTOs, Input/Output)    │
├─────────────────────────────────────────────────┤
│                 Entities                         │
│   (Domain models, Value Objects, Domain Events) │
└─────────────────────────────────────────────────┘
```

### Entities Layer (Innermost)

The innermost layer containing the core business objects and rules. Has no dependencies on any other layer.

| Term | Definition | AuthShield Lab Example |
|---|---|---|
| **Entity** | A business object with identity and lifecycle | `User`, `Course`, `Session`, `Assessment` |
| **Value Object** | An immutable object defined by attributes, not identity | `Email`, `PasswordHash`, `Score`, `IpAddress` |
| **Domain Event** | A record of something meaningful that happened | `UserRegistered`, `SessionExpired`, `CourseCompleted` |
| **Domain Service** | Business logic that doesn't belong to a single entity | `AuthenticationService`, `PolicyEngine` |
| **Aggregate** | A cluster of entities treated as a single unit for data changes | `UserAccount`, `CourseDefinition`, `SessionPool` |
| **Aggregate Root** | The top-level entity of an aggregate, enforcing invariants | `User` (in `UserAccount`), `Course` (in `CourseDefinition`) |

**Rules:**
- Contains zero imports from outer layers
- Defines interfaces (ports) that outer layers implement
- All business rules are expressed here

### Use Cases Layer

Orchestrates application-specific business rules. Coordinates entities and domain services to fulfill specific user interactions.

| Term | Definition | AuthShield Lab Example |
|---|---|---|
| **Use Case** | A single application operation triggered by a user action | `LoginUser`, `EnrollInCourse`, `SubmitAssessment` |
| **Input Port** | An interface defining what the use case requires | `LoginInput`, `EnrollmentInput` |
| **Output Port** | An interface defining what the use case produces | `LoginOutput`, `EnrollmentOutput` |
| **DTO (Data Transfer Object)** | A plain object carrying data between layers | `LoginRequest`, `CourseResponse`, `UserDto` |
| **Presenter** | A component formatting use case output for display | `CourseListPresenter`, `DashboardPresenter` |
| **Boundary** | The interface between use cases and adapters | `AuthenticationBoundary`, `CourseBoundary` |

**Rules:**
- Imports only from the Entities layer
- Each use case is a single class with a single `execute()` method
- Uses dependency inversion: depends on interfaces from the Entities layer

### Interface Adapters Layer

Converts data between the use case layer and external formats (HTTP, database, cache).

| Term | Definition | AuthShield Lab Example |
|---|---|---|
| **Controller** | Handles HTTP requests and delegates to use cases | `AuthController`, `UserController`, `CourseController` |
| **Repository** | Implements data access defined by domain interfaces | `UserRepositoryImpl`, `SessionRepositoryImpl` |
| **Gateway** | Implements external system integration | `SmtpGateway`, `SsoGateway`, `PaymentGateway` |
| **Adapter** | Translates between two interface formats | `JwtAdapter`, `LdapAdapter`, `CacheAdapter` |
| **Mapper** | Transforms objects between layers | `UserMapper`, `CourseMapper`, `AuditLogMapper` |
| **Schema** | Validates and serializes request/response data | `LoginRequestSchema`, `UserCreateSchema` |
| **Presenter** | Formats output for the specific delivery mechanism | `JsonPresenter`, `HtmlPresenter` |

**Rules:**
- Imports from Use Cases and Entities layers
- Implements interfaces defined in inner layers
- Contains no business logic (only translation/validation)

### Frameworks & Drivers Layer (Outermost)

The outermost layer containing frameworks, databases, UI, and external tools.

| Term | Definition | AuthShield Lab Example |
|---|---|---|
| **Framework** | An external library providing infrastructure | FastAPI, SQLAlchemy, Redis, Celery |
| **Driver** | Software enabling communication with infrastructure | PostgreSQL driver, Redis client |
| **Middleware** | A component intercepting requests in the framework pipeline | `AuthenticationMiddleware`, `RateLimitMiddleware` |
| **Configuration** | External settings injected into the application | `DatabaseConfiguration`, `SecurityConfiguration` |
| **Server** | The process hosting the application | Uvicorn, Gunicorn |

**Rules:**
- Imports from all inner layers
- Contains framework-specific code (decorators, annotations, etc.)
- Wires everything together (dependency injection)

### Dependency Rule

> Dependencies must point inward. Outer layers may depend on inner layers, but inner
> layers must never depend on outer layers.

```
Framework → Adapters → Use Cases → Entities

❌ Entities → Use Cases
❌ Use Cases → Adapters
❌ Adapters → Framework
```

---

## Domain-Driven Design (DDD) Terms

### Core Building Blocks

| Term | Definition | Key Characteristics |
|---|---|---|
| **Entity** | An object defined by its identity, not its attributes | Has a unique ID; mutable; equality by identity |
| **Value Object** | An object defined entirely by its attributes | Immutable; no ID; equality by value; self-validating |
| **Aggregate** | A cluster of entities and value objects forming a consistency boundary | One aggregate root; transactions within; references by ID across |
| **Aggregate Root** | The top-level entity of an aggregate | External code only accesses aggregate through the root; enforces invariants |
| **Domain Event** | A record of something meaningful that happened in the domain | Past-tense naming; immutable; carries event data |
| **Domain Service** | Stateless business logic spanning multiple entities | No identity; operates on entities and value objects |

### Strategic Design

| Term | Definition | AuthShield Lab Application |
|---|---|---|
| **Bounded Context** | A self-contained domain model with its own language and boundaries | Identity, Authorization, Education, Simulation, Analytics, Operations |
| **Ubiquitous Language** | A shared vocabulary between developers and domain experts | Defined per bounded context in Domain Taxonomy |
| **Context Map** | A visual and textual representation of relationships between bounded contexts | Identity → Authorization (upstream-downstream), etc. |
| **Anti-Corruption Layer (ACL)** | A translation boundary protecting one context from another's model | Identity ACL translating external IdP tokens |
| **Core Domain** | The most strategically important part of the system | Education and Simulation (differentiating features) |
| **Supporting Domain** | A domain that supports the core domain but isn't differentiating | Analytics (supports learning outcomes) |
| **Generic Domain** | A domain that could be purchased or used off-the-shelf | Operations (audit, logging) |

### Tactical Patterns

| Term | Definition | Implementation |
|---|---|---|
| **Repository** | An abstraction over data access, presented as a collection | One repository per aggregate root |
| **Factory** | An object encapsulating creation logic for complex entities | `TokenFactory`, `CourseFactory` |
| **Specification** | A business rule encapsulated as a predicate object | `ActiveUserSpecification`, `PublishedCourseSpecification` |
| **Domain Service** | Stateless logic that doesn't belong to any entity | `AuthorizationService`, `CertificateService` |
| **Application Service** | Orchestrates use cases; doesn't contain business logic itself | `LoginUseCase`, `EnrollmentUseCase` |

### Aggregate Invariants

| Aggregate | Invariants |
|---|---|
| `UserAccount` | Must have at least one credential; email must be unique; deactivation cascades to sessions |
| `CourseDefinition` | Must have at least one module; title must be unique; slug must be unique |
| `SessionPool` | Max concurrent sessions per user enforced; expired sessions cleaned up |
| `AssessmentDefinition` | Must have at least one question; passing_score 0-100; max_attempts >= 1 |
| `EnrollmentRecord` | One enrollment per user per course; cannot enroll in unpublished course |

---

## Event-Driven Architecture Terms

### Core Concepts

| Term | Definition | AuthShield Lab Usage |
|---|---|---|
| **Domain Event** | A record of something meaningful that happened in the business domain | `UserRegistered`, `SessionExpired`, `CourseCompleted` |
| **Integration Event** | An event published to communicate across bounded contexts | Events consumed by Analytics and Operations |
| **Event Bus** | An in-process mechanism for publishing and subscribing to events | Used within bounded contexts for local event handling |
| **Event Store** | A persistent log of all domain events (event sourcing) | Audit logs serve as a de facto event store |
| **Event Handler** | A function or class that reacts to an event by executing side effects | `OnUserRegistered: send_welcome_email()` |
| **Publisher** | A component that emits events to the bus | `UserRepository.save()` publishes `UserRegistered` |
| **Subscriber** | A component that listens for and processes events | `EmailService` subscribes to `UserRegistered` |

### Event Lifecycle

```
1. Entity emits domain event
2. Event published to Event Bus
3. Subscribers receive event
4. Side effects executed (email, analytics, audit)
5. Event persisted to Event Store (optional)
```

### Event Characteristics

| Characteristic | Requirement | Example |
|---|---|---|
| **Immutability** | Events are never modified after creation | `UserRegistered` data never changes |
| **Past Tense** | Events describe something that already happened | `SessionCreated` not `CreateSession` |
| **Self Containing** | Events carry all data needed by handlers | Includes `user_id`, `email`, `timestamp` |
| **Idempotent Handling** | Handlers must handle duplicate events gracefully | Check if action already performed |
| **Ordered within Context** | Events within a bounded context maintain order | Sequence numbers or timestamps |

### Event Naming Convention

All domain events use **past-tense verbs** in PascalCase:

```python
# Identity Events
UserRegistered
UserActivated
UserDeactivated
PasswordChanged
PasswordResetRequested
PasswordResetCompleted
SessionCreated
SessionExpired
SessionRevoked
MfaChallengeIssued
MfaChallengeVerified
MfaChallengeFailed

# Authorization Events
RoleCreated
RoleAssigned
RoleRevoked
PermissionGranted
PermissionRevoked
PolicyCreated
PolicyUpdated
PolicyDeactivated
AccessDenied
PrivilegeEscalationAttempt

# Education Events
CourseCreated
CoursePublished
CourseUnpublished
CourseUpdated
LessonCreated
LessonCompleted
AssessmentSubmitted
AssessmentGraded
ModuleCompleted
CourseCompleted
EnrollmentCreated
EnrollmentCancelled
CertificateIssued

# Simulation Events
SimulationCreated
SimulationActivated
SimulationStarted
SimulationStepCompleted
SimulationCompleted
SimulationTimedOut
VulnerabilityDiscovered
DefenseSuccessCriteriaMet

# Analytics Events
AnalyticsRecorded
ReportGenerated
CompetencyAchieved
EngagementThresholdMet
LearningStreakRecorded

# Operations Events
AuditLogCreated
ComplianceReportGenerated
SecurityAlertTriggered
SecurityAlertAcknowledged
SecurityAlertResolved
DeploymentStarted
DeploymentCompleted
DeploymentRolledBack
HealthCheckFailed
```

### Event Payload Structure

```python
@dataclass(frozen=True)
class DomainEvent:
    event_id: str           # UUID
    event_type: str         # e.g., "UserRegistered"
    occurred_at: datetime   # UTC timestamp
    aggregate_id: str       # ID of the aggregate root
    aggregate_type: str     # e.g., "UserAccount"
    version: int            # Event schema version
    data: dict              # Event-specific payload
```

---

## Design Pattern Terminology

### Creational Patterns

| Pattern | Definition | AuthShield Lab Usage |
|---|---|---|
| **Factory** | Encapsulates object creation logic, returning products of a known interface | `TokenFactory` creates JWTs; `CourseFactory` builds Course entities |
| **Builder** | Constructs complex objects step by step, allowing various representations | `QueryBuilder` builds SQL queries; `ReportBuilder` assembles reports |
| **Singleton** | Ensures a class has only one instance with global access | `ConfigProvider` (use sparingly; prefer dependency injection) |
| **Prototype** | Creates new objects by copying an existing instance | `SimulationScenario.clone()` for creating variations |

### Structural Patterns

| Pattern | Definition | AuthShield Lab Usage |
|---|---|---|
| **Adapter** | Converts the interface of one class into another interface clients expect | `JwtAdapter` wraps PyJWT for internal use |
| **Facade** | Provides a simplified interface to a complex subsystem | `AuthenticationFacade` simplifies auth operations for controllers |
| **Proxy** | Provides a placeholder for another object to control access | `CacheProxy` wraps repository with caching layer |
| **Decorator** | Adds behavior to an object dynamically | `@rate_limited`, `@cached`, `@logged` decorators |

### Behavioral Patterns

| Pattern | Definition | AuthShield Lab Usage |
|---|---|---|
| **Strategy** | Defines a family of algorithms and selects one at runtime | `PasswordHashingStrategy` (Argon2id, bcrypt) |
| **Observer** | Defines a one-to-many dependency so that when one object changes, dependents are notified | Domain event system implements Observer |
| **Mediator** | Defines an object that encapsulates how a set of objects interact | `SimulationOrchestrator` mediates between simulation components |
| **Chain of Responsibility** | Passes a request along a chain of handlers until one handles it | Authentication middleware chain: Rate Limit → Auth → Authorization |
| **Command** | Encapsulates a request as an object, enabling queuing and undo | LoginCommand, EnrollmentCommand |
| **Template Method** | Defines the skeleton of an algorithm, deferring specific steps to subclasses | `BaseService.process()` template with hook methods |
| **State** | Allows an object to alter its behavior when its internal state changes | `SimulationSession` states: pending, active, completed, timed_out |

---

## Infrastructure Terminology

### Request Processing

| Term | Definition | AuthShield Lab Usage |
|---|---|---|
| **Middleware** | A component intercepting requests before/after handlers | `AuthenticationMiddleware`, `RateLimitMiddleware`, `LoggingMiddleware` |
| **Pipeline** | The ordered sequence of middleware processing a request | Request → CORS → RateLimit → Auth → Handler → Response |
| **Handler** | A function processing a specific route | `login_handler`, `create_course_handler` |
| **Request Context** | The accumulated state during request processing | User info, permissions, timing data |
| **Response Formatter** | Middleware or utility converting internal data to HTTP response | `JsonResponseFormatter`, `ErrorResponseFormatter` |

### Caching

| Term | Definition | AuthShield Lab Usage |
|---|---|---|
| **Cache** | A high-speed data store for frequently accessed data | Redis for session and query caching |
| **Cache Key** | A structured identifier for cached values | `authshield:session:{token}`, `authshield:user:{id}` |
| **Cache TTL** | Time-to-live; how long a cached value persists | Session cache: 30 min; Query cache: 5 min |
| **Cache Invalidation** | Removing or refreshing cached data when source changes | Invalidate user cache on profile update |
| **Cache Stampede** | Many requests simultaneously computing the same uncached value | Prevented via locks or early expiration |

### Message Queues

| Term | Definition | AuthShield Lab Usage |
|---|---|---|
| **Queue** | A FIFO data structure for asynchronous message processing | Celery task queue for background jobs |
| **Producer** | A component that sends messages to a queue | Auth service enqueues email sends |
| **Consumer** | A component that reads and processes messages from a queue | Email worker processes send_email tasks |
| **Dead Letter Queue** | A queue for messages that couldn't be processed | Failed email sends go to DLQ for retry |
| **Retry** | Attempting to reprocess a failed message | Exponential backoff: 1min, 5min, 30min, 2hr |
| **Circuit Breaker** | A pattern preventing cascading failures by stopping calls to failing services | Circuit breaker on external email provider |

### Database

| Term | Definition | AuthShield Lab Usage |
|---|---|---|
| **Connection Pool** | A reusable set of database connections | Min: 5, Max: 20 connections per service |
| **Migration** | A versioned schema change script | Sequential numbered scripts (001, 002, ...) |
| **Transaction** | An atomic group of database operations | User creation: insert user + credential in one transaction |
| **Optimistic Locking** | Preventing conflicts by checking version before update | Course update checks `updated_at` hasn't changed |
| **Pessimistic Locking** | Preventing conflicts by locking rows during transaction | Session creation locks user row to check concurrent limit |
| **Read Replica** | A database copy optimized for read queries | Analytics queries against read replica |
| **Sharding** | Horizontal data partitioning across database instances | Not currently used; documented for future scaling |

### Authentication Infrastructure

| Term | Definition | AuthShield Lab Usage |
|---|---|---|
| **JWT (JSON Web Token)** | A signed token with claims, used for stateless authentication | Access tokens in Authorization header |
| **Refresh Token** | A long-lived token used to obtain new access tokens | Stored in httpOnly cookie; rotated on use |
| **OAuth 2.0** | An authorization framework for delegated access | Google, GitHub as external identity providers |
| **SAML** | An XML-based standard for exchanging authentication data | Enterprise SSO integration |
| **LDAP** | A protocol for accessing distributed directory services | Corporate directory authentication |
| **Password Hashing** | One-way transformation of passwords for secure storage | Argon2id with per-user salt |
| **Token Blacklist** | A set of revoked tokens checked during validation | Revoked tokens stored in Redis with TTL |

### Monitoring & Observability

| Term | Definition | AuthShield Lab Usage |
|---|---|---|
| **Structured Logging** | Logs in a machine-parseable format (JSON) | Every log entry includes timestamp, level, event, context |
| **Distributed Tracing** | Tracking requests across service boundaries | X-Request-ID header propagated across services |
| **Span** | A single unit of work within a trace | `auth.authentication.validate_credentials` |
| **Metric** | A numeric measurement collected over time | `authshield_login_attempts_total`, `authshield_request_duration_seconds` |
| **Dashboard** | A visual display of key metrics and alerts | Grafana dashboards for auth, education, and system health |
| **Alert Rule** | A condition that triggers a notification when true | Error rate > 5% for 5 minutes → page on-call |
| **SLA** | Service Level Agreement defining expected performance | 99.9% uptime; p95 latency < 200ms |

### Deployment

| Term | Definition | AuthShield Lab Usage |
|---|---|---|
| **Container** | An isolated, reproducible runtime environment | Docker containers for all services |
| **Image** | A template for creating containers | `authshield/api:1.2.3` |
| **Orchestration** | Automated container management, scaling, and networking | Kubernetes cluster |
| **Deployment** | The process of releasing a new version | Blue-green deployment with health checks |
| **Rollback** | Reverting to a previous deployment version | Automated rollback on health check failure |
| **Canary Deployment** | Releasing to a small percentage of users before full rollout | 5% traffic to new version for 10 minutes |
| **Blue-Green Deployment** | Running two identical environments, switching traffic | Blue = current, Green = new version |
| **Feature Flag** | A toggle enabling/disabling features without deployment | `ENABLE_MFA_TOTP` flag for gradual rollout |

---

## Summary: Key Relationships

```
Clean Architecture          DDD                  Event-Driven
─────────────────          ───                  ─────────────
Entities           ←→  Domain Model        ←→  Domain Events
Use Cases          ←→  Application Service ←→  Event Handlers
Interface Adapters ←→  Repositories        ←→  Event Bus
Frameworks         ←→  Infrastructure      ←→  Event Store
```

```
Patterns               Infrastructure
────────               ──────────────
Factory           →    Object Creation
Strategy          →    Algorithm Selection
Observer          →    Event Publishing
Mediator          →    Orchestration
Adapter           →    Interface Translation
Builder           →    Complex Construction
Repository        →    Data Access Abstraction
Chain of Resp.    →    Middleware Pipeline
```

---

*Last updated: 2025-01-15*
*Owner: AuthShield Lab Engineering*
