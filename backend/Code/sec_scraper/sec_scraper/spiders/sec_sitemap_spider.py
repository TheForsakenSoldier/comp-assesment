import json
import logging
import os
import requests
import pandas as pd

from scrapy import Spider, signals
from scrapy.exceptions import CloseSpider
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from scrapy.http import HtmlResponse
import psycopg2
from selenium import webdriver
import xml.etree.ElementTree as ET
#database values
conn=psycopg2.connect(database="postgres",
                      user="postgres",
                      password="If2722002!",
                      port="5432"
                      )


class SecSitemapSpider(Spider):
    name = 'SecSitemapSpider'
    start_urls = ['https://www.sec.gov/sitemap']

    def parse(self, response):
        try:
            # Select the table containing the links
            table = response.xpath('//table[@class="sitemap"]')

            # Select all the links within the table
            links = table.xpath('.//a/@href').getall()
            #implementing the cursor
            cur=conn.cursor()
            #creating index counter
            index=0
            #shoving the data to the table
            for link in links:
                cur.execute("INSERT INTO SEC_sitemap (index, links) VALUES (%s, %s)",(index, link))
                conn.commit()
                index=index+1
            cur.close()
            # Yield the links as items
            yield {'links': links}

        except Exception as e:
            logging.exception("Error occurred during parsing: %s", str(e))
            raise CloseSpider("Error occurred during parsing")


class SecInsiderTradesSpider(Spider):
        name = "sec_insider_trades"
        allowed_domains = ["sec.gov"]
        start_urls = ["http://www.sec.gov"]
        cik = None
        driver = None

        def __init__(self, cik=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cik = cik
            options = FirefoxOptions()
            options.add_argument('--headless')
            driver = webdriver.Firefox(options=options)
            self.driver = driver

        @classmethod
        def from_crawler(cls, crawler, *args, **kwargs):
            spider = super(SecInsiderTradesSpider, cls).from_crawler(crawler, *args, **kwargs)
            crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
            return spider

        def start_requests(self):
            try:
                url = f"https://www.sec.gov/edgar/browse/?CIK={self.cik}&owner=include"
                self.driver.get(url)
                element = self.driver.find_element(By.XPATH, '//*[@id="filingsStart"]/div[2]/div[5]/div')
                self.driver.execute_script('arguments[0].style.display="block"', element)
                element = WebDriverWait(self.driver, 50).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="filingsStart"]/div[2]/div[5]/div/button[1]')))
                element.click()

                body = self.driver.page_source.encode("utf-8")
                response = HtmlResponse(url=url, body=body, encoding="utf-8")

                yield from self.parse(response)

            except Exception as e:
                logging.exception("Error occurred during start_requests: %s", str(e))
                raise CloseSpider("Error occurred during start_requests")

        def parse(self, response):
            try:
                header_element = self.driver.find_element(By.XPATH, '//*[@id="filingsTable_wrapper"]/div[3]/div[1]/div/table/thead/tr')
                headings = [heading.text.replace("\n", " ") for heading in header_element.find_elements(By.TAG_NAME, "th")]
                table_body = self.driver.find_element(By.XPATH, '//*[@id="filingsTable"]/tbody')
                rows = table_body.find_elements(By.TAG_NAME, "tr")
                links = []
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    form_description_div = cells[1].find_element(By.CSS_SELECTOR, "div[data-export]")
                    form_description_link = form_description_div.find_element(By.CSS_SELECTOR, "a.document-link")
                    form_description_href = form_description_link.get_attribute("href")
                    links.append(form_description_href)
            except Exception as e:
                logging.exception("Error occurred during parsing: %s", str(e))
                raise CloseSpider("Error occurred during parsing")
            yield {"links": links}
        def spider_closed(self, spider):
                    if hasattr(spider, 'driver'):
                        spider.driver.quit()

class ProcessLinksSpider(Spider):
    name = "process_links"
    allowed_domains = ["sec.gov"]
    start_urls = []  # Define the start_urls in the code
    driver=None
    def __init__(self, links=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = links     #Define the start_urls
        options=FirefoxOptions     #Define the options
         #adding the executable path to the driver
        driver = webdriver.Firefox(options=options) #Define the driver
        self.driver = driver #local variable for the driver
        
    def parse(self, response):
        for url in self.start_urls:
            self.driver.get(url)
            individual_table=self.driver.find_element(By.XPATH, '/html/body/table[2]')
            share_type=self.driver.find_element(By.XPATH, '/html/body/table[3]' )
            print(individual_table)