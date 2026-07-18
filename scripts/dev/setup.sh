#!/usr/bin/env bash
#
# AuthShield Lab - Development Setup Script
#
# This script sets up the development environment for AuthShield Lab.
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

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    local missing=0
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed."
        echo "  Install from: https://nodejs.org/"
        missing=1
    else
        local node_version=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$node_version" -lt 18 ]; then
            log_error "Node.js version must be 18+. Current: $(node -v)"
            missing=1
        else
            log_info "Node.js: $(node -v)"
        fi
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed."
        echo "  Install from: https://www.python.org/downloads/"
        missing=1
    else
        local python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        local python_major=$(echo "$python_version" | cut -d'.' -f1)
        local python_minor=$(echo "$python_version" | cut -d'.' -f2)
        if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 11 ]); then
            log_error "Python version must be 3.11+. Current: $python_version"
            missing=1
        else
            log_info "Python: $python_version"
        fi
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed."
        echo "  Install with Node.js or from: https://www.npmjs.com/"
        missing=1
    else
        log_info "npm: $(npm -v)"
    fi
    
    if ! command -v git &> /dev/null; then
        log_warn "Git is not installed. Version control features may be limited."
    else
        log_info "Git: $(git --version)"
    fi
    
    if [ $missing -ne 0 ]; then
        echo ""
        log_error "Missing prerequisites. Please install the required tools."
        exit 1
    fi
    
    log_info "All prerequisites satisfied."
    echo ""
}

# Setup backend
setup_backend() {
    log_step "Setting up backend..."
    cd "$PROJECT_ROOT/backend"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    else
        log_info "Virtual environment already exists."
    fi
    
    source venv/bin/activate
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt --quiet
    
    # Create .env if not exists
    if [ ! -f ".env" ]; then
        log_info "Creating .env from example..."
        cp .env.example .env
    fi
    
    # Create data directory
    mkdir -p data
    
    # Initialize database
    log_info "Initializing database..."
    python -m app.database.init 2>/dev/null || log_warn "Database initialization skipped (not yet implemented)"
    
    log_info "Backend setup completed."
    echo ""
}

# Setup frontend
setup_frontend() {
    log_step "Setting up frontend..."
    cd "$PROJECT_ROOT/frontend"
    
    # Install dependencies
    log_info "Installing Node.js dependencies..."
    npm ci --silent 2>/dev/null || npm install --silent
    
    # Create .env if not exists
    if [ ! -f ".env" ]; then
        log_info "Creating .env from example..."
        cp .env.example .env
    fi
    
    log_info "Frontend setup completed."
    echo ""
}

# Setup development tools
setup_tools() {
    log_step "Setting up development tools..."
    cd "$PROJECT_ROOT"
    
    # Make scripts executable
    chmod +x scripts/build/build.sh
    chmod +x scripts/utilities/validate.sh
    chmod +x scripts/dev/setup.sh
    
    # Create log directory
    mkdir -p logs
    
    log_info "Development tools setup completed."
    echo ""
}

# Print summary
print_summary() {
    echo "============================================"
    echo ""
    echo "  AuthShield Lab - Development Environment"
    echo "  Setup Complete!"
    echo ""
    echo "============================================"
    echo ""
    echo "  Quick Start:"
    echo ""
    echo "  Terminal 1 - Backend:"
    echo "    cd backend"
    echo "    source venv/bin/activate"
    echo "    uvicorn app.main:app --reload --port 8000"
    echo ""
    echo "  Terminal 2 - Frontend:"
    echo "    cd frontend"
    echo "    npm run dev"
    echo ""
    echo "  Terminal 3 - Validation:"
    echo "    ./scripts/utilities/validate.sh"
    echo ""
    echo "  API Docs: http://localhost:8000/docs"
    echo "  Frontend: http://localhost:5173"
    echo ""
    echo "============================================"
    echo ""
    echo "  Documentation:"
    echo "    docs/guides/DEVELOPMENT.md"
    echo "    docs/guides/USER_GUIDE.md"
    echo "    docs/architecture/OVERVIEW.md"
    echo ""
    echo "============================================"
}

# Main setup function
main() {
    echo ""
    echo "============================================"
    echo "  AuthShield Lab - Development Setup"
    echo "============================================"
    echo ""
    
    check_prerequisites
    setup_backend
    setup_frontend
    setup_tools
    print_summary
}

# Run main function
main "$@"
