# layouts.py
from dash import dash_table, dcc, html


def create_layout():
    return html.Div([
        html.Div(className='pre-select-company', children=[
            dcc.Input(id="ticker-search", type="text", placeholder="Enter Company Ticker Here"),
            html.Button("Search", id="submit-button", n_clicks=0)
        ]),
        html.Div(id='post-select-company-div', style={'display': 'none'}, children=[
            html.H1(id='post-select-company-title'),
            html.Br(),
            dcc.Dropdown(multi=True, id='post-select-company-dropdown'),
            html.Br(),
            html.Button("Create Report", id="create-report-button", n_clicks=None)
        ]),
        html.Div(id='main-data-div', style={'display': 'none'}, children=[
            html.H1(id='main-data-title'),
            html.Br(),
            dash_table.DataTable(id='main-data-table')
        ])
    ])
