## Bug Report: NEWS Section Not Updated in addon.xml During Release

### Summary
`kodi-addon-builder release` command fails to update the `<news>` section in `addon.xml` during the release process, leaving outdated news information in the addon metadata.

### Environment
- **Tool Version:** kodi-addon-builder v0.3.7
- **Python Version:** 3.13.7
- **OS:** Linux (Ubuntu)
- **Installation:** Via uv/pip from custom git repo

### Expected Behavior
When running `kodi-addon-builder release [bump-type] --news "description"`, the tool should:
1. Update version numbers in addon.xml and pyproject.toml
2. Update CHANGELOG.md with new entry
3. **Update the `<news>` section in addon.xml** with the new version and provided news text
4. Commit all changes
5. Create and push git tag

This behavior is documented in the project's DEVELOPMENT.md and implemented in the custom `bump_version.py` script.

### Actual Behavior
- Version numbers are updated correctly in addon.xml and pyproject.toml
- CHANGELOG.md is updated with new entry
- **`<news>` section in addon.xml remains unchanged** with old version/news
- Release process appears to fail or abort before completing addon.xml news update
- Repository left in inconsistent state

### Steps to Reproduce

1. Have a Kodi addon project with existing `<news>` section in addon.xml
2. Run release command:
   ```bash
   kodi-addon-builder release patch --news "Bug fixes and improvements"
   ```
3. Check addon.xml after command completes/fails
4. Observe that `<news>` section still contains old version information

### Root Cause Analysis
This bug is likely related to the path resolution issue documented in the separate bug report. The tool probably:

1. Successfully updates version numbers and CHANGELOG.md
2. Attempts to update the addon.xml news section
3. Encounters the path resolution error when trying to process addon.xml file paths
4. Fails before completing the news section update
5. Leaves the addon.xml in partially updated state

The custom `bump_version.py` script shows the expected logic:
```python
# Update addon.xml news section
replacement_news = r'\g<1>' + new_version + ' - ' + news_text + r'\g<2>'
updated_content = re.sub(r'(<news>)[^<]*(</news>)', replacement_news, updated_content)
```

### Impact
- Addon metadata contains outdated news information
- Users see incorrect "what's new" information in Kodi addon manager
- Release process leaves repository in inconsistent state
- Manual intervention required to fix addon.xml news section

### Workaround
Manually update the `<news>` section in addon.xml after the failed release attempt, or use the custom `bump_version.py` script which correctly handles this update.

### Code Location
The bug likely occurs in the addon.xml processing logic in `cli.py`, possibly in the same area as the path resolution bug (around line 633 and similar locations).

### Relationship to Other Bugs
This issue appears to be a secondary symptom of the path resolution bug. When the path error occurs during addon.xml processing, it prevents the news section update from completing, even though other file updates succeed.

### Suggested Fix
Ensure that addon.xml news section updates are completed before any path-dependent operations that might fail. Consider updating the news section as part of the initial file processing phase rather than during the git operations phase.</content>
<parameter name="filePath">/home/bpreavey/Code/kodi.plugin.video.angelstudios/kodi-addon-builder-news-bug-report.md