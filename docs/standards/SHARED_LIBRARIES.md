# AuthShield Lab — Shared Library Architecture

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab is decomposed into shared libraries that provide reusable, well-defined capabilities. Each library has a single responsibility, a stable public API, and follows semantic versioning. Libraries are consumed by the backend, frontend (via TypeScript type equivalents), and plugins.

---

## 2. auth-core

### 2.1 Responsibilities

- Authentication flows: login, logout, session management
- Password hashing: Argon2id (primary), bcrypt (legacy), PBKDF2 (fallback)
- Session management: JWT creation/validation, token refresh, revocation
- Multi-factor authentication: TOTP (RFC 6238), backup codes
- Rate limiting: login attempt throttling, brute-force protection
- Account lockout: configurable lockout policies

### 2.2 Public API Sketch

```python
from authshield.auth_core import (
    AuthService,
    PasswordHasher,
    SessionManager,
    MFAManager,
    RateLimiter,
)
from authshield.auth_core.models import (
    User,
    Session,
    MFAToken,
    LoginAttempt,
)
from authshield.auth_core.types import (
    AuthResult,
    SessionToken,
    PasswordStrength,
)

# Password hashing
hasher = PasswordHasher(algorithm="argon2id")
hashed = hasher.hash("user_password")
verified = hasher.verify("user_password", hashed)

# Authentication
auth = AuthService(db=session)
result: AuthResult = await auth.authenticate(
    username="user@example.com",
    password="user_password",
    ip_address="192.168.1.1",
)

# Session management
session_mgr = SessionManager(secret_key="...", algorithm="HS256")
token: SessionToken = session_mgr.create_session(user_id="user_123")
user = session_mgr.validate_session(token)
session_mgr.revoke_session(token)

# MFA
mfa = MFAManager()
secret = mfa.generate_secret()
uri = mfa.get_provisioning_uri(secret, "user@example.com", "AuthShield Lab")
verified = mfa.verify_token(secret, "123456")
backup_codes = mfa.generate_backup_codes(count=10)
```

### 2.3 Internal Dependencies

- `cryptography` (password hashing primitives, Ed25519 for MFA secrets)
- `python-jose` (JWT creation/validation)
- `argon2-cffi` (Argon2id hashing)
- `passlib` (password hashing abstraction)
- `sqlalchemy` (session/user persistence)
- `structlog` (logging)

### 2.4 Versioning

- Current: 1.0.0
- Stability: Stable
- Breaking changes: Major version bump
- Deprecated APIs: 6-month warning before removal

---

## 3. crypto

### 3.1 Responsibilities

- Digital signatures: Ed25519 (primary), RSA-PSS (fallback)
- Integrity hashing: SHA-256 for file/document integrity
- Key management: key generation, storage, rotation, revocation
- Certificate management: self-signed certificate generation, validation
- Fernet symmetric encryption: encrypt/decrypt sensitive data at rest
- Checksum generation: SHA-256/SHA-512 file checksums

### 3.2 Public API Sketch

```python
from authshield.crypto import (
    DigitalSignature,
    IntegrityHasher,
    KeyManager,
    CertificateManager,
    SymmetricEncryptor,
)
from authshield.crypto.types import (
    KeyPair,
    Signature,
    Checksum,
    Certificate,
)

# Digital signatures
signer = DigitalSignature(algorithm="ed25519")
key_pair: KeyPair = signer.generate_keypair()
signature: Signature = signer.sign(b"data to sign", key_pair.private_key)
valid = signer.verify(b"data to sign", signature, key_pair.public_key)

# Integrity hashing
hasher = IntegrityHasher(algorithm="sha256")
checksum: Checksum = hasher.hash_file("/path/to/file")
valid = hasher.verify_file("/path/to/file", checksum)

# Key management
km = KeyManager(storage_path="/path/to/keys")
km.generate_keypair(name="release-signing", algorithm="ed25519")
key = km.load_key("release-signing")
km.rotate_key("release-signing")

# Certificate management
cm = CertificateManager()
cert: Certificate = cm.generate_self_signed(
    subject="authshield-lab",
    valid_days=365,
    key_algorithm="ed25519",
)

# Symmetric encryption
enc = SymmetricEncryptor()
encrypted = enc.encrypt(b"sensitive data", key="user-provided-key")
decrypted = enc.decrypt(encrypted, key="user-provided-key")
```

### 3.3 Internal Dependencies

- `cryptography` (all cryptographic primitives)
- `pathlib` (key storage)
- `structlog` (audit logging for key operations)
- `sqlalchemy` (key metadata persistence)

### 3.4 Versioning

- Current: 1.0.0
- Stability: Stable
- Breaking changes: Major version bump (cryptographic API changes are rare)
- Algorithm deprecation: 12-month warning; migration helper provided

---

## 4. a11y-engine

### 4.1 Responsibilities

- WCAG 2.2 AA validation (automated rules)
- Accessibility scoring: numeric score (0-100) with breakdown
- Keyboard navigation helpers: focus management, tab order utilities
- Screen reader compatibility: ARIA label generation, live region management
- High contrast detection: CSS custom property validation
- Reduced motion support: `prefers-reduced-motion` detection
- Accessibility audit report generation

### 4.2 Public API Sketch

```python
from authshield.a11y_engine import (
    WCAGValidator,
    AccessibilityScorer,
    KeyboardNavigator,
    ScreenReaderHelper,
)
from authshield.a11y_engine.types import (
    ValidationResult,
    Violation,
    Score,
    WCAGLevel,
)

# WCAG validation
validator = WCAGValidator(level=WCAGLevel.AA)
result: ValidationResult = validator.validate_html(html_content)
result = validator.validate_url("http://localhost:3000/dashboard")

# Accessibility scoring
scorer = AccessibilityScorer()
score: Score = scorer.score_component(my_react_component)
# Score(total=87, critical=2, serious=5, moderate=12, minor=8)

# Keyboard navigation
nav = KeyboardNavigator()
focus_order = nav.get_focus_order(html_content)
tab_trap = nav.create_focus_trap(element)
skip_links = nav.generate_skip_links(["main", "sidebar", "footer"])

# Screen reader helpers
sr = ScreenReaderHelper()
aria_label = sr.generate_label(element, context="navigation")
live_region = sr.create_live_region(message="Form submitted", polite=True)
```

### 4.3 Internal Dependencies

- `axe-core` (automated WCAG rule engine; bundled JS executed via subprocess or WASM)
- `jinja2` (HTML template parsing)
- `structlog` (violation logging)
- `sqlalchemy` (audit trail persistence)

### 4.4 Versioning

- Current: 1.0.0
- Stability: Stable
- WCAG version tracking: Updates when WCAG specification is revised
- Rule additions: Minor version bump; no breaking changes

---

## 5. localization-engine

### 5.1 Responsibilities

- Translation loading: JSON-based translation files
- Key lookup: dot-notation key resolution with fallback chain
- Plural rules: CLDR-based one/other/few/many/other forms
- Date formatting: locale-specific date/time/dateTime/relative formats
- Number formatting: locale-specific decimal, currency, percent, scientific
- RTL support: right-to-left layout detection and mirroring
- Translation completeness: per-locale completeness scoring
- Fallback chains: locale → regional → language → English (default)

### 5.2 Public API Sketch

```python
from authshield.localization_engine import (
    Translator,
    DateFormatter,
    NumberFormatter,
    RTLHelper,
    CompletenessChecker,
)
from authshield.localization_engine.types import (
    TranslationResult,
    Locale,
    PluralForm,
)

# Translation
translator = Translator(
    translation_dir="translations/",
    default_locale="en",
    fallback_chain=["te", "hi", "en"],
)
result: TranslationResult = translator.translate(
    "dashboard.welcome.message",
    locale="te",
    context={"user_name": "Alice"},
)

# Plural forms
msg = translator.translate_plural(
    key="dashboard.alerts.count",
    count=5,
    locale="te",
)
# "5 alerts" in English; CLDR rules for Telugu

# Date formatting
df = DateFormatter(locale="hi")
formatted = df.format_date(datetime.now(), style="long")
# "19 जुलाई 2026"
relative = df.format_relative(datetime.now() - timedelta(hours=2))
# "2 hours ago" in Hindi

# Number formatting
nf = NumberFormatter(locale="de")
formatted = nf.format_number(1234567.89)
# "1.234.567,89" (German grouping)
currency = nf.format_currency(42.50, currency="EUR")
# "42,50 €"

# RTL
rtl = RTLHelper()
is_rtl = rtl.is_rtl("ar")  # True
mirrored_css = rtl.get_logical_properties("margin-left", "1rem")
# Returns "margin-inline-start: 1rem"

# Completeness
checker = CompletenessChecker(translation_dir="translations/")
score = checker.check_locale("te")
# CompletenessScore(translated=450, total=500, percentage=90.0)
missing = checker.get_missing_keys("te")
```

### 5.3 Internal Dependencies

- `babel` (CLDR data, date/number formatting)
- `json` (translation file parsing)
- `pathlib` (file system operations)
- `structlog` (missing key warnings)

### 5.4 Versioning

- Current: 1.0.0
- Stability: Stable
- CLDR updates: Follow Unicode CLDR releases (2-3 per year)
- New locale additions: Minor version bump

---

## 6. simulation-engine

### 6.1 Responsibilities

- Synthetic data generation: realistic user/activity/network data
- Scenario execution: step-by-step lab scenario playback
- Timeline management: event ordering, time acceleration, pause/resume
- Attack simulation: phishing, brute force, privilege escalation patterns
- Defense simulation: IDS alerts, firewall rules, incident response
- Network topology: simulated network graphs with hosts/services
- Result capture: action logs, detection timestamps, response metrics

### 6.2 Public API Sketch

```python
from authshield.simulation_engine import (
    ScenarioRunner,
    DataGenerator,
    Timeline,
    NetworkSimulator,
    AttackSimulator,
    DefenseSimulator,
)
from authshield.simulation_engine.types import (
    Scenario,
    ScenarioResult,
    TimelineEvent,
    NetworkTopology,
    AttackStep,
)

# Scenario execution
runner = ScenarioRunner(db=session)
scenario = runner.load("phishing-response")
result: ScenarioResult = await runner.execute(
    scenario=scenario,
    user_id="user_123",
    time_acceleration=10.0,  # 10x speed
)

# Data generation
gen = DataGenerator(seed=42)
users = gen.generate_users(count=100)
activities = gen.generate_activities(users, days=30)
network = gen.generate_network(hosts=50)

# Timeline management
timeline = Timeline()
timeline.add_event(TimelineEvent(timestamp=..., action="login", source="10.0.0.1"))
timeline.add_event(TimelineEvent(timestamp=..., action="failed_login", source="10.0.0.5"))
timeline.pause()
timeline.resume()
timeline.set_speed(2.0)

# Attack simulation
attack = AttackSimulator()
phishing = attack.create_phishing_scenario(target_users=["user_123"])
brute_force = attack.create_brute_force(target_service="ssh", duration_minutes=5)
priv_esc = attack.create_privilege_escalation(initial_role="user", target_role="admin")

# Defense simulation
defense = DefenseSimulator()
ids_alert = defense.detect_brute_force(logs=activity_logs)
firewall = defense.block_ip("10.0.0.5")
incident = defense.create_incident(severity="high", description="...")
```

### 6.3 Internal Dependencies

- `faker` (synthetic data generation)
- `networkx` (network topology graphs)
- `sqlalchemy` (scenario/result persistence)
- `asyncio` (concurrent scenario execution)
- `structlog` (scenario logging)
- `json` (scenario definition files)

### 6.4 Versioning

- Current: 1.0.0
- Stability: Stable
- Scenario format: JSON-based, versioned; backward-compatible additions
- Breaking changes: Major version bump; scenario migration tool provided

---

## 7. learning-engine

### 7.1 Responsibilities

- Knowledge state tracking: per-user knowledge graph
- Adaptive pathways: dynamic content recommendation based on mastery
- Spaced repetition: SM-2 algorithm for review scheduling
- Assessment engine: question banks, scoring, rubric-based grading
- Progress tracking: module completion, skill badges, certificates
- Learning analytics: engagement metrics, difficulty calibration

### 7.2 Public API Sketch

```python
from authshield.learning_engine import (
    KnowledgeTracker,
    AdaptivePathway,
    SpacedRepetition,
    AssessmentEngine,
    ProgressTracker,
    LearningAnalytics,
)
from authshield.learning_engine.types import (
    KnowledgeState,
    LearningPath,
    ReviewSchedule,
    Assessment,
    AssessmentResult,
    ProgressReport,
)

# Knowledge tracking
tracker = KnowledgeTracker(db=session)
state: KnowledgeState = tracker.get_state(user_id="user_123")
tracker.record_interaction(
    user_id="user_123",
    concept="sql_injection",
    result="correct",
    difficulty=0.7,
    response_time_ms=4500,
)

# Adaptive pathways
pathway = AdaptivePathway(db=session)
path: LearningPath = pathway.get_next_modules(
    user_id="user_123",
    current_module="authentication_basics",
)

# Spaced repetition
sr = SpacedRepetition()
schedule: ReviewSchedule = sr.schedule_review(
    concept="xss_prevention",
    last_review=datetime.now() - timedelta(days=3),
    difficulty=0.6,
    correct_streak=4,
)

# Assessment engine
assess = AssessmentEngine(db=session)
assessment: Assessment = assess.get_assessment("phishing_awareness_101")
result: AssessmentResult = await assess.grade(
    assessment=assessment,
    user_id="user_123",
    answers=submitted_answers,
)

# Progress tracking
progress = ProgressTracker(db=session)
report: ProgressReport = progress.get_report(user_id="user_123")
completion = progress.get_module_completion(user_id="user_123", module_id="auth_basics")

# Learning analytics
analytics = LearningAnalytics(db=session)
engagement = analytics.get_engagement_metrics(user_id="user_123", period_days=30)
difficulty = analytics.calibrate_difficulty(module_id="auth_basics")
```

### 7.3 Internal Dependencies

- `sqlalchemy` (knowledge state, assessment, progress persistence)
- `datetime` (spaced repetition scheduling)
- `math` (SM-2 algorithm calculations)
- `structlog` (learning event logging)
- `json` (assessment/question bank files)

### 7.4 Versioning

- Current: 1.0.0
- Stability: Stable
- SM-2 algorithm: Standard implementation; parameter tuning via minor version
- Assessment format: JSON-based, versioned

---

## 8. ui-components

### 8.1 Responsibilities

- Shared React component library (desktop Electron and web deployment)
- Design system: consistent spacing, typography, color tokens
- Accessibility: built-in ARIA support, keyboard navigation
- Theme system: light/dark/high-contrast themes via CSS custom properties
- Common components: buttons, inputs, modals, tables, charts, alerts
- Layout components: sidebar, header, content area, responsive grid

### 8.2 Public API Sketch

```tsx
// React components
import {
  Button,
  Input,
  Select,
  Modal,
  DataTable,
  Alert,
  Card,
  Sidebar,
  Header,
  ThemeProvider,
  useTheme,
  useA11y,
} from "@authshield/ui-components";

// Button with accessibility
<Button
  variant="primary"
  size="md"
  aria-label="Submit assessment"
  onClick={handleSubmit}
>
  Submit
</Button>

// DataTable with sorting, filtering, pagination
<DataTable
  columns={[
    { key: "name", label: "Name", sortable: true },
    { key: "score", label: "Score", sortable: true, align: "right" },
    { key: "date", label: "Date", sortable: true },
  ]}
  data={assessmentResults}
  pagination={{ pageSize: 20 }}
  aria-label="Assessment results"
/>

// Modal with focus management
<Modal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  title="Confirm Submission"
  aria-describedby="modal-description"
>
  <p id="modal-description">Are you sure you want to submit?</p>
</Modal>

// Theme provider
<ThemeProvider defaultTheme="system">
  <App />
</ThemeProvider>

// Theme hook
const { theme, setTheme, resolvedTheme } = useTheme();

// A11y hook
const { announce, getFocusTrap } = useA11y();
announce("Form submitted successfully", "polite");
```

### 8.3 Internal Dependencies

- `react` (UI framework)
- `react-dom` (DOM rendering)
- `react-router-dom` (routing)
- `zustand` (lightweight state management)
- CSS custom properties (theme tokens, no CSS-in-JS dependency)

### 8.4 Versioning

- Current: 1.0.0
- Stability: Stable
- Component API: Follows React component patterns
- Breaking changes: Major version bump; migration codemod provided
- Theme tokens: Semantic versioning; new tokens are minor, renamed tokens are major

---

## 9. utils

### 9.1 Responsibilities

- Date helpers: formatting, parsing, timezone conversion, relative time
- Validation helpers: email, IP address, URL, UUID, password strength
- ID generation: UUID v4, ULID (time-ordered), nanoID
- String utilities: slugification, truncation, sanitization
- Collection helpers: deep merge, pick/omit, groupBy, unique
- Error handling: custom exception types, error aggregation
- Retry logic: exponential backoff, circuit breaker pattern

### 9.2 Public API Sketch

```python
from authshield.utils import (
    DateHelper,
    Validators,
    IDGenerator,
    StringHelper,
    CollectionHelper,
    RetryHelper,
    ErrorCode,
    ErrorResponse,
)

# Date helpers
dh = DateHelper()
formatted = dh.format_iso(datetime.now())
relative = dh.relative_time(datetime.now() - timedelta(hours=3))
localized = dh.format_locale(datetime.now(), locale="hi", style="long")

# Validators
v = Validators()
v.email("user@example.com")  # True
v.ip_address("192.168.1.1")  # True
v.url("https://example.com")  # True
v.password_strength("P@ssw0rd!2024")  # PasswordStrength.STRONG

# ID generation
id_gen = IDGenerator()
uuid = id_gen.uuid4()  # "550e8400-e29b-41d4-a716-446655440000"
ulid = id_gen.ulid()  # "01H2X3Y4Z5A6B7C8D9E0F1G2H"
short = id_gen.nanoid(length=12)  # "aB3kL9mN2pQ7"

# String utilities
sh = StringHelper()
sh.slugify("Hello World!")  # "hello-world"
sh.truncate("Long text...", max_length=20)  # "Long text..."
sh.sanitize("<script>alert('xss')</script>")  # "&lt;script&gt;...&lt;/script&gt;"

# Collection helpers
ch = CollectionHelper()
merged = ch.deep_merge(dict_a, dict_b)
grouped = ch.group_by(items, key="category")
unique = ch.unique_by(items, key="id")

# Retry helper
retry = RetryHelper(max_attempts=3, backoff_factor=2.0)
result = await retry.execute(lambda: unstable_api_call())
```

### 9.3 Internal Dependencies

- Minimal stdlib dependencies only (no external dependencies)
- `re` (regex for validators)
- `uuid` (UUID generation)
- `datetime` (date helpers)
- `hashlib` (hash-based ID generation)

### 9.4 Versioning

- Current: 1.0.0
- Stability: Stable
- API additions: Minor version bump
- Breaking changes: Major version bump (rare; utility functions are stable)

---

## 10. config

### 10.1 Responsibilities

- Configuration loading: TOML, YAML, JSON, environment variables
- Settings hierarchy: built-in → global → institution → project → user → env → CLI
- Settings validation: Pydantic `BaseSettings` integration
- Configuration migration: version-aware schema migration
- Configuration backup: automatic backup before migration
- Configuration recovery: restore from backup
- Secret handling: `SecretStr` for sensitive values, environment variable binding

### 10.2 Public API Sketch

```python
from authshield.config import (
    ConfigManager,
    Settings,
    ConfigMigration,
)
from authshield.config.types import (
    AppConfig,
    ConfigSource,
    MigrationResult,
)

# Configuration loading
config = ConfigManager(
    app_name="authshield-lab",
    config_dir=Path("~/.config/authshield-lab"),
    env_prefix="AUTHSHIELD_",
)
settings: AppConfig = config.load()

# Settings access
print(settings.database.url)
print(settings.server.host)
print(settings.security.session_timeout)

# Configuration migration
migration = ConfigMigration(db=session)
result: MigrationResult = migration.migrate(
    from_version="0.9.0",
    to_version="1.0.0",
    config_path=Path("~/.config/authshield-lab/config.toml"),
)
# Creates backup, applies migrations, validates result

# Backup and recovery
config.backup()
config.restore(backup_path=Path("~/.config/authshield-lab/backups/config.2026-07-19.toml"))
```

### 10.3 Internal Dependencies

- `pydantic-settings` (settings validation)
- `tomllib` (TOML parsing, Python 3.11+)
- `yaml` (YAML parsing, optional)
- `json` (JSON parsing)
- `pathlib` (file system operations)
- `structlog` (configuration logging)

### 10.4 Versioning

- Current: 1.0.0
- Stability: Stable
- Config schema versioning: Major version for schema breaking changes
- Migration scripts: Provided for each major version upgrade

---

## 11. logging

### 11.1 Responsibilities

- Structured logging: JSON-formatted log output
- Log rotation: daily rotation, configurable retention
- Log compression: gzip compression for rotated logs
- Diagnostic bundles: collect logs, config, system info into archive
- Log redaction: configurable sensitive field patterns
- Log levels: per-module configurable levels
- Performance logging: timing decorators, metric aggregation

### 11.2 Public API Sketch

```python
from authshield.logging import (
    LogManager,
    DiagnosticBundle,
    RedactionFilter,
    PerformanceLogger,
)

# Log manager setup
lm = LogManager(
    app_name="authshield-lab",
    log_dir=Path("~/.local/share/authshield-lab/logs"),
    default_level="INFO",
    rotation="daily",
    retention_days=30,
    compress_rotated=True,
)
logger = lm.get_logger("authshield.auth")

# Structured logging
logger.info("user.login", user_id="user_123", ip="192.168.1.1")
logger.warning("session.expired", user_id="user_123", session_id="sess_abc")
logger.error("auth.failed", username="user@example.com", reason="invalid_password")

# Redaction
redactor = RedactionFilter(patterns=["password", "secret", "token", "api_key"])
redacted = redactor.redact(log_entry)
# {"password": "[REDACTED]", "token": "[REDACTED]"}

# Diagnostic bundle
bundle = DiagnosticBundle(log_dir=Path("~/.local/share/authshield-lab/logs"))
archive_path = bundle.create(
    include_logs=True,
    include_config=True,
    include_system_info=True,
    output_path=Path("/tmp/diagnostic-bundle.tar.gz"),
)

# Performance logging
perf = PerformanceLogger(logger)
@perf.measure("api.assessment.grade")
async def grade_assessment(assessment_id: str):
    # ... grading logic ...
    pass
# Logs: {"event": "api.assessment.grade", "duration_ms": 150, "status": "success"}
```

### 11.3 Internal Dependencies

- `structlog` (structured logging framework)
- `python-json-logger` (fallback JSON formatter)
- `pathlib` (log file management)
- `gzip` (log compression)
- `tarfile` (diagnostic bundles)
- `platform` (system info collection)

### 11.4 Versioning

- Current: 1.0.0
- Stability: Stable
- Log format: Stable JSON schema
- Redaction patterns: Configurable, no version coupling

---

## 12. reporting

### 12.1 Responsibilities

- Template engine: Jinja2-based report generation
- PDF generation: HTML → PDF via WeasyPrint
- CSV export: tabular data export with locale-aware formatting
- JSON export: structured data export
- Report scheduling: on-demand or scheduled generation
- Report archiving: versioned report storage
- Report distribution: export to file, print, or email

### 12.2 Public API Sketch

```python
from authshield.reporting import (
    ReportEngine,
    PDFExporter,
    CSVExporter,
    JSONExporter,
    ReportScheduler,
    ReportArchive,
)
from authshield.reporting.types import (
    Report,
    ReportConfig,
    ExportResult,
    ScheduledReport,
)

# Report generation
engine = ReportEngine(
    template_dir="templates/reports/",
    output_dir=Path("~/.local/share/authshield-lab/reports"),
)

# PDF export
pdf = PDFExporter(engine)
result: ExportResult = pdf.export(
    template="assessment_report.html",
    context={
        "user": user,
        "assessment": assessment,
        "results": results,
        "generated_at": datetime.now(),
    },
    output_path=Path("/tmp/report.pdf"),
)

# CSV export
csv = CSVExporter()
result = csv.export(
    data=assessment_results,
    columns=["user", "score", "date", "module"],
    output_path=Path("/tmp/results.csv"),
    locale="en",
)

# JSON export
json_exp = JSONExporter()
result = json_exp.export(
    data=assessment_results,
    output_path=Path("/tmp/results.json"),
    indent=2,
)

# Report archiving
archive = ReportArchive(db=session)
archive.store(report_path=Path("/tmp/report.pdf"), metadata={...})
reports = archive.list(user_id="user_123", module_id="auth_basics")
```

### 12.3 Internal Dependencies

- `jinja2` (template engine)
- `weasyprint` (PDF generation)
- `csv` (CSV export, stdlib)
- `orjson` (JSON export)
- `pathlib` (file operations)
- `aiofiles` (async file I/O)
- `sqlalchemy` (report metadata persistence)

### 12.4 Versioning

- Current: 1.0.0
- Stability: Stable
- Template format: Jinja2 standard; no custom syntax
- Export format: Stable CSV/JSON schemas

---

## 13. validation

### 13.1 Responsibilities

- Input validation: Pydantic v2 model validation
- Schema validation: JSON Schema generation and validation
- Data integrity: checksum verification, hash validation
- Business rule validation: domain-specific constraint checking
- Sanitization: HTML sanitization, input cleaning
- Custom validators: reusable validation decorators

### 13.2 Public API Sketch

```python
from authshield.validation import (
    InputValidator,
    SchemaValidator,
    IntegrityChecker,
    BusinessRules,
    Sanitizer,
)
from authshield.validation.types import (
    ValidationResult,
    ValidationError,
    IntegrityResult,
)

# Input validation
validator = InputValidator()
result: ValidationResult = validator.validate(
    data=request_data,
    schema=AssessmentSubmissionSchema,
)

# Schema validation
schema_validator = SchemaValidator()
valid = schema_validator.validate_json(
    data=json_data,
    schema=assessment_json_schema,
)

# Integrity checking
checker = IntegrityChecker()
valid = checker.verify_checksum(
    file_path="/path/to/file",
    expected_checksum="sha256:abc123...",
)

# Business rules
rules = BusinessRules(db=session)
result = rules.validate_assessment_submission(
    user_id="user_123",
    assessment_id="assess_456",
    answers=submitted_answers,
    time_spent_seconds=300,
)

# Sanitization
sanitizer = Sanitizer()
clean_html = sanitizer.sanitize_html(user_input)
clean_text = sanitizer.strip_html(user_input)
clean_filename = sanitizer.sanitize_filename(user_filename)
```

### 13.3 Internal Dependencies

- `pydantic` (model validation, JSON Schema)
- `sqlalchemy` (database integrity checks)
- `hashlib` (checksum computation)
- `html` (HTML escaping)
- `re` (regex-based sanitization)
- `structlog` (validation failure logging)

### 13.4 Versioning

- Current: 1.0.0
- Stability: Stable
- Validation rules: Configurable; no version coupling
- Schema format: JSON Schema draft 2020-12

---

## 14. Library Dependency Graph

```
auth-core
├── crypto
├── utils
└── logging

crypto
├── utils
└── logging

a11y-engine
├── utils
└── logging

localization-engine
├── utils
└── logging

simulation-engine
├── utils
├── logging
└── validation

learning-engine
├── utils
├── logging
├── validation
└── config

ui-components
├── utils (TypeScript)
└── a11y-engine (TypeScript)

config
├── utils
└── logging

logging
├── utils

reporting
├── utils
├── logging
└── validation

validation
├── utils
└── logging
```

---

## 15. Library Usage Guidelines

### 15.1 Import Convention

```python
# Preferred: import from the library
from authshield.auth_core import AuthService

# Avoid: import from internal modules
from authshield.auth_core.internal.hasher import _argon2_hash  # private API
```

### 15.2 Version Compatibility Matrix

| Library | Python 3.12 | Python 3.11 | Notes |
|---------|-------------|-------------|-------|
| auth-core | ✓ | ✓ | Core library |
| crypto | ✓ | ✓ | Core library |
| a11y-engine | ✓ | ✓ | Core library |
| localization-engine | ✓ | ✓ | Core library |
| simulation-engine | ✓ | ✓ | Core library |
| learning-engine | ✓ | ✓ | Core library |
| ui-components | N/A (TS) | N/A (TS) | Electron only |
| utils | ✓ | ✓ | Core library |
| config | ✓ | ✓ | Core library |
| logging | ✓ | ✓ | Core library |
| reporting | ✓ | ✓ | Core library |
| validation | ✓ | ✓ | Core library |

---

*Document maintained by the AuthShield Lab Architecture Team. Review quarterly.*
