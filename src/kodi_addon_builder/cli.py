#!/usr/bin/env python3
"""Kodi Addon Builder CLI tool."""

import click


@click.group()
@click.version_option(version="0.1.0")
def main():
    """A CLI tool to automate version bumping, committing, tagging, pushing, releasing, and local zip artifact generation for Kodi addons."""
    pass


if __name__ == "__main__":
    main()