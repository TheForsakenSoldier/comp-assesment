# Project: TheForsakenSoldier/comp-assesment

Welcome to the repository for the comp-assesment project! This project is a comprehensive assessment tool designed to provide a financial outlook over a company based on a specific ticker. It is designed to be a friendly and informative resource for anyone interested in understanding the financial health of a company.

## Project Structure

- `backend/Code/data`: Contains the data of the companies that you look for.
- `backend/Code/web`: Contains the resources for the web application (so far just two images).
- `backend/Code`: This directory contains the main project that I worked on. Two files are the main "brains" of the project, `app.py` and `rest.api.py`.

## How to Run the Project

To run the project, you should navigate to the `backend/Code` directory and execute the `rest.api.py` script. This script is responsible for activating the main project and enabling all its functionalities. It will create a web app at https://127.0.0.1:8050. It doesn't do much yet, but soon there will be many functionalities in it.

## Documentation

### Data Fetching and Handling Module

This module contains functions for fetching financial data from the SEC's API, processing the data, and saving it locally. Key functions include:

- `get_cik_num(ticker, update_required)`: Fetches the CIK (Central Index Key) number for a given ticker symbol.
- `add_leading_zeros(cik)`: Adds leading zeros to a CIK number to ensure it is 10 digits long. (for the sec website)
- `get_company_facts(cik)`: Fetches company facts from the SEC's API using the CIK number.
- `turn_into_pandas(dictionary)`: Converts a dictionary of lists into a pandas DataFrame.
- `insert_spaces(s)`: Inserts spaces before uppercase characters in a string, improving readability.
- `export_local_data(data_frame, ticker)`: Exports a DataFrame to a local JSON file.
- `import_local_data_by_ticker(ticker)`: Imports data from a local JSON file based on the ticker symbol.
- `select_df_data_by_list(dataframe, list_of_values)`: Selects data from a DataFrame based on a list of values.
- `get_financial_data_by_ticker(ticker)`: Fetches financial data for a given ticker symbol, processes it, and returns it as a DataFrame.

### Dash Application Setup

The Dash application is initialized in `rest.api.py`, setting up the layout and registering callbacks.

### Layouts

Defined in `layouts.py`, the layout includes input fields for searching by ticker symbol, dropdowns for selecting company data, and a table for displaying the financial data.

### Callbacks

Defined in `callbacks.py`, the callbacks handle user interactions, such as searching for a company by ticker symbol and creating a report based on selected data.

## Contributing

Contributions to this project are welcome! If you have any suggestions or improvements, please feel free to open an issue or submit a pull request.

## License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).

## Contact

If you have any questions or need further clarification, please feel free to contact me.
