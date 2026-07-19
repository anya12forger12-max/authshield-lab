# Glossary

> Project-wide glossary for AuthShield Lab. 150+ terms organized alphabetically with
> definitions specific to this platform. Cross-references link related terms.

---

## How to Use This Glossary

- Terms are defined in the context of AuthShield Lab
- *See also* references point to related terms
- Deprecated terms are marked with ~~strikethrough~~ and include their replacement
- Terms are case-insensitive in documentation

---

## A

**Access Decision** — The result of an authorization check, indicating whether a user is permitted to perform an action. *See also: Authorization, Policy.*

**Access Scope** — The boundary within which a permission grant is valid. May be limited to specific resources, resource types, or time windows. *See also: Permission, Scope.*

**Access Token** — A bearer credential representing an authenticated session. Used in the `Authorization` header. *See also: Session, JWT.*

**ACL (Anti-Corruption Layer)** — A translation boundary that prevents external models from leaking into a bounded context. *See also: Bounded Context.*

**Active Session** — A session that has not expired and has not been revoked. *See also: Session, Session Revoked.*

**Adapter** — A component that translates between two interfaces. In Clean Architecture, adapters translate between use cases and external systems. *See also: Gateway, Port.*

**Aggregation** — A database operation that computes a summary value across multiple rows. *See also: Query.*

**Alert** — An automated notification triggered when a monitored metric exceeds a threshold. *See also: Monitoring, Threshold.*

**Alert Severity** — The urgency level of a security alert: info, warning, critical, emergency. *See also: Security Alert.*

**Alert Status** — The lifecycle state of a security alert: open, investigating, resolved, dismissed. *See also: Security Alert.*

**Analytics Dashboard** — A view displaying aggregated learning metrics, engagement data, and performance trends. *See also: Learning Analytics.*

**Angular Bracket** — Deprecated: ~~Angular Bracket~~ — Use **Less-Than / Greater-Than Sign** when discussing characters.

**API (Application Programming Interface)** — The contract defining how clients interact with the server. In AuthShield Lab, RESTful over HTTP. *See also: Endpoint, Route.*

**API Endpoint** — A specific URL path accepting HTTP requests. *See also: API, Route.*

**API Version** — A prefixed segment (e.g., `/api/v1/`) enabling independent evolution of API contracts. *See also: Endpoint.*

**ARIA** — Accessible Rich Internet Applications attributes for enhancing accessibility of dynamic content. *See also: WCAG, Screen Reader.*

**Assessment** — An evaluation testing a learner's knowledge or skill at a module or course level. Contains one or more questions. *See also: Question, Score, Assessment Graded.*

**Assessment Graded** — A domain event fired when an assessment submission is scored. May be auto-graded or manually graded. *See also: Assessment, Score.*

**Assessment Submitted** — A domain event fired when a learner submits answers to an assessment. *See also: Assessment.*

**Attack Scenario** — A simulated offensive technique with defined steps and expected outcomes. Part of a Simulation. *See also: Simulation, Defense Scenario.*

**Attack Type** — A category of offensive technique: brute_force, sql_injection, xss, phishing, credential_stuffing. *See also: Attack Scenario.*

**Audit Log** — An immutable, chronological record of system activity. Each entry captures actor, action, resource, and timestamp. *See also: Audit Service, Compliance.*

**Audit Service** — The domain service responsible for recording, querying, and exporting audit logs. *See also: Audit Log.*

**AuthShield Lab** — The cybersecurity education platform defined by this codebase. Covers authentication, authorization, education, simulation, analytics, and operations.

**Authentication** — The process of verifying a user's identity, typically via email/password, OAuth, or MFA. *See also: Authorization, MFA, Session.*

**Authentication Error** — An error type indicating identity verification failure. Subtypes: InvalidCredentialsError, AccountLockedError, MfaRequiredError, TokenExpiredError. *See also: Authentication.*

**Authentication Middleware** — A middleware component that intercepts requests to validate authentication state before route handlers execute. *See also: Middleware, Authentication.*

**Authentication Provider** — An external identity system (OAuth, LDAP, SAML) that authenticates users. *See also: Authentication, External Identity Provider.*

**Authentication Service** — The domain service orchestrating credential validation, MFA challenges, and session creation. *See also: Authentication.*

**Authorization** — The process of verifying whether an authenticated user has permission to perform a requested action. *See also: Authentication, Permission, RBAC.*

**Authorization Error** — An error type indicating insufficient permissions. Subtypes: InsufficientPermissionsError, RoleNotFoundError. *See also: Authorization.*

**Authorization Service** — The domain service evaluating permissions against policies for a given user-context pair. *See also: Authorization.*

**Auto-Graded** — Assessment scoring performed automatically by the system based on predefined correct answers. *See also: Assessment Graded.*

---

## B

**Base Controller** — An abstract controller class providing shared functionality for all controllers (error handling, serialization). *See also: Controller.*

**Base Service** — An abstract service class providing shared functionality for all services (logging, error wrapping). *See also: Service.*

**Bearer Token** — A credential passed in the `Authorization: Bearer {token}` header. *See also: Access Token, JWT.*

**Bounded Context** — A self-contained domain model with its own entities, value objects, and ubiquitous language. AuthShield Lab has six bounded contexts. *See also: Identity Context, Authorization Context.*

**Brute Force Attack** — An attack technique trying many password combinations. Defended by rate limiting and account lockout. *See also: Attack Type, Rate Limit, Account Lockout.*

**Builder Pattern** — A creational pattern for constructing complex objects step by step. *See also: Factory.*

**Business Logic** — The core rules and processes specific to AuthShield Lab, independent of infrastructure. *See also: Domain Service, Use Case.*

---

## C

**Cache** — A high-speed data store for frequently accessed data. AuthShield Lab uses Redis for session and query caching. *See also: Redis.*

**Cache Key** — A structured string identifying a cached value. Uses the pattern `authshield:{module}:{entity}:{id}`. *See also: Cache.*

**Certificate** — A credential issued upon successful course completion. Contains certificate number, user, course, and issue date. *See also: Certificate Issued, Course Completed.*

**Certificate Issued** — A domain event fired when a certificate is generated for a completed course. *See also: Certificate.*

**Certificate Number** — A unique identifier for a certificate, human-readable and verifiable. *See also: Certificate.*

**Certificate Service** — The domain service responsible for issuing and verifying certificates. *See also: Certificate.*

**Challenge** — See: MFA Challenge.

**Clean Architecture** — An architectural pattern separating concerns into concentric layers: Entities, Use Cases, Interface Adapters, Frameworks. *See also: Hexagonal Architecture.*

**Cohort** — A group of learners sharing common enrollment periods or characteristics. *See also: Cohort Filter.*

**Cohort Filter** — Criteria for grouping learners in analytics reports. *See also: Cohort.*

**Column** — A named field within a database table. *See also: Table, Index.*

**Component** — A reusable, self-contained UI building block. PascalCase named. *See also: View, Page.*

**Compliance** — Adherence to regulatory and organizational security policies. *See also: Compliance Report, Audit Log.*

**Compliance Report** — A document assessing the platform's adherence to compliance requirements. *See also: Compliance.*

**Condition** — A boolean expression within a policy that is evaluated against request context. *See also: Policy, Policy Engine.*

**Conflict Error** — An error type indicating a data uniqueness violation. Subtypes: DuplicateEnrollmentError, SessionConflictError. *See also: Error.*

**Container** — An isolated runtime environment (Docker) hosting a component of the system. *See also: Docker, Orchestration.*

**Content Negotiation** — The process by which client and server agree on response format via `Accept` and `Content-Type` headers. *See also: Representation.*

**Content Type** — The format of lesson content: video, text, interactive, lab, quiz. *See also: Lesson.*

**Controller** — A class responsible for handling HTTP requests and returning responses. *See also: Middleware, Service.*

**Course** — A structured learning path consisting of modules and lessons. *See also: Module, Lesson, Enrollment.*

**Course Completed** — A domain event fired when a learner completes all modules and assessments in a course. *See also: Course.*

**Course Created** — A domain event fired when a new course is authored. *See also: Course.*

**Course Definition** — An aggregate root encompassing a course, its modules, and lessons. *See also: Course, Module.*

**Course Management Service** — The domain service handling course CRUD and publishing workflow. *See also: Course.*

**Course Published** — A domain event fired when a course becomes available in the catalog. *See also: Course.*

**Course Slug** — A URL-safe, lowercase, hyphenated identifier for a course. *See also: Course.*

**CRUD** — Create, Read, Update, Delete. The four basic data operations. *See also: Repository.*

**CSRF** — Cross-Site Request Forgery. An attack tricking authenticated users into performing unwanted actions. *See also: Security.*

**Cursor Pagination** — Pagination using a pointer to the next result set, avoiding offset drift. *See also: Pagination.*

---

## D

**Dashboard** — The main authenticated view showing user-specific information (enrollments, progress, alerts). *See also: Page.*

**Data Feed** — A one-way flow of events from one bounded context to another. *See also: Context Map.*

**Database** — The persistent data store. AuthShield Lab uses PostgreSQL. *See also: Table, Migration.*

**Database Connection Error** — An infrastructure error indicating the application cannot reach the database. *See also: Infrastructure Error.*

**Defense Scenario** — A simulated defensive exercise with defined actions and success criteria. *See also: Simulation, Attack Scenario.*

**Defense Type** — A category of defensive technique: firewall_config, log_analysis, incident_response, forensics. *See also: Defense Scenario.*

**Difficulty Level** — The complexity rating of a course or simulation: beginner, intermediate, advanced, expert. *See also: Course, Simulation.*

**Domain Event** — A record of something meaningful that happened in the domain. Past-tense PascalCase naming. *See also: Event-Driven Architecture.*

**Domain Service** — A stateless service encapsulating business logic that doesn't belong to a single entity. *See also: Entity, Value Object.*

**Docker** — A container platform for packaging and running applications. *See also: Container, Image.*

**Domain Model** — The set of entities, value objects, and business rules representing the problem space. *See also: Bounded Context.*

**Duplicate Enrollment Error** — A conflict error raised when a user attempts to enroll in a course they're already enrolled in. *See also: Conflict Error, Enrollment.*

---

## E

**E2E Test** — An end-to-end test simulating complete user workflows through the full stack. *See also: Integration Test.*

**Email** — A validated value object representing a user's email address. Ensures RFC-compliant format. *See also: Value Object.*

**Email Format Error** — A validation error raised when an email address doesn't match the required format. *See also: ValidationError.*

**Encryption** — Transforming data to prevent unauthorized reading. Used for data at rest and in transit. *See also: Hashing, Cryptography.*

**Endpoint** — A specific URL path where an API can be accessed. Uses kebab-case, plural nouns, versioned prefix. *See also: Route, API.*

**Engagement Metric** — Data measuring how actively a learner interacts with content. *See also: Learning Analytics, Engagement Threshold Met.*

**Engagement Threshold Met** — A domain event fired when a learner reaches an engagement milestone. *See also: Engagement Metric.*

**Enrollment** — A user's registration and participation in a course. One enrollment per user per course. *See also: Course, Enrollment Created.*

**Enrollment Created** — A domain event fired when a user enrolls in a course. *See also: Enrollment.*

**Enrollment Service** — The domain service handling enrollment creation, cancellation, and prerequisite checks. *See also: Enrollment.*

**Entity** — A domain object with a unique identity that persists over time. In DDD, entities are distinguished by identity, not attributes. *See also: Value Object, Aggregate Root.*

**Error** — A typed exception representing a failure condition. Named PascalCase with `Error` suffix. *See also: Authentication Error, ValidationError.*

**Event Bus** — A mechanism for publishing and subscribing to domain events within a process. *See also: Event Handler, Publisher.*

**Event Handler** — A function or class that responds to a domain event by executing side effects. *See also: Event Bus, Subscriber.*

**External Identity Provider** — A third-party system (OAuth, LDAP, SAML) that authenticates users on behalf of AuthShield Lab. *See also: Authentication Provider.*

---

## F

**Factory** — A creational pattern encapsulating object creation logic. *See also: Builder.*

**Fixture** — Pre-defined data or state used in tests to ensure reproducibility. *See also: Mock, Test.*

**Focus** — The currently active interactive element in the UI, reachable via keyboard navigation. *See also: Focus Trap, Keyboard Navigation.*

**Focus Trap** — Restriction of keyboard focus within a component (e.g., modal) to prevent navigation outside it. *See also: Focus.*

**Foreign Key** — A column referencing a primary key in another table, establishing a relationship. *See also: Primary Key, Join.*

---

## G

**Gateway** — An adapter interfacing with an external system. Examples: SmtpGateway, SsoGateway. *See also: Adapter.*

**Grade** — Deprecated: ~~Grade~~ — Use **Score** for assessment results. AuthShield Lab uses numerical scores, not letter grades.

---

## H

**Hashing** — A one-way transformation of data (passwords) for secure storage. Distinct from encryption (reversible). *See also: Password Hash, Salt.*

**Health Check** — A periodic test verifying a component's operational status. *See also: System Health.*

**Health Monitor** — The domain service performing periodic health checks and aggregating status. *See also: Health Check.*

**Hexagonal Architecture** — An architectural pattern isolating core logic from infrastructure via ports and adapters. Same as Clean Architecture. *See also: Clean Architecture.*

---

## I

**Idempotency** — The property that performing an operation multiple times yields the same result as performing it once. *See also: API.*

**Image** — A template for creating Docker containers. Contains the application code and dependencies. *See also: Container.*

**Incident** — A confirmed security event requiring human response. *See also: Security Alert, Incident Response.*

**Incident Response** — An aggregate root in the Operations context managing security alerts through their lifecycle. *See also: Security Alert.*

**Index** — A database data structure that speeds up queries on specific columns. Named `idx_{table}_{column}`. *See also: Table, Query.*

**Infrastructure Error** — An error type indicating failure of external infrastructure. Subtypes: DatabaseConnectionError, CacheConnectionError, ExternalServiceError. *See also: Error.*

**Instructor** — A person who creates or delivers educational content in AuthShield Lab. *See also: Learner.*

**Invalid Credentials Error** — An authentication error raised when submitted credentials don't match stored records. *See also: Authentication Error.*

**IP Address** — A value object representing a client's network address. Supports v4 and v6. *See also: Value Object.*

---

## J

**JWT (JSON Web Token)** — A signed token containing claims about an authenticated user. Used for stateless session management. *See also: Access Token, Token Service.*

**JWT Expiry** — The time at which a JWT is no longer valid. Checked during token validation. *See also: JWT.*

---

## K

**Keyboard Navigation** — Controlling the entire interface using only the keyboard (Tab, Enter, Escape, Arrow keys). *See also: Accessibility, Focus.*

---

## L

**Lab** — A hands-on practical exercise where learners interact with simulated systems. *See also: Simulation.*

**Landmark** — A major page region identifiable by assistive technology via semantic HTML or ARIA roles. *See also: ARIA, Screen Reader.*

**Learner** — A person actively studying within AuthShield Lab. The preferred term over "student" or "user" in educational contexts. *See also: Enrollment, Progress.*

**Learning Analytics** — Aggregated data about learner behavior, performance, and engagement. *See also: Analytics Dashboard, Performance Report.*

**Learning Objective** — A specific skill or knowledge a learner will gain from a lesson or course. *See also: Competency.*

**Learning Streak** — A count of consecutive days a learner has been active. *See also: Engagement Metric.*

**Lesson** — An individual instructional unit within a module. Types: video, text, interactive, lab, quiz. *See also: Module, Content Type.*

**Lesson Completed** — A domain event fired when a learner finishes a lesson. *See also: Lesson.*

**Lockout** — Temporary restriction of an account after exceeding maximum failed login attempts. *See also: Account Locked Error.*

---

## M

**Mapper** — A component translating between object representations (e.g., database row to domain entity). *See also: Serialization.*

**Maximum Concurrent Sessions** — The limit on how many active sessions a single user may have simultaneously. *See also: Session Pool.*

**Metadata** — Additional contextual data attached to a domain event or audit log entry. *See also: Audit Log, Domain Event.*

**Metric** — A measurable value indicating system or learning performance. *See also: Learning Analytics, Simulation Metrics.*

**MFA (Multi-Factor Authentication)** — Authentication requiring more than one verification method. *See also: TOTP, MFA Challenge.*

**MFA Challenge** — An outstanding verification request requiring the user to provide an MFA code. *See also: MFA, Totp Code.*

**MFA Challenge Failed** — A domain event fired when a user submits an incorrect MFA code. *See also: MFA Challenge.*

**MFA Challenge Issued** — A domain event fired when an MFA prompt is sent to the user. *See also: MFA Challenge.*

**MFA Challenge Verified** — A domain event fired when a user correctly completes an MFA challenge. *See also: MFA Challenge.*

**Middleware** — A component that intercepts and processes HTTP requests before or after route handlers. *See also: Authentication Middleware, Rate Limit Middleware.*

**Migration** — A versioned database schema change. Sequentially numbered. *See also: Schema, Database.*

**Mock** — A test double that simulates a dependency and can verify interactions. *See also: Stub, Fixture.*

**Module** — A focused subdivision of a course covering one subtopic. Contains lessons and assessments. *See also: Course, Lesson.*

---

## N

**NotFoundError** — A resource error raised when a requested entity doesn't exist. Subtypes: UserNotFoundError, CourseNotFoundError. *See also: Error.*

---

## O

**OAuth** — An open standard for token-based authentication and authorization. Used as an external identity provider. *See also: External Identity Provider.*

**Operations Context** — The bounded context handling audit, compliance, alerts, and deployment. *See also: Audit Log, Security Alert.*

**Orchestration** — Coordinating multiple containers or services. AuthShield Lab uses Kubernetes. *See also: Container, Kubernetes.*

---

## P

**Paginate** — Dividing a large result set into manageable pages. Supports offset and cursor strategies. *See also: Pagination.*

**Page** — A top-level route with its own URL in the UI. PascalCase component files. *See also: View, Component.*

**Password Complexity Error** — A validation error raised when a password doesn't meet minimum requirements. *See also: ValidationError.*

**Password Hash** — A securely hashed password with algorithm metadata. Uses Argon2id. *See also: Hashing, Salt.*

**Password Hashing Algorithm** — The algorithm used to hash passwords. Default: Argon2id. *See also: Password Hash.*

**Password Reset Completed** — A domain event fired when a user successfully resets their password. *See also: Password Reset Requested.*

**Password Reset Requested** — A domain event fired when a user initiates a password reset. Includes a time-limited reset token. *See also: Password Reset Completed.*

**Password Rotation** — Periodic requirement to change passwords. Configurable interval. *See also: Password Service.*

**Password Service** — The domain service handling hashing, complexity validation, and rotation. *See also: Password Hash.*

**Pattern** — A reusable solution to a common design problem. AuthShield Lab uses Repository, Factory, Builder, Strategy, Observer, Mediator. *See also: Repository Pattern.*

**Performance Report** — A formatted summary of learning outcomes for a user or cohort. *See also: Learning Analytics.*

**Performance Test** — A test measuring system performance under load (latency, throughput). *See also: Load Test.*

**Permission** — A specific allowed action on a resource. Assigned to roles. *See also: Role, RBAC.*

**Permission Denied** — A domain event fired when an authorization check fails. *See also: Authorization Error.*

**Policy** — A rule evaluating conditions to grant or deny access. Has a name, conditions, effect (allow/deny), and priority. *See also: Policy Engine.*

**Policy Condition** — A boolean expression evaluated against request context. Contains field, operator, and value. *See also: Policy.*

**Policy Created** — A domain event fired when a new policy is defined. *See also: Policy.*

**Policy Deactivated** — A domain event fired when a policy is disabled. *See also: Policy.*

**Policy Engine** — The domain service interpreting and evaluating policy conditions. *See also: Policy.*

**Policy Set** — An aggregate root encompassing policies and their evaluation logic. *See also: Policy.*

**Policy Updated** — A domain event fired when a policy's conditions or metadata change. *See also: Policy.*

**Policy Violation Detected** — A domain event fired when a security policy is violated. *See also: Policy, Security Alert.*

**Port** — In Clean Architecture, an interface defining how the core interacts with external systems. *See also: Adapter, Gateway.*

**Primary Key** — A unique identifier for each database row. In AuthShield Lab, UUIDs. *See also: Foreign Key, Table.*

**Privilege** — The ability to perform a protected operation. *See also: Permission, Role.*

**Privilege Escalation Attempt** — A domain event fired when a suspicious permission grant is detected. *See also: Security Alert.*

**Progress** — Tracking of a learner's completion status for lessons, modules, and courses. *See also: Learner Progress.*

**Progress Tracking Service** — The domain service recording and retrieving learner progress. *See also: Progress.*

**Prerequisite** — A requirement (course, skill, score) that must be met before enrollment or access. *See also: Enrollment Service.*

**Publisher** — A component that emits domain events to an event bus. *See also: Event Bus, Subscriber.*

---

## Q

**Query** — A database read operation retrieving data based on conditions. *See also: Repository.*

**Question** — A single item within an assessment. Types: multiple_choice, fill_in, code_review. *See also: Assessment.*

---

## R

**Rate Limit** — A constraint on request frequency per client. Prevents abuse and ensures fair usage. *See also: Rate Limit Error.*

**Rate Limit Error** — An error raised when a client exceeds the allowed request frequency. *See also: Rate Limit.*

**Rate Limit Middleware** — Middleware that enforces rate limiting by tracking request counts per client. *See also: Middleware, Rate Limit.*

**RBAC (Role-Based Access Control)** — Authorization via role assignments. Users inherit permissions through their roles. *See also: ABAC, Role.*

**Redis** — An in-memory data store used for caching and session management. *See also: Cache.*

**Registration** — Deprecated: ~~Registration~~ — Use **Enrollment** for course sign-up. Use **User Registered** for account creation.

**Representation** — The serialized form of a resource in an API response (JSON, XML). *See also: Serialization.*

**Repository** — A data access abstraction encapsulating persistence logic. One repository per aggregate. *See also: Repository Pattern, Aggregate Root.*

**Repository Pattern** — A design pattern isolating domain logic from data access. *See also: Repository.*

**Resource** — In API context, a domain entity exposed via HTTP. In authorization context, an object being protected. *See also: API Resource, Resource Action.*

**Resource Action** — A value object pairing a resource with an action (e.g., `course:create`). Used in permission definitions. *See also: Permission.*

**ResourceType Error** — Deprecated: ~~ResourceType Error~~ — Use **NotFoundError** with specific subtypes.

**Response** — An outgoing HTTP message from the server to the client. *See also: Request.*

**Response Format** — The standardized structure of API responses: `{ data, meta, errors }`. *See also: API.*

**Result** — Deprecated: ~~Result~~ — Use **Score** for assessment results, **Simulation Result** for simulation outcomes.

**Retry** — The attempt to re-execute a failed operation. Configurable with exponential backoff. *See also: Circuit Breaker.*

**Role** — A named collection of permissions. Users are assigned roles to inherit permissions. *See also: Permission, RBAC.*

**Role Assigned** — A domain event fired when a role is granted to a user. *See also: Role.*

**Role Created** — A domain event fired when a new role is defined. *See also: Role.*

**Role Definition** — An aggregate root encompassing roles and their permissions. *See also: Role.*

**Role Management Service** — The domain service handling role CRUD and assignment. *See also: Role.*

**Role Revoked** — A domain event fired when a role is removed from a user. *See also: Role.*

**Rollback** — Reverting a deployment to a previous version. *See also: Deployment.*

**Route** — A URL pattern mapped to a handler function on the server side. *See also: Endpoint.*

---

## S

**Salt** — Random data added to a password before hashing to prevent rainbow table attacks. Unique per password. *See also: Password Hash, Hashing.*

**Schema** — The database structure definition (tables, columns, constraints). Also used for data validation objects. *See also: Database, Migration.*

**Screen Reader** — Software that reads page content aloud for visually impaired users. *See also: ARIA, WCAG.*

**Score** — A numerical result on an assessment (0-100%). *See also: Assessment Graded.*

**Security Alert** — A detected anomaly or potential security incident requiring investigation. *See also: Alert, Alert Severity.*

**Security Test** — A test verifying security properties (injection, access control, etc.). *See also: Vulnerability.*

**Service** — A class encapsulating business logic. Stateless. Orchestrates operations across entities. *See also: Domain Service.*

**Session** — An authenticated connection with a finite lifetime. Contains a token, user reference, and expiry. *See also: Session Created, Session Expired.*

**Session Created** — A domain event fired upon successful login. *See also: Session.*

**Session Expired** — A domain event fired when a session token reaches its TTL. *See also: Session.*

**Session Pool** — An aggregate root managing a user's active sessions and enforcing concurrency limits. *See also: Session.*

**Session Revoked** — A domain event fired when a session is explicitly terminated (logout). *See also: Session.*

**Session Service** — The domain service handling token generation, validation, renewal, and revocation. *See also: Session.*

**Session Token** — A value object representing an opaque authentication credential. Contains value and expiry. *See also: JWT, Access Token.*

**Simulation** — A controlled cybersecurity exercise. May be attack, defense, or hybrid type. *See also: Attack Scenario, Defense Scenario.*

**Simulation Completed** — A domain event fired when a learner finishes a simulation attempt. *See also: Simulation.*

**Simulation Metrics** — Value object containing performance measurements: time_to_detect, time_to_respond, accuracy, coverage. *See also: Simulation.*

**Simulation Orchestrator** — The domain service managing simulation lifecycle, step sequencing, and timeouts. *See also: Simulation.*

**Simulation Result** — The outcome of a simulation attempt. Contains score, metrics, and feedback. *See also: Simulation.*

**Simulation Session** — A learner's individual attempt at a simulation. Tracks status and timing. *See also: Simulation.*

**Simulation Started** — A domain event fired when a learner begins a simulation attempt. *See also: Simulation.*

**Simulation Type** — The category of simulation: attack, defense, hybrid. *See also: Simulation.*

**Slug** — A URL-safe, lowercase, hyphenated string identifier. *See also: Course Slug.*

**Smoke Test** — A minimal test verifying basic system functionality after deployment. *See also: E2E Test.*

**Spy** — Deprecated: ~~Spy~~ — Use **Mock** when the test double needs to verify interactions.

**Strategy Pattern** — A behavioral pattern that defines a family of algorithms and selects one at runtime. *See also: Observer Pattern.*

**Stub** — A test double returning fixed values without verifying interactions. *See also: Mock.*

**Subscriber** — A component that listens for and reacts to domain events. *See also: Publisher, Event Handler.*

**System Health** — The operational status of system components, including uptime, latency, and error rates. *See also: Health Check.*

---

## T

**Table** — A collection of related rows in the relational database. Named in singular snake_case. *See also: Column, Row.*

**Tab Order** — The sequence elements receive focus when navigating with the Tab key. Should match visual layout. *See also: Keyboard Navigation.*

**Test** — A verification of expected behavior. Named with `test_` prefix in Python. *See also: Test Suite, Assertion.*

**Test Case** — A specific scenario with inputs, actions, and expected outcomes. *See also: Test.*

**Test Suite** — A collection of related tests. *See also: Test.*

**Threshold** — A configured value that, when exceeded, triggers an alert. *See also: Alert, Monitoring.*

**Time Limit** — A duration constraint on an assessment or simulation. Contains minutes and strictness flag. *See also: Assessment.*

**Time Period** — A value object defining a reporting window with start_date, end_date, and granularity. *See also: Analytics Dashboard.*

**Time to Detect** — A simulation metric measuring how quickly a learner identifies a simulated threat. *See also: Simulation Metrics.*

**Time to Respond** — A simulation metric measuring how quickly a learner takes effective action. *See also: Simulation Metrics.*

**Token** — An opaque credential representing an authenticated session or authorization grant. *See also: Access Token, JWT.*

**Token Expired Error** — An authentication error raised when a token has passed its expiry time. *See also: Authentication Error, JWT.*

**Token Service** — The domain service handling JWT creation, parsing, refresh, and blacklisting. *See also: JWT.*

**TOTP (Time-based One-Time Password)** — An MFA method generating time-sensitive codes from a shared secret. *See also: MFA, MFA Challenge.*

**Totp Code** — A value object representing a time-based one-time password with its validity window. *See also: TOTP.*

**Transaction** — A group of database operations executed atomically. All succeed or all fail. *See also: Database.*

**Two-Factor Authentication** — Deprecated: ~~Two-Factor Authentication~~ — Use **MFA** (Multi-Factor Authentication) as it may involve more than two factors.

---

## U

**Ubiquitous Language** — A shared vocabulary between developers and domain experts, used consistently in code, docs, and conversation. *See also: Bounded Context.*

**Unique Constraint** — A database constraint preventing duplicate values in a column or set of columns. *See also: Index.*

**Unit Test** — A test verifying a single function or class in isolation. *See also: Integration Test.*

**Use Case** — In Clean Architecture, a business operation defined as a single action the system performs for a user. *See also: Clean Architecture, Domain Service.*

**User** — A registered person with a unique identity. In educational contexts, prefer "Learner". *See also: Learner, User Account.*

**User Account** — An aggregate root encompassing user identity, credentials, and profile. *See also: User, Credential.*

**User Activated** — A domain event fired when an admin enables a user account. *See also: User.*

**User Created** — Deprecated: ~~User Created~~ — Use **User Registered** for new account creation.

**User Created (Event)** — Deprecated: ~~User Created~~ — Use **UserRegistered** as the canonical event name.

**User Deactivated** — A domain event fired when an admin disables a user account. *See also: User.*

**User Registered** — A domain event fired when a new user account is created. *See also: User.*

---

## V

**Validation Error** — An error type indicating invalid input data. Subtypes: EmailFormatError, PasswordComplexityError. *See also: Error.*

**Value Object** — A domain object defined by its attributes rather than identity. Immutable. Equality by value. *See also: Entity.*

**Vulnerability** — A simulated security weakness identified during an attack exercise. Has a severity level. *See also: Attack Scenario, Severity Level.*

**Vulnerability Discovered** — A domain event fired when a learner identifies a simulated vulnerability. *See also: Vulnerability.*

---

## W

**WCAG (Web Content Accessibility Guidelines)** — International standards for web accessibility. AuthShield Lab targets WCAG 2.1 AA. *See also: ARIA, Accessibility.*

---

## X

**XSS (Cross-Site Scripting)** — An attack injecting malicious scripts into web pages. Defended by input sanitization and CSP. *See also: Security, Attack Type.*

---

## Deprecated Terms

| Deprecated Term | Replacement | Reason |
|---|---|---|
| ~~User Created (event)~~ | `UserRegistered` | Past-tense verb is more descriptive |
| ~~Two-Factor Authentication~~ | `MFA` | MFA covers more than two factors |
| ~~Grade~~ | `Score` | AuthShield Lab uses numerical scores |
| ~~Student~~ | `Learner` | More accurate for self-paced online education |
| ~~Class (course)~~ | `Course` | Avoids confusion with programming classes |
| ~~Widget~~ | `Component` | Modern UI terminology |
| ~~Snackbar~~ | `Toast` | Consistent with UI terminology standards |
| ~~UserCreated~~ | `UserRegistered` | More specific event name |
| ~~Result (assessment)~~ | `Score` | More precise terminology |
| ~~Spy~~ | `Mock` | Unified test double terminology |

---

*Last updated: 2025-01-15*
*Owner: AuthShield Lab Engineering*
