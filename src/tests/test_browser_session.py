from unittest.mock import MagicMock, patch

import pytest

from scraper.browser_session import BrowserSession


@pytest.fixture
def browser_session():
    with patch("selenium.webdriver.Chrome") as MockChrome:
        mock_driver = MagicMock()
        MockChrome.return_value = mock_driver
        session = BrowserSession()
        yield session, mock_driver
        session.close()


def test_visit(browser_session):
    session, mock_driver = browser_session
    session.visit("https://example.com")
    mock_driver.get.assert_called_once_with("https://example.com")


def test_get_elements(browser_session):
    session, mock_driver = browser_session
    mock_driver.find_elements.return_value = [MagicMock()]
    elements = session.get_elements("id", "test-id")
    mock_driver.find_elements.assert_called_once_with("id", "test-id")
    assert len(elements) == 1


def test_close(browser_session):
    session, mock_driver = browser_session
    session.close()
    mock_driver.quit.assert_called_once()
