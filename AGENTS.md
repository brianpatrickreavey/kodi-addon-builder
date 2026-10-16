# Agent Instructions

CLI tool to version, tag, and package Kodi addons (`kodi-addon-builder`). GitHub: `brianpatrickreavey/kodi-addon-builder`.

On a new machine:

```bash
git clone https://github.com/brianpatrickreavey/kodi-addon-builder.git
cd kodi-addon-builder
git checkout adopt-semantic-release   # WIP: python-semantic-release + custom commit parser
uv sync
```

Treat questions as read-only. Do not edit unless the user uses explicit action language.

`.github/copilot-instructions.md` still has the Angel Studios plugin header (copy-paste). Prefer this file. Ask-first still applies.

WIP on `adopt-semantic-release`: custom conventional commit parser in `src/kodi_addon_builder/custom_parser.py`, notes in `REFACTOR-KODI-ADDON-TOOL.md`. Two local git stashes exist on the old machine only (tiny, likely stale).
