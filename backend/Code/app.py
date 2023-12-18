# general imports
import pandas as pd
from pandasgui import show
import requests
from bs4 import BeautifulSoup
from currency_converter import CurrencyConverter



# exports the list of data
from pathlib import Path

# Function to convert the company ticker symbol to the CIK number
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup

def getCikNum(ticker, update_required):
   # Check if the ticker symbol exists in the current system
   if Path("./tickers.xlsx").exists() and not update_required:
       # Read the Excel file containing the ticker symbols and their corresponding CIK numbers
       cik_ticker_df = pd.read_excel("./tickers.xlsx")
       try:
           # Try to get the CIK number corresponding to the given ticker symbol
           cik_number_required = cik_ticker_df["CIK"].loc[cik_ticker_df["Ticker"]
                                                       == ticker].values
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
           cik_ticker_df = pd.DataFrame(
               list(ticker_cik_dict.items()), columns=["Ticker", "CIK"])
           # Sort the data frame
           cik_ticker_df = cik_ticker_df.sort_values("Ticker")
           cik_ticker_df = cik_ticker_df.reset_index(drop=True)
           # Export the data frame to an Excel file
           cik_ticker_df.to_excel("./tickers.xlsx", index=False)
           # Get the CIK number of the company
           cik_number_required = cik_ticker_df["CIK"].loc[cik_ticker_df["Ticker"]
                                                       == ticker].values
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
       return 'None Existant ticker symbol'


# Get the data from the json file
def get_local_json_data_as_pandas(path, which_data):
    if which_data == 'q':
        quarter_df = pd.read_json(
            path_or_buf=path, orient='split', compression='infer')
        return quarter_df
    elif which_data == 'a':
        annual_df = pd.read_json(
            path_or_buf=path, orient='split', compression='infer')
        return annual_df


# add leading zeros to a CIK number
def addLeadingZeros(cik):
    cik_str = str(cik)
    zeros_to_add = 10 - len(cik_str)
    cik_with_zeros = '0' * zeros_to_add + cik_str
    return cik_with_zeros



    

# get the dict data for the company
def get_company_facts(cik):

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    headers = {'From': 'IFlearnandwork@protonmail.com',
               'User-Agent': "IFleanandwork@protonmail.com"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for unsuccessful requests
        dict_data = response.json()
        return pd.DataFrame.from_dict(dict_data["facts"]["us-gaap"],orient= 'index')

    except requests.exceptions.RequestException as e:
        print(
            f"Error occurred while fetching company facts for CIK {cik}: {e}")

    except ValueError as e:
        print(f"Error occurred while parsing company facts for CIK {cik}: {e}")

    return None

# this gets the json from the SEC and summrises its debt.

def turn_into_pandas(dictionary):
    df=pd.DataFrame.from_dict(dictionary,orient='index')
    return df
    






def get_Financial_Data_By_Ticker(ticker):
    # converting ticker to a cik number
    cik = getCikNum(ticker=ticker, update_required=False)
    if cik != "None Existant ticker symbol":
        cik = addLeadingZeros(cik=cik)
        # get the json file from the sec containing the data of the company and turning it to a data frame
       
        company_facts = get_company_facts(cik=cik)
        company_facts['units'] = company_facts['units'].apply(turn_into_pandas)
        show(company_facts['units'])
       
        
        
        
    
    else:
        return "None Existant ticker symbol"
get_Financial_Data_By_Ticker("tsla")