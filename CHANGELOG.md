# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.6.0](https://github.com/brianpatrickreavey/kodi-addon-builder/compare/v0.5.0...v0.6.0) (2026-02-04)


### Features

* add automated build process ([d286a98](https://github.com/brianpatrickreavey/kodi-addon-builder/commit/d286a98c6f990bfbd306494ee06853761d9253b6))
* add build job to CI for required status checks ([f64733c](https://github.com/brianpatrickreavey/kodi-addon-builder/commit/f64733cf9eceac18ecf45bd3ac77d0667f9ed649))


### Bug Fixes

* align Black versions and update dependencies ([c90a0a6](https://github.com/brianpatrickreavey/kodi-addon-builder/commit/c90a0a6b468d66a00c5ef5e238c859515edb7bd0))
* Black version compatibility for CI ([c45ef62](https://github.com/brianpatrickreavey/kodi-addon-builder/commit/c45ef620d3f341c4186e51390443cede37afdc6f))
* install uv in build job to fix CI error ([f768b31](https://github.com/brianpatrickreavey/kodi-addon-builder/commit/f768b31f1266d2a5809433df3208c655ed6c7bb2))
* update release-please action to googleapis version ([5845151](https://github.com/brianpatrickreavey/kodi-addon-builder/commit/58451516429f52431415a2997fabb9e13dc8f6eb))
* use GITHUB_ACTIONS env var to detect CI vs act ([e388277](https://github.com/brianpatrickreavey/kodi-addon-builder/commit/e388277dbaa4eeba1ff78570a014659db8281598))
* use uv run for build commands in Makefile ([2c24f2f](https://github.com/brianpatrickreavey/kodi-addon-builder/commit/2c24f2fd97e8d91ef76f413de9f5a1ece9975fb2))

## [0.5.0] - 2026-02-04

### Changed
- **Breaking: Addon.xml detection** - Commands now only look for addon.xml in the current directory. Use `--addon-path` when running from repository root. This ensures deterministic behavior across different Python versions and filesystem implementations.
- **Python support** - Dropped Python 3.8 support, now requires Python >=3.9 to align with modern tooling requirements.

### Fixed
- **Non-deterministic test failures** - Fixed Python 3.12 test failures caused by `rglob()` returning files in non-deterministic order
- **Zip command path handling** - Fixed `--addon-path` option to properly resolve relative paths from repository root
- **Black configuration consistency** - Fixed discrepancy between `make format` and `pre-commit` Black formatting by updating pre-commit config to use explicit `--config pyproject.toml` and matching Black version (24.10.0)

---

## [0.4.1] - 2026-02-04

### Fixed
- **CI and pre-commit consistency** - Update CI workflow to use pre-commit hooks instead of manual linting commands
- **Comprehensive Python file checking** - Ensure all Python files (not just src/ tests/) are linted consistently
- **Pre-commit configuration** - Exclude .venv/ directory and check all other Python files
- **Development workflow gap** - Close inconsistency between local development and CI linting behavior

---

## [0.4.0] - 2026-02-04

### Added
- **Complete news formatting system** with Keep a Changelog markdown support
- **Enhanced release command** with required `--summary` and `--news` parameters
- **Addon.xml news section updates** with Kodi-compatible bracketed format ([new], [fix], [upd], etc.)
- **1500 character limit enforcement** for addon.xml news sections
- **Comprehensive dry-run mode** with preview file generation (`/dry-run` directory)
- **Integration testing infrastructure** with test addon (`script.module.test-kodi-addon-builder`)
- **Modern semver API** (no deprecation warnings)
- **Improved CLI** with simplified options and better error messages

### Changed
- **Release workflow** now requires both summary and news content
- **Addon.xml news format** updated to use bracketed categories instead of bullet points
- **Dry-run output** enhanced with complete file previews and executable git commands script
- **Test coverage** improved to 83% (from 48% by removing dead code)

### Removed
- **Deprecated CLI commands** (`bump`, `bump_commit`) replaced by enhanced `release` command
- **Old semver methods** updated to modern API
- **Dead code** (`cli-old.py`) removed

### Fixed
- **XML parsing** improved for both attribute and element-based version formats
- **Test expectations** updated for new dry-run message format
- **File cleanup** removed extraneous content from test files

---

## [0.3.6] - 2026-02-01
- Updated CI workflow to use uv export for dependency installation
- Improved CI dependency management with proper system Python installation
- Fixed Python 3.10 test failures by importing submodules in __init__.py
- Added --no-emit-project flag to uv export to prevent hash errors

## [0.3.5] - 2026-02-01
- Separated CI dependencies into dedicated `ci` group (anybadge)
- Updated CI workflow to use uv with system installation
- Improved dependency organization for better dev vs CI separation

## [0.3.4] - 2026-02-01
- Improved test coverage to 91%
- Added tests for --pyproject-file option in bump and release commands
- Added test for --version option
- Added test for __version__ fallback

## [0.3.3] - 2026-02-01
- Add --pyproject-file flag to bump, bump_commit, and release commands for updating pyproject.toml alongside addon.xml
- Fix __version__ to use importlib.metadata for the tool's version
- Add CLI --version flag
- Add pre-commit to dev dependencies

## [0.3.2] - 2026-02-01
- Add --pyproject-file flag to specify custom pyproject.toml for version info
- Add version command to display dynamic version
- Update pyproject.toml to use [dependency-groups] for uv compatibility

## [0.3.1] - 2026-02-01
- Fix AttributeError for missing __version__ attribute

## [0.3.0] - 2026-02-01
- Add changelog functionality to release command
- Set up uv for dependency management

## [0.2.0] - 2026-01-01
- Initial release
