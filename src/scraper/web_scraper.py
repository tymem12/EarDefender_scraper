import logging
import os
import time

import requests

from .audio_downloader import AudioDownloader
from .browser_session import BrowserSession
from .link_extractor import LinkExtractor


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
        download_dir: str = "./downloads",
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
        self.media_downloader = AudioDownloader(self.download_dir, max_time_per_file)

    def scrape(self, headers, analysis_id):
        try:
            self.start_time = time.time()

            while self.visit_queue:
                current_url, current_depth = self.visit_queue.pop(0)

                if self.check_conditions(current_depth):
                    break

                if current_url in self.visited:
                    continue

                self.visited.add(current_url)
                self.page_counter += 1

                self.process_page(current_url, current_depth, headers, analysis_id)

                if not self.visit_queue:
                    logging.info("Visit queue is empty.")
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
        finally:
            self.browser.close()
        return self.extracted_files

    def check_conditions(self, current_depth):
        elapsed_time = time.time() - self.start_time

        logging.info(
            f"""id: {
                id(self)}; time: {elapsed_time}; pages: {
                self.page_counter}; files: {
                self.file_counter}; depth: {current_depth}"""
        )
        return (
            self.page_counter >= self.max_pages
            or self.file_counter >= self.max_files
            or current_depth >= self.max_depth
            or elapsed_time >= self.max_total_time
        )

    def process_page(self, url, current_depth, headers, analysis_id):
        try:
            self.browser.visit(url)

            links = self.link_extractor.extract_links(url)

            search_result = self.find_existing_analysis(url, headers)

            if search_result is not None:
                self.update_analysis(headers, analysis_id, search_result)
                self.file_counter += 1
            else:
                path = self.media_downloader.download_audio(url)

                if path is not None:
                    self.extracted_files.append({"filePath": path, "link": url})
                    self.file_counter += 1

            unvisited_links = [link for link in links if link not in self.visited]
            for link in unvisited_links:
                self.visit_queue.append((link, current_depth + 1))
                self.link_counter += 1

                if self.link_counter >= self.max_pages:
                    break

        except Exception as e:
            logging.error(f"{id(self)} Error processing page {url}: {e}")
            self.browser.restart_browser()

    def find_existing_analysis(self, url, headers):
        try:
            body = {"links": [url]}
            logging.info(body)
            connector_address = os.getenv("CONNECTOR_ADDRESS")
            connector_port = os.getenv("CONNECTOR_PORT")

            response = requests.get(
                f"http://{connector_address}:{connector_port}/predictions/model/{self.model}",
                json=body,
                headers=headers,
                timeout=100,
            )

            if response.status_code == 200:
                logging.info("Received model predictions for given url.")

                response_data = response.json()

                if isinstance(response_data, list) and len(response_data) > 0:
                    first_item = response_data[0]
                    logging.info(f"First item link: {first_item['link']}")
                    return first_item
                else:
                    logging.info("Response body is not a list or is empty.")
                    return None
        except requests.RequestException as exc:
            logging.error(f"Request failed: {exc}")
            return None

    def update_analysis(self, headers, analysis_id, analysis_result):
        try:
            body = {"predictionResults": [analysis_result]}
            logging.info(
                f'Updating analysis {analysis_id}, link: {analysis_result["link"]}'
            )
            connector_address = os.getenv("CONNECTOR_ADDRESS")
            connector_port = os.getenv("CONNECTOR_PORT")

            response = requests.put(
                f"http://{connector_address}:{connector_port}/analyses/{analysis_id}/predictions",
                json=body,
                headers=headers,
                timeout=100,
            )

            if response.status_code == 200:
                logging.info("Successfully updated analysis")
            else:
                logging.error(
                    f"Error response: {response.status_code}, Body: {response.text}"
                )
        except requests.RequestException as exc:
            logging.error(f"Request failed: {exc}")
