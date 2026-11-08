# Plugin Communication Protocol

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

AuthShield Lab's plugin system enables third-party extensions while maintaining strict isolation, security, and stability. Plugins communicate with the core platform exclusively through the SDK Runtime Service, and with each other exclusively through the Event Bus. No direct cross-plugin references are permitted.

### 1.1 Communication Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Plugin Sandbox A                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Plugin Code  │  │ SDK Binding  │  │ Event Queue  │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                  │            │
│  ───────┼─────────────────┼──────────────────┼────────── │
│         │      Message Bus (Filtered)         │            │
│  ───────┼─────────────────┼──────────────────┼────────── │
│         │                 │                  │            │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐   │
│  │ Plugin B     │  │ SDK Binding  │  │ Event Queue  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                    Plugin Sandbox B                       │
└─────────────────────────────────────────────────────────┘
                          │
                    ┌─────▼─────┐
                    │    SDK    │
                    │  Runtime  │
                    │  Service  │
                    └─────┬─────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
        ┌─────▼───┐ ┌─────▼───┐ ┌────▼────┐
        │  Core   │ │  Event  │ │Service  │
        │Services │ │   Bus   │ │ Registry│
        └─────────┘ └─────────┘ └─────────┘
```

---

## 2. Service Discovery

### 2.1 Plugin Registry

The Plugin Registry maintains a catalog of all installed plugins and their capabilities.

```python
@dataclass
class PluginDescriptor:
    id: str
    name: str
    version: str
    author: str
    description: str
    sdk_version_min: str
    sdk_version_max: str
    capabilities: list[str]
    permissions: list[str]
    extension_points: list[str]
    event_subscriptions: list[str]
    commands_registered: list[str]
    lifecycle_hooks: list[str]
    status: PluginStatus
    installed_at: str
    enabled_at: str | None
    error_count: int
    last_error: str | None

class PluginRegistry:
    async def register(self, descriptor: PluginDescriptor) -> None:
        """Register a new plugin with the platform."""
        ...

    async def unregister(self, plugin_id: str) -> None:
        """Remove a plugin from the registry."""
        ...

    async def get_plugin(self, plugin_id: str) -> PluginDescriptor:
        """Retrieve plugin details by ID."""
        ...

    async def list_plugins(
        self,
        status: PluginStatus | None = None,
    ) -> list[PluginDescriptor]:
        """List all registered plugins."""
        ...

    async def find_by_capability(self, capability: str) -> list[PluginDescriptor]:
        """Find plugins that declare a specific capability."""
        ...

    async def find_by_extension_point(
        self,
        extension_point: str,
    ) -> list[PluginDescriptor]:
        """Find plugins that provide a specific extension point."""
        ...
```

### 2.2 Capability Queries

Plugins declare capabilities in their manifest. Other components can query what capabilities are available.

```python
class CapabilityQuery:
    async def query_capabilities(self) -> list[CapabilityDeclaration]:
        """Get all declared capabilities from all plugins."""
        ...

    async def check_capability(
        self,
        plugin_id: str,
        capability: str,
    ) -> bool:
        """Check if a specific plugin has a capability."""
        ...

    async def get_capability_providers(
        self,
        capability: str,
    ) -> list[str]:
        """Get all plugin IDs that provide a capability."""
        ...
```

---

## 3. Event Subscription

### 3.1 Plugin Event Subscription

Plugins subscribe to events through the SDK. The SDK Runtime validates subscriptions against the plugin's declared permissions.

```python
class PluginEventSubscription:
    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[Event], Coroutine],
        filter_fn: Callable[[Event], bool] | None = None,
    ) -> SubscriptionHandle:
        """Subscribe to events. Validates permission before subscribing."""
        ...

    async def unsubscribe(self, handle: SubscriptionHandle) -> None:
        """Cancel an event subscription."""
        ...

    async def list_subscriptions(self) -> list[SubscriptionInfo]:
        """List all active subscriptions for this plugin."""
        ...
```

### 3.2 Allowed Event Types

| Event Type Pattern | Permission Required | Description |
|-------------------|--------------------:|-------------|
| `course.*` | `events.course.read` | Course lifecycle events |
| `learning.*` | `events.learning.read` | Learning progress events |
| `assessment.*` | `events.assessment.read` | Assessment events |
| `plugin.*` | `events.plugin.read` | Plugin lifecycle events |
| `config.*` | `events.config.read` | Configuration change events |
| `app.*` | `events.app.read` | Application events |
| `a11y.*` | `events.accessibility.read` | Accessibility events |
| `plugin.event` | `events.inter_plugin` | Inter-plugin communication |

### 3.3 Event Publishing from Plugins

Plugins can publish events through the SDK. The SDK validates that the plugin has permission to publish events of the specified type.

```python
class PluginEventPublishing:
    async def publish(
        self,
        event_type: str,
        payload: dict,
        priority: str = "normal",
    ) -> PublishResult:
        """Publish an event. Plugin ID is automatically set as source."""
        ...
```

---

## 4. Command Registration

### 4.1 Plugin Commands

Plugins can register new commands that are exposed through the SDK Runtime Service.

```python
class PluginCommandRegistration:
    async def register_command(
        self,
        command_name: str,
        handler: Callable[[dict], Coroutine[dict]],
        schema: dict,
        description: str = "",
    ) -> CommandHandle:
        """Register a new command provided by this plugin."""
        ...

    async def unregister_command(self, handle: CommandHandle) -> None:
        """Unregister a previously registered command."""
        ...

    async def list_commands(self) -> list[CommandInfo]:
        """List all commands registered by this plugin."""
        ...
```

### 4.2 Command Naming Convention

Plugin commands are namespaced to prevent collisions:

```
plugin.{plugin_id}.{command_name}
```

Example: `plugin.vulnerability-scanner.scan-target`

### 4.3 Command Execution Validation

Before executing a plugin command, the SDK Runtime verifies:

1. The plugin is enabled and healthy
2. The command is registered
3. The caller has authorization
4. The input matches the declared schema
5. The plugin has not exceeded its rate limit
6. The plugin is not in an error state

---

## 5. Extension Points

### 5.1 Available Extension Points

| Extension Point | Description | Interface |
|----------------|-------------|-----------|
| `ui.sidebar.panel` | Add panels to the sidebar navigation | `SidebarPanelProvider` |
| `ui.toolbar.item` | Add items to the toolbar | `ToolbarItemProvider` |
| `ui.dashboard.widget` | Add widgets to the dashboard | `DashboardWidgetProvider` |
| `ui.settings.page` | Add settings pages | `SettingsPageProvider` |
| `ui.report.type` | Register custom report types | `ReportTypeProvider` |
| `ui.context.menu` | Add context menu items | `ContextMenuProvider` |
| `ui.command.palette` | Add command palette entries | `CommandPaletteProvider` |
| `data.source` | Provide additional data sources | `DataSourceProvider` |
| `analysis.tool` | Register analysis tools | `AnalysisToolProvider` |
| `export.format` | Add export format support | `ExportFormatProvider` |

### 5.2 Extension Point Registration

```python
class ExtensionPointRegistration:
    async def register_extension(
        self,
        extension_point: str,
        provider: ExtensionProvider,
        metadata: dict,
    ) -> ExtensionHandle:
        """Register an extension at a specific point."""
        ...

    async def unregister_extension(self, handle: ExtensionHandle) -> None:
        """Remove an extension."""
        ...

    async def list_extensions(
        self,
        extension_point: str | None = None,
    ) -> list[ExtensionInfo]:
        """List registered extensions."""
        ...
```

### 5.3 Extension Provider Contracts

Each extension point has a specific provider contract that plugins must implement:

```python
class SidebarPanelProvider:
    async def get_panel_id(self) -> str:
        """Unique panel identifier."""
        ...

    async def get_panel_title(self) -> str:
        """Display title for the panel."""
        ...

    async def render_panel(self) -> PanelContent:
        """Render the panel content."""
        ...

    async def get_icon(self) -> str:
        """Icon identifier or SVG path."""
        ...

    async def get_accessibility_label(self) -> str:
        """Accessible label for screen readers."""
        ...
```

---

## 6. Version Negotiation

### 6.1 SDK Version Compatibility

Plugins declare SDK version compatibility in their manifest:

```python
@dataclass
class SDKCompatibility:
    minimum_version: str    # e.g., "1.2.0"
    maximum_version: str    # e.g., "2.0.0"
    preferred_version: str  # e.g., "1.5.0"
```

### 6.2 Compatibility Matrix

| Plugin SDK Range | Platform Version | Status |
|-----------------|------------------|--------|
| 1.0.0 - 1.4.x | 1.0.0 - 1.4.x | Fully Compatible |
| 1.0.0 - 1.4.x | 1.5.0+ | Forward Compatible |
| 1.5.0+ | 1.0.0 - 1.4.x | Not Compatible |
| 2.0.0+ | 1.x.x | Not Compatible |

### 6.3 Version Negotiation Protocol

```
1. Plugin declares SDK version range in manifest
2. Platform checks current SDK version against range
3. If compatible → proceed with installation
4. If incompatible:
   a. Check if upgrade path exists
   b. Offer migration assistance if available
   c. Reject installation with detailed error
```

### 6.4 API Surface Stability

| Change Type | Version Action | Plugin Impact |
|-------------|---------------|---------------|
| New optional parameter | Minor version | None (backward compatible) |
| New required parameter | Major version | Plugin must update |
| Return type change | Major version | Plugin must update |
| New API method | Minor version | None (additive) |
| API method removed | Major version | Plugin must update |
| Error code change | Major version | Plugin must update |
| Event type added | Minor version | None (additive) |
| Event payload changed | Major version | Plugin must update |

---

## 7. Permission Validation

### 7.1 Permission Model

Every plugin operation is validated against the plugin's declared permissions.

```python
class PermissionValidator:
    async def validate_api_call(
        self,
        plugin_id: str,
        api_method: str,
        args: dict,
    ) -> PermissionResult:
        """Validate that a plugin is allowed to make an API call."""
        ...

    async def validate_event_publish(
        self,
        plugin_id: str,
        event_type: str,
    ) -> PermissionResult:
        """Validate that a plugin can publish an event type."""
        ...

    async def validate_event_subscribe(
        self,
        plugin_id: str,
        event_type: str,
    ) -> PermissionResult:
        """Validate that a plugin can subscribe to an event type."""
        ...

    async def validate_extension_point(
        self,
        plugin_id: str,
        extension_point: str,
    ) -> PermissionResult:
        """Validate that a plugin can register at an extension point."""
        ...
```

### 7.2 Permission Declarations

Permissions are declared in the plugin manifest:

```json
{
  "permissions": {
    "api": [
      "configuration.read",
      "configuration.write",
      "logging.info",
      "events.publish",
      "events.subscribe",
      "storage.read",
      "storage.write",
      "notifications.show"
    ],
    "events": {
      "subscribe": ["course.*", "learning.*"],
      "publish": ["plugin.event"]
    },
    "extension_points": [
      "ui.sidebar.panel",
      "ui.toolbar.item"
    ],
    "commands": [
      "register",
      "invoke"
    ]
  }
}
```

### 7.3 Runtime Permission Checks

```
Plugin makes API call
    │
    ├── SDK intercepts call
    │   ├── Extract plugin_id from context
    │   ├── Extract method name
    │   └── Extract arguments
    │
    ├── Permission check
    │   ├── Plugin is enabled?
    │   ├── Method allowed by declared permissions?
    │   ├── Arguments within allowed scope?
    │   └── Rate limit not exceeded?
    │
    ├── Pass → Execute call → Return result
    └── Fail → Return PermissionDeniedError → Log audit entry
```

---

## 8. Lifecycle Hooks

### 8.1 Lifecycle Phases

```
INSTALLED → ENABLED → ACTIVE → DISABLED → UNINSTALLED
                │                    │
                ▼                    ▼
            ERROR STATE ←───────────┘
```

### 8.2 Hook Definitions

| Hook | When Called | Purpose |
|------|-----------|---------|
| `on_load` | Plugin loaded into memory | Initialize resources, register commands |
| `on_activate` | Plugin enabled by admin | Start background tasks, subscribe to events |
| `on_deactivate` | Plugin disabled by admin | Stop background tasks, unsubscribe from events |
| `on_unload` | Plugin removed from memory | Release all resources, cleanup |
| `on_error` | Plugin encounters error | Handle error, potentially self-disable |
| `on_config_changed` | Platform config changes | React to configuration updates |
| `on_upgrade` | Plugin upgraded to new version | Migrate data, update registrations |

### 8.3 Hook Implementation

```python
class PluginLifecycleHooks:
    async def on_load(self) -> None:
        """Called when plugin is loaded into memory.
        
        Use this hook to:
        - Register commands
        - Set up storage
        - Initialize internal state
        """
        ...

    async def on_activate(self) -> None:
        """Called when plugin is enabled.
        
        Use this hook to:
        - Subscribe to events
        - Start background workers
        - Register extension points
        """
        ...

    async def on_deactivate(self) -> None:
        """Called when plugin is disabled.
        
        Use this hook to:
        - Unsubscribe from events
        - Cancel background workers
        - Persist state
        """
        ...

    async def on_unload(self) -> None:
        """Called when plugin is being removed.
        
        Use this hook to:
        - Release all resources
        - Clean up temporary data
        - Final state persistence
        """
        ...

    async def on_error(self, error: PluginError) -> None:
        """Called when plugin encounters an error.
        
        Use this hook to:
        - Log the error
        - Attempt recovery
        - Decide whether to self-disable
        """
        ...
```

### 8.4 Hook Execution Guarantees

- Hooks are executed sequentially (not concurrently)
- Each hook has a configurable timeout (default: 30 seconds)
- Hook failures are logged but do not prevent lifecycle transitions
- Critical hook failures (on_load, on_unload) trigger automatic disable
- All hook executions are audit-logged

---

## 9. Plugin-to-Core Communication

### 9.1 SDK API Calls

Plugins communicate with core services exclusively through the SDK API. The SDK Runtime routes calls to appropriate services.

```
Plugin Code → SDK API → Permission Check → Service Router → Core Service → Response
```

### 9.2 Supported SDK API Categories

| Category | Methods | Description |
|----------|---------|-------------|
| Configuration | `get_config`, `set_config`, `list_configs`, `reset_config` | Read/write platform configuration |
| Logging | `log_info`, `log_warning`, `log_error`, `log_debug` | Structured logging |
| Events | `publish_event`, `subscribe_event`, `unsubscribe_event` | Event bus interaction |
| Storage | `get_store`, `set_store`, `delete_store`, `list_store` | Persistent key-value storage |
| Reporting | `register_report_type`, `generate_report` | Report generation |
| Accessibility | `register_accessible_component`, `announce_to_screen_reader` | Accessibility features |
| Localization | `translate`, `get_current_locale`, `get_supported_locales` | Internationalization |
| Notifications | `show_toast`, `show_dialog`, `show_notification` | User notifications |
| Diagnostics | `health_check`, `get_system_info`, `report_metric` | System diagnostics |

### 9.3 SDK Call Restrictions

| Restriction | Description |
|-------------|-------------|
| No direct DB access | All data access through SDK APIs only |
| No filesystem access | Storage through SDK Storage API only |
| No network access | Platform is offline-first |
| No process spawning | No subprocess creation |
| No reflection on core | No import/inspect of core modules |
| Rate limiting | 100 calls/second per plugin |
| Timeout enforcement | 30-second maximum per call |

---

## 10. Core-to-Plugin Communication

### 10.1 Event Dispatch

The core communicates to plugins through events on the event bus.

```
Core Service publishes event → Event Bus → Plugin subscriber receives event
```

### 10.2 Command Invocation

The core can invoke commands registered by plugins through the SDK Runtime.

```
Core Service invokes plugin command → SDK Runtime → Permission Check → Plugin Handler → Response
```

### 10.3 Lifecycle Notifications

The core notifies plugins of lifecycle changes through dedicated events:

| Event | Trigger | Plugin Action |
|-------|---------|---------------|
| `system.startup` | Platform startup | Initialize |
| `system.shutdown` | Platform shutdown | Cleanup |
| `plugin.error` | Plugin error detected | Handle/recover |
| `config.updated` | Configuration changed | React to changes |
| `security威胁.detected` | Security threat detected | Suspend operations |

---

## 11. Plugin-to-Plugin Communication

### 11.1 Through Event Bus Only

Plugins cannot communicate directly with each other. All inter-plugin communication goes through the event bus.

```
Plugin A publishes event → Event Bus → Plugin B receives event
```

### 11.2 Inter-Plugin Event Contract

```json
{
  "type": "plugin.event",
  "source": "plugin.{plugin_id_a}",
  "payload": {
    "target_plugin": "plugin.{plugin_id_b}",
    "action": "custom_action_name",
    "data": { }
  }
}
```

### 11.3 Communication Rules

| Rule | Description |
|------|-------------|
| No direct references | Plugins cannot hold references to each other |
| Event-based only | All communication via event bus |
| No shared state | Plugins cannot share storage |
| No callback chains | Plugins cannot create synchronous call chains |
| Timeout enforcement | All inter-plugin events have TTL |
| Audit logging | All inter-plugin events are logged |

---

## 12. Message Contracts

### 12.1 Plugin Manifest Contract

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PluginManifest",
  "type": "object",
  "required": ["id", "name", "version", "sdk_version_min", "permissions"],
  "properties": {
    "id": { "type": "string", "pattern": "^[a-z0-9-]+$" },
    "name": { "type": "string", "minLength": 1, "maxLength": 100 },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "author": { "type": "string" },
    "description": { "type": "string", "maxLength": 500 },
    "sdk_version_min": { "type": "string" },
    "sdk_version_max": { "type": "string" },
    "permissions": {
      "type": "object",
      "required": ["api"],
      "properties": {
        "api": { "type": "array", "items": { "type": "string" } },
        "events": {
          "type": "object",
          "properties": {
            "subscribe": { "type": "array", "items": { "type": "string" } },
            "publish": { "type": "array", "items": { "type": "string" } }
          }
        },
        "extension_points": { "type": "array", "items": { "type": "string" } },
        "commands": { "type": "array", "items": { "type": "string" } }
      }
    },
    "extension_points": { "type": "array", "items": { "type": "string" } },
    "event_subscriptions": { "type": "array", "items": { "type": "string" } },
    "lifecycle_hooks": { "type": "array", "items": { "type": "string" } }
  }
}
```

### 12.2 Plugin Error Response Contract

```json
{
  "title": "PluginErrorResponse",
  "type": "object",
  "required": ["code", "message", "plugin_id"],
  "properties": {
    "code": { "type": "string", "pattern": "^PLUGIN-[A-Z]+-\\d{3}$" },
    "message": { "type": "string" },
    "plugin_id": { "type": "string" },
    "recoverable": { "type": "boolean" },
    "details": { "type": "object" }
  }
}
```

### 12.3 Plugin-to-SDK Message Format

```python
@dataclass
class PluginMessage:
    plugin_id: str
    message_type: str       # "api_call", "event", "command"
    method: str             # SDK method or event type
    request_id: str         # For request/response correlation
    payload: dict
    timeout: float = 30.0
    metadata: dict = field(default_factory=dict)

@dataclass
class SDKResponse:
    request_id: str
    success: bool
    data: Any | None
    error: PluginErrorResponse | None
    duration_ms: float
```
