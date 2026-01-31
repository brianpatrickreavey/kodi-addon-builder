# Kodi Addon Builder

[![CI](https://github.com/brianpatrickreavey/kodi-addon-builder/actions/workflows/ci.yml/badge.svg)](https://github.com/brianpatrickreavey/kodi-addon-builder/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/brianpatrickreavey/kodi-addon-builder/branch/master/graph/badge.svg)](https://codecov.io/gh/brianpatrickreavey/kodi-addon-builder)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A CLI tool to automate version management, git operations, and packaging for Kodi addons. Streamline your addon development workflow with commands for bumping versions, committing changes, creating tags, pushing to remotes, and generating release zips.

## Features

- **Version Bumping**: Automatically update `addon.xml` versions (major/minor/patch).
- **Git Operations**: Commit, tag, and push changes with custom messages.
- **Release Automation**: Combine all operations into a single `release` command.
- **Zip Generation**: Create addon zips using `git archive` for clean, reproducible builds.
- **Pre-commit Integration**: Run hooks for code quality checks.
- **CI/CD Ready**: Example GitHub Actions workflow for automated releases.

## Installation

Install directly from the git repository:

```bash
pip install git+https://github.com/yourusername/kodi-addon-builder.git
```

Or clone and install locally:

```bash
git clone https://github.com/yourusername/kodi-addon-builder.git
cd kodi-addon-builder
pip install -e .
```

## Quick Start

1. **Navigate to your addon directory** (containing `addon.xml`):
   ```bash
   cd /path/to/your/kodi/addon
   ```

2. **Bump the version**:
   ```bash
   kodi-addon-builder bump minor
   ```

3. **Commit changes**:
   ```bash
   kodi-addon-builder commit "Bump version to 1.1.0"
   ```

4. **Create a release** (bumps, commits, tags, pushes):
   ```bash
   kodi-addon-builder release patch --news "Fixed bug X"
   ```

5. **Build a zip**:
   ```bash
   kodi-addon-builder zip --output my-addon.zip
   ```

## Commands

### `bump <bump_type> [options]`

Bump the version in `addon.xml`.

- `<bump_type>`: `major`, `minor`, `patch`
- `--addon-path <path>`: Path to addon directory (auto-detected if not specified)
- `--news <text>`: Changelog/news for the version
- `--non-interactive`: Skip prompts
- `--dry-run`: Show changes without applying

### `commit <message> [options]`

Stage and commit changes.

- `<message>`: Commit message
- `--repo-path <path>`: Git repo path
- `--allow-empty`: Allow empty commits

### `tag <tag_name> [options]`

Create and push a git tag.

- `<tag_name>`: Tag name (e.g., `v1.0.0`)
- `--message <text>`: Tag annotation
- `--repo-path <path>`: Git repo path
- `--remote <name>`: Remote to push to

### `push [options]`

Push commits and tags.

- `--repo-path <path>`: Git repo path
- `--remote <name>`: Remote name
- `--branch <name>`: Branch to push

### `zip [options]`

Generate a zip archive of the addon.

- `--output <file>`: Output zip file path
- `--addon-path <path>`: Addon directory
- `--full-repo`: Zip entire repo instead of addon directory
- `--commit <sha>`: Specific commit to archive
- `--exclude <patterns>`: Files/patterns to exclude

### `release <bump_type> [options]`

Full release workflow: bump version, commit, tag, push.

- `<bump_type>`: Version bump type
- `--addon-path <path>`: Addon directory
- `--news <text>`: Release notes
- `--non-interactive`: Skip prompts
- `--dry-run`: Preview actions
- `--repo-path <path>`: Git repo path
- `--remote <name>`: Remote for push
- `--branch <name>`: Branch to push
- `--no-pre-commit`: Skip pre-commit hooks

## Workflows

### Local Development

For manual releases:
1. Develop and commit changes.
2. Run `kodi-addon-builder release <type>` to bump, commit, tag, and push.
3. The tag triggers your CI/CD for zip building and releases.

### CI/CD with GitHub Actions

Use the example workflow in `docs/example-github-workflow.yml`:

- **On push to branches**: Build test zips for CI.
- **On tag push**: Build versioned zip, create GitHub release with zip attached.

Copy to your addon's `.github/workflows/` and customize.

### Pre-commit Hooks

Set up code quality checks:

1. Install pre-commit: `pip install pre-commit`
2. Copy `docs/example-pre-commit-config.yaml` to `.pre-commit-config.yaml`
3. Run `pre-commit install`
4. Hooks run on commit: black (formatting), flake8 (linting).

## FAQ

**Q: Why does `release` fail with "Working directory has uncommitted changes"?**
A: Commit or stash all changes before running `release` to ensure clean versioning.

**Q: How do I customize the zip contents?**
A: Use `--exclude` for patterns, or `--full-repo` for the entire repository.

**Q: Can I use this for non-Kodi projects?**
A: The tool is Kodi-specific due to `addon.xml` parsing, but git operations are general.

**Q: What if pre-commit hooks fail?**
A: Fix the issues (e.g., run `black .` and `flake8 .`), then commit again.

## Troubleshooting

- **Command not found**: Ensure the tool is installed and in your PATH.
- **Git errors**: Check repo status and permissions.
- **Addon.xml not found**: Verify you're in the correct directory or use `--addon-path`.
- **CI failures**: Review GitHub Actions logs; ensure secrets (e.g., GITHUB_TOKEN) are set.

## Contributing

1. Fork the repository.
2. Set up pre-commit hooks: `pre-commit install`
3. Create a feature branch.
4. Add tests for new features.
5. Run `make unittest-with-coverage` (or `python -m pytest --cov=src/kodi_addon_builder`).
6. Submit a pull request.

## License

MIT License - see [LICENSE](LICENSE) for details.