# Terminology Standards

> Canonical definitions for terminology used across AuthShield Lab. Consistent terminology
> prevents confusion and ensures every team communicates with a shared vocabulary.

---

## Table of Contents

1. [API Terminology](#api-terminology)
2. [Database Terminology](#database-terminology)
3. [UI Terminology](#ui-terminology)
4. [Security Terminology](#security-terminology)
5. [Educational Terminology](#educational-terminology)
6. [DevOps Terminology](#devops-terminology)
7. [Testing Terminology](#testing-terminology)
8. [Accessibility Terminology](#accessibility-terminology)
9. [Usage Guidelines](#usage-guidelines)

---

## API Terminology

| Term | Definition | Usage | Avoid |
|---|---|---|---|
| **Endpoint** | A specific URL path where an API can be accessed | "The `/api/v1/users` endpoint returns all users" | "URL", "route handler" (use endpoint for the external-facing address) |
| **Route** | A URL pattern mapped to a handler function | "Define a route for `GET /courses/{id}`" | "endpoint" when referring to the server-side mapping |
| **Resource** | A domain entity exposed via the API | "The User resource has email, name, and role fields" | "model" when referring to the API representation |
| **Representation** | The serialized form of a resource in a response | "The JSON representation includes the user's enrollments" | "response body" (too vague) |
| **Request** | An incoming HTTP message to the server | "The request contains the user's new password" | "call" (too informal) |
| **Response** | An outgoing HTTP message to the client | "The response includes a Location header" | "reply" (too informal) |
| **Payload** | The data sent in the body of a request or response | "The POST payload contains the course title and description" | "data", "body" when referring to the semantic content |
| **Header** | A key-value pair in the HTTP request or response | "Set the `Authorization` header with the bearer token" | "metadata" (too vague) |
| **Status Code** | The numeric HTTP response code | "Return 404 when the course is not found" | "error code" (status code is more specific) |
| **Query Parameter** | A key-value pair appended to the URL after `?` | "Use `?page=2&limit=50` to paginate" | "query string parameter" (verbose) |
| **Path Parameter** | A variable segment in the URL path | "The `{course_id}` path parameter identifies the course" | "URL parameter" (ambiguous) |
| **Pagination** | Dividing a large result set into pages | "Support offset and cursor pagination" | "paging" (less standard) |
| **Rate Limit** | A constraint on request frequency | "The rate limit is 100 requests per minute" | "throttle" (as a noun; use "rate limiting" as gerund) |
| **Content Negotiation** | Client-server agreement on response format | "The client sends Accept: application/json" | "format negotiation" |
| **Idempotency** | The property that repeated identical requests have the same effect | "DELETE operations must be idempotent" | "repeatability" |

---

## Database Terminology

| Term | Definition | Usage | Avoid |
|---|---|---|---|
| **Table** | A collection of related rows in a relational database | "The `user` table stores account information" | "entity" (when referring to the database structure specifically) |
| **Column** | A named field within a table | "The `email` column has a unique constraint" | "field" (use column for database context) |
| **Row** | A single record in a table | "Each row represents one enrolled user" | "record" (acceptable but prefer "row") |
| **Index** | A data structure that speeds up queries | "Create an index on `user.email`" | "lookup" (too informal) |
| **Constraint** | A rule enforcing data integrity | "The foreign key constraint prevents orphaned records" | "rule" (too generic) |
| **Migration** | A versioned change to the database schema | "Run migration 007 to add the audit_log table" | "script" (too vague) |
| **Schema** | The structure definition of tables and relationships | "The current schema includes 15 tables" | "model" (ambiguous; schema is the DB structure) |
| **Foreign Key** | A column referencing a primary key in another table | "The `user_id` foreign key links to the user table" | "reference" (too informal) |
| **Primary Key** | A unique identifier for each row | "The `id` column is the primary key" | "ID" (when discussing the concept) |
| **Unique Constraint** | A constraint preventing duplicate values | "A unique constraint on `email` prevents duplicate accounts" | "unique index" (conflates concepts) |
| **Nullable** | A column that may contain NULL values | "The `deleted_at` column is nullable" | "optional" (too vague) |
| **Default Value** | A value assigned when none is specified | "The `is_active` column defaults to TRUE" | "fallback value" |
| **Join** | Combining rows from multiple tables | "Join `user` with `enrollment` on `user_id`" | "combine" (too informal) |
| **Aggregate** | A computation across multiple rows | "Compute the average score using an aggregate" | "summary" (too informal) |
| **Transaction** | A group of operations that succeed or fail atomically | "Wrap the inserts in a transaction" | "batch" (conflates concepts) |

---

## UI Terminology

| Term | Definition | Usage | Avoid |
|---|---|---|---|
| **Component** | A reusable, self-contained UI building block | "The `LoginForm` component handles authentication" | "widget" (dated terminology) |
| **View** | A complete screen or page layout | "The dashboard view shows enrollment status" | "screen" (acceptable but "view" is preferred) |
| **Page** | A top-level route with its own URL | "The `/courses` page displays the catalog" | "view" when referring to a URL-addressable unit |
| **Modal** | An overlay dialog that requires user interaction | "Show a confirmation modal before deleting" | "popup", "dialog" (use "modal" consistently) |
| **Toast** | A brief, non-blocking notification | "Show a success toast after saving" | "notification", "snackbar", "alert" (pick one: toast) |
| **Toast** (also) | A temporary message that auto-dismisses | "Display an error toast if the request fails" | "banner" (banners are persistent) |
| **Card** | A container grouping related content | "Display each course in a card with title and progress" | "tile", "box" |
| **Form** | A collection of input fields for data entry | "The registration form collects email and password" | "input" (input is a single field) |
| **Input** | A single field within a form | "The email input validates format in real time" | "field" (acceptable but "input" is more specific) |
| **Button** | A clickable action trigger | "The submit button sends the form data" | "link" (links navigate; buttons act) |
| **Badge** | A small indicator for counts or status | "Show a badge with the unread notification count" | "tag", "chip" (when indicating counts) |
| **Sidebar** | A vertical navigation panel | "The sidebar lists all enrolled courses" | "drawer" (drawer is a slide-in overlay) |
| **Header** (UI) | The top section of a page or layout | "The page header shows the course title" | "navbar" (navbar is specifically navigation) |
| **Footer** | The bottom section of a page or layout | "The footer contains copyright and links" | — |
| **Table** (UI) | A grid display of structured data | "The user table shows name, email, and role columns" | "list" (when data is tabular) |
| **List** | A vertical arrangement of items | "The notification list shows recent alerts" | "feed" (feed implies continuous update) |
| **Skeleton** | A loading placeholder matching content shape | "Show a skeleton while the page loads" | "placeholder" (too generic) |
| **Tooltip** | A hover-activated informational popup | "Show a tooltip explaining each permission" | "hint", "popover" |

---

## Security Terminology

| Term | Definition | Usage | Avoid |
|---|---|---|---|
| **Authentication** | The process of verifying identity | "Authentication requires email and password" | "auth" in formal documentation (too ambiguous) |
| **Authorization** | The process of verifying permissions | "Authorization checks run after authentication" | "access control" (too broad; use authorization) |
| **Session** | An authenticated connection with a stateful lifetime | "The session expires after 30 minutes of inactivity" | "connection" (too generic) |
| **Token** | An opaque credential representing a session or claim | "The bearer token is included in the Authorization header" | "key" (too generic; use token) |
| **Credential** | Authentication material (password, key, biometric) | "Store credentials securely with hashing" | "secret" (too narrow) |
| **Password Hash** | A one-way cryptographic transformation of a password | "Use Argon2id for password hashing" | "encrypted password" (hashing ≠ encryption) |
| **Salt** | Random data added to a password before hashing | "Each password gets a unique salt" | "nonce" (different concept) |
| **MFA** | Multi-Factor Authentication | "Require MFA for admin accounts" | "two-factor" (MFA may have more than 2 factors) |
| **RBAC** | Role-Based Access Control | "Implement RBAC for course management" | "permission system" (too vague) |
| **Abac** | Attribute-Based Access Control | "Use ABAC for fine-grained resource policies" | "policy-based" (too vague) |
| **CSRF** | Cross-Site Request Forgery | "Include CSRF tokens in form submissions" | "XSRF" (less recognized) |
| **XSS** | Cross-Site Scripting | "Sanitize input to prevent XSS" | "script injection" (less standard) |
| **CORS** | Cross-Origin Resource Sharing | "Configure CORS to allow trusted origins" | "cross-origin policy" |
| **JWT** | JSON Web Token | "Validate the JWT signature before processing" | "bearer token" when specifically discussing JWT structure |
| **Scope** | A defined boundary for token permissions | "The token scope includes read-only access to courses" | "permission" (scope is more limited) |
| **Cryptography** | The practice of secure communication | "Use modern cryptography for data at rest" | "encryption" (encryption is a subset of cryptography) |
| **Encryption** | Transforming data to prevent unauthorized reading | "Encrypt sensitive data at rest" | "scramble", "encode" (too informal) |
| **Hash** | A fixed-size output from a one-way function | "Compare the hash of the submitted password" | "checksum" (different use case) |
| **Vulnerability** | A weakness that can be exploited | "Patch known vulnerabilities promptly" | "weakness", "flaw" (vulnerability is more precise) |
| **Threat** | A potential cause of an unwanted incident | "Phishing is a common social engineering threat" | "attack" (attack is the action; threat is the potential) |
| **Attack** | An active attempt to breach security | "The brute-force attack targeted the login endpoint" | "intrusion" (too narrow) |
| **Defense** | Protective measures against attacks | "Deploy WAF as a defense against SQL injection" | "protection" (defense is more active) |
| **Incident** | A confirmed security event requiring response | "Report the incident within 1 hour" | "event" (event is too generic) |

---

## Educational Terminology

| Term | Definition | Usage | Avoid |
|---|---|---|---|
| **Course** | A structured learning path on a topic | "The Advanced Authentication course covers OAuth 2.0" | "class" (connotes live instruction) |
| **Module** | A focused subdivision of a course | "Module 3 covers session management" | "unit" (acceptable but prefer module) |
| **Lesson** | An individual instructional unit | "This lesson is a 15-minute video" | "lecture" (implies live delivery) |
| **Assessment** | An evaluation of learner knowledge | "The module assessment tests key concepts" | "test", "exam" (assessment is more broadly applicable) |
| **Question** | A single item within an assessment | "The question asks learners to identify the vulnerability" | "problem" (too informal) |
| **Enrollment** | A user's registration in a course | "Enrollment is open for the new cohort" | "registration" (enrollment is specific to education) |
| **Progress** | Tracking of completion status | "The learner's progress shows 60% complete" | "status" (progress implies measurement) |
| **Score** | A numerical result on an assessment | "A score of 80% or higher is required to pass" | "grade" (grade implies letter grades) |
| **Certificate** | A credential proving course completion | "The certificate is issued upon passing the final assessment" | "badge", "diploma" |
| **Competency** | A demonstrable skill or knowledge area | "Authentication Competency achieved at Expert level" | "skill" (competency is more formal) |
| **Prerequisite** | A requirement before accessing content | "Prerequisite: Basic Authentication course" | "requirement" (too vague) |
| **Curriculum** | The overall sequence of courses and learning objectives | "The cybersecurity curriculum spans 12 courses" | "syllabus" (syllabus is course-level) |
| **Cohort** | A group of learners progressing together | "The Q1 2025 cohort starts January 15" | "class", "group" |
| **Learning Objective** | A specific skill or knowledge a learner will gain | "By the end, learners will be able to implement JWT auth" | "goal" (too informal) |
| **Learner** | A person actively studying within the platform | "Each learner has a personalized dashboard" | "student", "user" (learner is preferred) |
| **Instructor** | A person who creates or delivers educational content | "The instructor authored the simulation scenarios" | "teacher" (too K-12 connotation) |
| **Lab** | A hands-on practical exercise | "Complete the OAuth 2.0 lab to practice token flows" | "exercise" (lab implies interactive environment) |

---

## DevOps Terminology

| Term | Definition | Usage | Avoid |
|---|---|---|---|
| **Pipeline** | An automated sequence of build, test, and deploy stages | "The CI pipeline runs tests on every push" | "workflow" (too vague) |
| **Stage** | A phase within a pipeline | "The deploy stage follows the test stage" | "step" (too generic) |
| **Job** | A unit of work within a stage | "The lint job checks code style" | "task" (too generic) |
| **Artifact** | A built output from a pipeline stage | "The Docker image is the build artifact" | "output" (too generic) |
| **Deployment** | The process of making a version available in an environment | "The deployment to production completes in 10 minutes" | "release" (release is the version; deployment is the action) |
| **Rollback** | Reverting to a previous version | "Execute a rollback if health checks fail" | "revert" (acceptable but rollback is DevOps-specific) |
| **Container** | An isolated runtime environment | "Run the API in a Docker container" | "instance" (container implies isolation) |
| **Image** | A template for creating containers | "The base image includes Python 3.12" | "template" (too vague) |
| **Environment** | A deployment target with its own configuration | "Deploy to staging before production" | "server" (environment is broader) |
| **Configuration** | Environment-specific settings | "Production configuration uses a larger pool" | "settings" (configuration is more formal) |
| **Secret** | Sensitive configuration value | "Store secrets in a vault, not in code" | "key", "token" (secret is the broader category) |
| **Monitoring** | Observing system health and performance | "Set up monitoring for response latency" | "observability" (too broad; monitoring is a subset) |
| **Alerting** | Automated notification when thresholds are breached | "Configure alerting for error rate spikes" | "notification" (too generic) |
| **Scaling** | Adjusting capacity to meet demand | "Auto-scaling adds instances during peak hours" | "provisioning" (provisioning is initial setup) |
| **Infrastructure** | The underlying compute, network, and storage | "Infrastructure is managed with Terraform" | "servers" (too narrow) |
| **Orchestration** | Coordinating multiple containers or services | "Kubernetes orchestrates the microservices" | "management" (too vague) |

---

## Testing Terminology

| Term | Definition | Usage | Avoid |
|---|---|---|---|
| **Test** | A verification of expected behavior | "Write a test for the login endpoint" | "check" (too informal) |
| **Test Suite** | A collection of related tests | "The authentication test suite has 42 tests" | "test set", "test group" |
| **Fixture** | Pre-defined data or state for a test | "Use the user fixture to set up test data" | "setup" (setup is the action; fixture is the data) |
| **Mock** | A controlled substitute for a dependency | "Mock the email service to test notification logic" | "stub" (stubs return fixed values; mocks verify interactions) |
| **Stub** | A simplified implementation returning fixed values | "Use a stub for the external API" | "mock" when only returning fixed values |
| **Assertion** | A statement verifying expected results | "Assert that the response status is 201" | "check", "verify" (assertion is the specific term) |
| **Test Case** | A specific scenario with inputs and expected outcomes | "This test case verifies expired token handling" | "test" (test case is the full scenario) |
| **Coverage** | The percentage of code exercised by tests | "Maintain at least 90% test coverage" | "completeness" (coverage is the standard term) |
| **Regression Test** | A test ensuring previously fixed bugs don't recur | "Add a regression test for issue #1234" | "retest" (retest is for verifying a fix once) |
| **Integration Test** | A test verifying component interaction | "The integration test covers the full auth flow" | "end-to-end test" (E2E is a subset) |
| **Unit Test** | A test verifying a single function or class | "Write unit tests for the password validator" | "component test" (unit tests are smaller) |
| **E2E Test** | A test simulating full user workflows | "The E2E test covers login → dashboard → logout" | "integration test" (E2E tests the full stack) |
| **Smoke Test** | A minimal test verifying basic functionality | "Run smoke tests after deployment" | "sanity check" (too informal) |
| **Performance Test** | A test measuring system performance under load | "Performance tests measure p95 latency under 200ms" | "load test" (load test is a type of performance test) |
| **Security Test** | A test verifying security properties | "Security tests check for injection vulnerabilities" | "pen test" (penetration testing is a specific practice) |

---

## Accessibility Terminology

| Term | Definition | Usage | Avoid |
|---|---|---|---|
| **WCAG** | Web Content Accessibility Guidelines | "All pages must meet WCAG 2.1 AA" | "accessibility standard" (too vague) |
| **ARIA** | Accessible Rich Internet Applications (attributes) | "Add ARIA labels to icon-only buttons" | "accessibility attributes" (use the acronym) |
| **Landmark** | A major page region identifiable by assistive tech | "Use `<nav>` as a landmark for main navigation" | "region" (landmark is more specific) |
| **Role** | An ARIA attribute defining an element's purpose | "Set role='alert' for error messages" | "type" (too generic) |
| **Focus** | The currently active interactive element | "Ensure focus is visible on all interactive elements" | "selection" (focus ≠ selection) |
| **Screen Reader** | Software that reads page content aloud | "Test with a screen reader to verify labels" | "reader" (too vague) |
| **Alt Text** | Descriptive text for images | "Provide alt text for all non-decorative images" | "image description" (alt text is the HTML attribute) |
| **Keyboard Navigation** | Controlling the interface with keyboard only | "Verify all features are accessible via keyboard navigation" | "keyboard-only" (less formal) |
| **Color Contrast** | The luminance ratio between foreground and background | "Ensure a minimum 4.5:1 color contrast ratio" | "readability" (readability is broader) |
| **Focus Trap** | Restricting focus within a modal or component | "Trap focus inside the modal when it opens" | "focus management" (too broad) |
| **Skip Link** | A hidden link to bypass repetitive navigation | "Add a skip link to jump to main content" | "skip navigation" (acceptable but skip link is standard) |
| **Live Region** | An ARIA region that updates dynamically | "Use aria-live='polite' for toast notifications" | "dynamic region" |
| **Tab Order** | The sequence elements receive focus via Tab key | "Ensure a logical tab order matches visual layout" | "navigation order" |
| **Accessible Name** | The text label announced by screen readers | "The button's accessible name is 'Submit enrollment'" | "label" (label is part of accessible name) |

---

## Usage Guidelines

### Consistency Rules

1. **Pick one term and stick with it.** If the glossary says "learner", never use "student" or "user" in educational contexts.
2. **Use the formal term in documentation.** Casual terms are acceptable in chat, but documentation and code comments use the glossary term.
3. **When multiple terms could apply, use the most specific one.** "Mock" is more specific than "test double"; use it when you mean a mock.
4. **Define terms on first use in long documents.** If a reader might not know a term, add a parenthetical definition.

### Documentation Writing Rules

| Rule | Example |
|---|---|
| Use "endpoint" for API addresses | "The `/users` endpoint returns a list" |
| Use "table" for database collections | "The `user` table stores accounts" |
| Use "component" for UI building blocks | "The `LoginForm` component handles input" |
| Use "assessment" for evaluations | "The assessment has 10 questions" |
| Use "pipeline" for CI/CD sequences | "The pipeline runs lint, test, and deploy stages" |
| Use "fixture" for test data | "The `admin_user` fixture provides a test user" |

### Code vs. Documentation

| Context | Term | Example |
|---|---|---|
| Code (variable/function) | snake_case | `get_user_by_id()` |
| Documentation (prose) | Full words | "The `get_user_by_id` function retrieves..." |
| API docs | kebab-case URLs | `GET /api/v1/users/{user-id}` |
| DB docs | snake_case table names | "The `enrollment` table..." |

---

*Last updated: 2025-01-15*
*Owner: AuthShield Lab Engineering*
