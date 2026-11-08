# AuthShield Lab — Microkernel Plugin Architecture

> **Version:** 1.0.0
> **Status:** Authoritative
> **Applies to:** AuthShield Lab Platform (Python 3.12+ / FastAPI Backend, Electron + React Frontend)

---

## 1. Overview

AuthShield Lab adopts a **microkernel architecture** for its plugin system. The kernel is a
minimal core responsible for lifecycle management, service registration, dependency injection,
and security enforcement. All domain logic — threat detection UI, lab exercises, assessment
engines, reporting dashboards — lives in plugins.

This separation guarantees that the platform itself can be extended without modifying core
code, satisfying the **open/closed principle** while keeping the attack surface minimal.

---

## 2. Design Principles

| Principle | How the kernel upholds it |
|---|---|
| **Open / Closed** | Core exposes extension points; plugins implement them without touching kernel source. |
| **Single Responsibility** | The kernel manages *lifecycle* only. Business logic belongs to plugins. |
| **Separation of Concerns** | Configuration, logging, security, accessibility, and localization are independent subsystems initialized in order. |
| **Least Privilege** | Plugins receive only the capabilities they declare in their manifest. The kernel enforces this at runtime. |
| **Defense in Depth** | Signature verification → sandbox isolation → runtime permission checks → audit logging. |
| **Offline-First** | Every subsystem works without network access. No external registries or package managers at runtime. |

---

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AuthShield Lab Platform                     │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                        MICROKERNEL                            │  │
│  │                                                               │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌────────────────────────┐ │  │
│  │  │  Bootstrap   │ │  DI Container │ │  Service Registry      │ │  │
│  │  └──────┬──────┘ └──────┬───────┘ └───────────┬────────────┘ │  │
│  │         │               │                      │              │  │
│  │  ┌──────▼──────┐ ┌──────▼───────┐ ┌───────────▼────────────┐ │  │
│  │  │  Module      │ │  Config      │ │  Event Bus              │ │  │
│  │  │  Discovery   │ │  Loader      │ │  (pub/sub)              │ │  │
│  │  └──────┬──────┘ └──────┬───────┘ └───────────┬────────────┘ │  │
│  │         │               │                      │              │  │
│  │  ┌──────▼──────────────▼──────────────────────▼────────────┐ │  │
│  │  │              Kernel Extension Points                     │ │  │
│  │  │  register_service()  register_hook()  emit_event()       │ │  │
│  │  └──────┬──────────────┬──────────────────────┬────────────┘ │  │
│  └─────────┼──────────────┼──────────────────────┼──────────────┘  │
│            │              │                      │                  │
│  ┌─────────▼──────────────▼──────────────────────▼──────────────┐  │
│  │                     PLUGIN RUNTIME                            │  │
│  │                                                               │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────┐ │  │
│  │  │ Feature     │ │ Educational│ │ Assessment │ │ Reporting │ │  │
│  │  │ Plugin      │ │ Content    │ │ Pack       │ │ Template  │ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └───────────┘ │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────┐ │  │
│  │  │ Localization│ │ Accessibility│ │ Theme    │ │ SDK Ext.  │ │  │
│  │  │ Pack        │ │ Profile     │ │           │ │           │ │  │
│  │  └────────────┘ └────────────┘ └────────────┘ └───────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    SECURITY BOUNDARY                          │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │  │
│  │  │  Signature    │ │  Sandbox     │ │  Audit Logger        │  │  │
│  │  │  Verifier     │ │  Enforcer    │ │  (immutable)         │  │  │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Core Kernel Responsibilities

### 4.1 Bootstrap

The bootstrap sequence is the first code that executes when the platform starts. It is
responsible for assembling the minimal runtime environment before any plugin is loaded.

**Sequence:**

1. Parse CLI arguments and environment variables.
2. Determine runtime mode (`development`, `testing`, `production`).
3. Locate the platform installation directory and plugin directories.
4. Initialise the logging subsystem so all subsequent steps produce audit trails.
5. Invoke the **Config Loader** to read `platform.json` and environment overrides.
6. Invoke **Module Discovery** to scan plugin directories and build the plugin manifest
   registry.
7. Invoke **Dependency Resolver** to topologically sort plugins.
8. Invoke the **DI Container** to register all kernel services.
9. Invoke **Security Init** to load trust anchors and signature policies.
10. Invoke **Accessibility Init** to load the default accessibility profile.
11. Invoke **Localization Init** to determine the active locale and load fallback chains.
12. Invoke **Event Bus Startup** to create the in-process publish/subscribe bus.
13. Invoke **Plugin Runtime Startup** to load and activate plugins in dependency order.
14. Signal readiness (bind FastAPI uvicorn workers, open Electron window).

### 4.2 Service Registration

The kernel maintains a **service registry** — a typed dictionary mapping service identifiers
to provider instances. Plugins may register new services or override existing ones (if the
manifest declares the appropriate capability).

```python
class ServiceRegistry:
    def register(self, service_id: str, provider: Any, *, override: bool = False) -> None: ...
    def resolve(self, service_id: str) -> Any: ...
    def has(self, service_id: str) -> bool: ...
    def list_services(self) -> list[str]: ...
```

**Rules:**

- A plugin may only register services it declared in `manifest.capabilities`.
- Overriding a kernel-internal service requires the `kernel:override` capability, which is
  restricted to first-party plugins signed by the platform publisher key.
- All registrations are logged to the audit trail.

### 4.3 Dependency Injection (DI) Container

The DI container wires services together. It supports three scopes:

| Scope | Lifetime |
|---|---|
| `singleton` | One instance for the entire platform lifetime. |
| `scoped` | One instance per request (FastAPI request scope). |
| `transient` | A new instance every time the service is resolved. |

```python
class DIContainer:
    def provide(self, service_id: str, factory: Callable, *, scope: str = "singleton") -> None: ...
    def resolve(self, service_id: str) -> Any: ...
    def resolve_scoped(self, service_id: str, scope_id: str) -> Any: ...
```

Plugins register their services through the DI container; the kernel resolves them at the
correct scope automatically.

### 4.4 Module Discovery

Module discovery scans one or more configured plugin directories, reads each plugin's
`manifest.json`, and builds an in-memory index.

**Discovery flow:**

1. Walk each directory in `plugin_paths` (configured in `platform.json`).
2. For each subdirectory, attempt to load `manifest.json`.
3. Parse and validate the manifest against the JSON Schema.
4. Collect the plugin into the discovery index keyed by `plugin_id`.
5. Log any malformed manifests as warnings (non-fatal).

Discovery is **eager** — all manifests are parsed at startup so that dependency resolution
can proceed. Actual plugin Python modules are loaded lazily (see §5).

### 4.5 Configuration Loading

Configuration is hierarchical:

```
platform.json          (platform-level, checked in)
  └─ plugin overrides  (per-plugin config/defaults)
       └─ user prefs   (~/.authshieldlab/preferences.json)
            └─ env vars (ASL_* prefix)
```

Each layer may override keys from the previous one. The kernel merges layers at startup
and exposes the merged result through the **Configuration API**.

Plugins receive a namespaced view of configuration under `plugins.<plugin_id>.*`.

### 4.6 Security Initialization

1. Load trust anchor certificates from `trust_anchors/`.
2. Load the platform signing policy (which keys are trusted).
3. For each discovered plugin, verify its digital signature against trust anchors.
4. Record verification results in the audit log.
5. Reject (disable) plugins that fail verification unless running in `development` mode
   with `--insecure-plugins` flag.

### 4.7 Accessibility Initialization

1. Load the default accessibility profile (`profiles/default.json`).
2. Enumerate installed accessibility profile plugins.
3. Merge user preferences.
4. Expose the resolved profile through the **Accessibility API**.

### 4.8 Localization Initialization

1. Determine the active locale from user preferences or system locale.
2. Load the fallback chain (e.g., `de-CH → de → en`).
3. Load built-in translation bundles.
4. Load translation bundles from installed localization plugins.
5. Expose the resolved catalog through the **Localization API**.

### 4.9 Logging Init

The logging subsystem is initialised before any other kernel component so that all
subsequent operations produce structured, timestamped logs.

- **Backend:** Python `structlog` writing NDJSON to `logs/platform.ndjson`.
- **Audit trail:** A separate, append-only, tamper-evident log at `logs/audit.ndjson`.
- **Plugin logs:** Each plugin gets a namespaced logger (`plugin.<plugin_id>`).

### 4.10 Event Bus Startup

The event bus is an in-process publish/subscribe system. It supports:

- **Synchronous events** — handlers run in the publishing thread.
- **Asynchronous events** — handlers are scheduled on the asyncio event loop.
- **Wildcard subscriptions** — `plugin.*` matches all events from any plugin.

```python
class EventBus:
    async def publish(self, topic: str, payload: dict) -> None: ...
    def subscribe(self, topic: str, handler: Callable) -> SubscriptionHandle: ...
    def unsubscribe(self, handle: SubscriptionHandle) -> None: ...
```

### 4.11 Plugin Runtime Startup

Once all kernel services are initialised, the plugin runtime starts plugins in
topologically sorted order (respecting dependency declarations).

For each plugin:

1. Load the Python module from `src/`.
2. Instantiate the plugin class (must subclass `PluginBase`).
3. Call `plugin.on_init(context)` — plugin allocates resources.
4. Call `plugin.on_activate(context)` — plugin registers services, hooks, and UI.
5. Mark the plugin as **active** in the registry.

If any plugin fails during activation, it is **deactivated** and marked as **faulted**; the
kernel continues loading remaining plugins.

### 4.12 Graceful Shutdown

On receiving `SIGTERM` or `SIGINT`:

1. Stop accepting new requests (FastAPI lifespan).
2. Publish a `platform.shutdown` event.
3. Iterate active plugins in **reverse** dependency order.
4. For each plugin, call `plugin.on_deactivate(context)` then `plugin.on_unload(context)`.
5. Release DI container resources.
6. Flush and close log files.
7. Exit with code 0.

If a plugin does not finish shutdown within 10 seconds, it is forcefully terminated and a
timeout error is logged.

---

## 5. Kernel Public APIs

| API | Module | Purpose |
|---|---|---|
| `Kernel.bootstrap()` | `kernel.bootstrap` | Entry point; runs the full startup sequence. |
| `Kernel.shutdown()` | `kernel.shutdown` | Triggers graceful shutdown. |
| `Kernel.services` | `kernel.services` | Access the `ServiceRegistry` instance. |
| `Kernel.container` | `kernel.container` | Access the `DIContainer` instance. |
| `Kernel.config` | `kernel.config` | Access the merged `ConfigurationAPI`. |
| `Kernel.events` | `kernel.events` | Access the `EventBus` instance. |
| `Kernel.plugins` | `kernel.plugins` | Access the `PluginRegistry`. |
| `Kernel.audit` | `kernel.audit` | Access the `AuditLogger`. |
| `Kernel.localize` | `kernel.localize` | Access the `LocalizationAPI`. |
| `Kernel.accessibility` | `kernel.accessibility` | Access the `AccessibilityAPI`. |
| `Kernel.context(plugin_id)` | `kernel.context` | Returns a sandboxed `PluginContext` for a plugin. |

---

## 6. Kernel Extension Points

Extension points are well-defined interfaces that plugins may implement to hook into kernel
behaviour. Unlike services, extension points are **invocation points** — the kernel calls
into the plugin.

| Extension Point | Interface | When Invoked |
|---|---|---|
| `lifecycle_hook` | `LifecycleHook` | At each lifecycle stage transition. |
| `config_validator` | `ConfigValidator` | Before configuration is committed. |
| `report_generator` | `ReportGenerator` | When a user requests a report. |
| `ui_panel` | `UIPanel` | When the frontend requests panel definitions. |
| `command_handler` | `CommandHandler` | When a registered command is executed. |
| `query_handler` | `QueryHandler` | When a registered query is executed. |
| `health_provider` | `HealthProvider` | During periodic health checks. |
| `migration_handler` | `MigrationHandler` | During plugin upgrade. |

---

## 7. Kernel Lifecycle

```
┌──────────────┐
│  INIT        │  Platform process starts.
└──────┬───────┘
       │
┌──────▼───────┐
│  BOOTSTRAP   │  Parse args, determine mode, load platform.json.
└──────┬───────┘
       │
┌──────▼───────┐
│  DISCOVER    │  Scan plugin dirs, parse manifests, build index.
└──────┬───────┘
       │
┌──────▼───────┐
│  RESOLVE     │  Topologically sort plugins, detect conflicts.
└──────┬───────┘
       │
┌──────▼───────┐
│  VERIFY      │  Check signatures, integrity checksums.
└──────┬───────┘
       │
┌──────▼───────┐
│  INIT_SERVICES │ Register kernel services in DI container.
└──────┬───────┘
       │
┌──────▼───────┐
│  INIT_SUBSYSTEMS │ Config, logging, security, a11y, i18n, event bus.
└──────┬───────┘
       │
┌──────▼───────┐
│  LOAD_PLUGINS │ Import plugin modules in dependency order.
└──────┬───────┘
       │
┌──────▼───────┐
│  ACTIVATE_PLUGINS │ Call on_init + on_activate for each plugin.
└──────┬───────┘
       │
┌──────▼───────┐
│  READY       │  Platform is fully operational.
└──────┬───────┘
       │
┌──────▼───────┐
│  RUNNING     │  Normal operation; plugins active.
└──────┬───────┘
       │  (SIGTERM / SIGINT)
┌──────▼───────┐
│  SHUTDOWN    │  Deactivate plugins in reverse order.
└──────┬───────┘
       │
┌──────▼───────┐
│  TERMINATED  │  Process exits.
└──────────────┘
```

---

## 8. Concurrency Model

- The **kernel main thread** runs the FastAPI event loop (uvicorn).
- Plugins may spawn background tasks via `asyncio.create_task()`, but the kernel limits
  concurrent plugin tasks to 64 per plugin.
- The event bus is single-threaded; handlers must be non-blocking or offload work to a
  thread pool.
- The DI container is not thread-safe; all resolutions happen on the asyncio event loop.

---

## 9. Error Handling Strategy

| Level | Strategy |
|---|---|
| **Kernel panic** | Unrecoverable error in the kernel itself → log, dump state, exit with code 1. |
| **Plugin fault** | Plugin throws during lifecycle → deactivate the plugin, log, continue. |
| **Service failure** | A service call raises → catch, log, return a `ServiceError` to the caller. |
| **Event handler failure** | A subscriber throws → log, remove the faulty handler, continue dispatch. |
| **Timeout** | Any lifecycle stage exceeding its timeout → force-terminate, fault the plugin. |

---

## 10. Observability

### 10.1 Structured Logging

Every log entry is a JSON object:

```json
{
  "ts": "2026-07-19T12:00:00Z",
  "level": "info",
  "component": "kernel.plugin_runtime",
  "plugin_id": "threat-dashboard",
  "message": "Plugin activated",
  "duration_ms": 42
}
```

### 10.2 Metrics

The kernel exposes Prometheus-compatible metrics at `/internal/metrics`:

- `authshield_plugin_load_duration_seconds` (histogram)
- `authshield_plugin_active` (gauge, per plugin)
- `authshield_event_bus_queue_depth` (gauge)
- `authshield_kernel_uptime_seconds` (gauge)

### 10.3 Audit Trail

Every security-relevant operation (plugin load, permission grant, config change) is written
to the append-only audit log with a chained hash for tamper evidence.

---

## 11. Versioning Policy

| Component | Policy |
|---|---|
| Kernel public API | Semantic Versioning. Breaking changes require a major bump. |
| Extension point interfaces | Each interface has its own version (`@1`, `@2`). Plugins declare which version they target. |
| Plugin manifest schema | SemVer. New optional fields are minor bumps; removing fields is a major bump. |

---

## 12. Compatibility Matrix

| Platform Version | Plugin API Level | Notes |
|---|---|---|
| 1.x | `@1` | Initial release. |
| 2.x | `@1`, `@2` | Adds async lifecycle hooks. |
| 3.x | `@1`, `@2`, `@3` | Adds scoped DI. |

Plugins targeting an older API level run under the compatibility shim provided by the
kernel. Shims are removed after two major versions.

---

## 13. Filesystem Layout

```
~/.authshieldlab/
├── platform.json
├── plugins/
│   ├── built-in/
│   │   ├── threat-dashboard/
│   │   │   ├── manifest.json
│   │   │   ├── src/
│   │   │   └── resources/
│   │   └── lab-simulator/
│   └── installed/
│       └── third-party-plugin/
├── trust_anchors/
├── logs/
│   ├── platform.ndjson
│   └── audit.ndjson
├── data/
│   └── plugins/
│       └── <plugin_id>/   (per-plugin isolated storage)
└── cache/
    └── plugins/
        └── <plugin_id>/
```

---

## 14. References

- [Plugin Framework](PLUGIN_FRAMEWORK.md)
- [Plugin Lifecycle](PLUGIN_LIFECYCLE.md)
- [Plugin SDK](PLUGIN_SDK.md)
- [Plugin Sandbox](PLUGIN_SANDBOX.md)
- [Plugin Security](PLUGIN_SECURITY.md)

---

*End of document.*
