# AuthShield Lab — Plugin Package Format

> **Version:** 1.0.0
> **Status:** Authoritative
> **See also:** [Plugin Manifest](PLUGIN_MANIFEST_SPECIFICATION.md) · [Plugin Security](PLUGIN_SECURITY.md)

---

## 1. Overview

An AuthShield Lab plugin is distributed as a **directory package** (not a compressed
archive). The package format is designed for:

- **Offline installation** — no network access needed.
- **Integrity verification** — checksums and digital signatures.
- **Security** — tamper detection before loading.
- **Accessibility** — metadata for assistive technologies.
- **Localization** — translation bundles for multiple locales.

---

## 2. Package Directory Layout

```
my-plugin/
├── manifest.json              # Required: plugin metadata
├── src/                       # Required: plugin Python code
│   ├── __init__.py
│   └── plugin.py              # Entry point module
├── resources/                 # Optional: static resources
│   ├── templates/
│   └── schemas/
├── localization/              # Optional: translation files
│   ├── en.json
│   ├── de-DE.json
│   ├── fr.json
│   └── ja-JP.json
├── accessibility/             # Optional: accessibility metadata
│   ├── aria-labels.json
│   └── keyboard-mappings.json
├── config/                    # Optional: default configuration
│   └── defaults.json
├── docs/                      # Optional: documentation
│   ├── user-guide.md
│   └── api-reference.md
├── assets/                    # Optional: images, icons
│   ├── icon-128.png
│   ├── icon-256.png
│   └── logo.svg
├── vendor/                    # Optional: vendored dependencies
│   └── my-library/
├── frontend/                  # Optional: frontend components
│   ├── components/
│   └── styles/
├── integrity.json             # Required for distribution: checksums
├── signature.p7s              # Required for distribution: digital signature
├── VERSION                    # Required: version file
├── CHANGELOG.md               # Recommended: version history
└── MIGRATION.md               # Optional: upgrade instructions
```

---

## 3. Required Files

### 3.1 manifest.json

The plugin manifest. See [Plugin Manifest Specification](PLUGIN_MANIFEST_SPECIFICATION.md)
for the full schema.

**Rules:**
- Must be valid JSON.
- Must conform to the manifest JSON Schema.
- Must be at the package root.

### 3.2 src/ Directory

Contains the plugin's Python source code.

**Rules:**
- Must contain at least one `.py` file.
- The entry point module (declared in `manifest.json → entry_point`) must exist.
- Entry point format: `src.plugin:MyPluginClass`.
- All code must be compatible with Python 3.12+.
- No compiled extensions (`.so`, `.pyd`) are allowed.

### 3.3 VERSION

A plain-text file containing the plugin version in SemVer format.

```
1.2.0
```

**Rules:**
- Must match the `version` field in `manifest.json`.
- Must be a valid SemVer string.
- Must not contain a trailing newline (optional, but recommended).

---

## 4. Required Files for Distribution

These files are required for plugins distributed outside the platform's built-in set.

### 4.1 integrity.json

Contains SHA-256 checksums for all files in the package.

```json
{
  "algorithm": "sha256",
  "files": {
    "manifest.json": "a1b2c3d4e5f6...",
    "src/__init__.py": "f6e5d4c3b2a1...",
    "src/plugin.py": "1a2b3c4d5e6f...",
    "VERSION": "6f5e4d3c2b1a..."
  }
}
```

**Rules:**
- Must cover all files except `integrity.json` itself, `signature.p7s`, and `.gitignore`.
- Checksums are hex-encoded SHA-256 hashes.
- The kernel verifies checksums during the Signature Verification lifecycle stage.

### 4.2 signature.p7s

A PKCS#7 detached signature (CMS) signed by the publisher's X.509 certificate or GPG key.

**Rules:**
- Must be verifiable against a trust anchor in the platform's `trust_anchors/` directory.
- If unsigned, the plugin can only be loaded in `development` mode with
  `--insecure-plugins` flag.
- The signature covers the `integrity.json` file, which transitively covers all other files.

---

## 5. Optional Files

### 5.1 src/ Subdirectories

| Directory | Purpose |
|---|---|
| `src/models/` | Data models (Pydantic or dataclasses). |
| `src/services/` | Service implementations. |
| `src/handlers/` | Event and command handlers. |
| `src/utils/` | Utility functions. |

### 5.2 resources/

Static resources used by the plugin at runtime:

- `resources/templates/` — Jinja2 or similar templates.
- `resources/schemas/` — JSON schemas for data validation.
- `resources/seeds/` — Seed data for initialization.

### 5.3 localization/

Translation files for internationalization. Each file is named by locale code:

```json
{
  "dashboard.greeting": "Willkommen, {name}!",
  "dashboard.threat_count": "{count} Bedrohungen gefunden",
  "dashboard.no_threats": "Keine Bedrohungen erkannt"
}
```

**Rules:**
- File names must match BCP 47 locale codes (e.g. `en.json`, `de-DE.json`).
- The base locale (usually `en.json`) must be present.
- Translation keys must be consistent across all locale files.

### 5.4 accessibility/

Accessibility metadata files:

- `accessibility/aria-labels.json` — ARIA labels for UI components.
- `accessibility/keyboard-mappings.json` — Keyboard shortcuts.
- `accessibility/screen-reader-hints.json` — Screen reader guidance.

### 5.5 config/

Default configuration values. The file `config/defaults.json` is merged into the platform
configuration under `plugins.<plugin_id>`.

```json
{
  "dashboard": {
    "refresh_rate": 30,
    "theme": "dark",
    "max_threats_displayed": 100
  }
}
```

### 5.6 docs/

Plugin documentation files. Referenced by `manifest.json → documentation_references`.

### 5.7 assets/

Images and icons used by the plugin in the UI.

**Recommended sizes:**
- Icon: 128×128 PNG (also 256×256 for high-DPI).
- Logo: SVG preferred, PNG fallback.

### 5.8 vendor/

Vendored dependencies. Each vendored dependency is a subdirectory with its own `manifest.json`
and `src/` directory.

**Rules:**
- Vendored dependencies are loaded by the kernel and subject to sandbox restrictions.
- Vendored dependencies must not duplicate installed plugins.

### 5.9 frontend/

Frontend components for the Electron + React UI.

```
frontend/
├── components/
│   ├── MyPanel.tsx
│   └── MyWidget.tsx
├── styles/
│   └── my-plugin.css
└── index.tsx                  # Frontend entry point
```

**Rules:**
- Frontend code is loaded by the Electron renderer process.
- Must use React 18+ and TypeScript 5+.
- Must not access Node.js APIs directly (IPC through the plugin bridge).

### 5.10 CHANGELOG.md

A Markdown file documenting version history:

```markdown
# Changelog

## 1.2.0 (2026-07-15)
- Added: Real-time threat feed integration.
- Fixed: Dashboard refresh rate now respects user preferences.

## 1.1.0 (2026-06-01)
- Added: Export to PDF functionality.
- Changed: Improved accessibility for screen readers.

## 1.0.0 (2026-04-01)
- Initial release.
```

### 5.11 MIGRATION.md

Upgrade instructions for major version changes:

```markdown
# Migration Guide: 1.x → 2.0

## Breaking Changes
- The `scan()` method now returns a `ScanResult` object instead of a dict.
- Configuration key `scan_interval` renamed to `refresh_rate`.

## Data Migration
- Automatic migration handles configuration key renames.
- Scan results from v1 are compatible with v2.

## Manual Steps
- None required.
```

---

## 6. Package Creation Process

### 6.1 Using the CLI

```bash
# Create a new plugin package from template
authshield-cli plugin create my-plugin --type feature

# Validate the package
authshield-cli plugin validate ./my-plugin/

# Package for distribution (generates integrity.json and signature)
authshield-cli plugin package ./my-plugin/ --output ./dist/

# Sign the package
authshield-cli plugin sign ./dist/my-plugin/ --key private-key.pem
```

### 6.2 Manual Creation

1. Create the directory structure.
2. Write `manifest.json` conforming to the schema.
3. Implement the plugin class in `src/`.
4. Add localization files in `localization/`.
5. Add accessibility metadata in `accessibility/`.
6. Add default configuration in `config/defaults.json`.
7. Add documentation in `docs/`.
8. Generate `integrity.json`:

```bash
authshield-cli integrity generate ./my-plugin/ --output ./my-plugin/integrity.json
```

9. Sign the package:

```bash
authshield-cli sign ./my-plugin/ --key publisher-key.pem --output ./my-plugin/signature.p7s
```

---

## 7. Package Validation Checklist

Before distributing a plugin, verify:

- [ ] `manifest.json` is valid and conforms to the JSON Schema.
- [ ] `src/` contains at least one Python file.
- [ ] Entry point class exists and subclasses `PluginBase`.
- [ ] `VERSION` file matches `manifest.json → version`.
- [ ] `integrity.json` checksums are correct for all files.
- [ ] `signature.p7s` is valid and verifiable against trust anchors.
- [ ] All declared capabilities are used (no undeclared capabilities).
- [ ] All declared permissions are justified.
- [ ] Localization files have consistent keys across all locales.
- [ ] Accessibility metadata is complete (WCAG level declared).
- [ ] Documentation files referenced in manifest exist.
- [ ] No restricted modules are imported.
- [ ] No restricted builtins are used.
- [ ] All interactive elements have keyboard navigation.
- [ ] All images have alt text.
- [ ] CHANGELOG.md is up to date.
- [ ] MIGRATION.md exists for major version upgrades.
- [ ] Plugin has been tested with the plugin test harness.

---

## 8. Package Size Limits

| Component | Maximum Size |
|---|---|
| Total package | 50 MB |
| `src/` directory | 10 MB |
| `resources/` directory | 20 MB |
| `localization/` directory | 5 MB |
| `frontend/` directory | 10 MB |
| Individual file | 5 MB |
| `manifest.json` | 64 KB |

These limits are enforced during validation. Exceeding limits causes a validation error.

---

## 9. Package Naming Convention

```
<plugin-id>-<version>.tar.gz
```

Example: `threat-dashboard-1.2.0.tar.gz`

**Rules:**
- `plugin-id` must match `manifest.json → plugin_id`.
- `version` must match `manifest.json → version`.
- Distribution format is `.tar.gz` (tarball with gzip compression).

---

## 10. Installation Process

When a user installs a plugin package:

1. Extract the tarball to `~/.authshieldlab/plugins/installed/<plugin-id>/`.
2. Verify `manifest.json` exists and is valid.
3. Verify `integrity.json` checksums.
4. Verify `signature.p7s` against trust anchors.
5. Register the plugin in the plugin index.
6. Load and activate the plugin (if `auto_activate` is true in platform config).

---

## 11. References

- [Plugin Manifest Specification](PLUGIN_MANIFEST_SPECIFICATION.md)
- [Plugin Security](PLUGIN_SECURITY.md)
- [Plugin SDK](PLUGIN_SDK.md)
- [Plugin Developer Guide](PLUGIN_DEVELOPER_GUIDE.md)

---

*End of document.*
