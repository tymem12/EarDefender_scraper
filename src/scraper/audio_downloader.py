import yt_dlp
import os
import uuid


class AudioDownloader:
    def __init__(self, download_dir='./downloads'):
        self.download_dir = download_dir
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
            'quiet': False,
            'ffmpeg_location': '/usr/bin/ffmpeg',
            'playlist_items': '1'
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = f"{unique_id}.mp3"
                return file_path
        except yt_dlp.utils.DownloadError as e:
            print(f"Failed to download {url}: {e}")
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")

        return None
