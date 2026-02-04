# Kodi Addon Builder

[![CI](https://github.com/brianpatrickreavey/kodi-addon-builder/actions/workflows/ci.yml/badge.svg)](https://github.com/brianpatrickreavey/kodi-addon-builder/actions/workflows/ci.yml)
![Coverage](https://raw.githubusercontent.com/brianpatrickreavey/kodi-addon-builder/badges/coverage-badge.svg)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A CLI tool to automate version management, git operations, and packaging for Kodi addons. Streamline your addon development workflow with commands for bumping versions, committing changes, creating tags, pushing to remotes, and generating release zips.

## Features

- **Version Bumping**: Automatically update `addon.xml` versions (major/minor/patch).
- **News Formatting**: Comprehensive news formatting system supporting Keep a Changelog markdown input with multiple output formats (commit messages, changelogs, addon.xml news sections).
- **Git Operations**: Commit, tag, and push changes with custom messages.
- **Release Automation**: Combine all operations into a single `release` command with news integration.
- **Addon.xml Updates**: Automatically update addon.xml news sections with Kodi-compatible bracketed format.
- **Zip Generation**: Create addon zips using `git archive` for clean, reproducible builds.
- **Pre-commit Integration**: Run hooks for code quality checks.
- **CI/CD Ready**: Example GitHub Actions workflow for automated releases.

## Installation

### From PyPI (Recommended)
```bash
pip install kodi-addon-builder
```

### From Source
Install directly from the git repository:

```bash
pip install git+https://github.com/brianpatrickreavey/kodi-addon-builder.git
```

Or clone and install locally:

```bash
git clone https://github.com/brianpatrickreavey/kodi-addon-builder.git
cd kodi-addon-builder
pip install -e .
```

## Quick Start

1. **Navigate to your addon directory** (containing `addon.xml`) or use `--addon-path`:
   ```bash
   # Option 1: Run from addon directory
   cd /path/to/your/kodi/addon
   kodi-addon-builder release patch \
     --summary "Fixed critical bug in playback" \
     --news "### Fixed\n- Resolved crash when loading videos\n- Fixed missing subtitles"

   # Option 2: Run from repo root with --addon-path
   cd /path/to/your/repo
   kodi-addon-builder release patch \
     --addon-path plugin.video.myaddon \
     --summary "Fixed critical bug in playback" \
     --news "### Fixed\n- Resolved crash when loading videos\n- Fixed missing subtitles"
   ```

2. **Build a zip**:
   ```bash
   kodi-addon-builder zip --output my-addon.zip
   ```

## Commands

### `release <bump_type> [options]`

**Complete release workflow**: bump version, update addon.xml news, update changelog, commit, tag, and push.

**Required parameters:**
- `<bump_type>`: `major`, `minor`, `patch`
- `--summary <text>`: Short summary for commit messages and changelog headers
- `--news <text>`: Detailed changes in Keep a Changelog markdown format

**Optional parameters:**
- `--addon-news <text>`: Custom summary for addon.xml news (if auto-generated exceeds 1500 chars)
- `--addon-path <path>`: Path to addon directory (required when running from repo root)
- `--pyproject-file <file>`: Path to pyproject.toml for version updates
- `--dry-run`: Preview all actions without making changes
- `--non-interactive`: Skip interactive prompts

**News Format Examples:**
```bash
# Basic release
kodi-addon-builder release patch \
  --summary "Fixed video playback issues" \
  --news "### Fixed\n- Resolved crash on startup\n- Fixed missing audio"

# Advanced release with custom addon news
kodi-addon-builder release minor \
  --summary "Added new streaming features" \
  --news "### Added\n- Support for HLS streams\n- New quality settings\n### Fixed\n- Memory leak in player" \
  --addon-news "New streaming features and bug fixes"
```

### `commit <message> [options]`

Create a git commit.

- `<message>`: Commit message
- `--repo-path <path>`: Git repository path
- `--allow-empty`: Allow empty commits

### `tag <tag_name> [options]`

Create and push a git tag.

- `<tag_name>`: Tag name (e.g., `v1.0.0`)
- `--message <text>`: Tag annotation message
- `--repo-path <path>`: Git repository path
- `--remote <name>`: Remote to push to (default: origin)

### `push [options]`

Push commits and tags.

- `--repo-path <path>`: Git repository path
- `--remote <name>`: Remote name (default: origin)
- `--branch <name>`: Branch to push (default: current branch)

### `zip [options]`

Generate a zip archive of the addon using `git archive`.

- `--output <file>`: Output zip file path (default: auto-generated)
- `--addon-path <path>`: Addon directory (required when running from repo root)
- `--full-repo`: Archive entire repository instead of addon directory
- `--commit <sha>`: Specific commit to archive (default: HEAD)
- `--exclude <patterns>`: Files/patterns to exclude from archive

## News Formatting

The news formatting system supports [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) markdown format for input and generates multiple output formats:

### Input Format (Keep a Changelog Markdown)

```markdown
### Added
- New feature description
- Another new feature

### Changed
- Modified existing functionality

### Fixed
- Bug fix description

### Removed
- Deprecated feature removal
```

### Output Formats

1. **Changelog (CHANGELOG.md)**: Full formatted changelog with version headers
2. **Addon.xml News**: Condensed summary for Kodi addon.xml (max 1500 characters)
3. **Git Commit Messages**: Short summary for commit messages

### Examples

**Simple patch release:**
```bash
kodi-addon-builder release patch \
  --summary "Fixed video playback issues" \
  --news "### Fixed\n- Resolved crash on startup\n- Fixed missing audio"
```

**Feature release with multiple changes:**
```bash
kodi-addon-builder release minor \
  --summary "Added new streaming features" \
  --news "### Added\n- Support for HLS streams\n- New quality settings\n### Fixed\n- Memory leak in player\n- Improved error handling"
```

**Breaking changes:**
```bash
kodi-addon-builder release major \
  --summary "API overhaul" \
  --news "### Changed\n- Complete API redesign\n- Breaking changes for custom integrations\n### Removed\n- Deprecated legacy methods"
```

### Auto-generated Addon.xml News

If `--addon-news` is not provided, the system automatically generates a summary from your news input. The summary is truncated to fit Kodi's 1500 character limit for addon.xml news sections.

## Workflows

### Local Development

For manual releases:
1. Develop and commit changes.
2. Run `kodi-addon-builder release <type> --summary "Brief description" --news "### Added\n- New features\n### Fixed\n- Bug fixes"` to bump version, update news, commit, tag, and push.
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
A: Fix the issues (e.g., run `make format` and `make lint`), then commit again.

## Troubleshooting

- **Command not found**: Ensure the tool is installed and in your PATH.
- **Git errors**: Check repo status and permissions.
- **Addon.xml not found**: Verify you're in the correct directory or use `--addon-path`.
- **CI failures**: Review GitHub Actions logs; ensure secrets (e.g., GITHUB_TOKEN) are set.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines, including commit message conventions and development standards.

1. Fork the repository.
2. Set up pre-commit hooks: `pre-commit install`
3. Create a feature branch.
4. Add tests for new features.
5. Run `make unittest-with-coverage` for testing with coverage, `make lint` for linting, `make format` for formatting.
6. Submit a pull request.

## License

MIT License - see [LICENSE](LICENSE) for details.# Build Process
The project now includes automated building and validation via CI.
