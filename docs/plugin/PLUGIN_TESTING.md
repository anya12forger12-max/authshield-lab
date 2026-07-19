# AuthShield Lab — Plugin Testing

> **Version:** 1.0.0
> **Status:** Authoritative
> **See also:** [Plugin Lifecycle](PLUGIN_LIFECYCLE.md) · [Plugin Sandbox](PLUGIN_SANDBOX.md)

---

## 1. Overview

Thorough testing is required for all AuthShield Lab plugins. The platform provides a
comprehensive test harness, fixture library, and CI/CD integration to ensure plugins are
reliable, secure, accessible, and performant.

---

## 2. Test Categories

### 2.1 Plugin Loading Tests

Verify that the plugin loads correctly through the full discovery-to-activation pipeline.

| Test | Description | Expected Result |
|---|---|---|
| `test_discovery` | Place plugin in scan directory. | Plugin found in index. |
| `test_manifest_valid` | Provide valid manifest.json. | Validation passes. |
| `test_manifest_invalid` | Provide malformed manifest.json. | Validation fails, plugin skipped. |
| `test_entry_point_exists` | Entry point class exists in module. | Plugin loads. |
| `test_entry_point_missing` | Entry point class does not exist. | Plugin faults. |
| `test_entry_point_wrong_base` | Entry point does not subclass PluginBase. | Plugin faults. |
| `test_module_import` | Python module imports without error. | Plugin loaded. |
| `test_module_import_error` | Python module has syntax error. | Plugin faults, error logged. |
| `test_duplicate_plugin_id` | Two plugins with same ID. | Second plugin rejected. |
| `test_plugin_load_order` | Multiple plugins with dependencies. | Loaded in dependency order. |

**Test fixture:**

```python
@pytest.fixture
def sample_plugin(tmp_path):
    """Create a minimal valid plugin package."""
    plugin_dir = tmp_path / "test-plugin"
    plugin_dir.mkdir()
    (plugin_dir / "manifest.json").write_text(json.dumps({
        "plugin_id": "test-plugin",
        "name": "Test Plugin",
        "description": "A minimal test plugin for unit testing purposes.",
        "author": {"name": "Test Author"},
        "version": "1.0.0",
        "min_platform_version": "1.0.0",
        "license": "MIT",
        "type": "feature",
        "entry_point": "src.plugin:TestPlugin",
    }))
    src_dir = plugin_dir / "src"
    src_dir.mkdir()
    (src_dir / "__init__.py").write_text("")
    (src_dir / "plugin.py").write_text("""
from authshield_sdk import PluginBase

class TestPlugin(PluginBase):
    async def on_init(self, ctx):
        pass
    async def on_activate(self, ctx):
        pass
    async def on_deactivate(self, ctx):
        pass
    async def on_unload(self, ctx):
        pass
""")
    return plugin_dir
```

### 2.2 Compatibility Tests

Verify that plugins work correctly across platform versions.

| Test | Description | Expected Result |
|---|---|---|
| `test_compatible_version` | Plugin min_platform_version ≤ platform. | Plugin loads. |
| `test_incompatible_version` | Plugin min_platform_version > platform. | Plugin rejected. |
| `test_max_version_exceeded` | Platform version > plugin max_platform_version. | Plugin rejected. |
| `test_python_version` | Plugin runs on Python 3.12+. | Plugin loads. |
| `test_api_level_compatible` | Plugin targets compatible API level. | Plugin loads. |
| `test_api_level_deprecated` | Plugin targets deprecated API level. | Warning logged, plugin loads. |
| `test_api_level_unsupported` | Plugin targets removed API level. | Plugin rejected. |

### 2.3 Lifecycle Tests

Test each of the 16 lifecycle stages.

| Test | Stage | Description | Expected Result |
|---|---|---|---|
| `test_stage_discovery` | Discovery | Plugin directory scanned. | Manifest parsed. |
| `test_stage_validation` | Validation | Manifest validated. | Schema conformance. |
| `test_stage_sig_verification` | Sig Verification | Signature checked. | Verification result. |
| `test_stage_compatibility` | Compatibility | Version checked. | Compatibility result. |
| `test_stage_dep_resolution` | Dep Resolution | Dependencies resolved. | Graph resolved. |
| `test_stage_loading` | Loading | Module imported. | Module available. |
| `test_stage_initialization` | Initialization | `on_init` called. | Plugin initialized. |
| `test_stage_activation` | Activation | `on_activate` called. | Plugin activated. |
| `test_stage_execution` | Execution | Plugin handles requests. | Requests processed. |
| `test_stage_suspension` | Suspension | `on_suspend` called. | Plugin suspended. |
| `test_stage_resumption` | Resumption | `on_resume` called. | Plugin resumed. |
| `test_stage_deactivation` | Deactivation | `on_deactivate` called. | Plugin deactivated. |
| `test_stage_unloading` | Unloading | `on_unload` called. | Plugin unloaded. |
| `test_stage_removal` | Removal | Resources freed. | Resources released. |
| `test_stage_upgrade` | Upgrade | `on_upgrade` called. | Plugin upgraded. |
| `test_stage_rollback` | Rollback | Previous version restored. | Rollback succeeded. |

**Test example:**

```python
@pytest.mark.asyncio
async def test_stage_initialization(plugin_runtime, sample_plugin):
    """Test that on_init is called during initialization."""
    plugin = await plugin_runtime.load(sample_plugin)
    assert plugin.status == "loaded"

    await plugin.initialize()
    assert plugin.status == "initialized"
    assert plugin.on_init_called is True

@pytest.mark.asyncio
async def test_stage_activation(plugin_runtime, sample_plugin):
    """Test that on_activate registers services."""
    plugin = await plugin_runtime.load(sample_plugin)
    await plugin.initialize()
    await plugin.activate()

    assert plugin.status == "active"
    assert "test-service" in plugin.runtime.services.list_services()
```

### 2.4 Sandboxing Tests

Verify that the sandbox correctly restricts plugin behavior.

| Test | Description | Expected Result |
|---|---|---|
| `test_import_restricted_module` | Plugin imports `subprocess`. | `SandboxViolation` raised. |
| `test_import_allowed_module` | Plugin imports `json`. | Import succeeds. |
| `test_use_restricted_builtin` | Plugin calls `exec()`. | `SandboxViolation` raised. |
| `test_use_allowed_builtin` | Plugin calls `len()`. | Call succeeds. |
| `test_memory_limit` | Plugin allocates > 256 MB. | `MemoryLimitExceeded` raised. |
| `test_cpu_timeout` | Plugin runs > 30 seconds. | `PluginTimeout` raised. |
| `test_storage_quota` | Plugin writes > 50 MB. | `StorageQuotaExceeded` raised. |
| `test_rate_limiting` | Plugin makes > 1000 API calls/min. | `RateLimitedError` raised. |
| `test_cross_plugin_isolation` | Plugin A reads Plugin B's storage. | `AccessDenied` raised. |
| `test_namespace_isolation` | Plugin A imports Plugin B's module. | `ImportError` raised. |

**Test example:**

```python
@pytest.mark.asyncio
async def test_import_restricted_module(plugin_runtime, malicious_plugin):
    """Test that importing restricted modules is blocked."""
    plugin = await plugin_runtime.load(malicious_plugin)

    with pytest.raises(SandboxViolation, match="subprocess"):
        await plugin.initialize()

@pytest.mark.asyncio
async def test_memory_limit(plugin_runtime, memory_hungry_plugin):
    """Test that memory limits are enforced."""
    plugin = await plugin_runtime.load(memory_hungry_plugin)
    await plugin.initialize()
    await plugin.activate()

    with pytest.raises(MemoryLimitExceeded):
        await plugin.execute_operation("allocate_memory", size_mb=300)
```

### 2.5 Permission Enforcement Tests

Verify that permissions are checked at runtime.

| Test | Description | Expected Result |
|---|---|---|
| `test_permission_granted` | Plugin uses declared permission. | Operation succeeds. |
| `test_permission_denied` | Plugin uses undeclared permission. | `PermissionDenied` raised. |
| `test_capability_enforced` | Plugin uses undeclared capability. | `CapabilityNotDeclared` raised. |
| `test_permission_revoked` | Permission revoked after activation. | `PermissionDenied` on next use. |
| `test_static_analysis_clean` | Plugin with no violations. | Analysis passes. |
| `test_static_analysis_violation` | Plugin with restricted imports. | Analysis flags violations. |

### 2.6 SDK Compatibility Tests

Verify that SDK APIs work correctly within the sandbox.

| Test | Description | Expected Result |
|---|---|---|
| `test_config_api` | Read/write configuration. | Values persisted. |
| `test_logging_api` | Write log entries. | Entries in log file. |
| `test_events_api` | Publish and subscribe. | Events delivered. |
| `test_storage_api` | Read/write storage. | Values persisted. |
| `test_validation_api` | Validate input and schema. | Validation works. |
| `test_notifications_api` | Show toast and dialog. | Notifications displayed. |
| `test_ui_extension_api` | Register panel and tab. | UI components registered. |
| `test_commands_api` | Register and execute command. | Command executes. |
| `test_queries_api` | Register and execute query. | Query returns results. |
| `test_diagnostics_api` | Health check and system info. | Info returned. |
| `test_localization_api` | Translate strings. | Translations correct. |
| `test_accessibility_api` | Register component and announce. | Component registered. |
| `test_reporting_api` | Register and generate report. | Report generated. |

### 2.7 Accessibility Tests

Verify that plugins meet accessibility requirements.

| Test | Description | Expected Result |
|---|---|---|
| `test_axe_clean` | Run axe-core on plugin UI. | Zero violations. |
| `test_keyboard_navigation` | Tab through all elements. | All elements focusable. |
| `test_focus_visible` | Check focus indicators. | Focus visible on all elements. |
| `test_alt_text` | Check all images. | All images have alt text. |
| `test_aria_labels` | Check ARIA labels. | All interactive elements labeled. |
| `test_live_regions` | Check dynamic updates. | Live regions present. |
| `test_color_contrast` | Check contrast ratios. | All text ≥ 4.5:1 ratio. |
| `test_font_scaling` | Scale to 200%. | Layout intact. |
| `test_reduced_motion` | Enable reduced motion. | Animations disabled. |
| `test_high_contrast` | Enable high contrast. | All content visible. |
| `test_screen_reader` | Test with NVDA/VoiceOver. | Content read correctly. |
| `test_skip_navigation` | Check skip links. | Skip link present and functional. |

**Test example:**

```python
import axe
from playwright.sync_api import Page

def test_axe_clean(page: Page, plugin_url: str):
    """Run axe-core accessibility checks."""
    page.goto(plugin_url)
    results = axe.run(page)
    violations = results.violations
    assert len(violations) == 0, f"Accessibility violations: {violations}"

def test_keyboard_navigation(page: Page, plugin_url: str):
    """Verify all interactive elements are keyboard accessible."""
    page.goto(plugin_url)
    interactive_elements = page.query_selector_all(
        'button, a, input, select, textarea, [tabindex]'
    )
    for element in interactive_elements:
        element.focus()
        assert element.evaluate(
            "el => document.activeElement === el"
        ), f"Element not focusable: {element}"
```

### 2.8 Localization Tests

Verify that localization works correctly.

| Test | Description | Expected Result |
|---|---|---|
| `test_translate_base_locale` | Translate in base locale. | Correct string returned. |
| `test_translate_other_locale` | Translate in non-base locale. | Translated string returned. |
| `test_translate_fallback` | Translate missing key. | Falls back to base locale. |
| `test_translate_plural` | Pluralization. | Correct plural form. |
| `test_locale_override` | Plugin overrides locale. | Override affects only this plugin. |
| `test_translation_completeness` | All keys present in all locales. | Completeness report generated. |
| `test_rtl_support` | Test with RTL locale. | Layout mirrors correctly. |

### 2.9 Performance Tests

Verify that plugins meet performance requirements.

| Test | Description | Threshold |
|---|---|---|
| `test_load_time` | Time to load plugin. | < 2 seconds |
| `test_activation_time` | Time to activate plugin. | < 5 seconds |
| `test_memory_usage` | RSS memory at idle. | < 50 MB |
| `test_memory_leak` | Memory after 1000 operations. | < 10% increase |
| `test_api_latency` | SDK call latency. | < 10ms (p95) |
| `test_event_throughput` | Events processed per second. | > 1000/sec |
| `test_startup_impact` | Platform startup time with plugin. | < 10% increase |
| `test_concurrent_operations` | 100 concurrent operations. | All complete < 5 seconds |

**Test example:**

```python
import time
import psutil

def test_load_time(plugin_runtime, sample_plugin):
    """Measure plugin load time."""
    start = time.monotonic()
    plugin = plugin_runtime.load_sync(sample_plugin)
    elapsed = time.monotonic() - start
    assert elapsed < 2.0, f"Load time {elapsed:.2f}s exceeds 2s threshold"

def test_memory_usage(plugin_runtime, sample_plugin):
    """Measure plugin memory usage at idle."""
    process = psutil.Process()
    mem_before = process.memory_info().rss
    plugin = plugin_runtime.load_sync(sample_plugin)
    plugin.initialize_sync()
    plugin.activate_sync()
    mem_after = process.memory_info().rss
    usage_mb = (mem_after - mem_before) / (1024 * 1024)
    assert usage_mb < 50, f"Memory usage {usage_mb:.1f}MB exceeds 50MB threshold"
```

### 2.10 Regression Tests

Ensure that previously fixed bugs do not recur.

| Test | Description | Bug Reference |
|---|---|---|
| `test_issue_123_memory_leak` | Memory leak in event handler. | #123 |
| `test_issue_456_config_override` | Config override not persisting. | #456 |
| `test_issue_789_accessibility_crash` | Crash when screen reader enabled. | #789 |

---

## 3. Test Harness for Plugin Developers

### 3.1 Using the Test Harness

```python
from authshield_testing import PluginTestHarness

# Create a test harness
harness = PluginTestHarness(plugin_path="./my-plugin/")

# Load and initialize the plugin
plugin = harness.load()
plugin.initialize()

# Test SDK APIs
assert plugin.ctx.config.get_config("key") == expected_value
assert plugin.ctx.storage.get_store("key") == expected_value

# Test event handling
result = harness.publish_event("test.event", {"data": "value"})
assert result.delivered is True

# Test error handling
with pytest.raises(PermissionDenied):
    plugin.ctx.storage.set_store("key", "value")  # No storage:rw permission

# Cleanup
plugin.deactivate()
plugin.unload()
```

### 3.2 Test Fixtures

The platform provides pre-built test fixtures:

| Fixture | Description |
|---|---|
| `sample_plugin` | A minimal valid plugin. |
| `malicious_plugin` | A plugin that tries to bypass sandbox. |
| `memory_hungry_plugin` | A plugin that allocates excessive memory. |
| `slow_plugin` | A plugin that takes a long time to initialize. |
| `incompatible_plugin` | A plugin targeting a different platform version. |
| `unsigned_plugin` | A plugin without a digital signature. |
| `corrupt_plugin` | A plugin with a corrupted manifest. |
| `accessible_plugin` | A fully accessible plugin for testing. |
| `localizable_plugin` | A plugin with full localization support. |

### 3.3 Fixture Library Location

```
<platform_root>/testing/fixtures/
├── sample_plugin/
├── malicious_plugin/
├── memory_hungry_plugin/
├── slow_plugin/
├── incompatible_plugin/
├── unsigned_plugin/
├── corrupt_plugin/
├── accessible_plugin/
└── localizable_plugin/
```

---

## 4. CI/CD Integration

### 4.1 GitHub Actions Workflow

```yaml
name: Plugin Tests
on:
  push:
    paths: ['plugins/**']
  pull_request:
    paths: ['plugins/**']

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12', '3.13']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[test]"
          pip install -e ".[dev]"

      - name: Lint
        run: |
          ruff check plugins/
          mypy plugins/ --strict

      - name: Unit tests
        run: |
          pytest plugins/ -v --cov=plugins/ --cov-report=xml

      - name: Plugin loading tests
        run: |
          pytest tests/plugin_loading/ -v

      - name: Lifecycle tests
        run: |
          pytest tests/lifecycle/ -v

      - name: Sandbox tests
        run: |
          pytest tests/sandbox/ -v

      - name: Permission tests
        run: |
          pytest tests/permissions/ -v

      - name: Accessibility tests
        run: |
          pytest tests/accessibility/ -v
          npx axe-core http://localhost:3000

      - name: Performance tests
        run: |
          pytest tests/performance/ -v

      - name: Generate coverage report
        run: |
          coverage xml
          coverage html

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

### 4.2 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: plugin-validate
        name: Validate plugin manifest
        entry: authshield-cli plugin validate
        language: system
        files: manifest\.json$

      - id: accessibility-check
        name: Run axe-core accessibility checks
        entry: npx axe-core
        language: system
        files: \.(tsx|jsx)$

      - id: lint-plugin
        name: Lint plugin code
        entry: ruff check
        language: system
        files: \.py$
```

### 4.3 Quality Gates

| Gate | Requirement | Enforced |
|---|---|---|
| Manifest validation | All manifests valid | Yes |
| Unit test coverage | ≥ 80% line coverage | Yes |
| Accessibility score | Lighthouse ≥ 90 | Yes |
| axe-core violations | Zero critical/serious | Yes |
| Load time | < 2 seconds | Yes |
| Memory usage | < 50 MB idle | Yes |
| No restricted imports | Static analysis clean | Yes |
| Documentation complete | All required docs present | Warning |

---

## 5. Test Reporting

### 5.1 Test Report Format

```json
{
  "plugin_id": "threat-dashboard",
  "plugin_version": "1.2.0",
  "platform_version": "3.0.0",
  "python_version": "3.12.4",
  "test_run_id": "uuid",
  "timestamp": "2026-07-19T12:00:00Z",
  "results": {
    "loading": { "total": 10, "passed": 10, "failed": 0 },
    "lifecycle": { "total": 16, "passed": 16, "failed": 0 },
    "sandbox": { "total": 10, "passed": 10, "failed": 0 },
    "permissions": { "total": 6, "passed": 6, "failed": 0 },
    "sdk": { "total": 13, "passed": 13, "failed": 0 },
    "accessibility": { "total": 12, "passed": 12, "failed": 0 },
    "localization": { "total": 7, "passed": 7, "failed": 0 },
    "performance": { "total": 8, "passed": 8, "failed": 0 }
  },
  "summary": {
    "total": 82,
    "passed": 82,
    "failed": 0,
    "skipped": 0,
    "duration_ms": 15234
  }
}
```

### 5.2 CI/CD Report Publishing

Test results are published to:

1. GitHub Actions summary.
2. Codecov (coverage).
3. Platform-internal test dashboard (if available).

---

## 6. References

- [Plugin Lifecycle](PLUGIN_LIFECYCLE.md)
- [Plugin Sandbox](PLUGIN_SANDBOX.md)
- [Plugin Accessibility](PLUGIN_ACCESSIBILITY.md)
- [Plugin Developer Guide](PLUGIN_DEVELOPER_GUIDE.md)

---

*End of document.*
