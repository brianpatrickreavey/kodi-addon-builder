## Plan: Adopt python-semantic-release for kodi-addon-builder Releases

Adopt python-semantic-release to automate project releases with full Keep a Changelog compliance, custom commit types covering all categories (Added, Changed, Deprecated, Removed, Fixed, Security), GitHub releases with changelog notes, and initial dummy PyPI publishing (echo/mock). Start from current 0.5.x version post-rollback, drop RELEASE_NOTES.md generation, and prioritize changelog alignment. Test thoroughly with dry-runs and GitHub attempts before enabling automation.

**Steps**
1. **Complete Cleanup Phase**: Confirm rollback to commit 0b1c774, delete v0.6.0 tag/release/PR, mark RELEASE-PLAN.md as aborted, verify no release-please traces remain.
2. **Setup python-semantic-release**: Add to pyproject.toml dev dependencies; configure in pyproject.toml with scipy parser, custom commit types (add/minor, change/minor, deprecate/minor, remove/major, fix/patch, security/patch); update .github/workflows/ci.yml to add release job after tests; update CONTRIBUTING.md with new commit types; ensure PYPI_TOKEN secret (initially mock).
3. **Address Changelog Gaps**: Since default sections don't match Keep a Changelog exactly, create custom commit parser (inherit ScipyCommitParser) with LONG_TYPE_NAMES mapping (e.g., "add": "Added") and custom changelog template for correct section names/ordering. Test with dry-run to verify.
4. **Testing Phase**: Run local dry-runs; use act for CI simulation; create dummy commits on test branch (e.g., `add: test feature`, `fix: test bug`) and verify bumps/changelog; attempt a dry-run release on GitHub if supported, or simulate with real commits on test branch.
5. **Manual GitHub Changes**: Set branch protection for master requiring build/test checks; enable repo features for commits/PRs/issues; add PYPI_TOKEN secret (mock initially).
6. **Deployment and Go-Live**: Merge setup changes; monitor first automated release; switch to real PyPI publishing later.

**Verification**
Run `semantic-release --dry-run` locally to check version bumps, changelog updates, and mock publishing. Use `act` for workflow simulation. On test branch, push dummy commits and verify GitHub release creation (or simulate). After go-live, confirm first release generates correct changelog/GitHub notes without overwriting existing entries.

**Decisions**
- Scope: Adopt for project releases only; defer tool refactor per REFACTOR-KODI-ADDON-TOOL.md.
- Addon.xml/Release Notes: N/A (tool doesn't use addon.xml; drop RELEASE_NOTES.md, use GitHub notes).
- Commit Types: Use add/change/deprecate/remove/fix/security with specified bumps; custom parser/template for Keep a Changelog sections.
- PyPI: Start with dummy publisher (echo); confirm token later.
- Version: Start from 0.5.x (e.g., 0.5.1 next).
- Changelog: Appends to existing CHANGELOG.md; custom setup ensures compatibility.
- Testing: Dry-runs, act, dummy commits; attempt GitHub release if possible.