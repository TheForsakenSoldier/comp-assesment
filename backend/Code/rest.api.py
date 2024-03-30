# app.py or rest.api.py (whichever you prefer as the main entry point)
from dash import Dash
from layouts import create_layout
from callbacks import register_callbacks

app = Dash(__name__, title="Top Swan", assets_folder="./web/assets")

# Set the layout of the Dash application
app.layout = create_layout()

# Register callbacks
register_callbacks(app)

# Run the Dash application
if __name__ == '__main__':
    app.run_server(debug=True)
