# REFACTOR-KODI-ADDON-TOOL.md

## Overview
This document outlines a potential future refactor of the kodi-addon-builder tool to use python-semantic-release instead of its current manual release process. This would automate releases, reduce maintenance, and align with modern practices, while preserving Kodi-specific features via custom scripts.

## Feature Comparison
| Feature | Kodi-Addon-Builder | Python-Semantic-Release | Gap/Workaround |
|---------|---------------------|-------------------------|----------------|
| **Release Trigger** | Manual command with `--summary` and `--news` parameters | Automatic on push with releasable commits | Gap: Manual vs. automatic. Workaround: Use conventional commits for automatic triggers, or run semantic-release manually if needed. |
| **Version Bumping** | Manual bump based on user input (patch, minor, major) | Automatic from commit types (e.g., `feat` -> minor, `fix` -> patch) | Gap: User-controlled vs. commit-driven. Workaround: Use specific commit types to control bumps (e.g., `feat` for minor). |
| **Changelog/Update Files** | Updates CHANGELOG.md and addon.xml with news in bracketed format ([new], [fix]) | Updates CHANGELOG.md in Keep a Changelog format; can edit other files via custom scripts | Gap: Kodi-specific addon.xml formatting. Workaround: Custom script to update addon.xml with bracketed news during release. |
| **Release Notes Generation** | Generates RELEASE_NOTES.md file with formatted news | Generates GitHub release notes from changelog | Gap: Separate file vs. inline notes. Workaround: Custom script to generate RELEASE_NOTES.md and commit it. |
| **Dry-Run Mode** | Preview mode with dry-run directory and git commands script | `--dry-run` flag for simulation without changes | Gap: Detailed preview files vs. simple simulation. Workaround: Use dry-run to check output, then manually verify. |
| **Git Operations** | Commits changes, creates tags, pushes | Commits changelog/version, creates tags, pushes | No gap—both handle git operations. |
| **Validation/Checks** | Validates news length, format | Basic commit analysis | Gap: Kodi-specific validations. Workaround: Add custom scripts for validation before release. |
| **PyPI Publishing** | Not included | Built-in PyPI publishing | Gap: Kodi-builder doesn't publish. Workaround: N/A (semantic-release adds this). |
| **GitHub Integration** | Basic git | Creates GitHub releases with notes | Gap: No GitHub releases. Workaround: N/A (semantic-release adds this). |
| **Automation Level** | Manual per release | Fully automated on commits | Gap: Manual vs. automated. Workaround: Adopt conventional commits for automation. |

## Potential Benefits
- Reduce manual release steps.
- Automate versioning and publishing.
- Leverage conventional commits for consistency.
- Maintain Kodi features with scripts.

## Next Steps (Future)
- Design custom scripts for addon.xml updates and RELEASE_NOTES.md.
- Test integration with existing kodi-addon-builder logic.
- Update documentation and workflows.

## Status
Deferred for now—focus on main project release automation first.