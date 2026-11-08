# AuthShield Lab — Permission-Based Navigation

## 1. Overview

This document defines how navigation, screen visibility, and feature access are
controlled by user roles in AuthShield Lab. The permission system enforces
access at the routing level using React Router guards and provides graceful
degradation for unauthorized access attempts.

---

## 2. Role Definitions

### 2.1 Role Hierarchy

```
Institution Manager
  └── inherits → Administrator
        └── inherits → Instructor
              └── inherits → Student

Plugin Developer (parallel track)
System Operator (parallel track)
```

### 2.2 Role Descriptions

| Role | Description | Scope |
|---|---|---|
| Student | Learns content, takes assessments, runs simulations | Own data only |
| Instructor | Creates content, manages courses, views analytics | Own courses |
| Administrator | Manages users, system settings, plugins | System-wide |
| Institution Manager | Institution-wide oversight and configuration | Institution-wide |
| Plugin Developer | Creates, tests, and publishes plugins | Plugin ecosystem |
| System Operator | Monitors system health, manages backups | System operations |

---

## 3. Role: Student

### 3.1 Default Landing Screen

**Dashboard (Student View)** — `/dashboard`

### 3.2 Visible Screens

| Screen | Route | Access Level |
|---|---|---|
| Dashboard | `/dashboard` | Read, configure layout |
| Course Browser | `/courses/browse` | Read, enroll |
| Enrolled Courses | `/courses/enrolled` | Read |
| Completed Courses | `/courses/completed` | Read |
| Course Detail | `/courses/:id` | Read, enroll |
| Learning Workspace | `/learning/:courseId` | Read, interact |
| Lesson View | `/learning/:courseId/lesson/:id` | Read, interact, notes |
| Simulation Browser | `/simulations/browse` | Read, execute |
| Simulation Detail | `/simulations/:id` | Read, start |
| Simulation Workspace | `/simulations/:id/run` | Execute |
| Debrief | `/simulations/:id/debrief` | Read |
| Assessment Browser | `/assessments/browse` | Read |
| Assessment Detail | `/assessments/:id` | Read, take |
| Assessment Workspace | `/assessments/:id/take` | Take |
| Results | `/assessments/:id/results` | Read |
| Reports Dashboard | `/reports/dashboard` | Read (own) |
| Report Detail | `/reports/:id` | Read (own) |
| Certificate Gallery | `/certificates` | Read (own) |
| Certificate Detail | `/certificates/:id` | Read (own), download |
| Analytics Dashboard | `/analytics` | Read (own) |
| Settings (Personal) | `/settings/general` | Write |
| Settings (Appearance) | `/settings/appearance` | Write |
| Settings (Accessibility) | `/settings/accessibility` | Write |
| Settings (Localization) | `/settings/localization` | Write |
| Settings (Security) | `/settings/security` | Write (personal) |
| Settings (Privacy) | `/settings/privacy` | Write (personal) |
| Settings (Notifications) | `/settings/notifications` | Write |
| Settings (Learning) | `/settings/learning` | Write |
| Settings (Storage) | `/settings/storage` | Read |
| Help Center | `/help/center` | Read |
| Tutorials | `/help/tutorials` | Read |
| Keyboard Shortcuts | `/help/shortcuts` | Read |
| Troubleshooting | `/help/troubleshooting` | Read |
| FAQ | `/help/faq` | Read |
| About | `/help/about` | Read |

### 3.3 Restricted Features

| Feature | Restriction | Behavior |
|---|---|---|
| Course Creation | Hidden | Not visible in UI |
| Assessment Creation | Hidden | Not visible in UI |
| User Management | Hidden | Not visible in UI |
| System Settings | Hidden | Not visible in UI |
| Plugin Management | Hidden | Not visible in UI |
| Backup/Restore | Hidden | Not visible in UI |
| Diagnostics | Hidden | Not visible in UI |
| Admin Dashboard | Hidden | Not visible in nav |
| Cross-user Reports | Hidden | Cannot access |
| Other Users' Certificates | Hidden | Cannot access |

### 3.4 Navigation Configuration

```
Primary Navigation:
  ├── Dashboard (Alt+1)
  ├── Courses (Alt+2)
  ├── Simulations (Alt+3)
  ├── Assessments (Alt+4)
  ├── Reports (Alt+5)
  ├── Settings (Alt+6)
  └── Help (Alt+7)

Secondary Navigation (per module):
  Dashboard: Overview, Activity, Progress
  Courses: Browse, Enrolled, Completed, Bookmarks
  Simulations: Browse, History, Bookmarks
  Assessments: Browse, Available, Completed, Results
  Reports: Dashboard, My Reports
  Settings: General, Appearance, Accessibility, Localization, Security, Privacy, Notifications, Storage, Learning
  Help: Center, Tutorials, Shortcuts, Troubleshooting, FAQ, About
```

### 3.5 Route Guard

```typescript
const studentGuard: RouteGuard = {
  allowedRoutes: STUDENT_ROUTES,
  deniedRoutes: ADMIN_ROUTES.concat(INSTRUCTOR_ROUTES),
  fallbackRoute: '/dashboard',
  onDenied: 'redirect-to-dashboard'
};
```

---

## 4. Role: Instructor

### 4.1 Default Landing Screen

**Dashboard (Instructor View)** — `/dashboard`

### 4.2 Visible Screens (All Student screens plus)

| Screen | Route | Access Level |
|---|---|---|
| Course Management | `/admin/courses` | Create, edit, publish |
| Course Editor | `/admin/courses/:id/edit` | Full edit |
| Assessment Creator | `/admin/assessments/create` | Create, edit |
| Assessment Editor | `/admin/assessments/:id/edit` | Full edit |
| Student Analytics (per course) | `/analytics/course/:id` | Read |
| Assessment Analytics | `/analytics/assessment/:id` | Read |
| Course Reports | `/reports/course/:id` | Create, read |
| Student Management (enrolled) | `/admin/courses/:id/students` | Read, limited manage |
| Content Manager | `/admin/content` | Create, edit, delete |
| Grading Queue | `/admin/grading` | Grade, review |

### 4.3 Restricted Features

| Feature | Restriction | Behavior |
|---|---|---|
| User Account Management | Hidden | Cannot manage user accounts |
| Role Management | Hidden | Cannot change roles |
| System Settings | Hidden | Cannot access system config |
| Plugin Management | Hidden | Cannot install/remove plugins |
| Institution Settings | Hidden | Cannot configure institution |
| Cross-Course Analytics | Hidden | Only own course analytics |
| Backup/Restore | Hidden | Cannot manage backups |
| Audit Logs | Hidden | Cannot view system audit |
| Diagnostics | Hidden | Cannot run diagnostics |
| Other Instructors' Courses | Hidden | Cannot access |

### 4.4 Navigation Configuration

```
Primary Navigation:
  ├── Dashboard (Alt+1)
  ├── Courses (Alt+2)
  ├── Simulations (Alt+3)
  ├── Assessments (Alt+4)
  ├── Reports (Alt+5)
  ├── Settings (Alt+6)
  └── Help (Alt+7)

Additional Admin-Lite Items:
  ├── Course Management (in Courses secondary nav)
  ├── Assessment Creator (in Assessments secondary nav)
  └── Student Lists (in Course Detail)

Secondary Navigation Additions:
  Courses: + Manage, Create, Content
  Assessments: + Create, Grade, Queue
  Reports: + Course Reports, Create
  Analytics: + Course Analytics, Assessment Analytics
```

---

## 5. Role: Administrator

### 5.1 Default Landing Screen

**Dashboard (Admin View)** — `/dashboard`

### 5.2 Visible Screens (All Instructor screens plus)

| Screen | Route | Access Level |
|---|---|---|
| Admin Dashboard | `/admin` | Read |
| User Management | `/admin/users` | Create, edit, deactivate |
| User Detail | `/admin/users/:id` | Read, edit |
| User Create/Edit | `/admin/users/:id/edit` | Full |
| Role Management | `/admin/roles` | Create, edit, assign |
| Role Editor | `/admin/roles/:id/edit` | Full |
| Permission Matrix | `/admin/roles/permissions` | Read, edit |
| Organization Management | `/admin/organizations` | Create, edit |
| Audit Log | `/admin/audit` | Read |
| Institution Settings | `/admin/institution` | Write |
| Plugin Manager | `/plugins` | Install, configure, remove |
| Plugin Browser | `/plugins/browse` | Read, install |
| Plugin Detail | `/plugins/:id` | Read, configure |
| Plugin Configuration | `/plugins/:id/configure` | Write |
| Plugin Logs | `/plugins/:id/logs` | Read |
| Backup & Restore | `/settings/backup` | Create, restore |
| Diagnostics | `/diagnostics` | Read, run |
| System Health | `/diagnostics/health` | Read |
| Log Viewer | `/diagnostics/logs` | Read |
| Performance Monitor | `/diagnostics/performance` | Read |
| Crash Reports | `/diagnostics/crashes` | Read |
| Advanced Settings | `/settings/advanced` | Write |
| System Settings | `/settings/security` | Write |
| Administration Settings | `/settings/administration` | Write |

### 5.3 Restricted Features

| Feature | Restriction | Behavior |
|---|---|---|
| Institution Cross-Analytics | Read only | Can view but not configure |
| System Operator Tools | Read only | Cannot run system-level ops |
| Plugin Development | Read only | Cannot test or debug plugins |

### 5.4 Navigation Configuration

```
Primary Navigation (with admin items):
  ├── Dashboard (Alt+1)
  ├── Courses (Alt+2)
  ├── Simulations (Alt+3)
  ├── Assessments (Alt+4)
  ├── Reports (Alt+5)
  ├── Administration (Alt+8) ← Admin only
  ├── Plugins (Alt+9) ← Admin only
  ├── Diagnostics (Alt+0) ← Admin only
  ├── Settings (Alt+6)
  └── Help (Alt+7)

Secondary Navigation Additions:
  Administration: Overview, Users, Roles, Organizations, Audit, Institution, Policies
  Plugins: Installed, Browse, Updates, Developer, Logs, Settings
  Diagnostics: Health, Logs, Performance, Network, Database, Crashes
  Settings: + Security (system), Diagnostics, Advanced, Administration
```

---

## 6. Role: Institution Manager

### 6.1 Default Landing Screen

**Dashboard (Admin View)** — `/dashboard`

### 6.2 Visible Screens (All Administrator screens plus)

| Screen | Route | Access Level |
|---|---|---|
| Institution Settings | `/admin/institution` | Write |
| Cross-Course Analytics | `/analytics/cross-course` | Read |
| Institution Reports | `/reports/institution` | Create, read |
| User Administration | `/admin/users` | Full (institution scope) |
| Bulk User Operations | `/admin/users/bulk` | Execute |
| Institution Policies | `/admin/policies` | Create, edit |
| Institution Plugins | `/plugins` | Approve, configure |

### 6.3 Restricted Features

| Feature | Restriction | Behavior |
|---|---|---|
| System Diagnostics | Read only | Cannot run system-level diagnostics |
| System Backup | Read only | Cannot create system backups |
| Developer Mode | Hidden | Cannot enable developer features |

### 6.4 Navigation Configuration

Same as Administrator with additional:
```
  Administration Secondary Nav:
    + Cross-Course Analytics
    + Institution Reports
    + Bulk Operations
    + Institution Policies
```

---

## 7. Role: Plugin Developer

### 7.1 Default Landing Screen

**Plugin Manager** — `/plugins`

### 7.2 Visible Screens

| Screen | Route | Access Level |
|---|---|---|
| Plugin Manager | `/plugins` | Read |
| Plugin Browser | `/plugins/browse` | Read |
| Plugin Detail | `/plugins/:id` | Read |
| Plugin SDK Documentation | `/help/plugins/sdk` | Read |
| Plugin Testing | `/plugins/developer/test` | Execute |
| Plugin Debugger | `/plugins/developer/debug` | Read |
| Plugin Logs | `/plugins/:id/logs` | Read |
| Plugin Configuration | `/plugins/:id/configure` | Write (own plugins) |
| Developer Settings | `/settings/advanced` | Write |
| Diagnostics | `/diagnostics` | Read (limited) |

### 7.3 Restricted Features

| Feature | Restriction | Behavior |
|---|---|---|
| Course Management | Hidden | Cannot manage courses |
| User Management | Hidden | Cannot manage users |
| System Settings | Hidden | Cannot access system config |
| Student Features | Hidden | Cannot enroll or take assessments |
| Plugin Installation (other devs) | Hidden | Cannot install other devs' plugins |

### 7.4 Navigation Configuration

```
Primary Navigation:
  ├── Plugin Manager (Alt+1) ← Primary landing
  ├── Plugins (Alt+2)
  ├── Diagnostics (Alt+3)
  ├── Settings (Alt+6)
  └── Help (Alt+7)

Secondary Navigation:
  Plugin Manager: Installed, Developer, Testing, Logs, SDK
  Help: Center, SDK Documentation, Troubleshooting
```

---

## 8. Role: System Operator

### 8.1 Default Landing Screen

**Diagnostics — System Health** — `/diagnostics/health`

### 8.2 Visible Screens

| Screen | Route | Access Level |
|---|---|---|
| System Health | `/diagnostics/health` | Read, run checks |
| Log Viewer | `/diagnostics/logs` | Read |
| Performance Monitor | `/diagnostics/performance` | Read |
| Network Status | `/diagnostics/network` | Read |
| Database Integrity | `/diagnostics/database` | Read, run |
| Crash Reports | `/diagnostics/crashes` | Read |
| Backup & Restore | `/settings/backup` | Create, restore |
| Diagnostics Settings | `/settings/diagnostics` | Write |
| Help Center | `/help/center` | Read |

### 8.3 Restricted Features

| Feature | Restriction | Behavior |
|---|---|---|
| User Management | Hidden | Cannot manage users |
| Course Management | Hidden | Cannot manage courses |
| Plugin Management | Hidden | Cannot manage plugins |
| Institution Settings | Hidden | Cannot configure institution |
| Analytics | Hidden | Cannot view analytics |
| Student Features | Hidden | Cannot enroll or learn |

### 8.4 Navigation Configuration

```
Primary Navigation:
  ├── System Health (Alt+1) ← Primary landing
  ├── Diagnostics (Alt+2)
  ├── Backup (Alt+3)
  ├── Settings (Alt+6)
  └── Help (Alt+7)

Secondary Navigation:
  Diagnostics: Health, Logs, Performance, Network, Database, Crashes
  Settings: Backup, Diagnostics
```

---

## 9. Permission Check Implementation

### 9.1 React Router Guard

```typescript
// Route guard wrapper
function ProtectedRoute({
  children,
  requiredRole,
  requiredPermission,
  fallback = '/dashboard'
}: ProtectedRouteProps) {
  const { user, hasRole, hasPermission } = useAuthStore();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to={fallback} replace />;
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <AccessDeniedScreen resource={requiredPermission} />;
  }

  return children;
}
```

### 9.2 Route Configuration

```typescript
const routes: RouteConfig[] = [
  // Public routes
  { path: '/login', element: <LoginScreen />, public: true },
  { path: '/setup', element: <FirstLaunchWizard />, public: true },

  // Student routes
  {
    path: '/dashboard',
    element: <Dashboard />,
    roles: ['student', 'instructor', 'admin', 'institution_manager'],
  },
  {
    path: '/courses/browse',
    element: <CourseBrowser />,
    roles: ['student', 'instructor', 'admin', 'institution_manager'],
  },
  {
    path: '/admin/users',
    element: <UserManagement />,
    roles: ['admin', 'institution_manager'],
  },
  {
    path: '/plugins',
    element: <PluginManager />,
    roles: ['admin', 'institution_manager', 'plugin_developer'],
  },
  {
    path: '/diagnostics',
    element: <Diagnostics />,
    roles: ['admin', 'institution_manager', 'system_operator'],
  },
];
```

### 9.3 Permission Hook

```typescript
function useNavigationPermissions() {
  const { user } = useAuthStore();
  const role = user?.role;

  return {
    canViewDashboard: true, // All roles
    canViewCourses: true, // All roles
    canCreateCourses: ['instructor', 'admin', 'institution_manager'].includes(role),
    canManageUsers: ['admin', 'institution_manager'].includes(role),
    canManagePlugins: ['admin', 'institution_manager', 'plugin_developer'].includes(role),
    canRunDiagnostics: ['admin', 'institution_manager', 'system_operator'].includes(role),
    canManageBackup: ['admin', 'institution_manager', 'system_operator'].includes(role),
    canAccessAdvancedSettings: ['admin'].includes(role),
    canAccessInstitutionSettings: ['admin', 'institution_manager'].includes(role),
  };
}
```

---

## 10. Graceful Degradation

### 10.1 Degradation Strategies

| Strategy | When Used | Behavior |
|---|---|---|
| Hidden | Feature not available for role | Element not rendered in DOM |
| Disabled | Feature exists but access denied | Element rendered, grayed out, tooltip explains |
| Restricted | Feature partially available | Show limited view with upgrade prompt |
| Redirect | Unauthorized direct URL access | Redirect to fallback screen |

### 10.2 Strategy by Context

| Context | Strategy | Example |
|---|---|---|
| Primary nav items | Hidden | Admin nav hidden from students |
| Secondary nav items | Hidden | "Create Course" hidden from students |
| Buttons | Disabled or Hidden | "Install Plugin" disabled for instructors |
| Table rows | Hidden or Restricted | Other users' data restricted |
| Context menus | Hidden | "Delete" hidden for non-admins |
| Direct URL access | Redirect | `/admin/users` redirects student to `/dashboard` |
| API calls | Deny with error | 403 response, toast error message |
| Bulk operations | Filter allowed items | Only show items user can operate on |

### 10.3 Access Denied Screen

```
┌─────────────────────────────────────────────────────┐
│                                                      │
│              🔒 Access Restricted                     │
│                                                      │
│  You don't have permission to access this page.      │
│                                                      │
│  Required role: Administrator                         │
│  Your role: Student                                   │
│                                                      │
│  If you believe this is an error, contact your        │
│  administrator.                                       │
│                                                      │
│  [Go to Dashboard]  [Contact Admin]                   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 10.4 Error Handling

```typescript
// Permission denied toast
function showPermissionDenied(resource: string) {
  toast.error({
    title: 'Access Denied',
    message: `You don't have permission to access ${resource}.`,
    action: {
      label: 'Contact Admin',
      handler: () => navigateTo('/help/troubleshooting'),
    },
    duration: 8000, // Longer for errors
  });
}

// Route guard redirect
function handleUnauthorizedAccess(route: string, userRole: string) {
  console.warn(`User with role "${userRole}" attempted to access "${route}"`);
  // Log for audit
  auditLog.record('unauthorized_access', { route, userRole });
  // Redirect
  navigateTo(getFallbackRoute(userRole));
  // Show message
  showPermissionDenied(route);
}
```

---

## 11. Workspace Switcher

### 11.1 Role-Based View Switching

Users with multiple roles can switch between workspace views:

| User Has Roles | Available Views | Switcher Shows |
|---|---|---|
| Student only | Student View | No switcher |
| Student + Instructor | Student, Instructor | Dropdown in user menu |
| Instructor + Admin | Instructor, Admin | Dropdown in user menu |
| Admin + Institution Manager | Admin, Institution Manager | Dropdown in user menu |
| Plugin Developer + Admin | Developer, Admin | Dropdown in user menu |

### 11.2 View Switching Behavior

```
User clicks workspace switcher → Dropdown appears:
  ○ Student View (current)
  ○ Instructor View
  ○ Admin View

User selects different view →
  1. Primary nav updates to match new role
  2. Dashboard updates to role-appropriate layout
  3. Secondary navs update
  4. URL may change if current screen unavailable
  5. Toast confirms: "Switched to Instructor View"
```

### 11.3 View Persistence

- Last selected view remembered per session
- Default view set in General Settings
- View persists across navigation within session
- Resets to default on application restart

---

## 12. Multi-Role Navigation Matrix

### 12.1 Combined Navigation for Multi-Role Users

When a user has multiple roles, their navigation is the union of all role permissions:

| Nav Item | Student | Instructor | Admin | Combined (Student+Instructor) |
|---|---|---|---|---|
| Dashboard | ✓ | ✓ | ✓ | ✓ |
| Courses | ✓ | ✓ | ✓ | ✓ |
| Course Management | ✗ | ✓ | ✓ | ✓ |
| Simulations | ✓ | ✓ | ✓ | ✓ |
| Assessments | ✓ | ✓ | ✓ | ✓ |
| Assessment Creator | ✗ | ✓ | ✓ | ✓ |
| Reports | ✓ | ✓ | ✓ | ✓ |
| Reports (Create) | ✗ | ✓ | ✓ | ✓ |
| Analytics | ✓ | ✓ | ✓ | ✓ |
| Analytics (Course) | ✗ | ✓ | ✓ | ✓ |
| Administration | ✗ | ✗ | ✓ | ✗ |
| Plugins | ✗ | ✗ | ✓ | ✗ |
| Diagnostics | ✗ | ✗ | ✓ | ✗ |
| Settings (System) | ✗ | ✗ | ✓ | ✗ |

### 12.2 Priority Rules

When roles conflict:
1. **Most permissive wins**: If any role grants access, user has access
2. **Highest role for defaults**: Dashboard variant uses highest role
3. **Navigation union**: All nav items from all roles shown
4. **Settings merge**: System settings visible if any role allows

---

## 13. Audit and Monitoring

### 13.1 Permission Events Logged

| Event | Details |
|---|---|
| Route access | User, route, role, timestamp, allowed/denied |
| Feature access | User, feature, role, timestamp, result |
| Role switch | User, from_role, to_role, timestamp |
| Unauthorized attempt | User, resource, role, timestamp, IP |
| Permission change | Admin, target_user, old_role, new_role, timestamp |

### 13.2 Audit Integration

All permission checks integrate with the audit log:

```typescript
function auditPermissionCheck(
  userId: string,
  resource: string,
  action: string,
  result: 'allowed' | 'denied'
) {
  auditLog.record('permission_check', {
    userId,
    resource,
    action,
    result,
    timestamp: Date.now(),
    userAgent: navigator.userAgent,
  });
}
```
