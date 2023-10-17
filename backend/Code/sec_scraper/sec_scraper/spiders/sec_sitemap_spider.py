import json
import logging
import os
import scrapy
import requests
import pandas as pd

from scrapy import Spider, signals
from scrapy.exceptions import CloseSpider
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from scrapy.http import HtmlResponse
import psycopg2
from selenium import webdriver
import xml.etree.ElementTree as ET
from lxml import etree as et

#database values


class SecSitemapSpider(Spider):
    name = 'SecSitemapSpider'
    start_urls = ['https://www.sec.gov/sitemap']
  
    def parse(self, response):
        try:
            # Select the table containing the links
            table = response.xpath('//table[@class="sitemap"]')
            conn=psycopg2.connect(database="postgres",
                                    user="postgres",
                                    password="If2722002!",
                                    port="5432"
                                    )
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
        # Configure Firefox options
        options = FirefoxOptions()
        # Uncomment the line below to run the browser in headless mode
        # options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        self.driver = driver

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # Connect the spider_closed signal to spider_closed method
        spider = super(SecInsiderTradesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def start_requests(self):
        try:
            # Construct URL with CIK and open it in the browser
            url = f"https://www.sec.gov/edgar/browse/?CIK={self.cik}&owner=include"
            self.driver.get(url)
            
            # Perform some actions on the page using Selenium
            element = self.driver.find_element(By.XPATH, '//*[@id="filingsStart"]/div[2]/div[5]/div')
            self.driver.execute_script('arguments[0].style.display="block"', element)
            element = WebDriverWait(self.driver, 50).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="filingsStart"]/div[2]/div[5]/div/button[1]')))
            element.click()

            # Get the page source and create a Scrapy response
            body = self.driver.page_source.encode("utf-8")
            response = HtmlResponse(url=url, body=body, encoding="utf-8")

            # Yield from the parse method to handle the response
            yield from self.parse(response)

        except Exception as e:
            # Log and handle exceptions during start_requests
            logging.exception("Error occurred during start_requests: %s", str(e))
            raise CloseSpider("Error occurred during start_requests")

    def parse(self, response):
        try:
            # Extract table headings
            header_element = self.driver.find_element(By.XPATH, '//*[@id="filingsTable_wrapper"]/div[3]/div[1]/div/table/thead/tr')
            headings = [heading.text.replace("\n", " ") for heading in header_element.find_elements(By.TAG_NAME, "th")]

            # Extract links from the table
            table_body = self.driver.find_element(By.XPATH, '//*[@id="filingsTable"]/tbody')
            rows = table_body.find_elements(By.TAG_NAME, "tr")
            links = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                form_description_div = cells[1].find_element(By.CSS_SELECTOR, "div[data-export]")
                form_description_link = form_description_div.find_element(By.CSS_SELECTOR, "a.document-link")
                form_description_href = form_description_link.get_attribute("href")
                links.append(form_description_href)
                break
        except Exception as e:
            # Log and handle exceptions during parsing
            logging.exception("Error occurred during parsing: %s", str(e))
            raise CloseSpider("Error occurred during parsing")
        
        # Yield the extracted links
        for link in links:
            yield scrapy.Request(url=link,callback=self.parse_link)
            break
            
    #parsing the links
    def parse_link(self, response):
        
        # getting the specific URL of the insider trade
        self.driver.get(response.url)

        # pulling the relevant data
        name=self.driver.find_element(by=By.XPATH,value="/html/body/table[2]/tbody/tr[1]/td[1]/table[1]/tbody/tr/td/a").text
        date=self.driver.find_element(by=By.XPATH,value="/html/body/table[2]/tbody/tr[2]/td/span[2]").text
        relationship=self.driver.find_element(by=By.XPATH,value="/html/body/table[2]/tbody/tr[1]/td[3]/table/tbody/tr[3]/td/span").text
        table_of_group_indivdual=self.driver.find_element(by=By.XPATH,value="/html/body/table[2]/tbody/tr[3]/td[2]/table/tbody")
        
    def spider_closed(self, spider):
        # Quit the browser when the spider is closed and reset the driver
        if hasattr(spider, 'driver'):
            spider.driver.quit()
            spider.driver=None


    