#!/usr/bin/env python3
"""Kodi Addon Builder CLI tool."""

import os
import xml.etree.ElementTree as ET
from pathlib import Path

import click
import semver


@click.group()
@click.version_option(version="0.1.0")
def main():
    """A CLI tool to automate version bumping, committing, tagging, pushing, releasing, and local zip artifact generation for Kodi addons."""
    pass


def find_addon_xml(start_path=None):
    """Find addon.xml file dynamically."""
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path)

    for path in start_path.rglob('addon.xml'):
        return path
    return None


def validate_addon_xml(addon_path):
    """Validate addon.xml structure and version format."""
    try:
        tree = ET.parse(addon_path)
        root = tree.getroot()
        if root.tag != 'addon':
            raise ValueError("Root element is not 'addon'")
        version = root.get('version')
        if not version:
            raise ValueError("No version attribute found")
        # Validate version format
        semver.VersionInfo.parse(version)
        return tree, root, version
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML: {e}")
    except ValueError as e:
        raise ValueError(f"Invalid version: {e}")


def bump_version(current_version, bump_type):
    """Bump the version based on type."""
    version = semver.VersionInfo.parse(current_version)
    if bump_type == 'major':
        return str(version.bump_major())
    elif bump_type == 'minor':
        return str(version.bump_minor())
    elif bump_type == 'patch':
        return str(version.bump_patch())
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


@click.command()
@click.argument('bump_type', type=click.Choice(['major', 'minor', 'patch']))
@click.option('--addon-path', type=click.Path(exists=True, dir_okay=True, file_okay=False),
              help='Path to the addon directory containing addon.xml')
@click.option('--news', help='News/changelog entry for this version')
@click.option('--non-interactive', is_flag=True, help='Run in non-interactive mode')
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
def bump(bump_type, addon_path, news, non_interactive, dry_run):
    """Bump the version in addon.xml."""
    # Find addon.xml
    if addon_path:
        addon_dir = Path(addon_path)
        addon_xml_path = addon_dir / 'addon.xml'
        if not addon_xml_path.exists():
            click.echo(f"Error: addon.xml not found at {addon_xml_path}", err=True)
            return
    else:
        addon_xml_path = find_addon_xml()
        if not addon_xml_path:
            click.echo("Error: Could not find addon.xml in current directory or subdirectories", err=True)
            return
        addon_dir = addon_xml_path.parent

    click.echo(f"Found addon.xml at: {addon_xml_path}")

    # Validate and parse
    try:
        tree, root, current_version = validate_addon_xml(addon_xml_path)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        return

    click.echo(f"Current version: {current_version}")

    # Bump version
    try:
        new_version = bump_version(current_version, bump_type)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        return

    click.echo(f"New version: {new_version}")

    # Handle news
    if not news and not non_interactive:
        news = click.prompt("Enter news/changelog for this version", default="")

    if news:
        click.echo(f"News: {news}")

    # Dry run
    if dry_run:
        click.echo("Dry run: No changes made")
        return

    # Update XML
    root.set('version', new_version)
    tree.write(addon_xml_path, encoding='UTF-8', xml_declaration=True)

    click.echo(f"Updated addon.xml with version {new_version}")


main.add_command(bump)


if __name__ == "__main__":
    main()