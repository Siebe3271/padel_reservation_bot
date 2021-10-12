#pip install dash
#pip install dash_core_components
#pip install dash_html_components
#pip install plotly.express

import io
import os
import dash  #(version 1.12.0)
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from dash.exceptions import PreventUpdate
from dash_extensions import Download
from flask import Flask

server = Flask(__name__)
app = dash.Dash(server=server)

os.chdir('c:\\Users\\sgodts\\Documents\\Personal Projects\\Part Time Larry')

# Import the cleaned data (importing csv into pandas)
df = pd.read_excel('reservations.xlsx', index_col=0)

# App layout
app = dash.Dash(__name__, prevent_initial_callbacks=True) # this was introduced in Dash version 1.12.0

# Sorting operators (https://dash.plotly.com/datatable/filtering)
app.layout = html.Div([
    
    html.Div(
                [   html.H1(children='Tennis Vlaanderen Automatic Reservation System'),
                    Download(id="download"),
                    html.Button("Update",
                                id="save-button"),
                    html.Div("Press button to update data to scheduling assistent.",
                             id="output-2"),
                    dash_table.DataTable(
                        id='datatable-interactivity',
                        columns=[
                            {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
                            if i == "iso_alpha3" or i == "year" or i == "id"
                            else {"name": i, "id": i, "deletable": True, "selectable": True}
                            for i in df.columns
                        ],
                        data=df.to_dict('records'),  # the contents of the table
                        editable=True,              # allow editing of data inside all cells
                        filter_action="native",     # allow filtering of data by user ('native') or not ('none')
                        sort_action="native",       # enables data to be sorted per-column by user or not ('none')
                        sort_mode="single",         # sort across 'multi' or 'single' columns
                        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                        row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                        row_deletable=True,         # choose if user can delete a row (True) or not (False)
                        selected_columns=[],        # ids of columns that user selects
                        selected_rows=[],           # indices of rows that user selects
                        page_action="native",       # all data is passed to the table up-front or not ('none')
                        page_current=0,             # page number that user is on
                        page_size=6,                # number of rows visible per page
                        style_cell={                # ensure adequate header width when text is shorter than cell's text
                            'minWidth': 95, 'maxWidth': 95, 'width': 95
                        },
                        style_cell_conditional=[    # align text columns to left. By default they are aligned to right
                            {
                                'if': {'column_id': c},
                                'textAlign': 'left'
                            } for c in ['country', 'iso_alpha3']
                        ],
                        style_data={                # overflow cells' content into multiple lines
                            'whiteSpace': 'normal',
                            'height': 'auto'
                        }
                    )

                    ]
            )
    
                    ])


# -------------------------------------------------------------------------------------
@app.callback(
    Output("download", "data"),
    Input("save-button", "n_clicks"),
    State("datatable-interactivity", "data"))
    
def download_as_csv(n_clicks, table_data):
    df = pd.DataFrame.from_dict(table_data)
    if not n_clicks:
      raise PreventUpdate
    download_buffer = io.StringIO()
    df.to_csv(download_buffer, index=False)
    download_buffer.seek(0)
    df.to_excel("reservations.xlsx", index = True, index_label = 'Reservation', columns = ['Date','StartHour', 'EndHour', 'Player1', 'Player2', 'Player3', 'Recurring', 'ReservationPossible'])
    return dict(content=download_buffer.getvalue(), filename="upcoming_reservations_copy.csv")

# -------------------------------------------------------------------------------------


if __name__ == '__main__':
    #host='127.0.0.1', port=8050, 
    app.run_server(debug=False)