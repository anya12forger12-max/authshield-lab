# Module Documentation

This document describes the purpose, components, and planned API endpoints for each module in AuthShield Lab.

---

## 1. Dashboard

### Purpose

The Dashboard serves as the central hub providing an at-a-glance overview of the entire platform. It aggregates data from all other modules to present key metrics, recent activity, and quick actions.

### Key Components

- **MetricsCards**: Display total users, active sessions, attack attempts, defense events
- **ActivityFeed**: Real-time stream of recent platform events
- **QuickActions**: Shortcuts to common operations (start attack, create user, view reports)
- **SystemStatus**: Backend health, database size, uptime
- **RecentAlerts**: Latest security alerts from defenses and audit
- **ChartsWidget**: Attack/defense trend visualization

### Dependencies

- Analytics module (metrics aggregation)
- Audit module (activity feed)
- Sessions module (active session count)
- Attacks module (recent attack data)
- Defenses module (defense event data)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard/metrics` | Aggregate platform metrics |
| GET | `/api/dashboard/activity` | Recent activity feed |
| GET | `/api/dashboard/alerts` | Active security alerts |
| GET | `/api/dashboard/status` | System health status |
| GET | `/api/dashboard/charts` | Trend data for charts |

### Data Models (Planned)

- `DashboardMetrics`: Aggregate counts and summaries
- `ActivityEvent`: Timestamped activity entry with actor and action
- `Alert`: Security alert with severity and status
- `SystemStatus`: Health check results

---

## 2. Authentication

### Purpose

Manages all authentication-related functionality including user login, registration, password management, token handling, and multi-factor authentication simulation.

### Key Components

- **LoginComponent**: Username/password login form
- **RegisterComponent**: New user registration
- **PasswordResetComponent**: Password recovery flow
- **MFASetupComponent**: TOTP authenticator enrollment
- **TokenManager**: JWT token lifecycle management
- **PasswordPolicy**: Configurable password complexity rules

### Dependencies

- Users module (user data)
- Sessions module (session creation)
- Audit module (login event logging)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | Authenticate user |
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/logout` | Invalidate session |
| POST | `/api/auth/refresh` | Refresh JWT token |
| POST | `/api/auth/password/change` | Change password |
| POST | `/api/auth/password/reset` | Request password reset |
| POST | `/api/auth/mfa/enable` | Enable MFA |
| POST | `/api/auth/mfa/verify` | Verify MFA code |
| GET | `/api/auth/mfa/status` | Check MFA enrollment |

### Data Models (Planned)

- `LoginRequest`: Username and password
- `TokenResponse`: Access and refresh tokens
- `PasswordPolicy`: Complexity requirements configuration
- `MFAConfig`: TOTP secret and recovery codes
- `PasswordResetToken`: Time-limited reset token

---

## 3. User Management

### Purpose

Handles the complete user lifecycle including creation, profile management, role assignment, and account deactivation. Provides the user directory for the platform.

### Key Components

- **UserList**: Searchable, filterable user directory
- **UserProfile**: User details and preferences
- **RoleManager**: Assign and modify user roles
- **UserCreation**: New user form with validation
- **BulkOperations**: Batch user import/export

### Dependencies

- Authentication module (user credentials)
- Audit module (user change logging)
- Sessions module (user session tracking)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/users` | List all users |
| GET | `/api/users/{id}` | Get user details |
| POST | `/api/users` | Create new user |
| PUT | `/api/users/{id}` | Update user |
| DELETE | `/api/users/{id}` | Deactivate user |
| PUT | `/api/users/{id}/role` | Change user role |
| GET | `/api/users/stats` | User statistics |

### Data Models (Planned)

- `User`: User entity with profile data
- `UserRole`: Role enum (student, instructor, admin, developer)
- `UserStats`: Registration and activity statistics

---

## 4. Session Management

### Purpose

Manages active user sessions, session history, and session-related security features. Provides tools for session monitoring and session-based attack simulations.

### Key Components

- **SessionList**: Active and historical sessions
- **SessionDetail**: Individual session information
- **SessionMonitor**: Real-time session activity
- **SessionRevoke**: Force session termination
- **SessionAnalytics**: Session duration and pattern analysis

### Dependencies

- Authentication module (token management)
- Users module (session ownership)
- Analytics module (session metrics)
- Audit module (session event logging)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/sessions` | List active sessions |
| GET | `/api/sessions/{id}` | Get session details |
| DELETE | `/api/sessions/{id}` | Revoke session |
| DELETE | `/api/sessions` | Revoke all sessions |
| GET | `/api/sessions/history` | Session history |
| GET | `/api/sessions/stats` | Session statistics |

### Data Models (Planned)

- `Session`: Active session with metadata
- `SessionHistory`: Historical session record
- `SessionStats`: Aggregated session metrics

---

## 5. Attack Simulations

### Purpose

Provides a comprehensive library of authentication attack simulations for educational purposes. Each attack is fully configurable with adjustable parameters and detailed logging.

### Key Components

- **AttackLibrary**: Catalog of available attack types
- **AttackConfigurator**: Parameter configuration for attacks
- **AttackExecutor**: Runs selected attack simulations
- **AttackResults**: Displays attack outcomes and analysis
- **AttackHistory**: Previous attack run records
- **CustomAttack**: User-defined attack scenario builder

### Supported Attacks

1. **Brute Force**: Sequential password guessing
2. **Credential Stuffing**: Known credential database testing
3. **Dictionary Attack**: Wordlist-based password cracking
4. **Password Spraying**: Common password testing across users
5. **Session Hijacking**: Token theft simulation
6. **SQL Injection**: Auth bypass via SQL injection
7. **XSS Attack**: Cross-site scripting for credential theft
8. **CSRF Attack**: Cross-site request forgery simulation
9. **Token Replay**: Reusing expired/invalid tokens
10. **Timing Attack**: Response time analysis

### Dependencies

- Users module (target accounts)
- Sessions module (session tokens)
- Defenses module (attack validation)
- Audit module (attack event logging)
- Analytics module (attack metrics)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/attacks` | List available attacks |
| GET | `/api/attacks/{id}` | Get attack details |
| POST | `/api/attacks/{id}/execute` | Run attack simulation |
| GET | `/api/attacks/{id}/results` | Get attack results |
| GET | `/api/attacks/history` | Attack run history |
| POST | `/api/attacks/custom` | Create custom attack |

### Data Models (Planned)

- `AttackType`: Attack type definition
- `AttackConfig`: Configuration parameters
- `AttackResult`: Execution results
- `AttackLog`: Detailed attack event log

---

## 6. Defense Mechanisms

### Purpose

Implements and demonstrates defensive security measures. Allows users to configure, test, and observe defense mechanisms in response to simulated attacks.

### Key Components

- **DefenseDashboard**: Overview of active defenses
- **RateLimiter**: Configurable rate limiting rules
- **AccountLockout**: Failed attempt threshold and lockout
- **IPBlocking**: IP-based access control simulation
- **WAFRules**: Web application firewall rule management
- **MFAEnforcement**: Require MFA for specific operations

### Supported Defenses

1. **Rate Limiting**: Request throttling per user/IP
2. **Account Lockout**: Temporary lock after failed attempts
3. **CAPTCHA**: Challenge-response verification
4. **IP Blocking**: Block suspicious IP addresses
5. **WAF Rules**: Web application firewall configuration
6. **Brute Force Detection**: Pattern-based detection
7. **Anomaly Detection**: Behavioral analysis
8. **MFA Enforcement**: Require multi-factor authentication

### Dependencies

- Attacks module (defense validation)
- Sessions module (session protection)
- Analytics module (defense metrics)
- Audit module (defense event logging)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/defenses` | List active defenses |
| PUT | `/api/defenses/{id}` | Update defense config |
| GET | `/api/defenses/{id}/events` | Defense trigger events |
| GET | `/api/defenses/stats` | Defense effectiveness stats |
| POST | `/api/defenses/test` | Test defense rules |

### Data Models (Planned)

- `DefenseRule`: Defense mechanism configuration
- `DefenseEvent`: Defense trigger record
- `DefenseStats`: Effectiveness metrics

---

## 7. Analytics

### Purpose

Collects, processes, and visualizes platform data for security insights. Provides real-time and historical analytics across all modules.

### Key Components

- **MetricsEngine**: Data collection and aggregation
- **ChartBuilder**: Interactive chart generation
- **FilterPanel**: Time range and category filtering
- **ExportService**: Data export to CSV/JSON
- **RealTimeFeed**: WebSocket-based live updates
- **TrendAnalyzer**: Pattern detection and forecasting

### Dependencies

- All modules (data collection)
- Reports module (report data)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/analytics/overview` | Platform overview metrics |
| GET | `/api/analytics/attacks` | Attack trend data |
| GET | `/api/analytics/defenses` | Defense effectiveness |
| GET | `/api/analytics/users` | User activity metrics |
| GET | `/api/analytics/sessions` | Session analytics |
| GET | `/api/analytics/trends` | Historical trend data |
| POST | `/api/analytics/export` | Export analytics data |

### Data Models (Planned)

- `AnalyticsOverview`: Platform-wide summary
- `TimeSeriesData`: Timestamped metric points
- `MetricAggregation`: Aggregated metric values

---

## 8. Reports

### Purpose

Generates comprehensive security reports from platform data. Supports multiple formats and customizable templates for different audiences.

### Key Components

- **ReportBuilder**: Configure report parameters
- **ReportTemplates**: Pre-built report templates
- **ReportGenerator**: PDF/HTML report generation
- **ReportHistory**: Previously generated reports
- **ScheduledReports**: Automated report generation
- **ExportManager**: Multi-format export

### Report Types

1. **Security Summary**: Overall security posture
2. **Attack Analysis**: Detailed attack simulation results
3. **Defense Effectiveness**: Defense mechanism performance
4. **User Activity**: User behavior and access patterns
5. **Compliance Report**: Regulatory compliance status
6. **Incident Report**: Security incident documentation

### Dependencies

- Analytics module (report data)
- Audit module (event details)
- Attacks module (attack results)
- Defenses module (defense events)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/reports` | List available reports |
| POST | `/api/reports/generate` | Generate new report |
| GET | `/api/reports/{id}` | Get report details |
| GET | `/api/reports/{id}/download` | Download report |
| DELETE | `/api/reports/{id}` | Delete report |
| GET | `/api/reports/templates` | List report templates |

### Data Models (Planned)

- `Report`: Report metadata and content
- `ReportTemplate`: Report configuration template
- `ReportSection`: Individual report section

---

## 9. Learning Center

### Purpose

Provides structured educational content for authentication security. Includes lessons, quizzes, hands-on exercises, and progress tracking.

### Key Components

- **CourseCatalog**: Browse available courses
- **LessonViewer**: Lesson content display
- **QuizEngine**: Interactive quiz system
- **ProgressTracker**: Learning progress dashboard
- **CertificateManager**: Course completion certificates
- **LabEnvironment**: Hands-on exercise sandbox

### Course Categories

1. **Fundamentals**: Authentication basics
2. **Attacks**: Understanding common attack vectors
3. **Defenses**: Implementing security measures
4. **Advanced Topics**: OAuth2, SAML, OIDC
5. **Incident Response**: Handling security events
6. **Compliance**: Regulatory requirements

### Dependencies

- Users module (learner profiles)
- Analytics module (learning metrics)
- Reports module (progress reports)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/learning/courses` | List courses |
| GET | `/api/learning/courses/{id}` | Get course details |
| GET | `/api/learning/lessons/{id}` | Get lesson content |
| POST | `/api/learning/quizzes/{id}/submit` | Submit quiz answers |
| GET | `/api/learning/progress` | Get learning progress |
| GET | `/api/learning/certificates` | List certificates |

### Data Models (Planned)

- `Course`: Course definition
- `Lesson`: Individual lesson content
- `Quiz`: Quiz with questions and answers
- `Progress`: User learning progress
- `Certificate`: Course completion certificate

---

## 10. Audit Trail

### Purpose

Maintains an immutable, comprehensive log of all platform activities. Supports investigation, compliance, and forensic analysis.

### Key Components

- **AuditLog**: Append-only event storage
- **EventFilter**: Advanced event search and filtering
- **EventDetail**: Individual event inspection
- **IntegrityChecker**: Log tampering detection
- **RetentionManager**: Log archival and cleanup

### Dependencies

- All modules (event source)
- Analytics module (audit metrics)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/audit/events` | List audit events |
| GET | `/api/audit/events/{id}` | Get event details |
| GET | `/api/audit/search` | Search audit events |
| GET | `/api/audit/stats` | Audit statistics |
| GET | `/api/audit/integrity` | Verify log integrity |
| DELETE | `/api/audit/events` | Purge old events (admin) |

### Data Models (Planned)

- `AuditEvent`: Single audit log entry
- `AuditSearch`: Advanced search parameters
- `AuditStats`: Event frequency analysis

---

## 11. Timeline

### Purpose

Provides a chronological view of platform events with forensics capabilities. Allows investigation of sequences of events and their relationships.

### Key Components

- **TimelineView**: Chronological event display
- **EventCorrelator**: Link related events
- **ForensicsMode**: Detailed event analysis
- **ReplayEngine**: Reconstruct event sequences
- **FilterBar**: Time range and event type filtering

### Dependencies

- Audit module (event data)
- Analytics module (timeline metrics)
- Sessions module (session events)
- Attacks module (attack events)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/timeline` | Get timeline events |
| GET | `/api/timeline/{id}` | Get event context |
| GET | `/api/timeline/correlate` | Find related events |
| GET | `/api/timeline/replay` | Reconstruct sequence |

### Data Models (Planned)

- `TimelineEvent`: Event with temporal context
- `EventGroup`: Related event cluster
- `EventRelationship`: Links between events

---

## 12. Settings

### Purpose

Platform-wide configuration management. Allows administrators to customize behavior, security policies, and user preferences.

### Key Components

- **GeneralSettings**: Application name, theme, language
- **SecuritySettings**: Password policy, session timeout, MFA
- **NotificationSettings**: Alert and notification preferences
- **BackupSettings**: Database backup configuration
- **AppearanceSettings**: Theme, font size, accessibility

### Dependencies

- Configuration module (settings storage)
- All modules (settings application)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/settings` | Get all settings |
| PUT | `/api/settings/{key}` | Update setting |
| POST | `/api/settings/reset` | Reset to defaults |
| GET | `/api/settings/export` | Export configuration |
| POST | `/api/settings/import` | Import configuration |

### Data Models (Planned)

- `Setting`: Key-value configuration entry
- `SecurityConfig`: Security-related settings
- `AppearanceConfig`: UI customization settings

---

## 13. Help

### Purpose

Provides in-app documentation, troubleshooting guides, and support resources. Includes interactive tutorials and contextual help.

### Key Components

- **DocumentationBrowser**: Searchable documentation viewer
- **InteractiveTutorial**: Guided platform walkthrough
- **Troubleshooter**: Common issue resolution
- **KeyboardShortcuts**: Shortcut reference
- **AboutDialog**: Version and build information
- **FeedbackForm**: Issue reporting form

### Dependencies

- Configuration module (help content storage)
- Users module (tutorial progress)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/help/docs` | List documentation |
| GET | `/api/help/docs/{id}` | Get document |
| GET | `/api/help/shortcuts` | Keyboard shortcuts |
| GET | `/api/help/faq` | Frequently asked questions |
| POST | `/api/help/feedback` | Submit feedback |

### Data Models (Planned)

- `HelpDocument`: Documentation entry
- `FAQItem`: Frequently asked question
- `ShortcutGroup`: Keyboard shortcut category

---

## 14. Vulnerability Scanner

### Purpose

Identifies and catalogs authentication vulnerabilities in the simulated environment. Provides remediation guidance for discovered issues.

### Key Components

- **ScanEngine**: Automated vulnerability detection
- **VulnerabilityCatalog**: Known vulnerability database
- **ScanResults**: Detailed findings with severity
- **RemediationGuide**: Fix recommendations
- **ScanHistory**: Previous scan results

### Dependencies

- Authentication module (auth vulnerability checks)
- Users module (user configuration checks)
- Sessions module (session security checks)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/scanner/scan` | Start vulnerability scan |
| GET | `/api/scanner/results` | Get scan results |
| GET | `/api/scanner/vulnerabilities` | List known vulnerabilities |
| GET | `/api/scanner/{id}/remediation` | Get fix guidance |

### Data Models (Planned)

- `Vulnerability`: Identified security issue
- `ScanResult`: Scan execution results
- `RemediationStep`: Fix instruction

---

## 15. Credential Vault

### Purpose

Simulates encrypted credential storage with access controls. Demonstrates secure credential management best practices.

### Key Components

- **VaultInterface**: Secure credential entry
- **AccessControl**: Per-credential access rules
- **EncryptionEngine**: AES-256 encryption simulation
- **CredentialRotation**: Automatic password rotation
- **AuditTrail**: Vault access logging

### Dependencies

- Authentication module (encryption keys)
- Users module (access permissions)
- Audit module (vault access logging)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/vault/credentials` | List credentials |
| POST | `/api/vault/credentials` | Store credential |
| GET | `/api/vault/credentials/{id}` | Retrieve credential |
| DELETE | `/api/vault/credentials/{id}` | Delete credential |
| POST | `/api/vault/rotate/{id}` | Rotate credential |

### Data Models (Planned)

- `VaultCredential`: Encrypted credential entry
- `AccessPolicy`: Access control rules
- `RotationPolicy`: Rotation schedule configuration

---

## 16. Network Monitor

### Purpose

Monitors and displays local network traffic related to the platform. Visualizes HTTP requests, WebSocket connections, and IPC communication.

### Key Components

- **TrafficInspector**: Real-time request/response viewer
- **ConnectionMap**: Visual network topology
- **PacketAnalyzer**: Request/response detail inspection
- **FilterEngine**: Protocol and endpoint filtering
- **ExportCapture**: Save traffic captures

### Dependencies

- Backend API (HTTP traffic)
- Electron IPC (IPC communication)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/network/connections` | Active connections |
| GET | `/api/network/traffic` | Recent traffic |
| GET | `/api/network/stats` | Traffic statistics |
| POST | `/api/network/capture` | Start traffic capture |

### Data Models (Planned)

- `NetworkConnection`: Active connection details
- `TrafficEntry`: Single request/response pair
- `TrafficStats`: Aggregate traffic metrics

---

## 17. Incident Response

### Purpose

Provides IR playbook execution and tracking for security incidents. Guides users through standardized response procedures.

### Key Components

- **PlaybookLibrary**: IR playbook catalog
- **PlaybookExecutor**: Step-by-step playbook runner
- **IncidentTracker**: Active incident management
- **CommunicationLog**: Team communication records
- **PostMortem**: Incident review templates

### Dependencies

- Audit module (incident evidence)
- Timeline module (event correlation)
- Reports module (incident reports)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/incidents` | List incidents |
| POST | `/api/incidents` | Create incident |
| PUT | `/api/incidents/{id}` | Update incident |
| GET | `/api/incidents/{id}/playbook` | Get playbook |
| POST | `/api/incidents/{id}/step` | Execute playbook step |

### Data Models (Planned)

- `Incident`: Security incident record
- `Playbook`: IR playbook definition
- `PlaybookStep`: Individual response step

---

## 18. Threat Intelligence

### Purpose

Manages Indicators of Compromise (IoCs) and simulated threat feeds. Provides context for attack simulations.

### Key Components

- **IoCCatalog**: Indicators of compromise database
- **ThreatFeedSim**: Simulated threat intelligence feeds
- **CorrelationEngine**: Match IoCs with observed activity
- **AlertGenerator**: IoC-triggered alerts
- **EnrichmentService**: IoC context enrichment

### Dependencies

- Attacks module (attack IoCs)
- Audit module (observed activity)
- Analytics module (correlation metrics)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/threats/iocs` | List IoCs |
| POST | `/api/threats/iocs` | Add IoC |
| GET | `/api/threats/feeds` | List threat feeds |
| GET | `/api/threats/correlate` | Correlate with activity |
| GET | `/api/threats/alerts` | IoC-triggered alerts |

### Data Models (Planned)

- `IoC`: Indicator of Compromise
- `ThreatFeed`: Threat intelligence feed source
- `CorrelationMatch`: IoC-activity match

---

## 19. Compliance Checker

### Purpose

Validates platform configurations against regulatory compliance standards including SOX, HIPAA, PCI-DSS, and GDPR.

### Key Components

- **ComplianceEngine**: Rule-based compliance checking
- **StandardLibrary**: Compliance requirement database
- **CheckResults**: Compliance check outcomes
- **GapAnalysis**: Non-compliance identification
- **ComplianceReport**: Compliance documentation

### Supported Standards

1. **SOX**: Sarbanes-Oxley access controls
2. **HIPAA**: Healthcare data protection
3. **PCI-DSS**: Payment card security
4. **GDPR**: Data privacy requirements
5. **NIST CSF**: Cybersecurity framework

### Dependencies

- Settings module (configuration)
- Users module (access controls)
- Audit module (compliance evidence)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/compliance/standards` | List standards |
| POST | `/api/compliance/check` | Run compliance check |
| GET | `/api/compliance/results` | Check results |
| GET | `/api/compliance/gaps` | Non-compliance gaps |
| GET | `/api/compliance/report` | Generate report |

### Data Models (Planned)

- `ComplianceStandard`: Standard definition
- `ComplianceCheck`: Individual requirement check
- `ComplianceResult`: Check outcome

---

## 20. API Security

### Purpose

Tests and validates OAuth2/OIDC flows, API key management, and API endpoint security. Provides hands-on API security training.

### Key Components

- **OAuth2Tester**: OAuth2 flow simulation
- **OIDCDemo**: OpenID Connect implementation
- **APIKeyManager**: API key lifecycle management
- **EndpointTester**: API security testing tools
- **TokenInspector**: JWT token analysis

### Dependencies

- Authentication module (auth flows)
- Sessions module (token management)
- Users module (API permissions)

### API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/api-security/oauth2` | OAuth2 flow status |
| POST | `/api/api-security/oauth2/test` | Test OAuth2 flow |
| GET | `/api/api-security/keys` | List API keys |
| POST | `/api/api-security/keys` | Generate API key |
| DELETE | `/api/api-security/keys/{id}` | Revoke API key |
| POST | `/api/api-security/test` | Run security test |

### Data Models (Planned)

- `OAuth2Config`: OAuth2 client configuration
- `APIKey`: API key with metadata
- `SecurityTest`: API security test definition
