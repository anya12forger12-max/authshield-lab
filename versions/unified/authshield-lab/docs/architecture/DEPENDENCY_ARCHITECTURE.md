# Dependency Architecture — AuthShield Lab

> Version: 1.0  
> Last Updated: 2026-07-19  
> Status: Current

---

## 1. Overview

The dependency architecture defines which layers and modules may depend on which others, how shared services are provided, and how circular dependencies are prevented. Dependencies flow inward toward the Domain core.

---

## 2. Allowed Dependencies Per Layer

### 2.1 Dependency Matrix

```
                      DEPENDS ON →
                      Core  Domain  App  Infra  Persist  Integr  Plugin  SDK  Pres
Layer (↓)
Shared Core           —     ✗       ✗    ✗      ✗        ✗       ✗       ✗    ✗
Domain                ✓     —       ✗    ✗      ✗        ✗       ✗       ✗    ✗
Application           ✓     ✓       —    ✗*     ✗*       ✗       ✗       ✗    ✗
Infrastructure        ✓     ✓       ✗    —      ✗        ✗       ✗       ✗    ✗
Persistence           ✓     ✓       ✗    ✗      —        ✗       ✗       ✗    ✗
Integration           ✓     ✗       ✗    ✓      ✗        —       ✗       ✗    ✗
Plugin                ✓     ✓(ro)   ✗    ✓      ✗        ✗       —       ✗    ✗
SDK                   ✓     ✓(ro)   ✗    ✗      ✗        ✗       ✗       —    ✗
Presentation          ✓     ✗       ✓    ✗      ✗        ✗       ✗       ✗    —
Testing               ✓     ✓       ✓    ✓      ✓        ✓       ✓       ✓    ✓
Tooling               ✓     ✓       ✓    ✓      ✓        ✓       ✓       ✓    ✓
Documentation         ✓     ✓       ✓    ✓      ✓        ✓       ✓       ✓    ✓
```

**Legend:** ✓ = allowed, ✓(ro) = read-only, ✗ = forbidden, ✗* = via interface only (Dependency Inversion)

---

### 2.2 Layer-by-Layer Dependencies

**Shared Core**
```
Dependencies: NONE
Dependents: ALL layers
```
- Leaf node in dependency graph
- Zero imports from any application layer
- Contains only Python stdlib dependencies

**Domain Layer**
```
Dependencies: Shared Core
Dependents: Application, Infrastructure, Persistence, Plugin, SDK, Testing, Tooling
```
- Depends only on Shared Core
- All other layers depend on Domain (not vice versa)

**Application Layer**
```
Dependencies: Shared Core, Domain
  * Persistence: via Repository interface (Dependency Inversion)
Dependents: Presentation, Testing, Tooling
```
- Uses Dependency Inversion for Persistence
- Never imports concrete repository implementations
- Receives repositories via constructor injection

**Infrastructure Layer**
```
Dependencies: Shared Core, Domain (event types only)
Dependents: Application (via DI), Integration, Testing, Tooling
```
- Domain dependency is read-only (event type definitions)
- Provides services consumed by all layers via DI

**Persistence Layer**
```
Dependencies: Shared Core, Domain (repository interfaces)
Dependents: Application (via DI), Testing, Tooling
```
- Implements Domain repository interfaces
- Never called directly (always via abstract interface)

**Integration Layer**
```
Dependencies: Shared Core, Infrastructure (config, logging)
Dependents: Testing, Tooling
```
- Bridges Electron IPC and file system
- Never called from Domain or Application directly

**Plugin Layer**
```
Dependencies: Shared Core, Domain (event types, read-only), Infrastructure (event bus, config)
Dependents: Testing, Tooling
```
- Read-only access to Domain event types
- Never writes to Persistence directly

**SDK Layer**
```
Dependencies: Shared Core, Domain (entity types, read-only)
Dependents: Plugin, Testing, Tooling
```
- Provides stable API surface for plugins
- Domain dependency is read-only

**Presentation Layer**
```
Dependencies: Shared Core, Application (via IPC)
Dependents: Testing, Tooling
```
- Never imports from Domain, Infrastructure, or Persistence
- All backend communication via IPC bridge

---

## 3. Forbidden Dependencies (with Rationale)

### 3.1 Critical Forbidden Dependencies

| From → To | Rationale |
|---|---|
| Domain → Infrastructure | Would leak technical concerns into business logic |
| Domain → Persistence | Would couple business rules to database schema |
| Domain → Application | Would create circular dependency (Application → Domain) |
| Domain → Presentation | Domain must not know about rendering |
| Presentation → Domain | Presentation must not bypass Application layer |
| Presentation → Infrastructure | Presentation must not access config, logging, event bus |
| Presentation → Persistence | Presentation must not access database |
| Persistence → Application | Repository must not call use cases |
| Persistence → Infrastructure | Repository must not use config or logging directly |
| Plugin → Persistence | Plugins must not access database directly |
| Plugin → Application | Plugins must not call use cases directly |
| Plugin → Integration | Plugins must not do file I/O |

### 3.2 Soft Forbidden (Allowed with Justification)

| From → To | Justification Required |
|---|---|
| Infrastructure → Domain | Read-only access to event types for routing |
| Application → Infrastructure | Via DI only; never direct import |
| Application → Persistence | Via interface only; Dependency Inversion |

---

## 4. Shared Services

### 4.1 Service Registry

All shared services are registered in a central service registry at startup and provided via dependency injection.

```python
class ServiceRegistry:
    def __init__(self):
        self._services: dict[str, Any] = {}
    
    def register(self, name: str, service: Any) -> None:
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        return self._services[name]
```

### 4.2 Shared Service Contracts

**Event Bus**
```python
class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None: ...
    
    @abstractmethod
    def subscribe(self, topic: str, handler: EventHandler) -> Subscription: ...
    
    @abstractmethod
    async def unsubscribe(self, subscription: Subscription) -> None: ...
```

**Configuration Service**
```python
class ConfigService(ABC):
    @abstractmethod
    def get(self, key: str, default: T = None) -> T: ...
    
    @abstractmethod
    def get_typed(self, key: str, type_: type[T]) -> T: ...
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None: ...
    
    @abstractmethod
    def all(self) -> dict[str, Any]: ...
```

**Logging Service**
```python
class LoggingService(ABC):
    @abstractmethod
    def get_logger(self, name: str) -> StructuredLogger: ...
    
    @abstractmethod
    async def flush(self) -> None: ...
    
    @abstractmethod
    def query(self, filters: LogFilters) -> list[LogEntry]: ...
```

**Localization Service**
```python
class LocalizationService(ABC):
    @abstractmethod
    def translate(self, key: str, **kwargs: Any) -> str: ...
    
    @abstractmethod
    def get_available_languages(self) -> list[str]: ...
    
    @abstractmethod
    def set_language(self, language: str) -> None: ...
```

---

## 5. Cross-Cutting Concerns

### 5.1 Concern Integration Matrix

| Concern | Presentation | Application | Domain | Infrastructure | Persistence |
|---|---|---|---|---|---|
| **Logging** | IPC calls logged | Use case entry/exit | Domain events | Log management | Query timing |
| **Security** | Input validation | Authorization | Invariants | Encryption | Data encryption |
| **Caching** | Component cache | Query cache | N/A | Cache service | N/A |
| **Error Handling** | Error boundaries | Result monad | Invariant errors | Error logging | DB errors |
| **Validation** | Form validation | DTO validation | Business rules | Config validation | Schema validation |
| **Accessibility** | ARIA, keyboard | Structured responses | N/A | N/A | N/A |

### 5.2 Cross-Cutting Implementation

**Logging Cross-Cutting:**
```
Presentation: window.api.invoke() logged via IPC bridge
Application: use case logged with timing and result
Domain: domain events logged at creation
Infrastructure: log management and rotation
Persistence: slow query logging (>100ms)
```

**Security Cross-Cutting:**
```
Presentation: client-side input sanitization
Application: RBAC permission check, rate limiting
Domain: password complexity, permission hierarchies
Infrastructure: token generation, encryption
Persistence: sensitive field encryption at rest
```

**Error Handling Cross-Cutting:**
```
Presentation: React error boundaries, toast notifications
Application: Result<T, E> monad for all use cases
Domain: InvariantViolation exceptions
Infrastructure: error classification and logging
Persistence: database error wrapping
```

---

## 6. Dependency Inversion Rules

### 6.1 Core Principle

> High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details. Details should depend on abstractions.

### 6.2 Dependency Inversion in AuthShield Lab

| High-Level | Abstraction | Low-Level (Implementation) |
|---|---|---|
| Application | `UserRepository` | `SQLAlchemyUserRepository` |
| Application | `EventBus` | `AsyncEventBus` |
| Application | `ConfigService` | `PydanticConfigService` |
| Application | `LoggingService` | `StructlogService` |
| Application | `AuthService` | `JWTAuthService` |
| Application | `EncryptionService` | `AESEncryptionService` |

### 6.3 Inversion Pattern

```python
# Abstraction (Domain layer)
class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: EntityID) -> User | None: ...

# Implementation (Persistence layer)
class SQLAlchemyUserRepository(UserRepository):
    async def find_by_id(self, id: EntityID) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == str(id))
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

# Wiring (Application layer, via DI)
def get_user_repository() -> UserRepository:
    return SQLAlchemyUserRepository(get_session())

# Usage (Application layer)
class GetUserHandler:
    def __init__(self, user_repo: UserRepository):  # Depends on abstraction
        self.user_repo = user_repo
    
    async def handle(self, query: GetUserQuery) -> Result[UserDTO, AppError]:
        user = await self.user_repo.find_by_id(query.user_id)  # Calls abstraction
        if user is None:
            return Result.err(NotFoundError("User"))
        return Result.ok(UserDTO.from_domain(user))
```

---

## 7. Circular Dependency Prevention

### 7.1 Automated Enforcement

```python
# arch_check/circular_detector.py
import ast
from collections import defaultdict

class CircularDependencyDetector:
    def __init__(self):
        self.graph: dict[str, set[str]] = defaultdict(set)
    
    def add_edge(self, source: str, target: str) -> None:
        self.graph[source].add(target)
    
    def detect_cycles(self) -> list[list[str]]:
        """Detect and return all cycles in the dependency graph."""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
            
            path.pop()
            rec_stack.remove(node)
        
        for node in self.graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
```

### 7.2 CI Integration

```bash
#!/bin/bash
# scripts/arch-check.sh
echo "Running architecture checks..."

# Check for circular dependencies
python -m arch_check.circular_detector src/backend/app/
if [ $? -ne 0 ]; then
    echo "FAIL: Circular dependencies detected"
    exit 1
fi

# Check for forbidden imports
python -m arch_check.import_validator src/backend/app/
if [ $? -ne 0 ]; then
    echo "FAIL: Forbidden imports detected"
    exit 1
fi

# Check layer compliance
python -m arch_check.layer_validator src/backend/app/
if [ $? -ne 0 ]; then
    echo "FAIL: Layer violations detected"
    exit 1
fi

echo "All architecture checks passed"
```

### 7.3 Prevention Rules

| Rule | Enforcement | Severity |
|---|---|---|
| No circular imports | AST analysis at CI | Critical (build fails) |
| No backward dependencies | Import graph validation | High (PR blocked) |
| Domain purity | Import whitelist for Domain | Critical (build fails) |
| Dependency Inversion | Interface-only imports | High (PR blocked) |
| Layer ordering | Topological sort validation | Medium (warning) |

---

## 8. Version Compatibility Matrix

### 8.1 SDK Version Compatibility

| SDK Version | Supported Python | Supported Host | Plugin Compatibility |
|---|---|---|---|
| 1.0.x | 3.12+ | 1.0.x | 1.0.x plugins |
| 1.1.x | 3.12+ | 1.0.x, 1.1.x | 1.0.x, 1.1.x plugins |
| 2.0.x | 3.12+ | 2.0.x | 2.0.x plugins (breaking) |

### 8.2 Database Schema Compatibility

| Schema Version | Application Version | Migration Path |
|---|---|---|
| v1-v10 | 1.0.x | Forward only |
| v11-v20 | 1.1.x | Forward + backward |
| v21+ | 2.0.x | Forward only (breaking) |

### 8.3 IPC Protocol Compatibility

| Protocol Version | Renderer Version | Main Version | Compatibility |
|---|---|---|---|
| v1 | 1.0.x | 1.0.x | Exact match |
| v2 | 1.1.x | 1.1.x | Backward compatible (1 cycle) |

---

## 9. Module Isolation Rules

### 9.1 Module Communication Rules

| Rule | Description |
|---|---|
| No direct module imports | Modules communicate via events or shared interfaces |
| Event-based coupling | Modules subscribe to events, never call each other |
| Shared interface contracts | Cross-module interfaces defined in Shared Core |
| No shared state | Modules do not share mutable state |

### 9.2 Module Dependency Validation

```python
# Module dependency declarations
MODULE_DEPENDENCIES = {
    "auth": {"users", "sessions", "audit"},
    "users": {"auth", "audit"},
    "sessions": {"auth", "audit"},
    "audit": set(),  # Leaf module
    "policies": {"rules", "audit", "users"},
    "defense": {"auth", "sessions", "audit", "policies", "rules"},
    # ... (all 25 modules declared)
}

def validate_module_dependencies() -> list[str]:
    errors = []
    for module, deps in MODULE_DEPENDENCIES.items():
        for dep in deps:
            if dep not in MODULE_DEPENDENCIES:
                errors.append(f"Module '{module}' depends on unknown module '{dep}'")
    # Check for cycles
    if has_cycle(MODULE_DEPENDENCIES):
        errors.append("Circular module dependency detected")
    return errors
```

### 9.3 Module Interface Contracts

Each module exposes a well-defined public interface:

```python
# Module interface example
class AuthModuleInterface:
    """Public interface for the auth module."""
    
    @abstractmethod
    async def authenticate(self, credentials: LoginCredentials) -> Result[AuthToken, AuthError]: ...
    
    @abstractmethod
    async def validate_token(self, token: str) -> Result[TokenPayload, AuthError]: ...
    
    @abstractmethod
    async def revoke_token(self, token_id: EntityID) -> Result[None, AuthError]: ...
```

---

## 10. Dependency Direction Visualization

```
                    ┌─────────────────────────┐
                    │    SHARED CORE           │
                    │    (no dependencies)     │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │    DOMAIN LAYER          │
                    │    (depends on: Core)    │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                   │
    ┌─────────▼─────────┐ ┌────▼──────────┐ ┌─────▼──────────┐
    │  APPLICATION      │ │ INFRASTRUCTURE│ │  PERSISTENCE   │
    │  (Core, Domain)   │ │ (Core, Domain)│ │  (Core, Domain)│
    └─────────┬─────────┘ └────┬──────────┘ └─────┬──────────┘
              │                 │                   │
              │    ┌────────────┘                   │
              │    │                                │
    ┌─────────▼────▼────────────────────────────────▼──────────┐
    │                  INTEGRATION LAYER                        │
    │                (Core, Infrastructure)                     │
    └───────────────────────────┬──────────────────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                   │
    ┌─────────▼─────────┐ ┌────▼──────────┐ ┌─────▼──────────┐
    │  PLUGIN LAYER     │ │  SDK LAYER    │ │  PRESENTATION  │
    │  (Core, Domain,   │ │  (Core, Domain│ │  (Core, App)   │
    │   Infrastructure) │ │   read-only)  │ │                │
    └─────────┬─────────┘ └───────────────┘ └────────────────┘
              │
    ┌─────────▼─────────┐
    │  EXTERNAL PLUGINS  │
    │  (SDK interface)   │
    └────────────────────┘
```

**Dependency Direction Rules:**
1. Arrows point FROM dependent TO dependency
2. No arrow may point outward from Core
3. No arrow may point from Domain to any outer layer
4. All arrows flow inward toward Core
5. Exceptions: Infrastructure → Domain (read-only event types)
6. Exceptions: Plugin → Domain (read-only event types)
