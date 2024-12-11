import logging
import time
from urllib.parse import urljoin

from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.common.by import By


class LinkExtractor:
    def __init__(self, browser_session):
        self.browser = browser_session

    def extract_links(self, base_url):
        try:
            anchors = self.browser.get_elements(By.TAG_NAME, "a")
        except WebDriverException as e:
            logging.error(f"Error retrieving anchor elements: {e}")
            return set()

        links = set()

        for anchor in anchors:
            try:
                href = anchor.get_attribute("href")
                if href:
                    full_url = urljoin(base_url, href)
                    links.add(full_url)
            except StaleElementReferenceException:
                continue
            except Exception as e:
                logging.error(f"Error processing anchor element: {e}")
                continue

        return links
