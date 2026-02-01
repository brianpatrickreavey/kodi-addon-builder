"""Kodi Addon Builder."""

import tomllib
from pathlib import Path

_version = "unknown"

def _load_version(path=None):
    global _version
    pyproject_path = Path(path) if path else Path.cwd() / "pyproject.toml"
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        _version = data["project"]["version"]
    except (FileNotFoundError, KeyError):
        _version = "unknown"

_load_version()

__version__ = _version
