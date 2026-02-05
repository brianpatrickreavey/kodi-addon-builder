# PYTHON-RELEASE-PLAN.md

## Status: Active Plan for Python Semantic Release

## Current Status
- Backup of plans completed to /tmp/kodi_backup/.
- Ready to start Phase 1: Cleanup.
- Rollback point confirmed as commit 0b1c774.

This plan outlines the complete process to switch from the aborted release-please attempt to automated releases using python-semantic-release. The goal is full Keep a Changelog compliance, custom commit types for all sections, and automated PyPI publishing without npm.

## Overview
- **Tool**: python-semantic-release (Python-based, no npm required).
- **Features**: Conventional commits, custom types (e.g., `change:` for Changed section and patch bumps), Keep a Changelog CHANGELOG.md, GitHub releases with notes, PyPI publishing.
- **Cleanup**: Full rollback of release-please attempt for a clean slate.
- **Testing**: Local dry-runs, act simulations, dummy commits.
- **Manual Changes**: GitHub branch protection, secrets, repo config.

## Phases

### Phase 1: Cleanup of Aborted Release-Please Attempt
**Goal**: Remove all traces of the release-please experiment, restoring the repo to a clean state before any changes.

#### Steps:
1. **Delete GitHub Release**: Remove release v0.6.0 (use `gh release delete v0.6.0` or web UI).
2. **Delete Tags**: Remove tag v0.6.0 locally (`git tag -d v0.6.0`) and remotely (`git push origin :refs/tags/v0.6.0`).
3. **Delete PR**: Close/delete PR #1 (use `gh pr delete 1` or web UI).
4. **Git Rollback**: Reset master to commit `0b1c774` (Add anybadge installation, before release-please changes: `git reset --hard 0b1c774`).
5. **Force Push**: Push the reset to origin (`git push origin master --force`).
6. **Mark Old Plan**: Update RELEASE-PLAN.md to include "ABORTED AND ROLLED BACK" at the top.
7. **Verify Clean Slate**: Ensure no release-please configs, workflows, or commits remain.

### Phase 2: Setup Python Semantic Release
**Goal**: Install and configure python-semantic-release for automated releases.

#### Steps:
1. **Install Dependency**: Add `python-semantic-release` to `pyproject.toml` dev dependencies.
2. **Create Config**: Add section to `pyproject.toml` or create `.semantic-release.toml` with custom commit types and rules (e.g., `change` -> patch bump, `deprecate` -> minor).
3. **Update CI Workflow**: Modify `.github/workflows/ci.yml` to add a release job that runs `semantic-release` after tests pass.
4. **Update Docs**: Add custom commit types to CONTRIBUTING.md (e.g., `change:`, `deprecate:`, `remove:`, `security:`).
5. **GitHub Secrets**: Ensure `PYPI_TOKEN` secret is set for PyPI publishing.

### Phase 3: Testing
**Goal**: Validate the setup works correctly before going live.

#### Methodology:
- **Local Dry-Runs**: Use `semantic-release --dry-run` to simulate releases without changes.
- **Local ACT Runs**: Use `act` to simulate GitHub Actions locally for CI/release jobs.
- **Dummy Commits**: Create test commits (e.g., `change: test change`, `feat: test feature`) on a test branch, push, and verify bumps/changelog.
- **Cleanup Tests**: Delete dummy commits and branches after validation.
- **Full Simulation**: Test a complete release cycle locally, then on a test branch.

### Phase 4: Manual GitHub Changes
**Goal**: Configure GitHub for the new workflow.

#### Changes:
- **Branch Protection**: Set rules for master to require "build" and test checks (e.g., "test (3.9)", "test (3.10)").
- **Repository Settings**: Enable features for commits, PRs, issues, etc. (e.g., allow squash merges).
- **Secrets**: Add `PYPI_TOKEN` for publishing.
- **Permissions**: Ensure workflows have write access for releases.

### Phase 5: Deployment and Go-Live
**Goal**: Activate the new release process.

#### Steps:
1. Merge setup changes.
2. Monitor first automated release.
3. Update any remaining docs.

#### Final Developer Workflow:
1. **Commit**: Use conventional commits (e.g., `feat: add new feature`, `change: update implementation`, `fix: bug fix`).
2. **Push**: Push to master; CI runs tests and build.
3. **Automated Release**: If releasable commits, python-semantic-release:
   - Bumps version (e.g., patch for `change`).
   - Updates CHANGELOG.md with full Keep a Changelog sections.
   - Creates GitHub release with changelog as notes.
   - Publishes to PyPI.
4. **No Manual Steps**: Developers just commit; releases happen automatically.

## Questions and Answers
1. **Rollback Point**: Commit `0b1c774` (Add anybadge installation, before release-please changes).
2. **Handling Merged PR**: Revert entirely (no code kept).
3. **Release/Tag Cleanup**: Use `gh` CLI or web UI (no preference).
4. **Testing Methodology**: Local dry-runs, act, dummy commits (deleted later).
5. **Manual GitHub Changes**: Branch protection, repo config (commits, PRs, etc.).
6. **Backup Location**: Plans backed up to /tmp/kodi_backup/.

## Risks and Rollback
- If issues, revert to manual releases.
- Test thoroughly in Phase 3.