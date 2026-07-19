# AuthShield Lab — Plugin Sandbox & Isolation

> **Version:** 1.0.0
> **Status:** Authoritative
> **See also:** [Plugin Security](PLUGIN_SECURITY.md) · [Plugin SDK](PLUGIN_SDK.md)

---

## 1. Overview

Every AuthShield Lab plugin runs inside a **logical sandbox**. The sandbox is not a
container or VM — it is a set of Python-level restrictions that limit what a plugin can
access. The goals are:

1. **Fault isolation** — a misbehaving plugin cannot crash the kernel.
2. **Data isolation** — a plugin cannot read another plugin's data.
3. **Resource limits** — a plugin cannot consume unbounded CPU, memory, or storage.
4. **Permission enforcement** — a plugin can only use capabilities it declared.

---

## 2. Security Boundaries Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         KERNEL                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Core services, event bus, DI container, audit log     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              SANDBOX BOUNDARY                           │  │
│  │                                                         │  │
│  │  ┌───────────────────┐  ┌───────────────────┐          │  │
│  │  │    Plugin A        │  │    Plugin B        │         │  │
│  │  │  ┌──────────────┐ │  │  ┌──────────────┐ │         │  │
│  │  │  │ Namespace A   │ │  │  │ Namespace B   │ │        │  │
│  │  │  │ Config A      │ │  │  │ Config B      │ │        │  │
│  │  │  │ Storage A     │ │  │  │ Storage B     │ │        │  │
│  │  │  │ Logger A      │ │  │  │ Logger B      │ │        │  │
│  │  │  └──────────────┘ │  │  └──────────────┘ │         │  │
│  │  └───────────────────┘  └───────────────────┘          │  │
│  │                                                         │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │            Permission Enforcement Layer            │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           RESTRICTED PYTHON ENVIRONMENT                 │  │
│  │  Allowed: json, os.path (read-only), datetime,         │  │
│  │           re, collections, math, uuid, hashlib,        │  │
│  │           authshield_sdk.*                              │  │
│  │  Blocked: subprocess, socket, ctypes, importlib,       │  │
│  │           multiprocessing, threading (limited)          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Logical Isolation

### 3.1 Separate Namespace

Each plugin's Python code is imported into an isolated module namespace. Plugins cannot
import each other's modules directly. Cross-plugin communication is only possible through
the kernel's event bus and service registry.

```python
# Kernel creates an isolated namespace for each plugin
plugin_globals = {
    "__name__": f"authshield_plugin.{plugin_id}",
    "__file__": str(entry_point_path),
    "__builtins__": restricted_builtins,
}
exec(plugin_module_code, plugin_globals)
```

### 3.2 Import Restrictions

Plugins can only import modules from an **allowlist**:

| Category | Allowed Modules |
|---|---|
| **Standard Library (safe)** | `json`, `os` (limited), `datetime`, `re`, `collections`, `math`, `uuid`, `hashlib`, `typing`, `dataclasses`, `enum`, `abc`, `functools`, `itertools`, `copy`, `textwrap`, `string`, `struct`, `base64`, `secrets`, `hmac` |
| **AuthShield SDK** | `authshield_sdk.*` |
| **Nothing else** | All other imports are blocked at the sandbox level. |

The sandbox intercepts `__import__` and raises `SandboxViolation` for disallowed modules.

### 3.3 Restricted Builtins

The following Python builtins are **removed** from the plugin's namespace:

| Removed Builtin | Reason |
|---|---|
| `exec` | Arbitrary code execution. |
| `eval` | Arbitrary code execution. |
| `compile` | Compile arbitrary code objects. |
| `__import__` | Direct import manipulation. |
| `open` | Direct filesystem access (use Storage API). |
| `input` | Blocking stdin. |
| `exit`, `quit` | Process termination. |
| `globals` | Introspection of sandbox. |
| `locals` | Introspection of sandbox. |
| `vars` | Introspection of sandbox. |
| `dir` | Introspection (limited replacement provided). |
| `getattr`, `setattr`, `delattr` | Object manipulation (limited replacements provided). |

---

## 4. Resource Limits

The kernel enforces resource limits per plugin:

| Resource | Default Limit | Configurable |
|---|---|---|
| **CPU Time** | 30 seconds per operation | Yes, in `platform.json` |
| **Memory** | 256 MB RSS | Yes, in `platform.json` |
| **Storage** | 50 MB per plugin | Yes, in `platform.json` |
| **API Calls** | 1000 per minute | Yes, in `platform.json` |
| **Concurrent Tasks** | 10 async tasks | Yes, in `platform.json` |
| **Event Subscriptions** | 50 per plugin | No |
| **Registered Services** | 20 per plugin | No |
| **Registered Commands** | 30 per plugin | No |
| **Registered UI Panels** | 20 per plugin | No |

### 4.1 CPU Time Enforcement

The kernel wraps plugin operations in a timeout context manager:

```python
async def run_with_timeout(coro, timeout_seconds):
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise PluginTimeout(f"Operation exceeded {timeout_seconds}s")
```

### 4.2 Memory Enforcement

The kernel monitors plugin memory usage using `resource.getrusage()` on Linux and
`tracemalloc` for fine-grained tracking. If a plugin exceeds its memory limit:

1. The kernel logs a warning.
2. If the plugin exceeds by more than 20%, it is force-deactivated.

### 4.3 Storage Enforcement

The Storage API enforces per-plugin storage quotas. Each write operation checks:

```python
def _check_storage_quota(self, plugin_id: str, additional_bytes: int) -> None:
    current = self._get_storage_usage(plugin_id)
    limit = self._get_storage_limit(plugin_id)
    if current + additional_bytes > limit:
        raise StorageQuotaExceeded(
            f"Plugin {plugin_id}: {current + additional_bytes} bytes exceeds limit of {limit}"
        )
```

### 4.4 API Call Rate Limiting

The kernel tracks API calls per plugin using a sliding window counter:

```python
class RateLimiter:
    def check(self, plugin_id: str) -> bool:
        """Return True if the call is allowed, False if rate-limited."""
        ...
```

Rate-limited calls receive a `RateLimitedError` exception.

---

## 5. Configuration Isolation

Each plugin has its own configuration namespace:

```json
{
  "plugins": {
    "threat-dashboard": {
      "theme": "dark",
      "refresh_rate": 30,
      "max_threats_displayed": 100
    },
    "lab-simulator": {
      "difficulty": "intermediate",
      "timeout_minutes": 30
    }
  }
}
```

Plugins can only read and write within their own namespace. The Configuration API
automatically prefixes keys with `plugins.<plugin_id>.`.

---

## 6. Storage Isolation

Each plugin's persistent storage is in a separate directory:

```
~/.authshieldlab/data/plugins/
├── threat-dashboard/
│   ├── store.json
│   ├── cache/
│   └── exports/
├── lab-simulator/
│   ├── store.json
│   ├── sessions/
│   └── results/
```

Plugins cannot access another plugin's storage directory. The Storage API provides
namespaced read/write operations.

---

## 7. Permission Validation

### 7.1 Static Analysis

During the Validation lifecycle stage, the kernel performs static analysis on the plugin's
Python code to detect:

- Imports of restricted modules.
- Direct filesystem access (`open()`, `os.path` writes).
- Network access patterns.
- Dynamic code execution (`exec`, `eval`).

Static analysis warnings are logged but do not block plugin loading in `development` mode.
In `production` mode, violations cause the plugin to be rejected.

### 7.2 Runtime Checks

At runtime, the kernel wraps SDK API calls with permission checks:

```python
def check_permission(self, plugin_id: str, permission: str) -> bool:
    """Check if the plugin has the required permission."""
    manifest = self._get_manifest(plugin_id)
    declared_permissions = {p["permission"] for p in manifest.get("permissions", [])}
    return permission in declared_permissions
```

If a plugin attempts to use an API without the required permission, a
`PermissionDenied` exception is raised.

---

## 8. API Restrictions

The SDK uses an **allowlist approach**. Plugins can only call SDK methods that are listed
in the allowlist for their declared capabilities.

| Capability | Allowed SDK Methods |
|---|---|
| `ui:panel` | `register_panel`, `register_tab` |
| `ui:toolbar` | `register_toolbar` |
| `storage:rw` | `get_store`, `set_store`, `delete_store`, `list_store` |
| `storage:read` | `get_store`, `list_store` |
| `event:subscribe` | `subscribe_event`, `unsubscribe` |
| `event:publish` | `publish_event` |
| `commands:register` | `register_command`, `execute_command` |
| `logging:write` | `log_info`, `log_warning`, `log_error`, `log_debug` |
| `config:read` | `get_config`, `list_configs` |
| `config:write` | `get_config`, `set_config`, `list_configs` |
| `localization:register` | `translate`, `get_locale`, `set_locale` |
| `accessibility:register` | `register_component`, `announce`, `focus_management` |
| `report:register` | `register_report`, `generate_report` |

Methods not in the allowlist raise `CapabilityNotDeclared`.

---

## 9. Capability Enforcement

Capabilities declared in the manifest are the **only** capabilities a plugin can use. The
kernel validates this at:

1. **Load time** — static analysis checks that declared capabilities match actual API
   usage.
2. **Runtime** — each SDK call checks the capability.

If a plugin tries to call `publish_event` but did not declare `event:publish` in its
manifest, the call is rejected with `CapabilityNotDeclared`.

---

## 10. Fault Isolation

### 10.1 Plugin Crash Handling

If a plugin raises an unhandled exception:

1. The exception is caught by the kernel's error handler.
2. The plugin's `on_error()` hook is called (if defined).
3. The exception is logged with full traceback.
4. The plugin is marked as **faulted**.
5. The kernel continues operating normally.

```python
try:
    await plugin.on_activate(context)
except Exception as exc:
    await plugin.on_error(context, exc)
    self._mark_faulted(plugin_id, exc)
    self.audit.log("plugin.activation_failed", plugin_id=plugin_id, error=str(exc))
```

### 10.2 Kernel Stability

The kernel itself is never affected by plugin errors. Each plugin runs in an isolated
execution context, and all exceptions are caught before they propagate to the kernel's main
event loop.

### 10.3 Cross-Plugin Isolation

Plugin A's errors do not affect Plugin B. Each plugin has its own:

- Module namespace.
- Configuration namespace.
- Storage directory.
- Logger instance.
- Async task group (limited to 10 tasks).

---

## 11. Crash Recovery

### 11.1 Automatic Deactivation

When a plugin faults during execution:

1. The kernel publishes a `plugin.faulted` event.
2. If the plugin has background tasks, they are cancelled.
3. The plugin's `on_deactivate()` is called (best-effort).
4. The plugin's `on_unload()` is called (best-effort).
5. The plugin's storage is preserved (not deleted).
6. The plugin is marked as `faulted` in the registry.

### 11.2 Error Logging

All plugin errors are logged to both:

- `logs/platform.ndjson` — standard application log.
- `logs/audit.ndjson` — audit trail (tamper-evident).

### 11.3 User Notification

The platform displays a non-intrusive notification when a plugin faults:

```
⚠ Plugin "threat-dashboard" encountered an error and has been deactivated.
  View details | Retry | Remove
```

---

## 12. Safe Shutdown

During platform shutdown:

1. The kernel iterates plugins in reverse dependency order.
2. For each active plugin, `on_deactivate()` is called with a 10-second timeout.
3. If the plugin does not complete, it is forcefully terminated.
4. `on_unload()` is called with a 5-second timeout.
5. If the plugin still does not complete, the kernel proceeds.
6. All plugin async tasks are cancelled.
7. All plugin file handles are closed.
8. The plugin's storage directory is preserved for the next startup.

---

## 13. Restricted Python Builtins — Complete List

### 13.1 Allowed Builtins

```python
ALLOWED_BUILTINS = {
    "abs", "all", "any", "bool", "bytearray", "bytes",
    "callable", "chr", "classmethod", "complex", "dict",
    "divmod", "enumerate", "filter", "float", "format",
    "frozenset", "getattr", "hasattr", "hash", "hex",
    "id", "int", "isinstance", "issubclass", "iter",
    "len", "list", "map", "max", "memoryview", "min",
    "next", "object", "oct", "ord", "pow", "print",
    "property", "range", "repr", "reversed", "round",
    "set", "setattr", "slice", "sorted", "staticmethod",
    "str", "sum", "super", "tuple", "type", "zip",
    "__build_class__", "__name__", "__doc__",
}
```

### 13.2 Blocked Builtins

```python
BLOCKED_BUILTINS = {
    "exec", "eval", "compile", "__import__", "open",
    "input", "exit", "quit", "globals", "locals",
    "vars", "breakpoint", "credits", "license",
    "copyright", "help",
}
```

---

## 14. Restricted Modules — Complete List

### 14.1 Allowed Modules

```python
ALLOWED_MODULES = {
    # Standard library (safe subset)
    "json", "os", "os.path", "datetime", "time", "re",
    "collections", "math", "uuid", "hashlib", "hmac",
    "typing", "dataclasses", "enum", "abc", "functools",
    "itertools", "copy", "textwrap", "string", "struct",
    "base64", "secrets", "decimal", "fractions", "random",
    "io", "pathlib", "logging",
    # AuthShield SDK
    "authshield_sdk",
}
```

### 14.2 Blocked Modules

```python
BLOCKED_MODULES = {
    "subprocess", "socket", "ctypes", "importlib",
    "multiprocessing", "threading", "signal", "asyncio",
    "sys", "builtins", "code", "codeop", "compileall",
    "py_compile", "shutil", "tempfile", "glob", "fnmatch",
    "pickle", "shelve", "sqlite3", "dbm", "xmlrpc",
    "http", "urllib", "ftplib", "smtplib", "poplib",
    "imaplib", "telnetlib", "xml", "html", "csv",
    "configparser", "argparse", "getopt", "optparse",
    "platform", "warnings", "traceback", "linecache",
    "pdb", "profile", "cProfile", "timeit", "dis",
    "inspect", "ast", "tokenize", "token", "keyword",
    "operator", "array", "weakref", "types",
}
```

---

## 15. Sandbox Configuration

Sandbox settings are configurable in `platform.json`:

```json
{
  "plugins": {
    "sandbox": {
      "enabled": true,
      "cpu_timeout_seconds": 30,
      "memory_limit_mb": 256,
      "storage_limit_mb": 50,
      "api_rate_limit_per_minute": 1000,
      "max_async_tasks": 10,
      "allow_network": false,
      "allow_filesystem": false,
      "log_violations": true
    }
  }
}
```

---

## 16. References

- [Plugin Security](PLUGIN_SECURITY.md)
- [Plugin SDK](PLUGIN_SDK.md)
- [Plugin Lifecycle](PLUGIN_LIFECYCLE.md)

---

*End of document.*
