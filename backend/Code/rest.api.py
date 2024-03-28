# Import necessary libraries and functions
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table
import pandas as pd
import json
from pandasgui import show
from dash.exceptions import PreventUpdate
import plotly.express as px
# Importing a function to fetch financial data by ticker symbol
from app import get_financial_data_by_ticker

# Initialize the Dash application
# Setting up the Dash application with a title and specifying the folder for static files
app = Dash(__name__, title="Top Swan", assets_folder="./web/assets")

# Define the layout of the Dash application
app.layout = html.Div([
    html.Div(className='pre-select-company', children=[  # Creating a div for pre-selection of company
        # Text input field for entering company ticker
        dcc.Input(id="ticker-search", type="text",
                  placeholder="Enter Company Ticker Here"),
        # Button to submit the entered ticker
        html.Button("Search", id="submit-button", n_clicks=0)
    ]),
    html.Div(id='post-select-company-div', style={'display': 'none'}, children=[  # Creating a hidden div for post-selection of company
        # Heading for the selected company
        html.H1(id='post-select-company-title'),
        html.Br(),  # Line break
        # Dropdown menu for selecting companies
        dcc.Dropdown(multi=True, id='post-select-company-dropdown'),
        html.Br(),  # Line break
        html.Button("Create Report", id="create-report-button",
                    n_clicks=None)  # Button to create a report
    ]),
    html.Div(className='main-data-div', style={'display': 'none'}, children=[  # Creating a hidden div for displaying main data
        html.H1(id='main-data-title'),  # Heading for the main data
        html.Br(),  # Line break
        # Table for displaying the main data
        dash_table.DataTable(id='main-data-table')
    ])
])

# Callback function to update the dropdown options when the search button is clicked


@app.callback(
    Output('post-select-company-dropdown', 'options'),
    Input('submit-button', 'n_clicks'),
    State('ticker-search', 'value'), prevent_initial_call=True)
def update_dropdown_options(n_clicks, ticker):
    if n_clicks is None or n_clicks <= 0:
        raise PreventUpdate
    else:
        ticker = ticker.lower()
        df = get_financial_data_by_ticker(ticker=ticker)
        dcc.Store(id="user-ticker", data=ticker)
        if df is None:
            print("No data retrieved for ticker: ", ticker)
            raise PreventUpdate
        options = df.index
        return options

# Callback function to show the div containing the dropdown after the search button is clicked


@app.callback(
    Output('post-select-company-div', 'style'),
    Input('submit-button', 'n_clicks'),
    State('post-select-company-div', 'style'))
def show_div(n_clicks, style):
    if n_clicks > 0:
        # If the search button is clicked, display the div
        return {'display': 'block'}
    else:
        return style  # Otherwise, keep the current style of the div

# Callback function to update the table after the create report button is clicked


@app.callback(
    Output('main-data-table', 'data'),
    Input('create-report-button', 'n_clicks'),
    State('post-select-company-dropdown', 'value'),
    State('ticker-search', 'value')
)

def update_table(n_clicks, selected_options, value):
    if n_clicks is not None:
        df = get_financial_data_by_ticker(value)
        list_of_dataframes = df.loc[df.index.isin(selected_options)]
        data_summary = []
        for i in range(0, len(list_of_dataframes), 1):
            current_df = pd.DataFrame.from_dict(
                list_of_dataframes.at[selected_options[i], "units"])
            current_df = current_df[['fy', 'fp', 'form', 'val']]
            data_summary[selected_options[i]].append(current_df.to_dict()) 
       # data_summary = pd.DataFrame.from_dict(data_summary, orient='index')
        dcc.Store(id="selected_company_data", data=data_summary)
        # Convert the summary dictionary to a list of dictionaries

        return data_summary#.to_dict('records')
    else:
        PreventUpdate


# Run the Dash application in debug mode
if __name__ == '__main__':
    app.run(debug=True)
