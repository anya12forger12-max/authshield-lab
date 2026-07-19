# Branch Strategy — AuthShield Lab

This document defines the Git branching model, merge rules, and branch protection policies for the AuthShield Lab repository.

---

## Branch Overview

```
main ─────────────────────────────────────────────────────────►
  │                                                           │
  ├── release/5.1.0 ──────┐                                   │
  │                       ├─── merge to main + develop         │
  ├── release/5.2.0 ──────┘                                   │
  │                                                           │
  ├── develop ────────────────────────────────────────────────►
  │   │                                                       │
  │   ├── feature/oauth2-saml ──┐                             │
  │   │                        ├── merge to develop           │
  │   ├── feature/plugin-api ──┘                             │
  │   │                                                       │
  │   ├── security/xss-fix ──── merge to develop              │
  │   │                                                       │
  │   └── experimental/webauthn ─ no merge guarantee          │
  │                                                           │
  └── hotfix/token-validation ─ merge to main + develop       │
```

---

## Branch Types

### `main`

**Purpose**: Production-ready code. Every commit on `main` represents a released version.

| Property | Value |
|----------|-------|
| Protected | Yes |
| Direct push | Forbidden |
| Requires PR | Yes |
| Required approvals | 1 minimum |
| Required status checks | All CI checks pass |
| Signed commits | Required |
| Force push | Forbidden |
| Branch deletion | Forbidden |
| Merge method | Squash and merge (from release/hotfix) |

### `develop`

**Purpose**: Integration branch for the next release. All feature, fix, and security branches merge here first.

| Property | Value |
|----------|-------|
| Protected | Yes |
| Direct push | Forbidden |
| Requires PR | Yes |
| Required approvals | 1 minimum |
| Required status checks | All CI checks pass |
| Signed commits | Required |
| Force push | Forbidden |
| Merge method | Squash and merge |
| Merge frequency | Daily (from feature branches) |

### `feature/*`

**Purpose**: Development of new features. Branches off from `develop` and merges back via PR.

| Property | Value |
|----------|-------|
| Naming | `feature/<short-description>` |
| Base branch | `develop` |
| Merge target | `develop` |
| Merge method | Squash and merge |
| Lifetime | Until feature is complete |
| Status checks | Required |

**Rules**:
- Branch from the latest `develop`
- Keep up to date with `develop` by rebasing regularly
- One feature per branch
- All new features must include tests
- All new UI features must include accessibility testing

### `release/*`

**Purpose**: Release preparation. Created when `develop` is ready for release. Only bug fixes are allowed.

| Property | Value |
|----------|-------|
| Naming | `release/<version>` (e.g., `release/5.1.0`) |
| Base branch | `develop` |
| Merge targets | `main` AND `develop` |
| Merge method | Squash and merge (to main), merge commit (to develop) |
| Lifetime | Until release is published |
| Allowed changes | Bug fixes, documentation updates, version bumps only |

**Rules**:
- Created from `develop` when all release features are complete
- Feature freeze is in effect — no new features
- Bug fixes are cherry-picked or committed directly to the release branch
- After release, the branch is deleted
- The version bump commit on `main` creates the release tag

### `hotfix/*`

**Purpose**: Critical fixes for production. Branches off from `main` and merges to both `main` and `develop`.

| Property | Value |
|----------|-------|
| Naming | `hotfix/<short-description>` |
| Base branch | `main` |
| Merge targets | `main` AND `develop` |
| Merge method | Squash and merge |
| Lifetime | Until fix is released |
| Review turnaround | 24 hours (expedited) |

**Rules**:
- Branch from the latest `main`
- Fix the issue with minimal changes
- Add or update tests for the fix
- Merge to `main` first, then merge to `develop`
- Create a patch release after merge

### `experimental/*`

**Purpose**: Experimental features with no merge guarantee. Used for prototyping and proof-of-concept work.

| Property | Value |
|----------|-------|
| Naming | `experimental/<short-description>` |
| Base branch | `develop` |
| Merge target | No guaranteed merge |
| Merge method | N/A (manual decision) |
| Lifetime | Until experiment concludes |

**Rules**:
- Clearly marked as experimental
- May be deleted at any time
- No CI required (but recommended)
- If experiment succeeds, create a proper `feature/*` branch
- Document findings before closing

### `documentation/*`

**Purpose**: Documentation-only changes that do not affect code.

| Property | Value |
|----------|-------|
| Naming | `documentation/<short-description>` |
| Base branch | `develop` |
| Merge target | `develop` |
| Merge method | Squash and merge |
| Status checks | Lint only (no code tests needed) |

### `security/*`

**Purpose**: Security fixes that need expedited handling.

| Property | Value |
|----------|-------|
| Naming | `security/<short-description>` |
| Base branch | `develop` (or `main` for critical) |
| Merge target | `develop` (and `main` if critical) |
| Merge method | Squash and merge |
| Review turnaround | 24 hours |
| Required approvals | 2 (security review) |

**Rules**:
- Security team must review
- Two approvals required
- No public discussion of vulnerability until fix is merged
- Follow responsible disclosure process

---

## Merge Rules Summary

| Source Branch | Target | Method | Approvals | CI Required | Notes |
|---------------|--------|--------|-----------|-------------|-------|
| `feature/*` | `develop` | Squash and merge | 1 | Yes | |
| `fix/*` | `develop` | Squash and merge | 1 | Yes | |
| `release/*` | `main` | Squash and merge | 1 | Yes | After release testing |
| `release/*` | `develop` | Merge commit | 1 | Yes | Back-merge |
| `hotfix/*` | `main` | Squash and merge | 1 | Yes | Expedited |
| `hotfix/*` | `develop` | Merge commit | 1 | Yes | Back-merge |
| `security/*` | `develop` | Squash and merge | 2 | Yes | Security review |
| `security/*` | `main` | Squash and merge | 2 | Yes | Critical only |
| `documentation/*` | `develop` | Squash and merge | 1 | Lint only | |
| `experimental/*` | `develop` | Manual | Manual | Optional | No guarantee |

---

## Required Status Checks

All CI checks must pass before merging. The following checks are enforced:

| Check | Required For | Description |
|-------|-------------|-------------|
| `lint` | All branches | ESLint code quality |
| `typecheck` | All branches | TypeScript type checking |
| `test` | All branches | Unit and integration tests |
| `test:a11y` | All branches | Accessibility tests |
| `build` | All branches | Production build verification |
| `coverage` | All branches | Minimum coverage threshold |

### Branch-Specific Checks

| Branch Type | Additional Checks |
|-------------|-------------------|
| `security/*` | Security scan, dependency audit |
| `release/*` | Full E2E test suite, performance benchmarks |
| `documentation/*` | Link checking, spelling |

---

## Signed Commits Policy

All commits to `main`, `develop`, `release/*`, and `security/*` branches must be signed.

### Setup

```bash
# Configure Git to sign commits
git config --global commit.gpgsign true
git config --global user.signingkey <YOUR_GPG_KEY_ID>

# For SSH-based signing
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
```

### Verification

GitHub verifies commit signatures automatically. Unsigned commits will be rejected by branch protection rules.

### Exceptions

- `experimental/*` branches do not require signed commits
- `documentation/*` branches do not require signed commits (but signing is encouraged)

---

## Stale Branch Management

| Branch Type | Stale After | Action |
|-------------|-------------|--------|
| `feature/*` | 14 days of inactivity | Warning comment on PR |
| `feature/*` | 30 days of inactivity | PR closed, branch deleted |
| `experimental/*` | 7 days of inactivity | Warning comment |
| `experimental/*` | 30 days of inactivity | Branch deleted |
| `release/*` | 3 days of inactivity | Escalation to maintainers |
| `hotfix/*` | 1 day of inactivity | Escalation to maintainers |

---

## Workflow Summary

### Daily Development

1. Create `feature/*` or `fix/*` from `develop`
2. Work on changes, commit with conventional commits
3. Push and create PR against `develop`
4. Address review feedback
5. Merge after approval and CI pass

### Release Cycle

1. `develop` is feature-frozen
2. Create `release/*` from `develop`
3. Bug fixes and version bumps only
4. Full test suite and accessibility audit
5. Merge `release/*` to `main` (squash)
6. Tag the release on `main`
7. Back-merge `release/*` to `develop`
8. Delete the release branch

### Emergency Hotfix

1. Create `hotfix/*` from `main`
2. Make minimal fix
3. Add/update tests
4. Merge to `main` (squash, expedited)
5. Tag the hotfix release
6. Back-merge to `develop`
7. Delete the hotfix branch
