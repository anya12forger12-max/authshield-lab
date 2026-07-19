# AuthShield Lab — Module Boundary Definitions

> Version: 1.0.0 | Last Updated: 2026-07-19
> Status: Living Document | Owner: Architecture Team

---

## 1. Overview

Every module in AuthShield Lab has an explicit boundary: a **public API** that other modules may consume, **private internals** that are implementation details, **declared dependencies** on other modules, and **dependents** that consume its API.

This document defines the boundary for every module across all six release waves (V1.0 through V6.0). It establishes dependency rules, anti-corruption layers, interface contracts, event boundaries, data ownership, maturity levels, and versioning strategy.

---

## 2. Module Inventory

| # | Module | Wave | Layer | Maturity |
|---|---|---|---|---|
| 1 | `auth` | V1.0 | Core | Mature |
| 2 | `users` | V1.0 | Core | Mature |
| 3 | `sessions` | V1.0 | Core | Mature |
| 4 | `audit` | V1.0 | Core | Mature |
| 5 | `policies` | V1.0 | Domain | Stable |
| 6 | `rules` | V1.0 | Domain | Stable |
| 7 | `defense` | V1.0 | Domain | Stable |
| 8 | `content` | V3.0 | Application | Stable |
| 9 | `lms` | V3.0 | Application | Stable |
| 10 | `simulation` | V3.0 | Application | Stable |
| 11 | `developer` | V3.0 | Application | Stable |
| 12 | `quality` | V3.0 | Application | Stable |
| 13 | `production` | V3.0 | Application | Stable |
| 14 | `ecosystem` | V4.0 | Infrastructure | Stable |
| 15 | `optimization` | V4.0 | Infrastructure | Experimental |
| 16 | `collaboration` | V5.0 | Presentation | Experimental |
| 17 | `standards` | V5.0 | Domain | Experimental |
| 18 | `content_studio` | V5.0 | Presentation | Experimental |
| 19 | `analytics` | V5.0 | Infrastructure | Experimental |
| 20 | `certification` | V5.0 | Application | Experimental |
| 21 | `learning` | V6.0 | Application | Experimental |
| 22 | `attacks` | V1.0 | Domain | Stable |
| 23 | `security` | V1.0 | Core | Mature |
| 24 | `shared` | V1.0 | Core | Mature |
| 25 | `config` | V1.0 | Core | Mature |
| 26 | `reports` | V3.0 | Application | Stable |

---

## 3. Module Definitions

### 3.1 `auth` — Authentication Engine

**Layer:** Core
**Maturity:** Mature | **Version:** 1.x.x

**Purpose:** Handles user authentication including login, logout, registration, password verification, MFA, and token management.

**Public API:**
- `AuthenticationService.authenticate(credentials) → AuthResult`
- `LoginService.login(email, password) → SessionToken`
- `LogoutService.logout(session_token) → void`
- `RegistrationService.register(user_data) → UserRecord`
- `PasswordVerificationService.verify(token, password) → bool`
- `PasswordPolicyService.validate(password) → PolicyResult`

**Private Internals:**
- `authentication/repositories/` — data access layer
- `authentication/validators/` — input validation logic
- `authentication/events/event_publisher.py` — event emission

**Dependencies:**
- `users` — user lookup during login
- `sessions` — session creation/destruction
- `audit` — event logging
- `security` — rate limiting, brute-force protection
- `config` — authentication configuration

**Dependents:**
- `lms` — learner authentication
- `simulation` — attacker/defender identity
- `developer` — API key authentication
- `collaboration` — user identity in collaborative sessions

---

### 3.2 `users` — User Management

**Layer:** Core
**Maturity:** Mature | **Version:** 1.x.x

**Purpose:** User CRUD operations, profile management, role assignment, and user lifecycle.

**Public API:**
- `UserService.create_user(data) → User`
- `UserService.get_user(user_id) → User`
- `UserService.update_user(user_id, data) → User`
- `UserService.delete_user(user_id) → void`
- `UserService.list_users(filters) → UserList`
- `UserService.assign_role(user_id, role) → void`

**Private Internals:**
- User entity definitions
- Profile image handling
- Role/permission resolution logic

**Dependencies:**
- `config` — user defaults
- `audit` — user lifecycle events

**Dependents:**
- `auth` — user lookup during authentication
- `sessions` — user association with sessions
- `lms` — learner profiles
- `collaboration` — user identity
- `certification` — certificate holders

---

### 3.3 `sessions` — Session Management

**Layer:** Core
**Maturity:** Mature | **Version:** 1.x.x

**Purpose:** Session creation, validation, refresh, expiration, and concurrent session management.

**Public API:**
- `SessionService.create_session(user_id) → Session`
- `SessionService.validate_session(token) → Session | null`
- `SessionService.refresh_session(token) → Session`
- `SessionService.destroy_session(token) → void`
- `SessionService.destroy_all_sessions(user_id) → void`

**Private Internals:**
- Token generation and rotation
- Session store (in-memory / SQLite)
- Cleanup scheduler

**Dependencies:**
- `config` — session TTL, max concurrent
- `audit` — session events
- `security` — IP binding, fingerprinting

**Dependents:**
- `auth` — session lifecycle during login/logout
- `simulation` — session state in attack scenarios

---

### 3.4 `audit` — Audit Logging

**Layer:** Core
**Maturity:** Mature | **Version:** 1.x.x

**Purpose:** Immutable audit trail for all security-relevant actions across the platform.

**Public API:**
- `AuditService.log(event: AuditEvent) → void`
- `AuditService.query(filters) → AuditEntry[]`
- `AuditService.export(format) → AuditReport`
- `AuditService.get_retention_policy() → RetentionPolicy`

**Private Internals:**
- Event serialization
- Storage engine (append-only)
- Retention enforcement

**Dependencies:**
- `config` — retention policy, log levels
- `users` — user identity resolution

**Dependents:**
- `auth` — authentication events
- `sessions` — session events
- `defense` — policy/rule evaluation events
- `simulation` — simulation events
- `production` — production events
- `certification` — certification events

---

### 3.5 `policies` — Policy Engine

**Layer:** Domain
**Maturity:** Stable | **Version:** 1.x.x

**Purpose:** Defines, stores, and evaluates security policies (authentication policies, access policies, rate-limiting policies).

**Public API:**
- `PolicyService.create_policy(data) → Policy`
- `PolicyService.evaluate(context) → PolicyDecision`
- `PolicyService.list_policies(filters) → Policy[]`
- `PolicyService.update_policy(id, data) → Policy`
- `PolicyService.delete_policy(id) → void`

**Private Internals:**
- Policy DSL parser
- Policy registry (in-memory cache)
- Evaluation engine

**Dependencies:**
- `rules` — rule evaluation within policies
- `config` — default policies
- `audit` — policy evaluation logging

**Dependents:**
- `defense` — policy-driven defense actions
- `auth` — authentication policy checks

---

### 3.6 `rules` — Rule Engine

**Layer:** Domain
**Maturity:** Stable | **Version:** 1.x.x

**Purpose:** Individual security rules that can be composed into policies (rate limits, IP blocks, credential checks, anomaly detection).

**Public API:**
- `RuleService.create_rule(data) → Rule`
- `RuleService.evaluate(rule_id, context) → RuleResult`
- `RuleService.list_rules(filters) → Rule[]`
- `RuleService.toggle_rule(id, enabled) → void`

**Private Internals:**
- Rule type definitions (rate-limit, block, allow, inspect)
- Rule condition parser
- Rule registry

**Dependencies:**
- `config` — default rules
- `audit` — rule evaluation logging

**Dependents:**
- `policies` — rules are consumed by policies
- `defense` — direct rule evaluation

---

### 3.7 `defense` — Defense Orchestration

**Layer:** Domain
**Maturity:** Stable | **Version:** 1.x.x

**Purpose:** Orchestrates defense responses by combining policies, rules, and automated countermeasures.

**Public API:**
- `DefenseService.analyze(threat) → DefenseDecision`
- `DefenseService.block(source, reason) → void`
- `DefenseService.unblock(source) → void`
- `DefenseService.get_active_defenses() → DefenseStatus[]`

**Private Internals:**
- Defense action executor
- Source tracking and scoring
- Alert dispatcher

**Dependencies:**
- `policies` — policy evaluation
- `rules` — rule evaluation
- `audit` — defense event logging
- `config` — defense configuration
- `users` — user context

**Dependents:**
- `auth` — defense integration during login
- `simulation` — defense responses in scenarios

---

### 3.8 `content` — Content Management

**Layer:** Application
**Maturity:** Stable | **Version:** 3.x.x

**Purpose:** Manages educational content (articles, lessons, exercises) with versioning and metadata.

**Public API:**
- `ContentService.create_content(data) → Content`
- `ContentService.get_content(id) → Content`
- `ContentService.list_content(filters) → ContentList`
- `ContentService.publish(id) → void`
- `ContentService.archive(id) → void`

**Private Internals:**
- Content storage and indexing
- Metadata extraction
- Version tracking

**Dependencies:**
- `users` — author identity
- `audit` — content lifecycle events
- `config` — content defaults

**Dependents:**
- `lms` — lesson content
- `content_studio` — content editing
- `quality` — content quality checks

---

### 3.9 `lms` — Learning Management System

**Layer:** Application
**Maturity:** Stable | **Version:** 3.x.x

**Purpose:** Structured learning paths, progress tracking, assignments, grading, and instructor tools.

**Public API:**
- `LmsService.create_learning_path(data) → LearningPath`
- `LmsService.enroll(user_id, path_id) → Enrollment`
- `LmsService.track_progress(user_id, content_id) → Progress`
- `LmsService.grade(submission_id, score) → Grade`
- `LmsService.get_analytics(path_id) → LmsAnalytics`

**Private Internals:**
- Enrollment management
- Progress calculation engine
- Grading rubrics

**Dependencies:**
- `content` — lesson content
- `users` — learner and instructor identity
- `auth` — authentication
- `audit` — learning events
- `analytics` — learning analytics

**Dependents:**
- `learning` — extended learning features
- `certification` — certification prerequisites

---

### 3.10 `simulation` — Attack/Defense Simulation

**Layer:** Application
**Maturity:** Stable | **Version:** 3.x.x

**Purpose:** Sandboxed attack and defense simulation scenarios, CTF challenges, and incident response playbooks.

**Public API:**
- `SimulationService.create_scenario(data) → Scenario`
- `SimulationService.start(user_id, scenario_id) → SimulationSession`
- `SimulationService.execute_action(session_id, action) → ActionResult`
- `SimulationService.complete(session_id) → SimulationResult`

**Private Internals:**
- Sandbox execution engine
- Action validation
- Scoring engine

**Dependencies:**
- `auth` — user identity
- `defense` — defense simulation
- `attacks` — attack scenario library
- `audit` — simulation events
- `users` — participant identity

**Dependents:**
- `learning` — integrated learning simulations
- `quality` — scenario quality validation

---

### 3.11 `developer` — Developer Tools

**Layer:** Application
**Maturity:** Stable | **Version:** 3.x.x

**Purpose:** API explorer, SDK generation, extension management, automation, and developer experience tooling.

**Public API:**
- `DeveloperService.register_api_key(name) → ApiKey`
- `DeveloperService.validate_api_key(key) → bool`
- `DeveloperService.list_extensions() → Extension[]`
- `DeveloperService.install_extension(id) → void`
- `DeveloperService.automate(workflow) → AutomationResult`

**Private Internals:**
- API key storage and rotation
- Extension loader and sandbox
- Workflow engine

**Dependencies:**
- `auth` — API key authentication
- `users` — developer identity
- `audit` — developer actions
- `ecosystem` — extension marketplace

**Dependents:**
- `plugins` — plugin installation via developer tools

---

### 3.12 `quality` — Quality Assurance

**Layer:** Application
**Maturity:** Stable | **Version:** 3.x.x

**Purpose:** Content quality validation, scenario testing, automated QA checks, and quality metrics.

**Public API:**
- `QualityService.validate_content(content_id) → QualityReport`
- `QualityService.validate_scenario(scenario_id) → QualityReport`
- `QualityService.run_automated_checks(target) → CheckResult[]`
- `QualityService.get_quality_metrics(filters) → Metrics`

**Private Internals:**
- Check engine
- Metric aggregation
- Quality scoring algorithms

**Dependencies:**
- `content` — content to validate
- `simulation` — scenarios to validate
- `audit` — quality events
- `config` — quality thresholds

**Dependents:**
- `production` — production readiness checks
- `content_studio` — quality feedback during editing

---

### 3.13 `production` — Production Readiness

**Layer:** Application
**Maturity:** Stable | **Version:** 3.x.x

**Purpose:** Feature flags, release management, health dashboards, governance, LTS support, and production validation.

**Public API:**
- `ProductionService.validate_release(release_id) → ReleaseReport`
- `ProductionService.toggle_feature(flag, enabled) → void`
- `ProductionService.get_health() → HealthStatus`
- `ProductionService.get_governance_status() → GovernanceStatus`

**Private Internals:**
- Feature flag store
- Release validation pipeline
- Health check aggregator

**Dependencies:**
- `quality` — quality gate checks
- `audit` — production events
- `config` — feature flag defaults
- `certification` — certification validation

**Dependents:**
- `analytics` — production metrics
- `optimization` — production performance data

---

### 3.14 `ecosystem` — Plugin Ecosystem

**Layer:** Infrastructure
**Maturity:** Stable | **Version:** 4.x.x

**Purpose:** Plugin marketplace, plugin lifecycle management, community contributions, and third-party integrations.

**Public API:**
- `EcosystemService.list_plugins(filters) → Plugin[]`
- `EcosystemService.install(plugin_id) → void`
- `EcosystemService.uninstall(plugin_id) → void`
- `EcosystemService.submit(plugin_data) → PluginSubmission`

**Private Internals:**
- Plugin registry
- Compatibility checker
- Review workflow

**Dependencies:**
- `users` — plugin author identity
- `audit` — plugin lifecycle events
- `security` — plugin security scanning
- `config` — ecosystem configuration

**Dependents:**
- `developer` — extension management

---

### 3.15 `optimization` — Performance Optimization

**Layer:** Infrastructure
**Maturity:** Experimental | **Version:** 4.x.x

**Purpose:** Caching strategies, query optimization, connection pooling, lazy loading, and performance monitoring.

**Public API:**
- `OptimizationService.get_cache_stats() → CacheStats`
- `OptimizationService.invalidate(pattern) → void`
- `OptimizationService.get_query_stats() → QueryStats`

**Private Internals:**
- Cache layer implementations
- Query plan analyzer
- Connection pool manager

**Dependencies:**
- `config` — caching configuration
- `production` — production metrics
- `audit` — optimization events

**Dependents:**
- `analytics` — performance data
- `learning` — content caching

---

### 3.16 `collaboration` — Collaborative Features

**Layer:** Presentation
**Maturity:** Experimental | **Version:** 5.x.x

**Purpose:** Real-time collaboration on scenarios, shared workspaces, peer review, and team exercises.

**Public API:**
- `CollaborationService.create_workspace(data) → Workspace`
- `CollaborationService.join_workspace(user_id, workspace_id) → void`
- `CollaborationService.submit_review(target_id, review) → Review`
- `CollaborationService.start_team_exercise(exercise_id) → TeamSession`

**Private Internals:**
- WebSocket session manager
- Conflict resolution
- Presence tracking

**Dependencies:**
- `auth` — user identity
- `users` — user profiles
- `simulation` — collaborative simulations
- `audit` — collaboration events

**Dependents:**
- `learning` — collaborative learning

---

### 3.17 `standards` — Standards Compliance

**Layer:** Domain
**Maturity:** Experimental | **Version:** 5.x.x

**Purpose:** Maps platform content and features to industry standards (NIST, OWASP, ISO 27001), evidence collection, and framework comparison.

**Public API:**
- `StandardsService.get_frameworks() → Framework[]`
- `StandardsService.map_content(content_id, framework_id) → Mapping`
- `StandardsService.collect_evidence(mapping_id) → Evidence[]`
- `StandardsService.compare(framework_a, framework_b) → Comparison`

**Private Internals:**
- Framework database
- Mapping algorithms
- Evidence aggregation

**Dependencies:**
- `content` — content to map
- `audit` — standards events
- `config` — framework definitions

**Dependents:**
- `certification` — certification standards mapping
- `quality` — standards compliance checks

---

### 3.18 `content_studio` — Content Authoring

**Layer:** Presentation
**Maturity:** Experimental | **Version:** 5.x.x

**Purpose:** WYSIWYG content editor, media management, template system, and content preview.

**Public API:**
- `ContentStudioService.create_draft(data) → Draft`
- `ContentStudioService.save_draft(draft_id, content) → Draft`
- `ContentStudioService.preview(draft_id) → Preview`
- `ContentStudioService.publish_draft(draft_id) → Content`

**Private Internals:**
- Editor state management
- Media upload handler
- Template engine

**Dependencies:**
- `content` — content creation
- `quality` — quality feedback
- `users` — author identity
- `audit` — content editing events

**Dependents:**
- `learning` — authored learning content

---

### 3.19 `analytics` — Analytics & Reporting

**Layer:** Infrastructure
**Maturity:** Experimental | **Version:** 5.x.x

**Purpose:** Learning analytics, platform usage metrics, custom report generation, and data visualization.

**Public API:**
- `AnalyticsService.get_learning_analytics(user_id) → LearningAnalytics`
- `AnalyticsService.get_platform_metrics() → PlatformMetrics`
- `AnalyticsService.generate_report(config) → Report`
- `AnalyticsService.get_dashboard(dashboard_id) → Dashboard`

**Private Internals:**
- Metric aggregation engine
- Report generator
- Data warehouse adapter

**Dependencies:**
- `lms` — learning data
- `users` — user data
- `production` — platform metrics
- `optimization` — performance metrics
- `audit` — event data

**Dependents:**
- `certification` — certification analytics
- `learning` — learning analytics

---

### 3.20 `certification` — Certification & Assessment

**Layer:** Application
**Maturity:** Experimental | **Version:** 5.x.x

**Purpose:** Certification exams, badge issuance, platform validation, disaster recovery, and sustainability metrics.

**Public API:**
- `CertificationService.create_certification(data) → Certification`
- `CertificationService.issue_badge(user_id, cert_id) → Badge`
- `CertificationService.validate_platform() → ValidationReport`
- `CertificationService.get_operations() → OperationsStatus`

**Private Internals:**
- Exam engine
- Badge renderer
- Validation pipeline

**Dependencies:**
- `standards` — certification standards
- `lms` — prerequisite tracking
- `quality` — quality gates
- `production` — production validation
- `audit` — certification events
- `users` — certificate holders

**Dependents:**
- `learning` — certification tracks

---

### 3.21 `learning` — Extended Learning (V6.0)

**Layer:** Application
**Maturity:** Experimental | **Version:** 6.x.x (target)

**Purpose:** Adaptive learning paths, AI-assisted tutoring, spaced repetition, and personalized learning recommendations.

**Public API:**
- `LearningService.create_adaptive_path(user_id) → AdaptivePath`
- `LearningService.get_recommendations(user_id) → Recommendation[]`
- `LearningService.track_spaced_repetition(user_id, item_id) → void`
- `LearningService.get_learning_insights(user_id) → Insights`

**Private Internals:**
- Adaptive algorithm engine
- Spaced repetition scheduler
- Recommendation engine

**Dependencies:**
- `lms` — base learning infrastructure
- `content` — learning content
- `analytics` — learning analytics
- `users` — learner identity
- `auth` — authentication
- `simulation` — simulation-based learning
- `optimization` — content caching

**Dependents:**
- (none — leaf module)

---

### 3.22 `attacks` — Attack Library

**Layer:** Domain
**Maturity:** Stable | **Version:** 1.x.x

**Purpose:** Pre-built attack scenarios, attack vectors, and attack chain definitions.

**Public API:**
- `AttackService.get_attacks(filters) → Attack[]`
- `AttackService.get_attack(id) → Attack`
- `AttackService.create_attack(data) → Attack`
- `AttackService.execute(attack_id, context) → AttackResult`

**Private Internals:**
- Attack vector definitions
- Attack chain engine
- Payload generators

**Dependencies:**
- `config` — attack configuration
- `audit` — attack events

**Dependents:**
- `simulation` — attack scenarios
- `defense` — attack pattern matching

---

### 3.23 `security` — Security Infrastructure

**Layer:** Core
**Maturity:** Mature | **Version:** 1.x.x

**Purpose:** Rate limiting, brute-force protection, CSRF protection, input sanitization, and security middleware.

**Public API:**
- `SecurityService.check_rate_limit(identifier) → bool`
- `SecurityService.validate_csrf_token(token) → bool`
- `SecurityService.sanitize_input(data) → SanitizedData`
- `SecurityService.check_permission(user_id, resource, action) → bool`

**Private Internals:**
- Rate limit store (in-memory sliding window)
- CSRF token generator
- Input sanitization rules

**Dependencies:**
- `config` — security thresholds
- `audit` — security events

**Dependents:**
- `auth` — brute-force protection
- `sessions` — IP binding
- `ecosystem` — plugin security scanning
- `developer` — API key security

---

### 3.24 `shared` — Shared Types & Utilities

**Layer:** Core
**Maturity:** Mature | **Version:** 1.x.x

**Purpose:** Shared data types, utility functions, base entities, and common abstractions.

**Public API:**
- Entity base classes (`BaseEntity`, `TimestampedEntity`)
- Utility functions (`paginate()`, `format_date()`, `hash_id()`)
- Shared type definitions
- Result/Either types

**Private Internals:**
- (minimal — mostly public API)

**Dependencies:**
- `config` — utility configuration

**Dependents:**
- (all modules — foundational types)

---

### 3.25 `config` — Configuration Module

**Layer:** Core
**Maturity:** Mature | **Version:** 1.x.x

**Purpose:** Configuration loading, validation, and access. Hierarchical settings with environment-aware overrides.

**Public API:**
- `get_config(namespace) → ConfigSection`
- `get_setting(key, default) → value`
- `validate_config() → ValidationResult`
- `reload_config() → void`

**Private Internals:**
- Config file reader
- Schema validator
- Environment variable resolver

**Dependencies:**
- (none — foundational module)

**Dependents:**
- (all modules — configuration access)

---

### 3.26 `reports` — Reporting Engine

**Layer:** Application
**Maturity:** Stable | **Version:** 3.x.x

**Purpose:** Report generation, export, scheduling, and template-based report rendering.

**Public API:**
- `ReportService.generate(template_id, data) → Report`
- `ReportService.schedule(schedule_config) → Schedule`
- `ReportService.export(report_id, format) → ExportResult`
- `ReportService.list_reports(filters) → ReportList`

**Private Internals:**
- Template engine
- PDF/CSV renderer
- Schedule executor

**Dependencies:**
- `users` — report owner
- `audit` — report events
- `config` — report defaults

**Dependents:**
- `analytics` — report integration
- `quality` — quality reports

---

## 4. Dependency Rules

### 4.1 Layer Dependency Matrix

Modules in a higher layer (lower number) may not depend on modules in a lower layer (higher number).

```
Layer 0 (Core):      config, shared, security, auth, users, sessions, audit
Layer 1 (Domain):    rules, policies, defense, attacks, standards
Layer 2 (Application): content, lms, simulation, developer, quality, production,
                       certification, reports, learning
Layer 3 (Infrastructure): ecosystem, optimization, analytics
Layer 4 (Presentation): collaboration, content_studio
```

**Rule:** A module may only depend on modules in the same layer or a lower-numbered layer.

### 4.2 Forbidden Dependencies

| From Layer | To Layer | Status |
|---|---|---|
| Core → Domain | Allowed |
| Core → Application | **Forbidden** |
| Core → Infrastructure | **Forbidden** |
| Core → Presentation | **Forbidden** |
| Domain → Application | **Forbidden** |
| Domain → Infrastructure | **Forbidden** |
| Domain → Presentation | **Forbidden** |
| Application → Infrastructure | Allowed |
| Application → Presentation | **Forbidden** |
| Infrastructure → Presentation | **Forbidden** |
| Presentation → Any higher layer | Allowed |

### 4.3 Circular Dependency Rule

No circular dependencies are permitted between modules. If module A depends on module B, module B must not depend on module A, either directly or transitively.

---

## 5. Anti-Corruption Layers

Modules with stable maturity must provide an anti-corruption layer (ACL) when integrating with experimental modules.

| ACL Owner | Protects Against | Implementation |
|---|---|---|
| `auth` | `learning` (experimental) | `LearningAuthAdapter` — translates auth events to learning domain language |
| `lms` | `content_studio` (experimental) | `ContentStudioAdapter` — normalizes content format from studio |
| `production` | `optimization` (experimental) | `OptimizationAdapter` — validates optimization recommendations |
| `defense` | `simulation` (experimental) | `SimulationDefenseAdapter` — sandboxed defense interaction |

**ACL Principles:**
1. The adapter lives in the stable module, not the experimental one.
2. The adapter maps external types to internal types.
3. The adapter handles version mismatches gracefully.
4. When the experimental module stabilizes, the ACL is removed.

---

## 6. Interface Contracts

### 6.1 Contract Format

Every module's public API must be documented with:

```python
# contracts/auth.py
class AuthServiceContract(Protocol):
    """Authentication service interface contract.
    
    Version: 1.2.0
    Stability: stable
    Breaking changes: None in 1.x
    """
    
    async def authenticate(self, credentials: Credentials) -> AuthResult:
        """Authenticate a user with the given credentials.
        
        Args:
            credentials: Authentication credentials (email + password).
        
        Returns:
            AuthResult with status, user_id, and optional session_token.
        
        Raises:
            AuthenticationError: Invalid credentials.
            RateLimitError: Too many attempts.
        
        Contract version: 1.2.0
        """
        ...
```

### 6.2 Contract Compliance

- Contract files live in `packages/<module>/contracts/`.
- Contracts are tested against implementations in `tests/contract/`.
- A contract violation fails the CI build.

---

## 7. Event Boundaries

### 7.1 Event Ownership

Each module owns the events it publishes. Other modules subscribe to events but may not modify them.

| Module | Events Published |
|---|---|
| `auth` | `auth.login.success`, `auth.login.failed`, `auth.logout`, `auth.register` |
| `users` | `users.created`, `users.updated`, `users.deleted`, `users.role_changed` |
| `sessions` | `sessions.created`, `sessions.expired`, `sessions.revoked` |
| `audit` | (consumes all events — does not publish) |
| `policies` | `policies.evaluated`, `policies.violated` |
| `defense` | `defense.blocked`, `defense.unblocked`, `defense.alert` |
| `simulation` | `simulation.started`, `simulation.completed`, `simulation.failed` |
| `content` | `content.published`, `content.archived` |
| `lms` | `lms.enrolled`, `lms.completed`, `lms.graded` |
| `developer` | `developer.api_key.created`, `developer.api_key.revoked` |
| `production` | `production.release.validated`, `production.feature.toggled` |
| `certification` | `certification.issued`, `certification.revoked` |

### 7.2 Event Schema

All events follow the schema defined in `packages/event-bus/contracts/event.py`:

```json
{
  "event_id": "uuid",
  "event_type": "auth.login.success",
  "timestamp": "ISO-8601",
  "source_module": "auth",
  "payload": { ... },
  "metadata": {
    "correlation_id": "uuid",
    "causation_id": "uuid",
    "version": "1.0"
  }
}
```

---

## 8. Data Ownership

Each module owns its data tables and schemas. No module may directly query another module's tables.

| Module | Owns Tables |
|---|---|
| `users` | `users`, `roles`, `permissions` |
| `sessions` | `sessions`, `session_tokens` |
| `audit` | `audit_logs`, `audit_events` |
| `auth` | `auth_credentials`, `mfa_secrets`, `password_history` |
| `policies` | `policies`, `policy_rules` |
| `rules` | `rules`, `rule_conditions` |
| `defense` | `defense_actions`, `blocked_sources` |
| `content` | `content`, `content_versions`, `content_metadata` |
| `lms` | `learning_paths`, `enrollments`, `progress`, `grades` |
| `simulation` | `scenarios`, `simulation_sessions`, `simulation_results` |
| `developer` | `api_keys`, `extensions`, `workflows` |
| `quality` | `quality_reports`, `check_results` |
| `production` | `feature_flags`, `releases`, `health_checks` |
| `ecosystem` | `plugins`, `submissions`, `reviews` |
| `certification` | `certifications`, `badges`, `exams` |
| `reports` | `reports`, `report_schedules` |

**Cross-module data access** is only permitted via:
1. The owning module's public API.
2. Events published by the owning module.
3. Read replicas exposed via dedicated query endpoints (with explicit permission).

---

## 9. Module Maturity Levels

| Level | Definition | Stability | Deprecation Policy |
|---|---|---|---|
| **Experimental** | May change without notice | Unstable | No commitment |
| **Stable** | API is stable; changes follow semver | Stable | 2 minor versions |
| **Mature** | Battle-tested, rarely changes | Very stable | 3 minor versions |
| **Deprecated** | Scheduled for removal | Frozen | Removed after window |

### 9.1 Maturity Promotion Criteria

| From | To | Criteria |
|---|---|---|
| Experimental → Stable | 6+ months, no breaking changes, full test coverage, 2+ external adopters |
| Stable → Mature | 12+ months, used in production, < 0.1% bug rate, full documentation |

---

## 10. Module Versioning Strategy

### 10.1 Version Format

```
MAJOR.MINOR.PATCH
```

- **MAJOR:** Breaking API changes (requires deprecation cycle).
- **MINOR:** New features, backward-compatible.
- **PATCH:** Bug fixes, no API changes.

### 10.2 Version Independence

Modules are versioned independently. A breaking change in `content` does not require a version bump in `auth`.

### 10.3 Cross-Module Version Pinning

Each module declares minimum compatible versions of its dependencies:

```json
{
  "dependencies": {
    "users": ">=1.2.0 <2.0.0",
    "audit": ">=1.0.0 <2.0.0"
  }
}
```

### 10.4 Wave Versioning

Release waves (V1.0, V3.0, etc.) are platform-level versions, not module-level versions. Modules may be at any version within a wave.

---

## 11. References

- [WORKSPACE_ARCHITECTURE.md](./WORKSPACE_ARCHITECTURE.md) — Workspace layout
- [SERVICE_COMMUNICATION.md](./SERVICE_COMMUNICATION.md) — Inter-module communication
- [DATA_FLOW.md](./DATA_FLOW.md) — Data lifecycle
- [DEPENDENCY_GRAPH.json](./DEPENDENCY_GRAPH.json) — Machine-readable dependency graph
- [MODULES.md](../architecture/MODULES.md) — Module overview
- [DECISIONS.md](../architecture/DECISIONS.md) — Architecture decisions
