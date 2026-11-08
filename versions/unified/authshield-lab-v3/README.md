# AuthShield Lab

![AuthShield Lab Logo](docs/assets/logo.png)

**Enterprise Authentication Attack & Defense Training Platform**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#)
[![Version](https://img.shields.io/badge/version-1.0.0--alpha.1-blue)](#)
[![License](https://img.shields.io/badge/license-MIT-yellow)](#license)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)

---

AuthShield Lab is a comprehensive desktop-based cybersecurity training platform designed for learning authentication vulnerabilities, attack methodologies, and defensive strategies in a completely isolated local environment.

## Features

### 20 Training Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | **Dashboard** | Central overview with metrics, alerts, and activity feed |
| 2 | **Authentication** | Simulated auth flows and credential management |
| 3 | **User Management** | User lifecycle, roles, and access control |
| 4 | **Session Management** | Token handling, session hijacking simulations |
| 5 | **Attack Simulations** | Brute force, credential stuffing, injection attacks |
| 6 | **Defense Mechanisms** | Rate limiting, MFA, account lockout, WAF rules |
| 7 | **Analytics** | Real-time threat analytics and visualization |
| 8 | **Reports** | Generated security reports and compliance docs |
| 9 | **Learning Center** | Interactive lessons, quizzes, and certifications |
| 10 | **Audit Trail** | Immutable audit logging and investigation |
| 11 | **Timeline** | Historical event timeline and forensics |
| 12 | **Settings** | Platform configuration and preferences |
| 13 | **Help** | Documentation browser and troubleshooting |
| 14 | **Vulnerability Scanner** | Identify and catalog auth weaknesses |
| 15 | **Credential Vault** | Encrypted credential storage simulation |
| 16 | **Network Monitor** | Local traffic inspection and analysis |
| 17 | **Incident Response** | IR playbook execution and tracking |
| 18 | **Threat Intelligence** | IOC tracking and threat feed simulation |
| 19 | **Compliance Checker** | SOX, HIPAA, PCI-DSS compliance validation |
| 20 | **API Security** | OAuth2/OIDC flow testing and API key management |

## Screenshots

![Dashboard](docs/assets/screenshot-dashboard.png)
![Attack Simulation](docs/assets/screenshot-attacks.png)
![Analytics View](docs/assets/screenshot-analytics.png)

---

## Quick Start

### Development

```bash
# Clone the repository
git clone https://github.com/authshieldlab/authshield-lab.git
cd authshield-lab

# Run development setup
./scripts/dev/setup.sh

# Start the application
npm run dev
```

### Production

```bash
# Build for production
./scripts/build/build.sh

# Or on Windows
scripts\build\build.bat
```

## Prerequisites

- **Node.js** 18+ (LTS recommended)
- **Python** 3.11+
- **pip** 23+
- **npm** 9+
- **Git** 2.40+
- **Rust** (for native modules, optional)

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/authshieldlab/authshield-lab.git
cd authshield-lab

# 2. Install Python dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Install frontend dependencies
cd ../frontend
npm install

# 4. Configure environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 5. Initialize database
cd ../backend
python -m app.database.init

# 6. Return to root
cd ..
```

## Development Setup

```bash
# Start backend (Terminal 1)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Start frontend (Terminal 2)
cd frontend
npm run dev

# Run validation (Terminal 3)
./scripts/utilities/validate.sh
```

## Project Structure

```
AuthShieldLab/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── authentication/   # Auth module
│   │   ├── users/            # User management
│   │   ├── sessions/         # Session handling
│   │   ├── attacks/          # Attack simulations
│   │   ├── defenses/         # Defense mechanisms
│   │   ├── analytics/        # Analytics engine
│   │   ├── reports/          # Report generation
│   │   ├── learning/         # Learning system
│   │   ├── audit/            # Audit logging
│   │   ├── config/           # Configuration
│   │   └── main.py           # Application entry
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # Electron + React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   ├── stores/           # Zustand stores
│   │   ├── pages/            # Route pages
│   │   ├── themes/           # Theme engine
│   │   ├── i18n/             # Internationalization
│   │   └── utils/            # Utilities
│   ├── package.json
│   └── tsconfig.json
├── docs/                     # Documentation
│   ├── architecture/
│   ├── guides/
│   ├── security/
│   └── accessibility/
├── scripts/                  # Automation scripts
│   ├── build/
│   ├── dev/
│   └── utilities/
├── .github/                  # GitHub config
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
└── configuration files
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Desktop Runtime** | Electron 28+ | Cross-platform desktop application |
| **Frontend UI** | React 18 | Component-based user interface |
| **Language** | TypeScript 5 | Type-safe development |
| **State Management** | Zustand | Lightweight global state |
| **Styling** | Tailwind CSS | Utility-first CSS framework |
| **Backend API** | FastAPI | High-performance Python API |
| **ORM** | SQLAlchemy 2.0 | Database abstraction |
| **Database** | SQLite | Embedded local database |
| **Auth** | bcrypt + JWT | Password hashing & tokens |
| **Testing** | pytest + Vitest | Backend & frontend tests |
| **Linting** | Ruff + ESLint | Code quality enforcement |
| **Build** | electron-builder | Application packaging |

## Application Modes

| Mode | Description | Target User |
|------|-------------|-------------|
| **Demo** | Read-only showcase with sample data | Evaluators |
| **Student** | Guided learning with progress tracking | Learners |
| **Instructor** | Classroom management and assessment | Teachers |
| **Admin** | Full system configuration | Administrators |
| **Developer** | Debug tools and API explorer | Contributors |

## Configuration

AuthShield Lab uses a layered configuration system:

```bash
# Environment variables
APP_MODE=student          # demo | student | instructor | admin | developer
APP_HOST=localhost        # Always localhost for security
APP_PORT=8000             # Backend API port
APP_SECRET_KEY=<random>   # JWT signing key
APP_DB_PATH=./data/app.db # SQLite database path
APP_LOG_LEVEL=info        # logging level
```

## Accessibility

AuthShield Lab is committed to WCAG 2.2 AA compliance:

- Full keyboard navigation across all modules
- Screen reader support with ARIA labels
- High-contrast and dyslexia-friendly themes
- Configurable font sizes (12px - 24px)
- Reduced motion mode for animations
- Color-blind safe palettes
- Focus indicators on all interactive elements
- Semantic HTML throughout the interface

## Security

- **Localhost-only**: All network communication restricted to 127.0.0.1
- **No external connections**: Zero outbound network requests by design
- **Isolated environment**: Training data never leaves the local machine
- **Encrypted storage**: Sensitive data encrypted at rest with AES-256
- **Password hashing**: bcrypt with configurable work factor
- **Session security**: Short-lived JWT tokens with refresh rotation
- **Input validation**: Pydantic models enforce strict schema validation
- **CORS restrictions**: Only local origins permitted
- **Audit logging**: All actions recorded with tamper-evident logs
- **Data sanitization**: All user inputs escaped and validated

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, branch naming conventions, and pull request process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issue Tracker**: [GitHub Issues](https://github.com/authshieldlab/authshield-lab/issues)
- **Security Issues**: See [SECURITY.md](SECURITY.md)
- **Code of Conduct**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

*Built with care for the cybersecurity education community.*
