# AuthShield Lab — Plugin Developer Guide

> **Version:** 1.0.0
> **Status:** Authoritative
> **See also:** [Plugin SDK](PLUGIN_SDK.md) · [Plugin Manifest](PLUGIN_MANIFEST_SPECIFICATION.md)

---

## 1. Getting Started

### 1.1 Prerequisites

- Python 3.12+
- AuthShield Lab platform installed
- `authshield-cli` command-line tool
- A text editor or IDE
- Git (optional, for version control)

### 1.2 Install the CLI

```bash
pip install authshield-cli
```

### 1.3 Create Your First Plugin

```bash
# Create a new plugin from the default template
authshield-cli plugin create my-first-plugin --type feature

# Navigate to the plugin directory
cd my-first-plugin/

# Validate the plugin
authshield-cli plugin validate .

# Run the plugin in development mode
authshield-cli plugin dev .
```

---

## 2. Creating a Plugin Step-by-Step

### Step 1: Choose a Plugin Type

| Type | Use Case |
|---|---|
| `feature` | Interactive UI features, lab scenarios, tools |
| `educational-content` | Lessons, tutorials, walkthroughs |
| `course-package` | Bundled curriculum with assessments |
| `assessment-pack` | Quizzes and lab challenges |
| `localization-pack` | Translations for a locale |
| `accessibility-profile` | Accessibility settings |
| `reporting-template` | Report layouts and exports |
| `theme` | Visual themes for the UI |
| `sdk-extension` | Extend the plugin SDK |
| `institution-config` | Institution-specific configuration |
| `example` | Reference implementation |

### Step 2: Create the Package Structure

```
my-plugin/
├── manifest.json
├── src/
│   ├── __init__.py
│   └── plugin.py
├── resources/
├── localization/
│   └── en.json
├── accessibility/
├── config/
│   └── defaults.json
├── docs/
│   └── README.md
├── assets/
│   └── icon-128.png
├── VERSION
├── CHANGELOG.md
└── MIGRATION.md
```

### Step 3: Write the Manifest

```json
{
  "plugin_id": "my-plugin",
  "name": "My Plugin",
  "description": "A description of what my plugin does for defensive cybersecurity education.",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "version": "1.0.0",
  "min_platform_version": "1.0.0",
  "license": "MIT",
  "type": "feature",
  "entry_point": "src.plugin:MyPlugin",
  "capabilities": [
    "ui:panel",
    "event:subscribe",
    "storage:rw"
  ],
  "permissions": [
    {
      "permission": "storage:rw",
      "reason": "Store user preferences and scan results."
    }
  ]
}
```

### Step 4: Implement the Plugin Class

```python
from authshield_sdk import PluginBase, PluginContext


class MyPlugin(PluginBase):
    """A defensive cybersecurity education plugin."""

    def __init__(self):
        self._scan_results = []

    async def on_init(self, ctx: PluginContext) -> None:
        """Called during initialization. Load saved state."""
        self._scan_results = ctx.storage.get_store("scan_results", default=[])
        ctx.logging.log_info("Plugin initialized", results_count=len(self._scan_results))

    async def on_activate(self, ctx: PluginContext) -> None:
        """Called during activation. Register services and hooks."""
        # Subscribe to events
        ctx.events.subscribe_event("lab.scan.completed", self._on_scan_completed)

        # Register a command
        ctx.commands.register_command(
            name="my-plugin:run-scan",
            handler=self._handle_run_scan,
            description="Run a defensive network scan"
        )

        # Register a UI panel
        ctx.ui.register_panel(
            id="my-plugin-panel",
            title="My Plugin",
            icon="shield",
            component="MyPluginPanel"
        )

        # Announce to screen readers
        ctx.accessibility.announce("My Plugin activated and ready.")

        ctx.logging.log_info("Plugin activated")

    async def on_deactivate(self, ctx: PluginContext) -> None:
        """Called during deactivation. Unregister everything."""
        ctx.logging.log_info("Plugin deactivated")

    async def on_unload(self, ctx: PluginContext) -> None:
        """Called during unloading. Release resources."""
        ctx.logging.log_info("Plugin unloaded")

    async def _on_scan_completed(self, payload: dict) -> None:
        """Handle lab scan completed event."""
        result = payload.get("result", {})
        self._scan_results.append(result)

    async def _handle_run_scan(self, args: dict) -> dict:
        """Handle the run-scan command."""
        return {
            "status": "completed",
            "results": self._scan_results
        }
```

### Step 5: Add Localization

Create `localization/en.json`:

```json
{
  "my-plugin.title": "My Plugin",
  "my-plugin.description": "A defensive cybersecurity tool.",
  "my-plugin.scan_complete": "Scan completed: {count} results found.",
  "my-plugin.no_results": "No scan results available."
}
```

Create `localization/de-DE.json`:

```json
{
  "my-plugin.title": "Mein Plugin",
  "my-plugin.description": "Ein defensives Cybersicherheitstool.",
  "my-plugin.scan_complete": "Scan abgeschlossen: {count} Ergebnisse gefunden.",
  "my-plugin.no_results": "Keine Scan-Ergebnisse verfügbar."
}
```

### Step 6: Add Default Configuration

Create `config/defaults.json`:

```json
{
  "my_plugin": {
    "scan_interval": 30,
    "max_results": 100,
    "enable_notifications": true
  }
}
```

### Step 7: Add Accessibility Metadata

Create `accessibility/aria-labels.json`:

```json
{
  "my-plugin-panel": "My Plugin Panel",
  "run-scan-button": "Run Defensive Scan",
  "results-table": "Scan Results Table"
}
```

### Step 8: Add Documentation

Create `docs/README.md`:

```markdown
# My Plugin

## Overview
A defensive cybersecurity education plugin.

## Features
- Run defensive scans
- View scan results
- Store preferences

## Configuration
| Key | Default | Description |
|---|---|---|
| scan_interval | 30 | Seconds between scans |
| max_results | 100 | Maximum results to display |
| enable_notifications | true | Show toast notifications |
```

### Step 9: Add Version File

Create `VERSION`:

```
1.0.0
```

### Step 10: Add Changelog

Create `CHANGELOG.md`:

```markdown
# Changelog

## 1.0.0 (2026-07-19)
- Initial release.
- Defensive scan functionality.
- Event-based architecture.
- Localized (English, German).
```

---

## 3. Using the SDK API

### 3.1 Configuration

```python
# Read configuration
refresh_rate = ctx.config.get_config("dashboard.refresh_rate", default=30)

# Write configuration
ctx.config.set_config("dashboard.last_scan", "2026-07-19")

# List all configuration
all_config = ctx.config.list_configs()
```

### 3.2 Logging

```python
ctx.logging.log_info("Plugin started", version="1.0.0")
ctx.logging.log_warning("Low disk space", available_mb=50)
ctx.logging.log_error("Connection failed", exc_info=True)
ctx.logging.log_debug("Processing item", item_id=42)
```

### 3.3 Events

```python
# Subscribe to events
handle = ctx.events.subscribe_event("lab.completed", self._on_lab_completed)

# Publish an event
await ctx.events.publish_event("my-plugin.scan.done", {"results": 42})

# Unsubscribe
ctx.events.unsubscribe(handle)
```

### 3.4 Storage

```python
# Write data
ctx.storage.set_store("last_scan_time", "2026-07-19T12:00:00Z")

# Read data
last_scan = ctx.storage.get_store("last_scan_time")

# Delete data
ctx.storage.delete_store("old_data")

# List all data
all_data = ctx.storage.list_store()
```

### 3.5 Notifications

```python
# Toast notification
ctx.notifications.show_toast("Scan complete!", level="success")

# Dialog
choice = await ctx.notifications.show_dialog(
    "Confirm",
    "Run a new scan?",
    buttons=["Yes", "No"]
)

# System notification
ctx.notifications.show_notification("Alert", "New threat detected!")
```

### 3.6 Localization

```python
# Translate a string
greeting = ctx.localization.translate("my-plugin.greeting", name="Admin")

# Pluralization
count = 5
message = ctx.localization.translate_plural("my-plugin.items", count, count=count)

# Get current locale
locale = ctx.localization.get_locale()
```

### 3.7 Accessibility

```python
# Register an accessible component
ctx.accessibility.register_component("my-panel", AccessibilityMetadata(
    role="region",
    label="My Plugin Panel",
    description="Defensive cybersecurity tool"
))

# Announce to screen readers
ctx.accessibility.announce("Scan completed with 3 results.")

# Move focus
ctx.accessibility.focus_management("results-table")
```

### 3.8 Validation

```python
# Validate input
result = ctx.validation.validate_input(port, rules=ValidationRules(
    type="integer",
    minimum=1,
    maximum=65535
))

# Validate against JSON schema
result = ctx.validation.validate_schema(data, schema)
```

### 3.9 UI Extensions

```python
# Register a panel
ctx.ui.register_panel(
    id="my-panel",
    title="My Panel",
    icon="shield",
    component="MyPanel"
)

# Register a tab
ctx.ui.register_tab(
    id="my-tab",
    title="Results",
    component="ResultsTab",
    parent_panel="my-panel"
)

# Register a toolbar button
ctx.ui.register_toolbar(
    id="my-scan-btn",
    label="Run Scan",
    icon="play",
    command="my-plugin:run-scan"
)
```

### 3.10 Commands and Queries

```python
# Register a command
ctx.commands.register_command(
    name="my-plugin:scan",
    handler=self._handle_scan,
    description="Run a defensive scan"
)

# Execute a command
result = await ctx.commands.execute_command("other-plugin:analyze")

# Register a query
ctx.queries.register_query(
    name="my-plugin:results",
    handler=self._query_results,
    description="Get scan results"
)

# Execute a query
results = await ctx.queries.execute_query("my-plugin:results", params={"limit": 10})
```

---

## 4. Implementing Accessibility

### 4.1 React Component Checklist

```typescript
// ✅ Keyboard navigation
<button
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
>
  Run Scan
</button>

// ✅ ARIA labels
<div role="region" aria-label="Scan Results">
  <table aria-label="Threat Results">
    <caption>Current threat scan results</caption>
    <thead>
      <tr>
        <th scope="col">Type</th>
        <th scope="col">Severity</th>
        <th scope="col">Action</th>
      </tr>
    </thead>
  </table>
</div>

// ✅ Live regions for dynamic updates
<div role="status" aria-live="polite">
  {resultCount} threats detected.
</div>

// ✅ Focus management
ctx.accessibility.focus_management("results-table");
```

### 4.2 CSS Accessibility

```css
/* ✅ Focus visible */
:focus-visible {
  outline: 2px solid var(--focus-color, #005fcc);
  outline-offset: 2px;
}

/* ✅ Reduced motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}

/* ✅ High contrast */
@media (forced-colors: active) {
  .threat-card {
    border: 2px solid ButtonText;
  }
}
```

---

## 5. Adding Localization

### 5.1 Translation Keys

Use dot-separated namespaces:

```
my-plugin.feature_name.action
```

### 5.2 Interpolation

```json
{
  "my-plugin.greeting": "Hello, {name}!",
  "my-plugin.count": "{count} items found"
}
```

```python
ctx.localization.translate("my-plugin.greeting", name="Admin")
# → "Hello, Admin!"
```

### 5.3 Pluralization

```json
{
  "my-plugin.items": {
    "one": "1 item",
    "other": "{count} items"
  }
}
```

```python
ctx.localization.translate_plural("my-plugin.items", count=5, count=5)
# → "5 items"
```

### 5.4 Adding a New Locale

1. Create `localization/<locale>.json`.
2. Copy all keys from `en.json`.
3. Translate all values.
4. Update `manifest.json → supported_languages`.

---

## 6. Testing Your Plugin

### 6.1 Local Testing

```bash
# Validate plugin
authshield-cli plugin validate .

# Run in development mode
authshield-cli plugin dev .

# Run tests
pytest tests/ -v

# Run accessibility tests
pytest tests/accessibility/ -v
```

### 6.2 Test Structure

```
tests/
├── test_plugin_loading.py
├── test_lifecycle.py
├── test_sandbox.py
├── test_permissions.py
├── test_sdk.py
├── test_accessibility.py
├── test_localization.py
├── test_performance.py
└── conftest.py
```

### 6.3 Writing Tests

```python
import pytest
from authshield_testing import PluginTestHarness

@pytest.fixture
def harness():
    return PluginTestHarness(plugin_path="./")

@pytest.mark.asyncio
async def test_plugin_loads(harness):
    plugin = harness.load()
    assert plugin.status == "loaded"

@pytest.mark.asyncio
async def test_plugin_activates(harness):
    plugin = harness.load()
    await plugin.initialize()
    await plugin.activate()
    assert plugin.status == "active"

@pytest.mark.asyncio
async def test_event_handler(harness):
    plugin = harness.load()
    await plugin.initialize()
    await plugin.activate()

    result = harness.publish_event("test.event", {"data": "value"})
    assert result.delivered is True
```

---

## 7. Packaging Your Plugin

### 7.1 Generate Integrity Manifest

```bash
authshield-cli integrity generate . --output integrity.json
```

### 7.2 Sign the Plugin

```bash
authshield-cli sign . --key publisher-key.pem --output signature.p7s
```

### 7.3 Create Distribution Package

```bash
authshield-cli plugin package . --output ../dist/
```

This creates:

```
dist/my-plugin-1.0.0.tar.gz
```

### 7.4 Validate the Package

```bash
authshield-cli plugin validate ../dist/my-plugin-1.0.0.tar.gz
```

---

## 8. Publishing Your Plugin

### 8.1 Publish to the Platform Registry

```bash
authshield-cli plugin publish ../dist/my-plugin-1.0.0.tar.gz
```

### 8.2 Institutional Distribution

Share the `.tar.gz` file directly with your institution. Users install with:

```bash
authshield-cli plugin install my-plugin-1.0.0.tar.gz
```

---

## 9. Updating Your Plugin

### 9.1 Version Bump

1. Update `VERSION` file.
2. Update `manifest.json → version`.
3. Add entry to `CHANGELOG.md`.
4. If major version, update `manifest.json → min_platform_version` and add `MIGRATION.md`.

### 9.2 Data Migration

If your update changes data formats, implement `on_upgrade()`:

```python
async def on_upgrade(self, ctx: PluginContext, old_version: str) -> None:
    if old_version.startswith("1."):
        # Migrate v1 data to v2 format
        old_data = ctx.storage.get_store("v1_data")
        new_data = self._migrate_v1_to_v2(old_data)
        ctx.storage.set_store("v2_data", new_data)
        ctx.storage.delete_store("v1_data")
```

### 9.3 Publish Update

```bash
authshield-cli plugin package . --output ../dist/
authshield-cli plugin publish ../dist/my-plugin-1.1.0.tar.gz
```

---

## 10. Troubleshooting

| Problem | Solution |
|---|---|
| Plugin not discovered | Check `manifest.json` is at package root and valid. |
| Plugin fails to load | Check entry point path matches `manifest.json → entry_point`. |
| `PermissionDenied` error | Add the required permission to `manifest.json → permissions`. |
| `CapabilityNotDeclared` error | Add the required capability to `manifest.json → capabilities`. |
| `SandboxViolation` error | Remove restricted module imports; use SDK APIs instead. |
| `MemoryLimitExceeded` error | Reduce memory usage; check for memory leaks. |
| `PluginTimeout` error | Optimize slow operations; increase timeout in `platform.json`. |
| Translation not found | Check key exists in all locale files. |
| Accessibility violation | Run `axe-core` and fix reported issues. |
| Signature invalid | Re-sign with a trusted publisher key. |

---

## 11. Best Practices

1. **Minimal permissions** — only request what you need.
2. **Graceful degradation** — handle missing optional dependencies.
3. **Accessible by default** — follow WCAG 2.2 AA from the start.
4. **Localize early** — use the Localization API for all user-visible text.
5. **Test thoroughly** — use the test harness and CI/CD.
6. **Document everything** — users and future maintainers will thank you.
7. **Follow conventions** — match existing code style and patterns.
8. **Version properly** — use SemVer; document breaking changes.
9. **Handle errors** — never let exceptions propagate to the kernel.
10. **Keep it offline** — no network calls; all data local.

---

## 12. Code Examples by Plugin Type

### 12.1 Educational Content Plugin

```python
from authshield_sdk import PluginBase, PluginContext

class SQLInjectionLesson(PluginBase):
    async def on_activate(self, ctx: PluginContext) -> None:
        ctx.ui.register_panel(
            id="sql-injection-lesson",
            title="SQL Injection Detection",
            icon="book",
            component="LessonPanel"
        )
        ctx.events.subscribe_event("lesson.progress", self._on_progress)

    async def _on_progress(self, payload: dict) -> None:
        step = payload.get("step", 0)
        self.ctx.logging.log_info(f"Lesson progress: step {step}")
```

### 12.2 Assessment Pack Plugin

```python
from authshield_sdk import PluginBase, PluginContext

class IncidentResponseQuiz(PluginBase):
    async def on_activate(self, ctx: PluginContext) -> None:
        ctx.reports.register_report("quiz-results", self._generate_results)
        ctx.commands.register_command(
            name="quiz:start",
            handler=self._start_quiz,
            description="Start the incident response quiz"
        )

    async def _start_quiz(self, args: dict) -> dict:
        return {"quiz_id": "ir-quiz-1", "questions": 20, "time_limit_minutes": 30}

    async def _generate_results(self, params: dict) -> ReportResult:
        return ReportResult(title="Quiz Results", format="json", data={})
```

### 12.3 Localization Pack Plugin

No Python code required — only localization files:

```
locale-de-DE/
├── manifest.json
├── localization/
│   ├── en.json
│   └── de-DE.json
└── VERSION
```

### 12.4 Theme Plugin

No Python code required — only CSS:

```
dark-theme/
├── manifest.json
├── frontend/
│   └── styles/
│       └── theme.css
└── VERSION
```

### 12.5 Reporting Template Plugin

```python
from authshield_sdk import PluginBase, PluginContext

class ComplianceReport(PluginBase):
    async def on_activate(self, ctx: PluginContext) -> None:
        ctx.reports.register_report("pci-dss-compliance", self._generate_compliance)

    async def _generate_compliance(self, params: dict) -> ReportResult:
        return ReportResult(
            title="PCI DSS Compliance Report",
            format="pdf",
            data={"status": "compliant", "controls": 256}
        )
```

---

## 13. References

- [Plugin SDK](PLUGIN_SDK.md)
- [Plugin Manifest Specification](PLUGIN_MANIFEST_SPECIFICATION.md)
- [Plugin Architecture](PLUGIN_ARCHITECTURE.md)
- [Plugin Testing](PLUGIN_TESTING.md)
- [Plugin Accessibility](PLUGIN_ACCESSIBILITY.md)
- [Plugin Security](PLUGIN_SECURITY.md)

---

*End of document.*
