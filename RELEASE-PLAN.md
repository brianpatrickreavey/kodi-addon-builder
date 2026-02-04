# PyPI Release Preparation Plan for Kodi Addon Builder

## Overview
Prepare the kodi-addon-builder project for PyPI publishing by implementing dynamic versioning, automated releases via GitHub Actions, and clean documentation, enabling pip installation in other Kodi addon projects without git dependencies. Incorporates user feedback: Emphasize easy-to-understand docs, confirm phases, select release-please with manual triggers, and add conventional commits, CONTRIBUTING.md updates, and Keep a Changelog standards.

## Status
- [x] Step 1: Update pyproject.toml for dynamic versioning using setuptools-scm
- [x] Step 2: Configure GitHub Actions workflow with release-please
- [x] Step 3: Add CI job for building distributions on releases
- [x] Step 4: Create concise documentation (README.md and CONTRIBUTING.md)
- [x] Step 5: Update CONTRIBUTING.md with standards
- [x] Step 6: Test the full process on the pypi-release-prep branch (versioning and build verified)
- [x] Step 7: Validate end-to-end (local install and functionality verified; TestPyPI upload held per user request)

## Steps
1. Update pyproject.toml for dynamic versioning using setuptools-scm, removing static version and adding scm config (it automatically derives versions from git tags without prompting).
2. Configure GitHub Actions workflow with release-please for automated releases: Handles changelog updates, version bumps, commits, tagging, and GitHub releases on merges to main (triggered by conventional commit PRs or manual workflow dispatch).
3. Add CI job for building distributions (wheel and sdist) on releases, ensuring packaging works.
4. Create concise, easy-to-understand documentation (e.g., update README.md and add PyPI section) explaining the release process, installation, and PyPI basics (account setup, tokens, TestPyPI).
5. Update CONTRIBUTING.md with conventional commits guidelines, Keep a Changelog format for changelogs, and other standards (e.g., semantic versioning, code style with Black, testing with pytest).
6. Test the full process on the pypi-release-prep branch: Simulate a release, verify versioning, build artifacts, and GitHub release creation.
7. Validate end-to-end: Ensure the tool can be installed via pip from TestPyPI and used in a sample Kodi addon project.

## Further Considerations
1. Release automation: Confirmed release-please (GitHub-native, simple PR-based flow, direct integration with releases). Uses manual workflow dispatch for control, creating release PRs from bot branch to main.
2. Teaching PyPI process: Yes—cover account creation, API tokens, uploading with twine, TestPyPI testing, and common issues like metadata validation.
3. Clean communications: Prioritize clarity and ease of understanding over minimal brevity; include examples and step-by-step guides.
4. End goal alignment: Yes—focus on seamless pip install for addon projects.
5. Phases: Yes—setup (versioning), automation (CI), testing (validation), docs (finalization).
6. Additional standards: Enforce semantic versioning (via release-please), code formatting (Black), linting (flake8), and testing (pytest with coverage). Require PRs for changes, and use pre-commit hooks for consistency. This ensures high-quality releases.

## Decisions
- Release tool: release-please with manual triggers.
- Versioning: setuptools-scm for dynamic versioning.
- Documentation: CONTRIBUTING.md for conventional commits and changelog standards.
- Triggers: Manual workflow dispatch to avoid conflicts with trunk-based development.
