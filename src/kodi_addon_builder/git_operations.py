"""Git operations for Kodi Addon Builder."""

import os
import subprocess
from pathlib import Path
from typing import Optional

import click
import git
from git import Repo


def get_repo(root_path: Optional[Path] = None) -> Repo:
    """Get the git repository object."""
    if root_path is None:
        root_path = Path.cwd()
    try:
        return Repo(root_path, search_parent_directories=True)
    except git.InvalidGitRepositoryError as e:
        raise ValueError(f"Not a git repository: {e}")


def run_pre_commit_hooks(repo: Repo) -> None:
    """Run pre-commit hooks if available."""
    # Check if pre-commit is installed
    try:
        subprocess.run(["pre-commit", "--version"], capture_output=True, check=True)
        pre_commit_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pre_commit_available = False

    if pre_commit_available:
        # Check if pre-commit config exists
        config_files = [".pre-commit-config.yaml", ".pre-commit-config.yml"]
        config_exists = any(os.path.exists(os.path.join(repo.working_dir, config)) for config in config_files)

        if config_exists:
            click.echo("Running pre-commit hooks...")
            result = subprocess.run(
                ["pre-commit", "run", "--all-files"], cwd=repo.working_dir, capture_output=True, text=True
            )
            if result.returncode != 0:
                raise ValueError(f"Pre-commit hooks failed:\n{result.stdout}\n{result.stderr}")


def stage_changes(repo: Repo, files: Optional[list[str]] = None) -> None:
    """Stage changes for commit."""
    if files:
        repo.index.add(files)
    else:
        repo.index.add("*")


def commit_changes(repo: Repo, message: str, allow_empty: bool = False) -> str:
    """Commit staged changes."""
    if not allow_empty and not repo.index.diff("HEAD", cached=True):
        raise ValueError("No changes to commit")

    commit = repo.index.commit(message)
    return commit.hexsha


def create_tag(repo: Repo, tag_name: str, message: Optional[str] = None) -> None:
    """Create a git tag."""
    # Check if tag already exists
    if any(tag.name == tag_name for tag in repo.tags):
        raise ValueError(f"Tag '{tag_name}' already exists")

    # Create annotated tag if message provided, lightweight otherwise
    if message:
        repo.create_tag(tag_name, message=message)
    else:
        repo.create_tag(tag_name)


def push_commits(repo: Repo, remote_name: str = "origin", branch: Optional[str] = None) -> None:
    """Push commits to remote."""
    if branch is None:
        branch = repo.active_branch.name

    try:
        origin = repo.remote(remote_name)
        origin.push(branch)
    except ValueError as e:
        raise ValueError(f"Failed to push to remote '{remote_name}': {e}")


def push_tags(repo: Repo, remote_name: str = "origin", tags: Optional[list[str]] = None) -> None:
    """Push tags to remote."""
    try:
        origin = repo.remote(remote_name)
        if tags:
            for tag in tags:
                origin.push(tag)
        else:
            origin.push(tags=True)  # Push all tags
    except ValueError as e:
        raise ValueError(f"Failed to push tags to remote '{remote_name}': {e}")


def get_current_branch(repo: Repo) -> str:
    """Get the current branch name."""
    return repo.active_branch.name


def checkout_branch(repo: Repo, branch_name: str) -> None:
    """Checkout to a branch."""
    if branch_name in [b.name for b in repo.branches]:
        repo.git.checkout(branch_name)
    else:
        # Create and checkout new branch
        repo.git.checkout("-b", branch_name)


def create_zip_archive(
    repo: Repo,
    output_path: Path,
    commit: str = "HEAD",
    paths: Optional[list[str]] = None,
    excludes: Optional[list[str]] = None,
) -> None:
    """Create a zip archive using git archive."""
    cmd = ["git", "archive", "--format=zip", f"--output={output_path}", commit]

    if paths:
        # Add specific paths to archive
        cmd.extend(["--"] + paths)

    # Run the command
    try:
        result = subprocess.run(cmd, cwd=repo.working_dir, capture_output=True, text=True, check=True)
        if result.stderr:
            click.echo(f"Warning: {result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to create zip archive: {e.stderr}")

    # Handle exclusions by extracting and re-archiving (git archive doesn't support --exclude directly)
    if excludes:
        # For exclusions, we need to extract, remove files, and re-zip
        # This is more complex, so for now we'll note it as a limitation
        # In a full implementation, we'd use zip command or similar
        click.echo("Warning: Exclusions not yet implemented in git archive mode")


def get_addon_relative_path(repo: Repo, addon_xml_path: Path) -> str:
    """Get the relative path of the addon directory from repo root."""
    repo_root = Path(repo.working_dir)
    return str(addon_xml_path.parent.relative_to(repo_root))
