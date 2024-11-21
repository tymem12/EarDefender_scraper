import pytest
from unittest.mock import patch, MagicMock
import time
from scraper.web_scraper import WebScraper


@pytest.fixture
def mock_browser_session():
    """Fixture to create a mock BrowserSession."""
    with patch("scraper.web_scraper.BrowserSession") as MockBrowserSession:
        mock_browser = MockBrowserSession.return_value
        yield mock_browser

@pytest.fixture
def mock_link_extractor():
    """Fixture to create a mock LinkExtractor."""
    with patch("scraper.web_scraper.LinkExtractor") as MockLinkExtractor:
        mock_extractor = MockLinkExtractor.return_value
        yield mock_extractor

@pytest.fixture
def mock_audio_downloader():
    """Fixture to create a mock AudioDownloader."""
    with patch("scraper.web_scraper.AudioDownloader") as MockAudioDownloader:
        mock_downloader = MockAudioDownloader.return_value
        yield mock_downloader

@pytest.fixture
def web_scraper(mock_browser_session, mock_link_extractor, mock_audio_downloader):
    """Fixture to initialize WebScraper with mocked dependencies."""
    return WebScraper(
        starting_point="https://example.com",
        max_depth=2,
        max_files=2,
        max_pages=2,
        model="sample_model",
        max_time_per_file=5,
        max_total_time=10,
        download_dir="./downloads"
    )


def test_initialization(web_scraper):
    """Test that WebScraper initializes with correct attributes."""
    assert web_scraper.starting_point == "https://example.com"
    assert web_scraper.max_depth == 2
    assert web_scraper.max_files == 2
    assert web_scraper.max_pages == 2
    assert web_scraper.model == "sample_model"
    assert web_scraper.max_time_per_file == 5
    assert web_scraper.max_total_time == 10
    assert web_scraper.download_dir == "./downloads"
    assert web_scraper.visit_queue == [("https://example.com", 0)]
    assert web_scraper.page_counter == 0
    assert web_scraper.file_counter == 0


@patch("time.time", side_effect=[0, 1, 2, 3, 4, 5, 6])
def test_scrape_process(mock_time, web_scraper, mock_browser_session, mock_link_extractor, mock_audio_downloader):
    """Test the scraping process."""
    mock_browser_session.visit.return_value = None
    mock_browser_session.close.return_value = None
    mock_link_extractor.extract_links.side_effect = [
        {"https://example.com/page1", "https://example.com/page2"},
        set()
    ]
    mock_audio_downloader.download_audio.side_effect = ["file1.mp3", None]

    extracted_files = web_scraper.scrape()
    assert extracted_files == ["file1.mp3"]
    
    assert mock_browser_session.visit.call_count == 2
    assert mock_link_extractor.extract_links.call_count == 2
    assert mock_audio_downloader.download_audio.call_count == 2
    mock_browser_session.close.assert_called_once()


def test_check_conditions(web_scraper):
    """Test that check_conditions stops the scrape process based on different limits."""
    web_scraper.page_counter = 2
    assert web_scraper.check_conditions(current_depth=1)

    web_scraper.page_counter = 0
    web_scraper.file_counter = 2
    assert web_scraper.check_conditions(current_depth=1)

    web_scraper.file_counter = 0
    assert web_scraper.check_conditions(current_depth=2)

    web_scraper.page_counter = 0
    web_scraper.file_counter = 0
    web_scraper.start_time = time.time() - 11
    assert web_scraper.check_conditions(current_depth=1)


def test_process_page(web_scraper, mock_browser_session, mock_link_extractor, mock_audio_downloader):
    """Test that process_page visits a URL, extracts links, and downloads audio."""
    mock_browser_session.visit.return_value = None
    mock_link_extractor.extract_links.return_value = set(["https://example.com/page1", "https://example.com/page2"])
    mock_audio_downloader.download_audio.return_value = "file1.mp3"
    web_scraper.max_pages = 3

    web_scraper.process_page("https://example.com", current_depth=0)
    assert web_scraper.file_counter == 1
    assert web_scraper.extracted_files == ["file1.mp3"]
    assert web_scraper.visit_queue == [("https://example.com", 0), ("https://example.com/page1", 1), ("https://example.com/page2", 1)]
    
    mock_browser_session.visit.assert_called_once_with("https://example.com")
    mock_link_extractor.extract_links.assert_called_once_with("https://example.com")
    mock_audio_downloader.download_audio.assert_called_once_with("https://example.com")
