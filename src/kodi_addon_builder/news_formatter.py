"""
News formatting system for Kodi addon releases.

This module provides comprehensive news formatting capabilities that support
different output formats for commit messages, changelog entries, addon.xml
news sections, and GitHub release notes.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional


class NewsFormatter:
    """
    Formats news content for different output targets.

    Supports Keep a Changelog markdown input with validation and conversion
    to various output formats including Kodi addon.xml bracketed format.
    """

    # Mapping from Keep a Changelog section headers to Kodi bracket codes
    BRACKET_CODES = {
        "added": "[new]",
        "fixed": "[fix]",
        "changed": "[upd]",
        "deprecated": "[dep]",
        "removed": "[rem]",
        "security": "[sec]",
    }

    def __init__(self, summary: str, news: str, version: str, date: Optional[str] = None):
        """
        Initialize the news formatter.

        Args:
            summary: Short summary for commit messages and changelog headers
            news: Full news content in Keep a Changelog markdown format
            version: Version string (e.g., '1.2.4')
            date: ISO date string (defaults to today if not provided)
        """
        self.summary = summary.strip()
        self.news = news.strip()
        self.version = version.strip()
        self.date = date or datetime.now().strftime("%Y-%m-%d")

        # Validate inputs
        self._validate_inputs()

        # Parse the news content
        self.parsed_sections = self._parse_news()

    def _validate_inputs(self) -> None:
        """Validate the input parameters."""
        if not self.summary:
            raise ValueError("Summary cannot be empty")

        if not self.news:
            raise ValueError("News content cannot be empty")

        if not self.version:
            raise ValueError("Version cannot be empty")

        # Check for required markdown section headers
        if not re.search(
            r"^###\s+(Added|Fixed|Changed|Deprecated|Removed|Security)", self.news, re.MULTILINE | re.IGNORECASE
        ):
            raise ValueError(
                "News must contain at least one Keep a Changelog section header (### Added, ### Fixed, etc.)"
            )

    def _parse_news(self) -> Dict[str, List[str]]:
        """
        Parse the markdown news content into sections.

        Returns:
            Dict mapping section names to lists of bullet points
        """
        sections = {}

        # Split by section headers
        section_pattern = r"^###\s+(Added|Fixed|Changed|Deprecated|Removed|Security)$"
        parts = re.split(section_pattern, self.news, flags=re.MULTILINE | re.IGNORECASE)

        # Process sections (parts[0] is any content before first header)
        for i in range(1, len(parts), 2):
            section_name = parts[i].lower()
            section_content = parts[i + 1] if i + 1 < len(parts) else ""

            # Extract bullet points
            bullets = []
            for line in section_content.split("\n"):
                line = line.strip()
                if line.startswith(("- ", "* ", "+ ")):
                    # Remove the bullet marker and clean up
                    bullet_text = re.sub(r"^[-*+]\s+", "", line)
                    if bullet_text:
                        bullets.append(bullet_text)

            if bullets:
                sections[section_name] = bullets

        return sections

    def format_for_commit(self) -> str:
        """
        Format for git commit message.

        Returns:
            Commit message string
        """
        return f"release: {self.version} - {self.summary}"

    def format_for_changelog(self) -> str:
        """
        Format for CHANGELOG.md entry.

        Returns:
            Full changelog entry with header and sections
        """
        lines = ["", f"## [{self.version}] - {self.date} - {self.summary}", ""]

        # Add each section
        for section_name, bullets in self.parsed_sections.items():
            section_title = section_name.capitalize()
            lines.append(f"### {section_title}")
            for bullet in bullets:
                lines.append(f"- {bullet}")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def format_for_addon_news(self, custom_summary: Optional[str] = None) -> str:
        """
        Format for addon.xml news section.

        Args:
            custom_summary: Optional custom summary to use instead of auto-generated

        Returns:
            Bracketed news format for Kodi addon.xml
        """
        lines = [f"v{self.version} ({self.date})"]

        # Add summary
        summary = custom_summary or self.summary
        lines.append(summary)

        # Add bracketed items
        for section_name, bullets in self.parsed_sections.items():
            bracket_code = self.BRACKET_CODES.get(section_name, f"[{section_name[:3]}]")
            for bullet in bullets:
                lines.append(f"{bracket_code} {bullet}")

        result = "\n".join(lines)

        # Check 1500 character limit
        if len(result) > 1500:
            raise ValueError(
                f"addon news limited to 1500 characters rendered (current news is {len(result)}). "
                "either shorten news, or provide summary in --addon-news flag"
            )

        return result

    def format_for_release_notes(self) -> str:
        """
        Format for GitHub RELEASE_NOTES.md file.

        Returns:
            Professional release notes with header and full changelog entry
        """
        lines = [f"# Release Notes - {self.version}", "", f"## [{self.version}] - {self.date} - {self.summary}", ""]

        # Add each section
        for section_name, bullets in self.parsed_sections.items():
            section_title = section_name.capitalize()
            lines.append(f"### {section_title}")
            for bullet in bullets:
                lines.append(f"- {bullet}")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"
