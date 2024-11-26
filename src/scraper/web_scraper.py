from .browser_session import BrowserSession
from .link_extractor import LinkExtractor
from .audio_downloader import AudioDownloader
import time
import logging


class WebScraper:
    def __init__(
            self,
            starting_point: str,
            max_depth: int,
            max_files: int,
            max_pages: int,
            model: str,
            max_time_per_file: int,
            max_total_time: int,
            download_dir: str='./downloads'
        ):
        self.starting_point = starting_point
        self.max_depth = max_depth
        self.max_files = max_files
        self.max_pages = max_pages
        self.model = model
        self.max_time_per_file = max_time_per_file
        self.max_total_time = max_total_time
        self.download_dir = download_dir
        
        self.start_time = time.time()
        self.visit_queue = [(self.starting_point, 0)]
        self.visited = set()
        self.extracted_files = list()
        self.page_counter = 0
        self.file_counter = 0
        self.link_counter = 1

        self.browser = BrowserSession()
        self.link_extractor = LinkExtractor(self.browser)
        self.media_downloader = AudioDownloader(self.download_dir)

    def scrape(self):
        self.start_time = time.time()

        while self.visit_queue:
            current_url, current_depth = self.visit_queue.pop(0)

            if self.check_conditions(current_depth):
                break

            if current_url in self.visited:
                continue

            self.visited.add(current_url)
            self.page_counter += 1

            self.process_page(current_url, current_depth)

        self.browser.close()
        return self.extracted_files
    
    def check_conditions(self, current_depth):
        elapsed_time = time.time() - self.start_time

        logging.log(f'id: {id(self)}; time: {elapsed_time}; pages: {self.page_counter}; files: {self.file_counter}; depth: {current_depth}')
        return (
            self.page_counter >= self.max_pages or
            self.file_counter >= self.max_files or
            current_depth >= self.max_depth or
            elapsed_time >= self.max_total_time
        )
    
    def process_page(self, url, current_depth):
        self.browser.visit(url)

        links = self.link_extractor.extract_links(url)
        path = self.media_downloader.download_audio(url)

        if path is not None:
            self.extracted_files.append(path)
            self.file_counter += 1

        unvisited_links = [link for link in links if link not in self.visited]
        for link in unvisited_links:
            self.visit_queue.append((link, current_depth + 1))
            self.link_counter += 1

            if self.link_counter >= self.max_pages:
                break
