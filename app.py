import os
from flask import Flask, render_template, url_for, request
import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
import subprocess

server = Flask(__name__)

server.config.from_pyfile('config.py')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=external_stylesheets,
    url_base_pathname='/dash/'
)

# Init values
subprocess.call(["gcc", "main.c", "-fopenmp"])

subprocess.call(["./a.exe", "0", "365", "2.2", "1", "0.2", "0.31429", "0.14286", "0.00549"])

file = open("output.txt", "r")
ignore, steps = file.readline().split('\t')
ignore2 = file.readline()
params = file.readline()

df = pandas.DataFrame(
    {
        'Days': [i for i in range(1, 365, 5)],
        'Susceptible': list(map(float, file.readline().split('\t'))),
        'Exposed': list(map(float, file.readline().split('\t'))),
        'Infected': list(map(float, file.readline().split('\t'))),
        'Recovered': list(map(float, file.readline().split('\t')))
    }
)

file.close()

fig = px.line(data_frame=df, x='Days', y=df.columns)

# app layout

app.layout = html.Div([
    html.H1(children="SEIR Model", style={'text-align': 'center'}),

    html.Label('Days of simulation'),
    dcc.Input(value=365, type='number', step=1, id='days_of_simulation'),

    html.Label('Basic reproduction number'),
    dcc.Input(value=2.2, type='number', step=0.1, id='reproduction'),

    html.Label('Mixing parameter'),
    dcc.Input(value=1, type='number', step=0.1, min=1, id='mixing'),

    html.Label('Immunity period'),
    dcc.Dropdown(
        id="dropdown",
        options=[
            {'label': '1 week', 'value': '1w'},
            {'label': '1 month', 'value': '1m'},
            {'label': '6 months', 'value': '6m'},
            {'label': '1 year', 'value': '1y'},
            {'label': '5 years', 'value': '5y'},
            {'label': 'permanent', 'value': 'pm'}
        ],
        value='6m',
        style={"width": "32%"},
    ),

    html.Label('Latency period'),
    dcc.Slider(
        id='latency-period',
        min=0,
        max=20,
        marks={i: 'days' if i == 20 else str(i) for i in range(1, 21)},
        value=5
    ),

    html.Label('Infectious period'),
    dcc.Slider(
        id='infectious-period',
        min=0,
        max=20,
        marks={i: 'days' if i == 20 else str(i) for i in range(1, 21)},
        step=1,
        value=7
    ),
    dcc.Graph(id="test-graph", figure=fig, animate=True)
])


@app.callback(Output("test-graph", 'figure'),
              Input('days_of_simulation', 'value'),
              Input('reproduction', 'value'),
              Input('latency-period', 'value'),
              Input('infectious-period', 'value'),
              Input('mixing', 'value'),
              Input('dropdown', 'value'))
def update_output(days, reproduction, latency, infectious, mixing, immunity):

    subprocess.call(["./a.exe", "0", str(days), str(reproduction),
                     str(mixing), str(1/latency), str(reproduction*(1/infectious)), str(1/infectious), str(count_days(immunity))])

    print([str(days), str(reproduction),
                     str(mixing), str(1/latency), str(reproduction*(1/infectious)), str(1/infectious), str(count_days(immunity))])
    file = open("output.txt", "r")
    ignore, steps = file.readline().split('\t')
    ignore2 = file.readline()
    params = file.readline()

    new_df = pandas.DataFrame(
        {
            'Days': [i for i in range(1, days, 5)],
            'Susceptible': list(map(float, file.readline().split('\t'))),
            'Exposed': list(map(float, file.readline().split('\t'))),
            'Infected': list(map(float, file.readline().split('\t'))),
            'Recovered': list(map(float, file.readline().split('\t')))
        }
    )
    file.close()
    return px.line(data_frame=new_df, x='Days', y=df.columns)


@server.route('/')
@server.route('/dash')
def my_dash_app():
    return app.index()


@server.route('/top10')
def main_simulation():
    return app.index()


def count_days(immunity_period):
    if immunity_period == "1w":
        return 1 / 7
    if immunity_period == "1m":
        return 1 / 30
    if immunity_period == "6m":
        return 1 / (31 + 28 + 31 + 30 + 31 + 30)
    if immunity_period == "1y":
        return 1 / 365
    if immunity_period == "5y":
        return 1 / (366 + 4*365)
    if immunity_period == "pm":
        return -1.00000


if __name__ == '__main__':
    server.run()
