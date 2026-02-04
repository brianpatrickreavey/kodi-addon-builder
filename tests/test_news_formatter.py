"""
Tests for news formatting functionality.
"""

import pytest

from kodi_addon_builder.news_formatter import NewsFormatter
from kodi_addon_builder.cli import update_changelog_with_content, update_addon_news


class TestNewsFormatter:
    """Test NewsFormatter class functionality."""

    def test_init_valid(self):
        """Test NewsFormatter initialization with valid inputs."""
        formatter = NewsFormatter(summary="Bug fixes", news="### Fixed\n- Fixed a bug\n- Another fix", version="1.2.3")
        assert formatter.summary == "Bug fixes"
        assert formatter.version == "1.2.3"
        assert "Fixed a bug" in formatter.news

    def test_init_invalid_news(self):
        """Test NewsFormatter rejects invalid news format."""
        with pytest.raises(ValueError, match="News must contain at least one Keep a Changelog section header"):
            NewsFormatter(summary="Test", news="Invalid format without headers", version="1.0.0")

    def test_format_for_commit(self):
        """Test commit message formatting."""
        formatter = NewsFormatter(summary="Bug fixes", news="### Fixed\n- Fixed issue #123", version="1.2.3")
        commit_msg = formatter.format_for_commit()
        assert commit_msg == "release: 1.2.3 - Bug fixes"

    def test_format_for_release_notes(self):
        """Test GitHub release notes formatting."""
        formatter = NewsFormatter(
            summary="New features",
            news="### Added\n- New feature A\n- New feature B\n### Fixed\n- Bug fix",
            version="2.0.0",
        )
        release_notes = formatter.format_for_release_notes()
        assert "# Release Notes - 2.0.0" in release_notes
        assert "## [2.0.0]" in release_notes
        assert "### Added" in release_notes
        assert "- New feature A" in release_notes
        assert "### Fixed" in release_notes
        assert "- Bug fix" in release_notes

    def test_format_for_changelog(self):
        """Test CHANGELOG.md entry formatting."""
        formatter = NewsFormatter(
            summary="Breaking changes", news="### Changed\n- Breaking change in API", version="3.0.0"
        )
        changelog_entry = formatter.format_for_changelog()
        assert "## [3.0.0]" in changelog_entry
        assert "- Breaking changes" in changelog_entry
        assert "### Changed" in changelog_entry
        assert "- Breaking change in API" in changelog_entry

    def test_format_for_addon_news(self):
        """Test addon.xml news formatting with bracket codes."""
        formatter = NewsFormatter(
            summary="Updates",
            news="### Added\n- New feature\n### Fixed\n- Bug fixed\n### Changed\n- API change",
            version="1.1.0",
        )
        addon_news = formatter.format_for_addon_news()
        assert "[new]" in addon_news
        assert "[fix]" in addon_news
        assert "[upd]" in addon_news
        assert "New feature" in addon_news
        assert "Bug fixed" in addon_news

    def test_format_for_addon_news_custom_summary(self):
        """Test addon.xml news with custom summary."""
        formatter = NewsFormatter(summary="Original summary", news="### Fixed\n- Bug fix", version="1.0.1")
        addon_news = formatter.format_for_addon_news(custom_summary="Custom summary for addon")
        assert "Custom summary for addon" in addon_news
        assert "[fix]" in addon_news

    def test_bracket_code_mapping(self):
        """Test that bracket codes are correctly mapped."""
        # Test each section type maps to correct bracket code
        test_cases = [
            ("### Added\n- New thing", "[new]"),
            ("### Fixed\n- Bug fix", "[fix]"),
            ("### Changed\n- Change", "[upd]"),
            ("### Deprecated\n- Deprecated", "[dep]"),
            ("### Removed\n- Removed", "[rem]"),
            ("### Security\n- Security fix", "[sec]"),
        ]

        for news_content, expected_bracket in test_cases:
            formatter = NewsFormatter(summary="Test", news=news_content, version="1.0.0")
            addon_news = formatter.format_for_addon_news()
            assert expected_bracket in addon_news

    def test_format_for_addon_news_too_long(self):
        """Test that addon news exceeding 1500 characters raises ValueError."""
        # Create a very long news content that will exceed 1500 characters when formatted
        long_news = "### Security\n\n" + "- test item\n" * 1000

        formatter = NewsFormatter(summary="Test Release", news=long_news, version="1.0.0")

        with pytest.raises(ValueError, match="addon news limited to 1500 characters"):
            formatter.format_for_addon_news()

    def test_init_empty_summary(self):
        """Test that empty summary raises ValueError."""
        with pytest.raises(ValueError, match="Summary cannot be empty"):
            NewsFormatter(summary="", news="### Added\n- feature", version="1.0.0")

    def test_init_empty_news(self):
        """Test that empty news raises ValueError."""
        with pytest.raises(ValueError, match="News content cannot be empty"):
            NewsFormatter(summary="Test", news="", version="1.0.0")

    def test_init_empty_version(self):
        """Test that empty version raises ValueError."""
        with pytest.raises(ValueError, match="Version cannot be empty"):
            NewsFormatter(summary="Test", news="### Added\n- feature", version="")


class TestUpdateFunctions:
    """Test utility update functions."""

    def test_update_changelog_with_content_new_file(self, tmp_path):
        """Test updating changelog when file doesn't exist."""
        changelog_path = tmp_path / "CHANGELOG.md"
        new_entry = "## [1.0.0] - 2024-01-01 - New release\n\n### Added\n- New feature\n"

        update_changelog_with_content(changelog_path, new_entry)

        content = changelog_path.read_text()
        assert "# Changelog" in content
        assert "## [1.0.0]" in content
        assert "New feature" in content

    def test_update_changelog_with_content_existing_file(self, tmp_path):
        """Test updating changelog when file already exists."""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text("""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.9.0] - 2023-12-01 - Previous release

### Fixed
- Previous bug fix
""")

        new_entry = "## [1.0.0] - 2024-01-01 - New release\n\n### Added\n- New feature\n"

        update_changelog_with_content(changelog_path, new_entry)

        content = changelog_path.read_text()
        # Should have header, then new entry, then old content
        assert "## [1.0.0]" in content
        assert "## [0.9.0]" in content
        assert "New feature" in content
        assert "Previous bug fix" in content

    def test_update_addon_news_new_element(self, tmp_path):
        """Test adding news element when it doesn't exist."""
        addon_xml_path = tmp_path / "addon.xml"
        addon_xml_path.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<addon id="plugin.video.test" version="1.0.0" xmlns="http://www.kodi.tv">
    <extension point="xbmc.addon.metadata">
        <summary>Test addon</summary>
        <version>1.0.0</version>
    </extension>
</addon>""")

        news_content = "[fix] Bug fix\n[upd] API change"
        update_addon_news(addon_xml_path, news_content)

        content = addon_xml_path.read_text()
        assert "news>" in content  # Check for news element (with or without namespace)
        assert news_content in content

    def test_update_addon_news_existing_element(self, tmp_path):
        """Test updating news element when it already exists."""
        addon_xml_path = tmp_path / "addon.xml"
        addon_xml_path.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<addon id="plugin.video.test" version="1.0.0" xmlns="http://www.kodi.tv">
    <extension point="xbmc.addon.metadata">
        <summary>Test addon</summary>
        <version>1.0.0</version>
        <news>Old news content</news>
    </extension>
</addon>""")

        news_content = "[new] New feature"
        update_addon_news(addon_xml_path, news_content)

        content = addon_xml_path.read_text()
        assert "news>" in content  # Check for news element (with or without namespace)
        assert news_content in content
        assert "Old news content" not in content

    def test_update_addon_news_invalid_xml(self, tmp_path):
        """Test error handling for invalid XML."""
        addon_xml_path = tmp_path / "addon.xml"
        addon_xml_path.write_text("Invalid XML content")

        with pytest.raises(ValueError, match="Invalid XML"):
            update_addon_news(addon_xml_path, "news content")

    def test_update_addon_news_missing_extension(self, tmp_path):
        """Test error handling when extension element is missing."""
        addon_xml_path = tmp_path / "addon.xml"
        addon_xml_path.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<addon id="plugin.video.test" version="1.0.0" xmlns="http://www.kodi.tv">
    <extension point="xbmc.python.script">
        <summary>Test addon</summary>
    </extension>
</addon>""")

        with pytest.raises(ValueError, match="Could not find xbmc.addon.metadata extension"):
            update_addon_news(addon_xml_path, "news content")
