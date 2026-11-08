# AuthShield Lab — Logging Architecture

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab implements a structured, multi-channel logging architecture designed for security auditing, debugging, performance monitoring, and compliance. All logs are structured JSON by default, with separate channels for different concerns. The architecture supports log rotation, compression, redaction, and exportable diagnostic bundles.

---

## 2. Log Channels

### 2.1 Channel Overview

| Channel | File | Level | Purpose | Retention |
|---------|------|-------|---------|-----------|
| **Application** | `app.log` | INFO+ | General application events | 30 days |
| **Security** | `security.log` | WARNING+ | Security-relevant events | 90 days |
| **Audit** | `audit.log` | ALL | Immutable append-only audit trail | 365 days |
| **Plugin** | `plugin-{name}.log` | Configurable | Per-plugin events | 30 days |
| **Performance** | `performance.log` | INFO+ | Timing data, metrics | 14 days |
| **Diagnostic** | `diagnostic.log` | DEBUG | Verbose diagnostic output | 7 days |
| **Accessibility** | `a11y.log` | WARNING+ | A11y violations, remediation | 30 days |
| **Crash** | `crash.log` | ERROR+ | Stack traces, minidump-style | 90 days |

### 2.2 Log Directory Structure

```
~/.local/share/authshield-lab/logs/
├── app.log                     # Current application log
├── app.log.2026-07-18          # Rotated application log (compressed)
├── app.log.2026-07-17.gz       # Compressed application log
├── security.log                # Current security log
├── security.log.2026-07-18     # Rotated security log
├── audit.log                   # Current audit log (immutable)
├── audit.log.2026-07-18        # Rotated audit log
├── plugin-phishing-sim.log     # Plugin-specific logs
├── performance.log             # Performance metrics
├── performance.log.2026-07-18  # Rotated performance log
├── diagnostic.log              # Diagnostic output
├── a11y.log                    # Accessibility violations
├── crash.log                   # Crash reports
├── crash-dump-2026-07-19-12-00-00.md  # Crash dump files
└── bundles/                    # Exported diagnostic bundles
    └── diagnostic-bundle-2026-07-19-12-00-00.tar.gz
```

---

## 3. Log Entry Format

### 3.1 Standard JSON Format

```json
{
  "timestamp": "2026-07-19T12:00:00.123456Z",
  "level": "info",
  "event": "user.login",
  "logger": "authshield.auth",
  "module": "auth-core",
  "request_id": "req_abc123def456",
  "user_id": "user_789",
  "ip_address": "192.168.1.1",
  "message": "User authentication successful",
  "data": {
    "method": "password",
    "mfa_used": true,
    "session_id": "sess_xyz789"
  }
}
```

### 3.2 Security Log Format

```json
{
  "timestamp": "2026-07-19T12:00:00.123456Z",
  "level": "warning",
  "event": "auth.failed",
  "logger": "authshield.security",
  "module": "auth-core",
  "severity": "medium",
  "request_id": "req_abc123def456",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "message": "Authentication failed: invalid password",
  "data": {
    "username": "user@example.com",
    "attempt_number": 3,
    "remaining_attempts": 2,
    "lockout_imminent": true
  },
  "risk_score": 0.6,
  "blocked": false
}
```

### 3.3 Audit Log Format

```json
{
  "timestamp": "2026-07-19T12:00:00.123456Z",
  "level": "info",
  "event": "assessment.submitted",
  "logger": "authshield.audit",
  "module": "learning-engine",
  "actor": {
    "user_id": "user_789",
    "role": "student",
    "ip_address": "192.168.1.1"
  },
  "action": "submit_assessment",
  "resource": {
    "type": "assessment",
    "id": "assess_456",
    "module": "phishing_awareness"
  },
  "result": "success",
  "changes": {
    "score": 85,
    "status": "graded",
    "time_spent_seconds": 300
  },
  "integrity_hash": "sha256:abc123..."
}
```

### 3.4 Performance Log Format

```json
{
  "timestamp": "2026-07-19T12:00:00.123456Z",
  "level": "info",
  "event": "api.request.complete",
  "logger": "authshield.performance",
  "module": "api",
  "method": "POST",
  "path": "/api/v1/assessment/submit",
  "status_code": 200,
  "duration_ms": 145,
  "request_id": "req_abc123def456",
  "user_id": "user_789",
  "data": {
    "db_queries": 3,
    "db_duration_ms": 45,
    "cpu_time_ms": 12,
    "memory_delta_kb": 2048
  }
}
```

---

## 4. Logger Configuration

### 4.1 LogManager Setup

```python
from authshield.logging import LogManager

log_manager = LogManager(
    app_name="authshield-lab",
    log_dir=Path("~/.local/share/authshield-lab/logs"),
    default_level="INFO",
    rotation="daily",
    retention_days=30,
    compress_rotated=True,
    json_format=True,
    redaction_patterns=[
        r"password",
        r"secret",
        r"token",
        r"api_key",
        r"authorization",
        r"credit_card",
        r"ssn",
    ],
)

# Get loggers for different channels
app_logger = log_manager.get_logger("authshield.app")
security_logger = log_manager.get_logger("authshield.security")
audit_logger = log_manager.get_logger("authshield.audit")
perf_logger = log_manager.get_logger("authshield.performance")
plugin_logger = log_manager.get_logger("authshield.plugins.my-plugin")
```

### 4.2 structlog Configuration

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        RedactionFilter(patterns=["password", "secret", "token"]),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.BoundLogger,
    cache_logger_on_first_use=True,
)
```

---

## 5. Log Rotation

### 5.1 Rotation Policies

| Policy | Trigger | Max files | Compression |
|--------|---------|-----------|-------------|
| **Daily** | Midnight UTC | 30 | gzip |
| **Size-based** | 100MB per file | 10 | gzip |
| **Monthly** | First of month | 12 | gzip |
| **Audit** | Size-based (1GB) | 365 | gzip (after 30 days) |

### 5.2 Rotation Implementation

```python
from authshield.logging import LogRotation

rotation = LogRotation(
    log_dir=Path("~/.local/share/authshield-lab/logs"),
    policy="daily",
    max_files=30,
    compress_after_days=1,
    archive_after_days=30,
)

# Rotation runs automatically via APScheduler or at startup
rotation.rotate_all()

# Manual rotation for specific log
rotation.rotate(
    log_file=Path("app.log"),
    policy="size",
    max_size_mb=100,
)
```

### 5.3 Rotation Schedule

```
Daily rotation:
  app.log → app.log.2026-07-19 → app.log.2026-07-19.gz (after 1 day)

Size-based rotation:
  performance.log (50MB) → performance.log.2026-07-19-12-00-00

Monthly rotation:
  audit.log → audit.log.2026-07 → audit.log.2026-07.gz (after 30 days)
```

---

## 6. Log Redaction

### 6.1 Redaction Rules

| Pattern | Action | Example |
|---------|--------|---------|
| `password` | Replace value with `[REDACTED]` | `"password": "[REDACTED]"` |
| `secret` | Replace value with `[REDACTED]` | `"secret_key": "[REDACTED]"` |
| `token` | Replace value with `[REDACTED]` | `"access_token": "[REDACTED]"` |
| `api_key` | Replace value with `[REDACTED]` | `"api_key": "[REDACTED]"` |
| `authorization` | Replace header value with `[REDACTED]` | `"authorization": "[REDACTED]"` |
| Email addresses | Partial redaction | `"user@*****.com"` |
| IP addresses | Configurable (full/partial) | `"192.168.1.***"` or full |
| Credit card numbers | Full redaction | `"****-****-****-1234"` |

### 6.2 Redaction Implementation

```python
from authshield.logging import RedactionFilter

# Custom redaction rules
redactor = RedactionFilter(
    patterns=[
        r"password",
        r"secret",
        r"token",
        r"api_key",
        r"authorization",
    ],
    email_pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    ip_pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    email_action="partial",  # Redact local part, keep domain
    ip_action="full",        # Full redaction
)

# Apply to log entry
log_entry = {
    "password": "my_secret_password",
    "user_email": "user@example.com",
    "ip_address": "192.168.1.100",
}
redacted = redactor.redact(log_entry)
# {
#   "password": "[REDACTED]",
#   "user_email": "u***@example.com",
#   "ip_address": "[REDACTED]",
# }
```

---

## 7. Audit Log Integrity

### 7.1 Append-Only Design

Audit logs are append-only with integrity verification:

```python
from authshield.logging import AuditLog

audit = AuditLog(
    log_dir=Path("~/.local/share/authshield-lab/logs"),
    integrity_check=True,
)

# Write audit entry (append-only)
audit.write({
    "event": "user.login",
    "actor": {"user_id": "user_123", "role": "student"},
    "action": "login",
    "result": "success",
})

# Verify audit log integrity
is_valid = audit.verify_integrity()
# Checks hash chain: each entry includes hash of previous entry

# Get integrity report
report = audit.integrity_report()
# IntegrityReport(total_entries=1500, valid=1500, tampered=0, gaps=0)
```

### 7.2 Hash Chain

```
Entry 1: {"data": {...}, "hash": "abc123", "prev_hash": "000000"}
Entry 2: {"data": {...}, "hash": "def456", "prev_hash": "abc123"}
Entry 3: {"data": {...}, "hash": "ghi789", "prev_hash": "def456"}
```

### 7.3 Tamper Detection

```python
# Detect tampering
audit.verify_integrity()
# Raises AuditLogTamperedError if:
#   - Hash chain broken
#   - Entry modified after write
#   - Missing entries
#   - Timestamp anomalies
```

---

## 8. Diagnostic Bundles

### 8.1 Bundle Contents

| Content | Description | Size Limit |
|---------|-------------|------------|
| Application logs | Last 7 days of app.log | 50MB |
| Security logs | Last 30 days of security.log | 25MB |
| Audit logs | Last 30 days of audit.log | 50MB |
| Plugin logs | Last 7 days of plugin logs | 10MB |
| Performance logs | Last 7 days of performance.log | 10MB |
| Accessibility logs | Last 30 days of a11y.log | 10MB |
| Configuration | Current config.toml (redacted) | 100KB |
| System info | OS, Python version, memory, disk | 10KB |
| Database info | Schema version, table sizes, indexes | 100KB |
| Plugin list | Installed plugins, versions, status | 50KB |

### 8.2 Bundle Creation

```python
from authshield.logging import DiagnosticBundle

bundle = DiagnosticBundle(
    log_dir=Path("~/.local/share/authshield-lab/logs"),
    config_path=Path("~/.config/authshield-lab/config.toml"),
    output_dir=Path("~/.local/share/authshield-lab/logs/bundles"),
)

# Create diagnostic bundle
archive_path = bundle.create(
    include_logs=True,
    include_config=True,  # Redacted automatically
    include_system_info=True,
    include_db_info=True,
    include_plugins=True,
    output_path=Path("/tmp/diagnostic-bundle.tar.gz"),
)

# Bundle is compressed (gzip) and includes SHA-256 checksum
# bundle.tar.gz
# ├── SHA256SUMS
# ├── manifest.json
# ├── logs/
# │   ├── app.log (last 7 days)
# │   ├── security.log (last 30 days)
# │   └── ...
# ├── config.toml (redacted)
# ├── system-info.json
# ├── db-info.json
# └── plugins.json
```

### 8.3 Bundle Validation

```python
# Validate bundle integrity
is_valid = bundle.validate(archive_path=archive_path)
# Checks SHA-256 checksums of all included files

# Extract bundle
bundle.extract(
    archive_path=archive_path,
    output_dir=Path("/tmp/extracted-bundle"),
)
```

---

## 9. Plugin Logging

### 9.1 Namespaced Logging

Each plugin gets its own log file with a namespaced logger:

```python
# Plugin __init__.py
from authshield.logging import get_plugin_logger

logger = get_plugin_logger("my-plugin")
# Writes to: logs/plugin-my-plugin.log

class MyPlugin:
    async def on_load(self):
        logger.info("plugin.loaded", version="1.0.0")

    async def process_data(self, data):
        logger.debug("plugin.data.processed", count=len(data))
        return processed_data
```

### 9.2 Configurable Levels

```toml
# In plugin.toml
[plugin.logging]
level = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
file = "plugin-my-plugin.log"  # Custom log file name
max_size_mb = 10  # Per-plugin log size limit
```

---

## 10. Performance Logging

### 10.1 Timing Decorator

```python
from authshield.logging import PerformanceLogger

perf = PerformanceLogger(perf_logger)

@perf.measure("api.assessment.grade", tags={"module": "assessment"})
async def grade_assessment(assessment_id: str):
    # ... grading logic ...
    pass
# Logs: {"event": "api.assessment.grade", "duration_ms": 145, "status": "success", "tags": {"module": "assessment"}}
```

### 10.2 Metric Aggregation

```python
from authshield.logging import MetricsAggregator

metrics = MetricsAggregator()

# Record metrics
metrics.record("api.response_time", value=145, tags={"endpoint": "/api/v1/assessment"})
metrics.record("db.query_time", value=45, tags={"query": "select_assessment"})
metrics.record("cache.hit_rate", value=0.85)

# Get aggregated metrics
summary = metrics.get_summary(
    metric="api.response_time",
    period="1h",
)
# MetricSummary(
#     count=1500,
#     mean=145.2,
#     median=138.0,
#     p95=220.0,
#     p99=350.0,
#     min=45,
#     max=500,
# )
```

---

## 11. Crash Logging

### 11.1 Crash Log Format

```json
{
  "timestamp": "2026-07-19T12:00:00.123456Z",
  "level": "critical",
  "event": "crash.unhandled_exception",
  "logger": "authshield.crash",
  "exception": {
    "type": "ValueError",
    "message": "Invalid assessment ID format",
    "traceback": "Traceback (most recent call last):\n  File \"/app/authshield/api/routes.py\", line 42, in get_assessment\n    assessment = await service.get(assessment_id)\nValueError: Invalid assessment ID format"
  },
  "context": {
    "request_id": "req_abc123",
    "user_id": "user_789",
    "endpoint": "/api/v1/assessment/invalid_id",
    "method": "GET"
  },
  "system": {
    "python_version": "3.12.4",
    "platform": "Linux-6.5.0",
    "memory_used_mb": 256,
    "memory_available_mb": 768
  }
}
```

### 11.2 Crash Dump

```python
from authshield.logging import CrashLogger

crash_logger = CrashLogger(
    log_dir=Path("~/.local/share/authshield-lab/logs"),
    dump_dir=Path("~/.local/share/authshield-lab/logs"),
)

# Automatic crash capture
try:
    # ... application code ...
except Exception as e:
    crash_logger.capture(
        exception=e,
        context={
            "request_id": request_id,
            "user_id": user_id,
            "endpoint": request.url.path,
        },
    )
    raise
```

---

## 12. Accessibility Logging

### 12.1 A11y Violation Logging

```python
from authshield.logging import A11yLogger

a11y_logger = A11yLogger(
    log_dir=Path("~/.local/share/authshield-lab/logs"),
)

# Log accessibility violation
a11y_logger.log_violation(
    rule="color-contrast",
    severity="serious",
    element="<button>Submit</button>",
    page="/assessment/submit",
    wcag_criterion="1.4.3",
    description="Insufficient color contrast ratio (2.5:1, required 4.5:1)",
    remediation="Increase contrast ratio to at least 4.5:1",
)

# Log remediation
a11y_logger.log_remediation(
    rule="color-contrast",
    page="/assessment/submit",
    remediated=True,
    new_contrast_ratio=5.2,
)
```

### 12.2 A11y Metrics

```json
{
  "timestamp": "2026-07-19T12:00:00.123456Z",
  "level": "warning",
  "event": "a11y.violation",
  "logger": "authshield.a11y",
  "rule": "color-contrast",
  "severity": "serious",
  "wcag_criterion": "1.4.3",
  "element": "button.submit",
  "page": "/assessment/submit",
  "description": "Insufficient color contrast ratio",
  "remediation": "Increase contrast ratio to at least 4.5:1",
  "current_ratio": 2.5,
  "required_ratio": 4.5
}
```

---

## 13. Log Export

### 13.1 Export Formats

| Format | Use Case | Implementation |
|--------|----------|---------------|
| **JSON** | Machine processing, SIEM integration | Default format |
| **CSV** | Spreadsheet analysis | `csv.DictWriter` |
| **Plain text** | Human readability | Custom formatter |
| **Syslog** | Enterprise logging systems | `syslog` module |
| **CEF** | Security event correlation | Custom formatter |

### 13.2 Export Implementation

```python
from authshield.logging import LogExporter

exporter = LogExporter(log_dir=Path("~/.local/share/authshield-lab/logs"))

# Export to CSV
exporter.to_csv(
    log_file="security.log",
    output_path=Path("/tmp/security-export.csv"),
    filters={"level": ["warning", "error", "critical"]},
    date_range=(start_date, end_date),
)

# Export to plain text
exporter.to_text(
    log_file="audit.log",
    output_path=Path("/tmp/audit-export.txt"),
    format="%(timestamp)s [%(level)s] %(event)s: %(message)s",
)

# Export to syslog
exporter.to_syslog(
    log_file="security.log",
    syslog_address="/dev/log",
    syslog_facility="auth",
    filters={"severity": ["high", "critical"]},
)
```

---

## 14. Log Search

### 14.1 Search Implementation

```python
from authshield.logging import LogSearch

search = LogSearch(log_dir=Path("~/.local/share/authshield-lab/logs"))

# Search across all logs
results = search.search(
    query="user.login",
    log_files=["app.log", "security.log"],
    date_range=(start_date, end_date),
    level=["info", "warning"],
    limit=100,
)

# Search with structured query
results = search.search_structured(
    log_files=["audit.log"],
    filters={
        "event": "assessment.submitted",
        "actor.user_id": "user_123",
        "result": "success",
    },
    date_range=(start_date, end_date),
)
```

---

## 15. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| **Log injection** | Sanitize all log values; no user input directly in log format strings |
| **Sensitive data in logs** | Automatic redaction of passwords, tokens, secrets |
| **Audit log tampering** | Hash chain integrity; append-only file permissions |
| **Log file permissions** | `chmod 600` for log files; owned by application user |
| **Log file size** | Rotation and compression prevent disk exhaustion |
| **Log retention** | Configurable retention; automatic cleanup |
| **Diagnostic bundles** | Redacted before export; checksummed for integrity |

---

*Document maintained by the AuthShield Lab Architecture Team. Review quarterly.*
