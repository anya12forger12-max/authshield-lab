#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
echo "Installing backend..."
cd backend
python3 -m venv .venv
.venv/bin/pip install --upgrade pip >/dev/null
if [ -f "pyproject.toml" ]; then .venv/bin/pip install -q -e ".[dev]" 2>/dev/null || .venv/bin/pip install -q . ; fi
if [ -f "requirements.txt" ]; then .venv/bin/pip install -q -r requirements.txt; fi
cd "$ROOT"
echo "Installing frontend..."
cd frontend
npm install --legacy-peer-deps
cd "$ROOT"
echo "Done. Backend: cd backend && source .venv/bin/activate; Frontend: cd frontend && npm run dev"
