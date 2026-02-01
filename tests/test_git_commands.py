"""Tests for git CLI commands."""

import pytest  # noqa: F401
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock
import git
import zipfile
import xml.etree.ElementTree as ET

from kodi_addon_builder.cli import commit, tag, push, zip_cmd, release


class TestCommitCommand:
    """Test the commit CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    @patch("kodi_addon_builder.cli.stage_changes")
    @patch("kodi_addon_builder.cli.commit_changes")
    def test_commit_success(
        self,
        mock_commit_changes,
        mock_stage_changes,
        mock_run_pre_commit,
        mock_get_repo,
    ):
        """Test successful commit."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo
        mock_commit_changes.return_value = "abc123"

        result = self.runner.invoke(commit, ["--message", "Test commit"])
        assert result.exit_code == 0
        assert "Repository: /fake/repo" in result.output
        assert "Committed changes: abc123" in result.output

        mock_get_repo.assert_called_once()
        mock_run_pre_commit.assert_called_once_with(mock_repo)
        mock_stage_changes.assert_called_once_with(mock_repo, None)
        mock_commit_changes.assert_called_once_with(mock_repo, "Test commit", False)

    @patch("kodi_addon_builder.cli.get_repo")
    def test_commit_no_repo(self, mock_get_repo):
        """Test commit with no git repository."""
        mock_get_repo.side_effect = ValueError("Not a git repository")

        result = self.runner.invoke(commit, ["--message", "Test commit"])
        assert result.exit_code == 1
        assert "Not a git repository" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    @patch("kodi_addon_builder.cli.stage_changes")
    @patch("kodi_addon_builder.cli.commit_changes")
    def test_commit_with_files(
        self,
        mock_commit_changes,
        mock_stage_changes,
        mock_run_pre_commit,
        mock_get_repo,
    ):
        """Test commit with specific files."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_commit_changes.return_value = "abc123"

        result = self.runner.invoke(
            commit,
            [
                "--message",
                "Test commit",
                "--files",
                "file1.txt",
                "--files",
                "file2.txt",
            ],
        )
        assert result.exit_code == 0
        mock_stage_changes.assert_called_once_with(mock_repo, ["file1.txt", "file2.txt"])

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    @patch("kodi_addon_builder.cli.stage_changes")
    @patch("kodi_addon_builder.cli.commit_changes")
    def test_commit_allow_empty(
        self,
        mock_commit_changes,
        mock_stage_changes,
        mock_run_pre_commit,
        mock_get_repo,
    ):
        """Test commit allowing empty commits."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_commit_changes.return_value = "abc123"

        result = self.runner.invoke(commit, ["--message", "Test commit", "--allow-empty"])
        assert result.exit_code == 0
        mock_commit_changes.assert_called_once_with(mock_repo, "Test commit", True)

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    @patch("kodi_addon_builder.cli.stage_changes")
    def test_commit_no_pre_commit(self, mock_stage_changes, mock_run_pre_commit, mock_get_repo):
        """Test commit skipping pre-commit hooks."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        result = self.runner.invoke(commit, ["--message", "Test commit", "--no-pre-commit"])
        assert result.exit_code == 0
        mock_run_pre_commit.assert_not_called()

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    @patch("kodi_addon_builder.cli.stage_changes")
    def test_commit_pre_commit_failure(self, mock_stage_changes, mock_run_pre_commit, mock_get_repo):
        """Test commit with pre-commit failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_run_pre_commit.side_effect = ValueError("Pre-commit failed")

        result = self.runner.invoke(commit, ["--message", "Test commit"])
        assert result.exit_code == 1
        assert "Pre-commit failed" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    def test_commit_stage_failure(self, mock_run_pre_commit, mock_get_repo):
        """Test commit with staging failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_repo.index.add.side_effect = Exception("Staging failed")

        result = self.runner.invoke(commit, ["--message", "Test commit"])
        assert result.exit_code == 1
        assert "Failed to stage changes: Staging failed" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    @patch("kodi_addon_builder.cli.stage_changes")
    @patch("kodi_addon_builder.cli.commit_changes")
    def test_commit_commit_failure(
        self,
        mock_commit_changes,
        mock_stage_changes,
        mock_run_pre_commit,
        mock_get_repo,
    ):
        """Test commit with commit failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_commit_changes.side_effect = ValueError("No changes to commit")

        result = self.runner.invoke(commit, ["--message", "Test commit"])
        assert result.exit_code == 1
        assert "No changes to commit" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    def test_commit_with_repo_path(self, mock_get_repo):
        """Test commit with custom repo path."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/custom/repo"
        mock_get_repo.return_value = mock_repo

        with patch("kodi_addon_builder.cli.run_pre_commit_hooks"), patch("kodi_addon_builder.cli.stage_changes"), patch(
            "kodi_addon_builder.cli.commit_changes", return_value="abc123"
        ):
            # Create the directory so Click validation passes
            import tempfile

            with tempfile.TemporaryDirectory() as tmpdir:
                result = self.runner.invoke(commit, ["--message", "Test commit", "--repo-path", tmpdir])
                assert result.exit_code == 0
                mock_get_repo.assert_called_once_with(Path(tmpdir))


class TestTagCommand:
    """Test the tag CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.create_tag")
    def test_tag_success_lightweight(self, mock_create_tag, mock_get_repo):
        """Test successful lightweight tag creation."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo

        result = self.runner.invoke(tag, ["v1.0.0"])
        assert result.exit_code == 0
        assert "Repository: /fake/repo" in result.output
        assert "Created tag: v1.0.0" in result.output

        mock_create_tag.assert_called_once_with(mock_repo, "v1.0.0", None)

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.create_tag")
    def test_tag_success_annotated(self, mock_create_tag, mock_get_repo):
        """Test successful annotated tag creation."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo

        result = self.runner.invoke(tag, ["v1.0.0", "--message", "Release v1.0.0"])
        assert result.exit_code == 0
        mock_create_tag.assert_called_once_with(mock_repo, "v1.0.0", "Release v1.0.0")

    @patch("kodi_addon_builder.cli.get_repo")
    def test_tag_no_repo(self, mock_get_repo):
        """Test tag with no git repository."""
        mock_get_repo.side_effect = ValueError("Not a git repository")

        result = self.runner.invoke(tag, ["v1.0.0"])
        assert result.exit_code == 1
        assert "Not a git repository" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.create_tag")
    def test_tag_already_exists(self, mock_create_tag, mock_get_repo):
        """Test tag creation when tag already exists."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_create_tag.side_effect = ValueError("Tag 'v1.0.0' already exists")

        result = self.runner.invoke(tag, ["v1.0.0"])
        assert result.exit_code == 1
        assert "Tag 'v1.0.0' already exists" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.create_tag")
    def test_tag_with_repo_path(self, mock_create_tag, mock_get_repo):
        """Test tag with custom repo path."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/custom/repo"
        mock_get_repo.return_value = mock_repo

        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.runner.invoke(tag, ["v1.0.0", "--repo-path", tmpdir])
            assert result.exit_code == 0
            mock_get_repo.assert_called_once_with(Path(tmpdir))


class TestPushCommand:
    """Test the push CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.push_commits")
    @patch("kodi_addon_builder.cli.get_current_branch")
    def test_push_commits_only(self, mock_get_branch, mock_push_commits, mock_get_repo):
        """Test pushing commits only."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo
        mock_get_branch.return_value = "main"

        result = self.runner.invoke(push, [])
        assert result.exit_code == 0
        assert "Repository: /fake/repo" in result.output
        assert "Pushed branch: main" in result.output

        mock_push_commits.assert_called_once_with(mock_repo, "origin", None)

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.push_commits")
    @patch("kodi_addon_builder.cli.push_tags")
    @patch("kodi_addon_builder.cli.get_current_branch")
    def test_push_commits_and_tags(self, mock_get_branch, mock_push_tags, mock_push_commits, mock_get_repo):
        """Test pushing commits and tags."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo
        mock_get_branch.return_value = "main"

        result = self.runner.invoke(push, ["--tags"])
        assert result.exit_code == 0
        assert "Pushed branch: main" in result.output
        assert "Pushed tags" in result.output

        mock_push_commits.assert_called_once_with(mock_repo, "origin", None)
        mock_push_tags.assert_called_once_with(mock_repo, "origin")

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.push_commits")
    def test_push_specific_branch(self, mock_push_commits, mock_get_repo):
        """Test pushing specific branch."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        result = self.runner.invoke(push, ["--branch", "feature-branch"])
        assert result.exit_code == 0
        assert "Pushed branch: feature-branch" in result.output

        mock_push_commits.assert_called_once_with(mock_repo, "origin", "feature-branch")

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.push_commits")
    def test_push_custom_remote(self, mock_push_commits, mock_get_repo):
        """Test pushing to custom remote."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        result = self.runner.invoke(push, ["--remote", "upstream"])
        assert result.exit_code == 0
        mock_push_commits.assert_called_once_with(mock_repo, "upstream", None)

    @patch("kodi_addon_builder.cli.get_repo")
    def test_push_no_repo(self, mock_get_repo):
        """Test push with no git repository."""
        mock_get_repo.side_effect = ValueError("Not a git repository")

        result = self.runner.invoke(push, [])
        assert result.exit_code == 1
        assert "Not a git repository" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.push_commits")
    @patch("kodi_addon_builder.cli.get_current_branch")
    def test_push_commits_failure(self, mock_get_branch, mock_push_commits, mock_get_repo):
        """Test push with commits failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_push_commits.side_effect = ValueError("Push failed")

        result = self.runner.invoke(push, [])
        assert result.exit_code == 1
        assert "Push failed" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.push_commits")
    @patch("kodi_addon_builder.cli.push_tags")
    @patch("kodi_addon_builder.cli.get_current_branch")
    def test_push_tags_failure(self, mock_get_branch, mock_push_tags, mock_push_commits, mock_get_repo):
        """Test push with tags failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_push_tags.side_effect = ValueError("Tags push failed")

        result = self.runner.invoke(push, ["--tags"])
        assert result.exit_code == 1
        assert "Tags push failed" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.push_commits")
    @patch("kodi_addon_builder.cli.get_current_branch")
    def test_push_with_repo_path(self, mock_get_branch, mock_push_commits, mock_get_repo):
        """Test push with custom repo path."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/custom/repo"
        mock_get_repo.return_value = mock_repo

        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.runner.invoke(push, ["--repo-path", tmpdir])
            assert result.exit_code == 0
            mock_get_repo.assert_called_once_with(Path(tmpdir))


class TestZipCommand:
    """Test the zip CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.create_zip_archive")
    @patch("kodi_addon_builder.cli.get_addon_relative_path")
    def test_zip_addon_only_success(
        self,
        mock_get_rel_path,
        mock_create_zip,
        mock_validate_xml,
        mock_find_xml,
        mock_get_repo,
    ):
        """Test successful zip creation for addon-only."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        # Mock XML validation
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.side_effect = lambda key: {
            "id": "plugin.video.test",
            "version": "1.0.0",
        }.get(key)
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        mock_get_rel_path.return_value = "plugin.video.test"

        result = self.runner.invoke(zip_cmd, [])
        assert result.exit_code == 0
        assert "Repository: /fake/repo" in result.output
        assert "Found addon.xml at: /fake/repo/plugin.video.test/addon.xml" in result.output
        assert "Addon ID: plugin.video.test, Version: 1.0.0" in result.output
        assert "Archiving addon directory: plugin.video.test" in result.output
        assert "Created zip archive: plugin.video.test-1.0.0.zip" in result.output

        mock_create_zip.assert_called_once_with(
            mock_repo,
            Path("plugin.video.test-1.0.0.zip"),
            "HEAD",
            ["plugin.video.test"],
            None,
        )

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.create_zip_archive")
    def test_zip_full_repo_success(self, mock_create_zip, mock_validate_xml, mock_find_xml, mock_get_repo):
        """Test successful zip creation for full repo."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.side_effect = lambda key: {
            "id": "plugin.video.test",
            "version": "1.0.0",
        }.get(key)
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        result = self.runner.invoke(zip_cmd, ["--full-repo"])
        assert result.exit_code == 0
        assert "Archiving full repository" in result.output

        mock_create_zip.assert_called_once_with(mock_repo, Path("plugin.video.test-1.0.0.zip"), "HEAD", None, None)

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.create_zip_archive")
    def test_zip_custom_output(self, mock_create_zip, mock_validate_xml, mock_find_xml, mock_get_repo):
        """Test zip with custom output path."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.side_effect = lambda key: {
            "id": "plugin.video.test",
            "version": "1.0.0",
        }.get(key)
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        with patch(
            "kodi_addon_builder.cli.get_addon_relative_path",
            return_value="plugin.video.test",
        ):
            result = self.runner.invoke(zip_cmd, ["--output", "/custom/output.zip"])
            assert result.exit_code == 0

        mock_create_zip.assert_called_once_with(
            mock_repo, Path("/custom/output.zip"), "HEAD", ["plugin.video.test"], None
        )

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.create_zip_archive")
    def test_zip_custom_commit(self, mock_create_zip, mock_validate_xml, mock_find_xml, mock_get_repo):
        """Test zip with custom commit."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.side_effect = lambda key: {
            "id": "plugin.video.test",
            "version": "1.0.0",
        }.get(key)
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        with patch(
            "kodi_addon_builder.cli.get_addon_relative_path",
            return_value="plugin.video.test",
        ):
            result = self.runner.invoke(zip_cmd, ["--commit", "v1.0.0"])
            assert result.exit_code == 0

        mock_create_zip.assert_called_once_with(
            mock_repo,
            Path("plugin.video.test-1.0.0.zip"),
            "v1.0.0",
            ["plugin.video.test"],
            None,
        )

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.create_zip_archive")
    def test_zip_with_excludes(self, mock_create_zip, mock_validate_xml, mock_find_xml, mock_get_repo):
        """Test zip with exclusions."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.side_effect = lambda key: {
            "id": "plugin.video.test",
            "version": "1.0.0",
        }.get(key)
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        with patch(
            "kodi_addon_builder.cli.get_addon_relative_path",
            return_value="plugin.video.test",
        ):
            result = self.runner.invoke(zip_cmd, ["--exclude", "*.tmp", "--exclude", "build/"])
            assert result.exit_code == 0

        mock_create_zip.assert_called_once_with(
            mock_repo,
            Path("plugin.video.test-1.0.0.zip"),
            "HEAD",
            ["plugin.video.test"],
            ["*.tmp", "build/"],
        )

    @patch("kodi_addon_builder.cli.get_repo")
    def test_zip_no_repo(self, mock_get_repo):
        """Test zip with no git repository."""
        mock_get_repo.side_effect = ValueError("Not a git repository")

        result = self.runner.invoke(zip_cmd, [])
        assert result.exit_code == 1
        assert "Not a git repository" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    def test_zip_no_addon_xml(self, mock_find_xml, mock_get_repo):
        """Test zip with no addon.xml found."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_find_xml.return_value = None

        result = self.runner.invoke(zip_cmd, [])
        assert result.exit_code == 1
        assert "Could not find addon.xml" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    def test_zip_invalid_addon_xml(self, mock_validate_xml, mock_find_xml, mock_get_repo):
        """Test zip with invalid addon.xml."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path
        mock_validate_xml.side_effect = ValueError("Invalid XML")

        result = self.runner.invoke(zip_cmd, [])
        assert result.exit_code == 1
        assert "Invalid addon.xml: Invalid XML" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.create_zip_archive")
    def test_zip_missing_addon_id(self, mock_create_zip, mock_validate_xml, mock_find_xml, mock_get_repo):
        """Test zip with addon.xml missing id."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.return_value = None  # No id
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        result = self.runner.invoke(zip_cmd, [])
        assert result.exit_code == 1
        assert "addon.xml missing 'id' attribute" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.create_zip_archive")
    def test_zip_archive_failure(self, mock_create_zip, mock_validate_xml, mock_find_xml, mock_get_repo):
        """Test zip with archive creation failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.side_effect = lambda key: {
            "id": "plugin.video.test",
            "version": "1.0.0",
        }.get(key)
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        mock_create_zip.side_effect = ValueError("Archive creation failed")

        with patch(
            "kodi_addon_builder.cli.get_addon_relative_path",
            return_value="plugin.video.test",
        ):
            result = self.runner.invoke(zip_cmd, [])
            assert result.exit_code == 1
            assert "Archive creation failed" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.create_zip_archive")
    @patch("kodi_addon_builder.cli.get_addon_relative_path")
    def test_zip_with_addon_path(
        self,
        mock_get_rel_path,
        mock_create_zip,
        mock_validate_xml,
        mock_find_xml,
        mock_get_repo,
    ):
        """Test zip with custom addon path."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        # Custom addon path
        mock_validate_xml.return_value = (MagicMock(), MagicMock(), "1.0.0")
        mock_get_rel_path.return_value = "addon"

        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake addon.xml in the temp dir
            addon_xml = Path(tmpdir) / "addon.xml"
            addon_xml.write_text('<addon id="test" version="1.0.0"/>')

            result = self.runner.invoke(zip_cmd, ["--addon-path", tmpdir])
            assert result.exit_code == 0
            # Should not call find_addon_xml when addon_path is provided
            mock_find_xml.assert_not_called()

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.create_zip_archive")
    @patch("kodi_addon_builder.cli.get_addon_relative_path")
    def test_zip_with_repo_path(
        self,
        mock_get_rel_path,
        mock_create_zip,
        mock_validate_xml,
        mock_find_xml,
        mock_get_repo,
    ):
        """Test zip with custom repo path."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/custom/repo"
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/custom/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.side_effect = lambda key: {
            "id": "plugin.video.test",
            "version": "1.0.0",
        }.get(key)
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.runner.invoke(zip_cmd, ["--repo-path", tmpdir])
            assert result.exit_code == 0
            mock_get_repo.assert_called_once_with(Path(tmpdir))


class TestZipCommandIntegration:
    """Integration tests for the zip CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_zip_addon_integration(self, tmp_path, sample_addon_xml_content):
        """Integration test: create git repo with addon, zip it."""
        # Create a temporary git repository
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()

        # Initialize git repo
        repo = git.Repo.init(repo_dir)

        # Create addon structure
        addon_dir = repo_dir / "plugin.video.test"
        addon_dir.mkdir()
        lib_dir = addon_dir / "lib"
        lib_dir.mkdir()

        # Create addon.xml
        addon_xml = addon_dir / "addon.xml"
        addon_xml.write_text(sample_addon_xml_content)

        # Create some addon files
        main_py = lib_dir / "main.py"
        main_py.write_text("# Main addon file")

        resources_dir = addon_dir / "resources"
        resources_dir.mkdir()
        settings_xml = resources_dir / "settings.xml"
        settings_xml.write_text("<settings></settings>")

        # Add and commit files
        repo.index.add("*")
        repo.index.commit("Initial commit")

        # Test zip command
        with self.runner.isolated_filesystem():
            # Change to repo directory
            import os

            old_cwd = os.getcwd()
            os.chdir(str(repo_dir))

            try:
                result = self.runner.invoke(zip_cmd, [])
                assert result.exit_code == 0
                assert "Repository:" in result.output
                assert "Found addon.xml at:" in result.output
                assert "Addon ID: plugin.video.test, Version: 1.0.0" in result.output
                assert "Archiving addon directory: plugin.video.test" in result.output
                assert "Created zip archive: plugin.video.test-1.0.0.zip" in result.output

                # Check that zip file was created
                zip_path = repo_dir / "plugin.video.test-1.0.0.zip"
                assert zip_path.exists()

                # Verify zip contents
                with zipfile.ZipFile(zip_path, "r") as zf:
                    # Should contain addon files but not repo files like .git
                    files = zf.namelist()
                    assert "plugin.video.test/addon.xml" in files
                    assert "plugin.video.test/lib/main.py" in files
                    assert "plugin.video.test/resources/settings.xml" in files
                    # Should not contain .git directory
                    assert not any(f.startswith(".git") for f in files)

            finally:
                os.chdir(old_cwd)

    def test_zip_full_repo_integration(self, tmp_path, sample_addon_xml_content):
        """Integration test: zip full repository."""
        # Create a temporary git repository
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()

        # Initialize git repo
        repo = git.Repo.init(repo_dir)

        # Create addon structure
        addon_dir = repo_dir / "plugin.video.test"
        addon_dir.mkdir()

        # Create addon.xml
        addon_xml = addon_dir / "addon.xml"
        addon_xml.write_text(sample_addon_xml_content)

        # Create some repo-level files
        readme = repo_dir / "README.md"
        readme.write_text("# Test Addon")

        makefile = repo_dir / "Makefile"
        makefile.write_text("test:\n\techo 'test'")

        # Add and commit files
        repo.index.add("*")
        repo.index.commit("Initial commit")

        # Test zip command with --full-repo
        with self.runner.isolated_filesystem():
            import os

            old_cwd = os.getcwd()
            os.chdir(str(repo_dir))

            try:
                result = self.runner.invoke(zip_cmd, ["--full-repo"])
                assert result.exit_code == 0
                assert "Archiving full repository" in result.output
                assert "Created zip archive: plugin.video.test-1.0.0.zip" in result.output

                # Check that zip file was created
                zip_path = repo_dir / "plugin.video.test-1.0.0.zip"
                assert zip_path.exists()

                # Verify zip contents
                with zipfile.ZipFile(zip_path, "r") as zf:
                    files = zf.namelist()
                    assert "plugin.video.test/addon.xml" in files
                    assert "README.md" in files
                    assert "Makefile" in files
                    # Should not contain .git directory
                    assert not any(f.startswith(".git") for f in files)

            finally:
                os.chdir(old_cwd)


class TestReleaseCommand:
    """Test the release CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.bump_version")
    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    @patch("kodi_addon_builder.cli.stage_changes")
    @patch("kodi_addon_builder.cli.commit_changes")
    @patch("kodi_addon_builder.cli.create_tag")
    @patch("kodi_addon_builder.cli.push_commits")
    @patch("kodi_addon_builder.cli.push_tags")
    @patch("kodi_addon_builder.cli.get_current_branch")
    @patch("kodi_addon_builder.cli.update_changelog")
    def test_release_success(
        self,
        mock_update_changelog,
        mock_get_branch,
        mock_push_tags,
        mock_push_commits,
        mock_create_tag,
        mock_commit_changes,
        mock_stage_changes,
        mock_run_pre_commit,
        mock_bump_version,
        mock_validate_xml,
        mock_find_xml,
        mock_get_repo,
    ):
        """Test successful release."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_repo.is_dirty.return_value = False
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        # Mock XML validation and parsing
        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.side_effect = lambda key: {"version": "1.0.0"}.get(key)
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        mock_bump_version.return_value = "1.1.0"
        mock_commit_changes.return_value = "abc123"
        mock_get_branch.return_value = "main"

        result = self.runner.invoke(release, ["patch", "--non-interactive"])
        assert result.exit_code == 0
        assert "Found addon.xml at: /fake/repo/plugin.video.test/addon.xml" in result.output
        assert "Current version: 1.0.0" in result.output
        assert "New version: 1.1.0" in result.output
        assert "Updated addon.xml and CHANGELOG.md with version 1.1.0" in result.output
        assert "Committed changes: abc123" in result.output
        assert "Created tag: v1.1.0" in result.output
        assert "Pushed branch: main" in result.output
        assert "Pushed tags" in result.output
        assert "Successfully released version 1.1.0" in result.output

        # Verify calls
        mock_get_repo.assert_called_once()
        mock_find_xml.assert_called_once()
        mock_validate_xml.assert_called_once_with(addon_xml_path)
        mock_bump_version.assert_called_once_with("1.0.0", "patch")
        mock_tree.write.assert_called_once()
        mock_run_pre_commit.assert_called_once_with(mock_repo)
        mock_stage_changes.assert_called_once_with(
            mock_repo, ["plugin.video.test/addon.xml", "plugin.video.test/CHANGELOG.md"]
        )
        mock_commit_changes.assert_called_once_with(mock_repo, "Bump version to 1.1.0", False)
        mock_create_tag.assert_called_once_with(mock_repo, "v1.1.0", "Release version 1.1.0")
        mock_push_commits.assert_called_once_with(mock_repo, "origin", None)
        mock_push_tags.assert_called_once_with(mock_repo, "origin")

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.bump_version")
    def test_release_dry_run(self, mock_bump_version, mock_validate_xml, mock_find_xml, mock_get_repo):
        """Test release with dry run."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.return_value = "1.0.0"
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        mock_bump_version.return_value = "1.1.0"

        result = self.runner.invoke(release, ["patch", "--dry-run", "--non-interactive"])
        assert result.exit_code == 0
        assert "Dry run: No changes made" in result.output
        assert "Would bump version to 1.1.0" in result.output
        assert "Would commit with message: 'Bump version to 1.1.0'" in result.output
        assert "Would create tag: v1.1.0" in result.output
        assert "Would push branch and tags to origin" in result.output

        # Verify no actual changes
        mock_tree.write.assert_not_called()

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.bump_version")
    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    @patch("kodi_addon_builder.cli.stage_changes")
    @patch("kodi_addon_builder.cli.commit_changes")
    @patch("kodi_addon_builder.cli.create_tag")
    @patch("kodi_addon_builder.cli.push_commits")
    @patch("kodi_addon_builder.cli.push_tags")
    @patch("kodi_addon_builder.cli.get_current_branch")
    @patch("kodi_addon_builder.cli.update_changelog")
    def test_release_with_news(
        self,
        mock_update_changelog,
        mock_get_branch,
        mock_push_tags,
        mock_push_commits,
        mock_create_tag,
        mock_commit_changes,
        mock_stage_changes,
        mock_run_pre_commit,
        mock_bump_version,
        mock_validate_xml,
        mock_find_xml,
        mock_get_repo,
    ):
        """Test release with news/changelog."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_repo.is_dirty.return_value = False
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.return_value = "1.0.0"
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        mock_bump_version.return_value = "1.1.0"
        mock_commit_changes.return_value = "abc123"
        mock_get_branch.return_value = "main"

        result = self.runner.invoke(release, ["patch", "--news", "Fixed a bug", "--non-interactive"])
        assert result.exit_code == 0
        assert "News: Fixed a bug" in result.output

        # Verify commit message includes news
        expected_commit_msg = "Bump version to 1.1.0\n\nFixed a bug"
        mock_commit_changes.assert_called_once_with(mock_repo, expected_commit_msg, False)

        # Verify tag message includes news
        expected_tag_msg = "Release version 1.1.0\n\nFixed a bug"
        mock_create_tag.assert_called_once_with(mock_repo, "v1.1.0", expected_tag_msg)

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.bump_version")
    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    @patch("kodi_addon_builder.cli.stage_changes")
    @patch("kodi_addon_builder.cli.commit_changes")
    @patch("kodi_addon_builder.cli.create_tag")
    @patch("kodi_addon_builder.cli.push_commits")
    @patch("kodi_addon_builder.cli.push_tags")
    @patch("kodi_addon_builder.cli.get_current_branch")
    @patch("kodi_addon_builder.cli.update_changelog")
    def test_release_custom_options(
        self,
        mock_update_changelog,
        mock_get_branch,
        mock_push_tags,
        mock_push_commits,
        mock_create_tag,
        mock_commit_changes,
        mock_stage_changes,
        mock_run_pre_commit,
        mock_bump_version,
        mock_validate_xml,
        mock_find_xml,
        mock_get_repo,
    ):
        """Test release with custom remote, branch, and options."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_repo.is_dirty.return_value = False
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.return_value = "1.0.0"
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        mock_bump_version.return_value = "1.1.0"
        mock_commit_changes.return_value = "abc123"
        mock_get_branch.return_value = "develop"

        result = self.runner.invoke(
            release,
            [
                "patch",
                "--remote",
                "upstream",
                "--branch",
                "develop",
                "--no-pre-commit",
                "--allow-empty-commit",
                "--non-interactive",
            ],
        )
        assert result.exit_code == 0

        # Verify custom options
        mock_run_pre_commit.assert_not_called()
        mock_commit_changes.assert_called_once_with(mock_repo, "Bump version to 1.1.0", True)
        mock_push_commits.assert_called_once_with(mock_repo, "upstream", "develop")
        mock_push_tags.assert_called_once_with(mock_repo, "upstream")

    @patch("kodi_addon_builder.cli.find_addon_xml")
    def test_release_no_addon_xml(self, mock_find_xml):
        """Test release with no addon.xml found."""
        mock_find_xml.return_value = None

        result = self.runner.invoke(release, ["patch"])
        assert result.exit_code == 1
        assert "Could not find addon.xml" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    def test_release_invalid_addon_xml(self, mock_validate_xml, mock_find_xml, mock_get_repo):
        """Test release with invalid addon.xml."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_validate_xml.side_effect = ValueError("Invalid XML")

        result = self.runner.invoke(release, ["patch"])
        assert result.exit_code == 1
        assert "Invalid addon.xml: Invalid XML" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.bump_version")
    def test_release_invalid_bump_type(self, mock_bump_version, mock_validate_xml, mock_find_xml, mock_get_repo):
        """Test release with invalid bump type."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        addon_xml_path = Path("/fake/repo/plugin.video.test/addon.xml")
        mock_find_xml.return_value = addon_xml_path

        mock_tree = MagicMock()
        mock_root = MagicMock()
        mock_root.get.return_value = "1.0.0"
        mock_validate_xml.return_value = (mock_tree, mock_root, "1.0.0")

        mock_bump_version.side_effect = ValueError("Invalid bump type")

        result = self.runner.invoke(release, ["invalid"])
        assert result.exit_code == 2
        assert "Invalid value for" in result.output and "'invalid' is not one of" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    def test_release_addon_xml_not_found(self, mock_get_repo, tmp_path):
        """Test release with addon.xml not found at specified path."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        # Create a temp directory (exists, so Click passes), but no addon.xml
        fake_dir = tmp_path / "fake_addon"
        fake_dir.mkdir()

        result = self.runner.invoke(release, ["major", "--addon-path", str(fake_dir)])
        assert result.exit_code == 1
        assert f"addon.xml not found at {fake_dir}/addon.xml" in result.output

    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.bump_version")
    def test_release_repo_error(self, mock_bump_version, mock_find_xml, mock_validate_xml, mock_get_repo):
        """Test release with repository error."""
        mock_validate_xml.return_value = (MagicMock(), MagicMock(), "1.0.0")
        mock_find_xml.return_value = Path("/fake/addon.xml")
        mock_bump_version.return_value = "1.1.0"
        mock_get_repo.side_effect = ValueError("No git repository found")

        result = self.runner.invoke(release, ["major", "--non-interactive"])
        assert result.exit_code == 1
        assert "No git repository found" in result.output

    @patch("kodi_addon_builder.cli.run_pre_commit_hooks")
    @patch("kodi_addon_builder.cli.get_repo")
    @patch("kodi_addon_builder.cli.validate_addon_xml")
    @patch("kodi_addon_builder.cli.find_addon_xml")
    @patch("kodi_addon_builder.cli.bump_version")
    @patch("kodi_addon_builder.cli.update_changelog")
    def test_release_pre_commit_error(
        self,
        mock_update_changelog,
        mock_bump_version,
        mock_find_xml,
        mock_validate_xml,
        mock_get_repo,
        mock_run_pre_commit,
    ):
        """Test release with pre-commit hooks error."""
        mock_validate_xml.return_value = (MagicMock(), MagicMock(), "1.0.0")
        mock_find_xml.return_value = Path("/fake/addon.xml")
        mock_bump_version.return_value = "1.1.0"
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_repo.is_dirty.return_value = False
        mock_get_repo.return_value = mock_repo
        mock_run_pre_commit.side_effect = ValueError("Pre-commit hooks failed")

        result = self.runner.invoke(release, ["major", "--non-interactive"])
        assert result.exit_code == 1
        assert "Pre-commit hooks failed" in result.output


class TestReleaseCommandIntegration:
    """Integration tests for the release CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_release_integration(self, tmp_path, sample_addon_xml_content):
        """Integration test: create git repo with addon, run full release."""
        # Create a temporary git repository
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()

        # Create a bare remote repo
        remote_dir = tmp_path / "remote_repo"
        remote_dir.mkdir()
        git.Repo.init(remote_dir, bare=True)

        # Initialize git repo
        repo = git.Repo.init(repo_dir)

        # Configure git user
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        # Add remote
        repo.create_remote("origin", str(remote_dir))

        # Create addon structure
        addon_dir = repo_dir / "plugin.video.test"
        addon_dir.mkdir()

        # Create addon.xml
        addon_xml = addon_dir / "addon.xml"
        addon_xml.write_text(sample_addon_xml_content)

        # Add and commit initial files
        repo.index.add("*")
        repo.index.commit("Initial commit")

        # Push initial commit
        repo.git.push("origin", "master")

        # Test release command
        with self.runner.isolated_filesystem():
            import os

            old_cwd = os.getcwd()
            os.chdir(str(repo_dir))

            try:
                # Run release in dry-run mode first
                result = self.runner.invoke(release, ["patch", "--dry-run", "--non-interactive"])
                assert result.exit_code == 0
                assert "Dry run: No changes made" in result.output
                assert "Would bump version to 1.0.1" in result.output

                # Verify no changes were made
                tree = ET.parse(addon_xml)
                root = tree.getroot()
                assert root.get("version") == "1.0.0"

                # Now run actual release
                result = self.runner.invoke(release, ["patch", "--news", "Test release"])
                assert result.exit_code == 0
                assert "Current version: 1.0.0" in result.output
                assert "New version: 1.0.1" in result.output
                assert "Successfully released version 1.0.1" in result.output

                # Verify addon.xml was updated
                tree = ET.parse(addon_xml)
                root = tree.getroot()
                assert root.get("version") == "1.0.1"

                # Verify git state
                assert repo.head.commit.message == "Bump version to 1.0.1\n\nTest release"
                assert "v1.0.1" in [tag.name for tag in repo.tags]

            finally:
                os.chdir(old_cwd)
