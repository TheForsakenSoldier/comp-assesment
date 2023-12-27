# Import necessary libraries and functions
from dash import Dash, html, dcc, Input, Output, State, callback,dash_table
import pandas as pd
import plotly.express as px
from app import get_cik_num

# Initialize the Dash application
app = Dash(__name__,title="Financial Data analysis",assets_folder="./src")

# Define the layout of the Dash application
app.layout = html.Div([
 # Add an input field for the user to enter a ticker symbol
 dcc.Input(id="ticker-search", type="text"),
 # Add a button that the user can click to submit their ticker symbol
 html.Button('Search', id='submit-button'),
 # Add a header that will display the CIK number associated with the entered ticker symbol
 html.H1(id="header", children=""),
 # Add a div that will be used to display additional output
 html.Div(id="output"),
])

# Define a callback function that updates the header when the user clicks the Search button
@app.callback(
 # Specify that the callback function should update the "children" property of the "header" component
 Output("header", "children"),
 # Specify that the callback function should be triggered when the "n_clicks" property of the "submit-button" component changes
 Input("submit-button", "n_clicks"),
 # Specify that the callback function should receive the current value of the "ticker-search" component as an argument
 State("ticker-search", "value")
)
def update_header(n_clicks, value):
 # If the Search button hasn't been clicked yet, return an empty string
 if n_clicks is None:
    return ""
 else:
    # Otherwise, call the get_cik_num function with the entered ticker symbol and update the header with the returned CIK number
    results = get_cik_num(value,False)
    return f"CIK Number: {results}"

# Run the Dash application
if __name__ == '__main__': 
   app.run(debug=True)
