"""Tests for the bump command in kodi-addon-builder."""

import pytest
from click.testing import CliRunner
from pathlib import Path  # noqa: F401
import xml.etree.ElementTree as ET
from unittest.mock import patch

from kodi_addon_builder.cli import (
    bump,
    find_addon_xml,
    validate_addon_xml,
    bump_version,
)


class TestFindAddonXml:
    """Test find_addon_xml function."""

    def test_find_addon_xml_in_current_dir(self, temp_addon_dir):
        """Test finding addon.xml in the current directory."""
        with patch("pathlib.Path.cwd", return_value=temp_addon_dir):
            result = find_addon_xml()
            assert result == temp_addon_dir / "addon.xml"

    def test_find_addon_xml_in_subdirectory(self, temp_nested_addon_dir):
        """Test finding addon.xml in subdirectories."""
        result = find_addon_xml(temp_nested_addon_dir)
        expected = temp_nested_addon_dir / "plugin.video.test" / "addon.xml"
        assert result == expected

    def test_find_addon_xml_not_found(self, tmp_path):
        """Test when addon.xml is not found."""
        result = find_addon_xml(tmp_path)
        assert result is None


class TestValidateAddonXml:
    """Test validate_addon_xml function."""

    def test_validate_valid_xml(self, temp_addon_dir):
        """Test validating a valid addon.xml."""
        addon_xml_path = temp_addon_dir / "addon.xml"
        tree, root, version = validate_addon_xml(addon_xml_path)
        assert root.tag == "addon"
        assert version == "1.0.0"
        assert root.get("version") == "1.0.0"

    def test_validate_invalid_root_element(self, tmp_path, invalid_addon_xml_content):
        """Test validating XML with invalid root element."""
        addon_xml = tmp_path / "addon.xml"
        addon_xml.write_text(invalid_addon_xml_content)
        with pytest.raises(ValueError, match="Root element is not 'addon'"):
            validate_addon_xml(addon_xml)

    def test_validate_no_version(self, tmp_path, addon_xml_no_version):
        """Test validating XML without version attribute."""
        addon_xml = tmp_path / "addon.xml"
        addon_xml.write_text(addon_xml_no_version)
        with pytest.raises(ValueError, match="No version attribute found"):
            validate_addon_xml(addon_xml)

    def test_validate_invalid_version(self, tmp_path, addon_xml_invalid_version):
        """Test validating XML with invalid version format."""
        addon_xml = tmp_path / "addon.xml"
        addon_xml.write_text(addon_xml_invalid_version)
        with pytest.raises(ValueError, match="Invalid version"):
            validate_addon_xml(addon_xml)

    def test_validate_malformed_xml(self, tmp_path, malformed_xml):
        """Test validating malformed XML."""
        addon_xml = tmp_path / "addon.xml"
        addon_xml.write_text(malformed_xml)
        with pytest.raises(ValueError, match="Invalid XML"):
            validate_addon_xml(addon_xml)


class TestBumpVersion:
    """Test bump_version function."""

    @pytest.mark.parametrize(
        "current_version,bump_type,expected",
        [
            ("1.0.0", "patch", "1.0.1"),
            ("1.0.0", "minor", "1.1.0"),
            ("1.0.0", "major", "2.0.0"),
            ("1.2.3", "patch", "1.2.4"),
            ("1.2.3", "minor", "1.3.0"),
            ("1.2.3", "major", "2.0.0"),
            ("0.1.0", "major", "1.0.0"),
        ],
    )
    def test_bump_version_valid(self, current_version, bump_type, expected):
        """Test bumping version with valid inputs."""
        result = bump_version(current_version, bump_type)
        assert result == expected

    def test_bump_version_invalid_type(self):
        """Test bumping version with invalid bump type."""
        with pytest.raises(ValueError, match="Invalid bump type"):
            bump_version("1.0.0", "invalid")


class TestBumpCommand:
    """Test the bump CLI command."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_bump_patch_success(self, temp_addon_dir):
        """Test successful patch bump."""
        with patch("pathlib.Path.cwd", return_value=temp_addon_dir):
            result = self.runner.invoke(bump, ["patch", "--non-interactive"])
            assert result.exit_code == 0
            assert "Current version: 1.0.0" in result.output
            assert "New version: 1.0.1" in result.output
            assert "Updated addon.xml with version 1.0.1" in result.output

            # Check XML was updated
            tree = ET.parse(temp_addon_dir / "addon.xml")
            root = tree.getroot()
            assert root.get("version") == "1.0.1"

    def test_bump_minor_success(self, temp_addon_dir):
        """Test successful minor bump."""
        with patch("pathlib.Path.cwd", return_value=temp_addon_dir):
            result = self.runner.invoke(bump, ["minor", "--non-interactive"])
            assert result.exit_code == 0
            assert "New version: 1.1.0" in result.output

            tree = ET.parse(temp_addon_dir / "addon.xml")
            root = tree.getroot()
            assert root.get("version") == "1.1.0"

    def test_bump_major_success(self, temp_addon_dir):
        """Test successful major bump."""
        with patch("pathlib.Path.cwd", return_value=temp_addon_dir):
            result = self.runner.invoke(bump, ["major", "--non-interactive"])
            assert result.exit_code == 0
            assert "New version: 2.0.0" in result.output

            tree = ET.parse(temp_addon_dir / "addon.xml")
            root = tree.getroot()
            assert root.get("version") == "2.0.0"

    def test_bump_with_addon_path(self, temp_addon_dir):
        """Test bump with --addon-path option."""
        result = self.runner.invoke(bump, ["patch", "--addon-path", str(temp_addon_dir), "--non-interactive"])
        assert result.exit_code == 0
        assert f"Found addon.xml at: {temp_addon_dir / 'addon.xml'}" in result.output

    def test_bump_addon_path_not_exists(self, tmp_path):
        """Test bump with non-existent addon path."""
        nonexistent_path = tmp_path / "nonexistent"
        result = self.runner.invoke(bump, ["patch", "--addon-path", str(nonexistent_path)])
        assert result.exit_code == 2  # Click exits with 2 for invalid path

    def test_bump_no_addon_xml_found(self, temp_addon_dir_no_xml):
        """Test bump when no addon.xml is found."""
        with patch("pathlib.Path.cwd", return_value=temp_addon_dir_no_xml):
            result = self.runner.invoke(bump, ["patch"])
            assert result.exit_code == 1
            assert "Error: Could not find addon.xml" in result.output

    def test_bump_invalid_xml(self, tmp_path, invalid_addon_xml_content):
        """Test bump with invalid XML."""
        addon_dir = tmp_path / "invalid_addon"
        addon_dir.mkdir()
        addon_xml = addon_dir / "addon.xml"
        addon_xml.write_text(invalid_addon_xml_content)

        with patch("pathlib.Path.cwd", return_value=addon_dir):
            result = self.runner.invoke(bump, ["patch"])
            assert result.exit_code == 1
            assert "Invalid addon.xml: Root element is not 'addon'" in result.output

    def test_bump_dry_run(self, temp_addon_dir):
        """Test bump with --dry-run option."""
        with patch("pathlib.Path.cwd", return_value=temp_addon_dir):
            result = self.runner.invoke(bump, ["patch", "--dry-run", "--non-interactive"])
            assert result.exit_code == 0
            assert "Dry run: No changes made" in result.output

            # Check XML was NOT updated
            tree = ET.parse(temp_addon_dir / "addon.xml")
            root = tree.getroot()
            assert root.get("version") == "1.0.0"

    def test_bump_with_news(self, temp_addon_dir):
        """Test bump with --news option."""
        news_text = "Added new feature"
        with patch("pathlib.Path.cwd", return_value=temp_addon_dir):
            result = self.runner.invoke(bump, ["patch", "--news", news_text])
            assert result.exit_code == 0
            assert f"News: {news_text}" in result.output

    @patch("click.prompt")
    def test_bump_interactive_news(self, mock_prompt, temp_addon_dir):
        """Test bump prompting for news in interactive mode."""
        mock_prompt.return_value = "Interactive news entry"
        with patch("pathlib.Path.cwd", return_value=temp_addon_dir):
            result = self.runner.invoke(bump, ["patch"])
            assert result.exit_code == 0
            assert "News: Interactive news entry" in result.output
            mock_prompt.assert_called_once_with("Enter news/changelog for this version", default="")

    def test_bump_non_interactive_no_news(self, temp_addon_dir):
        """Test bump in non-interactive mode without news."""
        with patch("pathlib.Path.cwd", return_value=temp_addon_dir):
            result = self.runner.invoke(bump, ["patch", "--non-interactive"])
            assert result.exit_code == 0
            assert "News:" not in result.output

    @patch("click.prompt")
    def test_bump_non_interactive_with_news(self, mock_prompt, temp_addon_dir):
        """Test bump in non-interactive mode with news provided."""
        with patch("pathlib.Path.cwd", return_value=temp_addon_dir):
            result = self.runner.invoke(bump, ["patch", "--non-interactive", "--news", "News provided"])
            assert result.exit_code == 0
            assert "News: News provided" in result.output
            # prompt should not be called
            mock_prompt.assert_not_called()

    def test_bump_invalid_bump_type(self):
        """Test bump with invalid bump type (should not happen due to click.Choice)."""
        # Test the underlying function directly
        with pytest.raises(ValueError, match="Invalid bump type"):
            bump_version("1.0.0", "invalid")
