import os
from unittest.mock import MagicMock, patch

import pytest
import yt_dlp

from scraper.audio_downloader import AudioDownloader


@pytest.fixture
def audio_downloader(tmp_path):
    download_dir = tmp_path / "downloads"
    downloader = AudioDownloader(download_dir=str(download_dir), timeout=10)
    return downloader, download_dir


def test_initialization(audio_downloader):
    """Test that the AudioDownloader initializes correctly and creates the download directory."""
    downloader, download_dir = audio_downloader
    assert download_dir.exists()
    assert download_dir.is_dir()


@patch("yt_dlp.YoutubeDL")
def test_download_audio_success(MockYoutubeDL, audio_downloader):
    """Test that download_audio returns the correct file path on success."""
    downloader, download_dir = audio_downloader
    mock_ydl = MockYoutubeDL.return_value
    mock_ydl.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.return_value = {
        "requested_downloads": [{"filepath": f"{download_dir}/1234.mp3"}]
    }

    # Simulate file existence for testing
    (download_dir / "1234.mp3").touch()

    url = "http://testurl.com/video"
    file_path = downloader.download_audio(url)

    expected_path = "1234.mp3"
    assert file_path == expected_path
    mock_ydl.extract_info.assert_called_once_with(url, download=True)


@patch("yt_dlp.YoutubeDL")
def test_download_audio_failure(MockYoutubeDL, audio_downloader):
    """Test that download_audio returns None on a DownloadError."""
    downloader, download_dir = audio_downloader
    mock_ydl = MockYoutubeDL.return_value
    mock_ydl.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Download failed")

    url = "http://invalidurl.com/video"
    file_path = downloader.download_audio(url)

    assert file_path is None
    mock_ydl.extract_info.assert_called_once_with(url, download=True)


@patch("yt_dlp.YoutubeDL")
def test_download_audio_general_exception(MockYoutubeDL, audio_downloader):
    """Test that download_audio returns None and handles a general exception."""
    downloader, download_dir = audio_downloader
    mock_ydl = MockYoutubeDL.return_value
    mock_ydl.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.side_effect = Exception("Unexpected error")

    url = "http://testurl.com/video"
    file_path = downloader.download_audio(url)

    assert file_path is None
    mock_ydl.extract_info.assert_called_once_with(url, download=True)


@patch("yt_dlp.YoutubeDL")
def test_download_audio_timeout(MockYoutubeDL, audio_downloader):
    """Test that download_audio returns None if the operation times out."""

    def long_running_download(*args, **kwargs):
        import time

        time.sleep(15)

    downloader, download_dir = audio_downloader
    mock_ydl = MockYoutubeDL.return_value
    mock_ydl.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.side_effect = long_running_download

    url = "http://testurl.com/video"
    file_path = downloader.download_audio(url)

    assert file_path is None
    mock_ydl.extract_info.assert_called_once_with(url, download=True)


@patch("yt_dlp.YoutubeDL")
def test_download_audio_no_file(MockYoutubeDL, audio_downloader):
    """Test that download_audio returns None when no file is returned."""
    downloader, download_dir = audio_downloader
    mock_ydl = MockYoutubeDL.return_value
    mock_ydl.__enter__.return_value = mock_ydl

    mock_ydl.extract_info.return_value = {"requested_downloads": []}

    url = "http://testurl.com/video"
    file_path = downloader.download_audio(url)

    assert file_path is None
    mock_ydl.extract_info.assert_called_once_with(url, download=True)
