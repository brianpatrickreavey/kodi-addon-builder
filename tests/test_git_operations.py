"""Tests for git_operations module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import subprocess
import git

from kodi_addon_builder.git_operations import (
    get_repo,
    run_pre_commit_hooks,
    stage_changes,
    commit_changes,
    create_tag,
    push_commits,
    push_tags,
    get_current_branch,
    checkout_branch,
    create_zip_archive,
    get_addon_relative_path,
)


class TestGetRepo:
    """Test get_repo function."""

    def test_get_repo_success(self, tmp_path):
        """Test getting repo from valid git directory."""
        # Create a mock git repo
        repo_dir = tmp_path / "repo"
        repo_dir.mkdir()

        with patch("kodi_addon_builder.git_operations.Repo") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            result = get_repo(repo_dir)
            assert result == mock_repo
            mock_repo_class.assert_called_once_with(repo_dir, search_parent_directories=True)

    def test_get_repo_invalid(self, tmp_path):
        """Test getting repo from invalid git directory."""
        repo_dir = tmp_path / "not_repo"
        repo_dir.mkdir()

        with patch("git.Repo", side_effect=git.InvalidGitRepositoryError("Not a repo")):
            with pytest.raises(ValueError, match="Not a git repository"):
                get_repo(repo_dir)

    def test_get_repo_default_cwd(self):
        """Test getting repo with default cwd."""
        with (
            patch("pathlib.Path.cwd", return_value=Path("/fake/cwd")),
            patch("kodi_addon_builder.git_operations.Repo") as mock_repo_class,
        ):
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            get_repo()
            mock_repo_class.assert_called_once_with(Path("/fake/cwd"), search_parent_directories=True)


class TestRunPreCommitHooks:
    """Test run_pre_commit_hooks function."""

    def test_pre_commit_not_available(self):
        """Test when pre-commit is not available."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"

        with patch("subprocess.run", side_effect=FileNotFoundError):
            # Should not raise
            run_pre_commit_hooks(mock_repo)

    def test_pre_commit_available_no_config(self):
        """Test when pre-commit is available but no config."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"

        with patch("subprocess.run") as mock_run, patch("pathlib.Path") as mock_path_class:
            mock_run.return_value = MagicMock(returncode=0)  # pre-commit --version succeeds
            mock_path = MagicMock()
            mock_path.exists.return_value = False
            mock_path_class.return_value = mock_path

            run_pre_commit_hooks(mock_repo)
            # Should not run pre-commit
            assert mock_run.call_count == 1  # Only the version check

    @patch("kodi_addon_builder.git_operations.click")
    def test_pre_commit_success(self, mock_click):
        """Test successful pre-commit run."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"

        with patch("subprocess.run") as mock_run, patch("os.path.exists") as mock_exists:
            # Mock pre-commit available
            version_result = MagicMock(returncode=0)
            run_result = MagicMock(returncode=0, stdout="", stderr="")
            mock_run.side_effect = [version_result, run_result]

            # Mock config exists
            mock_exists.side_effect = lambda p: "pre-commit-config" in str(p)

            run_pre_commit_hooks(mock_repo)

            expected_calls = [
                call(["pre-commit", "--version"], capture_output=True, check=True),
                call(
                    ["pre-commit", "run", "--all-files"],
                    cwd="/fake/repo",
                    capture_output=True,
                    text=True,
                ),
            ]
            mock_run.assert_has_calls(expected_calls)
            mock_click.echo.assert_called_once_with("Running pre-commit hooks...")

    @patch("kodi_addon_builder.git_operations.click")
    def test_pre_commit_failure(self, mock_click):
        """Test pre-commit run failure."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"

        with patch("subprocess.run") as mock_run, patch("os.path.exists", return_value=True):
            version_result = MagicMock(returncode=0)
            run_result = MagicMock(returncode=1, stdout="stdout", stderr="stderr")
            mock_run.side_effect = [version_result, run_result]

            with pytest.raises(ValueError, match="Pre-commit hooks failed"):
                run_pre_commit_hooks(mock_repo)


class TestStageChanges:
    """Test stage_changes function."""

    def test_stage_specific_files(self):
        """Test staging specific files."""
        mock_repo = MagicMock()
        files = ["file1.txt", "file2.txt"]

        stage_changes(mock_repo, files)
        mock_repo.index.add.assert_called_once_with(files)

    def test_stage_all_changes(self):
        """Test staging all changes."""
        mock_repo = MagicMock()

        stage_changes(mock_repo)
        mock_repo.index.add.assert_called_once_with("*")


class TestCommitChanges:
    """Test commit_changes function."""

    def test_commit_success(self):
        """Test successful commit."""
        mock_repo = MagicMock()
        mock_diff = MagicMock()
        mock_diff.__bool__ = lambda self: True  # Non-empty diff
        mock_repo.index.diff.return_value = [mock_diff]

        mock_commit = MagicMock()
        mock_commit.hexsha = "abc123"
        mock_repo.index.commit.return_value = mock_commit

        result = commit_changes(mock_repo, "Test commit")
        assert result == "abc123"
        mock_repo.index.commit.assert_called_once_with("Test commit")

    def test_commit_no_changes(self):
        """Test commit with no changes."""
        mock_repo = MagicMock()
        mock_repo.index.diff.return_value = []  # Empty diff

        with pytest.raises(ValueError, match="No changes to commit"):
            commit_changes(mock_repo, "Test commit")

    def test_commit_allow_empty(self):
        """Test commit allowing empty commits."""
        mock_repo = MagicMock()
        mock_repo.index.diff.return_value = []  # Empty diff

        mock_commit = MagicMock()
        mock_commit.hexsha = "abc123"
        mock_repo.index.commit.return_value = mock_commit

        result = commit_changes(mock_repo, "Test commit", allow_empty=True)
        assert result == "abc123"


class TestCreateTag:
    """Test create_tag function."""

    def test_create_lightweight_tag(self):
        """Test creating a lightweight tag."""
        mock_repo = MagicMock()
        mock_repo.tags = []  # No existing tags

        create_tag(mock_repo, "v1.0.0")
        mock_repo.create_tag.assert_called_once_with("v1.0.0")

    def test_create_annotated_tag(self):
        """Test creating an annotated tag."""
        mock_repo = MagicMock()
        mock_repo.tags = []

        create_tag(mock_repo, "v1.0.0", "Release v1.0.0")
        mock_repo.create_tag.assert_called_once_with("v1.0.0", message="Release v1.0.0")

    def test_tag_already_exists(self):
        """Test creating a tag that already exists."""
        mock_repo = MagicMock()
        mock_tag = MagicMock()
        mock_tag.name = "v1.0.0"
        mock_repo.tags = [mock_tag]

        with pytest.raises(ValueError, match="Tag 'v1.0.0' already exists"):
            create_tag(mock_repo, "v1.0.0")


class TestPushCommits:
    """Test push_commits function."""

    def test_push_current_branch(self):
        """Test pushing current branch."""
        mock_repo = MagicMock()
        mock_repo.active_branch.name = "main"
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote

        push_commits(mock_repo)
        mock_repo.remote.assert_called_once_with("origin")
        mock_remote.push.assert_called_once_with("main")

    def test_push_specific_branch(self):
        """Test pushing specific branch."""
        mock_repo = MagicMock()
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote

        push_commits(mock_repo, branch="feature-branch")
        mock_remote.push.assert_called_once_with("feature-branch")

    def test_push_remote_error(self):
        """Test push with remote error."""
        mock_repo = MagicMock()
        mock_repo.active_branch.name = "main"
        mock_repo.remote.side_effect = ValueError("Remote not found")

        with pytest.raises(ValueError, match="Failed to push to remote 'origin'"):
            push_commits(mock_repo)


class TestPushTags:
    """Test push_tags function."""

    def test_push_all_tags(self):
        """Test pushing all tags."""
        mock_repo = MagicMock()
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote

        push_tags(mock_repo)
        mock_remote.push.assert_called_once_with(tags=True)

    def test_push_specific_tags(self):
        """Test pushing specific tags."""
        mock_repo = MagicMock()
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote

        push_tags(mock_repo, tags=["v1.0.0", "v1.1.0"])
        expected_calls = [call("v1.0.0"), call("v1.1.0")]
        mock_remote.push.assert_has_calls(expected_calls)

    def test_push_tags_remote_error(self):
        """Test push tags with remote error."""
        mock_repo = MagicMock()
        mock_repo.remote.side_effect = ValueError("Remote not found")

        with pytest.raises(ValueError, match="Failed to push tags to remote 'origin'"):
            push_tags(mock_repo)


class TestGetCurrentBranch:
    """Test get_current_branch function."""

    def test_get_current_branch(self):
        """Test getting current branch name."""
        mock_repo = MagicMock()
        mock_repo.active_branch.name = "develop"

        result = get_current_branch(mock_repo)
        assert result == "develop"


class TestCheckoutBranch:
    """Test checkout_branch function."""

    def test_checkout_existing_branch(self):
        """Test checking out existing branch."""
        mock_repo = MagicMock()
        mock_branch = MagicMock()
        mock_branch.name = "feature-branch"
        mock_repo.branches = [mock_branch]

        checkout_branch(mock_repo, "feature-branch")
        mock_repo.git.checkout.assert_called_once_with("feature-branch")

    def test_checkout_new_branch(self):
        """Test creating and checking out new branch."""
        mock_repo = MagicMock()
        mock_repo.branches = []  # No existing branches

        checkout_branch(mock_repo, "new-branch")
        mock_repo.git.checkout.assert_called_once_with("-b", "new-branch")


class TestCreateZipArchive:
    """Test create_zip_archive function."""

    @patch("kodi_addon_builder.git_operations.subprocess.run")
    @patch("kodi_addon_builder.git_operations.click")
    def test_create_zip_full_repo(self, mock_click, mock_run):
        """Test creating zip archive of full repo."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        output_path = Path("/output/test.zip")

        mock_run.return_value = MagicMock(returncode=0, stderr="")

        create_zip_archive(mock_repo, output_path)

        expected_cmd = [
            "git",
            "archive",
            "--format=zip",
            "--output=/output/test.zip",
            "HEAD",
        ]
        mock_run.assert_called_once_with(expected_cmd, cwd="/fake/repo", capture_output=True, text=True, check=True)

    @patch("kodi_addon_builder.git_operations.subprocess.run")
    @patch("kodi_addon_builder.git_operations.click")
    def test_create_zip_with_paths(self, mock_click, mock_run):
        """Test creating zip archive with specific paths."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        output_path = Path("/output/test.zip")
        paths = ["addon/", "README.md"]

        mock_run.return_value = MagicMock(returncode=0, stderr="")

        create_zip_archive(mock_repo, output_path, paths=paths)

        expected_cmd = [
            "git",
            "archive",
            "--format=zip",
            "--output=/output/test.zip",
            "HEAD",
            "--",
            "addon/",
            "README.md",
        ]
        mock_run.assert_called_once_with(expected_cmd, cwd="/fake/repo", capture_output=True, text=True, check=True)

    @patch("kodi_addon_builder.git_operations.subprocess.run")
    @patch("kodi_addon_builder.git_operations.click")
    def test_create_zip_custom_commit(self, mock_click, mock_run):
        """Test creating zip archive with custom commit."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        output_path = Path("/output/test.zip")

        mock_run.return_value = MagicMock(returncode=0, stderr="")

        create_zip_archive(mock_repo, output_path, commit="v1.0.0")

        expected_cmd = [
            "git",
            "archive",
            "--format=zip",
            "--output=/output/test.zip",
            "v1.0.0",
        ]
        mock_run.assert_called_once_with(expected_cmd, cwd="/fake/repo", capture_output=True, text=True, check=True)

    @patch("kodi_addon_builder.git_operations.subprocess.run")
    @patch("kodi_addon_builder.git_operations.click")
    def test_create_zip_with_stderr(self, mock_click, mock_run):
        """Test creating zip archive with stderr output."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        output_path = Path("/output/test.zip")

        mock_run.return_value = MagicMock(returncode=0, stderr="warning message")

        create_zip_archive(mock_repo, output_path)

        mock_click.echo.assert_called_once_with("Warning: warning message")

    @patch("kodi_addon_builder.git_operations.subprocess.run")
    @patch("kodi_addon_builder.git_operations.click")
    def test_create_zip_failure(self, mock_click, mock_run):
        """Test zip archive creation failure."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        output_path = Path("/output/test.zip")

        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr="error message")

        with pytest.raises(ValueError, match="Failed to create zip archive: error message"):
            create_zip_archive(mock_repo, output_path)

    @patch("kodi_addon_builder.git_operations.click")
    def test_create_zip_with_excludes(self, mock_click):
        """Test creating zip archive with exclusions (not yet implemented)."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        output_path = Path("/output/test.zip")
        excludes = ["*.tmp", "build/"]

        with patch("kodi_addon_builder.git_operations.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            create_zip_archive(mock_repo, output_path, excludes=excludes)

            # Should still run git archive (exclusions not implemented)
            mock_run.assert_called_once()
            mock_click.echo.assert_called_once_with("Warning: Exclusions not yet implemented in git archive mode")


class TestGetAddonRelativePath:
    """Test get_addon_relative_path function."""

    def test_get_addon_relative_path(self):
        """Test getting relative path of addon directory."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/repo"

        addon_xml_path = Path("/repo/plugin.video.test/addon.xml")

        result = get_addon_relative_path(mock_repo, addon_xml_path)
        assert result == "plugin.video.test"
