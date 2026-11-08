# Release Process — AuthShield Lab

This document describes the end-to-end release process for AuthShield Lab, from planning through post-release monitoring.

---

## Version Number Strategy

We follow [Semantic Versioning](https://semver.org/) (SemVer):

```
MAJOR.MINOR.PATCH
```

| Component | When to Increment | Breaking Changes |
|-----------|-------------------|-----------------|
| **MAJOR** | Incompatible API or behavioral changes | Yes |
| **MINOR** | New features, backward-compatible | No |
| **PATCH** | Bug fixes, backward-compatible | No |

### Pre-release Identifiers

| Identifier | Example | Purpose |
|------------|---------|---------|
| `alpha` | `5.1.0-alpha.1` | Early development, unstable |
| `beta` | `5.1.0-beta.1` | Feature-complete, testing phase |
| `rc` | `5.1.0-rc.1` | Release candidate, final testing |

### Examples

```
5.0.0          — Stable major release
5.0.1          — Patch release (bug fix)
5.1.0          — Minor release (new features)
5.1.0-alpha.1  — Alpha pre-release
5.1.0-beta.2   — Beta pre-release
5.1.0-rc.1     — Release candidate
```

---

## Release Planning

### Timeline

Releases follow a predictable schedule:

| Release Type | Frequency | Development Period |
|-------------|-----------|-------------------|
| MAJOR | Annual | 3 months |
| MINOR | Quarterly | 6 weeks |
| PATCH | As needed | 1-2 weeks |
| HOTFIX | As needed | 1-3 days |

### Planning Steps

1. **Roadmap Review** — TSC reviews roadmap priorities (quarterly)
2. **Milestone Creation** — GitHub milestone is created for the release
3. **Issue Assignment** — Issues are assigned to the milestone
4. **Dependency Review** — New dependencies are audited
5. **Timeline Communication** — Release timeline is communicated to the community

### Release Milestone

Each release has a GitHub milestone with:
- Target release date
- List of issues/pull requests
- Testing checklist
- Documentation checklist
- Accessibility audit checklist

---

## Feature Freeze

### Definition

Feature freeze marks the point where no new features are added to the release. Only bug fixes, documentation updates, and release preparation work is allowed.

### Process

1. **Feature freeze date is set** — Communicated 2 weeks in advance
2. **`release/*` branch is created** — Branched from `develop`
3. **`develop` is unfrozen** — Development for the next release resumes
4. **Release notes draft is started** — Authors document their features

### Rules During Feature Freeze

| Allowed | Not Allowed |
|---------|------------|
| Bug fixes | New features |
| Documentation updates | Refactoring (unless fixing a bug) |
| Version bumps | Dependency additions (unless security) |
| Test fixes | Breaking changes |
| Release preparation | Experimental work |

---

## Testing Phases

### Phase 1: Automated Testing (Continuous)

| Check | Tool | Requirement |
|-------|------|-------------|
| Unit tests | Vitest | 100% pass rate |
| Integration tests | Vitest | 100% pass rate |
| Type checking | TypeScript | No errors |
| Linting | ESLint | No errors |
| Accessibility (automated) | axe-core, pa11y | No critical violations |
| Build | Vite | Successful production build |
| Security scan | npm audit | No high/critical vulnerabilities |

### Phase 2: Manual Testing

| Area | Tester | Checklist |
|------|--------|-----------|
| Core authentication flows | QA Team | Full test script |
| Attack simulations | Security Team | All attack scenarios |
| LMS functionality | QA Team | Course creation, progress, grading |
| Lab execution | QA Team | All lab types |
| API endpoints | Backend Team | All endpoints documented |
| CLI commands | CLI Team | All commands functional |
| UI/UX | Frontend Team | Responsive, accessible |
| Keyboard navigation | Accessibility Team | Full keyboard walkthrough |
| Screen reader testing | Accessibility Team | NVDA + VoiceOver |

### Phase 3: User Acceptance Testing

1. **Release candidate** is deployed to a staging environment
2. **Community testers** are invited to test
3. **Feedback period** — 5 business days
4. **Bug triage** — Critical bugs are fixed, non-critical deferred

---

## Release Candidate

### Creation

```bash
# Create release branch
git checkout develop
git checkout -b release/5.1.0

# Update version
npm version 5.1.0-rc.1

# Push
git push origin release/5.1.0
```

### RC Activities

1. **Deploy to staging** — Full environment deployment
2. **Run full test suite** — All automated checks
3. **Manual testing** — Complete testing checklist
4. **Accessibility audit** — Full WCAG 2.2 AA review
5. **Security audit** — Dependency and code review
6. **Documentation review** — All docs are current
7. **Community testing** — RC is available for community feedback

### RC Criteria

| Criterion | Requirement |
|-----------|-------------|
| All tests pass | 100% |
| No critical bugs | 0 open critical issues |
| No high-severity a11y issues | 0 open high issues |
| Documentation complete | All new features documented |
| Changelog updated | Complete for this release |
| Security audit passed | No high/critical vulnerabilities |

### RC Iterations

If bugs are found in the RC:

1. Fix on the release branch
2. Create new RC: `5.1.0-rc.2`
3. Retest affected areas
4. Repeat until stable

---

## Final Release

### Steps

1. **Final RC is validated** — All criteria met
2. **Version bump** — Update to final version
   ```bash
   npm version 5.1.0
   ```
3. **Changelog is finalized** — Move Unreleased entries to the version
4. **Merge to main** — Squash and merge the release branch
5. **Tag the release** — Create a Git tag
   ```bash
   git tag -a v5.1.0 -m "Release 5.1.0"
   git push origin v5.1.0
   ```
6. **Back-merge to develop** — Merge release branch back to develop
7. **Delete release branch** — Clean up
   ```bash
   git branch -d release/5.1.0
   git push origin --delete release/5.1.0
   ```
8. **Publish release** — GitHub Release with changelog
9. **Community notification** — Announce the release

### Release Checklist

- [ ] All tests pass on the release branch
- [ ] Version is bumped in package.json and all relevant files
- [ ] Changelog is complete and accurate
- [ ] Release notes are written for the GitHub Release
- [ ] Tag is created with the correct version
- [ ] Release branch is merged to main
- [ ] Release branch is back-merged to develop
- [ ] Release branch is deleted
- [ ] GitHub Release is published
- [ ] Community is notified

---

## Post-Release

### Monitoring (First 7 Days)

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Monitor GitHub Issues | Daily | All maintainers |
| Monitor error rates | Daily | DevOps |
| Review user feedback | Daily | Product lead |
| Security advisory monitoring | Daily | Security team |
| Performance monitoring | Daily | DevOps |

### Hotfix Readiness

For the first 7 days after release:
- A hotfix branch is on standby
- Maintainers are on-call for critical issues
- Emergency release process is ready to execute

### Retrospective

Within 2 weeks of release:
1. **Release retrospective** — What went well, what to improve
2. **Metrics review** — Build times, test coverage, issue resolution
3. **Process improvements** — Update this document if needed

---

## Hotfix Process

### Trigger

A hotfix is needed when:
- A critical security vulnerability is discovered
- A data loss or corruption bug is found
- A production system is down
- The issue affects all users and cannot wait for the next release

### Steps

1. **Create hotfix branch from main**:
   ```bash
   git checkout main
   git checkout -b hotfix/token-validation-fix
   ```

2. **Implement the fix**:
   - Make minimal changes
   - Add or update tests
   - Update changelog

3. **Commit with conventional format**:
   ```
   fix(tokens): correct JWT validation bypass vulnerability

   Fixes #XXX
   ```

4. **Create PR against main**:
   - Tag as `hotfix`
   - Request expedited review (24-hour turnaround)
   - Two approvals required for security fixes

5. **After approval and CI pass**:
   - Squash and merge to `main`
   - Create patch tag: `v5.0.1`
   - Back-merge to `develop`

6. **Publish**:
   - GitHub Release with hotfix notes
   - Notify users of the security update

### Hotfix Timeline

| Step | Timeline |
|------|----------|
| Issue identified | T+0 |
| Hotfix branch created | T+2 hours |
| Fix implemented | T+8 hours |
| PR submitted | T+10 hours |
| Review completed | T+24 hours |
| Merged and released | T+26 hours |

---

## LTS (Long-Term Support) Policy

### Support Duration

| Version Type | Support Duration | Security Patches |
|-------------|-----------------|-----------------|
| MAJOR | 24 months | Yes |
| MINOR | Until next MINOR | No (use next MINOR) |
| PATCH | N/A (part of MINOR cycle) | N/A |

### LTS Release Schedule

- LTS releases are designated at major version boundaries
- The previous major version receives security patches for 12 months after the new major
- LTS end-of-life dates are announced 6 months in advance

### LTS Branch

LTS releases have a dedicated branch:
```
main          — Current stable
lts/5.x       — LTS branch for v5.x
```

Security patches for LTS are cherry-picked from `main` and tested on the LTS branch.

---

## Release Naming

Releases are identified by version number only. We do not use code names for releases.

| Version | Date | Highlights |
|---------|------|-----------|
| 5.0.0 | 2026-07-19 | Initial stable release |

---

## Release Artifacts

Each release produces:

| Artifact | Description |
|----------|-------------|
| Git tag | Annotated tag with version |
| GitHub Release | Release notes with changelog |
| npm package | Published to npm registry |
| Docker image | Published to GitHub Container Registry |
| SBOM | Software Bill of Materials |
| Checksums | SHA-256 checksums for all artifacts |

---

*This process is reviewed and updated quarterly. Last update: July 2026.*
