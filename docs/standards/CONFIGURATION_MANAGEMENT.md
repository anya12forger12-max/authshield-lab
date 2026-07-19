# AuthShield Lab — Configuration Management

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab uses a hierarchical configuration system where settings are merged from multiple sources with well-defined precedence. This enables flexibility (environment-specific overrides), security (secrets via environment variables), and user customization (personal preferences) while maintaining sane defaults.

---

## 2. Configuration Hierarchy

Settings are loaded and merged in the following order (lowest to highest priority):

| Priority | Source | Location | Description |
|----------|--------|----------|-------------|
| 1 (lowest) | Built-in defaults | Bundled in application | Application defaults; always available |
| 2 | Global config | `~/.config/authshield-lab/config.toml` | User-wide defaults across all projects |
| 3 | Institution config | `/etc/authshield-lab/config.toml` | Organization-wide settings (managed by IT) |
| 4 | Project config | `.authshield-lab/config.toml` | Project-specific settings (in project directory) |
| 5 | User config | `~/.authshield-lab/config.toml` | Per-user overrides (personal preferences) |
| 6 | Environment variables | `AUTHSHIELD_*` prefix | Runtime overrides (deployment, secrets) |
| 7 (highest) | CLI arguments | Command-line flags | Immediate overrides (debug, one-off changes) |

### 2.1 Precedence Example

```toml
# Priority 1: Built-in defaults
[server]
host = "127.0.0.1"
port = 8000
workers = 1

# Priority 2: Global config (~/.config/authshield-lab/config.toml)
[server]
port = 9000  # Override default port

# Priority 3: Institution config (/etc/authshield-lab/config.toml)
[server]
workers = 4  # Override for multi-core server

# Priority 4: Project config (.authshield-lab/config.toml)
[server]
host = "0.0.0.0"  # Listen on all interfaces for this project

# Priority 6: Environment variable
AUTHSHIELD_SERVER_PORT=8080  # Override port for deployment

# Priority 7: CLI argument
--port=3000  # Override everything for this run
```

**Result:** `host=0.0.0.0`, `port=3000`, `workers=4`

---

## 3. Configuration Schema

### 3.1 Main Configuration Model

```python
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    host: str = Field(default="127.0.0.1", description="Server bind address")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=1, ge=1, le=32, description="Worker processes")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout (seconds)")
    cors_origins: list[str] = Field(default=["http://localhost:3000"], description="Allowed CORS origins")

    model_config = SettingsConfigDict(env_prefix="AUTHSHIELD_SERVER_")


class DatabaseSettings(BaseSettings):
    url: str = Field(default="sqlite+aiosqlite:///authshield.db", description="Database URL")
    echo: bool = Field(default=False, description="SQL echo mode")
    pool_size: int = Field(default=5, ge=1, le=100, description="Connection pool size")

    model_config = SettingsConfigDict(env_prefix="AUTHSHIELD_DB_")


class SecuritySettings(BaseSettings):
    secret_key: SecretStr = Field(description="Application secret key (required)")
    session_timeout: int = Field(default=3600, ge=300, le=86400, description="Session timeout (seconds)")
    max_login_attempts: int = Field(default=5, ge=1, le=20, description="Max login attempts before lockout")
    lockout_duration: int = Field(default=900, ge=60, le=3600, description="Lockout duration (seconds)")
    password_min_length: int = Field(default=12, ge=8, le=128, description="Minimum password length")
    csrf_enabled: bool = Field(default=True, description="Enable CSRF protection")
    csp_enabled: bool = Field(default=True, description="Enable Content Security Policy")

    model_config = SettingsConfigDict(env_prefix="AUTHSHIELD_SECURITY_")


class LoggingSettings(BaseSettings):
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="json", description="Log format (json/text)")
    file_path: str | None = Field(default=None, description="Log file path (None for stdout only)")
    rotation: str = Field(default="daily", description="Log rotation schedule")
    retention_days: int = Field(default=30, ge=1, le=365, description="Log retention in days")
    security_log_path: str | None = Field(default=None, description="Security log file path")
    audit_log_path: str | None = Field(default=None, description="Audit log file path")

    model_config = SettingsConfigDict(env_prefix="AUTHSHIELD_LOGGING_")


class LocalizationSettings(BaseSettings):
    default_locale: str = Field(default="en", description="Default locale")
    fallback_chain: list[str] = Field(default=["en"], description="Locale fallback chain")
    translation_dir: str = Field(default="translations/", description="Translation files directory")
    rtl_locales: list[str] = Field(default=["ar", "he"], description="RTL locale codes")

    model_config = SettingsConfigDict(env_prefix="AUTHSHIELD_I18N_")


class PluginSettings(BaseSettings):
    enabled: bool = Field(default=True, description="Enable plugin system")
    directory: str = Field(default="~/.config/authshield-lab/plugins", description="Plugin directory")
    auto_load: bool = Field(default=True, description="Auto-load plugins on startup")
    sandbox_level: int = Field(default=1, ge=0, le=3, description="Plugin isolation level (0-3)")
    load_timeout: float = Field(default=10.0, ge=1.0, le=60.0, description="Plugin load timeout (seconds)")

    model_config = SettingsConfigDict(env_prefix="AUTHSHIELD_PLUGIN_")


class ReportingSettings(BaseSettings):
    output_dir: str = Field(default="~/.local/share/authshield-lab/reports", description="Report output directory")
    template_dir: str = Field(default="templates/reports", description="Report template directory")
    default_format: str = Field(default="pdf", description="Default export format (pdf/csv/json)")
    archive_reports: bool = Field(default=True, description="Archive generated reports")
    max_archive_days: int = Field(default=365, ge=30, le=3650, description="Archive retention (days)")

    model_config = SettingsConfigDict(env_prefix="AUTHSHIELD_REPORTS_")


class AppConfig(BaseSettings):
    app_name: str = "AuthShield Lab"
    version: str = "1.0.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    data_dir: str = Field(default="~/.local/share/authshield-lab", description="Application data directory")
    config_version: str = Field(default="1.0.0", description="Configuration schema version")

    server: ServerSettings = Field(default_factory=ServerSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    localization: LocalizationSettings = Field(default_factory=LocalizationSettings)
    plugin: PluginSettings = Field(default_factory=PluginSettings)
    reporting: ReportingSettings = Field(default_factory=ReportingSettings)

    model_config = SettingsConfigDict(
        env_prefix="AUTHSHIELD_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )
```

### 3.2 Environment Variable Mapping

| Setting Path | Environment Variable | Type |
|-------------|---------------------|------|
| `server.host` | `AUTHSHIELD_SERVER_HOST` | string |
| `server.port` | `AUTHSHIELD_SERVER_PORT` | integer |
| `database.url` | `AUTHSHIELD_DB_URL` | string |
| `security.secret_key` | `AUTHSHIELD_SECURITY_SECRET_KEY` | secret |
| `security.session_timeout` | `AUTHSHIELD_SECURITY_SESSION_TIMEOUT` | integer |
| `logging.level` | `AUTHSHIELD_LOGGING_LEVEL` | string |
| `plugin.directory` | `AUTHSHIELD_PLUGIN_DIRECTORY` | string |

**Nested delimiter:** `__` (double underscore) for nested settings.

---

## 4. Configuration Loading

### 4.1 Load Process

```python
from authshield.config import ConfigManager
from authshield.config.types import AppConfig

manager = ConfigManager(
    app_name="authshield-lab",
    env_prefix="AUTHSHIELD_",
    config_version="1.0.0",
)

# Load configuration with full hierarchy
settings: AppConfig = manager.load(
    global_config=Path("~/.config/authshield-lab/config.toml"),
    institution_config=Path("/etc/authshield-lab/config.toml"),
    project_config=Path(".authshield-lab/config.toml"),
    user_config=Path("~/.authshield-lab/config.toml"),
    cli_overrides={"server": {"port": 3000}},
)
```

### 4.2 Load Sequence

```
1. Load built-in defaults (Pydantic model defaults)
2. Load global config TOML → merge
3. Load institution config TOML → merge
4. Load project config TOML → merge
5. Load user config TOML → merge
6. Read environment variables → merge (override TOML values)
7. Apply CLI arguments → merge (override everything)
8. Validate entire configuration
9. Return AppConfig instance
```

### 4.3 TOML File Format

```toml
# ~/.config/authshield-lab/config.toml

[server]
host = "127.0.0.1"
port = 9000
workers = 4

[database]
url = "sqlite+aiosqlite:///data/authshield.db"

[security]
session_timeout = 7200
max_login_attempts = 3

[logging]
level = "INFO"
rotation = "daily"
retention_days = 60

[localization]
default_locale = "en"
fallback_chain = ["en"]
rtl_locales = ["ar", "he"]

[plugin]
enabled = true
sandbox_level = 1
```

---

## 5. Configuration Validation

### 5.1 Validation Rules

| Setting | Type | Constraints | Error |
|---------|------|-------------|-------|
| `server.port` | int | 1-65535 | "Port must be between 1 and 65535" |
| `server.workers` | int | 1-32 | "Workers must be between 1 and 32" |
| `server.timeout` | int | 1-300 | "Timeout must be between 1 and 300 seconds" |
| `security.secret_key` | SecretStr | Required | "Secret key is required" |
| `security.session_timeout` | int | 300-86400 | "Session timeout must be 300-86400 seconds" |
| `security.password_min_length` | int | 8-128 | "Password min length must be 8-128" |
| `logging.level` | str | DEBUG/INFO/WARNING/ERROR/CRITICAL | "Invalid log level" |
| `plugin.sandbox_level` | int | 0-3 | "Sandbox level must be 0-3" |
| `localization.default_locale` | str | Must be in supported locales | "Unsupported locale" |

### 5.2 Validation on Load

```python
from pydantic import ValidationError

try:
    settings = manager.load()
except ValidationError as e:
    # Pydantic validation failed
    for error in e.errors():
        logger.error(
            "config.validation.error",
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            value=error.get("input"),
        )
    raise SystemExit("Configuration validation failed. Check logs for details.")
```

### 5.3 Custom Validators

```python
from pydantic import field_validator, model_validator

class SecuritySettings(BaseSettings):
    secret_key: SecretStr

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        return v

    @model_validator(mode="after")
    def validate_security_combination(self) -> "SecuritySettings":
        if self.max_login_attempts > 10 and self.lockout_duration < 300:
            raise ValueError(
                "High login attempts with short lockout is insecure. "
                "Either reduce max_login_attempts or increase lockout_duration."
            )
        return self
```

---

## 6. Configuration Migration

### 6.1 Migration Strategy

When configuration schema changes between versions, migration scripts transform old configs to new format.

```python
from authshield.config import ConfigMigration
from authshield.config.types import MigrationStep, MigrationResult

migration = ConfigMigration(
    current_version="1.0.0",
    migration_dir=Path("migrations/config/"),
)

# Define migration from 0.9.x to 1.0.0
migration.register(
    from_version="0.9.0",
    to_version="1.0.0",
    steps=[
        MigrationStep(
            description="Rename 'db_url' to 'database.url'",
            transform=lambda config: {
                **config,
                "database": {"url": config.pop("db_url", config.get("database", {}).get("url"))},
            },
        ),
        MigrationStep(
            description="Add 'logging.retention_days' default",
            transform=lambda config: {
                **config,
                "logging": {**config.get("logging", {}), "retention_days": 30},
            },
        ),
    ],
)

# Execute migration
result: MigrationResult = migration.migrate(config_path=Path("~/.config/authshield-lab/config.toml"))
# result.backup_path → backup of original config
# result.migrated_config → new config content
# result.warnings → deprecation notices
```

### 6.2 Migration File Structure

```
migrations/config/
├── 0.9.0_to_1.0.0.py
├── 1.0.0_to_1.1.0.py
└── README.md
```

---

## 7. Configuration Versioning

### 7.1 Version Format

Configuration schema uses semver:

| Version change | When |
|---------------|------|
| **Major** | Breaking schema changes (removed settings, renamed sections) |
| **Minor** | New settings added (with backward-compatible defaults) |
| **Patch** | Documentation changes, validation rule updates |

### 7.2 Version Check

```python
# On startup
if settings.config_version != current_config_version:
    logger.warning(
        "config.version.mismatch",
        current=settings.config_version,
        expected=current_config_version,
    )
    # Run migration
    migration.migrate(config_path)
```

---

## 8. Configuration Backup & Recovery

### 8.1 Automatic Backup

```python
from authshield.config import ConfigBackup

backup = ConfigBackup(
    config_dir=Path("~/.config/authshield-lab"),
    backup_dir=Path("~/.config/authshield-lab/backups"),
    max_backups=10,
)

# Backup before migration
backup_path = backup.create_backup(
    reason="pre_migration",
    version="1.0.0",
)
# Creates: ~/.config/authshield-lab/backups/config.2026-07-19_12-00-00.toml

# List available backups
backups = backup.list_backups()
# [BackupInfo(path=..., timestamp=..., reason=..., version=...)]
```

### 8.2 Recovery

```python
# Restore from backup
backup.restore(
    backup_path=Path("~/.config/authshield-lab/backups/config.2026-07-19_12-00-00.toml"),
    config_path=Path("~/.config/authshield-lab/config.toml"),
)

# Restore from last known good
backup.restore_last_good(config_path=Path("~/.config/authshield-lab/config.toml"))
```

### 8.3 Backup Rotation

```python
# Keep last 10 backups
backup.cleanup(keep=10)

# Backups older than 90 days are automatically removed
backup.cleanup(max_age_days=90)
```

---

## 9. Configuration Templates

### 9.1 Default Configuration

```toml
# ~/.config/authshield-lab/config.toml (generated on first run)

# AuthShield Lab Configuration
# For documentation, see: https://docs.authshield.dev/configuration

[server]
# Server bind address (use 127.0.0.1 for local-only, 0.0.0.0 for network)
host = "127.0.0.1"
# Server port (1-65535)
port = 8000
# Number of worker processes (1-32, recommended: CPU cores)
workers = 1
# Request timeout in seconds (1-300)
timeout = 30
# Allowed CORS origins
cors_origins = ["http://localhost:3000"]

[database]
# Database connection URL
# SQLite: sqlite+aiosqlite:///path/to/database.db
# PostgreSQL: postgresql+asyncpg://user:pass@localhost/authshield
url = "sqlite+aiosqlite:///authshield.db"
# Enable SQL query logging (for debugging)
echo = false
# Connection pool size (1-100)
pool_size = 5

[security]
# Application secret key (REQUIRED: generate with `authshield generate-key`)
# secret_key = "your-secret-key-here"
# Session timeout in seconds (300-86400, default: 1 hour)
session_timeout = 3600
# Maximum failed login attempts before lockout (1-20)
max_login_attempts = 5
# Lockout duration in seconds (60-3600)
lockout_duration = 900
# Minimum password length (8-128)
password_min_length = 12
# Enable CSRF protection
csrf_enabled = true
# Enable Content Security Policy
csp_enabled = true

[logging]
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
level = "INFO"
# Log format: json (structured) or text (human-readable)
format = "json"
# Log file path (null for stdout only)
file_path = null
# Log rotation: daily, weekly, monthly
rotation = "daily"
# Log retention in days (1-365)
retention_days = 30
# Security log file path (null to include in main log)
security_log_path = null
# Audit log file path (null to include in main log)
audit_log_path = null

[localization]
# Default locale code
default_locale = "en"
# Locale fallback chain
fallback_chain = ["en"]
# Translation files directory
translation_dir = "translations/"
# RTL locale codes
rtl_locales = ["ar", "he"]

[plugin]
# Enable plugin system
enabled = true
# Plugin directory path
directory = "~/.config/authshield-lab/plugins"
# Auto-load plugins on startup
auto_load = true
# Plugin isolation level (0=full, 1=import restrictions, 2=subprocess, 3=network-blocked)
sandbox_level = 1
# Plugin load timeout in seconds
load_timeout = 10.0

[reporting]
# Report output directory
output_dir = "~/.local/share/authshield-lab/reports"
# Report template directory
template_dir = "templates/reports"
# Default export format: pdf, csv, json
default_format = "pdf"
# Archive generated reports
archive_reports = true
# Archive retention in days
max_archive_days = 365
```

---

## 10. Configuration Access Patterns

### 10.1 Accessing Settings

```python
# Through ConfigManager
settings = config_manager.load()
port = settings.server.port

# Through dependency injection (FastAPI)
from fastapi import Depends

async def get_settings() -> AppConfig:
    return config_manager.load()

@router.get("/status")
async def status(settings: AppConfig = Depends(get_settings)):
    return {"version": settings.version, "debug": settings.debug}
```

### 10.2 Runtime Configuration Changes

```python
from authshield.config import RuntimeConfig

runtime = RuntimeConfig(settings)

# Change log level at runtime
runtime.update("logging.level", "DEBUG")

# Change server settings (requires restart)
runtime.update("server.workers", 4, restart_required=True)

# Check if restart is needed
if runtime.restart_required:
    logger.info("config.restart_required", changes=runtime.pending_changes)
```

---

## 11. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| **Secrets in config files** | Use `SecretStr` type; environment variables preferred; never commit secrets |
| **Config file permissions** | `chmod 600` for config files containing secrets |
| **Institution config** | Read-only for non-admin users; managed by IT |
| **Config file integrity** | Checksum verification for critical config sections |
| **Environment variable exposure** | Documented in `.env.example`; never logged |
| **Default security** | Secure defaults (localhost-only, CSRF enabled, CSP enabled) |

---

*Document maintained by the AuthShield Lab Architecture Team. Review quarterly.*
