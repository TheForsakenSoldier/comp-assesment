# Import necessary libraries and functions
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table
import pandas as pd
import json
from pandasgui import show
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

# Callback function to update the dropdown options when the search button is clicked
@app.callback(
 Output('post-select-company-dropdown', 'options'),
 Input('submit-button', 'n_clicks'),
 State('ticker-search', 'value'),prevent_initial_call=True)
def update_dropdown_options(n_clicks, ticker): 
 if n_clicks is None or n_clicks <= 0:
   raise PreventUpdate 
 else:
   ticker=ticker.lower()
   df = get_financial_data_by_ticker(ticker=ticker) 
   dcc.Store(id="user-ticker",data=ticker)
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
 if n_clicks >0:
     return {'display': 'block'} # If the search button is clicked, display the div
 else:
     return style # Otherwise, keep the current style of the div

# Callback function to update the table after the create report button is clicked
@app.callback(
 Output('main-data-table', 'data'),
 Input('create-report-button', 'n_clicks'),
 State('post-select-company-dropdown', 'value'),
 State('ticker-search', 'value')
)
def update_table(n_clicks, selected_options, value): 
 if n_clicks is not None :
   df = get_financial_data_by_ticker(value)
   list_of_dataframes = df.loc[df.index.isin(selected_options)]
   json_data_df_summary = {}
   for i in range(0, len(list_of_dataframes),1):
     current_df=pd.DataFrame.from_dict(list_of_dataframes.at[selected_options[i],"units"])
     current_df=current_df['fy','fp','form','val']
     json_data_df_summary[selected_options[i]].append(current_df)
   return

# Run the Dash application in debug mode
if __name__ == '__main__': 
 app.run(debug=True) 
