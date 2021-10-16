import io
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
import pause
import datetime
import schedule
import pause, schedule
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime

# server = Flask(__name__)
# app = dash.Dash(server=server)
scheduler = schedule.Scheduler()

#Reservation function via Selenium
def make_reservation(Date, startuur, einduur, player1, player2, player3, field):
    #Launch Browser and go to Tennis Vlaanderen
    driver = webdriver.Chrome(executable_path=r"/usr/bin/chromedriver.exe")
    driver.get('https://www.tennisvlaanderen.be/zoek-een-terrein')
    time.sleep(3)
    
    #Accept Cookies
    cookiesbutton = driver.find_element_by_xpath('/html/body/div[1]/div/a')
    cookiesbutton.click()

    #Login
    user = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/div[2]/div[1]/div/div[2]/div[2]/div[2]/form/fieldset/div/span[1]/span/span/input')
    user.send_keys("siebegodts@hotmail.com")
    passw = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/div[2]/div[1]/div/div[2]/div[2]/div[2]/form/fieldset/div/span[2]/span/span/input')
    passw.send_keys('Siebeforlife1,')

    loginbutton = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/div[2]/div[1]/div/div[2]/div[2]/div[2]/form/div/span').click()
    time.sleep(2)
    
    #Fill in reservation date and select field
    if field == 1:
        terrainid = 6503330
    elif field == 2:
        terrainid = 6503331
    elif field == 3:
        terrainid = 6503332
    elif field == 4:
        terrainid = 8294020
    elif field == 5:
        terrainid = 8294021
    
    webaddress = f"https://www.tennisvlaanderen.be/reservatie?clubId=2253&terrainId={terrainid}&reservationDate={Date}&startHour={startuur}&endHour={einduur}&returnUrl=%2Freserveer-een-terrein%3FclubId%3D2253%26planningDay%={Date}%26terrainGroupId%3D4706%26ownClub%3Dtrue%26clubCourts%5B0%5D%3DI%26clubCourts%5B1%5D%3DO"
    driver.get(webaddress)
    time.sleep(2)
    #Hier nog voor error zoeken, als er 'binnen de opgegeven uren bestaat er al ..' staat dan verder loopen
    
    #Add 3 Players
    add_button = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/form/div/div[2]/div/div/div[2]/div/div/span/div[1]/span/div/div[1]/a/i')
    add_button.click()
    time.sleep(1)

    text_player1 = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/form/div/div[2]/div/div/div[2]/div/div/span/div[1]/span/div[2]/div[2]/div[2]/div/div[1]/span/input[1]')
    text_player1.send_keys(player1)
    time.sleep(2)
    text_player1.send_keys(Keys.ENTER)

    add_button = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/form/div/div[2]/div/div/div[2]/div/div/span/div[1]/span/div[2]/div[1]/a[2]/i')
    add_button.click()
    time.sleep(1)

    text_player2 = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/form/div/div[2]/div/div/div[2]/div/div/span/div[1]/span/div[3]/div[2]/div[2]/div/div[1]/span/input[1]')
    text_player2.send_keys(player2)
    time.sleep(2)
    text_player2.send_keys(Keys.ENTER)

    add_button = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/form/div/div[2]/div/div/div[2]/div/div/span/div[1]/span/div[3]/div[1]/a[2]/i')
    add_button.click()
    time.sleep(1)

    text_player3 = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/form/div/div[2]/div/div/div[2]/div/div/span/div[1]/span/div[4]/div[2]/div[2]/div/div[1]/span/input[1]')
    text_player3.send_keys(player3)
    time.sleep(2)
    text_player3.send_keys(Keys.ENTER)
    time.sleep(2)

    #Make Reservation
    reservation_possible = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/form/div/div[2]/div/div/div[4]/input').is_enabled()
    if reservation_possible:
        reserve_button = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/form/div/div[2]/div/div/div[4]/input')
        reserve_button.click()
        print(f"Reservation Successful for {player1}, {player2}, {player3}!")
        message = (f"Reservation Successful for {player1}, {player2}, {player3}!")
    else:
        message = "Reservation Failed: "
        error_message = driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div/div/div/div/form/div/div[2]/div/div/span/ul')
        for mess in error_message:
            print(mess.text)
            message += mess.text
    
    return message

def update_schedule(df):
    #Execute or schedule reservation
    try:
        date = datetime.datetime(int(df[0][6:11]),int(df[0][3:5]),int(df[0][0:2]),int(df[1][0:2]),int(df[2][3:5]))
        reserve_date = (datetime.datetime(int(df[0][6:11]),int(df[0][3:5]),int(df[0][0:2])-7,int(df[1][0:2])-12,int(df[1][3:5])))

        #Check if reservation can be made, else wait
        if datetime.datetime.today() > reserve_date:
            print(f'Reservation is in less than 7 days and 12 hours, a reservation attempt will be made ...')
            message = make_reservation(df[0], df[1], df[2], df[3],df[4],df[5],df[6])
            scheduler.every(10).minutes.do(make_reservation,df[0], df[1], df[2], df[3],df[4],df[5],df[6])
        else:
            print(f'Reservation is more than 7 days and 12 hours away, a timer will be set to make the reservation at {reserve_date}!')
            scheduler.every(1).minutes.do(make_reservation,df[0], df[1], df[2], df[3],df[4],df[5],df[6])
            message = "scheduler 1st obs set"  
    except Exception as e: 
        message = (f'Wrong input: {e}')

    return message

# Import the cleaned data (importing csv into pandas)
# df = pd.read_excel('reservations.xlsx', index_col=0)
cols = [
    {"id": 0, "name": "Date"},
    {"id": 1, "name": "StartHour"},
    {"id": 2, "name": "EndHour"},
    {"id": 3, "name": "Player1"},
    {"id": 4, "name": "Player2"},
    {"id": 5, "name": "Player3"},
    {"id": 6, "name": "Field"},
    {"id": 7, "name": "Recurring"}]

colnames = ['Date','StartHour','Endhour','Player1','Player2','Player3','Field','Recurring']

# App layout
app = dash.Dash(__name__, prevent_initial_callbacks=True) # this was introduced in Dash version 1.12.0
app.title = 'Padel is Life!'


# Sorting operators (https://dash.plotly.com/datatable/filtering)
app.layout = html.Div([
    
    html.Div(
                [   html.Div(style={'backgroundColor':'#007eff'}),
                    html.H1(children='Tennis Vlaanderen Automatic Reservation System', style = {'textAlign': 'center', 'color':'#7FDBFF'}, id = 'output-1'),
                    Download(id="download"),
                    html.P(id='placeholder'),
                    html.Button("Load Data", style = {'textAlign': 'center'},
                                id="update-button"), 
                    html.Button("Save Data", style = {'textAlign': 'center'},
                                id="save-button"),
                    html.Button("Schedule", style = {'textAlign': 'center'},
                                id="schedule-button"),                 
                    html.Div("Don't forget to save your data before pressing schedule!",
                             id="output-2"), 
#                    html.Div(html.P([html.Br()])),
                 
                    dash_table.DataTable(
                        id='datatable-interactivity',
                        columns=[
                            {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
                            if i == "iso_alpha3" or i == "year" or i == "id"
                            else {"name": i, "id": i, "deletable": True, "selectable": True}
                            for i in colnames #df.columns
                        ],
                        data=[],#df.to_dict('records'),  # the contents of the table
                        editable=True,              # allow editing of data inside all cells
                        filter_action="native",     # allow filtering of data by user ('native') or not ('none')
                        sort_action="custom",       # enables data to be sorted per-column by user or not ('none')
                        sort_mode="single",         # sort across 'multi' or 'single' columns
                        sort_by = [{'column_id': colnames[0]}],
                        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                        row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                        row_deletable=True,         # choose if user can delete a row (True) or not (False)
                        selected_columns=[],        # ids of columns that user selects
                        selected_rows=[],           # indices of rows that user selects
                        page_action="native",       # all data is passed to the table up-front or not ('none')
                        page_current=0,             # page number that user is on
                        persistence = True,
                        persistence_type='local',
                        persisted_props='data',
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
                    ),
                     dash_table.DataTable(
                        id='table',
                        data=[]),
                     html.Div(html.P([html.Br()])),
                     html.Div(id="schedule-status")
                 

                    ]
            )
    
                    ])


# -------------------------------------------------------------------------------------
@app.callback(
    [Output("datatable-interactivity", "data"), Output('datatable-interactivity', 'columns')],
    [Input("update-button", "n_clicks")])
def updateTable(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    df = pd.read_excel('reservations.xlsx', index_col=0)
    return df.values[0:2], cols

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
    df.to_excel("reservations.xlsx", index = True, index_label = 'Reservation')
    return dict(content=download_buffer.getvalue(), filename="upcoming_reservations_copy.csv")

@app.callback(
    [Output("schedule-status", component_property='children')],
    [Input("schedule-button", "n_clicks")])
def schedule_reservation(n_clicks):
    if n_clicks is None:
        raise PreventUpdate        
    df = pd.read_excel('reservations.xlsx', index_col=0)
    for index, row in df.iterrows():
        output = update_schedule(df.values[index])
        print(output)

    return [f'Output: {output}']
     
    
# -------------------------------------------------------------------------------------
if __name__ == '__main__':
    #host='127.0.0.1', port=8050, 
    app.run_server(debug=False)
    while True:
        scheduler.run_pending()
        time.sleep(1)
