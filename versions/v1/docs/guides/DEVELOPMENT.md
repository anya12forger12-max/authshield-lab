# Development Setup Guide

This guide covers setting up AuthShield Lab for development.

## Prerequisites

- Node.js 18+ (20 LTS recommended)
- Python 3.11+ (3.12 recommended)
- pip 23+
- npm 9+
- Git 2.40+

## Initial Setup

### 1. Clone and Install

```bash
git clone https://github.com/authshieldlab/authshield-lab.git
cd authshield-lab
./scripts/dev/setup.sh
```

### 2. Verify Setup

```bash
./scripts/utilities/validate.sh
```

This runs all linting, type checking, and tests.

## Backend Development

### Starting the Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000` with auto-reloading.

### API Documentation

FastAPI provides automatic API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Database Management

```bash
# Initialize database
python -m app.database.init

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Reset database (development only)
rm data/app.db
python -m app.database.init
```

### Running Backend Tests

```bash
cd backend
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_authentication.py -v

# Run specific test
python -m pytest tests/test_authentication.py::test_login -v
```

### Code Quality

```bash
# Linting
ruff check app/
ruff format app/

# Type checking
mypy app/

# Security scanning
bandit -r app/
```

## Frontend Development

### Starting the Frontend

```bash
cd frontend
npm run dev
```

This starts the Electron development environment with hot reloading.

### Frontend Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run test` | Run tests |
| `npm run test:watch` | Run tests in watch mode |
| `npm run test:coverage` | Run tests with coverage |
| `npm run lint` | Lint TypeScript/React |
| `npm run lint:fix` | Auto-fix lint issues |
| `npm run typecheck` | Type check the project |

### Running Frontend Tests

```bash
cd frontend
npm run test

# With coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### Code Quality

```bash
# Linting
npm run lint

# Type checking
npm run typecheck

# Format
npx prettier --write "src/**/*.{ts,tsx,js,jsx}"
```

## Project Structure

```
AuthShieldLab/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config/
│   │   │   ├── __init__.py      # Settings export
│   │   │   └── settings.py      # Configuration
│   │   ├── database/
│   │   │   └── models/          # SQLAlchemy models
│   │   ├── authentication/      # Auth module
│   │   ├── users/               # User management
│   │   ├── sessions/            # Sessions
│   │   ├── attacks/             # Attack simulations
│   │   ├── defenses/            # Defense mechanisms
│   │   ├── analytics/           # Analytics
│   │   ├── reports/             # Reports
│   │   ├── learning/            # Learning center
│   │   └── audit/               # Audit logging
│   ├── tests/                   # Backend tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main/                # Electron main process
│   │   ├── renderer/            # React application
│   │   │   ├── components/      # React components
│   │   │   ├── hooks/           # Custom hooks
│   │   │   ├── stores/          # Zustand stores
│   │   │   ├── pages/           # Route pages
│   │   │   └── themes/          # Theme engine
│   │   └── shared/              # Shared types
│   ├── tests/                   # Frontend tests
│   ├── package.json
│   └── tsconfig.json
├── docs/                        # Documentation
├── scripts/                     # Automation scripts
└── .github/                     # GitHub configuration
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

Follow the coding standards:

- Backend: PEP 8 with type hints (enforced by Ruff and mypy)
- Frontend: ESLint + Prettier configuration
- Commit messages: Conventional Commits format

### 3. Run Validation

```bash
./scripts/utilities/validate.sh
```

This runs:
1. Python linting (Ruff)
2. Python type checking (mypy)
3. Frontend linting (ESLint)
4. Frontend type checking (TypeScript)
5. Backend tests (pytest)
6. Frontend tests (Vitest)

### 4. Commit and Push

```bash
git add .
git commit -m "feat(module): add new feature"
git push origin feature/my-feature
```

### 5. Create Pull Request

Fill out the PR template and request review.

## Environment Configuration

### Backend (.env)

```env
APP_MODE=developer
APP_HOST=localhost
APP_PORT=8000
APP_SECRET_KEY=dev-secret-key-change-in-production
APP_DB_PATH=./data/app.db
APP_LOG_LEVEL=debug
APP_CORS_ORIGINS=["http://localhost:5173"]
APP_RATE_LIMIT=100
APP_SESSION_TIMEOUT=30
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_APP_MODE=developer
VITE_WS_URL=ws://localhost:8000/ws
```

## Debugging

### Backend Debugging

For VS Code, create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env"
    }
  ]
}
```

### Frontend Debugging

1. Start the development server: `npm run dev`
2. In Electron, press `Ctrl+Shift+I` (or `Cmd+Option+I` on macOS) to open DevTools
3. Set breakpoints in VS Code for main process debugging
4. Use React DevTools for component inspection

### Database Inspection

Use any SQLite browser to open `backend/data/app.db`:

- [DB Browser for SQLite](https://sqlitebrowser.org/) (recommended)
- VS Code SQLite extension
- DBeaver

## Common Issues

### Hot Reload Not Working

- Ensure `--reload` flag is passed to uvicorn
- Check that file watchers are not hitting OS limits
- Try restarting the backend server

### TypeScript Errors

```bash
cd frontend
npm run typecheck
```

Common fixes:
- Run `npm install` to ensure types are installed
- Check for missing type imports
- Verify `tsconfig.json` configuration

### Import Errors

- Ensure virtual environment is activated for Python
- Ensure `node_modules` exists for JavaScript
- Check import paths match file structure

## Performance Tips

- Use `--reload` flag only in development (not production builds)
- Enable source maps for better debugging
- Use VS Code workspace settings for consistent formatting
- Run linters as file save hooks

## Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Electron Documentation](https://www.electronjs.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Zustand Documentation](https://docs.pmnd.rs/zustand/getting-started/introduction)
