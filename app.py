import os
from flask import Flask, render_template, url_for, request
import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input
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

df = pandas.DataFrame({
    'x': [1, 2, 3],
    'y': [1, 4, 9],
    'z': [1, 16, 27]
})

fig = px.line(data_frame=df, x='x', y=df.columns)

app.layout = html.Div(children=[
    html.H1(children="SEIR Model", style={'text-align': 'center'}),

    html.Div(children=[
        html.Label('Days of simulation'),
        dcc.Input(value=365, type='number', step=1),

        html.Label('Basic reproduction number'),
        dcc.Input(value=2.2, type='number', step=0.1),

        html.Label('Mixing parameter'),
        dcc.Input(value=1, type='number', step=0.1),

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

        html.Label('Immunity period'),
        dcc.Dropdown(
            options=[
                {'label': '1 week', 'value': '1w'},
                {'label': '1 month', 'value': '1m'},
                {'label': '6 months', 'value': '6m'},
                {'label': '1 year', 'value': '1y'},
                {'label': '5 years', 'value': '5y'},
                {'label': 'permanent', 'value': 'pm'}
            ],
            value='6m'
        ),
    ], id='data-input'),

    html.Div(children=dcc.Graph(id="test-graph", figure=fig, animate=True),
             id='graph-div')
], style={'columnCount': 1})


@server.route('/')
@server.route('/dash')
def my_dash_app():
    return app.index()


@server.route('/main')
def main_simulation():
    return render_template("main.html")


def count_days(immunity_period):
    if immunity_period == "6 Months":
        return 1 / (31 + 28 + 31 + 30 + 31 + 30)


if __name__ == '__main__':
    server.run()
