from selenium.webdriver.common.by import By
from urllib.parse import urljoin


class LinkExtractor:
    def __init__(self, browser_session):
        self.browser = browser_session

    def extract_links(self, base_url):
        anchors = self.browser.get_elements(By.TAG_NAME, 'a')
        links = set()

        for anchor in anchors:
            href = anchor.get_attribute('href')
            if href:
                full_url = urljoin(base_url, href)
                links.add(full_url)

        return links
