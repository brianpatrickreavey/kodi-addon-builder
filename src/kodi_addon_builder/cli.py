#!/usr/bin/env python3
"""Kodi Addon Builder CLI tool."""

import xml.etree.ElementTree as ET
from datetime import date
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

from .news_formatter import NewsFormatter
from . import __version__


@click.group()
@click.version_option(version=__version__)
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

        # Get version from addon element attribute
        version = root.get("version")
        if version:
            version = version.strip()
        else:
            # Fallback: look for version element in metadata extension
            extension = None
            for elem in root:
                # Handle namespaced tags
                tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if tag_name == "extension" and elem.get("point") == "xbmc.addon.metadata":
                    extension = elem
                    break

            if extension is None:
                raise ValueError("Could not find xbmc.addon.metadata extension in addon.xml")

            # Extract version
            version_elem = None
            for elem in extension:
                tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if tag_name == "version":
                    version_elem = elem
                    break

            if version_elem is None or version_elem.text is None:
                raise ValueError("Version not found in addon.xml")

            version = version_elem.text.strip()

        try:
            semver.Version.parse(version)
        except ValueError as e:
            raise ValueError(f"Invalid version format in addon.xml: {e}")

        return tree, root, version

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in addon.xml: {e}")
    except FileNotFoundError:
        raise ValueError(f"addon.xml not found at {addon_path}")


def update_addon_xml(addon_path, new_version):
    """Update version in addon.xml."""
    tree, root, _ = validate_addon_xml(addon_path)

    # Try to update version attribute on addon element first (preferred method)
    if root.get("version") is not None:
        root.set("version", new_version)
    else:
        # Fallback: update version element in metadata extension
        extension = None
        for elem in root:
            tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag_name == "extension" and elem.get("point") == "xbmc.addon.metadata":
                extension = elem
                break

        if extension is None:
            raise ValueError("Could not find xbmc.addon.metadata extension in addon.xml")

        version_elem = None
        for elem in extension:
            tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag_name == "version":
                version_elem = elem
                break

        if version_elem is None:
            raise ValueError("Version element not found in addon.xml")

        version_elem.text = new_version

    tree.write(addon_path, encoding="UTF-8", xml_declaration=True)


def bump_version(current_version, bump_type):
    """Bump version according to semver."""
    try:
        version_obj = semver.Version.parse(current_version)
        if bump_type == "major":
            return str(version_obj.bump_major())
        elif bump_type == "minor":
            return str(version_obj.bump_minor())
        elif bump_type == "patch":
            return str(version_obj.bump_patch())
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
    except Exception as e:
        raise ValueError(f"Failed to bump version: {e}")


def update_pyproject_version(pyproject_path, new_version):
    """Update version in pyproject.toml."""
    import sys

    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib

    try:
        import tomli_w
    except ImportError:
        raise ValueError("tomli_w is required to update pyproject.toml. Install it with: pip install tomli_w")

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    # Handle different pyproject.toml formats
    if "project" in data:
        data["project"]["version"] = new_version
    elif "tool" in data and "poetry" in data["tool"]:
        data["tool"]["poetry"]["version"] = new_version
    else:
        raise ValueError("Unsupported pyproject.toml format")

    with open(pyproject_path, "wb") as f:
        tomli_w.dump(data, f)


def update_changelog(changelog_path, version, news):
    """Update CHANGELOG.md with new version entry."""
    header = f"## [{version}] - {date.today().isoformat()}\n\n{news}\n\n"

    if changelog_path.exists():
        with open(changelog_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Insert after the header (after the --- line)
        lines = content.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("---"):
                insert_idx = i + 2
                break
        lines.insert(insert_idx, header)
        new_content = "\n".join(lines)
    else:
        # Create new changelog
        changelog_header = (
            "# Changelog\n\n"
            "All notable changes to this project will be documented in this file.\n\n"
            "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),\n"
            "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n\n"
            "---\n\n"
        )
        new_content = f"{changelog_header}{header}"

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def update_changelog_with_content(changelog_path, new_entry_content):
    """
    Update CHANGELOG.md by inserting new entry content after the header.

    Args:
        changelog_path: Path to CHANGELOG.md file
        new_entry_content: Full formatted changelog entry to insert
    """
    header = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
"""

    if changelog_path.exists():
        with open(changelog_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Find the separator and insert after it
        sep = "\n---\n"
        if sep in content:
            parts = content.split(sep, 1)
            new_content = parts[0] + sep + new_entry_content + parts[1]
        else:
            # Fallback: assume content starts with old header, replace and add sep
            if content.startswith("# Changelog\n\n"):
                rest = content[len("# Changelog\n\n") :]
                new_content = header + new_entry_content + rest
            else:
                new_content = header + new_entry_content + content
    else:
        new_content = header + new_entry_content

    # Ensure the directory exists
    changelog_path.parent.mkdir(parents=True, exist_ok=True)
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def update_addon_news(addon_xml_path, news_content):
    """
    Update the <news> section in addon.xml.

    Args:
        addon_xml_path: Path to addon.xml file
        news_content: Formatted news content for addon.xml

    Raises:
        ValueError: If XML structure is invalid or news section cannot be updated
    """
    try:
        tree = ET.parse(addon_xml_path)
        root = tree.getroot()

        # Find the extension element (should be the main addon metadata)
        extension = None
        for elem in root:
            # Handle namespaced tags
            tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag_name == "extension" and elem.get("point") == "xbmc.addon.metadata":
                extension = elem
                break

        if extension is None:
            raise ValueError("Could not find xbmc.addon.metadata extension in addon.xml")

        # Find or create news element
        news_elem = None
        for elem in extension:
            tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag_name == "news":
                news_elem = elem
                break

        if news_elem is None:
            # Create new news element with proper namespace
            ns = root.tag.split("}")[0] + "}" if "}" in root.tag else ""
            news_elem = ET.SubElement(extension, f"{ns}news")

        # Update news content
        news_elem.text = news_content

        # Write back to file with proper formatting
        tree.write(addon_xml_path, encoding="UTF-8", xml_declaration=True)

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in addon.xml: {e}")
    except Exception as e:
        raise ValueError(f"Failed to update addon.xml news section: {e}")


@click.command()
@click.option("--message", "-m", required=True, help="Commit message")
@click.option("--files", multiple=True, help="Specific files to stage (default: all changes)")
@click.option("--allow-empty", is_flag=True, help="Allow empty commits")
@click.option("--no-pre-commit", is_flag=True, help="Skip pre-commit hook checks")
@click.option(
    "--repo-path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Path to the git repository",
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
@click.option(
    "--repo-path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Path to the git repository",
)
@click.option("--message", "-m", help="Tag message")
def tag(tag_name, repo_path, message):
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
@click.option(
    "--repo-path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Path to the git repository",
)
@click.option("--remote", default="origin", help="Remote name (default: origin)")
@click.option("--branch", "-b", help="Branch to push (default: current branch)")
@click.option("--tags", is_flag=True, help="Also push tags")
def push(repo_path, remote, branch, tags):
    """Push commits and optionally tags."""
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
@click.option(
    "--full-repo",
    is_flag=True,
    help="Archive the full repository instead of addon-only",
)
@click.option("--exclude", multiple=True, help="Files/patterns to exclude from archive")
@click.option(
    "--addon-path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Path to the addon directory containing addon.xml",
)
@click.option(
    "--repo-path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Path to the git repository",
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

    # Archive
    if full_repo:
        # Archive the entire repo
        paths = None
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
        create_zip_archive(repo, Path(output_path), commit, paths, list(exclude) if exclude else None)
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
@click.option(
    "--pyproject-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to pyproject.toml to also update version in",
)
@click.option("--summary", required=True, help="Short summary for commit message and changelog header")
@click.option("--news", required=True, help="Detailed news in Keep a Changelog markdown format")
@click.option("--addon-news", help="Custom summary for addon.xml news (used when auto-generated exceeds 1500 chars)")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
def release(
    bump_type,
    addon_path,
    pyproject_file,
    summary,
    news,
    addon_news,
    dry_run,
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
    changelog_path = addon_dir / "CHANGELOG.md"

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

    # Validate and create news formatter
    try:
        news_formatter = NewsFormatter(summary=summary, news=news, version=new_version)
    except ValueError as e:
        raise click.ClickException(f"Invalid news format: {e}")

    click.echo(f"Summary: {summary}")
    click.echo("News content validated and parsed")

    # Dry run
    if dry_run:
        click.echo("Dry run: Creating preview files in /dry-run directory")
        click.echo(f"Would bump version to {new_version}")
        click.echo(f"Would commit with message: '{news_formatter.format_for_commit()}'")
        click.echo(f"Would create tag: v{new_version}")
        click.echo("Would push branch and tags to origin")
        if pyproject_file:
            click.echo(f"Would update {pyproject_file} with version {new_version}")

        # Create dry-run directory
        dry_run_dir = Path.cwd() / "dry-run"
        try:
            dry_run_dir.mkdir(exist_ok=True)
            click.echo(f"Created dry-run directory: {dry_run_dir}")

            # Copy and modify addon.xml
            addon_xml_dry = dry_run_dir / "addon.xml"
            try:
                addon_xml_dry.write_text(addon_xml_path.read_text(encoding="utf-8"))
                update_addon_xml(addon_xml_dry, new_version)
                addon_news_content = news_formatter.format_for_addon_news(custom_summary=addon_news)
                update_addon_news(addon_xml_dry, addon_news_content)
                click.echo("Created addon.xml with proposed changes")
            except (OSError, FileNotFoundError):
                click.echo("Note: Could not create addon.xml preview (file access issue)")

            # Copy and modify CHANGELOG.md
            changelog_dry = dry_run_dir / "CHANGELOG.md"
            try:
                changelog_dry.write_text(changelog_path.read_text(encoding="utf-8"))
                changelog_content = news_formatter.format_for_changelog()
                update_changelog_with_content(changelog_dry, changelog_content)
                click.echo("Created CHANGELOG.md with proposed changes")
            except (OSError, FileNotFoundError):
                click.echo("Note: Could not create CHANGELOG.md preview (file access issue)")

            # Create RELEASE_NOTES.md
            release_notes_dry = dry_run_dir / "RELEASE_NOTES.md"
            try:
                release_notes_content = news_formatter.format_for_release_notes()
                release_notes_dry.write_text(release_notes_content)
                click.echo("Created RELEASE_NOTES.md with release notes")
            except OSError:
                click.echo("Note: Could not create RELEASE_NOTES.md (file access issue)")

            # Create git-commands.sh script
            git_commands_script = dry_run_dir / "git-commands.sh"
            try:
                commit_message = news_formatter.format_for_commit()
                git_commands_content = f"""#!/bin/bash
# Dry-run: Commands that would be executed
# Can be run manually to complete the release after reviewing dry-run files

git add addon.xml CHANGELOG.md RELEASE_NOTES.md
git commit -m '{commit_message}'
git tag v{new_version}
git push origin HEAD --tags
"""
                if pyproject_file:
                    git_commands_content = git_commands_content.replace(
                        "git add addon.xml CHANGELOG.md RELEASE_NOTES.md",
                        f"git add addon.xml CHANGELOG.md RELEASE_NOTES.md {Path(pyproject_file).name}",
                    )

                git_commands_script.write_text(git_commands_content)
                git_commands_script.chmod(0o755)  # Make executable
                click.echo("Created executable git-commands.sh script")

                click.echo("\nTo complete the release after review:")
                click.echo(f"1. Review files in {dry_run_dir}")
                click.echo("2. Run: ./dry-run/git-commands.sh")
            except OSError:
                click.echo("Note: Could not create git-commands.sh script (file access issue)")

        except OSError:
            click.echo("Note: Could not create dry-run directory (permission issue)")
            click.echo("Dry-run completed with preview only")
        return

    # Get repo for git operations
    repo = get_repo(None)  # Auto-detect from current directory

    # Update addon.xml version
    root.set("version", new_version)
    tree.write(addon_xml_path, encoding="UTF-8", xml_declaration=True)

    # Update CHANGELOG.md
    changelog_content = news_formatter.format_for_changelog()
    update_changelog_with_content(changelog_path, changelog_content)

    # Update addon.xml news section
    addon_news_content = news_formatter.format_for_addon_news(custom_summary=addon_news)
    update_addon_news(addon_xml_path, addon_news_content)

    # Update pyproject.toml if provided
    if pyproject_file:
        update_pyproject_version(pyproject_file, new_version)

    click.echo(f"Updated addon.xml and CHANGELOG.md with version {new_version}")
    if pyproject_file:
        click.echo(f"Updated {pyproject_file} with version {new_version}")

    # Run pre-commit hooks (always for release workflow)
    try:
        run_pre_commit_hooks(repo)
    except ValueError as e:
        raise click.ClickException(str(e))  # pragma: no cover

    # Stage changes
    repo_path = Path(repo.working_dir)
    files_to_stage = [
        str(addon_xml_path.resolve().relative_to(repo_path)),
        str(changelog_path.resolve().relative_to(repo_path)),
    ]
    if pyproject_file:
        files_to_stage.append(str(Path(pyproject_file).resolve().relative_to(repo_path)))
    try:
        stage_changes(repo, files_to_stage)
    except Exception as e:
        raise click.ClickException(f"Failed to stage changes: {e}")  # pragma: no cover

    # Commit
    commit_message = news_formatter.format_for_commit()
    try:
        commit_hash = commit_changes(repo, commit_message, False)  # No empty commits for release
        click.echo(f"Committed changes: {commit_hash}")
    except ValueError as e:
        raise click.ClickException(str(e))  # pragma: no cover

    # Create tag
    tag_name = f"v{new_version}"
    tag_message = commit_message
    try:
        create_tag(repo, tag_name, tag_message)
        click.echo(f"Created tag: {tag_name}")
    except ValueError as e:
        raise click.ClickException(str(e))  # pragma: no cover

    # Push commits
    try:
        push_commits(repo, "origin", None)  # Use default remote and current branch
        current_branch = get_current_branch(repo)
        click.echo(f"Pushed branch: {current_branch}")
    except ValueError as e:
        raise click.ClickException(str(e))  # pragma: no cover

    # Push tags
    try:
        push_tags(repo, "origin")  # Use default remote
        click.echo("Pushed tags")
    except ValueError as e:
        raise click.ClickException(str(e))  # pragma: no cover

    click.echo(f"Successfully released version {new_version}")


main.add_command(commit)
main.add_command(tag)
main.add_command(push)
main.add_command(zip_cmd, name="zip")
main.add_command(release)
