#!/usr/bin/env python3
"""Kodi Addon Builder CLI tool."""

import xml.etree.ElementTree as ET
from pathlib import Path

import click
import semver

from .git_operations import (
    get_repo,
    run_pre_commit_hooks,
    stage_changes,
    commit_changes,
    create_tag,
    push_commits,
    push_tags,
    get_current_branch,
    create_zip_archive,
    get_addon_relative_path,
)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """CLI tool for Kodi addon version management and packaging."""
    pass  # pragma: no cover


def find_addon_xml(start_path=None):
    """Find addon.xml file dynamically."""
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path)

    for path in start_path.rglob("addon.xml"):
        return path
    return None


def validate_addon_xml(addon_path):
    """Validate addon.xml structure and version format."""
    try:
        tree = ET.parse(addon_path)
        root = tree.getroot()
        if root.tag != "addon":
            raise ValueError("Root element is not 'addon'")
        version = root.get("version")
        if not version:
            raise ValueError("No version attribute found")
        # Validate version format
        semver.VersionInfo.parse(version)
        return tree, root, version
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML: {e}")
    except ValueError as e:
        if "Invalid XML" in str(e) or "Root element" in str(e) or "No version" in str(e):
            raise  # Re-raise as is
        else:
            raise ValueError(f"Invalid version: {e}")


def bump_version(current_version, bump_type):
    """Bump the version based on type."""
    version = semver.VersionInfo.parse(current_version)
    if bump_type == "major":
        return str(version.bump_major())
    elif bump_type == "minor":
        return str(version.bump_minor())
    elif bump_type == "patch":
        return str(version.bump_patch())
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")  # pragma: no cover


@click.command()
@click.argument("bump_type", type=click.Choice(["major", "minor", "patch"]))
@click.option(
    "--addon-path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Path to the addon directory containing addon.xml",
)
@click.option("--news", help="News/changelog entry for this version")
@click.option("--non-interactive", is_flag=True, help="Run in non-interactive mode")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
def bump(bump_type, addon_path, news, non_interactive, dry_run):
    """Bump the version in addon.xml."""
    # Find addon.xml
    if addon_path:
        addon_dir = Path(addon_path)
        addon_xml_path = addon_dir / "addon.xml"
        if not addon_xml_path.exists():
            raise click.ClickException(f"addon.xml not found at {addon_xml_path}")
    else:
        addon_xml_path = find_addon_xml()
        if not addon_xml_path:
            raise click.ClickException("Could not find addon.xml in current directory or subdirectories")
        addon_dir = addon_xml_path.parent

    click.echo(f"Found addon.xml at: {addon_xml_path}")

    # Validate and parse
    try:
        tree, root, current_version = validate_addon_xml(addon_xml_path)
    except ValueError as e:
        raise click.ClickException(f"Invalid addon.xml: {e}")

    click.echo(f"Current version: {current_version}")

    # Bump version
    try:
        new_version = bump_version(current_version, bump_type)
    except ValueError as e:
        raise click.ClickException(f"Failed to bump version: {e}")

    click.echo(f"New version: {new_version}")

    # Handle news
    if not news and not non_interactive:
        news = click.prompt("Enter news/changelog for this version", default="")

    if news:
        click.echo(f"News: {news}")  # pragma: no cover

    # Dry run
    if dry_run:
        click.echo("Dry run: No changes made")
        return

    # Update XML
    root.set("version", new_version)
    tree.write(addon_xml_path, encoding="UTF-8", xml_declaration=True)

    click.echo(f"Updated addon.xml with version {new_version}")


@click.command()
@click.option("--message", "-m", required=True, help="Commit message")
@click.option("--files", multiple=True, help="Specific files to stage (default: all changes)")
@click.option("--allow-empty", is_flag=True, help="Allow empty commits")
@click.option("--no-pre-commit", is_flag=True, help="Skip pre-commit hook checks")
@click.option(
    "--repo-path", type=click.Path(exists=True, dir_okay=True, file_okay=False), help="Path to the git repository"
)
def commit(message, files, allow_empty, no_pre_commit, repo_path):
    """Stage and commit changes with a custom message."""
    try:
        repo = get_repo(Path(repo_path) if repo_path else None)
    except ValueError as e:
        raise click.ClickException(str(e))

    click.echo(f"Repository: {repo.working_dir}")

    # Run pre-commit hooks
    if not no_pre_commit:
        try:
            run_pre_commit_hooks(repo)
        except ValueError as e:
            raise click.ClickException(str(e))

    # Stage changes
    try:
        stage_changes(repo, list(files) if files else None)
    except Exception as e:
        raise click.ClickException(f"Failed to stage changes: {e}")

    # Commit
    try:
        commit_hash = commit_changes(repo, message, allow_empty)
        click.echo(f"Committed changes: {commit_hash}")
    except ValueError as e:
        raise click.ClickException(str(e))


@click.command()
@click.argument("tag_name")
@click.option("--message", "-m", help="Tag message (creates annotated tag)")
@click.option(
    "--repo-path", type=click.Path(exists=True, dir_okay=True, file_okay=False), help="Path to the git repository"
)
def tag(tag_name, message, repo_path):
    """Create a git tag."""
    try:
        repo = get_repo(Path(repo_path) if repo_path else None)
    except ValueError as e:
        raise click.ClickException(str(e))

    click.echo(f"Repository: {repo.working_dir}")

    try:
        create_tag(repo, tag_name, message)
        click.echo(f"Created tag: {tag_name}")
    except ValueError as e:
        raise click.ClickException(str(e))


@click.command()
@click.option("--branch", "-b", help="Branch to push (default: current branch)")
@click.option("--tags", is_flag=True, help="Also push tags")
@click.option("--remote", default="origin", help="Remote name (default: origin)")
@click.option(
    "--repo-path", type=click.Path(exists=True, dir_okay=True, file_okay=False), help="Path to the git repository"
)
def push(branch, tags, remote, repo_path):
    """Push commits and optionally tags to remote."""
    try:
        repo = get_repo(Path(repo_path) if repo_path else None)
    except ValueError as e:
        raise click.ClickException(str(e))

    click.echo(f"Repository: {repo.working_dir}")

    # Push commits
    try:
        push_commits(repo, remote, branch)
        current_branch = branch or get_current_branch(repo)
        click.echo(f"Pushed branch: {current_branch}")
    except ValueError as e:
        raise click.ClickException(str(e))

    # Push tags if requested
    if tags:
        try:
            push_tags(repo, remote)
            click.echo("Pushed tags")
        except ValueError as e:
            raise click.ClickException(str(e))


@click.command()
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(dir_okay=False),
    help="Output path for the zip file (default: auto-generated)",
)
@click.option("--commit", default="HEAD", help="Git commit/tag to archive (default: HEAD)")
@click.option("--full-repo", is_flag=True, help="Archive the full repository instead of addon-only")
@click.option("--exclude", multiple=True, help="Files/patterns to exclude from archive")
@click.option(
    "--addon-path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Path to the addon directory containing addon.xml",
)
@click.option(
    "--repo-path", type=click.Path(exists=True, dir_okay=True, file_okay=False), help="Path to the git repository"
)
def zip_cmd(output_path, commit, full_repo, exclude, addon_path, repo_path):
    """Create a zip archive of the addon using git archive."""
    # Get repo
    try:
        repo = get_repo(Path(repo_path) if repo_path else None)
    except ValueError as e:
        raise click.ClickException(str(e))

    click.echo(f"Repository: {repo.working_dir}")

    # Find addon.xml
    if addon_path:
        addon_dir = Path(addon_path)
        addon_xml_path = addon_dir / "addon.xml"
        if not addon_xml_path.exists():
            raise click.ClickException(f"addon.xml not found at {addon_xml_path}")
    else:
        addon_xml_path = find_addon_xml()
        if not addon_xml_path:
            raise click.ClickException("Could not find addon.xml in current directory or subdirectories")
        addon_dir = addon_xml_path.parent

    click.echo(f"Found addon.xml at: {addon_xml_path}")

    # Validate addon.xml
    try:
        tree, root, version = validate_addon_xml(addon_xml_path)
    except ValueError as e:
        raise click.ClickException(f"Invalid addon.xml: {e}")

    addon_id = root.get("id")
    if not addon_id:
        raise click.ClickException("addon.xml missing 'id' attribute")

    click.echo(f"Addon ID: {addon_id}, Version: {version}")

    # Determine output path
    if not output_path:
        output_path = f"{addon_id}-{version}.zip"
    output_path = Path(output_path)

    # Determine what to archive
    if full_repo:
        paths = None  # Archive entire repo
        click.echo("Archiving full repository")
    else:
        # Archive only the addon directory
        try:
            addon_rel_path = get_addon_relative_path(repo, addon_xml_path)
            paths = [addon_rel_path]
            click.echo(f"Archiving addon directory: {addon_rel_path}")
        except ValueError as e:
            raise click.ClickException(f"Failed to determine addon path: {e}")

    # Create the archive
    try:
        create_zip_archive(repo, output_path, commit, paths, list(exclude) if exclude else None)
        click.echo(f"Created zip archive: {output_path}")
    except ValueError as e:
        raise click.ClickException(str(e))


@click.command()
@click.argument("bump_type", type=click.Choice(["major", "minor", "patch"]))
@click.option(
    "--addon-path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Path to the addon directory containing addon.xml",
)
@click.option("--news", help="News/changelog entry for this version")
@click.option("--non-interactive", is_flag=True, help="Run in non-interactive mode")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.option(
    "--repo-path", type=click.Path(exists=True, dir_okay=True, file_okay=False), help="Path to the git repository"
)
@click.option("--remote", default="origin", help="Remote name (default: origin)")
@click.option("--branch", "-b", help="Branch to push (default: current branch)")
@click.option("--no-pre-commit", is_flag=True, help="Skip pre-commit hook checks")
@click.option("--allow-empty-commit", is_flag=True, help="Allow empty commits")
def release(
    bump_type, addon_path, news, non_interactive, dry_run, repo_path, remote, branch, no_pre_commit, allow_empty_commit
):
    """Bump version, commit, tag, and push in one command."""
    # Find addon.xml
    if addon_path:
        addon_dir = Path(addon_path)
        addon_xml_path = addon_dir / "addon.xml"
        if not addon_xml_path.exists():
            raise click.ClickException(f"addon.xml not found at {addon_xml_path}")
    else:
        addon_xml_path = find_addon_xml()
        if not addon_xml_path:
            raise click.ClickException("Could not find addon.xml in current directory or subdirectories")
        addon_dir = addon_xml_path.parent

    click.echo(f"Found addon.xml at: {addon_xml_path}")

    # Validate and parse
    try:
        tree, root, current_version = validate_addon_xml(addon_xml_path)
    except ValueError as e:
        raise click.ClickException(f"Invalid addon.xml: {e}")

    click.echo(f"Current version: {current_version}")

    # Bump version
    try:
        new_version = bump_version(current_version, bump_type)
    except ValueError as e:
        raise click.ClickException(f"Failed to bump version: {e}")

    click.echo(f"New version: {new_version}")

    # Handle news
    if not news and not non_interactive:
        news = click.prompt("Enter news/changelog for this version", default="")

    if news:
        click.echo(f"News: {news}")

    # Dry run
    if dry_run:
        click.echo("Dry run: No changes made")
        click.echo(f"Would bump version to {new_version}")
        click.echo(f"Would commit with message: 'Bump version to {new_version}'")
        click.echo(f"Would create tag: v{new_version}")
        click.echo(f"Would push branch and tags to {remote}")
        return

    # Get repo
    try:
        repo = get_repo(Path(repo_path) if repo_path else None)
        # Check git cleanliness
        if repo.is_dirty():
            raise click.ClickException(
                "Working directory has uncommitted changes. Please commit or stash them before releasing."
            )
    except ValueError as e:
        raise click.ClickException(str(e))  # pragma: no cover

    click.echo(f"Repository: {repo.working_dir}")

    # Update XML
    root.set("version", new_version)
    tree.write(addon_xml_path, encoding="UTF-8", xml_declaration=True)
    click.echo(f"Updated addon.xml with version {new_version}")

    # Run pre-commit hooks
    if not no_pre_commit:
        try:
            run_pre_commit_hooks(repo)
        except ValueError as e:
            raise click.ClickException(str(e))  # pragma: no cover

    # Stage changes
    try:
        stage_changes(repo, [str(addon_xml_path.relative_to(repo.working_dir))])
    except Exception as e:
        raise click.ClickException(f"Failed to stage changes: {e}")  # pragma: no cover

    # Commit
    commit_message = f"Bump version to {new_version}"
    if news:
        commit_message += f"\n\n{news}"
    try:
        commit_hash = commit_changes(repo, commit_message, allow_empty_commit)
        click.echo(f"Committed changes: {commit_hash}")
    except ValueError as e:
        raise click.ClickException(str(e))  # pragma: no cover

    # Create tag
    tag_name = f"v{new_version}"
    tag_message = f"Release version {new_version}"
    if news:
        tag_message += f"\n\n{news}"
    try:
        create_tag(repo, tag_name, tag_message)
        click.echo(f"Created tag: {tag_name}")
    except ValueError as e:
        raise click.ClickException(str(e))  # pragma: no cover

    # Push commits
    try:
        push_commits(repo, remote, branch)
        current_branch = branch or get_current_branch(repo)
        click.echo(f"Pushed branch: {current_branch}")
    except ValueError as e:
        raise click.ClickException(str(e))  # pragma: no cover

    # Push tags
    try:
        push_tags(repo, remote)
        click.echo("Pushed tags")
    except ValueError as e:
        raise click.ClickException(str(e))  # pragma: no cover

    click.echo(f"Successfully released version {new_version}")


main.add_command(bump)
main.add_command(commit)
main.add_command(tag)
main.add_command(push)
main.add_command(zip_cmd, name="zip")
main.add_command(release)
