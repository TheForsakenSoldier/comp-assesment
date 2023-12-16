import json
import logging
import os

import scrapy,re
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
import re

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
    json_data=pd.DataFrame(columns=["name","date","data"])
    custom_settings = {
          'LOG_LEVEL': 'ERROR',
      }
    
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
            
            
    #parsing the links
    def parse_link(self, response):
        
        # getting the specific URL of the insider trade
        self.driver.get(response.url)

        # pulling the relevant data
        name=self.driver.find_element(by=By.XPATH,value="/html/body/table[2]/tbody/tr[1]/td[1]/table[1]/tbody/tr/td/a").text
        date=self.driver.find_element(by=By.XPATH,value="/html/body/table[2]/tbody/tr[2]/td/span[2]").text
        relationship=self.driver.find_element(by=By.XPATH,value="/html/body/table[2]/tbody/tr[1]/td[3]/table/tbody/tr[3]/td/span").text
        table_of_stocks=self.driver.find_element(by=By.XPATH,value="/html/body/table[3]/tbody").text
        table_of_options= self.driver.find_element(by=By.XPATH, value="/html/body/table[4]/tbody")
        
        # Splitting the data into rows and creating DataFrame
        df_stocks = pd.DataFrame([row.split() for row in table_of_stocks.split("\n")], columns=["Title", "Title1", "Transaction Date", "Transaction Code", "Amount", "Type", "Price", "Total", "Disposition"])
        
        # Merging 'Title' columns and dropping 'Title1' in one step
        df_stocks['Title'] = df_stocks['Title'] + ' ' + df_stocks["Title1"]
        df_stocks.drop('Title1', axis=1, inplace=True)
        
        #stocks dataframe is clean now handling options
        #creating memory calls for the handling loop
        rows=[]
        table_data=[]
        add_dolar=None
        
        table_of_options_rows=table_of_options.find_elements(By.TAG_NAME,"tr")
        # turning web element into 2 dimentional array for the options table
        for tr in table_of_options_rows:
            for td in tr.find_elements(By.TAG_NAME,"td"):
                #adding null values to empty td's to keep the data stracture correct
                if (td.get_attribute('innerHTML')!=''and td.get_attribute('innerHTML')!=' '):
                    #going through spans the spans to get the relevant data and filtering 
                    for span in td.find_elements(By.TAG_NAME,value='span'):
                        if (span.text != '$'):
                            if(span.get_attribute('class')=='SmallFormData' or span.get_attribute('class')=='FormData'):
                                if add_dolar==None:
                                    if(len(span.text) >0):
                                      table_data.append(span.text)
                                    else:
                                        table_data.append("null")
                                else:
                                    table_data.append('$'+span.text)
                                    add_dolar=None
                        else:
                            add_dolar=True
                            
                else:
                    table_data.append('null')
            rows.append(table_data)
            table_data=[]          
        
        table_options_headers=[ #date format in the data bellow is (month/day/year)
            "Title of Derivative Security",
            "Conversion or Exercise Price of Derivative Security",
            "Transaction Date",
            "Deemed Execution Date, if any",
            "Code", 
            "V","(A)","(D)",
            "Date Exercisable",
            "Expiration Date",
            "Title",
            "Amount or Number of Shares",
            "8. Price of Derivative Security",
            "Number of derivative Securities Beneficially Owned Following Reported Transaction(s)",
            "Ownership Form: Direct (D) or Indirect (I)",
            "Nature of Indirect Beneficial Ownership"
            ]
        df_options=pd.DataFrame(rows,columns=table_options_headers)
        
        
        #adding all of the data together to a stringable data file
        mega_json_data={
            "name":name,
            "date":date,
            "data":{
                "relationship":relationship,
                "data_about_stocks":df_stocks.to_json(orient='records'),
                "data_about_options":df_options.to_json(orient='records')
            } 
        }
        self.json_data.loc[len(self.json_data)]=mega_json_data
        
        
            
        
        
    def spider_closed(self, spider):
        # Quit the browser when the spider is closed and reset the driver
        if hasattr(spider, 'driver'):
            spider.driver.quit()
            spider.driver=None
        return(self.json_data)


    