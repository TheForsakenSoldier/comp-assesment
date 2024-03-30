# Import necessary components from Dash
from dash import dash_table, dcc, html


def create_layout():
    # Define the layout of the Dash application
    return html.Div([
        # Div for the company selection input and search button
        html.Div(className='pre-select-company', children=[
            # Input field for entering the company ticker
            dcc.Input(id="ticker-search", type="text",
                      placeholder="Enter Company Ticker Here"),
            # Button to submit the search
            html.Button("Search", id="submit-button", n_clicks=0)
        ]),
        # Div for displaying the company selection dropdown and report creation button
        # Initially hidden (display: 'none')
        html.Div(id='post-select-company-div', style={'display': 'none'}, children=[
            # Title for the company selection section
            html.H1(id='post-select-company-title'),
            html.Br(),  # Line break
            # Dropdown for selecting the company data
            dcc.Dropdown(multi=True, id='post-select-company-dropdown'),
            html.Br(),  # Line break
            # Button to create a report based on the selected data
            html.Button("Create Report",
                        id="create-report-button", n_clicks=None)
        ]),
        # Div for displaying the main data table
        # Initially hidden (display: 'none')
        html.Div(id='main-data-div', style={'display': 'none'}, children=[
            # Title for the main data section
            html.H1(id='main-data-title'),
            html.Br(),  # Line break
            # DataTable component for displaying the financial data
            dash_table.DataTable(id='main-data-table')
        ])
    ])
