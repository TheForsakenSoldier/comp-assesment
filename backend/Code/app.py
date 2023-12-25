# general imports

from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from currency_converter import CurrencyConverter
from pandasgui import show


def get_cik_num(ticker, update_required):
    # Check if the ticker symbol exists in the current system
    if Path("./tickers.xlsx").exists() and not update_required:
        # Read the Excel file containing the ticker symbols and their corresponding CIK numbers
        cik_ticker_df = pd.read_excel("./tickers.xlsx")
        # Check if the ticker symbol exists in the DataFrame
        if ticker in cik_ticker_df["Ticker"].values:
            # If it exists, get the corresponding CIK number
            cik_number_required = cik_ticker_df["CIK"].loc[cik_ticker_df["Ticker"]
                                                           == ticker].values[0]
        else:
            # If it doesn't exist, call the function again with update_required set to True
            return get_cik_num(ticker=ticker, update_required=True)
    else:
        # If the ticker symbol does not exist or the system does not have the tickers.xlsx file in it
        ticker_to_CIK_URL = "https://www.sec.gov/include/ticker.txt"
        headers = {'User-Agent': "IFleanandwork@protonmail.com"}
        response = requests.get(ticker_to_CIK_URL, headers=headers)
        # Check if the HTTP request was successful
        if response.status_code != 200:
            # If it wasn't, print an error message and return None
            print("Error: Unable to connect to https://www.sec.gov/include/ticker.txt.")
            return None
        soup = BeautifulSoup(response.content, "html5lib")
        txt_dirty = soup.get_text()
        lines = [line.strip() for line in txt_dirty.split('\n')]
        lines = [line.strip() for line in txt_dirty.split()]
        ticker_cik_dict = dict(zip(lines[::2], lines[1::2]))
        cik_ticker_df = pd.DataFrame(
            list(ticker_cik_dict.items()), columns=["Ticker", "CIK"])
        cik_ticker_df = cik_ticker_df.sort_values("Ticker")
        cik_ticker_df = cik_ticker_df.reset_index(drop=True)
        cik_ticker_df.to_excel("./tickers.xlsx", index=False)
        # Check if the ticker symbol exists in the DataFrame
        if ticker in cik_ticker_df["Ticker"].values:
            # If it exists, get the corresponding CIK number
            cik_number_required = cik_ticker_df["CIK"].loc[cik_ticker_df["Ticker"]
                                                           == ticker].values[0]
        else:
            # If it doesn't exist, print an error message and return None
            print(f"Error: Ticker {ticker} not found.")
            return "None Existant ticker symbol"
    # Return the CIK number
    return cik_number_required

# add leading zeros to a CIK number
def add_leading_zeros(cik):
    cik_str = str(cik)
    zeros_to_add = 10 - len(cik_str)
    cik_with_zeros = '0' * zeros_to_add + cik_str
    return cik_with_zeros

# Define the function to get company facts
def get_company_facts(cik):
  # Construct the URL for the API request
  url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
  # Define the headers for the API request
  headers = {'From': 'IFlearnandwork@protonmail.com',
             'User-Agent': "IFleanandwork@protonmail.com"}
  
  # Send the GET request to the API
  response = requests.get(url, headers=headers)
  # Check the status of the HTTP response
  if response.status_code != 200:
      # If the request was unsuccessful, print an error message and return None
      print(f"Error occurred while fetching company facts for CIK {cik}: {response.reason}")
      return None
  
  # Parse the JSON response
  dict_data = response.json()
  # Check if the response contains the expected data
  if "facts" in dict_data and "us-gaap" in dict_data["facts"]:
      # If the data is present, convert it to a DataFrame and return it
      return pd.DataFrame.from_dict(dict_data["facts"]["us-gaap"], orient='index')
  else:
      # If the data is not present, print an error message and return None
      print(f"Error occurred while parsing company facts for CIK {cik}: Unexpected response format")
      return None


# this turns a dict into a dataframe considering the dict is structured as a list of dictionaries
def turn_into_pandas(dictionary):
    for key in dictionary.keys():
        list_of_data = dictionary[key]
        df = pd.DataFrame(list_of_data)
        return df

# exporting the data to local filesystem
def export_local_data(data_frame, ticker):
    path = Path('/data/' + ticker + '.json')
    data_frame.to_json(path)

# import from local filesystem


def import_local_data(ticker):
    path_local_file = Path("data" / ticker + '.json')
    if Path('/data/').exists == False:

        #  if path_local_file.exists():
        return pd.read_json(path_local_file)
    else:
        return "Unsuccessful import"


def get_financial_data_by_ticker(ticker):
    # converting ticker to a cik number
    cik = get_cik_num(ticker=ticker, update_required=False)
    if cik != "None Existant ticker symbol":
        cik = add_leading_zeros(cik=cik)
        # get the dictionary file from the sec containing the data of the company and turning it to a data frame
        company_facts = get_company_facts(cik=cik)
        company_facts.rename(columns={"index": "search_val"}, inplace=True)
        company_facts['units'] = company_facts['units'].apply(turn_into_pandas)

    else:
        return "None Existant ticker symbol"


get_financial_data_by_ticker("")
