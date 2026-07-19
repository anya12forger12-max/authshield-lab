# Developer Onboarding — AuthShield Lab

Welcome to AuthShield Lab! This guide will help you get up and running as a contributor.

---

## Prerequisites

Before you begin, ensure you have the following installed:

| Tool | Version | Install |
|------|---------|---------|
| **Node.js** | ≥ 20.0 | [nodejs.org](https://nodejs.org/) |
| **npm** | ≥ 10.0 | Comes with Node.js |
| **Git** | ≥ 2.40 | [git-scm.com](https://git-scm.com/) |
| **Docker** (optional) | ≥ 24.0 | [docker.com](https://docker.com/) |

### Verify Installation

```bash
node --version    # Should be v20.x or later
npm --version     # Should be 10.x or later
git --version     # Should be 2.40 or later
```

---

## Repository Setup

### 1. Fork the Repository

Go to [https://github.com/anya12forger12-max/authshield-lab](https://github.com/anya12forger12-max/authshield-lab) and click **Fork**.

### 2. Clone Your Fork

```bash
git clone https://github.com/<your-username>/authshield-lab.git
cd authshield-lab
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/anya12forger12-max/authshield-lab.git
```

### 4. Install Dependencies

```bash
npm install
```

### 5. Set Up Environment

```bash
cp .env.example .env
```

Review `.env` and adjust any values if needed. The defaults work for local development.

### 6. Verify Setup

```bash
npm run dev
```

The application should start and be available at `http://localhost:3000`.

---

## IDE Setup

### VS Code (Recommended)

Install the following extensions:

| Extension | Purpose |
|-----------|---------|
| **ESLint** | Linting integration |
| **Prettier** | Code formatting |
| **TypeScript** | Enhanced TypeScript support |
| **Tailwind CSS IntelliSense** | Tailwind class autocomplete |
| **Error Lens** | Inline error display |
| **GitLens** | Git integration |
| **Accessibility Viewer** | ARIA and accessibility testing |

### Recommended VS Code Settings

Add to your workspace `.vscode/settings.json`:

```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

### Other Editors

Any editor with TypeScript support works. Ensure you have:
- ESLint integration
- Prettier integration
- TypeScript language server

---

## Running Locally

### Development Server

```bash
npm run dev
```

This starts the development server with hot reload at `http://localhost:3000`.

### Available Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm test` | Run all tests |
| `npm run test:watch` | Run tests in watch mode |
| `npm run test:coverage` | Run tests with coverage report |
| `npm run test:a11y` | Run accessibility tests |
| `npm run lint` | Check for linting issues |
| `npm run lint:fix` | Auto-fix linting issues |
| `npm run format` | Format code with Prettier |
| `npm run typecheck` | Run TypeScript type checking |
| `npm run docker:up` | Start Docker containers |
| `npm run docker:down` | Stop Docker containers |

### Docker (Alternative)

```bash
# Build and start all services
docker compose up --build

# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

---

## Running Tests

### All Tests

```bash
npm test
```

### Test Categories

```bash
# Unit tests only
npm test -- --run unit

# Integration tests only
npm test -- --run integration

# Accessibility tests
npm run test:a11y

# Full coverage report
npm run test:coverage
```

### Writing Tests

Tests are co-located with source files using the `.test.ts` suffix:

```
src/
  core/
    token.ts
    token.test.ts     ← unit test
  api/
    auth.ts
    auth.test.ts       ← unit test
    auth.integration.ts ← integration test
```

See the [Contributing Guide](../../CONTRIBUTING.md#testing-requirements) for testing standards.

---

## Code Walkthrough

### Repository Structure

```
authshield-lab/
├── .github/                    # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml              # Main CI pipeline
│       └── release.yml         # Release automation
├── docs/                       # Documentation
│   └── development/
│       └── ONBOARDING.md       # This file
├── governance/                 # Governance documents
│   ├── policies/
│   │   ├── BRANCH_STRATEGY.md
│   │   └── COMMIT_CONVENTIONS.md
│   └── processes/
│       ├── REVIEW_PROCESS.md
│       └── RELEASE_PROCESS.md
├── packages/                   # Monorepo packages
│   ├── core/                   # Core authentication engine
│   ├── attacks/                # Attack simulation library
│   ├── tokens/                 # JWT/OAuth/SAML token testing
│   ├── lms/                    # Learning management system
│   ├── labs/                   # Interactive lab runner
│   ├── api/                    # REST API server
│   ├── cli/                    # Command-line interface
│   ├── sdk/                    # JavaScript/TypeScript SDK
│   ├── ui/                     # React web interface
│   ├── analytics/              # Analytics and reporting
│   ├── plugins/                # Plugin framework
│   └── i18n/                   # Internationalization
├── src/                        # Main application source
│   ├── auth/                   # Authentication modules
│   ├── config/                 # Configuration management
│   ├── db/                     # Database layer
│   ├── middleware/             # Express middleware
│   ├── routes/                 # API routes
│   ├── services/               # Business logic
│   ├── types/                  # TypeScript type definitions
│   └── utils/                  # Utility functions
├── tests/                      # Test infrastructure
│   ├── fixtures/               # Test data
│   ├── helpers/                # Test utilities
│   └── setup.ts                # Test setup
├── public/                     # Static assets
├── package.json                # Project configuration
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite build configuration
├── .eslintrc.json              # ESLint configuration
├── .prettierrc                 # Prettier configuration
├── Dockerfile                  # Docker build
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # Project README
```

### Key Modules

#### Core Engine (`packages/core`)

The heart of AuthShield Lab. Handles:
- Token validation and verification
- Session management
- Credential analysis
- Configuration management

#### Attack Library (`packages/attacks`)

Pre-built attack simulations:
- Brute force with wordlist support
- Credential stuffing
- Session hijacking and fixation
- MFA bypass techniques
- Token replay attacks

#### Token Engine (`packages/tokens`)

Specialized token testing:
- JWT signing and verification
- OAuth 2.0 flow simulation
- SAML assertion testing
- Algorithm confusion attacks

#### LMS (`packages/lms`)

Learning management:
- Course structure and content
- Progress tracking
- Grading and scoring
- Certificate generation

#### Lab Runner (`packages/labs`)

Sandboxed execution:
- Lab environment isolation
- Real-time feedback
- Score calculation
- Time management

#### API Server (`packages/api`)

REST API:
- Authentication endpoints
- Lab execution endpoints
- User management
- Analytics endpoints

#### React UI (`packages/ui`)

Web interface:
- Responsive design with Tailwind CSS
- Full keyboard navigation
- Screen reader support
- High contrast mode

---

## Common Tasks

### Adding a New Attack Type

1. Create the attack module in `packages/attacks/src/`:
   ```typescript
   // packages/attacks/src/my-attack.ts
   import { BaseAttack } from '../base';
   
   export class MyAttack extends BaseAttack {
     name = 'my-attack';
     description = 'Description of the attack';
     
     async execute(config: AttackConfig): Promise<AttackResult> {
       // Implementation
     }
   }
   ```

2. Add tests: `packages/attacks/src/my-attack.test.ts`
3. Export from the attacks package index
4. Register in the attack registry
5. Add lab scenario in `packages/labs/`
6. Update documentation

### Adding a New API Endpoint

1. Define the route in `src/routes/`
2. Add input validation with Zod schemas
3. Implement the controller logic
4. Add unit tests
5. Add integration tests
6. Update API documentation
7. Run `npm run test` and `npm run lint`

### Adding a New UI Component

1. Create the component in `packages/ui/src/components/`
2. Ensure full keyboard accessibility
3. Add ARIA attributes where needed
4. Add visual tests
5. Add accessibility tests
6. Update the component library documentation
7. Test with screen readers (NVDA or VoiceOver)

### Updating Dependencies

1. Check for outdated dependencies:
   ```bash
   npm outdated
   ```
2. Update carefully (one major version at a time):
   ```bash
   npm update <package>
   ```
3. Run the full test suite
4. Check for breaking changes in the changelog
5. Commit with `deps:` type

### Fixing a Bug

1. Check if an issue exists; if not, create one
2. Create a branch: `fix/<description>`
3. Write a failing test that reproduces the bug
4. Fix the bug
5. Verify the test passes
6. Run the full test suite
7. Submit a PR

---

## Architecture Overview

### High-Level Architecture

```
User → React UI → REST API → Core Engine → Database
                                  ↓
                            Attack Library
                            Token Engine
                            LMS Engine
```

### Data Flow

1. **User Interaction** — User interacts with the React UI
2. **API Request** — UI sends request to the REST API
3. **Authentication** — API validates the user's session
4. **Business Logic** — Service layer processes the request
5. **Core Engine** — Core engine executes the operation
6. **Database** — Results are persisted
7. **Response** — Response flows back to the UI

### Key Design Decisions

- **Offline-first**: No external API calls; everything runs locally
- **SQLite**: Lightweight, embedded database for portability
- **Monorepo**: All packages in one repository for atomic changes
- **TypeScript**: Full type safety across the codebase
- **Functional style**: Preference for functions over classes
- **Immutable data**: Preference for immutable operations

---

## Getting Help

| Channel | Purpose | Response Time |
|---------|---------|---------------|
| [GitHub Discussions](https://github.com/anya12forger12-max/authshield-lab/discussions) | Questions, ideas, help | 3-7 days |
| [GitHub Issues](https://github.com/anya12forger12-max/authshield-lab/issues) | Bug reports, feature requests | 3-5 days |
| [Contributing Guide](../../CONTRIBUTING.md) | How to contribute | N/A |
| [Code of Conduct](../../CODE_OF_CONDUCT.md) | Community standards | N/A |

### Onboarding Checklist

Use this checklist to track your progress:

- [ ] Repository cloned and dependencies installed
- [ ] Development server runs successfully
- [ ] All tests pass
- [ ] Reviewed the architecture overview
- [ ] Read the contributing guide
- [ ] Set up IDE with recommended extensions
- [ ] Completed a small task (typo fix, doc update, etc.)
- [ ] Submitted your first pull request
- [ ] Received your first code review

---

## Welcome Aboard!

We're glad to have you as a contributor. Don't hesitate to ask questions — everyone was new once. The community is here to help.

Happy coding!
