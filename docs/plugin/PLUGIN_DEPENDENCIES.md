# AuthShield Lab — Plugin Dependency Management

> **Version:** 1.0.0
> **Status:** Authoritative
> **See also:** [Plugin Framework](PLUGIN_FRAMEWORK.md) · [Plugin Lifecycle](PLUGIN_LIFECYCLE.md)

---

## 1. Overview

AuthShield Lab operates in an **offline-first** environment. All plugin dependencies must be
bundled with the plugin package or pre-installed on the platform. There is no runtime
dependency download. The dependency management system resolves, validates, and enforces
version constraints at startup.

---

## 2. Dependency Types

### 2.1 Required Dependencies

Declared under `manifest.json → dependencies`. These **must** be present and compatible for
the plugin to load.

```json
{
  "dependencies": {
    "core-data-service": "^1.0.0",
    "lab-engine": ">=2.0.0 <3.0.0"
  }
}
```

**Rules:**
- All required dependencies must be installed.
- Version constraints must be satisfied.
- If any required dependency is missing or incompatible, the plugin is marked as
  `unresolvable` and does not load.

### 2.2 Optional Dependencies

Declared under `manifest.json → optional_dependencies`. These enhance functionality but
are not required.

```json
{
  "optional_dependencies": {
    "notification-center": "^1.0.0",
    "advanced-analytics": "^2.0.0"
  }
}
```

**Rules:**
- If present and compatible, the plugin loads with full functionality.
- If missing, the plugin loads with reduced functionality.
- The plugin must gracefully handle the absence of optional dependencies.

---

## 3. Version Constraints (SemVer Ranges)

AuthShield Lab uses **SemVer 2.0.0** with range notation derived from
[node-semver](https://github.com/npm/node-semver):

| Range | Meaning |
|---|---|
| `^1.0.0` | ≥1.0.0 and <2.0.0 |
| `^1.2.3` | ≥1.2.3 and <2.0.0 |
| `~1.0.0` | ≥1.0.0 and <1.1.0 |
| `~1.2.3` | ≥1.2.3 and <1.3.0 |
| `>=1.0.0 <2.0.0` | Explicit range |
| `1.0.0` | Exact match only |
| `*` | Any version (discouraged) |
| `>=1.0.0` | No upper bound (discouraged) |

**Best practice:** Always use `^` for compatible ranges. Avoid `>=` without an upper bound.

---

## 4. Conflict Detection

### 4.1 Version Incompatibilities

When two plugins depend on the same dependency with incompatible ranges:

```
Plugin A requires: core-data-service ^1.0.0  (>=1.0.0 <2.0.0)
Plugin B requires: core-data-service ^2.0.0  (>=2.0.0 <3.0.0)
```

The resolver detects this conflict and reports:

```
Conflict: core-data-service
  Plugin A requires ^1.0.0 (compatible with 1.x)
  Plugin B requires ^2.0.0 (compatible with 2.x)
  No version satisfies both constraints.
```

**Resolution options:**
1. The user disables one of the conflicting plugins.
2. The user updates one plugin to a version with compatible dependency ranges.
3. The kernel applies the **most restrictive** strategy (refuse to load both).

### 4.2 Conflict Report

When conflicts are detected, the kernel generates a detailed report:

```json
{
  "conflicts": [
    {
      "dependency": "core-data-service",
      "requests": [
        { "plugin_id": "plugin-a", "version_range": "^1.0.0" },
        { "plugin_id": "plugin-b", "version_range": "^2.0.0" }
      ],
      "resolution": "none_possible"
    }
  ],
  "affected_plugins": ["plugin-a", "plugin-b"],
  "installed_versions": ["1.5.0", "2.1.0"]
}
```

---

## 5. Circular Dependency Prevention

The dependency resolver builds a directed acyclic graph (DAG) of plugin dependencies. If a
cycle is detected, the resolver reports an error.

### 5.1 Detection Algorithm

```python
def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Detect cycles in the dependency graph using DFS."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    parent = {node: None for node in graph}
    cycles = []

    def dfs(node):
        color[node] = GRAY
        for neighbor in graph.get(node, []):
            if color[neighbor] == GRAY:
                # Found a cycle
                cycle = []
                current = node
                while current != neighbor:
                    cycle.append(current)
                    current = parent[current]
                cycle.append(neighbor)
                cycle.reverse()
                cycles.append(cycle)
            elif color[neighbor] == WHITE:
                parent[neighbor] = node
                dfs(neighbor)
        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            dfs(node)

    return cycles
```

### 5.2 Example

```
Plugin A → Plugin B → Plugin C → Plugin A   (CYCLE DETECTED)
```

The kernel reports:

```
Circular dependency detected:
  A → B → C → A
  All plugins in the cycle will not load.
```

---

## 6. Upgrade Compatibility

### 6.1 Migration Guides

When upgrading a plugin that declares a `MIGRATION.md` file, the kernel:

1. Reads the migration guide.
2. Calls the plugin's `on_upgrade()` hook with the old version.
3. Executes any data migration logic.
4. Verifies the upgrade succeeded.

### 6.2 Upgrade Rules

| Scenario | Rule |
|---|---|
| Patch upgrade (1.0.0 → 1.0.1) | Automatic, no migration needed. |
| Minor upgrade (1.0.0 → 1.1.0) | Automatic, new features available. |
| Major upgrade (1.0.0 → 2.0.0) | Migration required. `on_upgrade()` called. |

### 6.3 Upgrade Ordering

Plugins are upgraded in **reverse dependency order** (dependents first, then dependencies).
This ensures that when a dependency is upgraded, all its dependents have already been
upgraded to support the new version.

---

## 7. Downgrade Protection

The platform prevents accidental downgrades:

1. **Manifest check:** If the installed version is newer than the version being loaded, the
   kernel logs a warning and refuses to load unless `--allow-downgrade` flag is set.
2. **Data compatibility:** Downgrades may break data formats. The kernel checks the
   `min_platform_version` of the currently installed version to ensure compatibility.
3. **Rollback exception:** The Rollback lifecycle stage is the only controlled downgrade
   path. It restores the previous version and its data.

---

## 8. Offline Dependency Resolution

All dependencies must be available locally:

1. **Bundled dependencies:** Plugin packages include their dependencies in `vendor/` or
   reference other local plugins.
2. **Pre-installed dependencies:** The platform ships with core plugins (e.g.
   `core-data-service`, `lab-engine`) pre-installed.
3. **No network access:** The dependency resolver never attempts to download packages.

### 8.1 Dependency Bundling

Plugins may vendor their dependencies:

```
my-plugin/
├── manifest.json
├── src/
│   └── plugin.py
└── vendor/
    └── my-library/
        ├── manifest.json
        └── src/
```

Vendored plugins are loaded from the `vendor/` directory and subject to the same sandbox
restrictions.

### 8.2 Platform Core Dependencies

The platform ships with these core plugins that other plugins commonly depend on:

| Plugin ID | Version | Purpose |
|---|---|---|
| `core-data-service` | 2.x | Data access layer |
| `lab-engine` | 2.x | Lab execution engine |
| `assessment-framework` | 1.x | Assessment and grading |
| `notification-center` | 1.x | User notifications |
| `report-service` | 1.x | Report generation |
| `i18n-engine` | 1.x | Internationalization |

---

## 9. Dependency Resolution Algorithm

### 9.1 Algorithm Overview

```
1. Build the dependency graph from all discovered plugin manifests.
2. Validate all dependency IDs exist in the plugin index.
3. Validate all version constraints can be satisfied by installed versions.
4. Detect circular dependencies.
5. Detect conflicts (incompatible version ranges).
6. Topologically sort the graph.
7. Return the sorted load order.
```

### 9.2 Topological Sort

The kernel uses Kahn's algorithm for topological sorting:

```python
def topological_sort(graph: dict[str, list[str]], in_degree: dict[str, int]) -> list[str]:
    """Kahn's algorithm for topological sort."""
    queue = [node for node in graph if in_degree[node] == 0]
    result = []

    while queue:
        queue.sort()  # Deterministic ordering
        node = queue.pop(0)
        result.append(node)

        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(graph):
        raise CircularDependencyError("Dependency graph contains cycles")

    return result
```

### 9.3 Resolution Priority

When multiple versions of a dependency are available:

1. Use the version that satisfies the most constraints.
2. Prefer the newest compatible version.
3. If still ambiguous, prefer the version installed in `built-in/` over `installed/`.

---

## 10. Error Messages for Dependency Failures

| Error | Message |
|---|---|
| Missing required dependency | `Plugin "{plugin_id}" requires "{dep_id}" but it is not installed. Install "{dep_id}" >= {min_version}.` |
| Version conflict | `Plugin "{plugin_id}" requires "{dep_id}" {range} but installed version is {installed}. No compatible version found.` |
| Circular dependency | `Circular dependency detected: {cycle}. These plugins cannot be loaded.` |
| Incompatible versions | `Plugins "{plugin_a}" and "{plugin_b}" require incompatible versions of "{dep_id}". {plugin_a} needs {range_a}, {plugin_b} needs {range_b}.` |
| Missing optional dependency (warning) | `Plugin "{plugin_id}" optionally depends on "{dep_id}" which is not installed. Reduced functionality.` |
| Downgrade detected | `Plugin "{plugin_id}" version {new} is older than installed version {installed}. Downgrade blocked. Use --allow-downgrade to override.` |

---

## 11. Dependency Graph Cache

The resolved dependency graph is cached to speed up subsequent startups:

```
~/.authshieldlab/cache/dependency_graph.json
```

The cache is invalidated when:

- A plugin is installed, upgraded, or removed.
- The platform version changes.
- The cache file is older than 24 hours.

---

## 12. References

- [Plugin Framework](PLUGIN_FRAMEWORK.md)
- [Plugin Lifecycle](PLUGIN_LIFECYCLE.md)
- [Plugin Manifest Specification](PLUGIN_MANIFEST_SPECIFICATION.md)
- [Plugin Package Format](PLUGIN_PACKAGE_FORMAT.md)

---

*End of document.*
