from unittest.mock import MagicMock

import pytest
from selenium.webdriver.common.by import By

# Adjust the import path if needed
from scraper.link_extractor import LinkExtractor


@pytest.fixture
def mock_browser_session():
    """Fixture to create a mock browser session."""
    return MagicMock()


@pytest.fixture
def link_extractor(mock_browser_session):
    """Fixture to initialize LinkExtractor with a mock browser session."""
    return LinkExtractor(mock_browser_session)


def test_extract_links_with_absolute_urls(link_extractor, mock_browser_session):
    """Test extracting links when all anchor tags have absolute URLs."""
    # Set up mock anchor elements
    mock_anchor1 = MagicMock()
    mock_anchor1.get_attribute.return_value = "https://example.com/page1"

    mock_anchor2 = MagicMock()
    mock_anchor2.get_attribute.return_value = "https://example.com/page2"

    mock_browser_session.get_elements.return_value = [mock_anchor1, mock_anchor2]

    # Call extract_links and verify results
    base_url = "https://example.com"
    links = link_extractor.extract_links(base_url)

    expected_links = {"https://example.com/page1", "https://example.com/page2"}
    assert links == expected_links
    mock_browser_session.get_elements.assert_called_once_with(By.TAG_NAME, "a")


def test_extract_links_with_relative_urls(link_extractor, mock_browser_session):
    """Test extracting links when anchor tags have relative URLs."""
    # Set up mock anchor elements with relative URLs
    mock_anchor1 = MagicMock()
    mock_anchor1.get_attribute.return_value = "/page1"

    mock_anchor2 = MagicMock()
    mock_anchor2.get_attribute.return_value = "/page2"

    mock_browser_session.get_elements.return_value = [mock_anchor1, mock_anchor2]

    # Call extract_links and verify results
    base_url = "https://example.com"
    links = link_extractor.extract_links(base_url)

    expected_links = {"https://example.com/page1", "https://example.com/page2"}
    assert links == expected_links
    mock_browser_session.get_elements.assert_called_once_with(By.TAG_NAME, "a")


def test_extract_links_with_mixed_urls(link_extractor, mock_browser_session):
    """Test extracting links with a mix of absolute, relative, and empty hrefs."""
    # Set up mock anchor elements with mixed URLs
    mock_anchor1 = MagicMock()
    mock_anchor1.get_attribute.return_value = "https://example.com/page1"

    mock_anchor2 = MagicMock()
    mock_anchor2.get_attribute.return_value = "/page2"

    mock_anchor3 = MagicMock()
    mock_anchor3.get_attribute.return_value = ""  # Empty href

    mock_anchor4 = MagicMock()
    mock_anchor4.get_attribute.return_value = None  # None href

    mock_browser_session.get_elements.return_value = [
        mock_anchor1,
        mock_anchor2,
        mock_anchor3,
        mock_anchor4,
    ]

    # Call extract_links and verify results
    base_url = "https://example.com"
    links = link_extractor.extract_links(base_url)

    expected_links = {"https://example.com/page1", "https://example.com/page2"}
    assert links == expected_links
    mock_browser_session.get_elements.assert_called_once_with(By.TAG_NAME, "a")


def test_extract_links_no_links(link_extractor, mock_browser_session):
    """Test extract_links when there are no anchor tags or hrefs."""
    # Set up mock to return an empty list
    mock_browser_session.get_elements.return_value = []

    # Call extract_links and verify results
    base_url = "https://example.com"
    links = link_extractor.extract_links(base_url)

    # Expect an empty set when no links are found
    assert links == set()
    mock_browser_session.get_elements.assert_called_once_with(By.TAG_NAME, "a")
