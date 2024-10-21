from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import time


class WebScraper:

    def __init__(self, starting_point, max_depth, max_pages):
        self.starting_point = starting_point
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited = set()

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')

        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape(self):
        found_links = [self.starting_point]
        to_visit = [(self.starting_point, 0)]
        pages_scraped = 0

        while to_visit and pages_scraped < self.max_pages:
            current_url, current_depth = to_visit.pop(0)

            if current_depth >= self.max_depth or len(found_links) >= self.max_pages:
                break

            if current_url in self.visited:
                continue

            self.driver.get(current_url)
            time.sleep(5)

            links = self.extract_links(current_url)

            self.visited.add(current_url)
            pages_scraped += 1

            for link in links:
                if len(found_links) < self.max_pages:
                    found_links.append(link)
                    
            for link in links:
                if link not in self.visited:
                    to_visit.append((link, current_depth + 1))

        self.driver.quit()

        return found_links

    def extract_links(self, base_url):
        anchors = self.driver.find_elements(By.TAG_NAME, 'a')
        links = set()

        for anchor in anchors:
            href = anchor.get_attribute('href')
            if href:
                full_url = urljoin(base_url, href)
                links.add(full_url)

        return links
