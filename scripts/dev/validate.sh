#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0
SKIP=0

run_check() {
    local name="$1"
    shift
    echo -e "\n${BLUE}━━━ $name ━━━${NC}"
    if "$@"; then
        echo -e "${GREEN}✓ PASS${NC}: $name"
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC}: $name"
        ((FAIL++))
    fi
}

run_check_optional() {
    local name="$1"
    shift
    echo -e "\n${BLUE}━━━ $name ━━━${NC}"
    if "$@"; then
        echo -e "${GREEN}✓ PASS${NC}: $name"
        ((PASS++))
    elif [[ $? -eq 127 ]]; then
        echo -e "${YELLOW}⊘ SKIP${NC}: $name (not installed)"
        ((SKIP++))
    else
        echo -e "${RED}✗ FAIL${NC}: $name"
        ((FAIL++))
    fi
}

echo ""
echo "============================================="
echo "  AuthShield Lab - Validation Suite"
echo "============================================="
echo ""

cd "$REPO_ROOT"

# Activate venv if it exists
if [[ -f ".venv/bin/activate" ]]; then
    # shellcheck source=/dev/null
    source ".venv/bin/activate"
fi

# 1. Python linting with Ruff
if command -v ruff &>/dev/null; then
    run_check "Ruff Linter (Python)" ruff check src/ tests/ --config configs/python/pyproject.toml
else
    echo -e "\n${YELLOW}⊘ SKIP${NC}: Ruff Linter (not installed)"
    ((SKIP++))
fi

# 2. Python type checking with mypy
if command -v mypy &>/dev/null; then
    run_check "mypy Type Checker (Python)" mypy src/ --config-file configs/python/pyproject.toml
else
    echo -e "\n${YELLOW}⊘ SKIP${NC}: mypy Type Checker (not installed)"
    ((SKIP++))
fi

# 3. Python tests with pytest
if command -v pytest &>/dev/null; then
    run_check "pytest (Python Tests)" pytest --config=configs/pytest/pytest.ini -x --timeout=300
else
    echo -e "\n${YELLOW}⊘ SKIP${NC}: pytest (not installed)"
    ((SKIP++))
fi

# 4. ESLint (TypeScript)
if command -v npx &>/dev/null && [[ -d "node_modules" ]]; then
    run_check_optional "ESLint (TypeScript)" npx eslint "packages/**/*.{ts,tsx,js,jsx}" --config configs/eslint/.eslintrc.json --max-warnings=0
else
    echo -e "\n${YELLOW}⊘ SKIP${NC}: ESLint (node_modules not found)"
    ((SKIP++))
fi

# 5. Prettier formatting check
if command -v npx &>/dev/null && [[ -d "node_modules" ]]; then
    run_check_optional "Prettier Format Check" npx prettier --check "packages/**/*.{ts,tsx,js,jsx,json,css,scss,md}" --config configs/prettier/.prettierrc.json
else
    echo -e "\n${YELLOW}⊘ SKIP${NC}: Prettier (node_modules not found)"
    ((SKIP++))
fi

# 6. TypeScript type checking
if command -v npx &>/dev/null && [[ -d "node_modules" ]]; then
    echo -e "\n${BLUE}━━━ TypeScript Type Check ━━━${NC}"
    TS_PASS=true
    for pkg in packages/*/tsconfig.json; do
        if [[ -f "$pkg" ]]; then
            PKG_DIR="$(dirname "$pkg")"
            echo -e "  Checking ${BLUE}$PKG_DIR${NC}..."
            if ! npx tsc --noEmit --project "$pkg" 2>/dev/null; then
                TS_PASS=false
            fi
        fi
    done
    if $TS_PASS; then
        echo -e "${GREEN}✓ PASS${NC}: TypeScript Type Check"
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC}: TypeScript Type Check"
        ((FAIL++))
    fi
else
    echo -e "\n${YELLOW}⊘ SKIP${NC}: TypeScript Type Check (node_modules not found)"
    ((SKIP++))
fi

# 7. Accessibility checks (axe)
if command -v npx &>/dev/null && [[ -d "node_modules" ]] && [[ -f "packages/ui/package.json" ]]; then
    echo -e "\n${BLUE}━━━ Accessibility (a11y) Checks ━━━${NC}"
    if npx eslint "packages/ui/src/**/*.{tsx,jsx}" --config configs/eslint/.eslintrc.json --rule '{"jsx-a11y/anchor-is-valid": "error", "jsx-a11y/click-events-have-key-events": "error", "jsx-a11y/no-static-element-interactions": "error"}' 2>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}: Accessibility Checks"
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC}: Accessibility Checks"
        ((FAIL++))
    fi
else
    echo -e "\n${YELLOW}⊘ SKIP${NC}: Accessibility Checks (not configured)"
    ((SKIP++))
fi

# 8. Check for secrets
echo -e "\n${BLUE}━━━ Secret Detection ━━━${NC}"
if command -v gitleaks &>/dev/null; then
    if gitleaks detect --source "$REPO_ROOT" --no-banner 2>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}: Secret Detection (gitleaks)"
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC}: Secret Detection (gitleaks)"
        ((FAIL++))
    fi
elif [[ -f ".pre-commit-config.yaml" ]]; then
    if grep -q "detect-private-key" .pre-commit-config.yaml; then
        echo -e "${GREEN}✓ PASS${NC}: Secret Detection (pre-commit hook configured)"
        ((PASS++))
    else
        echo -e "${YELLOW}⊘ SKIP${NC}: Secret Detection (no tool configured)"
        ((SKIP++))
    fi
else
    echo -e "${YELLOW}⊘ SKIP${NC}: Secret Detection (no tool installed)"
    ((SKIP++))
fi

# 9. Check file size limits
echo -e "\n${BLUE}━━━ Large File Check ━━━${NC}"
LARGE_FILES=0
while IFS= read -r -d '' file; do
    SIZE=$(stat -f%z "$file" 2>/dev/null || stat --format=%s "$file" 2>/dev/null)
    if [[ "$SIZE" -gt 512000 ]]; then
        echo -e "  ${RED}Large file: $file ($(( SIZE / 1024 ))KB)${NC}"
        ((LARGE_FILES++))
    fi
done < <(git ls-files -z 2>/dev/null)
if [[ "$LARGE_FILES" -eq 0 ]]; then
    echo -e "${GREEN}✓ PASS${NC}: No files exceed 500KB"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}: $LARGE_FILES file(s) exceed 500KB"
    ((FAIL++))
fi

# Summary
echo ""
echo "============================================="
echo "  Validation Summary"
echo "============================================="
echo ""
echo -e "  ${GREEN}Passed: $PASS${NC}"
echo -e "  ${RED}Failed: $FAIL${NC}"
echo -e "  ${YELLOW}Skipped: $SKIP${NC}"
echo ""

if [[ "$FAIL" -gt 0 ]]; then
    echo -e "${RED}Some checks failed. Please fix the issues above.${NC}"
    exit 1
else
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
fi
