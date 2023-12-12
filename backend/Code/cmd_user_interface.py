import asyncio
import os

from app import (
    export_pandas_data,
    get_Financial_Data_By_Ticker,
    get_relevant_json_data_as_pandas,
)


async def main():
    while (True):
        ticker = input("Enter company ticker: (-1 to finish): \n")
        if (ticker == -1 or ticker == "-1"):
            break
        type_c = input(
            "Enter the type of the document q for quarterly and a for annual b for both: \n")
        directory = "Data"
        # creating the url to get

        isExistDir = os.path.isdir('./'+directory)
        # if the directory to hold the excel data dosent exist
        if (isExistDir == False):
            path = os.path.join('./', directory)
            os.mkdir(path)
         # creating the path for the json file and checking if it exists
        path = directory+'/'+ticker+'/'
        isExist = os.path.exists(path)
        if (isExist):
            company = get_relevant_json_data_as_pandas(ticker, path)
            print(company)
            print("--------------")
        else:
            # if the file dosent exist (meaning the company wasnt analysed before) add him and print it
            companies_data = get_Financial_Data_By_Ticker(ticker=ticker)
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
                os.makedirs(path)
                export_pandas_data(companies_data, path)

asyncio.run(main())
