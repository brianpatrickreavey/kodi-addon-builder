# Clean Reset Plan for python-semantic-release Adoption

## Overview
Reset git history to clean state, start versioning at v0.0.0, enable allow_zero_version, and test on isolated branch. Follow best practices: clean history, good documentation, plan adherence, reassess as needed.

## Answers to Key Questions
1. **Version numbers in commits**: Removing old tags should prevent issues. Semantic-release uses tags for versioning; old commit messages won't affect unless conventionally formatted.
2. **History scanning**: If starting with no tags, it scans all history. Pre-conventional commits may be ignored or classified as "unknown". Tag starting commit as v0.0.0 to limit scanning to post-tag commits.
3. **Testing on non-master**: Yes, works by configuring `branches = ["master", "adopt-semantic-release"]` in semantic-release config. Allows releases/testing on the branch.

## Steps
1. **Reset master**: `git reset --hard 0b1c774` (clean rollback point).
2. **Delete old tags**: `git tag -d v0.3.0 v0.4.0 v0.5.0` (remove detached tags).
3. **Create fresh v0.0.0**: `git tag -a v0.0.0 -m "v0.0.0"` on 0b1c774.
4. **Force push**: `git push origin master --force` (sync with GitHub).
5. **Create new branch**: `git checkout -b adopt-semantic-release`.
6. **Setup on branch**:
   - Add python-semantic-release to pyproject.toml dev deps.
   - Configure [tool.semantic_release] with scipy parser, allow_zero_version = true, branches = ["master", "adopt-semantic-release"], custom commit types.
   - Update CI workflow for release job.
   - Create CONTRIBUTING.md.
   - Create custom parser in src/kodi_addon_builder/custom_parser.py.
7. **Test incrementally**: Dry-runs on branch, reassess after each step.
8. **Merge when stable**: To master, then manual GitHub changes.

## Risks
- Force push rewrites history; backups exist.
- Old history ignored; start fresh at v0.0.0.

## Backup Location
Plan backed up to /tmp/kodi_backup/.


# Notes from the Architect as we go.
Why do we need .semantic-release.toml when we have pyproject.toml?

