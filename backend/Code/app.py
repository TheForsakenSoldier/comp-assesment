# general imports
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys

from currency_converter import CurrencyConverter
# spider libraries
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
# self made spiders
from sec_scraper.sec_scraper.spider_folder.spiders import SecInsiderTradesSpider


# Add the directory containing the spider file to the system path
sys.path.append(os.path.abspath('./sec_scraper/sec_scraper/spiders'))

# Function to convert the company ticker symbol to the CIK number
def getCikNum(ticker, update_required):
   # Check if the ticker symbol exists in the current system
   if os.path.isfile("./tickers.xlsx") and not update_required:
       # Read the Excel file containing the ticker symbols and their corresponding CIK numbers
       cik_ticker_df = pd.read_excel("./tickers.xlsx")
       try:
           # Try to get the CIK number corresponding to the given ticker symbol
           cik_number_required = cik_ticker_df["CIK"].loc[cik_ticker_df["Ticker"] == ticker].values
       except IndexError:
           # If the ticker symbol is not found, call the function again with update_required set to True
           return getCikNum(ticker=ticker, update_required=True)
   else:
       # If the ticker symbol does not exist or the system does not have the tickers.xlsx file in it
       try:
           # Get the list of ticker symbols and their corresponding CIK numbers from the SEC website
           ticker_to_CIK_URL = "https://www.sec.gov/include/ticker.txt"
           headers = {'User-Agent': "IFleanandwork@protonmail.com"}
           response = requests.get(ticker_to_CIK_URL, headers=headers)
           soup = BeautifulSoup(response.content, "html5lib")
           txt_dirty = soup.get_text()
           # Clean the data
           lines = [line.strip() for line in txt_dirty.split('\n')]
           lines = [line.strip() for line in txt_dirty.split()]
           ticker_cik_dict = dict(zip(lines[::2], lines[1::2]))
           cik_ticker_df = pd.DataFrame(list(ticker_cik_dict.items()), columns=["Ticker", "CIK"])
           # Sort the data frame
           cik_ticker_df = cik_ticker_df.sort_values("Ticker")
           cik_ticker_df = cik_ticker_df.reset_index(drop=True)
           # Export the data frame to an Excel file
           cik_ticker_df.to_excel("./tickers.xlsx", index=False)
           # Get the CIK number of the company
           cik_number_required = cik_ticker_df["CIK"].loc[cik_ticker_df["Ticker"] == ticker].values
       except requests.exceptions.RequestException:
           # If there is an error connecting to the SEC website, print an error message and return None
           print("Error: Unable to connect to https://www.sec.gov/include/ticker.txt.")
           return None
   try:
       # Try to get the first CIK number from the list of CIK numbers
       cik_number_required = cik_number_required[0]
       return cik_number_required
   except IndexError:
       # If the ticker symbol is not found, print an error message and return None
       print(f"Error: Ticker {ticker} not found.")
       return None


# add leading zeros to a CIK number
def addLeadingZeros(cik):
    cik_str = str(cik)
    zeros_to_add = 10 - len(cik_str)
    cik_with_zeros = '0' * zeros_to_add + cik_str
    return cik_with_zeros

# calculate the growth rate between two values
def calculate_growth_rate(initial_value, final_value):
    growth_rate = ((final_value - initial_value) / initial_value) * 100
    return growth_rate


# get the json data for the company
def get_company_facts(cik):

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    headers = {'From': 'IFlearnandwork@protonmail.com',
               'User-Agent': "IFleanandwork@protonmail.com"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for unsuccessful requests
        json_data = response.json()
        return json_data

    except requests.exceptions.RequestException as e:
        print(
            f"Error occurred while fetching company facts for CIK {cik}: {e}")

    except ValueError as e:
        print(f"Error occurred while parsing company facts for CIK {cik}: {e}")

    return None

#this gets the json from the SEC and summrises its debt.
def summarize_debt_quarterly(json_list, currency_list):
    c = CurrencyConverter()
    summary = []
    # Iterate over each JSON object and currency
    for json_obj, currency in zip(json_list, currency_list):
        # Iterate over each JSON item within the current JSON object
        for json_item in json_obj:
            # Get the currency debt amount
            debt_amount = json_item['val']
            try:
                # Convert debt amount to USD
                debt_usd = c.convert(debt_amount, currency, 'USD')
            except:
                # Handle currency conversion errors
                print(
                    f"Error converting {currency} to USD for debt amount: {debt_amount}")
                continue

            # Extract year and quarter information
            year = json_item['fy']
            quarter = json_item['fp']
            if (quarter == 'FY'):
                quarter = 'Q4'
            # Create a summary dictionary for the current debt
            debt_summary = {
                'year': year,
                'quarter': quarter,
                'long_term_debt': debt_usd
            }
            # Append the debt summary to the list
            summary.append(debt_summary)

    return summary

# This function creates a single dataframe from a list of dataframes annualy. Each dataframe in the list represents data for a company from a certain subject (like gross profit, net income, etc.)
def create_1_dataframe_annual(df_list, column_list):
   # Create an empty DataFrame to store the combined data
   combined_df = pd.DataFrame(columns=column_list)
   
   # Iterate over each dataframe in the list
   for df in df_list:
       # If the dataframe has a column named 'frame', drop it
       if 'frame' in df.columns:
           df = df.drop('frame', axis=1)
       
       # If the dataframe has a column named 'form', filter out rows where 'form' is '10-K/A' or '10-Q'
       if 'form' in df.columns:
           df = df[df['form'] != '10-K/A']
           df = df[df['form'] != '10-Q']
           df.reset_index(drop=True, inplace=True)
       
       # If the dataframe has a column named 'end', create new columns 'year' and 'quarter' from the 'end' column
       if 'end' in df.columns:
           df['year'] = pd.to_datetime(df['end']).dt.year
           df['quarter'] = pd.to_datetime(df['end']).dt.quarter
       
       # Try to add the relevant columns from the current dataframe to the combined dataframe
       try:
           if 'equity' in df.columns:
               combined_df[['year', 'quarter', 'equity']] = df[['year', 'quarter', 'equity']]
           elif 'long_term_debt' in df.columns:
               combined_df['long_term_debt'] = df['long_term_debt']
           elif 'gross_profit' in df.columns:
               combined_df['gross_profit'] = df['gross_profit']
           elif 'net_income' in df.columns:
               combined_df['net_income'] = df['net_income']
           elif 'EPS' in df.columns:
               combined_df['EPS'] = df['EPS']
       except Exception as e:
           print(f"Error occurred during join: {e}")

   # If the combined dataframe is empty, return it as is
   if combined_df.empty:
       return combined_df
   
   # Group the combined dataframe by 'year' and 'quarter', and sum the values in each group
   combined_df = combined_df.groupby(['year', 'quarter'], as_index=False).sum()
   
   # Reset the index of the combined dataframe
   combined_df = combined_df.reset_index(drop=True)

   # Return the combined dataframe
   return combined_df


# This function creates a single dataframe from a list of dataframes quarterly. Each dataframe in the list represents data for a company from a certain subject (like gross profit, net income, etc.)
def create_1_dataframe_quarterly(df_list, column_list):
   # Create an empty DataFrame to store the combined data
   combined_df = pd.DataFrame(columns=column_list)

   # Loop through each DataFrame in the list
   for df in df_list:
       # If 'frame' column exists in the DataFrame, drop it
       if 'frame' in df.columns:
           df = df.drop('frame', axis=1)
       # If 'form' column exists in the DataFrame, filter out rows where 'form' is '10-K/A' or '10-K'
       if 'form' in df.columns:
           df = df[df['form'] != '10-K/A']
           df = df[df['form'] != '10-K']
           # Reset the index of the DataFrame
           df.reset_index(drop=True, inplace=True)
       # If 'end' column exists in the DataFrame, extract the year and quarter from it
       if 'end' in df.columns:
           df['year'] = pd.to_datetime(df['end']).dt.year
           df['quarter'] = pd.to_datetime(df['end']).dt.quarter

       # Try to add the relevant columns from the DataFrame to the combined DataFrame
       try:
           if 'equity' in df.columns:
               combined_df[['year', 'quarter', 'equity']] = df[['year', 'quarter', 'equity']]
           elif 'long_term_debt' in df.columns:
               combined_df['long_term_debt'] = df['long_term_debt']
           elif 'gross_profit' in df.columns:
               combined_df['gross_profit'] = df['gross_profit']
           elif 'net_income' in df.columns:
               combined_df['net_income'] = df['net_income']
           elif 'EPS' in df.columns:
               combined_df['EPS'] = df['EPS']
       # If an error occurs during the join, print the error message
       except Exception as e:
           print(f"Error occurred during join: {e}")

   # If the combined DataFrame is empty, return it
   if combined_df.empty:
       return combined_df

   # Group the combined DataFrame by 'year' and 'quarter', and sum the values for each group
   combined_df = combined_df.groupby(['year', 'quarter'], as_index=False).sum()
   # Reset the index of the combined DataFrame
   combined_df = combined_df.reset_index(drop=True)

   # Return the combined DataFrame
   return combined_df


# This function extracts relevant data from a JSON file and returns two dataframes: one for annual data and one for quarterly data
def get_relevant_json_data(json_data):
   # Initialize an empty list to store the dataframes
   df_list = []

   # Try to extract the list of liabilities from the JSON data
   try:
       list_of_liabilities = json_data['facts']['us-gaap']['Liabilities']['units']['USD']
   except KeyError:
       list_of_liabilities = None 

   # Try to extract the list of net income from the JSON data
   try:
       list_of_net_income = json_data['facts']['us-gaap']['NetIncomeLoss']['units']['USD']
   except KeyError:
       try:
           list_of_net_income = json_data['facts']['us-gaap']['ProfitLoss']['units']['USD']
       except:
           print("Error: Unable to find NetIncomeLoss or ProfitLoss.")
           list_of_net_income = None 

   # Try to extract the list of gross profit from the JSON data
   try:
       list_of_gross_profit = json_data['facts']['us-gaap']['GrossProfit']['units']['USD']
   except KeyError:
       try:
           list_of_gross_profit = json_data['facts']['us-gaap']['IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest']['units']['USD']
       except KeyError:
           print("Error: Unable to find GrossProfit or IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest.")
           list_of_gross_profit = None 

   # Try to extract the list of equity from the JSON data
   try:
       list_of_equity = json_data['facts']['us-gaap']['StockholdersEquity']['units']['USD']
   except KeyError:
       list_of_equity = None

   # Try to extract the list of long term debt from the JSON data
   try:
       list_of_long_term_debt = json_data['facts']['us-gaap']['OtherLiabilitiesNoncurrent']['units']['USD']
   except KeyError:
       try:
           list_of_long_term_debt = json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units']['USD']
       except:
           try:
               list_of_long_term_debt = json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units']['USD']
           except KeyError:
               try:
                  if len(list(json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units'].keys())) > 1:
                      print("speacial case: long term debt in multiple currencies")
                      currencies = list(json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units'].keys())
                      list_of_long_term_debt = []
                      for currency in currencies:
                          list_of_long_term_debt.append(json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units'][currency])
                      list_of_long_term_debt = summarize_debt_quarterly(list_of_long_term_debt, currencies)
               except:
                  print("cant find long term debt please contact us.")
                  list_of_long_term_debt = None

   # Try to extract the list of EPS from the JSON data
   try:
       list_of_eps = json_data['facts']['us-gaap']['EarningsPerShareDiluted']['units']['USD/shares']
   except KeyError:
       try:
           list_of_eps = json_data['facts']['us-gaap']['EarningsPerShareBasic']['units']['USD/shares']
       except KeyError:
           print("Error: Unable to find EarningsPerShare.")
           list_of_eps = None

   # Convert the lists of data to dataframes
   df_gross_profit = pd.DataFrame(list_of_gross_profit)
   df_net_income = pd.DataFrame(list_of_net_income)
   df_long_term_debt = pd.DataFrame(list_of_long_term_debt)
   df_equity = pd.DataFrame(list_of_equity)
   df_eps = pd.DataFrame(list_of_eps)

   # Rename the 'val' column in each dataframe to a more descriptive name
   df_equity.rename(columns={"val": 'equity'}, inplace=True)
   df_long_term_debt.rename(columns={'val': "long_term_debt"}, inplace=True)
   df_gross_profit.rename(columns={'val': 'gross_profit'}, inplace=True)
   df_net_income.rename(columns={'val': 'net_income'}, inplace=True)
   df_eps.rename(columns={'val': 'EPS'}, inplace=True)
   
   # Add the dataframes to the list
   df_list.append(df_net_income)
   df_list.append(df_gross_profit)
   df_list.append(df_long_term_debt)
   df_list.append(df_equity)
   df_list.append(df_eps)

   # Define the columns that will be in the final dataframes
   columns = ['year', 'quarter', 'net_income', 'equity',
              'gross_profit', 'long_term_debt', 'EPS']
    
   # Call the function to create the final dataframes
   mega_frame_quarters = create_1_dataframe_quarterly(df_list=df_list, column_list=columns)
   mega_frame_annual = create_1_dataframe_annual(df_list=df_list, column_list=columns)
   return [mega_frame_annual, mega_frame_quarters]

#this function calls to a spider to get the insider data from the SEC website
def get_Insider_Trades_Data(cik):
   # Create a Scrapy crawler process
    process = CrawlerProcess(get_project_settings())
    # Start the spider
    process.crawl(SecInsiderTradesSpider, cik=cik)
    links = process.start(stop_after_crawl=True)
   

def get_Financial_Data_By_Ticker(ticker):
    #converting ticker to a cik number
    cik = getCikNum(ticker=ticker, update_required=False)
    if cik is not None:
        cik = addLeadingZeros(cik=cik)
        #get the json file from the sec containing the data of the company
        company_facts = get_company_facts(cik=cik)
        #handle the giant json file and clean irrelevant data
        data = get_relevant_json_data(company_facts)
        #getting the insider data
        company_insider_data = get_Insider_Trades_Data(cik=cik)
        return(data)
    

print(get_Financial_Data_By_Ticker("tsla"))
