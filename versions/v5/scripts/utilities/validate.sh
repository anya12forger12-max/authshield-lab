#!/usr/bin/env bash
#
# AuthShield Lab - Validation Script
#
# This script validates the project by running linting, type checking,
# and tests for both backend and frontend.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNED=0

log_info() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED=$((PASSED + 1))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    WARNED=$((WARNED + 1))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAILED=$((FAILED + 1))
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log_step "Checking dependencies..."
    cd "$PROJECT_ROOT"
    
    # Check backend dependencies
    if [ -d "backend/venv" ]; then
        log_info "Backend virtual environment exists."
    else
        log_error "Backend virtual environment not found. Run setup first."
        return 1
    fi
    
    # Check frontend dependencies
    if [ -d "frontend/node_modules" ]; then
        log_info "Frontend node_modules exists."
    else
        log_error "Frontend node_modules not found. Run setup first."
        return 1
    fi
}

# Backend linting
lint_backend() {
    log_step "Linting backend (Python)..."
    cd "$PROJECT_ROOT/backend"
    
    source venv/bin/activate
    
    if ruff check app/ --quiet; then
        log_info "Python linting passed."
    else
        log_error "Python linting failed."
        ruff check app/
    fi
    
    if ruff format --check app/ --quiet; then
        log_info "Python formatting check passed."
    else
        log_warn "Python formatting check failed (run 'ruff format app/' to fix)."
    fi
}

# Backend type checking
typecheck_backend() {
    log_step "Type checking backend (Python)..."
    cd "$PROJECT_ROOT/backend"
    
    source venv/bin/activate
    
    if mypy app/ --ignore-missing-imports; then
        log_info "Python type checking passed."
    else
        log_warn "Python type checking completed with warnings."
    fi
}

# Frontend linting
lint_frontend() {
    log_step "Linting frontend (TypeScript/React)..."
    cd "$PROJECT_ROOT/frontend"
    
    if npm run lint -- --quiet; then
        log_info "TypeScript/React linting passed."
    else
        log_error "TypeScript/React linting failed."
    fi
}

# Frontend type checking
typecheck_frontend() {
    log_step "Type checking frontend (TypeScript)..."
    cd "$PROJECT_ROOT/frontend"
    
    if npm run typecheck; then
        log_info "TypeScript type checking passed."
    else
        log_error "TypeScript type checking failed."
    fi
}

# Backend tests
test_backend() {
    log_step "Running backend tests..."
    cd "$PROJECT_ROOT/backend"
    
    source venv/bin/activate
    
    if python -m pytest tests/ -v --tb=short 2>&1; then
        log_info "Backend tests passed."
    else
        log_error "Backend tests failed."
    fi
}

# Frontend tests
test_frontend() {
    log_step "Running frontend tests..."
    cd "$PROJECT_ROOT/frontend"
    
    if npm run test -- --run 2>&1; then
        log_info "Frontend tests passed."
    else
        log_error "Frontend tests failed."
    fi
}

# Check file structure
check_structure() {
    log_step "Checking project structure..."
    
    local required_dirs=(
        "backend/app"
        "backend/tests"
        "frontend/src"
        "frontend/tests"
        "docs"
        "scripts"
    )
    
    local required_files=(
        "backend/requirements.txt"
        "backend/.env.example"
        "backend/app/main.py"
        "backend/app/config/settings.py"
        "frontend/package.json"
        "frontend/tsconfig.json"
        "frontend/.env.example"
        "README.md"
        "LICENSE"
        "SECURITY.md"
        "CHANGELOG.md"
        "CONTRIBUTING.md"
        "CODE_OF_CONDUCT.md"
        ".gitignore"
        ".editorconfig"
    )
    
    cd "$PROJECT_ROOT"
    
    local structure_ok=true
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            log_info "Directory exists: $dir"
        else
            log_error "Missing directory: $dir"
            structure_ok=false
        fi
    done
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_info "File exists: $file"
        else
            log_error "Missing file: $file"
            structure_ok=false
        fi
    done
}

# Check security
check_security() {
    log_step "Running security checks..."
    cd "$PROJECT_ROOT"
    
    # Check for hardcoded secrets
    if grep -r "password.*=.*['\"]" backend/app/ --include="*.py" -q 2>/dev/null; then
        log_warn "Potential hardcoded passwords found in backend code."
    else
        log_info "No hardcoded passwords found."
    fi
    
    # Check .env not in git
    if git check-ignore backend/.env frontend/.env 2>/dev/null; then
        log_info ".env files are gitignored."
    else
        log_warn ".env files may not be gitignored."
    fi
    
    # Check for secrets in git
    if git log --oneline --all --diff-filter=A -- "*.env" 2>/dev/null | head -1 | grep -q "."; then
        log_warn ".env files may have been committed in the past."
    else
        log_info "No .env files in git history."
    fi
}

# Print summary
print_summary() {
    echo ""
    echo "============================================"
    echo ""
    echo "  Validation Summary"
    echo ""
    echo "============================================"
    echo ""
    echo -e "  ${GREEN}Passed:  $PASSED${NC}"
    echo -e "  ${YELLOW}Warned:  $WARNED${NC}"
    echo -e "  ${RED}Failed:  $FAILED${NC}"
    echo ""
    echo "============================================"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "  ${GREEN}All checks passed!${NC}"
        echo ""
        return 0
    else
        echo -e "  ${RED}Some checks failed. Please fix the issues above.${NC}"
        echo ""
        return 1
    fi
}

# Main validation function
main() {
    echo ""
    echo "============================================"
    echo "  AuthShield Lab - Project Validation"
    echo "============================================"
    echo ""
    
    check_dependencies
    check_structure
    lint_backend
    typecheck_backend
    lint_frontend
    typecheck_frontend
    test_backend
    test_frontend
    check_security
    
    print_summary
}

# Run main function
main "$@"
