from inspect import FullArgSpec
import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from random import randint

PORT = 8050
external_stylesheets = [dbc.themes.BOOTSTRAP]

# Creating app

app = dash.Dash(external_stylesheets=external_stylesheets)
# Associating server
server = app.server
app.title = "Activity tracker"
app.config.suppress_callback_exceptions = True

df_dates = pd.read_csv("days.csv", delimiter=";", names=["day_id", "date"])
header = ["day_id", "time", "name", "track_id", "activity"]
df = pd.read_csv("activities.csv", delimiter=";", names=header)
df = pd.merge(df, df_dates, how="left", on="day_id")
df["date_time"] = df["time"] + " " + df["date"]
df_activity = df["activity"].str.split(";", expand = True)
df["top-1"] = df_activity[0]
df["top-2"] = df_activity[1]
df["power"] = 1 if len(df["top-1"]) != 0 else 0
df["delta"] = 13


app.layout = html.Div(
    [html.H1("Daily activity tracker",
     ),
     
    dcc.Markdown("""*Select the tracking-id (person name),
                 the prediction level (top-1 & top-2) and 
                 the desired time period to filter data.*
         """
     ),
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.P('Track id', style={"height": "auto", 
                                                  "margin-bottom": "auto",
                                                  "font-weight": "bold"}
                        ),
                        dcc.Dropdown(
                            id='dropdown_1',
                            options=[{'label': i, 'value': i} for i in df["track_id"].unique()],
                            placeholder="Select track id",
                            multi=False,
                            value=1,
                            style={'height': '30px', 'width': '200px'}
                        ),
                    ]
                )
            ),
            dbc.Col(
                html.Div(
                    [
                        html.P('Predictions', style={"height": "auto",
                                                     "margin-bottom": "auto",
                                                     "font-weight": "bold"}
                        ),
                        dcc.Dropdown(
                            id='dropdown_2',
                            options=[{'label': i, 'value': i} for i in ["top-1", "top-2"]],
                            placeholder="Select top predictions",
                            multi=False,
                            value="top-1",
                            style={'height': '30px', 'width': '200px'}
                        )
                    ]
                )
            ),
            dbc.Col(
                html.Div(
                    [
                        html.P('Date from', style={"height": "auto", 
                                                   "margin-bottom": "auto",
                                                   "font-weight": "bold"}
                        ),
                        dcc.Input(
                            id="date_from",
                            type="text",
                            placeholder="Example: 2020-12-1",
                            style={'height': '38px', 'width': '200px'}
                        ),
                    ]
                ),
            ),
            dbc.Col(
                html.Div(
                    [
                        html.P('Date to', style={"height": "auto",
                                                 "margin-bottom": "auto",
                                                 "font-weight": "bold"}
                        ),
                        dcc.Input(
                            id="date_to",
                            type="text",
                            placeholder="Example: 2020-12-12",
                            style={'height': '38px', 'width': '200px'}
                        ),
                    ]
                )
            ),
            dbc.Col(
                html.Div(
                    [
                        html.P('Time from', style={"height": "auto",
                                                   "margin-bottom": "auto",
                                                  "font-weight": "bold"}
                        ),
                        dcc.Input(
                            id="time_from",
                            type="text",
                            placeholder="Example: 17:00:00",
                            style={'height': '38px', 'width': '200px'}
                        ),
                    ]
                )
            ),
            dbc.Col(
                html.Div(
                    [
                        html.P('Time to', style={"height": "auto",
                                                 "margin-bottom": "auto",
                                                  "font-weight": "bold"}
                        ),
                        dcc.Input(
                            id="time_to",
                            type="text",
                            placeholder="Example: 18:00:00",
                            style={'height': '38px', 'width': '200px'}
                        ),
                    ]
                )
            ),

        ]
    ),
    dbc.Row(
        [
            dbc.Col(html.Div("The predictions were made at each time stamps")),
            dbc.Col(html.Div("The approximate amount of minutes has spent on activities by a selected person over the selected period"))
        ]
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    dcc.Graph(id='timeseries_graph_1')
                ], style={'width': '50vh'}
            ),
            dbc.Col(
                [
                    dcc.Graph(id='timeseries_graph_2')
                ], style={'width': '50vh'}
            ),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(html.Div("The total number of minutes were spent on paticulart activity by all detected people")),
            dbc.Col(html.Div("The approximate amount of minutes was spent on activities by each person"))
        ]
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    dcc.Graph(id='timeseries_graph_3')
                ], style={'width': '50vh'}
            ),
            dbc.Col(
                [
                    dcc.Graph(id='timeseries_graph_4')
                ], style={'width': '50vh'}
            )
        ]
    ),
    ]
)

@app.callback(
    dash.dependencies.Output('timeseries_graph_1', 'figure'),
    [dash.dependencies.Input('dropdown_1', 'value'),
     dash.dependencies.Input('dropdown_2', 'value'),
     dash.dependencies.Input('date_from', 'value'),
     dash.dependencies.Input('date_to', 'value'),
     dash.dependencies.Input('time_from', 'value'),
     dash.dependencies.Input('time_to', 'value')])
def update_graph(value1, value2, date_from, date_to, time_from, time_to):
    if date_from is not None:
        date_from = date_from
    else:
        date_from = "2020-12-01"
    if date_to is not None:
       date_to = date_to
    else:
        date_to = "2020-12-31"
    if time_from is not None:
        time_from = time_from
    else:
        time_from = "07:00:00"
    if time_to is not None:
        time_to = time_to
    else:
        time_to = "23:00:00"
    dff = df[df["date"] >= date_from]
    dff = dff[dff["date"] <= date_to]
    dff = dff[dff["time"] >= time_from]
    dff = dff[dff["time"] <= time_to]
    dff1 = dff[dff["track_id"] == value1]
    try:
        fig = px.bar(dff1, x="date_time", y="power", color=value2, title="Detected activity",
                 labels={'date_time': 'Time stamp', "power": "Detected activity"},
        )
    except:
        fig = px.bar(df, x="date_time", y="power", color=value2, title="Detected activity",
                 labels={'date_time': 'Time stamp', "power": "Detected activity"},
        )
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=40, t=50, b=20),
        paper_bgcolor="white",
        yaxis = dict(
            tickmode = 'array',
            tickvals = [0, 1],
            ticktext = ["No", "Yes"],
        ),
    )
    return fig

@app.callback(
    dash.dependencies.Output('timeseries_graph_2', 'figure'),
    [dash.dependencies.Input('dropdown_1', 'value'),
     dash.dependencies.Input('dropdown_2', 'value'),
     dash.dependencies.Input('date_from', 'value'),
     dash.dependencies.Input('date_to', 'value'),
     dash.dependencies.Input('time_from', 'value'),
     dash.dependencies.Input('time_to', 'value')])
def update_graph(value1, value2, date_from, date_to, time_from, time_to):
    if date_from is not None:
        date_from = date_from
    else:
        date_from = "2020-12-01"
    if date_to is not None:
       date_to = date_to
    else:
        date_to = "2020-12-31"
    if time_from is not None:
        time_from = time_from
    else:
        time_from = "07:00:00"
    if time_to is not None:
        time_to = time_to
    else:
        time_to = "23:00:00"
    dff = df[df["date"] >= date_from]
    dff = dff[dff["date"] <= date_to]
    dff = dff[dff["time"] >= time_from]
    dff = dff[dff["time"] <= time_to]
    dff1 = dff[dff["track_id"] == value1]
    out = dff1.groupby(value2).agg({"delta": "sum"})
    out.reset_index(inplace=True)
    out["delta"] = out["delta"] / 60
    try:
        fig = px.bar(out, y="delta", x=value2,
                     title="Activity index",
                     color=value2,
                     labels={'delta':'Minutes', value2: "Type of activity"},
        )
    except:
        fig = px.bar(df, y="delta", x=value2,
                     title="Activity index",
                     color=value2,
                     labels={'delta':'Minutes', value2: "Type of activity"},
        )  
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=40, t=50, b=20),
        paper_bgcolor="white",
    )
    #fig = px.pie(out, values='delta', names='top-1')
    #fig.update_traces(textposition='inside', textfont_size=14)
    return fig

@app.callback(
    dash.dependencies.Output('timeseries_graph_3', 'figure'),
    [dash.dependencies.Input('dropdown_2', 'value')])
def update_graph(value):
    out = df.groupby(value).agg({"delta": "sum"})
    out.reset_index(inplace=True)
    out["delta"] = out["delta"] / 60
    fig = px.bar(out, y="delta", x=value, barmode='group',
                 title="Overall amount of activities over the selected period",
                 color=value,
                 labels={'delta':'Minutes', "track_id": "Tracking id"},
    )
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=40, t=50, b=20),
        paper_bgcolor="white",
    )
    #fig = px.pie(out, values='delta', names='top-1')
    #fig.update_traces(textposition='inside', textfont_size=14)
    return fig

@app.callback(
    dash.dependencies.Output('timeseries_graph_4', 'figure'),
    [dash.dependencies.Input('dropdown_2', 'value')])
def update_graph(value):
    out = df.groupby(["track_id", value]).agg({"delta": "sum"})
    out.reset_index(inplace=True)
    out["delta"] = out["delta"] / 60
    fig = px.bar(out, y="delta", x="track_id", barmode='group',
                 title="Activity index for each tracking id",
                 color=value,
                 labels={'delta':'Minutes', "track_id": "Tracking id"},
    )
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=40, t=50, b=20),
        paper_bgcolor="white",
    )
    #fig = px.pie(out, values='delta', names='top-1')
    #fig.update_traces(textposition='inside', textfont_size=14)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=PORT)
    #app.server.run(debug=True, threaded=True)
