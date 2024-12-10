import yt_dlp
import os
import uuid
import logging
import concurrent.futures


class TimeoutException(Exception):
    pass


class AudioDownloader:
    def __init__(self, download_dir='./downloads', timeout=30):
        self.download_dir = download_dir
        self.timeout = timeout
        os.makedirs(download_dir, exist_ok=True)

    def download_audio(self, url):
        unique_id = str(uuid.uuid4())
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_dir, f'{unique_id}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'ffmpeg_location': '/usr/bin/ffmpeg',
            'playlist_items': '1'
        }

        def download():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if 'requested_downloads' in info:
                        for download_info in info['requested_downloads']:
                            if 'filepath' in download_info:
                                file_path = download_info['filepath']
                                if os.path.exists(file_path):
                                    return os.path.basename(file_path)
            except yt_dlp.utils.DownloadError as e:
                logging.error(f"Failed to download {url}: {e}")
                return None
            except Exception as e:
                logging.error(f"An error occurred while processing {url}: {e}")
                return None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(download)
            try:
                return future.result(timeout=self.timeout)
            except concurrent.futures.TimeoutError:
                logging.info(f"Download operation timed out for {url}.")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")

        return None
