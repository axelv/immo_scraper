from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from itertools import count
import logging
import csv
import sys
import re
import time
from tqdm import tqdm


class ScrapeJob:
    pass


class ImmoWebScraper:

    def __init__(self,
                 url_suffix="appartement/te-koop/gent/9000",
                 sleep_interval=2,
                 chrome_driver_path="C:\\Users\\axelv\\Downloads\\chromedriver_win32\\chromedriver.exe"):

        self.page_url = "https://www.immoweb.be/nl/zoek/" + url_suffix + "?page=%d"
        self.prop_url = "https://www.immoweb.be/nl/zoekertje/" + url_suffix + "/id%s"
        self.sleep_interval=sleep_interval
        self.logger = logging.getLogger(__name__)

        # configure chrome_options
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--start-maximized")
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        self.browser = webdriver.Chrome(executable_path=chrome_driver_path,
                                   options=chrome_options)
        self.browser.delete_all_cookies()
        self.browser.set_window_position(0, 0)

    def _parse_url(self, page):
        return self.page_url % page

    def iterate_pages(self):
        for i in tqdm(count(1), desc="Page"):
            div_list = list()
            try_counter = 0
            url = self._parse_url(i)
            while not div_list or try_counter > 10:
                if try_counter > 0:
                    self.logger.warning("Try %s again." % url)
                self.browser.get(url)
                html = BeautifulSoup(self.browser.page_source, 'html.parser')
                div_list = html.findAll("div", {"data-type": re.compile("resultgallery")})
                try_counter += 1
                time.sleep(self.sleep_interval)

            if div_list:
                for div_item in div_list:
                    yield div_item

    @staticmethod
    def is_relevant(div):
        return not bool(div.findAll("div", {"class": re.compile("logo-bloc")}))

    def extract_info(self, div):
        url = self.prop_url % div['id']
        return url

    def run(self):
        div_iterator = self.iterate_pages()
        relevant_div_iter = filter(self.is_relevant, div_iterator)
        for div in relevant_div_iter:
            print(self.extract_info(div))



if __name__ == "__main__":
    scraper = ImmoWebScraper()
    scraper.run()
