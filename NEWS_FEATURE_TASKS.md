# Task List: Enhanced News Formatting & Addon.xml News Section Updates

## Overview
Implement comprehensive news formatting system that supports different output formats for commit messages, changelog entries, and addon.xml news sections. Add missing addon.xml news section updates with proper Kodi-compatible formatting.

## Current State Analysis
- ✅ **News Input**: `--news` parameter accepts raw text
- ✅ **Changelog**: Basic markdown formatting (`- {news}`)
- ✅ **Commit Messages**: First line extraction (`v{version}: {first_line}`)
- ❌ **Addon.xml News**: **MISSING** - no updates to `<news>` section
- ❌ **Format Flexibility**: No support for different output formats

## Proposed CLI Design

### CLI Design Options

**Final Decision: Require BOTH --summary AND --news for releases**
```bash
# Both required for meaningful releases
kodi-addon-builder release patch \
  --summary "Security fixes and dependency updates" \
  --news "### Security\n- Fixed authentication bypass\n- Updated SSL certificates"

# Error cases:
kodi-addon-builder release patch  # ❌ No summary/news
kodi-addon-builder release patch --summary "Fixes"  # ❌ No news
kodi-addon-builder release patch --news "..."  # ❌ No summary
```

**Rationale:**
- Ensures clean, meaningful commit messages
- Guarantees changelog and addon.xml news updates
- Forces users to provide both summary and detailed changes
- Maintains high quality release documentation

### New CLI Options
- `--summary TEXT`: **Required** for releases - short summary for commit messages and changelog
- `--news TEXT`: **Required** for releases - detailed changes in Keep a Changelog markdown format
- `--addon-news TEXT`: **Optional** - custom summary for addon.xml news (used when auto-generated exceeds 1500 chars)

## Format Specifications

### Input Format Requirements
- **MANDATORY**: Keep a Changelog markdown format with `###` section headers
- **Required sections**: `### Added`, `### Fixed`, `### Changed`, `### Deprecated`, `### Removed`, `### Security`
- **Bullet points**: `-`, `*`, `+` for list items under each section
- **Validation**: Error if input doesn't contain proper `###` section headers
- **No plain text**: All news input must be structured markdown

### Output Formats

**✅ DECIDED: Option A - Require Summary**
- `--summary` is **mandatory** for all release commands
- Forces meaningful commit messages and changelog entries
- Clear user intent with no automatic fallbacks
- Detailed news content still supported in changelog and addon.xml

**Recommendation: Add `--summary` option**
- Allows user control over commit message
- Avoids misleading automatic extraction
- Maintains backward compatibility (fallback to extraction)
- Clear separation: summary for commits, full news for changelog/addon.xml

**2. Changelog Format (Keep a Changelog)**
- Full markdown with proper structure
- Format: `## [{version}] - {date}\n{formatted_news}\n`
- Preserve markdown formatting: headers, lists, links, etc.
- Support all Keep a Changelog sections

**3. Addon.xml News Format**
- **Exact same data** as changelog, different formatting
- Kodi-compatible bracketed format
- Format:
  ```
  v{version} ({date})
  [new] Added search functionality
  [fix] Resolved playback crash on startup
  [fix] Fixed missing icon in menu
  [upd] Updated dependencies
  ```
- **1500 character limit** (Kodi addon.xml constraint)
- Bracket categories: `[new]`, `[fix]`, `[upd]`, `[rem]`, `[sec]`, etc.
- Each item on separate line
- Plain text (no markdown)

### Character Limit Handling

**Addon.xml News: 1500 character limit** (enforced by Kodi)

**✅ DECIDED: Error on exceedance, no automatic truncation**
- **Changelog/Markdown**: No length limit - full expressiveness
- **Addon.xml**: **ERROR** if rendered output >1500 characters
- **Error message**: "addon news limited to 1500 characters rendered (current news is XXX). either shorten news, or provide summary in --addon-news flag"
- **Solution**: Use `--addon-news TEXT` flag for custom concise summary
- **Forces user choice**: Either shorten content or provide explicit summary
- Preserve version/date header, truncate from bottom of list
- Allow users to override with `--force` flag if needed

**Rationale:**
- Changelog should be comprehensive and detailed
- Addon.xml needs to be concise for Kodi UI
- Truncation preserves most important information
- Users get warned about truncation
- No artificial constraints on changelog expressiveness

**Alternative Considered:** Force all content <1500 characters
- Rejected because it would constrain changelog expressiveness unnecessarily

---

## Data Flow: Summary vs News

**✅ DECIDED: Summary included in changelog release line**

**Format:**
```
## [1.1.1] - 2023-03-05 - Security fixes and dependency updates

### Security
- Fixed authentication bypass
- Updated SSL certificates

### Changed
- Updated dependencies
```

**Data Flow:**
- **`--summary`**: Used for commit message (`release: v{version} - {summary}`) AND changelog release line
- **`--news`**: Used for detailed changelog sections AND addon.xml news (converted to bracketed format)

**Addon.xml News Format:**
```
v1.1.1 (2023-03-05)
Security fixes and dependency updates
[new] Added search functionality
[fix] Resolved playback crash on startup
[fix] Fixed missing icon in menu
[upd] Updated dependencies
[rem] Removed deprecated API calls
[sec] Fixed authentication bypass
[dep] Marked old methods as deprecated
```

**✅ DECIDED: Use Keep a Changelog bracket codes**
- `[new]` for Added sections
- `[fix]` for Fixed sections
- `[upd]` for Changed sections
- `[rem]` for Removed sections
- `[sec]` for Security sections
- `[dep]` for Deprecated sections

**Character Impact Assessment:**
- Each bracket code: 6 characters (`[new] ` including space)
- Very minimal impact on 1500 character limit
- Consistent with Keep a Changelog standards
- Familiar to users of structured changelogs

**✅ DECIDED: Bracket Categories - Use Keep a Changelog standards**

**Standard Bracket Codes Mapping:**
- `[new]` ← `### Added` sections
- `[fix]` ← `### Fixed` sections
- `[upd]` ← `### Changed` sections
- `[dep]` ← `### Deprecated` sections
- `[rem]` ← `### Removed` sections
- `[sec]` ← `### Security` sections

**Example Input → Output:**
```markdown
### Added
- New search functionality
- Added user preferences

### Fixed
- Resolved crash on startup
- Fixed missing icons

### Security
- Updated SSL certificates
```
**Becomes:**
```
[new] New search functionality
[new] Added user preferences
[fix] Resolved crash on startup
[fix] Fixed missing icons
[sec] Updated SSL certificates
```

**✅ DECIDED: Date Format - ALWAYS ISO format**
- Use `2023-01-02` format in addon.xml news
- Consistent with Keep a Changelog standards
- ISO format is unambiguous and sortable

**✅ DECIDED: Truncation Strategy - Error on >1500 characters**
- If rendered addon news >1500 characters: **ERROR** with message:
  > "addon news limited to 1500 characters rendered (current news is XXX). either shorten news, or provide summary in --addon-news flag"
- Add optional `--addon-news TEXT` flag for custom addon.xml summary
- Forces users to be concise for Kodi compatibility
- No automatic truncation - user must explicitly choose summary or shorten

**✅ DECIDED: CLI Options - Always markdown, no format options**
- Input **MUST** be markdown with `###` section headers
- Error if news doesn't contain expected `### Added/Fixed/Changed/etc.` formats
- No `--news-format` or `--addon-news-format` options
- Simplifies CLI, enforces structured input
- Clear error messages guide users to proper format

### GitHub Release Integration

**Problem**: GitHub's auto-generated release notes from commit messages are too brief
**Solution**: Automatically generate detailed release notes file for GitHub releases

**Automatic Behavior**:
- RELEASE_NOTES.md is generated for every release command
- Contains full changelog details for rich GitHub release notes

**GitHub Workflow Update**:
```yaml
- name: Create GitHub Release
  uses: softprops/action-gh-release@v2
  with:
    files: plugin.video.angelstudios-${{ github.ref_name }}.zip
    body_path: RELEASE_NOTES.md  # Automatically generated by release command
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**RELEASE_NOTES.md Format**:
```
# Release Notes - v{version}

## [{version}] - {date} - {summary}

### Security
- Fixed authentication bypass
- Updated SSL certificates

### Changed
- Updated dependencies
```

**Benefits:**
- Clear "Release Notes" branding for GitHub releases
- Maintains full changelog structure for consistency
- Professional appearance in GitHub release body
- Still compatible with CHANGELOG.md format

5. **CLI Options**: Do we still want `--news-format` and `--addon-news-format` options, or should this be automatic based on input detection?

Please review and let me know your preferences on these points!

## Implementation Tasks

### Phase 1: Core News Formatting System

#### 1.1 Create News Formatter Module
- [x] New file: `src/kodi_addon_builder/news_formatter.py`
- [x] Classes: `NewsFormatter` (simplified architecture - single class)
- [x] Methods: `format_for_commit()`, `format_for_changelog()`, `format_for_addon_news()`, `format_for_release_notes()`

#### 1.2 Implement Format Detection
- [x] Auto-detect input format (markdown vs plain text via validation)
- [x] Support explicit format specification (not implemented - markdown mandatory)
- [x] Validate format options (regex validation for ### headers)

#### 1.3 Add CLI Options
- [ ] Update `release` command to require both `--summary` and `--news`
- [ ] Add validation to ensure both are provided together
- [ ] Add `--addon-news` optional flag for custom addon.xml summaries
- [ ] **Automatically generate RELEASE_NOTES.md for all releases**
- [ ] Add clear error messages when either is missing
- [ ] Add `--news-format` and `--addon-news-format` options
- [ ] Update help text to reflect new requirements

### Phase 2: Addon.xml News Section Updates

#### 2.1 Implement News Section Logic
- [x] Add `update_addon_news()` function in `cli.py`
- [x] Handle existing news sections (update) and missing sections (create)
- [x] Use proper XML manipulation (ElementTree with namespace support)

#### 2.2 XML Structure Handling
- [x] Parse addon.xml to find/update `<news>` elements
- [x] Support nested news elements within `<extension point="xbmc.addon.metadata">`
- [x] Preserve XML formatting and encoding (namespace-aware)

#### 2.3 Error Handling
- [x] Graceful handling of malformed XML
- [x] Validation of news content
- [x] Fallback behavior for edge cases
- [x] **1500 character limit enforcement: ERROR if exceeded**
- [x] Error message: "addon news limited to 1500 characters rendered (current news is XXX). either shorten news, or provide summary in --addon-news flag"
- [ ] Support for `--addon-news` custom summary override (function exists, CLI not integrated)

### Phase 3: Integration & Testing

#### 3.1 Update Existing Commands
- [ ] Modify `bump_commit()` and `release()` to call news section updates
- [ ] Ensure proper ordering: version → news → changelog → commit
- [ ] Handle dry-run mode for news sections

#### 3.2 Comprehensive Test Coverage
- [x] Unit tests for news formatter (18 tests, 100% coverage)
- [x] Integration tests for addon.xml updates (utility functions tested)
- [x] Test different input formats and output conversions
- [x] Test edge cases: missing news sections, malformed XML, etc.

#### 3.3 Update Test Fixtures
- [x] Add sample addon.xml with news sections (test fixtures exist)
- [x] Update existing tests to verify news section updates
- [x] Add format conversion tests (comprehensive test suite)

### Phase 4: Documentation & Examples

#### 4.1 Update Documentation
- [ ] README.md: Document new CLI options and format examples
- [ ] Add examples for different news formats
- [ ] Document addon.xml news section behavior

#### 4.2 Example Workflows
- [ ] Basic release with news
- [ ] Advanced release with custom formatting
- [ ] Migration guide for existing users

## Technical Implementation Details

### News Formatter Architecture
```python
class NewsFormatter:
    def __init__(self, news_text: str, input_format: str = 'auto'):
        self.news_text = news_text
        self.input_format = self._detect_format() if input_format == 'auto' else input_format

    def format_for_commit(self, summary: str) -> str:
        """Use provided summary for commit message (required when news provided)"""
        return summary

    def format_for_changelog(self) -> str:
        """Return markdown-formatted changelog entry"""
        if self.input_format == 'markdown':
            return self._clean_markdown()
        return f"- {self.news_text}"

    def format_for_addon_news(self, version: str, date: str) -> str:
        """Return Kodi bracketed format for addon.xml news section"""
        # Parse Keep a Changelog markdown and convert to bracketed format
        lines = []
        lines.append(f"v{version} ({date})")

        current_bracket = None

        for line in self.news_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Convert Keep a Changelog headers to bracketed categories
            if line.startswith('### '):
                category = line[4:].lower().strip()
                if category in ['added', 'new']:
                    current_bracket = '[new]'
                elif category in ['fixed', 'bug', 'bugs']:
                    current_bracket = '[fix]'
                elif category == 'security':
                    current_bracket = '[sec]'
                elif category in ['changed', 'updated', 'update']:
                    current_bracket = '[upd]'
                elif category in ['removed', 'deleted', 'delete']:
                    current_bracket = '[rem]'
                elif category == 'deprecated':
                    current_bracket = '[dep]'
                else:
                    current_bracket = f'[{category[:3]}]'
                continue  # Skip header lines

            # Convert bullet points to bracketed items
            if line.startswith(('- ', '* ', '+ ')) and current_bracket:
                item_text = line[2:].strip()
                lines.append(f"{current_bracket} {item_text}")

        return '\n'.join(lines)
```

### Addon.xml News Section Structure
```xml
<addon>
  <extension point="xbmc.addon.metadata">
    <news>
v1.2.3 (2023-01-02)
[new] Added search functionality
[fix] Resolved playback crash on startup
[fix] Fixed missing icon in menu
[sec] Fixed authentication bypass vulnerability
[upd] Updated dependencies
    </news>
  </extension>
</addon>
```

**Example Conversion:**
```
Input (Keep a Changelog markdown):
### Fixed
- Resolved playback crash on startup
- Fixed missing icon in menu
### Security
- Fixed authentication bypass vulnerability
### Changed
- Updated dependencies

Output (addon.xml):
v1.2.3 (2023-01-02)
[fix] Resolved playback crash on startup
[fix] Fixed missing icon in menu
[sec] Fixed authentication bypass vulnerability
[upd] Updated dependencies
```

### Backward Compatibility
- Existing `--news` usage continues to work unchanged
- Default formats maintain current behavior
- No breaking changes to existing workflows

## Success Criteria
- [x] All existing tests pass (NewsFormatter tests)
- [ ] Release command requires both `--summary` and `--news` parameters
- [x] News sections update correctly in addon.xml with bracketed format (utility functions work)
- [x] Different output formats work as expected (commit, changelog, addon.xml)
- [x] 1500 character limit enforced for addon.xml news
- [x] Backward compatibility maintained for other commands
- [x] Comprehensive test coverage (>95%) - **ACHIEVED: 100% for NewsFormatter**
- [ ] Documentation updated with examples

## Risk Assessment
- **Low Risk**: New functionality, not modifying core logic
- **Mitigation**: Extensive testing, gradual rollout
- **Fallback**: Can disable addon news updates if issues arise

## Timeline Estimate
- Phase 1: 2-3 days (core formatting system) - **COMPLETED**
- Phase 2: 1-2 days (addon.xml integration) - **COMPLETED**
- Phase 3: 2-3 days (testing & integration) - **UNIT TESTS COMPLETED, INTEGRATION PENDING**
- Phase 4: 1 day (documentation) - **NOT STARTED**
- **Phase 5: 1-2 days (integration testing setup with dummy addon)** - **NOT STARTED**

**Total: ~1-2 weeks** for complete implementation and testing.
**Progress: ~40% complete** - Core system and testing done, CLI integration and docs remaining.

## Integration Testing Setup

### Dummy Kodi Addon for Testing

**Purpose**: Create a test addon for integration testing the news formatting system without affecting real addons

#### Test Addon Structure
- [ ] Create `test-addon/` directory with minimal Kodi addon structure
- [ ] Addon ID: `script.module.newsformatting` (script addon type)
- [ ] `addon.xml` starting at version `1.2.3` with existing news section
- [ ] `CHANGELOG.md` with sample historical entries
- [ ] Basic addon metadata for testing

#### Dry-Run Mode Implementation
- [ ] Add `--dry-run` flag to release commands
- [ ] **✅ DECIDED: Creates `/dry-run` directory in current working directory** (where command is run, usually addon root)
- [ ] Copies actual files that would be modified:
  - `addon.xml` (with proposed news section updates)
  - `CHANGELOG.md` (with proposed new entries)
  - `RELEASE_NOTES.md` (generated release notes)
- [ ] **✅ DECIDED: Creates executable `git-commands.sh` script** for manual release completion (actual git commands, not echo statements)

#### Dry-Run Output Format
**git-commands.sh** (executable):
```bash
#!/bin/bash
# Dry-run: Commands that would be executed
# Can be run manually to complete the release after reviewing dry-run files

git add addon.xml CHANGELOG.md RELEASE_NOTES.md
git commit -m 'release: v1.1.1 - Security fixes and dependency updates'
git tag v1.1.1
git push origin main --tags
```

#### Testing Scenarios
- [ ] Test major/minor/patch releases from v1.2.3 baseline
- [ ] Test with various news formats (security, features, fixes)
- [ ] Test 1500 character limit enforcement and --addon-news override
- [ ] Test error cases (missing summary, malformed markdown)
- [ ] Manual execution of git-commands.sh after dry-run review

#### Usage Example
```bash
cd test-addon
kodi-addon-builder release patch \
  --summary "Security fixes" \
  --news "### Security\n- Fixed auth bypass" \
  --dry-run

# Creates /dry-run/ with:
# - addon.xml (modified)
# - CHANGELOG.md (modified)
# - RELEASE_NOTES.md (generated)
# - git-commands.sh (script)
```