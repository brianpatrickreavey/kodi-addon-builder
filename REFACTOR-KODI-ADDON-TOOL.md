# REFACTOR-KODI-ADDON-TOOL.md

## Overview
This document outlines a potential future refactor of the kodi-addon-builder tool to use python-semantic-release instead of its current manual release process. This would automate releases, reduce maintenance, and align with modern practices, while preserving Kodi-specific features via custom scripts. Recent discussions have shifted focus toward adopting a conventional commit-style changelog (grouping by types like Features, Bug Fixes) instead of Keep a Changelog format, and exploring Jinja2 templating to generate addon.xml natively as a "changelog" output for version synchronization.

## Feature Comparison
| Feature | Kodi-Addon-Builder | Python-Semantic-Release | Gap/Workaround |
|---------|---------------------|-------------------------|----------------|
| **Release Trigger** | Manual command with `--summary` and `--news` parameters | Automatic on push with releasable commits | Gap: Manual vs. automatic. Workaround: Use conventional commits for automatic triggers, or run semantic-release manually if needed. |
| **Version Bumping** | Manual bump based on user input (patch, minor, major) | Automatic from commit types (e.g., `feat` -> minor, `fix` -> patch) | Gap: User-controlled vs. commit-driven. Workaround: Use specific commit types to control bumps (e.g., `feat` for minor). |
| **Changelog/Update Files** | Updates CHANGELOG.md and addon.xml with news in bracketed format ([new], [fix]) | Updates CHANGELOG.md in conventional commit style (grouped by type); can generate addon.xml via Jinja2 templating as a "changelog" output | Gap: Kodi-specific addon.xml formatting. Workaround: Use Jinja2 template for addon.xml with variables like {{ version }}, {{ commits }}, rendered during release. |
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
- Flexible templating for addon.xml and other files using Jinja2.

## Open Questions
- What specific commit types should we support (e.g., standard conventional like feat/fix, or custom like add/change)?
- How to handle Kodi-specific validations (e.g., news length/format) in the automated flow?
- Can Jinja2 templating fully replicate addon.xml updates, including bracketed news ([new], [fix])?
- What variables from semantic-release (version, commits, etc.) are sufficient for addon.xml templating?
- Should we maintain backward compatibility with manual releases?
- How to integrate with existing CI (e.g., GitHub Actions) and handle branches (e.g., main vs. release branches)?
- Tradeoffs: Automation vs. control—how much manual oversight is needed?

## Proposed CI Flow
1. **Development Branch**: Developers commit using conventional format (e.g., `feat: add new feature`).
2. **Accumulate Commits**: Push to main as needed; releases are not triggered on every push.
3. **Release Trigger Options**:
   - **Tag-Based**: When ready to bundle and release, push a "release" tag from dev environment (e.g., `git tag release && git push origin release`). CI detects the tag and runs semantic-release.
   - **PR Label-Based**: For short-lived feature branches, add a "release" label to the PR. On merge, CI checks the label and runs semantic-release if present.
   - In both cases, semantic-release:
     - Parses commits, bumps version.
     - Generates CHANGELOG.md (conventional style).
     - Renders addon.xml via Jinja2 template using version/commits variables.
     - Optionally generates RELEASE_NOTES.md via custom script.
     - Commits changes, creates `v.x.x.x` tag, pushes.
     - Cleans up (e.g., deletes "release" tag if used).
4. **Publishing**: Creates GitHub release with notes; optionally publishes to PyPI if applicable.
5. **Tag Management**: Only one "release" tag can exist at a time; if it already exists (conflict), manually delete it before pushing a new one. This prevents accidental multiple releases.

## Other Pertinent Details
- **Templating Variables**: Jinja2 has access to version, date, commits (list with type/subject/etc.), release, previous_release, unreleased_commits.
- **Custom Scripts**: Needed for Kodi validations, RELEASE_NOTES.md generation, and any post-release steps.
- **Testing**: Start with dry-run testing on a feature branch to avoid disrupting main.
- **Dependencies**: Ensure python-semantic-release v8+ for Jinja2 support; may need upgrades.
- **Risks**: Potential for incorrect addon.xml if templating fails; need robust error handling.

## Next Steps (Future)
- Design Jinja2 templates for addon.xml and changelog.
- Implement custom scripts for validations and RELEASE_NOTES.md.
- Test integration with existing kodi-addon-builder logic.
- Update documentation and workflows.
- Answer open questions through research and prototyping.

## Status
Active exploration—shifting from Keep a Changelog to conventional style and Jinja2 for addon.xml.