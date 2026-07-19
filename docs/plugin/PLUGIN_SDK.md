# AuthShield Lab — Plugin SDK

> **Version:** 1.0.0
> **Status:** Authoritative
> **See also:** [Plugin Architecture](PLUGIN_ARCHITECTURE.md) · [Plugin Manifest](PLUGIN_MANIFEST_SPECIFICATION.md)

---

## 1. Overview

The Plugin SDK is the public API surface that plugins use to interact with the AuthShield
Lab platform. Every API is accessible through the `PluginContext` object passed to lifecycle
hooks.

The SDK is designed for **offline-first** operation. All API calls resolve locally; no
network access is required or permitted from within a plugin sandbox.

---

## 2. SDK API Reference

### 2.1 Configuration API

**Purpose:** Read and write configuration values scoped to the plugin's namespace.

```python
class ConfigurationAPI:
    def get_config(self, key: str, default: Any = None) -> Any:
        """Read a configuration value. Key is dot-separated (e.g. 'theme.primary_color')."""

    def set_config(self, key: str, value: Any) -> None:
        """Write a configuration value. Only keys declared in the plugin's config schema are writable."""

    def list_configs(self, prefix: str = "") -> dict[str, Any]:
        """List all configuration keys under the given prefix."""
```

**Example:**

```python
async def on_init(self, ctx: PluginContext) -> None:
    refresh_rate = ctx.config.get_config("dashboard.refresh_rate", default=30)
    ctx.config.set_config("dashboard.last_view", "threats")
```

**Versioning:** Stable since API level `@1`.

**Deprecation:** `set_config` for non-declared keys will be removed in API level `@3`.

---

### 2.2 Logging API

**Purpose:** Write structured log entries to the platform's logging subsystem.

```python
class LoggingAPI:
    def log_info(self, message: str, **extra: Any) -> None: ...
    def log_warning(self, message: str, **extra: Any) -> None: ...
    def log_error(self, message: str, *, exc_info: bool = False, **extra: Any) -> None: ...
    def log_debug(self, message: str, **extra: Any) -> None: ...
```

**Example:**

```python
async def on_activate(self, ctx: PluginContext) -> None:
    ctx.logging.log_info("Plugin activated", services_count=3)
```

**Versioning:** Stable since API level `@1`.

**Rules:**
- Log messages are namespaced to the plugin (`plugin.<plugin_id>`).
- `log_error` with `exc_info=True` includes the traceback.
- Debug logs are only written when `platform.json → log_level` is `debug`.

---

### 2.3 Events API

**Purpose:** Publish and subscribe to platform events.

```python
class EventsAPI:
    async def publish_event(self, topic: str, payload: dict) -> None:
        """Publish an event to the bus."""

    def subscribe_event(self, topic: str, handler: Callable[[dict], Awaitable[None]]) -> SubscriptionHandle:
        """Subscribe to events matching the topic. Supports wildcards (e.g. 'lab.*')."""

    def unsubscribe(self, handle: SubscriptionHandle) -> None:
        """Cancel a subscription."""
```

**Example:**

```python
async def on_activate(self, ctx: PluginContext) -> None:
    ctx.events.subscribe_event("lab.completed", self._on_lab_completed)

async def _on_lab_completed(self, payload: dict) -> None:
    lab_id = payload["lab_id"]
    self.logging.log_info(f"Lab {lab_id} completed")
```

**Versioning:** Stable since API level `@1`. Async handlers required since `@2`.

---

### 2.4 Reporting API

**Purpose:** Register and generate reports.

```python
class ReportingAPI:
    def register_report(self, report_id: str, generator: ReportGenerator) -> None:
        """Register a report type."""

    async def generate_report(self, report_id: str, params: dict) -> ReportResult:
        """Generate a report with the given parameters."""
```

**Example:**

```python
async def on_activate(self, ctx: PluginContext) -> None:
    ctx.reports.register_report("threat-summary", self._generate_threat_summary)

async def _generate_threat_summary(self, params: dict) -> ReportResult:
    return ReportResult(
        title="Threat Summary",
        format="pdf",
        data={"total_threats": 42}
    )
```

**Versioning:** Stable since API level `@1`.

---

### 2.5 Localization API

**Purpose:** Translate strings and manage locale.

```python
class LocalizationAPI:
    def translate(self, key: str, **kwargs: Any) -> str:
        """Translate a key using the active locale. Falls back to base locale."""

    def translate_plural(self, key: str, count: int, **kwargs: Any) -> str:
        """Translate with pluralization support."""

    def get_locale(self) -> str:
        """Return the active locale code (e.g. 'de-DE')."""

    def set_locale(self, locale: str) -> None:
        """Override the locale for this plugin only (does not affect other plugins)."""

    def get_available_locales(self) -> list[str]:
        """List locales for which translations are available."""
```

**Example:**

```python
async def on_activate(self, ctx: PluginContext) -> None:
    greeting = ctx.localization.translate("dashboard.greeting", name="Admin")
    # Returns "Welcome, Admin!" in English or "Willkommen, Admin!" in German.
```

**Versioning:** `translate_plural` added in API level `@2`.

---

### 2.6 Accessibility API

**Purpose:** Register accessible components, manage focus, and announce changes.

```python
class AccessibilityAPI:
    def register_component(self, component_id: str, metadata: AccessibilityMetadata) -> None:
        """Register an accessible component with ARIA metadata."""

    def announce(self, message: str, priority: str = "polite") -> None:
        """Announce a message to screen readers. Priority: 'polite' | 'assertive'."""

    def focus_management(self, target_id: str) -> None:
        """Move focus to the specified component."""

    def get_contrast_ratio(self, foreground: str, background: str) -> float:
        """Calculate WCAG contrast ratio between two colors."""
```

**Example:**

```python
async def on_activate(self, ctx: PluginContext) -> None:
    ctx.accessibility.register_component("threat-panel", AccessibilityMetadata(
        role="region",
        label="Threat Dashboard",
        description="Real-time threat visualization"
    ))
    ctx.accessibility.announce("Threat dashboard loaded with 3 active threats.")
```

**Versioning:** Stable since API level `@1`. `get_contrast_ratio` added in `@2`.

---

### 2.7 Storage API

**Purpose:** Persistent key-value storage scoped to the plugin.

```python
class StorageAPI:
    def get_store(self, key: str, default: Any = None) -> Any:
        """Read a value from the plugin's persistent store."""

    def set_store(self, key: str, value: Any) -> None:
        """Write a value to the plugin's persistent store."""

    def delete_store(self, key: str) -> None:
        """Delete a key from the store."""

    def list_store(self, prefix: str = "") -> dict[str, Any]:
        """List all keys under the given prefix."""
```

**Example:**

```python
async def on_init(self, ctx: PluginContext) -> None:
    last_scan = ctx.storage.get_store("last_scan_time")
    if last_scan:
        self.logging.log_info(f"Last scan was at {last_scan}")

    ctx.storage.set_store("last_scan_time", datetime.utcnow().isoformat())
```

**Versioning:** Stable since API level `@1`.

**Rules:**
- Storage is isolated per plugin. Plugin A cannot read Plugin B's store.
- Maximum storage per plugin: 50 MB (configurable in `platform.json`).
- Values must be JSON-serializable.

---

### 2.8 Validation API

**Purpose:** Validate user input and data schemas.

```python
class ValidationAPI:
    def validate_input(self, value: Any, rules: ValidationRules) -> ValidationResult:
        """Validate a value against a set of rules."""

    def validate_schema(self, data: Any, schema: dict) -> ValidationResult:
        """Validate data against a JSON Schema."""
```

**Example:**

```python
result = ctx.validation.validate_input(port, rules=ValidationRules(
    type="integer",
    minimum=1,
    maximum=65535
))
if not result.is_valid:
    ctx.notifications.show_toast(f"Invalid port: {result.errors}")
```

**Versioning:** Stable since API level `@1`.

---

### 2.9 Notifications API

**Purpose:** Display toast messages, dialogs, and notifications to the user.

```python
class NotificationsAPI:
    def show_toast(self, message: str, *, level: str = "info", duration_ms: int = 3000) -> None:
        """Show a toast notification. Level: 'info' | 'success' | 'warning' | 'error'."""

    async def show_dialog(self, title: str, message: str, *, buttons: list[str] = None) -> str:
        """Show a modal dialog and return the button text the user clicked."""

    def show_notification(self, title: str, body: str, *, icon: str = None) -> None:
        """Show a system notification (if permission granted)."""
```

**Example:**

```python
async def on_activate(self, ctx: PluginContext) -> None:
    ctx.notifications.show_toast("Plugin activated successfully!", level="success")
    choice = await ctx.notifications.show_dialog(
        "Confirm",
        "Run initial scan?",
        buttons=["Yes", "No"]
    )
```

**Versioning:** `show_notification` added in API level `@2`. System notifications require
OS permission; the platform will not grant this without user consent.

---

### 2.10 UI Extension API

**Purpose:** Register UI panels, tabs, and toolbar items in the Electron frontend.

```python
class UIExtensionAPI:
    def register_panel(self, *, id: str, title: str, icon: str, component: str, position: str = "sidebar") -> None:
        """Register a UI panel in the sidebar or main area."""

    def register_tab(self, *, id: str, title: str, component: str, parent_panel: str) -> None:
        """Register a tab within an existing panel."""

    def register_toolbar(self, *, id: str, label: str, icon: str, command: str) -> None:
        """Register a toolbar button that executes a command."""
```

**Example:**

```python
async def on_activate(self, ctx: PluginContext) -> None:
    ctx.ui.register_panel(
        id="threat-dashboard",
        title="Threat Dashboard",
        icon="shield-alert",
        component="ThreatDashboardPanel",
        position="sidebar"
    )
```

**Versioning:** Stable since API level `@1`.

**Rules:**
- `component` must be a React component name registered by the plugin's frontend bundle.
- Panel IDs must be globally unique.
- Maximum 20 panels per plugin.

---

### 2.11 Commands API

**Purpose:** Register and execute CLI/API commands.

```python
class CommandsAPI:
    def register_command(self, *, name: str, handler: Callable, description: str) -> None:
        """Register a command that can be invoked via CLI or API."""

    async def execute_command(self, name: str, args: dict | None = None) -> Any:
        """Execute a registered command."""
```

**Example:**

```python
async def on_activate(self, ctx: PluginContext) -> None:
    ctx.commands.register_command(
        name="threat-dashboard:scan",
        handler=self._handle_scan,
        description="Run a defensive network scan"
    )

async def _handle_scan(self, args: dict) -> dict:
    return {"status": "completed", "threats_found": 0}
```

**Versioning:** Stable since API level `@1`.

---

### 2.12 Queries API

**Purpose:** Register and execute data queries.

```python
class QueriesAPI:
    def register_query(self, *, name: str, handler: Callable, description: str) -> None:
        """Register a data query."""

    async def execute_query(self, name: str, params: dict | None = None) -> Any:
        """Execute a registered query."""
```

**Example:**

```python
async def on_activate(self, ctx: PluginContext) -> None:
    ctx.queries.register_query(
        name="threat-dashboard:recent-threats",
        handler=self._query_recent_threats,
        description="Retrieve recent threats from the last 24 hours"
    )
```

**Versioning:** Stable since API level `@1`.

---

### 2.13 Diagnostics API

**Purpose:** Health checks and system information.

```python
class DiagnosticsAPI:
    def health_check(self) -> HealthStatus:
        """Return the plugin's health status."""

    def system_info(self) -> SystemInfo:
        """Return platform system information (read-only)."""
```

**Example:**

```python
async def on_activate(self, ctx: PluginContext) -> None:
    info = ctx.diagnostics.system_info()
    self.logging.log_info(f"Platform version: {info.platform_version}")
    self.logging.log_info(f"Python version: {info.python_version}")
```

**Versioning:** Stable since API level `@1`.

---

## 3. SDK Versioning Rules

| Rule | Description |
|---|---|
| **Backward Compatible** | New methods, new optional parameters, new event topics. |
| **Breaking Change** | Removing methods, changing required parameters, changing return types. |
| **Deprecation Notice** | A method is deprecated one major version before removal. Deprecated methods emit a warning. |
| **Compatibility Shim** | The kernel provides shims for deprecated APIs. Shims are removed after two major versions. |

---

## 4. SDK Compatibility Policy

- Plugins targeting API level `@N` must work on all platform versions that support level `@N`.
- The kernel maintains backward compatibility for at least two major versions.
- Plugins should target the **oldest** API level that provides the features they need.

---

## 5. SDK Import

Plugins import the SDK from:

```python
from authshield_sdk import PluginBase, PluginContext
from authshield_sdk.types import (
    ReportResult, HealthStatus, SystemInfo,
    ValidationRules, ValidationResult, AccessibilityMetadata,
    SubscriptionHandle,
)
```

The SDK is bundled with the platform and available in the plugin sandbox's import path.

---

## 6. References

- [Plugin Architecture](PLUGIN_ARCHITECTURE.md)
- [Plugin Manifest](PLUGIN_MANIFEST_SPECIFICATION.md)
- [Plugin Sandbox](PLUGIN_SANDBOX.md)
- [Plugin Developer Guide](PLUGIN_DEVELOPER_GUIDE.md)

---

*End of document.*
