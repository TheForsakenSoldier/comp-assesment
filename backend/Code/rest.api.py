# Import necessary libraries and functions
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table
import pandas as pd
from dash.exceptions import PreventUpdate
import plotly.express as px
from app import get_financial_data_by_ticker

# Initialize the Dash application
app = Dash(__name__, title="Financial Data analysis", assets_folder="./src")

# Define the layout of the Dash application
app.layout = html.Div([
  html.Div(className='pre-select-company', children=[
    dcc.Input( id="ticker-search", type="text", placeholder="Enter Company Ticker Here"),
    html.Button("Search", id="submit-button", n_clicks=None)
  ]),
  html.Div(id='post-select-company-div', style={'display':'none'}, children=[
    html.H1(id='post-select-company-title'),
    html.Br(),
    dcc.Dropdown(multi=True, id='post-select-company-dropdown')
  ])
])

@app.callback(
   Output('post-select-company-dropdown', 'options'),
   Input('ticker-search', 'value'))
def update_dropdown_options(ticker):
   if ticker is None:
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
def show_div(n_clicks, style):
   if n_clicks is not None:
       return {'display': 'block'}
   else:
       return style


# Run the Dash application
if __name__ == '__main__': 
  app.run(debug=True)
