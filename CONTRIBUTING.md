# Contributing

## Commit Message Conventions

This project uses conventional commits for automated versioning and changelog generation.

### Commit Types

Use the following types in your commit messages:

- `add:` - New features or additions (minor version bump)
- `change:` - Changes to existing functionality (minor version bump)
- `deprecate:` - Deprecations (minor version bump)
- `remove:` - Removals or breaking changes (major version bump)
- `fix:` - Bug fixes (patch version bump)
- `security:` - Security fixes (patch version bump)

### Format

```
<type>: <description>

[optional body]

[optional footer]
```

Example:
```
fix: resolve issue with addon.xml parsing

The parser was not handling empty news sections correctly.

Closes #123
```

### Version Bumping

- `add`, `change`, `deprecate` → Minor version
- `fix`, `security` → Patch version
- `remove` → Major version