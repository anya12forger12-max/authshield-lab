#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

check_version() {
    local cmd="$1"
    local min_version="$2"
    local current_version
    current_version=$("$cmd" --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?')
    if [[ -z "$current_version" ]]; then
        return 1
    fi
    printf '%s\n%s\n' "$min_version" "$current_version" | sort -V -C
}

echo ""
echo "============================================="
echo "  AuthShield Lab - Development Environment"
echo "============================================="
echo ""

# --- Python ---
info "Checking Python..."
if ! command -v python3 &>/dev/null; then
    error "Python 3 is not installed. Please install Python >= 3.12"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if ! check_version python3 "3.12.0"; then
    error "Python >= 3.12 is required. Found: $PYTHON_VERSION"
    exit 1
fi
success "Python $PYTHON_VERSION found"

# --- Virtual Environment ---
VENV_DIR="$REPO_ROOT/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
    info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    success "Virtual environment created at $VENV_DIR"
else
    info "Virtual environment already exists at $VENV_DIR"
fi

# Activate virtual environment
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# --- Python Dependencies ---
info "Installing Python dependencies..."
cd "$REPO_ROOT"
pip install --upgrade pip setuptools wheel -q
pip install -e ".[dev,test,docs]" -q 2>/dev/null || {
    warn "Full install failed, trying minimal install..."
    pip install -r requirements.txt -q 2>/dev/null || warn "No requirements.txt found"
}
success "Python dependencies installed"

# --- Node.js ---
info "Checking Node.js..."
if ! command -v node &>/dev/null; then
    error "Node.js is not installed. Please install Node.js >= 20"
    exit 1
fi

NODE_VERSION=$(node --version | tr -d 'v')
if ! check_version node "20.0.0"; then
    error "Node.js >= 20 is required. Found: $NODE_VERSION"
    exit 1
fi
success "Node.js $NODE_VERSION found"

# --- npm ---
if ! command -v npm &>/dev/null; then
    error "npm is not installed"
    exit 1
fi
NPM_VERSION=$(npm --version)
success "npm $NPM_VERSION found"

# --- Node Dependencies ---
info "Installing Node.js dependencies..."
cd "$REPO_ROOT"
if [[ -f "pnpm-lock.yaml" ]]; then
    info "Using pnpm..."
    if ! command -v pnpm &>/dev/null; then
        npm install -g pnpm
    fi
    pnpm install
elif [[ -f "yarn.lock" ]]; then
    info "Using yarn..."
    yarn install --frozen-lockfile
else
    npm ci 2>/dev/null || npm install
fi
success "Node.js dependencies installed"

# --- Pre-commit ---
info "Setting up pre-commit hooks..."
if command -v pre-commit &>/dev/null; then
    pre-commit install
    pre-commit install --hook-type commit-msg
    success "Pre-commit hooks installed"
else
    warn "pre-commit not found, installing..."
    pip install pre-commit -q
    pre-commit install
    pre-commit install --hook-type commit-msg
    success "Pre-commit hooks installed"
fi

# --- Initial Checks ---
info "Running initial validation checks..."
echo ""

info "Running ruff linter..."
ruff check src/ tests/ 2>/dev/null || warn "Ruff found issues or is not configured"
success "Ruff check complete"

info "Running mypy type checker..."
mypy src/ 2>/dev/null || warn "Mypy found issues or is not configured"
success "Mypy check complete"

info "Running prettier format check..."
if [[ -d "packages" ]]; then
    npx prettier --check "packages/**/*.{ts,tsx,js,jsx,json,css,scss}" 2>/dev/null || warn "Prettier found formatting issues"
fi
success "Prettier check complete"

echo ""
echo "============================================="
echo "  Setup Complete!"
echo "============================================="
echo ""
echo "  Next steps:"
echo "    1. Activate the virtual environment:"
echo "       source .venv/bin/activate"
echo ""
echo "    2. Start the backend server:"
echo "       uvicorn authshield.app:app --reload"
echo ""
echo "    3. Start the Electron app:"
echo "       cd packages/electron && npm run dev"
echo ""
echo "    4. Run the test suite:"
echo "       pytest"
echo ""
echo "    5. Run all linting:"
echo "       pre-commit run --all-files"
echo ""
echo "  Documentation:"
echo "    docs/ - Project documentation"
echo "    README.md - Getting started"
echo "============================================="
