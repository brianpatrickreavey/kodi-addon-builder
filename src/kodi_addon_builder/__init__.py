"""Kodi Addon Builder."""

try:
    from importlib.metadata import version

    __version__ = version("kodi-addon-builder")
except Exception:
    __version__ = "unknown"

# Import submodules to make them available for patching
from . import cli, git_operations  # noqa: F401
