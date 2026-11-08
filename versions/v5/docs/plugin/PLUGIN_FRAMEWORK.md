# AuthShield Lab — Plugin Framework Design

> **Version:** 1.0.0
> **Status:** Authoritative
> **See also:** [Plugin Architecture](PLUGIN_ARCHITECTURE.md) · [Plugin Lifecycle](PLUGIN_LIFECYCLE.md)

---

## 1. Overview

The Plugin Framework defines the **types** of plugins the platform supports, how they are
discovered, loaded, and registered. Every plugin type follows the same lifecycle but offers
different capabilities and carries different permission requirements.

All plugins in AuthShield Lab are **defensive and educational**. The platform never ships
offensive tooling.

---

## 2. Plugin Type Catalogue

### 2.1 Feature Plugin

| Attribute | Value |
|---|---|
| **Purpose** | Adds a new interactive feature to the platform (e.g. a new lab scenario, a threat-map widget). |
| **Lifecycle** | Full lifecycle: init → activate → execute → deactivate → unload. |
| **Capabilities** | UI panels, commands, queries, event subscriptions, storage. |
| **Permission Requirements** | Varies by feature; declared in manifest. Typical: `ui:panel`, `storage:rw`, `event:subscribe`. |
| **Dependencies** | May depend on other feature plugins or SDK extensions. |
| **Version Constraints** | `min_platform_version` required; `max_platform_version` optional. |

**Example:** `threat-dashboard` — a real-time threat visualization panel.

---

### 2.2 Educational Content Plugin

| Attribute | Value |
|---|---|
| **Purpose** | Provides structured learning content: lessons, tutorials, walkthroughs. |
| **Lifecycle** | Loaded eagerly (content must be available immediately). |
| **Capabilities** | `content:register`, `ui:panel`, `event:subscribe`. |
| **Permission Requirements** | `content:register`, `ui:panel`. No storage or command permissions by default. |
| **Dependencies** | Typically standalone; may depend on a `course-package` for context. |
| **Version Constraints** | Must declare `min_platform_version`. Content schema version must match platform content API. |

**Example:** `intro-to-sql-injection` — a guided lesson on SQL injection detection.

---

### 2.3 Course Package

| Attribute | Value |
|---|---|
| **Purpose** | Bundles multiple educational content plugins into a structured curriculum with prerequisites, assessments, and progress tracking. |
| **Lifecycle** | Eagerly loaded; metadata parsed at discovery. |
| **Capabilities** | `course:register`, `progress:track`, `assessment:grade`. |
| **Permission Requirements** | `course:register`, `progress:read`, `progress:write`. |
| **Dependencies** | Lists the content plugins it includes as required dependencies. |
| **Version Constraints** | Must be compatible with the course framework API version. |

**Example:** `defensive-network-fundamentals` — a 12-week course package.

---

### 2.4 Assessment Pack

| Attribute | Value |
|---|---|
| **Purpose** | Contains quizzes, lab challenges, and grading rubrics. |
| **Lifecycle** | Loaded on demand when an assessment is started. |
| **Capabilities** | `assessment:register`, `assessment:grade`, `event:publish`. |
| **Permission Requirements** | `assessment:grade`, `event:publish`. Read-only storage for results. |
| **Dependencies** | May depend on content plugins for context material. |
| **Version Constraints** | Assessment API version must be compatible. |

**Example:** `advanced-incident-response-quiz` — a 50-question assessment pack.

---

### 2.5 Localization Pack

| Attribute | Value |
|---|---|
| **Purpose** | Provides translations for a specific locale (e.g. `de-DE`, `ja-JP`). |
| **Lifecycle** | Loaded during localization init (before feature plugins). |
| **Capabilities** | `localization:register`. No other capabilities. |
| **Permission Requirements** | `localization:register` only. |
| **Dependencies** | Must not depend on feature plugins (would create circular dependency). |
| **Version Constraints** | Localization API version compatibility required. |

**Example:** `locale-fr-FR` — French translations.

---

### 2.6 Accessibility Profile

| Attribute | Value |
|---|---|
| **Purpose** | Defines accessibility overrides: contrast settings, font scaling rules, keyboard mappings, screen-reader templates. |
| **Lifecycle** | Loaded during accessibility init (before feature plugins). |
| **Capabilities** | `accessibility:register`. No other capabilities. |
| **Permission Requirements** | `accessibility:register` only. |
| **Dependencies** | Must not depend on feature plugins. |
| **Version Constraints** | Accessibility API version compatibility required. |

**Example:** `high-contrast-profile` — a high-contrast accessibility profile.

---

### 2.7 Reporting Template

| Attribute | Value |
|---|---|
| **Purpose** | Defines report layouts, data bindings, and export formats (PDF, CSV, HTML). |
| **Lifecycle** | Loaded on demand when a report is generated. |
| **Capabilities** | `report:register`, `storage:read`. |
| **Permission Requirements** | `report:register`, `storage:read`. No write access. |
| **Dependencies** | May depend on data-source plugins. |
| **Version Constraints** | Reporting API version must be compatible. |

**Example:** `compliance-report-pdf` — a PCI DSS compliance report template.

---

### 2.8 Theme

| Attribute | Value |
|---|---|
| **Purpose** | Provides CSS variables, color palettes, icon sets, and layout overrides for the Electron frontend. |
| **Lifecycle** | Loaded at frontend startup (before any UI renders). |
| **Capabilities** | `theme:register`. Strictly UI; no backend capabilities. |
| **Permission Requirements** | `theme:register` only. |
| **Dependencies** | Must not depend on backend plugins. |
| **Version Constraints** | Theme API version (CSS variable contract) must be compatible. |

**Example:** `dark-mode-pro` — an enhanced dark mode theme.

---

### 2.9 SDK Extension

| Attribute | Value |
|---|---|
| **Purpose** | Extends the plugin SDK itself — adds new APIs, new extension points, new service interfaces. |
| **Lifecycle** | Loaded **before** all other plugin types (infrastructure priority). |
| **Capabilities** | `sdk:extend`, `kernel:register_extension_point`. |
| **Permission Requirements** | Requires `kernel:override` capability (restricted to platform-signed plugins). |
| **Dependencies** | Must not depend on any other plugin type. |
| **Version Constraints** | Must target the exact major version of the kernel API. |

**Example:** `advanced-diagnostics-sdk` — adds network-trace diagnostic APIs.

---

### 2.10 Institution Configuration Package

| Attribute | Value |
|---|---|
| **Purpose** | Pre-configures the platform for a specific institution: branding, LDAP settings, course enrollments, policy defaults. |
| **Lifecycle** | Applied during bootstrap (before any plugin loads). |
| **Capabilities** | `config:write` (scoped to institution namespace). |
| **Permission Requirements** | `config:write` for institution config. No other capabilities. |
| **Dependencies** | May reference other plugins to auto-enable. |
| **Version Constraints** | Platform config schema version must be compatible. |

**Example:** `university-of-oxford-config` — Oxford-specific platform configuration.

---

### 2.11 Example / Reference Implementation

| Attribute | Value |
|---|---|
| **Purpose** | Demonstrates how to build a plugin of a specific type. Ships with source code and annotations. Intended for developer education. |
| **Lifecycle** | May be loaded in `development` mode only. |
| **Capabilities** | Typically minimal; mirrors the type it demonstrates. |
| **Permission Requirements** | Minimal permissions; read-only where possible. |
| **Dependencies** | Documented but not enforced (for learning purposes). |
| **Version Constraints** | Must work with the current platform version. |

**Example:** `example-feature-plugin` — a fully commented feature plugin with unit tests.

---

## 3. Plugin Discovery Mechanism

### 3.1 Directory Scanning

At startup, the kernel scans the following directories in order:

1. `<platform_root>/plugins/built-in/` — platform-bundled plugins.
2. `<platform_root>/plugins/extensions/` — platform-signed SDK extensions.
3. `~/.authshieldlab/plugins/installed/` — user-installed plugins.
4. Paths listed in `platform.json → plugin_paths` — custom directories.

Scanning is **recursive to depth 1** — each immediate subdirectory is treated as a plugin
package root. If a subdirectory contains `manifest.json`, it is a plugin.

### 3.2 Manifest Parsing

For each discovered plugin directory:

1. Read `manifest.json`.
2. Validate against the [Manifest JSON Schema](PLUGIN_MANIFEST_SPECIFICATION.md).
3. If validation fails, log a warning and skip the plugin.
4. Extract `plugin_id`, `version`, `type`, `dependencies`, and `capabilities`.
5. Add to the in-memory plugin index.

### 3.3 Plugin Index

The plugin index is a dictionary:

```python
plugin_index: dict[str, PluginEntry] = {
    "threat-dashboard": PluginEntry(
        plugin_id="threat-dashboard",
        version="1.2.0",
        type="feature",
        path=Path("/home/anya/.authshieldlab/plugins/installed/threat-dashboard"),
        manifest=<parsed manifest>,
        status="discovered",
    ),
    ...
}
```

---

## 4. Plugin Loading Strategy

### 4.1 Lazy Loading (Default)

Most plugin Python modules are **not imported** at discovery time. The kernel only parses
manifests. Actual Python code is loaded when:

- The plugin is first activated during startup, **or**
- A request or event triggers the plugin for the first time.

This keeps startup fast and reduces memory usage.

### 4.2 Eager Loading

The following plugin types are loaded eagerly (their Python code is imported at startup):

| Type | Reason |
|---|---|
| Localization Pack | Translations must be available before content plugins render. |
| Accessibility Profile | A11y settings must be applied before UI renders. |
| SDK Extension | New APIs must be available before dependent plugins activate. |
| Institution Config | Must be applied before other plugins read configuration. |
| Course Package | Metadata must be indexed before content plugins reference it. |

### 4.3 Loading Process

```
1. Read plugin package from disk (manifest.json + src/).
2. Create a sandboxed module namespace (see PLUGIN_SANDBOX.md).
3. Import the plugin's Python module into the sandbox.
4. Locate the plugin entry point class (declared in manifest → entry_point).
5. Instantiate the class, passing a PluginContext.
6. Call plugin.on_init(context).
7. Call plugin.on_activate(context).
8. Mark plugin as "active" in the registry.
```

If step 2–7 raises an exception, the plugin is marked as "faulted" and the error is logged.
The kernel continues loading remaining plugins.

---

## 5. Plugin Registration Process

### 5.1 Service Registration

During `on_activate()`, a plugin may register services:

```python
class MyPlugin(PluginBase):
    async def on_activate(self, ctx: PluginContext) -> None:
        ctx.services.register("my-service", MyServiceProvider())
```

The kernel validates that the plugin has the required capability before allowing the
registration.

### 5.2 Hook Registration

Plugins may register lifecycle hooks:

```python
class MyPlugin(PluginBase):
    async def on_activate(self, ctx: PluginContext) -> None:
        ctx.hooks.register("pre_report_generation", self.on_pre_report)
```

### 5.3 Event Subscription

Plugins subscribe to events:

```python
class MyPlugin(PluginBase):
    async def on_activate(self, ctx: PluginContext) -> None:
        ctx.events.subscribe("lab.completed", self.on_lab_completed)
```

### 5.4 UI Registration

Frontend plugins register panels, tabs, and toolbar items:

```python
class MyPlugin(PluginBase):
    async def on_activate(self, ctx: PluginContext) -> None:
        ctx.ui.register_panel(
            id="my-panel",
            title="My Panel",
            icon="shield",
            component="MyPanel",
        )
```

### 5.5 Command Registration

Plugins may register CLI and API commands:

```python
class MyPlugin(PluginBase):
    async def on_activate(self, ctx: PluginContext) -> None:
        ctx.commands.register(
            name="my-plugin:scan",
            handler=self.handle_scan,
            description="Run a defensive scan",
        )
```

---

## 6. Conflict Resolution

### 6.1 Version Conflicts

If two plugins require different versions of the same dependency:

1. The kernel attempts to resolve using SemVer compatibility rules.
2. If resolution fails, both plugins are flagged and the user is presented with a
   conflict report.
3. The user may choose to disable one plugin to resolve the conflict.

### 6.2 Service Conflicts

If two plugins attempt to register the same service ID:

1. The second registration is rejected unless the plugin holds the `kernel:override`
   capability.
2. A warning is logged.

### 6.3 Capability Conflicts

If a plugin requests a capability that conflicts with another plugin's exclusive access:

1. The kernel checks whether the capability is marked as exclusive.
2. If exclusive, the second request is rejected.
3. A warning is logged.

---

## 7. Plugin Metadata Enrichment

After discovery, the kernel enriches plugin metadata:

- **Dependency graph** — resolved and validated.
- **Load order** — computed via topological sort.
- **Compatibility flags** — computed from platform version and manifest constraints.
- **Risk score** — computed from permissions requested (more permissions = higher risk).

---

## 8. Plugin Lifecycle States

Plugins transition through these states during their lifetime:

```
discovered → validated → loaded → initializing → active → running → suspending →
suspended → resuming → deactivating → deactivated → unloading → unloaded → removed
```

Additionally, a plugin may enter a **faulted** state from any operational state if an
error occurs.

See [Plugin Lifecycle](PLUGIN_LIFECYCLE.md) for the full state machine.

---

## 9. Plugin Type Summary Table

| # | Type | Eager Load | Backend | Frontend | Storage | Events |
|---|---|---|---|---|---|---|
| 1 | Feature Plugin | No | Yes | Yes | Yes | Yes |
| 2 | Educational Content | Yes | Yes | Yes | No | Yes |
| 3 | Course Package | Yes | Yes | Yes | Yes | Yes |
| 4 | Assessment Pack | No | Yes | Yes | Yes | Yes |
| 5 | Localization Pack | Yes | Yes | No | No | No |
| 6 | Accessibility Profile | Yes | No | Yes | No | No |
| 7 | Reporting Template | No | Yes | Yes | Yes | Yes |
| 8 | Theme | Yes | No | Yes | No | No |
| 9 | SDK Extension | Yes | Yes | No | No | Yes |
| 10 | Institution Config | Yes | Yes | Yes | Yes | No |
| 11 | Example / Reference | Dev only | Yes | Yes | No | No |

---

## 10. References

- [Plugin Architecture](PLUGIN_ARCHITECTURE.md)
- [Plugin Lifecycle](PLUGIN_LIFECYCLE.md)
- [Plugin Manifest Specification](PLUGIN_MANIFEST_SPECIFICATION.md)
- [Plugin SDK](PLUGIN_SDK.md)
- [Plugin Sandbox](PLUGIN_SANDBOX.md)

---

*End of document.*
