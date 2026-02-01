"""Kodi Addon Builder."""

import tomllib
from pathlib import Path

# Read version from pyproject.toml
pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
with open(pyproject_path, "rb") as f:
    data = tomllib.load(f)
__version__ = data["project"]["version"]
