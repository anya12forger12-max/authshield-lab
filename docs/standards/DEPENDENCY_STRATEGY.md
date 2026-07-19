# AuthShield Lab — Dependency Management Strategy

> Version: 1.0.0 | Last Updated: 2026-07-19 | Status: Approved

## 1. Overview

AuthShield Lab operates as an offline-first platform with strict security requirements. This dependency management strategy ensures reproducible builds, supply chain security, offline capability, and minimal attack surface.

---

## 2. Python Dependencies

### 2.1 Project Configuration: pyproject.toml

```toml
[project]
name = "authshield-lab"
version = "1.0.0"
requires-python = ">=3.12,<4.0"
dependencies = [
    "fastapi>=0.111,<0.112",
    "uvicorn[standard]>=0.30,<0.31",
    "sqlalchemy[asyncio]>=2.0,<2.1",
    "aiosqlite>=0.20,<0.21",
    "pydantic>=2.7,<2.8",
    "pydantic-settings>=2.2,<2.3",
    "structlog>=24.1,<24.2",
    "httpx>=0.27,<0.28",
    "python-jose[cryptography]>=3.3,<3.4",
    "passlib[argon2]>=1.7.4,<1.8",
    "argon2-cffi>=23.1,<24.0",
    "cryptography>=42,<43",
    "jinja2>=3.1,<3.2",
    "weasyprint>=62,<63",
    "orjson>=3.10,<3.11",
    "aiofiles>=24.1,<24.2",
    "babel>=2.15,<2.16",
    "tomli>=2.0,<2.1; python_version < '3.11'",
    "tomllib; python_version >= '3.11'",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0,<8.1",
    "pytest-asyncio>=0.23,<0.24",
    "pytest-cov>=5.0,<5.1",
    "ruff>=0.4,<0.5",
    "mypy>=1.10,<1.11",
    "pip-audit>=2.7,<2.8",
    "pip-tools>=7.4,<7.5",
]
windows = [
    "pywin32>=306,<307",
]
postgresql = [
    "asyncpg>=0.29,<0.30",
    "psycopg2-binary>=2.9,<2.10",
]
msgpack = [
    "msgpack>=1.8,<1.9",
]
scheduling = [
    "apscheduler>=3.10,<3.11",
]
di = [
    "dependency-injector>=4.41,<4.42",
]
rust = [
    "authshield-core>=0.1.0",
]

[project.scripts]
authshield = "authshield.cli:main"

[project.entry-points."authshield.plugins"]
example = "authshield_plugins.example:ExamplePlugin"

[project.entry-points."authshield.routes"]
example = "authshield_plugins.example.routes:router"

[project.entry-points."authshield.themes"]
default = "authshield_plugins.default_theme:DefaultTheme"
```

### 2.2 Version Pinning Strategy

| Environment | Pinning strategy | Rationale |
|-------------|-----------------|-----------|
| **Production** | Exact versions (`==`) in lock file | Reproducible builds; no surprise behavior |
| **Development** | Compatible ranges (`>=X,<X+1`) in `pyproject.toml` | Allow patch/minor updates during development |
| **CI/CD** | Lock file (exact versions) | Deterministic builds; cache-friendly |
| **Developer machine** | Lock file (exact versions) | Match production exactly |

**Lock file generation:**

```bash
# Generate lock file
pip-compile --strip-extras --output-file=requirements.lock pyproject.toml

# Regenerate with latest compatible versions
pip-compile --upgrade --strip-extras --output-file=requirements.lock pyproject.toml

# Install from lock file
pip install -r requirements.lock

# Verify lock file consistency
pip check
```

### 2.3 Dependency Auditing

```bash
# Audit for known vulnerabilities
pip-audit --require-hashes --desc

# Audit with fix suggestions
pip-audit --fix

# Generate SBOM
pip-audit --format cyclonedx --output sbom.json
```

**CI/CD integration:**

```yaml
# .github/workflows/security.yml
- name: Audit Python dependencies
  run: |
    pip-audit --require-hashes --strict
    pip-audit --format cyclonedx --output sbom-python.json

- name: Verify lock file hashes
  run: |
    pip install --require-hashes -r requirements.lock --dry-run
```

### 2.4 Private Registry (optional)

```toml
# pyproject.toml
[tool.uv]
index-url = "https://pypi.org/simple"
extra-index-url = "https://internal-registry.authshield.dev/simple"

# Or for pip
# pip.conf
[global]
index-url = https://pypi.org/simple
extra-index-url = https://internal-registry.authshield.dev/simple
trusted-host = internal-registry.authshield.dev
```

### 2.5 Vendoring Critical Dependencies

For offline-first deployment, critical dependencies are vendored:

```
vendor/
├── python/
│   ├── cryptography/      # Cryptographic primitives
│   ├── argon2/            # Password hashing
│   ├── passlib/           # Password hashing abstraction
│   ├── jose/              # JWT handling
│   └── pydantic/          # Data validation
└── verify/
    └── checksums.sha256   # Vendored dependency checksums
```

**Vendoring process:**

```bash
# Download all dependencies to vendor directory
pip download --dest=vendor/python -r requirements-vendor.txt

# Generate checksums
cd vendor/python && sha256sum *.whl *.tar.gz > ../verify/checksums.sha256

# Verify vendor integrity
cd vendor && sha256sum -c verify/checksums.sha256
```

### 2.6 Offline Cache

```bash
# Populate pip cache
pip cache populate --packages

# Create local mirror
pip download --dest=offline-cache/ -r requirements.lock

# Install from offline cache
pip install --no-index --find-links=offline-cache/ -r requirements.lock
```

---

## 3. Node.js Dependencies

### 3.1 Package Configuration: package.json

```json
{
  "name": "authshield-lab-desktop",
  "version": "1.0.0",
  "private": true,
  "description": "AuthShield Lab Desktop Application",
  "main": "dist/main/index.js",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint src/ --ext .ts,.tsx",
    "lint:fix": "eslint src/ --ext .ts,.tsx --fix",
    "format": "prettier --write src/",
    "typecheck": "tsc --noEmit",
    "electron:build": "electron-builder",
    "electron:build:win": "electron-builder --win",
    "electron:build:mac": "electron-builder --mac",
    "electron:build:linux": "electron-builder --linux",
    "audit": "npm audit --audit-level=high",
    "audit:fix": "npm audit fix",
    "sbom": "cyclonedx-npm --output-file sbom-node.json"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "zustand": "^4.5.0",
    "react-router-dom": "^6.23.0",
    "electron-store": "^8.2.0",
    "axe-core": "^4.9.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@types/node": "^20.12.0",
    "typescript": "^5.3.0",
    "vite": "^5.4.0",
    "@vitejs/plugin-react": "^4.3.0",
    "vitest": "^2.0.0",
    "@testing-library/react": "^15.0.0",
    "@testing-library/jest-dom": "^6.4.0",
    "playwright": "^1.44.0",
    "electron": "^28.0.0",
    "electron-builder": "^25.0.0",
    "electron-updater": "^6.1.0",
    "eslint": "^9.0.0",
    "@typescript-eslint/eslint-plugin": "^8.0.0",
    "@typescript-eslint/parser": "^8.0.0",
    "prettier": "^3.2.0"
  },
  "engines": {
    "node": ">=20.0.0",
    "npm": ">=10.0.0"
  }
}
```

### 3.2 Package Manager Selection

| Manager | Decision | Rationale |
|---------|----------|-----------|
| **npm** | Default choice | Bundled with Node.js; largest ecosystem; `npm ci` for reproducible installs |
| **pnpm** | Alternative (evaluated) | Disk-efficient (content-addressable store); stricter dependency resolution |
| **yarn** | Not adopted | Berry (v4) has good features but ecosystem fragmentation; npm is sufficient |

**Lock file strategy:**

| File | Strategy |
|------|----------|
| `package-lock.json` | Exact versions; regenerated monthly; committed to git |
| `.npmrc` | `save-exact=true` for exact version pinning in package.json |

### 3.3 Dependency Auditing

```bash
# Audit for vulnerabilities
npm audit --audit-level=high

# Audit and fix (non-breaking)
npm audit fix

# Generate SBOM
npx cyclonedx-npm --output-file sbom-node.json
```

**CI/CD integration:**

```yaml
- name: Audit Node.js dependencies
  run: |
    npm ci
    npm audit --audit-level=critical --audit-level=high

- name: Generate SBOM
  run: npx cyclonedx-npm --output-file sbom-node.json
```

### 3.4 Offline Cache

```bash
# Populate npm cache
npm cache add --all

# Install from cache (no network)
npm ci --prefer-offline

# Verify cache integrity
npm cache verify
```

### 3.5 Electron-Specific Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| electron | ≥ 28 | Desktop shell |
| electron-builder | ≥ 25 | Packaging |
| electron-updater | ≥ 6.1 | Auto-updates (disabled by default) |
| electron-store | ≥ 8.2 | Persistent storage |
| @electron/remote | Not used | Security: prefer IPC |

**Security rule:** Never use `@electron/remote`. Always use IPC with `contextBridge`.

---

## 4. Rust Dependencies (optional)

### 4.1 Cargo.toml

```toml
[package]
name = "authshield-core"
version = "0.1.0"
edition = "2021"
rust-version = "1.77"

[lib]
name = "authshield_core"
crate-type = ["cdylib", "rlib"]

[dependencies]
pyo3 = { version = "0.21", features = ["extension-module"] }
ed25519-dalek = "2.1"
sha2 = "0.10"
argon2 = "0.5"
rand = "0.8"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
msgpack-serde = "1.3"
brotli = "6.0"
tokio = { version = "1.0", features = ["full"] }

[dev-dependencies]
criterion = "0.5"
proptest = "1.4"
```

### 4.2 Rust Dependency Auditing

```bash
# Audit for known vulnerabilities
cargo audit

# Audit with fix suggestions
cargo audit fix

# Vendor dependencies for offline build
cargo vendor --versioned-dirs vendor/
```

### 4.3 Offline Build

```bash
# Vendor all dependencies
cargo vendor --versioned-dirs vendor/

# Build offline
CARGO_HOME=$(pwd)/.cargo cargo build --release

# Configure cargo to use vendored deps
mkdir -p .cargo
cat > .cargo/config.toml << 'EOF'
[source.crates-io]
replace-with = "vendored"

[source.vendored]
directory = "vendor"
EOF
```

---

## 5. Dependency Security

### 5.1 Hash Verification

```bash
# Python: requirements.lock with hashes
pip-compile --generate-hashes --output-file=requirements.lock pyproject.toml

# Verify hashes on install
pip install --require-hashes -r requirements.lock

# Node.js: package-lock.json contains integrity hashes
npm ci  # Uses lock file hashes automatically

# Rust: cargo-audit checks known vulnerabilities
cargo audit
```

### 5.2 Supply Chain Security

| Measure | Implementation |
|---------|---------------|
| **Dependency pinning** | Exact versions in lock files; ranges only in pyproject.toml/package.json |
| **Hash verification** | Python `--generate-hashes`; npm integrity hashes; Cargo.lock checksums |
| **Vulnerability scanning** | `pip-audit`, `npm audit`, `cargo-audit` in CI/CD |
| **SBOM generation** | `cyclonedx` format; generated per release; attached to GitHub releases |
| **Signed releases** | Ed25519 signatures for release artifacts |
| **Minimal dependencies** | Regular review of dependency necessity; remove unused |
| **Vendor critical deps** | Cryptography, password hashing, accessibility libraries vendored |

### 5.3 Dependency Review Process

```yaml
# .github/workflows/dependency-review.yml
name: Dependency Review
on: pull_request
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Review Python dependencies
        run: |
          pip install pip-audit
          pip-audit --require-hashes --strict
      - name: Review Node dependencies
        run: |
          npm ci
          npm audit --audit-level=critical
      - name: Review Rust dependencies
        if: hashFiles('Cargo.toml') != ''
        run: |
          cargo install cargo-audit
          cargo audit
```

---

## 6. Update Policy

### 6.1 Update Schedule

| Type | Frequency | Process |
|------|-----------|---------|
| **Security patches** | Within 48 hours | Automated Dependabot/Renovate PRs; expedited review |
| **Patch updates** | Monthly | Review changelog; test in CI; merge if green |
| **Minor updates** | Quarterly | Feature evaluation; compatibility testing |
| **Major updates** | Annually | Migration planning; staged rollout; extended testing |

### 6.2 Update Process

```bash
# 1. Check for outdated dependencies
pip list --outdated
npm outdated
cargo outdated  # requires cargo-outdated plugin

# 2. Update lock file (Python)
pip-compile --upgrade --strip-extras --output-file=requirements.lock pyproject.toml

# 3. Update lock file (Node)
npm update
npm audit fix

# 4. Update lock file (Rust)
cargo update

# 5. Run full test suite
pytest --cov
npm test
cargo test

# 6. Audit updated dependencies
pip-audit --require-hashes
npm audit
cargo audit
```

### 6.3 Breaking Change Policy

| Breaking change type | Action |
|---------------------|--------|
| **API breaking** | Major version bump; migration guide; 6-month compatibility window |
| **Behavioral breaking** | Minor version bump; changelog documentation |
| **Configuration breaking** | Config migration script; backward-compatible defaults |
| **Database schema** | Alembic migration; backward-compatible column additions; no destructive migrations |

---

## 7. Offline Build Strategy

### 7.1 Pre-build Cache Population

```bash
#!/bin/bash
# scripts/populate-offline-cache.sh

set -euo pipefail

CACHE_DIR="offline-cache"
mkdir -p "$CACHE_DIR/python" "$CACHE_DIR/node" "$CACHE_DIR/rust"

# Python: download all dependencies
pip download \
    --dest="$CACHE_DIR/python" \
    -r requirements.lock

# Node: pack all dependencies
npm pack --pack-destination="$CACHE_DIR/node"

# Rust: vendor all dependencies
cargo vendor --versioned-dirs="$CACHE_DIR/rust/vendor"

# Generate integrity manifest
find "$CACHE_DIR" -type f -exec sha256sum {} \; > "$CACHE_DIR/SHA256SUMS"

echo "Offline cache populated at $CACHE_DIR"
echo "Size: $(du -sh "$CACHE_DIR" | cut -f1)"
```

### 7.2 Offline Build

```bash
#!/bin/bash
# scripts/offline-build.sh

set -euo pipefail

CACHE_DIR="offline-cache"

# Verify cache integrity
sha256sum -c "$CACHE_DIR/SHA256SUMS"

# Python: install from cache
pip install \
    --no-index \
    --find-links="$CACHE_DIR/python" \
    -r requirements.lock

# Node: install from cache
npm ci --prefer-offline

# Rust: build with vendored dependencies
CARGO_HOME=$(pwd)/.cargo cargo build --release

echo "Offline build complete"
```

---

## 8. Dependency Metrics

### 8.1 Tracked Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Python dependencies** | < 30 direct | `pip list --format=columns` |
| **Node dependencies** | < 50 direct | `npm ls --depth=0` |
| **Total transitive** | < 200 | `pipdeptree` / `npm ls` |
| **Known vulnerabilities** | 0 critical/high | `pip-audit` / `npm audit` |
| **Outdated (security)** | 0 within 48h | Dependabot alerts |
| **Outdated (feature)** | < 10% within 3 months | `pip list --outdated` |

### 8.2 Dependency Health Dashboard

```bash
# Generate dependency health report
pip list --format=json > deps-python.json
npm ls --json > deps-node.json
cargo tree --depth=1 --edges normal > deps-rust.txt

# Vulnerability summary
pip-audit --format=json > vuln-python.json
npm audit --json > vuln-node.json
cargo audit --json > vuln-rust.json
```

---

## 9. CI/CD Integration

### 9.1 Full Dependency Pipeline

```yaml
# .github/workflows/dependencies.yml
name: Dependency Management
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 1 * *'  # Monthly

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Audit Python
        run: |
          pip install pip-audit
          pip-audit --require-hashes --strict
      - name: Audit Node
        run: |
          npm ci
          npm audit --audit-level=high
      - name: Generate SBOMs
        run: |
          pip install cyclonedx-bom
          cyclonedx-py environment --output-file sbom-python.json
          npx cyclonedx-npm --output-file sbom-node.json
      - name: Upload SBOMs
        uses: actions/upload-artifact@v4
        with:
          name: sboms
          path: sbom-*.json
```

---

## 10. Rollback Strategy

### 10.1 Dependency Rollback

```bash
# Python: revert to previous lock file
git checkout HEAD~1 -- requirements.lock
pip install -r requirements.lock

# Node: revert to previous lock file
git checkout HEAD~1 -- package-lock.json
npm ci

# Rust: revert Cargo.lock
git checkout HEAD~1 -- Cargo.lock
cargo build
```

### 10.2 Emergency Patch Process

1. Create hotfix branch from release tag
2. Cherry-pick security fix (or pin vulnerable dependency version)
3. Update lock file with fix
4. Run full test suite
5. Audit for additional vulnerabilities
6. Release patch version
7. Merge hotfix back to main

---

*Document maintained by the AuthShield Lab Architecture Team. Review quarterly.*
