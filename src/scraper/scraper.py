from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import time
import yt_dlp
import os


class WebScraper:

    def __init__(self, starting_point, max_depth, max_pages):
        self.starting_point = starting_point
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited = set()

        self.download_dir = './downloads'

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')

        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape(self):
        links_counter = 0
        to_visit = [(self.starting_point, 0)]
        pages_scraped = 0

        while to_visit and pages_scraped < self.max_pages:
            current_url, current_depth = to_visit.pop(0)

            if current_depth >= self.max_depth or links_counter >= self.max_pages:
                break

            if current_url in self.visited:
                continue

            self.driver.get(current_url)
            time.sleep(5)

            links = self.extract_links(current_url)
            self.download_media(current_url)

            self.visited.add(current_url)
            pages_scraped += 1
                    
            for link in links:
                if link not in self.visited:
                    to_visit.append((link, current_depth + 1))
                    links_counter += 1

        self.driver.quit()

        return links_counter

    def extract_links(self, base_url):
        anchors = self.driver.find_elements(By.TAG_NAME, 'a')
        links = set()

        for anchor in anchors:
            href = anchor.get_attribute('href')
            if href:
                full_url = urljoin(base_url, href)
                links.add(full_url)

        return links


    def download_media(self, url):
        """Use yt-dlp Python library to download the media file, whether audio or video."""
        ydl_opts = {
            'format': 'bestaudio/best',  # Best audio quality
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),  # Output filename
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',  # Extract only the audio
                'preferredcodec': 'mp3',  # Convert to mp3
                'preferredquality': '192',  # Audio quality
            }],
            'quiet': False  # Set to True if you want to suppress the output
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])  # Download the media
                print(f"Downloaded: {url}")
        except yt_dlp.utils.DownloadError as e:
            print(f"Failed to download {url}: {e}")
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")
