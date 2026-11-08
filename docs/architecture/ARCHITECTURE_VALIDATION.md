# Architecture Validation — AuthShield Lab

> Version: 1.0  
> Last Updated: 2026-07-19  
> Status: Current

---

## 1. Overview

Architecture validation ensures AuthShield Lab maintains its clean architecture, dependency rules, naming conventions, and quality standards over time. Validation is automated, integrated into CI/CD, and enforced at every commit.

```
┌─────────────────────────────────────────────────────────────────┐
│                ARCHITECTURE VALIDATION FRAMEWORK                  │
│                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│
│  │   Layering   │ │  Dependency  │ │       Naming              ││
│  │   Rules      │ │  Rules       │ │       Rules               ││
│  └──────────────┘ └──────────────┘ └──────────────────────────┘│
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│
│  │   Module     │ │ Architecture │ │     Documentation         ││
│  │  Isolation   │ │   Drift      │ │     Consistency           ││
│  └──────────────┘ └──────────────┘ └──────────────────────────┘│
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│
│  │  Security    │ │Accessibility │ │      Automated            ││
│  │  Boundaries  │ │ Requirements │ │      Tooling              ││
│  └──────────────┘ └──────────────┘ └──────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Layering Rules Validation

### 2.1 Rules

| Rule ID | Rule | Severity |
|---|---|---|
| L001 | Domain layer must not import from any outer layer | Critical |
| L002 | Application layer must not import from Presentation | High |
| L003 | Application layer must not import from Infrastructure (direct) | High |
| L004 | Persistence layer must not import from Application | High |
| L005 | Infrastructure must not import from Application | High |
| L006 | Presentation must not import from Domain, Persistence, or Infrastructure | Critical |
| L007 | Plugin must not import from Application or Persistence | Critical |
| L008 | SDK must not import from Application, Infrastructure, or Persistence | Critical |
| L009 | Integration must not import from Domain or Application | High |
| L010 | Shared Core must not import from any application layer | Critical |

### 2.2 Validation Logic

```python
# tools/arch_check/layer_validator.py
import ast
from pathlib import Path

LAYER_MAP = {
    "core": 0,
    "domain": 1,
    "application": 2,
    "infrastructure": 3,
    "persistence": 4,
    "integration": 5,
    "plugins": 6,
    "sdk": 7,
}

ALLOWED_IMPORTS = {
    "core": [],  # No imports from application layers
    "domain": ["core"],
    "application": ["core", "domain"],
    "infrastructure": ["core", "domain"],
    "persistence": ["core", "domain"],
    "integration": ["core", "infrastructure"],
    "plugins": ["core", "domain", "infrastructure", "sdk"],
    "sdk": ["core", "domain"],
}

class LayerValidator:
    def __init__(self, root: Path):
        self.root = root
        self.violations: list[Violation] = []
    
    def validate(self) -> list[Violation]:
        for py_file in self.root.rglob("*.py"):
            source_layer = self._detect_layer(py_file)
            if source_layer is None:
                continue
            
            tree = ast.parse(py_file.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._check_import(source_layer, alias.name, py_file, node.lineno)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._check_import(source_layer, node.module, py_file, node.lineno)
        
        return self.violations
    
    def _detect_layer(self, path: Path) -> str | None:
        parts = path.relative_to(self.root).parts
        for layer in LAYER_MAP:
            if layer in parts:
                return layer
        return None
    
    def _check_import(self, source: str, target_module: str, file: Path, line: int) -> None:
        target_layer = self._detect_layer_from_module(target_module)
        if target_layer and target_layer not in ALLOWED_IMPORTS.get(source, []):
            self.violations.append(Violation(
                rule=f"L{source}_{target_layer}",
                severity="critical" if source == "domain" else "high",
                file=str(file),
                line=line,
                message=f"Layer '{source}' cannot import from layer '{target_layer}'"
            ))
```

### 2.3 CI Integration

```bash
# scripts/validate-layers.sh
#!/bin/bash
set -e

echo "=== Layer Validation ==="
python -m tools.arch_check.layer_validator src/backend/app/
LAYER_RESULT=$?

if [ $LAYER_RESULT -ne 0 ]; then
    echo "FAIL: Layer violations detected"
    exit 1
fi

echo "PASS: All layer rules satisfied"
```

---

## 3. Dependency Rules Validation

### 3.1 Rules

| Rule ID | Rule | Severity |
|---|---|---|
| D001 | No circular module dependencies | Critical |
| D002 | Domain depends only on Shared Core | Critical |
| D003 | Application uses Dependency Inversion for Persistence | High |
| D004 | Plugin dependencies declared in manifest must be valid | High |
| D005 | SDK version compatibility with host application | High |
| D006 | No transitive forbidden dependencies | High |
| D007 | All shared services accessed via DI, not direct import | Medium |

### 3.2 Circular Dependency Detection

```python
# tools/arch_check/circular_detector.py
from collections import defaultdict

class CircularDependencyDetector:
    def __init__(self):
        self.graph: dict[str, set[str]] = defaultdict(set)
    
    def build_from_imports(self, root: Path) -> None:
        """Build dependency graph from import analysis."""
        for py_file in root.rglob("*.py"):
            source_module = self._module_name(py_file)
            tree = ast.parse(py_file.read_text())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    target_module = self._resolve_module(node.module)
                    if target_module != source_module:
                        self.graph[source_module].add(target_module)
    
    def detect_cycles(self) -> list[list[str]]:
        """Detect all cycles using DFS."""
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
                    cycles.append(path[cycle_start:])
            
            path.pop()
            rec_stack.remove(node)
        
        for node in sorted(self.graph):
            if node not in visited:
                dfs(node, [])
        
        return cycles
```

### 3.3 Dependency Matrix Validation

```python
# tools/arch_check/dependency_matrix.py

EXPECTED_DEPENDENCIES = {
    "core": [],
    "domain": ["core"],
    "application": ["core", "domain"],
    "infrastructure": ["core", "domain"],
    "persistence": ["core", "domain"],
    "integration": ["core", "infrastructure"],
    "plugins": ["core", "domain", "infrastructure"],
    "sdk": ["core", "domain"],
}

def validate_dependency_matrix(actual_deps: dict[str, set[str]]) -> list[str]:
    errors = []
    for module, expected in EXPECTED_DEPENDENCIES.items():
        actual = actual_deps.get(module, set())
        
        # Check forbidden dependencies
        forbidden = actual - set(expected)
        if forbidden:
            errors.append(
                f"Module '{module}' has forbidden dependencies: {forbidden}"
            )
        
        # Check missing dependencies (warning only)
        missing = set(expected) - actual
        if missing:
            errors.append(
                f"Module '{module}' missing expected dependencies: {missing}"
            )
    
    return errors
```

---

## 4. Naming Rules Validation

### 4.1 Rules

| Rule ID | Rule | Examples | Severity |
|---|---|---|---|
| N001 | Module names: snake_case | `authentication`, `user_management` | Medium |
| N002 | Class names: PascalCase | `UserService`, `LoginHandler` | Medium |
| N003 | Function names: snake_case | `get_user_by_id()`, `validate_token()` | Medium |
| N004 | Constants: UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` | Low |
| N005 | Private names: underscore prefix | `_internal_method`, `_cache` | Low |
| N006 | Boolean names: is/has/can prefix | `is_active`, `has_permission` | Low |
| N007 | Event names: past tense verb | `UserCreated`, `LoginFailed` | Medium |
| N008 | Handler names: verb + noun + Handler | `LoginHandler`, `CreateUserHandler` | Medium |
| N009 | Repository names: entity + Repository | `UserRepository`, `CourseRepository` | Medium |
| N010 | Service names: entity + Service | `AuthService`, `TokenService` | Medium |
| N011 | DTO names: entity + DTO | `UserDTO`, `CourseDTO` | Medium |
| N012 | File names: snake_case.py | `user_service.py`, `login_handler.py` | Medium |

### 4.2 Naming Validation

```python
# tools/arch_check/naming_validator.py
import re
from pathlib import Path

NAMING_RULES = {
    "module": re.compile(r"^[a-z][a-z0-9_]*$"),
    "class": re.compile(r"^[A-Z][a-zA-Z0-9]*$"),
    "function": re.compile(r"^[a-z][a-z0-9_]*$"),
    "constant": re.compile(r"^[A-Z][A-Z0-9_]*$"),
    "private": re.compile(r"^_[a-z][a-z0-9_]*$"),
    "boolean": re.compile(r"^(is|has|can|should)[A-Z][a-zA-Z0-9]*$"),
    "event": re.compile(r"^[A-Z][a-zA-Z]+(Created|Updated|Deleted|Completed|Failed|Changed)$"),
    "handler": re.compile(r"^[A-Z][a-zA-Z]+Handler$"),
    "repository": re.compile(r"^[A-Z][a-zA-Z]+Repository$"),
    "service": re.compile(r"^[A-Z][a-zA-Z]+Service$"),
    "dto": re.compile(r"^[A-Z][a-zA-Z]+DTO$"),
}

class NamingValidator:
    def validate_file(self, path: Path) -> list[Violation]:
        violations = []
        tree = ast.parse(path.read_text())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not NAMING_RULES["class"].match(node.name):
                    violations.append(Violation(
                        rule="N002",
                        severity="medium",
                        file=str(path),
                        line=node.lineno,
                        message=f"Class name '{node.name}' not PascalCase"
                    ))
            
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith("_"):
                    pattern = "private"
                elif any(node.name.startswith(p) for p in ("is_", "has_", "can_")):
                    pattern = "boolean"
                else:
                    pattern = "function"
                
                if not NAMING_RULES[pattern].match(node.name):
                    violations.append(Violation(
                        rule="N003",
                        severity="medium",
                        file=str(path),
                        line=node.lineno,
                        message=f"Function name '{node.name}' not snake_case"
                    ))
        
        return violations
```

---

## 5. Module Isolation Validation

### 5.1 Rules

| Rule ID | Rule | Severity |
|---|---|---|
| M001 | Modules must not import from each other directly | Critical |
| M002 | Cross-module communication via events only | High |
| M003 | Module dependencies must match declared dependencies | High |
| M004 | Module public API must be defined in `__init__.py` | Medium |
| M005 | Internal implementation must use underscore prefix | Low |

### 5.2 Module Isolation Check

```python
# tools/arch_check/module_isolation.py

EXPECTED_MODULE_DEPS = {
    "auth": {"users", "sessions", "audit"},
    "users": {"auth", "audit"},
    "sessions": {"auth", "audit"},
    "audit": set(),
    "policies": {"rules", "audit", "users"},
    "rules": {"audit"},
    "defense": {"auth", "sessions", "audit", "policies", "rules"},
    "content": {"audit", "quality"},
    "lms": {"content", "audit"},
    "simulation": {"content", "defense", "audit"},
    "developer": {"audit"},
    "quality": {"content", "audit"},
    "production": {"config", "audit"},
    "ecosystem": {"audit"},
    "optimization": {"analytics", "config", "audit"},
    "collaboration": {"users", "content", "audit"},
    "standards": {"policies", "audit", "quality"},
    "content_studio": {"content", "quality", "audit"},
    "analytics": {"audit", "users", "lms"},
    "certification": {"lms", "analytics", "users", "audit"},
    "learning": {"lms", "analytics", "content", "users"},
    "config": set(),
    "backup": {"config", "audit"},
    "testing": {"audit", "analytics"},
    "documentation": {"audit"},
}

class ModuleIsolationValidator:
    def validate(self, root: Path) -> list[Violation]:
        violations = []
        
        for module, expected_deps in EXPECTED_MODULE_DEPS.items():
            actual_deps = self._scan_module_imports(root, module)
            unexpected = actual_deps - expected_deps - {module}
            
            if unexpected:
                violations.append(Violation(
                    rule="M003",
                    severity="high",
                    file=f"src/backend/app/{module}/",
                    message=f"Module '{module}' has undeclared dependencies: {unexpected}"
                ))
        
        return violations
```

---

## 6. Architecture Drift Detection

### 6.1 Drift Categories

| Category | Detection Method | Frequency |
|---|---|---|
| New forbidden imports | Import graph analysis | Every commit |
| New circular dependencies | Cycle detection | Every commit |
| Module dependency changes | Dependency matrix comparison | Every PR |
| API surface changes | Public API diff | Every release |
| Naming convention drift | AST analysis | Every commit |
| Test coverage drops | Coverage comparison | Every CI run |
| Performance regression | Benchmark comparison | Every release |

### 6.2 Drift Baseline

```json
{
  "architecture_baseline": {
    "version": "1.0.0",
    "created_at": "2026-07-19",
    "layer_dependencies": {
      "core": [],
      "domain": ["core"],
      "application": ["core", "domain"],
      "infrastructure": ["core", "domain"],
      "persistence": ["core", "domain"],
      "integration": ["core", "infrastructure"],
      "plugins": ["core", "domain", "infrastructure"],
      "sdk": ["core", "domain"]
    },
    "module_dependencies": { "...": "..." },
    "naming_patterns": { "...": "..." },
    "test_coverage": {
      "unit": 87.5,
      "integration": 72.3,
      "e2e": 65.0,
      "a11y": 90.0
    },
    "performance_benchmarks": {
      "cold_start_ms": 2800,
      "p50_request_ms": 45,
      "p99_request_ms": 450
    }
  }
}
```

### 6.3 Drift Comparison

```python
# tools/arch_check/drift_detector.py

class DriftDetector:
    def __init__(self, baseline_path: Path):
        self.baseline = json.loads(baseline_path.read_text())
    
    def detect_drift(self, current: dict) -> list[DriftReport]:
        reports = []
        
        # Layer dependency drift
        for layer, expected_deps in self.baseline["layer_dependencies"].items():
            actual_deps = current.get("layer_dependencies", {}).get(layer, [])
            if set(actual_deps) != set(expected_deps):
                reports.append(DriftReport(
                    category="layer_dependency",
                    severity="critical",
                    expected=expected_deps,
                    actual=actual_deps,
                    message=f"Layer '{layer}' dependency changed"
                ))
        
        # Module dependency drift
        for module, expected_deps in self.baseline["module_dependencies"].items():
            actual_deps = current.get("module_dependencies", {}).get(module, [])
            if set(actual_deps) != set(expected_deps):
                reports.append(DriftReport(
                    category="module_dependency",
                    severity="high",
                    expected=expected_deps,
                    actual=actual_deps,
                    message=f"Module '{module}' dependency changed"
                ))
        
        # Coverage drift
        for metric, threshold in self.baseline["test_coverage"].items():
            actual = current.get("test_coverage", {}).get(metric, 0)
            if actual < threshold - 5:  # 5% grace period
                reports.append(DriftReport(
                    category="test_coverage",
                    severity="high",
                    expected=f">= {threshold}%",
                    actual=f"{actual}%",
                    message=f"Test coverage for '{metric}' dropped below threshold"
                ))
        
        return reports
```

---

## 7. Documentation Consistency Checks

### 7.1 Rules

| Rule ID | Rule | Severity |
|---|---|---|
| DOC001 | Every module must have a docstring | Medium |
| DOC002 | Every public class must have a docstring | Medium |
| DOC003 | Every public method must have a docstring | Low |
| DOC004 | API endpoints must have OpenAPI descriptions | Medium |
| DOC005 | Architecture docs must match code structure | High |
| DOC006 | README must list all modules | Low |
| DOC007 | Changelog must document breaking changes | Medium |

### 7.2 Documentation Validation

```python
# tools/arch_check/doc_validator.py

class DocumentationValidator:
    def validate_modules_have_docs(self, root: Path) -> list[Violation]:
        violations = []
        modules_dir = root / "src" / "backend" / "app"
        
        for module_dir in modules_dir.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith("_"):
                doc_file = root / "docs" / "modules" / f"{module_dir.name}.md"
                if not doc_file.exists():
                    violations.append(Violation(
                        rule="DOC001",
                        severity="medium",
                        file=str(module_dir),
                        message=f"Module '{module_dir.name}' has no documentation"
                    ))
        
        return violations
    
    def validate_api_docs(self, app) -> list[Violation]:
        violations = []
        
        for route in app.routes:
            if hasattr(route, "endpoint"):
                if not route.endpoint.__doc__:
                    violations.append(Violation(
                        rule="DOC004",
                        severity="medium",
                        file=getattr(route, "file", "unknown"),
                        line=getattr(route, "line", 0),
                        message=f"Endpoint '{route.path}' has no docstring"
                    ))
        
        return violations
```

---

## 8. Security Boundary Validation

### 8.1 Rules

| Rule ID | Rule | Severity |
|---|---|---|
| SEC001 | No hardcoded secrets in source code | Critical |
| SEC002 | No plaintext password storage | Critical |
| SEC003 | No external network calls | Critical |
| SEC004 | Plugin sandbox restrictions enforced | Critical |
| SEC005 | All inputs validated before processing | High |
| SEC006 | Sensitive data logged as `***REDACTED***` | High |
| SEC007 | Token expiry enforced | High |
| SEC008 | RBAC checks on all protected endpoints | High |
| SEC009 | Database encryption for sensitive columns | High |
| SEC010 | Audit log integrity chain maintained | High |

### 8.2 Secret Scanning

```bash
# scripts/scan-secrets.sh
#!/bin/bash

echo "=== Secret Scanning ==="

# Check for hardcoded secrets
grep -rn "password\s*=\s*['\"]" src/ --include="*.py" | \
    grep -v "hashed_password" | \
    grep -v "password_hash" | \
    grep -v "test"

# Check for API keys
grep -rn "api_key\s*=\s*['\"]" src/ --include="*.py" | \
    grep -v "config\." | \
    grep -v "test"

# Check for tokens
grep -rn "token\s*=\s*['\"]" src/ --include="*.py" | \
    grep -v "bearer" | \
    grep -v "test"

echo "=== Secret Scan Complete ==="
```

### 8.3 Network Call Detection

```python
# tools/arch_check/network_detector.py

FORBIDDEN_NETWORK_MODULES = {
    "socket", "http", "urllib", "requests", "aiohttp",
    "websockets", "httpx", "httplib2",
}

class NetworkCallDetector:
    def detect(self, root: Path) -> list[Violation]:
        violations = []
        
        for py_file in root.rglob("*.py"):
            tree = ast.parse(py_file.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split(".")[0] in FORBIDDEN_NETWORK_MODULES:
                            violations.append(Violation(
                                rule="SEC003",
                                severity="critical",
                                file=str(py_file),
                                line=node.lineno,
                                message=f"Network module '{alias.name}' import detected"
                            ))
        
        return violations
```

---

## 9. Accessibility Requirements Validation

### 9.1 Rules

| Rule ID | Rule | Severity |
|---|---|---|
| A11Y001 | All interactive elements have accessible names | Critical |
| A11Y002 | All images have alt text | Critical |
| A11Y003 | All forms have labels | Critical |
| A11Y004 | Heading hierarchy is valid | Medium |
| A11Y005 | Color contrast ratios meet WCAG AA | Critical |
| A11Y006 | Focus indicators visible | High |
| A11Y007 | Modal dialogs manage focus correctly | High |
| A11Y008 | Live regions announce updates | Medium |
| A11Y009 | Skip links present on all pages | Medium |
| A11Y010 | Tables have captions and headers | Medium |

### 9.2 Automated A11y Validation

```python
# tools/arch_check/a11y_validator.py

class A11yValidator:
    def validate_component(self, component_path: Path) -> list[Violation]:
        violations = []
        content = component_path.read_text()
        
        # Check for aria-label or visible text on buttons
        buttons = re.findall(r'<button[^>]*>', content)
        for button in buttons:
            if 'aria-label' not in button and 'children' not in button:
                violations.append(Violation(
                    rule="A11Y001",
                    severity="critical",
                    file=str(component_path),
                    message="Button without accessible name"
                ))
        
        # Check for alt text on images
        images = re.findall(r'<img[^>]*>', content)
        for img in images:
            if 'alt=' not in img:
                violations.append(Violation(
                    rule="A11Y002",
                    severity="critical",
                    file=str(component_path),
                    message="Image without alt text"
                ))
        
        # Check for labels on inputs
        inputs = re.findall(r'<input[^>]*>', content)
        for inp in inputs:
            if 'aria-label' not in inp and 'id=' not in inp:
                violations.append(Violation(
                    rule="A11Y003",
                    severity="critical",
                    file=str(component_path),
                    message="Input without label"
                ))
        
        return violations
```

---

## 10. Automated Tooling

### 10.1 Tool Inventory

| Tool | Purpose | Location | Trigger |
|---|---|---|---|
| `arch-check` | Full architecture validation | `tools/arch_check/` | CI, pre-commit |
| `layer-validator` | Layering rule enforcement | `tools/arch_check/` | Every commit |
| `circular-detector` | Cycle detection | `tools/arch_check/` | Every commit |
| `naming-validator` | Naming convention check | `tools/arch_check/` | Every commit |
| `module-isolation` | Module boundary check | `tools/arch_check/` | Every PR |
| `drift-detector` | Architecture drift check | `tools/arch_check/` | Every release |
| `secret-scanner` | Hardcoded secret detection | `scripts/` | Every commit |
| `network-detector` | Network call detection | `tools/arch_check/` | Every commit |
| `a11y-validator` | Accessibility rule check | `tools/arch_check/` | Every PR |
| `doc-validator` | Documentation consistency | `tools/arch_check/` | Every PR |

### 10.2 CI/CD Integration

```yaml
# .github/workflows/architecture.yml
name: Architecture Validation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  layer-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate layers
        run: python -m tools.arch_check.layer_validator src/backend/app/

  dependency-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Detect circular dependencies
        run: python -m tools.arch_check.circular_detector src/backend/app/
      - name: Validate dependency matrix
        run: python -m tools.arch_check.dependency_matrix src/backend/app/

  naming-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate naming conventions
        run: python -m tools.arch_check.naming_validator src/backend/app/

  module-isolation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate module isolation
        run: python -m tools.arch_check.module_isolation src/backend/app/

  security-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Scan for secrets
        run: bash scripts/scan-secrets.sh
      - name: Detect network calls
        run: python -m tools.arch_check.network_detector src/backend/app/

  a11y-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate accessibility
        run: python -m tools.arch_check.a11y_validator src/renderer/components/
```

### 10.3 Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: arch-check
        name: Architecture Validation
        entry: python -m tools.arch_check.main
        language: python
        files: \.py$
        pass_filenames: false
```

---

## 11. Violation Severity Levels

### 11.1 Severity Definitions

| Severity | Definition | Response Time | Blocking |
|---|---|---|---|
| **Critical** | Security risk, data loss risk, architecture violation | Immediate fix | Blocks merge |
| **High** | Significant quality issue, major rule violation | Fix within 1 sprint | Blocks merge |
| **Medium** | Code quality issue, minor rule violation | Fix within 2 sprints | Warning |
| **Low** | Style issue, convention violation | Fix opportunistically | Info only |

### 11.2 Violation Response Matrix

| Severity | Developer | Reviewer | CI/CD | Release |
|---|---|---|---|---|
| Critical | Fix immediately | Block merge | Build fails | Release blocked |
| High | Fix before PR | Block merge | Build warning | Must be resolved |
| Medium | Note in PR | Request fix | Warning logged | Track for fix |
| Low | Optional fix | Suggest fix | Info logged | Acknowledge |

### 11.3 Violation Tracking

```json
{
  "violations": [
    {
      "id": "V001",
      "rule": "L001",
      "severity": "critical",
      "file": "src/backend/app/infrastructure/auth.py",
      "line": 15,
      "message": "Infrastructure layer imports from Application layer",
      "created_at": "2026-07-19T10:30:00Z",
      "resolved_at": null,
      "assigned_to": null,
      "status": "open"
    }
  ]
}
```

---

## 12. Remediation Procedures

### 12.1 Critical Violation Remediation

1. **Immediate**: Stop all other work
2. **Identify**: Locate the exact violation and root cause
3. **Assess**: Determine impact (security, data, functionality)
4. **Fix**: Implement the minimum change to resolve
5. **Test**: Verify fix doesn't introduce new violations
6. **Review**: Get expedited code review
7. **Deploy**: Hotfix deployment if in production
8. **Document**: Add to ADR if architectural change needed
9. **Prevent**: Add automated check if one doesn't exist

### 12.2 High Violation Remediation

1. **Plan**: Add to current sprint backlog
2. **Analyze**: Understand why the violation occurred
3. **Fix**: Implement fix with tests
4. **Review**: Standard code review process
5. **Verify**: Run full validation suite
6. **Document**: Update architecture docs if needed

### 12.3 Medium/Low Violation Remediation

1. **Track**: Add to violation tracking system
2. **Batch**: Group related violations for efficient fix
3. **Fix**: Address during regular development
4. **Verify**: Standard validation checks

### 12.4 Recurring Violation Prevention

| Pattern | Prevention |
|---|---|
| Same import violation | Add to linting rules |
| Same naming violation | Add to naming validator |
| Same module isolation violation | Add to module isolation checker |
| Same a11y violation | Add to a11y validator |
| Same security violation | Add to security scanner |

---

## 13. Validation Reporting

### 13.1 Validation Report Structure

```json
{
  "validation_report": {
    "timestamp": "2026-07-19T10:30:00Z",
    "version": "1.0.0",
    "duration_ms": 4500,
    "results": {
      "layer_validation": {
        "status": "pass",
        "violations": 0,
        "checked_files": 342
      },
      "dependency_validation": {
        "status": "pass",
        "violations": 0,
        "circular_dependencies": 0,
        "modules_checked": 25
      },
      "naming_validation": {
        "status": "warning",
        "violations": 3,
        "details": [...]
      },
      "module_isolation": {
        "status": "pass",
        "violations": 0,
        "modules_checked": 25
      },
      "security_validation": {
        "status": "pass",
        "violations": 0,
        "secrets_found": 0,
        "network_calls_found": 0
      },
      "a11y_validation": {
        "status": "pass",
        "violations": 0,
        "components_checked": 156
      }
    },
    "summary": {
      "total_violations": 3,
      "critical": 0,
      "high": 0,
      "medium": 3,
      "low": 0,
      "overall_status": "pass"
    }
  }
}
```

### 13.2 Trend Tracking

| Metric | Baseline | Current | Trend |
|---|---|---|---|
| Total violations | 12 | 3 | Improving |
| Critical violations | 0 | 0 | Stable |
| High violations | 2 | 0 | Improving |
| Medium violations | 10 | 3 | Improving |
| Layer violations | 0 | 0 | Stable |
| Naming violations | 8 | 3 | Improving |
| A11y violations | 5 | 0 | Improving |
| Security violations | 0 | 0 | Stable |
