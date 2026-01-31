"""Tests for git CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock

from kodi_addon_builder.cli import commit, tag, push


class TestCommitCommand:
    """Test the commit CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.run_pre_commit_hooks')
    @patch('kodi_addon_builder.cli.stage_changes')
    @patch('kodi_addon_builder.cli.commit_changes')
    def test_commit_success(self, mock_commit_changes, mock_stage_changes,
                           mock_run_pre_commit, mock_get_repo):
        """Test successful commit."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo
        mock_commit_changes.return_value = "abc123"

        result = self.runner.invoke(commit, ['--message', 'Test commit'])
        assert result.exit_code == 0
        assert "Repository: /fake/repo" in result.output
        assert "Committed changes: abc123" in result.output

        mock_get_repo.assert_called_once()
        mock_run_pre_commit.assert_called_once_with(mock_repo)
        mock_stage_changes.assert_called_once_with(mock_repo, None)
        mock_commit_changes.assert_called_once_with(mock_repo, 'Test commit', False)

    @patch('kodi_addon_builder.cli.get_repo')
    def test_commit_no_repo(self, mock_get_repo):
        """Test commit with no git repository."""
        mock_get_repo.side_effect = ValueError("Not a git repository")

        result = self.runner.invoke(commit, ['--message', 'Test commit'])
        assert result.exit_code == 1
        assert "Not a git repository" in result.output

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.run_pre_commit_hooks')
    @patch('kodi_addon_builder.cli.stage_changes')
    @patch('kodi_addon_builder.cli.commit_changes')
    def test_commit_with_files(self, mock_commit_changes, mock_stage_changes,
                              mock_run_pre_commit, mock_get_repo):
        """Test commit with specific files."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_commit_changes.return_value = "abc123"

        result = self.runner.invoke(commit, ['--message', 'Test commit', '--files', 'file1.txt', '--files', 'file2.txt'])
        assert result.exit_code == 0
        mock_stage_changes.assert_called_once_with(mock_repo, ['file1.txt', 'file2.txt'])

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.run_pre_commit_hooks')
    @patch('kodi_addon_builder.cli.stage_changes')
    @patch('kodi_addon_builder.cli.commit_changes')
    def test_commit_allow_empty(self, mock_commit_changes, mock_stage_changes,
                               mock_run_pre_commit, mock_get_repo):
        """Test commit allowing empty commits."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_commit_changes.return_value = "abc123"

        result = self.runner.invoke(commit, ['--message', 'Test commit', '--allow-empty'])
        assert result.exit_code == 0
        mock_commit_changes.assert_called_once_with(mock_repo, 'Test commit', True)

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.run_pre_commit_hooks')
    @patch('kodi_addon_builder.cli.stage_changes')
    def test_commit_no_pre_commit(self, mock_stage_changes, mock_run_pre_commit, mock_get_repo):
        """Test commit skipping pre-commit hooks."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        result = self.runner.invoke(commit, ['--message', 'Test commit', '--no-pre-commit'])
        assert result.exit_code == 0
        mock_run_pre_commit.assert_not_called()

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.run_pre_commit_hooks')
    @patch('kodi_addon_builder.cli.stage_changes')
    def test_commit_pre_commit_failure(self, mock_stage_changes, mock_run_pre_commit, mock_get_repo):
        """Test commit with pre-commit failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_run_pre_commit.side_effect = ValueError("Pre-commit failed")

        result = self.runner.invoke(commit, ['--message', 'Test commit'])
        assert result.exit_code == 1
        assert "Pre-commit failed" in result.output

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.run_pre_commit_hooks')
    def test_commit_stage_failure(self, mock_run_pre_commit, mock_get_repo):
        """Test commit with staging failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_repo.index.add.side_effect = Exception("Staging failed")

        result = self.runner.invoke(commit, ['--message', 'Test commit'])
        assert result.exit_code == 1
        assert "Failed to stage changes: Staging failed" in result.output

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.run_pre_commit_hooks')
    @patch('kodi_addon_builder.cli.stage_changes')
    @patch('kodi_addon_builder.cli.commit_changes')
    def test_commit_commit_failure(self, mock_commit_changes, mock_stage_changes,
                                  mock_run_pre_commit, mock_get_repo):
        """Test commit with commit failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_commit_changes.side_effect = ValueError("No changes to commit")

        result = self.runner.invoke(commit, ['--message', 'Test commit'])
        assert result.exit_code == 1
        assert "No changes to commit" in result.output

    @patch('kodi_addon_builder.cli.get_repo')
    def test_commit_with_repo_path(self, mock_get_repo):
        """Test commit with custom repo path."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/custom/repo"
        mock_get_repo.return_value = mock_repo

        with patch('kodi_addon_builder.cli.run_pre_commit_hooks'), \
             patch('kodi_addon_builder.cli.stage_changes'), \
             patch('kodi_addon_builder.cli.commit_changes', return_value="abc123"):
            # Create the directory so Click validation passes
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                result = self.runner.invoke(commit, ['--message', 'Test commit', '--repo-path', tmpdir])
                assert result.exit_code == 0
                mock_get_repo.assert_called_once_with(Path(tmpdir))


class TestTagCommand:
    """Test the tag CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.create_tag')
    def test_tag_success_lightweight(self, mock_create_tag, mock_get_repo):
        """Test successful lightweight tag creation."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo

        result = self.runner.invoke(tag, ['v1.0.0'])
        assert result.exit_code == 0
        assert "Repository: /fake/repo" in result.output
        assert "Created tag: v1.0.0" in result.output

        mock_create_tag.assert_called_once_with(mock_repo, 'v1.0.0', None)

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.create_tag')
    def test_tag_success_annotated(self, mock_create_tag, mock_get_repo):
        """Test successful annotated tag creation."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo

        result = self.runner.invoke(tag, ['v1.0.0', '--message', 'Release v1.0.0'])
        assert result.exit_code == 0
        mock_create_tag.assert_called_once_with(mock_repo, 'v1.0.0', 'Release v1.0.0')

    @patch('kodi_addon_builder.cli.get_repo')
    def test_tag_no_repo(self, mock_get_repo):
        """Test tag with no git repository."""
        mock_get_repo.side_effect = ValueError("Not a git repository")

        result = self.runner.invoke(tag, ['v1.0.0'])
        assert result.exit_code == 1
        assert "Not a git repository" in result.output

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.create_tag')
    def test_tag_already_exists(self, mock_create_tag, mock_get_repo):
        """Test tag creation when tag already exists."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_create_tag.side_effect = ValueError("Tag 'v1.0.0' already exists")

        result = self.runner.invoke(tag, ['v1.0.0'])
        assert result.exit_code == 1
        assert "Tag 'v1.0.0' already exists" in result.output

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.create_tag')
    def test_tag_with_repo_path(self, mock_create_tag, mock_get_repo):
        """Test tag with custom repo path."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/custom/repo"
        mock_get_repo.return_value = mock_repo

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.runner.invoke(tag, ['v1.0.0', '--repo-path', tmpdir])
            assert result.exit_code == 0
            mock_get_repo.assert_called_once_with(Path(tmpdir))


class TestPushCommand:
    """Test the push CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.push_commits')
    @patch('kodi_addon_builder.cli.get_current_branch')
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

        mock_push_commits.assert_called_once_with(mock_repo, 'origin', None)

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.push_commits')
    @patch('kodi_addon_builder.cli.push_tags')
    @patch('kodi_addon_builder.cli.get_current_branch')
    def test_push_commits_and_tags(self, mock_get_branch, mock_push_tags, mock_push_commits, mock_get_repo):
        """Test pushing commits and tags."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/fake/repo"
        mock_get_repo.return_value = mock_repo
        mock_get_branch.return_value = "main"

        result = self.runner.invoke(push, ['--tags'])
        assert result.exit_code == 0
        assert "Pushed branch: main" in result.output
        assert "Pushed tags" in result.output

        mock_push_commits.assert_called_once_with(mock_repo, 'origin', None)
        mock_push_tags.assert_called_once_with(mock_repo, 'origin')

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.push_commits')
    def test_push_specific_branch(self, mock_push_commits, mock_get_repo):
        """Test pushing specific branch."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        result = self.runner.invoke(push, ['--branch', 'feature-branch'])
        assert result.exit_code == 0
        assert "Pushed branch: feature-branch" in result.output

        mock_push_commits.assert_called_once_with(mock_repo, 'origin', 'feature-branch')

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.push_commits')
    def test_push_custom_remote(self, mock_push_commits, mock_get_repo):
        """Test pushing to custom remote."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        result = self.runner.invoke(push, ['--remote', 'upstream'])
        assert result.exit_code == 0
        mock_push_commits.assert_called_once_with(mock_repo, 'upstream', None)

    @patch('kodi_addon_builder.cli.get_repo')
    def test_push_no_repo(self, mock_get_repo):
        """Test push with no git repository."""
        mock_get_repo.side_effect = ValueError("Not a git repository")

        result = self.runner.invoke(push, [])
        assert result.exit_code == 1
        assert "Not a git repository" in result.output

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.push_commits')
    @patch('kodi_addon_builder.cli.get_current_branch')
    def test_push_commits_failure(self, mock_get_branch, mock_push_commits, mock_get_repo):
        """Test push with commits failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_push_commits.side_effect = ValueError("Push failed")

        result = self.runner.invoke(push, [])
        assert result.exit_code == 1
        assert "Push failed" in result.output

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.push_commits')
    @patch('kodi_addon_builder.cli.push_tags')
    @patch('kodi_addon_builder.cli.get_current_branch')
    def test_push_tags_failure(self, mock_get_branch, mock_push_tags, mock_push_commits, mock_get_repo):
        """Test push with tags failure."""
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_push_tags.side_effect = ValueError("Tags push failed")

        result = self.runner.invoke(push, ['--tags'])
        assert result.exit_code == 1
        assert "Tags push failed" in result.output

    @patch('kodi_addon_builder.cli.get_repo')
    @patch('kodi_addon_builder.cli.push_commits')
    @patch('kodi_addon_builder.cli.get_current_branch')
    def test_push_with_repo_path(self, mock_get_branch, mock_push_commits, mock_get_repo):
        """Test push with custom repo path."""
        mock_repo = MagicMock()
        mock_repo.working_dir = "/custom/repo"
        mock_get_repo.return_value = mock_repo

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.runner.invoke(push, ['--repo-path', tmpdir])
            assert result.exit_code == 0
            mock_get_repo.assert_called_once_with(Path(tmpdir))