# Architecture Overview

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AuthShield Lab Desktop                    │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  Electron Shell                        │  │
│  │  ┌──────────────┐          ┌──────────────────────┐   │  │
│  │  │  Main Process │◄────────►│   Renderer Process   │   │  │
│  │  │  (Node.js)    │   IPC   │   (Chromium)          │   │  │
│  │  │               │          │                      │   │  │
│  │  │  - Window Mgr │          │  ┌────────────────┐  │   │  │
│  │  │  - File I/O   │          │  │  React App     │  │   │  │
│  │  │  - Native API │          │  │  ├─ Pages      │  │   │  │
│  │  │  - DB Access  │          │  │  ├─ Components │  │   │  │
│  │  └──────┬───────┘          │  │  ├─ Stores     │  │   │  │
│  │         │                   │  │  └─ Themes     │  │   │  │
│  │         │                   │  └────────────────┘  │   │  │
│  │         │                   └──────────────────────┘   │  │
│  └─────────┼─────────────────────────────────────────────┘  │
│            │                                                 │
│  ┌─────────▼─────────────────────────────────────────────┐  │
│  │              FastAPI Backend Server                    │  │
│  │              (localhost:8000)                           │  │
│  │                                                        │  │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │   Auth   │ │ Sessions │ │  Attacks │ │ Defenses │  │  │
│  │  │ Module   │ │  Module  │ │  Module  │ │  Module  │  │  │
│  │  └────┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │  │
│  │       │           │            │             │         │  │
│  │  ┌────┴────┐ ┌────┴─────┐ ┌───┴────┐ ┌─────┴─────┐   │  │
│  │  │  Users  │ │Analytics │ │Reports │ │ Learning  │   │  │
│  │  │ Module  │ │  Module  │ │ Module │ │  Module   │   │  │
│  │  └────┬────┘ └────┬─────┘ └───┬────┘ └─────┬─────┘   │  │
│  │       │           │           │             │         │  │
│  │  ┌────▼───────────▼───────────▼─────────────▼─────┐   │  │
│  │  │              SQLAlchemy ORM                     │   │  │
│  │  └────────────────────┬───────────────────────────┘   │  │
│  │                       │                               │  │
│  │  ┌────────────────────▼───────────────────────────┐   │  │
│  │  │           SQLite Database                       │   │  │
│  │  │           (data/app.db)                         │   │  │
│  │  └────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### FastAPI Application

The backend follows a modular architecture built on FastAPI:

```
backend/app/
├── main.py              # Application entry point
├── config/              # Configuration management
│   ├── __init__.py      # Settings re-export
│   └── settings.py      # Pydantic settings
├── database/            # Database layer
│   ├── __init__.py
│   ├── engine.py        # SQLAlchemy engine setup
│   ├── session.py       # Session factory
│   └── models/          # ORM models
├── authentication/      # Authentication module
├── users/               # User management
├── sessions/            # Session handling
├── attacks/             # Attack simulations
├── defenses/            # Defense mechanisms
├── analytics/           # Analytics engine
├── reports/             # Report generation
├── learning/            # Learning center
├── audit/               # Audit logging
├── middleware/          # FastAPI middleware
└── utils/               # Shared utilities
```

### Request Flow

```
Client Request
    │
    ▼
┌─────────────────┐
│  CORS Middleware  │ ──► Reject non-localhost origins
└────────┬────────┘
         │
┌────────▼────────┐
│ Rate Limiter     │ ──► Block excessive requests
└────────┬────────┘
         │
┌────────▼────────┐
│  Auth Middleware  │ ──► Validate JWT, attach user
└────────┬────────┘
         │
┌────────▼────────┐
│  Audit Logger    │ ──► Record request metadata
└────────┬────────┘
         │
┌────────▼────────┐
│  Route Handler   │ ──► Business logic
└────────┬────────┘
         │
┌────────▼────────┐
│  Response Model  │ ──► Pydantic serialization
└────────┬────────┘
         │
         ▼
   Client Response
```

### SQLAlchemy ORM

The database layer uses SQLAlchemy 2.0 with the async engine:

- **Declarative Base**: All models inherit from a shared base
- **Session Management**: Context-managed sessions with automatic cleanup
- **Migrations**: Alembic for schema version control
- **Relationships**: Properly defined with lazy loading where appropriate

## Frontend Architecture

### Electron + React

```
frontend/
├── src/
│   ├── main/                 # Electron main process
│   │   ├── index.ts          # Main process entry
│   │   ├── window.ts         # Window management
│   │   ├── ipc.ts            # IPC handlers
│   │   └── menu.ts           # Application menu
│   ├── renderer/             # React application
│   │   ├── App.tsx           # Root component
│   │   ├── index.tsx         # Entry point
│   │   ├── pages/            # Route pages
│   │   ├── components/       # Reusable components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── stores/           # Zustand state stores
│   │   ├── themes/           # Theme definitions
│   │   ├── i18n/             # Translations
│   │   └── utils/            # Utility functions
│   └── shared/               # Shared types
│       └── types.ts
├── public/                   # Static assets
├── package.json
└── tsconfig.json
```

### Component Hierarchy

```
<App>
├── <ThemeProvider>
│   ├── <AuthProvider>
│   │   ├── <Layout>
│   │   │   ├── <Sidebar>
│   │   │   │   ├── <NavSection>
│   │   │   │   └── <UserMenu>
│   │   │   ├── <Header>
│   │   │   │   ├── <SearchBar>
│   │   │   │   └── <Notifications>
│   │   │   ├── <Breadcrumbs>
│   │   │   ├── <MainContent>
│   │   │   │   └── <Routes>
│   │   │   │       ├── <DashboardPage>
│   │   │   │       ├── <AuthPage>
│   │   │   │       ├── <UsersPage>
│   │   │   │       ├── <AttacksPage>
│   │   │   │       └── ...
│   │   │   └── <Footer>
│   │   └── <ToastProvider>
│   └── <AccessibilityProvider>
└── <ErrorBoundary>
```

### State Management (Zustand)

State is organized into focused stores:

| Store | Purpose |
|-------|---------|
| `useAuthStore` | Current user, tokens, permissions |
| `useThemeStore` | Active theme, font size, preferences |
| `useUsersStore` | User list, selected user, filters |
| `useSessionsStore` | Active sessions, session history |
| `useAttacksStore` | Attack configurations, results, history |
| `useDefensesStore` | Defense rules, active protections |
| `useAnalyticsStore` | Metrics, charts, real-time data |
| `useNavigationStore` | Sidebar state, breadcrumbs, favorites |

## Communication Flow

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Renderer    │         │     Main     │         │   Backend    │
│   (React)     │         │   Process    │         │  (FastAPI)   │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │  ipcRenderer.invoke()  │                        │
       │───────────────────────►│                        │
       │                        │  HTTP Request          │
       │                        │  (localhost:8000)      │
       │                        │───────────────────────►│
       │                        │                        │
       │                        │  HTTP Response         │
       │                        │◄───────────────────────│
       │  ipcRenderer.send()    │                        │
       │◄───────────────────────│                        │
       │                        │                        │
```

## Security Architecture

### Network Isolation

```
┌─────────────────────────────────────────┐
│              Local Machine               │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │         AuthShield Lab            │  │
│  │         (127.0.0.1:8000)         │  │
│  └───────────────┬───────────────────┘  │
│                  │                       │
│         ┌────────▼────────┐             │
│         │   Loopback Only  │             │
│         │   Interface      │             │
│         └────────┬────────┘             │
│                  │                       │
│         ┌────────▼────────┐             │
│         │  OS Firewall     │             │
│         │  (Blocks external)│            │
│         └─────────────────┘             │
│                                          │
│  ✗ External Network: BLOCKED             │
│  ✗ Cloud Services: BLOCKED              │
│  ✗ Telemetry: BLOCKED                   │
└─────────────────────────────────────────┘
```

### Password Hashing

```
User Password
    │
    ▼
┌─────────────┐
│  Generate    │
│  Salt        │ ──► 16 bytes CSPRNG
└──────┬──────┘
       │
┌──────▼──────┐
│  bcrypt      │
│  (cost=12)   │
└──────┬──────┘
       │
┌──────▼──────┐
│  Store       │
│  hash+salt   │ ──► 60-byte bcrypt hash
└─────────────┘
```

### Session Management

```
Login Request
    │
    ▼
┌─────────────────┐
│  Validate        │
│  Credentials     │
└────────┬────────┘
         │
┌────────▼────────┐
│  Generate JWT    │ ──► Header + Payload + Signature
│  (15min expiry)  │
└────────┬────────┘
         │
┌────────▼────────┐
│  Generate        │
│  Refresh Token   │ ──► 7-day expiry, single use
└────────┬────────┘
         │
┌────────▼────────┐
│  Return Tokens   │
│  to Client       │
└─────────────────┘
```

## Module Dependency Map

```
┌─────────────┐
│  Dashboard   │ ◄── Aggregates data from all modules
└──────┬──────┘
       │
       ├──────► Analytics ──► Audit
       ├──────► Sessions ──► Authentication
       ├──────► Users ──► Authentication
       ├──────► Attacks ──► Users, Sessions
       ├──────► Defenses ──► Attacks, Sessions
       ├──────► Reports ──► Analytics, Audit
       ├──────► Learning ──► Reports, Analytics
       └──────► Settings ──► Config
```

## Data Flow Diagrams

### Attack Simulation Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Student  │────►│  Select  │────►│ Configure│────►│ Execute  │
│  Selects  │     │  Attack  │     │ Params   │     │ Attack   │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                         │
┌──────────┐     ┌──────────┐     ┌──────────┐          │
│  Review  │◄────│ Analyze  │◄────│  Capture │◄─────────┘
│  Results │     │ Results  │     │  Logs    │
└──────────┘     └──────────┘     └──────────┘
```

### Learning Progress Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Browse  │────►│  Start   │────►│ Complete │
│  Lessons │     │  Module  │     │  Quiz    │
└──────────┘     └──────────┘     └────┬─────┘
                                       │
┌──────────┐     ┌──────────┐          │
│  Earn    │◄────│  Update  │◄─────────┘
│  Badge   │     │ Progress │
└──────────┘     └──────────┘
```

## Deployment Architecture

AuthShield Lab is deployed as a desktop application:

```
┌─────────────────────────────────────────────┐
│           User's Machine                     │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │     Electron Application Package      │  │
│  │                                       │  │
│  │  ┌─────────────┐  ┌───────────────┐  │  │
│  │  │   Electron   │  │   Bundled     │  │  │
│  │  │   Runtime    │  │   Assets      │  │  │
│  │  │   (Chromium) │  │   (React App) │  │  │
│  │  └─────────────┘  └───────────────┘  │  │
│  │                                       │  │
│  │  ┌─────────────┐  ┌───────────────┐  │  │
│  │  │   Backend    │  │   SQLite      │  │  │
│  │  │   (FastAPI)  │  │   Database    │  │  │
│  │  │   + Uvicorn  │  │   (app.db)    │  │  │
│  │  └─────────────┘  └───────────────┘  │  │
│  │                                       │  │
│  │  ┌─────────────┐  ┌───────────────┐  │  │
│  │  │   Python     │  │   Config      │  │  │
│  │  │   Runtime    │  │   Files       │  │  │
│  │  │   (Embedded) │  │               │  │  │
│  │  └─────────────┘  └───────────────┘  │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Platform-specific packages:                │
│  - Windows: .exe installer (NSIS)          │
│  - macOS: .dmg disk image                  │
│  - Linux: .AppImage, .deb, .rpm           │
└─────────────────────────────────────────────┘
```
