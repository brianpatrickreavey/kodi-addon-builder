"""Kodi Addon Builder."""

try:
    from importlib.metadata import version

    __version__ = version("kodi-addon-builder")
except Exception:
    __version__ = "unknown"
