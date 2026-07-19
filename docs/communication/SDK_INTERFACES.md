# SDK Interface Contracts

## Document Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Status | Authoritative |
| Last Updated | 2026-07-19 |
| Owner | Architecture Team |
| Classification | Internal |

---

## 1. Overview

The AuthShield Lab SDK provides a stable, versioned API surface for plugin developers. All SDK methods are defined as Python Protocol classes, enabling type-safe interface contracts. The SDK acts as a façade over core services, enforcing permissions, rate limiting, and input validation for every call.

### 1.1 Design Principles

| Principle | Description |
|-----------|-------------|
| Protocol-Based | All interfaces use Python `typing.Protocol` for structural subtyping |
| Immutable Contracts | Once released, interface signatures cannot change within a major version |
| Defensive Validation | Every call validates inputs before forwarding to services |
| Audit Trail | Every SDK call is logged with plugin ID, method, and duration |
| Fail-Fast | Errors are returned immediately, never swallowed |
| Thread Safety | All SDK methods are safe to call from any async context |

### 1.2 SDK Version History

| Version | Changes | Status |
|---------|---------|--------|
| 1.0.0 | Initial SDK release | Current |
| 1.1.0 | Added accessibility API | Current |
| 1.2.0 | Added diagnostics API | Current |
| 2.0.0 | Planned: async-first redesign | Deprecated |

---

## 2. Configuration API

### 2.1 Protocol Definition

```python
from typing import Protocol, Any

class ConfigurationAPI(Protocol):
    """SDK interface for platform configuration access."""

    async def get_config(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key.
        
        Args:
            key: Configuration key in dot notation (e.g., 'security.max_login_attempts')
            default: Value to return if key is not found
            
        Returns:
            The configuration value, or default if not found
            
        Raises:
            ConfigKeyNotFoundError: If key is invalid and no default provided
            PermissionDeniedError: If plugin lacks config.read permission
        """
        ...

    async def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key in dot notation
            value: New value (must be JSON-serializable)
            
        Raises:
            ConfigValidationError: If value fails validation
            ConfigReadOnlyError: If key is read-only
            PermissionDeniedError: If plugin lacks config.write permission
        """
        ...

    async def list_configs(self, prefix: str = "") -> dict[str, Any]:
        """List all configuration values matching a prefix.
        
        Args:
            prefix: Optional prefix filter (e.g., 'security')
            
        Returns:
            Dictionary of matching configuration key-value pairs
        """
        ...

    async def reset_config(self, key: str) -> None:
        """Reset a configuration value to its default.
        
        Args:
            key: Configuration key to reset
            
        Raises:
            ConfigKeyNotFoundError: If key does not exist
            PermissionDeniedError: If plugin lacks config.write permission
        """
        ...
```

### 2.2 Versioning

| Version | Change | Compatibility |
|---------|--------|---------------|
| 1.0.0 | Initial release | Baseline |
| 1.1.0 | Added `prefix` parameter to `list_configs` | Backward compatible |
| 1.2.0 | Added `category` parameter to `list_configs` | Backward compatible |

### 2.3 Deprecation Rules

- Parameters deprecated with minimum 2 minor versions notice
- Deprecated parameters remain functional but trigger `SDKDeprecationWarning`
- Removed in next major version only

### 2.4 Thread Safety

All methods are fully thread-safe. Concurrent calls from different plugin tasks are serialized at the SDK Runtime level.

---

## 3. Logging API

### 3.1 Protocol Definition

```python
class LoggingAPI(Protocol):
    """SDK interface for structured logging."""

    async def log_info(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Log an informational message.
        
        Args:
            message: Log message (max 10,000 characters)
            context: Optional structured context data
        """
        ...

    async def log_warning(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Log a warning message.
        
        Args:
            message: Warning message (max 10,000 characters)
            context: Optional structured context data
        """
        ...

    async def log_error(
        self,
        message: str,
        error: Exception | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Log an error message.
        
        Args:
            message: Error message (max 10,000 characters)
            error: Optional exception object
            context: Optional structured context data
        """
        ...

    async def log_debug(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Log a debug message. Only emitted when debug logging is enabled.
        
        Args:
            message: Debug message (max 10,000 characters)
            context: Optional structured context data
        """
        ...
```

### 3.2 Logging Levels

| Level | When to Use | Default Visibility |
|-------|------------|-------------------|
| `debug` | Detailed diagnostic information | Off by default |
| `info` | General operational messages | Always on |
| `warning` | Unexpected but non-critical situations | Always on |
| `error` | Failures that require attention | Always on |

### 3.3 Log Enrichment

All plugin log entries are automatically enriched with:
- Plugin ID
- Plugin name and version
- Timestamp (ISO 8601)
- Log level
- Correlation ID (if in request context)

### 3.4 Sensitive Data Filtering

The SDK automatically redacts the following from log messages:
- Passwords and tokens
- Session IDs
- Personal identifiable information (PII)
- Configuration values marked as sensitive

---

## 4. Events API

### 4.1 Protocol Definition

```python
from typing import Callable, Coroutine

class EventsAPI(Protocol):
    """SDK interface for event bus interaction."""

    async def publish_event(
        self,
        event_type: str,
        payload: dict[str, Any],
        priority: str = "normal",
    ) -> PublishResult:
        """Publish an event to the event bus.
        
        Args:
            event_type: Event type (e.g., 'plugin.my-plugin.scan-complete')
            payload: Event payload (must be JSON-serializable)
            priority: Event priority ('low', 'normal', 'high', 'critical')
            
        Returns:
            PublishResult with delivery statistics
            
        Raises:
            EventPermissionError: If plugin lacks permission to publish this event type
            EventValidationError: If payload fails schema validation
        """
        ...

    async def subscribe_event(
        self,
        event_type: str,
        handler: Callable[[Event], Coroutine],
        filter_fn: Callable[[Event], bool] | None = None,
    ) -> SubscriptionHandle:
        """Subscribe to events on the event bus.
        
        Args:
            event_type: Event type pattern (supports '*' wildcard)
            handler: Async callback function
            filter_fn: Optional filter predicate
            
        Returns:
            SubscriptionHandle for managing the subscription
            
        Raises:
            EventPermissionError: If plugin lacks permission to subscribe to this event type
        """
        ...

    async def unsubscribe_event(
        self,
        handle: SubscriptionHandle,
    ) -> None:
        """Unsubscribe from events.
        
        Args:
            handle: Subscription handle returned by subscribe_event
        """
        ...
```

### 4.2 Event Type Restrictions

Plugins can only subscribe to event types matching their declared permissions. Attempting to subscribe to unauthorized events raises `EventPermissionError`.

### 4.3 Subscription Limits

| Limit | Value | Description |
|-------|-------|-------------|
| Max subscriptions per plugin | 50 | Prevents resource exhaustion |
| Max event payload size | 1 MB | Prevents memory issues |
| Handler execution timeout | 30s | Prevents blocking event bus |
| Max concurrent handlers | 10 | Prevents thread pool exhaustion |

---

## 5. Storage API

### 5.1 Protocol Definition

```python
class StorageAPI(Protocol):
    """SDK interface for persistent key-value storage."""

    async def get_store(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve a value from plugin storage.
        
        Storage is namespaced per plugin; plugins cannot access each other's storage.
        
        Args:
            key: Storage key (alphanumeric, dots, hyphens, underscores)
            default: Value to return if key is not found
            
        Returns:
            The stored value, or default if not found
        """
        ...

    async def set_store(
        self,
        key: str,
        value: Any,
        ttl: float | None = None,
    ) -> None:
        """Store a value in plugin storage.
        
        Args:
            key: Storage key
            value: Value to store (must be JSON-serializable)
            ttl: Optional time-to-live in seconds (None = no expiration)
            
        Raises:
            StorageQuotaExceededError: If storage limit reached
            StorageValidationError: If value fails validation
        """
        ...

    async def delete_store(self, key: str) -> None:
        """Delete a value from plugin storage.
        
        Args:
            key: Storage key to delete
        """
        ...

    async def list_store(
        self,
        prefix: str = "",
    ) -> dict[str, Any]:
        """List all stored values matching a prefix.
        
        Args:
            prefix: Optional prefix filter
            
        Returns:
            Dictionary of matching key-value pairs
        """
        ...

    async def get_store_path(self) -> str:
        """Get the filesystem path for plugin storage.
        
        Returns:
            Absolute path to the plugin's storage directory
            
        Note: Direct filesystem access is not permitted.
        This is informational only.
        """
        ...
```

### 5.2 Storage Limits

| Limit | Value |
|-------|-------|
| Max storage per plugin | 10 MB |
| Max key length | 256 characters |
| Max value size | 1 MB |
| Max entries per plugin | 10,000 |
| Default TTL | No expiration |

---

## 6. Reporting API

### 6.1 Protocol Definition

```python
class ReportingAPI(Protocol):
    """SDK interface for report generation."""

    async def register_report_type(
        self,
        report_type: str,
        handler: Callable[[ReportRequest], Coroutine[Report]],
        metadata: ReportMetadata,
    ) -> ReportTypeHandle:
        """Register a custom report type.
        
        Args:
            report_type: Unique report type identifier
            handler: Async function that generates the report
            metadata: Report metadata (title, description, parameters)
            
        Returns:
            ReportTypeHandle for managing the report type
        """
        ...

    async def generate_report(
        self,
        report_type: str,
        parameters: dict[str, Any],
    ) -> Report:
        """Generate a report of the specified type.
        
        Args:
            report_type: Report type identifier
            parameters: Report-specific parameters
            
        Returns:
            Generated report
            
        Raises:
            ReportGenerationError: If report generation fails
            ReportNotFoundError: If report type is not registered
        """
        ...

    async def list_reports(self) -> list[ReportTypeInfo]:
        """List all registered report types.
        
        Returns:
            List of available report type information
        """
        ...
```

### 6.2 Report Metadata

```python
@dataclass
class ReportMetadata:
    title: str
    description: str
    parameters: list[ReportParameter]
    required_permissions: list[str]
    accessibility_compatible: bool = True
    export_formats: list[str] = field(default_factory=lambda: ["json"])
```

---

## 7. Accessibility API

### 7.1 Protocol Definition

```python
class AccessibilityAPI(Protocol):
    """SDK interface for accessibility features."""

    async def register_accessible_component(
        self,
        component_id: str,
        component_type: str,
        label: str,
        role: str,
        properties: dict[str, str] | None = None,
    ) -> None:
        """Register an accessible UI component.
        
        Args:
            component_id: Unique component identifier
            component_type: Component type ('button', 'input', 'panel', etc.)
            label: Human-readable label
            role: ARIA role ('button', 'dialog', 'navigation', etc.)
            properties: Additional ARIA properties
        """
        ...

    async def announce_to_screen_reader(
        self,
        message: str,
        priority: str = "polite",
    ) -> None:
        """Announce a message to screen readers.
        
        Args:
            message: Message to announce
            priority: 'polite' (waits) or 'assertive' (interrupts)
        """
        ...

    async def manage_focus(
        self,
        component_id: str,
        action: str = "move",
    ) -> None:
        """Manage keyboard focus.
        
        Args:
            component_id: Target component ID
            action: 'move', 'trap', or 'release'
        """
        ...
```

### 7.2 WCAG Compliance

All accessibility API calls enforce WCAG 2.1 AA compliance:
- Color contrast ratios validated
- Keyboard navigation guaranteed
- Screen reader compatibility verified
- Focus management follows WAI-ARIA patterns

### 7.3 Accessible Component Types

| Type | Role | Required Properties |
|------|------|-------------------|
| `button` | `button` | `label` |
| `input` | `textbox` | `label`, `described_by` |
| `panel` | `region` | `label`, `heading` |
| `dialog` | `dialog` | `label`, `modal` |
| `navigation` | `navigation` | `label` |
| `alert` | `alert` | `label` |
| `link` | `link` | `label` |
| `image` | `img` | `label` (alt text) |

---

## 8. Localization API

### 8.1 Protocol Definition

```python
class LocalizationAPI(Protocol):
    """SDK interface for internationalization."""

    async def translate(
        self,
        key: str,
        variables: dict[str, str] | None = None,
        locale: str | None = None,
    ) -> str:
        """Translate a message key to the current locale.
        
        Args:
            key: Translation key in dot notation (e.g., 'plugin.errors.not_found')
            variables: Interpolation variables (e.g., {'name': 'Plugin A'})
            locale: Optional locale override
            
        Returns:
            Translated string, or key itself if translation not found
        """
        ...

    async def get_current_locale(self) -> str:
        """Get the current active locale.
        
        Returns:
            Locale code (e.g., 'en', 'es', 'fr-CA')
        """
        ...

    async def get_supported_locales(self) -> list[str]:
        """Get list of supported locale codes.
        
        Returns:
            List of locale codes
        """
        ...

    async def register_locale(
        self,
        locale: str,
        translations: dict[str, str],
    ) -> None:
        """Register custom translations for a locale.
        
        Args:
            locale: Locale code
            translations: Dictionary of key-value translation pairs
            
        Raises:
            LocalizationPermissionError: If plugin lacks permission
        """
        ...
```

### 8.2 Translation Key Convention

Plugin translation keys are namespaced:

```
plugin.{plugin_id}.{category}.{key}
```

Example: `plugin.vulnerability-scanner.errors.target_not_found`

---

## 9. Notifications API

### 9.1 Protocol Definition

```python
class NotificationsAPI(Protocol):
    """SDK interface for user notifications."""

    async def show_toast(
        self,
        message: str,
        level: str = "info",
        duration: float = 5.0,
        actions: list[ToastAction] | None = None,
    ) -> str:
        """Show a toast notification.
        
        Args:
            message: Toast message (max 500 characters)
            level: 'info', 'success', 'warning', 'error'
            duration: Display duration in seconds
            actions: Optional action buttons
            
        Returns:
            Toast ID for tracking
        """
        ...

    async def show_dialog(
        self,
        title: str,
        message: str,
        buttons: list[DialogButton],
        modal: bool = True,
    ) -> DialogResponse:
        """Show a dialog box.
        
        Args:
            title: Dialog title
            message: Dialog message
            buttons: Available buttons
            modal: Whether dialog blocks interaction
            
        Returns:
            DialogResponse with selected button
        """
        ...

    async def show_notification(
        self,
        title: str,
        body: str,
        category: str = "general",
        priority: str = "normal",
    ) -> str:
        """Show a persistent notification.
        
        Args:
            title: Notification title
            body: Notification body
            category: Notification category
            priority: 'low', 'normal', 'high'
            
        Returns:
            Notification ID
        """
        ...

    async def show_progress(
        self,
        title: str,
        total: int,
        cancellable: bool = False,
    ) -> ProgressHandle:
        """Show a progress indicator.
        
        Args:
            title: Progress title
            total: Total steps
            cancellable: Whether user can cancel
            
        Returns:
            ProgressHandle for updating progress
        """
        ...
```

### 9.2 Toast Action

```python
@dataclass
class ToastAction:
    label: str
    handler: Callable[[], Coroutine]
    style: str = "default"  # 'default', 'primary', 'danger'
```

### 9.3 Dialog Button

```python
@dataclass
class DialogButton:
    label: str
    value: str
    style: str = "default"  # 'default', 'primary', 'danger'
    accessibility_label: str | None = None
```

---

## 10. Diagnostics API

### 10.1 Protocol Definition

```python
class DiagnosticsAPI(Protocol):
    """SDK interface for system diagnostics."""

    async def health_check(self) -> HealthStatus:
        """Perform a health check of the plugin's subsystems.
        
        Returns:
            HealthStatus with component health information
        """
        ...

    async def get_system_info(self) -> SystemInfo:
        """Get system information.
        
        Returns:
            SystemInfo with platform version, OS, memory, etc.
        """
        ...

    async def report_metric(
        self,
        name: str,
        value: float,
        metric_type: str = "gauge",
        tags: dict[str, str] | None = None,
    ) -> None:
        """Report a custom metric.
        
        Args:
            name: Metric name (dot notation)
            value: Metric value
            metric_type: 'gauge', 'counter', 'histogram'
            tags: Optional metric tags
        """
        ...
```

### 10.2 Health Status

```python
@dataclass
class HealthStatus:
    status: str  # 'healthy', 'degraded', 'unhealthy'
    components: dict[str, ComponentHealth]
    checked_at: str  # ISO 8601

@dataclass
class ComponentHealth:
    name: str
    status: str
    message: str | None = None
    latency_ms: float | None = None
```

### 10.3 System Info

```python
@dataclass
class SystemInfo:
    platform_version: str
    sdk_version: str
    python_version: str
    os_name: str
    os_version: str
    memory_total_mb: float
    memory_available_mb: float
    cpu_count: int
    disk_available_mb: float
    uptime_seconds: float
```

---

## 11. Plugin Management API

### 11.1 Protocol Definition

```python
class PluginManagementAPI(Protocol):
    """SDK interface for querying installed plugins."""

    async def get_installed_plugins(self) -> list[PluginInfo]:
        """List all installed plugins.
        
        Returns:
            List of plugin information objects
        """
        ...

    async def get_plugin_info(self, plugin_id: str) -> PluginInfo:
        """Get detailed information about a specific plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Detailed plugin information
            
        Raises:
            PluginNotFoundError: If plugin is not installed
        """
        ...
```

### 11.2 Plugin Info

```python
@dataclass
class PluginInfo:
    id: str
    name: str
    version: str
    author: str
    description: str
    status: str  # 'enabled', 'disabled', 'error'
    capabilities: list[str]
    installed_at: str
    enabled_at: str | None
    error_count: int
    last_error: str | None
```

---

## 12. SDK Error Handling

### 12.1 Error Hierarchy

```python
class SDKError(Exception):
    """Base SDK error."""
    code: str
    message: str
    details: dict

class PermissionDeniedError(SDKError):
    """Plugin lacks required permission."""
    code = "SDK-PERM-001"

class RateLimitExceededError(SDKError):
    """Plugin exceeded rate limit."""
    code = "SDK-RATE-001"

class ValidationError(SDKError):
    """Input validation failed."""
    code = "SDK-VAL-001"

class TimeoutError(SDKError):
    """SDK call timed out."""
    code = "SDK-TMO-001"

class DeprecationWarning(SDKError):
    """Deprecated API usage detected."""
    code = "SDK-DEP-001"

class PluginStorageQuotaExceededError(SDKError):
    """Plugin storage quota exceeded."""
    code = "SDK-STOR-001"
```

### 12.2 Error Response Format

```python
@dataclass
class SDKErrorResponse:
    code: str
    message: str
    details: dict
    correlation_id: str
    timestamp: str
    plugin_id: str
    method: str
    recoverable: bool
    retry_after: float | None = None
```

---

## 13. SDK Rate Limiting

| API Category | Rate Limit | Window | Burst |
|-------------|------------|--------|-------|
| Configuration | 100/sec | 1 second | 20 |
| Logging | 500/sec | 1 second | 100 |
| Events | 100/sec | 1 second | 20 |
| Storage | 50/sec | 1 second | 10 |
| Reporting | 10/sec | 1 second | 3 |
| Accessibility | 200/sec | 1 second | 50 |
| Localization | 200/sec | 1 second | 50 |
| Notifications | 20/sec | 1 second | 5 |
| Diagnostics | 10/sec | 1 second | 3 |
| Plugin Management | 20/sec | 1 second | 5 |
