#general imports
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os,sys

from currency_converter import CurrencyConverter
#spider libraries
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
#self made spiders 
from sec_scraper.sec_scraper.spider_folder.spiders import SecInsiderTradesSpider


# Add the directory containing the spider file to the system path
sys.path.append(os.path.abspath('./sec_scraper/sec_scraper/spiders'))

# Import the spider


# import data from an excel file
def importExcelComp(company_name):
    """
    This function imports data from an Excel file located at ./companies_data/ directory
    """
    try:
        df = pd.read_excel(f'./companies_data/{company_name}.xlsx')
        return df
    except FileNotFoundError:
        print(
            f"Error: File {company_name}.xlsx not found in ./companies_data/ directory.")


# convert the company ticker symbol to the CIK number
def getCikNum(ticker, update_required):
    """
    This function returns the CIK number for a given ticker symbol
    """
    # check to see if the ticker symbol exists in the current system
    if os.path.isfile("./tickers.xlsx") and not update_required:
        cik_ticker_df = pd.read_excel("./tickers.xlsx")
        try:
            cik_number_required = cik_ticker_df["CIK"].loc[cik_ticker_df["Ticker"]
                                                           == ticker].values
        except IndexError:
            return getCikNum(ticker=ticker, update_required=True)
    else:
        # if the ticker dosent exist or the system dosent have the tickers.xlsx file in it
        try:
            # get the list from the sec website
            ticker_to_CIK_URL = "https://www.sec.gov/include/ticker.txt"
            headers = {'User-Agent': "IFleanandwork@protonmail.com"}
            response = requests.get(ticker_to_CIK_URL, headers=headers)
            soup = BeautifulSoup(response.content, "html5lib")
            txt_dirty = soup.get_text()
            # clean the data
            lines = [line.strip() for line in txt_dirty.split('\n')]
            lines = [line.strip() for line in txt_dirty.split()]
            ticker_cik_dict = dict(zip(lines[::2], lines[1::2]))
            # put it in a dataframe
            cik_ticker_df = pd.DataFrame(
                list(ticker_cik_dict.items()), columns=["Ticker", "CIK"])
            # sort the data frame
            cik_ticker_df = cik_ticker_df.sort_values("Ticker")
            cik_ticker_df = cik_ticker_df.reset_index(drop=True)
            # export it to excel
            cik_ticker_df.to_excel("./tickers.xlsx", index=False)
            # get the CIK number of the company
            cik_number_required = cik_ticker_df["CIK"].loc[cik_ticker_df["Ticker"]
                                                           == ticker].values
        except requests.exceptions.RequestException:
            print("Error: Unable to connect to https://www.sec.gov/include/ticker.txt.")
            return None
    # kinda self explanetory
    try:
        cik_number_required = cik_number_required[0]
        return cik_number_required
    except IndexError:
        print(f"Error: Ticker {ticker} not found.")
        return None

# add leading zeros to a CIK number


def addLeadingZeros(cik):
    """
    This function adds leading zeros to a CIK number until it has a length of 10
    """
    cik_str = str(cik)
    zeros_to_add = 10 - len(cik_str)
    cik_with_zeros = '0' * zeros_to_add + cik_str
    return cik_with_zeros

# calculate the growth rate between two values


def calculate_growth_rate(initial_value, final_value):
    """
    Calculates the growth rate between two values.
    Args:
        initial_value (float): The initial value.
        final_value (float): The final value.
    Returns:
        float: The growth rate as a percentage.
    """
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


def summarize_debt_quarterly(json_list, currency_list):
    # Create an instance of CurrencyRates
    c = CurrencyConverter()
    # Initialize the summary list
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
# summerise the data from the list of data of the companies from a certain subject (like gross profit, net income, etc.)


def create_1_dataframe_annual(df_list, column_list):
    # Create an empty DataFrame to store the combined data
    combined_df = pd.DataFrame(columns=column_list)

    for df in df_list:
        if 'frame' in df.columns:
            df = df.drop('frame', axis=1)
        if 'form' in df.columns:
            df = df[df['form'] != '10-K/A']
            df = df[df['form'] != '10-Q']
            df.reset_index(drop=True, inplace=True)
        if 'end' in df.columns:
            df['year'] = pd.to_datetime(df['end']).dt.year
            df['quarter'] = pd.to_datetime(df['end']).dt.quarter
        try:
            if 'equity' in df.columns:
                combined_df[['year', 'quarter', 'equity']
                            ] = df[['year', 'quarter', 'equity']]
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

    if combined_df.empty:
        return combined_df

    combined_df = combined_df.groupby(
        ['year', 'quarter'], as_index=False).sum()
    combined_df = combined_df.reset_index(drop=True)

    return combined_df


def create_1_dataframe_quarterly(df_list, column_list):
    # Create an empty DataFrame to store the combined data
    combined_df = pd.DataFrame(columns=column_list)

    for df in df_list:
        if 'frame' in df.columns:
            df = df.drop('frame', axis=1)
        if 'form' in df.columns:
            df = df[df['form'] != '10-K/A']
            df = df[df['form'] != '10-K']
            df.reset_index(drop=True, inplace=True)
        if 'end' in df.columns:
            df['year'] = pd.to_datetime(df['end']).dt.year
            df['quarter'] = pd.to_datetime(df['end']).dt.quarter

        try:
            if 'equity' in df.columns:
                combined_df[['year', 'quarter', 'equity']
                            ] = df[['year', 'quarter', 'equity']]
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

    if combined_df.empty:
        return combined_df

    combined_df = combined_df.groupby(
        ['year', 'quarter'], as_index=False).sum()
    combined_df = combined_df.reset_index(drop=True)

    return combined_df


def get_relevant_json_data(json_data):
   # getting the lists from the json file
    df_list = []
    # getting the values from the json file
    try:
        list_of_liabilities = json_data['facts']['us-gaap']['Liabilities']['units']['USD']
    except KeyError:
        list_of_liabilities = None  # or any other default value or error handling logic

    try:
        list_of_net_income = json_data['facts']['us-gaap']['NetIncomeLoss']['units']['USD']
    except KeyError:
        try:
            # or any other default value or error handling logic
            list_of_net_income = json_data['facts']['us-gaap']['ProfitLoss']['units']['USD']
        except:
            print("Error: Unable to find NetIncomeLoss or ProfitLoss.")
            list_of_net_income = None  # or any other default value or error handling logic
    try:
        list_of_gross_profit = json_data['facts']['us-gaap']['GrossProfit']['units']['USD']
    except KeyError:
        try:
            # or any other default value or error handling logic
            list_of_gross_profit = json_data['facts']['us-gaap']['IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest']['units']['USD']
        except KeyError:
            print("Error: Unable to find GrossProfit or IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest.")
            list_of_gross_profit = None  # or any other default value or error handling logic

    try:
        list_of_equity = json_data['facts']['us-gaap']['StockholdersEquity']['units']['USD']
    except KeyError:
        list_of_equity = None  # or any other default value or error handling logic

    try:
        list_of_long_term_debt = json_data['facts']['us-gaap']['OtherLiabilitiesNoncurrent']['units']['USD']
    except KeyError:
        try:
            # or any other default value or error handling logic
            list_of_long_term_debt = json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units']['USD']
        except:
            try:
                list_of_long_term_debt = json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units']['USD']
            except KeyError:
                try:
                    if len(list(json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units'].keys())) > 1:
                        print("speacial case: long term debt in multiple currencies")
                        currencies = list(
                            json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units'].keys())
                      #  print(json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units']['GBP'])
                        list_of_long_term_debt = [
                            json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units'][currencies[0]]]
                        list_of_long_term_debt.append(
                            json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units'][currencies[1]])
                        list_of_long_term_debt.append(
                            json_data['facts']['us-gaap']['DebtAndCapitalLeaseObligations']['units'][currencies[2]])
                        list_of_long_term_debt = summarize_debt_quarterly(
                            list_of_long_term_debt, currencies)
                except:
                    print("cant find long term debt please contact us.")
                    list_of_long_term_debt = None  # or any other default value or error handling

    try:
        list_of_eps = json_data['facts']['us-gaap']['EarningsPerShareDiluted']['units']['USD/shares']
    except KeyError:
        # handle the case where eps is stated other then the default value
        try:
            list_of_eps = json_data['facts']['us-gaap']['EarningsPerShareBasic']['units']['USD/shares']
        except KeyError:
            print("Error: Unable to find EarningsPerShare.")
            list_of_eps = None

    # turning the lists to dataframes
    df_gross_profit = pd.DataFrame(list_of_gross_profit)
    df_net_income = pd.DataFrame(list_of_net_income)
    df_long_term_debt = pd.DataFrame(list_of_long_term_debt)
    df_equity = pd.DataFrame(list_of_equity)
    df_eps = pd.DataFrame(list_of_eps)

    # renaming the val column to the meaning of the value
    df_equity.rename(columns={"val": 'equity'}, inplace=True)
    df_long_term_debt.rename(columns={'val': "long_term_debt"}, inplace=True)
    df_gross_profit.rename(columns={'val': 'gross_profit'}, inplace=True)
    df_net_income.rename(columns={'val': 'net_income'}, inplace=True)
    df_eps.rename(columns={'val': 'EPS'}, inplace=True)
    # adding the databases to make one list of databases
    df_list.append(df_net_income)
    df_list.append(df_gross_profit)
    df_list.append(df_long_term_debt)
    df_list.append(df_equity)
    df_list.append(df_eps)
    columns = ['year', 'quarter', 'net_income', 'equity',
               'gross_profit', 'long_term_debt', 'EPS']
    # calling the function to handle the list o databases
    mega_frame_quarters = create_1_dataframe_quarterly(
        df_list=df_list, column_list=columns)
    mega_frame_annual = create_1_dataframe_annual(
        df_list=df_list, column_list=columns)
    return [mega_frame_annual, mega_frame_quarters]


def get_Insider_Trades_Data(cik):
   # Create a Scrapy crawler process
    process = CrawlerProcess(get_project_settings())
    # Start the spider
    process.crawl(SecInsiderTradesSpider,cik=cik)
    links=process.start(stop_after_crawl=True)
   # process1=CrawlerProcess(get_project_settings())
   # process1.crawl(ProcessLinksSpider,links=links)
   
    
def get_Financial_Data_By_Ticker(ticker):
    cik = getCikNum(ticker=ticker, update_required=False)
    if cik is not None:
        company_insider_data = get_Insider_Trades_Data(cik=cik)
        cik = addLeadingZeros(cik=cik)
        company_facts = get_company_facts(cik=cik)
        data = get_relevant_json_data(company_facts)

        # return(data)

get_Insider_Trades_Data("1318605")
