# Kodi Addon Builder - Implementation Plan

## Overview
This project creates a reusable CLI tool (`kodi-addon-builder`) to automate version bumping, committing, tagging, pushing, releasing, and local zip artifact generation for Kodi addons. It will be packaged as a Python project installable via pip from git, with an example GitHub Actions workflow, pre-commit hooks setup, and comprehensive README.md.

## Executable Steps

### 1. Project Setup ✅
- Initialize Python project structure with `pyproject.toml` for packaging and dependencies.
- Define dependencies: `click` (CLI), `gitpython` (Git ops), `semver` (versioning), `xml.etree` (addon.xml parsing).
- Create basic CLI entry point with Click.

### 2. Implement Version Bump Command ✅
- Create `bump` subcommand to parse and update addon.xml (detect path dynamically or via --addon-path).
- Support bump types (major/minor/patch), news input, non-interactive mode, and dry-run.
- Validate addon.xml structure and version format.
- Include comprehensive unit and integration tests.

### 3. Implement Git Operations ✅
- Add `commit` subcommand to stage and commit changes with custom messages.
- Add `tag` subcommand to create and push tags (e.g., v1.0.0).
- Add `push` subcommand for pushing commits and tags.
- Support custom branching and pre-commit hook checks.
- Include comprehensive unit and integration tests.

### 4. Implement Zip Generation ✅
- Create `zip` subcommand using `git archive` for local artifacts.
- Options: full repo or addon-only, custom commit, output path, exclusions.
- Validate git repo and addon.xml presence.

### 5. Implement Release Command ✅
- Combine bump, commit, tag, push into a `release` subcommand.
- Add git cleanliness check to ensure no uncommitted changes before release.
- Include comprehensive unit and integration tests with error handling.

### 6. Add Example GitHub Actions Workflow and Pre-commit Setup ✅
- Create `docs/example-github-workflow.yml` as a template for CI/CD (tag-triggered releases with zip building).
- Create `docs/example-pre-commit-config.yaml` with black, flake8, and optional pyright hooks.
- Set up pre-commit hooks in the repo for code quality (black + flake8).
- Demonstrate zip building, artifact upload, and automated releases.

### 7. Write Comprehensive README.md
- Overview, installation, quick start, command reference, workflows, examples, FAQ.

### 8. Testing and Validation
- Unit tests for each command (mock git/addon.xml).
- Integration tests with sample addon.
- Validate zip contents and git state.
- Achieve high test coverage (96%+ with pragma for error paths).

### 9. Publish and Integrate
- Push to git repo.
- Update addon projects' requirements-dev.txt to install via git+https://github.com/user/kodi-addon-builder.git.

## Further Considerations
1. Support custom branching and hooks.
2. Addon.xml validation and security exclusions.
3. Local zips for dev, example workflow for CI/CD.
4. Optional GitHub release creation via gh CLI for manual releases.
5. Pre-commit hooks for fast code quality checks (black, flake8).
6. Git cleanliness checks in release to prevent dirty commits.