# AuthShield Lab — Plugin Manifest Specification

> **Version:** 1.0.0
> **Status:** Authoritative
> **Schema File:** `manifest.schema.json`

---

## 1. Overview

Every AuthShield Lab plugin **must** include a `manifest.json` file at the root of its
package directory. This manifest declares the plugin's identity, capabilities, permissions,
dependencies, and compatibility constraints.

The manifest is parsed and validated by the kernel during the Discovery and Validation
stages of the plugin lifecycle.

---

## 2. Schema Definition

The complete JSON Schema for `manifest.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://authshieldlab.dev/schemas/plugin-manifest-v1.json",
  "title": "AuthShield Lab Plugin Manifest",
  "description": "Schema for AuthShield Lab plugin manifest.json files.",
  "type": "object",
  "required": [
    "plugin_id",
    "name",
    "description",
    "author",
    "version",
    "min_platform_version",
    "license",
    "type",
    "entry_point"
  ],
  "properties": {
    "plugin_id": {
      "type": "string",
      "pattern": "^[a-z0-9][a-z0-9\\-]{1,62}[a-z0-9]$",
      "description": "Unique reverse-DNS or kebab-case identifier for the plugin."
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128,
      "description": "Human-readable display name."
    },
    "description": {
      "type": "string",
      "minLength": 10,
      "maxLength": 2048,
      "description": "Short description of the plugin's purpose."
    },
    "author": {
      "type": "object",
      "required": ["name"],
      "properties": {
        "name": { "type": "string", "minLength": 1, "maxLength": 256 },
        "email": { "type": "string", "format": "email" },
        "url": { "type": "string", "format": "uri" },
        "organization": { "type": "string", "maxLength": 256 }
      },
      "additionalProperties": false
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+(-[a-zA-Z0-9.]+)?(\\+[a-zA-Z0-9.]+)?$",
      "description": "Semantic Version (SemVer 2.0.0)."
    },
    "min_platform_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Minimum platform version required."
    },
    "max_platform_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Maximum platform version supported (optional)."
    },
    "license": {
      "type": "string",
      "description": "SPDX license identifier (e.g. 'MIT', 'Apache-2.0', 'Proprietary')."
    },
    "type": {
      "type": "string",
      "enum": [
        "feature",
        "educational-content",
        "course-package",
        "assessment-pack",
        "localization-pack",
        "accessibility-profile",
        "reporting-template",
        "theme",
        "sdk-extension",
        "institution-config",
        "example"
      ],
      "description": "Plugin type."
    },
    "entry_point": {
      "type": "string",
      "description": "Dotted Python path to the plugin class (e.g. 'src.plugin:MyPlugin')."
    },
    "organization": {
      "type": "object",
      "properties": {
        "name": { "type": "string", "maxLength": 256 },
        "url": { "type": "string", "format": "uri" }
      },
      "additionalProperties": false
    },
    "capabilities": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-z][a-z0-9\\-]*(\\.[a-z][a-z0-9\\-]*)*$"
      },
      "uniqueItems": true,
      "description": "List of capabilities this plugin requires."
    },
    "permissions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["permission"],
        "properties": {
          "permission": {
            "type": "string",
            "description": "Permission identifier (e.g. 'storage:rw', 'ui:panel')."
          },
          "reason": {
            "type": "string",
            "maxLength": 512,
            "description": "Justification for the permission."
          },
          "scope": {
            "type": "string",
            "description": "Optional scope limitation."
          }
        },
        "additionalProperties": false
      },
      "description": "Explicit permissions requested by the plugin."
    },
    "dependencies": {
      "type": "object",
      "additionalProperties": {
        "type": "string",
        "description": "Version constraint (SemVer range)."
      },
      "description": "Required dependencies (plugin_id → version range)."
    },
    "optional_dependencies": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      },
      "description": "Optional dependencies (plugin_id → version range)."
    },
    "supported_languages": {
      "type": "array",
      "items": { "type": "string", "pattern": "^[a-z]{2}(-[A-Z]{2})?$" },
      "description": "ISO 639-1 / BCP 47 locale codes supported."
    },
    "accessibility_metadata": {
      "type": "object",
      "properties": {
        "wcag_level": {
          "type": "string",
          "enum": ["A", "AA", "AAA"],
          "description": "WCAG conformance level claimed."
        },
        "keyboard_only": {
          "type": "boolean",
          "description": "Fully usable with keyboard only."
        },
        "screen_reader_tested": {
          "type": "boolean",
          "description": "Tested with major screen readers."
        },
        "high_contrast": {
          "type": "boolean",
          "description": "Compatible with high contrast modes."
        },
        "reduced_motion": {
          "type": "boolean",
          "description": "Respects prefers-reduced-motion."
        },
        "font_scaling": {
          "type": "boolean",
          "description": "Supports up to 200% font scaling."
        },
        "notes": {
          "type": "string",
          "maxLength": 1024,
          "description": "Additional accessibility notes."
        }
      },
      "additionalProperties": false
    },
    "localization_metadata": {
      "type": "object",
      "properties": {
        "base_locale": {
          "type": "string",
          "default": "en",
          "description": "Base locale of the plugin content."
        },
        "translation_dirs": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Relative paths to directories containing .json translation files."
        },
        "rtl_support": {
          "type": "boolean",
          "description": "Supports right-to-left layouts."
        }
      },
      "additionalProperties": false
    },
    "integrity_metadata": {
      "type": "object",
      "properties": {
        "checksum_algorithm": {
          "type": "string",
          "enum": ["sha256", "sha512"],
          "default": "sha256"
        },
        "checksum_file": {
          "type": "string",
          "default": "integrity.json",
          "description": "Relative path to checksum manifest."
        }
      },
      "additionalProperties": false
    },
    "signature_metadata": {
      "type": "object",
      "properties": {
        "algorithm": {
          "type": "string",
          "enum": ["gpg", "x509"],
          "description": "Signing algorithm."
        },
        "signature_file": {
          "type": "string",
          "default": "signature.p7s",
          "description": "Relative path to signature file."
        },
        "key_id": {
          "type": "string",
          "description": "Identifier of the signing key."
        }
      },
      "additionalProperties": false
    },
    "documentation_references": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["title", "path"],
        "properties": {
          "title": { "type": "string", "maxLength": 256 },
          "path": { "type": "string", "description": "Relative path within the plugin package." }
        }
      },
      "description": "References to documentation files."
    },
    "tags": {
      "type": "array",
      "items": { "type": "string", "maxLength": 64 },
      "description": "Searchable tags for plugin discovery."
    },
    "icon": {
      "type": "string",
      "description": "Relative path to plugin icon (PNG, 128x128 recommended)."
    },
    "homepage": {
      "type": "string",
      "format": "uri",
      "description": "Plugin homepage URL."
    },
    "repository": {
      "type": "string",
      "format": "uri",
      "description": "Source code repository URL."
    }
  },
  "additionalProperties": false
}
```

---

## 3. Required Fields — Detailed Validation

### 3.1 `plugin_id`

- **Type:** `string`
- **Pattern:** `^[a-z0-9][a-z0-9\-]{1,62}[a-z0-9]$`
- **Length:** 3–64 characters.
- **Rules:**
  - Must be globally unique within the platform installation.
  - Must use lowercase kebab-case (e.g. `threat-dashboard`, `lab-simulator`).
  - Must not start or end with a hyphen.
  - Must not collide with kernel-internal IDs (prefixed `kernel.*`).

### 3.2 `name`

- **Type:** `string`
- **Length:** 1–128 characters.
- **Rules:**
  - Must be non-empty.
  - May contain Unicode characters.
  - Used for display in the UI.

### 3.3 `description`

- **Type:** `string`
- **Length:** 10–2048 characters.
- **Rules:**
  - Must be at least 10 characters.
  - Should clearly describe what the plugin does.
  - Used in plugin marketplace listings and UI tooltips.

### 3.4 `author`

- **Type:** `object`
- **Required sub-field:** `name` (1–256 characters).
- **Optional sub-fields:** `email`, `url`, `organization`.
- **Rules:**
  - `email` must be a valid email format.
  - `url` must be a valid URI.

### 3.5 `version`

- **Type:** `string`
- **Pattern:** SemVer 2.0.0.
- **Rules:**
  - Must be a valid SemVer string.
  - Pre-release versions (e.g. `1.0.0-beta.1`) are allowed.
  - Build metadata (e.g. `1.0.0+build.42`) is allowed but ignored for comparison.

### 3.6 `min_platform_version`

- **Type:** `string`
- **Pattern:** `^\d+\.\d+\.\d+$`
- **Rules:**
  - Must be a valid version string.
  - The kernel must be at least this version for the plugin to load.

### 3.7 `license`

- **Type:** `string`
- **Rules:**
  - Should be an SPDX license identifier.
  - Common values: `MIT`, `Apache-2.0`, `BSD-3-Clause`, `Proprietary`.
  - The kernel does not enforce license compatibility but displays the license in the UI.

### 3.8 `type`

- **Type:** `string`
- **Allowed values:** See schema enum (11 types).
- **Rules:**
  - Must be one of the enumerated plugin types.
  - Determines loading strategy and available capabilities.

### 3.9 `entry_point`

- **Type:** `string`
- **Rules:**
  - Dotted Python path relative to the plugin's `src/` directory.
  - Format: `module.path:ClassName`.
  - The class must subclass `PluginBase`.

---

## 4. Optional Fields — Detailed Validation

### 4.1 `max_platform_version`

- Same format as `min_platform_version`.
- If omitted, no upper bound on platform version.
- Must be ≥ `min_platform_version`.

### 4.2 `capabilities`

- Array of dot-separated lowercase identifiers (e.g. `ui:panel`, `storage:rw`).
- Must be non-empty if declared.
- All declared capabilities must be recognized by the kernel.
- Unrecognized capabilities cause a validation warning (non-fatal).

### 4.3 `permissions`

- Each entry has a `permission` string, optional `reason`, and optional `scope`.
- Permissions are checked at runtime by the sandbox.
- Declaring a permission the plugin never uses is harmless but discouraged.

### 4.4 `dependencies`

- Keys are plugin IDs; values are SemVer range strings (e.g. `^1.0.0`, `>=2.0.0 <3.0.0`).
- Required dependencies must be installed and compatible for the plugin to load.

### 4.5 `optional_dependencies`

- Same format as `dependencies`.
- If present, the plugin loads with reduced functionality.

### 4.6 `supported_languages`

- Array of BCP 47 locale codes (e.g. `en`, `de-DE`, `fr`).
- If omitted, only the base locale is supported.

### 4.7 `accessibility_metadata`

- Declares WCAG conformance level and accessibility features.
- Used by the platform to filter and display accessibility information.

### 4.8 `localization_metadata`

- `base_locale`: the locale of the plugin's source strings (default: `en`).
- `translation_dirs`: relative paths to directories containing translation JSON files.
- `rtl_support`: whether the plugin supports right-to-left layouts.

### 4.9 `integrity_metadata`

- `checksum_algorithm`: hash algorithm (default: `sha256`).
- `checksum_file`: path to the integrity manifest (default: `integrity.json`).

### 4.10 `signature_metadata`

- `algorithm`: signing algorithm (`gpg` or `x509`).
- `signature_file`: path to the signature (default: `signature.p7s`).
- `key_id`: identifier of the signing key (used for trust verification).

### 4.11 `documentation_references`

- Array of `{ title, path }` objects.
- `path` is relative to the plugin package root.
- Used by the platform to display plugin documentation.

---

## 5. Example Manifest

```json
{
  "plugin_id": "threat-dashboard",
  "name": "Threat Dashboard",
  "description": "A real-time threat visualization dashboard for defensive monitoring and educational demonstration of network threat patterns.",
  "author": {
    "name": "AuthShield Lab Team",
    "email": "plugins@authshieldlab.dev",
    "url": "https://authshieldlab.dev",
    "organization": "AuthShield Lab"
  },
  "version": "1.2.0",
  "min_platform_version": "1.0.0",
  "max_platform_version": "3.99.99",
  "license": "Apache-2.0",
  "type": "feature",
  "entry_point": "src.plugin:ThreatDashboardPlugin",
  "organization": {
    "name": "AuthShield Lab",
    "url": "https://authshieldlab.dev"
  },
  "capabilities": [
    "ui:panel",
    "ui:toolbar",
    "event:subscribe",
    "event:publish",
    "storage:rw",
    "commands:register"
  ],
  "permissions": [
    {
      "permission": "storage:rw",
      "reason": "Store dashboard layout preferences and cached threat data.",
      "scope": "threat-dashboard"
    },
    {
      "permission": "ui:panel",
      "reason": "Display the main threat visualization panel."
    }
  ],
  "dependencies": {
    "core-data-service": "^1.0.0"
  },
  "optional_dependencies": {
    "notification-center": "^1.0.0"
  },
  "supported_languages": ["en", "de-DE", "fr", "ja-JP"],
  "accessibility_metadata": {
    "wcag_level": "AA",
    "keyboard_only": true,
    "screen_reader_tested": true,
    "high_contrast": true,
    "reduced_motion": true,
    "font_scaling": true,
    "notes": "All charts have text alternatives."
  },
  "localization_metadata": {
    "base_locale": "en",
    "translation_dirs": ["localization/"],
    "rtl_support": false
  },
  "integrity_metadata": {
    "checksum_algorithm": "sha256",
    "checksum_file": "integrity.json"
  },
  "signature_metadata": {
    "algorithm": "x509",
    "signature_file": "signature.p7s",
    "key_id": "authshield-lab-prod-key-2026"
  },
  "documentation_references": [
    { "title": "User Guide", "path": "docs/user-guide.md" },
    { "title": "API Reference", "path": "docs/api-reference.md" }
  ],
  "tags": ["threats", "visualization", "dashboard", "real-time"],
  "icon": "assets/icon-128.png",
  "homepage": "https://authshieldlab.dev/plugins/threat-dashboard",
  "repository": "https://github.com/authshieldlab/threat-dashboard"
}
```

---

## 6. Schema File: manifest.schema.json

The JSON Schema file is distributed with the platform SDK at:

```
<platform_root>/schemas/manifest.schema.json
```

Plugin developers may reference this schema in their `manifest.json` using:

```json
{
  "$schema": "https://authshieldlab.dev/schemas/plugin-manifest-v1.json",
  ...
}
```

---

## 7. Manifest Validation Rules Summary

| Field | Required | Type | Validation |
|---|---|---|---|
| `plugin_id` | Yes | string | Regex, unique, 3–64 chars |
| `name` | Yes | string | 1–128 chars |
| `description` | Yes | string | 10–2048 chars |
| `author` | Yes | object | `name` required |
| `version` | Yes | string | SemVer 2.0.0 |
| `min_platform_version` | Yes | string | Version format |
| `license` | Yes | string | SPDX identifier |
| `type` | Yes | string | Enum (11 values) |
| `entry_point` | Yes | string | `module:Class` format |
| `max_platform_version` | No | string | Version format, ≥ min |
| `organization` | No | object | `name` optional |
| `capabilities` | No | array | Dot-separated IDs |
| `permissions` | No | array | Objects with `permission` |
| `dependencies` | No | object | Plugin ID → SemVer range |
| `optional_dependencies` | No | object | Plugin ID → SemVer range |
| `supported_languages` | No | array | BCP 47 codes |
| `accessibility_metadata` | No | object | WCAG level + booleans |
| `localization_metadata` | No | object | Locale + dirs |
| `integrity_metadata` | No | object | Algorithm + file path |
| `signature_metadata` | No | object | Algorithm + file + key |
| `documentation_references` | No | array | `{ title, path }` objects |
| `tags` | No | array | Strings ≤ 64 chars |
| `icon` | No | string | Relative path |
| `homepage` | No | string | URI |
| `repository` | No | string | URI |

---

## 8. References

- [Plugin Architecture](PLUGIN_ARCHITECTURE.md)
- [Plugin Package Format](PLUGIN_PACKAGE_FORMAT.md)
- [Plugin SDK](PLUGIN_SDK.md)

---

*End of document.*
