# AuthShield Lab — Plugin Lifecycle

> **Version:** 1.0.0
> **Status:** Authoritative
> **See also:** [Plugin Architecture](PLUGIN_ARCHITECTURE.md) · [Plugin Framework](PLUGIN_FRAMEWORK.md)

---

## 1. Overview

Every AuthShield Lab plugin passes through a well-defined lifecycle. The lifecycle is
managed by the kernel and consists of **16 stages**. Each stage has explicit preconditions,
postconditions, error handling rules, timeout limits, and audit events.

---

## 2. State Machine Diagram

```
                    ┌──────────────┐
                    │  DISCOVERY   │
                    └──────┬───────┘
                           │ manifest parsed
                    ┌──────▼───────┐
                    │  VALIDATION  │
                    └──────┬───────┘
                           │ schema valid
                    ┌──────▼───────────┐
                    │ SIG VERIFICATION │
                    └──────┬───────────┘
                           │ signature valid
                    ┌──────▼───────────┐
                    │ COMPAT CHECK     │
                    └──────┬───────────┘
                           │ compatible
                    ┌──────▼───────────┐
                    │ DEP RESOLUTION   │
                    └──────┬───────────┘
                           │ deps resolved
                    ┌──────▼───────┐
                    │   LOADING    │
                    └──────┬───────┘
                           │ module imported
                    ┌──────▼───────────┐
                    │ INITIALIZATION   │
                    └──────┬───────────┘
                           │ on_init ok
                    ┌──────▼───────────┐
                    │   ACTIVATION     │
                    └──────┬───────────┘
                           │ on_activate ok
                    ┌──────▼───────┐
                    │  EXECUTION   │◄─────┐
                    └──────┬───────┘      │
                           │              │ resume
                    ┌──────▼───────┐      │
                    │ SUSPENSION   │      │
                    └──────┬───────┘      │
                           │              │
                    ┌──────▼───────┐      │
                    │ SUSPENDED    │──────┘
                    └──────┬───────┘
                           │ deactivate
                    ┌──────▼─────────┐
                    │ DEACTIVATION   │
                    └──────┬─────────┘
                           │ on_deactivate ok
                    ┌──────▼───────┐
                    │  UNLOADING    │
                    └──────┬───────┘
                           │ on_unload ok
                    ┌──────▼───────┐
                    │   REMOVAL    │
                    └──────┬───────┘
                           │ resources freed
                    ┌──────▼───────┐
                    │  TERMINATED  │
                    └──────────────┘

    ┌───────────┐          ┌───────────┐
    │  UPGRADE  │──────────│ ROLLBACK  │
    └───────────┘          └───────────┘
    (re-enters               (re-enters
     LOADING)                LOADING)

    Any stage ──error──► FAULTED
```

---

## 3. Stage Definitions

### Stage 1: Discovery

| Attribute | Value |
|---|---|
| **Preconditions** | Plugin directory exists and contains `manifest.json`. |
| **Postconditions** | Manifest is parsed into a `PluginManifest` object and added to the plugin index. |
| **Error Handling** | Missing or unreadable `manifest.json` → skip directory, log warning. |
| **Audit Event** | `plugin.discovered` with `plugin_id`, `path`, `manifest_hash`. |
| **Timeout** | 5 seconds per plugin directory. |

---

### Stage 2: Validation

| Attribute | Value |
|---|---|
| **Preconditions** | Manifest is parsed (from Discovery). |
| **Postconditions** | Manifest conforms to the JSON schema. All required fields present. Version strings are valid SemVer. |
| **Error Handling** | Schema violation → mark plugin as `invalid`, log error with specific field violations. |
| **Audit Event** | `plugin.validated` or `plugin.validation_failed`. |
| **Timeout** | 2 seconds. |

---

### Stage 3: Signature Verification

| Attribute | Value |
|---|---|
| **Preconditions** | Manifest is valid (from Validation). |
| **Postconditions** | Digital signature verified against trust anchors. Integrity checksums match. |
| **Error Handling** | Invalid signature → mark plugin as `untrusted`, log security warning. In `production` mode, disable the plugin. In `development` mode, allow with warning. |
| **Audit Event** | `plugin.signature_verified` or `plugin.signature_invalid`. |
| **Timeout** | 10 seconds (signature verification may involve crypto operations). |

---

### Stage 4: Compatibility Check

| Attribute | Value |
|---|---|
| **Preconditions** | Signature is verified (from Sig Verification). |
| **Postconditions** | Platform version is within `[min_platform_version, max_platform_version]`. OS and architecture are supported. |
| **Error Handling** | Incompatible → mark plugin as `incompatible`, log error with specific version mismatch. |
| **Audit Event** | `plugin.compatible` or `plugin.incompatible`. |
| **Timeout** | 1 second. |

---

### Stage 5: Dependency Resolution

| Attribute | Value |
|---|---|
| **Preconditions** | Plugin is compatible (from Compatibility Check). All dependency manifests are discovered. |
| **Postconditions** | Dependency graph is resolved. No circular dependencies. All required dependencies are present and compatible. |
| **Error Handling** | Missing dependency → mark plugin as `unresolvable`. Version conflict → mark as `conflict`. Circular dependency → mark as `cyclic`. |
| **Audit Event** | `plugin.deps_resolved` or `plugin.deps_failed`. |
| **Timeout** | 5 seconds (for graph analysis). |

---

### Stage 6: Loading

| Attribute | Value |
|---|---|
| **Preconditions** | Dependencies are resolved. Plugin package is intact on disk. |
| **Postconditions** | Python module is imported into a sandboxed namespace. Entry point class is located. |
| **Error Handling** | Import error → mark plugin as `faulted`, log traceback. Missing entry point → same. |
| **Audit Event** | `plugin.loaded` or `plugin.load_failed`. |
| **Timeout** | 15 seconds (includes disk I/O and import). |

---

### Stage 7: Initialization

| Attribute | Value |
|---|---|
| **Preconditions** | Module is loaded. Entry point class is instantiated. |
| **Postconditions** | `plugin.on_init(context)` has returned without error. Plugin has acquired any non-reversible resources (file handles, temp files). |
| **Error Handling** | Exception in `on_init` → mark plugin as `faulted`, skip to Unloading. Log error with traceback. |
| **Audit Event** | `plugin.initialized` or `plugin.init_failed`. |
| **Timeout** | 10 seconds. |

---

### Stage 8: Activation

| Attribute | Value |
|---|---|
| **Preconditions** | Plugin is initialized. |
| **Postconditions** | `plugin.on_activate(context)` has returned without error. Plugin has registered its services, hooks, UI, and commands. |
| **Error Handling** | Exception in `on_activate` → deactivate the plugin (call `on_deactivate` if possible), mark as `faulted`, skip to Unloading. |
| **Audit Event** | `plugin.activated` or `plugin.activation_failed`. |
| **Timeout** | 15 seconds. |

---

### Stage 9: Execution

| Attribute | Value |
|---|---|
| **Preconditions** | Plugin is activated. |
| **Postconditions** | Plugin is actively handling requests, events, and user interactions. |
| **Error Handling** | Runtime exceptions are caught per-operation. The plugin remains active unless a fatal error occurs (see Faulted state). |
| **Audit Event** | No audit event for normal execution (too high volume). Errors are logged individually. |
| **Timeout** | N/A (ongoing). |

---

### Stage 10: Suspension

| Attribute | Value |
|---|---|
| **Preconditions** | Plugin is in Execution state. |
| **Postconditions** | `plugin.on_suspend(context)` has been called. Plugin has paused background tasks and released transient resources. |
| **Error Handling** | Exception in `on_suspend` → force-suspend (ignore error), log warning. |
| **Audit Event** | `plugin.suspended`. |
| **Timeout** | 5 seconds. |

---

### Stage 11: Suspended

| Attribute | Value |
|---|---|
| **Preconditions** | Plugin is suspended. |
| **Postconditions** | Plugin is inactive but retains its loaded state. Can be resumed or deactivated. |
| **Error Handling** | No errors possible (passive state). |
| **Audit Event** | None. |
| **Timeout** | N/A. |

---

### Stage 12: Deactivation

| Attribute | Value |
|---|---|
| **Preconditions** | Plugin is active or suspended. |
| **Postconditions** | `plugin.on_deactivate(context)` has returned without error. Plugin has unregistered its services, hooks, and UI. |
| **Error Handling** | Exception in `on_deactivate` → force-deactivate, log error, continue to Unloading. |
| **Audit Event** | `plugin.deactivated` or `plugin.deactivation_forced`. |
| **Timeout** | 10 seconds. |

---

### Stage 13: Unloading

| Attribute | Value |
|---|---|
| **Preconditions** | Plugin is deactivated. |
| **Postconditions** | `plugin.on_unload(context)` has returned. Plugin module is removed from the sandbox namespace. |
| **Error Handling** | Exception in `on_unload` → force-unload, log error, continue to Removal. |
| **Audit Event** | `plugin.unloaded` or `plugin.unload_forced`. |
| **Timeout** | 5 seconds. |

---

### Stage 14: Removal

| Attribute | Value |
|---|---|
| **Preconditions** | Plugin is unloaded. |
| **Postconditions** | All plugin resources (memory, file handles, temp files) are released. Plugin is removed from the registry. |
| **Error Handling** | Resource leak detected → log warning, schedule garbage collection. |
| **Audit Event** | `plugin.removed`. |
| **Timeout** | 5 seconds. |

---

### Stage 15: Upgrade

| Attribute | Value |
|---|---|
| **Preconditions** | Plugin is installed. A new version is available on disk. |
| **Postconditions** | Old plugin is deactivated and unloaded. New plugin is loaded and activated. Migration handler (if any) has been executed. |
| **Error Handling** | Migration failure → rollback to old version. New version fails → rollback. See Rollback stage. |
| **Audit Event** | `plugin.upgrade_started`, `plugin.upgrade_completed`, or `plugin.upgrade_failed`. |
| **Timeout** | 30 seconds (includes migration). |

---

### Stage 16: Rollback

| Attribute | Value |
|---|---|
| **Preconditions** | An upgrade has failed, or the user has requested a rollback. |
| **Postconditions** | Previous version is restored and activated. |
| **Error Handling** | Rollback failure → mark plugin as `faulted`, require manual intervention. |
| **Audit Event** | `plugin.rollback_completed` or `plugin.rollback_failed`. |
| **Timeout** | 30 seconds. |

---

## 4. Faulted State

A plugin enters the **faulted** state when an unrecoverable error occurs at any operational
stage (Loading through Execution).

**Faulted state behaviour:**

- The plugin is deactivated if it was active.
- The plugin is unloaded if it was loaded.
- The plugin remains in the registry with status `faulted`.
- The user is notified through the UI.
- The plugin can be retried (re-enter Loading) or removed.
- A faulted plugin does not consume runtime resources.

---

## 5. Lifecycle Hooks for Plugin Developers

Plugins may override these methods on their `PluginBase` subclass:

```python
class PluginBase:
    async def on_init(self, ctx: PluginContext) -> None:
        """Called during Initialization stage. Allocate non-reversible resources."""

    async def on_activate(self, ctx: PluginContext) -> None:
        """Called during Activation stage. Register services, hooks, UI."""

    async def on_suspend(self, ctx: PluginContext) -> None:
        """Called during Suspension stage. Pause background tasks."""

    async def on_resume(self, ctx: PluginContext) -> None:
        """Called when resuming from Suspended. Resume background tasks."""

    async def on_deactivate(self, ctx: PluginContext) -> None:
        """Called during Deactivation stage. Unregister everything."""

    async def on_unload(self, ctx: PluginContext) -> None:
        """Called during Unloading stage. Release all resources."""

    async def on_upgrade(self, ctx: PluginContext, old_version: str) -> None:
        """Called during Upgrade stage. Migrate data if needed."""

    async def on_error(self, ctx: PluginContext, error: Exception) -> None:
        """Called when an error occurs. May attempt recovery."""
```

---

## 6. Error Recovery per Stage

| Stage | Recovery Strategy |
|---|---|
| Discovery | Skip the directory; continue with next. |
| Validation | Skip the plugin; log schema errors. |
| Signature Verification | Disable in production; warn in development. |
| Compatibility Check | Skip the plugin; log version mismatch. |
| Dependency Resolution | Skip the plugin; suggest installing missing deps. |
| Loading | Mark as faulted; allow retry. |
| Initialization | Mark as faulted; call `on_error` if available. |
| Activation | Deactivate; mark as faulted; allow retry. |
| Execution | Catch per-operation; log; continue. Fatal errors → faulted. |
| Suspension | Force-suspend; log. |
| Deactivation | Force-deactivate; log. |
| Unloading | Force-unload; log. |
| Removal | Log resource leak; schedule GC. |
| Upgrade | Rollback to previous version. |
| Rollback | Mark as faulted; require manual intervention. |

---

## 7. Timeout Handling per Stage

| Stage | Timeout | On Timeout |
|---|---|---|
| Discovery | 5s per directory | Skip directory. |
| Validation | 2s | Mark invalid. |
| Signature Verification | 10s | Mark untrusted. |
| Compatibility Check | 1s | Mark incompatible. |
| Dependency Resolution | 5s | Mark unresolvable. |
| Loading | 15s | Mark faulted. |
| Initialization | 10s | Mark faulted. |
| Activation | 15s | Deactivate, mark faulted. |
| Suspension | 5s | Force-suspend. |
| Deactivation | 10s | Force-deactivate. |
| Unloading | 5s | Force-unload. |
| Removal | 5s | Log, continue. |
| Upgrade | 30s | Rollback. |
| Rollback | 30s | Mark faulted. |

All timeouts are configurable in `platform.json` under `plugins.timeouts`.

---

## 8. Concurrency and Ordering

- Plugins are loaded sequentially in dependency order.
- Plugins in the same dependency "layer" (no inter-dependencies) may be loaded in parallel
  using `asyncio.gather()` to improve startup time.
- Lifecycle hooks are always called on the asyncio event loop (never in threads).
- Suspension and resumption can be triggered by the kernel (e.g. low memory) or by the
  user.

---

## 9. Audit Event Schema

Every lifecycle audit event follows this structure:

```json
{
  "event_id": "uuid-v4",
  "timestamp": "2026-07-19T12:00:00Z",
  "event_type": "plugin.activated",
  "plugin_id": "threat-dashboard",
  "plugin_version": "1.2.0",
  "platform_version": "3.0.0",
  "user_id": null,
  "details": {
    "duration_ms": 42,
    "services_registered": ["threat-service", "alert-service"]
  },
  "previous_hash": "sha256:abc123...",
  "hash": "sha256:def456..."
}
```

The `previous_hash` and `hash` fields create a tamper-evident chain.

---

## 10. References

- [Plugin Architecture](PLUGIN_ARCHITECTURE.md)
- [Plugin Framework](PLUGIN_FRAMEWORK.md)
- [Plugin Sandbox](PLUGIN_SANDBOX.md)
- [Plugin Security](PLUGIN_SECURITY.md)

---

*End of document.*
