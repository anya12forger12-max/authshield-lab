# AuthShield Lab — Plugin Ecosystem Architecture

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab's plugin system enables extensibility without modifying core code. Plugins follow a well-defined lifecycle with security-first design: capability-based permissions, signature verification, sandboxed execution, and graceful degradation. The architecture is inspired by Stevedore, VS Code extensions, and Firefox WebExtensions.

---

## 2. Plugin Discovery

### 2.1 Discovery Mechanisms

Plugins are discovered through two mechanisms:

| Mechanism | Source | Use Case |
|-----------|--------|----------|
| **Python entry points** | `pyproject.toml` `[project.entry-points]` | Python-based plugins installed as packages |
| **Plugin directory scan** | `~/.config/authshield-lab/plugins/` | Standalone plugins (unpacked directories) |

### 2.2 Entry Point Registration

```toml
# In plugin's pyproject.toml
[project.entry-points."authshield.plugins"]
my_plugin = "my_plugin:MyPlugin"

[project.entry-points."authshield.routes"]
my_api = "my_plugin.routes:router"

[project.entry-points."authshield.themes"]
my_theme = "my_plugin.theme:MyTheme"

[project.entry-points."authshield.localizations"]
my_locale = "my_plugin.locales:get_translations"
```

### 2.3 Directory Scan Format

```
~/.config/authshield-lab/plugins/
├── my-plugin/
│   ├── manifest.json       # Required: plugin metadata
│   ├── plugin.toml         # Required: configuration
│   ├── __init__.py         # Entry point
│   ├── routes.py           # Optional: API routes
│   ├── theme.css           # Optional: theme overrides
│   └── translations/       # Optional: locale files
│       ├── en.json
│       └── te.json
```

### 2.4 Manifest Format (manifest.json)

```json
{
  "name": "my-plugin",
  "version": "1.2.0",
  "description": "A custom assessment plugin",
  "author": "Plugin Developer",
  "license": "MIT",
  "min_platform": "1.0.0",
  "max_platform": "2.0.0",
  "repository": "https://github.com/example/my-plugin",
  "entry_point": "my_plugin:MyPlugin",
  "icon": "icon.png",
  "required_permissions": [
    "filesystem:read",
    "database:read"
  ],
  "provides": [
    "route:/api/v1/my-plugin",
    "menu:Tools > My Plugin",
    "dashboard:widget:my_widget"
  ],
  "depends_on": [],
  "platforms": ["linux", "macos", "windows"],
  "signature": {
    "algorithm": "ed25519",
    "public_key": "base64-encoded-public-key",
    "signature": "base64-encoded-signature"
  },
  "checksum": {
    "algorithm": "sha256",
    "value": "hex-encoded-checksum-of-plugin-files"
  }
}
```

---

## 3. Plugin Version Compatibility

### 3.1 Platform Version Range

Plugins declare compatibility with platform versions using semver ranges:

| Range | Meaning |
|-------|---------|
| `>=1.0.0` | Any version >= 1.0.0 |
| `>=1.0.0,<2.0.0` | Version 1.x.x only |
| `~1.2.0` | Patch updates only (1.2.x) |
| `^1.2.0` | Minor and patch updates (1.x.x, x >= 2) |

### 3.2 Platform Matrix

| Platform | Minimum Version | Maximum Version | Notes |
|----------|----------------|-----------------|-------|
| **Linux (x86_64)** | 1.0.0 | 2.0.0 | Full support |
| **Linux (ARM64)** | 1.0.0 | 2.0.0 | Full support |
| **macOS (x86_64)** | 1.0.0 | 2.0.0 | Full support |
| **macOS (ARM64)** | 1.0.0 | 2.0.0 | Full support (Apple Silicon) |
| **Windows (x86_64)** | 1.0.0 | 2.0.0 | Full support |
| **Windows (ARM64)** | 1.2.0 | 2.0.0 | Partial support (experimental) |

### 3.3 Compatibility Checking

```python
from authshield.plugins import CompatibilityChecker

checker = CompatibilityChecker()

# Check if plugin is compatible with current platform
is_compatible = checker.check(
    plugin_manifest=manifest,
    platform=current_platform,  # {"os": "linux", "arch": "x86_64"}
    platform_version=current_version,  # "1.3.0"
)

# Get compatibility report
report = checker.get_report(manifest)
# CompatibilityReport(
#     compatible=True,
#     platform_support=["linux", "macos", "windows"],
#     version_range=">=1.0.0,<2.0.0",
#     warnings=["Plugin uses deprecated API v1"]
# )
```

---

## 4. Capability Declaration

### 4.1 Plugin Configuration (plugin.toml)

```toml
[plugin]
name = "my-plugin"
version = "1.2.0"
description = "Custom assessment plugin"
author = "Plugin Developer"
license = "MIT"

[plugin.platform]
min_platform = "1.0.0"
max_platform = "<2.0.0"
platforms = ["linux", "macos", "windows"]

[plugin.permissions]
# Filesystem access
filesystem_read = true      # Read files from plugin directory and data dir
filesystem_write = false    # Write files to data dir only
filesystem_execute = false  # No executable file access

# Database access
database_read = true        # Read from application database
database_write = false      # No write access to core database
database_own = true         # Can create plugin-specific tables

# Network access (disabled by default for offline-first)
network_internal = false    # No network access
network_external = false    # No external network access

# UI access
ui_routes = true            # Can register API routes
ui_menu_items = true        # Can add menu items
ui_dashboard_widgets = true # Can add dashboard widgets
ui_themes = false           # Cannot override themes
ui_modals = false           # Cannot show system modals

# API access
api_read = true             # Can call existing API endpoints
api_write = false           # Cannot modify core data
api_admin = false           # No admin API access

[plugin.provides]
routes = ["/api/v1/my-plugin"]
menu_items = ["Tools > My Plugin"]
dashboard_widgets = ["my_widget"]
assessment_types = ["custom_quiz"]
report_types = ["custom_report"]
themes = []
localizations = ["en", "te"]

[plugin.depends_on]
# No dependencies on other plugins
# Core platform dependencies are implicit
```

### 4.2 Permission Model

| Permission | Description | Risk Level | Default |
|-----------|-------------|------------|---------|
| `filesystem:read` | Read files from plugin/data directories | Low | `true` |
| `filesystem:write` | Write files to plugin data directory | Medium | `false` |
| `filesystem:execute` | Execute files from plugin directory | High | `false` |
| `database:read` | Read from application database | Medium | `false` |
| `database:write` | Write to application database | High | `false` |
| `database:own` | Create/manage plugin-specific tables | Low | `true` |
| `network:internal` | Access localhost services | Medium | `false` |
| `network:external` | Access external network (breaks offline-first) | Critical | `false` |
| `ui:routes` | Register API routes | Low | `true` |
| `ui:menu_items` | Add menu items | Low | `true` |
| `ui:dashboard_widgets` | Add dashboard widgets | Low | `true` |
| `ui:themes` | Override themes | Medium | `false` |
| `ui:modals` | Show system modals | Medium | `false` |
| `api:read` | Call existing API endpoints | Low | `true` |
| `api:write` | Modify core data | High | `false` |
| `api:admin` | Access admin API | Critical | `false` |

### 4.3 Permission Enforcement

```python
from authshield.plugins import PermissionGuard

guard = PermissionGuard()

# Check permission before action
if guard.has_permission(plugin_id="my-plugin", permission="filesystem:read"):
    data = plugin.read_file("config.json")

# Enforce permission (raises PermissionDenied if not allowed)
guard.enforce(plugin_id="my-plugin", permission="database:write")
```

---

## 5. Sandboxed Execution

### 5.1 Execution Isolation Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **Level 0: Full access** | No isolation; runs in main process | Trusted first-party plugins (reviewed) |
| **Level 1: Import restrictions** | Restricted import whitelist; no `os`, `subprocess`, `ctypes` | Standard third-party plugins |
| **Level 2: Subprocess isolation** | Runs in separate Python process; IPC via JSON | Untrusted plugins; experimental |
| **Level 3: Process + network** | Subprocess with network disabled via OS-level controls | Highly untrusted plugins |

### 5.2 Import Restrictions (Level 1)

```python
# Allowed imports for Level 1 plugins
ALLOWED_IMPORTS = {
    "json", "math", "datetime", "re", "typing",
    "authshield.utils", "authshield.logging",
    "authshield.validation", "authshield.config",
    "pydantic", "structlog",
}

# Blocked imports
BLOCKED_IMPORTS = {
    "os", "subprocess", "ctypes", "importlib",
    "socket", "http", "urllib", "requests",
    "eval", "exec", "compile",
}
```

### 5.3 Subprocess Isolation (Level 2)

```python
from authshield.plugins import SandboxedPluginRunner

runner = SandboxedPluginRunner(
    isolation_level=2,
    timeout_seconds=30,
    memory_limit_mb=256,
    allowed_permissions=["filesystem:read", "database:read"],
)

# Execute plugin function in sandbox
result = await runner.execute(
    plugin_id="my-plugin",
    function="process_data",
    args=(input_data,),
    kwargs={"format": "json"},
)
```

---

## 6. Dependency Resolution

### 6.1 Dependency Graph

Plugins declare dependencies on other plugins and core platform modules:

```toml
[plugin.depends_on]
# Other plugins
plugins = [
    "shared-utils >=1.0.0",
    "reporting-engine >=2.0.0",
]

# Core platform modules
core = [
    "auth-core >=1.0.0",
    "learning-engine >=1.0.0",
]
```

### 6.2 Resolution Algorithm

```python
from authshield.plugins import DependencyResolver

resolver = DependencyResolver()

# Resolve all plugin dependencies
resolution = resolver.resolve(plugins=installed_plugins)

if resolution.conflicts:
    for conflict in resolution.conflicts:
        logger.error(
            "plugin.dependency.conflict",
            plugin_a=conflict.plugin_a,
            plugin_b=conflict.plugin_b,
            requirement=conflict.requirement,
        )

if resolution.missing:
    for missing in resolution.missing:
        logger.error(
            "plugin.dependency.missing",
            plugin=missing.plugin,
            required_by=missing.required_by,
            requirement=missing.requirement,
        )

# Load plugins in dependency order
for plugin in resolution.load_order:
    plugin.load()
```

### 6.3 Topological Sort

```
shared-utils (no deps)
    ↓
learning-engine (depends on shared-utils)
    ↓
custom-assessment (depends on learning-engine, shared-utils)
    ↓
reporting-addon (depends on custom-assessment, learning-engine)
```

---

## 7. Digital Signature Verification

### 7.1 Signing Process

```python
from authshield.crypto import DigitalSignature

signer = DigitalSignature(algorithm="ed25519")

# Developer generates keypair (one-time)
key_pair = signer.generate_keypair()

# Developer signs plugin
signature = signer.sign_plugin(
    plugin_path=Path("./my-plugin/"),
    private_key=key_pair.private_key,
)

# Signature stored in manifest.json
manifest["signature"] = {
    "algorithm": "ed25519",
    "public_key": key_pair.public_key_b64,
    "signature": signature.b64,
}
```

### 7.2 Verification Process

```python
from authshield.plugins import SignatureVerifier

verifier = SignatureVerifier(
    trusted_keys_dir=Path("~/.config/authshield-lab/trusted-keys/"),
)

# Verify plugin signature
result = verifier.verify(manifest=manifest, plugin_path=plugin_path)

if not result.valid:
    logger.error(
        "plugin.signature.invalid",
        plugin=manifest["name"],
        reason=result.reason,
    )
    raise PluginLoadError(f"Invalid signature: {result.reason}")

# Verify file integrity
integrity = verifier.verify_integrity(
    plugin_path=plugin_path,
    expected_checksum=manifest["checksum"]["value"],
    algorithm=manifest["checksum"]["algorithm"],
)
```

### 7.3 Trusted Key Management

```
~/.config/authshield-lab/trusted-keys/
├── keys.toml
├── authshield-team.key      # Official AuthShield team key
├── community.key            # Community plugins key
└── custom.key               # User-added trusted key
```

```toml
# keys.toml
[[trusted_keys]]
name = "AuthShield Team"
key_path = "authshield-team.key"
trust_level = "official"
allowed_plugins = ["authshield-*"]

[[trusted_keys]]
name = "Community"
key_path = "community.key"
trust_level = "community"
allowed_plugins = ["community-*"]

[[trusted_keys]]
name = "Custom"
key_path = "custom.key"
trust_level = "custom"
allowed_plugins = ["*"]
```

---

## 8. Safe Loading

### 8.1 Loading Sequence

```
1. Discovery
   ├── Scan plugin directory
   ├── Parse entry points
   └── Parse manifests

2. Validation
   ├── Verify signatures
   ├── Check checksums
   ├── Validate permissions
   └── Check compatibility

3. Dependency Resolution
   ├── Build dependency graph
   ├── Check for conflicts
   ├── Topological sort
   └── Verify load order

4. Loading
   ├── Import plugin module
   ├── Lazy-load components
   ├── Register routes/menus/widgets
   └── Call on_load() hook

5. Activation
   ├── Enable plugin
   ├── Notify platform
   └── Log activation
```

### 8.2 Lazy Import Strategy

```python
# Plugin __init__.py
class MyPlugin:
    def __init__(self):
        self._heavy_module = None

    @property
    def heavy_module(self):
        """Lazy import of heavy dependency"""
        if self._heavy_module is None:
            import heavy_dependency
            self._heavy_module = heavy_dependency
        return self._heavy_module

    async def on_load(self):
        """Called when plugin is loaded"""
        pass

    async def on_activate(self):
        """Called when plugin is activated"""
        pass
```

### 8.3 Error Isolation

```python
from authshield.plugins import PluginLoader

loader = PluginLoader()

try:
    plugin = loader.load(plugin_id="my-plugin")
except PluginLoadError as e:
    logger.error("plugin.load.failed", plugin="my-plugin", error=str(e))
    # Plugin is marked as failed; other plugins continue loading
    # User sees plugin as "Failed to load" in UI
    # Error details available for debugging
```

### 8.4 Timeout Protection

```python
from authshield.plugins import PluginLoader

loader = PluginLoader(
    load_timeout=10.0,  # 10 seconds max for plugin loading
    init_timeout=5.0,   # 5 seconds max for plugin initialization
)

# Plugin loading is cancelled if it exceeds timeout
# Error logged and plugin marked as failed
```

---

## 9. Safe Unloading

### 9.1 Unloading Sequence

```
1. Deactivation
   ├── Call on_deactivate() hook
   ├── Unregister routes/menus/widgets
   └── Stop background tasks

2. State Persistence
   ├── Save plugin state to plugin data directory
   ├── Commit pending database changes
   └── Flush buffered log entries

3. Resource Cleanup
   ├── Close database connections
   ├── Release file handles
   ├── Cancel async tasks
   └── Clear caches

4. Module Unload
   ├── Remove from sys.modules
   ├── Clear import cache
   └── Release memory
```

### 9.2 State Persistence

```python
class MyPlugin:
    async def on_deactivate(self):
        """Save state before unloading"""
        state = {
            "last_run": datetime.now().isoformat(),
            "results": self.results_cache,
            "settings": self.settings,
        }
        self.save_state(state)  # Saved to plugin data directory

    async def on_load(self):
        """Restore state after loading"""
        state = self.load_state()
        if state:
            self.results_cache = state.get("results", {})
            self.settings = state.get("settings", {})
```

---

## 10. Extension Points

### 10.1 Route Extension Points

```python
# Plugin registers API routes
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/my-plugin", tags=["my-plugin"])

@router.get("/data")
async def get_data():
    return {"message": "Hello from plugin"}

# Registered via entry point:
# [project.entry-points."authshield.routes"]
# my_api = "my_plugin.routes:router"
```

### 10.2 Menu Item Extension Points

```toml
# plugin.toml
[plugin.provides]
menu_items = [
    { label = "Tools > My Plugin", action = "my-plugin:open", icon = "puzzle" },
    { label = "Reports > Custom Report", action = "my-plugin:report", icon = "file-text" },
]
```

### 10.3 Dashboard Widget Extension Points

```python
# Plugin registers dashboard widget
class MyWidget:
    component = "MyWidgetComponent"  # React component name
    title = "My Custom Widget"
    size = {"w": 4, "h": 3}  # Grid units
    refresh_interval = 60  # seconds

    async def get_data(self):
        return {"metric": 42, "trend": "up"}

# Registered via entry point:
# [project.entry-points."authshield.widgets"]
# my_widget = "my_plugin.widgets:MyWidget"
```

### 10.4 Report Type Extension Points

```python
# Plugin registers custom report type
class CustomReport:
    name = "Custom Assessment Report"
    template = "custom_report.html"
    formats = ["pdf", "csv", "json"]

    async def generate(self, assessment_id, options):
        # Custom report generation logic
        return report_data

# Registered via entry point:
# [project.entry-points."authshield.reports"]
# custom = "my_plugin.reports:CustomReport"
```

### 10.5 Assessment Type Extension Points

```python
# Plugin registers custom assessment type
class CustomAssessment:
    type_name = "custom_quiz"
    question_types = ["multiple_choice", "true_false", "short_answer"]

    async def create(self, config):
        return assessment

    async def grade(self, assessment, answers):
        return grading_result

    async def get_results(self, assessment_id):
        return results

# Registered via entry point:
# [project.entry-points."authshield.assessments"]
# custom_quiz = "my_plugin.assessments:CustomAssessment"
```

### 10.6 Theme Extension Points

```python
# Plugin registers theme overrides
class CustomTheme:
    name = "My Custom Theme"
    base_theme = "default"  # Inherits from default theme
    tokens = {
        "color-primary": "#0066cc",
        "color-background": "#ffffff",
        "font-size-base": "16px",
        "spacing-unit": "8px",
    }

# Registered via entry point:
# [project.entry-points."authshield.themes"]
# my_theme = "my_plugin.theme:CustomTheme"
```

### 10.7 Localization Extension Points

```python
# Plugin registers translations
def get_translations():
    return {
        "en": load_json("locales/en.json"),
        "te": load_json("locales/te.json"),
        "hi": load_json("locales/hi.json"),
    }

# Registered via entry point:
# [project.entry-points."authshield.localizations"]
# my_locales = "my_plugin.locales:get_translations"
```

---

## 11. Plugin Lifecycle Hooks

| Hook | When | Purpose |
|------|------|---------|
| `on_load()` | After import | Initialize resources, register components |
| `on_activate()` | When enabled | Start background tasks, open connections |
| `on_deactivate()` | When disabled | Stop tasks, save state |
| `on_unload()` | Before removal | Final cleanup, release resources |
| `on_config_change()` | When config changes | Update settings, reconfigure |
| `on_platform_update()` | When platform updates | Handle compatibility changes |

---

## 12. Plugin API

### 12.1 Plugin Context

```python
from authshield.plugins import PluginContext

class MyPlugin:
    def __init__(self, context: PluginContext):
        self.context = context
        self.db = context.get_database()  # Plugin-scoped database
        self.config = context.get_config()  # Plugin config
        self.logger = context.get_logger()  # Namespaced logger
        self.a11y = context.get_a11y()  # Accessibility helpers
        self.i18n = context.get_i18n()  # Localization
```

### 12.2 Plugin Database

```python
# Plugin creates its own tables
class MyPlugin:
    async def on_load(self):
        async with self.db.engine.begin() as conn:
            await conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS plugin_my_plugin_data (
                        id TEXT PRIMARY KEY,
                        key TEXT NOT NULL,
                        value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            )
```

### 12.3 Plugin Event System

```python
from authshield.plugins import EventBus

# Plugin listens to events
class MyPlugin:
    async def on_load(self):
        self.context.events.on("user.login", self.handle_user_login)
        self.context.events.on("assessment.completed", self.handle_assessment)

    async def handle_user_login(self, event):
        self.logger.info("user.login.observed", user_id=event.user_id)

    async def handle_assessment(self, event):
        self.logger.info("assessment.observed", assessment_id=event.assessment_id)

# Plugin emits events
class MyPlugin:
    async def do_something(self):
        await self.context.events.emit("my-plugin.action", {
            "action": "data_processed",
            "count": 42,
        })
```

---

## 13. Plugin Security Summary

| Security Measure | Implementation |
|-----------------|---------------|
| **Capability-based permissions** | `plugin.toml` declares required permissions; enforced at load time |
| **Digital signature verification** | Ed25519 signatures; trusted key management |
| **Integrity verification** | SHA-256 checksums for all plugin files |
| **Import restrictions** | Whitelist of allowed imports; blocked dangerous modules |
| **Sandboxed execution** | Optional subprocess isolation with resource limits |
| **Network blocking** | `network:external` permission denied by default |
| **Timeout protection** | Configurable load/init timeouts |
| **Error isolation** | Failed plugins don't affect other plugins or core |
| **Audit logging** | All plugin actions logged for security review |

---

*Document maintained by the AuthShield Lab Architecture Team. Review quarterly.*
