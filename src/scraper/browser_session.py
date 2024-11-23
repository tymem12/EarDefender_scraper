from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import logging


class BrowserSession:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--remote-debugging-port=9222')
        self.driver = webdriver.Chrome(options=chrome_options)

    def visit(self, url):
        self.driver.get(url)
        logging.info('PRZED 5 S')
        time.sleep(5)
        logging.info('PO 5 S')


    def get_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def close(self):
        self.driver.quit()
