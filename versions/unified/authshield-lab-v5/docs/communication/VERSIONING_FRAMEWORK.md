# Versioning Framework

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

AuthShield Lab uses semantic versioning (SemVer) across all public surfaces. This framework defines compatibility rules, migration processes, and negotiation protocols to ensure smooth upgrades and plugin compatibility.

### 1.1 Versioned Surfaces

| Surface | Versioned Independently | Example |
|---------|------------------------|---------|
| Platform Release | Yes | `1.0.0` |
| SDK API | Yes | `1.0.0` |
| REST API | Yes (via URL prefix) | `/api/v1/`, `/api/v2/` |
| Event Schemas | Yes (via event version) | `1.0`, `1.1`, `2.0` |
| IPC Messages | Internal only | No external contract |
| Plugin Manifest | Yes | `1.0.0` |
| Configuration Schema | Yes | `1.0.0` |

---

## 2. Semantic Versioning

### 2.1 Format

```
MAJOR.MINOR.PATCH
```

| Component | Increment When |
|-----------|---------------|
| MAJOR | Breaking changes to public interfaces |
| MINOR | Backward-compatible new features |
| PATCH | Backward-compatible bug fixes |

### 2.2 Pre-Release Identifiers

```
MAJOR.MINOR.PATCH-PRERELEASE.N
```

| Prerelease | Meaning |
|------------|---------|
| `alpha` | Early development, API unstable |
| `beta` | Feature complete, API may change |
| `rc` | Release candidate, API frozen |

Examples: `1.0.0-alpha.1`, `1.0.0-beta.3`, `1.0.0-rc.1`

### 2.3 Version Ordering

```
1.0.0-alpha.1 < 1.0.0-alpha.2 < 1.0.0-beta.1 < 1.0.0-beta.3
< 1.0.0-rc.1 < 1.0.0 < 1.0.1 < 1.1.0 < 2.0.0
```

---

## 3. Backward Compatibility Rules

### 3.1 Minor Version Compatibility

Minor version increments MUST be backward compatible:

| Change Type | Allowed in Minor | Example |
|-------------|-----------------|---------|
| New optional parameter | Yes | `get_course(include_lessons=False)` |
| New return field | Yes | Response includes new `category` field |
| New enum value | Yes | New difficulty level `expert` added |
| New event type | Yes | `course.reviewed` event added |
| New SDK method | Yes | `get_analytics_summary()` added |
| New API endpoint | Yes | `GET /api/v1/analytics/summary` added |
| New configuration key | Yes | `security.lockout_duration` added |

### 3.2 Patch Version Compatibility

Patch version increments MUST be backward compatible AND behavior-preserving:

| Change Type | Allowed in Patch | Example |
|-------------|-----------------|---------|
| Bug fix | Yes | Fix incorrect progress calculation |
| Documentation | Yes | Updated API docs |
| Performance | Yes | Optimized database query |
| Security fix | Yes | Patched authentication bypass |
| Internal refactoring | Yes | No public behavior change |

### 3.3 Breaking Changes (Major Only)

The following changes REQUIRE a major version increment:

| Change Type | Description | Migration Required |
|-------------|-------------|-------------------|
| Parameter removal | Existing parameter removed | Yes |
| Parameter rename | Existing parameter renamed | Yes |
| Type change | Parameter/return type changed | Yes |
| Return field removal | Existing return field removed | Yes |
| Behavior change | Existing behavior modified | Yes |
| Error code removal | Existing error code retired | Yes |
| Event type removal | Existing event type removed | Yes |
| Event payload change | Required field removed/renamed | Yes |
| API endpoint removal | Endpoint removed | Yes |
| Authentication change | Auth mechanism changed | Yes |

### 3.4 Compatibility Decision Tree

```
Is this a new feature?
├── Yes → Is it backward compatible?
│   ├── Yes → Minor version bump
│   └── No  → Major version bump
└── No (bug fix or patch)
    ├── Does behavior change? → Major version bump
    └── Does behavior stay same? → Patch version bump
```

---

## 4. Forward Compatibility

### 4.1 Client Forward Compatibility

All clients (plugins, REST API consumers) MUST handle unknown fields gracefully:

```python
class ForwardCompatibleParser:
    def parse(self, data: dict) -> ParsedResult:
        """Parse response, ignoring unknown fields."""
        known_fields = {f.name for f in self.fields}
        unknown_fields = {k: v for k, v in data.items() if k not in known_fields}
        
        if unknown_fields:
            logger.debug(f"Ignoring unknown fields: {list(unknown_fields.keys())}")
        
        return self._extract_known(data)
```

### 4.2 Server Forward Compatibility

Servers MUST NOT reject requests containing unknown fields:

```python
class ForwardCompatibleValidator:
    def validate(self, data: dict) -> ValidationResult:
        """Validate request, allowing unknown fields."""
        errors = []
        for field in self.required_fields:
            if field.name not in data:
                errors.append(f"Missing required field: {field.name}")
        
        # Unknown fields are ignored, not rejected
        return ValidationResult(valid=len(errors) == 0, errors=errors)
```

### 4.3 Forward Compatibility Guarantees

| Guarantee | Description |
|-----------|-------------|
| Unknown fields ignored | Clients/servers ignore unrecognized fields |
| New enum values accepted | Clients accept new enum values they don't know |
| New event types ignored | Subscribers ignore event types they don't handle |
| Optional fields remain optional | New fields in responses are always optional |
| Default values provided | New parameters always have default values |

---

## 5. SDK Compatibility Matrix

### 5.1 Compatibility Table

| SDK Version | Platform 1.0.x | Platform 1.1.x | Platform 1.2.x | Platform 2.0.x |
|------------|----------------|----------------|----------------|----------------|
| SDK 1.0.0  | Full           | Full           | Full           | Partial        |
| SDK 1.1.0  | N/A            | Full           | Full           | Partial        |
| SDK 1.2.0  | N/A            | N/A            | Full           | Partial        |
| SDK 2.0.0  | N/A            | N/A            | N/A            | Full           |

**Legend:** Full = Fully compatible, Partial = Forward compatible (some features unavailable), N/A = Not applicable

### 5.2 SDK Compatibility Rules

| Rule | Description |
|------|-------------|
| Same major version | Full compatibility guaranteed |
| SDK ≤ Platform | Full compatibility (backward compatible) |
| SDK > Platform | Forward compatible; new features unavailable |
| Plugin min SDK ≤ Platform SDK | Plugin can load |
| Plugin max SDK < Platform SDK | Plugin cannot load (version too low) |

### 5.3 SDK Version Check Flow

```
Plugin declares: sdk_version_min="1.0.0", sdk_version_max="2.0.0"
Platform SDK version: 1.5.0

1. Check: 1.5.0 >= 1.0.0? → Yes (meets minimum)
2. Check: 1.5.0 <= 2.0.0? → Yes (within maximum)
3. Result: Plugin is compatible → Load plugin
```

---

## 6. Plugin Compatibility Matrix

### 6.1 Compatibility States

| State | Meaning | User Action |
|-------|---------|-------------|
| `compatible` | Fully compatible | None needed |
| `forward_compatible` | Plugin newer than platform | Upgrade platform recommended |
| `backward_compatible` | Platform newer than plugin | Upgrade plugin recommended |
| `incompatible` | Major version mismatch | Must update before use |
| `unknown` | Cannot determine compatibility | Manual verification needed |

### 6.2 Plugin Manifest Version Fields

```json
{
  "id": "example-plugin",
  "version": "1.2.3",
  "sdk_version_min": "1.0.0",
  "sdk_version_max": "1.99.99",
  "platform_version_min": "1.0.0",
  "platform_version_max": "1.99.99",
  "python_version_min": "3.12"
}
```

### 6.3 Plugin Upgrade Scenarios

| Scenario | Impact | Migration |
|----------|--------|-----------|
| Plugin minor bump | New features available | Automatic |
| Plugin major bump | Breaking changes in plugin API | Plugin provides migration guide |
| Platform minor bump | New SDK features available | Plugin can optionally use new features |
| Platform major bump | SDK breaking changes | Plugin must update for new SDK |

---

## 7. IPC Compatibility

### 7.1 Internal Nature

IPC messages are internal to the platform. No external compatibility guarantees are provided.

### 7.2 Internal Versioning Rules

| Rule | Description |
|------|-------------|
| Same release | All IPC messages are compatible |
| Patch release | IPC messages are compatible |
| Minor release | New message types may be added; existing unchanged |
| Major release | IPC format may change entirely |

### 7.3 IPC Migration

Since IPC is internal, migration happens automatically during platform upgrades. No manual migration is required.

---

## 8. API Versioning

### 8.1 REST API Versioning

REST API versions are managed through URL path prefixes:

```
/api/v1/users    (current stable)
/api/v2/users    (next version, if applicable)
```

### 8.2 API Version Lifecycle

```
Development → Beta → Current → Deprecated → Sunset → Removed
     │           │         │           │          │         │
     │           │         │           │          │         │
  Internal    Preview   Stable    Warning    Limited   Gone
              period    release   period     period
```

### 8.3 API Version Overlap

When a new API version is introduced:

| Phase | Duration | v1 Status | v2 Status |
|-------|----------|-----------|-----------|
| Introduction | 3 months | Current | Beta |
| Coexistence | 6 months | Current | Current |
| Deprecation | 6 months | Deprecated | Current |
| Sunset | 3 months | Sunset | Current |
| Removal | After sunset | Removed | Current |

---

## 9. Event Versioning

### 9.1 Event Schema Versioning

Events use a two-part version (`major.minor`):

```json
{
  "type": "course.published",
  "version": "1.0",
  "payload": { ... }
}
```

### 9.2 Event Version Rules

| Change | Version Action | Subscriber Impact |
|--------|---------------|-------------------|
| New optional field | Minor bump (1.0 → 1.1) | None (forward compatible) |
| New event type | None (new type) | None |
| Field removed | Major bump (1.x → 2.0) | Must update handler |
| Field renamed | Major bump (1.x → 2.0) | Must update handler |
| Field type changed | Major bump (1.x → 2.0) | Must update handler |

### 9.3 Event Subscriber Version Declaration

Subscribers declare which event version they support:

```python
@subscribe("course.published", version="<2.0")
async def handle_course_published(event: Event):
    """Handle course published events (version 1.x)."""
    ...
```

---

## 10. API Deprecation Process

### 10.1 Deprecation Workflow

```
1. Identify API element for deprecation
2. Add deprecation notice in documentation
3. Add deprecation headers to responses
4. Log deprecation warnings on usage
5. Wait minimum 2 minor versions
6. Remove in next major version
```

### 10.2 Deprecation Notice Requirements

| Artifact | Notice |
|----------|--------|
| OpenAPI spec | `deprecated: true` flag |
| Response headers | `Deprecation`, `Sunset`, `Link` headers |
| Log entries | `SDK-DEP-001` warning logged |
| Documentation | Deprecation notice with migration guide |
| Release notes | Deprecation announced in changelog |

### 10.3 Minimum Deprecation Period

| Version Type | Minimum Notice |
|-------------|---------------|
| Minor version deprecation | 2 minor versions (e.g., deprecated in 1.3, removed in 2.0) |
| Patch version deprecation | 2 patch versions (rare; only for bugs) |
| Emergency deprecation | 1 minor version (security critical only) |

### 10.4 Deprecation Tracking

```python
@dataclass
class DeprecationRecord:
    api_element: str        # e.g., "POST /api/v1/users/import"
    deprecated_in: str      # e.g., "1.3.0"
    removal_version: str    # e.g., "2.0.0"
    replacement: str | None # e.g., "POST /api/v2/users/import"
    reason: str             # e.g., "Replaced by batch import endpoint"
    migration_guide: str    # URL or markdown content
    usage_count: int        # How many consumers still use it
    last_used: str | None   # Last time it was called
```

---

## 11. Migration Guidance

### 11.1 Migration Guide Structure

Every breaking change includes a migration guide:

```markdown
## Migration: [Feature Name]

### What Changed
Description of the breaking change.

### Why It Changed
Reason for the change.

### Before (v1.x)
```python
# Old API usage
result = old_method(param="value")
```

### After (v2.0)
```python
# New API usage
result = new_method(parameter="value")
```

### Step-by-Step Migration
1. Update import statements
2. Rename parameter `param` → `parameter`
3. Update return type handling
4. Test with new API

### Automated Migration
Run the migration script:
```bash
authshield migrate --from 1.x --to 2.0
```

### Timeline
- Deprecated: v1.3.0
- Warning: v1.4.0 - v1.9.x
- Removed: v2.0.0
```

### 11.2 Migration Script Support

For major version upgrades, the platform provides automated migration scripts:

```bash
# Check what needs migration
authshield migrate --check --from 1.x --to 2.0

# Run migration (dry run)
authshield migrate --dry-run --from 1.x --to 2.0

# Run migration
authshield migrate --from 1.x --to 2.0

# Rollback migration
authshield migrate --rollback --from 2.0 --to 1.x
```

### 11.3 Migration Checklist

| Step | Description | Required |
|------|-------------|----------|
| 1 | Review changelog for breaking changes | Yes |
| 2 | Update plugin manifest SDK version range | Yes |
| 3 | Update deprecated API calls | If applicable |
| 4 | Update event handlers for new schemas | If applicable |
| 5 | Update error handling for new error codes | If applicable |
| 6 | Run migration script | If applicable |
| 7 | Run test suite | Yes |
| 8 | Verify plugin functionality | Yes |
| 9 | Update documentation references | If applicable |

---

## 12. Version Negotiation Protocol

### 12.1 Plugin Installation Negotiation

```
1. Plugin declares version requirements in manifest
2. Platform reads plugin manifest
3. Platform checks SDK version compatibility
4. Platform checks Python version compatibility
5. Platform checks platform version compatibility
6. If all checks pass → Install plugin
7. If any check fails → Reject with detailed error
```

### 12.2 Runtime Version Negotiation

```
1. Plugin calls SDK method
2. SDK checks method exists in current SDK version
3. If method exists → Execute and return result
4. If method does not exist → Return SDKVersionMismatchError
5. Plugin handles error or falls back to alternative method
```

### 12.3 REST API Version Negotiation

```
1. Client sends request to /api/v1/... or /api/v2/...
2. Server routes to versioned handler
3. If version exists → Process request
4. If version does not exist → Return 404 or redirect to current version
5. If version deprecated → Add deprecation headers
```

### 12.4 Version Header

Clients can include version preference in requests:

```http
Accept-Version: v1.5
X-Platform-Version: 1.5.0
X-SDK-Version: 1.5.0
```

### 12.5 Version Response Headers

All API responses include version information:

```http
X-API-Version: v1
X-Platform-Version: 1.5.0
X-SDK-Version: 1.5.0
X-Deprecated: false
```

---

## 13. Versioning Governance

### 13.1 Version Committee

| Role | Responsibility |
|------|---------------|
| Lead Architect | Final decision on version bumps |
| SDK Maintainer | SDK compatibility review |
| API Maintainer | REST API compatibility review |
| Plugin Liaison | Plugin ecosystem impact assessment |

### 13.2 Version Review Process

```
1. Propose change with version impact analysis
2. Committee reviews compatibility implications
3. Committee assigns version bump
4. Migration guide drafted
5. Deprecation timeline published
6. Change implemented
7. Change released
```

### 13.3 Exception Process

Emergency changes (security patches) may bypass normal versioning:

| Exception Type | Requirement |
|---------------|-------------|
| Security patch | Minimum 1 minor version notice |
| Data loss prevention | Immediate patch release |
| Compliance requirement | As required by regulation |

---

## 14. Versioning Tools

### 14.1 Version Check Commands

```bash
# Check platform version
authshield --version

# Check SDK compatibility
authshield sdk check --plugin ./my-plugin

# Check all plugins compatibility
authshield plugins check-compatibility

# Generate compatibility report
authshield plugins compatibility-report --output report.json
```

### 14.2 Version Validation in CI/CD

```yaml
# Example CI/CD version validation
version_check:
  steps:
    - name: Check SDK version range
      run: |
        python -c "
        from authshield.sdk.compat import check_compatibility
        result = check_compatibility('1.5.0', '1.0.0', '2.0.0')
        assert result.compatible, f'Incompatible: {result.reason}'
        "
    
    - name: Validate OpenAPI spec
      run: openapi-spec-validator openapi.json
    
    - name: Check for breaking changes
      run: openapi-diff --fail-on-incompatible old.json new.json
```
