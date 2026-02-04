## Bug Report: Path Resolution Error in kodi-addon-builder v0.3.7

### Summary
`kodi-addon-builder` fails with a `ValueError` when using `--addon-path` or `--pyproject-file` options with relative paths. The error occurs during path calculation when trying to make relative paths between mixed absolute/relative Path objects.

### Environment
- **Tool Version:** kodi-addon-builder v0.3.7
- **Python Version:** 3.13.7
- **OS:** Linux (Ubuntu)
- **Installation:** Via uv/pip

### Steps to Reproduce

1. Have a Kodi addon project with structure:
   ```
   project/
   ├── plugin.video.addon/
   │   └── addon.xml
   ├── pyproject.toml
   └── ...other files
   ```

2. Run release command with explicit relative paths:
   ```bash
   kodi-addon-builder release patch --addon-path plugin.video.addon --pyproject-file pyproject.toml --news "Test release"
   ```

3. Tool fails with:
   ```
   ValueError: 'plugin.video.addon/addon.xml' is not in the subpath of '/path/to/project'
   ```

### Root Cause
The bug occurs in `cli.py` at line 633 (and similar locations) where the code calls:
```python
str(addon_xml_path.relative_to(repo.working_dir))
```

**Problem:**
- `addon_xml_path` is a relative Path object (e.g., `plugin.video.addon/addon.xml`)
- `repo.working_dir` is an absolute path string (e.g., `/path/to/project`)

The `Path.relative_to()` method requires both paths to be the same type (both absolute or both relative). Mixing types causes the ValueError.

### Expected Behavior
- Tool should handle relative path arguments correctly
- Should resolve paths properly before calling `relative_to()`
- Release process should complete successfully

### Actual Behavior
- Tool updates version files successfully
- Fails during git operations with path resolution error
- Leaves repository in partially updated state

### Workaround
Use auto-detection by omitting `--addon-path` and `--pyproject-file` options:
```bash
kodi-addon-builder release patch --news "Test release"
```

### Code Fix Suggestion
Ensure both paths are absolute before calling `relative_to()`:

```python
# Instead of:
addon_xml_path.relative_to(repo.working_dir)

# Use:
addon_xml_path.absolute().relative_to(Path(repo.working_dir))
```

Or resolve relative paths to absolute first:
```python
addon_xml_path = Path(addon_path).resolve()
```

### Additional Context
- Auto-detection works perfectly (no path arguments needed)
- Bug only occurs when explicitly specifying relative paths
- Tool successfully updates addon.xml, CHANGELOG.md, and pyproject.toml before failing
- Git operations (commit/tag/push) fail due to the path error

### Impact
- Blocks automated release workflows when using explicit paths
- Requires manual completion of release process
- Inconsistent behavior between auto-detection and explicit path modes

This appears to be a regression or untested code path in the path handling logic. The auto-detection path works correctly, suggesting the explicit path handling needs the same path resolution fixes.</content>
<parameter name="filePath">/home/bpreavey/Code/kodi.plugin.video.angelstudios/kodi-addon-builder-bug-report.md