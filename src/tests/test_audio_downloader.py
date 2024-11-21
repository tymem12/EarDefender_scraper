import pytest
import os
from unittest.mock import patch, MagicMock
from scraper.audio_downloader import AudioDownloader
import yt_dlp


@pytest.fixture
def audio_downloader(tmp_path):
    download_dir = tmp_path / "downloads"
    downloader = AudioDownloader(download_dir=str(download_dir))
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
    mock_ydl.extract_info.return_value = {"title": "test_audio"}

    url = "https://example.com/fake_video"
    file_path = downloader.download_audio(url)

    expected_path = os.path.join(download_dir, "test_audio.mp3")
    assert file_path == "test_audio.mp3"
    mock_ydl.extract_info.assert_called_once_with(url, download=True)


@patch("yt_dlp.YoutubeDL")
def test_download_audio_failure(MockYoutubeDL, audio_downloader, capsys):
    """Test that download_audio returns None on a DownloadError."""
    downloader, download_dir = audio_downloader
    mock_ydl = MockYoutubeDL.return_value
    mock_ydl.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Download failed")

    url = "https://example.com/fake_video"
    file_path = downloader.download_audio(url)

    assert file_path is None
    mock_ydl.extract_info.assert_called_once_with(url, download=True)

    captured = capsys.readouterr()
    assert "Failed to download https://example.com/fake_video: Download failed" in captured.out


@patch("yt_dlp.YoutubeDL")
def test_download_audio_general_exception(MockYoutubeDL, audio_downloader, capsys):
    """Test that download_audio returns None and handles a general exception."""
    downloader, download_dir = audio_downloader
    mock_ydl = MockYoutubeDL.return_value
    mock_ydl.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.side_effect = Exception("Unexpected error")

    url = "https://example.com/fake_video"
    file_path = downloader.download_audio(url)

    assert file_path is None
    mock_ydl.extract_info.assert_called_once_with(url, download=True)

    captured = capsys.readouterr()
    assert "An error occurred while processing https://example.com/fake_video: Unexpected error" in captured.out
