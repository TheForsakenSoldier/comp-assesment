# callbacks.py
from dash.dependencies import Input, Output, State
import dash
import pandas as pd
from data_fetching_and_handeling import get_financial_data_by_ticker
def register_callbacks(app):
    @app.callback(
        Output('post-select-company-dropdown', 'options'),
        Input('submit-button', 'n_clicks'),
        State('ticker-search', 'value'), prevent_initial_call=True)
    def update_dropdown_options(n_clicks, ticker):
        if n_clicks is None or n_clicks <= 0:
            raise dash.exceptions.PreventUpdate
        else:
            ticker = ticker.lower()
            df = get_financial_data_by_ticker(ticker=ticker)
            if df is None:
                print("No data retrieved for ticker: ", ticker)
                raise dash.exceptions.PreventUpdate
            options = df.index.tolist()
            return [{'label': i, 'value': i} for i in options]

    @app.callback(
        Output('post-select-company-div', 'style'),
        Input('submit-button', 'n_clicks'),
        State('post-select-company-div', 'style'))
    def show_div(n_clicks, style):
        if n_clicks > 0:
            return {'display': 'block'}
        else:
            return style

    @app.callback(
        [Output('main-data-table', 'data'),
         Output('main-data-div', 'style')],
        Input('create-report-button', 'n_clicks'),
        State('post-select-company-dropdown', 'value'),
        State('ticker-search', 'value'))
    def update_table(n_clicks, selected_options, value):
        if n_clicks is not None:
            df = get_financial_data_by_ticker(value)
            if df is None or df.empty:
                print(f"No data retrieved for ticker: {value}")
                return [], {'display': 'none'}
            
            list_of_dataframes = df.loc[df.index.isin(selected_options)]
            if list_of_dataframes.empty:
                print("No matching data found for the selected options.")
                return [], {'display': 'none'}
            
            # Assuming fetch_and_process_data is defined elsewhere
            data_summary_list = fetch_and_process_data(value, selected_options)
            if not data_summary_list:
                return [], {'display': 'none'}
            else:
                return data_summary_list, {'display': 'block'}
        else:
            raise dash.exceptions.PreventUpdate
def fetch_and_process_data(ticker, selected_options):
    """
    Fetches financial data for the given ticker and processes it based on the selected options.
    Returns a list of dictionaries suitable for the Dash table, or an empty list if an error occurs.
    """
    try:
        # Fetch financial data by ticker
        df = get_financial_data_by_ticker(ticker)
        if df is None or df.empty:
            print(f"No data retrieved for ticker: {ticker}")
            return []
        
        # Filter the data based on selected options
        list_of_dataframes = df.loc[df.index.isin(selected_options)]
        if list_of_dataframes.empty:
            print("No matching data found for the selected options.")
            return []
        
        # Initialize an empty DataFrame to hold the data summary
        data_summary = pd.DataFrame(columns=['fy', 'fp'])
        
        for i, option in enumerate(selected_options):
            current_df = pd.DataFrame.from_dict(list_of_dataframes.at[option, "units"])
            current_df = current_df[['fy', 'fp','form', 'val']]
            current_df.rename(columns={'val': option}, inplace=True)
            current_df.columns = [f'{col}_{i}' if col in ['fy', 'fp'] else col for col in current_df.columns]
            
            if data_summary.empty:
                data_summary = current_df
            else:
                data_summary = pd.concat([data_summary, current_df], axis=1)
        
        # Sort the DataFrame by 'fy' and 'fp'
        data_summary.sort_values(by=['fy_0', 'fp_0'], inplace=True)
        
        # Convert the DataFrame to a list of dictionaries for the Dash table
        return data_summary.to_dict(orient='records')
    except Exception as e:
        print(f"Error processing data: {e}")
        return []
