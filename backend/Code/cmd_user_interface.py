import os
import asyncio
from app import get_Financial_Data_By_Ticker,importExcelComp
async def main():
   while(True):
      ticker=input("Enter company ticker: (-1 to finish): \n")
      if(ticker==-1 or ticker =="-1"):
         break
      type_c=input("Enter the type of the document q for quarterly and a for annual b for both: \n")
      directory="companies_data"
      #creating the url to get
   
      isExistDir=os.path.isdir('./'+directory)
      #if the directory to hold the excel data dosent exist
      if(isExistDir==False):
         path=os.path.join('./',directory)
         os.mkdir(path)
   #creating the path for the excel file and checking if it exists
      path=directory+'/'+ticker+".xlsx"
      isExist=os.path.exists(path)
      if(isExist):
         company=importExcelComp(ticker)
         print(company)
         print("--------------")
      else:
      #if the file dosent exist (meaning the company wasent analized before) add him and print it
         companies_data=get_Financial_Data_By_Ticker(ticker=ticker)
         if(type_c=="q"):
            print(companies_data[1])
         elif(type_c=="a"):
            print(companies_data[0])
         elif(type_c=="b"):
            print(companies_data[0])
            print("----------------------------------------------------")
            print(companies_data[1])
asyncio.run(main())