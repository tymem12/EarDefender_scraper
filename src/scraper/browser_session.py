import logging
import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BrowserSession:
    def __init__(self):
        self._initialize_browser()

    def _initialize_browser(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--no-first-run")
        self.driver = webdriver.Chrome(options=chrome_options)

    def visit(self, url, retries=3):
        for attempt in range(retries):
            try:
                start_time = time.time()
                self.driver.get(url)

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                WebDriverWait(self.driver, 5).until(
                    lambda driver: (time.time() - start_time) >= 5
                )

                return
            except Exception as e:
                logging.error(
                    f"Attempt {
                        attempt +
                        1} failed visiting {url}: {e}"
                )
                if attempt < retries - 1:
                    continue
                self.restart_browser()
                raise

    def get_elements(self, by, value):
        try:
            return self.driver.find_elements(by, value)
        except WebDriverException as e:
            logging.error(f"Error retrieving elements: {e}")
            self.restart_browser()
            return []

    def close(self):
        if self.driver:
            self.driver.quit()

    def restart_browser(self):
        logging.info("Restarting browser session...")
        self.close()
        self._initialize_browser()
