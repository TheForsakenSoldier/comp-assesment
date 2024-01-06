# Import necessary libraries and functions
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table
import pandas as pd
from dash.exceptions import PreventUpdate
import plotly.express as px
from app import get_financial_data_by_ticker # Importing a function to fetch financial data by ticker symbol

# Initialize the Dash application
app = Dash(__name__, title="Top Swan", assets_folder="./web/assets") # Setting up the Dash application with a title and specifying the folder for static files

# Define the layout of the Dash application
app.layout = html.Div([
 html.Div(className='pre-select-company', children=[ # Creating a div for pre-selection of company
   dcc.Input( id="ticker-search", type="text", placeholder="Enter Company Ticker Here"), # Text input field for entering company ticker
   html.Button("Search", id="submit-button", n_clicks=0) # Button to submit the entered ticker
 ]),
 html.Div(id='post-select-company-div', style={'display':'none'}, children=[ # Creating a hidden div for post-selection of company
   html.H1(id='post-select-company-title'), # Heading for the selected company
   html.Br(), # Line break
   dcc.Dropdown(multi=True, id='post-select-company-dropdown'), # Dropdown menu for selecting companies
   html.Br(), # Line break
   html.Button("Create Report", id="create-report-button", n_clicks=None) # Button to create a report
 ]),
 html.Div(className='main-data-div', style={'display':'none'}, children=[ # Creating a hidden div for displaying main data
     html.H1(id='main-data-title'), # Heading for the main data
     html.Br(), # Line break
     dash_table.DataTable(id='main-data-table') # Table for displaying the main data
 ])
])

@app.callback(
 Output('post-select-company-dropdown', 'options'),
 Input('submit-button', 'n_clicks'),
 State('ticker-search', 'value'))
def update_dropdown_options(n_clicks, ticker): 
 if n_clicks is None or n_clicks <= 0:
     raise PreventUpdate 
 else:
     df = get_financial_data_by_ticker(ticker=ticker) 
     if df is None:
         raise PreventUpdate 
     else:
         options = df['label'].unique() 
         return options 

@app.callback(
  Output('post-select-company-div', 'style'),
  Input('submit-button', 'n_clicks'),
  State('post-select-company-div', 'style'))
def show_div(n_clicks, style): # Function to show the div containing the dropdown after the search button is clicked
  if n_clicks >0:
      return {'display': 'block'} # If the search button is clicked, display the div
  else:
      return style # Otherwise, keep the current style of the div

# Run the Dash application
if __name__ == '__main__': 
 app.run(debug=True) # Start the Dash application in debug mode
