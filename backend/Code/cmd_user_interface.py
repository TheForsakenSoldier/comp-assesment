import asyncio
from pathlib import Path

from app import (
    export_pandas_data,
    get_financial_data_by_ticker,
    get_local_json_data_as_pandas,
)


async def main():
    while (True):
        ticker = input("Enter company ticker: (-1 to finish): \n")
        if (ticker == str(-1)):
            break

        directory = Path("Data")
        # creating the url to get
        isExistDir = directory.is_dir()
        # if the directory to hold the excel data dosent exist
        if (not isExistDir):
            directory.mkdir()
         # creating the path for the json file and checking if it exists
        path = directory / ticker

        if_path_exists = path.exists()
        if (if_path_exists and ticker != None):
            type_c = input(
                "\n (annual/quarterly/both) type (a/q/b) respectively to receive the data you want \n")
            if type_c == 'a':
                company = get_local_json_data_as_pandas(
                    path / 'annual.json', type_c)
            if type_c == 'q':
                company = get_local_json_data_as_pandas(
                    path / 'quarterly.json', type_c)
            if type_c == 'b':
                company = [get_local_json_data_as_pandas(
                    path / 'quarterly.json', 'a'), get_local_json_data_as_pandas(path / 'annual.json', 'q')]
            print(type(company))
            if str(type(company)) != '<class list>':
                print(company)
                print("--------------")
            else:
                for data in company:
                    print('\n'+data)
                    print("--------------")

        elif not ticker:
            # if the file dosent exist (meaning the company wasnt analysed before) add him and print it
            companies_data = await get_financial_data_by_ticker(ticker=ticker)
            if (companies_data == "None Existant ticker symbol"):
                print("Could not find The comapny ticker, did you write it correctly?")
            else:
                type_c = input(
                    "\n (annual/quarterly/both) type (a/q/b) respectively to receive the data you want \n")
                if (type_c == "q"):
                    print(companies_data[1])
                elif (type_c == "a"):
                    print(companies_data[0])
                elif (type_c == "b"):
                    print(companies_data[0])
                    print("----------------------------------------------------")
                    print(companies_data[1])
                type_c = input(
                    "Would you like to export the data for this company so i will work faster next time ? (y/n): ")
                if (type_c == "y"):
                    path.mkdir(parents=True, exist_ok=True)
                    export_pandas_data(companies_data, path)
        else:
            print("Could not find The comapny ticker, did you write it correctly?")
asyncio.run(main())
