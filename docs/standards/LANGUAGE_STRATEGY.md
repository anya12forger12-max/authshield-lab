# AuthShield Lab — Programming Language Strategy

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab uses a polyglot architecture with three programming languages, each chosen for specific strengths. This document defines the rationale, usage boundaries, and long-term strategy for each language.

---

## 2. Primary: Python 3.12+

### 2.1 Selection Rationale

| Criterion | Assessment |
|-----------|------------|
| **Domain fit** | Python dominates cybersecurity tooling, scripting, and automation. Libraries like `cryptography`, `paramiko`, `scapy`, and `nmap` are Python-native. Security researchers and educators predominantly use Python. |
| **Developer availability** | Python is the most popular language in cybersecurity education; hiring pool is large. |
| **Library ecosystem** | 400,000+ PyPI packages; mature libraries for every requirement (web, async, crypto, testing, reporting). |
| **Offline-first** | Single-file deployment via PyInstaller; no runtime compilation required; `importlib` for dynamic loading. |
| **Type safety** | PEP 484 type hints + mypy strict mode provide compile-time safety without sacrificing runtime flexibility. |
| **Async support** | `asyncio` native since Python 3.4; `async`/`await` syntax since 3.5; mature async libraries (FastAPI, SQLAlchemy, httpx, aiofiles). |
| **Cross-platform** | Official CPython distributions for Windows, macOS, Linux; `pathlib` for OS-agnostic file operations. |

### 2.2 Usage Boundaries

| Component | Python responsibility |
|-----------|----------------------|
| Backend API | FastAPI routes, middleware, dependency injection |
| Database layer | SQLAlchemy models, migrations, queries |
| Business logic | Authentication, session management, assessment engine |
| Services | Learning engine, simulation engine, reporting |
| Plugin system | Plugin discovery, loading, lifecycle management |
| CLI | Command-line interface (argparse or click) |
| SDK | Python SDK for plugin developers |
| Testing | pytest test suites, fixtures, mocking |
| Build scripts | Packaging, compilation, CI/CD scripts |

### 2.3 Version Strategy

| Version | Status | Target |
|---------|--------|--------|
| Python 3.12 | Primary target | Production releases |
| Python 3.11 | Minimum supported | Backward compatibility |
| Python 3.13 | Evaluation | Preview features (free-threaded, `tomllib` improvements) |

**Drop policy:** Drop support 24 months after Python release reaches end-of-life.

### 2.4 Performance Characteristics

- **Startup time:** ~100ms (interpreter + stdlib import)
- **Async I/O throughput:** 10,000+ concurrent connections via uvicorn
- **CPU-bound:** Single-threaded; GIL limits parallelism (mitigated by `multiprocessing`, `concurrent.futures`, or Rust extensions)
- **Memory:** ~30MB base; ~100MB with full stack loaded

### 2.5 Security Posture

- **Input validation:** Pydantic v2 validates all external input
- **Type checking:** mypy strict mode catches type errors at build time
- **Dependency auditing:** `pip-audit` in CI/CD pipeline
- **Code signing:** Ed25519 signatures for release packages
- **No `eval()`/`exec()` with user input:** Strict prohibition enforced by ruff rules

### 2.6 Tooling

| Tool | Purpose | Version |
|------|---------|---------|
| ruff | Linting + formatting | ≥ 0.4 |
| mypy | Static type checking | ≥ 1.10 |
| pytest | Testing framework | ≥ 8.0 |
| pip-audit | Dependency security | ≥ 2.7 |
| pip-compile | Lock file generation | ≥ 7.4 |
| pyinstaller | Executable packaging | ≥ 6.5 |

### 2.7 Learning Curve

- **Onboarding:** 1-2 weeks for Python-proficient developers
- **Async patterns:** 2-3 weeks for developers new to `asyncio`
- **Pydantic v2:** 1 week migration from v1 patterns
- **FastAPI:** 1-2 weeks for developers familiar with Flask/Django

---

## 3. Secondary: TypeScript 5.3+

### 3.1 Selection Rationale

| Criterion | Assessment |
|-----------|------------|
| **Electron integration** | TypeScript is the primary language for Electron development; native Chromium V8 support; source maps for debugging. |
| **Type safety** | Compile-time type checking prevents runtime errors; structural typing enables API contract sharing with Python Pydantic models. |
| **React ecosystem** | React + TypeScript is the dominant combination for enterprise applications; types ensure component prop safety. |
| **DX** | IDE autocomplete, refactoring, go-to-definition, inline documentation; catches bugs before runtime. |
| **ECMAScript alignment** | TypeScript follows ECMAScript proposals; ensures forward compatibility with JavaScript standards. |
| **Package ecosystem** | npm has 2M+ packages; TypeScript-native packages dominate for modern tooling (Vite, Vitest, Playwright). |

### 3.2 Usage Boundaries

| Component | TypeScript responsibility |
|-----------|------------------------|
| Electron renderer | React UI components, state management, routing |
| Electron main process | App lifecycle, window management, IPC, auto-update |
| Preload scripts | Secure context bridge between renderer and main |
| Shared types | Type definitions shared between frontend and backend (via OpenAPI codegen or manual `types.ts`) |
| Build configuration | Vite config, TypeScript config, ESLint config |
| E2E tests | Playwright tests for Electron UI |
| Unit tests | Vitest tests for React components and utilities |

### 3.3 Version Strategy

| Version | Status | Target |
|---------|--------|--------|
| TypeScript 5.3 | Primary target | Production releases |
| TypeScript 5.4+ | Evaluation | New features (e.g., `satisfies` improvements, decorators) |

**ECMAScript target:** ES2022 (Chromium 130+ supports all ES2022 features natively).

### 3.4 Performance Characteristics

- **V8 JIT compilation:** Near-native execution speed for JavaScript
- **Type erasure:** TypeScript types are erased at compile time (zero runtime cost)
- **Bundle size:** ~200KB gzipped for full React app (code-split by route)
- **Startup time:** ~200ms (Vite dev server) / ~100ms (production bundle)

### 3.5 Security Posture

- **Strict mode:** `"strict": true` in `tsconfig.json` enables all strict type checks
- **No implicit any:** All variables/functions require explicit types
- **ESLint rules:** `@typescript-eslint/recommended` + custom rules for security patterns
- **Context isolation:** `contextBridge` + `sandbox: true` in Electron preload
- **CSP headers:** Content Security Policy enforced in Electron BrowserWindow

### 3.6 Tooling

| Tool | Purpose | Version |
|------|---------|---------|
| Vite | Build tool + dev server | ≥ 5.4 |
| SWC | TypeScript compilation (optional) | ≥ 1.6 |
| ESLint | Linting | ≥ 9.0 |
| Prettier | Formatting | ≥ 3.2 |
| Vitest | Unit testing | ≥ 2.0 |
| Playwright | E2E testing | ≥ 1.44 |
| electron-builder | Packaging | ≥ 25.0 |
| TypeScript | Type checking | ≥ 5.3 |

### 3.7 Learning Curve

- **Onboarding:** 1-2 weeks for TypeScript-proficient developers
- **React + TypeScript:** 1-2 weeks for developers new to React
- **Electron IPC:** 2-3 weeks for understanding main/renderer/preload architecture
- **Shared types:** 1 week for Pydantic → TypeScript type generation

---

## 4. Tertiary: Rust (optional)

### 4.1 Selection Rationale

| Criterion | Assessment |
|-----------|------------|
| **Performance-critical paths** | Cryptographic operations, data serialization, compression, heavy computation |
| **Security** | Memory safety without garbage collection; no null pointer dereferences; no data races at compile time |
| **WASM potential** | Rust compiles to WebAssembly for browser/Node.js integration |
| **PyO3 integration** | `PyO3` crate enables native Python extension modules |
| **Community growth** | Rust is the most admired language (Stack Overflow Survey); growing cybersecurity tooling ecosystem |
| **Binary size** | Statically linked executables; no runtime dependencies |

### 4.2 Usage Boundaries

| Component | Rust responsibility | Priority |
|-----------|-------------------|----------|
| Cryptographic primitives | Ed25519/RSA signature generation, key derivation | Low (Python `cryptography` is sufficient) |
| Data serialization | High-performance msgpack/JSON encoding/decoding | Low (Python `orjson` is sufficient) |
| Compression | Fast gzip/brotli compression for report bundles | Low (Python `zlib` is sufficient) |
| Hash computation | Large-file SHA-256 for integrity verification | Medium (when processing multi-GB files) |
| Password hashing | Parallel Argon2id batch verification | Low (single-password verification is fast enough) |

### 4.3 Integration Strategy

```
Rust → Python (PyO3):
├── Compile as Python extension module (.so/.pyd)
├── Publish as separate wheel per platform
├── Optional dependency: falls back to pure Python
└── Build via maturin (Rust ↔ Python build tool)

Rust → WASM:
├── Compile to wasm32-wasi target
├── Bundle as Node.js native addon or WASM module
├── Used in Electron renderer for CPU-intensive operations
└── Build via wasm-pack
```

### 4.4 Version Strategy

| Component | Status | Target |
|-----------|--------|--------|
| Rust toolchain | Stable channel | Latest stable release |
| PyO3 | ≥ 0.21 | Python 3.12 compatibility |
| wasm-pack | ≥ 0.12 | WASM compilation |
| maturin | ≥ 1.7 | Python extension building |

### 4.5 Performance Characteristics

- **Compilation:** Slower than Python/TypeScript (mitigated by incremental compilation, `cargo check` for type-only verification)
- **Runtime:** 10-100x faster than Python for CPU-bound tasks; near C performance
- **Memory:** No garbage collector; predictable memory usage; zero-cost abstractions
- **Binary size:** ~1-5MB for typical extension module

### 4.6 Security Posture

- **Memory safety:** Borrow checker prevents use-after-free, double-free, buffer overflows
- **No unsafe by default:** `unsafe` blocks require explicit annotation and code review
- **Dependency auditing:** `cargo-audit` in CI/CD pipeline
- **Supply chain:** `cargo-vendor` for vendored dependencies; `cargo-sign` for signed releases

### 4.7 Tooling

| Tool | Purpose | Version |
|------|---------|---------|
| cargo | Build system + package manager | Stable channel |
| clippy | Linting | ≥ 1.77 |
| rustfmt | Formatting | ≥ 1.77 |
| cargo-audit | Dependency security | ≥ 0.20 |
| cargo-tarpaulin | Code coverage | ≥ 0.27 |
| pyo3 | Python bindings | ≥ 0.21 |
| wasm-pack | WASM compilation | ≥ 0.12 |
| maturin | Python extension building | ≥ 1.7 |

### 4.8 Learning Curve

- **Onboarding:** 4-8 weeks for Python/TypeScript developers new to Rust
- **Ownership model:** 2-4 weeks to internalize borrow checker patterns
- **PyO3 integration:** 1-2 weeks for basic Python bindings
- **Recommendation:** Rust components should be developed by team members with Rust experience; not required for core team

### 4.9 Long-term Viability

- Rust has strong corporate backing (Mozilla, Microsoft, Google, Amazon)
- Rust Foundation ensures governance and funding
- Growing adoption in security-critical systems (Linux kernel, Android, Windows)
- Risk: Rust ecosystem for cybersecurity is smaller than Python (mitigated by Rust→Python bridge)

---

## 5. Configuration Languages

### 5.1 TOML

| Attribute | Detail |
|-----------|--------|
| **Role** | Primary configuration format for Python and Rust projects |
| **Files** | `pyproject.toml`, `Cargo.toml`, `.authshield-lab/config.toml`, `plugin.toml` |
| **Justification** | Python 3.11+ `tomllib` (stdlib); human-readable; comments supported; nested structures; used by Python ecosystem standard (`pyproject.toml`). |
| **Parser** | `tomllib` (Python 3.11+), `toml` (npm), `toml-rs` (Rust) |

### 5.2 YAML

| Attribute | Detail |
|-----------|--------|
| **Role** | Plugin manifests, CI/CD configuration, Docker Compose |
| **Files** | `plugin.yaml`, `.github/workflows/*.yml`, `docker-compose.yml` |
| **Justification** | Human-readable; comments preserved; anchors/aliases; widely used in DevOps; GitHub Actions native format. |
| **Parser** | `ruamel.yaml` (Python), `js-yaml` (Node.js), `serde_yaml` (Rust) |

### 5.3 JSON

| Attribute | Detail |
|-----------|--------|
| **Role** | Translation files, API payloads, lock files |
| **Files** | `translations/*.json`, `package-lock.json`, `pnpm-lock.yaml` |
| **Justification** | Machine-readable; no comments (by design); native JavaScript; universal parser support; `orjson` for fast Python parsing. |
| **Parser** | `orjson` / `json` (Python), `JSON.parse()` (JavaScript), `serde_json` (Rust) |

---

## 6. Documentation Languages

### 6.1 Markdown

| Attribute | Detail |
|-----------|--------|
| **Role** | Primary documentation format |
| **Files** | `*.md`, `README.md`, `CHANGELOG.md`, `docs/**/*.md` |
| **Justification** | Git-native (diffs, blame); GitHub/GitLab rendering; tooling support (mdbook, mkdocs); low barrier to contribution. |
| **Extensions** | GitHub Flavored Markdown (GFM): tables, task lists, syntax highlighting, admonitions |
| **Linting** | `markdownlint` (CLI) or `markdownlint-cli2` |

### 6.2 reStructuredText

| Attribute | Detail |
|-----------|--------|
| **Role** | API reference documentation (Sphinx) |
| **Files** | `docs/api/**/*.rst` |
| **Justification** | Sphinx native format; cross-references; `autodoc` for Python docstring extraction; `doctest` for code examples. |
| **Alternative** | Consider `mkdocs` + `mkdocstrings` (Markdown-based API docs) if rST adoption is low |

---

## 7. Shell Languages

### 7.1 Bash (Linux/macOS)

| Attribute | Detail |
|-----------|--------|
| **Role** | Build scripts, CI/CD, setup scripts, developer tooling |
| **Files** | `scripts/*.sh`, `setup.sh`, `Makefile` |
| **Justification** | POSIX standard; available on all Unix-like systems; `shellcheck` for linting; `bash` is default on macOS (despite zsh). |
| **Linting** | `shellcheck` (static analysis for common bugs) |
| **Style** | Google Shell Style Guide; `shfmt` for formatting |

### 7.2 PowerShell (Windows)

| Attribute | Detail |
|-----------|--------|
| **Role** | Windows-specific build scripts, setup, administration |
| **Files** | `scripts/*.ps1`, `setup.ps1`, `install.ps1` |
| **Justification** | Native Windows automation; .NET integration; `PowerShell 7+` is cross-platform; `PSScriptAnalyzer` for linting. |
| **Linting** | `PSScriptAnalyzer` (static analysis) |
| **Style** | PowerShell Best Practices and Style Guide |

### 7.3 Cross-platform Scripting

| Approach | Implementation |
|----------|---------------|
| **Makefile** | `make` targets for common tasks; works on Linux, macOS, Windows (via Git Bash or WSL) |
| **Python scripts** | `scripts/*.py` for cross-platform build/setup tasks |
| **npm scripts** | `package.json` scripts for frontend tasks (build, test, lint) |

---

## 8. Type Sharing Strategy

### 8.1 Python ↔ TypeScript

```python
# Python Pydantic model
class AssessmentResult(BaseModel):
    id: str
    score: float
    timestamp: datetime
    module_id: str
    user_id: str
```

```typescript
// TypeScript interface (generated from OpenAPI schema)
interface AssessmentResult {
  id: string;
  score: number;
  timestamp: string; // ISO 8601
  module_id: string;
  user_id: string;
}
```

**Mechanism:** FastAPI generates OpenAPI schema → TypeScript types generated via `openapi-typescript` or `openapi-generator-cli`.

### 8.2 Python ↔ Rust

```rust
// Rust struct (PyO3)
#[pyclass]
struct AssessmentResult {
    id: String,
    score: f64,
    timestamp: String,
    module_id: String,
    user_id: String,
}
```

**Mechanism:** PyO3 `#[pyclass]`/`#[pymethods]` annotations expose Rust structs to Python.

---

## 9. Language Selection Decision Matrix

| Criteria | Weight | Python | TypeScript | Rust |
|----------|--------|--------|------------|------|
| Backend development | 25% | ★★★★★ | ★★☆☆☆ | ★★★☆☆ |
| Frontend development | 25% | ★★☆☆☆ | ★★★★★ | ★☆☆☆☆ |
| Security tooling | 15% | ★★★★★ | ★★☆☆☆ | ★★★★☆ |
| Performance | 15% | ★★☆☆☆ | ★★★★☆ | ★★★★★ |
| Developer availability | 10% | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| Offline-first | 10% | ★★★★★ | ★★★★☆ | ★★★★★ |

**Conclusion:** Python is the primary language for backend/services; TypeScript is the primary language for frontend/Electron; Rust is optional for performance-critical extensions.

---

## 10. Migration & Evolution Strategy

| Timeline | Action |
|----------|--------|
| **Q1 2026** | Establish Python + TypeScript foundation; core backend and Electron shell |
| **Q2 2026** | Evaluate Rust extensions for crypto/serialization benchmarks |
| **Q3 2026** | Adopt Python 3.13 features (free-threaded mode evaluation) |
| **Q4 2026** | Evaluate WebAssembly for browser-based simulation engine |
| **2027** | Consider Python 3.14+ if stable; evaluate Deno/Bun for Electron alternatives |
| **2028** | Major version review; evaluate language strategy effectiveness |

---

*Document maintained by the AuthShield Lab Architecture Team. Review quarterly.*
