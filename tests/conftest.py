"""Test configuration and fixtures for kodi-addon-builder."""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def sample_addon_xml_content():
    """Sample addon.xml content for testing."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="plugin.video.test" name="Test Addon" version="1.0.0" provider-name="Test Provider">
    <requires>
        <import addon="xbmc.python" version="3.0.0"/>
    </requires>
    <extension point="xbmc.python.pluginsource" library="lib">
        <provides>video</provides>
    </extension>
    <extension point="xbmc.addon.metadata">
        <summary>Test addon for Kodi</summary>
        <description>Test addon description</description>
        <platform>all</platform>
    </extension>
</addon>"""


@pytest.fixture
def invalid_addon_xml_content():
    """Invalid addon.xml content for testing."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<notaddon id="plugin.video.test" name="Test Addon" version="1.0.0" provider-name="Test Provider">
    <requires>
        <import addon="xbmc.python" version="3.0.0"/>
    </requires>
</notaddon>"""


@pytest.fixture
def addon_xml_no_version():
    """addon.xml without version attribute."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="plugin.video.test" name="Test Addon" provider-name="Test Provider">
    <requires>
        <import addon="xbmc.python" version="3.0.0"/>
    </requires>
</addon>"""


@pytest.fixture
def addon_xml_invalid_version():
    """addon.xml with invalid version."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="plugin.video.test" name="Test Addon" version="invalid.version" provider-name="Test Provider">
    <requires>
        <import addon="xbmc.python" version="3.0.0"/>
    </requires>
</addon>"""


@pytest.fixture
def malformed_xml():
    """Malformed XML content."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="plugin.video.test" name="Test Addon" version="1.0.0" provider-name="Test Provider">
    <requires>
        <import addon="xbmc.python" version="3.0.0"/>
    </requires>
    <!-- Missing closing tag -->"""


@pytest.fixture
def temp_addon_dir(tmp_path, sample_addon_xml_content):
    """Create a temporary directory with addon.xml."""
    addon_dir = tmp_path / "addon"
    addon_dir.mkdir()
    addon_xml = addon_dir / "addon.xml"
    addon_xml.write_text(sample_addon_xml_content)
    return addon_dir


@pytest.fixture
def temp_addon_dir_no_xml(tmp_path):
    """Create a temporary directory without addon.xml."""
    addon_dir = tmp_path / "addon_no_xml"
    addon_dir.mkdir()
    return addon_dir


@pytest.fixture
def temp_nested_addon_dir(tmp_path, sample_addon_xml_content):
    """Create a temporary directory with addon.xml in a subdirectory."""
    root_dir = tmp_path / "nested"
    root_dir.mkdir()
    addon_dir = root_dir / "plugin.video.test"
    addon_dir.mkdir()
    addon_xml = addon_dir / "addon.xml"
    addon_xml.write_text(sample_addon_xml_content)
    return root_dir


@pytest.fixture
def mock_repo():
    """Mock git repository for testing."""
    repo = MagicMock()
    repo.git = MagicMock()
    return repo
