# Identity Management Architecture

## User Lifecycle

The identity system manages users through a comprehensive lifecycle state machine that tracks every transition from anonymous browsing to account deletion.

### Lifecycle States

| State | Description |
|-------|-------------|
| `anonymous` | Unauthenticated visitor |
| `registered` | Account created, pending verification |
| `pending_verification` | Email verification required |
| `active` | Fully verified and active |
| `authenticated` | Currently authenticating |
| `active_session` | Has an active session |
| `idle` | Session exists but inactive |
| `logged_out` | Explicitly logged out |
| `locked` | Temporarily locked (failed attempts) |
| `disabled` | Admin-disabled account |
| `suspended` | Suspended for policy violation |
| `password_reset_required` | Must reset password |
| `archived` | Inactive, soft-deleted |
| `deleted` | Permanently removed |

### Valid Transitions

The lifecycle enforces strict state machine rules:

- `anonymous` -> `registered` (registration)
- `registered` -> `active` or `pending_verification`
- `active` -> `authenticated`, `locked`, `disabled`, `suspended`, `archived`, `deleted`
- `locked` -> `active` (unlocking), `disabled`, `deleted`
- `disabled` -> `active` (re-enabling), `archived`, `deleted`
- `deleted` -> (no transitions, terminal state)

Invalid transitions raise `ValueError` with detailed error messages listing allowed targets.

## Role Architecture

Roles are named permission groups that define authorization boundaries. The system uses a hierarchical role model with built-in roles and custom role support.

### Built-in Roles

| Role | Description | Key Permissions |
|------|-------------|-----------------|
| `student` | Default role for learners | `labs.execute`, `progress.view`, `profile.edit` |
| `instructor` | Teaching role | All student permissions + `labs.create`, `students.view` |
| `admin` | Full administration | All permissions |
| `developer` | API and integration access | `api.access`, `logs.view`, `config.edit` |

### Role Entity

```python
@dataclass
class RoleEntity:
    role_id: str
    name: str
    display_name: str
    description: str
    is_builtin: bool
    is_active: bool
    version: int
    permissions: list[str]
    created_at: datetime
```

### Role Assignment Flow

1. Admin creates or selects a role
2. Role is associated with user via `user_roles` association table
3. Role permissions are resolved via `role_permissions` association table
4. AuthorizationEngine evaluates permission sets for access decisions

## Permission Model

Permissions are granular access controls organized by category. Each permission follows a `resource.action` naming convention.

### Permission Categories

| Category | Example Permissions |
|----------|-------------------|
| `users` | `users.read`, `users.write`, `users.delete` |
| `sessions` | `sessions.read`, `sessions.manage` |
| `labs` | `labs.execute`, `labs.create`, `labs.configure` |
| `admin` | `admin.manage`, `admin.users`, `admin.system` |
| `audit` | `audit.read`, `audit.export` |
| `reports` | `reports.view`, `reports.create` |
| `defenses` | `defenses.manage`, `policies.read` |

### Permission Entity

```python
@dataclass
class PermissionEntity:
    permission_id: str
    name: str           # "users.read"
    display_name: str
    description: str
    category: str       # "users"
    is_active: bool
    created_at: datetime
```

Permissions can be created from dot-separated strings via `PermissionEntity.from_string("users.read")`.

## Session Management

Sessions are created upon successful authentication and tracked throughout their lifecycle.

### Session Properties

| Property | Description |
|----------|-------------|
| `session_id` | UUID v4 identifier |
| `user_id` | Foreign key to users table |
| `expires_at` | Absolute expiry timestamp |
| `last_activity` | Last recorded activity time |
| `idle_timeout_minutes` | Idle timeout (default: 30) |
| `status` | active, idle, expired, revoked, terminated, invalid |
| `authentication_method` | Password, token, etc. |
| `platform` | Client platform |
| `device_id` | Associated device |
| `ip_address` | Client IP |
| `remember_me` | Extended session flag |
| `security_level` | Trust level (1-5) |

### Session Properties

- `is_expired`: True if current time > expires_at
- `is_active`: True if status is "active" and not expired
- `is_idle`: True if idle_time > idle_timeout_minutes
- `idle_time_minutes`: Minutes since last activity

## Device Management

The device tracking system maintains a registry of client devices that have authenticated against the platform.

### Device Properties

| Property | Description |
|----------|-------------|
| `device_id` | Unique device identifier |
| `friendly_name` | User-assigned name |
| `platform` | OS platform (linux, windows, macos) |
| `operating_system` | Full OS version string |
| `application_version` | Client app version |
| `is_trusted` | Whether device is trusted |
| `is_active` | Whether device record is active |
| `risk_level` | low, medium, high |
| `last_seen` | Last authentication timestamp |
| `session_count` | Total sessions from this device |

## Preferences Engine

User preferences are stored in the `UserPreference` model with support for:

- **Theme**: light, dark, high_contrast, solarized, monokai
- **Accessibility**: high_contrast, reduced_motion, font_size, dyslexia_font, screen_reader_optimized
- **Notifications**: enabled, sound
- **Developer**: developer_mode
- **Privacy**: analytics_enabled
- **Custom**: JSON field for user-defined preferences

## Authorization Foundation

The authorization system combines role-based access control (RBAC) with policy-based evaluation:

1. **Permission Registry**: Centralized catalog of all permissions
2. **Role Resolution**: Map user roles to permission sets
3. **AuthorizationEngine**: Evaluate permission requirements
4. **Policy Engine**: Dynamic policies for advanced access control

### Authorization Flow

```
API Request
    │
    ▼
Extract User Context
    │
    ▼
Resolve User Roles ──► Role Table
    │
    ▼
Resolve Permissions ──► Permission Table
    │
    ▼
Evaluate AuthorizationPolicy
    │
    ├─► ALLOW ──► Proceed
    └─► DENY ──► 403 Response
```

The current implementation evaluates policies synchronously. Future versions will support async policy evaluation with caching.
